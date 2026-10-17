"""A tiny fixture repo with the awkward formats the real one has."""

import textwrap

import pytest

from studymcp import config
from studymcp.tools import Study

FILES = {
    "STUDY-PLAN.md": """
        # Exam overview and priorities: Term 4 Pre-Q 2026

        ## The exams

        | Exam | Date | Format | Start here |
        |---|---|---|---|
        | Mathematics | Tue 27 Oct, morning | one 3h paper, 180 marks | x |
        | Geography | Wed 4 Nov, morning | 3h, sections A–D | x |
        """,
    "T4-MAQ/SYLLABUS.md": """
        # Mathematics — Pre-Q Syllabus

        **Final exam.** One paper, 3 hours, 180 marks.

        | Term | Content | Notes |
        |---|---|---|
        | 1 | Algebra | [Algebra](notes/algebra.md) |

        | # | Topic | Codes | Notes | Cards |
        |---|---|---|---|---|
        | 0a | Exam errors | — | [notes](notes/exam-errors.md) | [deck](anki/exam-errors.txt) |
        | 2 | Algebra | E2.1–2.8 | [notes](notes/algebra.md) | [deck](anki/algebra.txt) |
        | 3 | Graphs | E2.9–2.11, E5 | [notes](notes/graphs.md) | [deck](anki/graphs.txt) |

        ## 2. Algebra

        - **E2.1** Use letters for generalised numbers.
        - **E2.9** Interpret travel graphs.
        """,
    "T4-MAQ/FORMULAS.md": """
        # Formulas

        ## Quadratics

        $$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$
        """,
    "T4-MAQ/notes/algebra.md": """
        # Algebra

        ## Quadratics — factorising and the formula

        A **quadratic** is an expression in $x^2$. The quadratic formula (QF) solves any quadratic.

        $$
        x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}
        $$

        **This loses marks:** forgetting the $\\pm$.

        ## Quadratics — factorising and the formula

        Duplicate heading on purpose.
        """,
    "T4-MAQ/notes/graphs.md": "# Graphs\n\n## Travel graphs\n\nGradient is speed.\n",
    "T4-MAQ/notes/exam-errors.md": "# Exam errors\n\n## Rounding\n\nGive 3 s.f. (2023 Q6(a)(v)).\n",
    "T4-MAQ/notes/study-guide.md": """
        # Maths study guide

        ## The exam

        One paper.

        ## Priority order

        | # | Study | Why here | How |
        |---|---|---|---|
        | 1 | [Exam errors](../notes/exam-errors.md) | Your main weakness | Read it |
        | 2 | [Algebra](algebra.md) | Most marks | Past papers |

        ## Topic checklist

        | Tier | Topic | Notes | Cards | Done |
        |---|---|---|---|---|
        | Start | Exam errors | [notes](../notes/exam-errors.md) | [deck](../anki/exam-errors.txt) | ☐ |
        | **2** | Graphs | [notes](../notes/graphs.md) | [deck](../anki/graphs.txt) | ☐ |
        """,
    "T4-MAQ/anki/algebra.txt": (
        "#separator:tab\n#html:true\n#notetype column:1\n#deck:Mathematics::2 Algebra\n#tags:maths algebra\n"
        "Pre-Q Basic\tQuadratic formula?\t\\(x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}\\)\tMinus b\n"
        "Pre-Q Cloze\tDiscriminant {{c1::b² − 4ac}}; real roots if {{c2::≥ 0}}\t<i>two</i> blanks<br>check\t\n"
        "Pre-Q Basic\t\"Solve\" demands?\tworking &amp; answer\t\n"
    ),
    "T4-MAQ/anki/graphs.txt": "#separator:tab\n#deck:Mathematics::3 Graphs\nPre-Q Basic\tGradient of distance-time?\tSpeed\t\n",
    "T4-MAQ/anki/exam-errors.txt": "#separator:tab\n#deck:Mathematics::0 Errors\nPre-Q Basic\tDefault accuracy?\t3 s.f.\t\n",
    "T4-GEQ/SYLLABUS.md": """
        # Geography — Pre-Q Syllabus

        ## Term 4 examination, 2026 format

        Four sections.

        ## Pages and decks

        | Deck | Page | Notes | Cards |
        |---|---|---|---|
        | **Theme 1: Natural Environment** | | | |
        | 25 | Coasts | [notes](notes/coasts.md) | [deck](anki/coasts.txt) |
        | 23 | Rivers | [notes](notes/rivers.md) | [deck](anki/rivers.txt) |

        ## Theme 1: Natural Environment
        **1.3 Weathering and erosion**
        - [Rivers](notes/rivers.md): erosion processes in rivers.
        - [Coasts](notes/coasts.md): waves and coastal landforms.
        """,
    "T4-GEQ/TERMS.md": "# Glossary\n\n**Hydraulic action** — erosion by the force of water in cracks.\n",
    "T4-GEQ/notes/coasts.md": """
        # Coasts

        ## Waves

        **Wave** = energy transferred through water by wind.

        | | Constructive | Destructive |
        |---|---|---|
        | Frequency | 6–8 a minute | 10–14 a minute |

        ![Wave types with swash and backwash](geo-wave-types.svg)

        ## This loses marks

        - Spit without the change in coastline direction.
        """,
    "T4-GEQ/notes/rivers.md": "# Rivers\n\n## Erosion\n\nHydraulic action, abrasion, attrition.\n",
    "T4-GEQ/notes/study-guide.md": """
        # Geography study guide

        ## The paper

        Three hours.

        ## Priority order

        | Rank | Page or task | Why it is here | How |
        |---|---|---|---|
        | 1 | [Coasts](../notes/coasts.md) | Section A is 50 marks | draw it |

        ## Topic checklist

        | ☐ | Topic | Section | Tier | Notes | Deck |
        |---|---|---|---|---|---|
        | ☐ | Rivers | A | 2 | [notes](../notes/rivers.md) | [23](../anki/rivers.txt) |
        """,
    "T4-GEQ/anki/coasts.txt": "#separator:tab\n#deck:Geography::25 Coasts\nPre-Q Cloze\tLongshore drift: swash {{c1::at an angle}}\t\t1 blank\n",
    "T4-GEQ/anki/rivers.txt": "#separator:tab\n#deck:Geography::23 Rivers\nPre-Q Basic\tAttrition?\tRocks knock together\t\n",
    "local/extracted/GEQ/GEQ-F001.md": """
        # GEQ-F001

        Local extraction only; not a verified transcription. Source: `sources/assessment/2024/term-2/question-papers/Geo T2.pdf`

        ## Page 1

        Q3 Explain how longshore drift forms a spit. [4]

        ## Page 2

        Q4 Describe a wave-cut platform.   [3]
        """,
    "local/extracted/GEQ/GEQ-F002.md": """
        # GEQ-F002

        Local extraction only; not a verified transcription. Source: `sources/assessment/2024/term-2/question-papers/Geo T2 copy.pdf`

        ## Page 1

        Q3 Explain how longshore drift forms a spit. [4]
        """,
}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for rel, text in FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        body = text if "\t" in text else textwrap.dedent(text).lstrip("\n")
        p.write_text(body, encoding="utf-8", newline="\n")
    monkeypatch.setenv("STUDY_ROOT", str(tmp_path))
    monkeypatch.delenv("STUDY_PROGRESS", raising=False)
    return tmp_path


@pytest.fixture
def study(repo):
    return Study(config.load(repo)).ready()
