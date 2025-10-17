# main.py
# Just to demonstrate Aho-Corasick usage and output formatting
from __future__ import annotations

from importlib.machinery import SourceFileLoader
from collections import defaultdict
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.text import Text

# --- Load Aho-Corasick from a filename with a dash. >_<
ac_module = SourceFileLoader("aho_corasick", "aho-corasick.py").load_module()
AhoCorasick = ac_module.AhoCorasick  # type: ignore[attr-defined]

console = Console()


def group_matches(matches: List[Tuple[int, int]], patterns: List[str]) -> Dict[str, List[int]]:
    """
    Group matches by pattern string.
    Return: {pattern: [start_index, ...] (sorted)}
    """
    groups: Dict[str, List[int]] = defaultdict(list)
    for start, pidx in matches:
        pat = patterns[pidx]
        groups[pat].append(start)
    for pat in groups:
        groups[pat].sort()
    return groups


def snippet_with_highlight(text: str, start: int, length: int, context: int = 40) -> Text:
    """
    Build a snippet around the match and highlight it (bold cyan).
    """
    end = start + length
    # Clamp context window
    s = max(0, start - context)
    e = min(len(text), end + context)

    # Build Text snippet
    snippet = Text()
    if s > 0:
        snippet.append("…")
    snippet.append(text[s:start])
    matched = Text(text[start:end], style="bold cyan")
    snippet.append(matched)
    snippet.append(text[end:e])
    if e < len(text):
        snippet.append("…")

    # Quote it
    quoted = Text('"')
    quoted.append(snippet)
    quoted.append('"')
    return quoted


def main() -> None:
    text = (
        "She sells seashells by the seashore while he whistles and she hums. "
        "The shepherd shouted that his sheep were hers, but he knew she didn't hear. "
        "In the hush of the evening, the usher showed her seat as the show began."
    )

    patterns = [
        "she",
        "he",
        "his",
        "hers",
        "her",
        "sea",
        "seashells",
        "seashore",
        "shore",
        "sheep",
        "shepherd",
        "hush",
        "usher",
        "show",
        "seat",
        "whistles",
        "hums",
        "evening",
        "knew",
        "hear",
    ]

    ac = AhoCorasick(patterns)
    matches = ac.search(text)  # [(start, pattern_index), ...]

    console.print(Text("Original sentence:", style="bold"))
    console.print(Text(text))
    console.print()

    groups = group_matches(matches, patterns)

    # ---- Summary table -------------------------------------------------------
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Pattern", style="cyan", no_wrap=True)
    table.add_column("Count", style="yellow", justify="right")
    table.add_column("First Hit (idx)", style="green", justify="right")
    table.add_column("Example", style="white")

    # Stable order: by pattern name
    for pat in sorted(groups.keys()):
        starts = groups[pat]
        first = starts[0]
        row_example = snippet_with_highlight(text, first, len(pat), context=35)
        table.add_row(pat, str(len(starts)), str(first), row_example)

    console.print(table)
    console.print()


if __name__ == "__main__":
    main()
