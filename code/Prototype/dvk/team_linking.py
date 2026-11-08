"""v0.5 CKC team-name linking; competition IDs are source context only."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping

from .real_data_import import RealTeamMembership

CKC_CLUB_RELATION_CODE = "BBDZ08H"
MATCHDAYS = ("Algemeen/Zaterdag", "Algemeen/Zondag")


@dataclass(frozen=True, order=True)
class CkcTeamIdentity:
    name: str
    matchday: str = ""

    @property
    def team_id(self) -> str:
        """Shared human-readable key, not a Sportlink competition identifier."""
        return f"2 / {self.matchday}" if self.name == "2" else self.name


def membership_identity(membership: RealTeamMembership) -> CkcTeamIdentity | None:
    name = membership.team_id.strip()
    if not name:
        return None
    matchday = (membership.matchday or "").strip() if name == "2" else ""
    if name == "2" and matchday not in MATCHDAYS:
        return None
    return CkcTeamIdentity(name, matchday)


@dataclass(frozen=True)
class ProgramTeamLink:
    record_key: str
    home_team_name: str
    away_team_name: str
    home_club_code: str
    away_club_code: str
    side: str | None
    original_team_name: str | None
    source_team_id: str | None
    competition: str
    competition_type: str
    normalized_name: str | None
    normalizations: tuple[str, ...]
    candidates: tuple[CkcTeamIdentity, ...]
    status: str
    reason: str

    @property
    def identity(self) -> CkcTeamIdentity | None:
        return self.candidates[0] if self.status == "matched" else None


def link_program_team(
    row: Mapping[str, object], catalog: Iterable[CkcTeamIdentity], *, record_key: str,
) -> ProgramTeamLink:
    """Apply only the CKC-approved rules; never use a match date or team ID."""
    raw = lambda key: str(row.get(key) or "")
    home_code, away_code = raw("thuisteamclubrelatiecode"), raw("uitteamclubrelatiecode")
    home = home_code.strip() == CKC_CLUB_RELATION_CODE
    away = away_code.strip() == CKC_CLUB_RELATION_CODE
    context = dict(
        record_key=record_key, home_team_name=raw("thuisteam"), away_team_name=raw("uitteam"),
        home_club_code=home_code, away_club_code=away_code,
        competition=raw("competitie"), competition_type=raw("competitiesoort"),
    )
    if home == away:
        return ProgramTeamLink(
            **context, side=None, original_team_name=None, source_team_id=None,
            normalized_name=None, normalizations=(), candidates=(),
            status="unmatched", reason="CKC-wedstrijdzijde ontbreekt of is dubbelzinnig",
        )
    side = "thuis" if home else "uit"
    original_name = raw(side + "team")
    name = original_name.strip()
    steps: list[str] = []
    if name != original_name:
        steps.append("trim_outer_whitespace")
    if name.startswith("CKC "):
        name = name[4:]
        steps.append("remove_CKC_prefix")
    if raw("competitiesoort").strip() in ("Rijnmond Cup", "Rijnmondcup"):
        if name == "JO O13":
            name = "O13"
            steps.append("Rijnmond_JO_O13_to_O13")
        if re.fullmatch(r"(?:MO|O)\d+", name):
            name += "-1"
            steps.append("Rijnmond_add_team_number_1")
    # Multiple member rows of the same team are not multiple team candidates.
    candidates = tuple(sorted({team for team in catalog if team.name == name}))
    reason = "Geen overeenkomstig bestaand CKC-team"
    if name == "2":
        competition = raw("competitie").casefold()
        saturday = bool(re.search(r"\bzaterdag\b", competition))
        sunday = bool(re.search(r"\bzondag\b", competition))
        if saturday == sunday:
            return ProgramTeamLink(
                **context, side="HOME" if home else "AWAY", original_team_name=original_name,
                source_team_id=raw(side + "teamid"), normalized_name=name,
                normalizations=tuple(steps), candidates=candidates,
                status="ambiguous" if len(candidates) > 1 else "unmatched",
                reason="Competitieomschrijving bepaalt zaterdag/zondag niet eenduidig",
            )
        matchday = MATCHDAYS[0] if saturday else MATCHDAYS[1]
        candidates = tuple(team for team in candidates if team.matchday == matchday)
    status = "matched" if len(candidates) == 1 else "ambiguous" if candidates else "unmatched"
    if status == "matched":
        reason = "Unieke overeenkomst met bestaand CKC-team"
    elif status == "ambiguous":
        reason = "Meerdere overeenkomstige CKC-teams"
    return ProgramTeamLink(
        **context, side="HOME" if home else "AWAY", original_team_name=original_name,
        source_team_id=raw(side + "teamid"), normalized_name=name,
        normalizations=tuple(steps), candidates=candidates, status=status, reason=reason,
    )
