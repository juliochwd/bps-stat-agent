"""Tests for mini_agent/utils/terminal_utils.py — terminal display utilities."""

import pytest

from mini_agent.utils.terminal_utils import (
    ANSI_ESCAPE_RE,
    calculate_display_width,
    pad_to_width,
    truncate_with_ellipsis,
)


class TestCalculateDisplayWidth:
    """Tests for calculate_display_width."""

    def test_ascii_text(self):
        assert calculate_display_width("Hello") == 5

    def test_empty_string(self):
        assert calculate_display_width("") == 0

    def test_east_asian_wide(self):
        """Chinese characters are 2 columns each."""
        assert calculate_display_width("你好") == 4

    def test_emoji(self):
        """Emoji characters are 2 columns."""
        assert calculate_display_width("🤖") == 2

    def test_ansi_escape_codes(self):
        """ANSI codes should not count toward width."""
        assert calculate_display_width("\033[31mRed\033[0m") == 3

    def test_mixed_content(self):
        """Mixed ASCII, CJK, and ANSI."""
        text = "\033[1mHello 你好\033[0m"
        # "Hello " = 6, "你好" = 4, ANSI = 0
        assert calculate_display_width(text) == 10

    def test_combining_characters(self):
        """Combining characters have zero width."""
        # 'e' + combining acute accent
        text = "é"
        assert calculate_display_width(text) == 1

    def test_fullwidth_characters(self):
        """Fullwidth Latin characters are 2 columns."""
        # Ａ is fullwidth A
        assert calculate_display_width("Ａ") == 2


class TestTruncateWithEllipsis:
    """Tests for truncate_with_ellipsis."""

    def test_no_truncation_needed(self):
        assert truncate_with_ellipsis("Hello", 10) == "Hello"

    def test_exact_width(self):
        assert truncate_with_ellipsis("Hello", 5) == "Hello"

    def test_truncation(self):
        result = truncate_with_ellipsis("Hello World", 8)
        assert len(result) <= 8
        assert result.endswith("…")

    def test_zero_width(self):
        assert truncate_with_ellipsis("Hello", 0) == ""

    def test_width_less_than_ellipsis(self):
        result = truncate_with_ellipsis("Hello World", 1)
        assert len(result) == 1

    def test_cjk_truncation(self):
        """CJK characters should be truncated respecting 2-column width."""
        result = truncate_with_ellipsis("你好世界", 5)
        # "你好" = 4 columns + "…" = 1 column = 5
        assert calculate_display_width(result) <= 5

    def test_ansi_stripped_on_truncation(self):
        """ANSI codes are stripped when truncation is needed."""
        text = "\033[31mHello World\033[0m"
        result = truncate_with_ellipsis(text, 8)
        assert "\033" not in result


class TestPadToWidth:
    """Tests for pad_to_width."""

    def test_left_align(self):
        result = pad_to_width("Hello", 10, align="left")
        assert result == "Hello     "
        assert calculate_display_width(result) == 10

    def test_right_align(self):
        result = pad_to_width("Hello", 10, align="right")
        assert result == "     Hello"

    def test_center_align(self):
        result = pad_to_width("Test", 10, align="center")
        assert result == "   Test   "

    def test_no_padding_needed(self):
        result = pad_to_width("Hello", 5, align="left")
        assert result == "Hello"

    def test_text_wider_than_target(self):
        result = pad_to_width("Hello World", 5, align="left")
        assert result == "Hello World"

    def test_cjk_padding(self):
        """CJK characters should be padded correctly."""
        result = pad_to_width("你好", 10, align="left")
        # "你好" = 4 columns, need 6 spaces
        assert result == "你好      "
        assert calculate_display_width(result) == 10

    def test_invalid_align(self):
        with pytest.raises(ValueError, match="Invalid align"):
            pad_to_width("Hello", 10, align="invalid")

    def test_custom_fill_char(self):
        result = pad_to_width("Hi", 6, align="left", fill_char=".")
        assert result == "Hi...."


class TestAnsiEscapeRegex:
    """Test the ANSI escape regex."""

    def test_removes_color_codes(self):
        text = "\033[31mRed\033[0m"
        clean = ANSI_ESCAPE_RE.sub("", text)
        assert clean == "Red"

    def test_removes_bold(self):
        text = "\033[1mBold\033[0m"
        clean = ANSI_ESCAPE_RE.sub("", text)
        assert clean == "Bold"

    def test_no_ansi(self):
        text = "Plain text"
        clean = ANSI_ESCAPE_RE.sub("", text)
        assert clean == "Plain text"
