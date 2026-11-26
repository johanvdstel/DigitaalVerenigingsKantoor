"""Read the local Sportlink credential without evaluating shell syntax."""
import os
from pathlib import Path
import re


_CONFIG_PATH = Path("Development/DVK-Data/Config/sportlink.env")
_ASSIGNMENT = re.compile(r"(?:export[ \t]+)?SPORTLINK_CLIENT_ID(?=[= \t]|$)")
_VALUE = re.compile(r"""=(?P<quote>['"]?)(?P<value>[A-Za-z0-9._~+/=-]+)(?P=quote)(?:[ \t]+#.*)?""")


class SportlinkConfigError(ValueError):
    """A configuration problem safe to display to the planner."""


def load_sportlink_client_id() -> str:
    client_id = os.environ.get("SPORTLINK_CLIENT_ID", "").strip()
    if client_id:
        return client_id

    message = (
        "Sportlink Programma en Vrijwilligers zijn niet beschikbaar. "
        f"Controleer of ~/{_CONFIG_PATH} een geldige, niet-lege instelling "
        "voor SPORTLINK_CLIENT_ID bevat."
    )
    try:
        lines = (Path.home() / _CONFIG_PATH).read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError, RuntimeError):
        raise SportlinkConfigError(message) from None

    for line in lines:
        line = line.strip()
        assignment = _ASSIGNMENT.match(line)
        if assignment:
            value = _VALUE.fullmatch(line, assignment.end())
            if value is None or client_id:
                raise SportlinkConfigError(message)
            client_id = value["value"]
    if not client_id:
        raise SportlinkConfigError(message)
    return client_id
