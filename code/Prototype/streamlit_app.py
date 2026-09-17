from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import uuid4

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
    "Planning": "planning",
    "Brongegevens onjuist": "source_data_incorrect",
    "Anders": "other",
}


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


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
    matches = (Match("W-001", "Senioren 1", datetime.combine(monday + timedelta(days=5), time(14, 30)), "home"),)
    statuses = (
        PlanningSourceStatus("Sportlink Wedstrijden", datetime.now() - timedelta(minutes=18), "actueel"),
        PlanningSourceStatus("Sportlink Diensten", datetime.now() - timedelta(minutes=12), "actueel"),
        PlanningSourceStatus("Leden- en vrijwilligersgegevens", datetime.now() - timedelta(days=1), "bevestigd"),
    )
    return services, needs, matches, statuses


def _demo_proposals(service: DutyService, need: StaffingNeed):
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"], W_CASE_BY_ID["W09"])
    memberships = tuple(
        TeamMembership(case.person.person_id, "SEN-8", service.starts_at.date() - timedelta(days=60), service.starts_at.date() + timedelta(days=300))
        for case in cases
    )
    assessments = tuple(assess_candidate(case, service, memberships, (), TODAY) for case in cases)
    eligible = tuple(a for a in assessments if a.eligible)
    priorities = prioritize_candidates(eligible, cases, service.starts_at.date())
    by_person = {p.person_id: p for p in priorities}
    proposals = tuple(
        create_assignment_proposal(
            f"DEMO-{service.service_id}-{case.person.person_id}", service, case,
            next(a for a in eligible if a.person_id == case.person.person_id),
            by_person[case.person.person_id], (),
        )
        for case in cases if case.person.person_id in by_person
    )
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
if not overview.services: st.info("Geen diensten in de gekozen periode.")
else:
    st.dataframe([{"Datum": _datum_met_dag(r.starts_at), "Tijd": f"{r.starts_at:%H:%M}–{r.ends_at:%H:%M}", "Dienst": r.service_type, "Locatie": r.location, "Min": r.minimum_staff, "Max": r.maximum_staff, "Bevestigd": r.confirmed_occupancy, "Open minimum": r.open_need, "Vrije capaciteit": r.remaining_capacity} for r in overview.services], use_container_width=True, hide_index=True)

st.markdown("### Kandidaten en voorstellen")
if not overview.services:
    st.info("Selecteer een periode met diensten om kandidaten te bekijken.")
else:
    selected_service_id = st.selectbox(
        "Dienst",
        [r.service_id for r in overview.services],
        format_func=lambda sid: f"{_datum_met_dag(service_by_id[sid].starts_at)} · {service_by_id[sid].service_type} · {service_by_id[sid].starts_at:%H:%M}",
    )
    service = service_by_id[selected_service_id]
    need = need_by_service[selected_service_id]
    cases, planned = _demo_proposals(service, need)
    case_by_person = {case.person.person_id: case for case in cases}
    if not planned:
        st.info("Geen kandidaatvoorstellen: de maximumbezetting is bereikt of er zijn geen geschikte kandidaten.")
    else:
        st.dataframe([{
            "Rang": item.proposal.priority_rank,
            "Kandidaat": case_by_person[item.proposal.person_id].person.name,
            "Resterende uren": item.proposal.E,
            "Doel": "Minimumbezetting" if item.staffing_purpose == "minimum_coverage" else "Aanvullende capaciteit",
            "Wedstrijdcontext": item.proposal.match_relation,
            "Waarom": "; ".join(item.proposal.applied_priority_rules),
        } for item in planned], use_container_width=True, hide_index=True)

        proposal_ids = [item.proposal.proposal_id for item in planned]
        chosen_id = st.selectbox("Kandidaat beoordelen", proposal_ids, format_func=lambda pid: case_by_person[next(i.proposal.person_id for i in planned if i.proposal.proposal_id == pid)].person.name)
        chosen = next(item.proposal for item in planned if item.proposal.proposal_id == chosen_id)
        chosen_case = case_by_person[chosen.person_id]
        st.caption("De DVK doet een voorstel. Pas na jouw expliciete goedkeuring ontstaat een DutyAssignment.")
        left, right = st.columns(2)
        with left:
            if st.button("Goedkeuren", type="primary", use_container_width=True):
                result = ProposalDecisionApplicationService(identity).approve(chosen, service, chosen_case, assignment_id=f"UI-{uuid4()}")
                st.session_state[f"decision-{chosen.proposal_id}"] = result
        with right:
            with st.form(f"reject-{chosen.proposal_id}"):
                reason_label = st.selectbox("Redencategorie", tuple(REJECTION_LABELS))
                reason = st.text_input("Toelichting afwijzing")
                rejected = st.form_submit_button("Afwijzen", use_container_width=True)
                if rejected:
                    if not reason.strip(): st.error("Een toelichting is verplicht bij afwijzen.")
                    else:
                        result = ProposalDecisionApplicationService(identity).reject(chosen, chosen_case, reason_category=REJECTION_LABELS[reason_label], reason=reason)
                        st.session_state[f"decision-{chosen.proposal_id}"] = result
        result = st.session_state.get(f"decision-{chosen.proposal_id}")
        if result:
            if result.decision.decision == "approved": st.success(f"Goedgekeurd door {result.decision.decided_by}. DutyAssignment {result.assignment.assignment_id} is aangemaakt.")
            else: st.warning(f"Afgewezen door {result.decision.decided_by}: {result.decision.reason}")

st.markdown("### Wedstrijden")
if not overview.matches: st.info("Geen wedstrijden in de gekozen periode.")
else: st.dataframe([{"Datum": _datum_met_dag(m.starts_at), "Tijd": m.starts_at.strftime("%H:%M"), "Team": m.team_id, "Thuis/uit": "Thuis" if m.home_away.strip().lower() == "home" else "Uit"} for m in overview.matches], use_container_width=True, hide_index=True)

st.markdown("### Databronnen")
st.dataframe([{"Databron": s.source, "Laatst opgehaald": s.fetched_at.strftime("%d-%m-%Y %H:%M") if s.fetched_at else "onbekend", "Status": s.status} for s in overview.source_statuses], use_container_width=True, hide_index=True)
st.markdown("### Datakwaliteit")
if overview.data_quality_signals: st.dataframe([{"Ernst": s.severity, "Code": s.code, "Melding": s.message} for s in overview.data_quality_signals], use_container_width=True, hide_index=True)
else: st.success("Geen datakwaliteitssignalen voor deze planning.")
st.caption("Gate 8 gebruikt demonstratiedata. Kandidaatselectie, prioritering en beslisregels zitten buiten Streamlit; mutaties lopen via ProposalDecisionApplicationService en autorisatie.")
