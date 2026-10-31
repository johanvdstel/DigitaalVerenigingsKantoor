"""BL-20: source matchdays and minimum-only emergency choices."""
from dataclasses import replace

from .real_data_import import RealTeamMembership
from .proposal_planning import PlannedProposal, plan_proposals
from .team_linking import membership_identity

MATCHDAY_WEEKDAYS = {
    "Algemeen/Vrijdag": 4,
    "Algemeen/Zaterdag": 5, "Algemeen/Zondag": 6,
    "Zaterdag": 5,
}
EMERGENCY_MATCHDAY_REASON = "Noodkandidaat: andere teamspeeldag; uitsluitend voor minimumbezetting"


class TeamMatchdayError(ValueError):
    pass


def validate_team_matchdays(memberships):
    """Validate every imported team row, including non-player roles."""
    by_team = {}
    for membership in memberships:
        day = MATCHDAY_WEEKDAYS.get((membership.matchday or "").strip())
        if day is None:
            raise TeamMatchdayError("Teams-bronfout: Speeldag ontbreekt of is onbekend. Kandidaten en voorstellen zijn geblokkeerd.")
        identity = membership_identity(membership)
        if identity is None:
            raise TeamMatchdayError("Teams-bronfout: teamidentiteit is niet eenduidig. Controleer Speeldag.")
        previous = by_team.setdefault(identity, day)
        if previous != day:
            raise TeamMatchdayError("Teams-bronfout: tegenstrijdige Speeldag voor hetzelfde team. Kandidaten en voorstellen zijn geblokkeerd.")


def validate_source_team_matchdays(source):
    # Diagnostic records retain even rows rejected because a person could not be
    # linked. A serious team-attribute error must not disappear with that row.
    teams = []
    for record in source.diagnostic_records:
        if record.dataset == "teams":
            values = dict(record.values)
            teams.append(RealTeamMembership(record.person_id, values.get("Team", "").strip(),
                                            None, None, matchday=values.get("Speeldag")))
    validate_team_matchdays(tuple(teams) if teams else source.team_memberships)


def other_weekend_persons(memberships, service):
    validate_team_matchdays(memberships)
    weekday = service.starts_at.weekday()
    if weekday < 5:
        return frozenset()
    by_person = {}
    for membership in memberships:
        if ((membership.team_type or "").casefold() == "bond"
                and (membership.team_role or "").casefold() == "teamspeler"
                and membership.playing_member is True):
            # Friday does not impose a weekend restriction; other links retain theirs.
            if MATCHDAY_WEEKDAYS[membership.matchday.strip()] < 5:
                continue
            by_person.setdefault(membership.person_id, set()).add(
                MATCHDAY_WEEKDAYS[membership.matchday.strip()])
    return frozenset(pid for pid, days in by_person.items() if weekday not in days)


def plan_matchday_proposals(proposals, need, other_weekend):
    regular = tuple(p for p in proposals if p.person_id not in other_weekend)
    emergency = tuple(p for p in proposals if p.person_id in other_weekend)
    planned = plan_proposals(regular, need, offer_all=True)
    if need.remaining_capacity <= 0:
        return ()
    if len(regular) >= need.minimum_coverage_slots:
        return planned
    # Offer alternatives for human selection, never automatic scheduling.
    return planned + tuple(PlannedProposal(
        replace(p, suitability="emergency",
                uncertainties=p.uncertainties + (EMERGENCY_MATCHDAY_REASON,)),
        "emergency_minimum_coverage",
    ) for p in emergency)


def validate_emergency_selection(proposals, need):
    emergency = sum(EMERGENCY_MATCHDAY_REASON in p.uncertainties for p in proposals)
    regular = len(proposals) - emergency
    if emergency and emergency > max(0, need.minimum_coverage_slots - regular):
        raise ValueError("Noodkandidaten van de andere teamspeeldag zijn uitsluitend toegestaan tot de minimumbezetting.")
