from __future__ import annotations

import os

from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient


TASK_CODES = ("701", "741", "761", "442")


def main() -> None:
    client_id = os.environ.get("SPORTLINK_CLIENT_ID", "").strip()
    if not client_id:
        raise SystemExit("SPORTLINK_CLIENT_ID is not available")

    adapter = SportlinkVrijwilligersAdapter()
    client = SportlinkVrijwilligersClient(
        adapter,
        timeout_seconds=30.0,
    )

    print("DVK v0.4 Sportlink Vrijwilligers live validation")

    total_rows = 0
    all_fields: set[str] = set()

    for task_code in TASK_CODES:
        fetched = client.fetch_rows(
            client_id=client_id,
            task_code=task_code,
            days=60,
            weekoffset=-1,
        )

        fields = sorted(
            {
                str(key)
                for row in fetched.rows
                for key in row
            }
        )

        all_fields.update(fields)
        total_rows += len(fetched.rows)

        print(
            f"task_code={task_code} "
            f"rows={len(fetched.rows)} "
            f"fields={fields}"
        )

    print(f"total_rows={total_rows}")
    print(f"all_fields={sorted(all_fields)}")


if __name__ == "__main__":
    main()
