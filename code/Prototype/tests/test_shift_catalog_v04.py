from __future__ import annotations

from datetime import datetime, timezone

from dvk.shift_catalog import ShiftCatalogAdapter

IMPORTED_AT = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)


def row(**overrides):
    data = {
        "task_code": "442",
        "service_type": "Commissiekamer",
        "duration_hours": "2.5",
        "minimum_staff": "1",
        "maximum_staff": "2",
    }
    data.update(overrides)
    return data


def test_r12_imports_corrected_commissiekamer_code_442():
    result = ShiftCatalogAdapter().import_rows([row()], imported_at=IMPORTED_AT)
    definition = result.definitions[0]
    assert definition.task_code == "442"
    assert definition.minimum_staff == 1
    assert definition.maximum_staff == 2
    assert not result.signals


def test_r12_741_is_one_definition_with_friday_staffing_rule():
    result = ShiftCatalogAdapter().import_rows([
        row(
            task_code="741", service_type="Bar weekend", minimum_staff="2", maximum_staff="4",
            staffing_rules=[{"condition": "vrijdag", "minimum_staff": 1, "maximum_staff": 2}],
        )
    ], imported_at=IMPORTED_AT)
    definition = result.definitions[0]
    assert definition.staffing_for() == (2, 4)
    assert definition.staffing_for("vrijdag") == (1, 2)
    assert not result.signals


def test_r12_candidate_target_uses_applicable_maximum():
    result = ShiftCatalogAdapter().import_rows([
        row(
            task_code="741", service_type="Bar weekend", minimum_staff="2", maximum_staff="4",
            staffing_rules=[{"condition": "vrijdag", "minimum_staff": 1, "maximum_staff": 2}],
        )
    ], imported_at=IMPORTED_AT)
    definition = result.definitions[0]
    assert definition.candidate_target() == 4
    assert definition.candidate_target("vrijdag") == 2


def test_r12_temporary_capacity_rule_can_raise_candidate_target():
    result = ShiftCatalogAdapter().import_rows([
        row(
            task_code="741", service_type="Bar weekend", minimum_staff="2", maximum_staff="4",
            staffing_rules=[{"condition": "groot-feest", "minimum_staff": 2, "maximum_staff": 6}],
        )
    ], imported_at=IMPORTED_AT)
    definition = result.definitions[0]
    assert definition.staffing_for("groot-feest") == (2, 6)
    assert definition.candidate_target("groot-feest") == 6


def test_r12_service_uses_applicable_minimum_as_operational_requirement():
    adapter = ShiftCatalogAdapter()
    result = adapter.import_rows([
        row(
            task_code="741", service_type="Bar weekend", minimum_staff="2", maximum_staff="4",
            staffing_rules=[{"condition": "vrijdag", "minimum_staff": 1, "maximum_staff": 2}],
        )
    ], imported_at=IMPORTED_AT)
    starts_at = datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc)
    service = adapter.create_service(result.definitions[0], service_id="S-741-FRI", starts_at=starts_at, location="CKC", condition="vrijdag")
    assert service.required_staff == 1
    assert service.duration_hours == 2.5


def test_r12_rejects_duplicate_task_code():
    result = ShiftCatalogAdapter().import_rows([row(), row(service_type="Andere definitie")], imported_at=IMPORTED_AT)
    assert len(result.definitions) == 1
    assert any(signal.code == "DUPLICATE_SHIFT_CODE" for signal in result.signals)


def test_r12_rejects_invalid_staff_bounds():
    result = ShiftCatalogAdapter().import_rows([row(minimum_staff="3", maximum_staff="2")], imported_at=IMPORTED_AT)
    assert not result.definitions
    assert any(signal.code == "INVALID_SHIFT_DEFINITION" for signal in result.signals)


def test_r12_records_configuration_provenance_per_task_code():
    result = ShiftCatalogAdapter().import_rows([row()], imported_at=IMPORTED_AT)
    provenance = result.provenance[0]
    assert provenance.source_system == "CKC"
    assert provenance.source_dataset == "ShiftCatalog"
    assert provenance.source_record_key == "442"
    assert provenance.kind == "CONFIGURATION"
