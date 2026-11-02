"""Presentation-only ordering and pagination; no no-show or sanction policy."""
from collections import Counter
from dataclasses import dataclass
from datetime import timezone


PAGE_SIZE = 10


def person_labels(names):
    names = {pid: name or "Persoon onbekend" for pid, name in names.items()}
    counts = Counter(names.values())
    labels = {pid: name + (f" (relatie {pid})" if counts[name] > 1 else "")
              for pid, name in names.items()}
    return dict(sorted(labels.items(), key=lambda item: (item[1].casefold(), item[1], item[0])))


@dataclass(frozen=True)
class HistoryPage:
    rows: tuple
    number: int
    count: int
    total: int


def history_page(history, number=1):
    def key(row):
        event, _ = row
        moment = event.recorded_at
        # New events have explicit offsets. Keep legacy unzoned values as stored;
        # never add a guessed timezone or rewrite the historical event.
        if moment.tzinfo is not None:
            moment = moment.astimezone(timezone.utc)
        return moment.isoformat(timespec="microseconds"), event.no_show_id
    ordered = sorted(history, key=key, reverse=True)
    count = max(1, (len(ordered) + PAGE_SIZE - 1) // PAGE_SIZE)
    number = min(max(1, number), count)
    start = (number - 1) * PAGE_SIZE
    return HistoryPage(tuple(ordered[start:start + PAGE_SIZE]), number, count, len(ordered))
