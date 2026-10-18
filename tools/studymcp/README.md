# studymcp

A local MCP server for Claude Code over the Pre-Q notes. It handles retrieval and study state; the `/study` skill (`.claude/skills/study/`) holds the teaching behaviour.

```
.mcp.json ──> uv run studymcp serve ──> seven tools: session · search · read · topic · drill · log · plan
                     │
                     ├─ index.py   in-memory SQLite FTS5 over notes, TERMS/reference, SYLLABUS,
                     │             Anki decks and local/extracted (rebuilt from file stats, ~1.5 s)
                     ├─ links.py   topic graph: syllabus objectives, study-guide rank/why/method,
                     │             tiers, decks, traps, past-paper cites, exam dates (STUDY-PLAN.md)
                     ├─ ideas.py   idea clusters (a `##` section plus its sub-sections), gists, content hints
                     ├─ drill.py   per-item memory model with levels, and the quick-fire queue
                     └─ state.py   local/progress/events.jsonl + <CODE>-errors.md (gitignored)
```

Nothing is cached on disk except the study state. Edit a note and the next tool call sees it.

## Run

```bash
uv sync --project tools/studymcp                      # once, installs mcp into tools/studymcp/.venv
uv run --project tools/studymcp studymcp doctor       # parse everything, report counts and broken links
uv run --project tools/studymcp studymcp session econ        # the brief a study session starts from
uv run --project tools/studymcp studymcp search "longshore drift"
uv run --project tools/studymcp studymcp topic econ ped
uv run --project tools/studymcp studymcp drill maths --n 5
uv run --project tools/studymcp studymcp plan
uv run --project tools/studymcp pytest                # fixture-repo tests plus a real-repo smoke test
```

Claude Code starts the server from `.mcp.json`; `.claude/settings.json` allows its tools and runs `studymcp brief --hook` at session start.

## On claude.ai (web and phone)

`serve --http PORT` runs the same tools over streamable HTTP; `web.ps1` puts it behind an ngrok static domain, so it works from any network while the laptop is on. The URL path holds a secret from `local/mcp-token` (the only auth: keep the URL private; delete the file to rotate it).

Once: `ngrok config add-authtoken <token>` (dashboard.ngrok.com), claim the free static domain and write it to `local/ngrok-domain`. Then run `tools/studymcp/web.ps1` and add the printed URL on claude.ai under Settings › Connectors › Add custom connector. Later runs print the same URL.

## Update quickly

| Change | Where |
|---|---|
| Note content, new sections | just edit the notes |
| New topic | a row in `SYLLABUS.md` and in the study guide's priority order / checklist |
| Exam dates | the exams table in `STUDY-PLAN.md` |
| Subject weights, aliases, topic aliases, new term (`T5`) | `config.toml` |
| Drill timing (how soon misses come back, recall target, growth) | `[drill]` in `config.toml`; history is replayed, so changes apply to past reviews too |
| Levels (credit per level, exam floor, multiple-choice share) | `[levels]` in `config.toml` |
| Session brief (ideas per brief, how many mixed in, when an idea is solid) | `[session]` in `config.toml` |
| Planner weights | `[plan]` in `config.toml` |
| Teaching behaviour | `.claude/skills/study/SKILL.md`; task how-tos in `methods.md`; what counts as right per subject in `subjects.md` |
| Server code | `src/studymcp/`, then `/mcp` → reconnect |

Run `doctor` after big edits: it lists notes with no rank or tier, links to missing pages, and subjects whose priority table did not parse.

## Ideas and levels

An **idea** is one `##` section of a notes page with its `###` sub-sections (pages with fewer than three `##` sections are split at `###`; "This loses marks" sections are traps, not ideas). Its id is the first section's id, so `read(id)` returns the whole idea.

Every item (idea, flashcard or logged mistake) has a **level** from 0 to 5: 1 spot it, 2 fix it, 3 build it, 4 explain it, 5 from memory. An answer at level r moves it: ok raises it to at least r, shaky sets it to r − 1, a miss caps it at r − 1, and a slip leaves it alone. The next task is one level up, one lower if the item is fading, and at least 3 for seen items within three days of the exam.

**Timing** uses a stability S in days; predicted recall after t days is 0.9^(t/S). An item comes back once recall drops below the target (0.90, or 0.95 within two days of that subject's exam). A miss sets S to about 10 minutes; a right answer multiplies S by up to 2.5, scaled by the level's credit (an easy true/false counts for less than a blurt).

`session` picks a topic: the one named, the one studied last in that subject (moving on once every idea is at level 3 and not fading), or the planner's pick. It lists missed, fading and new ideas first, puts ideas touched today at the back, and mixes in a few ideas from neighbouring or weak topics in the same subject. `drill` serves flashcards and past mistakes the same way, as quick-fire items whose form follows the level.

## Adding a tool

Add a method to `Study` in `tools.py` (return compact markdown, cap the size), register it in `server.py` with `@mcp.tool(structured_output=False)`, add a CLI command in `cli.py` if useful, add a test, and mention it in the skill. A new task type needs no code: describe it in `methods.md` and log it with any `mode` name. Nothing in the package may print to stdout: that channel carries JSON-RPC.
