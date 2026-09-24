import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_streamlit_has_no_replacement_controls_or_imports():
    text = (ROOT / "streamlit_app.py").read_text()
    for abandoned in ("### Vervangende inzet", "Vervangende inzet koppelen", "Uitgevoerd bevestigen", "replacement", "ReplacementDuty"):
        assert abandoned not in text


def test_production_code_has_no_replacement_dependency():
    assert not (ROOT / "dvk/replacement_duty.py").exists()
    assert not (ROOT / "dvk/persistence/replacement_records.py").exists()
    for path in [ROOT / "streamlit_app.py", *(ROOT / "dvk").rglob("*.py")]:
        text = path.read_text()
        assert "ReplacementDuty" not in text, path
        assert "ActiveSanctionState" not in text, path
        assert "active_sanction_state" not in text, path
        if path.name != "migrations.py":
            assert "replacement_duties" not in text, path
            assert "replacement_records" not in text, path
        imports = [n for n in ast.walk(ast.parse(text)) if isinstance(n, (ast.Import, ast.ImportFrom))]
        assert not any("replacement" in ast.unparse(n) for n in imports), path
