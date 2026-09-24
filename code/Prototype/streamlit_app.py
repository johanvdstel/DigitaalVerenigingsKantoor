from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from dvk.application_services import NoShowApplicationService, PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_selection import assess_candidate
from dvk.no_show import NoShowEvent, season_id
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.proposal_planning import plan_proposals
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY
from dvk.demo_data_v05 import demo_candidate_cases, demo_previous_season_backlog, demo_team_memberships, demo_planning_data
from dvk.workstream_model import DutyService, Match, TeamMembership

DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")
REJECTION_LABELS = {"Persoonlijke omstandigheid": "personal_circumstance", "Niet geschikt voor deze dienst": "unsuitable_for_service", "Brongegevens kloppen niet": "source_data_incorrect", "Andere bijzonderheid": "other"}
MATCH_LABELS = {"no_match_context": "Geen wedstrijd", "no_match_that_day": "Geen wedstrijd", "home_match_overlaps_service": "Thuiswedstrijd overlapt", "home_match_same_day": "Thuiswedstrijd", "away_match_overlaps_service": "Uitwedstrijd overlapt", "away_match_same_day": "Uitwedstrijd"}
RULE_LABELS = {"previous_season_backlog_before_december": "Openstaande uren uit vorig seizoen meegewogen", "home_match_overlap": "Thuiswedstrijd sluit aan op dienst", "home_match_same_day": "Thuiswedstrijd op dezelfde dag", "away_match_emergency": "Uitwedstrijd meegewogen als noodoptie"}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


def _assignment_label(context) -> str:
    service_info = context.service
    person_name = context.person_name or "Persoon onbekend"
    if service_info is None:
        return f"Datum/tijd en dienst onbekend — {person_name}"
    return f"{_datum_met_dag(service_info.starts_at)} {service_info.starts_at:%H:%M}–{service_info.ends_at:%H:%M} — {service_info.service_type or 'Dienst onbekend'} — {person_name}"


def _vriendelijke_wedstrijdcontext(value: str) -> str:
    return MATCH_LABELS.get(value, value.replace("_", " ").capitalize())


def _vriendelijke_waarom(proposal) -> str:
    details: list[str] = []
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

def _demo_proposals(service: DutyService, need: StaffingNeed, matches: tuple[Match, ...], *, proposal_run_id: str | None = None):
    cases = demo_candidate_cases()
    memberships = demo_team_memberships(service, cases)
    assessments = tuple(assess_candidate(case, service, memberships, matches, TODAY) for case in cases)
    eligible = tuple(a for a in assessments if a.eligible)
    priorities = prioritize_candidates(eligible, cases, service.starts_at.date(), previous_season_backlog=demo_previous_season_backlog())
    by_person = {p.person_id: p for p in priorities}
    proposals = tuple(create_assignment_proposal(f"DEMO-{service.service_id}-{case.person.person_id}-{proposal_run_id or uuid4()}", service, case, next(a for a in eligible if a.person_id == case.person.person_id), by_person[case.person.person_id], matches) for case in cases if case.person.person_id in by_person)
    return cases, plan_proposals(proposals, need)

st.set_page_config(page_title="DVK — Ledendienst Planning", page_icon="📋", layout="wide")
st.title("CKC Digitaal Verenigings Kantoor (DVK)")
st.subheader("Ledendienst Planning")
st.caption("Prototype v0.5 — Planning, kandidaten en menselijke beslissing")
with st.sidebar:
    st.header("Periode")
    mode = st.radio("Selectie", ("Dag", "Week", "Aangepast"), index=1)
    selected = st.date_input("Vanaf", value=date.today())
    if mode == "Dag": period = PlanningPeriod(selected, selected)
    elif mode == "Week":
        monday = selected - timedelta(days=selected.weekday()); period = PlanningPeriod(monday, monday + timedelta(days=6))
    else:
        until = st.date_input("Tot en met", value=selected + timedelta(days=6), min_value=selected); period = PlanningPeriod(selected, until)

identity = Identity("demo-planner", "Demo planner", frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL, Permission.MANAGE_NO_SHOWS}))
database = SQLiteDatabase(Path(__file__).with_name("dvk_v05.sqlite"))
database.initialize()
services, needs, matches, statuses = _demo_data(period.start)
overview = PlanningApplicationService(identity).build_overview(period=period, services=services, staffing_needs=needs, matches=matches, source_statuses=statuses)
need_by_service = {n.service_id: n for n in needs}; service_by_id = {s.service_id: s for s in services}
st.write(f"**Periode:** {overview.period.start:%d-%m-%Y} t/m {overview.period.end:%d-%m-%Y}")
c1, c2, c3, c4 = st.columns(4); c1.metric("Diensten", len(overview.services)); c2.metric("Open minimum", sum(r.open_need for r in overview.services)); c3.metric("Bevestigd", sum(r.confirmed_occupancy for r in overview.services)); c4.metric("Resterende capaciteit", sum(r.remaining_capacity for r in overview.services))

