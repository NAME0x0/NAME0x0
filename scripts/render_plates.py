#!/usr/bin/env python3
"""Render assets/stats.svg and assets/stoic.svg for the profile README.

Stdlib only. Pulls live data from the GitHub API (authenticated when
GITHUB_TOKEN is set, anonymous otherwise) and bakes it into self-backgrounded
SVG plates matching the repo's industrial design system.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "NAME0x0")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
EXCLUDED_REPOS = {"BidGenius"}

OFFWHITE = "#F4F1EA"
BLACK = "#0A0A0A"
ORANGE = "#FF6B00"
FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def api_get(path):
    req = urllib.request.Request(API + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", USER)
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def truncate(text, limit):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def fetch_stats():
    user = api_get(f"/users/{USER}")
    repos = []
    page = 1
    while True:
        batch = api_get(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    own = [
        r
        for r in repos
        if not r["fork"] and r["name"] not in EXCLUDED_REPOS
    ]
    stars = sum(r["stargazers_count"] for r in own)

    lang_weight = {}
    for r in own:
        if r.get("language"):
            lang_weight[r["language"]] = lang_weight.get(r["language"], 0) + max(r.get("size", 0), 1)
    top_langs = sorted(lang_weight.items(), key=lambda kv: kv[1], reverse=True)[:5]

    commits_this_year = None
    year = date.today().year
    try:
        found = api_get(
            f"/search/commits?q=author:{USER}+author-date:>{year - 1}-12-31&per_page=1"
        )
        commits_this_year = found.get("total_count")
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError):
        commits_this_year = None

    last_ship = None
    try:
        events = api_get(f"/users/{USER}/events/public?per_page=100")
        for ev in events:
            if ev.get("type") != "PushEvent":
                continue
            full = ev["repo"]["name"]
            repo_name = full.split("/")[-1]
            if repo_name in EXCLUDED_REPOS:
                continue
            # payload.commits is often empty on the public events feed;
            # fetch the repo's latest commit directly instead.
            latest = api_get(f"/repos/{full}/commits?per_page=1")
            if not latest:
                continue
            msg = latest[0]["commit"]["message"].splitlines()[0]
            day = latest[0]["commit"]["author"]["date"][:10]
            last_ship = (repo_name, msg, day)
            break
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, IndexError):
        last_ship = None

    return {
        "repos": user.get("public_repos", 0),
        "stars": stars,
        "followers": user.get("followers", 0),
        "commits": commits_this_year,
        "langs": top_langs,
        "ship": last_ship,
    }


def fmt(n):
    if n is None:
        return "—"
    return f"{n:,}"


def render_stats(s):
    counters = [
        ("REPOS", fmt(s["repos"])),
        ("STARS", fmt(s["stars"])),
        ("FOLLOWERS", fmt(s["followers"])),
        (f"COMMITS {date.today().year}", fmt(s["commits"])),
    ]
    cells = []
    x = 34
    for label, value in counters:
        cells.append(
            f'<text x="{x}" y="72" font-size="40" font-weight="900" fill="{OFFWHITE}">{escape(value)}</text>'
            f'<text x="{x}" y="96" font-size="11" font-weight="700" letter-spacing="3" fill="{OFFWHITE}" opacity="0.55">{escape(label)}</text>'
        )
        x += 240

    total = sum(w for _, w in s["langs"]) or 1
    bar_x, bar_w, bar_y = 34, 1132, 128
    segs, labels = [], []
    cx = bar_x
    shades = ["#F4F1EA", "#C9C4B8", "#9E988A", "#FF6B00", "#6E695E"]
    for i, (lang, w) in enumerate(s["langs"]):
        seg_w = max(int(bar_w * w / total), 24)
        if cx + seg_w > bar_x + bar_w or i == len(s["langs"]) - 1:
            seg_w = bar_x + bar_w - cx
        segs.append(f'<rect x="{cx}" y="{bar_y}" width="{seg_w}" height="14" fill="{shades[i % len(shades)]}"/>')
        cx += seg_w

    # Legend rendered as its own evenly-spaced row: color chip + name.
    # Decoupled from segment x positions so narrow segments never collide.
    lx = bar_x
    for i, (lang, w) in enumerate(s["langs"]):
        name = truncate(lang.upper(), 14)
        pct = round(100 * w / total)
        label = f"{name} {pct}%"
        labels.append(
            f'<rect x="{lx}" y="{bar_y + 26}" width="10" height="10" fill="{shades[i % len(shades)]}"/>'
            f'<text x="{lx + 18}" y="{bar_y + 35}" font-size="10" font-weight="700" letter-spacing="2" fill="{OFFWHITE}" opacity="0.65">{escape(label)}</text>'
        )
        lx += 18 + int(len(label) * 8.4) + 34

    if s["ship"]:
        repo, msg, day = s["ship"]
        ship_text = f'LAST SHIP: {repo} — “{truncate(msg, 60)}” — {day}'
    else:
        ship_text = "LAST SHIP: —"
    refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="230" viewBox="0 0 1200 230" role="img" aria-label="Live GitHub statistics for {escape(USER)}, regenerated daily from the GitHub API">
  <style> text {{ font-family: {FONT}; }} </style>
  <rect width="1200" height="230" fill="{BLACK}"/>
  <rect x="0" y="0" width="6" height="230" fill="{ORANGE}"/>
  <text x="34" y="30" font-size="12" font-weight="800" letter-spacing="4" fill="{ORANGE}">&#8220;LIVE TELEMETRY&#8221;</text>
  <text x="1166" y="30" text-anchor="end" font-size="10" font-weight="600" letter-spacing="2" fill="{OFFWHITE}" opacity="0.45">REFRESHED {escape(refreshed)} &#183; SOURCE: GITHUB API &#183; NO THIRD PARTIES</text>
  {''.join(cells)}
  {''.join(segs)}
  {''.join(labels)}
  <text x="34" y="206" font-size="13" font-weight="800" letter-spacing="2" fill="{ORANGE}">{escape(ship_text)}</text>
</svg>
'''


def render_stoic(quotes):
    idx = date.today().timetuple().tm_yday % len(quotes)
    q = quotes[idx]
    text = truncate(q["q"], 100)
    author = q["a"].upper()
    size = 20 if len(text) <= 72 else 16
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="140" viewBox="0 0 1200 140" role="img" aria-label="Daily stoic quote: {escape(text)} — {escape(author)}">
  <style> text {{ font-family: {FONT}; }} </style>
  <rect x="1" y="1" width="1198" height="138" fill="{OFFWHITE}" stroke="{BLACK}" stroke-width="2"/>
  <rect x="0" y="0" width="6" height="140" fill="{BLACK}"/>
  <text x="34" y="34" font-size="11" font-weight="800" letter-spacing="4" fill="{BLACK}" opacity="0.5">DAILY DOCTRINE &#183; NO. {idx + 1:03d}</text>
  <text x="34" y="80" font-size="{size}" font-weight="800" letter-spacing="1" fill="{BLACK}">&#8220;{escape(text.upper())}&#8221;</text>
  <text x="1166" y="116" text-anchor="end" font-size="12" font-weight="700" letter-spacing="3" fill="{ORANGE}">c/o {escape(author)}</text>
</svg>
'''


def main():
    with open(os.path.join(ROOT, "scripts", "quotes.json"), encoding="utf-8") as f:
        quotes = json.load(f)

    stats_svg = render_stats(fetch_stats())
    stoic_svg = render_stoic(quotes)

    assets = os.path.join(ROOT, "assets")
    os.makedirs(assets, exist_ok=True)
    with open(os.path.join(assets, "stats.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(stats_svg)
    with open(os.path.join(assets, "stoic.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(stoic_svg)
    print("wrote assets/stats.svg and assets/stoic.svg")


if __name__ == "__main__":
    sys.exit(main())
