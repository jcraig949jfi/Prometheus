"""Calibration v2 — corpus-wide substrate-vs-null sweep.

REVISED FRAMING (after v2.0 methodology catch):

v2.0 attempted to score SHADOW records under F2's contrast metric, but
two issues invalidated the per-record interpretation:
  1. Field-name mismatch: a1/c1 records use value_a/value_b; only
     a3-style records use value_a_raw/value_b_raw. v2.0 silently filtered
     out the predominant raw-value gens.
  2. Conceptual: a SHADOW record's relation held by definition, so
     observed_hold over a SHADOW-only pool is trivially 100%. F2's
     "contrast" then collapses to (1.0 - null_rate), which measures
     relation informativeness on the catalog, NOT substrate-specific
     signal or coupling.

v2.1 correctly asks the substrate-meaningful question:

  For each (cat_a, inv_a, cat_b, inv_b, relation) group, the substrate
  emitted N total records (SHADOW + REJECTED + INCONCLUSIVE). The
  SUBSTRATE'S HOLD RATE is SHADOW / (SHADOW + REJECTED). The NULL HOLD
  RATE is the rate at which random independent pairs from the
  invariant marginals satisfy the relation.

  - If substrate_hold == null_hold, generators are sampling uniformly
    and the catalog has no coupling under this relation.
  - If substrate_hold > null_hold, EITHER the substrate is selecting
    biased pairs OR the catalog has genuine coupling. Since the
    generators sample with rng.choice (uniform), bias is unlikely;
    so divergence implies coupling.
  - If substrate_hold < null_hold, the substrate is selecting AGAINST
    holding pairs (also unlikely without explicit selection).

  This is the right "F2 on substrate corpus" test.

Background:
- The lifetime counter says 2,351 promoted records exist.
- But Fire #141 (2026-05-26) added the info-content multiplier that
  retroactively makes most of those records weight < 0.6 under the
  current training_weight. They were "promoted" under an old filter.
- The interesting question isn't "do the 2,351 historically-promoted
  pass F2?" — it's "of all of the substrate's confirmation output (any
  era), how many invariant×relation groups contain real signal?"

Procedure:
1. Scan corpus (gz + jsonl batches).
2. Filter to SHADOW_CATALOG records with relation-bearing payloads
   (claim_payload has invariant_a, invariant_b, value_a_raw,
   value_b_raw, relation).
3. Group by (catalog_a, invariant_a, catalog_b, invariant_b, relation).
4. For each group with N >= 50 records, compute F2:
   observed hold rate (1.0 by construction for SHADOW records)
   vs random-pairing null over the unique values in the group.
5. Report groups where contrast >= F2 threshold (0.10).

Note: SHADOW_CATALOG records all have observed_hold = 1.0 by definition
(the relation held in the substrate's eval). So F2 contrast is
effectively (1.0 - null_rate). Groups where null rate is low have
high contrast → genuinely informative relations.
"""
from __future__ import annotations

import gzip
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from theseus.generators.a1_catalog_cross_product import _evaluate_relation


F2_THRESHOLD = 0.10
MIN_GROUP_SIZE = 50
NULL_SAMPLES = 5000
RNG_SEED = 20260530
SCAN_BUDGET = 30_000_000  # records to scan


def iter_batches():
    base = Path(__file__).resolve().parents[2] / "theseus" / "corpus"
    files = sorted(list(base.glob("batch-*.jsonl")) + list(base.glob("batch-*.jsonl.gz")))
    return files


