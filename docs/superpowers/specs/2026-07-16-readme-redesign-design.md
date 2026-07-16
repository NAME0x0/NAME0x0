# NAME0x0 Profile README Redesign — Design Spec

Date: 2026-07-16
Status: Approved by user (consultation rounds 1–5)

## Goal

Rebuild the GitHub profile README (`NAME0x0/NAME0x0`) as a self-hosted,
Off-White-inspired industrial design system. Replace third-party widget imports
with SVG assets owned by this repo, refreshed daily by a GitHub Action pulling
real data from the GitHub API. Serve five audiences: recruiters (signals),
casual visitors (impressed), technical visitors (inspiration), first-timers
(captivated), search engines (crawlable keywords).

## Brand System

- **Name on the plate:** `NAME0x0` (primary). "Muhammad Afsah Mumtaz" appears
  once in crawlable prose. AFSAH secondary.
- **Palette:** off-white `#F4F1EA` plates, black `#0A0A0A` type/plates,
  safety orange `#FF6B00` accent (stripes, stamps, sparingly).
- **Typography (in SVGs):** Helvetica/Arial Bold caps, `"QUOTED"` labels,
  `c/o` attribution lines, diagonal hazard-stripe dividers.
- **Constraint:** GitHub sanitizes README HTML (no style/JS/classes). All
  styling and animation lives INSIDE SVG files (CSS keyframes/SMIL in-SVG).
  Every SVG carries its own background → identical on GitHub dark/light.
- Inspired-by Off-White; do NOT copy trademarked marks (cross-arrows logo).

## Page Skeleton (approved order)

1. gh-ascii card — dark theme only, plain `<img src="dark_mode.svg" width="100%">`
2. `assets/brand-header.svg` — NAME0x0 wordmark + cycling quoted roles (animated)
3. `assets/label-status.svg` — "OPEN TO WORK" · AI/ML/SWE · Dubai/remote ·
   Golden Visa (no sponsorship) · m.afsah.279@gmail.com
4. `assets/manifesto.svg` — "FROM SCRATCH" list: car, language, compiler,
   computer, phone, clothes — each stamped `NOT YET` (animated stamps).
   50/50 visionary/goofy tone.
5. Tier-1 project plates: `plate-pantheon.svg`, `plate-ava.svg`, `plate-mald.svg`
6. Tier-2 strip: `strip-tier2.svg` — WebDesk · OMNI · pane
7. Everything-else strip (markdown one-liners + links): MAVIS, Terminus,
   neural-nets, AGI-Ledger. **BidGenius excluded entirely.**
8. `assets/stats.svg` — native stats (generated daily, see Automation)
9. Capabilities matrix — markdown table (crawlable, keyword-dense; keep
   existing content, refresh wording)
10. Musashi GIF — framed: stripe divider above/below + `"VAGABOND"` caption plate
11. Beyond the Repos — hackathon 2× runner-up, Chairman MDX Computing Society,
    Committee Chair BCS. HAGI demoted to at most a passing link (noise).
12. `assets/stoic.svg` — daily stoic quote from own `quotes.json`
13. Spotify widget (keep as-is) + contribution snake (keep as-is)
14. Contact footer: email · LinkedIn · Portfolio · Pantheon live · Ko-fi button

## Project Content (receipts)

- **Pantheon-Trades** (12★): live pantheon-trades.vercel.app, 11 LLM agents,
  Brier 0.149 / 200-market backtest, 714 Python + 65 Solidity tests.
  Wit label allowed: "11 AGENTS, ZERO CONSENSUS".
- **AVA** (4★): 2B LLM fine-tune → 82.0% ARC-Challenge / 92.0% ARC-Easy,
  beats Llama 3.2 3B-Instruct (78.6%), 42 MB adapter, 4 GB GPU,
  17-benchmark / 16,872-task eval harness.
