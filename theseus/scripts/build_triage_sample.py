"""Build stratified 300-record sample of promoted-eligible records.

Uses the OLD training_weight (pre-Fire #141 fix) to identify what
the daemon would have promoted historically. Stratification per
ChatGPT's recipe in frontier synthesis.

Strata:
- 100 = one per distinct high-frequency template cluster
- 75  = top info-density across diverse gen families
- 50  = random promoted records
- 50  = rare generator / rare claim-kind / rare domain-pair
- 25  = model-disagreement / verifier-weirdness (REJECTED with rare kill_pattern)
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import glob
import json
import os
import random
from collections import Counter, defaultdict
from pathlib import Path

# Old training_weight (pre-Fire #141)
PER_RELATION_OLD = {"equal": 0.025, "equal_mod_2": 0.65, "divides": 0.35}


def abs_diff_K_weight(k: int) -> float:
    if k <= 3: return 0.60
    if k <= 10: return 0.50
    if k <= 50: return 0.35
    if k <= 500: return 0.20
    return 0.10


KIND_DEFAULT = {
    "operator_rotation": 0.35, "composition_test": 0.35,
    "conservation_law": 0.35, "symmetry_transform": 0.35,
    "literature_mined": 0.20, "kill_neighborhood": 0.40,
    "bridge_extension": 0.55, "statistical_correlation": 0.35,
    "functional_identity": 0.30, "ratio_invariance": 0.40,
    "distribution_match": 0.30,
}

NON_DISC = {"b1", "c4", "f1", "g3"}


def old_base(rec: dict) -> float:
    p = rec.get("claim_payload") or {}
    rel = p.get("relation", "")
    if rel in PER_RELATION_OLD:
        return PER_RELATION_OLD[rel]
    if rel.startswith("abs_diff_le_"):
        try:
            return abs_diff_K_weight(int(rel.rsplit("_", 1)[-1]))
        except ValueError:
            return 0.25
    return KIND_DEFAULT.get(rec.get("claim_kind", ""), 0.25)


def old_verdict_mult(rec: dict) -> float:
    v = rec.get("verdict", "")
    if v == "PROMOTED": return 1.5
    if v == "SHADOW_CATALOG": return 1.0
    if v == "INCONCLUSIVE": return 0.6
    if v == "REJECTED":
        kp = rec.get("kill_pattern") or ""
        return 1.0 if any(s in kp for s in (
            "specific", "violated", "boundary",
            "F1_triggered", "F6_triggered", "F9_triggered", "F11_triggered"
        )) else 0.6
    if v == "UNVERIFIED": return 0.1
    return 0.3


def old_weight(rec: dict) -> float:
    base = old_base(rec)
    v = old_verdict_mult(rec)
    t = 1.3 if rec.get("step_trace") else 1.0
    return max(0.0, min(1.0, base * v * t))


def template_key(rec: dict) -> str:
    """Stable identifier for a record's template shape."""
    p = rec.get("claim_payload") or {}
    return f"{rec.get('generator_id')}:{rec.get('claim_kind')}:{p.get('relation', '?')}"


def domain_pair(rec: dict) -> str:
    p = rec.get("claim_payload") or {}
    a = (p.get("invariant_a") or p.get("object_a") or "?")
    b = (p.get("invariant_b") or p.get("object_b") or "?")
    # Extract domain prefix (e.g. "knot:" or "ec:")
    da = a.split(":")[0] if isinstance(a, str) and ":" in a else "?"
    db = b.split(":")[0] if isinstance(b, str) and ":" in b else "?"
    return f"{da}_x_{db}"


def trim_record(rec: dict) -> dict:
    """Strip large fields to keep the sample compact."""
    keep_keys = {
        "record_id", "batch_id", "generator_id", "claim_kind",
        "verdict", "kill_pattern", "claim_payload",
        "canonical_claim_text", "step_trace",
    }
    out = {k: rec[k] for k in keep_keys if k in rec}
    # truncate text fields
    if "canonical_claim_text" in out:
        out["canonical_claim_text"] = (out["canonical_claim_text"] or "")[:300]
    return out


