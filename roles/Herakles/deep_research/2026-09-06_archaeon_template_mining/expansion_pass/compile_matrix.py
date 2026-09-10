"""Assemble the 69-entry matrix from the analysts' entry files.

Validates coverage against the inbox rather than trusting the analysts to have
covered it: a missing template is reported by name, not silently dropped. Also
counts what the directive asks to be counted separately -- distinct MECHANISMS
and distinct CAPABILITIES, not just template names.

    python compile_matrix.py
"""
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PROMETHEUS_REPO") or HERE.parents[4])
INBOX = REPO / "archaeon" / "templates" / "inbox"

FIELDS = ("TEMPLATE_ID", "FIELD", "KIND", "QUESTION", "MECHANISM", "CANDIDATE",
          "WORLD", "WHAT_CHANGES", "MEASURED", "INFORMATIVE_FAILURE",
          "SOURCE_CHECK", "SHARED_MECHANISM", "ROUTES", "BLOCKER", "FAITHFUL",
          "REDUCTION")
ROUTE_CODES = ("R-NOW", "R-REPAIR", "R-COMPOSE", "R-EXECUTOR", "R-SUBSTRATE",
               "R-WORLD", "R-BACKEND", "R-ARCH")
ENTRY_RE = re.compile(r"BEGIN_ENTRY\s*(.*?)\s*END_ENTRY", re.S)


def parse_entry(block):
    """Line-oriented with continuations, same shape as the expansion blocks."""
    out, key = {}, None
    for line in block.split("\n"):
        m = re.match(r"^\s*([A-Z_]+):\s*(.*)$", line)
        if m and m.group(1) in FIELDS:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def main():
    entries, seen = [], {}
    for p in sorted(HERE.glob("entries_*.txt")):
        text = io.open(p, encoding="utf-8", errors="replace").read()
        for b in ENTRY_RE.findall(text):
            e = parse_entry(b)
            if not e.get("TEMPLATE_ID"):
                continue
            e["_src"] = p.name
            tid = e["TEMPLATE_ID"].strip()
            if tid in seen:
                print("DUPLICATE entry for %s (%s and %s)"
                      % (tid, seen[tid], p.name))
            seen[tid] = p.name
            entries.append(e)

    want = {p.stem for p in INBOX.glob("*.json")}
    got = {e["TEMPLATE_ID"].strip() for e in entries}
    missing = sorted(want - got)
    extra = sorted(got - want)

    print("entry files read ........ %d" % len(list(HERE.glob('entries_*.txt'))))
    print("entries parsed .......... %d" % len(entries))
    print("templates in inbox ...... %d" % len(want))
    print("covered ................. %d" % len(got & want))
    print("MISSING ................. %d" % len(missing))
    for m in missing:
        print("    missing: %s" % m)
    for x in extra:
        print("    entry for a template not in the inbox: %s" % x)

    incomplete = [(e["TEMPLATE_ID"], f) for e in entries for f in FIELDS
                  if not e.get(f)]
    if incomplete:
        print("incomplete fields ....... %d" % len(incomplete))
        for tid, f in incomplete[:15]:
            print("    %s missing %s" % (tid, f))

    # ---- the counts the directive asks for, kept separate
    mech = Counter(e.get("SHARED_MECHANISM", "?").strip().lower()
                   for e in entries)
    def _grade(e):
        raw = (e.get("SOURCE_CHECK") or "").split()
        if not raw:
            return "?"
        return re.sub("[^A-Za-z]", "", raw[0]).upper() or "?"
    src = Counter(_grade(e) for e in entries)
    routes = Counter()
    first_route = Counter()
    for e in entries:
        rs = [r.strip().upper() for r in
              re.split(r"[,\s]+", e.get("ROUTES", "")) if r.strip()]
        rs = [r for r in rs if r in ROUTE_CODES]
        for r in rs:
            routes[r] += 1
        if rs:
            first_route[rs[0]] += 1

    print()
    print("DISTINCT MECHANISMS ..... %d  (across %d templates)"
          % (len(mech), len(entries)))
    print("SOURCE CHECK ............ " + ", ".join(
        "%s=%d" % kv for kv in sorted(src.items())))
    print()
    print("ROUTES, counting every route named:")
    for r in ROUTE_CODES:
        print("    %-12s %3d" % (r, routes.get(r, 0)))
    print("ROUTES, counting only the PREFERRED route per template:")
    for r in ROUTE_CODES:
        print("    %-12s %3d" % (r, first_route.get(r, 0)))
    print()
    print("Mechanisms shared by 2+ templates (the cross-discipline duplicates):")
    bym = defaultdict(list)
    for e in entries:
        bym[e.get("SHARED_MECHANISM", "?").strip().lower()].append(
            (e["TEMPLATE_ID"], e.get("FIELD", "?")))
    for m, group in sorted(bym.items(), key=lambda kv: -len(kv[1])):
        if len(group) > 1:
            print("    %-34s %d: %s" % (m, len(group),
                  ", ".join(g[1][:22] for g in group)))

    # ---- write the matrix
    entries.sort(key=lambda e: e["TEMPLATE_ID"])
    out = ["# The 69-entry matrix", "",
           "One entry per PROPOSED template. Produced by six analysts against",
           "`ANALYST_BRIEF.md`, compiled by `compile_matrix.py`, coverage",
           "validated against the inbox rather than assumed.", "",
           "Route codes: R-NOW executable now; R-REPAIR needs parameters;",
           "R-COMPOSE several specs plus downstream analysis; R-EXECUTOR new",
           "executor or adapter; R-SUBSTRATE new substrate capability; R-WORLD",
           "new world or organism; R-BACKEND external backend the engine",
           "orchestrates; R-ARCH different architecture.", "", "---", ""]
    for e in entries:
        out.append("## %s" % e["TEMPLATE_ID"])
        out.append("")
        out.append("**Field:** %s  **Kind:** %s  **Mechanism tag:** `%s`"
                   % (e.get("FIELD", "?"), e.get("KIND", "?"),
                      e.get("SHARED_MECHANISM", "?")))
        out.append("")
        for f in ("QUESTION", "MECHANISM", "CANDIDATE", "WORLD",
                  "WHAT_CHANGES", "MEASURED", "INFORMATIVE_FAILURE",
                  "SOURCE_CHECK", "ROUTES", "BLOCKER", "FAITHFUL",
                  "REDUCTION"):
            if e.get(f):
                out.append("**%s:** %s" % (f.replace("_", " ").title(),
                                           e[f]))
                out.append("")
        out.append("---")
        out.append("")
    io.open(HERE / "MATRIX.md", "w", encoding="utf-8", newline="").write(
        "\n".join(out))
    json.dump(entries, io.open(HERE / "MATRIX.json", "w", encoding="utf-8"),
              indent=1)
    print()
    print("wrote MATRIX.md and MATRIX.json")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
