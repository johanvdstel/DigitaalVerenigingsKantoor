"""Source-based B-05/B-06/B-07; the historical case engine stays intact."""
from dataclasses import dataclass
from datetime import date

from .model import DutyPolicy, Person
from .real_data_import import RealDataImportResult, SportlinkRealDataAdapter


def canonical_address(person: Person) -> tuple[str, str, str] | None:
    if person.address_conflicting or not person.postal_code or not person.house_number:
        return None
    postcode = "".join(person.postal_code.upper().split())
    number = person.house_number.strip().upper()
    if not postcode or not number:
        return None
    return postcode, number, (person.house_number_addition or "").strip().upper()


def family_criteria(left: Person, right: Person) -> tuple[str, ...]:
    """Only a complete, non-conflicting registered address proves a household."""
    address = canonical_address(left)
    return ("address",) if address is not None and address == canonical_address(right) else ()


def _possible_family(left: Person, right: Person) -> bool:
    return canonical_address(left) is None or canonical_address(right) is None


def _age(person: Person, as_of: date) -> int | None:
    born = person.birth_date
    if born is None or born > as_of:
        return None
    return as_of.year - born.year - ((as_of.month, as_of.day) < (born.month, born.day))


@dataclass(frozen=True)
class DutyGround:
    code: str
    supporting_person_id: str | None = None
    criteria: tuple[str, ...] = ()
    registrations: tuple = ()


@dataclass(frozen=True)
class MemberDutyExpectation:
    person_id: str
    status: str
    expected_required_hours: int | None
    grounds: tuple[DutyGround, ...]
    source_facts: tuple
    as_of: date
    policy_version: str
    kind: str = "DERIVED"


