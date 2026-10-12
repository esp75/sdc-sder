"""Parse the Rulebook Markdown into parts and rules, and render it to HTML.

Shared by ``build_rulebook_pdf.py`` (branded PDF) and ``export_rulebook.py``
(interactive version on maximekadri.org), so both are generated from the one
source file, ``spec/rulebook-v0.2-consultation-draft.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "spec" / "rulebook-v0.2-consultation-draft.md"
REPO_URL = "https://github.com/spacedebriscredit/sdc-sder/blob/main/"

PART_RE = re.compile(
    r"^## (Part ([A-J]): (.+)|Annex [A-Z]: .+|Consultation questions|How to read this draft)$"
)
RULE_RE = re.compile(r"^\*\*([A-J]\d+) (.+?)\*\*(.*)$")
KIND_RE = re.compile(r"^- \*(Rule|Why|Open)\.\*\s?(.*)$")

_md = MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")


@dataclass
class Segment:
    kind: str  # "rule" | "why" | "open" | "text"
    markdown: str


@dataclass
class Rule:
    id: str
    title: str
    coded: bool
    option: bool
    code_note: str = ""
    segments: list[Segment] = field(default_factory=list)


@dataclass
class Section:
    key: str  # "A".."J", or a slug for unlettered sections
    title: str
    intro: str = ""
    rules: list[Rule] = field(default_factory=list)


def math_html(tex: str) -> str:
    """Render the few TeX fragments the Rulebook uses as plain HTML."""
    s = tex.strip()
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = (
        s.replace(r"\times", "×")
        .replace("\\Delta ", "Δ")
        .replace(r"\Delta", "Δ")
        .replace(r"\sum", "Σ")
        .replace(r"\,", " ")
    )
    s = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", s)
    s = re.sub(r"(?<![<\w/])([A-Za-z]{1,2})(?=[\s<)=,]|$)", r"<i>\1</i>", s)
    return f'<span class="math">{s}</span>'


def render(markdown: str, *, absolute_links: bool = True) -> str:
    """Markdown to HTML, with math converted and repository links made absolute."""
    store: list[str] = []

    def stash(m: re.Match[str]) -> str:
        store.append(m.group(1))
        return f"MATHSLOT{len(store) - 1}TOLSHTAM"

    html = _md.render(re.sub(r"\$([^$]+)\$", stash, markdown))
    for i, tex in enumerate(store):
        html = html.replace(f"MATHSLOT{i}TOLSHTAM", math_html(tex))
    if absolute_links:
        html = re.sub(
            r'href="(?!https?:|#|mailto:)([^"]+)"', lambda m: f'href="{_absolute(m.group(1))}"', html
        )
    return html


def _absolute(path: str) -> str:
    """Resolve a link relative to ``spec/`` into a GitHub URL."""
    parts: list[str] = ["spec"]
    for piece in path.split("/"):
        if piece == "..":
            parts.pop() if parts else None
        elif piece != ".":
            parts.append(piece)
    return REPO_URL + "/".join(parts)


def parse(text: str | None = None) -> tuple[str, list[Section]]:
    """Return the header block and the ordered sections of the Rulebook."""
    lines = (text if text is not None else SOURCE.read_text()).splitlines()
    header: list[str] = []
    sections: list[Section] = []
    current_rule: Rule | None = None
    buffer: list[str] = []
    kind = "text"

    def flush() -> None:
        nonlocal buffer
        body = "\n".join(buffer).strip("\n")
        if body.strip():
            if current_rule is not None:
                current_rule.segments.append(Segment(kind, _dedent_item(body, kind)))
            elif sections:
                sections[-1].intro = (sections[-1].intro + "\n\n" + body).strip()
        buffer = []

    for line in lines[1:]:
        m = PART_RE.match(line)
        if m:
            flush()
            current_rule = None
            kind = "text"
            if m.group(2):
                sections.append(Section(m.group(2), m.group(3)))
            else:
                title = m.group(1)
                sections.append(Section(_slug(title), title))
            continue
        if not sections:
            header.append(line)
            continue
        if line.strip() == "---":
            continue
        r = RULE_RE.match(line)
        if r:
            flush()
            title = r.group(2).rstrip(".")
            rest = r.group(3)
            current_rule = Rule(
                id=r.group(1),
                title=title.replace(" (option)", ""),
                coded="⚙︎" in rest or "⚙︎" in title,
                option="(option)" in title,
            )
            sections[-1].rules.append(current_rule)
            kind = "text"
            if "⚙︎" in rest:
                current_rule.coded = True
                current_rule.code_note = rest.replace("⚙︎", "").strip().strip("()").strip()
            elif rest.strip():
                buffer.append(rest.strip())
            continue
        if current_rule is not None and "⚙︎" in line:
            current_rule.coded = True
            line = line.replace(" ⚙︎", "").replace("⚙︎", "")
        k = KIND_RE.match(line)
        if k and current_rule is not None:
            flush()
            kind = k.group(1).lower()
            buffer.append(k.group(2))
            continue
        if current_rule is not None and kind != "text" and line and not line.startswith("  "):
            flush()
            kind = "text"
        buffer.append(line)
    flush()
    return "\n".join(header).strip(), sections


def _dedent_item(body: str, kind: str) -> str:
    if kind == "text":
        return body
    return "\n".join(line[2:] if line.startswith("  ") else line for line in body.splitlines())


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def all_rule_ids(sections: list[Section]) -> list[str]:
    return [r.id for s in sections for r in s.rules]
