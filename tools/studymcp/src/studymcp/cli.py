"""studymcp command line.

    studymcp serve                 run the MCP server on stdio (what .mcp.json starts)
    studymcp search "longshore drift" [--subject geo] [--kind notes]
    studymcp read ECQ/markets#conditions-of-demand
    studymcp topic econ ped
    studymcp drill [subject] [topic] [--n 10] [--focus missed]
    studymcp plan [subject]
    studymcp brief [--hook]        session-start brief (--hook prints SessionStart JSON)
    studymcp doctor                check parsing and links after big edits
"""

import argparse
import json
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(prog="studymcp", description="Pre-Q study MCP server and tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve")
    s = sub.add_parser("search")
    s.add_argument("query", nargs="+")
    s.add_argument("--subject")
    s.add_argument("--kind", default="all")
    s.add_argument("--limit", type=int, default=8)
    r = sub.add_parser("read")
    r.add_argument("id")
    r.add_argument("--part", type=int, default=1)
    t = sub.add_parser("topic")
    t.add_argument("words", nargs="+")
    d = sub.add_parser("drill")
    d.add_argument("words", nargs="*")
    d.add_argument("--n", type=int, default=10)
    d.add_argument("--focus", default="auto")
    p = sub.add_parser("plan")
    p.add_argument("subject", nargs="?")
    b = sub.add_parser("brief")
    b.add_argument("--hook", action="store_true")
    sub.add_parser("doctor")
    a = ap.parse_args(argv)

    if a.cmd == "serve":
        from .server import run
        return run()

    sys.stdout.reconfigure(encoding="utf-8")
    from .tools import Study
    st = Study()
    if a.cmd == "brief":
        try:
            text = st.brief()
        except Exception as exc:  # never break session start
            text = f"study brief unavailable: {exc}"
        if a.hook:
            print(json.dumps({"systemMessage": text,
                              "hookSpecificOutput": {"hookEventName": "SessionStart",
                                                     "additionalContext": "Study brief (studymcp):\n" + text}}))
        else:
            print(text)
        return
    if a.cmd == "search":
        out = st.search(" ".join(a.query), a.subject, a.kind, a.limit)
    elif a.cmd == "read":
        out = st.read(a.id, a.part)
    elif a.cmd == "topic":
        out = st.topic(" ".join(a.words))
    elif a.cmd == "drill":
        out = st.drill(" ".join(a.words) or None, None, a.n, a.focus)
    elif a.cmd == "plan":
        out = st.plan(a.subject)
    else:
        out = st.doctor()
    print(out)


if __name__ == "__main__":
    main()
