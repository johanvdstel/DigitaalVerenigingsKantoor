"""B-02 qualification of one parsed team registration; no source validation."""


def is_bond_team_player(team_type: str | None, team_role: str | None,
                        playing_member: bool | None) -> bool:
    """All three conditions must hold on the same registration.

    Parsing, validation, person aggregation and planning remain with callers.
    Preserve casefold semantics; do not add whitespace cleanup or date rules.
    """
    return ((team_type or "").casefold() == "bond"
            and (team_role or "").casefold() == "teamspeler"
            and playing_member is True)
