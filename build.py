#!/usr/bin/env python3
"""Build the GitHub wiki and the offline PDFs from the subject folders.

    python build.py wiki            regenerate wiki/ from the subject folders
    python build.py push-wiki       regenerate, then push wiki/ to the GitHub wiki
    python build.py pdf             build pdf/<SUBJECT>.pdf for every subject
    python build.py pdf PHQ MAQ     build only those subjects
    python build.py stats           refresh the README badges, stats card and subject table

Each subject folder holds SYLLABUS.md, notes/*.md, anki/*.txt and optional
reference files. Reading order comes from the links in SYLLABUS.md, so the
syllabus is the single place that defines sequence.
"""

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI = ROOT / "wiki"
PDF = ROOT / "pdf"

SUBJECTS = {
    "BUQ": "Business",
    "ECQ": "Economics",
    "ENQ": "English",
    "GEQ": "Geography",
    "MAQ": "Mathematics",
    "PHQ": "Physics",
}

REPO = "https://github.com/xeri/school-notes"


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #

def subject_dir(code):
    return ROOT / f"T4-{code}"


def page_name(subject, stem):
    """wiki page name: Physics + atomic-space -> Physics-Atomic-Space"""
    return subject + "-" + "-".join(w.capitalize() for w in stem.split("-"))


def reading_order(code):
    """notes stems in the order SYLLABUS.md links them, then any unlinked ones."""
    d = subject_dir(code)
    syllabus = d / "SYLLABUS.md"
    order = []
    if syllabus.exists():
        for m in re.finditer(r"notes/([A-Za-z0-9_-]+)\.md", syllabus.read_text(encoding="utf-8")):
            if m.group(1) not in order:
                order.append(m.group(1))
    for f in sorted((d / "notes").glob("*.md")):
        if f.stem not in order:
            order.append(f.stem)
    return [s for s in order if (d / "notes" / f"{s}.md").exists()]


def sidebar_groups(code):
    """[(group, subgroup, stem)] from the SYLLABUS.md index table.

    A row whose first cell is **bold** and has no notes link starts a group;
    an *italic* one starts a subgroup inside it.
    """
    syllabus = subject_dir(code) / "SYLLABUS.md"
    out, group, sub, seen, in_index = [], None, None, set(), False
    if not syllabus.exists():
        return out
    for line in syllabus.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            in_index = False
            continue
        if "Notes" in line and "Cards" in line:
            in_index = True
        if not in_index:
            continue
        first = line.strip("|").split("|")[0].strip()
        stems = re.findall(r"notes/([A-Za-z0-9_-]+)\.md", line)
        if not stems:
            if re.fullmatch(r"\*\*[^*]+\*\*", first):
                group, sub = first.strip("*"), None
            elif re.fullmatch(r"\*[^*]+\*", first):
                sub = first.strip("*")
            continue
        for s in stems:
            if s not in seen:
                seen.add(s)
                out.append((group, sub, s))
    return out


def sidebar_entries(code, subject, topics, refs):
    """nested markdown list for one subject: groups, subgroups, then pages."""
    d = subject_dir(code)
    grouped = {s: (g, sub) for g, sub, s in sidebar_groups(code)}
    # ungrouped pages first, then the table's groups in order
    rows = [(None, None, s) for s in topics if grouped.get(s, (None, None))[0] is None]
    rows += [(g, sub, s) for g, sub, s in sidebar_groups(code) if g and s in topics]
    lines, cur_g, cur_sub = [], None, None
    for g, sub, stem in rows:
        if g != cur_g:
            lines.append(f"- **{g}**")
            cur_g, cur_sub = g, None
        if sub != cur_sub:
            lines.append(f"  - *{sub}*")
            cur_sub = sub
        indent = "  " * ((g is not None) + (sub is not None))
        title = note_title(d / "notes" / f"{stem}.md", stem)
        lines.append(f"{indent}- [{title}]({page_name(subject, stem)})")
    if refs:
        lines.append("- **Reference**")
        for ref in refs:
            lines.append(f"  - [{ref.stem.replace('-', ' ').capitalize()}]({page_name(subject, ref.stem.lower())})")
    return lines


def reference_files(code):
    """subject-specific reference files at the subject root, excluding SYLLABUS."""
    d = subject_dir(code)
    return sorted(f for f in d.glob("*.md") if f.name != "SYLLABUS.md")


# --------------------------------------------------------------------------- #
# wiki
# --------------------------------------------------------------------------- #

