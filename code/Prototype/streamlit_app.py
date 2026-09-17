from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import uuid4

import pandas as pd
import streamlit as st

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_selection import assess_candidate
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.proposal_planning import plan_proposals
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership

DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")
REJECTION_LABELS = {
    "Persoonlijke omstandigheid": "personal_circumstance",
    "Niet geschikt voor deze dienst": "unsuitable_for_service",
    "Brongegevens kloppen niet": "source_data_incorrect",
    "Andere bijzonderheid": "other",
}
MATCH_LABELS = {
    "no_match_context": "Geen wedstrijdcontext nodig",
    "no_match_that_day": "Geen wedstrijd op deze dag",
    "home_overlap": "Thuiswedstrijd overlapt met dienst",
    "home_same_day": "Thuiswedstrijd op dezelfde dag",
    "away_overlap": "Uitwedstrijd overlapt met dienst",
    "away_same_day": "Uitwedstrijd op dezelfde dag",
}
RULE_LABELS = {
    "higher_current_E": "Veel openstaande vrijwilligersuren",
    "previous_season_backlog_before_december": "Achterstand vorig seizoen meegewogen",
    "home_match_overlap": "Thuiswedstrijd sluit aan op dienst",
    "home_match_same_day": "Thuiswedstrijd op dezelfde dag",
}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


def _vriendelijke_wedstrijdcontext(value: str) -> str:
    return MATCH_LABELS.get(value, value.replace("_", " ").capitalize())


def _vriendelijke_waarom(rules: tuple[str, ...]) -> str:
    if not rules:
        return "Geschikt volgens de planningsregels"
    return "; ".join(RULE_LABELS.get(rule, rule.replace("_", " ").capitalize()) for rule in rules)


def _demo_data(start: date):
    monday = start - timedelta(days=start.weekday())
    services = (
        DutyService("BAR-WO-1", "Bardienst", datetime.combine(monday + timedelta(days=2), time(19)), datetime.combine(monday + timedelta(days=2), time(22)), "Clubhuis", 2),
        DutyService("BAR-ZA-1", "Bardienst", datetime.combine(monday + timedelta(days=5), time(9)), datetime.combine(monday + timedelta(days=5), time(13)), "Clubhuis", 3),
        DutyService("CK-ZA-1", "Gastvrouw/heer", datetime.combine(monday + timedelta(days=5), time(12, 30)), datetime.combine(monday + timedelta(days=5), time(17)), "Commissiekamer", 1),
    )
    needs = (
        StaffingNeed("BAR-WO-1", 2, 3, 1, 1, 2),
        StaffingNeed("BAR-ZA-1", 3, 5, 3, 0, 2),
        StaffingNeed("CK-ZA-1", 1, 2, 0, 1, 2),
    )
    matches = (
        Match("W-001", "Senioren 1", datetime.combine(monday + timedelta(days=5), time(14, 30)), "home"),
        Match("W-002", "Senioren 8", datetime.combine(monday + timedelta(days=5), time(12, 15)), "away"),
        Match("W-003", "JO17-1", datetime.combine(monday + timedelta(days=6), time(10, 30)), "away"),
    )
    statuses = (
        PlanningSourceStatus("Sportlink Wedstrijden", datetime.now() - timedelta(minutes=18), "actueel"),
        PlanningSourceStatus("Sportlink Diensten", datetime.now() - timedelta(minutes=12), "actueel"),
        PlanningSourceStatus("Leden- en vrijwilligersgegevens", datetime.now() - timedelta(days=1), "bevestigd"),
    )
    return services, needs, matches, statuses


def _demo_proposals(service: DutyService, need: StaffingNeed):
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"], W_CASE_BY_ID["W09"])
    memberships = tuple(TeamMembership(case.person.person_id, "SEN-8", service.starts_at.date() - timedelta(days=60), service.starts_at.date() + timedelta(days=300)) for case in cases)
    assessments = tuple(assess_candidate(case, service, memberships, (), TODAY) for case in cases)
    eligible = tuple(a for a in assessments if a.eligible)
    priorities = prioritize_candidates(eligible, cases, service.starts_at.date())
    by_person = {p.person_id: p for p in priorities}
    proposals = tuple(create_assignment_proposal(f"DEMO-{service.service_id}-{case.person.person_id}", service, case, next(a for a in eligible if a.person_id == case.person.person_id), by_person[case.person.person_id], ()) for case in cases if case.person.person_id in by_person)
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
        monday = selected - timedelta(days=selected.weekday())
        period = PlanningPeriod(monday, monday + timedelta(days=6))
    else:
        until = st.date_input("Tot en met", value=selected + timedelta(days=6), min_value=selected)
        period = PlanningPeriod(selected, until)

