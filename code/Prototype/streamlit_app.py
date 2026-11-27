from __future__ import annotations

from dvk.candidate_presenter import KICKOFF_PRIORITY_LABELS, priority_explanation

from datetime import date, datetime, time, timedelta
from hashlib import sha256
from itertools import groupby
from pathlib import Path
from uuid import uuid4

import sqlite3

import streamlit as st

from dvk.application_services import NoShowApplicationService, PlanningApplicationService, ProposalDecisionApplicationService
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.team_matchday import EMERGENCY_MATCHDAY_REASON
from dvk.application_version import active_application_version
from dvk.planning_source_presenter import planning_source_rows, skipped_team_matches_note
from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.new_planning import NewPlanningApplicationService
from dvk.no_show import NoShowEvent, TZ, season_id
from dvk.persistence import SQLiteDatabase
from dvk.persistence.schema_validation import SchemaValidationError
from dvk.planning_diagnostics import trace_planning
from dvk.planning import PlanningPeriod
from dvk.planning_session import PlanningCandidateSources, PlanningSessionApplicationService
from dvk.proposals import match_for_assessment
from dvk.planner_presenter import period_capacity
from dvk.security import Identity, Permission
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient, VrijwilligersFetchError
from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter, same_task_group, overlaps_service_date
from dvk.sportlink_config import SportlinkConfigError, load_sportlink_client_id
from dvk.sportlink_exports import (
    ExportFileError, default_export_directory, export_location_hint, save_export_directory,
)
from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.shift_catalog import load_shift_catalog
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from dvk.duty_control_presenter import EXPORTS, FILTERS, load_duty_dashboard, suggested_season, validate_season

DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")
MATCH_LABELS = {"no_match_context": "Geen wedstrijd", "no_match_that_day": "Geen wedstrijd", "home_match_overlaps_service": "Thuiswedstrijd overlapt", "home_match_same_day": "Thuiswedstrijd", "away_match_overlaps_service": "Uitwedstrijd overlapt", "away_match_same_day": "Uitwedstrijd"}
RULE_LABELS = {"previous_season_backlog_before_december": "Openstaande uren uit vorig seizoen meegewogen", "home_match_overlap": "Thuiswedstrijd sluit aan op dienst", "home_match_same_day": "Thuiswedstrijd op dezelfde dag", "away_match_emergency": "Uitwedstrijd meegewogen als noodoptie"}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


def _sportlink_booking_names(service, bindings, bookings):
    """Present original source names using the existing catalog overlap helpers.

    Source registrations remain separate, including repeated Afgeschermd names.
    This presentation does not change person deduplication or staffing totals.
    """
    code = next(binding.task_code for binding in bindings if binding.service.service_id == service.service_id)
    return tuple(b.volunteer_name for b in bookings
                 if same_task_group(b.task_code, code) and overlaps_service_date(b.starts_at, b.ends_at, service))


def _assignment_label(context, *, source_name=False) -> str:
    service_info = context.service
    person_name = ((getattr(context.assignment, "volunteer_name", None) if source_name else None)
                   or context.person_name or "Persoon onbekend")
    if service_info is None:
        return f"Datum/tijd en dienst onbekend — {person_name}"
    return f"{_datum_met_dag(service_info.starts_at)} {service_info.starts_at:%H:%M}–{service_info.ends_at:%H:%M} — {service_info.service_type or 'Dienst onbekend'} — {person_name}"


def _vriendelijke_wedstrijdcontext(value: str) -> str:
    return MATCH_LABELS.get(value, value.replace("_", " ").capitalize())


def _vriendelijke_waarom(proposal) -> str:
    details: list[str] = []
    if "temporary_planning_same_day_emergency" in proposal.uncertainties:
        details.append("Alleen nood-/uitwijkkandidaat: al tijdelijk ingepland op dezelfde dag")
    if proposal.previous_season_backlog > 0 and proposal.previous_season_considered:
        details.append(f"Nog {proposal.previous_season_backlog} openstaande uren uit vorig seizoen")
    for rule in proposal.applied_priority_rules:
        if rule in {"higher_current_E", "previous_season_backlog_before_december"}:
            continue
        label = KICKOFF_PRIORITY_LABELS.get(rule) or RULE_LABELS.get(rule)
        if label and label not in details:
            details.append(label)
    return "; ".join(details) if details else "—"


st.set_page_config(page_title="DVK — Digitaal Verenigingskantoor", page_icon="📋", layout="wide")
st.title("CKC Digitaal Verenigingskantoor (DVK)")
st.caption(active_application_version(__file__))


def _clear_period_widgets():
    for key in list(st.session_state):
        if key in {"selected_service_id", "candidate-context", "candidate-load-error",
                   "candidate-session-id", "initial-volunteer-error", "planning-review"} or key.startswith(
                ("proposal-run-", "candidate-detail-", "candidate-focus-", "candidate-pick-", "candidate-limit-")):
            del st.session_state[key]


def _planning_entry(database, identity, session):
    if session:
        with database.unit_of_work() as uow:
            sessions = PlanningSessionApplicationService(uow, identity)
            stored = sessions.candidate_sources(session.session_id)
            known = VolunteerPlanningApplicationService(uow, identity, session.catalog).source(session.period)[2]
        st.info(f"Bewaarde planning: {_period_label(session.period)}")
        st.caption(_source_label(stored.context if stored else None, known))
        if st.button("Bestaande planning hervatten", key="resume-planning"):
            st.session_state["planning-resumed"] = session.session_id
            st.session_state.pop("planning-close-request", None)
            st.rerun()

    if st.session_state.get("planning-mode") == "Aangepast":
        st.session_state["planning-mode"] = "Periode"
    mode = st.radio("Selectie", ("Dag", "Week", "Periode"), index=1, key="planning-mode", horizontal=True)
    selected = st.date_input("Week waarin datum valt" if mode == "Week" else "Vanaf",
                             value=datetime.now(TZ).date(), key="planning-from")
    if mode == "Week":
        monday = selected - timedelta(days=selected.weekday())
        period = PlanningPeriod(monday, monday + timedelta(days=6))
    elif mode == "Periode":
        if st.session_state.get("planning-until", selected) < selected:
            st.session_state["planning-until"] = selected + timedelta(days=6)
        until = st.date_input("Tot en met", value=selected + timedelta(days=6),
                              min_value=selected, key="planning-until")
        period = PlanningPeriod(selected, until)
    else:
        period = PlanningPeriod(selected, selected)
    st.markdown(f"**Roosterperiode: {_period_label(period)}**")
    suggested = suggested_season(period.start)
    source_period = st.text_input("Seizoen van Overzicht per periode", value=suggested,
                                 key=f"start-source-season-{suggested}",
                                 help="Controleer of dit seizoen overeenkomt met het lokale Sportlink-bestand.")

    start = st.button("Start nieuwe planning", key="activate-planning", type="primary")
    if session:
        if start:
            st.session_state["planning-close-request"] = (session.session_id, period, source_period)
        pending = st.session_state.get("planning-close-request")
        start = False
        if pending == (session.session_id, period, source_period):
            st.warning("De tijdelijke DVK-indelingen vervallen. Bevestig dat ze niet meer nodig zijn "
                       "en dat de noodzakelijke handmatige verwerking in Sportlink is afgehandeld.")
            start = st.button("Vervangen en nieuwe planning starten", key="confirm-close-planning")
            if st.button("Annuleren", key="cancel-close-planning"):
                st.session_state.pop("planning-close-request", None)
                st.rerun()
        elif pending is not None:
            st.session_state.pop("planning-close-request")
    if not start:
        return
    try:
        with database.unit_of_work() as uow:
            catalog = PlanningSessionApplicationService(uow, identity).catalog()
        with st.status("Bronnen voor de nieuwe planning laden…", expanded=True) as progress:
            started = NewPlanningApplicationService(database, identity).start(
                period=period, catalog=catalog, source_period=source_period,
                client_id=_sportlink_client_id, progress=progress.write,
                expected_session_id=session.session_id if session else None,
            )
    except ValueError as exc:
        st.error(str(exc))
        return
    _clear_period_widgets()
    st.session_state.pop("planning-close-request", None)
    st.session_state["planning-resumed"] = started.session_id
    st.session_state["candidate-season"] = source_period
    st.rerun()


def _period_label(period):
    return f"{period.start:%d-%m-%Y} t/m {period.end:%d-%m-%Y}"


def _source_label(context, known):
    if context and context.error is None:
        return "Broncontext beschikbaar" if known else "Kandidaatcontext beschikbaar · Sportlink-bezetting onbekend"
    return "Sportlink-bezetting beschikbaar · Kandidaatcontext onbekend" if known else "Broncontext en bezetting onbekend"