def rewrite_links(text, code, subject):
    """turn in-repo relative links into wiki page links and repo blob links."""
    # notes/<stem>.md  ->  Physics-Waves
    text = re.sub(
        r"\]\((?:\.\./)?notes/([A-Za-z0-9_-]+)\.md(#[^)]*)?\)",
        lambda m: f"]({page_name(subject, m.group(1))}{m.group(2) or ''})",
        text,
    )
    # bare sibling links inside notes/: (finance.md) or (finance.md#ratios)
    notes_dir = subject_dir(code) / "notes"
    text = re.sub(
        r"\]\(([a-z0-9][a-z0-9-]*)\.md(#[^)]*)?\)",
        lambda m: f"]({page_name(subject, m.group(1))}{m.group(2) or ''})"
        if (notes_dir / f"{m.group(1)}.md").exists() else m.group(0),
        text,
    )
    # FORMULAS.md / TERMS.md / ...  ->  Physics-Formulas
    text = re.sub(
        r"\]\((?:\.\./)?([A-Z][A-Z-]*)\.md(#[^)]*)?\)",
        lambda m: f"]({page_name(subject, m.group(1).lower())}{m.group(2) or ''})",
        text,
    )
    # anki/<stem>.txt and anki/ -> the deck file in the repo, not a wiki page
    text = re.sub(
        r"\]\((?:\.\./)?anki/([A-Za-z0-9_-]+)\.txt\)",
        lambda m: f"]({REPO}/blob/main/T4-{code}/anki/{m.group(1)}.txt)",
        text,
    )
    text = text.replace("](anki/)", f"]({REPO}/tree/main/T4-{code}/anki)")
    return text


def build_wiki():
    if WIKI.exists():
        for f in list(WIKI.glob("*.md")) + list(WIKI.glob("*.svg")):
            f.unlink()
    WIKI.mkdir(exist_ok=True)

    sidebar = ["**[Study plan](Study-Plan)**", "", "### Subjects", ""]
    plan = ROOT / "STUDY-PLAN.md"
    if plan.exists():
        write_page("Study-Plan", plan.read_text(encoding="utf-8"))
    home = [
        "# School study notes",
        "",
        "Pre-Q syllabuses and revision notes for six subjects. Each subject has one",
        "syllabus page listing every assessed objective, a notes page per topic, and",
        "an Anki deck per topic for the rote learning.",
        "",
        "**Start with the [study plan](Study-Plan)**: exams, priorities, study methods and Anki settings.",
        "",
        "| Subject | Syllabus | Topics | Flashcards |",
        "|---|---|---|---|",
    ]

    for code, subject in SUBJECTS.items():
        d = subject_dir(code)
        if not (d / "SYLLABUS.md").exists():
            continue
        topics = reading_order(code)
        refs = reference_files(code)

        syl_page = page_name(subject, "syllabus")
        home.append(
            f"| {subject} | [{subject} syllabus]({syl_page}) | {len(topics)} | "
            f"[{len(list((d / 'anki').glob('*.txt')))} decks]({REPO}/tree/main/T4-{code}/anki) |"
        )

        sidebar.append(f"**[{subject}]({syl_page})**")
        sidebar.append("")
        sidebar += sidebar_entries(code, subject, topics, refs)
        sidebar.append("")

        # syllabus page
        write_page(
            syl_page,
            rewrite_links((d / "SYLLABUS.md").read_text(encoding="utf-8"), code, subject),
        )

        # reference pages
        for ref in refs:
            write_page(
                page_name(subject, ref.stem.lower()),
                rewrite_links(ref.read_text(encoding="utf-8"), code, subject),
            )

        # topic pages, each with prev/next and a link back to the syllabus
        for i, stem in enumerate(topics):
            body = rewrite_links(
                (d / "notes" / f"{stem}.md").read_text(encoding="utf-8"), code, subject
            )
            nav = [f"[← {subject} syllabus]({syl_page})"]
            if i:
                prev = topics[i - 1]
                nav.append(f"[← {note_title(d / 'notes' / f'{prev}.md', prev)}]({page_name(subject, prev)})")
            if i + 1 < len(topics):
                nxt = topics[i + 1]
                nav.append(f"[{note_title(d / 'notes' / f'{nxt}.md', nxt)} →]({page_name(subject, nxt)})")
            write_page(page_name(subject, stem), body + "\n\n---\n\n" + " · ".join(nav) + "\n")

        # diagrams referenced by the notes live beside them, flat in the wiki
        for svg in (d / "notes").glob("*.svg"):
            shutil.copy(svg, WIKI / svg.name)

    write_page("Home", "\n".join(home) + "\n")
    write_page("_Sidebar", "\n".join(sidebar) + f"\n[Repository]({REPO})\n")
    print(f"wiki: {len(list(WIKI.glob('*.md')))} pages, {len(list(WIKI.glob('*.svg')))} diagrams -> {WIKI}")


