# School notes repo

Pre-Q revision notes for six subjects, authored here and published to the GitHub wiki. Exams: see `STUDY-PLAN.md`.

## Studying

- The `study` MCP server (`tools/studymcp`) indexes the notes, reference sheets, syllabi, Anki decks and the school material in `local/extracted`, and keeps the study state.
- For any question about subject content, ground the answer in `search` / `read` and cite the ids; the notes outrank general knowledge. Use `topic` to link an answer back to the exam.
- Study sessions run through the `/study` skill: one command (`/study [subject] [topic]`), then plain talk. `session` gives a sweep (quick true/false over a topic, level 1) or ideas to deepen at levels 2–5. Every answer is logged with its level.
- Study state lives in `local/progress/` (gitignored): `events.jsonl`, `<CODE>-errors.md` and `carryover/<CODE>.md` (where the next session starts). Never copy it into a tracked file.
- The prep bank (`local/bank/`, gitignored) holds Claude-written gists and true/false statements per topic. `studymcp bank` shows stale topics; `.claude/skills/study/prep.md` rebuilds one.

## Authoring

- `T4-<CODE>/SYLLABUS.md` defines reading order: its index table links each `notes/<stem>.md` and `anki/<stem>.txt`. A new topic needs a row there and a row in `notes/study-guide.md` (priority order and topic checklist), or it shows as unranked.
- Notes: one `# Title`, sections at `##`/`###`; definitions as `**Term** = …` in notes or `**Term** — …` in TERMS.md; traps under a "This loses marks" heading or a `**This loses marks:**` paragraph. Editing a heading changes its section id.
- Anki decks: tab-separated, Anki header lines, four columns (note type, Front/Text, Back/Extra, Hint).
- `local/` (school material, toolchain, progress) is gitignored and must stay unpublished.
- Accent colour: electro purple `#c800ff` (`ACCENT` in `build.py`) for the README badges and stats card, PDF headings, the occlusion preview and Anki cloze styling. Diagram colours are data encodings, not the accent: leave them.

## Cambridge AS & A Level (2027–28)

- `cambridge/` holds next year's course: `maths`, `economics`, `business`, `geography`, `english-language`, `english-literature`, each one folder for the whole AS + A Level syllabus. `cambridge/README.md` is the context for how AS and A Level work and for the folder's conventions; `cambridge/PLAN.md` has the exams.
- Each subject folder's `README.md` is its hub: papers, topics with rank and progress, exam technique. Topic files sit beside it, named after the syllabus (`economics/02-price-system.md`, `maths/p1-quadratics.md`). Each opens with what the syllabus asks and what it builds on from Pre-Q. Definitions and traps follow the note conventions above, plus:
  - A topic starts as a skeleton: its first line is `*Status: skeleton…*`, then one `##` per syllabus subtopic. Deleting that line makes it live.
  - *(to verify)* marks facts not yet checked against the official syllabus; never put it in a heading.
  - Decks use `#deck:Cambridge::<Subject>::…` and the note types Cambridge Basic / Cambridge Cloze.
- The study server, `build.py` and `/study` don't read `cambridge/` yet (they're wired up after the Pre-Q exams). Until then, answer from the files directly.

## Commands

- `python build.py wiki | push-wiki | pdf [CODES]` builds the wiki and PDFs. `python build.py stats` refreshes the README counts after adding notes, decks or diagrams.
- `uv run --project tools/studymcp studymcp doctor` checks parsing and links after big edits; `... pytest` runs the server tests.
- Edits to notes reach the server on the next tool call. After changing server code or `tools/studymcp/config.toml`, reconnect it with `/mcp`.