@trace_planning
def _render_planning():
    st.subheader("Ledendienst Planning")
    database = SQLiteDatabase(Path(__file__).with_name("dvk_v05.sqlite"))
    database.initialize()
    identity = _planner_identity()
    with database.unit_of_work() as uow:
        sessions = PlanningSessionApplicationService(uow, identity)
        active_session = sessions.current()
        if active_session and st.session_state.get("planning-resumed") == active_session.session_id:
            try:
                catalog = sessions.catalog()
            except ValueError as exc:
                st.error(str(exc))
                return
            _restore_candidate_sources(sessions, active_session.session_id)
    if not active_session or st.session_state.get("planning-resumed") != active_session.session_id:
        _planning_entry(database, identity, active_session)
        return
    period = active_session.period
    context_col, action_col = st.columns((4, 1))
    context_col.markdown(f"**Actieve planningsperiode** · {_period_label(period)}")
    if action_col.button("Andere planning", key="start-new-planning"):
        for key in ("planning-resumed", "planning-mode", "planning-from", "planning-until", "planning-review"):
            st.session_state.pop(key, None)
        st.rerun()
    if active_session.initial_load_pending:
        st.warning("De eerste automatische bronlading is niet volledig afgerond. "
                   "Ga naar Ledendiensten → Databronnen om ontbrekende bronnen alsnog te laden.")
    if active_session.source_revision and active_session.catalog is None:
        st.warning("Deze bewaarde sessie heeft nog geen ingelezen lokale catalogus. "
                   "Gebruik Dienstencatalogus opnieuw laden onder Databronnen.")
    source_summary = st.container()
    metrics = st.container()
    work_area = st.container()

    candidate_context = st.session_state.get("candidate-context")
    with database.unit_of_work() as uow:
        source_app = VolunteerPlanningApplicationService(uow, identity, catalog)
        success, attempt, known = source_app.source(period)
        source_bookings = source_app.bookings(period)
        bindings = source_app.service_bindings(period)
        services, needs, matches, statuses = source_app.planning_data(period)
        if candidate_context and candidate_context.error is None:
            matches = candidate_context.program.matches
        planning_app = PlanningApplicationService(identity, uow=uow)
        overview = planning_app.build_overview(period=period, services=services, staffing_needs=needs,
                                               matches=matches, source_statuses=statuses)
        needs = planning_app.staffing_needs(services=services, source_needs=needs)
        temporary_rows = planning_app.temporary_assignment_contexts(
            persons=candidate_context.source.persons if candidate_context else (),
        )
    load_error = st.session_state.get("candidate-load-error")
    _render_dashboard_sources(source_summary, candidate_context, known, period, success, attempt,
                              source_bookings, load_error)
    with metrics:
        _render_capacity(overview.services, known)
    if st.session_state.get("planning-review") == active_session.session_id:
        with work_area:
            st.subheader("Planning beoordelen")
            st.caption(_period_label(period))
            if st.button("Terug naar dashboard", key="close-planning-review"):
                st.session_state.pop("planning-review", None)
                st.rerun()
            st.dataframe([_roster_row(row, known) for row in overview.services], hide_index=True, height=280)
            st.markdown("#### Tijdelijke werkvoorraad")
            _render_temporary(database, identity, temporary_rows, "review")
            if message := st.session_state.pop("undo-planning-result", None):
                st.success(message)
        return

    state_key = (active_session.session_id, active_session.source_revision)
    if st.session_state.get("planner-revision") != state_key:
        for key in tuple(st.session_state):
            if key.startswith(("proposal-run-", "candidate-focus-", "candidate-pick-")):
                del st.session_state[key]
        if st.session_state.get("planner-revision", (None,))[0] != active_session.session_id:
            st.session_state.pop("selected_service_id", None)
        st.session_state["planner-revision"] = state_key

    with work_area:
        roster, candidates, fixtures = st.columns((36, 35, 29), gap="small")
    with roster:
        st.markdown("### Rooster Ledendiensten")
        selected_id = _render_roster(overview.services, known)
        service = next((item for item in services if item.service_id == selected_id), None)
        if service:
            st.markdown(f"**Geselecteerde dienst · {service.service_type}** · {_datum_met_dag(service.starts_at)}")
            st.caption(f"{service.starts_at:%H:%M}–{service.ends_at:%H:%M} · {service.location}")
            st.markdown("**Ingeroosterd in Sportlink**")
            if known:
                for name in _sportlink_booking_names(service, bindings, source_bookings) or ("Geen boekingen",):
                    st.write(name)
            else:
                st.write("Onbekend")
            st.markdown("**Tijdelijke DVK-indelingen**")
            _render_temporary(database, identity,
                              tuple(row for row in temporary_rows if row.service == service), "duty")
    if message := st.session_state.pop("undo-planning-result", None):
        roster.success(message)
    if message := st.session_state.pop("planner-assignment-result", None):
        roster.success(message)
    need = next((item for item in needs if item.service_id == selected_id), None)
    with candidates:
        result, focus, selected = _render_dashboard_candidates(
            database, identity, candidate_context, known, service, need,
        )
    with fixtures:
        _render_dashboard_fixtures(overview.matches, candidate_context, service, result, focus)
    _render_dashboard_actions(database, identity, active_session, service, need, selected)


def _render_dashboard_sources(container, candidate_context, known, period, success, attempt, source_bookings, load_error):
    with container:
        st.caption(_source_label(candidate_context, known))
        if not known:
            st.warning("De Sportlink-bezetting is onbekend voor deze periode. "
                       "Ga naar Databronnen om feitelijke inroosteringen handmatig op te halen.")
        if candidate_context and (candidate_context.historical_backlog is None
                                  or not candidate_context.historical_backlog.available):
            st.caption("Historische urenbron niet beschikbaar. Bekijk de brondetails.")
        if load_error or (candidate_context and candidate_context.error):
            st.error(load_error or candidate_context.error)
        if attempt and attempt["status"] == "Mislukt":
            st.warning("De laatste verversing is mislukt. Bekijk de brondetails.")
        if candidate_context and candidate_context.program and candidate_context.program.skipped_team_matches:
            st.warning(skipped_team_matches_note(candidate_context.program.skipped_team_matches))
        if candidate_context and candidate_context.error is None and any(
                signal.severity in {"ERROR", "WARNING"} for signal in candidate_context.source.signals):
            st.info("Bij enkele personen zijn bronafwijkingen gemeld. De overige kandidaten worden normaal beoordeeld.")
        with st.expander("Bronstatus bekijken"):
            st.dataframe(planning_source_rows(
                context=candidate_context, load_error=load_error,
                volunteer_success=success, volunteer_attempt=attempt, volunteer_matching=known,
                volunteer_error=st.session_state.get("initial-volunteer-error"),
            ), hide_index=True, height=280)
            st.button("Naar Databronnen", key="planner-sources", on_click=_navigate, args=("sources",))
            _render_candidate_diagnostics(candidate_context)
            _render_booking_diagnostics(known, period, success, attempt, source_bookings)


def _render_candidate_diagnostics(candidate_context):
    if candidate_context is not None:
        history = candidate_context.historical_backlog
        if history is None:
            st.warning("Historische urenbron is niet beschikbaar; historische achterstanden zijn niet meegewogen.")
        elif not history.available:
            st.warning(history.message)
        else:
            st.caption(history.message)
            if history.signals:
                st.warning("Historische urenbron bevat onbetrouwbare of niet gekoppelde regels. Betrokken kandidaten blijven beschikbaar; hun historische achterstand telt niet mee.")
                names = {p.person_id: p.name for p in candidate_context.source.persons}
                with st.expander("Aandachtspunten historische urenbron"):
                    st.table([{"Lid": names.get(s.record_key, "Geen gekoppeld actueel lid"),
                               "Melding": s.message} for s in history.signals])
        st.caption(f"Exportseizoen: {candidate_context.source_period}")
        st.caption("Ingelezen bestanden: " + ", ".join(candidate_context.source_files))
        st.caption("Bestanden handmatig gewijzigd? Kies Brongegevens vernieuwen in Databronnen.")
        stats = candidate_context.stats
        st.caption(f"Kandidaatbronnen geladen: {candidate_context.fetched_at:%d-%m-%Y %H:%M}. Programma API: {stats.calls} aanvraag, {stats.retries} herhalingen, {stats.failures} definitieve fouten.")
        if candidate_context.error:
            st.error(candidate_context.error)
        elif stats.retries:
            st.warning("Programma API tijdelijk instabiel; een herhaalpoging is geslaagd. De wedstrijdcontext is beschikbaar.")
        else:
            st.caption("Programma API: technisch geslaagd, ook als Sportlink geen wedstrijden aanlevert.")
        if candidate_context.program and candidate_context.program.skipped_team_matches:
            st.warning(skipped_team_matches_note(candidate_context.program.skipped_team_matches))
        if candidate_context.signal_counts:
            if candidate_context.error is None and any(signal.severity in {"ERROR", "WARNING"} for signal in candidate_context.source.signals):
                st.info("Kandidaatbronnen geladen. Bij enkele personen zijn bronafwijkingen gemeld. Personen met onvoldoende betrouwbare gegevens worden niet voorgesteld; de overige kandidaten worden normaal beoordeeld. U hoeft deze administratieve bijzonderheden niet eerst in Sportlink te corrigeren.")
            with st.expander("Bronmeldingen kandidaatcontext"):
                for code, count in candidate_context.signal_counts.items():
                    st.caption(f"{code}: {count}")
                st.dataframe([{"Bronbestand": d.filename, "Omschrijving": d.description,
                               "Relatiecode": d.person_id, "Naam": d.name,
                               "Bronregel": d.row_number, "Bronwaarden": dict(d.values)}
                              for d in candidate_context.diagnostic_details],
                             hide_index=True, height=300)


