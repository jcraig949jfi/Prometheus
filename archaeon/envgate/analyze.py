"""ENVGATE-01 analysis: frozen with the preregistration (its sha256 is in PREREG.json). Reads runs/block_XX.json, writes RESULTS.json.

Paired unit = ARRIVAL: arrival index a of block b is the same tape, in the same chamber, at the same epoch, in every arm. E_arm(b, a) = 1
iff that arrival founded an ESTABLISHED_RANDOM_INFLOW_LINEAGE in that arm (engine.World.established).

PRIMARY test per contrast (X over Y, predicted X >= Y): exact one-sided McNemar on arrivals discordant between X and Y, pooled over
blocks; Holm-Bonferroni over the four primary contrasts at family alpha 0.05. Robustness (reported, not decisive): exact one-sided sign
test on per-block established-count differences. A contrast with fewer than 5 discordant arrivals cannot reach p < 0.05 and is
reported UNDERPOWERED.

Decision (first match): DESIGN_OR_INSTRUMENT_FAILURE (pairing mismatch, missing/errored block, a control-origin founder scored, any
lineage into a chamber) > NO_ESTABLISHMENT_AT_TESTED_EXPOSURE (0 established in every arm) > GATING_CAUSALLY_SUPPORTED (U>BAND
significant, U vs SHAM not significant and SHAM suppression < half of BAND suppression, RESCUE>BAND significant) >
GATING_PARTIALLY_SUPPORTED (any of U>BAND, U>BLOCK_128, RESCUE>BAND significant) > GATING_NOT_SUPPORTED (none significant, U has >= 5
establishments) > INCONCLUSIVE_LOW_ESTABLISHMENT (none significant, U has 1-4). ALTERNATE_MECHANISM_OBSERVED is reported alongside the
verdict when > 50% of all established lineages have founders the frozen ruler classes as non-copiers (WRITER / TOUCH / INERT); each such
lineage is labelled NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

from archaeon.envgate import mechanism as M

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
CONTRASTS = [("U", "BAND_BLOCK", "C1_gate_band_removed"), ("U", "SHAM_BLOCK", "C2_sham_band_removed"),
             ("U", "BLOCK_128", "C3_dominant_gate_removed"), ("RESCUE_128", "BAND_BLOCK", "C4_dominant_gate_restored")]
COPIER = {"EXACT_UNGATED", "EXACT_GATED", "NEAR_COPIER", "SPAN_COPIER"}


def binom_tail(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def holm(ps: dict, alpha: float = 0.05) -> dict:
    order = sorted(ps, key=lambda k: ps[k]); out = {}; stop = False
    for i, k in enumerate(order):
        thr = alpha / (len(order) - i)
        if not stop and ps[k] <= thr: out[k] = True
        else: stop = True; out[k] = False
    return out


def analyze(blocks: list, expected_blocks: int) -> dict:
    fail = []
    if len(blocks) != expected_blocks: fail.append("blocks present %d of %d" % (len(blocks), expected_blocks))
    E = {a: set() for a in M.ARM_ORDER}; per_block = defaultdict(dict); lin_all = []; hits_all = {}; ruler = Counter(); arrivals = 0
    for b in blocks:
        if len(set(b["pairing_sha256"].values())) != 1: fail.append("pairing mismatch block %s" % b["block"])
        arrivals += b["arrivals"]; ruler.update(b["ruler_counts"])
        for a_idx, h in b["hits"].items(): hits_all[(b["block"], int(a_idx))] = h
        for arm, s in b["arms"].items():
            if s["refused_into_chamber"]: fail.append("birth into chamber %s/%s" % (b["block"], arm))
            per_block[b["block"]][arm] = s["n_established"]
            for x in s["established_arrivals"]: E[arm].add((b["block"], x))
            for r in s["lineages"]:
                if r["established"]:
                    if r["origin"] != "random_inflow": fail.append("non-inflow founder scored %s/%s" % (b["block"], arm))
                    h = hits_all.get((b["block"], r["arrival"])) or b["hits"].get(str(r["arrival"]))
                    lin_all.append(dict(r, block=b["block"], arm=arm, ruler_class=(h or {}).get("class", "NON_COPIER(WRITER/TOUCH/INERT)"),
                                        ruler_exact_inputs=(h or {}).get("exact_inputs", []), ruler_birth_inputs=(h or {}).get("birth_inputs", [])))
    n_est = {a: len(E[a]) for a in M.ARM_ORDER}
    contrasts = {}; ps = {}
    for X, Y, name in CONTRASTS:
        n10 = len(E[X] - E[Y]); n01 = len(E[Y] - E[X]); p = binom_tail(n10, n10 + n01)
        diffs = [per_block[b].get(X, 0) - per_block[b].get(Y, 0) for b in sorted(per_block)]
        pos = sum(d > 0 for d in diffs); neg = sum(d < 0 for d in diffs)
        contrasts[name] = {"X": X, "Y": Y, "established_X": n_est[X], "established_Y": n_est[Y], "discordant_X_only": n10, "discordant_Y_only": n01,
                           "mcnemar_one_sided_p": p, "underpowered": n10 + n01 < 5, "suppression": n10 - n01,
                           "block_diffs": diffs, "block_sign_test_one_sided_p": binom_tail(pos, pos + neg)}
        ps[name] = p
    sig = holm(ps)
    for k in contrasts: contrasts[k]["holm_significant"] = sig[k]
    c1, c2, c3, c4 = (contrasts[n] for _, _, n in CONTRASTS)
    specific = (not c2["holm_significant"]) and (c2["suppression"] < 0.5 * c1["suppression"])
    # latent opportunity (identical across arms except gate availability)
    exact = [h for h in hits_all.values() if h["class"] in ("EXACT_UNGATED", "EXACT_GATED")]
    opp = {a: sum(1 for h in exact if set(h["exact_inputs"]) & M.alphabet(M.ARMS[a])) for a in M.ARM_ORDER}
    g128 = [k for k, h in hits_all.items() if h.get("exact_inputs") == [128]]
    noncop = [r for r in lin_all if r["ruler_class"] not in COPIER]
    alternate = bool(lin_all) and len(noncop) / len(lin_all) > 0.5
    for r in lin_all:
        if r["ruler_class"] not in COPIER: r["label"] = "NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE"
    band_128 = sum(1 for r in lin_all if r["arm"] == "BAND_BLOCK" and r["ruler_exact_inputs"] == [128])
    u_128 = sum(1 for r in lin_all if r["arm"] == "U" and r["ruler_exact_inputs"] == [128])
    falsifiers = {
        "F1_BAND_as_U": (not c1["holm_significant"]) and n_est["U"] >= 5,
        "F2_SHAM_suppresses_like_BAND": c2["holm_significant"] or (c1["suppression"] > 0 and c2["suppression"] >= c1["suppression"]),
        "F3_128_BLOCK_no_effect": (not c3["holm_significant"]) and n_est["U"] >= 5,
        "F4_RESCUE_fails_where_128_copiers_entered": (not c4["holm_significant"]) and any((k in E["U"]) for k in g128),
        "F5_establishment_mostly_from_non_copiers": alternate,
        "F6_128_gated_lineages_establish_without_their_gate": u_128 > 0 and band_128 >= 0.5 * u_128,
        "F7_exposure_or_occupancy_confound": bool(fail),
    }
    if fail: verdict = "DESIGN_OR_INSTRUMENT_FAILURE"
    elif sum(n_est.values()) == 0: verdict = "NO_ESTABLISHMENT_AT_TESTED_EXPOSURE"
    elif c1["holm_significant"] and specific and c4["holm_significant"]: verdict = "GATING_CAUSALLY_SUPPORTED"
    elif c1["holm_significant"] or c3["holm_significant"] or c4["holm_significant"]: verdict = "GATING_PARTIALLY_SUPPORTED"
    elif n_est["U"] >= 5: verdict = "GATING_NOT_SUPPORTED"
    else: verdict = "INCONCLUSIVE_LOW_ESTABLISHMENT"
    return {"schema": "archaeon.envgate.results.v1", "assay": M.ASSAY_ID, "verdict": verdict, "alternate_mechanism_observed": alternate, "failures": fail,
            "blocks": len(blocks), "arrivals_per_arm": arrivals, "ruler_counts_per_arm": dict(ruler),
            "latent": {"exact_copier_arrivals": len(exact), "per_million": round(1e6 * len(exact) / max(1, arrivals), 3),
                       "gated_exact_arrivals": sum(1 for h in exact if h["class"] == "EXACT_GATED"), "gate_128_arrivals": len(g128),
                       "gate_available_exact_arrivals_by_arm": opp, "all_hit_arrivals": len(hits_all)},
            "established_by_arm": n_est, "established_per_million_arrivals": {a: round(1e6 * n_est[a] / max(1, arrivals), 3) for a in M.ARM_ORDER},
            "established_per_latent_exact_copier": {a: round(n_est[a] / max(1, len(exact)), 4) for a in M.ARM_ORDER},
            "per_block": {str(k): v for k, v in sorted(per_block.items())}, "contrasts": contrasts, "specificity_holds": specific,
            "falsifiers": falsifiers, "established_lineages": lin_all}


def main(argv=None) -> int:
    pre = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8"))
    blocks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RUNS.glob("block_*.json"))]
    res = analyze(blocks, len(pre["blocks"]))
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("verdict", "alternate_mechanism_observed", "established_by_arm", "latent")}, default=str))
    for k, v in res["contrasts"].items(): print(k, {x: v[x] for x in ("discordant_X_only", "discordant_Y_only", "mcnemar_one_sided_p", "holm_significant")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
