"""Fossil metabolism S2 phase 2: the multi-fossil census (a census, not an
experiment; submits nothing).

For every bitstring landscape (seed_root, length) with >= 2 usable fossils
in the evidence corpus, run the exact solver and report what the fossils
jointly determine, what remains ambiguous, and whether an inference-derived
proposal (the posterior mode under a uniform prior over the feasible set)
would differ from (a) the S1 one-bit rule and (b) the uniform control.

Usable fossil: an ENGINE_WORK_RESULT observation whose content carries
result.bits (0/1 string of the landscape's length) and result.score.
"""
from __future__ import annotations

import collections
import hashlib
import json
from math import comb
from typing import Any, Dict, List, Optional

from . import fossil_inference as FI


def landscape_fossils(corpus, worlds_meta: Dict[str, Dict[str, Any]], content_of) -> Dict[tuple, List[Dict[str, Any]]]:
    """Group corpus rows by (seed_root, length). `worlds_meta[world_id]` must
    carry seed_root; `content_of(row)` returns the observation content."""
    out: Dict[tuple, List[Dict[str, Any]]] = collections.defaultdict(list)
    for r in corpus.rows:
        w = worlds_meta.get(r.region) or {}
        c = content_of(r) or {}
        res = c.get("result") if isinstance(c.get("result"), dict) else c
        bits = res.get("bits"); L = res.get("length"); sc = res.get("score")
        if not (isinstance(bits, str) and isinstance(L, int) and len(bits) == L and sc is not None and w.get("seed_root") is not None):
            continue
        out[(int(w["seed_root"]), int(L))].append({"world_id": r.region, "obs_id": r.row_id, "exp_id": r.anchors.get("exp_id"), "seq": r.seq, "bits": bits, "score": float(sc)})
    return dict(out)


def flip_position(pair_id: str, L: int) -> int:
    return int(hashlib.sha256(("S1-flip:" + pair_id).encode()).hexdigest(), 16) % L


def census_landscape(key, fossils: List[Dict[str, Any]]) -> Dict[str, Any]:
    seed_root, L = key
    fs = [FI.Fossil(f["bits"], f["score"]) for f in fossils]
    rec: Dict[str, Any] = {"seed_root": seed_root, "length": L, "n_fossils": len(fossils), "n_distinct": len(set(fs)),
                           "fossils": sorted(fossils, key=lambda f: f["seq"])}
    try:
        inf = FI.infer(fs)
    except FI.Contradiction as exc:
        rec.update({"contradiction": str(exc)}); return rec
    # information added by each fossil, in ledger order: feasible-set size after each prefix (order used only for this report)
    prefix_sizes = []
    for i in range(1, len(fs) + 1):
        try:
            prefix_sizes.append(FI.infer(sorted(fossils, key=lambda f: f["seq"])[:i] and [FI.Fossil(f["bits"], f["score"]) for f in sorted(fossils, key=lambda f: f["seq"])[:i]]).feasible_targets)
        except FI.Contradiction:
            prefix_sizes.append(0)
    best = max(fossils, key=lambda f: (f["score"], -f["seq"]))
    mode = FI.posterior_mode(inf, tie_break=best["bits"])
    e_mode = FI.expected_score(inf, mode); e_best = FI.expected_score(inf, best["bits"])
    s = best["score"]; e_onebit = s + (1 - 2 * s) / L
    pid = "s2-" + str(seed_root)
    onebit = best["bits"]; pos = flip_position(pid, L); onebit = onebit[:pos] + ("1" if onebit[pos] == "0" else "0") + onebit[pos + 1:]
    rec.update({"feasible_targets": inf.feasible_targets, "log2_feasible": inf.feasible_targets.bit_length() - 1, "prior_log2": L,
                "prefix_feasible_sizes_ledger_order": prefix_sizes, "status": inf.status(),
                "fixed_bits": {str(k): v for k, v in sorted(inf.fixed_bits.items())}, "n_fixed": inf.n_fixed,
                "count_known_blocks": inf.count_known_blocks, "ambiguous_blocks": len(inf.ambiguous_blocks),
                "best_fossil": best, "posterior_mode": mode, "E_score_mode": e_mode, "E_score_best_fossil_as_proposal": e_best,
                "E_score_onebit_rule": e_onebit, "E_score_uniform": 0.5,
                "mode_differs_from_best": mode != best["bits"], "mode_differs_from_onebit": mode != onebit, "hamming_mode_vs_best": sum(a != b for a, b in zip(mode, best["bits"])),
                "F2_advantage_over_onebit": e_mode - e_onebit, "F2_advantage_over_uniform": e_mode - 0.5})
    return rec


def run_census(corpus, worlds_meta, content_of) -> Dict[str, Any]:
    groups = landscape_fossils(corpus, worlds_meta, content_of)
    multi = {k: v for k, v in groups.items() if len({(f["bits"], f["score"]) for f in v}) >= 2}
    recs = [census_landscape(k, v) for k, v in sorted(multi.items())]
    return {"landscapes_total": len(groups), "landscapes_multi_fossil": len(multi), "single_fossil_landscapes": len(groups) - len(multi),
            "records": recs,
            "summary": {"contradictions": sum(1 for r in recs if "contradiction" in r), "with_fixed_bits": sum(1 for r in recs if r.get("n_fixed")),
                        "mode_differs_from_onebit": sum(1 for r in recs if r.get("mode_differs_from_onebit")),
                        "F2_beats_onebit_by_ge_1_over_L": sum(1 for r in recs if r.get("F2_advantage_over_onebit", 0) >= 1.0 / r["length"] - 1e-12),
                        "median_log2_feasible": sorted(r.get("log2_feasible", 0) for r in recs)[len(recs) // 2] if recs else None}}
