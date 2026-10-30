"""Synthetic regression tests for file locations; no live sources or real exports."""
from datetime import datetime
from io import StringIO
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.sportlink_exports import (
    EXPORT_FILENAMES, ExportFileError, default_export_directory,
    export_location_hint, export_path, read_export_text,
)
from test_real_data_import_v04 import exports
from test_programma_team_linking_v05 import row, validation_command

ROOT = Path(__file__).resolve().parents[1]
ARGUMENTS = {"leden": "members_path", "functies": "functions_path", "commissies": "committees_path",
             "teams": "teams_path", "vrijwilligers_periode": "duty_path"}


@pytest.fixture
def local_home(tmp_path, monkeypatch):
    home = tmp_path / "synthetic-user"
    home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    return home


@pytest.fixture
def standard_exports(tmp_path, local_home):
    explicit = tmp_path / "legacy-explicit"
    explicit.mkdir()
    paths = exports(explicit)  # Existing accepted, synthetic fixture stays unchanged.
    folder = local_home / "Documents" / "DVK-Sportlink-exports"
    folder.mkdir(parents=True)
    for dataset, argument in ARGUMENTS.items():
        shutil.copyfile(paths[argument], folder / EXPORT_FILENAMES[dataset])
    return paths


def test_home_relative_central_map_and_all_five_exact_filenames(local_home):
    assert default_export_directory() == local_home / "Documents" / "DVK-Sportlink-exports"
    assert EXPORT_FILENAMES == {
        "leden": "Leden.csv", "functies": "Functies.csv", "commissies": "Commissies.csv",
        "teams": "Teams.csv", "vrijwilligers_periode": "Overzicht per periode.csv",
    }
    assert not default_export_directory().exists()  # Computing a path never creates it.


@pytest.mark.parametrize("dataset", ARGUMENTS)
def test_each_default_is_read_by_existing_csv_parser_without_changing_bytes(standard_exports, dataset):
    path = export_path(dataset)
    before = path.read_bytes()
    default_rows = SportlinkRealDataAdapter.read_rows(None, dataset)
    explicit_rows = SportlinkRealDataAdapter.read_rows(standard_exports[ARGUMENTS[dataset]], dataset)
    assert default_rows == explicit_rows
    assert path.read_bytes() == before


def test_all_default_imports_equal_existing_explicit_import_calls(standard_exports):
    at = datetime(2026, 10, 24, 12)
    expected = SportlinkRealDataAdapter().load_exports(**standard_exports, imported_at=at)
    actual = SportlinkRealDataAdapter().load_exports(imported_at=at)
    assert actual == expected


