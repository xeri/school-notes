# Prep a topic for the study bank

You are building the study bank for one topic: the plain gists and true/false statements that `/study` sessions use. You run in the background; the student never sees this. Work from the repo root.

## Steps

1. Get the input:
   ```bash
   uv run --quiet --frozen --project tools/studymcp studymcp prep <CODE> <stem>
   ```
   Add `--thin` to also rebuild ideas that have fewer statements than their notes deserve. It prints the file to write, the topic's priority, syllabus objectives, traps and past-paper hits (a section says "none" when the topic has none), then each idea that needs building: id, how many statements it needs, possible links and the full notes text. The folder `local/bank/<CODE>/` is created when you write the draft.
2. Read it all and think it through before writing: what each idea really says, what the exam asks about it, and where students go wrong.
3. Write the draft to `local/bank/<CODE>/<stem>.draft.json` (format below). On a partial rebuild, include only the ideas listed.
4. Save it:
   ```bash
   uv run --quiet --frozen --project tools/studymcp studymcp bank --save <CODE> <stem>
   ```
   It validates the draft, stamps it and moves it into place. If it prints errors, fix the draft and run it again until it says `saved`. Fix every warning you can: each one names a real weakness.
5. Reply with one line: `<CODE>/<stem>: N ideas, M flags`.

## Format

```json
{
  "ideas": {
    "ECQ/markets#conditions-of-demand": {
      "gist": "Demand shifts when something other than the good's own price changes: income, tastes, related goods, expectations.",
      "weight": "high",
      "statements": [
        {"text": "A rise in income shifts demand for a normal good to the right.", "true": true},
        {"text": "A rise in income shifts supply of a normal good to the right.", "true": false,
         "fix": "Income shifts demand, not supply.", "change": "close terms"}
      ],
      "mixups": ["shift of demand vs movement along it"],
      "links": ["ECQ/elasticity-failure#income-elasticity", "BUQ/marketing#pricing-methods"]
    }
  },
  "flags": ["ECQ/markets#x: no example of a complement"]
}
```

## Rules

- **gist:** what the idea says is true, in plain words a 15-year-old would follow, at most 200 characters. It states the content ("Waves erode cliffs by hydraulic action and abrasion"), never the layout of the notes ("A table of erosion processes"). Not the first sentence of the notes.
- **weight:** `high`, `medium` or `low`: how much the exam leans on this idea compared with the rest of the topic, judged from the objectives and past-paper hits. About a third of a topic's ideas are high. Practice sets, worked models and index pages that repeat other topics are medium or low.
- **statements:** at least the number the prep output gives for each idea (4 for a short one, more for a long one, at most 16), about half false, in no pattern.
  - Together they cover the idea's main points, spread across the whole of its notes, not one corner.
  - Each tests one point and is one short sentence (under about 20 words) a student could judge in a few seconds.
  - Each states the subject, never the notes: "Forced migration mostly harms the migrants", not "The plan argues that…".
  - A true statement must be exactly supported by the notes. Phrase it positively where you can: a "not" in a true statement is easy to misremember as its opposite.
  - A false statement has exactly one believable change, the kind a real student makes, and the fix word or two that would make it true should be clear. `change` is one of: direction, cause and effect, close terms, number, condition, always, people and places, missing link. Prefer the topic's traps.
  - True and false statements look alike: similar length and tone; "only", "always" and "never" appear in true ones too.
  - The same thing gets the same word throughout, the notes' own term.
  - `fix` is one line that states the right version in full.
  - Exam-specific facts (quotes, figures, case details, named places) come only from the notes. English quotes stay word for word in true statements; in a false one change exactly one word of the quote and keep everything around it true, so the word is the only error.
- **By subject:** each subject's statements feed the method the student uses for it.
  - Geography: pair a concept with a case ("Cyclone Gabrielle shows how ex-tropical cyclones…"). False ones swap the place, the figure or the process.
  - Business: most statements apply an idea to a business or give its consequence ("For a bakery with inelastic demand, a price rise raises revenue"). A bare definition only where the exam asks for one.
  - Economics: which curve shifts which way, and one link in a chain. False ones flip a direction, swap cause and effect, or drop a link.
  - English: a quote with its speaker, act or film moment and the point it makes for a theme. False ones change one word, the speaker or the act.
  - Maths: the first step or method for a type of problem, and when a rule applies. False ones change a sign, a condition or a rearrangement.
  - Physics: which formula or principle fits a situation, and its units. False ones swap a unit, a prefix or a rearrangement.
- **mixups:** up to 3 short pairs students confuse with this idea.
- **links:** 1–3 ids of closely related ideas, from this subject or a paired one (Economics ↔ Business, Economics ↔ Geography, Maths ↔ Physics). Use `search` or the `prep` output to find real ids; never invent one.
- **flags:** only for notes that are thin, unclear or contradict each other. One line each, starting with the idea id. They are saved for the notes' author and never shown in a session.

Don't edit any other file.
