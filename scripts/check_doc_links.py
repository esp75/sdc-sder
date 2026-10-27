"""Check that every relative link in the README and docs/ points to a file that exists.

Anchors and external URLs are not checked. Exit status is 1 if any link is broken.

    uv run python scripts/check_doc_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"""(?:\]\(|src=["']|href=["'])([^)"'\s]+)""")


def documents() -> list[Path]:
    return [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]


def broken_links(path: Path) -> list[str]:
    problems = []
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        file_part = target.split("#", 1)[0]
        if not file_part:
            continue
        if not (path.parent / file_part).resolve().exists():
            problems.append(f"{path.resolve().relative_to(ROOT)}: {target}")
    return problems


def main() -> int:
    problems = [p for doc in documents() for p in broken_links(doc)]
    for problem in problems:
        print(f"broken: {problem}")
    print(f"checked {len(documents())} documents, {len(problems)} broken links")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
