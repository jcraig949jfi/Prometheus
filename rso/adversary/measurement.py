"""The measurement table (directive Generation 5 s7): per known historical defect, was it caught automatically, yes/no.
The CATALOG is the hand-written half (what the defect was, where it is recorded, which kit variant reproduces its shape, or
None when the kit does not cover it). The yes/no is COMPUTED from a runner pass, never typed. A LIMITATION verdict is "no":
the counterfeit reached a verdict, the owner has recorded that it can, and the build does not fail.

    python -m rso.adversary table [--write]        run all targets, print (and write rso/adversary/MEASUREMENT.md)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "MEASUREMENT.md")

# (id, campaign, defect, recorded in, (target, attack, variant-prefix) | None, note)
CATALOG = [
    ("H1", "C-017", "integration removed 1 of 6 confirmatory shards; the frozen analyzer still printed ATTRIBUTION_QUALIFIED",
     "rso/completeness/README.md:5-9", ("z80_completeness", "DROP", "shard-"), ""),
    ("H2", "C-017", "a shard presented twice / under another shard's identity", "rso/completeness/README.md (finding kinds)",
     ("z80_completeness", "DUPLICATE", "shard"), ""),
    ("H3", "C-017", "a row altered after the writer recorded its digest, count preserved", "rso/completeness/README.md (ALTERED)",
     ("z80_completeness", "DUPLICATE", "row"), ""),
    ("H4", "C-017", "an internally consistent rewrite of a derived count (SUBSTITUTED: not the frozen bytes)",
     "rso/completeness/verify.py:47-64 (_check_shard)", ("z80_completeness", "REWRITE_DERIVED", ""), ""),
    ("H5", "C-017", "an answer-bearing label (ground truth) removed from a row", "rso/completeness/verify.py:47-64 (_check_shard)",
     ("z80_completeness", "SCRUB_ANSWER", ""), ""),
    ("H6", "C-018", "analyser reads a smaller experiment: a shard (E5) or a whole law absent", "rso/aether/tests/test_adapter.py:566",
     ("aether_confirm", "DROP", ""), ""),
    ("H7", "C-018", "a copied unit under another seed label (B5)", "rso/aether/confirm.py:15-19",
     ("aether_confirm", "DUPLICATE", ""), ""),
    ("H8", "C-018", "invariant-respecting rewrite of a clamp array of a NON-sampled unit (R1c)", "rso/aether/RESULT.md:28",
     ("aether_confirm", "REWRITE_DERIVED", "clamp-non-sampled"), "known limitation: 58 of 64 units; closed only by the D1 replay audit"),
    ("H9", "C-018", "the same rewrite on a replay-sampled unit (first seed of each shard)", "rso/aether/RESULT.md:28",
     ("aether_confirm", "REWRITE_DERIVED", "clamp-sampled"), ""),
    ("H10", "C-018", "recorded B / attributed tree trusted instead of recomputed", "rso/aether/tests/test_adapter.py:177-200",
     ("aether_confirm", "SCRUB_ANSWER", ""), ""),
    ("H11", "C-017", "'always INSERTED' passed the origin rule Q2 (a rule loose enough for a constant)",
     "rso/qualify/tests/test_falsifiable.py:41-50", ("qualify_falsifiable", "CONSTANT", "always-INSERTED vs loose"), ""),
    ("H12", "C-017", "a recipe lookup table keyed on the registered arm IS the ground-truth table (A2)",
     "rso/qualify/tests/test_falsifiable.py:53-72", ("qualify_falsifiable", "SCRUB_ANSWER", ""), ""),
    ("H13", "C-016", "a control registered with no near-miss: the inference has no demonstrated counterfeit",
     "rso/qualify/falsifiable.py:54-60", ("qualify_falsifiable", "DROP", ""), ""),
    ("H14", "C-013", "analyze.py counted row['discovery'] without re-deriving it from certificate / seeded (D1 integration mutation)",
     "rso/registry/entries.py (stratified-holm-analysis counterexamples)", ("reach_d1_analyze", "REWRITE_DERIVED", ""),
     "known limitation: analyze.py is not qualified as a general analyzer"),
    ("H15", "C-013", "an incomplete round silently read as a smaller experiment", "rso/reach/analyze.py:39-47",
     ("reach_d1_analyze", "DROP", ""), ""),
    ("H16", "C-017", "baselines b1 / b2 had no ENV output (a detector that cannot emit a class)", "rso/qualify/tests/test_falsifiable.py:21-38",
     None, "NOT an attack: caught by rso.qualify cannot_emit inside audit(); no kit variant"),
    ("H17", "C-016", "self-relative comparator passed by perturbation noise (K1 vs own frozen arm)", "rso/qualify/tests/test_falsifiable.py:94-115",
     None, "NOT an attack: needs a case-specific near-miss; caught by near_miss_rejected only if registered"),
    ("H18", "C-018", "invariant-respecting rewrite of the attributed TREE (B1)", "rso/aether/evaluate.py:104-121",
     None, "NOT covered: closed by the tree replay (confirm.py tree_problem); a tree-rewrite variant is a candidate next attack"),
]


def _matches(row, key):
    target, attack, prefix = key
    return row["target"] == target and row["attack"] == attack and row["variant"].startswith(prefix)


def classify(rows, key):
    """(caught_automatically: 'yes' | 'no' | 'not covered', verdict summary)."""
    if key is None:
        return "not covered", "-"
    hit = [r for r in rows if _matches(r, key)]
    if not hit:
        raise KeyError("catalog names a variant that does not exist: %r" % (key,))
    vs = {r["verdict"] for r in hit}
    summary = ", ".join("%s%s" % (v, " " + "/".join(sorted({r["limitation"] for r in hit if r["verdict"] == v and r["limitation"]}))
                                  if v == "LIMITATION" else "") + (" x%d" % sum(r["verdict"] == v for r in hit) if len(hit) > 1 else "")
                        for v in sorted(vs))
    if vs == {"REJECTED"}:
        return "yes", summary
    return "no", summary


def table(rows):
    out = []
    for hid, camp, defect, src, key, note in CATALOG:
        caught, summary = classify(rows, key)
        out.append(dict(id=hid, campaign=camp, defect=defect, recorded_in=src, kit_variant=None if key is None else "%s / %s / %s*" % key,
                        caught_automatically=caught, verdict=summary, note=note))
    return out


REVIEWER_TEMPLATE = """## Reviewer template (the Q3 reviewer fills this; the kit supplements the review, it does not replace it)

