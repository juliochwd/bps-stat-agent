"""Tests for the shared Colors module."""

from mini_agent.colors import Colors


class TestColors:
    def test_reset_defined(self):
        assert Colors.RESET == "\033[0m"

    def test_bold_defined(self):
        assert Colors.BOLD == "\033[1m"

    def test_all_foreground_colors(self):
        """Verify all standard foreground colors are defined."""
        for attr in ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"]:
            assert hasattr(Colors, attr)
            assert "\033[" in getattr(Colors, attr)

    def test_all_bright_colors(self):
        """Verify all bright colors are defined."""
        for attr in [
            "BRIGHT_RED",
            "BRIGHT_GREEN",
            "BRIGHT_YELLOW",
            "BRIGHT_BLUE",
            "BRIGHT_MAGENTA",
            "BRIGHT_CYAN",
            "BRIGHT_WHITE",
            "BRIGHT_BLACK",
        ]:
            assert hasattr(Colors, attr)
            assert "\033[9" in getattr(Colors, attr) or "\033[90" in getattr(Colors, attr)

    def test_background_colors(self):
        """Verify background colors are defined."""
        for attr in ["BG_RED", "BG_GREEN", "BG_YELLOW", "BG_BLUE"]:
            assert hasattr(Colors, attr)
            assert "\033[4" in getattr(Colors, attr)
