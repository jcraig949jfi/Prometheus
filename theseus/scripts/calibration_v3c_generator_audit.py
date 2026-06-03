"""Calibration v3c — per-generator audit of the non-mutated F2 contrast.

FOLLOW-ON FROM v3 (calibration_v3_nonmutated.py)
------------------------------------------------
v3 found: excluding mutation-derived records, 61/96 groups still show F2
contrast — BUT restricting to generator a1 (pure uniform rng.choice) gives
0/96 (sub_hold approx null). So the residual contrast comes from NON-a1,
non-mutation generators that emit selected or operator-transformed pairs.

This script names them. For each non-mutated generator_id, it computes the
SAME group-level contrast v3 used, but per generator — using a WITHIN-
GENERATOR null (random re-pairing of that generator's own observed values
for the group). A generator is:

  - UNIFORM-LIKE (clean)   if its per-group sub_hold approx null (like a1).
  - BIAS-INJECTING         if sub_hold diverges from its own re-pairing null,
                           i.e. the pairs it emits are non-independent
                           (targeting) OR the stored raw values are not the
                           values the relation was evaluated on (transform).

The within-generator null is the key: re-pairing a generator's OWN values
isolates whether THAT generator's pairings are independent. a1 should show
~0 (independent by construction); selection/transform generators should show
a positive contrast.

Usage:
    python theseus/scripts/calibration_v3c_generator_audit.py [scan_budget]

Doctrinal anchors: feedback_counter_baseline_discriminator (within-generator
null is the per-generator counter-baseline), feedback_assume_wrong,
feedback_permutation_null.
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
MIN_GROUP_SIZE = 50          # min records per (generator, group)
NULL_SAMPLES = 5000
RNG_SEED = 20260530
POOL_CAP = 4000
DEFAULT_SCAN_BUDGET = 30_000_000


def iter_batches():
    base = Path(__file__).resolve().parents[2] / "theseus" / "corpus"
    return sorted(list(base.glob("batch-*.jsonl")) + list(base.glob("batch-*.jsonl.gz")))


def get_value(p, side):
    v = p.get(f"value_{side}")
    if v is None:
        v = p.get(f"value_{side}_raw")
    return v if isinstance(v, int) else None


def main():
    scan_budget = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SCAN_BUDGET
    rng = random.Random(RNG_SEED)
    files = iter_batches()
    print(f"Corpus files: {len(files)}  |  scan_budget: {scan_budget:,}")

    # (generator_id, group_key) -> counts + pools
    cells: Dict[Tuple, Dict] = defaultdict(
        lambda: {"shadow": 0, "rejected": 0, "vals_a": [], "vals_b": []})
    gen_records: Dict[str, int] = defaultdict(int)

    n_records = 0
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
                    if rec.get("verdict") not in ("SHADOW_CATALOG", "REJECTED"):
                        continue
                    if rec.get("parent_record_id") is not None:
                        continue  # non-mutated only
                    gid = rec.get("generator_id") or "?"
                    p = rec.get("claim_payload") or {}
                    ca = p.get("catalog_a"); cb = p.get("catalog_b")
                    ia = p.get("invariant_a"); ib = p.get("invariant_b")
                    rel = p.get("relation")
                    va = get_value(p, "a"); vb = get_value(p, "b")
                    if not (ca and cb and ia and ib and rel
                            and va is not None and vb is not None):
                        continue
                    gen_records[gid] += 1
                    cell = cells[(gid, (ca, ia, cb, ib, rel))]
                    if rec.get("verdict") == "SHADOW_CATALOG":
                        cell["shadow"] += 1
                    else:
                        cell["rejected"] += 1
                    if len(cell["vals_a"]) < POOL_CAP:
                        cell["vals_a"].append(va)
                    if len(cell["vals_b"]) < POOL_CAP:
                        cell["vals_b"].append(vb)
        except Exception as e:
            print(f"  skip {bp.name}: {e}")

    print(f"Scanned {n_records:,} records | non-mutated gens: {len(gen_records)}")

    # Per-generator aggregate over its eligible groups.
    per_gen: Dict[str, Dict] = defaultdict(
        lambda: {"groups": 0, "promoted": 0, "max_contrast": 0.0,
                 "sum_contrast": 0.0, "records": 0})
    rows = []  # (gid, group_key, n, sub_hold, null, contrast)
    for (gid, key), c in cells.items():
        n = c["shadow"] + c["rejected"]
        if n < MIN_GROUP_SIZE:
            continue
        rel = key[4]
        sub = c["shadow"] / n
        a_pool, b_pool = c["vals_a"], c["vals_b"]
        if not a_pool or not b_pool:
            null = 0.0
        else:
            h = 0
            for _ in range(NULL_SAMPLES):
                if _evaluate_relation(rng.choice(a_pool), rng.choice(b_pool), rel):
                    h += 1
            null = h / NULL_SAMPLES
        contrast = abs(sub - null)
        g = per_gen[gid]
        g["groups"] += 1
        g["records"] += n
        g["sum_contrast"] += contrast
        if contrast >= F2_THRESHOLD:
            g["promoted"] += 1
        if contrast > g["max_contrast"]:
            g["max_contrast"] = contrast
        rows.append((gid, key, n, sub, null, contrast))

    # Sort generators by promote rate then mean contrast.
    gen_summary = []
    for gid, g in per_gen.items():
        if g["groups"] == 0:
            continue
        gen_summary.append({
            "gid": gid,
            "groups": g["groups"],
            "promoted": g["promoted"],
            "promote_rate": g["promoted"] / g["groups"],
            "mean_contrast": g["sum_contrast"] / g["groups"],
            "max_contrast": g["max_contrast"],
            "records": g["records"],
        })
    gen_summary.sort(key=lambda x: (-x["promote_rate"], -x["mean_contrast"]))

    date = datetime.now(timezone.utc).date().isoformat()
    o = []
    o.append("# Calibration v3c — per-generator audit of non-mutated F2 contrast")
    o.append("")
    o.append(f"**Date:** {date}")
    o.append(f"**Scan budget:** {scan_budget:,} records (non-mutated only)")
    o.append(f"**Null:** within-generator random re-pairing of that generator's own values.")
    o.append(f"**Min (generator, group) size:** {MIN_GROUP_SIZE}   **F2 threshold:** {F2_THRESHOLD}")
    o.append("")
    o.append("A generator with promote_rate approx 0 and mean_contrast approx 0 is")
    o.append("UNIFORM-LIKE (its pairings are independent, like a1). A generator with")
    o.append("high promote_rate / mean_contrast is BIAS-INJECTING: its emitted pairs")
    o.append("are non-independent (targeting) or its stored raw values are not the")
    o.append("values the relation was evaluated on (operator transform).")
    o.append("")
    o.append("## Per-generator summary (sorted by promote_rate)")
    o.append("")
    o.append("```")
    o.append(f"  {'gen':>5} {'groups':>7} {'promoted':>9} {'prom_rate':>10} "
             f"{'mean_ctr':>9} {'max_ctr':>8} {'records':>12}")
    for s in gen_summary:
        o.append(f"  {s['gid']:>5} {s['groups']:>7} {s['promoted']:>9} "
                 f"{s['promote_rate']:>10.2%} {s['mean_contrast']:>9.3f} "
                 f"{s['max_contrast']:>8.3f} {s['records']:>12,}")
    o.append("```")
    o.append("")
    o.append("## Top 25 (generator, group) cells by contrast")
    o.append("")
    o.append("```")
    o.append(f"  {'gen':>5} {'contrast':>9} {'sub':>7} {'null':>7} {'n':>9}  group")
    for gid, key, n, sub, null, contrast in sorted(rows, key=lambda r: -r[5])[:25]:
        ca, ia, cb, ib, rel = key
        o.append(f"  {gid:>5} {contrast:>9.3f} {sub:>7.2%} {null:>7.2%} {n:>9,}  "
                 f"{ca}/{ia} {rel} {cb}/{ib}")
    o.append("```")
    o.append("")
    o.append("## Interpretation")
    o.append("")
    o.append("Per `feedback_assume_wrong`: the within-generator null re-pairs each")
    o.append("generator's OWN observed values, so a positive contrast means that")
    o.append("generator's (a,b) pairings are not independent draws from its own")
    o.append("marginals — selection or transform. a1 is the calibration floor")
    o.append("(independent by construction). Generators ranking high here are the")
    o.append("ones whose SHADOW verdicts inflated the v2 corpus signal; their records")
    o.append("should not be scored against a raw-value null in the content-aware")
    o.append("corpus without first reconciling the transform / selection mechanism.")

    out_path = (Path(__file__).resolve().parents[2] / "pivot" /
                f"calibration_v3c_generator_audit_{date}.md")
    out_path.write_text("\n".join(o), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print("\nPer-generator (sorted by promote_rate):")
    for s in gen_summary:
        print(f"  {s['gid']:>5}: groups={s['groups']:>3} promoted={s['promoted']:>3} "
              f"rate={s['promote_rate']:.0%} mean_ctr={s['mean_contrast']:.3f} "
              f"max={s['max_contrast']:.3f} n={s['records']:,}")


if __name__ == "__main__":
    main()
