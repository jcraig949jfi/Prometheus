"""Adjudicate the salvage evaluation (v1, 143 rows) into one row per component and render SALVAGE_MATRIX.md tables.

The final review (wf_335d0a49-a24) found that v1 counted some components twice with conflicting categories, and that
the name-based join of skeptic records attached four records to the wrong row. This script makes those corrections
explicit and reproducible:

  1. Skeptic records are joined by evidence identity against salvage/skeptic_challenges.jsonl (the raw challenge
     records). Where one record had been attached to two rows, it is removed from the row it does not describe and
     that row returns to its evaluator category (MISJOINED below).
  2. Rows describing the same component are merged (MERGES). The losing row is kept in a 'superseded' list.
  3. Category conflicts are resolved by a fixed rule: a skeptic-reviewed category beats an unreviewed one; when both
     are reviewed, the category with less code reuse wins (KEEP > HARDEN > EXTRACT > REBUILD > HISTORICAL_CONTROL >
     RETIRE); a file that a kept fixture depends on is HISTORICAL_CONTROL rather than RETIRE.
  4. A file shared by distinct components is assigned to one row; the others carry a note (SHARED).

Run:   python tools/salvage_adjudicate.py          (writes salvage.jsonl, salvage/NEW_DEFECTS.md and the generated
                                                    blocks of SALVAGE_MATRIX.md)
       python tools/salvage_adjudicate.py --check  (fails if outputs are stale)
"""
import collections
import json
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
V1 = os.path.join(PKG, "salvage", "salvage_v1.jsonl")
CHAL = os.path.join(PKG, "salvage", "skeptic_challenges.jsonl")
OUT = os.path.join(PKG, "salvage.jsonl")
MD = os.path.join(PKG, "SALVAGE_MATRIX.md")
DEFECTS = os.path.join(PKG, "salvage", "NEW_DEFECTS.md")

ORDER = ["KEEP", "HARDEN", "EXTRACT", "REBUILD", "HISTORICAL_CONTROL", "RETIRE", "UNKNOWN"]

MISJOINED = {
    "Proteus foundry v0 VM + grammar":
        "v1 carried the SplitMix64 row's skeptic record (no challenge was raised against this row); restored to the "
        "evaluator category, consistent with its own reason",
    "Ensorain WTP-01..03 foundry":
        "v1 carried the WTP-03 collider row's skeptic record; category unchanged",
    "Harmonia STANDING_RULES.md":
        "v1 carried the QR-1.2.1 row's skeptic record; category unchanged",
    "SFE as a service":
        "v1 carried the Daedalus ledger-core row's skeptic record (no challenge was raised against this row); restored "
        "to the evaluator category",
}

# rows whose own text says a kept fixture depends on them (rule 3: HISTORICAL_CONTROL rather than RETIRE)
FIXTURE_RULE = {
    "Proteus foundry v0 VM + grammar":
        "its own reason keeps a frozen copy as the substrate under the C4 fixtures (a kept HISTORICAL_CONTROL row "
        "imports proteus.foundry grammar/vm), so by rule 3 it is HISTORICAL_CONTROL rather than RETIRE",
}

