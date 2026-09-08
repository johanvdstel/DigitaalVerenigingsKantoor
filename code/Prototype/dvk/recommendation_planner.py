from __future__ import annotations

from dataclasses import dataclass

from .workstream_model import CandidatePriority, DutyService


@dataclass(frozen=True)
class RecommendationPlan:
    recommended: tuple[CandidatePriority, ...]
    skipped_same_day: frozenset[tuple[str, str]]


def _same_priority(a: CandidatePriority, b: CandidatePriority) -> bool:
    return (a.remaining_hours, a.previous_season_backlog, a.previous_season_considered, a.match_preference) == (
        b.remaining_hours, b.previous_season_backlog, b.previous_season_considered, b.match_preference
    )


def plan_recommendations(
    priorities: tuple[CandidatePriority, ...],
    services: tuple[DutyService, ...],
) -> RecommendationPlan:
    """Plan first recommendations across services without duplicating a person on one day.

    Existing per-service ranking remains authoritative. For later services on the
    same day, someone already proposed is skipped while another ranked candidate
    is available. Equal substantive first choices stay visible together.
    """
    services_by_id = {service.service_id: service for service in services}
    missing_services = {p.service_id for p in priorities} - services_by_id.keys()
    if missing_services:
        raise ValueError(f"unknown service ids in priorities: {sorted(missing_services)}")

    recommended: list[CandidatePriority] = []
    skipped_same_day: set[tuple[str, str]] = set()
    proposed_by_day: dict[object, set[str]] = {}

    service_ids = sorted(
        {p.service_id for p in priorities},
        key=lambda service_id: services_by_id[service_id].starts_at,
    )
    for service_id in service_ids:
        service = services_by_id[service_id]
        day = service.starts_at.date()
        used = proposed_by_day.setdefault(day, set())
        rows = sorted((p for p in priorities if p.service_id == service_id), key=lambda p: p.rank)
        available = [row for row in rows if row.person_id not in used]
        if available:
            for row in rows:
                if row.person_id in used:
                    skipped_same_day.add((service_id, row.person_id))
            pool = available
        else:
            pool = rows
        if not pool:
            continue

        first = pool[0]
        selected = [first, *(row for row in pool[1:] if _same_priority(row, first))]
        recommended.extend(selected)
        used.update(row.person_id for row in selected)

    return RecommendationPlan(tuple(recommended), frozenset(skipped_same_day))