- **MALD** (4★): Rust single-binary PKM, hybrid FTS5 + HNSW search, cited RAG
  to file+line, distributed via own scoop bucket.
- **WebDesk** (3★, C#): any website/video/shader as live Windows wallpaper.
- **OMNI** (Rust): 1.05T-parameter sparse MoE research — the vision project.
- **pane** (Rust): real Linux desktops on Windows (WSL2/XRDP), shipped pane.exe.

## Asset Inventory (`assets/`)

| File | Content | Animated | Source |
|---|---|---|---|
| brand-header.svg | wordmark + cycling roles | yes | hand-crafted |
| label-status.svg | open-to-work line | subtle | hand-crafted |
| manifesto.svg | FROM SCRATCH + NOT YET stamps | yes | hand-crafted |
| plate-pantheon/ava/mald.svg | project plates | no | hand-crafted |
| strip-tier2.svg | 3 mini plates | no | hand-crafted |
| divider-stripes.svg | hazard stripes | no | hand-crafted |
| caption-vagabond.svg | musashi frame caption | no | hand-crafted |
| stats.svg | live GitHub stats + LAST SHIP line | no | generated daily |
| stoic.svg | daily quote plate | no | generated daily |

`dark_mode.svg` / `light_mode.svg` (gh-ascii cards) live at repo root,
refreshed daily. Only dark is embedded; light kept for optional future use.

## Automation

New `.github/workflows/refresh.yml` (daily cron ~00:07 UTC + workflow_dispatch,
`permissions: contents: write`):

1. `curl -fL "https://gh.crafter.run/NAME0x0?theme=dark" -o dark_mode.svg`
   (and light). Non-fatal on failure (keep last good copy).
2. `python scripts/render_plates.py`:
   - GitHub API (built-in `GITHUB_TOKEN`): public repo count, total stars,
     followers, commit count (contributions), top languages, latest public
     push (repo + commit message + date) → render `assets/stats.svg`.
   - Pick quote deterministically (date-seeded) from `scripts/quotes.json`
     (own curated Marcus Aurelius / Seneca / Epictetus set, ~60 quotes)
     → render `assets/stoic.svg`.
   - Rendering via string templates into SVG (no external deps beyond
     `requests` or stdlib urllib; prefer stdlib).
3. Commit + push only if diff.

**Deletes:** `focus.yml`, `quote.yml` (superseded). **Keeps:** `snake.yml`.

SVG text safety: escape XML entities; truncate commit messages to fit plate
width; fixed-width layout so generated text never overflows.

## SEO / Visibility

- Real markdown headings with keywords: AI Engineer, LLM fine-tuning,
  multi-agent systems, Rust, Dubai. Signals live in text, never image-only.
- Full name once in prose. Descriptive alt text on every image.
- Set profile repo description + topics via `gh api` (e.g. `ai-engineer`,
  `llm`, `fine-tuning`, `multi-agent`, `rust`, `profile-readme`).
- Capabilities matrix remains crawlable markdown.

## Execution Split (fable-gpt)

- **Claude (orchestrator):** all hand-crafted SVGs, README.md assembly,
  final review, commit.
- **Codex (executor):** `scripts/render_plates.py`, `scripts/quotes.json`,
  `refresh.yml`. Claude reviews every hunk, runs the script locally before
  accepting.

## Acceptance Criteria

1. README renders correctly on github.com/NAME0x0 in dark AND light theme
   (verified via browser screenshot).
2. All images load from own repo except: Spotify widget, snake (own repo
   output branch), komarev visitor badge if kept (drop it — replaced by
   native stats plate... decision: DROP).
3. `render_plates.py` runs green locally and in Action; stats.svg + stoic.svg
   valid SVG/XML.
4. No BidGenius mention. No HAGI section (link at most).
5. focus.yml/quote.yml removed; snake.yml untouched; refresh.yml green run.
6. Commit style: conventional commits, no co-author trailer (user preference).
