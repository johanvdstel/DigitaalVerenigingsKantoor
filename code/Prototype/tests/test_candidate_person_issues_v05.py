"""PR #44 correction: person errors are local, technical CSV errors remain fatal."""
import csv
import io

import pytest

from dvk.candidate_context import CandidateSourceError
from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.model import Person
from test_candidate_context_v05 import (IDENTITY, PERIOD, context, csv_bytes, exports, factory,
                                         propose, service)


def data_with_two():
    return exports(members=[dict(pid='M1', born='01-01-1990', team='O17-1', number='1'),
                            dict(pid='M2', born='01-01-1991', team='O17-1', number='2')])


def rows(data, dataset):
    return list(csv.DictReader(io.StringIO(data[dataset].decode('utf-8-sig')), delimiter=';'))


def write_rows(data, dataset, values):
    fields = list(dict.fromkeys(key for value in values for key in value))
    data[dataset] = csv_bytes(fields, values)


def ids(result):
    return [item.proposal.person_id for item in result.planned]


@pytest.mark.parametrize('status', ['Afgemeld', 'Overschrijving spelactiviteit', 'Oud bondslid', 'Oud relatie'])
@pytest.mark.parametrize('end', ['', '01-01-2015', '01-07-2027'])
def test_only_definitief_may_proceed_regardless_of_other_status_end_date(status, end):
    data = data_with_two()
    members = rows(data, 'leden')
    members[1].update({'Lidstatus': status, 'Afmelddatum': end})
    write_rows(data, 'leden', members)
    ctx = context(data)
    assert ctx.error is None
    assert ids(propose(ctx)) == ['M1']
    if status != 'Afgemeld':
        assert 'UNKNOWN_MEMBERSHIP_STATUS' in ctx.signal_counts


@pytest.mark.parametrize('end,expected', [('', ['M1', 'M2']), ('01-07-2027', ['M1', 'M2']), ('01-01-2026', ['M1'])])
def test_definitief_still_respects_existing_termination_and_reference_date(end, expected):
    data = data_with_two()
    members = rows(data, 'leden')
    members[1]['Afmelddatum'] = end
    write_rows(data, 'leden', members)
    assert ids(propose(context(data))) == expected


def test_sportlink_duty_for_definitive_nonplaying_member_is_not_policy_filtered():
    data = data_with_two()
    members = rows(data, 'leden')
    members[1]['Lidsoort'] = 'Relatie'
    write_rows(data, 'leden', members)
    teams = rows(data, 'teams')
    teams[1].update({'Teamsoort': 'Vereniging', 'Teamrol': 'Teammanager', 'Spelend lid': 'Nee'})
    write_rows(data, 'teams', teams)
    result = propose(context(data))
    assert ids(result) == ['M1', 'M2']
    assert next(c for c in result.controls if c.person_id == 'M2').expectation.status == 'vrijgesteld'


@pytest.mark.parametrize('conflict', ['historical', 'active', 'identity', 'birth_date'])
def test_conflicting_duplicates_exclude_only_the_affected_relation_code(conflict):
    data = data_with_two()
    members = rows(data, 'leden')
    duplicate = dict(members[1])
    if conflict == 'historical':
        members[1].update({'Lidstatus': 'Oud bondslid', 'Afmelddatum': '01-01-2015'})
        duplicate.update({'Lidstatus': 'Oud relatie', 'Afmelddatum': '01-01-2023'})
    elif conflict == 'active':
        duplicate.update({'Lidstatus': 'Afgemeld', 'Afmelddatum': '01-01-2023'})
    elif conflict == 'identity':
        duplicate['Naam'] = 'Andere synthetische persoon'
    else:
        duplicate['Geb.dat.'] = '01-01-1992'
    write_rows(data, 'leden', members + [duplicate])
    ctx = context(data)
    assert ctx.error is None
    assert ctx.signal_counts['DUPLICATE_PERSON_SOURCE_RECORD'] == 1
    assert any(code.startswith('CONFLICTING_DUPLICATE') for code in ctx.signal_counts)
    result = propose(ctx)
    assert ids(result) == ['M1']
    assert all(case.person.person_id != 'M2' for case in result.cases)
    assert result.planned[0].proposal.E == 10


def test_identical_duplicate_rows_do_not_duplicate_candidate_or_hours():
    data = data_with_two()
    members = rows(data, 'leden')
    write_rows(data, 'leden', members + [dict(members[1])])
    result = propose(context(data))
    assert ids(result) == ['M1', 'M2']
    assert [p.proposal.E for p in result.planned] == [10, 10]


