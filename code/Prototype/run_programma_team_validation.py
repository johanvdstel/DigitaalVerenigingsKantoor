"""Local read-only v0.5 verification. Never writes CSV/API rows or a database."""
from __future__ import annotations

import argparse
from collections import Counter
import os

from dvk.programma_client import ProgrammaFetchError, SportlinkProgrammaClient
from dvk.programma_team_adapter import CkcProgrammaAdapter, UnresolvedProgramTeamsError
from dvk.real_data_import import RealTeamMembership, SportlinkRealDataAdapter


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teams", required=True, help="Local CKC Teams CSV; not uploaded")
    parser.add_argument("--details", action="store_true", help="Show team-only linking context locally")
    args = parser.parse_args(argv)
    client_id = os.environ.get("SPORTLINK_CLIENT_ID", "").strip()
    if not client_id:
        parser.error("SPORTLINK_CLIENT_ID is niet beschikbaar in de bestaande lokale configuratie")
    try:
        rows = SportlinkRealDataAdapter.read_rows(args.teams, "teams")
        # Only team metadata is needed here; this command does not assess persons.
        memberships = tuple(RealTeamMembership(
            "", str(row.get("Team") or "").strip(), None, None,
            matchday=row.get("Speeldag"), source_team_name=row.get("Team"),
        ) for row in rows)
        adapter = CkcProgrammaAdapter(team_memberships=memberships)
        fetched = SportlinkProgrammaClient(adapter).fetch_rows(client_id=client_id)
        result = adapter.import_rows(fetched.rows)
    except (OSError, ValueError, ProgrammaFetchError):
        # Transport exceptions may contain a request URL; do not print credentials.
        print("Broncontrole mislukt; controleer lokaal CSV-structuur, configuratie en verbinding.")
        return 1
    print(f"Ontvangen wedstrijden: {len(fetched.rows)}")
    print(f"Teamkoppelingen: {dict(sorted(Counter(link.status for link in result.links).items()))}")
    print(f"Bronmeldingen: {dict(sorted(Counter(signal.code for signal in result.signals).items()))}")
    if args.details:
        for link in result.links:
            print(dict(side=link.side, original_name=link.original_team_name,
                       competition=link.competition, competition_type=link.competition_type,
                       normalized_name=link.normalized_name, normalizations=link.normalizations,
                       team=link.identity.team_id if link.identity else None,
                       status=link.status, reason=link.reason))
    try:
        print(f"Gekoppelde operationele wedstrijden: {len(result.matches)}")
    except UnresolvedProgramTeamsError:
        print("Teamkoppelingen zijn onvolledig: niet gebruiken als wedstrijdloze kandidaatcontext.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
