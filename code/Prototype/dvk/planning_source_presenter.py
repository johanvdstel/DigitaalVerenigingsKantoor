"""BL-24: existing source evidence; no fetching, storage or planning policy."""
from datetime import datetime
from .sportlink_exports import EXPORT_FILENAMES
from .historical_backlog import HISTORICAL_FILENAME


def _time(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime('%d-%m-%Y %H:%M') if value else 'onbekend'


def planning_source_rows(*, context=None, load_error=None, volunteer_success=None,
                         volunteer_attempt=None, volunteer_matching=False, demo=False):
    rows = []
    def add(name, kind, moment, status, usable, note=''):
        rows.append({'Databron': name, 'Type': kind, 'Laatst ingelezen / opgehaald': _time(moment),
                     'Status': status, 'Bruikbaarheid': usable, 'Toelichting': note})
    for dataset, filename in EXPORT_FILENAMES.items():
        loaded = context is not None and filename in context.source_files
        signals = tuple(s for s in context.source.signals if s.dataset == dataset) if loaded else ()
        add(filename, 'CSV', context.csv_loaded_at if loaded else None,
            'Ingelezen' if loaded else 'Niet geladen',
            'Bronmeldingen; zie datakwaliteit' if signals else ('Beschikbaar' if loaded else 'Onbekend'),
            '; '.join(sorted({s.message for s in signals})) if loaded else
            (load_error or 'Nog niet ingelezen; beschikbaarheid niet vastgesteld.'))
    history = context.historical_backlog if context else None
    add(HISTORICAL_FILENAME, 'CSV (optioneel)', history.loaded_at if history else None,
        ('Ingelezen' if history.available else 'Niet beschikbaar / onbruikbaar') if history else 'Niet geladen',
        ('Deels bruikbaar; zie bronmeldingen' if history.signals else 'Beschikbaar')
        if history and history.available else 'Historie niet meegewogen; planning blijft bruikbaar',
        history.message if history else 'Optioneel. Planner borgt het juiste vorige seizoen; bronstatus onbekend.')
    success = volunteer_success
    failed = volunteer_attempt and volunteer_attempt.get('status') == 'Mislukt'
    total = (success.get('identity') or {}).get('total') if success else None
    note = f'Aangeleverde inroosteringen: {total}.' if total is not None else 'Aantal aangeleverde inroosteringen onbekend.'
    if failed:
        note += ' Laatste verversing mislukt: ' + volunteer_attempt.get('message', '') + '. Vorige bron behouden.'
    if success:
        note += f" Bronperiode: {success['start']} t/m {success['end']}."
    add('Sportlink Vrijwilligers', 'API', success.get('fetched_at') if success else None,
        'Laatste verversing mislukt' if failed else ('Technisch geslaagd' if success else 'Niet opgehaald'),
        'Gevalideerd voor gekozen periode' if volunteer_matching else 'Geen gevalideerde bron voor gekozen periode', note)
    program = context.program if context else None
    if program is None:
        add('Sportlink Programma', 'API', None, 'Aanvraag mislukt' if context else 'Niet opgehaald',
            'Wedstrijdcontext onbekend', context.error if context else 'Nog geen ophaalresultaat beschikbaar.')
    else:
        # Raw result stays inspectable even when operational team links are invalid.
        count = len(program.program.matches)
        note = f'Operationele wedstrijden in ontvangen bron: {count}.'
        if not count:
            note += ' Technisch geslaagd; geen operationele wedstrijden aangeleverd.'
        note += f' Aanvragen: {context.stats.calls}; herhalingen: {context.stats.retries}; definitieve fouten: {context.stats.failures}.'
        if context.error:
            note += ' ' + context.error
        add('Sportlink Programma', 'API', context.fetched_at, 'Technisch geslaagd',
            'Niet bruikbaar; zie bronmeldingen' if context.error else 'Beschikbaar', note)
    if demo:
        for row in rows:
            row.update({'Laatst ingelezen / opgehaald': 'onbekend', 'Status': 'Demonstratie',
                        'Bruikbaarheid': 'Synthetische planning', 'Toelichting': 'Demonstratie toont geen actuele bronstatus.'})
    return rows