identity = Identity("demo-planner", "Demo planner", frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL}))
services, needs, matches, statuses = _demo_data(period.start)
overview = PlanningApplicationService(identity).build_overview(period=period, services=services, staffing_needs=needs, matches=matches, source_statuses=statuses)
need_by_service = {need.service_id: need for need in needs}
service_by_id = {service.service_id: service for service in services}

st.write(f"**Periode:** {overview.period.start:%d-%m-%Y} t/m {overview.period.end:%d-%m-%Y}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Diensten", len(overview.services)); c2.metric("Open minimum", sum(r.open_need for r in overview.services)); c3.metric("Bevestigd", sum(r.confirmed_occupancy for r in overview.services)); c4.metric("Resterende capaciteit", sum(r.remaining_capacity for r in overview.services))

st.markdown("### Diensten")
selected_service_id = None
if not overview.services:
    st.info("Geen diensten in de gekozen periode.")
else:
    previous_service = st.session_state.get("selected_service_id")
    service_rows = [{"Kies": r.service_id == previous_service, "service_id": r.service_id, "Datum": _datum_met_dag(r.starts_at), "Tijd": f"{r.starts_at:%H:%M}–{r.ends_at:%H:%M}", "Dienst": r.service_type, "Locatie": r.location, "Min": r.minimum_staff, "Max": r.maximum_staff, "Bevestigd": r.confirmed_occupancy, "Open minimum": r.open_need, "Vrije capaciteit": r.remaining_capacity} for r in overview.services]
    edited_services = st.data_editor(
        pd.DataFrame(service_rows),
        hide_index=True,
        use_container_width=True,
        height=210,
        disabled=["service_id", "Datum", "Tijd", "Dienst", "Locatie", "Min", "Max", "Bevestigd", "Open minimum", "Vrije capaciteit"],
        column_config={"service_id": None, "Kies": st.column_config.CheckboxColumn("Kies", help="Selecteer één dienst")},
        key="services_editor",
    )
    selected_rows = edited_services[edited_services["Kies"]]
    if len(selected_rows) > 1:
        st.error("Selecteer maximaal één dienst.")
    elif len(selected_rows) == 1:
        selected_service_id = selected_rows.iloc[0]["service_id"]
        st.session_state["selected_service_id"] = selected_service_id
    else:
        st.session_state.pop("selected_service_id", None)

st.markdown("### Kandidaten en voorstellen")
if selected_service_id is None:
    st.info("Selecteer eerst één dienst in de tabel hierboven.")
