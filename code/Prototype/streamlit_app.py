from __future__ import annotations

from dvk.candidate_presenter import priority_explanation

from datetime import date, datetime, time, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import inspect
import sqlite3

import pandas as pd
import streamlit as st

from dvk.application_services import NoShowApplicationService, PlanningApplicationService, ProposalDecisionApplicationService
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.team_matchday import EMERGENCY_MATCHDAY_REASON
from dvk.application_version import active_application_version
from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.no_show import NoShowEvent, season_id
from dvk.persistence import SQLiteDatabase
from dvk.planning_diagnostics import trace_planning
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.planning_session import PlanningSessionApplicationService
from dvk.proposal_planning import plan_proposals
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY
from dvk.demo_data_v05 import demo_candidate_cases, demo_previous_season_backlog, demo_team_memberships, demo_planning_data
from dvk.workstream_model import DutyService, Match, TeamMembership
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient, VrijwilligersFetchError
from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter, ServiceBinding, same_task_group, overlaps_service_date
from dvk.sportlink_exports import export_location_hint
from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.shift_catalog import load_shift_catalog
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from dvk.duty_control_presenter import EXPORTS, FILTERS, load_duty_dashboard, suggested_season, validate_season
import os

DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")
MATCH_LABELS = {"no_match_context": "Geen wedstrijd", "no_match_that_day": "Geen wedstrijd", "home_match_overlaps_service": "Thuiswedstrijd overlapt", "home_match_same_day": "Thuiswedstrijd", "away_match_overlaps_service": "Uitwedstrijd overlapt", "away_match_same_day": "Uitwedstrijd"}
RULE_LABELS = {"previous_season_backlog_before_december": "Openstaande uren uit vorig seizoen meegewogen", "home_match_overlap": "Thuiswedstrijd sluit aan op dienst", "home_match_same_day": "Thuiswedstrijd op dezelfde dag", "away_match_emergency": "Uitwedstrijd meegewogen als noodoptie"}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


def _sportlink_names(service, bindings, bookings):
    """Present original source names using the existing catalog overlap helpers.

    Source registrations remain separate, including repeated Afgeschermd names.
    This presentation does not change person deduplication or staffing totals.
    """
    code = next(binding.task_code for binding in bindings if binding.service.service_id == service.service_id)
    return ", ".join(b.volunteer_name for b in bookings
                     if same_task_group(b.task_code, code) and overlaps_service_date(b.starts_at, b.ends_at, service)) or "geen namen"


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
        label = RULE_LABELS.get(rule)
        if label and label not in details:
            details.append(label)
    return "; ".join(details) if details else "—"


def _demo_data(start: date):
    return demo_planning_data(start)

def _demo_proposals(service: DutyService, need: StaffingNeed, matches: tuple[Match, ...], *, planning_app, proposal_run_id: str | None = None):
    cases = demo_candidate_cases()
    memberships = demo_team_memberships(service, cases)
    assessments = planning_app.assess_candidates(cases=cases, service=service, team_memberships=memberships, matches=matches, today=TODAY)
    eligible = tuple(a for a in assessments if a.eligible)
    priorities = prioritize_candidates(eligible, cases, service.starts_at.date(), previous_season_backlog=demo_previous_season_backlog())
    by_person = {p.person_id: p for p in priorities}
    proposals = tuple(create_assignment_proposal(f"DEMO-{service.service_id}-{case.person.person_id}-{proposal_run_id or uuid4()}", service, case, next(a for a in eligible if a.person_id == case.person.person_id), by_person[case.person.person_id], matches) for case in cases if case.person.person_id in by_person)
    return cases, plan_proposals(proposals, need, offer_all=True)

st.set_page_config(page_title="DVK — Digitaal Verenigingskantoor", page_icon="📋", layout="wide")
st.title("CKC Digitaal Verenigingskantoor (DVK)")
st.caption(active_application_version(__file__))


def _cancel_period_change():
    for key, value in st.session_state["planning-accepted-inputs"].items():
        st.session_state[key] = value


def _clear_period_widgets():
    for key in list(st.session_state):
        if key in {"services_editor", "selected_service_id", "candidate-context", "candidate-load-key", "candidate-load-error"} or key.startswith(
                ("proposal-run-", "confirmed-", "pick-", "services_editor-", "service-choice-", "candidate-table-", "candidate-detail-")):
            del st.session_state[key]


def _table_column_options(factory, *, pinned=False, alignment=None):
    """Use optional native features only when the installed version exposes them."""
    parameters = inspect.signature(factory).parameters
    options = {}
    if "pinned" in parameters:
        options["pinned"] = pinned
    if "alignment" in parameters and alignment is not None:
        options["alignment"] = alignment
    return options


def _table_width_options():
    # 1.40 accepts integer widths; later versions also accept 'stretch'.
    if inspect.signature(st.data_editor).parameters["width"].default == "stretch":
        return {"width": "stretch"}
    return {"use_container_width": True}


