"""v0.5 import boundary linking Teams and Programma before candidate selection.

The accepted v0.4 transport/date/status adapter remains unchanged. Copies of
linked rows carry the resolved key internally; original source values are kept
in links. Unresolved links cannot be consumed as an empty planning context.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .programma_adapter import ProgramImportResult, SportlinkProgrammaAdapter
from .real_data_import import DataQualitySignal, RealTeamMembership
from .team_linking import CKC_CLUB_RELATION_CODE, ProgramTeamLink, link_program_team, membership_identity
from .workstream_model import Match, TeamMembership


class UnresolvedProgramTeamsError(ValueError):
    """Inspect the import's links and signals before using planning context."""


@dataclass(frozen=True)
class LinkedProgramImportResult:
    program: ProgramImportResult
    links: tuple[ProgramTeamLink, ...]
    signals: tuple[DataQualitySignal, ...]
    _team_memberships: tuple[TeamMembership, ...]
    _unresolved_memberships: bool

    def _require_team_links(self) -> None:
        if self._unresolved_memberships or any(link.status != "matched" for link in self.links):
            raise UnresolvedProgramTeamsError(
                "Teamkoppeling ontbreekt of is ambigu; beoordeel de bronmeldingen vóór kandidaatselectie"
            )

    @property
    def matches(self) -> tuple[Match, ...]:
        self._require_team_links()
        return self.program.matches

    @property
    def team_memberships(self) -> tuple[TeamMembership, ...]:
        self._require_team_links()
        return self._team_memberships


class CkcProgrammaAdapter(SportlinkProgrammaAdapter):
    """Explicit v0.5 entry point; requires the existing CKC Teams import.

    Inherits the read-only request contract for SportlinkProgrammaClient. The
    legacy v0.4 adapter stays available for its accepted baseline cases.
    """

    def __init__(self, *, team_memberships: Iterable[RealTeamMembership]):
        super().__init__(club_relation_code=CKC_CLUB_RELATION_CODE)
        self.source_memberships = tuple(team_memberships)

    def import_rows(self, rows: Iterable[dict[str, object]], *,
                    retrieved_at: datetime | None = None) -> LinkedProgramImportResult:
        memberships: list[TeamMembership] = []
        catalog = set()
        signals: list[DataQualitySignal] = []
        unresolved_memberships = False
        for index, membership in enumerate(self.source_memberships, 1):
            identity = membership_identity(membership)
            if identity is None:
                unresolved_memberships = True
                signals.append(DataQualitySignal(
                    "CKC_TEAM_MEMBERSHIP_UNRESOLVED", "ERROR", "teams", str(index),
                    "Teamnaam ontbreekt of team 2 heeft geen eenduidige Speeldag",
                ))
                continue
            catalog.add(identity)
            memberships.append(TeamMembership(membership.person_id, identity.team_id))

        linked_rows = []
        links = []
        for index, row in enumerate(rows, 1):
            link = link_program_team(row, catalog, record_key=self._record_key(row, index))
            links.append(link)
            if link.identity is None:
                signals.append(DataQualitySignal(
                    "PROGRAM_TEAM_AMBIGUOUS" if link.status == "ambiguous" else "PROGRAM_TEAM_UNMATCHED",
                    "ERROR", "programma", link.record_key, link.reason,
                ))
                continue
            normalized_row = dict(row)
            normalized_row["thuisteamid" if link.side == "HOME" else "uitteamid"] = link.identity.team_id
            linked_rows.append(normalized_row)
        program = super().import_rows(linked_rows, retrieved_at=retrieved_at)
        return LinkedProgramImportResult(
            program, tuple(links), tuple(signals) + program.signals,
            tuple(memberships), unresolved_memberships,
        )
