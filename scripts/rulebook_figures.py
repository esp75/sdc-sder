"""Static SVG figures for the Rulebook PDF (the web version draws interactive ones)."""

from __future__ import annotations

# Space Debris Credits brand tokens (brand dossier 10_color/tokens.json).
INK = "#0A1628"
SURFACE = "#1E293B"
BODY = "#4A5568"
PAPER = "#F7FAFC"
LINE = "#E2E8F0"
LINE_STRONG = "#CBD5E0"
VERIFIED = "#00805C"  # green means verified, and nothing else; deep tone for small text on light
ALERT = "#D64545"  # rejection and failure only
MUTED = BODY

_DEFS = f"""<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>"""


def _box(
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    *,
    fill: str = "#fff",
    stroke: str = LINE,
    color: str = INK,
    bold: bool = False,
    size: int = 12,
) -> str:
    weight = 700 if bold else 500
    lines = label.split("\n")
    y0 = y + h / 2 - (len(lines) - 1) * size * 0.6
    text = "".join(
        f'<text x="{x + w / 2}" y="{y0 + i * size * 1.2}" text-anchor="middle" dominant-baseline="middle" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{line}</text>'
        for i, line in enumerate(lines)
    )
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>{text}'


def _arrow(x1: float, y1: float, x2: float, y2: float, *, label: str = "", dash: bool = False) -> str:
    d = ' stroke-dasharray="4 3"' if dash else ""
    out = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="1.3" marker-end="url(#arr)"{d}/>'
    if label:
        out += (
            f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 5}" text-anchor="middle" font-size="9.5" '
            f'fill="{MUTED}">{label}</text>'
        )
    return out


def _svg(w: int, h: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}" '
        f"font-family=\"'Space Grotesk', 'DM Sans', system-ui, sans-serif\"><title>{title}</title>{_DEFS}{body}</svg>"
    )


def journey() -> str:
    steps = [
        ("B", "Rate the\nmission"),
        ("C", "Act and\nclaim"),
        ("D", "Verify"),
        ("E", "Record"),
        ("F", "Use or\nretire"),
        ("H", "Fund\naccess"),
    ]
    w, gap, bw = 640, 14, 92
    body = ""
    for i, (part, label) in enumerate(steps):
        x = 6 + i * (bw + gap)
        body += _box(
            x,
            26,
            bw,
            58,
            label,
            fill=PAPER if part != "H" else INK,
            stroke=LINE_STRONG if part != "H" else "none",
            color=INK if part != "H" else "#fff",
            bold=True,
            size=11.5,
        )
        body += (
            f'<text x="{x + bw / 2}" y="16" text-anchor="middle" font-size="10" font-weight="700" '
            f'fill="{INK}" letter-spacing="1.2">PART {part}</text>'
        )
        if i < len(steps) - 1:
            body += _arrow(x + bw + 1, 55, x + bw + gap - 1, 55)
    body += (
        f'<text x="{w / 2}" y="108" text-anchor="middle" font-size="10.5" fill="{MUTED}">Part A sets the terms '
        f"and the law, Part G how the rules change, Part I how the scheme is adopted, Part J how it is judged.</text>"
    )
    return _svg(w, 118, body, "How one claim moves through the Rulebook")


def lifecycle() -> str:
    main = ["claimed", "under_review", "verified", "issued", "retired"]
    bw, gap, y = 104, 22, 30
    body = ""
    xs = []
    for i, state in enumerate(main):
        x = 6 + i * (bw + gap)
        xs.append(x)
        body += _box(
            x,
            y,
            bw,
            40,
            state,
            fill=PAPER if state != "retired" else INK,
            stroke=VERIFIED if state == "verified" else (LINE_STRONG if state != "retired" else "none"),
            color=VERIFIED if state == "verified" else (INK if state != "retired" else "#fff"),
            bold=True,
            size=11,
        )
        if i:
            body += _arrow(xs[i - 1] + bw + 1, y + 20, x - 1, y + 20)
    body += _box(
        xs[0] + 40,
        118,
        150,
        36,
        "rejected (final)",
        fill="#fff",
        stroke=ALERT,
        color=ALERT,
        bold=True,
        size=11,
    )
    body += _box(
        xs[3] - 40,
        118,
        170,
        36,
        "revoked (final)",
        fill="#fff",
        stroke=ALERT,
        color=ALERT,
        bold=True,
        size=11,
    )
    body += _arrow(xs[0] + bw / 2, y + 41, xs[0] + 90, 117, dash=True)
    body += _arrow(xs[1] + bw / 2, y + 41, xs[0] + 150, 117, dash=True)
    for i in (2, 3, 4):
        body += _arrow(xs[i] + bw / 2, y + 41, xs[3] + 45, 117, dash=True)
    body += (
        f'<text x="320" y="182" text-anchor="middle" font-size="10.5" fill="{MUTED}">Solid: normal path. '
        f"Dashed: rejection or revocation, each with a published reason (C10). A retired unit can still be revoked.</text>"
    )
    return _svg(640, 192, body, "Claim lifecycle (rule C7)")


