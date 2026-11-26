"""Configuration and startup checks with synthetic files and HTTP responses."""
import io
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from dvk.programma_client import SportlinkProgrammaClient
from dvk.sportlink_config import load_sportlink_client_id
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
from test_navigation_v05 import app_at
from test_planning_ui_names_v05 import page


ENV_KEY = "SPORTLINK_CLIENT_ID"
FILE_ID = "synthetic-file-id"


@pytest.fixture
def config_file(monkeypatch):
    monkeypatch.delenv(ENV_KEY)
    path = Path.home() / "Development" / "DVK-Data" / "Config" / "sportlink.env"
    path.parent.mkdir()
    return path


@pytest.mark.parametrize("environment", [None, "", " \t", " synthetic-environment-id "])
def test_environment_precedes_export_when_nonempty(config_file, monkeypatch, environment):
    config_file.write_text(f'# Local config\nexport {ENV_KEY}="{FILE_ID}" # comment\n', encoding="utf-8")
    if environment is not None:
        monkeypatch.setenv(ENV_KEY, environment)
    assert load_sportlink_client_id() == ((environment or "").strip() or FILE_ID)
    assert os.environ.get(ENV_KEY) == environment


@pytest.mark.parametrize("contents", [
    None,
    f"export {ENV_KEY}=\n".encode(),
    f'export {ENV_KEY}="{FILE_ID}\n'.encode(),
    f"export {ENV_KEY}=$(touch {FILE_ID})\n".encode(),
    f"export {ENV_KEY}={FILE_ID}; echo other\n".encode(),
    b"\xff",
])
def test_invalid_config_is_reported_without_leaking_values(
    config_file, contents, tmp_path, caplog, capsys,
):
    if contents is not None:
        config_file.write_bytes(contents.replace(b"touch ", f"touch {tmp_path}/".encode()))
    app = app_at(tmp_path)
    assert not app.exception
    assert len(app.error) == 1
    message = app.error[0].value
    assert "Sportlink Programma en Vrijwilligers" in message
    assert "~/Development/DVK-Data/Config/sportlink.env" in message
    assert ENV_KEY in message
    output = capsys.readouterr()
    assert FILE_ID not in message + caplog.text + output.out + output.err
    assert not (tmp_path / FILE_ID).exists()
    assert not (tmp_path / "dvk_v05.sqlite").exists()


def test_new_planning_passes_file_config_to_both_read_only_clients(config_file, monkeypatch, tmp_path):
    config_file.write_text(f"export {ENV_KEY}={FILE_ID}\n", encoding="utf-8")
    requests = {"programma": [], "vrijwilligers": []}

    def record_requests(api, fetch):
        def fetch_with_recording(self, **kwargs):
            def opener(request, *, timeout):
                requests[api].append((request.get_method(), parse_qs(urlsplit(request.full_url).query)))
                return io.BytesIO(b"[]")

            self.opener = opener
            return fetch(self, **kwargs)

        return fetch_with_recording

    monkeypatch.setattr(SportlinkProgrammaClient, "fetch_rows",
                        record_requests("programma", SportlinkProgrammaClient.fetch_rows))
    monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows",
                        record_requests("vrijwilligers", SportlinkVrijwilligersClient.fetch_rows))

    app, _ = page(tmp_path, automatic=True)
    assert not app.error
    for api_requests in requests.values():
        assert api_requests
        assert all(method == "GET" and params["client_id"] == [FILE_ID] for method, params in api_requests)
