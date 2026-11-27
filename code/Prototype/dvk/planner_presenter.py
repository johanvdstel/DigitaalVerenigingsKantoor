"""Presentation of the already calculated period capacity."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodCapacity:
    services: int
    maximum: int
    sportlink: int | None
    temporary: int
    free: int | None
    overbooked: bool

    @property
    def percentages(self):
        if not self.maximum or self.sportlink is None or self.overbooked:
            return None
        counts = (self.sportlink, self.temporary, self.free)
        floors, remainders = zip(*(divmod(count * 100, self.maximum) for count in counts))
        extra = sorted(range(3), key=lambda index: -remainders[index])[:100 - sum(floors)]
        return tuple(floor + (index in extra) for index, floor in enumerate(floors))


def period_capacity(rows, known):
    return PeriodCapacity(
        len(rows), sum(row.maximum_staff for row in rows),
        sum(row.source_occupancy for row in rows) if known else None,
        sum(row.temporary_occupancy for row in rows),
        sum(row.remaining_capacity for row in rows) if known else None,
        known and any(row.source_occupancy + row.temporary_occupancy > row.maximum_staff for row in rows),
    )
