"""
L1 and L2 gate classification: hand verdicts merged with a mechanical arm-level profile.

Two independent components, deliberately kept separate:

  HAND      the three-way reachability verdict per row, mine, disputable, listed as data
            below so it can be argued with row by row.
  MECHANICAL the per-arm gate STRENGTH profile and the chance floor, computed by regex
            from the test text with no judgement.

Run from repo root:
    python aporia/q100/probes/gate_classify_l1_l2.py           # report only
    python aporia/q100/probes/gate_classify_l1_l2.py --write   # also update the registries
"""
import json
import os
import re
import sys

BASE = os.path.join(os.path.dirname(__file__), "..")

# ---------------------------------------------------------------------------
# HAND VERDICTS
#
# Coding rule, applied uniformly:
#   THEOREM_BLOCKED  a named theorem forbids the PASS condition
#   BOUNDARY_GATE    the PASS condition is an absolute (zero/all/exact/always/none)
#                    with no tolerance, so no band remains for a measurement to land in
#   REACHABLE        a threshold strictly inside the attainable range
#   NO_GATE          no arm declares a threshold OR a direction
# Scored by the worst gated arm. The rubric scores the TESTS, not the question's ambition.
#
# BOUNDED-DOMAIN EXCEPTION -- authored DURING coding, not preregistered, disclosed:
#   an absolute PASS over a domain the test itself bounds to a finite enumerable set,
#   where the property is decidable on that set, is REACHABLE rather than BOUNDARY_GATE.
#   Both codings are reported. STRICT (no exception) is the one comparable to L3 and L4,
#   because the L3 pass coded structurally-guaranteed zeros as BOUNDARY_GATE.
# ---------------------------------------------------------------------------

L1_BOUNDARY_BOTH = {
    "Q005": "T2 'no completeness loss' -- zero loss over an unbounded problem class",
    "Q013": "T2 restored posterior 'matches' fresh inference exactly; T3 invariants 'always' hold",
    "Q028": "T2 'no systematic exploit' -- a universal negative over adapting opponents",
    "Q035": "T2 'ONLY logically affected conclusions change' over unseen exception structures",
    "Q055": "T3 '>=10x fewer states WITHOUT solution loss' -- zero loss over an unbounded state space",
    "Q073": "T2 'ALL logically dependent beliefs update' over an unbounded dependency set",
    "Q077": "T3 'NO REDUCTION in average natural-shift accuracy' -- zero-degradation absolute",
    "Q083": "T3 'PASS ZERO disabling' over an open-ended set of invisible opportunities",
}

L1_BOUNDARY_STRICT_ONLY = {
    "Q006": "T1 zero kernel-invalid over 1e6 proofs, T2 'all rejected' -- bounded trial count, kernel check decidable per proof",
    "Q039": "T3 'passes EXHAUSTIVE small-domain verification' -- domain explicitly bounded and decidable",
    "Q040": "T3 'ZERO errors exhaustively verified' -- exhaustive over a bounded domain",
    "Q053": "T1 '1e4 updates ZERO previous-rule violations' -- bounded update count, rule satisfaction decidable",
    "Q056": "T3 '>=30% smaller operator set with UNCHANGED solvability' -- unchanged over the bounded eval set",
    "Q057": "T3 'EXACT compliance returns' -- compliance over the restored finite rule set is decidable",
    "Q060": "T2 'NOT reproducible within bound' -- the bound makes the composition space finite and the search decidable",
    "Q080": "T2 'PASS NONE within verified domain' -- the verified domain is the bound, and verification decides it",
    "Q081": "T1 'ZERO prohibited actions over 1e6 trials' -- bounded trials, constraints machine-checkable by construction",
}

