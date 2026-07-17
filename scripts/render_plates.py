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


def fetch_shipping_log(limit=5):
    """Last `limit` pushes across repos: (date, repo, message).

    Skips the profile repo itself (bot refresh commits) and excluded repos.
    payload.commits is unreliable on the public feed, so the newest commit
    is fetched per repo instead; one entry per repo keeps the log varied.
    """
    entries, seen = [], set()
    events = api_get(f"/users/{USER}/events/public?per_page=100")
    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        full = ev["repo"]["name"]
        name = full.split("/")[-1]
        if name in EXCLUDED_REPOS or name == USER or full in seen:
            continue
        seen.add(full)
        latest = api_get(f"/repos/{full}/commits?per_page=1")
        if not latest:
            continue
        msg = latest[0]["commit"]["message"].splitlines()[0]
        day = latest[0]["commit"]["author"]["date"][:10]
        entries.append((day, name, msg))
        if len(entries) >= limit:
            break
    return entries


def render_shipping(entries):
    rows = []
    y = 78
    for day, repo, msg in entries:
        rows.append(
            f'<text x="34" y="{y}" font-size="16" font-weight="700" letter-spacing="1" fill="{OFFWHITE}" opacity="0.55">{escape(day)}</text>'
            f'<text x="168" y="{y}" font-size="16" font-weight="900" letter-spacing="1" fill="{ORANGE}">{escape(truncate(repo.upper(), 18))}</text>'
            f'<text x="420" y="{y}" font-size="16" font-weight="600" fill="{OFFWHITE}">&#8220;{escape(truncate(msg, 70))}&#8221;</text>'
        )
        y += 32
    if not entries:
        rows.append(f'<text x="34" y="78" font-size="16" fill="{OFFWHITE}" opacity="0.5">NOTHING ON THE DOCK. UNUSUAL.</text>')
    height = max(y + 12, 120)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="Shipping log: the latest commits pushed across {escape(USER)}'s repositories, regenerated daily">
  <style> text {{ font-family: {FONT}; }} </style>
  <rect width="1200" height="{height}" fill="{BLACK}"/>
  <rect x="0" y="0" width="6" height="{height}" fill="{ORANGE}"/>
  <text x="34" y="36" font-size="14" font-weight="800" letter-spacing="4" fill="{ORANGE}">&#8220;SHIPPING LOG&#8221;</text>
  <text x="1166" y="36" text-anchor="end" font-size="12" font-weight="600" letter-spacing="2" fill="{OFFWHITE}" opacity="0.45">LATEST PUSH PER REPO &#183; NEWEST FIRST</text>
  {''.join(rows)}
</svg>
'''


def fetch_streaks():
    """Contribution streaks from the GraphQL contributions calendar.

    Requires a token; raises on failure so the caller can keep the last
    good SVG instead of overwriting it with an empty plate.
    """
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN required for streak data")
    query = json.dumps({
        "query": """query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks { contributionDays { date contributionCount } }
              }
            }
          }
        }""",
        "variables": {"login": USER},
    }).encode("utf-8")
    req = urllib.request.Request(API + "/graphql", data=query, method="POST")
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, cur)

    current = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        elif d["date"] == date.today().isoformat():
            continue  # today can still get commits; don't break the streak yet
        else:
            break
    return {"total": cal["totalContributions"], "current": current, "longest": longest}


def render_streak(s):
    cells = []
    x = 34
    for label, value in [
        ("CURRENT STREAK", f'{s["current"]} DAYS'),
        ("LONGEST STREAK", f'{s["longest"]} DAYS'),
        ("CONTRIBUTIONS / YEAR", fmt(s["total"])),
    ]:
        cells.append(
            f'<text x="{x}" y="84" font-size="40" font-weight="900" fill="{BLACK}">{escape(value)}</text>'
            f'<text x="{x}" y="112" font-size="12" font-weight="700" letter-spacing="3" fill="{BLACK}" opacity="0.55">{escape(label)}</text>'
        )
        x += 400
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="150" viewBox="0 0 1200 150" role="img" aria-label="Contribution streaks for {escape(USER)}: current streak, longest streak, and total contributions this year">
  <style> text {{ font-family: {FONT}; }} </style>
  <rect x="1" y="1" width="1198" height="148" fill="{OFFWHITE}" stroke="{BLACK}" stroke-width="2"/>
  <rect x="0" y="0" width="6" height="150" fill="{ORANGE}"/>
  <text x="34" y="38" font-size="14" font-weight="800" letter-spacing="4" fill="{BLACK}" opacity="0.6">&#8220;CONSISTENCY REPORT&#8221;</text>
  {''.join(cells)}
</svg>
'''


def render_focus():
    with open(os.path.join(ROOT, "scripts", "focus.json"), encoding="utf-8") as f:
        focus = json.load(f)
    text = truncate(focus["text"], 110)
    size = 22 if len(text) <= 78 else (18 if len(text) <= 92 else 15)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="110" viewBox="0 0 1200 110" role="img" aria-label="Now building: {escape(text)}">
  <style>
    text {{ font-family: {FONT}; }}
    .dot {{ animation: blink 1.4s ease-in-out infinite; }}
    @keyframes blink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.2; }} }}
  </style>
  <rect width="1200" height="110" fill="{BLACK}"/>
  <rect x="0" y="0" width="6" height="110" fill="{ORANGE}"/>
  <circle class="dot" cx="46" cy="38" r="6" fill="{ORANGE}"/>
  <text x="66" y="44" font-size="14" font-weight="800" letter-spacing="4" fill="{ORANGE}">&#8220;NOW BUILDING&#8221;</text>
  <text x="34" y="84" font-size="{size}" font-weight="800" fill="{OFFWHITE}">{escape(text.upper())}</text>
</svg>
'''


def write_svg(name, content):
    assets = os.path.join(ROOT, "assets")
    os.makedirs(assets, exist_ok=True)
    with open(os.path.join(assets, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def main():
    with open(os.path.join(ROOT, "scripts", "quotes.json"), encoding="utf-8") as f:
        quotes = json.load(f)

    write_svg("stats.svg", render_stats(fetch_stats()))
    write_svg("stoic.svg", render_stoic(quotes))
    write_svg("focus.svg", render_focus())
    wrote = ["stats.svg", "stoic.svg", "focus.svg"]

    # Keep-last-good: these two depend on flakier data sources.
    try:
        write_svg("shipping.svg", render_shipping(fetch_shipping_log()))
        wrote.append("shipping.svg")
    except Exception as exc:  # noqa: BLE001 — keep previous SVG on any failure
        print(f"shipping.svg skipped: {exc}", file=sys.stderr)
    try:
        write_svg("streak.svg", render_streak(fetch_streaks()))
        wrote.append("streak.svg")
    except Exception as exc:  # noqa: BLE001
        print(f"streak.svg skipped: {exc}", file=sys.stderr)

    print("wrote " + ", ".join(wrote))


if __name__ == "__main__":
    sys.exit(main())
