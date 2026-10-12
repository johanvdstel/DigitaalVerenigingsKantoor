"""Explicit dashboard population selection; source and duty rules remain intact."""
from dataclasses import dataclass
from datetime import date

from .real_data_import import SportlinkRealDataAdapter


@dataclass(frozen=True)
class SelectionRow:
    person_id: str
    member: str
    outcome: str
    reason: str


def select_population(member_rows, source, as_of: date):
    adapter = SportlinkRealDataAdapter
    grouped = {}
    for row in member_rows:
        pid = adapter.value(row, 'Rel. code')
        if pid:
            grouped.setdefault(pid, []).append(row)
    persons = {p.person_id: p for p in source.persons}
    memberships = {m.person_id: m for m in source.memberships}
    results = []
    for pid, variants in grouped.items():
        names = {adapter.value(row, 'Naam') for row in variants}
        name = next(iter(names)) if len(names) == 1 else 'Naam niet eenduidig'
        blocking = [s for s in source.signals if s.dataset == 'leden' and s.record_key == pid
                    and s.code in {'CONFLICTING_DUPLICATE_IDENTITY',
                                   'CONFLICTING_DUPLICATE_MEMBERSHIP', 'INVALID_TERMINATION_DATE'}]
        membership = memberships.get(pid)
        if blocking:
            outcome, reason = 'Selectieprobleem', '; '.join(dict.fromkeys(s.message for s in blocking))
        elif pid not in persons or membership is None:
            outcome, reason = 'Selectieprobleem', 'Ledenregel kon niet betrouwbaar worden verwerkt'
        else:
            status = membership.status.strip().casefold()
            if status in {'in behandeling', 'afgewezen', 'aspirant lid'}:
                outcome, reason = 'Uitgesloten', f'Lidstatus: {membership.status}'
            elif status not in {'definitief', 'afgemeld', 'oud lid', 'afmelding in de toekomst'}:
                outcome, reason = 'Selectieprobleem', f'Onbekende lidstatus: {membership.status}'
            else:
                current = adapter.current_membership(membership.status, membership.end_date, as_of)
                if current is None:
                    outcome, reason = 'Selectieprobleem', 'Afmelddatum ontbreekt; lidmaatschap op peildatum onzeker'
                elif current:
                    outcome, reason = 'Meegenomen', 'Lid op peildatum'
                else:
                    outcome, reason = 'Uitgesloten', f'Afmelddatum bereikt: {membership.end_date:%d-%m-%Y}'
        results.append(SelectionRow(pid, name or 'Naam onbekend', outcome, reason))
    return tuple(results)
