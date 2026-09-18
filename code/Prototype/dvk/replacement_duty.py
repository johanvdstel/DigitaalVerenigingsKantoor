from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .no_show import NoShowEvent, SanctionAssessment


@dataclass(frozen=True)
class ReplacementDuty:
    """A self-arranged replacement duty linked to a first no-show."""

    replacement_id: str
    no_show_id: str
    assignment_id: str
    person_id: str
    season: str
    registered_at: datetime
    registered_by: str
    completed_at: datetime | None = None
    completed_by: str | None = None

    @property
    def completed(self) -> bool:
        return self.completed_at is not None


@dataclass(frozen=True)
class ActiveSanctionState:
    """Current sanction state; historical events remain separate facts."""

    person_id: str
    season: str
    counter: int
    assessment: SanctionAssessment | None
    repaired_no_show_ids: tuple[str, ...] = ()


def active_sanction_state(
    person_id: str,
    season: str,
    no_shows: tuple[NoShowEvent, ...],
    replacements: tuple[ReplacementDuty, ...] = (),
) -> ActiveSanctionState:
    """Derive active counter from history, including Gate-10 first-stage repair.

    Only a successfully completed replacement linked to a first-stage no-show
    resets the active counter. Later-stage no-shows do not open a repair path.
    """
    valid = sorted(
        (event for event in no_shows if event.person_id == person_id and event.season == season and event.status == "valid"),
        key=lambda event: (event.occurred_at, event.no_show_id),
    )
    completed_by_no_show = {
        replacement.no_show_id: replacement
        for replacement in replacements
        if replacement.person_id == person_id
        and replacement.season == season
        and replacement.completed
    }

    counter = 0
    last_assessment = None
    repaired: list[str] = []
    prior_active: list[NoShowEvent] = []
    for event in valid:
        # Re-use the accepted Gate-9 ladder, but feed only events that still
        # contribute to the active counter.
        from .no_show import assess_sanction

        assessment = assess_sanction(event, tuple(prior_active))
        counter = assessment.counter
        last_assessment = assessment
        if counter == 1 and event.no_show_id in completed_by_no_show:
            repaired.append(event.no_show_id)
            counter = 0
            last_assessment = None
            prior_active = []
        else:
            prior_active.append(event)

    return ActiveSanctionState(person_id, season, counter, last_assessment, tuple(repaired))
