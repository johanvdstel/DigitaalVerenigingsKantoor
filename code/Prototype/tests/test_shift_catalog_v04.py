from __future__ import annotations

from datetime import datetime, timezone

from dvk.shift_catalog import ShiftCatalogAdapter


IMPORTED_AT = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)


def row(**overrides):
    data = {
        "task_code": "442",
        "pattern": "standaard",
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
    assert definition.pattern == "standaard"
    assert definition.service_type == "Commissiekamer"
    assert definition.duration_hours == 2.5
    assert definition.minimum_staff == 1
    assert definition.maximum_staff == 2
    assert not result.signals


def test_r12_accepts_same_task_code_with_distinct_patterns():
    result = ShiftCatalogAdapter().import_rows(
        [
            row(task_code="741", pattern="weekend", service_type="Bar weekend", minimum_staff="2", maximum_staff="4"),
            row(task_code="741", pattern="vrijdag", service_type="Bar weekend", minimum_staff="1", maximum_staff="2"),
        ],
        imported_at=IMPORTED_AT,
    )
    assert len(result.definitions) == 2
    assert {(d.pattern, d.minimum_staff, d.maximum_staff) for d in result.definitions} == {
        ("weekend", 2, 4),
        ("vrijdag", 1, 2),
    }
    assert not result.signals


def test_r12_service_uses_minimum_staff_as_operational_requirement():
    adapter = ShiftCatalogAdapter()
    result = adapter.import_rows(
        [row(task_code="761", pattern="zo-do", service_type="Bar Zo-Do")],
        imported_at=IMPORTED_AT,
    )
    starts_at = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    service = adapter.create_service(
        result.definitions[0], service_id="S-761-1", starts_at=starts_at, location="CKC"
    )
    assert service.required_staff == 1
    assert service.duration_hours == 2.5


def test_r12_rejects_duplicate_task_code_and_pattern():
    result = ShiftCatalogAdapter().import_rows(
        [row(), row(service_type="Andere definitie")],
        imported_at=IMPORTED_AT,
    )
    assert len(result.definitions) == 1
    assert any(signal.code == "DUPLICATE_SHIFT_DEFINITION" for signal in result.signals)


def test_r12_rejects_invalid_staff_bounds():
    result = ShiftCatalogAdapter().import_rows(
        [row(minimum_staff="3", maximum_staff="2")],
        imported_at=IMPORTED_AT,
    )
    assert not result.definitions
    assert any(signal.code == "INVALID_SHIFT_DEFINITION" for signal in result.signals)


def test_r12_records_configuration_provenance_with_natural_key():
    result = ShiftCatalogAdapter().import_rows([row()], imported_at=IMPORTED_AT)
    provenance = result.provenance[0]
    assert provenance.source_system == "CKC"
    assert provenance.source_dataset == "ShiftCatalog"
    assert provenance.source_record_key == "442:standaard"
    assert provenance.kind == "CONFIGURATION"
