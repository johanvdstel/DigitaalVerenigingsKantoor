from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from dvk.application_services import NoShowApplicationService, PlanningApplicationService, ProposalDecisionApplicationService, ReplacementDutyApplicationService
from dvk.candidate_selection import assess_candidate
from dvk.no_show import NoShowEvent, season_id
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.proposal_planning import plan_proposals
from dvk.replacement_duty import ReplacementDuty
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership

DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")
REJECTION_LABELS = {"Persoonlijke omstandigheid": "personal_circumstance", "Niet geschikt voor deze dienst": "unsuitable_for_service", "Brongegevens kloppen niet": "source_data_incorrect", "Andere bijzonderheid": "other"}
MATCH_LABELS = {"no_match_context": "Geen wedstrijd", "no_match_that_day": "Geen wedstrijd", "home_match_overlaps_service": "Thuiswedstrijd overlapt", "home_match_same_day": "Thuiswedstrijd", "away_match_overlaps_service": "Uitwedstrijd overlapt", "away_match_same_day": "Uitwedstrijd"}
RULE_LABELS = {"previous_season_backlog_before_december": "Openstaande uren uit vorig seizoen meegewogen", "home_match_overlap": "Thuiswedstrijd sluit aan op dienst", "home_match_same_day": "Thuiswedstrijd op dezelfde dag", "away_match_emergency": "Uitwedstrijd meegewogen als noodoptie"}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


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
    monday = start - timedelta(days=start.weekday())
    services = (
        DutyService("BAR-WO-1", "Bardienst", datetime.combine(monday + timedelta(days=2), time(19)), datetime.combine(monday + timedelta(days=2), time(22)), "Clubhuis", 2),
        DutyService("BAR-ZA-1", "Bardienst", datetime.combine(monday + timedelta(days=5), time(9)), datetime.combine(monday + timedelta(days=5), time(13)), "Clubhuis", 3),
        DutyService("CK-ZA-1", "Gastvrouw/heer", datetime.combine(monday + timedelta(days=5), time(12, 30)), datetime.combine(monday + timedelta(days=5), time(17)), "Commissiekamer", 1),
    )
    needs = (StaffingNeed("BAR-WO-1", 2, 3, 1, 1, 2), StaffingNeed("BAR-ZA-1", 3, 5, 3, 0, 2), StaffingNeed("CK-ZA-1", 1, 2, 0, 1, 2))
    matches = (
        Match("W-001", "Senioren 1", datetime.combine(monday + timedelta(days=5), time(14, 30)), "home"),
        Match("W-002", "SEN-8", datetime.combine(monday + timedelta(days=5), time(12, 15)), "away"),
        Match("W-003", "JO17-1", datetime.combine(monday + timedelta(days=6), time(10, 30)), "away"),
    )
    statuses = (PlanningSourceStatus("Sportlink Wedstrijden", datetime.now() - timedelta(minutes=18), "actueel"), PlanningSourceStatus("Sportlink Diensten", datetime.now() - timedelta(minutes=12), "actueel"), PlanningSourceStatus("Leden- en vrijwilligersgegevens", datetime.now() - timedelta(days=1), "bevestigd"))
    return services, needs, matches, statuses


def _demo_proposals(service: DutyService, need: StaffingNeed, matches: tuple[Match, ...], *, proposal_run_id: str | None = None):
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"], W_CASE_BY_ID["W09"])
    memberships = tuple(TeamMembership(case.person.person_id, "SEN-8", service.starts_at.date() - timedelta(days=60), service.starts_at.date() + timedelta(days=300)) for case in cases)
    assessments = tuple(assess_candidate(case, service, memberships, matches, TODAY) for case in cases)
    eligible = tuple(a for a in assessments if a.eligible)
    priorities = prioritize_candidates(eligible, cases, service.starts_at.date())
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
    assignment_rows = NoShowApplicationService(uow, identity).available_assignments()
if not assignment_rows:
    st.info("Nog geen inroosteringen beschikbaar waarop een no-show kan worden geregistreerd.")
else:
    assignment_options = {}
    for assignment in assignment_rows:
        service_info = service_by_id.get(assignment.service_id)
        person_name = next((case.person.name for case in W_CASE_BY_ID.values() if case.person.person_id == assignment.person_id), assignment.person_id)
        if service_info:
            assignment_options[assignment.assignment_id] = f"{_datum_met_dag(service_info.starts_at)} {service_info.starts_at:%H:%M}–{service_info.ends_at:%H:%M} — {service_info.service_type} — {person_name}"
        else:
            assignment_options[assignment.assignment_id] = f"{assignment.service_id} — {person_name}"
    with st.form("no-show-form"):
        assignment_id = st.selectbox("Inroostering", tuple(assignment_options), format_func=assignment_options.get)
        submitted_no_show = st.form_submit_button("No-show bevestigen", type="primary")
    if submitted_no_show:
        with database.unit_of_work() as uow:
            assignment = uow.assignments.get(assignment_id)
            service_info = service_by_id.get(assignment.service_id)
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