def test_explicit_team_path_wins_over_missing_default(standard_exports, tmp_path):
    export_path("teams").unlink()
    custom = tmp_path / "arbitrary-name.csv"
    custom.write_text("Rel. code;Team;Teamrol;Spelend lid\nP1;O17-1;Teamspeler;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(teams_path=str(custom))
    assert result.team_memberships[0].team_id == "O17-1"
    assert export_path("teams", custom) == custom


def test_explicit_none_still_skips_hours_and_stream_arguments_remain_supported(standard_exports):
    export_path("vrijwilligers_periode").unlink()
    streams = {key: StringIO(value.read_text()) for key, value in standard_exports.items() if key != "duty_path"}
    result = SportlinkRealDataAdapter().load_exports(**streams, duty_path=None)
    assert result.team_memberships
    assert not result.duty_records
    result = SportlinkRealDataAdapter().load_exports(duty_path=None)
    assert not result.duty_records


@pytest.mark.parametrize("dataset", ARGUMENTS)
def test_missing_standard_exports_name_location_and_user_action(standard_exports, dataset):
    path = export_path(dataset)
    path.unlink()
    before = set(default_export_directory().iterdir())
    with pytest.raises(ExportFileError) as error:
        SportlinkRealDataAdapter().load_exports()
    message = str(error.value)
    assert path.name in message and str(path) in message
    assert "Plaats" in message and "Sportlink-export" in message
    assert set(default_export_directory().iterdir()) == before


def test_missing_folder_or_explicit_file_is_not_created(local_home, tmp_path):
    for explicit in (None, tmp_path / "custom-file.csv"):
        expected = export_path("teams", explicit)
        with pytest.raises(ExportFileError) as error:
            SportlinkRealDataAdapter.read_rows(explicit, "teams")
        assert expected.name in str(error.value) and str(expected) in str(error.value)
        assert not expected.exists()
    assert not default_export_directory().exists()


@pytest.mark.parametrize("problem", ["permissions", "directory", "encoding"])
def test_unreadable_files_are_explicit_without_empty_data_fallback(local_home, monkeypatch, problem):
    path = export_path("teams")
    path.parent.mkdir(parents=True)
    if problem == "directory":
        path.mkdir()
    elif problem == "encoding":
        path.write_bytes(b"\xff\xfeinvalid-utf8")
    else:
        path.write_text("synthetic", encoding="utf-8")
        def denied(*args, **kwargs):
            raise PermissionError("synthetic denial")
        monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(ExportFileError, match="niet leesbaar") as error:
        SportlinkRealDataAdapter.read_rows(None, "teams")
    assert path.name in str(error.value) and str(path) in str(error.value)
    if problem == "encoding":
        assert path.read_bytes() == b"\xff\xfeinvalid-utf8"


@pytest.mark.parametrize("delimiter", [";", ",", "\t"])
def test_original_encoding_delimiters_columns_and_values_are_preserved(local_home, delimiter):
    path = export_path("teams")
    path.parent.mkdir(parents=True)
    text = delimiter.join(["Rel. code", "Team", "Teamrol", "Spelend lid", "Speeldag", "Extra"])
    text += "\r\n" + delimiter.join(["SYNTHETIC-P1", "2", "Teamspeler", "Ja", "Algemeen/Zondag", "  café  "])
    original = b"\xef\xbb\xbf" + text.encode("utf-8")
    path.write_bytes(original)
    rows = SportlinkRealDataAdapter.read_rows(None, "teams")
    assert rows[0]["Extra"] == "  café  "
    assert rows[0]["Speeldag"] == "Algemeen/Zondag"
    assert path.read_bytes() == original
    assert read_export_text("teams").startswith("Rel. code")


def test_missing_required_columns_remain_invalid(local_home):
    path = export_path("teams")
    path.parent.mkdir(parents=True)
    path.write_text("Team;Extra\nO17-1;synthetic", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        SportlinkRealDataAdapter.read_rows(None, "teams")


@pytest.mark.parametrize("explicit", [False, True])
def test_cli_default_and_explicit_override_preserve_existing_options(standard_exports, monkeypatch, capsys, explicit):
    command = validation_command()
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "SYNTHETIC-SECRET")
    monkeypatch.setattr(command, "SportlinkProgrammaClient", lambda adapter: SimpleNamespace(
        fetch_rows=lambda **kwargs: SimpleNamespace(rows=[row("CKC Senioren 8")])) )
    argv = ["--details"]
    if explicit:
        export_path("teams").write_text("invalid default", encoding="utf-8")
        argv += ["--teams", str(standard_exports["teams_path"])]
    assert command.main(argv) == 0
    output = capsys.readouterr().out
    assert "'matched': 1" in output and "Gekoppelde operationele wedstrijden: 1" in output
    assert "SYNTHETIC-SECRET" not in output and "Jan Smit" not in output


def test_cli_missing_standard_file_reports_location_before_network(local_home, monkeypatch, capsys):
    command = validation_command()
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "SYNTHETIC-SECRET")
    def forbidden(*args, **kwargs):
        raise AssertionError("Missing CSV must not initiate API access")
    monkeypatch.setattr(command, "SportlinkProgrammaClient", forbidden)
    assert command.main([]) == 1
    output = capsys.readouterr().out
    assert "Teams.csv" in output and str(export_path("teams")) in output and "Plaats" in output
    assert "SYNTHETIC-SECRET" not in output


def test_ui_reads_standard_exports_without_manual_uploads(standard_exports, tmp_path, monkeypatch):
    path = tmp_path / "streamlit_app.py"
    path.write_text((ROOT / "streamlit_app.py").read_text())
    app = AppTest.from_file(str(path), default_timeout=20).run()
    assert not app.exception and not app.get("file_uploader")
    app.button(key="nav-control").click().run()
    assert not app.exception and not app.get("file_uploader")
    captions = "\n".join(item.value for item in app.caption)
    assert str(default_export_directory()) in captions
    assert all(name in captions for name in EXPORT_FILENAMES.values())
    assert app.button(key="refresh-duty-sources").label == "Brongegevens vernieuwen"
    app.button(key="nav-planning").click().run()
    assert not app.exception and not app.get("file_uploader")


@pytest.mark.parametrize("ignorecase", ["true", "false"])
def test_gitignore_protects_exports_without_hiding_accepted_fixtures(ignorecase):
    ignored = ["DVK-Sportlink-exports/private.csv", "Leden.csv", "Functies.csv", "Commissies.csv", "Teams.csv",
               "Overzicht per periode.csv", "code/Prototype/Teams 999 personen gevonden.csv"]
    kept = ["code/Prototype/testdata/v03_import/members.csv", "code/Prototype/testdata/v03_import/teams.csv",
            "code/Prototype/dvk/configuration/function_classification.csv"]
    result = subprocess.run(["git", "-c", f"core.ignorecase={ignorecase}", "check-ignore", "--no-index", "--stdin"],
                            input="\n".join(ignored + kept) + "\n", text=True, capture_output=True,
                            cwd=ROOT.parents[1], check=False)
    assert result.returncode == 0
    assert set(result.stdout.splitlines()) == set(ignored)
