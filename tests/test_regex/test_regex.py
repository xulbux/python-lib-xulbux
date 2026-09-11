import xulbux.regex as _regex_module
import regex as rx


def test_quotes_matching_single_and_double() -> None:
    pattern = _regex_module.quotes()
    assert rx.findall(pattern, """He said 'Hello' and "World" and 'Another' string""") == [
        ("'", "Hello"),
        ('"', "World"),
        ("'", "Another"),
    ]
    assert rx.findall(pattern, "No quotes here") == []
    assert rx.findall(pattern, "") == []


def test_quotes_nested_and_escaped() -> None:
    pattern = _regex_module.quotes()
    assert len(rx.findall(pattern, r'He said "She said \"Hello\" to me"')) >= 1
    assert rx.findall(pattern, "Unclosed 'quote") == []


def test_brackets_standard_delimiters() -> None:
    assert rx.findall(_regex_module.brackets(), "Call fn(param1, param2) and fn(other)") == ["(param1, param2)", "(other)"]
    assert rx.findall(_regex_module.brackets("[", "]"), "Items [1, 2] and [3, 4]") == ["[1, 2]", "[3, 4]"]
    assert rx.findall(_regex_module.brackets("{", "}"), "Dict {a: 1} and {b: 2}") == ["{a: 1}", "{b: 2}"]


def test_brackets_options_group_spaces_and_strings() -> None:
    assert (match_group := rx.search(_regex_module.brackets(is_group=True), "fn(content)")) is not None
    assert match_group.group(1) == "content"

    assert len(rx.findall(_regex_module.brackets(strip_spaces=True, is_group=True), "fn( spaced content )")) == 1
    assert len(rx.findall(_regex_module.brackets(ignore_in_strings=True), 'fn("param(x)")')) == 1
    assert len(rx.findall(_regex_module.brackets(ignore_in_strings=False), 'fn("param(x)")')) >= 1

    assert rx.findall(_regex_module.brackets("<<", ">>"), "custom <<content>>") == ["<<content>>"]


def test_outside_strings() -> None:
    assert rx.findall(_regex_module.outside_strings(r"\d+"), 'Number 123 and "string 456" and 789') == ["123", "789"]
    assert isinstance(_regex_module.outside_strings(), str)


def test_all_except_with_and_without_ignore() -> None:
    assert (match := rx.match(_regex_module.all_except(">"), "Hello > World")) is not None
    assert match.group(0) == "Hello "

    assert (
        match_with_ignore := rx.match(_regex_module.all_except(">", "->", is_group=True), "Content without greater sign")
    ) is not None
    assert match_with_ignore.group(1) == "Content without greater sign"


def test_func_call_any_and_specific() -> None:
    assert rx.findall(_regex_module.func_call(), "call_one(1, 2) and call_two(3)") == [("call_one", "1, 2"), ("call_two", "3")]
    assert rx.findall(_regex_module.func_call(""), "call(1)") == [("call", "1")]
    assert rx.findall(_regex_module.func_call("print"), "print(hello) and input(prompt) and print(world)") == [
        ("print", "hello"),
        ("print", "world"),
    ]


def test_rgba_str_formats_and_options() -> None:
    assert len(rx.findall(_regex_module.rgba_str(), "rgba(255, 128, 0, 0.5), rgb(100, 200, 50), and 255,128,0")) == 3
    assert len(rx.findall(_regex_module.rgba_str(allow_alpha=False), "rgb(255, 0, 0)")) == 1
    assert len(rx.findall(_regex_module.rgba_str(fix_sep="|"), "255|128|0")) == 1
    assert len(rx.findall(_regex_module.rgba_str(fix_sep=None), "255 128 0")) == 1


def test_hsla_str_formats_and_options() -> None:
    assert len(rx.findall(_regex_module.hsla_str(), "hsla(240, 100%, 50%, 0.8), hsl(360, 100%, 50%), and 120,80%,60%")) == 3
    assert len(rx.findall(_regex_module.hsla_str(allow_alpha=False), "hsl(240, 100%, 50%)")) == 1
    assert len(rx.findall(_regex_module.hsla_str(fix_sep=" "), "240 100% 50%")) == 1
    assert len(rx.findall(_regex_module.hsla_str(fix_sep=None), "240-100%-50%")) == 1


def test_hexa_str_formats_and_options() -> None:
    assert (
        len(
            rx.findall(
                _regex_module.hexa_str(allow_alpha=True),
                "Colors: #FF0000, 0xABCDEF, F00, #FF0000FF, and 0xF00F",
            )
        )
        == 5
    )
    assert len(rx.findall(_regex_module.hexa_str(allow_alpha=False), "Colors: #FF0000 and F00")) == 2