def note_title(path, fallback):
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return fallback.replace("-", " ").capitalize()


def github_math(text):
    """protect LaTeX from GitHub's markdown pass.

    GitHub applies markdown escapes before handing $...$ to MathJax, so \\$ and
    \\% inside math are eaten (\\% becomes a TeX comment) and the delimiters
    pair up wrongly. $`...`$ and ```math blocks pass their contents raw.
    """
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        m = re.fullmatch(r"(\s*)\$\$(.+?)\$\$\s*", line)
        if fenced:
            out.append(line)
        elif m:
            out += [f"{m.group(1)}```math", f"{m.group(1)}{m.group(2).strip()}", f"{m.group(1)}```"]
        else:
            out.append(inline_math(line))
    return "\n".join(out)


def inline_math(line):
    """rewrite $...$ as $`...`$, skipping code spans and escaped \\$ outside math."""
    res, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            res.append(line[i:i + 2])
            i += 2
        elif c == "`":
            j = line.find("`", i + 1)
            j = len(line) - 1 if j < 0 else j
            res.append(line[i:j + 1])
            i = j + 1
        elif c == "$":
            j = i + 1
            while j < len(line) and line[j] != "$":
                j += 2 if line[j] == "\\" else 1
            if j >= len(line) or j == i + 1:
                res.append(c)
                i += 1
            else:
                res.append(f"$`{line[i + 1:j]}`$")
                i = j + 1
        else:
            res.append(c)
            i += 1
    return "".join(res)


def write_page(name, text):
    (WIKI / f"{name}.md").write_text(github_math(text), encoding="utf-8")


def push_wiki():
    build_wiki()
    url = REPO + ".wiki.git"
    work = ROOT / ".wiki-clone"
    if work.exists():
        shutil.rmtree(work, onerror=_force_rm)
    fresh = subprocess.run(["git", "clone", url, str(work)]).returncode != 0
    if fresh:
        # GitHub only materialises the wiki repository once it has a page, so on
        # the very first run initialise it locally and push master into being.
        work.mkdir()
        subprocess.run(["git", "init", "-b", "master"], cwd=work, check=True)
        subprocess.run(["git", "remote", "add", "origin", url], cwd=work, check=True)
    for f in list(work.glob("*.md")) + list(work.glob("*.svg")):
        f.unlink()
    for f in list(WIKI.glob("*.md")) + list(WIKI.glob("*.svg")):
        shutil.copy(f, work / f.name)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=work).returncode:
        subprocess.run(["git", "commit", "-m", "Regenerate wiki from subject notes"], cwd=work, check=True)
        push = ["git", "push", "-u", "origin", "master"] if fresh else ["git", "push"]
        if subprocess.run(push, cwd=work).returncode:
            sys.exit(
                "Wiki push rejected. Check that wikis are enabled for the repository:\n"
                f"  gh api repos/<owner>/<repo> --method PATCH -F has_wiki=true\n"
                f"and that {REPO}/wiki is reachable."
            )
        print("wiki pushed")
    else:
        print("wiki already up to date")
    shutil.rmtree(work, onerror=_force_rm)


def _force_rm(func, path, _):
    os.chmod(path, 0o700)
    func(path)


# --------------------------------------------------------------------------- #
# pdf
# --------------------------------------------------------------------------- #

def binary(env, *candidates):
    if os.environ.get(env):
        return os.environ[env]
    for c in candidates:
        p = ROOT / "local" / "toolchain" / c
        if p.exists():
            return str(p)
    found = shutil.which(env.replace("STUDY_", "").lower())
    if found:
        return found
    sys.exit(f"{env} not found. Set {env} to the executable, or keep it under local/toolchain/.")


