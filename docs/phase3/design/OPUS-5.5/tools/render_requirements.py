"""Validate requirements_data.py and render requirements.jsonl plus the generated tables in REQUIREMENTS.md.

Usage:  python render_requirements.py [--check]
  --check   validate and verify the committed outputs are current; exit 1 on any problem.

Validation (each is a control that can fail; tools/test_render_requirements.py plants a violation of each):
  - unique ids; valid category, priority, gate, enforce, build and op values; ASCII everywhere
  - every failure class in TAXONOMY (Tityos T01-T24, Sisyphus SD1-SD15, Tantalus TD1-TD19, Ixion ID1-ID12) is
    covered by >= 1 requirement whose priority is REQUIRED or REJECTED/AVOID AND whose enforcement is BLOCK or RULE
  - every coverage reference exists and is not WITHDRAWN
  - every REQUIRED requirement with enforce BLOCK names a counterfeit or a test
  - every live requirement names a discriminating test (it is what "falsified if" resolves to)
  - every live SLICE requirement is assigned to exactly one S1 work item, and S1 budgets sum to <= the cap
"""
import json
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)

BEGIN = "<!-- BEGIN GENERATED TABLES (tools/render_requirements.py) -->"
END = "<!-- END GENERATED TABLES -->"
BUILD_MID = {"0": 0, "S": 2.5, "M": 17.5, "L": 65, "XL": 150}  # M tokens processed, midpoint of the band


def load():
    import importlib
    import requirements_data as rd
    return importlib.reload(rd)


def validate(rd):
    errs = []
    ids = [r["id"] for r in rd.R]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errs.append("duplicate ids: %s" % dup)
    cats = {c for c, _ in rd.CATEGORIES}
    by_id = {r["id"]: r for r in rd.R}
    for r in rd.R:
        rid = r["id"]
        if r["cat"] not in cats:
            errs.append("%s: unknown category" % rid)
        if r["pri"] not in rd.PRIORITIES:
            errs.append("%s: bad priority %r" % (rid, r["pri"]))
        if r["pri"] != "WITHDRAWN":
            if not (r["gate"] in rd.GATES_FIXED and r["gate"]) and not r["gate"].startswith("GATE-C:"):
                errs.append("%s: bad gate %r" % (rid, r["gate"]))
            if r["enforce"] not in rd.ENFORCE or not r["enforce"]:
                errs.append("%s: bad enforce %r" % (rid, r["enforce"]))
            if r["pri"] == "REQUIRED" and r["enforce"] == "BLOCK" and not (r["fake"] or r["test"]):
                errs.append("%s: BLOCK requirement with neither counterfeit nor test" % rid)
            if r["gate"] == "SLICE" and r["enforce"] == "BLOCK" and not r["fake"]:
                errs.append("%s: SLICE BLOCK requirement without a counterfeit fixture" % rid)
        if r["build"] not in rd.BUILD:
            errs.append("%s: bad build %r" % (rid, r["build"]))
        if r["op"] not in rd.OP:
            errs.append("%s: bad op %r" % (rid, r["op"]))
        for k, v in r.items():
            if any(ord(ch) > 127 for ch in str(v)):
                errs.append("%s.%s: non-ASCII" % (rid, k))
    for cls in rd.TAXONOMY:
        refs = rd.COVERAGE.get(cls, [])
        if not refs:
            errs.append("class %s (%s) not covered" % (cls, rd.TAXONOMY[cls]))
            continue
        ok = False
        for ref in refs:
            r = by_id.get(ref)
            if r is None:
                errs.append("class %s -> unknown id %s" % (cls, ref))
                continue
            if r["pri"] == "WITHDRAWN":
                errs.append("class %s -> withdrawn id %s" % (cls, ref))
                continue
            if r["pri"] in ("REQUIRED", "REJECTED/AVOID") and r["enforce"] in ("BLOCK", "RULE") and r.get("fake"):
                ok = True
        if not ok:
            errs.append("class %s (%s) has no REQUIRED/REJECTED requirement enforced by BLOCK or RULE with a counterfeit"
                        % (cls, rd.TAXONOMY[cls]))
    for cls in rd.COVERAGE:
        if cls not in rd.TAXONOMY:
            errs.append("coverage key %s not in TAXONOMY" % cls)
    for r in rd.R:
        if r["pri"] != "WITHDRAWN" and not r["test"]:
            errs.append("%s: live requirement without a discriminating test" % r["id"])
    items = getattr(rd, "S1_WORK_ITEMS", None)
    if items is not None:
        seen = {}
        for wid, _title, _budget, refs in items:
            for ref in refs:
                r = by_id.get(ref)
                if r is None or r["pri"] == "WITHDRAWN" or r["gate"] != "SLICE":
                    errs.append("S1 work item %s -> %s is not a live SLICE requirement" % (wid, ref))
                seen.setdefault(ref, []).append(wid)
        for r in rd.R:
            if r["pri"] != "WITHDRAWN" and r["gate"] == "SLICE" and len(seen.get(r["id"], [])) != 1:
                errs.append("%s: SLICE requirement assigned to %d S1 work items (must be exactly 1)"
                            % (r["id"], len(seen.get(r["id"], []))))
        total = sum(b for _w, _t, b, _r in items)
        if total > rd.S1_BUDGET_CAP_M:
            errs.append("S1 work-item budgets sum to %sM, above the %sM cap" % (total, rd.S1_BUDGET_CAP_M))
    return errs


