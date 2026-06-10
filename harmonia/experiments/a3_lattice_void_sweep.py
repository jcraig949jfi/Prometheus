"""a3_lattice_void_sweep.py — Proposal B execution driver (Harmonia D, 2026-06-10).

Exhaustive audit of a3's FULL functional-identity lattice:
    6 ops (f) x 6 ops (g) x 6 knot invariants x 4 EC invariants x 4 relations
    = 3,456 cells   [Proposal B's "20,736" was an arithmetic slip — see results]
each evaluated EXACTLY over the full 52-knot x 1000-EC cross-product via the
factored evaluator in harmonia/primitives/lattice_void_miner.py.

Engine semantics are injected from theseus (zero reimplementation):
operators from a3, relation evaluator + invariant lists from a1, catalogs from
theseus.config. Validator: harmonia/experiments/test_lattice_void_miner.py
(14 checks incl. factored==direct exact-count regression).

Emits (written from Python, flushed — feedback_background_output_capture):
  harmonia/experiments/a3_lattice_sweep_results.json   full per-cell data
  harmonia/experiments/a3_candidate_identities.jsonl   one row per exact void
  console summary incl. 144-projection cross-check vs the 2026-05-30 sampled
  pass and the Proposal-A costume gate verdict.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a3_functional_identity import OPERATORS                 # noqa: E402
from theseus.generators.a1_catalog_cross_product import (                       # noqa: E402
    _load_catalog, _get_int, _evaluate_relation,
    KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS, RELATIONS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH                      # noqa: E402
from harmonia.primitives.lattice_void_miner import (                            # noqa: E402
    LatticeSpec, mine, cell_id, costume_gate, _value_sets,
)

OUT_JSON = Path(__file__).parent / "a3_lattice_sweep_results.json"
OUT_JSONL = Path(__file__).parent / "a3_candidate_identities.jsonl"
PRIOR_REPORT = REPO / "pivot" / "a3_lattice_voids_2026-05-30.md"


def build_spec() -> LatticeSpec:
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    side_a = {ki: [v for v in (_get_int(k, ki) for k in knots) if v is not None]
              for ki in KNOT_INTEGER_INVARIANTS}
    side_b = {ei: [v for v in (_get_int(e, ei) for e in ecs) if v is not None]
              for ei in EC_INTEGER_INVARIANTS}
    return LatticeSpec(
        side_a_name="knot", side_b_name="ec",
        side_a=side_a, side_b=side_b,
        operators=dict(OPERATORS), relations=tuple(RELATIONS),
        eval_relation=_evaluate_relation,
    )


def project_144(cells) -> dict:
    """Marginalize the full lattice onto (f, g, rel), weighting each (ki, ei)
    by its defined-pair count — the exact estimand of the 2026-05-30 sampled
    pass (uniform draws over (k, e, ki, ei) with None-skip)."""
    holds = defaultdict(int)
    evals = defaultdict(int)
    for c in cells:
        key = (c["f"], c["g"], c["rel"])
        holds[key] += c["hold_count"]
        evals[key] += c["n_eval"]
    return {key: holds[key] / evals[key] for key in evals}


def parse_prior_table() -> dict:
    """Read the 2026-05-30 report's full-lattice table for the cross-check."""
    txt = PRIOR_REPORT.read_text(encoding="utf-8")
    block = txt.split("## Full lattice (sorted by hold_rate descending)")[1]
    rows = {}
    for line in block.splitlines():
        m = re.match(r"\s+(\w+)\s+(\w+)\s+\|\s+(\w+)\s+\|\s+([0-9.]+)\s*$", line)
        if m:
            f, g, rel, rate = m.group(1), m.group(2), m.group(3), float(m.group(4))
            rows[(f, g, rel)] = rate
    return rows


def cross_check(projection: dict, prior: dict) -> dict:
    """Compare exact projection vs the prior sampled estimates. With ~2000
    samples/cell the prior's binomial s.e. is <= ~0.011; flag cells deviating
    by more than 4 s.e. (accounting for its own None-skip thinning)."""
    diffs = []
    for key, prior_rate in prior.items():
        if key not in projection:
            continue
        exact = projection[key]
        se = max((exact * (1 - exact) / 2000) ** 0.5, 0.0035)
        diffs.append({"cell": key, "prior_sampled": prior_rate,
                      "exact": round(exact, 4),
                      "abs_diff": round(abs(exact - prior_rate), 4),
                      "z": round((prior_rate - exact) / se, 2) if se else 0.0})
    worst = sorted(diffs, key=lambda d: -abs(d["z"]))[:10]
    n_flag = sum(1 for d in diffs if abs(d["z"]) > 4)
    return {"n_compared": len(diffs), "n_flagged_4se": n_flag, "worst10": worst}