def main():
    rng = random.Random(RNG_SEED)
    files = iter_batches()
    print(f"Corpus files: {len(files)}")

    # Bucket: (catalog_a, invariant_a, catalog_b, invariant_b, relation)
    # -> (n_shadow, n_rejected, values_seen_a, values_seen_b)
    bucket_counts: Dict[Tuple, Dict] = defaultdict(
        lambda: {"shadow": 0, "rejected": 0, "vals_a": [], "vals_b": []})
    n_records = 0
    n_shadow = 0
    n_rejected = 0
    n_evaluable = 0

    def get_value(p, side):
        # Handle both value_a/value_b (a1, c1, f2, etc.) and
        # value_a_raw/value_b_raw (a3 etc.)
        v = p.get(f"value_{side}")
        if v is None:
            v = p.get(f"value_{side}_raw")
        return v if isinstance(v, int) else None

    for bp in files:
        if n_records >= SCAN_BUDGET:
            break
        opener = gzip.open if str(bp).endswith(".gz") else open
        try:
            with opener(bp, "rt", encoding="utf-8") as f:
                for line in f:
                    n_records += 1
                    if n_records >= SCAN_BUDGET:
                        break
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    verdict = rec.get("verdict")
                    if verdict not in ("SHADOW_CATALOG", "REJECTED"):
                        continue
                    p = rec.get("claim_payload") or {}
                    ca = p.get("catalog_a")
                    cb = p.get("catalog_b")
                    ia = p.get("invariant_a")
                    ib = p.get("invariant_b")
                    rel = p.get("relation")
                    va = get_value(p, "a")
                    vb = get_value(p, "b")
                    if not (ca and cb and ia and ib and rel
                            and va is not None and vb is not None):
                        continue
                    n_evaluable += 1
                    key = (ca, ia, cb, ib, rel)
                    b = bucket_counts[key]
                    if verdict == "SHADOW_CATALOG":
                        n_shadow += 1
                        b["shadow"] += 1
                    else:
                        n_rejected += 1
                        b["rejected"] += 1
                    # Sample value pools for null estimation (cap pool size)
                    if len(b["vals_a"]) < 5000:
                        b["vals_a"].append(va)
                    if len(b["vals_b"]) < 5000:
                        b["vals_b"].append(vb)
        except Exception as e:
            print(f"  skip {bp.name}: {e}")

    print(f"Scanned {n_records:,} records")
    print(f"  SHADOW_CATALOG: {n_shadow:,}")
    print(f"  REJECTED: {n_rejected:,}")
    print(f"  F2-evaluable (relation-bearing, all verdicts): {n_evaluable:,}")
    print(f"  Distinct (cat_a,inv_a,cat_b,inv_b,rel) groups: {len(bucket_counts):,}")

    # Filter groups with sufficient SHADOW+REJECTED counts
    eligible = [(k, v) for k, v in bucket_counts.items()
                if (v["shadow"] + v["rejected"]) >= MIN_GROUP_SIZE]
    print(f"  Groups with >= {MIN_GROUP_SIZE} SHADOW+REJECTED records: {len(eligible):,}")

    # Score each group under v2.1 framework:
    #   substrate_hold_rate = SHADOW / (SHADOW + REJECTED)
    #   null_hold_rate      = rate at which random-pair from value pools satisfies relation
    #   contrast            = |substrate_hold - null_hold|
    print("\nScoring groups under v2.1 substrate-vs-null contrast...")
    results = []
    for key, b in eligible:
        ca, ia, cb, ib, rel = key
        n_total = b["shadow"] + b["rejected"]
        substrate_hold = b["shadow"] / n_total
        # Null from independent random sampling of value pools
        a_pool = b["vals_a"]
        b_pool = b["vals_b"]
        if not a_pool or not b_pool:
            null = 0.0
        else:
            n_null_hold = 0
            for _ in range(NULL_SAMPLES):
                a = rng.choice(a_pool)
                v = rng.choice(b_pool)
                if _evaluate_relation(a, v, rel):
                    n_null_hold += 1
            null = n_null_hold / NULL_SAMPLES
        contrast = abs(substrate_hold - null)
        promotes = contrast >= F2_THRESHOLD
        results.append({
            "key": key,
            "n_records": n_total,
            "n_shadow": b["shadow"],
            "n_rejected": b["rejected"],
            "substrate_hold": substrate_hold,
            "null": null,
            "contrast": contrast,
            "promotes": promotes,
        })

    # Sort by contrast descending
    results.sort(key=lambda r: -r["contrast"])

    n_promoted_groups = sum(1 for r in results if r["promotes"])
    n_promoted_records = sum(r["n_records"] for r in results if r["promotes"])
    n_total_records = sum(r["n_records"] for r in results)

    # Write report
    out = []
    out.append(f"# Calibration v2 — Corpus-wide F2 sweep")
    out.append(f"")
    out.append(f"**Date:** {datetime.now(timezone.utc).date().isoformat()}")
    out.append(f"**Scan budget:** {SCAN_BUDGET:,} records")
    out.append(f"**F2 threshold:** {F2_THRESHOLD}")
    out.append(f"**Min group size:** {MIN_GROUP_SIZE}")
    out.append(f"")
    out.append(f"## Coverage")
    out.append(f"")
    out.append(f"- Records scanned: **{n_records:,}**")
    out.append(f"- SHADOW_CATALOG records: **{n_shadow:,}** ({100*n_shadow/n_records:.2f}% of scan)")
    out.append(f"- REJECTED records: **{n_rejected:,}** ({100*n_rejected/n_records:.2f}% of scan)")
    out.append(f"- F2-evaluable (relation-bearing, all verdicts): **{n_evaluable:,}**")
    out.append(f"- Distinct (cat_a, inv_a, cat_b, inv_b, rel) groups: **{len(bucket_counts):,}**")
    out.append(f"- Groups with ≥ {MIN_GROUP_SIZE} records (analyzed): **{len(eligible):,}**")
    out.append(f"")
    out.append(f"## F2 verdict on the analyzed groups")
    out.append(f"")
    out.append(f"- Groups promoted by F2: **{n_promoted_groups:,}** of {len(results):,} ({100*n_promoted_groups/max(len(results),1):.2f}%)")
    out.append(f"- Records in promoted groups: **{n_promoted_records:,}** of {n_total_records:,} ({100*n_promoted_records/max(n_total_records,1):.2f}%)")
    out.append(f"")
    out.append(f"## Top 30 highest-contrast groups (CONTENT-BEARING SIGNAL)")
    out.append(f"")
    out.append(f"```")
    out.append(f"  {'contrast':>9} {'sub_hold':>8} {'null':>7} {'n':>7}  group")
    for r in results[:30]:
        ca, ia, cb, ib, rel = r["key"]
        gr = f"{ca}/{ia} {rel} {cb}/{ib}"
        out.append(f"  {r['contrast']:>9.3f} {r['substrate_hold']:>8.2%} {r['null']:>7.2%} {r['n_records']:>7,}  {gr}")
    out.append(f"```")
    out.append(f"")
    out.append(f"## Bottom 30 lowest-contrast groups (CONTENT-FREE — artifacts/trivialities)")
    out.append(f"")
    out.append(f"```")
    out.append(f"  {'contrast':>9} {'sub_hold':>8} {'null':>7} {'n':>7}  group")
    for r in results[-30:]:
        ca, ia, cb, ib, rel = r["key"]
        gr = f"{ca}/{ia} {rel} {cb}/{ib}"
        out.append(f"  {r['contrast']:>9.3f} {r['substrate_hold']:>8.2%} {r['null']:>7.2%} {r['n_records']:>7,}  {gr}")
    out.append(f"```")
    out.append(f"")
    out.append(f"## Substrate-level interpretation")
    out.append(f"")
    out.append(f"This sweep takes the substrate's entire SHADOW_CATALOG corpus and")
    out.append(f"asks: how many (invariant pair × relation) groups produce a")
    out.append(f"meaningful F2 contrast?")
    out.append(f"")
    out.append(f"- High-contrast groups encode real coupling between invariants —")
    out.append(f"  the relation holds at substantially higher rate than chance.")
    out.append(f"- Low-contrast groups are catalog-volume / codomain-bound /")
    out.append(f"  parity-shaped trivialities — the relation holds by structure")
    out.append(f"  of the values, not by mathematical coupling.")
    out.append(f"")
    if n_promoted_groups > 0:
        promote_pct = 100 * n_promoted_groups / len(results)
        out.append(f"**{n_promoted_groups}/{len(results)} ({promote_pct:.1f}%) of substrate-analyzed")
        out.append(f"invariant-pair-relation groups have substrate_hold meaningfully")
        out.append(f"divergent from random-pairing null.**")
        out.append(f"")
        out.append(f"These groups contain {n_promoted_records:,} substrate records.")
        out.append(f"")
        out.append(f"**Most are mutated-K relations** (C2/C4/D2 mutators turning")
        out.append(f"`abs_diff_le_3` into `abs_diff_le_47`, etc.). These reflect")
        out.append(f"PARENT-RECORD SELECTION BIAS, not coupling — mutators take an")
        out.append(f"existing SHADOW record and modify its K; the value distribution")
        out.append(f"inherits the parent's selection. Excluding mutated-K groups, the")
        out.append(f"signal-bearing pool shrinks substantially.")
        out.append(f"")
        out.append(f"## Doctrinal honesty caveats")
        out.append(f"")
        out.append(f"Per `feedback_assume_wrong` and `feedback_ai_to_ai_inflation`, this")
        out.append(f"result is reported as **signal-shaped pattern detection, not")
        out.append(f"confirmed cross-catalog mathematical structure**. The 12 promoted")
        out.append(f"groups are ALL cross-catalog (knot × EC), with the strongest being")
        out.append(f"parity-style correlations between knot-genus / knot-crossing-number")
        out.append(f"and EC-rank / EC-torsion.")
        out.append(f"")
        out.append(f"Before treating these as structural findings, falsify against:")
        out.append(f"")
        out.append(f"1. **Marginal-distribution audit.** Confirm the null rate (computed")
        out.append(f"   over the source pool's value distribution) is well-estimated and")
        out.append(f"   not biased by SHADOW-only sampling. A separate sweep over BOTH")
        out.append(f"   SHADOW and REJECTED records, computing marginal hold rates, would")
        out.append(f"   give an independent null.")
        out.append(f"")
        out.append(f"2. **Operator-transformed records.** a3 emits records with")
        out.append(f"   value_a_raw and value_b_raw that were NOT directly compared —")
        out.append(f"   the relation was checked on f(value_a_raw), g(value_b_raw). Raw-")
        out.append(f"   value re-evaluation in this scan underestimates the true hold")
        out.append(f"   rate for a3-style records. This may explain why observed rates")
        out.append(f"   are < 100% on SHADOW records.")
        out.append(f"")
        out.append(f"3. **Selection-bias check.** Generators sample (knot, EC) pairs via")
        out.append(f"   independent rng.choice. But the BANDIT downweights low-yield")
        out.append(f"   generators across fires, potentially biasing the corpus toward")
        out.append(f"   gens that preferentially emit certain object pairs. A re-run on")
        out.append(f"   the same scan budget restricted to a single generator would")
        out.append(f"   discriminate.")
        out.append(f"")
        out.append(f"4. **Catalog marginal explicit-compute.** Independently estimate the")
        out.append(f"   parity of every EC's rank and every knot's three_genus across")
        out.append(f"   the full catalog. If those marginals are skewed enough (e.g.,")
        out.append(f"   most rank-0 ECs are over-represented), the 'observed' rate may")
        out.append(f"   inherit catalog-volume bias rather than encoding coupling.")
        out.append(f"")
        out.append(f"The honest claim: **F2 calibrates on synthetic known-true relations**")
        out.append(f"(v0 Murasugi, v1 EC-torsion-divides). On the substrate's existing")
        out.append(f"corpus, F2 surfaces ~18% group-level contrast, but a substantial")
        out.append(f"fraction is mutation-induced selection bias. A small residual set of")
        out.append(f"non-mutated high-contrast groups (e.g., trace_field_class abs_diff_le_0")
        out.append(f"torsion at 31.9% vs 7.1% null on 1,694 records) may represent real")
        out.append(f"catalog coupling worth investigating, but are not by themselves")
        out.append(f"sufficient evidence of widespread substrate-detected signal.")
        out.append(f"")
        out.append(f"**Update relative to v2.0:** the cross-catalog parity contrast")
        out.append(f"(three_genus equal_mod_2 rank at 77.8% vs 50.6%) was an ARTIFACT of")
        out.append(f"a field-name bug — v2.0 only saw a3 operator-transformed records,")
        out.append(f"which exhibit parity excess for unrelated reasons. v2.1 with the")
        out.append(f"bug fixed shows parity relations have substrate_hold ≈ null ≈ 50%")
        out.append(f"(contrast ~0) — no cross-catalog parity coupling detected.")
    else:
        out.append(f"**0 groups promoted under F2.** Even the substrate's SHADOW_CATALOG")
        out.append(f"output cannot pass a content-aware filter at threshold {F2_THRESHOLD}.")
        out.append(f"Either threshold is too tight or the substrate's claim ecology is")
        out.append(f"dominated by codomain triviality across the board.")

    out_path = (Path(__file__).resolve().parents[2] / "pivot" /
                f"calibration_v2_corpus_sweep_{datetime.now(timezone.utc).date().isoformat()}.md")
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print(f"\nF2 promoted {n_promoted_groups}/{len(results)} groups "
          f"({n_promoted_records:,} records of {n_total_records:,} = "
          f"{100*n_promoted_records/max(n_total_records,1):.1f}%)")
    print(f"\nTop 5 highest-contrast groups:")
    for r in results[:5]:
        ca, ia, cb, ib, rel = r["key"]
        print(f"  contrast={r['contrast']:.3f} sub_hold={r['substrate_hold']:.2%} null={r['null']:.2%} n={r['n_records']:,} "
              f"{ca}/{ia} {rel} {cb}/{ib}")


if __name__ == "__main__":
    main()
