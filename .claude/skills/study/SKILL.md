---
name: study
description: Run a Pre-Q exam study session from this repo's notes. Modes are next, blurt, quiz, paper, cards and errors. Use when the student types /study, asks what to study next, asks to be quizzed or tested on a subject or topic, wants to blurt a topic, wants a timed past-paper section, or wants to review Anki cards with Claude.
---

# /study: exam study sessions

Repo root is the folder that holds `STUDY-PLAN.md`. Subjects and folders:

| Subject | Folder | Anki deck | Code |
|---|---|---|---|
| Maths | `T4-MAQ` | Mathematics | MAQ |
| Economics | `T4-ECQ` | Economics | ECQ |
| English | `T4-ENQ` | English | ENQ |
| Business | `T4-BUQ` | Business | BUQ |
| Geography | `T4-GEQ` | Geography | GEQ |
| Physics | `T4-PHQ` | Physics | PHQ |

Ground truth for content is the subject's `notes/*.md`, `SYLLABUS.md` and reference files. The school's own material is in `local/extracted/<CODE>/*.md` (text) and `local/sources/<CODE>/` (originals). Never mark against memory when the notes say something specific. Cite the note page when you correct an answer.

The personal error log is `local/progress/<CODE>-errors.md`. It is gitignored and never published. Append one line per lost mark:
`- YYYY-MM-DD · topic · what went wrong · the fix · source page`

Keep every session short and active. The student types or says the answers; you never answer for them.

## Modes

### `next`
No timetable and no fixed times: the student chooses when to study. Recommend what to work on now.
1. Read the exam dates and the "Priority across subjects" section in `STUDY-PLAN.md`. Work out which exam is next and how many days are left.
2. Read that subject's `notes/study-guide.md` priority order and its error log. If the Anki MCP tools are available, call `list_decks` with stats.
3. Reply with: the next exam and the days left; the top two or three things to work on (the highest-priority item not yet secure, plus anything that shows up repeatedly in the error log), each linked to its note page and paired with its method; and the Anki due and new counts. Keep it to a short list, not a schedule.

### `blurt <subject> <topic>`
1. Find the topic's note page or section. Tell the student which section to read, and to close it when done.
2. Ask them to write everything they remember: definitions, chains, diagram labels, examples, quotes.
3. Mark it against the page. List what was correct, what was **missing** (most important first) and what was **wrong**. Log wrong items to the error log.
4. Finish with three questions on the missing items. Mark those answers too.

### `quiz <subject> <topic>`
1. Set five to eight exam-style questions in the subject's real format, taken from the study guide and the past-question patterns in `SYLLABUS.md`:
   - **Maths and Physics:** calculations with marks. Physics needs equation, substitution, answer and unit.
   - **Economics and Business:** command-word questions with mark values. In Business, include the application to a case.
   - **English:** quote recall by theme or scene, then a 10-minute plan for a past question.
   - **Geography:** define, explain a named process in three steps, name an example, and one diagram to describe.
2. Ask one question at a time and wait for the answer.
3. Mark each answer with the subject's mark rules: Maths M/A/S marks and accuracy from `notes/exam-errors.md`; Business [k] [app] [an] [ev]; Geography's mark-scheme points and the need for named examples. Give the score and the fix.
4. Log every lost mark. At the end, give the score and the one habit to change.

### `paper <subject> [topic]`
1. Choose a real question. Use school papers in `local/extracted/<CODE>` first (Maths term exams and common tests; English past papers; the Geography Term 2 paper; the Business 2018 specimen). Otherwise use IGCSE-style questions built from the notes. Say which source you used.
2. Give the question, the marks and a time limit of about one minute per mark (1.5 for Economics and Business essays). Ask the student to say when they start and when they finish.
3. Mark against the mark scheme in `local/extracted/<CODE>` when one exists, otherwise against the notes. Show the marks awarded line by line and what a full-mark answer adds.
4. Log every lost mark.

### `cards <deck>`
Use the Anki MCP review loop. Call `get_due_cards` for the deck, then `present_card` showing the question only. Wait for the student's answer, then show the answer. Suggest a rating, but let the student confirm it before calling `rate_card`. Continue until they stop or nothing is due. Report how many cards were reviewed and which ones were missed.

### `errors <subject>`
Read the error log. Group the entries by type and rank them by frequency. Then set one fresh question for each of the top three error types. If the same error appears three or more times, offer to add an Anki card for it to that subject's `0 ...` deck. Add the card with `add_note` only if the student says yes.

## Rules
- The exam dates are in `STUDY-PLAN.md`. Within two days of a subject's exam, consolidate only: no new topics, and point to the subject's errors or traps page.
- Don't write long lectures. If the student is stuck, give the smallest hint first.
- Keep the error log factual and short. Never put it in a published file.
