"""Default UI sources are synthetic; no test reads the user's CKC home exports."""
import io
from pathlib import Path
import shutil
import pytest


@pytest.fixture(autouse=True)
def synthetic_home(tmp_path, monkeypatch):
    from dvk.sportlink_exports import EXPORT_FILENAMES
    from dvk.real_data_import import SportlinkRealDataAdapter
    from dvk.programma_client import SportlinkProgrammaClient
    from dvk.programma_team_adapter import CkcProgrammaAdapter
    home = tmp_path / "synthetic-home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "synthetic-test-only")
    folder = home / "Documents" / "DVK-Sportlink-exports"
    folder.mkdir(parents=True)
    for filename in ("shift_definitions.csv", "shift_week_pattern.csv"):
        shutil.copyfile(Path(__file__).parents[1] / "dvk" / "configuration" / filename, folder / filename)
    for dataset, filename in EXPORT_FILENAMES.items():
        fields = sorted(SportlinkRealDataAdapter.REQUIRED_COLUMNS[dataset])
        if dataset == "leden":
            fields.append("Geb.dat.")
        (folder / filename).write_text(";".join(fields) + "\n")
    original = SportlinkProgrammaClient.__init__
    def init(self, adapter, **kwargs):
        if isinstance(adapter, CkcProgrammaAdapter) and "opener" not in kwargs:
            kwargs["opener"] = lambda *a, **k: io.BytesIO(b"[]")
        original(self, adapter, **kwargs)
    monkeypatch.setattr(SportlinkProgrammaClient, "__init__", init)


@pytest.fixture(autouse=True)
def native_editor_state_roundtrip(monkeypatch):
    # AppTest 1.64 lacks editor events/state forwarding. Model the native browser
    # protocol so a later confirmation retains checkbox edits in integration tests.
    from streamlit.testing.v1 import element_tree
    from ui_table_events import preserving_editors
    monkeypatch.setattr(element_tree, "get_widget_state",
                        preserving_editors(element_tree.get_widget_state))