def _render_booking_diagnostics(source_matches, period, success, attempt, source_bookings):
    if not source_matches:
        st.warning("De Sportlink-bezetting is onbekend voor deze periode. "
                   "Ga naar Databronnen om feitelijke inroosteringen handmatig op te halen.")
    st.caption(f"Gekozen periode: {period.start:%d-%m-%Y} t/m {period.end:%d-%m-%Y}")
    if success:
        st.caption(f"Laatste geslaagde bronperiode: {success['start']} t/m {success['end']}; opgehaald: {success['fetched_at']}")
        st.write(success.get("status", "Geslaagd"))
        report = success.get("identity")
        if report is not None:
            st.write(f"Opgehaalde Sportlink-inroosteringen: {report['total']} · "
                     f"Afgeschermd: {report['shielded']} · "
                     f"Zonder betrouwbare unieke persoonskoppeling: {report['unlinked']}")
            if report["details"]:
                st.warning(f"Administratieve aandachtspunten voor {report['problem_names']} verschillende probleemnamen. "
                           "Aantallen boekingen per categorie kunnen overlappen.")
                for category in report["categories"]:
                    st.write(f"{category['problem']}: {category['bookings']} boeking(en), {category['names']} verschillende naam/namen.")
                with st.expander("Lokale administratieve aandachtspunten"):
                    st.table([{"Sportlink-naam": row["name"], "Probleem": row["problem"],
                               "Aantal boekingen": row["bookings"]} for row in report["details"]])
        if source_bookings:
            with st.expander("Sportlink-inroosteringen voor de gekozen periode"):
                st.table([{"Sportlink-naam": b.volunteer_name, "Datum": _datum_met_dag(b.starts_at),
                           "Tijd": f"{b.starts_at:%H:%M}–{b.ends_at:%H:%M}",
                           "Dienst": b.service.service_type if b.service else "Dienst onbekend",
                           "No-showregistratie mogelijk": "Ja" if b.can_register_no_show else "Nee"}
                          for b in source_bookings])
        st.caption("Aantal geplande diensten hieronder betreft catalogusmomenten bij het ophalen; aanvullende Sportlink-tijdvakken staan ook in de dienstentabel.")
        st.dataframe([{"Sportlink-taakcode": row["task_code"], "Taakomschrijving": row["description"],
                       "Aantal geplande diensten": row["services"], "Aantal Sportlink-inroosteringen": row["bookings"],
                       "Uitvraagstatus": row["status"]} for row in success["tasks"]], hide_index=True, height=190)
    else:
        st.info("Nog geen geslaagde Sportlink-synchronisatie.")
    if attempt and attempt["status"] == "Mislukt":
        st.error(f"Verversen mislukt voor {attempt['start']} t/m {attempt['end']} ({attempt['at']}): {attempt['message']}. Vorige bron en tijdelijke planning behouden.")
        st.write("Taakcodes en uitvraagstatus laatste poging: " + "; ".join(
            f"{row['task_code']} — {row['description']}: {row['status']}"
            for row in attempt["tasks"]))


def _render_capacity(rows, known):
    capacity = period_capacity(rows, known)
    metrics = (
        ("Diensten", capacity.services), ("Totale capaciteit", capacity.maximum),
        ("Ingeroosterd in Sportlink", capacity.sportlink),
        ("Tijdelijk ingedeeld in DVK", capacity.temporary), ("Vrije capaciteit", capacity.free),
    )
    for column, (label, value) in zip(st.columns(5), metrics):
        column.metric(label, value if value is not None else "Onbekend")
    if capacity.overbooked:
        st.warning("Eén of meer diensten zijn overbezet. De aantallen hierboven tonen de werkelijke bezetting en de vrije capaciteit per dienst.")
    elif capacity.sportlink is None:
        st.caption("Geen bezettingsverdeling beschikbaar zolang Sportlink-bezetting onbekend is.")
    elif capacity.percentages is None:
        st.caption("Geen bezettingsverdeling bij nul capaciteit.")
    else:
        labels = ("Sportlink", "Tijdelijk DVK", "Vrij")
        colors = ("#078137", "#0964e9", "#a65c00")
        counts = (capacity.sportlink, capacity.temporary, capacity.free)
        segments = "".join(
            f'<span style="flex:{count};background:{color};min-height:0.6rem"></span>'
            for count, color in zip(counts, colors) if count
        )
        st.markdown(f'<div aria-hidden="true" style="display:flex;overflow:hidden;border-radius:0.35rem">{segments}</div>',
                    unsafe_allow_html=True)
        st.caption(" · ".join(f"{label} {count} ({percent}%)"
                              for label, count, percent in zip(labels, counts, capacity.percentages)))


def _roster_row(row, known):
    return {"Datum": _datum_met_dag(row.starts_at),
            "Tijd": f"{row.starts_at:%H:%M}–{row.ends_at:%H:%M}", "Dienst": row.service_type,
            "Max.": row.maximum_staff, "SL": row.source_occupancy if known else "—",
            "DVK": row.temporary_occupancy, "Vrij": row.remaining_capacity if known else "—"}


def _render_roster(rows, known):
    only_free = st.checkbox("Alleen diensten met vrije capaciteit", key="planner-free-only", disabled=not known)
    st.caption("Max. = maximum · SL = Sportlink · DVK = tijdelijk · — = onbekend")
    selected = st.session_state.get("selected_service_id")
    visible = [row for row in rows if not (only_free and known) or row.remaining_capacity > 0]
    if not visible:
        st.info("Geen diensten met vrije capaciteit." if only_free and known else "Geen diensten in de gekozen periode.")
    if selected and all(row.service_id != selected for row in visible):
        st.caption("De geselecteerde dienst valt buiten het filter. De details blijven hieronder beschikbaar.")
    with st.container(height=310, border=True):
        for day, group in groupby(visible, key=lambda row: row.starts_at.date()):
            st.markdown(f"**{day:%d-%m-%Y}**")
            for row in group:
                fields = _roster_row(row, known)
                label = f"{fields['Tijd']} · {fields['Dienst']}"
                st.button(label, key=f"planner-duty-{row.service_id}",
                          type="primary" if selected == row.service_id else "secondary",
                          on_click=_select_dashboard_service, args=(row.service_id,))
                st.caption(f"Max. {fields['Max.']} · SL {fields['SL']} · DVK {fields['DVK']} · Vrij {fields['Vrij']}")
    return selected


def _select_dashboard_service(service_id):
    if st.session_state.get("selected_service_id") == service_id:
        st.session_state.pop("selected_service_id", None)
    else:
        st.session_state["selected_service_id"] = service_id


def _render_temporary(database, identity, rows, view):
    if not rows:
        st.caption("Geen tijdelijke DVK-indelingen.")
    for row in rows:
        st.write(_assignment_label(row) if view == "review" else row.person_name or "Persoon onbekend")
        if st.button("Ongedaan maken", key=f"planner-undo-{view}-{row.assignment.assignment_id}"):
            try:
                with database.unit_of_work() as uow:
                    ProposalDecisionApplicationService(identity, uow=uow).undo(row.assignment.assignment_id)
            except ValueError as exc:
                st.error(str(exc))
            else:
                for key in tuple(st.session_state):
                    if key.startswith("proposal-run-"):
                        del st.session_state[key]
                st.session_state["undo-planning-result"] = "Tijdelijke inroostering ongedaan gemaakt."
                st.rerun()


