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


@pytest.fixture
def historical_registration_context(monkeypatch):
    """Existing BL-11 scenarios run at source start, not the wall clock of CI.

    Distinct historical same-day tasks are explicitly acknowledged here; BL-19
    rejection/confirmation behavior is tested separately without this fixture.
    Original source dates and sanction cases remain unchanged.
    """
    from dvk.application_services import NoShowApplicationService
    original = NoShowApplicationService.register
    def historical(self, event, **kwargs):
        previous_clock = self.clock
        self.clock = lambda: event.occurred_at
        try:
            context = event.booking or self.uow.sportlink_bookings.get(event.assignment_id)
            if context is not None:
                _, possible = self.duplicate_check(context)
                kwargs.setdefault("acknowledged_possible", tuple(e.no_show_id for e in possible))
            return original(self, event, **kwargs)
        finally:
            self.clock = previous_clock
    monkeypatch.setattr(NoShowApplicationService, "register", historical)