def _select_service(service_ids, editor_key):
    """Consume the checkbox edit before rendering the next single-selection table."""
    previous = st.session_state.get("selected_service_id")
    edits = st.session_state[editor_key].get("edited_rows", {})
    chosen = [service_ids[int(index)] for index, values in edits.items()
              if values.get("Kies") is True and service_ids[int(index)] != previous]
    if chosen:
        st.session_state["selected_service_id"] = chosen[-1]
    elif any(service_ids[int(index)] == previous and values.get("Kies") is False
             for index, values in edits.items()):
        st.session_state.pop("selected_service_id", None)
    # A fresh widget identity removes the old checkbox edits in this same rerun.
    st.session_state["services-table-revision"] = st.session_state.get("services-table-revision", 0) + 1


def _choose_service(service_ids, click_key):
    """A row action changes only the active UI choice, never the planning."""
    click = st.session_state[click_key]
    if click is not None and 0 <= click["row"] < len(service_ids):
        service_id = service_ids[click["row"]]
        if st.session_state.get("selected_service_id") == service_id:
            st.session_state.pop("selected_service_id", None)
        else:
            st.session_state["selected_service_id"] = service_id


@trace_planning
def _render_planning():
    st.subheader("Ledendienst Planning")
    settings = st.container()
    with settings:
        st.markdown("## 1 — Instellingen")
    data_sources = st.container()
    with data_sources:
        st.markdown("## 2 — Databronnen")
    duties = st.container()
    with duties:
        st.markdown("## 3 — Diensten")
        sportlink_source = st.container()
        duty_table = st.container()
    candidates = st.container()
    with candidates:
        st.markdown("## 4 — Kandidaten")
    fixtures = st.container()
    with fixtures:
        st.markdown("## 5 — Wedstrijden")
    database = SQLiteDatabase(Path(__file__).with_name("dvk_v05.sqlite"))
    database.initialize()
    identity = Identity("demo-planner", "Demo planner", frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL, Permission.MANAGE_NO_SHOWS}))
    with settings:
        with database.unit_of_work() as uow:
            active_session = PlanningSessionApplicationService(uow, identity).current()
        active_period = active_session.period if active_session else None
        needs_resume = active_session and st.session_state.get("planning-resumed") != active_session.session_id
        if needs_resume:
            st.info(f"Bewaarde planning: {active_period.start:%d-%m-%Y} t/m {active_period.end:%d-%m-%Y}")
            if st.button("Bestaande planning hervatten", key="resume-planning"):
                st.session_state["planning-resumed"] = active_session.session_id
                st.session_state["planning-mode"] = "Aangepast"
                st.session_state["planning-from"] = active_period.start
                st.session_state["planning-until"] = active_period.end
                _clear_period_widgets()
                st.rerun()
        if active_session and st.button("Nieuwe planning starten" if needs_resume else "Start nieuwe planning", key="start-new-planning"):
            st.session_state["planning-close-request"] = active_session.session_id
        if st.session_state.get("planning-close-request"):
            st.warning("De tijdelijke DVK-indelingen komen te vervallen. Bevestig dat deze niet langer nodig zijn "
                       "en dat je de noodzakelijke handmatige verwerking in Sportlink hebt afgehandeld. "
                       "DVK controleert die verwerking niet.")
            if st.button("Afsluiten en nieuwe planning starten", key="confirm-close-planning"):
                with database.unit_of_work() as uow:
                    PlanningSessionApplicationService(uow, identity).close(confirmed=True,
                        expected_session_id=st.session_state["planning-close-request"])
                for key in ("planning-close-request", "planning-resumed", "planning-mode", "planning-from", "planning-until"):
                    st.session_state.pop(key, None)
                _clear_period_widgets()
                st.rerun()
            if st.button("Annuleren", key="cancel-close-planning"):
                st.session_state.pop("planning-close-request", None)
                st.rerun()
            return
        if needs_resume:
            return
        # Widget state may disappear on navigation; restore the durable period.
        if active_period is not None and "planning-mode" not in st.session_state:
            st.session_state["planning-mode"] = "Aangepast"
            st.session_state["planning-from"] = active_period.start
            st.session_state["planning-until"] = active_period.end
        mode = st.radio("Selectie", ("Dag", "Week", "Aangepast"), index=1, key="planning-mode")
        selected = st.date_input("Vanaf", value=date.today(), key="planning-from")
        if mode == "Dag": period = PlanningPeriod(selected, selected)
        elif mode == "Week":
            monday = selected - timedelta(days=selected.weekday()); period = PlanningPeriod(monday, monday + timedelta(days=6))
        else:
            if st.session_state.get("planning-until", selected) < selected:
                st.session_state["planning-until"] = selected + timedelta(days=6)
            until = st.date_input("Tot en met", value=selected + timedelta(days=6), min_value=selected, key="planning-until"); period = PlanningPeriod(selected, until)
        inputs = {key: st.session_state[key] for key in
                  ("planning-mode", "planning-from", "planning-until") if key in st.session_state}
        if active_session is not None and active_period != period:
            st.caption(f"Actieve planningsperiode: {active_period.start:%d-%m-%Y} t/m {active_period.end:%d-%m-%Y}")
            st.warning("Bij het wijzigen van de planningsperiode worden alle tijdelijke indelingen verwijderd. "
                       "Bevestig dat deze niet langer nodig zijn en dat de noodzakelijke handmatige verwerking in Sportlink is afgehandeld. DVK controleert die verwerking niet.")
            if st.button("Periode wijzigen en tijdelijke indelingen verwijderen", key="confirm-period-change"):
                with database.unit_of_work() as uow:
                    session = PlanningSessionApplicationService(uow, identity).start(
                        period, confirmed=True, expected_session_id=active_session.session_id)
                st.session_state["planning-resumed"] = session.session_id
                st.session_state["planning-accepted-inputs"] = inputs
                _clear_period_widgets()
                st.rerun()
            st.button("Annuleren", key="cancel-period-change", on_click=_cancel_period_change)
            return
        if active_period is not None and active_period != period:
            _clear_period_widgets()
        st.session_state["planning-accepted-inputs"] = inputs
        with database.unit_of_work() as uow:
            active_session = PlanningSessionApplicationService(uow, identity).current()
        if active_session:
            st.session_state["planning-resumed"] = active_session.session_id
        elif st.button("Start nieuwe planning", key="activate-planning"):
            with database.unit_of_work() as uow:
                session = PlanningSessionApplicationService(uow, identity).start(period)
            st.session_state["planning-resumed"] = session.session_id
            st.rerun()
        st.caption("Prototype v0.5 — Planning, kandidaten en menselijke beslissing")

    with data_sources:
        demo = st.radio("Gegevens", ("Sportlink en DVK-catalogus", "Demonstratie"), key="planning-source-mode") == "Demonstratie"
    if st.session_state.get("candidate-source-mode") != demo:
        st.session_state.pop("candidate-context", None)
        st.session_state.pop("candidate-load-key", None)
        for key in list(st.session_state):
            if key.startswith(("proposal-run-", "confirmed-", "pick-", "candidate-table-", "candidate-detail-")):
                del st.session_state[key]
    st.session_state["candidate-source-mode"] = demo
    candidate_context = st.session_state.get("candidate-context")
    if candidate_context is not None and candidate_context.period != period:
        st.session_state.pop("candidate-context", None)
        candidate_context = None
    catalog = load_shift_catalog()
    with database.unit_of_work() as uow:
        source_app = VolunteerPlanningApplicationService(uow, identity, catalog)
        success, attempt, source_matches = source_app.source(period)
        source_bookings = source_app.bookings(period) if not demo else ()
        services, needs, matches, statuses = _demo_data(period.start) if demo else source_app.planning_data(period)
    with data_sources:
        if demo:
            st.info("Demonstratie: diensten, bezetting, kandidaten, wedstrijden en actualiteit zijn synthetisch.")
        else:
            st.info("Diensten uit de CKC-catalogus; bezetting uit Sportlink. Kandidaten gebruiken de vijf lokale CKC-exports en het Sportlink-wedstrijdprogramma. Persoonsconflicten met Sportlink-inroosteringen zijn nog niet aangesloten.")
            if not source_matches:
                st.warning("Geen gevalideerde Sportlink-bezetting voor deze periode. Bezetting en resterende behoefte zijn onbekend totdat de bron succesvol is opgehaald.")
    if not demo and candidate_context is not None and candidate_context.error is None:
        matches = candidate_context.program.matches
    with database.unit_of_work() as uow:
        planning_app = PlanningApplicationService(identity, uow=uow)
        overview = planning_app.build_overview(period=period, services=services, staffing_needs=needs, matches=matches, source_statuses=statuses)
        needs = planning_app.staffing_needs(services=services, source_needs=needs)
    need_by_service = {n.service_id: n for n in needs}; service_by_id = {s.service_id: s for s in services}
    with duty_table:
        st.write(f"**Periode:** {overview.period.start:%d-%m-%Y} t/m {overview.period.end:%d-%m-%Y}")
        known = demo or source_matches
        c1, c2, c3, c4 = st.columns(4); c1.metric("Diensten", len(overview.services)); c2.metric("Open minimum", sum(r.open_need for r in overview.services) if known else "Onbekend"); c3.metric("DVK-planningsbezetting", sum(r.confirmed_occupancy for r in overview.services) if known else "Onbekend"); c4.metric("Resterende capaciteit", sum(r.remaining_capacity for r in overview.services) if known else "Onbekend")

        st.markdown("### Diensten")
        selected_service_id = None
        if not overview.services: st.info("Geen diensten in de gekozen periode.")
        else:
            previous_service = st.session_state.get("selected_service_id")
            row_actions = hasattr(st.column_config, "ButtonColumn")
            bindings = catalog.bindings(period)
            names_by_service = {s.service_id: _sportlink_names(s, bindings, source_bookings)
                                for s in services} if not demo else {s.service_id: "Onbekend" for s in services}
            rows = [{"Kies": ("☑" if r.service_id == previous_service else "☐") if row_actions else r.service_id == previous_service, "service_id": r.service_id, "Datum": _datum_met_dag(r.starts_at), "Tijd": f"{r.starts_at:%H:%M}–{r.ends_at:%H:%M}", "Dienst": r.service_type, "Min": r.minimum_staff, "Max": r.maximum_staff, "Sportlink": names_by_service[r.service_id], "Tijdelijk DVK": r.temporary_occupancy, "DVK-bezetting": r.confirmed_occupancy, "Open minimum": r.open_need, "Vrije capaciteit": r.remaining_capacity} for r in overview.services]
            if not known:
                for row in rows:
                    for field in ("Sportlink", "DVK-bezetting", "Open minimum", "Vrije capaciteit"):
                        row[field] = "Onbekend"
            numeric = ("Min", "Max", "Tijdelijk DVK", "DVK-bezetting", "Open minimum", "Vrije capaciteit")
            widths = {"Datum": 90, "Tijd": 110, "Dienst": 170, **{name: 65 for name in numeric}}
            columns = {name: st.column_config.Column(name, width=width, help=name,
                       **_table_column_options(st.column_config.Column,
                                               alignment="right" if name in numeric else "left"))
                       for name, width in widths.items()}
            columns.update({"service_id": None,
                            "Kies": st.column_config.CheckboxColumn("Kies", width=55,
                                help="Selecteer één dienst; een nieuwe keuze vervangt de vorige.",
                                **_table_column_options(st.column_config.CheckboxColumn, pinned=True)),
                            "Sportlink": st.column_config.TextColumn("Sportlink", width=320, help="Originele Sportlink-namen. Dubbelklik op een cel om de volledige inhoud te lezen en te kopiëren; wijzigen is niet mogelijk.")})
            service_ids = tuple(row["service_id"] for row in rows)
            row_key = sha256("\0".join(service_ids).encode()).hexdigest()
            if row_actions:
                click_key = f"service-choice-{row_key}"
                columns["Kies"] = st.column_config.ButtonColumn("Kies", width=55, pinned=True,
                    type="tertiary", help="Kies één dienst. Klik het aangevinkte vakje om de keuze op te heffen.",
                    on_click=_choose_service, args=(service_ids, click_key), key=click_key)
                editor_key = f"services_editor-stable-{row_key}"
            else:
                # Older runtimes lack row actions. Preserve their previous fallback;
                # stable scrolling is verified for the accepted runtime 1.64.0.
                editor_key = f"services_editor-{st.session_state.get('services-table-revision', 0)}"
            st.data_editor(pd.DataFrame(rows), hide_index=True, **_table_width_options(), height=210, row_height=32,
                           disabled=[name for name in rows[0] if name != "Kies"], column_config=columns,
                           key=editor_key, on_change=None if row_actions else _select_service,
                           args=None if row_actions else (service_ids, editor_key))

            selected_service_id = previous_service if previous_service in service_by_id else None

    candidate_result = None
    with data_sources:
        if not demo:
            st.caption("Achterstallige uren uit vorig seizoen zijn nog niet beschikbaar en tellen niet mee.")
            st.caption(export_location_hint())
            with settings:
                source_period = st.text_input("Seizoen van Overzicht per periode", value=suggested_season(period.start), key="candidate-season")
            st.caption("Controleer zelf of de vijf handmatig vernieuwde exports bij dit seizoen horen. Sportlink is de bron voor het wedstrijdprogramma; beoordeel de kandidaten altijd in die context.")
            if candidate_context is not None and candidate_context.source_period != source_period.strip():
                st.session_state.pop("candidate-context", None)
                candidate_context = None
            refresh_candidates = st.button("Brongegevens vernieuwen", key="load-candidate-sources")
            candidate_load_key = (period, source_period)
            if refresh_candidates or st.session_state.get("candidate-load-key") != candidate_load_key:
                st.session_state["candidate-load-key"] = candidate_load_key
                st.session_state.pop("candidate-load-error", None)
                st.session_state.pop("candidate-context", None)
                for key in list(st.session_state):
                    if key.startswith(("proposal-run-", "confirmed-", "pick-", "candidate-table-", "candidate-detail-")):
                        del st.session_state[key]
                try:
                    with st.spinner("Lokale CSV-bronnen en wedstrijdprogramma laden…"):
                        candidate_context = CandidateContextApplicationService(identity).load(
                            period=period, source_period=source_period,
                            client_id=os.environ.get("SPORTLINK_CLIENT_ID", ""))
                    st.session_state["candidate-context"] = candidate_context
                    st.rerun()
                except CandidateSourceError as exc:
                    candidate_context = None
                    st.session_state["candidate-load-error"] = str(exc)
            if st.session_state.get("candidate-load-error"):
                st.error(st.session_state["candidate-load-error"])
            if candidate_context is not None:
                st.caption("Ingelezen bestanden: " + ", ".join(candidate_context.source_files))
                st.caption("Bestanden handmatig gewijzigd? Kies Brongegevens vernieuwen. DVK controleert de map niet op de achtergrond.")
                stats = candidate_context.stats
                st.caption(f"Kandidaatbronnen geladen: {candidate_context.fetched_at:%d-%m-%Y %H:%M}. Programma API: {stats.calls} aanvraag, {stats.retries} herhalingen, {stats.failures} definitieve fouten.")
                if candidate_context.error:
                    st.error(candidate_context.error)
                elif stats.retries:
                    st.warning("Programma API tijdelijk instabiel; een herhaalpoging is geslaagd. De wedstrijdcontext is beschikbaar.")
                else:
                    st.caption("Programma API: technisch geslaagd, ook als Sportlink geen wedstrijden aanlevert.")
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
    with candidates:
        st.markdown("### Kandidaten en voorstellen")
        ready = demo or (known and candidate_context is not None and candidate_context.error is None)
        if not ready:
            st.info("Kandidaten zijn beschikbaar na een geslaagde bronimport en gevalideerde Sportlink-bezetting voor deze periode.")
        elif selected_service_id is None:
            st.info("Selecteer eerst één dienst in de tabel hierboven.")
        else:
            service = service_by_id[selected_service_id]; need = need_by_service[selected_service_id]
            proposal_run_key = f"proposal-run-{selected_service_id}"
            if proposal_run_key not in st.session_state:
                st.session_state[proposal_run_key] = str(uuid4())
            with database.unit_of_work() as uow:
                planning_app = PlanningApplicationService(identity, uow=uow)
                if demo:
                    cases, planned = _demo_proposals(service, need, matches, planning_app=planning_app, proposal_run_id=st.session_state[proposal_run_key])
                else:
                    try:
                        candidate_result = CandidateContextApplicationService(identity).propose(
                            candidate_context, service=service, need=need, planning_app=planning_app,
                            proposal_run_id=st.session_state[proposal_run_key])
                        cases, planned = candidate_result.cases, candidate_result.planned
                    except CandidateSourceError as exc:
                        st.error(str(exc))
                        cases, planned = (), ()
            if candidate_result is not None:
                uncertain = sum(control.status == "niet betrouwbaar beoordeelbaar" for control in candidate_result.controls)
                if uncertain:
                    st.warning(f"{uncertain} leden beleidsmatig of op brongegevens niet betrouwbaar beoordeelbaar. Betrouwbare Sportlink-taakplicht blijft voor planning leidend; bekijk de Taakplichtcontrole voor toelichting.")
                if any(control.status == "afwijking" for control in candidate_result.controls):
                    st.warning("Bij leden wijkt de Sportlink-urenverplichting af van de DVK-afleiding. De actuele Sportlink-urenpositie blijft leidend; bekijk de Taakplichtcontrole voor herbeoordeling.")
            case_by_person = {c.person.person_id: c for c in cases}
            if not planned:
                if not demo and candidate_result is None:
                    pass  # The explicit source error above is not an empty candidate result.
                elif need.remaining_capacity == 0: st.info("Geen kandidaatvoorstellen: de maximumbezetting is bereikt.")
                else: st.info("Geen kandidaatvoorstellen: er zijn geen geschikte kandidaten voor deze dienst.")
            else:
                st.caption(f"Er zijn nog {need.remaining_capacity} plaatsen beschikbaar. Niet geselecteerde kandidaten blijven beschikbaar voor een volgende planning.")
                candidate_rows = [{"Kies": False, "proposal_id": item.proposal.proposal_id,
                                   "Rang": item.proposal.priority_rank,
                                   "Kandidaat": case_by_person[item.proposal.person_id].person.name,
                                   "Team": item.proposal.team_id or "—", "Openstaande uren": item.proposal.E,
                                   "Doel": {"minimum_coverage": "Min bezetting", "emergency_minimum_coverage": "Noodkandidaat — Min bezetting",
                                            "optional_capacity": "Aanvulling tot Max"}[item.staffing_purpose],
                                   "Wedstrijdcontext": _vriendelijke_wedstrijdcontext(item.proposal.match_relation),
                                   "Opmerkingen": "; ".join(filter(None, (_vriendelijke_waarom(item.proposal), *(reason for reason in item.proposal.uncertainties if reason == EMERGENCY_MATCHDAY_REASON))))} for item in planned]
                row_identity = sha256("\0".join(row["proposal_id"] for row in candidate_rows).encode()).hexdigest()
                candidate_table = st.data_editor(pd.DataFrame(candidate_rows), hide_index=True, height=330, row_height=32,
                    **_table_width_options(), disabled=[name for name in candidate_rows[0] if name != "Kies"],
                    column_config={"proposal_id": None,
                                   "Kies": st.column_config.CheckboxColumn("Kies", width=55,
                                       **_table_column_options(st.column_config.CheckboxColumn, pinned=True)),
                                   "Rang": st.column_config.NumberColumn(width=60),
                                   "Kandidaat": st.column_config.TextColumn(width=190)},
                    key=f"candidate-table-{selected_service_id}-{row_identity}")
                selected_proposal_ids = candidate_table.loc[candidate_table["Kies"], "proposal_id"].tolist()
                proposals_by_id = {item.proposal.proposal_id: item.proposal for item in planned}
                for detail_id in selected_proposal_ids:
                    p = proposals_by_id[detail_id]
                    st.markdown("#### " + case_by_person[p.person_id].person.name)
                    if candidate_result is not None:
                        detail = next(row for row in candidate_result.explanations if row.person_id == p.person_id)
                        st.caption("DVK-beleidscontrole taakplicht: " + detail.why)
                        st.caption("Geregistreerde Sportlink-taakplicht is leidend voor planning.")
                    st.caption(priority_explanation(p))
                    st.caption("Wedstrijdcontext: " + _vriendelijke_wedstrijdcontext(p.match_relation))
                    remarks = "; ".join(filter(None, (_vriendelijke_waarom(p), *(reason for reason in p.uncertainties if reason == EMERGENCY_MATCHDAY_REASON))))
                    if remarks != "—":
                        st.caption(remarks)
                st.write("De DVK stelt geschikte kandidaten voor. Selecteer wie je wilt inroosteren en bevestig je keuze.")
                with database.unit_of_work() as uow:
                    selection_problem = PlanningApplicationService(identity, uow=uow).selection_problem(
                        person_ids=tuple(next(i.proposal.person_id for i in planned if i.proposal.proposal_id == pid)
                                         for pid in selected_proposal_ids), service=service, staffing_need=need)
                if selection_problem and selected_proposal_ids:
                    st.warning(selection_problem)
                if st.button("Selectie bevestigen", type="primary", disabled=bool(selection_problem) or not selected_proposal_ids):
                    selections = tuple((next(i.proposal for i in planned if i.proposal.proposal_id == pid), case_by_person[next(i.proposal for i in planned if i.proposal.proposal_id == pid).person_id], f"UI-{uuid4()}") for pid in selected_proposal_ids)
                    try:
                        with database.unit_of_work() as uow:
                            results = ProposalDecisionApplicationService(identity, uow=uow).approve_many(selections, service, need)
                        st.session_state[f"confirmed-{selected_service_id}"] = results
                        st.session_state[proposal_run_key] = str(uuid4())
                        st.rerun()
                    except ValueError as exc: st.error(str(exc))
            confirmed = st.session_state.get(f"confirmed-{selected_service_id}")
            if confirmed:
                names = [case_by_person[r.assignment.person_id].person.name for r in confirmed if r.assignment]; st.success(f"Inroostering bevestigd voor: {', '.join(names)}.")

        st.divider()
        st.markdown("### Actieve tijdelijke DVK-inroosteringen")
        st.caption("Deze werkvoorraad telt mee in de planning; de Sportlink-bronbezetting blijft ongewijzigd.")
        with database.unit_of_work() as uow:
            temporary_rows = PlanningApplicationService(identity, uow=uow).temporary_assignment_contexts(
                persons=(tuple(c.person for c in demo_candidate_cases()) if demo else
                         candidate_context.source.persons if candidate_context is not None else ()),
            )
        if temporary_rows:
            temporary_labels = {row.assignment.assignment_id: _assignment_label(row) for row in temporary_rows}
            with st.form("undo-temporary-planning"):
                undo_id = st.selectbox("Tijdelijke inroostering", tuple(temporary_labels), format_func=temporary_labels.get)
                undo_submitted = st.form_submit_button("Tijdelijke inroostering ongedaan maken")
            if undo_submitted:
                try:
                    with database.unit_of_work() as uow:
                        ProposalDecisionApplicationService(identity, uow=uow).undo(undo_id)
                    # A fresh proposal run also permits selecting the undone person again.
                    for key in list(st.session_state):
                        if key.startswith("proposal-run-") or key.startswith("confirmed-"):
                            del st.session_state[key]
                    st.session_state["undo-planning-result"] = "Tijdelijke inroostering ongedaan gemaakt. Bezetting en beschikbaarheid zijn opnieuw berekend."
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        else:
            st.info("Geen actieve tijdelijke inroosteringen.")
        undo_result = st.session_state.pop("undo-planning-result", None)
        if undo_result:
            st.success(undo_result)

        st.divider()
        st.markdown("### No-shows")
        st.caption("Registreer een no-show uitsluitend op een feitelijke Sportlink-inroostering. Tijdelijke DVK-planning is hiervoor niet beschikbaar.")
        with database.unit_of_work() as uow:
            assignment_rows = NoShowApplicationService(uow, identity).assignment_contexts(
                services=services, persons=tuple(c.person for c in demo_candidate_cases()), period=period,
            )
        if not assignment_rows:
            st.info("Geen betrouwbaar aan een persoon gekoppelde inroosteringen beschikbaar voor no-showregistratie.")
        else:
            assignment_by_id = {c.assignment.assignment_id: c for c in assignment_rows}
            assignment_options = {key: _assignment_label(c, source_name=True) for key, c in assignment_by_id.items()}
            with st.form("no-show-form"):
                assignment_id = st.selectbox("Inroostering", tuple(assignment_options), format_func=assignment_options.get)
                submitted_no_show = st.form_submit_button("No-show bevestigen", type="primary")
            if submitted_no_show:
                with database.unit_of_work() as uow:
                    context = assignment_by_id[assignment_id]
                    assignment = context.assignment
                    service_info = context.service
                    if service_info is None:
                        st.error("De datum/tijd van deze inroostering is niet beschikbaar in de huidige planning.")
                        st.stop()
                    occurred_at = service_info.starts_at
                    event = NoShowEvent(
                        f"NS-{uuid4()}", assignment.assignment_id, assignment.person_id,
                        occurred_at, datetime.now().astimezone(), identity.subject_id,
                        season_id(occurred_at.date()),
                    )
                    try:
                        assessment = NoShowApplicationService(uow, identity).register(event, period=period,
                            source_revision=st.session_state.get("no-show-selection-revision"))
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["last-no-show"] = assessment
            assessment = st.session_state.pop("last-no-show", None)
            if assessment:
                if assessment.counter == 1:
                    st.warning("Eerste no-show: waarschuwing. Betrokkene moet zelf een vervangende inzet regelen.")
                else:
                    card = "gele kaart" if assessment.card == "yellow" else "rode kaart"
                    follow_up = " Bestuurlijke vervolgactie is vereist." if assessment.board_follow_up else ""
                    st.warning(f"No-show {assessment.counter}: {card}, €{assessment.fine_eur} boete en {assessment.suspension_matches} wedstrijd(en) schorsing.{follow_up}")
                st.info("Communicatie hierover is vereist. Het DVK registreert dit; verzending en uitvoering zijn niet geautomatiseerd in v0.5.")

        st.session_state["no-show-selection-revision"] = assignment_rows[0].source_revision if assignment_rows else None

        with database.unit_of_work() as uow:
            revocable_rows = NoShowApplicationService(uow, identity).revocable_no_shows(
                services=services, persons=tuple(c.person for c in demo_candidate_cases()),
            )

        if st.session_state.pop("clear-no-show-revocation-reason", False):
            st.session_state["no-show-revocation-reason"] = ""

        if revocable_rows:
            no_show_labels = {row.no_show.no_show_id: _assignment_label(row.assignment) for row in revocable_rows}
            with st.form("no-show-revocation-form"):
                revoke_no_show_id = st.selectbox("No-show intrekken", tuple(no_show_labels), format_func=no_show_labels.get,
                                              key="no-show-revocation-id")
                revocation_reason = st.text_area("Toelichting voor intrekking (verplicht)", key="no-show-revocation-reason")
                revoke_submitted = st.form_submit_button("Intrekking bevestigen", type="primary")
            if revoke_submitted:
                try:
                    with database.unit_of_work() as uow:
                        app = NoShowApplicationService(uow, identity)
                        app.revoke(revoke_no_show_id, reason=revocation_reason, revoked_at=datetime.now().astimezone())
                        selected_row = next(row for row in revocable_rows if row.no_show.no_show_id == revoke_no_show_id)
                        selected_no_show = selected_row.no_show
                        state = app.current_state(selected_no_show.person_id, selected_no_show.season)
                    person_label = selected_row.assignment.person_name or "dit lid (naam onbekend)"
                    st.session_state["no-show-revocation-result"] = f"No-show ingetrokken. Actuele no-showteller voor {person_label} in seizoen {state.season}: {state.counter}."
                    st.session_state["clear-no-show-revocation-reason"] = True
                    st.session_state.pop("last-no-show", None)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        else:
            st.info("Geen geregistreerde no-shows beschikbaar voor intrekking.")

        revocation_result = st.session_state.pop("no-show-revocation-result", None)
        if revocation_result:
            st.success(revocation_result)

    with fixtures, st.expander("Wedstrijdoverzicht voor de gekozen periode", expanded=True):
        if not demo and (candidate_context is None or candidate_context.error):
            st.info("Wedstrijdcontext onbekend: laad de kandidaatbronnen en beoordeel eventuele bronmeldingen.")
        elif not overview.matches: st.info("Sportlink heeft geen wedstrijden aangeleverd voor de gekozen periode.")
        else: st.dataframe([{"Datum": _datum_met_dag(m.starts_at), "Tijd": m.starts_at.strftime("%H:%M"), "Team": m.team_id, "Thuis/uit": "Thuis" if m.home_away.strip().lower() == "home" else "Uit"} for m in overview.matches], use_container_width=True, hide_index=True, height=230)
    with sportlink_source:
        with st.expander("Feitelijke Sportlink-inroosteringen ophalen"):
            st.caption(export_location_hint(("leden",)))
            st.caption("Leden.csv wordt bij synchroniseren opnieuw uit de vaste lokale map gelezen voor persoonskoppeling.")
            st.caption("Alle actieve catalogustaakcodes worden opgehaald voor de gekozen periode. Bij succes vervallen alle tijdelijke indelingen. Boekingen zonder betrouwbare persoonskoppeling tellen mee in de bezetting; no-showregistratie is daarop niet beschikbaar.")
            replace_confirmed = False
            replacing = bool(active_session and (active_session.source_revision or temporary_rows))
            if replacing:
                replace_confirmed = st.checkbox("Ik bevestig dat tijdelijke indelingen mogen vervallen, niet langer nodig zijn en dat noodzakelijke handmatige verwerking in Sportlink is afgehandeld.", key=f"confirm-source-{active_session.source_revision}")
                st.caption("DVK controleert deze verklaring niet. Bij een mislukte synchronisatie blijft de bestaande planning behouden.")
            if st.button("Sportlink-inroosteringen synchroniseren", disabled=demo or (replacing and not replace_confirmed)):
                try:
                    persons = LocalCsvSourceApplicationService().volunteer_persons()
                    with database.unit_of_work() as uow:
                        if active_session is None:
                            active_session = PlanningSessionApplicationService(uow, identity).start(period)
                            st.session_state["planning-resumed"] = active_session.session_id
                        error = VolunteerPlanningApplicationService(uow, identity, catalog).synchronize(
                            period=period,
                            client=SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter()),
                            client_id=os.environ.get("SPORTLINK_CLIENT_ID", ""),
                            persons=persons, imported_at=datetime.now().astimezone(),
                            confirmed=replace_confirmed, source_revision=active_session.source_revision)
                    if error:
                        st.error(error)
                    else:
                        st.session_state["sportlink-sync-result"] = "Sportlink-inroosteringen vernieuwd; tijdelijke DVK-planning vervangen."
                        st.rerun()
                except (ValueError, UnicodeError, VrijwilligersFetchError) as exc:
                    st.error(str(exc))
            for signal in st.session_state.get("sportlink-booking-signals", ()):
                st.error(signal.message)
            sync_result = st.session_state.pop("sportlink-sync-result", None)
            if sync_result:
                st.success(sync_result)
        if not demo:
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
    with data_sources:
        with st.expander("Bronstatus en actualiteit", expanded=False):
            st.dataframe([{"Databron": s.source, "Laatst opgehaald": s.fetched_at.strftime("%d-%m-%Y %H:%M") if s.fetched_at else "onbekend", "Status": s.status} for s in overview.source_statuses], use_container_width=True, hide_index=True, height=360)
        st.markdown("### Datakwaliteit")
        if overview.data_quality_signals: st.dataframe([{"Ernst": s.severity, "Code": s.code, "Melding": s.message} for s in overview.data_quality_signals], use_container_width=True, hide_index=True, height=360)
        else: st.success("Geen datakwaliteitssignalen voor deze planning.")
        st.caption("Gate 10 ondersteunt expliciete intrekking van no-shows met een verplichte toelichting en afzonderlijke auditregistratie. Gate 8 gebruikt demonstratiedata. Niet selecteren is geen afwijzing.")