def _render_dashboard_candidates(database, identity, context, known, service, need):
    st.markdown("### Kandidaten")
    if not known or context is None or context.error:
        st.info("Kandidaten zijn beschikbaar na een geslaagde bronimport en gevalideerde Sportlink-bezetting voor deze periode.")
        return None, None, ()
    if service is None:
        st.info("Selecteer een dienst in het rooster.")
        return None, None, ()
    run_key = f"proposal-run-{service.service_id}"
    if run_key not in st.session_state:
        st.session_state[run_key] = str(uuid4())
    try:
        with database.unit_of_work() as uow:
            result = CandidateContextApplicationService(identity).propose(
                context, service=service, need=need, planning_app=PlanningApplicationService(identity, uow=uow),
                proposal_run_id=st.session_state[run_key],
            )
    except CandidateSourceError as exc:
        st.error(str(exc))
        return None, None, ()

    uncertain = sum(control.status == "niet betrouwbaar beoordeelbaar" for control in result.controls)
    if uncertain:
        st.warning(f"{uncertain} leden zijn niet betrouwbaar beoordeelbaar. Raadpleeg Taakplichtcontrole voor toelichting.")
    if any(control.status == "afwijking" for control in result.controls):
        st.warning("De Sportlink-urenverplichting wijkt bij enkele leden af van de DVK-afleiding. De Sportlink-urenpositie blijft leidend.")
    if not result.planned:
        st.info("Geen kandidaatvoorstellen: de maximumbezetting is bereikt." if not need.remaining_capacity
                else "Geen kandidaatvoorstellen: er zijn geen geschikte kandidaten voor deze dienst.")
        return result, None, ()

    cases = {case.person.person_id: case for case in result.cases}
    priorities = {row.person_id: row for row in result.priorities}
    proposals = [item.proposal for item in result.planned]
    stamp = sha256("\0".join(proposal.proposal_id for proposal in proposals).encode()).hexdigest()
    focus_key = f"candidate-focus-{stamp}"
    focus_id = st.session_state.get(focus_key)
    limit_key = f"candidate-limit-{stamp}"
    limit = st.session_state.get(limit_key, 24)
    picks = []
    st.caption(f"{need.remaining_capacity} vrije plaatsen · {len(proposals)} kandidaten")
    with st.container(height=400, border=True):
        for group, items in groupby(proposals[:limit], key=lambda p: _candidate_group(p, priorities[p.person_id])):
            st.markdown(f"**{group}**")
            for proposal in items:
                case = cases[proposal.person_id]
                focused = focus_id == proposal.proposal_id
                st.button(case.person.name, key=f"candidate-detail-{stamp}-{proposal.person_id}",
                          type="primary" if focused else "secondary",
                          on_click=_set_candidate_focus, args=(focus_key, proposal.proposal_id,))
                history = proposal.previous_season_backlog if proposal.previous_season_considered else "Onbekend"
                kickoff = proposal.match_starts_at.strftime("%H:%M") if proposal.match_starts_at else "—"
                st.caption(f"{proposal.team_id or 'Team onbekend'} · Open {proposal.E} u · Historie {history} · Aftrap {kickoff}")
                if st.checkbox(f"Indelen · {case.person.name}", key=f"candidate-pick-{stamp}-{proposal.person_id}"):
                    picks.append((proposal, case))
        if limit < len(proposals):
            st.button(f"Meer kandidaten ({len(proposals) - limit})", key=f"candidate-more-{stamp}",
                      on_click=_show_more_candidates, args=(limit_key, limit))
    focus = next((proposal for proposal in proposals if proposal.proposal_id == focus_id), None)
    return result, focus, tuple(picks)


def _show_more_candidates(key, limit):
    st.session_state[key] = limit + 24


def _set_candidate_focus(key, proposal_id):
    if st.session_state.get(key) == proposal_id:
        st.session_state.pop(key, None)
    else:
        st.session_state[key] = proposal_id


def _candidate_group(proposal, priority):
    if priority.match_preference != "other_weekend" and "temporary_planning_same_day_emergency" in proposal.uncertainties:
        return "Noodgroep · al op dezelfde dag ingedeeld"
    return {"youth_home": "Jeugd · thuis", "preferred": "Voorkeur · thuis",
            "neutral": "Noodgroep · zonder wedstrijd", "avoid": "Noodgroep · uit",
            "other_weekend": "Noodgroep · andere teamspeeldag"}[priority.match_preference]


def _render_dashboard_fixtures(matches, context, service, result, focus):
    st.markdown("### Wedstrijden")
    relevant = None
    if focus:
        assessment = next(item for item in result.assessments if item.person_id == focus.person_id)
        relevant = match_for_assessment(assessment, service, matches)
    if context is None or context.error:
        st.info("Wedstrijdcontext onbekend. Bekijk de bronstatus.")
    elif not matches:
        st.info("Sportlink heeft geen wedstrijden aangeleverd voor de gekozen periode.")
    else:
        day_matches = tuple(match for match in matches if service and match.starts_at.date() == service.starts_at.date())
        if service:
            _render_fixture_rows(day_matches, relevant)
        with st.expander(f"Volledig programma · {len(matches)} wedstrijden"):
            _render_fixture_rows(matches, relevant)
    st.markdown("### Kandidaatdetails")
    if focus is None:
        st.caption("Kies een kandidaat om de details te bekijken.")
        return
    case = next(case for case in result.cases if case.person.person_id == focus.person_id)
    priority = next(item for item in result.priorities if item.person_id == focus.person_id)
    st.markdown(f"**{case.person.name}**")
    st.caption(f"{focus.team_id or 'Team onbekend'} · {_candidate_group(focus, priority)} · Rang {focus.priority_rank}")
    st.write(f"Taakplicht {focus.A} u · Correctie {focus.B} u · Gerealiseerd {focus.C} u · Ingeroosterd {focus.D} u")
    st.write(f"Openstaand {focus.E} u · Historie " +
             (f"{focus.previous_season_backlog} u" if focus.previous_season_considered else "onbekend"))
    st.caption(_vriendelijke_wedstrijdcontext(focus.match_relation))
    if relevant:
        st.caption(f"Aftrap {_datum_met_dag(relevant.starts_at)} om {relevant.starts_at:%H:%M}")
    with st.expander("Selectietoelichting en bijzonderheden"):
        explanation = next(item for item in result.explanations if item.person_id == focus.person_id)
        st.write(explanation.why)
        st.caption("Geregistreerde Sportlink-taakplicht is leidend voor planning.")
        st.write(priority_explanation(focus))
        remarks = _vriendelijke_waarom(focus)
        if remarks != "—":
            st.caption(remarks)
        if EMERGENCY_MATCHDAY_REASON in focus.uncertainties:
            st.caption(EMERGENCY_MATCHDAY_REASON)


def _render_fixture_rows(matches, relevant):
    if not matches:
        st.caption("Geen wedstrijden op de dag van de geselecteerde dienst.")
    for match in matches:
        label = (f"{_datum_met_dag(match.starts_at)} {match.starts_at:%H:%M} · "
                 f"{match.team_id} · {'Thuis' if match.home_away.lower() == 'home' else 'Uit'}")
        if relevant and match.match_id == relevant.match_id:
            st.info(f"{label} · Wedstrijd van kandidaat")
        else:
            st.write(label)


def _render_dashboard_actions(database, identity, session, service, need, selected):
    problem = None
    if selected:
        with database.unit_of_work() as uow:
            problem = PlanningApplicationService(identity, uow=uow).selection_problem(
                person_ids=tuple(proposal.person_id for proposal, _ in selected), service=service, staffing_need=need,
            )
    with (getattr(st, "bottom", None) or st.container()):
        summary, assign, review = st.columns((2, 1, 1))
        duty = (f"{service.service_type} · {_datum_met_dag(service.starts_at)} "
                f"{service.starts_at:%H:%M}–{service.ends_at:%H:%M}") if service else "Geen dienst geselecteerd"
        selection = f"{len(selected)} geselecteerd"
        if len(selected) == 1:
            selection += f" · {selected[0][1].person.name}"
        summary.write(f"{duty} · {selection}")
        if problem:
            summary.warning(problem)
        if assign.button("Tijdelijk indelen", key="planner-assign", type="primary", disabled=not selected or bool(problem)):
            selections = tuple((proposal, case, f"UI-{uuid4()}") for proposal, case in selected)
            try:
                with database.unit_of_work() as uow:
                    ProposalDecisionApplicationService(identity, uow=uow).approve_many(
                        selections, service, need, expected_session=session,
                    )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.session_state[f"proposal-run-{service.service_id}"] = str(uuid4())
                names = ", ".join(case.person.name for _, case in selected)
                st.session_state["planner-assignment-result"] = f"Tijdelijk ingedeeld: {names}."
                st.rerun()
        if review.button("Planning beoordelen", key="planner-review"):
            st.session_state["planning-review"] = session.session_id
            st.rerun()


def _planner_identity():
    return Identity("demo-planner", "Demo planner", frozenset({
        Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL, Permission.MANAGE_NO_SHOWS,
    }))


