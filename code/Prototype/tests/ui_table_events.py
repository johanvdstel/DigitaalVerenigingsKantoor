"""Synthetic editor events: AppTest has no public data_editor edit helper.

Send the same JSON widget-state protocol as a native checkbox edit, so callbacks
and Streamlit reruns are exercised rather than calling UI functions directly.
"""
import json


def table(app, prefix="candidate-table-"):
    return next(t for t in app.dataframe if t.key and t.key.startswith(prefix))


def edit(app, target, edits):
    states = app._tree.get_widget_states()
    # Existing edits must survive subsequent cell edits, just as in the browser.
    value = dict(app.session_state[target.key])
    rows = {str(k): dict(v) for k, v in value.get("edited_rows", {}).items()}
    for index, changes in edits.items():
        rows.setdefault(str(index), {}).update(changes)
    value.update(edited_rows=rows, added_rows=[], deleted_rows=[])
    retained = [state for state in states.widgets if state.id != target.proto.id]
    del states.widgets[:]
    states.widgets.extend(retained)
    state = states.widgets.add()
    state.id = target.proto.id
    state.string_value = json.dumps(value)
    return app._run(states)


def pick(app, index=0, value=True):
    return edit(app, table(app), {index: {"Kies": value}})


def editor_widget_state(node):
    """AppTest omits editor state on button reruns; browsers submit it each time."""
    from streamlit.proto.WidgetStates_pb2 import WidgetState
    if node.type != "dataframe" or not node.key or not node.proto.editing_mode:
        return None
    state = WidgetState()
    state.id = node.proto.id
    try:
        value = node.root._runner.session_state[node.key]
    except KeyError:
        return None  # Deliberately invalidated widget from the previous screen.
    state.string_value = json.dumps(dict(value))
    return state


def preserving_editors(original):
    def get_state(node):
        return editor_widget_state(node) or original(node)
    return get_state


def choose_service(app, index):
    target = table(app, "services_editor-")
    if not target.proto.button_click_widgets:
        return edit(app, target, {index: {"Kies": True}})
    states = app._tree.get_widget_states()
    state = states.widgets.add()
    state.id = target.proto.button_click_widgets["Kies"]
    state.string_trigger_value.data = json.dumps({"row": index, "label": target.value.iloc[index]["Kies"]})
    return app._run(states)
