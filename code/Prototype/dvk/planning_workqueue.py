"""Active local planning, separate from Sportlink facts and legacy no-show data."""
from dataclasses import dataclass, replace

from .staffing import StaffingNeed
from .workstream_model import CandidateAssessment, DutyAssignment, DutyService


@dataclass(frozen=True)
class TemporaryPlanning:
    assignment: DutyAssignment
    service: DutyService


def same_service(left: DutyService, right: DutyService) -> bool:
    # Demo service IDs repeat across weeks; a concrete occurrence includes time.
    return (left.service_id, left.starts_at, left.ends_at) == (right.service_id, right.starts_at, right.ends_at)


def planning_conflict(person_id: str, service: DutyService, active: tuple[TemporaryPlanning, ...]) -> str | None:
    same_day = False
    for entry in active:
        if entry.assignment.person_id != person_id:
            continue
        other = entry.service
        if same_service(service, other):
            return "same_service"
        if service.starts_at < other.ends_at and service.ends_at > other.starts_at:
            return "overlap"
        same_day |= service.starts_at.date() == other.starts_at.date()
    return "same_day" if same_day else None


def assess_planning_availability(assessment: CandidateAssessment, service: DutyService, active: tuple[TemporaryPlanning, ...]) -> CandidateAssessment:
    if not assessment.eligible:
        return assessment
    conflict = planning_conflict(assessment.person_id, service, active)
    if conflict in {"same_service", "overlap"}:
        return replace(assessment, eligible=False, preference="none", exclusion_reason=(
            "Al tijdelijk ingepland op deze dienst" if conflict == "same_service"
            else "Overlapt met een actieve tijdelijke DVK-inroostering"
        ))
    if conflict == "same_day":
        return replace(assessment, preference="avoid", planning_relation="same_day_emergency")
    return assessment


def planning_staffing(service: DutyService, source: StaffingNeed, active: tuple[TemporaryPlanning, ...]) -> StaffingNeed:
    """Recalculate from source occupancy, never add local occupancy twice."""
    if source.service_id != service.service_id or source.minimum_staff != service.required_staff:
        raise ValueError("staffing need does not belong to service")
    local = sum(same_service(service, entry.service) for entry in active)
    occupancy = source.confirmed_occupancy + local
    return replace(source, temporary_occupancy=local,
                   open_need=max(0, source.minimum_staff - occupancy),
                   remaining_capacity=max(0, source.maximum_staff - occupancy))


def validate_planning_selection(person_ids: tuple[str, ...], service: DutyService, source: StaffingNeed, active: tuple[TemporaryPlanning, ...]) -> None:
    if len(set(person_ids)) != len(person_ids):
        raise ValueError("a person can only be selected once for the same service")
    for person_id in person_ids:
        conflict = planning_conflict(person_id, service, active)
        if conflict in {"same_service", "overlap"}:
            raise ValueError(f"temporary planning conflict: {conflict}")
    if len(person_ids) > planning_staffing(service, source, active).remaining_capacity:
        raise ValueError("selection exceeds remaining service capacity")
