from __future__ import annotations

import json
import ssl
from dataclasses import dataclass, replace
from http.client import IncompleteRead
from time import sleep
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .programma_adapter import SportlinkProgrammaAdapter


class ProgrammaFetchError(RuntimeError):
    """Programma could not be retrieved safely; messages contain no request data."""


@dataclass(frozen=True)
class ProgrammaFetchResult:
    rows: tuple[dict[str, object], ...]


@dataclass
class ProgrammaFetchStats:
    calls: int = 0
    retries: int = 0
    failures: int = 0


class SportlinkProgrammaClient:
    """Read-only client, using Rooster2's four attempts and 1.5 second delay.

    Transport/HTTP failures are retried. SSL and invalid responses fail directly,
    as in Rooster2. Unlike that reference, failures never become an empty list.
    Only an actual JSON list (also items: []) confirms a successful empty fetch.
    """

    def __init__(self, adapter: SportlinkProgrammaAdapter, *,
                 opener: Callable[..., object] = urlopen,
                 timeout_seconds: float = 30.0, sleeper: Callable[[float], None] = sleep):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.adapter = adapter
        self.opener = opener
        self.timeout_seconds = timeout_seconds
        self.sleeper = sleeper
        self._stats = ProgrammaFetchStats()

    @property
    def stats(self) -> ProgrammaFetchStats:
        return replace(self._stats)

    def fetch_rows(self, *, client_id: str, days: int = 60, max_rows: int = 500) -> ProgrammaFetchResult:
        if not client_id or not client_id.strip():
            raise ValueError("Sportlink client_id is required at runtime")
        url = self.adapter.build_url(client_id=client_id.strip(), days=days, max_rows=max_rows)
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "DVK-Prototype/0.4"})
        self._stats.calls += 1
        for attempt in range(1, 5):
            try:
                with self.opener(request, timeout=self.timeout_seconds) as response:
                    payload = response.read()
            except HTTPError as exc:
                error = f"Sportlink Programma HTTP {exc.code}"
            except (ssl.SSLError, URLError) as exc:
                if isinstance(exc, ssl.SSLError) or isinstance(getattr(exc, "reason", None), ssl.SSLError):
                    self._stats.failures += 1
                    raise ProgrammaFetchError("Sportlink Programma SSL-certificaatfout") from None
                error = "Sportlink Programma connection failure"
            except (TimeoutError, OSError, IncompleteRead):
                error = "Sportlink Programma transport failure"
            else:
                try:
                    data = json.loads(payload.decode("utf-8"))
                    if isinstance(data, dict):
                        # An error envelope must never masquerade as no matches.
                        if any(key in data for key in ("error", "errors", "fout")):
                            raise ValueError("API error object")
                        data = data.get("items")
                    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
                        raise ValueError("response is not a list of objects")
                except (UnicodeDecodeError, ValueError):
                    self._stats.failures += 1
                    raise ProgrammaFetchError("Sportlink Programma returned invalid JSON or an invalid response") from None
                return ProgrammaFetchResult(tuple(data))
            if attempt < 4:
                self._stats.retries += 1
                self.sleeper(1.5)
        self._stats.failures += 1
        raise ProgrammaFetchError(error + " na vier pogingen") from None
