import json

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


def test_r13_client_accepts_plain_list_and_empty_response():
    responses = iter([Response(b'[{"naam":"A"}]'), Response(b"")])
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=lambda *a, **k: next(responses))
    assert client.fetch_rows(client_id="x", task_code="442").rows == ({"naam": "A"},)
    assert client.fetch_rows(client_id="x", task_code="442").rows == ()


def test_r13_client_rejects_invalid_json():
    client = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=lambda *a, **k: Response(b"not-json"))
    with pytest.raises(VrijwilligersFetchError):
        client.fetch_rows(client_id="x", task_code="741")