def _render_planning_screen():
    try:
        _render_planning()
    except sqlite3.DatabaseError as exc:
        # Known schema/storage failures may block planning, but never the CSV control.
        # Unknown SQL errors and programming errors must remain visible to developers.
        storage_codes = {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED, sqlite3.SQLITE_READONLY,
                         sqlite3.SQLITE_CANTOPEN, sqlite3.SQLITE_IOERR, sqlite3.SQLITE_FULL,
                         sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB}
        missing_schema = isinstance(exc, sqlite3.OperationalError) and str(exc).startswith(
            ("no such table:", "no such column:"))
        if not missing_schema and (getattr(exc, "sqlite_errorcode", 0) & 0xff) not in storage_codes:
            raise
        st.error("De planning en no-showregistratie zijn niet beschikbaar door een databaseprobleem. "
                 "Laat de database afzonderlijk controleren. Open Taakplichtcontrole via de zijbalk; die blijft beschikbaar.")


# Only retain scalar input values. Uploads and action/selection widgets follow
# Streamlit's normal cleanup when their screen is no longer rendered.
for _key in ("planning-mode", "planning-from", "planning-until", "planning-source-mode",
             "duty-control-date", "duty-control-period", "duty-control-filter"):
    if _key in st.session_state:
        st.session_state[_key] = st.session_state[_key]


