"""Build the branded PDF of the Rulebook from its Markdown source.

    uv run --group research python scripts/build_rulebook_pdf.py [--chromium PATH] [--html-only]

The Markdown in ``spec/`` is the only source. This script renders it to HTML
with the SDC Institute print style, prints it with Chromium (via Playwright),
reads back the page on which each Part starts, and prints again so the table
of contents carries page numbers.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rulebook_doc import ROOT, Section, parse, render
from rulebook_figures import FIGURES, journey

OUT_PDF = ROOT / "spec" / "rulebook-v0.2-consultation-draft.pdf"
OUT_HTML = ROOT / "build" / "rulebook.html"
LOCKUP = (ROOT / "brand" / "primary_v1.svg").read_text()
MONOGRAM = (ROOT / "brand" / "monogram.svg").read_text()
WEB = "https://maximekadri.org/research/space-debris-credits/rulebook"
TITLE = "SDC and SDER Rulebook"
VERSION = "Consultation draft v0.2 · 12 October 2026"

CSS = """
@font-face { font-family: "Space Grotesk"; src: local("Space Grotesk"), local("SpaceGrotesk-Variable"); font-weight: 300 700; }
@page { size: A4; margin: 20mm 19mm 22mm 19mm;
  @top-left { content: "SDC Institute  ·  Rulebook, consultation draft v0.2"; font: 500 7.5pt var(--font); color: #4A5568; }
  @top-right { content: "NOT IN FORCE"; font: 600 7pt var(--font); letter-spacing: .14em; color: #4A5568; }
  @bottom-left { content: "CC BY-SA 4.0  ·  github.com/spacedebriscredit/sdc-sder"; font: 400 7.5pt var(--font); color: #4A5568; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 600 8pt var(--font); color: #0A1628; }
}
@page :first { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-left { content: none } @bottom-right { content: none } }
/* Space Debris Credits brand tokens (brand dossier 10_color/tokens.json). Green means verified, and nothing else. */
:root { --bg:#0A1628; --surface:#1E293B; --ink:#0A1628; --body:#4A5568; --paper:#F7FAFC; --line:#E2E8F0; --line-strong:#CBD5E0;
  --verified:#00805C; --alert:#D64545; --font: "Space Grotesk", "DM Sans", system-ui, sans-serif; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 400 9.4pt/1.55 var(--font); color: var(--ink); hyphens: auto; }
a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--line-strong); text-underline-offset: 2px; }
.math { font-family: "Times New Roman", Times, serif; font-size: 1.08em; white-space: nowrap; }
.math i { font-style: italic; }
code { font: 8.4pt "SF Mono", Menlo, monospace; background: var(--paper); padding: 0 3px; border-radius: 3px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 8.2pt; line-height: 1.42; break-inside: auto; }
thead th { background: var(--bg); color: #fff; text-align: left; font-weight: 600; padding: 5px 7px; }
td { padding: 5px 7px; border-bottom: .6pt solid var(--line); vertical-align: top; color: var(--ink); }
tr { break-inside: avoid; }
ul, ol { padding-left: 15px; margin: 4px 0; }
li { margin: 2px 0; }

/* cover: after 09_marketing/Document Cover */
.cover { height: 297mm; padding: 34mm 24mm 22mm; background: #fff; position: relative; overflow: hidden; break-after: page;
  display: flex; flex-direction: column; align-items: center; text-align: center; }
.cover .bar { position: absolute; top: 0; left: 0; right: 0; height: 8px; background: var(--bg); }
.cover .lockup svg { width: 118mm; height: auto; display: block; }
.cover .lockup svg > rect { fill: none; }
.cover .eyebrow { margin-top: 42mm; color: var(--body); font-weight: 600; letter-spacing: .22em; font-size: 9pt; text-transform: uppercase; }
.cover h1 { font-weight: 700; font-size: 40pt; line-height: 1.08; letter-spacing: -.02em; margin: 7mm 0 0; }
.cover .rule { width: 64px; height: 3px; background: var(--bg); margin: 10mm auto; }
.cover .sub { font-size: 12.5pt; line-height: 1.5; color: var(--body); max-width: 120mm; margin: 0; }
.cover .pending { margin-top: 9mm; display: inline-block; border: 1px dashed var(--line-strong); border-radius: 4px; color: var(--body);
  padding: 2.2mm 4mm; font-size: 9pt; }
.cover .meta { margin-top: auto; width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 6mm 10mm; padding-top: 8mm;
  border-top: 1px solid var(--line); font-size: 8.3pt; color: var(--body); text-align: left; }
.cover .meta b { display: block; color: var(--ink); font-size: 7.3pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 1px; }
.cover .meta a { color: var(--ink); }

/* front matter */
.front { break-after: page; }
.front h2 { font-size: 22pt; font-weight: 600; letter-spacing: -.02em; margin: 0 0 4mm; padding-bottom: 3mm; border-bottom: 2px solid var(--ink); }
.status { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 4mm 5mm; margin-bottom: 6mm; font-size: 8.6pt; color: var(--body); }
.status p { margin: 0; } .status strong { color: var(--ink); }
.toc { list-style: none; padding: 0; margin: 4mm 0 0; }
.toc li { display: flex; align-items: baseline; gap: 6px; padding: 2.1mm 0; border-bottom: .6pt solid var(--line); font-size: 10pt; }
.toc .k { width: 9mm; color: var(--ink); font-weight: 700; }
.toc .t { flex: 1; } .toc .t a { text-decoration: none; font-weight: 500; }
.toc .n { font-weight: 600; font-variant-numeric: tabular-nums; }
.toc .sub { color: var(--body); font-size: 8pt; margin-left: 0; font-weight: 400; }
figure { margin: 6mm 0; break-inside: avoid; }
figure svg { width: 100%; height: auto; }
figcaption { font-size: 7.8pt; color: var(--body); margin-top: 2mm; }

/* parts and rules: section header = eyebrow + h2 over a 2px ink rule */
.section { break-before: page; }
.part-head { margin: 0 0 7mm; padding-bottom: 3.5mm; border-bottom: 2px solid var(--ink); display: flex; align-items: baseline; gap: 5mm; }
.part-head .k { font-size: 8pt; font-weight: 600; letter-spacing: .14em; color: var(--body); white-space: nowrap; text-transform: uppercase; }
.part-head h2 { margin: 0; font-size: 21pt; font-weight: 600; letter-spacing: -.02em; line-height: 1.12; }
.intro { color: var(--body); }
.rule { margin: 0 0 5.5mm; }
.rule-head { display: flex; align-items: baseline; gap: 7px; margin-bottom: 1.6mm; break-after: avoid; }
.rule-head .id { background: var(--bg); color: #fff; font-weight: 600; font-size: 7.8pt; padding: 1px 6px; border-radius: 4px; letter-spacing: .04em; }
.rule-head h3 { margin: 0; font-size: 11pt; font-weight: 600; letter-spacing: -.01em; }
.tag { font-size: 6.8pt; font-weight: 600; letter-spacing: .06em; color: var(--body); border: .7pt solid var(--line-strong);
  border-radius: 4px; padding: 0 4px; }
.seg { display: grid; grid-template-columns: 13mm 1fr; gap: 3mm; padding: 1.6mm 0; }
.seg > .lbl { font-size: 6.8pt; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--body); padding-top: 1.3mm; }
.seg > div > p:first-child { margin-top: 0; } .seg > div > p:last-child { margin-bottom: 0; }
.seg.rule-text { background: var(--paper); border: 1px solid var(--line); border-left: 2.5pt solid var(--ink); border-radius: 4px; padding: 2.2mm 3mm; }
.seg.rule-text > .lbl { color: var(--ink); }
.seg.why > div { color: var(--body); }
.seg.open { border: 1px dashed var(--line-strong); border-radius: 4px; padding: 2mm 3mm; margin: 1mm 0; }
.seg.text { display: block; }
.plain > :first-child { margin-top: 0; }
.back { break-before: page; }
.back .box { background: var(--bg); color: #fff; padding: 8mm; border-radius: 8px; margin-top: 6mm; }
.back .box a { color: #fff; text-decoration-color: rgba(255,255,255,.4); }
"""

LABELS = {"rule": "Rule", "why": "Why", "open": "Open"}


def rule_html(rule) -> str:
    tags = ""
    if rule.coded:
        note = f" · {html.escape(re.sub('`', '', rule.code_note))}" if rule.code_note else ""
        tags += f'<span class="tag">⚙︎ in reference code{note}</span>'
    if rule.option:
        tags += '<span class="tag">Option</span>'
    out = [
        f'<div class="rule" id="{rule.id.lower()}"><div class="rule-head"><span class="id">{rule.id}</span>'
        f"<h3>{html.escape(rule.title)}</h3>{tags}</div>"
    ]
    for seg in rule.segments:
        body = render(seg.markdown)
        if seg.kind == "text":
            out.append(f'<div class="seg text plain">{body}</div>')
        else:
            cls = "rule-text" if seg.kind == "rule" else seg.kind
            out.append(
                f'<div class="seg {cls}"><span class="lbl">{LABELS[seg.kind]}</span><div>{body}</div></div>'
            )
    if rule.id in FIGURES:
        fn, caption = FIGURES[rule.id]
        out.append(f"<figure>{fn()}<figcaption>{caption}</figcaption></figure>")
    out.append("</div>")
    return "".join(out)


def section_html(sec: Section) -> str:
    lettered = len(sec.key) == 1
    head = (
        f'<div class="part-head"><div class="k">PART {sec.key}</div><h2>{html.escape(sec.title)}</h2></div>'
        if lettered
        else f'<div class="part-head"><div class="k">Reference</div><h2>{html.escape(sec.title)}</h2></div>'
    )
    intro = f'<div class="intro plain">{render(sec.intro)}</div>' if sec.intro else ""
    return f'<section class="section" id="sec-{sec.key.lower()}">{head}{intro}{"".join(rule_html(r) for r in sec.rules)}</section>'


def toc_html(sections: list[Section], pages: dict[str, int]) -> str:
    rows = []
    for s in sections:
        if s.key == "how-to-read-this-draft":
            continue
        k = s.key if len(s.key) == 1 else ""
        ids = ", ".join(r.id for r in s.rules)
        n = pages.get(s.key, 0)
        rows.append(
            f'<li><span class="k">{k}</span><span class="t"><a href="#sec-{s.key.lower()}">{html.escape(s.title)}</a>'
            f'{f"<div class=sub>{ids}</div>" if ids else ""}</span><span class="n">{n or "00"}</span></li>'
        )
    return f'<ul class="toc">{"".join(rows)}</ul>'


def document(pages: dict[str, int]) -> str:
    header, sections = parse()
    how = next(s for s in sections if s.key == "how-to-read-this-draft")
    body_sections = [s for s in sections if s.key != "how-to-read-this-draft"]
    cover = f"""<div class="cover"><div class="bar"></div>
<div class="lockup">{LOCKUP}</div>
<div class="eyebrow">Consultation draft</div>
<h1>SDC and SDER<br>Rulebook</h1>
<div class="rule"></div>
<p class="sub">Rules for describing a mission's debris exposure, recording verified reductions in long-lived debris risk,
and funding fair access to space.</p>
<div class="pending">Not in force. No rating or credit has been issued under these rules.</div>
<div class="meta">
  <div><b>Version</b>{VERSION}<br>SDC Institute (in formation)</div>
  <div><b>Licence</b>© 2026 Maxime Kadri · CC BY-SA 4.0<br>Use does not imply endorsement or certification</div>
  <div><b>Interactive version</b><a href="{WEB}">maximekadri.org/research/space-debris-credits/rulebook</a></div>
  <div><b>Source and code</b><a href="https://github.com/spacedebriscredit/sdc-sder">github.com/spacedebriscredit/sdc-sder</a></div>
</div></div>"""
    status = f'<div class="status plain">{render(header.replace(chr(10), "  " + chr(10)))}</div>'
    front = f"""<div class="front"><h2>Contents</h2>{status}{toc_html(body_sections, pages)}</div>
<section class="section" id="sec-how"><div class="part-head"><div class="k">Before you start</div><h2>{how.title}</h2></div>
<div class="plain">{render(how.intro)}</div>
<figure>{journey()}<figcaption>Figure 1. The Parts follow the path of one claim, from rating a mission to funding access.</figcaption></figure></section>"""
    back = f"""<section class="back"><div class="part-head"><div class="k">Respond</div><h2>How to take part in the consultation</h2></div>
<p>Comments on any rule are welcome, especially on the questions above and on every point marked <b>Open</b>.
Use the consultation template in the repository, or open a review issue. Every response is read, and the reasons for
accepting or rejecting a substantive change are published (rule G1).</p>
<div class="box"><p><b>Consultation template:</b> <a href="https://github.com/spacedebriscredit/sdc-sder/blob/main/spec/consultation-template.md">github.com/spacedebriscredit/sdc-sder/blob/main/spec/consultation-template.md</a></p>
<p><b>Interactive version, with explanations of every term:</b> <a href="{WEB}">{WEB.removeprefix("https://")}</a></p>
<p><b>Cite as:</b> Kadri, M. (2026). <i>SDC and SDER Rulebook: consultation draft v0.2.</i> SDC Institute (in formation). CC BY-SA 4.0.</p>
<p style="margin-bottom:0"><b>Generated</b> {date.today().isoformat()} from <code style="background:none;color:#fff">spec/rulebook-v0.2-consultation-draft.md</code>.</p></div></section>"""
    sections_html = "".join(section_html(s) for s in body_sections)
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{TITLE}: {VERSION}</title>'
        f"<style>{CSS}</style></head><body>{cover}{front}{sections_html}{back}</body></html>"
    )


def find_chromium(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    found = sorted(cache.glob("chromium-*/chrome-mac*/*.app/Contents/MacOS/*"), reverse=True)
    return str(found[0]) if found else None


def print_pdf(page_html: str, out: Path, chromium: str | None) -> None:
    from playwright.sync_api import sync_playwright

    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(page_html)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium) if chromium else p.chromium.launch()
        page = browser.new_page()
        page.goto(OUT_HTML.as_uri())
        page.pdf(path=str(out), prefer_css_page_size=True, print_background=True, tagged=True, outline=True)
        browser.close()


def part_pages(pdf: Path) -> dict[str, int]:
    from pypdf import PdfReader

    _, sections = parse()
    reader = PdfReader(str(pdf))
    texts = [re.sub(r"\s", "", page.extract_text() or "") for page in reader.pages]
    pages: dict[str, int] = {}
    for s in sections:
        needle = re.sub(r"\s", "", (f"PART{s.key}" + s.title) if len(s.key) == 1 else s.title)
        for i, t in enumerate(texts[2:], start=3):
            if needle in t:
                pages[s.key] = i
                break
    return pages


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--chromium", help="path to a Chromium executable (default: newest in the Playwright cache)"
    )
    ap.add_argument("--html-only", action="store_true", help="write build/rulebook.html and stop")
    args = ap.parse_args()
    if args.html_only:
        OUT_HTML.parent.mkdir(exist_ok=True)
        OUT_HTML.write_text(document({}))
        print(f"wrote {OUT_HTML}")
        return
    chromium = find_chromium(args.chromium)
    print_pdf(document({}), OUT_PDF, chromium)
    pages = part_pages(OUT_PDF)
    print_pdf(document(pages), OUT_PDF, chromium)
    if part_pages(OUT_PDF) != pages:
        print("warning: page numbers moved between passes", file=sys.stderr)
    from pypdf import PdfReader

    print(f"wrote {OUT_PDF} ({len(PdfReader(str(OUT_PDF)).pages)} pages); parts start on {pages}")


if __name__ == "__main__":
    main()
