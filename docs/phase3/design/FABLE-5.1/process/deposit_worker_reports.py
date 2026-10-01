"""Deposit the salvage workers' final messages from the session transcript.

The workers' own transcript files were empty on this host, so the only record
of what they reported is the coordinator's session transcript (a JSONL file
outside the repository). This script reads it, takes the LAST message each
worker sent, and writes it under salvage_reports/ with a header.

What it changes in the text: XML escapes from the notification wrapper are
undone, trailing whitespace is stripped, and one sentence in report 04 is
replaced by a redaction marker. Nothing else. It refuses non-ASCII text.

It also checks the three reports that were deposited by hand (01, 02, 03)
against the transcript, line by line, and prints what differs.

    python deposit_worker_reports.py <transcript.jsonl>          # check 01-03, write 04-07
    python deposit_worker_reports.py <transcript.jsonl> --check  # write nothing
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "salvage_reports"
RULE = "-" * 70

# summary text in the notification -> (file name, scope number, title, brief file)
SCOPES = {
    "Salvage facts: program substrates": ("01_program_substrates.md", 1, "program-like organism substrates",
                                          "01_SCOPE_program_substrates.md"),
    "Salvage facts: other substrates": ("02_other_substrates.md", 2, "non-program substrates and designed learners",
                                        "02_SCOPE_other_substrates.md"),
    "Salvage facts: world machinery": ("03_worlds.md", 3, "world machinery", "03_SCOPE_worlds.md"),
    "Salvage facts: qualification instruments": ("04_qualification_instruments.md", 4,
                                                 "qualification instruments and failure fixtures",
                                                 "04_SCOPE_qualification_instruments.md"),
    "Salvage facts: causal instruments": ("05_causal_instruments.md", 5,
                                          "causal, lineage and intervention instruments",
                                          "05_SCOPE_causal_instruments.md"),
    "Salvage facts: infrastructure": ("06_infrastructure.md", 6, "infrastructure", "06_SCOPE_infrastructure.md"),
    "Salvage facts: search machinery": ("07_search_machinery.md", 7, "search, evolution and generation machinery",
                                        "07_SCOPE_search_machinery.md"),
}
HAND_COPIED = {1, 2, 3}

# Report 04 describes, in one sentence, the fields of a row of a holdout file
# that one of the worker's searches printed. The description is kept out of
# tracked files. The sentence is matched by its fixed opening and its end.
REDACT_OPEN = "It is a JSON row with "
REDACT_MARK = ("[REDACTED at deposit by Dionysus: one sentence in which the worker described the fields of the "
               "row it saw. See 00_SEARCH_RULE_INCIDENT.md.]")


def notifications(path):
    """Yield (timestamp, summary, result_text, usage) for each distinct agent notification, in order."""
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if obj.get("type") != "queue-operation":
                continue
            c = obj.get("content")
            if not isinstance(c, str) or "<task-notification>" not in c or c in seen:
                continue
            seen.add(c)
            m_sum = re.search(r"<summary>Agent \"(.*?)\" finished</summary>", c)
            m_res = re.search(r"<result>(.*)</result>", c, re.S)
            if not (m_sum and m_res):
                continue
            usage = {}
            for key in ("subagent_tokens", "tool_uses", "duration_ms"):
                m = re.search(r"<%s>(\d+)</%s>" % (key, key), c)
                if m:
                    usage[key] = int(m.group(1))
            yield obj.get("timestamp"), m_sum.group(1), html.unescape(m_res.group(1)), usage


def clean(text):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    out = "\n".join(lines) + "\n"
    bad = sorted({ch for ch in out if ord(ch) > 127})
    if bad:
        raise SystemExit("non-ASCII characters in a worker message: %r" % bad)
    return out


def redact(text):
    n = 0
    out = []
    for ln in text.split("\n"):
        i = ln.find(REDACT_OPEN)
        if i >= 0 and "holdout" in ln:
            ln = ln[:i] + REDACT_MARK
            n += 1
        out.append(ln)
    return "\n".join(out), n


def header(scope, title, brief, ts, earlier, usage, redactions):
    mins = usage.get("duration_ms", 0) / 60000.0
    h = ["# Salvage worker report: scope %d, %s" % (scope, title), ""]
    h += ["Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. Extracted by script",
          "(process/deposit_worker_reports.py) from the coordinator's session transcript:",
          "the worker's final message, recorded %s. The text is the worker's," % ts,
          "unchanged except that XML escapes from the notification wrapper are undone",
          "and trailing whitespace is stripped%s." % (
              "; one sentence is redacted (see the note below)" if redactions else ""), ""]
    if earlier:
        h += ["The same worker sent an earlier message (%s). This one" % ", ".join(earlier),
              "replaced it after the coordinator's search-rule correction. The earlier text",
              "is not deposited.", ""]
    h += ["Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and",
          "%s. Worker model: opus, read-only." % brief,
          "Worker usage as reported by the harness: %s tokens, %d tool uses, about" % (
              format(usage.get("subagent_tokens", 0), ","), usage.get("tool_uses", 0)),
          "%.1f minutes (totals for the worker, all messages)." % mins, ""]
    if redactions:
        h += ["Redaction. One of this worker's searches printed one line of a holdout file",
              "(the brief's exclusion pattern covered directories only; the fault is the",
              "coordinator's). The worker reported it and described the row in one sentence.",
              "That sentence is replaced below by a marker so the description does not enter",
              "a tracked file. Path and line number are kept. See 00_SEARCH_RULE_INCIDENT.md.", ""]
    h += ["This is a worker's fact sheet. Its claims are the worker's, graded by its own",
          "VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.", "", RULE, ""]
    return "\n".join(h) + "\n"


def compare_hand_copy(name, transcript_text):
    """Line-level comparison of a hand-copied deposit with the transcript text."""
    path = OUT / name
    body = path.read_text(encoding="utf-8").split(RULE + "\n", 1)[1]
    norm = lambda s: re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()
    want = [norm(x) for x in transcript_text.split("\n") if norm(x) and not norm(x).startswith("===")]
    have = [norm(x) for x in body.split("\n") if norm(x)]
    have_set, want_set = set(have), set(want)
    missing = [x for x in want if x not in have_set]
    extra = [x for x in have if x not in want_set]
    print("%s: transcript lines %d, deposited lines %d, missing from deposit %d, only in deposit %d" % (
        name, len(want), len(have), len(missing), len(extra)))
    for x in missing[:12]:
        print("   MISSING: " + x[:200])
    for x in extra[:12]:
        print("   ONLY IN DEPOSIT: " + x[:200])
    return len(missing), len(extra)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    check_only = "--check" in argv
    by_scope = {}
    for ts, summary, text, usage in notifications(argv[1]):
        if summary in SCOPES:
            by_scope.setdefault(summary, []).append((ts, text, usage))
    if set(by_scope) != set(SCOPES):
        print("missing notifications for: %s" % sorted(set(SCOPES) - set(by_scope)))
        return 1
    rc = 0
    for summary, (name, scope, title, brief) in sorted(SCOPES.items(), key=lambda kv: kv[1][1]):
        msgs = by_scope[summary]
        ts, text, usage = msgs[-1]
        earlier = [m[0] for m in msgs[:-1]]
        text = clean(text)
        if scope in HAND_COPIED:
            compare_hand_copy(name, text)
            continue
        redactions = 0
        if scope == 4:
            text, redactions = redact(text)
            if redactions != 1:
                print("report 04: expected exactly one redaction, made %d" % redactions)
                rc = 1
        doc = header(scope, title, brief, ts, earlier, usage, redactions) + text
        print("%s: %d lines, %d characters, messages from this worker %d, redactions %d" % (
            name, doc.count("\n"), len(doc), len(msgs), redactions))
        if not check_only:
            (OUT / name).write_text(doc, encoding="ascii", newline="\n")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
