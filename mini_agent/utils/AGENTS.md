<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# utils — Utility Modules

## Purpose

Terminal display utilities for the BPS Stat Agent CLI. Provides Unicode-aware text width calculation for proper box-drawing alignment in the interactive terminal interface, handling ANSI escape codes, emoji, East Asian wide characters, and combining characters correctly.

This is a **leaf module** with no internal or external dependencies — pure Python implementation.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Re-exports: `calculate_display_width`, `pad_to_width`, `truncate_with_ellipsis`. |
| `terminal_utils.py` | Implementation of display width calculation. Uses compiled regex `ANSI_ESCAPE_RE` for stripping ANSI codes. Unicode category detection via `unicodedata.east_asian_width()` for CJK characters (width 2). Emoji detection via Unicode range (U+1F300-U+1FAFF, width 2). Combining characters (width 0). Standard ASCII (width 1). |

## For AI Agents

### Working In This Directory

- `calculate_display_width(text: str) -> int` — returns visual width of text in terminal columns. Correctly handles:
  - ANSI escape sequences (stripped, width 0)
  - Emoji characters (width 2)
  - East Asian Wide/Fullwidth characters like CJK (width 2)
  - Combining characters (width 0)
  - Regular ASCII (width 1)
- `pad_to_width(text: str, width: int) -> str` — pads text with spaces to exact visual width
- `truncate_with_ellipsis(text: str, max_width: int) -> str` — truncates with "..." respecting visual width
- These are used throughout `cli.py` for box-drawing alignment (banners, step headers, session info boxes)
- ANSI escape sequences are stripped before width calculation using pre-compiled regex

### Testing Requirements

- Test with pure ASCII strings
- Test with CJK characters (e.g., "你好" should be width 4)
- Test with emoji (e.g., "🤖" should be width 2)
- Test with ANSI color codes (should be width 0)
- Test with mixed content (ASCII + ANSI + emoji + CJK)
- Test `pad_to_width` produces correct visual alignment
- Test `truncate_with_ellipsis` respects visual width boundaries

### Common Patterns

```python
from mini_agent.utils import calculate_display_width

# Calculate visual width (ignoring ANSI color codes)
width = calculate_display_width(f"{Colors.BOLD}Step 1/50{Colors.RESET}")

# Pad for box alignment
BOX_WIDTH = 58
padding = max(0, BOX_WIDTH - 1 - width)  # -1 for leading space

# Truncate long text
short = truncate_with_ellipsis(long_text, max_width=50)
```

## Dependencies

### Internal
- None (leaf module — no internal dependencies)

### External
- None (pure Python: `re`, `unicodedata` from stdlib)