# (keeper name prefix, [merged name prefixes], adjudicated category, note)
MERGES = [
    ("Proteus SplitMix64 keyed random streams", ["proteus.foundry.prng keyed streams"], "REBUILD",
     "same file evaluated by org-a (REBUILD) and search (HARDEN), both skeptic-reviewed; less reuse wins. The generator "
     "core is correct SplitMix64; derivation and seeding are rebuilt behind a declared key schema (REP-07), with "
     "prng.py kept as a golden-vector fixture"),
    ("Ares carriers.py carrier attribution", ["Ares carriers.py edge/SCC carrier"], "REBUILD",
     "exact duplicate (org-b and meas-b)"),
    ("Proteus mutation-kernel crucibles V0.3-V0.6", ["Proteus mutation-kernel crucible V0.3-V0.6"],
     "HISTORICAL_CONTROL", "exact duplicate (org-a and search)"),
    ("Ensorain N0-N6 null ladder / substrate collider",
     ["Ensorain null ladder N0-N5 + XC", "Ensorain WTP-03 collider protocol"], "HISTORICAL_CONTROL",
     "one file (ensorain/wtp3/collider.py) evaluated three times; two skeptic reviews say HISTORICAL_CONTROL, the "
     "unreviewed world row said REBUILD; reviewed wins. The MEA-03 baseline ladder is a new build that uses this "
     "ladder's missing-rung failure as a fixture"),
    ("Z80 material-taint shadow interpreters",
     ["NPE z8taint (H3 material ruler R3)", "Archaeon taint VM and lineage core"], "HISTORICAL_CONTROL",
     "the same taint code evaluated by org-b (reviewed: HISTORICAL_CONTROL) and meas-b (unreviewed: REBUILD, "
     "HISTORICAL_CONTROL); reviewed wins. The DGM provenance shadow (ORG-08) is a new build informed by its design"),
    ("Ananke mirror-twin interchange lens", ["Ananke mirror-pair carrier-swap lens"], "HISTORICAL_CONTROL",
     "lens.py and lens_swap.py evaluated by org-b (reviewed: HISTORICAL_CONTROL) and meas-b (unreviewed: REBUILD); "
     "reviewed wins. The R2 interchange ruler is a new build; this lens is its failure corpus and canary source"),
    ("Ensorain WTP-01..03 foundry", ["Ensorain WTP world-genome foundry"], "HISTORICAL_CONTROL",
     "same foundry evaluated by org-b and world"),
    ("Ensorain arc3/suff sufficiency ladder", ["Ensorain ARC3 answer-keyed processes with exact Bayes"],
     "HISTORICAL_CONTROL",
     "worlds.py evaluated by org-b (reviewed: HISTORICAL_CONTROL as a sealed known-answer cross-check) and world "
     "(reviewed: HARDEN as the F3 core); less reuse wins. Using it as the F3 core would destroy its value as an "
     "independent check of the F3 solver (WLD-04, WLD-17); F3's exact Bayes is small to rebuild. The MEA-07 learners "
     "in the same package are REBUILD"),
    ("Bellerophon Worlds Kernel", ["prometheus.toolbox receipt"], "REBUILD",
     "receipt.py evaluated by world (reviewed: REBUILD) and infra (reviewed: EXTRACT upheld); both skeptics found the "
     "same defects (optional chain, unkeyed ids, json default=str collisions); less reuse wins. The schema design and "
     "the forensic-scan property tests are kept as acceptance tests for the new R0 ledger"),
    ("D-5 register machine package", ["D-5 GA navigators and substrate"], "HISTORICAL_CONTROL",
     "same package evaluated by org-a and search"),
    ("Tyche audits and world certificates", ["Tyche v2 certify.py"], "HISTORICAL_CONTROL",
     "certify.py evaluated by org-b and world"),
]

