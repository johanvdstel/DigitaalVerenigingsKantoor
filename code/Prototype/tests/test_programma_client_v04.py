from __future__ import annotations

import json
from urllib.error import URLError

import pytest

from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.programma_client import ProgrammaFetchError, SportlinkProgrammaClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_client_requires_runtime_client_id():
    client = SportlinkProgrammaClient(SportlinkProgrammaAdapter(club_relation_code="BBDZ08H"))
    with pytest.raises(ValueError, match="client_id"):
        client.fetch_rows(client_id="")


def test_client_fetches_items_envelope_read_only_with_timeout():
    observed = {}

    def opener(request, *, timeout):
        observed["method"] = request.get_method()
        observed["url"] = request.full_url
        observed["timeout"] = timeout
        payload = json.dumps({"items": [{"wedstrijdnummer": "123"}]}).encode()
        return FakeResponse(payload)

    client = SportlinkProgrammaClient(
        SportlinkProgrammaAdapter(club_relation_code="BBDZ08H"),
        opener=opener,
        timeout_seconds=12.5,
    )
    result = client.fetch_rows(client_id="runtime-secret")

    assert observed["method"] == "GET"
    assert observed["timeout"] == 12.5
    assert "client_id=runtime-secret" in observed["url"]
    assert result.rows == ({"wedstrijdnummer": "123"},)


def test_client_accepts_plain_list_response():
    def opener(request, *, timeout):
        return FakeResponse(json.dumps([{"wedstrijdnummer": "456"}]).encode())

    client = SportlinkProgrammaClient(
        SportlinkProgrammaAdapter(club_relation_code="BBDZ08H"), opener=opener
    )
    assert client.fetch_rows(client_id="runtime").rows[0]["wedstrijdnummer"] == "456"


def test_client_reports_connection_failure():
    def opener(request, *, timeout):
        raise URLError("offline")

    client = SportlinkProgrammaClient(
        SportlinkProgrammaAdapter(club_relation_code="BBDZ08H"), opener=opener
    )
    with pytest.raises(ProgrammaFetchError, match="connection failure"):
        client.fetch_rows(client_id="runtime")


def test_client_reports_invalid_json():
    def opener(request, *, timeout):
        return FakeResponse(b"not-json")

    client = SportlinkProgrammaClient(
        SportlinkProgrammaAdapter(club_relation_code="BBDZ08H"), opener=opener
    )
    with pytest.raises(ProgrammaFetchError, match="invalid JSON"):
        client.fetch_rows(client_id="runtime")
