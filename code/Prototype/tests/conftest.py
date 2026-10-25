"""Default UI sources are synthetic; no test reads the user's CKC home exports."""
import io
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
