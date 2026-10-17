# studymcp

A local MCP server for Claude Code over the Pre-Q notes. It handles retrieval and study state; the `/study` skill (`.claude/skills/study/`) holds the teaching behaviour.

```
.mcp.json ──> uv run studymcp serve ──> six tools: search · read · topic · drill · log · plan
                     │
                     ├─ index.py   in-memory SQLite FTS5 over notes, TERMS/reference, SYLLABUS,
                     │             Anki decks and local/extracted (rebuilt from file stats, ~1.5 s)
                     ├─ links.py   topic graph: syllabus objectives, study-guide rank/why/method,
                     │             tiers, decks, traps, past-paper cites, exam dates (STUDY-PLAN.md)
                     ├─ drill.py   per-item memory model and the adaptive queue
                     └─ state.py   local/progress/events.jsonl + <CODE>-errors.md (gitignored)
```

Nothing is cached on disk except the study state. Edit a note and the next tool call sees it.

## Run

```bash
uv sync --project tools/studymcp                      # once, installs mcp into tools/studymcp/.venv
uv run --project tools/studymcp studymcp doctor       # parse everything, report counts and broken links
uv run --project tools/studymcp studymcp search "longshore drift"
uv run --project tools/studymcp studymcp topic econ ped
uv run --project tools/studymcp studymcp drill maths --n 5
uv run --project tools/studymcp studymcp plan
uv run --project tools/studymcp pytest                # fixture-repo tests plus a real-repo smoke test
```

Claude Code starts the server from `.mcp.json`; `.claude/settings.json` allows its tools and runs `studymcp brief --hook` at session start.

## Update quickly

| Change | Where |
|---|---|
| Note content, new sections | just edit the notes |
| New topic | a row in `SYLLABUS.md` and in the study guide's priority order / checklist |
| Exam dates | the exams table in `STUDY-PLAN.md` |
| Subject weights, aliases, topic aliases, new term (`T5`) | `config.toml` |
| Drill timing (how soon misses come back, recall target, growth) | `[drill]` in `config.toml`; history is replayed, so changes apply to past reviews too |
| Planner weights | `[plan]` in `config.toml` |
| Teaching behaviour | `.claude/skills/study/SKILL.md` and `marking.md` |
| Server code | `src/studymcp/`, then `/mcp` → reconnect |

Run `doctor` after big edits: it lists notes with no rank or tier, links to missing pages, and subjects whose priority table did not parse.

## The drill model

Each item (flashcard or logged mistake) has a stability S in days; predicted recall after t days is 0.9^(t/S). An item is due once recall drops below the target (0.90, or 0.95 within two days of that subject's exam). A miss sets S to about 10 minutes, so it comes back in the same session; a correct answer multiplies S by up to 2.5, more when recall had faded and almost not at all when asked again too soon. Batches are: recent misses, then the most-faded due items weighted by topic priority, then new items from the highest-priority topics.

## Adding a tool

Add a method to `Study` in `tools.py` (return compact markdown, cap the size), register it in `server.py` with `@mcp.tool(structured_output=False)`, add a CLI command in `cli.py` if useful, add a test, and mention it in the skill. Nothing in the package may print to stdout: that channel carries JSON-RPC.
