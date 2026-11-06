"""Browser harness compiles a temporary app without opening a real database."""
from pathlib import Path
import serve_synthetic_planning as probe


def test_launcher_uses_compilable_isolated_script(monkeypatch, tmp_path):
    observed=[]
    def run(command, **kwargs):
        target=Path(command[5])
        assert target.parent != Path(probe.__file__).parents[1]
        text=target.read_text()
        compile(text,str(target),"exec")
        assert "synthetic_exports(12, True)" in text
        assert "patch('dvk.local_csv_sources.read_export_text'" in text
        assert "fetch_rows" in text and "browser-runs.jsonl" in text
        assert command[command.index("--server.address")+1] == "127.0.0.1"
        observed.append(target)
    monkeypatch.setattr(probe.subprocess,"run",run)
    probe.serve(Path(probe.__file__).resolve().parents[1],12,True,8531)
    assert len(observed)==1 and not observed[0].exists()
