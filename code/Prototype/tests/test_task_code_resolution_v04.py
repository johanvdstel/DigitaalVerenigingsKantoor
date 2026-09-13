from dvk.shift_catalog import ShiftDefinition
from dvk.task_code_resolution import resolve_task_code


def definition(task_code: str, service_type: str = "Bar") -> ShiftDefinition:
    return ShiftDefinition(task_code, service_type, 2.5, 1, 2)


def test_r15_known_task_code_resolves_exact_definition():
    known = definition("741", "Bar weekend")
    result = resolve_task_code("741", (known, definition("442", "Commissiekamer")))

    assert result.definition == known
    assert not result.signals


def test_r15_unknown_task_code_is_signalled_and_not_mapped():
    result = resolve_task_code("999", (definition("741"), definition("442")))

    assert result.definition is None
    assert len(result.signals) == 1
    assert result.signals[0].code == "UNKNOWN_TASK_CODE"
    assert result.signals[0].record_key == "999"


def test_r15_similar_code_is_not_guessed():
    result = resolve_task_code("74", (definition("741"), definition("761")))

    assert result.definition is None
    assert result.signals[0].code == "UNKNOWN_TASK_CODE"


def test_r15_whitespace_is_not_silently_trimmed():
    result = resolve_task_code("741 ", (definition("741"),))

    assert result.definition is None
    assert result.signals[0].code == "UNKNOWN_TASK_CODE"


def test_r15_ambiguous_task_code_is_signalled_without_choice():
    result = resolve_task_code(
        "741",
        (definition("741", "Bar A"), definition("741", "Bar B")),
    )

    assert result.definition is None
    assert len(result.signals) == 1
    assert result.signals[0].code == "AMBIGUOUS_TASK_CODE"
