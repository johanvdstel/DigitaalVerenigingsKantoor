from datetime import datetime, timezone

from dvk.model import DutyPosition, SportlinkDutyRegistration
from dvk.real_data_import import DutyImportRecord
from dvk.season_closing import build_season_closing_records, previous_season_backlog


def test_season_closing_freezes_sportlink_position_and_provenance():
    duty = DutyImportRecord(
        SportlinkDutyRegistration("P1", 10, 0, 4, 2),
        source_remaining_hours=4,
        position=DutyPosition(10, 0, 4, 2),
    )
    at = datetime(2026, 7, 1, 0, 5, tzinfo=timezone.utc)
    records = build_season_closing_records((duty,), season="2025/2026", captured_at=at)
    record = records[0]
    assert record.remaining_hours == 4
    assert record.source_remaining_hours == 4
    assert record.season == "2025/2026"
    assert record.captured_at == at
    assert record.source_system == "Sportlink"
    assert previous_season_backlog(records, season="2025/2026") == {"P1": 4}