L2_NO_GATE = {
    "L2-005": "every arm measures ('measure the breakdown point', 'correlate', 'is the circuit distinct') -- no threshold, no direction",
    "L2-020": "T1 'quantify residual variance', T2 'chart which axes', T3 empty",
    "L2-022": "T1 'locate the breakdown', T2 'which measure predicts', T3 empty",
    "L2-023": "T1 'is it task-invariant or governed by', T2 'constant slope or curving contours', T3 empty",
    "L2-028": "all three arms are yes/no questions with no predicted answer",
    "L2-045": "T1 census, T2 a dichotomy readout with neither branch predicted, T3 a correlation",
    "L2-046": "T1 'does the frontier worsen', T2 'compare compressibility', T3 'bits to specify' -- all open",
    "L2-047": "T1 'which degrades less' with no predicted winner, T2 derive-and-search, T3 measure",
    "L2-090": "T1/T2 'does confidence move' with no predicted answer, T3 a comparison",
}

L2_BOUNDARY = {
    "L2-027": "T2 'discriminator must reach AUC ~0.5' -- indistinguishability cannot be established, only not rejected",
    "L2-055": "T1 'drives probe-detection to ZERO while true behavior stays high'",
    "L2-064": "T1 'confinement drives exfiltration to ZERO'",
    "L2-091": "T1 'NO regime pushes below the aleatoric floor' -- a universal negative over objectives",
}

# ---------------------------------------------------------------------------
# MECHANICAL ARM PROFILE
# ---------------------------------------------------------------------------

NUMERIC = re.compile(
    r"(>=|<=|>|<|~)\s*\d|\d+\s*(%|x\b|pt\b|points?\b|bits?\b)|"
    r"\bECE\s*[<>]|\bAUC\s*[>~]|\bR2\s*>=|\bSpearman\s*[>=]|\d\.\d", re.I
)
# a declared sign with no magnitude: PREDICT, or an explicit comparative
DIRECTIONAL = re.compile(
    r"\bPREDICT\b|\bNULL to falsify\b|\bmust (?:reach|separate|be)\b|"
    r"\b(?:better|worse|higher|lower|more|less|faster|sharper|fewer) than\b|"
    r"\brises?\b|\bfalls?\b|\bcollapses?\b|\bdegrades?\b|\bpersists?\b|"
    r"\bbeats\b|\bunderperforms?\b|\bstill (?:fires|helps)\b", re.I
)
# how many independent sign claims one arm conjoins -> chance floor 2**-k
SIGN_CLAIM = re.compile(
    r"\brises?\b|\bfalls?\b|\bcollapses?\b|\bdegrades?\b|\bdeclines?\b|\bpersists?\b|"
    r"\bgrows?\b|\bshrinks?\b|\bflattens?\b|\bbetter\b|\bworse\b|\bhigher\b|\blower\b|"
    r"\bnear-?zero\b|\bnon-?zero\b|\bsharp\b|\bmonotone\b|\bunbounded\b", re.I
)
PASS_TOK = re.compile(r"\bPASS\b")
FAIL_TOK = re.compile(r"\bFAIL\b")
# does the test declare a chance level, null, or baseline to beat?
FLOOR_DECL = re.compile(
    r"\bchance\b|\bbaseline\b|\bnull\b|\bcontrol\b|\bplacebo\b|\bcompute-matched\b|"
    r"\bmatched-compute\b|\brandom\b", re.I
)


def arm_profile(text):
    """Gate strength of one test arm."""
    if not text or not text.strip():
        return "EMPTY", 0
    has_num = bool(NUMERIC.search(text))
    two_sided = bool(PASS_TOK.search(text) and FAIL_TOK.search(text))
    if two_sided and has_num:
        return "TWO_SIDED", 0
    if has_num:
        return "ONE_SIDED_NUMERIC", 0
    if DIRECTIONAL.search(text):
        return "DIRECTIONAL", max(1, len(set(m.group(0).lower() for m in SIGN_CLAIM.finditer(text))))
    return "NONE", 0


def row_profile(row):
    arms = {}
    k_total = 0
    for a in ("t1", "t2", "t3"):
        kind, k = arm_profile(row.get(a))
        arms[a] = kind
        k_total += k
    return arms, k_total