def main():
    out_dir = Path("F:/Prometheus/pivot")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "promoted_triage_sample.jsonl"

    batches = sorted(
        glob.glob("F:/Prometheus/theseus/corpus/batch-*.jsonl"),
        reverse=True,
    )[:6]
    print(f"Sampling from {len(batches)} recent batches...")
    for b in batches:
        print(f"  {os.path.basename(b)}: {os.path.getsize(b)/1024/1024:.0f}MB")

    random.seed(42)
    all_high_weight = []
    n_scanned = 0
    PER_BATCH_CAP = 60_000

    for bp in batches:
        n_batch = 0
        with open(bp, encoding="utf-8") as f:
            for line in f:
                n_batch += 1
                if n_batch > PER_BATCH_CAP:
                    break
                n_scanned += 1
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("generator_id") in NON_DISC:
                    continue
                w = old_weight(rec)
                if w >= 0.6:
                    all_high_weight.append((w, rec))

    print(f"\nScanned: {n_scanned:,} records / collected {len(all_high_weight):,} promote-eligible")
    if not all_high_weight:
        print("No promote-eligible records found — aborting")
        return

    # Bucket by template
    by_template = defaultdict(list)
    for w, r in all_high_weight:
        by_template[template_key(r)].append((w, r))

    template_freq = Counter({k: len(v) for k, v in by_template.items()})
    print(f"Distinct templates: {len(by_template):,}")
    print(f"Top-5 templates by frequency:")
    for t, c in template_freq.most_common(5):
        print(f"  {t}: {c:,}")

    # Stratum 1: 100 from top high-frequency template clusters
    #   pick from top 100 most-frequent templates, one each
    stratum_1 = []
    seen_ids = set()
    for tpl, _ in template_freq.most_common(100):
        rec = sorted(by_template[tpl], key=lambda x: -x[0])[0][1]
        rid = rec.get("record_id")
        if rid and rid not in seen_ids:
            stratum_1.append((tpl, "S1_high_freq_template", rec))
            seen_ids.add(rid)

    # Stratum 2: 75 top info-density across diverse gen families
    #   sort all records by weight desc, take 1 per gen family in order
    by_gen = defaultdict(list)
    for w, r in all_high_weight:
        by_gen[r.get("generator_id", "?")].append((w, r))
    for gid in by_gen:
        by_gen[gid].sort(key=lambda x: -x[0])
    # round-robin top picks
    stratum_2 = []
    iters = {gid: iter(recs) for gid, recs in by_gen.items()}
    while len(stratum_2) < 75 and iters:
        for gid in list(iters):
            try:
                w, r = next(iters[gid])
                rid = r.get("record_id")
                if rid and rid not in seen_ids:
                    stratum_2.append((gid, "S2_top_diverse_gens", r))
                    seen_ids.add(rid)
                    if len(stratum_2) >= 75:
                        break
            except StopIteration:
                del iters[gid]

    # Stratum 3: 50 random
    random_pool = [r for _, r in all_high_weight if r.get("record_id") not in seen_ids]
    random.shuffle(random_pool)
    stratum_3 = []
    for r in random_pool[:50]:
        stratum_3.append(("random", "S3_random", r))
        seen_ids.add(r.get("record_id"))

    # Stratum 4: 50 from rare gen / rare kind / rare domain-pair
    gen_freq = Counter(r.get("generator_id") for _, r in all_high_weight)
    kind_freq = Counter(r.get("claim_kind") for _, r in all_high_weight)
    dom_freq = Counter(domain_pair(r) for _, r in all_high_weight)
    rare_gens = {g for g, c in gen_freq.items() if c < 100}
    rare_kinds = {k for k, c in kind_freq.items() if c < 100}
    rare_doms = {d for d, c in dom_freq.items() if c < 100}
    stratum_4 = []
    for w, r in all_high_weight:
        if r.get("record_id") in seen_ids:
            continue
        if (r.get("generator_id") in rare_gens
                or r.get("claim_kind") in rare_kinds
                or domain_pair(r) in rare_doms):
            stratum_4.append(("rare", "S4_rare_axis", r))
            seen_ids.add(r.get("record_id"))
            if len(stratum_4) >= 50:
                break

    # Stratum 5: 25 REJECTED with unusual kill_pattern
    kp_freq = Counter(r.get("kill_pattern") or "" for _, r in all_high_weight)
    rare_kps = {kp for kp, c in kp_freq.items() if 0 < c < 100 and kp}
    stratum_5 = []
    for w, r in all_high_weight:
        if r.get("record_id") in seen_ids:
            continue
        if r.get("verdict") == "REJECTED" and (r.get("kill_pattern") or "") in rare_kps:
            stratum_5.append(("rare_kill", "S5_verifier_weird", r))
            seen_ids.add(r.get("record_id"))
            if len(stratum_5) >= 25:
                break

    samples = stratum_1 + stratum_2 + stratum_3 + stratum_4 + stratum_5
    print()
    print(f"Stratum 1 (top-freq templates):  {len(stratum_1)}")
    print(f"Stratum 2 (top diverse gens):    {len(stratum_2)}")
    print(f"Stratum 3 (random):              {len(stratum_3)}")
    print(f"Stratum 4 (rare axis):           {len(stratum_4)}")
    print(f"Stratum 5 (verifier-weird):      {len(stratum_5)}")
    print(f"TOTAL:                           {len(samples)}")

    with open(out_path, "w", encoding="utf-8") as f:
        for label, stratum, rec in samples:
            entry = {
                "stratum": stratum,
                "stratum_subkey": label,
                "old_weight": old_weight(rec),
                "record": trim_record(rec),
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
