# School notes repo

Pre-Q revision notes for six subjects, authored here and published to the GitHub wiki. Exams: see `STUDY-PLAN.md`.

## Studying

- The `study` MCP server (`tools/studymcp`) indexes the notes, reference sheets, syllabi, Anki decks and the school material in `local/extracted`, and keeps the study state.
- For any question about subject content, ground the answer in `search` / `read` and cite the ids; the notes outrank general knowledge. Use `topic` to link an answer back to the exam.
- Study sessions run through the `/study` skill (next, explain, need, blurt, quiz, paper, drill, cards, errors).
- Study state lives in `local/progress/` (gitignored): `events.jsonl` and `<CODE>-errors.md`. Never copy it into a tracked file.

## Authoring

- `T4-<CODE>/SYLLABUS.md` defines reading order: its index table links each `notes/<stem>.md` and `anki/<stem>.txt`. A new topic needs a row there and a row in `notes/study-guide.md` (priority order and topic checklist), or it shows as unranked.
- Notes: one `# Title`, sections at `##`/`###`; definitions as `**Term** = …` in notes or `**Term** — …` in TERMS.md; traps under a "This loses marks" heading or a `**This loses marks:**` paragraph. Editing a heading changes its section id.
- Anki decks: tab-separated, Anki header lines, four columns (note type, Front/Text, Back/Extra, Hint).
- `local/` (school material, toolchain, progress) is gitignored and must stay unpublished.

## Commands

- `python build.py wiki | push-wiki | pdf [CODES]` builds the wiki and PDFs.
- `uv run --project tools/studymcp studymcp doctor` checks parsing and links after big edits; `... pytest` runs the server tests.
- Edits to notes reach the server on the next tool call. After changing server code or `tools/studymcp/config.toml`, reconnect it with `/mcp`.