def build_pdf(codes):
    pandoc = binary("STUDY_PANDOC", "pandoc-3.6.4/pandoc.exe", "pandoc-3.6.4/pandoc")
    typst = binary("STUDY_TYPST", "typst-x86_64-pc-windows-msvc/typst.exe", "typst/typst")
    PDF.mkdir(exist_ok=True)

    for code in codes:
        d = subject_dir(code)
        if not (d / "SYLLABUS.md").exists():
            print(f"{code}: no SYLLABUS.md, skipped")
            continue
        parts = [d / "SYLLABUS.md"]
        parts += reference_files(code)
        parts += [d / "notes" / f"{s}.md" for s in reading_order(code)]

        # Concatenate into one file inside notes/ so that the diagrams, which the
        # notes reference by bare filename, resolve for the PDF engine too.
        merged = d / "notes" / "_merged.md"
        merged.write_text(
            "\n\n\\newpage\n\n".join(strip_repo_links(p.read_text(encoding="utf-8")) for p in parts),
            encoding="utf-8",
        )
        out = PDF / f"{code}.pdf"
        env = dict(os.environ, PATH=str(Path(typst).parent) + os.pathsep + os.environ["PATH"])
        cmd = [
            pandoc, merged.name,
            "-o", str(out),
            "--pdf-engine=typst",
            "--toc", "--toc-depth=2",
            "-V", "papersize=a4",
            "-V", "fontsize=10pt",
            "--metadata", f"title={SUBJECTS[code]} — Pre-Q",
        ]
        r = subprocess.run(cmd, env=env, cwd=merged.parent)
        merged.unlink()
        if r.returncode:
            print(f"{code}: FAILED")
        else:
            print(f"{code}: {out.name}  {out.stat().st_size // 1024} KB  ({len(parts)} sections)")


def strip_repo_links(text):
    """flatten in-repo navigation links to plain text — they mean nothing in a PDF."""
    text = re.sub(r"\[([^\]]+)\]\((?:\.\./)?(?:notes|anki)/[^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\((?:\.\./)?[A-Z][A-Z-]*\.md\)", r"\1", text)
    return text.replace("](anki/)", "")


# --------------------------------------------------------------------------- #
# README stats
# --------------------------------------------------------------------------- #

README = ROOT / "README.md"
STATS_DIR = ROOT / ".github" / "readme"
WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
BADGE_COLOR = "2a78d6"

# the same tokens stepped for each GitHub theme; the README swaps them with <picture>
CARD_THEMES = {
    "light": {"surface": "#fcfcfb", "border": "#e4e3df", "text": "#0b0b0b", "muted": "#52514e", "accent": "#2a78d6"},
    "dark": {"surface": "#1a1a19", "border": "#383835", "text": "#f0efec", "muted": "#c3c2b7", "accent": "#3987e5"},
}


def subject_stats(code):
    """counts for one subject: notes pages, reference sheets, decks, Anki notes, cards, diagrams, words."""
    d = subject_dir(code)
    topics, refs = reading_order(code), reference_files(code)
    decks = sorted((d / "anki").glob("*.txt"))
    notes = cards = 0
    for deck in decks:
        for line in deck.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            kind, text = (line.split("\t") + [""])[:2]
            notes += 1
            # a cloze note makes one card per cloze number
            cards += len(set(re.findall(r"\{\{c(\d+)::", text))) if kind.endswith("Cloze") else 1
    pages = [d / "SYLLABUS.md", *refs, *(d / "notes" / f"{s}.md" for s in topics)]
    return {
        "pages": len(topics),
        "refs": len(refs),
        "decks": len(decks),
        "notes": notes,
        "cards": cards,
        "diagrams": len(list((d / "notes").glob("*.svg"))),
        "words": sum(len(WORD.findall(p.read_text(encoding="utf-8"))) for p in pages),
    }


def compact(n):
    """1,284 · 12.9K · 307K"""
    if n < 10_000:
        return f"{n:,}"
    return f"{n / 1000:.1f}K" if n < 100_000 else f"{round(n / 1000)}K"


def badge(label, value, logo=None, link=None):
    """a static shields.io badge in markdown."""
    q = lambda s: s.replace("-", "--").replace("_", "__").replace(" ", "%20").replace(",", "%2C")
    url = f"https://img.shields.io/badge/{q(label)}-{q(value)}-{BADGE_COLOR}?style=for-the-badge"
    if logo:
        url += f"&logo={logo}&logoColor=white"
    img = f"![{label}: {value}]({url})"
    return f"[{img}]({link})" if link else img


