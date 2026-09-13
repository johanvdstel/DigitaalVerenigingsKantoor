from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .vrijwilligers_adapter import SportlinkVrijwilligersAdapter


class VrijwilligersFetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class VrijwilligersFetchResult:
    task_code: str
    rows: tuple[dict[str, object], ...]


class SportlinkVrijwilligersClient:
    """Read-only Sportlink Vrijwilligers client; credentials remain runtime-only."""

    def __init__(self, adapter: SportlinkVrijwilligersAdapter, *, opener: Callable[..., object] = urlopen, timeout_seconds: float = 30.0):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.adapter = adapter
        self.opener = opener
        self.timeout_seconds = timeout_seconds

    def fetch_rows(self, *, client_id: str, task_code: str, days: int = 60, weekoffset: int = -1) -> VrijwilligersFetchResult:
        if not client_id or not client_id.strip():
            raise ValueError("Sportlink client_id is required at runtime")
        if not task_code or not task_code.strip():
            raise ValueError("Sportlink volunteer task code is required")
        code = task_code.strip()
        url = self.adapter.build_url(client_id=client_id.strip(), task_code=code, days=days, weekoffset=weekoffset)
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "DVK-Prototype/0.4"}, method="GET")
        try:
            response = self.opener(request, timeout=self.timeout_seconds)
            with response:
                payload = response.read()
        except HTTPError as exc:
            raise VrijwilligersFetchError(f"Sportlink Vrijwilligers HTTP {exc.code}") from exc
        except (URLError, TimeoutError) as exc:
            raise VrijwilligersFetchError(f"Sportlink Vrijwilligers connection failure: {exc}") from exc
        except OSError as exc:
            raise VrijwilligersFetchError(f"Sportlink Vrijwilligers transport failure: {exc}") from exc
        if not payload:
            return VrijwilligersFetchResult(code, ())
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VrijwilligersFetchError("Sportlink Vrijwilligers returned invalid JSON") from exc
        if isinstance(data, dict):
            data = data.get("items", [])
        if not isinstance(data, list):
            raise VrijwilligersFetchError("Sportlink Vrijwilligers response is not a list or items envelope")
        rows = []
        for item in data:
            if not isinstance(item, dict):
                raise VrijwilligersFetchError("Sportlink Vrijwilligers response contains a non-object item")
            rows.append(item)
        return VrijwilligersFetchResult(code, tuple(rows))