def _render_volunteer_sync(database, identity, catalog, period, active_session,
                           temporary_rows, source_matches):
    sync_key = f"sync-volunteers-{active_session.session_id}-{active_session.source_revision}"
    with st.expander("Feitelijke Sportlink-inroosteringen ophalen"):
        st.caption(export_location_hint(("leden",)))
        st.caption("Leden.csv wordt bij synchroniseren uit de ingestelde exportmap gelezen voor persoonskoppeling.")
        st.caption("Alle actieve catalogustaakcodes worden opgehaald voor de gekozen periode. Bij succes vervallen alle tijdelijke indelingen. Boekingen zonder betrouwbare persoonskoppeling tellen mee in de bezetting; no-showregistratie is daarop niet beschikbaar.")
        replace_confirmed = False
        replacing = bool(active_session and (active_session.source_revision or temporary_rows))
        if replacing:
            replace_confirmed = st.checkbox("Ik bevestig dat tijdelijke indelingen mogen vervallen, niet langer nodig zijn en dat noodzakelijke handmatige verwerking in Sportlink is afgehandeld.", key=f"confirm-source-{sync_key}")
            st.caption("DVK controleert deze verklaring niet. Bij een mislukte synchronisatie blijft de bestaande planning behouden.")
        if not source_matches:
            st.warning("De actuele bezetting van de vrijwilligersdiensten is nog niet beschikbaar voor deze roosterperiode. Haal de roostergegevens op via de onderstaande knop om de bezetting en resterende behoefte te kunnen bepalen.")
        if st.button("Sportlink-inroosteringen synchroniseren", key=sync_key, disabled=replacing and not replace_confirmed):
            try:
                persons = LocalCsvSourceApplicationService().volunteer_persons()
                with database.unit_of_work(migrate_schema=False) as uow:
                    sessions = PlanningSessionApplicationService(uow, identity)
                    if sessions.current() != active_session:
                        raise ValueError("De planningssessie is gewijzigd. Controleer de periode en bevestig opnieuw.")
                    error = VolunteerPlanningApplicationService(uow, identity, catalog).synchronize(
                        period=period,
                        client=SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter()),
                        client_id=_sportlink_client_id,
                        persons=persons, imported_at=datetime.now().astimezone(),
                        confirmed=replace_confirmed, source_revision=active_session.source_revision)
                if error:
                    st.error(error)
                else:
                    st.session_state.pop("initial-volunteer-error", None)
                    st.session_state["sportlink-sync-result"] = "Sportlink-inroosteringen vernieuwd; tijdelijke DVK-planning vervangen."
                    st.rerun()
            except (ValueError, UnicodeError, VrijwilligersFetchError) as exc:
                st.error(str(exc))
        for signal in st.session_state.get("sportlink-booking-signals", ()):
            st.error(signal.message)
        sync_result = st.session_state.pop("sportlink-sync-result", None)
        if sync_result:
            st.success(sync_result)


def _set_candidate_sources(session_id, sources):
    if (st.session_state.get("candidate-session-id") != session_id
            or st.session_state.get("candidate-context") != sources.context):
        for key in list(st.session_state):
            if key.startswith(("proposal-run-", "candidate-detail-", "candidate-focus-", "candidate-pick-", "candidate-limit-")):
                del st.session_state[key]
    for key, value in (
        ("candidate-session-id", session_id),
        ("candidate-context", sources.context),
        ("candidate-load-error", sources.error),
        ("initial-volunteer-error", sources.initial_volunteer_error),
    ):
        if value is None:
            st.session_state.pop(key, None)
        else:
            st.session_state[key] = value


def _restore_candidate_sources(sessions, session_id):
    stored = sessions.candidate_sources(session_id)
    _set_candidate_sources(session_id if stored is not None else None, stored or PlanningCandidateSources())


def _render_candidate_refresh(database, identity, session):
    period = session.period
    current_context = st.session_state.get("candidate-context")
    season = current_context.source_period if current_context else suggested_season(period.start)
    st.caption("Controleer of de handmatig vernieuwde exports bij dit seizoen horen. Sportlink is de bron voor het wedstrijdprogramma.")
    source_period = st.text_input("Seizoen van Overzicht per periode", value=season, key="candidate-season")
    st.caption("Het historische urenbestand is optioneel. Controleer zelf of het bij het vorige seizoen hoort.")
    if st.button("Brongegevens vernieuwen", key="load-candidate-sources"):
        context = error = None
        try:
            with st.spinner("Lokale CSV-bronnen en wedstrijdprogramma laden…"):
                context = CandidateContextApplicationService(identity).load(
                    period=period, source_period=source_period,
                    client_id=_sportlink_client_id)
        except CandidateSourceError as exc:
            error = str(exc)
        sources = PlanningCandidateSources(context, error, st.session_state.get("initial-volunteer-error"))
        try:
            with database.unit_of_work(migrate_schema=False) as uow:
                PlanningSessionApplicationService(uow, identity).save_candidate_sources(session.session_id, sources)
        except ValueError as exc:
            st.error(str(exc))
            return
        _set_candidate_sources(session.session_id, sources)


def _render_catalog_reload(database, identity, active_session):
    period = active_session.period
    st.caption("Leest de roosterindeling opnieuw in. Na bevestiging begint een nieuwe planningssessie en vervalt de tijdelijke planning.")
    if st.button("Dienstencatalogus (roosterindeling) opnieuw laden", key="reload-catalog"):
        try:
            pending_catalog = load_shift_catalog()
            pending_catalog.bindings(period)
            st.session_state["catalog-reload-request"] = (pending_catalog, period,
                active_session.session_id if active_session else None)
        except ValueError as exc:
            st.error(str(exc))
    pending_reload = st.session_state.get("catalog-reload-request")
    if pending_reload and pending_reload[2] != active_session.session_id:
        st.session_state.pop("catalog-reload-request")
        st.warning("De planning is gewijzigd. Vraag catalogusherlaad opnieuw aan.")
        return
    if pending_reload:
        st.warning("Dienstencatalogus (roosterindeling) opnieuw laden beëindigt de huidige planningssessie en verwijdert alle tijdelijke indelingen. "
                   "Bevestig dat deze niet langer nodig zijn en noodzakelijke handmatige verwerking in Sportlink is afgehandeld. "
                   "Sportlink-bezetting moet daarna opnieuw worden opgehaald.")
        if st.button("Opnieuw laden bevestigen", key="confirm-reload-catalog"):
            try:
                with database.unit_of_work() as uow:
                    PlanningSessionApplicationService(uow, identity).reload_catalog(
                        pending_reload[1], confirmed=True, expected_session_id=pending_reload[2], catalog=pending_reload[0])
            except ValueError as exc:
                st.error(str(exc))
                return
            st.session_state.pop("catalog-reload-request", None)
            _clear_period_widgets()
            st.rerun()
        if st.button("Annuleren", key="cancel-reload-catalog"):
            st.session_state.pop("catalog-reload-request", None)
            st.rerun()
        return

