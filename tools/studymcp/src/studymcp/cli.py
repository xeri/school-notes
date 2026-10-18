"""studymcp command line.

    studymcp serve                 run the MCP server on stdio (what .mcp.json starts)
    studymcp serve --http 8765     streamable HTTP for claude.ai via a tunnel (see README)
    studymcp search "longshore drift" [--subject geo] [--kind notes]
    studymcp read ECQ/markets#conditions-of-demand
    studymcp session [subject] [focus words] [--sweep]
    studymcp carryover <subject>   the rolling note the next session starts from
    studymcp prep <subject> <topic>            input for building a topic's bank (prep.md)
    studymcp bank [subject] [--flags]          bank status: built / stale / missing per topic
    studymcp bank --save <subject> <topic>     validate a draft and move it into the bank
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
    sv = sub.add_parser("serve")
    sv.add_argument("--http", type=int, metavar="PORT", help="streamable HTTP on 127.0.0.1:PORT instead of stdio")
    s = sub.add_parser("search")
    s.add_argument("query", nargs="+")
    s.add_argument("--subject")
    s.add_argument("--kind", default="all")
    s.add_argument("--limit", type=int, default=8)
    r = sub.add_parser("read")
    r.add_argument("id")
    r.add_argument("--part", type=int, default=1)
    se = sub.add_parser("session")
    se.add_argument("words", nargs="*")
    se.add_argument("--sweep", action="store_true")
    co = sub.add_parser("carryover")
    co.add_argument("subject")
    pr = sub.add_parser("prep")
    pr.add_argument("subject")
    pr.add_argument("topic")
    pr.add_argument("--thin", action="store_true", help="also rebuild ideas with too few statements")
    bk = sub.add_parser("bank")
    bk.add_argument("subject", nargs="?")
    bk.add_argument("--flags", action="store_true")
    bk.add_argument("--save", nargs=2, metavar=("SUBJECT", "TOPIC"))
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
        return run(a.http)

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
    elif a.cmd == "session":
        out = st.session(" ".join(a.words) or None, sweep=a.sweep)
    elif a.cmd == "carryover":
        st.ready()
        code, err = st.subject_or_error(a.subject)
        out = err or st.carryover(code) or "(no history yet)"
    elif a.cmd == "prep":
        out = st.prep(a.subject, a.topic, a.thin)
    elif a.cmd == "bank":
        out = st.bank_save(*a.save) if a.save else st.bank_status(a.subject, a.flags)
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