def derive_member_duties(source: RealDataImportResult, as_of: date,
                         policy: DutyPolicy) -> tuple[MemberDutyExpectation, ...]:
    persons = {p.person_id: p for p in source.persons}
    memberships = {m.person_id: m for m in source.memberships}
    current = {pid: SportlinkRealDataAdapter.current_membership(m.status, m.end_date, as_of)
               for pid, m in memberships.items()}
    relevant = {pid for pid, m in memberships.items() if current[pid] is True
                and m.plays_football and not m.recreational}
    possible_relevant = {pid for pid, m in memberships.items() if current[pid] is not False
                         and m.plays_football and not m.recreational}
    ages = {pid: _age(p, as_of) for pid, p in persons.items()}
    functions = {}
    for item in source.function_classification.registrations:
        fact = item.source
        if (getattr(fact, "active", True)
                and (fact.start_date is None or fact.start_date <= as_of)
                and (fact.end_date is None or fact.end_date >= as_of)):
            functions.setdefault(fact.person_id, []).append(item)
    # Per-assessment lookup tables, not a cross-run result cache. Keep original
    # record order when gathering evidence for a person and supporting members.
    addresses = {pid: canonical_address(person) for pid, person in persons.items()}
    teams_by_person, member_provenance = {}, {}
    for index, fact in enumerate(source.team_memberships):
        teams_by_person.setdefault(fact.person_id, []).append((index, fact))
    for index, fact in enumerate(source.provenance):
        if fact.source_dataset == "leden":
            member_provenance.setdefault(fact.source_record_key.split(":", 1)[0], []).append((index, fact))
    family_registrations = {pid: (tuple(item for item in items if item.household_exempt),
                                 tuple(item for item in items if not item.known))
                            for pid, items in functions.items()}
    relevant_by_address = {}
    for pid in possible_relevant:
        relevant_by_address.setdefault(addresses.get(pid), set()).add(pid)
    results = []
    for pid, person in persons.items():
        membership = memberships.get(pid)
        grounds, uncertainty, support_ids = [], [], {pid}
        if membership is None or current.get(pid) is None:
            uncertainty.append(DutyGround("membership_unknown"))
        elif current[pid] is False:
            grounds.append(DutyGround("inactive_membership"))
        elif membership.recreational:
            grounds.append(DutyGround("recreational"))
        elif not membership.plays_football:
            grounds.append(DutyGround("not_playing"))
        if membership is not None and membership.honorary:
            grounds.append(DutyGround("honorary"))
        for item in functions.get(pid, ()):
            if item.self_exempt:
                grounds.append(DutyGround("personal_function", pid, registrations=(item,)))
            elif not item.known:
                uncertainty.append(DutyGround("function_classification_unknown", pid, registrations=(item,)))
        for other_id, registrations in functions.items():
            if other_id == pid or current.get(other_id) is False:
                continue
            household, unknown = family_registrations[other_id]
            if not household and not unknown:
                continue
            other = persons.get(other_id)
            support_ids.add(other_id)
            address = addresses[pid]
            other_address = addresses.get(other_id)
            if current.get(other_id) is None:
                if household and (address is None or other_address is None or address == other_address):
                    uncertainty.append(DutyGround("household_membership_unknown", other_id, registrations=household))
                continue
            if unknown and (address is None or other_address is None or address == other_address):
                uncertainty.append(DutyGround("household_function_classification_unknown", other_id, registrations=unknown))
            if not household:
                continue
            if address is not None and address == other_address:
                grounds.append(DutyGround("household_function", other_id, ("address",), household))
            elif address is None or other_address is None:
                uncertainty.append(DutyGround("household_address_insufficient", other_id, registrations=household))
        if pid in relevant and addresses[pid] is None and ages[pid] is not None and ages[pid] >= 18:
            uncertainty.append(DutyGround("household_address_insufficient"))
        older = []
        if ages[pid] is None:
            uncertainty.append(DutyGround("birth_date_insufficient"))
        elif ages[pid] < 18 and pid in relevant:
            if addresses[pid] is None:
                uncertainty.append(DutyGround("family_data_insufficient"))
            possible_family = (possible_relevant if addresses[pid] is None else
                               relevant_by_address.get(addresses[pid], set()) | relevant_by_address.get(None, set()))
            for other_id in sorted(possible_family - {pid}):
                other = persons.get(other_id)
                if other is None:
                    continue
                criteria = ("address",) if addresses[pid] is not None and addresses[pid] == addresses[other_id] else ()
                possible = addresses[pid] is None or addresses[other_id] is None
                if not criteria and not possible:
                    continue
                if ages.get(other_id) is None:
                    support_ids.add(other_id)
                    uncertainty.append(DutyGround("family_birth_date_insufficient" if criteria
                                                  else "family_data_insufficient", other_id, criteria))
                    continue
                if ages[other_id] >= 18 or other.birth_date > person.birth_date:
                    continue
                if current[other_id] is None:
                    if criteria or possible:
                        support_ids.add(other_id)
                        uncertainty.append(DutyGround("family_membership_unknown", other_id, criteria))
                    continue
                if criteria:
                    support_ids.add(other_id)
                    if other.birth_date == person.birth_date:
                        uncertainty.append(DutyGround("oldest_minor_undetermined", other_id, criteria))
                    else:
                        older.append((other.birth_date, other_id, criteria))
                elif possible:
                    support_ids.add(other_id)
                    uncertainty.append(DutyGround("family_data_insufficient", other_id))
            if older:
                oldest_date = min(item[0] for item in older)
                grounds.extend(DutyGround("younger_minor", subject, criteria)
                               for born, subject, criteria in sorted(older) if born == oldest_date)
        if grounds:
            status, hours = "vrijgesteld", 0
        elif uncertainty:
            status, hours = "niet betrouwbaar beoordeelbaar", None
        else:
            status, hours = "taakplichtig", policy.required_hours
            # FB-01: only the explanation changes; status and hours are already set.
            multiple_minors = ages[pid] is not None and ages[pid] < 18 and any(
                other_id != pid and ages.get(other_id) is not None and ages[other_id] < 18
                and other_id in persons and addresses[pid] is not None
                and addresses[pid] == addresses[other_id]
                for other_id in relevant_by_address.get(addresses[pid], set()) if other_id in relevant)
            grounds.append(DutyGround("oldest_minor" if multiple_minors else "no_exemption_found"))
        facts = tuple(persons[sid] for sid in sorted(support_ids) if sid in persons)
        facts += tuple(memberships[sid] for sid in sorted(support_ids) if sid in memberships)
        facts += tuple(fact for _, fact in sorted(
            (entry for sid in support_ids for entry in teams_by_person.get(sid, ())), key=lambda entry: entry[0]))
        facts += tuple(fact for _, fact in sorted(
            (entry for sid in support_ids for entry in member_provenance.get(sid, ())), key=lambda entry: entry[0]))
        results.append(MemberDutyExpectation(pid, status, hours, tuple(grounds + uncertainty),
                                             facts, as_of, policy.version))
    return tuple(results)
