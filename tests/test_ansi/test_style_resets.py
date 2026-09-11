from xulbux.ansi import S, _style_reset_codes


def test_fg_color_auto_restore_after_nested_fg_color() -> None:
    result = S.GREEN("Green ", S.RED("Red "), "Green again")
    assert result.ansi == "\x1b[32mGreen \x1b[31mRed \x1b[39m\x1b[32mGreen again\x1b[39m"
    assert result.raw == "Green Red Green again"

    hex_result = S.hex("#00ff00")("Hex green ", S.hex("#ff0000")("Hex red "), "Hex green again")
    assert (
        hex_result.ansi
        == "\x1b[38;2;0;255;0mHex green \x1b[38;2;255;0;0mHex red \x1b[39m\x1b[38;2;0;255;0mHex green again\x1b[39m"
    )
    assert hex_result.raw == "Hex green Hex red Hex green again"

    c256_result = S.color256(46)("256 green ", S.color256(196)("256 red "), "256 green again")
    assert c256_result.ansi == "\x1b[38;5;46m256 green \x1b[38;5;196m256 red \x1b[39m\x1b[38;5;46m256 green again\x1b[39m"
    assert c256_result.raw == "256 green 256 red 256 green again"


def test_bg_color_auto_restore_after_nested_bg_color() -> None:
    result = S.BG.BLUE("Blue ", S.BG.RED("Red "), "Blue again")
    assert result.ansi == "\x1b[44mBlue \x1b[41mRed \x1b[49m\x1b[44mBlue again\x1b[49m"
    assert result.raw == "Blue Red Blue again"

    hex_result = S.BG.hex("#0000ff")("Hex blue ", S.BG.hex("#ff0000")("Hex red "), "Hex blue again")
    assert (
        hex_result.ansi
        == "\x1b[48;2;0;0;255mHex blue \x1b[48;2;255;0;0mHex red \x1b[49m\x1b[48;2;0;0;255mHex blue again\x1b[49m"
    )
    assert hex_result.raw == "Hex blue Hex red Hex blue again"

    c256_result = S.BG.color256(21)("256 blue ", S.BG.color256(196)("256 red "), "256 blue again")
    assert c256_result.ansi == "\x1b[48;5;21m256 blue \x1b[48;5;196m256 red \x1b[49m\x1b[48;5;21m256 blue again\x1b[49m"
    assert c256_result.raw == "256 blue 256 red 256 blue again"


def test_intensity_auto_restore_bold_and_dim() -> None:
    dim_result = S.DIM("Some dim ", S.BOLD("& bold"), " text…")
    assert dim_result.ansi == "\x1b[2mSome dim \x1b[1m& bold\x1b[22m\x1b[2m text…\x1b[22m"
    assert dim_result.raw == "Some dim & bold text…"

    bold_result = S.BOLD("Some bold ", S.DIM("& dim"), " text…")
    assert bold_result.ansi == "\x1b[1mSome bold \x1b[2m& dim\x1b[22m\x1b[1m text…\x1b[22m"
    assert bold_result.raw == "Some bold & dim text…"


def test_underline_auto_restore_single_and_double() -> None:
    under_result = S.UNDERLINE("Under ", S.DOUBLE_UNDERLINE("Double "), "Under again")
    assert under_result.ansi == "\x1b[4mUnder \x1b[21mDouble \x1b[24m\x1b[4mUnder again\x1b[24m"
    assert under_result.raw == "Under Double Under again"

    double_result = S.DOUBLE_UNDERLINE("Double ", S.UNDERLINE("Single "), "Double again")
    assert double_result.ansi == "\x1b[21mDouble \x1b[4mSingle \x1b[24m\x1b[21mDouble again\x1b[24m"
    assert double_result.raw == "Double Single Double again"


def test_explicit_resets_not_restored() -> None:
    assert S.RED("Red ", S.RESET_FG, "Default ").ansi == "\x1b[31mRed \x1b[39mDefault \x1b[39m"
    assert S.DIM("Dim ", S.RESET_DIM, "Default ").ansi == "\x1b[2mDim \x1b[22mDefault \x1b[22m"
    assert S.BG.BLUE("Blue ", S.RESET_BG, "Default ").ansi == "\x1b[44mBlue \x1b[49mDefault \x1b[49m"
    assert S.UNDERLINE("Underline ", S.RESET_UNDERLINE, "Default ").ansi == "\x1b[4mUnderline \x1b[24mDefault \x1b[24m"
    assert S.BOLD("Bold ", S.RESET, "Default ").ansi == "\x1b[1mBold \x1b[0mDefault \x1b[22m"
    assert (
        S(S.RED("Red ", S.RESET_FG, "Default "), "Still default").ansi == "\x1b[31mRed \x1b[39mDefault \x1b[39mStill default"
    )