st.markdown("### Diensten")
selected_service_id = None
if not overview.services: st.info("Geen diensten in de gekozen periode.")
else:
    previous_service = st.session_state.get("selected_service_id")
    rows = [{"Kies": r.service_id == previous_service, "service_id": r.service_id, "Datum": _datum_met_dag(r.starts_at), "Tijd": f"{r.starts_at:%H:%M}–{r.ends_at:%H:%M}", "Dienst": r.service_type, "Locatie": r.location, "Min": r.minimum_staff, "Max": r.maximum_staff, "Bevestigd": r.confirmed_occupancy, "Open minimum": r.open_need, "Vrije capaciteit": r.remaining_capacity} for r in overview.services]
    edited = st.data_editor(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=210, disabled=["service_id", "Datum", "Tijd", "Dienst", "Locatie", "Min", "Max", "Bevestigd", "Open minimum", "Vrije capaciteit"], column_config={"service_id": None, "Kies": st.column_config.CheckboxColumn("Kies", help="Selecteer één dienst")}, key="services_editor")
    picked = edited[edited["Kies"]]
    if len(picked) > 1: st.error("Selecteer maximaal één dienst.")
    elif len(picked) == 1:
        selected_service_id = picked.iloc[0]["service_id"]; st.session_state["selected_service_id"] = selected_service_id
    else: st.session_state.pop("selected_service_id", None)

st.markdown("### Kandidaten en voorstellen")
if selected_service_id is None: st.info("Selecteer eerst één dienst in de tabel hierboven.")
else:
    service = service_by_id[selected_service_id]; need = need_by_service[selected_service_id]
    proposal_run_key = f"proposal-run-{selected_service_id}"
    if proposal_run_key not in st.session_state:
        st.session_state[proposal_run_key] = str(uuid4())
    cases, planned = _demo_proposals(service, need, matches, proposal_run_id=st.session_state[proposal_run_key]); case_by_person = {c.person.person_id: c for c in cases}
    if not planned:
        if need.remaining_capacity == 0: st.info("Geen kandidaatvoorstellen: de maximumbezetting is bereikt.")
        else: st.info("Geen kandidaatvoorstellen: er zijn geen geschikte kandidaten voor deze dienst.")
    else:
        st.caption(f"Er zijn nog {need.remaining_capacity} plaatsen beschikbaar. Niet geselecteerde kandidaten blijven beschikbaar voor een volgende planning.")
        selected_proposal_ids = []
        with st.container(height=330, border=True):
            header = st.columns((0.6, 0.6, 1.8, 1.2, 1.4, 1.6, 1.9, 2.2, 0.7))
            for col, text in zip(header, ("Kies", "Rang", "Kandidaat", "Team", "Openstaande uren", "Doel", "Wedstrijdcontext", "Opmerkingen", "Meer")): col.markdown(f"**{text}**")
            for item in planned:
                p = item.proposal; cols = st.columns((0.6, 0.6, 1.8, 1.2, 1.4, 1.6, 1.9, 2.2, 0.7))
                if cols[0].checkbox("Selecteer", key=f"pick-{selected_service_id}-{p.proposal_id}", label_visibility="collapsed"): selected_proposal_ids.append(p.proposal_id)
                cols[1].write(p.priority_rank); cols[2].write(case_by_person[p.person_id].person.name); cols[3].write(p.team_id or "—"); cols[4].write(p.E)
                cols[5].write("Min bezetting" if item.staffing_purpose == "minimum_coverage" else "Aanvulling tot Max"); cols[6].write(_vriendelijke_wedstrijdcontext(p.match_relation)); cols[7].write(_vriendelijke_waarom(p))
                with cols[8].popover("⋯"):
                    st.caption("Alleen gebruiken als er een bijzondere reden is om deze kandidaat niet te gebruiken.")
                    with st.form(f"exception-{p.proposal_id}"):
                        label = st.selectbox("Reden", tuple(REJECTION_LABELS), key=f"reasoncat-{p.proposal_id}"); reason = st.text_input("Toelichting", key=f"reason-{p.proposal_id}"); submitted = st.form_submit_button("Uitzondering vastleggen")
                        if submitted:
                            if not reason.strip(): st.error("Een toelichting is verplicht.")
                            else:
                                with database.unit_of_work() as uow:
                                    result = ProposalDecisionApplicationService(identity, uow=uow).reject(p, case_by_person[p.person_id], reason_category=REJECTION_LABELS[label], reason=reason)
                                st.session_state[f"exception-result-{p.proposal_id}"] = result
                    if st.session_state.get(f"exception-result-{p.proposal_id}"): st.warning("Uitzondering vastgelegd. De urenpositie blijft ongewijzigd; deze persoon kan bij een volgende planning opnieuw worden voorgesteld.")
        st.write("De DVK stelt geschikte kandidaten voor. Selecteer wie je wilt inroosteren en bevestig je keuze.")
        if st.button("Selectie bevestigen", type="primary", disabled=not selected_proposal_ids):
            selections = tuple((next(i.proposal for i in planned if i.proposal.proposal_id == pid), case_by_person[next(i.proposal for i in planned if i.proposal.proposal_id == pid).person_id], f"UI-{uuid4()}") for pid in selected_proposal_ids)
            try:
                with database.unit_of_work() as uow:
                    results = ProposalDecisionApplicationService(identity, uow=uow).approve_many(selections, service, need)
                st.session_state[f"confirmed-{selected_service_id}"] = results
                st.session_state[proposal_run_key] = str(uuid4())
            except ValueError as exc: st.error(str(exc))
        confirmed = st.session_state.get(f"confirmed-{selected_service_id}")
        if confirmed:
            names = [case_by_person[r.assignment.person_id].person.name for r in confirmed if r.assignment]; st.success(f"Inroostering bevestigd voor: {', '.join(names)}.")