def _navigate(screen):
    if screen != st.session_state.get("dvk-screen"):
        for key in ("candidate-load-key", "duty-load-key"):
            st.session_state.pop(key, None)
    st.session_state["dvk-screen"] = screen


def _render_navigation():
    with st.sidebar:
        st.header("DVK")
        st.button("Startscherm", key="nav-home", on_click=_navigate, args=("home",))
        st.subheader("Ledendiensten & Vrijwilligersbeleid")
        st.button("Ledendienst Planning", key="nav-planning", on_click=_navigate, args=("planning",))
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
    st.write("**Taakplichtcontrole** — beschikbare read-only functie binnen Ledendienst Planning.")
    st.write("**Rooster Generator** — operationele externe toepassing, nog niet geïntegreerd in DVK.")
    st.markdown("### Overige werkgebieden")
    st.write("**Ledenadministratie** — toekomstig, niet beschikbaar.")
    st.write("**Wedstrijdsecretariaat** — toekomstig, niet beschikbaar.")
    st.write("**Kledingadministratie** — toekomstig, niet beschikbaar.")
    st.markdown("### DVK Beheer")
    st.write("**Toegangsbeheer** — toekomstig, niet beschikbaar.")
    st.write("**Tabelonderhoud** — toekomstig, niet beschikbaar.")
    st.info("CSV-bronnen worden bij gebruik uit de vaste lokale map geladen. Gebruik Brongegevens vernieuwen nadat u exports heeft vervangen. Peildatum, seizoen en filter blijven binnen deze sessie behouden.")


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



_render_navigation()
_screen = st.session_state.get("dvk-screen", "home")
if _screen == "planning":
    _render_planning_screen()
elif _screen == "control":
    _render_duty_control()
else:
    _render_home()