def _render_sources():
    st.subheader("Databronnen")
    local = LocalCsvSourceApplicationService()
    try:
        directory = local.directory
        st.caption(f"Ingestelde exportmap: {directory}")
    except ExportFileError as exc:
        directory = None
        st.error(str(exc))

    with st.form("export-settings"):
        value = st.text_input("Sportlink-exportmap", value=str(directory) if directory else "")
        if st.form_submit_button("Exportmap opslaan"):
            try:
                saved = save_export_directory(value)
            except ExportFileError as exc:
                st.error(str(exc))
            else:
                st.session_state["export-settings-result"] = f"Exportmap opgeslagen: {saved}"
                st.rerun()
    if message := st.session_state.pop("export-settings-result", None):
        st.success(message)

    identity = _planner_identity()
    database = SQLiteDatabase(Path(__file__).with_name("dvk_v05.sqlite"))
    session = catalog = success = attempt = None
    matching = False
    temporary_rows = ()
    if database.path.is_file():
        try:
            with database.unit_of_work(migrate_schema=False) as uow:
                sessions = PlanningSessionApplicationService(uow, identity)
                session = sessions.current()
                if session:
                    _restore_candidate_sources(sessions, session.session_id)
                    success, attempt, matching = VolunteerPlanningApplicationService(
                        uow, identity, session.catalog).source(session.period)
                    try:
                        catalog = sessions.catalog()
                    except ValueError as exc:
                        st.warning(str(exc))
                    temporary_rows = PlanningApplicationService(identity, uow=uow).active_planning()
        except SchemaValidationError:
            session = None
            st.warning("De opgeslagen planning gebruikt een afwijkend databaseschema. Open Ledendienst Planning om dit te controleren.")
        except sqlite3.DatabaseError as exc:
            session = None
            _show_planning_storage_error(exc)

    if session:
        period = session.period
        st.caption(f"Actieve planningsperiode: {period.start:%d-%m-%Y} t/m {period.end:%d-%m-%Y}")
        with st.expander("Dienstencatalogus"):
            _render_catalog_reload(database, identity, session)
        _render_candidate_refresh(database, identity, session)
        if catalog is not None:
            _render_volunteer_sync(database, identity, catalog, period, session,
                                   temporary_rows, matching)
    else:
        st.info("Start een planningssessie via Ledendienst Planning om kandidaatbronnen of Sportlink-inroosteringen voor die periode op te halen.")

    same_context = session and st.session_state.get("candidate-session-id") == session.session_id
    load_error = st.session_state.get("candidate-load-error") if same_context else None
    if load_error:
        st.error(load_error)
    context = st.session_state.get("candidate-context") if same_context else None
    availability = local.availability() if directory is not None else {}
    volunteer_error = st.session_state.get("initial-volunteer-error") if same_context else None
    rows = planning_source_rows(context=context, load_error=load_error,
                                volunteer_success=success, volunteer_attempt=attempt,
                                volunteer_matching=matching, availability=availability,
                                volunteer_error=volunteer_error)
    st.markdown("### Lokale CSV-bronnen")
    st.caption("Beschikbaarheid hoort bij de ingestelde map. Inleesstatus toont het laatst bekende resultaat voor de actieve planning.")
    if context and context.source_directory and context.source_directory != directory:
        st.info(f"De getoonde inleesstatus komt uit de eerder gebruikte map: {context.source_directory}.")
    st.dataframe([row for row in rows if row["Type"] == "CSV"], hide_index=True, height=250)
    st.markdown("### API-bronnen")
    st.dataframe([row for row in rows if row["Type"] == "API"], hide_index=True, height=115)


def _render_no_show_management():
    from dvk.no_show import TZ, MANUAL_DECLARATION, registration_period
    from dvk.no_show_source import NoShowSourceApplicationService
    from dvk.no_show_presenter import person_labels, history_page, PAGE_SIZE
    st.markdown("### No-showmanagement")
    database = SQLiteDatabase(Path(__file__).with_name("dvk_v05.sqlite"))
    database.initialize()
    identity = Identity("demo-planner", "Demo planner", frozenset({Permission.MANAGE_NO_SHOWS}))
    now = datetime.now(TZ)
    mode = st.radio("Registratievorm", ("Sportlink", "Handmatig"), horizontal=True)
    persons, catalog = (), None
    try:
        persons = LocalCsvSourceApplicationService().volunteer_persons()
    except ValueError as exc:
        st.error(str(exc))
    try:
        catalog = load_shift_catalog()
    except ValueError as exc:
        st.error(str(exc))
    source = None
    if catalog is not None:
        source = NoShowSourceApplicationService(identity,
            SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter()),
            _sportlink_client_id, catalog, persons)
    context, selected, inputs = None, None, None
    if mode == "Sportlink":
        st.caption("Feitelijke Sportlink-inroosteringen; deze raadpleging verandert geen planning.")
        if st.button("Sportlink-diensten raadplegen", disabled=source is None or not persons):
            st.session_state.pop("ns-source", None)
            try:
                st.session_state["ns-source"] = source.consult(datetime.now(TZ))
            except (ValueError, VrijwilligersFetchError) as exc:
                st.error(str(exc))
        consulted = st.session_state.get("ns-source")
        if consulted:
            st.caption(f"Bron geraadpleegd: {consulted.fetched_at:%d-%m-%Y %H:%M}. Bij bevestiging wordt de gekozen taak opnieuw gecontroleerd.")
            with database.unit_of_work() as uow:
                choices = NoShowApplicationService(uow, identity).registration_choices(consulted.bookings)
            for signal in consulted.signals:
                st.warning(signal.message)
            if choices:
                labels = {b.assignment_id: f"{b.starts_at:%d-%m-%Y %H:%M %z}–{b.ends_at:%d-%m %H:%M %z} — {b.service.service_type} — {b.volunteer_name}" for b in choices}
                chosen = st.selectbox("Inroostering", tuple(labels), format_func=labels.get)
                selected = next(b for b in choices if b.assignment_id == chosen)
                context = selected
            else:
                st.info("Geen betrouwbare inroosteringen binnen de registratietermijn en vanaf dienstaanvang.")
    else:
        st.caption("Voor een oorspronkelijke Sportlink-indeling die inmiddels is verwijderd. Geen actuele boeking vereist.")
        members = {p.person_id: p for p in persons}
        member_labels = person_labels({pid: p.name for pid, p in members.items()})
        if members:
            person_id = st.selectbox("Persoon", tuple(member_labels), format_func=member_labels.get)
            definitions = {d.task_code: d for d in catalog.definitions} if catalog else {}
            task = st.selectbox("Oorspronkelijke dienst", (*definitions, "Andere dienst"),
                format_func=lambda code: definitions[code].service_type if code in definitions else code)
            other = task == "Andere dienst"
            description = st.text_input("Dienstomschrijving (verplicht)") if other else ""
            historical_code = st.text_input("Oorspronkelijke taakcode (optioneel, onbevestigd)") if other else task
            st.caption("Een No-show kan worden geregistreerd vanaf 14 kalenderdagen geleden tot en met vandaag, mits de dienst al is begonnen.")
            registration_window = registration_period(now)
            start_day = st.date_input("Begindatum", value=now.date(),
                                      min_value=registration_window.start, max_value=registration_window.end)
            start_time = st.time_input("Begintijd", value=time(10))
            end_day = st.date_input("Einddatum", value=now.date(),
                                    min_value=registration_window.start, max_value=registration_window.end)
            end_time = st.time_input("Eindtijd", value=time(12))
            location = st.text_input("Locatie (optioneel)")
            explanation = st.text_area("Toelichting (optioneel)")
            confirmed = st.checkbox(MANUAL_DECLARATION)
            inputs = dict(person_id=person_id, persons=persons, catalog=catalog,
                          task_code=historical_code, description=description,
                          start_day=start_day, start_time=start_time, end_day=end_day, end_time=end_time,
                          other=other, location=location, explanation=explanation, confirmed=confirmed)
            if confirmed:
                try:
                    with database.unit_of_work() as uow:
                        context = NoShowApplicationService(uow, identity).manual_context(**inputs)
                except ValueError as exc:
                    st.error(str(exc))
        else:
            st.info("Laad Leden.csv om een bekende persoon te selecteren.")
    acknowledged = ()
    if context is not None:
        with database.unit_of_work() as uow:
            exact, possible = NoShowApplicationService(uow, identity).duplicate_check(context)
        if exact:
            st.error("Voor deze inroostering is al een no-show geregistreerd.")
        if possible:
            st.warning("Mogelijk duplicaat: controleer de bestaande registraties.")
            st.dataframe([_no_show_history_row(e, None) for e in possible], hide_index=True, height=230)
            if st.checkbox("Ik heb deze mogelijke duplicaten gecontroleerd en wil doorgaan."):
                acknowledged = tuple(e.no_show_id for e in possible)
        with st.form("no-show-form"):
            submitted = st.form_submit_button("No-show bevestigen", type="primary", disabled=bool(exact))
        if submitted:
            try:
                with database.unit_of_work() as uow:
                    app = NoShowApplicationService(uow, identity)
                    if mode == "Handmatig":
                        # Re-read members and catalog at actual confirmation.
                        inputs["persons"] = LocalCsvSourceApplicationService().volunteer_persons()
                        if not inputs["other"]:
                            inputs["catalog"] = load_shift_catalog()
                        assessment = app.register_manual(**inputs, acknowledged_possible=acknowledged)
                    else:
                        assessment = app.register_booking(selected, source=source, acknowledged_possible=acknowledged)
                st.session_state["last-no-show"] = assessment
            except (ValueError, VrijwilligersFetchError) as exc:
                st.error(str(exc))
    assessment = st.session_state.pop("last-no-show", None)
    if assessment:
        if assessment.counter == 1:
            st.warning("Eerste no-show: waarschuwing. Betrokkene moet zelf een vervangende inzet regelen.")
        else:
            card = "gele kaart" if assessment.card == "yellow" else "rode kaart"
            follow_up = " Bestuurlijke vervolgactie is vereist." if assessment.board_follow_up else ""
            st.warning(f"No-show {assessment.counter}: {card}, €{assessment.fine_eur} boete en {assessment.suspension_matches} wedstrijd(en) schorsing.{follow_up}")
        st.info("Communicatie hierover is vereist. Het DVK registreert dit; verzending en uitvoering zijn niet geautomatiseerd in v0.5.")
    st.markdown("#### Seizoensoverzicht en historie")
    with database.unit_of_work() as uow:
        app = NoShowApplicationService(uow, identity)
        history = app.history()
    seasons = sorted({season_id(now.date()), *(e.season for e, r in history)}, reverse=True)
    season = st.selectbox("Seizoen", seasons)
    historical_names = {e.person_id: e.context.person_name for e, r in history if e.context}
    historical_names.update({p.person_id: p.name for p in persons})
    filter_labels = {None: "Alle personen", **person_labels(historical_names)}
    person_filter = st.selectbox("Persoonfilter", tuple(filter_labels), format_func=filter_labels.get)
    status = st.selectbox("Status", ("Alle", "Actief", "Ingetrokken"))
    with database.unit_of_work() as uow:
        app = NoShowApplicationService(uow, identity)
        filtered = app.history(season=season, person_id=person_filter, status=None if status == "Alle" else status)
        revocable_rows = app.revocable_no_shows()
    filters = (season, person_filter, status)
    if st.session_state.get("no-show-history-filters") != filters:
        st.session_state["no-show-history-page"] = 1
        st.session_state["no-show-history-filters"] = filters
        st.session_state.pop("no-show-history-detail", None)
    page = history_page(filtered, st.session_state.get("no-show-history-page", 1))
    previous, following = st.columns(2)
    go_back = previous.button("Vorige pagina", key="no-show-history-previous", disabled=page.number == 1)
    go_forward = following.button("Volgende pagina", key="no-show-history-next", disabled=page.number == page.count)
    if go_back or go_forward:
        st.session_state["no-show-history-page"] = page.number + (1 if go_forward else -1)
        st.session_state.pop("no-show-history-detail", None)
        st.rerun()
    st.session_state["no-show-history-page"] = page.number
    st.caption(f"Pagina {page.number} van {page.count} · {page.total} registraties")
    st.dataframe([_no_show_history_row(e, r) for e, r in page.rows], hide_index=True, use_container_width=True, height=360)
    if page.rows:
        detail_labels = {e.no_show_id: f"{i}. {e.recorded_at:%d-%m-%Y %H:%M:%S} — {e.context.person_name or 'Persoon onbekend'} — {e.context.service.service_type}"
                         for i, (e, r) in enumerate(page.rows, (page.number - 1) * PAGE_SIZE + 1)}
        if st.session_state.get("no-show-history-detail") not in detail_labels:
            st.session_state.pop("no-show-history-detail", None)
        selected_detail = st.selectbox("Details van No-show", tuple(detail_labels), format_func=detail_labels.get,
                                       key="no-show-history-detail")
        event, revocation = next(row for row in page.rows if row[0].no_show_id == selected_detail)
        context = event.context
        with st.container(border=True):
            st.markdown("##### Details geselecteerde No-show")
            st.write(f"Persoon: {context.person_name or 'Persoon onbekend'}")
            st.write(f"Dienst: {context.service.service_type or 'Dienst onbekend'}")
            if context.task_code:
                st.write(f"Taakcode: {context.task_code}")
            st.write(f"Begin: {context.starts_at:%d-%m-%Y %H:%M %z}")
            st.write(f"Einde: {context.ends_at:%d-%m-%Y %H:%M %z}")
            if context.location:
                st.write(f"Locatie: {context.location}")
            actor = identity.display_name if event.recorded_by == identity.subject_id else event.recorded_by
            st.write(f"Registratie: {event.recorded_at:%d-%m-%Y %H:%M:%S %z} door {actor}; {event.registration_mode}.")
            if event.manual:
                st.write(event.manual.declaration)
                st.write("Verklaring bevestigd: Ja")
                st.write("Taakidentiteit: " + ("catalogus" if event.manual.task_identity_verified else "onbevestigd"))
                if event.manual.explanation:
                    st.write(event.manual.explanation)
            elif event.booking and event.booking.provenance:
                provenance = event.booking.provenance
                st.write(f"Bron: {provenance.source_system} — {provenance.source_dataset}")
                st.write(f"Bron geraadpleegd: {provenance.imported_at:%d-%m-%Y %H:%M:%S %z}")
                st.write(f"Oorspronkelijke bronnaam: {event.booking.volunteer_name}")
            if revocation:
                actor = identity.display_name if revocation.revoked_by == identity.subject_id else revocation.revoked_by
                st.write(f"Intrekking: {revocation.revoked_at:%d-%m-%Y %H:%M:%S %z} door {actor}: {revocation.reason}")
            with database.unit_of_work() as uow:
                current = NoShowApplicationService(uow, identity).current_state(event.person_id, event.season)
            st.write(f"Actuele seizoensteller: {current.counter}")
            if current.assessment:
                sanction = current.assessment
                card = {None: "waarschuwing", "yellow": "gele kaart", "red": "rode kaart"}[sanction.card]
                st.write(f"Actuele sanctie: {card}; boete €{sanction.fine_eur}; schorsing {sanction.suspension_matches} wedstrijd(en).")
                if sanction.board_follow_up:
                    st.write("Bestuurlijke vervolgactie is vereist.")
            else:
                st.write("Actuele sanctie: geen actieve No-shows in dit seizoen.")
    else:
        st.info("Geen No-shows binnen deze filters.")
    visible_ids = {e.no_show_id for e, r in filtered if r is None}
    revocable_rows = tuple(row for row in revocable_rows if row.no_show.no_show_id in visible_ids)
    if st.session_state.pop("clear-no-show-revocation-reason", False):
        st.session_state["no-show-revocation-reason"] = ""
    if revocable_rows:
        labels = {row.no_show.no_show_id: _assignment_label(row.assignment) for row in revocable_rows}
        with st.form("no-show-revocation-form"):
            identifier = st.selectbox("No-show intrekken", tuple(labels), format_func=labels.get, key="no-show-revocation-id")
            reason = st.text_area("Toelichting voor intrekking (verplicht)", key="no-show-revocation-reason")
            revoke = st.form_submit_button("Intrekking bevestigen", type="primary")
        if revoke:
            try:
                with database.unit_of_work() as uow:
                    app = NoShowApplicationService(uow, identity)
                    app.revoke(identifier, reason=reason, revoked_at=datetime.now(TZ))
                    row = next(row for row in revocable_rows if row.no_show.no_show_id == identifier)
                    state = app.current_state(row.no_show.person_id, row.no_show.season)
                person_label = row.assignment.person_name or "dit lid (naam onbekend)"
                st.session_state["no-show-revocation-result"] = f"No-show ingetrokken. Actuele no-showteller voor {person_label} in seizoen {state.season}: {state.counter}."
                st.session_state["clear-no-show-revocation-reason"] = True
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    if result := st.session_state.pop("no-show-revocation-result", None):
        st.success(result)


