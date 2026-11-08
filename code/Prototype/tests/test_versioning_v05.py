from datetime import date, datetime, timezone

import pytest

from dvk.persistence import SQLiteDatabase
from dvk.versioning import ConfigVersion, PolicyVersion, SoftwareVersion, canonical_json

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc)
EFFECTIVE = date(2026, 9, 1)
COMMIT = "fabbb5f439148e89d1f431f0e0c452b87b6fcc84"


def test_canonical_json_and_hash_are_independent_of_mapping_key_order():
    left = PolicyVersion.create("P1", {"b": 2, "a": 1}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    right = PolicyVersion.create("P2", {"a": 1, "b": 2}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    assert left.content_hash == right.content_hash
    assert len(left.content_hash) == 64


def test_content_change_changes_sha256_hash():
    v1 = ConfigVersion.create("C1", {"maximum": 4}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    v2 = ConfigVersion.create("C2", {"maximum": 5}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    assert v1.content_hash != v2.content_hash


def test_versions_persist_with_exact_content_and_software_commit(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    policy = PolicyVersion.create("policy-v0.5.1", {"required_hours": 10}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    config = ConfigVersion.create("shift-catalog-v1", {"BAR": {"minimum": 2, "maximum": 4}}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    software = SoftwareVersion("software-v0.5", "dvk-0.5", COMMIT, NOW)
    with db.unit_of_work() as uow:
        uow.policy_versions.add(policy); uow.config_versions.add(config); uow.software_versions.add(software); uow.commit()
    with db.unit_of_work() as uow:
        assert uow.policy_versions.get(policy.version_id) == policy
        assert uow.config_versions.get(config.version_id) == config
        assert uow.software_versions.get(software.version_id) == software


def test_version_id_is_append_only_and_cannot_be_overwritten(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    original = PolicyVersion.create("policy-v0.5.1", {"required_hours": 10}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    changed = PolicyVersion.create("policy-v0.5.1", {"required_hours": 12}, created_at=NOW, created_by="admin", effective_from=EFFECTIVE)
    with db.unit_of_work() as uow: uow.policy_versions.add(original); uow.commit()
    with pytest.raises(Exception):
        with db.unit_of_work() as uow:
            uow.policy_versions.add(changed); uow.commit()
    with db.unit_of_work() as uow:
        assert uow.policy_versions.get("policy-v0.5.1") == original


def test_software_version_requires_full_git_commit_id():
    with pytest.raises(ValueError, match="40-character"):
        SoftwareVersion("software-v0.5", "dvk-0.5", "fabbb5f", NOW)
