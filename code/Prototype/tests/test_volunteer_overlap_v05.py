"""Positive interval overlap, using synthetic source instants only."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from dvk.vrijwilligers_adapter import overlaps_service_date, same_task_group
from dvk.workstream_model import DutyService

TZ = ZoneInfo("Europe/Amsterdam")


def moment(hour, minute=0):
    return datetime(2026, 10, 21, hour, minute, tzinfo=TZ)


@pytest.mark.parametrize("start,end,expected", [
    (moment(19), moment(20), True),
    (moment(19), moment(22,30), True),
    (moment(19,30), moment(20,30), True),
    (moment(18), moment(19), False),
    (moment(20), moment(21), False),
    (moment(19), moment(19), False),
    (moment(20), moment(19), False),
    (moment(19)+timedelta(days=7),moment(20)+timedelta(days=7),False),
    (moment(19).astimezone(timezone.utc),moment(20).astimezone(timezone.utc),True),
])
def test_positive_overlap_full_partial_adjacent_and_date(start,end,expected):
    service = DutyService("S", "Synthetic slot", moment(19),moment(20),"Synthetic",1)
    assert overlaps_service_date(start,end,service) is expected


@pytest.mark.parametrize("source", ["701","741","761","442"])
@pytest.mark.parametrize("catalog", ["701","741","761","442"])
def test_confirmed_task_groups(source,catalog):
    assert same_task_group(source,catalog) is ((source=="442") == (catalog=="442"))