def stats_card(tiles, c):
    """a 3 × 2 grid of stat tiles (label, value, note) as SVG, in one theme's colours."""
    cols, gap, tw, th = 3, 12, 284, 112
    w, h = cols * tw + (cols - 1) * gap, 2 * th + gap
    font = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    summary = "; ".join(f"{label} {value}" for label, value, _ in tiles)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" font-family="{font}">',
        f"<title>{html.escape(summary)}</title>",
    ]
    for i, (label, value, note) in enumerate(tiles):
        x, y = (i % cols) * (tw + gap), (i // cols) * (th + gap)
        out += [
            f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{tw - 1}" height="{th - 1}" rx="12" '
            f'fill="{c["surface"]}" stroke="{c["border"]}"/>',
            f'<rect x="{x + 20}" y="{y + 18}" width="24" height="4" rx="2" fill="{c["accent"]}"/>',
            f'<text x="{x + 20}" y="{y + 42}" font-size="14" fill="{c["muted"]}">{html.escape(label)}</text>',
            f'<text x="{x + 20}" y="{y + 80}" font-size="32" font-weight="600" fill="{c["text"]}">'
            f"{html.escape(value)}</text>",
            f'<text x="{x + 20}" y="{y + 100}" font-size="13" fill="{c["muted"]}">{html.escape(note)}</text>',
        ]
    return "\n".join(out + ["</svg>"]) + "\n"


def write_stats():
    """refresh the generated README blocks and the stats card from the subject folders."""
    per = {code: subject_stats(code) for code in SUBJECTS if (subject_dir(code) / "SYLLABUS.md").exists()}
    tot = {k: sum(s[k] for s in per.values()) for k in next(iter(per.values()))}
    wiki_pages = tot["pages"] + tot["refs"] + len(per) + 1  # + each syllabus and the study plan

    tiles = [
        ("Subjects", str(len(per)), "Term 4 Pre-Q exams"),
        ("Notes pages", f"{tot['pages']:,}", f"plus {tot['refs']} reference sheets"),
        ("Words", compact(tot["words"]), "of notes, syllabi and references"),
        ("Flashcards", f"{tot['cards']:,}", f"from {tot['notes']:,} Anki notes"),
        ("Anki decks", f"{tot['decks']:,}", "tab-separated, ready to import"),
        ("Diagrams", f"{tot['diagrams']:,}", "labelled SVGs"),
    ]
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    for theme, colors in CARD_THEMES.items():
        (STATS_DIR / f"stats-{theme}.svg").write_text(stats_card(tiles, colors), encoding="utf-8")

    rel = STATS_DIR.relative_to(ROOT).as_posix()
    alt = "; ".join(f"{label}: {value} ({note})" for label, value, note in tiles)
    top = "\n".join([
        badge("subjects", str(len(per))),
        badge("notes pages", f"{tot['pages']:,}", "markdown", f"{REPO}/wiki"),
        badge("words", compact(tot["words"])),
        badge("flashcards", f"{tot['cards']:,}", "anki"),
        badge("anki decks", f"{tot['decks']:,}", "anki"),
        badge("diagrams", f"{tot['diagrams']:,}"),
        badge("wiki pages", f"{wiki_pages:,}", "github", f"{REPO}/wiki"),
        "",
        "<picture>",
        f'  <source media="(prefers-color-scheme: dark)" srcset="{rel}/stats-dark.svg">',
        f'  <img alt="{html.escape(alt)}" src="{rel}/stats-light.svg" width="100%">',
        "</picture>",
    ])

    rows = [
        "| Subject | Syllabus | Reference | Notes pages | Flashcards | Diagrams | Words |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for code, s in per.items():
        d = subject_dir(code).relative_to(ROOT).as_posix()
        refs = " · ".join(f"[{r.stem}]({d}/{r.name})" for r in reference_files(code))
        rows.append(f"| {SUBJECTS[code]} | [{d}/SYLLABUS.md]({d}/SYLLABUS.md) | {refs} | "
                    f"{s['pages']} | {s['cards']:,} | {s['diagrams']} | {s['words']:,} |")
    rows.append(f"| **Total** | | | **{tot['pages']}** | **{tot['cards']:,}** | "
                f"**{tot['diagrams']}** | **{tot['words']:,}** |")

    text = README.read_text(encoding="utf-8")
    for name, block in (("stats", top), ("subjects", "\n".join(rows))):
        pattern = re.compile(rf"(<!-- {name}:begin[^>]*-->\n).*?(<!-- {name}:end -->)", re.S)
        if not pattern.search(text):
            sys.exit(f"README.md needs <!-- {name}:begin --> and <!-- {name}:end --> markers")
        text = pattern.sub(lambda m: m.group(1) + block + "\n" + m.group(2), text)
    README.write_text(text, encoding="utf-8")
    print(f"stats: {tot['pages']} pages, {tot['cards']:,} cards in {tot['decks']} decks, "
          f"{tot['diagrams']} diagrams, {tot['words']:,} words -> README.md, {rel}/")


# --------------------------------------------------------------------------- #

def main():
    args = sys.argv[1:] or ["wiki"]
    cmd, rest = args[0], [a.upper() for a in args[1:]]
    if cmd == "wiki":
        build_wiki()
    elif cmd == "push-wiki":
        push_wiki()
    elif cmd == "pdf":
        build_pdf(rest or list(SUBJECTS))
    elif cmd == "stats":
        write_stats()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
