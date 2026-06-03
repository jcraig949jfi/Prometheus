"""Calibration v3 — non-mutated falsification of the v2 corpus sweep.

WHAT THIS FALSIFIES
-------------------
v2.1 (`calibration_v2_corpus_sweep.py`) found ~18.5% of analyzed
(cat_a, inv_a, cat_b, inv_b, relation) groups have F2 contrast >= 0.10
(substrate_hold meaningfully divergent from a random-pairing null). Its
own doctrinal-honesty caveat flagged that MOST of that contrast is
mutation-induced selection bias:

    "Most are mutated-K relations (C2/C4/D2 mutators turning
     abs_diff_le_3 into abs_diff_le_47, etc.). These reflect
     PARENT-RECORD SELECTION BIAS, not coupling — mutators take an
     existing SHADOW record and modify its K; the value distribution
     inherits the parent's selection."

v2 caveat #3 (selection-bias check) proposed: "A re-run on the same scan
budget restricted to a single generator would discriminate."

v3 implements a cleaner, generator-agnostic version of that probe. A
record is mutation-derived IFF it carries a `parent_record_id` (it was
produced by transforming an existing record). A record with
parent_record_id == None was sampled INDEPENDENTLY from the catalog
marginals (a1-style cross-product, rng.choice on each side), so its
(value_a, value_b) carries no parent-inherited selection bias by
construction.

The decisive question:

    Of the high-contrast groups v2 surfaced, how many SURVIVE when
    restricted to independently-sampled (non-mutated) records?

    - If contrast collapses to ~0 on the non-mutated subset, v2's
      corpus signal was a mutation-selection artifact (substrate finding:
      the existing corpus carries little content-bearing coupling).
    - If contrast survives on the non-mutated subset, those groups
      encode genuine catalog coupling worth investigating.

METHOD
------
Matches v2 exactly except:
  - Scans the SAME sorted-file window (oldest N records) for
    apples-to-apples comparison with v2's published table.
  - Per group, tracks ALL-record shadow/rejected counts (cheap ints)
    AND non-mutated-only counts + value pools.
  - Eligibility + F2 scoring run on the NON-MUTATED subset only.
  - Reports mutation_frac per group so the collapse/survival is visible.

Usage:
    python theseus/scripts/calibration_v3_nonmutated.py [scan_budget]

    scan_budget defaults to 30_000_000 (v2's budget). Pass a small value
    (e.g. 200000) for a smoke run.

Doctrinal anchors: feedback_assume_wrong (all assumptions wrong until
proven), feedback_permutation_null (independent null mandatory),
feedback_sampling_strategy_is_analysis (the oldest-N window is itself a
sampling choice; matched to v2 deliberately and noted in the report).
"""
from __future__ import annotations

import gzip
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from theseus.generators.a1_catalog_cross_product import _evaluate_relation


F2_THRESHOLD = 0.10
MIN_GROUP_SIZE = 50          # min NON-MUTATED (shadow+rejected) per group
NULL_SAMPLES = 5000
RNG_SEED = 20260530          # same seed as v2 for comparability
POOL_CAP = 5000
DEFAULT_SCAN_BUDGET = 30_000_000

# The single strongest non-mutated candidate v2 named, tracked explicitly.
WATCH_KEY = ("knot", "trace_field_class", "ec", "torsion", "abs_diff_le_0")


def iter_batches():
    base = Path(__file__).resolve().parents[2] / "theseus" / "corpus"
    files = sorted(list(base.glob("batch-*.jsonl")) + list(base.glob("batch-*.jsonl.gz")))
    return files


def get_value(p, side):
    v = p.get(f"value_{side}")
    if v is None:
        v = p.get(f"value_{side}_raw")
    return v if isinstance(v, int) else None