def esaf() -> str:
    sources = [
        "Allocation or\nauction proceeds",
        "Verification and\nregistry fees",
        "Penalties and\nforfeited bonds",
        "Transfer fees\n(only if allowed)",
        "Voluntary and\nco-financing",
    ]
    programmes = [
        "Capacity\nbuilding",
        "Compliance\ncost support",
        "Technology and\nopen tools",
        "Participation",
    ]
    body = ""
    for i, s in enumerate(sources):
        y = 8 + i * 50
        body += _box(6, y, 150, 42, s, fill="#fff" if i != 3 else PAPER, size=10.5)
        body += _arrow(157, y + 21, 254, 133)
    body += _box(
        256,
        98,
        128,
        70,
        "ESAF\nboard: equal seats",
        fill=INK,
        stroke="none",
        color="#fff",
        bold=True,
        size=12,
    )
    for i, p in enumerate(programmes):
        y = 22 + i * 58
        body += _arrow(385, 133, 482, y + 22)
        body += _box(484, y, 150, 44, p, fill=PAPER, stroke=LINE_STRONG, bold=True, size=10.5)
    body += (
        f'<text x="320" y="268" text-anchor="middle" font-size="10.5" fill="{MUTED}">At least half of each '
        f"year's disbursements reach emerging space actors (H6). Accounts and every grant are published (H7).</text>"
    )
    return _svg(640, 278, body, "Equitable Space Access Fund: sources and programmes (Part H)")


def phases() -> str:
    items = [
        ("0", "Pilot", "verification cost,\ndispute rate known"),
        ("1", "Insurers and\nprocurement", "behaviour\nchanges"),
        ("2", "National\nlicensing", "no double counting;\nrisk growth slows"),
        ("3", "Harmonisation", "five-yearly\nreview"),
    ]
    body = ""
    bw = 148
    for i, (n, name, gate) in enumerate(items):
        x = 6 + i * (bw + 10)
        pts = (
            f"{x},10 {x + bw - 14},10 {x + bw},48 {x + bw - 14},86 {x},86 {x + 14},48"
            if i
            else f"{x},10 {x + bw - 14},10 {x + bw},48 {x + bw - 14},86 {x},86"
        )
        fill = [PAPER, LINE, SURFACE, INK][i]
        color = INK if i < 2 else "#fff"
        body += f'<polygon points="{pts}" fill="{fill}"/>'
        body += (
            f'<text x="{x + bw / 2 + 4}" y="30" text-anchor="middle" font-size="10" font-weight="700" '
            f'fill="{color}" letter-spacing="1.2">PHASE {n}</text>'
        )
        for j, line in enumerate(name.split("\n")):
            body += (
                f'<text x="{x + bw / 2 + 4}" y="{50 + j * 14}" text-anchor="middle" font-size="12" '
                f'font-weight="700" fill="{color}">{line}</text>'
            )
        body += f'<text x="{x + bw / 2}" y="108" text-anchor="middle" font-size="9.5" font-weight="700" fill="{INK}" letter-spacing="1.2">GATE</text>'
        for j, line in enumerate(gate.split("\n")):
            body += f'<text x="{x + bw / 2}" y="{123 + j * 12}" text-anchor="middle" font-size="10" fill="{MUTED}">{line}</text>'
    return _svg(640, 150, body, "Phases and evidence gates (rule I1)")


FIGURES = {
    "C7": (lifecycle, "Figure 2. The claim lifecycle in rule C7, as enforced by the reference registry."),
    "H2": (esaf, "Figure 3. Where the Equitable Space Access Fund's money comes from and what it pays for."),
    "I1": (phases, "Figure 4. Each phase opens only when the previous phase's evidence gates are met."),
}