@pytest.mark.parametrize('invalid', ['hours', 'duplicate_hours', 'birth_date', 'termination'])
def test_other_person_data_errors_do_not_block_a_regular_candidate(invalid):
    data = data_with_two()
    if invalid in {'hours', 'duplicate_hours'}:
        hours = rows(data, 'vrijwilligers_periode')
        if invalid == 'hours':
            hours[1]['Niet ingedeeld'] = '999'
        else:
            hours.append(dict(hours[1]))
        write_rows(data, 'vrijwilligers_periode', hours)
    else:
        members = rows(data, 'leden')
        members[1]['Geb.dat.' if invalid == 'birth_date' else 'Afmelddatum'] = 'synthetisch ongeldig'
        write_rows(data, 'leden', members)
    ctx = context(data)
    assert ctx.error is None
    assert ids(propose(ctx)) == ['M1']
    if invalid == 'birth_date':
        assert ctx.signal_counts['INVALID_BIRTH_DATE'] == 1


def test_orphan_row_number_is_not_a_relation_code_and_missing_id_is_not_everyones_fault():
    data = exports(members=[dict(pid='1', born='01-01-1990', team='O17-1')],
                   hours=[('ORPHAN', 10, 0, 0, 0, 10), ('1', 10, 0, 0, 0, 10)])
    members = rows(data, 'leden')
    members.append(dict(members[0], **{'Rel. code': '', 'Naam': 'Synthetische regel zonder code'}))
    write_rows(data, 'leden', members)
    ctx = context(data)
    assert ctx.signal_counts['MISSING_PERSON_ID'] == 1
    assert ctx.signal_counts['UNMATCHED_PERSON_REFERENCE'] == 1
    assert ids(propose(ctx)) == ['1']
    # Diagnostics remain intact in the original source context.
    assert any(s.code == 'UNMATCHED_PERSON_REFERENCE' and s.record_key == '1' for s in ctx.source.signals)


def test_identical_names_keep_separate_code_based_hours_without_new_name_matching():
    data = data_with_two()
    members = rows(data, 'leden')
    for member in members:
        member['Naam'] = 'Synthetische gelijke naam'
    write_rows(data, 'leden', members)
    hours = rows(data, 'vrijwilligers_periode')
    hours[1].update({'Voldaan': '6', 'Niet ingedeeld': '4'})
    write_rows(data, 'vrijwilligers_periode', hours)
    result = propose(context(data))
    assert [(p.proposal.person_id, p.proposal.E) for p in result.planned] == [('M1', 10), ('M2', 4)]


def test_actual_ambiguous_name_matching_keeps_no_automatic_person_choice_and_other_matches():
    slot = service()
    people = (Person('A', 'Synthetisch A', sportlink_name='Dubbele naam'),
              Person('B', 'Synthetisch B', sportlink_name='Dubbele naam'),
              Person('C', 'Synthetisch C', sportlink_name='Unieke naam'))
    booking_rows = [dict(naam=name, datumvanaf=slot.starts_at.isoformat(), datumtot=slot.ends_at.isoformat())
                    for name in ('Dubbele naam', 'Unieke naam')]
    imported = SportlinkVrijwilligersAdapter().import_rows(
        task_code='741', rows=booking_rows, services=[ServiceBinding('741', slot)],
        persons=people, imported_at=slot.starts_at)
    assert imported.bookings[0].person_id is None
    assert imported.bookings[1].person_id == 'C'
    assert any(s.code == 'VOLUNTEER_PERSON_AMBIGUOUS' for s in imported.signals)


@pytest.mark.parametrize('invalid', ['missing_file', 'missing_column', 'broken_row'])
def test_technical_csv_failures_still_block_source_as_a_whole(invalid):
    data = data_with_two()
    if invalid == 'missing_file':
        del data['leden']
    elif invalid == 'missing_column':
        data['leden'] = b'Onbruikbare kolom\nsynthetisch\n'
    else:
        data['leden'] += b'extra;broken;row\n'
    with pytest.raises(CandidateSourceError):
        context(data)


def test_other_function_subject_hours_error_does_not_invalidate_regular_person():
    data = data_with_two()
    write_rows(data, 'functies', [{'Rel. code': 'M2', 'Functie': 'Trainer Senioren'}])
    hours = rows(data, 'vrijwilligers_periode')
    hours[1]['Niet ingedeeld'] = '999'
    write_rows(data, 'vrijwilligers_periode', hours)
    ctx = context(data)
    result = propose(ctx)
    assert ids(result) == ['M1']
    assert ctx.signal_counts['DUTY_REMAINING_MISMATCH'] == 1
    assert next(c for c in result.controls if c.person_id == 'M2').status == 'niet betrouwbaar beoordeelbaar'
    regular = next(c for c in result.controls if c.person_id == 'M1')
    assert regular.status == 'overeenkomst'
    assert all(s.code != 'DUTY_REMAINING_MISMATCH' for s in regular.signals)
