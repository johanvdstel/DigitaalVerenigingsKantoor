from __future__ import annotations

from datetime import date, datetime, time, timedelta

import streamlit as st

from dvk.application_services import PlanningApplicationService
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_model import DutyService, Match


DAGEN = ("ma", "di", "wo", "do", "vr", "za", "zo")


def _datum_met_dag(moment: datetime) -> str:
    return f"{DAGEN[moment.weekday()]} {moment:%d-%m}"


st.set_page_config(page_title="DVK — Ledendienst Planning", page_icon="📋", layout="wide")
st.title("Digitaal Verenigings Kantoor (DVK)")
st.subheader("Ledendienst Planning")
st.caption("Alleen-lezen planningsoverzicht — Prototype v0.5")


def _demo_data(start: date):
    monday = start - timedelta(days=start.weekday())
    services = (
        DutyService("BAR-WO-1", "Bardienst", datetime.combine(monday + timedelta(days=2), time(19, 0)), datetime.combine(monday + timedelta(days=2), time(22, 0)), "Clubhuis", 2),
        DutyService("BAR-ZA-1", "Bardienst", datetime.combine(monday + timedelta(days=5), time(9, 0)), datetime.combine(monday + timedelta(days=5), time(13, 0)), "Clubhuis", 3),
        DutyService("CK-ZA-1", "Gastvrouw/heer", datetime.combine(monday + timedelta(days=5), time(12, 30)), datetime.combine(monday + timedelta(days=5), time(17, 0)), "Commissiekamer", 1),
    )
    needs = (
        StaffingNeed("BAR-WO-1", 2, 3, 1, 1, 2),
        StaffingNeed("BAR-ZA-1", 3, 5, 3, 0, 2),
        StaffingNeed("CK-ZA-1", 1, 2, 0, 1, 2),
    )
    matches = (
        Match("W-001", "Senioren 1", datetime.combine(monday + timedelta(days=5), time(14, 30)), "home"),
    )
    statuses = (
        PlanningSourceStatus("Sportlink Programma", datetime.now() - timedelta(minutes=18), "actueel"),
        PlanningSourceStatus("Sportlink Vrijwilligers", datetime.now() - timedelta(minutes=12), "actueel"),
        PlanningSourceStatus("Leden- en vrijwilligersgegevens", datetime.now() - timedelta(days=1), "bevestigd"),
    )
    return services, needs, matches, statuses


with st.sidebar:
    st.header("Periode")
    mode = st.radio("Selectie", ("Dag", "Week", "Aangepast"), index=1)
    selected = st.date_input("Vanaf", value=date.today())
    if mode == "Dag":
        period = PlanningPeriod(selected, selected)
    elif mode == "Week":
        monday = selected - timedelta(days=selected.weekday())
        period = PlanningPeriod(monday, monday + timedelta(days=6))
    else:
        until = st.date_input("Tot en met", value=selected + timedelta(days=6), min_value=selected)
        period = PlanningPeriod(selected, until)

identity = Identity("demo-planner", "Demo planner", frozenset({Permission.VIEW_PLANNING}))
services, needs, matches, statuses = _demo_data(period.start)
overview = PlanningApplicationService(identity).build_overview(
    period=period, services=services, staffing_needs=needs, matches=matches,
    source_statuses=statuses,
)

st.write(f"**Periode:** {overview.period.start:%d-%m-%Y} t/m {overview.period.end:%d-%m-%Y}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Diensten", len(overview.services))
c2.metric("Open minimum", sum(row.open_need for row in overview.services))
c3.metric("Bevestigd", sum(row.confirmed_occupancy for row in overview.services))
c4.metric("Resterende capaciteit", sum(row.remaining_capacity for row in overview.services))

st.markdown("### Diensten")
if not overview.services:
    st.info("Geen diensten in de gekozen periode.")
else:
    st.dataframe([
        {
            "Datum": _datum_met_dag(row.starts_at),
            "Tijd": f"{row.starts_at:%H:%M}–{row.ends_at:%H:%M}",
            "Dienst": row.service_type,
            "Locatie": row.location,
            "Min": row.minimum_staff,
            "Max": row.maximum_staff,
            "Bevestigd": row.confirmed_occupancy,
            "Open minimum": row.open_need,
            "Vrije capaciteit": row.remaining_capacity,
            "Thuiswedstrijd": row.match_team_id or "—",
            "Aanvang wedstrijd": row.match_starts_at.strftime("%H:%M") if row.match_starts_at else "—",
        }
        for row in overview.services
    ], use_container_width=True, hide_index=True)

st.markdown("### Wedstrijden")
if not overview.matches:
    st.info("Geen wedstrijden in de gekozen periode.")
else:
    st.dataframe([
        {
            "Datum": _datum_met_dag(match.starts_at),
            "Tijd": match.starts_at.strftime("%H:%M"),
            "Team": match.team_id,
            "Thuis/uit": "Thuis" if match.home_away.strip().lower() == "home" else "Uit",
        }
        for match in overview.matches
    ], use_container_width=True, hide_index=True)

st.markdown("### Databronnen")
st.dataframe([
    {
        "Databron": status.source,
        "Laatst opgehaald": status.fetched_at.strftime("%d-%m-%Y %H:%M") if status.fetched_at else "onbekend",
        "Status": status.status,
    }
    for status in overview.source_statuses
], use_container_width=True, hide_index=True)

st.markdown("### Datakwaliteit")
if overview.data_quality_signals:
    st.dataframe([
        {"Ernst": signal.severity, "Code": signal.code, "Melding": signal.message}
        for signal in overview.data_quality_signals
    ], use_container_width=True, hide_index=True)
else:
    st.success("Geen datakwaliteitssignalen voor deze planning.")

st.caption("Gate 7 gebruikt demonstratiedata via dezelfde alleen-lezen PlanningApplicationService. De UI bevat geen planningsregels of mutatieacties.")