def _no_show_history_row(event, revocation):
    context = event.context
    return {"Geregistreerd": event.recorded_at.strftime("%d-%m-%Y %H:%M:%S %z"),
            "Persoon": context.person_name or "Persoon onbekend", "Dienst": context.service.service_type,
            "Begin": context.starts_at.strftime("%d-%m-%Y %H:%M %z"),
            "Einde": context.ends_at.strftime("%d-%m-%Y %H:%M %z"), "Locatie": context.location or "—",
            "Registratievorm": event.registration_mode, "Status": "Ingetrokken" if revocation else "Actief"}


def _render_planning_screen(render=_render_planning):
    try:
        render()
    except sqlite3.DatabaseError as exc:
        _show_planning_storage_error(exc)


def _show_planning_storage_error(exc):
    # Known schema/storage failures may block planning, but never the CSV control.
    # Unknown SQL errors and programming errors must remain visible to developers.
    storage_codes = {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED, sqlite3.SQLITE_READONLY,
                     sqlite3.SQLITE_CANTOPEN, sqlite3.SQLITE_IOERR, sqlite3.SQLITE_FULL,
                     sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB}
    missing_schema = isinstance(exc, sqlite3.OperationalError) and str(exc).startswith(
        ("no such table:", "no such column:"))
    if not missing_schema and (getattr(exc, "sqlite_errorcode", 0) & 0xff) not in storage_codes:
        raise exc
    st.error("De planning en no-showregistratie zijn niet beschikbaar door een databaseprobleem. "
             "Laat de database afzonderlijk controleren. Open Taakplichtcontrole via de zijbalk; die blijft beschikbaar.")

# Only retain scalar input values. Uploads and action/selection widgets follow
# Streamlit's normal cleanup when their screen is no longer rendered.
for _key in ("planning-mode", "planning-from", "planning-until",
             "duty-control-date", "duty-control-period", "duty-control-filter", "candidate-season"):
    if _key in st.session_state:
        st.session_state[_key] = st.session_state[_key]


def _navigate(screen):
    st.session_state["dvk-screen"] = screen