st.markdown("### Vervangende inzet")
st.caption("Na een eerste no-show regelt de betrokkene zelf een nieuwe dienst. Een bevoegd lid van de Vrijwilligerscommissie koppelt die inroostering en bevestigt na afloop of de vervangende inzet is uitgevoerd.")
with database.unit_of_work() as uow:
    recent_assignments = NoShowApplicationService(uow, identity).available_assignments()
    first_no_shows = []
    for assignment in recent_assignments:
        no_show = uow.no_shows.for_assignment(assignment.assignment_id)
        if no_show is None or no_show.status != "valid" or uow.replacements.for_no_show(no_show.no_show_id) is not None:
            continue
        state = ReplacementDutyApplicationService(uow, identity)._state(no_show.person_id, no_show.season)
        if state.counter == 1 and state.assessment and state.assessment.no_show_id == no_show.no_show_id:
            first_no_shows.append(no_show)
    pending_replacements = tuple(
        replacement
        for no_show in first_no_shows
        for replacement in ()
    )
    all_replacements = tuple(
        replacement
        for no_show in (uow.no_shows.for_assignment(a.assignment_id) for a in recent_assignments)
        if no_show is not None
        for replacement in (uow.replacements.for_no_show(no_show.no_show_id),)
        if replacement is not None and not replacement.completed
    )

if first_no_shows:
    no_show_labels = {n.no_show_id: f"{n.occurred_at:%d-%m-%Y} — {next((c.person.name for c in W_CASE_BY_ID.values() if c.person.person_id == n.person_id), n.person_id)}" for n in first_no_shows}
    with st.form("replacement-link-form"):
        repair_no_show_id = st.selectbox("Eerste no-show", tuple(no_show_labels), format_func=no_show_labels.get)
        selected_no_show = next(n for n in first_no_shows if n.no_show_id == repair_no_show_id)
        eligible_assignments = tuple(a for a in recent_assignments if a.person_id == selected_no_show.person_id and a.assignment_id != selected_no_show.assignment_id)
        replacement_labels = {a.assignment_id: f"{a.service_id} — {next((c.person.name for c in W_CASE_BY_ID.values() if c.person.person_id == a.person_id), a.person_id)}" for a in eligible_assignments}
        replacement_assignment_id = st.selectbox("Zelf geregelde vervangende inroostering", tuple(replacement_labels), format_func=replacement_labels.get) if replacement_labels else None
        link_submitted = st.form_submit_button("Vervangende inzet koppelen", disabled=not replacement_labels)
    if link_submitted and replacement_assignment_id:
        with database.unit_of_work() as uow:
            state = ReplacementDutyApplicationService(uow, identity).register_replacement(
                ReplacementDuty(f"RV-{uuid4()}", repair_no_show_id, replacement_assignment_id, selected_no_show.person_id, selected_no_show.season, datetime.now().astimezone(), identity.subject_id)
            )
        st.success("Vervangende inzet geregeld. De actieve teller blijft 1 totdat uitvoering is bevestigd.")
        st.rerun()

if all_replacements:
    st.write("**Uitvoering nog te bevestigen**")
    replacement_labels = {r.replacement_id: f"{r.assignment_id} — {next((c.person.name for c in W_CASE_BY_ID.values() if c.person.person_id == r.person_id), r.person_id)}" for r in all_replacements}
    selected_replacement_id = st.selectbox("Vervangende inzet", tuple(replacement_labels), format_func=replacement_labels.get)
    c_done, c_noshow = st.columns(2)
    if c_done.button("Uitgevoerd bevestigen", type="primary"):
        with database.unit_of_work() as uow:
            state = ReplacementDutyApplicationService(uow, identity).complete_replacement(selected_replacement_id, completed_at=datetime.now().astimezone())
        st.success("Vervangende inzet uitgevoerd. Actieve no-showteller is teruggezet naar 0.")
        st.rerun()
    if c_noshow.button("No-show vastleggen voor vervangende inzet"):
        replacement = next(r for r in all_replacements if r.replacement_id == selected_replacement_id)
        with database.unit_of_work() as uow:
            assignment = uow.assignments.get(replacement.assignment_id)
            now = datetime.now().astimezone()
            assessment = NoShowApplicationService(uow, identity).register(
                NoShowEvent(f"NS-{uuid4()}", assignment.assignment_id, assignment.person_id, now, now, identity.subject_id, season_id(now.date()))
            )
        st.warning(f"No-show {assessment.counter} geregistreerd. De vervangende inzet heeft de eerdere no-show niet hersteld.")
        st.rerun()
elif not first_no_shows:
    st.info("Geen openstaande vervangende inzet na een eerste no-show.")

st.markdown("### Wedstrijden")
if not overview.matches: st.info("Geen wedstrijden in de gekozen periode.")
else: st.dataframe([{"Datum": _datum_met_dag(m.starts_at), "Tijd": m.starts_at.strftime("%H:%M"), "Team": m.team_id, "Thuis/uit": "Thuis" if m.home_away.strip().lower() == "home" else "Uit"} for m in overview.matches], use_container_width=True, hide_index=True, height=230)
st.markdown("### Databronnen")
st.dataframe([{"Databron": s.source, "Laatst opgehaald": s.fetched_at.strftime("%d-%m-%Y %H:%M") if s.fetched_at else "onbekend", "Status": s.status} for s in overview.source_statuses], use_container_width=True, hide_index=True)
st.markdown("### Datakwaliteit")
if overview.data_quality_signals: st.dataframe([{"Ernst": s.severity, "Code": s.code, "Melding": s.message} for s in overview.data_quality_signals], use_container_width=True, hide_index=True)
else: st.success("Geen datakwaliteitssignalen voor deze planning.")
st.caption("Gate 10 ondersteunt de door de Vrijwilligerscommissie bevestigde no-show en vervangende inzet. Gate 8 gebruikt demonstratiedata. Niet selecteren is geen afwijzing; uitzonderingen worden alleen expliciet vastgelegd via de secundaire actie.")
