"""Diomedes cycle 001 — PRE-FLIGHT for the h1 counterfactual-hunt test.

Runs BEFORE the pre-registration, because the cycle contract requires the metric's
attainable range and its SE to be known before any gate line is chosen
(feedback_gate_must_be_shown_reachable, feedback_gate_must_exceed_measurement_error).

This measures ONLY viability. It answers:
  1. Which relations and invariants do h1 hunts actually use?
  2. Can an exact (catalog, invariant, object) -> value table be harvested from the
     corpus itself, and how dense is it?
  3. For a sampled parent state x and a candidate pool of k objects, what fraction
     of candidates BREAK the relation?  That fraction is the chance floor for the
     ranking task and its spread is the headroom.

If |A*|/k sits at ~0 or ~1 the ranking task is degenerate and cycle 001 must be
re-posed rather than run.  That is a VACUOUS reading, pre-committed.

Read-only.  Bounded: reads at most MAX_FILES corpus files, MAX_LINES each.

    python roles/Diomedes/cycle001_preflight.py
"""
import collections
import glob
import gzip
import json
import pathlib
import random
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = pathlib.Path(__file__).resolve().parent / "cycle001_preflight.json"

MAX_FILES = 8
MAX_LINES = 120_000
K = 100          # candidate pool size, frozen here and inherited by the prereg
SEED = 20260824  # frozen


def relation_holds(rel, va, vb):
    """Deterministic relation predicates. Returns None if the relation is unknown,
    so unknown relations are excluded rather than silently scored."""
    try:
        if rel == "equal_mod_2":
            return (va - vb) % 2 == 0
        if rel.startswith("abs_diff_le_"):
            return abs(va - vb) <= int(rel.rsplit("_", 1)[1])
        if rel == "equal":
            return va == vb
        if rel.startswith("ratio_le_"):
            return abs(vb) > 0 and abs(va / vb) <= float(rel.rsplit("_", 1)[1])
        if rel.startswith("equal_mod_"):
            m = int(rel.rsplit("_", 1)[1])
            return (va - vb) % m == 0
    except Exception:
        return None
    return None


def main():
    files = sorted(glob.glob(str(CORPUS / "batch-*.jsonl.gz")))
    idx = [int(len(files) * k / MAX_FILES) for k in range(MAX_FILES)]

    # (catalog, invariant) -> {object: value}
    values = collections.defaultdict(dict)
    parents = []
    rel_counts = collections.Counter()
    inv_pairs = collections.Counter()
    side_counts = collections.Counter()

    for i in idx:
        f = files[min(i, len(files) - 1)]
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for j, line in enumerate(fh):
                if j >= MAX_LINES:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                p = d.get("claim_payload") or {}

                # harvest exact (catalog, invariant, object) -> value pairs
                for sfx in ("a", "b"):
                    cat = p.get(f"catalog_{sfx}")
                    inv = p.get(f"invariant_{sfx}")
                    obj = p.get(f"object_{sfx}")
                    val = p.get(f"value_{sfx}")
                    if cat and inv and obj is not None and isinstance(val, (int, float)):
                        values[(cat, inv)][obj] = val

                if d.get("generator_id") != "h1":
                    continue
                rel = p.get("parent_relation")
                rel_counts[rel] += 1
                inv_pairs[(p.get("invariant_a"), p.get("invariant_b"))] += 1
                side_counts[str(p.get("hunter_varied_side"))] += 1
                if p.get("hunter_success") and p.get("hunter_varied_side") in ("a", "b"):
                    parents.append({
                        "rel": rel,
                        "inv_a": p.get("invariant_a"), "inv_b": p.get("invariant_b"),
                        "obj_a": p.get("parent_object_a"), "obj_b": p.get("parent_object_b"),
                        "val_a": p.get("parent_value_a"), "val_b": p.get("parent_value_b"),
                        "side": p.get("hunter_varied_side"),
                        "hunter_obj": p.get(f"hunter_object_{p.get('hunter_varied_side')}"),
                    })

    # h1 payloads omit catalog_*; infer it from where the invariant was harvested.
    inv_to_cat = {}
    for (cat, inv), d in values.items():
        inv_to_cat.setdefault(inv, collections.Counter())[cat] = len(d)
    inv_cat = {inv: c.most_common(1)[0][0] for inv, c in inv_to_cat.items()}

    rng = random.Random(SEED)
    fracs, usable, unusable = [], 0, collections.Counter()
    for st in parents:
        inv = st["inv_a"] if st["side"] == "a" else st["inv_b"]
        cat = inv_cat.get(inv)
        if cat is None:
            unusable["no_catalog_for_invariant"] += 1
            continue
        pool_src = values.get((cat, inv), {})
        if len(pool_src) < K:
            unusable["pool_too_small"] += 1
            continue
        if st["val_a"] is None or st["val_b"] is None:
            unusable["missing_parent_value"] += 1
            continue
        cands = rng.sample(sorted(pool_src), K)
        broke = 0
        scored = 0
        for c in cands:
            v = pool_src[c]
            va, vb = (v, st["val_b"]) if st["side"] == "a" else (st["val_a"], v)
            h = relation_holds(st["rel"], va, vb)
            if h is None:
                continue
            scored += 1
            if not h:
                broke += 1
        if scored < K // 2:
            unusable["relation_unknown"] += 1
            continue
        fracs.append(broke / scored)
        usable += 1

    rep = {
        "scope": f"{MAX_FILES} stratified files, <={MAX_LINES} lines each",
        "K": K, "seed": SEED,
        "value_table": {
            "n_catalog_invariant_keys": len(values),
            "n_object_value_pairs": sum(len(v) for v in values.values()),
            "largest_pools": sorted(
                ((f"{c}/{i}", len(v)) for (c, i), v in values.items()),
                key=lambda t: -t[1])[:12],
        },
        "h1": {
            "parents_with_successful_hunt": len(parents),
            "relations": rel_counts.most_common(10),
            "top_invariant_pairs": [[list(k), v] for k, v in inv_pairs.most_common(8)],
            "varied_side": side_counts.most_common(),
        },
        "attainable_range": {
            "usable_parent_states": usable,
            "unusable_reasons": unusable.most_common(),
        },
    }
    if fracs:
        fracs.sort()
        n = len(fracs)
        rep["attainable_range"].update({
            "frac_candidates_breaking_mean": round(statistics.fmean(fracs), 4),
            "median": round(fracs[n // 2], 4),
            "p05": round(fracs[max(0, int(0.05 * n))], 4),
            "p95": round(fracs[min(n - 1, int(0.95 * n))], 4),
            "stdev_across_states": round(statistics.pstdev(fracs), 4) if n > 1 else None,
            "share_degenerate_ge_0.95": round(sum(f >= 0.95 for f in fracs) / n, 4),
            "share_degenerate_le_0.05": round(sum(f <= 0.05 for f in fracs) / n, 4),
        })
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1)[:2600])
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