def main():
    scan_budget = DEFAULT_SCAN_BUDGET
    if len(sys.argv) > 1:
        scan_budget = int(sys.argv[1])
    # Optional: restrict to a single generator_id (e.g. 'a1' for the
    # uniform-sampling baseline). None = all non-mutated generators.
    gen_filter = sys.argv[2] if len(sys.argv) > 2 else None

    rng = random.Random(RNG_SEED)
    files = iter_batches()
    print(f"Corpus files: {len(files)}  |  scan_budget: {scan_budget:,}"
          f"  |  generator_filter: {gen_filter or 'ALL'}")

    # Per group: all-record counts (ints only) + non-mutated counts + pools.
    buckets: Dict[Tuple, Dict] = defaultdict(lambda: {
        "shadow_all": 0, "rejected_all": 0,
        "shadow_nm": 0, "rejected_nm": 0,
        "vals_a": [], "vals_b": [],
    })

    n_records = 0
    n_eval_all = 0
    n_eval_nm = 0
    n_shadow_all = 0
    n_rejected_all = 0
    n_with_parent = 0

    stop = False
    for bp in files:
        if stop:
            break
        opener = gzip.open if str(bp).endswith(".gz") else open
        try:
            with opener(bp, "rt", encoding="utf-8") as f:
                for line in f:
                    n_records += 1
                    if n_records >= scan_budget:
                        stop = True
                        break
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    verdict = rec.get("verdict")
                    if verdict not in ("SHADOW_CATALOG", "REJECTED"):
                        continue
                    if gen_filter is not None and rec.get("generator_id") != gen_filter:
                        continue
                    p = rec.get("claim_payload") or {}
                    ca = p.get("catalog_a"); cb = p.get("catalog_b")
                    ia = p.get("invariant_a"); ib = p.get("invariant_b")
                    rel = p.get("relation")
                    va = get_value(p, "a"); vb = get_value(p, "b")
                    if not (ca and cb and ia and ib and rel
                            and va is not None and vb is not None):
                        continue
                    n_eval_all += 1
                    key = (ca, ia, cb, ib, rel)
                    b = buckets[key]
                    is_shadow = (verdict == "SHADOW_CATALOG")
                    if is_shadow:
                        n_shadow_all += 1
                        b["shadow_all"] += 1
                    else:
                        n_rejected_all += 1
                        b["rejected_all"] += 1

                    has_parent = rec.get("parent_record_id") is not None
                    if has_parent:
                        n_with_parent += 1
                        continue  # mutation-derived: excluded from non-mutated subset

                    # Independently-sampled record.
                    n_eval_nm += 1
                    if is_shadow:
                        b["shadow_nm"] += 1
                    else:
                        b["rejected_nm"] += 1
                    if len(b["vals_a"]) < POOL_CAP:
                        b["vals_a"].append(va)
                    if len(b["vals_b"]) < POOL_CAP:
                        b["vals_b"].append(vb)
        except Exception as e:
            print(f"  skip {bp.name}: {e}")

    print(f"Scanned {n_records:,} records")
    print(f"  evaluable (all): {n_eval_all:,}  |  non-mutated: {n_eval_nm:,}  "
          f"|  with parent: {n_with_parent:,}")
    print(f"  SHADOW(all): {n_shadow_all:,}  REJECTED(all): {n_rejected_all:,}")
    print(f"  distinct groups: {len(buckets):,}")

    # Eligible on NON-MUTATED counts.
    eligible = [(k, v) for k, v in buckets.items()
                if (v["shadow_nm"] + v["rejected_nm"]) >= MIN_GROUP_SIZE]
    print(f"  groups with >= {MIN_GROUP_SIZE} non-mutated records: {len(eligible):,}")

    results = []
    for key, b in eligible:
        ca, ia, cb, ib, rel = key
        n_nm = b["shadow_nm"] + b["rejected_nm"]
        n_all = b["shadow_all"] + b["rejected_all"]
        sub_hold = b["shadow_nm"] / n_nm
        a_pool = b["vals_a"]; b_pool = b["vals_b"]
        if not a_pool or not b_pool:
            null = 0.0
        else:
            n_null_hold = 0
            for _ in range(NULL_SAMPLES):
                if _evaluate_relation(rng.choice(a_pool), rng.choice(b_pool), rel):
                    n_null_hold += 1
            null = n_null_hold / NULL_SAMPLES
        contrast = abs(sub_hold - null)
        mut_frac = 1.0 - (n_nm / n_all) if n_all else 0.0
        results.append({
            "key": key, "n_nm": n_nm, "n_all": n_all,
            "mut_frac": mut_frac, "sub_hold": sub_hold,
            "null": null, "contrast": contrast,
            "promotes": contrast >= F2_THRESHOLD,
        })

    results.sort(key=lambda r: -r["contrast"])
    n_prom = sum(1 for r in results if r["promotes"])
    n_prom_records = sum(r["n_nm"] for r in results if r["promotes"])
    n_total_nm = sum(r["n_nm"] for r in results)

    # Watch-key survival.
    watch = next((r for r in results if r["key"] == WATCH_KEY), None)
    watch_all = buckets.get(WATCH_KEY)

    date = datetime.now(timezone.utc).date().isoformat()
    o = []
    o.append("# Calibration v3 — non-mutated falsification of the v2 corpus sweep")
    o.append("")
    o.append(f"**Date:** {date}")
    o.append(f"**Scan budget:** {scan_budget:,} records (matched to v2's window: sorted-file, oldest-N)")
    o.append(f"**F2 threshold:** {F2_THRESHOLD}   **Min non-mutated group size:** {MIN_GROUP_SIZE}")
    o.append(f"**Filter:** records with a `parent_record_id` (mutation-derived) EXCLUDED; "
             f"only independently-sampled records scored.")
    o.append("")
    o.append("## Coverage")
    o.append("")
    o.append(f"- Records scanned: **{n_records:,}**")
    o.append(f"- Evaluable (relation-bearing, SHADOW+REJECTED): **{n_eval_all:,}**")
    o.append(f"- Of which mutation-derived (had parent_record_id): **{n_with_parent:,}** "
             f"({100*n_with_parent/max(n_eval_all,1):.1f}% of evaluable)")
    o.append(f"- Independently-sampled (non-mutated, scored): **{n_eval_nm:,}**")
    o.append(f"- Distinct groups: **{len(buckets):,}**  |  with >= {MIN_GROUP_SIZE} non-mutated: **{len(eligible):,}**")
    o.append("")
    o.append("## F2 verdict on NON-MUTATED groups")
    o.append("")
    o.append(f"- Groups promoted by F2 (non-mutated): **{n_prom:,}** of {len(results):,} "
             f"({100*n_prom/max(len(results),1):.2f}%)")
    o.append(f"- Non-mutated records in promoted groups: **{n_prom_records:,}** of {n_total_nm:,} "
             f"({100*n_prom_records/max(n_total_nm,1):.2f}%)")
    o.append("")
    o.append("Compare to v2 (all records): 198/1068 groups (18.54%) promoted. The delta")
    o.append("between this non-mutated rate and v2's all-record rate is the share of v2's")
    o.append("'signal' that was parent-inheritance selection bias.")
    o.append("")
    o.append("## Watch group — strongest non-mutated candidate v2 named")
    o.append("")
    o.append(f"`{WATCH_KEY[0]}/{WATCH_KEY[1]} {WATCH_KEY[4]} {WATCH_KEY[2]}/{WATCH_KEY[3]}` "
             f"(v2 reported: 31.9% vs 7.1% null on 1,694 records)")
    o.append("")
    if watch is not None:
        o.append(f"- **SURVIVES eligibility.** non-mutated n={watch['n_nm']:,} "
                 f"(all-record n={watch['n_all']:,}, mutation_frac={watch['mut_frac']:.1%})")
        o.append(f"- non-mutated sub_hold={watch['sub_hold']:.2%}  null={watch['null']:.2%}  "
                 f"contrast={watch['contrast']:.3f}  -> "
                 f"{'PROMOTES' if watch['promotes'] else 'does NOT promote'}")
    elif watch_all is not None:
        nm = watch_all["shadow_nm"] + watch_all["rejected_nm"]
        al = watch_all["shadow_all"] + watch_all["rejected_all"]
        o.append(f"- **COLLAPSES below eligibility.** all-record n={al:,} but only "
                 f"{nm:,} non-mutated records (< {MIN_GROUP_SIZE}). The v2 signal in this group "
                 f"was {100*(1-nm/max(al,1)):.1f}% mutation-derived.")
    else:
        o.append("- Group not present in this scan window.")
    o.append("")
    o.append("## Top 30 non-mutated groups by contrast")
    o.append("")
    o.append("```")
    o.append(f"  {'contrast':>9} {'sub_hold':>8} {'null':>7} {'n_nm':>7} {'mut%':>6}  group")
    for r in results[:30]:
        ca, ia, cb, ib, rel = r["key"]
        o.append(f"  {r['contrast']:>9.3f} {r['sub_hold']:>8.2%} {r['null']:>7.2%} "
                 f"{r['n_nm']:>7,} {r['mut_frac']:>6.1%}  {ca}/{ia} {rel} {cb}/{ib}")
    o.append("```")
    o.append("")
    o.append("## Interpretation")
    o.append("")
    o.append("Per `feedback_assume_wrong` + `feedback_ai_to_ai_inflation`, reported as")
    o.append("signal-shaped pattern detection, NOT confirmed cross-catalog structure.")
    o.append("")
    o.append("- If the non-mutated promote rate is far below v2's 18.5% and the watch")
    o.append("  group collapses, v2's corpus 'signal' was substantially mutation-selection")
    o.append("  bias — a substrate self-finding, not catalog coupling.")
    o.append("- Surviving non-mutated high-contrast groups are the genuine residual worth")
    o.append("  a marginal-explicit-compute pass (v2 caveat #4) before any further claim.")
    o.append("")
    o.append("**Sampling-window note** (`feedback_sampling_strategy_is_analysis`): this scans")
    o.append("the OLDEST N records (sorted batch filenames), matched to v2 for comparability.")
    o.append("It is NOT a uniform sample of the 658M-record lifetime corpus. A mtime-stratified")
    o.append("re-run is the natural follow-up if the residual survives.")

    suffix = f"_{gen_filter}" if gen_filter else ""
    out_path = (Path(__file__).resolve().parents[2] / "pivot" /
                f"calibration_v3_nonmutated{suffix}_{date}.md")
    out_path.write_text("\n".join(o), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print(f"Non-mutated F2 promoted {n_prom}/{len(results)} groups "
          f"(vs v2 all-record 198/1068 = 18.5%)")
    if watch is not None:
        print(f"WATCH {WATCH_KEY}: contrast={watch['contrast']:.3f} "
              f"n_nm={watch['n_nm']:,} mut_frac={watch['mut_frac']:.1%} "
              f"-> {'PROMOTES' if watch['promotes'] else 'no'}")
    elif watch_all is not None:
        nm = watch_all["shadow_nm"] + watch_all["rejected_nm"]
        print(f"WATCH {WATCH_KEY}: COLLAPSED ({nm} non-mutated < {MIN_GROUP_SIZE})")
    print("\nTop 5 non-mutated by contrast:")
    for r in results[:5]:
        ca, ia, cb, ib, rel = r["key"]
        print(f"  contrast={r['contrast']:.3f} sub={r['sub_hold']:.2%} null={r['null']:.2%} "
              f"n_nm={r['n_nm']:,} mut={r['mut_frac']:.0%}  {ca}/{ia} {rel} {cb}/{ib}")


if __name__ == "__main__":
    main()
