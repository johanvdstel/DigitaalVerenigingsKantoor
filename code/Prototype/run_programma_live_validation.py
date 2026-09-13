from __future__ import annotations

import os
from collections import Counter

from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.programma_client import SportlinkProgrammaClient


CKC_CLUB_RELATION_CODE = "BBDZ08H"


def main() -> None:
    client_id = os.environ.get("SPORTLINK_CLIENT_ID", "").strip()
    if not client_id:
        raise SystemExit("SPORTLINK_CLIENT_ID is not available")

    adapter = SportlinkProgrammaAdapter(
        club_relation_code=CKC_CLUB_RELATION_CODE
    )
    client = SportlinkProgrammaClient(
        adapter,
        timeout_seconds=30.0,
    )

    fetched = client.fetch_rows(
        client_id=client_id,
        days=60,
        max_rows=500,
    )
    imported = adapter.import_rows(fetched.rows)

    field_names = sorted(
        {key for row in fetched.rows for key in row}
    )

    statuses = Counter(
        str(row.get("status") or "<missing>").strip()
        for row in fetched.rows
    )

    sides = Counter(
        match.home_away for match in imported.matches
    )

    id_sources = Counter(
        "wedstrijdcode"
        if str(row.get("wedstrijdcode") or "").strip()
        else "wedstrijdnummer"
        if str(row.get("wedstrijdnummer") or "").strip()
        else "missing"
        for row in fetched.rows
    )

    print("DVK v0.4 Sportlink Programma live validation")
    print(f"rows={len(fetched.rows)}")
    print(f"fields={field_names}")
    print(f"statuses={dict(sorted(statuses.items()))}")
    print(f"canonical_home_away={dict(sorted(sides.items()))}")
    print(f"match_id_sources={dict(sorted(id_sources.items()))}")
    print(f"canonical_matches={len(imported.matches)}")
    print(
        f"excluded_non_operational="
        f"{len(imported.excluded_records)}"
    )

    print("signals=")
    for signal in imported.signals:
        print(
            f"  {signal.severity} {signal.code}: "
            f"{signal.message}"
        )


if __name__ == "__main__":
    main()
