from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .programma_adapter import SportlinkProgrammaAdapter


class ProgrammaFetchError(RuntimeError):
    """Programma could not be retrieved safely."""


@dataclass(frozen=True)
class ProgrammaFetchResult:
    rows: tuple[dict[str, object], ...]
    url: str


class SportlinkProgrammaClient:
    """Small read-only HTTP client; client_id is supplied only at runtime."""

    def __init__(
        self,
        adapter: SportlinkProgrammaAdapter,
        *,
        opener: Callable[..., object] = urlopen,
        timeout_seconds: float = 30.0,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.adapter = adapter
        self.opener = opener
        self.timeout_seconds = timeout_seconds

    def fetch_rows(self, *, client_id: str, days: int = 60, max_rows: int = 500) -> ProgrammaFetchResult:
        if not client_id or not client_id.strip():
            raise ValueError("Sportlink client_id is required at runtime")

        url = self.adapter.build_url(client_id=client_id.strip(), days=days, max_rows=max_rows)
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "DVK-Prototype/0.4"})

        try:
            response = self.opener(request, timeout=self.timeout_seconds)
            with response:
                payload = response.read()
        except HTTPError as exc:
            raise ProgrammaFetchError(f"Sportlink Programma HTTP {exc.code}") from exc
        except (URLError, TimeoutError) as exc:
            raise ProgrammaFetchError(f"Sportlink Programma connection failure: {exc}") from exc
        except OSError as exc:
            raise ProgrammaFetchError(f"Sportlink Programma transport failure: {exc}") from exc

        if not payload:
            return ProgrammaFetchResult((), url)

        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProgrammaFetchError("Sportlink Programma returned invalid JSON") from exc

        if isinstance(data, dict):
            data = data.get("items", [])
        if not isinstance(data, list):
            raise ProgrammaFetchError("Sportlink Programma response is not a list or items envelope")

        rows: list[dict[str, object]] = []
        for item in data:
            if not isinstance(item, dict):
                raise ProgrammaFetchError("Sportlink Programma response contains a non-object item")
            rows.append(item)
        return ProgrammaFetchResult(tuple(rows), url)
