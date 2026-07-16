# NAME0x0 Profile README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild profile README as self-hosted Off-White-inspired SVG design system with daily native-stats refresh.

**Architecture:** Hand-crafted static/animated SVGs in `assets/` (self-backgrounded, theme-proof) + `scripts/render_plates.py` generating `stats.svg`/`stoic.svg` daily via `refresh.yml`. README.md is thin markdown assembling the assets. Spec: `docs/superpowers/specs/2026-07-16-readme-redesign-design.md`.

**Tech Stack:** SVG (in-file CSS animation), Python 3 stdlib only, GitHub Actions, GitHub API via GITHUB_TOKEN.

## Global Constraints

- Palette: off-white `#F4F1EA`, black `#0A0A0A`, accent safety orange `#FF6B00` (sparing).
- Typography in SVGs: Helvetica/Arial Bold caps, `"QUOTED"` labels, `c/o` lines.
- Every SVG carries its own background rect (theme-proof). Font stack `Helvetica Neue, Helvetica, Arial, sans-serif` only (no webfonts — GitHub blocks external loads in SVG-as-img).
- No `<foreignObject>`, no external refs in SVGs (camo strips them).
- No BidGenius anywhere. HAGI at most a passing link.
- Commits: conventional, no co-author trailer.
- Verification per asset: render via local HTTP + headless browse screenshot (file:// blocked by daemon).

---

### Task 1: Static brand assets (dividers, caption, status label)

**Files:** Create `assets/divider-stripes.svg`, `assets/caption-vagabond.svg`, `assets/label-status.svg`
**Produces:** Visual language baseline (stripe pattern, plate style, label style) reused by all later assets.

- [ ] divider-stripes.svg: full-width (1200×24) diagonal hazard stripes, black/off-white, thin orange keyline.
- [ ] caption-vagabond.svg: small black plate, `"VAGABOND"` quoted caps + `c/o MIYAMOTO MUSASHI` line.
- [ ] label-status.svg: off-white plate, `STATUS: "OPEN TO WORK"` + AI/ML/SWE · DUBAI / REMOTE · GOLDEN VISA — NO SPONSORSHIP · blinking orange dot (CSS keyframes).
- [ ] Screenshot all three via local HTTP preview; iterate until clean.
- [ ] Commit: `feat: add industrial brand SVG baseline (dividers, captions, status)`

### Task 2: brand-header.svg (animated wordmark)

**Files:** Create `assets/brand-header.svg`
- [ ] 1200×220 black plate. `NAME0x0` giant bold caps off-white; orange `®`-style tick. Sub-line cycles quoted roles via CSS keyframes opacity swap (4 roles × 3s): "AI ENGINEER" / "SYSTEMS ARCHITECT" / "MULTI-AGENT WRANGLER" / "FROM-SCRATCH ABSOLUTIST". `c/o MUHAMMAD AFSAH MUMTAZ — DUBAI` footer line.
- [ ] Screenshot; verify animation via 2 timed screenshots (different frames visible).
- [ ] Commit: `feat: add animated brand header`

### Task 3: manifesto.svg (FROM SCRATCH list)

**Files:** Create `assets/manifesto.svg`
- [ ] Off-white plate, title `"FROM SCRATCH"` + sub `THINGS I WILL BUILD MYSELF. ALL OF THEM.`. Rows: CAR / LANGUAGE / PROGRAMMING LANGUAGE / COMPUTER / MOBILE PHONE / CLOTHES, each with dotted leader + stamp `NOT YET` (orange, rotated ~-6°, staggered fade-in animation). Last row: `EXCUSES` → stamp `NEVER` (black).
- [ ] Screenshot; commit: `feat: add from-scratch manifesto plate`

### Task 4: Tier-1 project plates + tier-2 strip

**Files:** Create `assets/plate-pantheon.svg`, `assets/plate-ava.svg`, `assets/plate-mald.svg`, `assets/strip-tier2.svg`
- [ ] Shared plate layout (1200×150): left big quoted project name + wit label, right receipts block, bottom tech line + repo path. Content per spec (Brier 0.149 / ARC 82.0% / scoop-shipped etc.). Pantheon wit: `11 AGENTS, ZERO CONSENSUS`. AVA wit: `2B PARAMS, 3B PROBLEMS`. MALD wit: `YOUR NOTES, NOBODY'S CLOUD`.
- [ ] strip-tier2.svg (1200×90): three mini-cells — WEBDESK / OMNI / PANE with one-liners.
- [ ] Screenshot all; commit: `feat: add project plates and tier-2 strip`

### Task 5: Generated plates pipeline (CODEX delegation)

**Files:** Create `scripts/render_plates.py`, `scripts/quotes.json`, initial `assets/stats.svg`, `assets/stoic.svg`
**Interfaces (Codex brief must pin):**
- `python scripts/render_plates.py` — no args; env `GITHUB_TOKEN` optional (unauthenticated fallback OK for local run), env `GH_USER` default `NAME0x0`.
- Writes `assets/stats.svg` (1200×230): REPOS / STARS / FOLLOWERS / COMMITS-THIS-YEAR counters + TOP LANGUAGES bar (top 5 by repo bytes) + `LAST SHIP: <repo> — "<msg 60ch>" — <YYYY-MM-DD>` from latest public PushEvent.
- Writes `assets/stoic.svg` (1200×140): date-seeded quote from quotes.json, attribution line.
- quotes.json: `[{"q": str, "a": str}]`, ≥60 entries, Marcus Aurelius/Seneca/Epictetus.
- stdlib only (urllib, json, datetime). XML-escape all interpolated text. Truncate to fixed widths. Same palette/typography constants as Task 1 assets (pass exact hex + font stack in brief).
- [ ] Delegate to Codex via codex:rescue with exact brief.
- [ ] Review every hunk; run `python scripts/render_plates.py` locally; screenshot both SVGs.
- [ ] Commit: `feat: add native stats + stoic plate generator`

### Task 6: refresh.yml workflow (CODEX delegation, same session)

**Files:** Create `.github/workflows/refresh.yml`; Delete `.github/workflows/focus.yml`, `.github/workflows/quote.yml`
- [ ] Daily cron `17 0 * * *` + workflow_dispatch; permissions contents:write; checkout, curl both gh-ascii cards with `|| true` (keep last good), run render_plates.py with `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`, commit-if-diff push.
- [ ] Review hunks; `actionlint` if available, else careful read.
- [ ] Commit: `feat: replace focus/quote crons with unified refresh workflow`

### Task 7: README.md assembly

**Files:** Rewrite `README.md`
- [ ] Assemble approved 14-slot skeleton. Crawlable prose block after header (full name once, keywords: AI engineer, LLM fine-tuning, multi-agent systems, Rust, Dubai). Everything-else strip: MAVIS · Terminus · neural-nets · AGI-Ledger one-liners. Capabilities matrix kept (reworded tight). Keep Spotify embed, snake, Ko-fi. Descriptive alt on every img. Drop komarev badge, typing-svg, github-readme-stats, streak, profile-summary-cards, followers badge (replaced by native system).
- [ ] Commit: `feat: rebuild profile README on self-hosted design system`

### Task 8: SEO + ship + verify

- [ ] `gh api` set repo description + topics (`ai-engineer, llm, fine-tuning, multi-agent, rust, profile-readme, dubai`).
- [ ] Push; screenshot live github.com/NAME0x0 full page, dark + light theme; verify every image loads, animations run, no broken camo refs.
- [ ] `gh workflow run refresh.yml`; verify green run + no spurious diff commit.
- [ ] Fix-forward anything broken; final screenshot to user.

## Self-Review Notes

- Spec coverage: all 14 skeleton slots covered (T1–T7); automation (T5–T6); SEO (T8); acceptance criteria 1–6 mapped to T8 verification + global constraints.
- Deviation from writing-plans template: SVG source not inlined in plan (visual-iterative craft, verified by screenshot per task) — accepted trade-off per user token-efficiency rules.