def _render_navigation():
    with st.sidebar:
        st.header("DVK")
        st.button("Startscherm", key="nav-home", on_click=_navigate, args=("home",))
        st.subheader("Ledendiensten & Vrijwilligersbeleid")
        st.button("Ledendienst Planning", key="nav-planning", on_click=_navigate, args=("planning",))
        st.button("Databronnen", key="nav-sources", on_click=_navigate, args=("sources",))
        st.button("No-showmanagement", key="nav-no-shows", on_click=_navigate, args=("no-shows",))
        st.button("Taakplichtcontrole", key="nav-control", on_click=_navigate, args=("control",))
        st.button("Rooster Generator — extern, nog niet geïntegreerd", disabled=True, key="nav-rooster")
        st.subheader("Overige werkgebieden")
        for name in ("Ledenadministratie", "Wedstrijdsecretariaat", "Kledingadministratie"):
            st.button(f"{name} — niet beschikbaar", disabled=True, key=f"nav-{name}")
        st.subheader("DVK Beheer")
        for name in ("Toegangsbeheer", "Tabelonderhoud"):
            st.button(f"{name} — niet beschikbaar", disabled=True, key=f"nav-{name}")


def _render_home():
    st.subheader("Welkom bij het Digitaal Verenigingskantoor")
    st.write("Kies een scherm via de zijbalk. Via Startscherm keer je altijd terug naar dit overzicht.")
    st.markdown("### Ledendiensten & Vrijwilligersbeleid")
    st.write("**Ledendienst Planning** — beschikbaar als prototype v0.5, in ontwikkeling.")
    st.write("**Databronnen** — lokale exportmap instellen en bronnen vernieuwen.")
    st.write("**No-showmanagement** — zelfstandig registreren, historie en intrekken.")
    st.write("**Taakplichtcontrole** — beschikbare read-only functie binnen Ledendienst Planning.")
    st.write("**Rooster Generator** — operationele externe toepassing, nog niet geïntegreerd in DVK.")
    st.markdown("### Overige werkgebieden")
    st.write("**Ledenadministratie** — toekomstig, niet beschikbaar.")
    st.write("**Wedstrijdsecretariaat** — toekomstig, niet beschikbaar.")
    st.write("**Kledingadministratie** — toekomstig, niet beschikbaar.")
    st.markdown("### DVK Beheer")
    st.write("**Toegangsbeheer** — toekomstig, niet beschikbaar.")
    st.write("**Tabelonderhoud** — toekomstig, niet beschikbaar.")
    st.info("CSV-bronnen komen uit de exportmap die is ingesteld in Databronnen. Gebruik Brongegevens vernieuwen nadat u exports heeft vervangen. Peildatum, seizoen en filter blijven binnen deze sessie behouden.")


def _render_duty_control():
    st.markdown("### Taakplichtcontrole — read-only")
    control_as_of = st.date_input("Peildatum taakplichtcontrole", value=date.today(), key="duty-control-date")
    control_period = st.text_input("Periode / seizoen van Overzicht per periode",
                                   value=suggested_season(control_as_of), key="duty-control-period",
                                   placeholder="2026-2027",
                                   help="Gebruik JJJJ-JJJJ, bijvoorbeeld 2026-2027. Het seizoen loopt van 1 juli tot 30 juni. Controleer of dit overeenkomt met de geladen export; je kunt het voorstel aanpassen.")
    st.caption("Lokale Sportlink-exports voor menselijke controle. Een afwijking vraagt om herbeoordeling; het dashboard corrigeert niets. Bestanden worden alleen in geheugen verwerkt.")
    st.caption(export_location_hint(EXPORTS))
    control_filter = st.radio("Toon taakplichtcontrole", tuple(FILTERS), horizontal=True, key="duty-control-filter")
    refresh = st.button("Brongegevens vernieuwen", key="refresh-duty-sources")
    load_key = (control_as_of, control_period)
    try:
        validated_period = validate_season(control_period)
    except ValueError as exc:
        validated_period = None
        st.session_state.pop("local-duty-control", None)
        st.session_state.pop("duty-load-key", None)
        st.error(str(exc))
    if validated_period is not None:
        if refresh or st.session_state.get("duty-load-key") != load_key:
            st.session_state["duty-load-key"] = load_key
            st.session_state.pop("local-duty-control", None)
            st.session_state.pop("duty-load-error", None)
            try:
                st.session_state["local-duty-control"] = LocalCsvSourceApplicationService().duty_control(
                    as_of=control_as_of, source_period=validated_period)
            except ValueError as exc:
                st.session_state["duty-load-error"] = str(exc)
        if st.session_state.get("duty-load-error"):
            st.error(st.session_state["duty-load-error"])
        loaded_control = st.session_state.get("local-duty-control")
        if loaded_control is not None:
            dashboard = loaded_control.dashboard
            try:
                current_directory = default_export_directory()
            except ExportFileError:
                current_directory = None
            loaded_directory = loaded_control.sources.directory
            if loaded_directory and loaded_directory != current_directory:
                st.info(f"De getoonde gegevens komen uit de eerder gebruikte map: {loaded_directory}. Kies Brongegevens vernieuwen om de ingestelde map te gebruiken.")
            st.caption("Ingelezen bestanden: " + ", ".join(loaded_control.sources.filenames))
            st.caption(f"Bronnen laatst geladen: {loaded_control.sources.loaded_at:%d-%m-%Y %H:%M:%S}. Na vervangen van exports: Brongegevens vernieuwen.")
            st.markdown("#### Selectieverantwoording")
            for column, (label, count) in zip(st.columns(4), dashboard.selection_counts.items()):
                column.metric(label, count)
            with st.expander("Redenen voor uitsluiting en selectieproblemen"):
                selection_rows = [{"Lid": r.member, "Relatiecode": r.person_id,
                                   "Selectie": r.outcome, "Reden": r.reason}
                                  for r in dashboard.selection if r.outcome != "Meegenomen"]
                st.caption(f"{len(selection_rows)} records getoond. Ledenregels zonder relatiecode blijven in de brondiagnose.")
                st.dataframe(selection_rows, hide_index=True, use_container_width=True, height=360)
            st.markdown("#### Taakplichtbeoordeling")
            for column, (label, count) in zip(st.columns(4), dashboard.counts.items()):
                column.metric(label.capitalize(), count)
            st.caption(f"Peildatum: {control_as_of:%d-%m-%Y} · Periode: {control_period}")
            control_rows = [{"Lid": r.member, "DVK verwachte A": r.expected, "Waarom": r.why,
                             "Sportlink-A": r.registered, "Controlestatus": r.status,
                             "Relatiecode": r.person_id} for r in dashboard.filtered(control_filter)]
            if control_rows:
                st.caption(f"{len(control_rows)} van {len(dashboard.rows)} beoordeelde leden getoond.")
                st.dataframe(control_rows, hide_index=True, use_container_width=True, height=360)
            else:
                st.info("Geen leden binnen dit filter.")
            control_names = {p.person_id: p.name or "Naam onbekend" for p in dashboard.source.persons}
            family_details = [{"Beoordeeld lid": r.member, "Vergelijking met": control_names.get(d.compared_person_id, "—"),
                               "Gegevens van": d.subject, "Betrokken lid": d.involved_member,
                               "Criterium": d.criterion, "Oorzaak": d.issue, "Toelichting": d.explanation}
                              for r in dashboard.filtered(control_filter) for d in r.family_diagnostics]
            if family_details:
                with st.expander("Nadere uitleg bij onvoldoende gezinsgegevens"):
                    st.caption(f"{len(family_details)} oorzaken binnen het gekozen filter. Deze uitleg verandert de beoordeling niet.")
                    st.dataframe(family_details, hide_index=True, use_container_width=True, height=360)
            with st.expander("Bron- en controlediagnose"):
                st.caption("Relatiecode is de koppelsleutel. Bronregels die niet gekoppeld of verwerkt konden worden blijven hier zichtbaar.")
                st.caption(f"{len(dashboard.source.signals)} diagnosemeldingen getoond.")
                st.dataframe([{"Bron": s.dataset, "Ernst": s.severity, "Code": s.code,
                               "Bronreferentie": s.record_key, "Melding": s.message}
                              for s in dashboard.source.signals], hide_index=True, use_container_width=True, height=360)



try:
    _sportlink_client_id = load_sportlink_client_id()
except SportlinkConfigError as exc:
    _sportlink_client_id = ""
    st.error(str(exc))

_render_navigation()
_screen = st.session_state.get("dvk-screen", "home")
if _screen == "planning":
    _render_planning_screen()
elif _screen == "sources":
    _render_sources()
elif _screen == "no-shows":
    _render_planning_screen(_render_no_show_management)
elif _screen == "control":
    _render_duty_control()
else:
    _render_home()
