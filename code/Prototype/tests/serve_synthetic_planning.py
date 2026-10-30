"""Real local Streamlit/browser probe. Sources and SQLite are synthetic and disposable.
Run: python -B tests/serve_synthetic_planning.py --members 1500 --mixed --port 8531
Optional --root points to a frozen code-only baseline for an identical comparison.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap


@lru_cache(maxsize=4)
def synthetic_exports(count, mixed):
    from test_candidate_context_v05 import exports
    members = [dict(pid=f"SYNTH-{i}", born="01-01-2011" if mixed and i%3==0 else "01-01-1990",
                    team="O17-1", number=str(i+1)) for i in range(count)]
    functions = tuple({"Rel. code": f"SYNTH-{i}", "Functie": "Trainer Senioren"}
                      for i in range(0, count, 6)) if mixed else ()
    return exports(members=members, functions=functions)


def serve(root, count, mixed, port, historical=False):
    tests = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="dvk-browser-synthetic-") as directory:
        target = Path(directory)/"streamlit_app.py"
        body = (root/"streamlit_app.py").read_text().replace("value=date.today()", "value=date(2026,10,19)")
        header = f"""from __future__ import annotations
import sys, time as probe_time, json as probe_json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, {str(root)!r})
sys.path.insert(0, {str(tests)!r})
import streamlit as st
from serve_synthetic_planning import synthetic_exports
from test_historical_backlog_v05 import history_text, history_row
from dvk.sportlink_exports import ExportFileError
from dvk.persistence import SQLiteDatabase
from dvk.planning_session import PlanningSessionApplicationService
from dvk.shift_catalog import load_shift_catalog
from dvk.programma_client import SportlinkProgrammaClient, ProgrammaFetchResult
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from test_volunteer_planning_integration_v05 import sync, PERIOD, IDENTITY
_data=synthetic_exports({count!r}, {mixed!r})
def _read_source(dataset, explicit_path=None):
    if explicit_path is None:
        return _data[dataset].decode('utf-8-sig')
    if {historical!r}:
        return history_text([history_row(f'SYNTH-{{i}}', (i % 3) * 4) for i in range({count!r})])
    raise ExportFileError('Synthetic historical file unavailable')
if 'probe-seeded' not in st.session_state:
    _db=SQLiteDatabase(Path(__file__).with_name('dvk_v05.sqlite'))
    _db.initialize()
    with _db.unit_of_work() as _uow:
        _app=PlanningSessionApplicationService(_uow,IDENTITY)
        _session=_app.current() or _app.start(PERIOD)
    # Source seeding occurs only before initial use, never on a selection rerun.
    with _db.unit_of_work() as _uow:
        _known=VolunteerPlanningApplicationService(_uow,IDENTITY,load_shift_catalog()).source(PERIOD)[2]
    if not _known:
        assert sync(_db,load_shift_catalog(),{{}})[0] is None
    st.session_state.update({{'probe-seeded':True,'dvk-screen':'planning',
        'planning-resumed':_session.session_id,'planning-mode':'Aangepast',
        'planning-from':PERIOD.start,'planning-until':PERIOD.end}})
_probe_run=st.session_state.get('probe-run',0)+1
st.session_state['probe-run']=_probe_run
_probe_start=probe_time.perf_counter()
_probe_outcome='rerun-or-error'
"""
        body = body.replace("from __future__ import annotations", "", 1)
        wrapper = """with patch('dvk.local_csv_sources.read_export_text',_read_source), patch.object(SportlinkProgrammaClient,'fetch_rows',lambda self,**kwargs:ProgrammaFetchResult(())):
    try:
"""
        footer = r"""
        _probe_outcome='completed'
    finally:
        _probe_ms=(probe_time.perf_counter()-_probe_start)*1000
        _record={'run':_probe_run,'script_ms':round(_probe_ms,2),'outcome':_probe_outcome}
        with open(str(Path(__file__).with_name('browser-runs.jsonl')),'a') as _stream:
            _stream.write(probe_json.dumps(_record)+'\n')
        if _probe_outcome=='completed':
            st.caption(f'Synthetische proef — run {_probe_run} — Python {_probe_ms:.1f} ms')
"""
        target.write_text(header + wrapper + textwrap.indent(body, "        ") + footer)
        print("Uitsluitend synthetische bronnen; tijdelijke database en timings:", directory, flush=True)
        print(f"Browser: http://127.0.0.1:{port}", flush=True)
        subprocess.run([sys.executable,"-B","-m","streamlit","run",str(target),
                        "--server.address","127.0.0.1","--server.port",str(port),
                        "--server.headless","true","--browser.gatherUsageStats","false",
                        "--server.fileWatcherType","none"],check=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--members",type=int,default=250)
    parser.add_argument("--mixed",action="store_true")
    parser.add_argument("--historical",action="store_true", help="Synthetische historische CSV aansluiten")
    parser.add_argument("--port",type=int,default=8531)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    if args.members < 1:
        parser.error("--members moet positief zijn")
    serve(args.root.resolve(),args.members,args.mixed,args.port,args.historical)
