"""Synthetic server-side before/after AppTest timings (no browser timing).
Run from code/Prototype: python -B tests/measure_planning_actions.py --members 250
"""
from ui_table_events import table as ui_table
import argparse
import os
import textwrap
import cProfile
import json
import pstats
import statistics
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import sys
ROOT = Path(os.environ.get("DVK_BENCHMARK_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest
from ui_table_events import pick, preserving_editors, choose_service
from streamlit.testing.v1 import element_tree
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.programma_client import SportlinkProgrammaClient, ProgrammaFetchResult
from dvk.persistence import SQLiteDatabase
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_v05 import exports
from test_volunteer_planning_integration_v05 import sync, PERIOD


def main(count, mixed=False, legacy_selection=False, actions="all"):
    members=[dict(pid=f'SYNTH-{i}',born='01-01-2011' if mixed and i%3==0 else '01-01-1990',team='O17-1',number=str(i+1)) for i in range(count)]
    functions=tuple({'Rel. code':f'SYNTH-{i}','Functie':'Trainer Senioren'} for i in range(0,count,6)) if mixed else ()
    data=exports(members=members, functions=functions)
    counters={'csv_files':0,'programme_fetches':0,'database_initializations':0}
    def read(dataset):
        counters['csv_files']+=1
        return data[dataset].decode('utf-8-sig')
    def fetch(self,**kwargs):
        counters['programme_fetches']+=1
        return ProgrammaFetchResult(())
    initialize=SQLiteDatabase.initialize
    def init(self):
        counters['database_initializations']+=1
        return initialize(self)
    with tempfile.TemporaryDirectory(prefix='dvk-synthetic-profile-') as directory:
        target=Path(directory)/'streamlit_app.py'
        source=ROOT/'streamlit_app.py'
        original=source.read_text().replace('value=date.today()','value=date(2026,10,19)')
        # Profile every script attempt, including the attempt aborted by st.rerun.
        header = """from __future__ import annotations
import cProfile, streamlit as st, time as profile_time, json as profile_json
_profile=cProfile.Profile()
_seq=st.session_state.get('benchmark-sequence',0)+1
st.session_state['benchmark-sequence']=_seq
_started=profile_time.perf_counter()
_profile.enable()
"""
        body = original.replace('from __future__ import annotations', '', 1)
        footer = """
finally:
    _profile.disable()
    _stem=PROFILE_DIRECTORY+'/profile-'+str(_seq)
    _profile.dump_stats(_stem+'.stats')
    with open(_stem+'.json','w') as _out:
        profile_json.dump({'script_ms':(profile_time.perf_counter()-_started)*1000},_out)
""".replace('PROFILE_DIRECTORY', repr(directory))
        target.write_text(header + 'try:\n' + textwrap.indent(body, '    ') + footer)
        with patch.object(element_tree, 'get_widget_state', preserving_editors(element_tree.get_widget_state)), patch('dvk.local_csv_sources.read_export_text',read), patch.object(SportlinkProgrammaClient,'fetch_rows',fetch), patch.object(SQLiteDatabase,'initialize',init):
            app=AppTest.from_file(str(target),default_timeout=60).run()
            app.button(key='nav-planning').click().run()
            app.button(key='activate-planning').click().run()
            db=SQLiteDatabase(Path(directory)/'dvk_v05.sqlite')
            assert sync(db,load_shift_catalog(),{})[0] is None
            app.run()
            service_ids=ui_table(app, "services_editor-").value.service_id.tolist()
            def timed(kind, action):
                before=dict(counters); existing=set(Path(directory).glob('profile-*.stats')); start=time.perf_counter()
                # Streamlit's script runs in another thread; profile is collected
                # inside that script, not merely around the AppTest dispatcher.
                app.session_state['profile-run']=str(Path(directory)/'profile.stats')
                action()
                elapsed=time.perf_counter()-start
                profiles=sorted(set(Path(directory).glob('profile-*.stats'))-existing)
                stats=pstats.Stats(str(profiles[0]))
                for filename in profiles[1:]:
                    stats.add(str(filename))
                stages={}
                for key,value in stats.stats.items():
                    if key[2] in {'load', 'load_exports', 'read_export_text', 'derive_member_duties', 'propose','compare_required_hours','prioritize_candidates','initialize','approve_many','commit','data_editor','dataframe','_render_planning'}:
                        label=Path(key[0]).name+':'+key[2]
                        stages[label]=round(value[3]*1000,2)
                return {'action':kind,'wall_ms':round(elapsed*1000,2), 'script_runs':len(profiles),
                        'script_ms':round(sum(json.loads(p.with_suffix('.json').read_text())['script_ms'] for p in profiles),2),
                        'calls':{key:counters[key]-before[key] for key in counters},'cumulative_ms':stages, 'sql_ms':round(sum(v[3]*1000 for k,v in stats.stats.items() if 'sqlite3.Connection' in k[2] and 'execute' in k[2]),2), 'sql_calls':sum(v[1] for k,v in stats.stats.items() if 'sqlite3.Connection' in k[2] and 'execute' in k[2])}
            results=[]
            if actions == "candidate":
                choose_service(app, 0)
            for index in range(3 if actions in {"all", "service"} else 0):
                def select(index=index):
                    if legacy_selection:
                        app.session_state['selected_service_id']=service_ids[index]
                        app.run()
                    else:
                        choose_service(app,index)
                results.append(timed('service_selection',select))
            for index in range(3 if actions in {'all', 'candidate'} else 0):
                results.append(timed('candidate_selection',lambda index=index:pick(app, value=index%2==0)))
            for index in range(3 if actions in {"all", "confirmation"} else 0):
                choose_service(app,index)
                pick(app)
                results.append(timed('confirmation',lambda:next(b for b in app.button if b.label=='Selectie bevestigen').click().run()))
            assert not app.exception
            print(json.dumps({'members':count,'mixed':mixed,'legacy_selection':legacy_selection,'results':results},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--members',type=int,default=250)
    parser.add_argument('--actions',choices=['all','service','candidate','confirmation'],default='all')
    parser.add_argument('--mixed',action='store_true',help='One third minors and one sixth function holders')
    parser.add_argument('--legacy-selection',action='store_true',help='Keep earlier direct session-injection comparison')
    args=parser.parse_args(); main(args.members,args.mixed,args.legacy_selection,args.actions)