def known_fact_tags(spec: LatticeSpec, v: dict) -> list:
    """Tag T3 marginal facts that correspond to known mathematics (the
    rediscovery-calibration leg). Conservative: only facts that are
    unambiguous theorems/structures get a tag."""
    tags = []
    c = v["cell"]
    cert = v["certificate"] or {}
    A, B = _value_sets(spec, c)
    if cert.get("form") == "PARITY_CONSTANT":
        if c["inv_a"] == "determinant" and c["f"] in ("identity", "abs", "neg") \
                and cert.get("parity") == 1:
            tags.append("KNOWN: knot determinant is always odd "
                        "(det(K) = |Delta_K(-1)|, Delta_K(-1) odd for knots)")
        # (a 'conductor all-even' tag shipped in v1 was doubly dead: premise
        # false — catalog is 788 even / 212 odd — and the branch unreachable;
        # removed per the 2026-06-10 panel audit)
    if cert.get("form") == "INTERVAL_WIDTH":
        if c["inv_b"] == "torsion" and c["g"] == "log2_floor":
            tags.append("THEOREM (MAZUR): torsion order in {1..10,12} => "
                        "log2_floor(torsion) <= 3 on EVERY EC/Q catalog — "
                        "this bound is theorem-protected, not selection")
        if c["inv_b"] == "rank":
            tags.append("SELECTION: catalog ranks lie in {0,1,2} by designed "
                        "quota (500/400/100); rank>=3 curves exist inside the "
                        "conductor window (5077a1); breaks under extension")
        if c["inv_a"] == "three_genus":
            tags.append("CATALOG-FACT: three_genus in [1,4] for this 52-knot table")
    if cert.get("form") == "DIVIDES_GCD":
        if set(A) == {1}:
            tags.append("TAUTOLOGY: A == {1}; 1 divides everything")
    return tags


