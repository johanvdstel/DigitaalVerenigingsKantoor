import ast
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from dvk.application_services import AssignmentContext, ReplacementLinkContext, ReplacementOverview, ReplacementStatusContext
from dvk.demo_data_v05 import demo_candidate_cases, demo_planning_data
from dvk.replacement_duty import ReplacementDuty
from dvk.no_show import NoShowEvent
from dvk.workstream_model import DutyAssignment


SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def _presentation_namespace():
    """Execute the pure formatting helpers without starting the Streamlit app."""
    tree = ast.parse(SOURCE.read_text())
    selected = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in {"_datum_met_dag", "_assignment_label"}
    ) or (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DAGEN" for t in node.targets)
    )]
    namespace = {"datetime": datetime}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


def _context():
    services, _, _, _ = demo_planning_data(datetime(2026, 9, 14).date())
    person = demo_candidate_cases()[2].person
    assignment = DutyAssignment("UI-technical-assignment", "proposal", services[2].service_id, person.person_id, "parent_guardian", 4.5, "vc1")
    return AssignmentContext(assignment, services[2], person.name)


def test_shared_assignment_label_shows_actual_human_context_without_internal_ids():
    context = _context()
    label = _presentation_namespace()["_assignment_label"](context)
    assert label == "za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis"
    assert context.assignment.assignment_id == "UI-technical-assignment"
    assert context.assignment.assignment_id not in label
    assert context.assignment.service_id not in label
    assert context.assignment.person_id not in label


def test_missing_context_is_explicit_without_guessing_name_service_or_date():
    context = _context()
    label = _presentation_namespace()["_assignment_label"]
    assert label(AssignmentContext(context.assignment, None, None)) == "Datum/tijd en dienst onbekend — Persoon onbekend"
    assert label(AssignmentContext(context.assignment, None, context.person_name)) == "Datum/tijd en dienst onbekend — Jeugdlid Thuis"
    assert label(AssignmentContext(context.assignment, context.service, None)).endswith(" — Persoon onbekend")


def test_streamlit_uses_public_services_instead_of_repositories_or_private_state():
    tree = ast.parse(SOURCE.read_text())
    attributes = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
    assert not any(isinstance(node.value, ast.Name) and node.value.id == "uow" for node in attributes)
    assert not any(node.attr.startswith("_") for node in attributes)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert any(node.func.attr == "overview" for node in calls)
    assert any(node.func.attr == "assignment_contexts" for node in calls)


class _Display:
    def __init__(self):
        self.warnings = []
        self.infos = []
        self.choices = []
        self.buttons = []

    def warning(self, text): self.warnings.append(text)
    def info(self, text): self.infos.append(text)
    def write(self, text): pass
    def form(self, key): return self
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def form_submit_button(self, label, **kwargs): return False

    def selectbox(self, label, options, *, format_func):
        self.choices.append((tuple(options), tuple(format_func(key) for key in options)))
        return options[0]

    def columns(self, count): return (self,) * count

    def button(self, label, **kwargs):
        self.buttons.append(label)
        return False


def _render_replacement_status(overview):
    """Exercise the actual status/selection block with a small display double."""
    tree = ast.parse(SOURCE.read_text())
    start = next(i for i, node in enumerate(tree.body) if isinstance(node, ast.For)
                 and isinstance(node.iter, ast.Attribute) and node.iter.attr == "with_no_show")
    block = ast.Module(body=tree.body[start:start + 2], type_ignores=[])
    namespace = _presentation_namespace()
    display = _Display()
    namespace.update(st=display, replacement_overview=overview)
    exec(compile(block, str(SOURCE), "exec"), namespace)
    return display


def _row(replacement_id="R1"):
    context = _context()
    replacement = ReplacementDuty(replacement_id, "N1", context.assignment.assignment_id,
                                  context.assignment.person_id, "2026/2027", datetime(2026, 9, 18), "vc1")
    return ReplacementStatusContext(replacement, context)


def test_replacement_no_show_is_visible_without_pending_selector_or_completion_button():
    display = _render_replacement_status(ReplacementOverview((), (), (_row(),)))
    assert display.warnings == ["za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis — No-show geregistreerd op vervangende dienst."]
    assert display.choices == []
    assert display.buttons == []
    assert display.infos == []  # Must not also claim there are no open replacements.


def test_only_normal_pending_replacement_is_selectable_using_stable_internal_key():
    display = _render_replacement_status(ReplacementOverview((), (_row("pending-id"),), (_row("no-show-id"),)))
    assert display.choices == [(('pending-id',), ("za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis",))]
    assert display.buttons == ["Uitgevoerd bevestigen", "No-show vastleggen voor vervangende inzet"]
    assert len(display.warnings) == 1


def test_link_choices_keep_distinct_assignment_ids_even_with_equal_human_labels():
    context = _context()
    other = replace(context, assignment=replace(context.assignment, assignment_id="second-assignment"))
    when = datetime(2026, 9, 18, 10)
    event = NoShowEvent("N1", "original", context.assignment.person_id, when, when, "vc1", "2026/2027")
    option = ReplacementLinkContext(event, context, (context, other))
    tree = ast.parse(SOURCE.read_text())
    block = next(node for node in tree.body if isinstance(node, ast.If)
                 and isinstance(node.test, ast.Attribute) and node.test.attr == "link_options")
    display = _Display()
    namespace = _presentation_namespace()
    namespace.update(st=display, replacement_overview=ReplacementOverview((option,), (), ()))
    exec(compile(ast.Module(body=[block], type_ignores=[]), str(SOURCE), "exec"), namespace)
    keys, labels = display.choices[1]
    assert keys == ("UI-technical-assignment", "second-assignment")
    assert labels == ("za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis",) * 2


def test_streamlit_source_compiles_without_importing_or_starting_app():
    compile(SOURCE.read_text(), str(SOURCE), "exec")
