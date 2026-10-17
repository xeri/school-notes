---
name: study
description: Run a Pre-Q exam study session from this repo's notes, using the study MCP tools. Modes are next, explain, need, blurt, quiz, paper, drill, cards and errors. Use when the student types /study, asks to explain a concept from one of their subjects, asks what they need to know for a topic or exam, asks what to study next, wants to be quizzed, drilled or tested, wants to blurt a topic, wants a timed past-paper question, or wants to review flashcards.
---

# /study: exam study sessions

Six subjects: Maths `MAQ`, Economics `ECQ`, English `ENQ`, Business `BUQ`, Geography `GEQ`, Physics `PHQ`. Short names work everywhere (maths, econ, eng, bus, geo, phys).

## Tools

The `study` MCP server holds the content and the student's state. Use it instead of reading files by hand.

| Tool | Use it for |
|---|---|
| `search(query, subject?, kind?)` | find the right section; `kind="papers"` for past papers and mark schemes, `kind="terms"` for definitions |
| `read(id)` | full text of a section, with an exam-link footer (rank, objectives, traps, deck) |
| `topic(subject, topic?)` | what the exam needs for a topic; with no topic, the subject's format and mark rules |
| `drill(subject?, topic?, n, focus?)` | the next adaptive batch: recent misses, items about to be forgotten, then new ones |
| `log(subject, topic, mode, score?, out_of?, errors?, reviews?)` | record marks, lost marks and drill grades |
| `plan(subject?)` | countdown, top three to do now, mastery, error types |

If the tools are missing, say the `study` server is not connected (check `/mcp`), then work from `T4-<CODE>/notes/*.md`, `SYLLABUS.md` and the reference files directly.

Ground truth is the notes. Cite the ids you used (`ECQ/markets#conditions-of-demand`). Results tagged school material are an unverified extraction of the school's papers: use them for question style and mark-scheme points, and say so.

## Reading the command

`/study <mode> [subject] [topic]`. With no mode: a question or concept means `explain`; nothing means `next`. Topic is free text (`ped`, `coasts`, `quadratics`); the tools resolve it.

## Voice

- **explain and need:** clear, plain, full sentences, even if a terse style is active elsewhere. Use the notes' own wording and the exam's command words. No padding.
- **quiz, drill, marking:** terse. One question at a time.
- Never answer for the student. When they are stuck, give the smallest hint first.

## Modes

### `next`
Call `plan()`. Reply with the next exam and days left, the three recommendations (each with why, method and the `/study` command to start it) and the drill queue. A short list, not a timetable.

### `explain <topic or question>`
1. `search` the question (with the subject if known), then `read` the best notes section. Use a `Definition` hit if there is one.
2. Answer in at most about 250 words unless the student asks for more:
   - **The idea:** one sentence.
   - **How it works:** the chain, mechanism or steps, in the notes' wording, with the worked example, named example (Geography) or quotation (English) the notes give. If the section has a `[figure: …]`, tell them to draw it.
   - **In the exam:** the objective it belongs to, how it is asked (command word and marks), what earns the marks, and the trap. Take these from the `read` footer, or call `topic` when the footer is thin.
   - **Sources:** the ids used.
3. If the notes do not cover it, say so first, then explain briefly from general knowledge and label it as such.
4. Ask one short exam-style check question. Mark it, then `log(subject, topic, "explain", score, out_of, errors)`. A miss becomes a drill item automatically.

### `need <subject> <topic>`
Call `topic`. Turn it into a checklist of what the exam needs, about 20 lines:
- exam date and days left, priority rank and tier, and why it matters;
- **Define** (terms), **Draw** (diagrams), **Calculate** (formulas), **Explain** (chains, processes), **Quote / name** (quotations, case studies);
- **Traps** that lose marks;
- **Typical questions** with marks: past-paper references and possible school questions;
- **You:** mastery and recent misses.

End with the best next mode (`blurt` when unknown, `quiz` when weak, `drill` when nearly secure).

### `blurt <subject> <topic>`
1. `topic`, then pick the section to learn. Tell the student which section to read (id and title), and to close it when done.
2. Ask them to write everything they remember: definitions, chains, diagram labels, examples, quotes.
3. `read` the section and mark against it: what was correct, what was **missing** (most important first) and what was **wrong**.
4. Ask three questions on the missing items and mark those too.
5. `log` with score = key points recalled out of key points, and an error for each wrong or important missing point.

### `quiz <subject> <topic>`
1. `topic` for objectives, traps and past questions; `search(…, kind="papers")` for real question wording.
2. Set five to eight questions in the subject's real format (see [marking.md](marking.md)), one at a time.
3. Mark each with the subject's mark rules and give the score and the fix.
4. One `log` at the end: total score, out of, and one error per lost mark (`what`, `fix`, `type`, `source` id). Finish with the one habit to change.

### `paper <subject> [topic]`
1. Find a real question: `search("<topic> question", subject, kind="papers")`, then `read` the page. Prefer school papers (Maths term exams and common tests, English past papers, the Geography Term 2 paper, the Business 2018 specimen). Otherwise write an IGCSE-style question from the notes. Say which source you used.
2. Give the question, the marks and a time limit of about a minute per mark (1.5 for Economics and Business essays). Ask them to say when they start and finish.
3. Mark against the mark scheme (`search` the same paper's scheme, `kind="papers"`) or the notes. Show the marks line by line and what a full-mark answer adds.
4. `log` the score and every lost mark.

### `drill [subject] [topic]`
Works without Anki. The server picks items; you run the loop.
1. `drill(subject, topic, n=10)`. Each item has an id, Q, A and maybe a hint.
2. Show one question (cloze blanks show as `[…]`). Never show the answer first; give the hint only if asked.
3. Grade: **ok** (key terms right, unaided), **shaky** (partly right, slow or needed the hint), **miss**. After shaky or miss, give the answer in one line.
4. Re-ask each miss after about three other items, until it is right (at most three tries).
5. Every five answers and at the end, `log(subject, topic, "drill", reviews=[{id, grade}, …])`, including re-asks in the order they happened.
6. Finish with the score, the items missed, and any leeches the log reports (offer to `explain` them). Offer another batch.

Items with ids starting `ERR/` are the student's own past mistakes: ask for the correct version.

### `cards <deck>`
Anki review through anki-mcp (needs Anki open). `get_due_cards` for the deck, then `present_card` with the question only. Wait for the answer, show the answer, suggest a rating and let the student confirm before `rate_card`. Report how many were reviewed and which were missed. If anki-mcp is not connected, offer `drill` instead.

### `errors <subject>`
`plan(subject)` for the error types, then `drill(subject, focus="missed")` and run the drill loop on them. If the same mistake appears three or more times, offer to add an Anki card for it to that subject's `0 …` deck; call `add_note` only if the student says yes.

## Rules

- **Consolidate only within two days of a subject's exam:** no new topics; errors, traps and drill on what has been seen. `plan` and `drill` already follow this.
- **Log everything that was marked.** The error log (`local/progress/<CODE>-errors.md`) is private and gitignored; never copy it into a published file.
- Keep sessions short and active. No long lectures.
- Marking rules for every subject are in [marking.md](marking.md). Read it before marking a quiz, paper or blurt.