st.markdown("### No-shows")
st.caption("Registreer een no-show alleen op een bestaande inroostering. Het DVK toont het beleidsgevolg; het voert boetes of schorsingen niet zelf uit.")
with database.unit_of_work() as uow:
    assignment_rows = NoShowApplicationService(uow, identity).assignment_contexts(
        services=services, persons=tuple(c.person for c in demo_candidate_cases()),
    )
if not assignment_rows:
    st.info("Nog geen inroosteringen beschikbaar waarop een no-show kan worden geregistreerd.")
else:
    assignment_by_id = {c.assignment.assignment_id: c for c in assignment_rows}
    assignment_options = {key: _assignment_label(c) for key, c in assignment_by_id.items()}
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
            assessment = NoShowApplicationService(uow, identity).register(event)
        st.session_state["last-no-show"] = assessment
    assessment = st.session_state.get("last-no-show")
    if assessment:
        if assessment.counter == 1:
            st.warning("Eerste no-show: waarschuwing. Betrokkene moet zelf een vervangende inzet regelen.")
        else:
            card = "gele kaart" if assessment.card == "yellow" else "rode kaart"
            follow_up = " Bestuurlijke vervolgactie is vereist." if assessment.board_follow_up else ""
            st.warning(f"No-show {assessment.counter}: {card}, €{assessment.fine_eur} boete en {assessment.suspension_matches} wedstrijd(en) schorsing.{follow_up}")
        st.info("Communicatie hierover is vereist. Het DVK registreert dit; verzending en uitvoering zijn niet geautomatiseerd in v0.5.")

with database.unit_of_work() as uow:
    revocable_rows = NoShowApplicationService(uow, identity).revocable_no_shows(
        services=services, persons=tuple(c.person for c in demo_candidate_cases()),
    )

if revocable_rows:
    no_show_labels = {row.no_show.no_show_id: _assignment_label(row.assignment) for row in revocable_rows}
    with st.form("no-show-revocation-form"):
        revoke_no_show_id = st.selectbox("No-show intrekken", tuple(no_show_labels), format_func=no_show_labels.get)
        revocation_reason = st.text_area("Toelichting voor intrekking (verplicht)")
        revoke_submitted = st.form_submit_button("Intrekking bevestigen", type="primary")
    if revoke_submitted:
        try:
            with database.unit_of_work() as uow:
                app = NoShowApplicationService(uow, identity)
                app.revoke(revoke_no_show_id, reason=revocation_reason, revoked_at=datetime.now().astimezone())
                selected_no_show = next(row.no_show for row in revocable_rows if row.no_show.no_show_id == revoke_no_show_id)
                state = app.current_state(selected_no_show.person_id, selected_no_show.season)
            st.session_state["no-show-revocation-result"] = f"No-show ingetrokken. Actuele teller voor seizoen {state.season}: {state.counter}."
            st.session_state.pop("last-no-show", None)
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
else:
    st.info("Geen geregistreerde no-shows beschikbaar voor intrekking.")

revocation_result = st.session_state.pop("no-show-revocation-result", None)
if revocation_result:
    st.success(revocation_result)

st.markdown("### Wedstrijden")
if not overview.matches: st.info("Geen wedstrijden in de gekozen periode.")
else: st.dataframe([{"Datum": _datum_met_dag(m.starts_at), "Tijd": m.starts_at.strftime("%H:%M"), "Team": m.team_id, "Thuis/uit": "Thuis" if m.home_away.strip().lower() == "home" else "Uit"} for m in overview.matches], use_container_width=True, hide_index=True, height=230)
st.markdown("### Databronnen")
st.dataframe([{"Databron": s.source, "Laatst opgehaald": s.fetched_at.strftime("%d-%m-%Y %H:%M") if s.fetched_at else "onbekend", "Status": s.status} for s in overview.source_statuses], use_container_width=True, hide_index=True)
st.markdown("### Datakwaliteit")
if overview.data_quality_signals: st.dataframe([{"Ernst": s.severity, "Code": s.code, "Melding": s.message} for s in overview.data_quality_signals], use_container_width=True, hide_index=True)
else: st.success("Geen datakwaliteitssignalen voor deze planning.")
st.caption("Gate 10 ondersteunt expliciete intrekking van no-shows met een verplichte toelichting en afzonderlijke auditregistratie. Gate 8 gebruikt demonstratiedata. Niet selecteren is geen afwijzing; uitzonderingen worden alleen expliciet vastgelegd via de secundaire actie.")