def main():
    spec = build_spec()
    print("Sweeping full lattice "
          f"({len(spec.operators)}f x {len(spec.operators)}g x "
          f"{len(spec.side_a)}ki x {len(spec.side_b)}ei x "
          f"{len(spec.relations)}rel = "
          f"{len(spec.operators)**2 * len(spec.side_a) * len(spec.side_b) * len(spec.relations)} cells) "
          f"over {len(spec.side_a['determinant'])} knots x "
          f"{len(spec.side_b['rank'])} ECs exact cross-product...")
    mined = mine(spec)
    cells, voids = mined["cells"], mined["voids"]
    print(f"  cells={len(cells)}  exact_voids={len(voids)}  "
          f"by_class={mined['summary']['voids_by_class']}")

    # --- per-class census + T3 detail -------------------------------------
    for v in voids:
        v["known_fact_tags"] = known_fact_tags(spec, v)
    t3 = [v for v in voids if v["triviality_class"] == "T3_MARGINAL_FACT"]
    print(f"\nT3 (marginal-fact) voids: {len(t3)}")
    for v in t3:
        c = v["cell"]
        A, B = _value_sets(spec, c)
        v["set_summary"] = {
            "A": {"min": min(A), "max": max(A), "uniq": len(set(A))},
            "B": {"min": min(B), "max": max(B), "uniq": len(set(B))},
        }
        print(f"  {v['cell_id']}: {v['certificate']['statement']}"
              f"  n_eval={c['n_eval']}  tags={v['known_fact_tags']}")

    # --- near-void bands (the gradient; failure shapes, not verdicts) -----
    print("\nNear-void bands (not exact, statistical treatment):")
    for band, lst in mined["near_voids"].items():
        print(f"  >= {band}: {len(lst)} cells")
        for c in sorted(lst, key=lambda x: -x["hold_rate"])[:6]:
            print(f"    {cell_id(c)}  hold={c['hold_rate']:.5f} "
                  f"({c['n_eval'] - c['hold_count']}/{c['n_eval']} violations)")

    # --- held-out honesty note + conductor-band split for near-voids ------
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    med = sorted(_get_int(e, "conductor") for e in ecs)[len(ecs) // 2]
    lo = [e for e in ecs if _get_int(e, "conductor") <= med]
    hi = [e for e in ecs if _get_int(e, "conductor") > med]
    held_out = []
    top_near = sorted((c for lst in mined["near_voids"].values() for c in lst),
                      key=lambda x: -x["hold_rate"])[:12]
    for c in top_near:
        rates = {}
        for name, sub in (("lo_conductor", lo), ("hi_conductor", hi)):
            vb = [v for v in (_get_int(e, c["inv_b"]) for e in sub) if v is not None]
            va = spec.side_a[c["inv_a"]]
            f, g = spec.operators[c["f"]], spec.operators[c["g"]]
            hold = sum(spec.eval_relation(f(a), g(b), c["rel"])
                       for a in va for b in vb)
            rates[name] = round(hold / (len(va) * len(vb)), 5) if va and vb else None
        held_out.append({"cell_id": cell_id(c), "full": round(c["hold_rate"], 5),
                         **rates})
    print("\nConductor-band split on top near-voids "
          "(exact voids: split replication is logically vacuous — subset of an "
          "all-holds set always holds; generalization lives in the Lean leg):")
    for h in held_out:
        print(f"  {h['cell_id']}: full={h['full']} lo={h['lo_conductor']} "
              f"hi={h['hi_conductor']}")

    # --- 144-projection cross-check vs 2026-05-30 sampled pass ------------
    proj = project_144(cells)
    prior = parse_prior_table()
    cc = cross_check(proj, prior)
    print(f"\nProjection cross-check vs pivot/a3_lattice_voids_2026-05-30.md: "
          f"{cc['n_compared']} cells compared, {cc['n_flagged_4se']} beyond 4 s.e.")
    for d in cc["worst10"][:5]:
        print(f"  {d['cell']}: prior={d['prior_sampled']} exact={d['exact']} "
              f"z={d['z']}")

    # --- Proposal A costume gate ------------------------------------------
    print("\nCostume gate (Proposal A primitive, custom Jaccard comparator):")
    verdict, generic_control = costume_gate(spec, mined)
    print(f"  verdict: {verdict.verdict}  "
          f"[NOT evidence by itself — see degeneracy caveat; read the ladder]")
    for r in verdict.per_baseline:
        print(f"    {r.name}: agreement={r.agreement_rate:.4f} "
              f"deltas={r.actionable_deltas} n_union={r.n_shared_keys}")
    print(f"  degeneracy control (A generic catalog, same wiring): "
          f"{generic_control.verdict} — identity-copier hole, filed to Proposal A")

    # --- emit ---------------------------------------------------------------
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for v in voids:
            row = {
                "cell_id": v["cell_id"], **{k: v["cell"][k] for k in
                                            ("f", "g", "inv_a", "inv_b", "rel",
                                             "n_eval", "hold_rate")},
                "marginal_null_rate": v["nulls"]["relation_laxity"]["generic_hold_rate"],
                "marginal_pairing_null": "DEGENERATE_BY_THEOREM",
                "replication_verdict": "VACUOUS_FOR_EXACT_VOIDS_SEE_LEAN_LEG",
                "triviality_class": v["triviality_class"],
                "certificate": v["certificate"],
                "known_fact_tags": v["known_fact_tags"],
                "n_objects": [v["nulls"]["object_domination"]["n_objects_a"],
                              v["nulls"]["object_domination"]["n_objects_b"]],
                "thin_support": v["nulls"]["object_domination"]["thin"],
            }
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    print(f"\nWrote {len(voids)} candidate rows -> {OUT_JSONL}")

    payload = {
        "meta": {
            "date": "2026-06-10", "author": "Harmonia_M2_D (Proposal B)",
            "lattice": "6f x 6g x 6ki x 4ei x 4rel = 3456 cells "
                       "(Proposal B's 20736 was an arithmetic slip)",
            "catalogs": {"knots": 52, "ecs": 1000},
            "evaluation": "exact full cross-product via factored histograms; "
                          "validator test_lattice_void_miner.py 14/14",
        },
        "summary": mined["summary"],
        "projection_cross_check": cc,
        "held_out_near_voids": held_out,
        "costume_verdict": {
            "verdict": verdict.verdict, "headline": verdict.headline,
            "per_baseline": {r.name: {"agreement": r.agreement_rate,
                                      "deltas": r.actionable_deltas,
                                      "n_union": r.n_shared_keys}
                             for r in verdict.per_baseline},
            "z_vs_null": verdict.z_vs_null,
            "interpretation": "tie at 1.0 is PRE-ORDAINED for unique-key "
                              "claims (identity-copier degeneracy; panel C7 "
                              "REFUTED) — the evidence is the ladder "
                              "pigeonhole < constant-absorber < certificate",
            "generic_catalog_control": {
                "verdict": generic_control.verdict,
                "note": "A's marginal_majority ties any unique-key claim — "
                        "interface hole filed to Proposal A (Harmonia B)",
            },
        },
        "voids": [{k: v[k] for k in ("cell_id", "triviality_class",
                                     "certificate", "certificate_verified",
                                     "known_fact_tags")}
                  for v in voids],
        "cells": cells,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"Wrote full results -> {OUT_JSON}")


if __name__ == "__main__":
    main()
