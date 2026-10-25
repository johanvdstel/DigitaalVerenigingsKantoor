"""Synthetic server-side before/after AppTest timings (no browser timing).
Run from code/Prototype: python -B tests/measure_planning_actions.py --members 250
"""
import argparse
import cProfile
import json
import pstats
import statistics
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest
from ui_table_events import pick, preserving_editors
from streamlit.testing.v1 import element_tree
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.programma_client import SportlinkProgrammaClient, ProgrammaFetchResult
from dvk.persistence import SQLiteDatabase
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_v05 import exports
from test_volunteer_planning_integration_v05 import sync, PERIOD


def main(count):
    members=[dict(pid=f'SYNTH-{i}',born='01-01-1990',team='O17-1',number=str(i+1)) for i in range(count)]
    data=exports(members=members)
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
        source=Path(__file__).parents[1]/'streamlit_app.py'
        original=source.read_text().replace('value=date.today()','value=date(2026,10,19)')
        instrumented=original.replace('from __future__ import annotations',
            'from __future__ import annotations\nimport cProfile\n_profile=cProfile.Profile()\n_profile.enable()',1)
        target.write_text(instrumented+'\n_profile.disable()\n_profile.dump_stats('+repr(str(Path(directory)/'profile.stats'))+')\n')
        with patch.object(element_tree, 'get_widget_state', preserving_editors(element_tree.get_widget_state)), patch('dvk.local_csv_sources.read_export_text',read), patch.object(SportlinkProgrammaClient,'fetch_rows',fetch), patch.object(SQLiteDatabase,'initialize',init):
            app=AppTest.from_file(str(target),default_timeout=60).run()
            app.button(key='nav-planning').click().run()
            app.button(key='activate-planning').click().run()
            db=SQLiteDatabase(Path(directory)/'dvk_v05.sqlite')
            assert sync(db,load_shift_catalog(),{})[0] is None
            app.run()
            service_ids=app.dataframe[0].value.service_id.tolist()
            def timed(kind, action):
                before=dict(counters); start=time.perf_counter()
                # Streamlit's script runs in another thread; profile is collected
                # inside that script, not merely around the AppTest dispatcher.
                app.session_state['profile-run']=str(Path(directory)/'profile.stats')
                action()
                elapsed=time.perf_counter()-start
                stats=pstats.Stats(str(Path(directory)/'profile.stats'))
                stages={}
                for key,value in stats.stats.items():
                    if key[2] in {'propose','compare_required_hours','prioritize_candidates','initialize','_render_planning'}:
                        label=Path(key[0]).name+':'+key[2]
                        stages[label]=round(value[3]*1000,2)
                return {'action':kind,'wall_ms':round(elapsed*1000,2),
                        'calls':{key:counters[key]-before[key] for key in counters},'cumulative_ms':stages, 'sql_ms':round(sum(v[3]*1000 for k,v in stats.stats.items() if 'sqlite3.Connection' in k[2] and 'execute' in k[2]),2), 'sql_calls':sum(v[1] for k,v in stats.stats.items() if 'sqlite3.Connection' in k[2] and 'execute' in k[2])}
            results=[]
            for index in range(3):
                def select(index=index):
                    app.session_state['selected_service_id']=service_ids[index]
                    app.run()
                results.append(timed('service_selection',select))
            for index in range(3):
                results.append(timed('candidate_selection',lambda index=index:pick(app, value=index%2==0)))
            assert not app.exception
            print(json.dumps({'members':count,'results':results},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--members',type=int,default=250)
    main(parser.parse_args().members)
