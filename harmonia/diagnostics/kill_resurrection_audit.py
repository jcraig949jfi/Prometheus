"""Kill-resurrection retrodiction, re-keyed on REPRESENTABILITY.

The question (META_SYNTHESIS_2026-08-12_v1.md section 5, v4): of the program's historical
kills, what fraction were ROUTING ARTIFACTS -- non-promoted because the claim's KIND
could not be expressed or dispatched -- rather than CONTENT FAILURES, where the claim
was evaluated and genuinely did not hold?

This is a RETRODICTION: the data was written before the hypothesis existed and cannot
be tuned to fit.

Method (pre-registered in harmonia/experiments/kill_resurrection_prereg_20260819.md):

  1. KILL := verdict == REJECTED. SHADOW_CATALOG is a content-PASS that was never
     promoted -- a different failure -- and is reported separately, never as a kill.
  2. Re-evaluate every record's relation INDEPENDENTLY from the stored operands, using
     semantics written from the relation NAME. The stored `holds` flag is never read
     as input; it is only compared against afterwards.
  3. Score each killed record:
       CONTENT_FAILURE   - re-evaluation confirms the relation is violated (kill correct)
       ROUTING_ARTIFACT  - representable, re-evaluates TRUE, yet was killed (resurrection)
       UNREPRESENTABLE   - cannot be re-evaluated from stored fields. Scored as its own
                           class, explicitly NOT as a resurrection (Harmonia D's standing
                           test: a meter must not score "cannot decide" as "novel").
  4. Denominator discipline: the sample is stratified with unknown inclusion
     probabilities, so only S3_random supports unbiased extrapolation. It is reported
     separately from the pooled figure.

Zero counts are reported with the rule-of-three 95% upper bound (~3/n) rather than as
a bare "0%", because a zero on a finite sample is a ceiling, not a certainty.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/kill_resurrection_audit.py
  ... --json D:\\Prometheus\\harmonia\\diagnostics\\_kill_resurrection.json

Harmonia C, 2026-08-19.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE = os.path.join(REPO, "pivot", "promoted_triage_sample.jsonl")

CONTENT_FAILURE = "CONTENT_FAILURE"
ROUTING_ARTIFACT = "ROUTING_ARTIFACT"
UNREPRESENTABLE = "UNREPRESENTABLE"


# ---------------------------------------------------------------------------
# Relation semantics, re-implemented from the relation NAME.
# Deliberately NOT imported from theseus.generators: an independent re-derivation is
# the point. Returns None when the relation is not expressible here.
# ---------------------------------------------------------------------------
def evaluate(relation, a, b):
    if relation is None or a is None or b is None:
        return None
    try:
        a = float(a)
        b = float(b)
    except (TypeError, ValueError):
        return None
    if relation == "equal":
        return a == b
    if relation == "equal_mod_2":
        return (int(a) % 2) == (int(b) % 2)
    m = re.fullmatch(r"abs_diff_le_(\d+)", relation)
    if m:
        return abs(a - b) <= int(m.group(1))
    if relation == "divides":
        if a == 0:
            return b == 0
        return (b % a) == 0
    m = re.fullmatch(r"equal_mod_(\d+)", relation)
    if m:
        k = int(m.group(1))
        return k != 0 and (int(a) % k) == (int(b) % k)
    return None


TIGHT_BOUNDARY_EPS = 2.0   # from the substrate's own kill_pattern "d4_loose_boundary_epsX>2.0"


def assertion(rec):
    """Re-derive (my_value, stored_value, note) for the record's ACTUAL assertion.

    Each claim_kind asserts something different, and using value_a/value_b uniformly
    is wrong for three of the five kinds. Getting this wrong manufactures phantom
    findings: an earlier revision of this file scored 13 records as substrate
    false-passes that were purely my own operand-selection error. What each kind
    actually asserts:

      invariant_equality  relation(value_a, value_b)                  -> holds
      mutation            relation at the MUTATED threshold           -> new_holds|holds
      symmetry_transform  truth of the relation is INVARIANT under
                          reflection of operand a                     -> reflection_symmetric
      kill_neighborhood   kill/pass pair straddle a TIGHT boundary:
                          epsilon <= 2.0                              -> tight_boundary
      bridge_extension    per-extension relation holds                -> n_holding
    """
    p = rec["claim_payload"]
    kind = rec.get("claim_kind")
    rel = p.get("relation")

    if kind in ("invariant_equality", "mutation"):
        mine = evaluate(rel, p.get("value_a"), p.get("value_b"))
        stored = p.get("new_holds") if isinstance(p.get("new_holds"), bool) else p.get("holds")
        return mine, stored, ""

    if kind == "symmetry_transform":
        raw = evaluate(rel, p.get("value_a"), p.get("value_b"))
        refl = evaluate(rel, p.get("reflected_value_a"), p.get("value_b"))
        if raw is None or refl is None:
            return None, p.get("reflection_symmetric"), "reflection operands missing"
        return (raw == refl), p.get("reflection_symmetric"), "reflection invariance"

    if kind == "kill_neighborhood":
        eps = p.get("epsilon")
        if eps is None:
            return None, p.get("tight_boundary"), "no epsilon"
        return (float(eps) <= TIGHT_BOUNDARY_EPS), p.get("tight_boundary"), "epsilon <= 2.0"

    if kind == "bridge_extension":
        exts = p.get("extensions") or []
        kv = p.get("knot_value")
        n_hold = 0
        for e in exts:
            v = evaluate(rel, kv, e.get("value"))
            if v is None:
                return None, p.get("n_holding"), "extension not expressible"
            n_hold += bool(v)
        return n_hold, p.get("n_holding"), "n_holding recomputed"

    mine = evaluate(rel, p.get("value_a"), p.get("value_b"))
    return mine, p.get("holds"), "fallback value_a/value_b"


def classify(rec):
    mine, stored, note = assertion(rec)
    if mine is None:
        return UNREPRESENTABLE, mine, stored, note or "not expressible"
    truth = mine > 0 if isinstance(mine, int) and not isinstance(mine, bool) else bool(mine)
    return (ROUTING_ARTIFACT if truth else CONTENT_FAILURE), mine, stored, note


def rule_of_three(n):
    return 3.0 / n if n else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=SAMPLE)
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.sample, encoding="utf-8") if l.strip()]

    out = []
    for r in rows:
        rec = r["record"]
        cls, mine, sh, note = classify(rec)
        out.append({
            "stratum": r["stratum"], "verdict": rec.get("verdict"),
            "claim_kind": rec.get("claim_kind"),
            "relation": rec["claim_payload"].get("relation"),
            "generator_id": rec.get("generator_id"),
            "kill_pattern": rec.get("kill_pattern"),
            "record_id": rec.get("record_id"),
            "class": cls, "reeval": mine, "stored_holds": sh,
            "disagrees": (mine is not None and sh is not None and mine != sh),
            "note": note,
            "text": rec.get("canonical_claim_text"),
        })

    kills = [r for r in out if r["verdict"] == "REJECTED"]
    shadow = [r for r in out if r["verdict"] == "SHADOW_CATALOG"]

    print("Kill-resurrection retrodiction (representability-keyed)")
    print(f"sample: {a.sample}")
    print(f"records {len(out)} | KILLS (REJECTED) {len(kills)} | "
          f"SHADOW_CATALOG {len(shadow)}")
    print("=" * 84)

    def block(label, rs):
        c = Counter(r["class"] for r in rs)
        n = len(rs)
        print(f"\n{label}  (n={n})")
        for k in (CONTENT_FAILURE, ROUTING_ARTIFACT, UNREPRESENTABLE):
            v = c.get(k, 0)
            print(f"   {k:<18}{v:>5}   {v/n:>7.1%}" if n else f"   {k:<18}{v:>5}")
        return c

    print("\n--- THE RETRODICTION: killed records, independently re-evaluated ---")
    ck = block("ALL KILLS (pooled, purposive strata included)", kills)

    s3 = [r for r in kills if r["stratum"] == "S3_random"]
    c3 = block("S3_random only (the unbiased stratum)", s3)

    print("\nper-stratum kill classification")
    print("-" * 84)
    print(f"{'stratum':<26}{'kills':>7}{'content_fail':>14}{'routing':>9}{'unrepr':>9}")
    by = defaultdict(list)
    for r in kills:
        by[r["stratum"]].append(r)
    for s, rs in sorted(by.items()):
        c = Counter(r["class"] for r in rs)
        print(f"{s:<26}{len(rs):>7}{c.get(CONTENT_FAILURE,0):>14}"
              f"{c.get(ROUTING_ARTIFACT,0):>9}{c.get(UNREPRESENTABLE,0):>9}")

    res_pooled = ck.get(ROUTING_ARTIFACT, 0)
    res_s3 = c3.get(ROUTING_ARTIFACT, 0)
    print("\n" + "=" * 84)
    print("RESURRECTION RATE")
    print(f"  pooled   : {res_pooled}/{len(kills)}"
          + (f"  (95% upper bound {rule_of_three(len(kills)):.1%} - a zero on a finite"
             " sample is a ceiling, not a certainty)" if res_pooled == 0 else
             f" = {res_pooled/len(kills):.1%}"))
    print(f"  S3_random: {res_s3}/{len(s3)}"
          + (f"  (95% upper bound {rule_of_three(len(s3)):.1%})" if res_s3 == 0
             else f" = {res_s3/len(s3):.1%}"))

    print("\n--- CONTROL: does my re-evaluation reproduce the substrate's own flag? ---")
    cmp_rows = [r for r in out if r["reeval"] is not None and r["stored_holds"] is not None]
    dis = [r for r in cmp_rows if r["disagrees"]]
    if cmp_rows:
        print(f"  comparable records: {len(cmp_rows)}   disagreements: {len(dis)}"
              f"  ({len(dis)/len(cmp_rows):.1%})")
    else:
        print("  none comparable")
    for r in dis[:8]:
        print(f"    {r['generator_id']} {r['relation']}: mine={r['reeval']} "
              f"stored={r['stored_holds']} | {str(r['text'])[:80]}")

    print("\n--- SHADOW_CATALOG: content PASSED, never promoted (not a kill) ---")
    cs = Counter(r["class"] for r in shadow)
    print(f"  n={len(shadow)}  re-evaluates TRUE: {cs.get(ROUTING_ARTIFACT,0)}  "
          f"FALSE: {cs.get(CONTENT_FAILURE,0)}  unrepresentable: {cs.get(UNREPRESENTABLE,0)}")
    print("  (a SHADOW_CATALOG that re-evaluates TRUE is the substrate working as built:")
    print("   the content check passed and promotion still did not happen.)")

    print("\n--- representability by claim_kind (the blind-band question) ---")
    print(f"{'claim_kind':<22}{'n':>5}{'representable':>15}")
    bk = defaultdict(list)
    for r in out:
        bk[r["claim_kind"]].append(r)
    for k, rs in sorted(bk.items(), key=lambda kv: -len(kv[1])):
        rep = sum(1 for r in rs if r["class"] != UNREPRESENTABLE)
        print(f"{k:<22}{len(rs):>5}{rep:>10}/{len(rs):<4}")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"rows": out,
                       "kills": len(kills), "shadow": len(shadow),
                       "resurrections_pooled": res_pooled,
                       "resurrections_s3_random": res_s3,
                       "disagreements": len(dis)}, fh, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
