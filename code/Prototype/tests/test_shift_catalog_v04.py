from __future__ import annotations

from datetime import datetime, timezone

from dvk.shift_catalog import ShiftCatalogAdapter


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
    result = ShiftCatalogAdapter().import_rows(
        [row()], imported_at=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
    )
    definition = result.definitions[0]
    assert definition.task_code == "442"
    assert definition.service_type == "Commissiekamer"
    assert definition.duration_hours == 2.5
    assert definition.minimum_staff == 1
    assert definition.maximum_staff == 2
    assert not result.signals


def test_r12_preserves_minimum_and_maximum_as_distinct_configuration():
    result = ShiftCatalogAdapter().import_rows(
        [row(task_code="741", service_type="Bar weekend", minimum_staff="2", maximum_staff="4")],
        imported_at=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )
    definition = result.definitions[0]
    assert definition.minimum_staff == 2
    assert definition.maximum_staff == 4


def test_r12_service_uses_minimum_staff_as_operational_requirement():
    adapter = ShiftCatalogAdapter()
    result = adapter.import_rows(
        [row(task_code="761", service_type="Bar Zo-Do")],
        imported_at=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )
    starts_at = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    service = adapter.create_service(
        result.definitions[0], service_id="S-761-1", starts_at=starts_at, location="CKC"
    )
    assert service.required_staff == 1
    assert service.duration_hours == 2.5


def test_r12_rejects_duplicate_task_code():
    result = ShiftCatalogAdapter().import_rows(
        [row(), row(service_type="Andere definitie")],
        imported_at=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )
    assert len(result.definitions) == 1
    assert any(signal.code == "DUPLICATE_SHIFT_CODE" for signal in result.signals)


def test_r12_rejects_invalid_staff_bounds():
    result = ShiftCatalogAdapter().import_rows(
        [row(minimum_staff="3", maximum_staff="2")],
        imported_at=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )
    assert not result.definitions
    assert any(signal.code == "INVALID_SHIFT_DEFINITION" for signal in result.signals)


def test_r12_records_configuration_provenance():
    imported_at = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
    result = ShiftCatalogAdapter().import_rows([row()], imported_at=imported_at)
    provenance = result.provenance[0]
    assert provenance.source_system == "CKC"
    assert provenance.source_dataset == "ShiftCatalog"
    assert provenance.source_record_key == "442"
    assert provenance.kind == "CONFIGURATION"
