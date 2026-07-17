#!/usr/bin/env python3
"""Render dark_mode.svg — the self-hosted ASCII profile card.

Replaces the third-party gh-ascii service. Fetches the current GitHub
avatar, converts it to ASCII art, and lays it out neofetch-style next to
live profile data, all in the repo's industrial palette.

Requires Pillow (the only non-stdlib dependency in this repo's pipeline).
"""

import io
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

from render_plates import USER, api_get, fetch_stats

OFFWHITE = "#F4F1EA"
BLACK = "#0A0A0A"
ORANGE = "#FF6B00"
GREY = "#8a857a"
MONO = "Consolas, 'Courier New', monospace"

ART_COLS = 96
CHAR_W = 6.0
CHAR_H = 11.0
# Light-on-dark: brighter pixel -> denser glyph.
RAMP = " .`':,;-~=+*coxwXWM@"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch_avatar(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read()))


def ascii_art(img):
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    rows = int(ART_COLS * img.height / img.width * (CHAR_W / CHAR_H))
    img = img.resize((ART_COLS, rows))
    px = img.load()
    lines = []
    for y in range(rows):
        line = "".join(
            RAMP[min(px[x, y] * len(RAMP) // 256, len(RAMP) - 1)]
            for x in range(ART_COLS)
        )
        lines.append(line.rstrip())
    return lines


def uptime_text(created_at):
    start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = now.year - start.year
    months = now.month - start.month
    days = now.day - start.day
    if days < 0:
        months -= 1
        days += 30
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"


def leader(label, value, width=58):
    dots = "." * max(width - len(label) - len(value), 2)
    return label, dots, value


def render(user, stats, art):
    year = date.today().year
    langs = ", ".join(l for l, _ in stats["langs"][:5]) or "—"
    info = [
        ("head", f"{USER}@github"),
        ("kv", leader("Uptime", uptime_text(user["created_at"]))),
        ("kv", leader("Location", user.get("location") or "—")),
        ("kv", leader("Languages", langs)),
        ("gap", None),
        ("head", "Contact"),
        ("kv", leader("Twitter", "@" + (user.get("twitter_username") or "—"))),
        ("kv", leader("GitHub", f"github.com/{USER}")),
        ("gap", None),
        ("head", "GitHub Stats"),
        ("kv", leader("Repos", f'{stats["repos"]}', 28)),
        ("kv", leader("Stars", f'{stats["stars"]}', 28)),
        ("kv", leader(f"Commits {year}", f'{stats["commits"] or "—"}', 28)),
        ("kv", leader("Followers", f'{stats["followers"]}', 28)),
    ]

    art_x, art_y = 30, 46
    height = max(int(art_y + len(art) * CHAR_H + 30), 460)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" '
        f'aria-label="ASCII profile card for {escape(USER)}: avatar art plus live GitHub stats, self-generated daily">',
        f'<style> text {{ font-family: {MONO}; white-space: pre; }} </style>',
        f'<rect width="1200" height="{height}" fill="{BLACK}"/>',
        f'<rect x="0" y="0" width="6" height="{height}" fill="{ORANGE}"/>',
        f'<text x="{art_x}" y="28" font-size="11" font-weight="700" letter-spacing="4" fill="{ORANGE}" font-family="Helvetica, Arial, sans-serif">&#8220;SELF-PORTRAIT, SELF-HOSTED&#8221;</text>',
        f'<text x="1170" y="28" text-anchor="end" font-size="10" letter-spacing="2" fill="{OFFWHITE}" opacity="0.4" font-family="Helvetica, Arial, sans-serif">NO CARD SERVICE. DREW IT MYSELF.</text>',
    ]

    for i, line in enumerate(art):
        if not line:
            continue
        y = art_y + (i + 1) * CHAR_H
        parts.append(
            f'<text x="{art_x}" y="{y:.0f}" font-size="10.5" xml:space="preserve" fill="{OFFWHITE}">{escape(line)}</text>'
        )

    ix, iy = 660, 120
    for kind, payload in info:
        if kind == "gap":
            iy += 14
            continue
        if kind == "head":
            parts.append(
                f'<text x="{ix}" y="{iy}" font-size="14" font-weight="700" fill="{ORANGE}">{escape(payload)}</text>'
            )
            parts.append(
                f'<rect x="{ix}" y="{iy + 6}" width="480" height="1" fill="{OFFWHITE}" opacity="0.2"/>'
            )
            iy += 26
            continue
        label, dots, value = payload
        parts.append(
            f'<text x="{ix}" y="{iy}" font-size="12.5" xml:space="preserve">'
            f'<tspan fill="{ORANGE}">. </tspan>'
            f'<tspan fill="{OFFWHITE}">{escape(label)}: </tspan>'
            f'<tspan fill="{GREY}">{escape(dots)} </tspan>'
            f'<tspan fill="{OFFWHITE}" font-weight="700">{escape(value)}</tspan></text>'
        )
        iy += 20

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    user = api_get(f"/users/{USER}")
    stats = fetch_stats()
    art = ascii_art(fetch_avatar(user["avatar_url"]))
    svg = render(user, stats, art)
    out = os.path.join(ROOT, "dark_mode.svg")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote dark_mode.svg ({len(art)} art rows)")


if __name__ == "__main__":
    sys.exit(main())
