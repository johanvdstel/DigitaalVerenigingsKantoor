"""Opt-in local timings: no source values, arguments, names, IDs or exceptions."""
import cProfile
from datetime import datetime, timezone
from functools import wraps
from itertools import count
import json
import os
from pathlib import Path
import pstats
import tempfile
from time import perf_counter
import warnings

_RUNS = count(1)
_STAGES = {
    ("sportlink_exports.py", "read_export_text"): "csv_read",
    ("real_data_import.py", "load_exports"): "csv_normalization",
    ("candidate_context.py", "load"): "source_context_load",
    ("candidate_context.py", "propose"): "candidate_calculation",
    ("member_duty.py", "derive_member_duties"): "duty_derivation",
    ("hours_control.py", "compare_required_hours"): "hours_control",
    ("application_services.py", "assess_candidates"): "candidate_assessment",
    ("prioritization.py", "prioritize_candidates"): "prioritization",
    ("application_services.py", "approve_many"): "confirmation",
    ("application_services.py", "undo"): "undo",
    ("sqlite.py", "initialize"): "schema_check",
    ("sqlite.py", "commit"): "db_commit",
    ("data_editor.py", "data_editor"): "editor_build",
    ("arrow.py", "dataframe"): "dataframe_build",
}


def output_path():
    return Path(tempfile.gettempdir()) / "dvk-planning-profile.jsonl"


def summarize(profile):
    stages = {}
    self_ms = {"dvk": 0, "persistence": 0, "streamlit": 0, "other": 0}
    for (filename, _, name), (_, calls, own, cumulative, _) in pstats.Stats(profile).stats.items():
        phase = _STAGES.get((Path(filename).name, name))
        if Path(filename).name == "safe_session_state.py" and name in {"__getitem__", "__setitem__", "__delitem__"}:
            phase = "session_state"
        if "sqlite3.Connection" in name and "execute" in name:
            phase = "sql_execute"
        if phase:
            item = stages.setdefault(phase, {"calls": 0, "ms": 0})
            item["calls"] += calls
            item["ms"] += cumulative * 1000
        group = ("persistence" if "/dvk/persistence/" in filename else
                 "dvk" if "/dvk/" in filename else
                 "streamlit" if "/streamlit/" in filename else "other")
        self_ms[group] += own * 1000
    return {"stages": {key: {"calls": value["calls"], "ms": round(value["ms"], 2)}
                       for key, value in stages.items()},
            "self_ms": {key: round(value, 2) for key, value in self_ms.items()}}


def trace_planning(function):
    @wraps(function)
    def measured(*args, **kwargs):
        if os.environ.get("DVK_PLANNING_PROFILE") != "1":
            return function(*args, **kwargs)
        profile = cProfile.Profile()
        run = next(_RUNS)
        started = datetime.now(timezone.utc).isoformat()
        start = perf_counter()
        outcome = "completed"
        profile.enable()
        try:
            return function(*args, **kwargs)
        except BaseException as exc:
            # Streamlit's explicit rerun uses a control exception. Never log its
            # contents, or any exception text/arguments which may contain sources.
            outcome = "rerun" if type(exc).__name__ == "RerunException" else "error"
            raise
        finally:
            profile.disable()
            record = {"run": run, "started_utc": started, "outcome": outcome,
                      "total_ms": round((perf_counter() - start) * 1000, 2), **summarize(profile)}
            try:
                descriptor = os.open(output_path(), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                with os.fdopen(descriptor, "a") as stream:
                    stream.write(json.dumps(record) + "\n")
            except OSError:
                warnings.warn("Lokale prestatiemeting kon niet worden opgeslagen.", stacklevel=2)
    return measured
