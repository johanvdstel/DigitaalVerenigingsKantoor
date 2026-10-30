import json
from urllib.error import HTTPError, URLError

import pytest

from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient, VrijwilligersFetchError


class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.data


def test_r13_client_uses_get_and_preserves_query_task_code():
    seen = {}
    def opener(request, timeout):
        seen["method"] = request.get_method()
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return Response(json.dumps({"items": [{"naam": "Jan"}]}).encode())
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=opener, timeout_seconds=12)
    result = client.fetch_rows(client_id="runtime-secret", task_code="741", days=60)
    assert seen["method"] == "GET"
    assert "vrijwilligerstaakcode=741" in seen["url"]
    assert seen["timeout"] == 12
    assert result.task_code == "741"
    assert result.rows == ({"naam": "Jan"},)


def test_r13_client_requires_runtime_client_id():
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter())
    with pytest.raises(ValueError):
        client.fetch_rows(client_id="", task_code="741")


# VRIJ-01 explicitly replaces acceptance of an empty HTTP body with an error;
# an explicitly empty JSON collection remains valid.
@pytest.mark.parametrize("payload, expected", [
    (b'[{"naam":"A"}]', ({"naam": "A"},)),
    (b'[]', ()),
    (b'{"items":[{"naam":"A"}]}', ({"naam": "A"},)),
    (b'{"items":[]}', ()),
])
def test_vrij01_client_accepts_only_supported_collections(payload, expected):
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(),
                                        opener=lambda *a, **k: Response(payload))
    assert client.fetch_rows(client_id="x", task_code="442").rows == expected


@pytest.mark.parametrize("payload, message", [
    (b'{"error":"synthetic"}', "not a list or items envelope"),
    (b'{}', "not a list or items envelope"),
    (b'{"items":null}', "not a list or items envelope"),
    (b'{"items":{}}', "not a list or items envelope"),
    (b'{"items":"wrong"}', "not a list or items envelope"),
    (b'{"items":1}', "not a list or items envelope"),
    (b'', "empty HTTP body"),
    (b'   ', "invalid JSON"),
    (b'\xff', "invalid JSON"),
    (b'null', "not a list or items envelope"),
    (b'"wrong"', "not a list or items envelope"),
    (b'[null]', "non-object item"),
    (b'[1]', "non-object item"),
    (b'["wrong"]', "non-object item"),
    (b'[[]]', "non-object item"),
    (b'{"items":[{},false]}', "non-object item"),
])
def test_vrij01_client_rejects_invalid_response_structure(payload, message):
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(),
                                        opener=lambda *a, **k: Response(payload))
    with pytest.raises(VrijwilligersFetchError, match=message):
        client.fetch_rows(client_id="x", task_code="741")


@pytest.mark.parametrize("failure, message", [
    (HTTPError("https://example.invalid", 401, "synthetic", None, None), "HTTP 401"),
    (HTTPError("https://example.invalid", 403, "synthetic", None, None), "HTTP 403"),
    (URLError("synthetic offline"), "connection failure"),
    (TimeoutError("synthetic timeout"), "connection failure"),
    (OSError("synthetic transport"), "transport failure"),
])
def test_vrij01_client_reports_transport_errors(failure, message):
    def unavailable(*args, **kwargs):
        raise failure
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=unavailable)
    with pytest.raises(VrijwilligersFetchError, match=message):
        client.fetch_rows(client_id="x", task_code="741")


def test_r13_client_rejects_invalid_json():
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=lambda *a, **k: Response(b"not-json"))
    with pytest.raises(VrijwilligersFetchError):
        client.fetch_rows(client_id="x", task_code="741")