def falsifier_ids():
    path = os.path.join(PKG, "FALSIFIERS.md")
    if not os.path.exists(path):
        return set()
    return set(re.findall(r"\b[A-Z]{3}-[0-9]{2}\b", open(path, encoding="ascii").read()))


def render_jsonl(rd):
    lines = []
    for r in rd.R:
        rec = dict(r)
        rec["covers"] = sorted(c for c, refs in rd.COVERAGE.items() if r["id"] in refs)
        lines.append(json.dumps(rec, sort_keys=True))
    return "\n".join(lines) + "\n"


def render_tables(rd):
    live = [r for r in rd.R if r["pri"] != "WITHDRAWN"]
    out = [BEGIN, ""]
    out.append("### Counts by category and priority")
    out.append("")
    pris = rd.PRIORITIES[:4]
    out.append("    cat  REQUIRED  HIGH-VALUE  EXPERIMENTAL  REJECTED/AVOID  total")
    tot = {p: 0 for p in pris}
    for c, _ in rd.CATEGORIES:
        row = [sum(1 for r in live if r["cat"] == c and r["pri"] == p) for p in pris]
        for p, n in zip(pris, row):
            tot[p] += n
        out.append("    %-4s %8d  %10d  %12d  %14d  %5d" % (c, row[0], row[1], row[2], row[3], sum(row)))
    out.append("    all  %8d  %10d  %12d  %14d  %5d" % (tot[pris[0]], tot[pris[1]], tot[pris[2]], tot[pris[3]],
                                                         sum(tot.values())))
    out.append("")
    out.append("### Gates (when a requirement must exist) and enforcement")
    out.append("")
    order = {"SLICE": 0, "CORE": 1, "RULE": 2, "GATE-NOVELTY": 9}
    fals = falsifier_ids()
    gates = sorted({r["gate"] for r in live}, key=lambda g: (order.get(g, 3), g))
    out.append("Build-token column: sum of per-requirement standalone bands (midpoints, millions of tokens processed).")
    out.append("It overcounts heavily because requirements share implementation; S1 work-item budgets are in the next")
    out.append("table, later items are budgeted under INF-06. Use the column only to compare gates with each other.")
    out.append("")
    out.append("    gate                 n   REQUIRED  standalone-band-sum (M tokens, REQUIRED only)")
    for g in gates:
        rs = [r for r in live if r["gate"] == g]
        req = [r for r in rs if r["pri"] == "REQUIRED"]
        out.append("    %-20s %3d   %8d  %8.1f" % (g, len(rs), len(req), sum(BUILD_MID[r["build"]] for r in req)))
    out.append("")
    items = getattr(rd, "S1_WORK_ITEMS", None)
    if items is not None:
        out.append("### S1 work items (SLICE-MIN build plan; budgets in M tokens processed)")
        out.append("")
        out.append("Every SLICE requirement is built by exactly one item; the checker fails otherwise, and when the budgets")
        out.append("exceed the cap of %sM (40%% of the upper 90-day build envelope)." % rd.S1_BUDGET_CAP_M)
        out.append("")
        out.append("    item  budget  SLICE requirements built / content")
        for wid, title, budget, refs in items:
            out.append("    %-4s  %6s  %s" % (wid, budget, ", ".join(refs) if refs else "(none: supports X1a)"))
            out.append("                  %s" % title)
        out.append("    total %6s  (cap %s)" % (sum(b for _w, _t, b, _r in items), rd.S1_BUDGET_CAP_M))
        out.append("")
    enf = {}
    for r in live:
        enf.setdefault(r["enforce"], []).append(r["id"])
    for e in rd.ENFORCE:
        if e and e in enf:
            out.append("    enforce %-6s %3d" % (e, len(enf[e])))
    out.append("")
    weak = [r["id"] for r in live if r["pri"] == "REQUIRED" and r["enforce"] in ("FLAG", "AUDIT", "PROSE")]
    out.append("REQUIRED items without a blocking mechanism yet (the architecture must supply one): %s"
               % (", ".join(weak) if weak else "none"))
    out.append("")
    wd = [r for r in rd.R if r["pri"] == "WITHDRAWN"]
    if wd:
        out.append("Withdrawn (kept for id stability): %s" % "; ".join("%s %s" % (r["id"], r["text"]) for r in wd))
        out.append("")
    for c, name in rd.CATEGORIES:
        rows = [r for r in live if r["cat"] == c]
        out.append("### %s -- %s" % (c, name))
        out.append("")
        for r in rows:
            out.append("**%s [%s | %s | %s] %s.** %s" % (r["id"], r["pri"], r["gate"], r["enforce"], r["title"],
                                                       r["text"]))
            out.append("")
            out.append("- Why: %s" % r["why"])
            if r["motive"]:
                out.append("- Historical motive: %s" % r["motive"])
            if r["alt"]:
                out.append("- Alternative considered: %s" % r["alt"])
            if r["test"]:
                out.append("- Discriminating test / verification: %s" % r["test"])
            if r["fake"]:
                out.append("- Counterfeit the enforcement must reject: %s" % r["fake"])
            if r["fake"]:
                verdict = ("- Success means: the discriminating test passes and the counterfeit is refused. Falsified if: "
                           "the counterfeit is accepted or the test fails")
            else:
                verdict = "- Success means: the discriminating test passes. Falsified if: the test fails"
            if r["id"] in fals:
                verdict += "; see also the FALSIFIERS.md row naming %s" % r["id"]
            out.append(verdict + ".")
            for am in r.get("amendments", []):
                out.append("- Post-freeze amendment %s" % am)
            out.append("- Build inference: %s; inference when operated: %s" % (r["build"], r["op"]))
            out.append("")
    out.append("### Coverage of the recovered failure classes")
    out.append("")
    out.append("Each class must map to at least one REQUIRED (or REJECTED/AVOID) requirement enforced by BLOCK or RULE;")
    out.append("the renderer fails otherwise.")
    out.append("")
    out.append("    class  description                                  requirements")
    for cls in rd.TAXONOMY:
        out.append("    %-5s  %-44s %s" % (cls, rd.TAXONOMY[cls][:44], ", ".join(rd.COVERAGE.get(cls, []))))
    out.append("")
    out.append(END)
    return "\n".join(out)