def test_orthogonal_styles_no_redundant_restore() -> None:
    assert S.GREEN("Green ", S.BOLD("Bold "), "Green again").ansi == "\x1b[32mGreen \x1b[1mBold \x1b[22mGreen again\x1b[39m"
    assert (
        S.BG.BLUE("Blue ", S.ITALIC("Italic "), "Blue again").ansi == "\x1b[44mBlue \x1b[3mItalic \x1b[23mBlue again\x1b[49m"
    )


def test_style_group_auto_restore() -> None:
    # Outer bold + green, inner red (only green reset):
    assert (S.BOLD | S.GREEN)(
        "Bold green ", S.RED("Bold red "), "Bold green again"
    ).ansi == "\x1b[1;32mBold green \x1b[31mBold red \x1b[39m\x1b[32mBold green again\x1b[22;39m"

    # Outer bold + green, inner dim (only bold reset):
    assert (S.BOLD | S.GREEN)(
        "Bold green ", S.DIM("Dim green "), "Bold green again"
    ).ansi == "\x1b[1;32mBold green \x1b[2mDim green \x1b[22m\x1b[1mBold green again\x1b[22;39m"

    # Outer bold + green, inner dim + red (both reset):
    assert (S.BOLD | S.GREEN)(
        "Bold green ", (S.DIM | S.RED)("Dim red "), "Bold green again"
    ).ansi == "\x1b[1;32mBold green \x1b[2;31mDim red \x1b[22;39m\x1b[1;32mBold green again\x1b[22;39m"

    # Group with duplicate reset channels (last active style restored):
    assert (S.RED | S.GREEN)(
        "Green ", S.BLUE("Blue "), "Green again"
    ).ansi == "\x1b[31;32mGreen \x1b[34mBlue \x1b[39m\x1b[32mGreen again\x1b[39m"


def test_end_of_block_no_trailing_restore() -> None:
    assert S.GREEN("Green ", S.RED("Red")).ansi == "\x1b[32mGreen \x1b[31mRed\x1b[39m\x1b[39m"
    assert S.DIM("Dim ", S.BOLD("Bold")).ansi == "\x1b[2mDim \x1b[1mBold\x1b[22m\x1b[22m"


def test_nested_tuples_auto_restore() -> None:
    # Conflicting item inside tuple followed by another item inside tuple:
    assert (
        S.GREEN("Green ", (S.RED("Red "), "Inner green "), "Outer green").ansi
        == "\x1b[32mGreen \x1b[31mRed \x1b[39m\x1b[32mInner green Outer green\x1b[39m"
    )

    # Conflicting item at the end of the tuple:
    assert (
        S.GREEN("Green ", ("Inner green 1 ", S.RED("Red ")), "Outer green").ansi
        == "\x1b[32mGreen Inner green 1 \x1b[31mRed \x1b[39m\x1b[32mOuter green\x1b[39m"
    )


def test_matmul_operator_auto_restore() -> None:
    assert (
        S.GREEN("Green ", S.RED("Red "), "Green again")
    ).ansi == "\x1b[32mGreen \x1b[31mRed \x1b[39m\x1b[32mGreen again\x1b[39m"
    assert (
        S.hex("#00ff00")("Hex green ", S.hex("#ff0000")("Hex red "), "Hex green again")
    ).ansi == "\x1b[38;2;0;255;0mHex green \x1b[38;2;255;0;0mHex red \x1b[39m\x1b[38;2;0;255;0mHex green again\x1b[39m"
    assert (
        S.color256(46)("256 green ", S.color256(196)("256 red "), "256 green again")
    ).ansi == "\x1b[38;5;46m256 green \x1b[38;5;196m256 red \x1b[39m\x1b[38;5;46m256 green again\x1b[39m"
    assert (
        (S.BOLD | S.GREEN)("Bold green ", S.RED("Bold red "), "Bold green again")
    ).ansi == "\x1b[1;32mBold green \x1b[31mBold red \x1b[39m\x1b[32mBold green again\x1b[22;39m"


def test_gradient_nested_in_color_restores_color() -> None:
    assert "\x1b[32mGreen again\x1b[39m" in S.GREEN("Green ", S.gradient("#ff0000", "#0000ff")("Grad"), "Green again").ansi
    assert (S.BOLD | S.DIM | S.gradient("#ff0000", "#0000ff"))("Grad")._reset_codes == (39, 22)


def test_slice_and_mul_preserves_reset_codes() -> None:
    red_obj = S.RED("12345")
    assert red_obj._reset_codes == (39,)
    assert red_obj[1:4]._reset_codes == (39,)
    assert (red_obj * 2)._reset_codes == (39,)


def test_style_reset_codes_edge_cases() -> None:
    assert _style_reset_codes(S.RESET) == ()
    assert _style_reset_codes(S.link("https://example.com")) == ()
