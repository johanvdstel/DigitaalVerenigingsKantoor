"""Local diagnostics never retain source contents or change return/raise behavior."""
import json
import pytest
from dvk import planning_diagnostics as diagnostic


def test_disabled_diagnostics_do_not_write(tmp_path, monkeypatch):
    monkeypatch.delenv("DVK_PLANNING_PROFILE", raising=False)
    monkeypatch.setattr(diagnostic, "output_path", lambda: tmp_path/"timings")
    assert diagnostic.trace_planning(lambda: 17)() == 17
    assert not (tmp_path/"timings").exists()


def test_profile_records_timings_and_never_arguments_or_error_contents(tmp_path, monkeypatch):
    monkeypatch.setenv("DVK_PLANNING_PROFILE", "1")
    target = tmp_path/"timings"
    monkeypatch.setattr(diagnostic, "output_path", lambda: target)
    @diagnostic.trace_planning
    def fail(name, relation, credential):
        raise ValueError(name + relation + credential)
    with pytest.raises(ValueError):
        fail("SYNTHETIC-NAME", "SYNTHETIC-RELATION", "SYNTHETIC-SECRET")
    text = target.read_text()
    assert all(value not in text for value in ("SYNTHETIC", "ValueError", "test_planning_diagnostics", str(tmp_path)))
    result = json.loads(text)
    assert result["outcome"] == "error" and result["total_ms"] >= 0
    assert result["self_ms"] and "stages" in result
    assert target.stat().st_mode & 0o777 == 0o600


def test_explicit_rerun_is_recorded_without_swallowing_it(tmp_path, monkeypatch):
    monkeypatch.setenv("DVK_PLANNING_PROFILE", "1")
    target = tmp_path/"timings"
    monkeypatch.setattr(diagnostic, "output_path", lambda: target)
    class RerunException(BaseException):
        pass
    @diagnostic.trace_planning
    def rerun():
        raise RerunException("synthetic secret")
    with pytest.raises(RerunException):
        rerun()
    assert json.loads(target.read_text())["outcome"] == "rerun"
