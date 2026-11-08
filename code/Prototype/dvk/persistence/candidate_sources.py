"""Round-trip the validated planning context without rereading Sportlink exports."""
import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from ..candidate_context import CandidateContext
from ..historical_backlog import HistoricalBacklogSource
from ..model import DutyPosition, Membership, Person, RoleAssignment, SportlinkDutyRegistration
from ..planning import PlanningPeriod
from ..planning_session import PlanningCandidateSources, TZ
from ..programma_adapter import ProgramImportResult, ProgramMatchRecord
from ..programma_client import ProgrammaFetchStats
from ..programma_team_adapter import LinkedProgramImportResult
from ..real_data_import import (
    CommitteeMembership, DataQualitySignal, DiagnosticSourceRecord, DutyImportRecord,
    FootballParticipation, Provenance, RealDataImportResult, RealTeamMembership,
)
from ..team_linking import CkcTeamIdentity, ProgramTeamLink
from ..workstream_model import Match, TeamMembership


def _encode(value):
    return str(value) if isinstance(value, Path) else value.isoformat()


def encode_sources(session_id, sources):
    return json.dumps({"session_id": session_id, **asdict(sources)}, default=_encode)


def _dates(row, *keys):
    return {**row, **{key: date.fromisoformat(row[key]) if row[key] else None for key in keys}}


def _timestamp(value):
    return datetime.fromisoformat(value) if value else None


def _provenance(row):
    return Provenance(**{**row, "imported_at": _timestamp(row["imported_at"])}) if row else None


def _duty(row):
    return DutyImportRecord(SportlinkDutyRegistration(**row["registration"]), row["source_remaining_hours"],
                            DutyPosition(**row["position"]))


def _source(row):
    return RealDataImportResult(
        persons=tuple(Person(**{**p, "parent_names": tuple(p["parent_names"])}) for p in
                      (_dates(item, "birth_date") for item in row["persons"])),
        memberships=tuple(Membership(**_dates(item, "start_date", "end_date")) for item in row["memberships"]),
        football_participations=tuple(FootballParticipation(**item) for item in row["football_participations"]),
        roles=tuple(RoleAssignment(**{**_dates(item, "start_date", "end_date"),
                                      "provenance": _provenance(item["provenance"])}) for item in row["roles"]),
        committees=tuple(CommitteeMembership(**{**_dates(item, "start_date", "end_date"),
                                                "provenance": _provenance(item["provenance"])})
                         for item in row["committees"]),
        team_memberships=tuple(RealTeamMembership(**item) for item in row["team_memberships"]),
        duty_records=tuple(_duty(item) for item in row["duty_records"]),
        provenance=tuple(_provenance(item) for item in row["provenance"]),
        signals=tuple(DataQualitySignal(**item) for item in row["signals"]),
        source_dates=tuple((name, date.fromisoformat(value)) for name, value in row["source_dates"]),
        membership_as_of=tuple(tuple(item) for item in row["membership_as_of"]),
        diagnostic_records=tuple(DiagnosticSourceRecord(**{**item, "values": tuple(map(tuple, item["values"]))})
                                 for item in row["diagnostic_records"]),
    )


def _match(row):
    return Match(**{**row, "starts_at": _timestamp(row["starts_at"]).astimezone(TZ)})


def _match_record(row):
    return ProgramMatchRecord(**{**row, "match": _match(row["match"])})


def _program(row):
    if row is None:
        return None
    program = row["program"]
    return LinkedProgramImportResult(
        program=ProgramImportResult(
            matches=tuple(_match(item) for item in program["matches"]),
            records=tuple(_match_record(item) for item in program["records"]),
            excluded_records=tuple(_match_record(item) for item in program["excluded_records"]),
            provenance=tuple(_provenance(item) for item in program["provenance"]),
            signals=tuple(DataQualitySignal(**item) for item in program["signals"]),
            retrieved_at=_timestamp(program["retrieved_at"]),
        ),
        links=tuple(ProgramTeamLink(**{**item, "normalizations": tuple(item["normalizations"]),
                                     "candidates": tuple(CkcTeamIdentity(**c) for c in item["candidates"])})
                    for item in row["links"]),
        signals=tuple(DataQualitySignal(**item) for item in row["signals"]),
        _team_memberships=tuple(TeamMembership(**_dates(item, "start_date", "end_date"))
                                for item in row["_team_memberships"]),
        _unresolved_memberships=row["_unresolved_memberships"],
    )


def _history(row):
    if row is None:
        return None
    return HistoricalBacklogSource(
        row["available"], tuple(_duty(item) for item in row["records"]),
        tuple(DataQualitySignal(**item) for item in row["signals"]), row["message"], _timestamp(row["loaded_at"]),
    )


def decode_sources(payload, session_id):
    data = json.loads(payload)
    if data["session_id"] != session_id:
        return None
    row = data["context"]
    context = None
    if row is not None:
        context = CandidateContext(
            period=PlanningPeriod(**_dates(row["period"], "start", "end")),
            source_period=row["source_period"], source=_source(row["source"]),
            program=_program(row["program"]), fetched_at=_timestamp(row["fetched_at"]),
            stats=ProgrammaFetchStats(**row["stats"]), error=row["error"], source_files=tuple(row["source_files"]),
            historical_backlog=_history(row["historical_backlog"]), csv_loaded_at=_timestamp(row["csv_loaded_at"]),
            source_directory=Path(row["source_directory"]) if row["source_directory"] else None,
        )
    return PlanningCandidateSources(context, data["error"], data["initial_volunteer_error"])