def main():
    rd = load()
    check = "--check" in sys.argv
    errs = validate(rd)
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    jsonl = render_jsonl(rd)
    tables = render_tables(rd)
    jpath = os.path.join(PKG, "requirements.jsonl")
    mpath = os.path.join(PKG, "REQUIREMENTS.md")
    md = open(mpath, encoding="ascii").read() if os.path.exists(mpath) else ""
    if BEGIN not in md or END not in md:
        print("REQUIREMENTS.md lacks generated-table markers")
        sys.exit(1)
    new_md = md[:md.index(BEGIN)] + tables + md[md.index(END) + len(END):]
    if check:
        ok = True
        if not os.path.exists(jpath) or open(jpath, encoding="ascii").read().replace("\r\n", "\n") != jsonl:
            print("requirements.jsonl is stale")
            ok = False
        if md.replace("\r\n", "\n") != new_md.replace("\r\n", "\n"):
            print("REQUIREMENTS.md tables are stale")
            ok = False
        live = sum(1 for r in rd.R if r["pri"] != "WITHDRAWN")
        print("OK: %d live requirements valid, %d failure classes covered, outputs current" % (live, len(rd.TAXONOMY))
              if ok else "STALE")
        sys.exit(0 if ok else 1)
    with open(jpath, "w", encoding="ascii", newline="\n") as f:
        f.write(jsonl)
    with open(mpath, "w", encoding="ascii", newline="\n") as f:
        f.write(new_md)
    print("wrote %d requirements" % len(rd.R))


if __name__ == "__main__":
    main()