else:
    service = service_by_id[selected_service_id]
    need = need_by_service[selected_service_id]
    cases, planned = _demo_proposals(service, need)
    case_by_person = {case.person.person_id: case for case in cases}
    if not planned:
        st.info("Geen kandidaatvoorstellen: de maximumbezetting is bereikt of er zijn geen geschikte kandidaten.")
    else:
        st.caption(f"Selecteer maximaal {need.remaining_capacity} kandidaat/kandidaten. Niet geselecteerde kandidaten blijven beschikbaar voor een volgende planning.")
        selected_proposal_ids = []
        with st.container(height=330, border=True):
            header = st.columns((0.7, 0.7, 2.2, 1.5, 1.8, 2.0, 2.4, 0.9))
            for col, text in zip(header, ("Kies", "Rang", "Kandidaat", "Openstaande uren", "Doel", "Wedstrijdcontext", "Waarom", "Meer")):
                col.markdown(f"**{text}**")
            for item in planned:
                proposal = item.proposal
                cols = st.columns((0.7, 0.7, 2.2, 1.5, 1.8, 2.0, 2.4, 0.9))
                if cols[0].checkbox("Selecteer", key=f"pick-{selected_service_id}-{proposal.proposal_id}", label_visibility="collapsed"):
                    selected_proposal_ids.append(proposal.proposal_id)
                cols[1].write(proposal.priority_rank)
                cols[2].write(case_by_person[proposal.person_id].person.name)
                cols[3].write(proposal.E)
                cols[4].write("Minimumbezetting" if item.staffing_purpose == "minimum_coverage" else "Aanvulling tot maximum")
                cols[5].write(_vriendelijke_wedstrijdcontext(proposal.match_relation))
                cols[6].write(_vriendelijke_waarom(proposal.applied_priority_rules))
                with cols[7].popover("⋯"):
                    st.caption("Alleen gebruiken als er een bijzondere reden is om deze kandidaat niet te gebruiken.")
                    with st.form(f"exception-{proposal.proposal_id}"):
                        reason_label = st.selectbox("Reden", tuple(REJECTION_LABELS), key=f"reasoncat-{proposal.proposal_id}")
                        reason = st.text_input("Toelichting", key=f"reason-{proposal.proposal_id}")
                        submitted = st.form_submit_button("Uitzondering vastleggen")
                        if submitted:
                            if not reason.strip():
                                st.error("Een toelichting is verplicht.")
                            else:
                                result = ProposalDecisionApplicationService(identity).reject(proposal, case_by_person[proposal.person_id], reason_category=REJECTION_LABELS[reason_label], reason=reason)
                                st.session_state[f"exception-result-{proposal.proposal_id}"] = result
                    if st.session_state.get(f"exception-result-{proposal.proposal_id}"):
                        st.warning("Uitzondering vastgelegd. De urenpositie blijft ongewijzigd; deze persoon kan bij een volgende planning opnieuw worden voorgesteld.")

        if len(selected_proposal_ids) > need.remaining_capacity:
            st.error(f"Je hebt {len(selected_proposal_ids)} kandidaten geselecteerd. Voor deze dienst zijn nog maximaal {need.remaining_capacity} plaatsen beschikbaar.")
        st.write("De DVK stelt geschikte kandidaten voor. Selecteer wie je wilt inroosteren en bevestig je keuze.")
        if st.button("Selectie bevestigen", type="primary", disabled=(not selected_proposal_ids or len(selected_proposal_ids) > need.remaining_capacity)):
            results = []
            for proposal_id in selected_proposal_ids:
                proposal = next(item.proposal for item in planned if item.proposal.proposal_id == proposal_id)
                results.append(ProposalDecisionApplicationService(identity).approve(proposal, service, case_by_person[proposal.person_id], assignment_id=f"UI-{uuid4()}"))
            st.session_state[f"confirmed-{selected_service_id}"] = results
        confirmed = st.session_state.get(f"confirmed-{selected_service_id}")
        if confirmed:
            names = [case_by_person[result.assignment.person_id].person.name for result in confirmed if result.assignment]
            st.success(f"Inroostering bevestigd voor: {', '.join(names)}.")

st.markdown("### Wedstrijden")
if not overview.matches:
    st.info("Geen wedstrijden in de gekozen periode.")
else:
    st.dataframe(
        [{"Datum": _datum_met_dag(m.starts_at), "Tijd": m.starts_at.strftime("%H:%M"), "Team": m.team_id, "Thuis/uit": "Thuis" if m.home_away.strip().lower() == "home" else "Uit"} for m in overview.matches],
        use_container_width=True,
        hide_index=True,
        height=230,
    )

st.markdown("### Databronnen")
st.dataframe([{"Databron": s.source, "Laatst opgehaald": s.fetched_at.strftime("%d-%m-%Y %H:%M") if s.fetched_at else "onbekend", "Status": s.status} for s in overview.source_statuses], use_container_width=True, hide_index=True)
st.markdown("### Datakwaliteit")
if overview.data_quality_signals: st.dataframe([{"Ernst": s.severity, "Code": s.code, "Melding": s.message} for s in overview.data_quality_signals], use_container_width=True, hide_index=True)
else: st.success("Geen datakwaliteitssignalen voor deze planning.")
st.caption("Gate 8 gebruikt demonstratiedata. Wedstrijden toont alle thuis- en uitwedstrijden binnen de gekozen periode. Niet selecteren is geen afwijzing; uitzonderingen worden alleen expliciet vastgelegd via de secundaire actie.")
