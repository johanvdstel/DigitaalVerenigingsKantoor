from datetime import date, datetime

from dvk.application_services import ProposalDecisionApplicationService
from dvk.candidate_selection import assess_candidate
from dvk.import_management import ImportBatch, ImportStatus, SourceSnapshot
from dvk.persistence import SQLiteDatabase
from dvk.prioritization import prioritize_candidates
from dvk.proposals import create_assignment_proposal
from dvk.run_context import EngineRun, EngineRunStatus
from dvk.security import Identity, Permission
from dvk.versioning import ConfigVersion, PolicyVersion, SoftwareVersion
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, TeamMembership


def test_v07_durable_chain_reconstructs_after_database_reopen(tmp_path):
    path = tmp_path / "dvk.sqlite"
    db = SQLiteDatabase(path)
    now = datetime(2026, 9, 17, 20, 0)
    case = W_CASE_BY_ID["W08"]
    service = DutyService("BAR-V07", "bardienst", datetime(2026, 9, 18, 18), datetime(2026, 9, 18, 22), "Clubhuis", 1)
    teams = (TeamMembership(case.person.person_id, "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),)
    assessment = assess_candidate(case, service, teams, (), TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    run = EngineRun("RUN-V07", now, "planner-1", date(2026, 9, 18), date(2026, 9, 18), EngineRunStatus.COMPLETED, ("SNAP-V07",), (), "policy-v07", "config-v07", "software-v07", now)
    proposal = create_assignment_proposal("P-V07", service, case, assessment, priority, (), engine_run=run)
    identity = Identity("planner-1", "Planner", frozenset({Permission.DECIDE_PROPOSAL}))

    with db.unit_of_work() as uow:
        policy = PolicyVersion.create("policy-v07", {"norm": 10}, created_at=now, created_by="admin", effective_from=date(2026, 7, 1))
        config = ConfigVersion.create("config-v07", {"shift": "bar"}, created_at=now, created_by="admin", effective_from=date(2026, 7, 1))
        software = SoftwareVersion("software-v07", "v0.5-test", "a" * 40, now)
        uow.policy_versions.add(policy); uow.config_versions.add(config); uow.software_versions.add(software)
        batch = ImportBatch("B-V07", "Sportlink", "leden", "2026-2027", now, "admin", ImportStatus.CONFIRMED, confirmed_at=now, confirmed_by="admin")
        uow.import_batches.add(batch)
        uow.snapshots.add(SourceSnapshot("SNAP-V07", "B-V07", "Sportlink", "leden", "2026-2027", now), ())
        uow.engine_runs.add(run)
        ProposalDecisionApplicationService(identity, uow=uow).approve(proposal, service, case, assignment_id="A-V07")

    reopened = SQLiteDatabase(path)
    with reopened.unit_of_work() as uow:
        assignment = uow.assignments.get("A-V07")
        assert assignment is not None
        decision = uow.decisions.get(assignment.proposal_id)
        proposal2 = uow.proposals.get(assignment.proposal_id)
        assert decision is not None and proposal2 is not None
        run2 = uow.engine_runs.get(proposal2.engine_run_id)
        assert run2 is not None
        assert decision.decided_by == "planner-1"
        assert decision.decided_at is not None
        assert assignment.decided_at == decision.decided_at
        assert run2.snapshot_ids == ("SNAP-V07",)
        assert uow.snapshots.get("SNAP-V07") is not None
        assert uow.policy_versions.get(run2.policy_version).version_id == "policy-v07"
        assert uow.config_versions.get(run2.config_version).version_id == "config-v07"
        assert uow.software_versions.get(run2.engine_version).version_id == "software-v07"