Campaign / packet: ____    Reviewer: ____    Date: ____    Kit run (git sha + `python -m rso.adversary run all` exit code): ____

1. Kit coverage read before starting (which of the five attacks already fire on this packet's component): ____
2. Defects found. One row per DEFECT CLASS (not per instance):

| # | defect class | found by (KIT / REVIEWER-ONLY / BOTH) | minutes to find | is it one of the five attacks? | if not: proposed new attack or target |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

3. Reviewer time: total hours ____ ; hours before the first defect ____ ; hours spent re-deriving a defect class already in
   rso/adversary/MEASUREMENT.md ____ (the waste the kit exists to remove).
4. Derived (fill after the above):
   - defects caught automatically = ____ (kit rows) ; defects found only by the reviewer = ____ (REVIEWER-ONLY rows)
   - cost per new defect class = reviewer hours / count of REVIEWER-ONLY classes = ____
   - adversarial coverage per reviewer hour = (attack classes exercised: kit + REVIEWER-ONLY) / reviewer hours = ____
5. Attacks the reviewer invented that should be added to rso/adversary (name, target, one-line shape): ____
6. Kit attacks that were vacuous or misleading on this packet: ____
"""


def render(rows):
    t = table(rows)
    n_yes = sum(r["caught_automatically"] == "yes" for r in t)
    n_no = sum(r["caught_automatically"] == "no" for r in t)
    n_nc = sum(r["caught_automatically"] == "not covered" for r in t)
    lines = ["# Measurement table (C-019-T011; directive Generation 5 s7)", "",
             "Generated by `python -m rso.adversary table --write` from a runner pass; the yes/no column is computed, not typed.",
             "", "Known historical defects: %d. Caught automatically: **%d yes**, **%d no** (LIMITATION: the counterfeit reaches a verdict and the "
             "owner has recorded it), **%d not covered** (no kit variant)." % (len(t), n_yes, n_no, n_nc), "",
             "| id | gen | defect | recorded in | kit variant | caught automatically | verdict |", "|---|---|---|---|---|---|---|"]
    for r in t:
        lines.append("| %s | %s | %s | %s | %s | %s | %s%s |" % (r["id"], r["campaign"], r["defect"], r["recorded_in"], r["kit_variant"] or "-",
                                                               r["caught_automatically"], r["verdict"], " (" + r["note"] + ")" if r["note"] else ""))
    lines += ["", "Defects found only by a reviewer, reviewer time and cost per new defect class are NOT measured by this file: they are "
              "filled by each Q3 reviewer below and copied into the campaign closeout.", "", REVIEWER_TEMPLATE]
    return "\n".join(lines), t


def write(rows):
    text, t = render(rows)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return t
