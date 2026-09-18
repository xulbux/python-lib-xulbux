import xulbux.data as _data_module
from xulbux.ansi import S
from xulbux.data import _DataRenderHelper
import pytest


def test_render_compactness_levels() -> None:
    sample_data = {"a": [1, 2, 3], "b": {"c": 4}}

    rendered_expanded = _data_module.render(sample_data, compactness=0)
    assert "\n" in rendered_expanded.raw

    rendered_compact = _data_module.render(sample_data, compactness=2)
    assert "\n" not in rendered_compact.raw

    rendered_auto = _data_module.render(sample_data, compactness=1)
    assert len(rendered_auto.raw) > 0

    rendered_primitive = _data_module.render(42)  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]
    assert rendered_primitive.raw == "42"


def test_render_json_mode() -> None:
    sample_data = {"text": "hello", "active": True, "count": 42, "empty": None}
    rendered_json = _data_module.render(sample_data, as_json=True)
    assert '"text": "hello"' in rendered_json.raw
    assert '"active": true' in rendered_json.raw
    assert '"count": 42' in rendered_json.raw
    assert '"empty": null' in rendered_json.raw

    rendered_special = _data_module.render({"inf": float("inf"), "nan": float("nan")}, as_json=True)
    assert '"inf": null' in rendered_special.raw
    assert '"nan": null' in rendered_special.raw


def test_render_syntax_highlighting() -> None:
    rendered_hl = _data_module.render({"a": 1, "b": "str"}, syntax_highlighting=True)
    assert rendered_hl.ansi != rendered_hl.raw

    custom_hl = _data_module.render({"a": 1}, syntax_highlighting={"number": S.RED})
    assert custom_hl is not None


def test_render_data_types_formatting() -> None:
    assert _data_module.render({"bytes": b"hello"}, as_json=False).ansi != ""
    assert _data_module.render({"bytearray": bytearray(b"hello")}, as_json=False).ansi != ""
    assert _data_module.render({"bytes": b"\xff\xfe"}, as_json=False).ansi != ""
    assert _data_module.render({"bytes": b"\xff\xfe"}, as_json=True).raw != ""
    assert _data_module.render({"complex": 1 + 2j}, as_json=False).ansi != ""
    assert _data_module.render({"complex": 1 + 2j}, as_json=True).raw != ""
    assert _data_module.render({1, 2}).ansi != ""
    assert _data_module.render(frozenset([1, 2])).ansi != ""
    assert _data_module.render(set()).ansi != ""
    assert _data_module.render(frozenset()).ansi != ""
    assert _data_module.render((1,)).ansi != ""
    assert _data_module.render([1, 2], as_json=True).raw != ""

    class CustomObject:
        def __init__(self) -> None:
            self.attr = "value"

    assert _data_module.render({"custom": CustomObject()}).raw != ""


def test_render_complexity_calculation() -> None:
    rendered_nested = _data_module.render(
        {"tuple": (1, (2,)), "set": {1, frozenset([2])}, "frozen": frozenset([1, 2]), "list": [1, [2]]},
        compactness=1,
    )
    assert len(rendered_nested.raw) > 0


def test_should_expand_compactness_2() -> None:
    helper = _DataRenderHelper([1], indent=0, compactness=2, max_width=10, sep=",", as_json=False, syntax_highlighting=False)
    assert helper.should_expand([1]) is False


def test_render_validation_errors() -> None:
    with pytest.raises(ValueError, match="must be a non-negative integer"):
        _data_module.render({}, indent=-1)

    with pytest.raises(ValueError, match="must be a positive integer"):
        _data_module.render({}, max_width=0)

    with pytest.raises(TypeError, match="must be a dict or bool"):
        _data_module.render({}, syntax_highlighting="invalid_type")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]


def test_render_max_width_dict_expansion() -> None:
    short_dict = {"a": 1, "b": 2}
    rendered_short = _data_module.render(short_dict, compactness=1, max_width=50)
    assert "\n" not in rendered_short.raw

    long_dict = {
        "total": "15.7 GB",
        "available": "1.2 GB",
        "used": "14.5 GB",
        "usage_percent": "92.4%",
        "swap_total": "26.0 GB",
        "swap_used": "9.0 GB",
        "swap_percent": "34.5%",
    }
    rendered_long = _data_module.render(long_dict, compactness=1, max_width=50)
    assert "\n" in rendered_long.raw


def test_render_max_width_sequence_expansion() -> None:
    short_seq = [1, 2, 3]
    rendered_short = _data_module.render(short_seq, compactness=1, max_width=50)
    assert "\n" not in rendered_short.raw

    long_seq = [f"long_element_name_{i}" for i in range(10)]
    rendered_long = _data_module.render(long_seq, compactness=1, max_width=50)
    assert "\n" in rendered_long.raw


def test_render_nested_dict_line_width_expansion() -> None:
    nested_data: dict[str, dict[str, str | list[str]]] = {
        "memory": {
            "total": "15.7 GB",
            "available": "1.2 GB",
            "used": "14.5 GB",
            "usage_percent": "92.4%",
            "swap_total": "26.0 GB",
            "swap_used": "9.0 GB",
            "swap_percent": "34.5%",
        },
        "gpu": {"gpus": []},
    }
    rendered = _data_module.render(nested_data, indent=2, compactness=1, max_width=127, as_json=True)
    raw_lines = rendered.raw.splitlines()

    # Verify memory is expanded into multiple lines:
    assert '"memory": {' in rendered.raw

    # Verify compact gpu dict is preserved on a single line:
    assert '"gpu": {"gpus": []}' in rendered.raw

    # Verify no line exceeds `max_width`:
    for line in raw_lines:
        assert len(line) <= 127