def chance_floor(arms, k_total):
    """
    Probability the row passes under a null of no effect, where computable.
    NONE/EMPTY arms cannot fail -> 1.0. DIRECTIONAL arms pass on the sign -> 2**-k.
    Numeric arms depend on the threshold and the population and CANNOT be computed
    from the text; reported as None rather than guessed.
    """
    kinds = set(arms.values())
    if kinds <= {"NONE", "EMPTY"}:
        return 1.0
    if kinds & {"TWO_SIDED", "ONE_SIDED_NUMERIC"}:
        return None
    return 2.0 ** (-k_total) if k_total else 0.5


def load(fn):
    path = os.path.join(BASE, fn)
    return path, [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    write = "--write" in sys.argv
    summary = {}

    for name, fn in [("L1", "REGISTRY.jsonl"), ("L2", "REGISTRY_L2.jsonl")]:
        path, rows = load(fn)
        counts_strict, counts_ref, arm_counts, floors = {}, {}, {}, []
        floor_declared = 0
        for r in rows:
            rid = r["id"]
            arms, k = row_profile(r)
            for v in arms.values():
                arm_counts[v] = arm_counts.get(v, 0) + 1
            cf = chance_floor(arms, k)
            if cf is not None:
                floors.append(cf)
            blob = " ".join(filter(None, [r.get("t1"), r.get("t2"), r.get("t3")]))
            if FLOOR_DECL.search(blob):
                floor_declared += 1

            if name == "L1":
                if rid in L1_BOUNDARY_BOTH:
                    strict = refined = "BOUNDARY_GATE"
                    reason = L1_BOUNDARY_BOTH[rid]
                elif rid in L1_BOUNDARY_STRICT_ONLY:
                    strict, refined = "BOUNDARY_GATE", "REACHABLE"
                    reason = "BOUNDED-DOMAIN EXCEPTION: " + L1_BOUNDARY_STRICT_ONLY[rid]
                else:
                    strict = refined = "REACHABLE"
                    reason = "banded: every declared PASS sits strictly inside the attainable range"
            else:
                if rid in L2_NO_GATE:
                    strict = refined = "NO_GATE"
                    reason = L2_NO_GATE[rid]
                elif rid in L2_BOUNDARY:
                    strict = refined = "BOUNDARY_GATE"
                    reason = L2_BOUNDARY[rid]
                else:
                    strict = refined = "REACHABLE"
                    reason = ("reachable on the frozen axis, but the gate is DIRECTIONAL: "
                              f"chance floor {cf:.3f}" if cf is not None
                              else "banded: a numeric threshold is declared")

            counts_strict[strict] = counts_strict.get(strict, 0) + 1
            counts_ref[refined] = counts_ref.get(refined, 0) + 1
            r["_gate_verdict"] = strict
            r["_gate_verdict_refined"] = refined
            r["_gate_reason"] = reason
            r["_gate_arm_profile"] = arms
            r["_chance_floor"] = cf
            r["_gate_coded"] = "2026-09-01 Aporia, PREREG_L1_L2_GATE_REACHABILITY.md"

        summary[name] = (counts_strict, counts_ref, arm_counts, floors, floor_declared, len(rows))
        if write:
            with open(path, "w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r) + "\n")

    for name, (cs, cr, ac, floors, fd, n) in summary.items():
        print(f"\n=== {name} ({n} rows) ===")
        print("  STRICT  (comparable to L3/L4):", {k: f"{v} ({100*v/n:.0f}%)" for k, v in sorted(cs.items())})
        print("  REFINED (bounded-domain exc):", {k: f"{v} ({100*v/n:.0f}%)" for k, v in sorted(cr.items())})
        print("  arm gate strength (300 arms):", dict(sorted(ac.items())))
        if floors:
            import statistics
            print(f"  computable chance floors: {len(floors)}/{n} rows, "
                  f"median {statistics.median(floors):.3f}, max {max(floors):.3f}")
        else:
            print("  computable chance floors: 0 rows")
        print(f"  rows naming a chance level / baseline / null anywhere: {fd}/{n} ({100*fd/n:.0f}%)")

    if write:
        print("\nregistries updated")


if __name__ == "__main__":
    main()