# (path, row prefix that keeps it, [other row prefixes], note)
SHARED = [
    ("hecate/metamorphic/harness.py", "Hecate metamorphic evaluator harness",
     ["Hecate evaluator contract + metamorphic harness"],
     "both rows skeptic-reviewed; less reuse wins: the harness is HISTORICAL_CONTROL, and the REBUILD row covers the "
     "evaluator contract only"),
    ("Aether/observatory/aeth03_propagation.py", "Aether verification kit",
     ["Aether aeth01.v1 byte lattice", "Aether one-bit twin"],
     "kept frozen as a fixture under the verification kit; the one-bit twin design is rebuilt on DGM hooks"),
    ("ludus/controls/fixtures.py", "Ludus qualification fixtures", ["Ludus differential leak audit"],
     "the Kuhn leak worlds are kept fixtures; the leak audit itself is rebuilt"),
    ("ergon/gen3/cheat_control.py, ergon/gen3/mde_p3.py", "Ergon bounded-null machinery",
     ["Ergon library seeding"], "the skeptic-reviewed row keeps these files"),
    ("proteus/graph/witness.py", "Proteus known-answer search fixtures", ["Proteus graph_organism.v1"],
     "a kept fixture depends on it, so it is HISTORICAL_CONTROL, not RETIRE"),
    ("proteus/foundry/{generate,grammar,lineage}.py", "Proteus foundry v0 VM + grammar", ["Archaeon WSE GA loop"],
     "frozen with the foundry under the C4 fixtures; the GA loop's design is rebuilt without them"),
    ("proteus/v0_5/multiplicity.py", "Proteus mutation-kernel crucibles V0.3-V0.6",
     ["Statistics code repo-wide"], "the buggy Holm code is an MEA-11 known-answer specimen"),
    ("tyche/worlds.py, tyche/v2/", "Tyche audits and world certificates", ["Tyche lens DAG ecology"],
     "both HISTORICAL_CONTROL; no conflict"),
    ("fabric/executors.py", "Agent Fabric store + worker", ["Fabric claude executor"], "both REBUILD; no conflict"),
    ("apollo/src/blackboard_evolve.py", "Apollo program substrates", ["Apollo Branch C blackboard MAP-Elites"],
     "both RETIRE; no conflict"),
]


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def find(rows, prefix):
    hits = [r for r in rows if r["name"].startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit("prefix %r matched %d rows" % (prefix, len(hits)))
    return hits[0]


def first_sentences(text, limit=420):
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text.rfind(". ", 0, limit)
    return text[: cut + 1] if cut > 80 else text[:limit].rstrip() + " ..."


def adjudicate():
    rows = load(V1)
    chal = {c["evidence"][:200]: c for c in load(CHAL)}
    used = collections.Counter()
    for r in rows:
        r["evaluator_reason"] = r["reason"]
        r["corrections"] = []
        r["superseded"] = []
        r["shared_paths"] = []
        r["greenfield"] = r["paths"].strip().lower().startswith("none")
        if r["name"] in MISJOINED:
            r["corrections"].append("skeptic record removed: " + MISJOINED[r["name"]])
            r["skeptic"], r["skeptic_evidence"] = "", ""
            r["category"] = r["evaluator_category"]
        if r["skeptic"]:
            c = chal.get((r["skeptic_evidence"] or "")[:200])
            if c is None:
                raise SystemExit("skeptic evidence of %r not found in challenges" % r["name"])
            used[c["evidence"][:200]] += 1
            r["skeptic_component"] = c["component"]
            r["skeptic_proposed"] = c.get("proposed_category")
    dup = [k for k, n in used.items() if n > 1]
    if dup or len(used) != len(chal):
        raise SystemExit("skeptic join not one-to-one: %d duplicated, %d of %d used" % (len(dup), len(used), len(chal)))
    v1_stats = stats_changes(rows)
    for r in rows:
        if r["name"] in FIXTURE_RULE:
            r["corrections"].append("category %s -> HISTORICAL_CONTROL: %s" % (r["category"], FIXTURE_RULE[r["name"]]))
            r["category"] = "HISTORICAL_CONTROL"

    for keep, others, cat, note in MERGES:
        k = find(rows, keep)
        for o in others:
            r = find(rows, o)
            k["superseded"].append({key: r[key] for key in ("group", "name", "paths", "evaluator_category",
                                                            "category", "skeptic", "evaluator_reason", "defects",
                                                            "skeptic_evidence")})
            rows.remove(r)
        if cat != k["category"]:
            k["corrections"].append("category %s -> %s by merge adjudication" % (k["category"], cat))
        k["category"] = cat
        k["corrections"].append("merged: " + note)

    for path, keeper, others, note in SHARED:
        k = find(rows, keeper)
        k["shared_paths"].append({"path": path, "kept_here": True, "note": note})
        for o in others:
            find(rows, o)["shared_paths"].append({"path": path, "kept_here": False, "kept_by": k["name"],
                                                  "kept_category": k["category"], "note": note})

    for r in rows:
        if r["skeptic"] == "DOWNGRADE":
            prop = r.get("skeptic_proposed") or r["category"]
            r["disposition"] = "%s. Skeptic finding: %s" % (prop.rstrip("."), first_sentences(r["skeptic_evidence"]))
        else:
            r["disposition"] = r["evaluator_reason"]
        r.pop("reason", None)
    return rows, v1_stats


def stats_changes(rows):
    ch = collections.Counter()
    for r in rows:
        if r["evaluator_category"] != r["category"]:
            ch[(r["evaluator_category"], r["category"])] += 1
    verdicts = collections.Counter(r["skeptic"] for r in rows if r["skeptic"])
    changed = [r for r in rows if r["evaluator_category"] != r["category"]]
    less = sum(1 for r in changed if ORDER.index(r["category"]) > ORDER.index(r["evaluator_category"]))
    up_verdicts = sum(1 for r in changed if r["skeptic"] != "DOWNGRADE")
    return {"rows": len(rows), "changes": ch, "verdicts": verdicts, "less": less, "upward_verdicts": up_verdicts}


def render_counts(rows, v1):
    c = collections.Counter(r["category"] for r in rows)
    n = len(rows)
    green = sum(1 for r in rows if r["category"] == "REBUILD" and r["greenfield"])
    meaning = {
        "KEEP": "nothing is suitable as is",
        "HARDEN": "sound concept and code; fix named defects, then use",
        "EXTRACT": "lift a small primitive into shared infrastructure",
        "REBUILD": "the need is REQUIRED; build new (%d greenfield with no predecessor; %d replace an inadequate "
                   "predecessor whose design becomes the specification)" % (green, c["REBUILD"] - green),
        "HISTORICAL_CONTROL": "not production machinery; known-answer fixtures, planted positives/negatives, "
                              "canaries, anti-calibration items or design references",
        "RETIRE": "no Phase 3 role",
    }
    out = ["    category              count   share   what it means here"]
    for cat in ORDER[:-1]:
        text = meaning[cat]
        lines, cur = [], ""
        for word in text.split():
            if len(cur) + len(word) + 1 > 72:
                lines.append(cur)
                cur = word
            else:
                cur = (cur + " " + word).strip()
        lines.append(cur)
        out.append("    %-20s %6d   %5.2f   %s" % (cat, c[cat], c[cat] / float(n), lines[0]))
        for extra in lines[1:]:
            out.append("    %-20s %6s   %5s   %s" % ("", "", "", extra))
    out.append("    %-20s %6d" % ("total components", n))
    out.append("")
    merged = sum(len(r["superseded"]) for r in rows)
    out.extend(textwrap.wrap(
        "Deduplication: v1 had %d evaluation rows; %d rows described a component already evaluated by another "
        "group and are merged into it (kept in each row's 'superseded' field), leaving %d distinct components. "
        "Four skeptic records had been attached to the wrong row by a name-based join; they are removed "
        "(tools/salvage_adjudicate.py, MISJOINED)." % (v1["rows"], merged, n), 120))
    out.append("")
    parts = ", ".join("%d %s -> %s" % (k, a, b) for (a, b), k in sorted(v1["changes"].items(), key=lambda x: -x[1]))
    nch = sum(v1["changes"].values())
    out.extend(textwrap.wrap(
        "Skeptic verdicts on the v1 rows: %d challenges, %d downgrades, %d upheld; %d category changes (%s). %d move "
        "toward less code reuse; the other %d are EXTRACT -> HARDEN, which sits higher in the reuse ordering but was "
        "recorded by the skeptics as a downgrade (more fixing before any use). %d changes came from a verdict other "
        "than DOWNGRADE. The two 'upward' changes reported in the first version (RETIRE -> REBUILD, RETIRE -> "
        "HISTORICAL_CONTROL) were the mis-joins."
        % (sum(v1["verdicts"].values()), v1["verdicts"]["DOWNGRADE"], v1["verdicts"]["UPHELD"], nch, parts,
           v1["less"], nch - v1["less"], v1["upward_verdicts"]), 120))
    return out


def render_table(rows):
    out = []
    for cat in ORDER:
        sel = [r for r in rows if r["category"] == cat]
        if not sel:
            continue
        out.append("### %s (%d)" % (cat, len(sel)))
        out.append("")
        for r in sel:
            head = "- **%s** [%s; %s; cost %s]" % (r["name"], r["group"], r["seat"], r["cost"])
            if r["evaluator_category"] != r["category"]:
                head += " (evaluator: %s)" % r["evaluator_category"]
            if r["greenfield"]:
                head += " (greenfield)"
            body = [head + ". Slot: %s. Serves: %s." % (r["slot"], ", ".join(r["serves"]) or "-")]
            body.append("  - Disposition: %s" % " ".join(r["disposition"].split()))
            body.append("  - Correctness: %s" % " ".join((r.get("correctness") or "not stated").split()))
            body.append("  - Coupling: %s" % " ".join((r.get("coupling") or "not stated").split()))
            body.append("  - Skeptic: %s." % (r["skeptic"] or "not challenged"))
            for s in r["superseded"]:
                body.append("  - Superseded row: %s [%s; evaluator %s; v1 final %s; skeptic %s]."
                            % (s["name"], s["group"], s["evaluator_category"], s["category"], s["skeptic"] or "none"))
            for c in r["corrections"]:
                body.append("  - Correction: %s." % c.rstrip("."))
            for sp in r["shared_paths"]:
                if sp["kept_here"]:
                    body.append("  - Shared file %s: assigned to this row (%s)." % (sp["path"], sp["note"]))
                else:
                    body.append("  - Shared file %s: assigned to %s [%s] (%s)."
                                % (sp["path"], sp["kept_by"], sp["kept_category"], sp["note"]))
            out.extend(body)
        out.append("")
    return out


def render_defects(rows):
    out = ["# Defects found during salvage", ""]
    out.extend(textwrap.wrap(
        "Found by salvage evaluators and skeptics (workflow wf_93b1779f-c3f) by reading code and running probes in "
        "scratch copies. Claude-family readings (independence class I1); not confirmed by owners; not fixed. "
        "Generated by tools/salvage_adjudicate.py from salvage.jsonl: one section per distinct component with its "
        "adjudicated category; defects and skeptic records of rows merged into a component are listed under it, and "
        "skeptic records are attached by evidence identity (the first version attached four to the wrong row).", 120))
    out.append("")
    for r in rows:
        merged = [m for m in r["superseded"] if m.get("defects") or m.get("skeptic_evidence")]
        if not (r.get("defects") or r.get("skeptic_evidence") or merged):
            continue
        out.append("## %s (%s; %s)" % (r["name"], r["group"], r["category"]))
        out.append("Paths: %s" % r["paths"])
        for d in r.get("defects") or []:
            out.append("- %s" % " ".join(d.split()))
        if r.get("skeptic_evidence"):
            out.append("- Skeptic (%s): %s" % (r["skeptic"], " ".join(r["skeptic_evidence"].split())))
        for m in merged:
            out.append("- From the merged row '%s' (%s; v1 %s):" % (m["name"], m["group"], m["category"]))
            for d in m.get("defects") or []:
                out.append("  - %s" % " ".join(d.split()))
            if m.get("skeptic_evidence"):
                out.append("  - Skeptic (%s): %s" % (m["skeptic"], " ".join(m["skeptic_evidence"].split())))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def splice(text, begin, end, lines):
    a = text.index(begin) + len(begin)
    b = text.index(end)
    return text[:a] + "\n" + "\n".join(lines).rstrip("\n") + "\n" + text[b:]


def main():
    rows, v1 = adjudicate()
    jsonl = "".join(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n" for r in rows)
    md = open(MD).read()
    md2 = splice(md, "<!-- BEGIN GENERATED SALVAGE COUNTS -->", "<!-- END GENERATED SALVAGE COUNTS -->",
                 render_counts(rows, v1))
    md2 = splice(md2, "<!-- BEGIN GENERATED SALVAGE TABLE -->", "<!-- END GENERATED SALVAGE TABLE -->",
                 render_table(rows))
    defects = render_defects(rows)
    for name, s in (("salvage.jsonl", jsonl), ("SALVAGE_MATRIX.md", md2), ("NEW_DEFECTS.md", defects)):
        if any(ord(ch) > 127 for ch in s):
            raise SystemExit("non-ASCII output in " + name)
    if "--check" in sys.argv:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        curd = open(DEFECTS).read() if os.path.exists(DEFECTS) else ""
        if cur != jsonl or md != md2 or curd != defects:
            raise SystemExit("salvage outputs are stale; run tools/salvage_adjudicate.py")
        print("OK: %d components, outputs current" % len(rows))
        return
    with open(OUT, "w", newline="\n") as f:
        f.write(jsonl)
    with open(MD, "w", newline="\n") as f:
        f.write(md2)
    with open(DEFECTS, "w", newline="\n") as f:
        f.write(defects)
    c = collections.Counter(r["category"] for r in rows)
    print("wrote %d components: %s" % (len(rows), dict(c)))


if __name__ == "__main__":
    main()
