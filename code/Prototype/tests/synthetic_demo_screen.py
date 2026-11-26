"""Exercise retained demo helpers only in an AppTest-owned temporary script.

No runtime flag, session-state switch or user route is added to the planner.
"""
from pathlib import Path


def use_synthetic_demo(app):
    script = Path(app._script_path)
    source = script.read_text()
    production = Path(__file__).parents[1] / 'streamlit_app.py'
    assert script.resolve() != production.resolve()
    marker = 'demo = False  # The normal planner always uses operational sources.'
    demo_marker = 'demo = True  # Synthetic test copy only.'
    assert source.count(marker) + source.count(demo_marker) == 1
    if marker in source:
        script.write_text(source.replace(marker, demo_marker))
    app.run()
    assert not app.exception
    return app
