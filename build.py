#!/usr/bin/env python3
"""Build the GitHub wiki and the offline PDFs from the subject folders.

    python build.py wiki            regenerate wiki/ from the subject folders
    python build.py push-wiki       regenerate, then push wiki/ to the GitHub wiki
    python build.py pdf             build pdf/<SUBJECT>.pdf for every subject
    python build.py pdf PHQ MAQ     build only those subjects

Each subject folder holds SYLLABUS.md, notes/*.md, anki/*.txt and optional
reference files. Reading order comes from the links in SYLLABUS.md, so the
syllabus is the single place that defines sequence.
"""

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

REPO = "https://github.com/mr-enderman280/school-notes"


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
        r"\]\((?:\.\./)?notes/([A-Za-z0-9_-]+)\.md\)",
        lambda m: f"]({page_name(subject, m.group(1))})",
        text,
    )
    # FORMULAS.md / TERMS.md / ...  ->  Physics-Formulas
    text = re.sub(
        r"\]\((?:\.\./)?([A-Z][A-Z-]*)\.md\)",
        lambda m: f"]({page_name(subject, m.group(1).lower())})",
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

    sidebar = ["### Subjects", ""]
    home = [
        "# School study notes",
        "",
        "Pre-Q syllabuses and revision notes for six subjects. Each subject has one",
        "syllabus page listing every assessed objective, a notes page per topic, and",
        "an Anki deck per topic for the rote learning.",
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
        for stem in topics:
            title = note_title(d / "notes" / f"{stem}.md", stem)
            sidebar.append(f"- [{title}]({page_name(subject, stem)})")
        for ref in refs:
            sidebar.append(f"- [{ref.stem.title()}]({page_name(subject, ref.stem.lower())})")
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


def write_page(name, text):
    (WIKI / f"{name}.md").write_text(text, encoding="utf-8")


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

def main():
    args = sys.argv[1:] or ["wiki"]
    cmd, rest = args[0], [a.upper() for a in args[1:]]
    if cmd == "wiki":
        build_wiki()
    elif cmd == "push-wiki":
        push_wiki()
    elif cmd == "pdf":
        build_pdf(rest or list(SUBJECTS))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
