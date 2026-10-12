"""Export the Rulebook for the interactive version on maximekadri.org.

    uv run --group research python scripts/export_rulebook.py ../maximekadri.org

Writes into the site repository:
* ``src/content/rulebook.json``: parts, rules and segments as HTML, with every
  glossary term from ``spec/rulebook-terms.yaml`` linked on its first use in
  each rule, plus the term cards and the claim lifecycle;
* ``src/lab/rulebook/parity.json``: the lifecycle and a hash-chained registry
  log produced by the Python reference code, which the site's tests replay;
* ``public/papers/sdc-rulebook-v0.2.pdf`` and ``.md``: downloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rulebook_doc import ROOT, SOURCE, Rule, parse, render

from sdc.models import TRANSITIONS, ClaimState
from sdc.registry import GENESIS, Registry

TERMS = ROOT / "spec" / "rulebook-terms.yaml"
PDF = ROOT / "spec" / "rulebook-v0.2-consultation-draft.pdf"

# Which explainer the web page draws after which rule.
VISUALS = {
    "A2": "risk",
    "A5": "law",
    "B5": "rating",
    "C1": "units",
    "C3": "baseline",
    "C7": "lifecycle",
    "D2": "verification",
    "E2": "registry",
    "F1": "instruments",
    "H2": "esaf",
    "I1": "phases",
}

_SKIP_TAGS = {"a", "code", "button", "th", "h1", "h2", "h3", "strong", "span"}

# Formulas rendered as math spans that have their own term card.
MATH_TERMS = {'<span class="math">ΔR<sub>0</sub></span>': "delta-r0"}


def load_terms() -> list[dict[str, Any]]:
    data = yaml.safe_load(TERMS.read_text())
    terms: list[dict[str, Any]] = data["terms"]
    ids = [t["id"] for t in terms]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate term id in rulebook-terms.yaml")
    return terms


def term_pattern(terms: list[dict[str, Any]]) -> tuple[re.Pattern[str], dict[str, str]]:
    lookup: dict[str, str] = {}
    for t in terms:
        for m in t["match"]:
            lookup.setdefault(m, t["id"])
    phrases = sorted(lookup, key=len, reverse=True)
    alternation = "|".join(re.escape(p) for p in phrases)
    return re.compile(rf"(?<![\w-])({alternation})(?![\w-])"), lookup


def link_terms(fragment: str, pattern: re.Pattern[str], lookup: dict[str, str], seen: set[str]) -> str:
    """Wrap the first use of each term (per rule) in a button, outside links, code and headings."""
    for span, tid in MATH_TERMS.items():
        if tid not in seen and span in fragment:
            seen.add(tid)
            fragment = fragment.replace(
                span, f'<button type="button" class="term" data-term="{tid}">{span}</button>', 1
            )
    out: list[str] = []
    depth: dict[str, int] = {}
    for token in re.split(r"(<[^>]+>)", fragment):
        if token.startswith("<"):
            m = re.match(r"</?([a-zA-Z0-9]+)", token)
            if m:
                tag = m.group(1).lower()
                if tag in _SKIP_TAGS:
                    depth[tag] = depth.get(tag, 0) + (-1 if token.startswith("</") else 1)
            out.append(token)
            continue
        if any(v > 0 for v in depth.values()):
            out.append(token)
            continue

        def wrap(m: re.Match[str]) -> str:
            tid = lookup[m.group(1)]
            if tid in seen:
                return m.group(0)
            seen.add(tid)
            return f'<button type="button" class="term" data-term="{tid}">{m.group(1)}</button>'

        out.append(pattern.sub(wrap, token))
    return "".join(out)


def rule_payload(rule: Rule, pattern: re.Pattern[str], lookup: dict[str, str]) -> dict[str, Any]:
    seen: set[str] = set()
    segments = [
        {"kind": seg.kind, "html": link_terms(render(seg.markdown), pattern, lookup, seen)}
        for seg in rule.segments
    ]
    return {
        "id": rule.id,
        "title": rule.title,
        "coded": rule.coded,
        "codeNote": re.sub("`", "", rule.code_note),
        "option": rule.option,
        "segments": segments,
        "visual": VISUALS.get(rule.id),
    }


def registry_demo() -> list[dict[str, Any]]:
    """A full lifecycle for a real derelict (WP-04 rank 1), logged by the Python registry."""
    reg = Registry()
    t = "2026-10-12T09:00:00+00:00"
    reg.record(
        "submit",
        "servicer-a",
        {
            "claim_id": "DEMO-1",
            "object_id": "23343",
            "outcome_type": "active_removal",
            "event_date": "2027-06-01",
            "claimant": "servicer-a",
            "unit_definition": "one unit per 1.0 of conservative ΔR",
            "baseline": "object remains in its shell",
            "evidence": ["tracking-before", "rendezvous-log", "tracking-after", "consent-letter"],
        },
        t,
    )
    reg.record("assign_verifier", "admin", {"claim_id": "DEMO-1", "verifier": "verifier-b"}, t)
    reg.record("verify", "verifier-b", {"claim_id": "DEMO-1"}, t)
    reg.record("issue", "admin", {"claim_id": "DEMO-1", "units": 10}, t)
    reg.record("retire", "operator-c", {"claim_id": "DEMO-1", "reason": "licence obligation"}, t)
    return reg.entries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("site", type=Path, help="path to the maximekadri.org repository")
    args = ap.parse_args()

    terms = load_terms()
    pattern, lookup = term_pattern(terms)
    header, sections = parse()
    source = SOURCE.read_bytes()

    parts = []
    for s in sections:
        seen: set[str] = set()
        parts.append(
            {
                "key": s.key,
                "title": s.title,
                "lettered": len(s.key) == 1,
                "introHtml": link_terms(render(s.intro), pattern, lookup, seen) if s.intro else "",
                "rules": [rule_payload(r, pattern, lookup) for r in s.rules],
            }
        )
    rule_ids = {r["id"] for p in parts for r in p["rules"]}
    for t in terms:
        if t["rule"] not in rule_ids:
            raise SystemExit(f"term {t['id']} points to unknown rule {t['rule']}")

    content = {
        "version": "v0.2",
        "date": "2026-10-12",
        "sourceSha256": hashlib.sha256(source).hexdigest(),
        "pdfPages": len(PdfReader(str(PDF)).pages),
        "headerHtml": render(header.replace("\n", "  \n")),
        "parts": parts,
        "terms": {t["id"]: {k: t.get(k) for k in ("label", "short", "why", "rule", "visual")} for t in terms},
        "lifecycle": {s.value: sorted(x.value for x in TRANSITIONS[s]) for s in ClaimState},
    }
    parity = {"lifecycle": content["lifecycle"], "genesis": GENESIS, "registry": registry_demo()}

    out_content = args.site / "src" / "content" / "rulebook.json"
    out_parity = args.site / "src" / "lab" / "rulebook" / "parity.json"
    out_public = args.site / "public" / "papers"
    out_parity.parent.mkdir(parents=True, exist_ok=True)
    out_public.mkdir(parents=True, exist_ok=True)
    out_content.write_text(json.dumps(content, ensure_ascii=False, separators=(",", ":")))
    out_parity.write_text(json.dumps(parity, ensure_ascii=False, indent=1))
    shutil.copyfile(PDF, out_public / "sdc-rulebook-v0.2.pdf")
    shutil.copyfile(SOURCE, out_public / "sdc-rulebook-v0.2.md")
    linked = sum(
        seg["html"].count('class="term"') for p in parts for r in p["rules"] for seg in r["segments"]
    )
    print(
        f"wrote {out_content} ({out_content.stat().st_size // 1024} KB, {len(rule_ids)} rules, {linked} term links)"
    )
    print(f"wrote {out_parity}, {out_public}/sdc-rulebook-v0.2.pdf and .md")


if __name__ == "__main__":
    main()
