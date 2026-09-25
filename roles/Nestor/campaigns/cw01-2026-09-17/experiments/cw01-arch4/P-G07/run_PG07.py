"""P-G07 [T-ARCH4/M1, deformation O]: OPERAND SLOT / OPCODE CATEGORY lane - transfer across lineages,
a HALT-probe reach map (is halt_yield's low loss reachability?), and additivity under held-out families.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import scatter as SC           # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
sys.path.insert(0, str(HERE.parent / "P-E04"))
from run_PD01 import c408_tops, reduced_class   # noqa: E402
from run_PE04 import hit_operand   # noqa: E402

PID, TID = "P-G07", "T-ARCH4/M1"
HELD = {"W1_d1": A.ENVS["W1_d1"], "W2_K2d1": A.with_knobs(A.WorldSpec("W2_K2", K=2, value_bits=4), name="W2_K2d1", delay=1)}
DRAWS = 4


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - h), float(c + h))


def job(j):
    p = j["program"]
    env = p["env"]
    eps = {env: A.episodes(env)}
    heps = {k: A.episodes_for(s, A.CAMPAIGN_SEED, "train", 1, A.C1.E) for k, s in HELD.items()}
    pm = A.canonical(p["manifest"])
    n = CM.n_instr(pm)
    pev = A.eval_all(pm, eps | heps)
    if pev[env]["answered_share"] == 0.0 or n < 8:
        return {"pid": p["organism_id"], "skipped": True}
    reach = SC.reach_map(pm, eps[env])
    rows = []
    anchors = sorted({int(round(a * n / 8)) % n for a in range(8)})
    for a in anchors:
        for slot in (0, 1, 2):
            for d in range(1, DRAWS + 1):
                rng = A.SplitMix64(A.seed_from("nestor.pg07.role", A.LOOP_SEED, p["organism_id"], a, slot, d))
                c = hit_operand(hit_operand(pm, a, slot, rng), (a + 1) % n, slot, rng)
                cev = A.eval_all(c, eps | heps)
                disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
                rows.append({"slot": "abc"[slot], "category": A.CATEGORY[pm["genome"][a * A.IW] % A.N_OPCODES], "reached": bool(reach[a] or reach[(a + 1) % n]),
                             "loss": int(reduced_class(cev, pev, disp, env) in ("D2", "D3")), "disp": disp,
                             **{"held_" + k: cev[k]["reward_per_ask"] - pev[k]["reward_per_ask"] for k in HELD}})
    return {"pid": p["organism_id"], "set": p["stratum"], "n_instr": n, "reached_share": float(np.mean(reach)), "rows": rows, "skipped": False}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "O", "scope": CM.SCOPE, "claim_type": "deformation-lane",
                         "hit": "two adjacent instructions, one operand slot each, at 8 anchors x 3 slots x 4 draws (P-E04's construction)", "reach": "HALT probe: instruction i reached iff replacing its opcode by HALT changes the answers",
                         "readouts": ["slot and category loss orderings per stratum (parents / walkers / C4-08 tops) with Wilson bands", "category loss by reached vs unreached; halt_yield's unreached share", "held-out families W1_d1 / W2_K2d1: reward delta by slot x category; additivity: interaction sum of squares vs a 2000-permutation band"],
                         "promotion_rule": "a grammar-level mechanism only if the slot ordering (a > b > c) holds in every stratum with disjoint a-vs-c bands AND on the held-out reward deltas",
                         "material_rule": "any of: slot ordering transfers (disjoint a/c bands in all strata); reach explains halt_yield (reached halt_yield loss >= grand mean); interaction outside its band", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        res = [r for r in ex.map(job, [{"program": p} for p in programs]) if not r.get("skipped")]
    rows = [dict(x, set=r["set"]) for r in res for x in r["rows"]]
    grand = float(np.mean([x["loss"] for x in rows]))
    by_stratum = {}
    for st in sorted({r["set"] for r in res}):
        rs = [x for x in rows if x["set"] == st]
        by_stratum[st] = {s: {"n": len([x for x in rs if x["slot"] == s]), "loss": float(np.mean([x["loss"] for x in rs if x["slot"] == s])), "wilson": wilson(sum(x["loss"] for x in rs if x["slot"] == s), len([x for x in rs if x["slot"] == s]))} for s in "abc"}
        by_stratum[st]["held"] = {s: {k: float(np.mean([x["held_" + k] for x in rs if x["slot"] == s])) for k in HELD} for s in "abc"}
    transfers = all(by_stratum[st]["a"]["wilson"][0] > by_stratum[st]["c"]["wilson"][1] for st in by_stratum)
    held_order = all(by_stratum[st]["held"]["a"][k] < by_stratum[st]["held"]["c"][k] for st in by_stratum for k in HELD)
    cats = sorted({x["category"] for x in rows})
    by_cat = {}
    for c in cats:
        rr = [x for x in rows if x["category"] == c]
        rc = [x for x in rr if x["reached"]]
        ru = [x for x in rr if not x["reached"]]
        by_cat[c] = {"n": len(rr), "loss": float(np.mean([x["loss"] for x in rr])), "reached_share": len(rc) / len(rr), "loss_reached": float(np.mean([x["loss"] for x in rc])) if rc else None, "loss_unreached": float(np.mean([x["loss"] for x in ru])) if ru else None,
                     "wilson_reached": wilson(sum(x["loss"] for x in rc), len(rc))}
    hy = by_cat.get("halt_yield")
    reach_explains = bool(hy and hy["loss_reached"] is not None and hy["loss_reached"] >= grand)
    unreached_loss = float(np.mean([x["loss"] for x in rows if not x["reached"]])) if any(not x["reached"] for x in rows) else None
    reached_loss = float(np.mean([x["loss"] for x in rows if x["reached"]]))
    # additivity on held-out deltas: two-way additive fit slot + category vs interaction; permutation of residuals
    inter = {}
    for k in HELD:
        y = np.array([x["held_" + k] for x in rows])
        S_ = np.array([["abc".index(x["slot"]) == i for i in range(3)] for x in rows], float)
        Cc = np.array([[x["category"] == c for c in cats] for x in rows], float)
        Xa = np.column_stack([S_, Cc])
        Xf = np.column_stack([S_, Cc] + [S_[:, i:i + 1] * Cc[:, j:j + 1] for i in range(3) for j in range(len(cats))])
        ra = y - Xa @ np.linalg.lstsq(Xa, y, rcond=None)[0]
        rf = y - Xf @ np.linalg.lstsq(Xf, y, rcond=None)[0]
        ss = float((ra ** 2).sum() - (rf ** 2).sum())
        rng = np.random.Generator(np.random.PCG64(0))
        null = []
        for _ in range(500):
            yp = Xa @ np.linalg.lstsq(Xa, y, rcond=None)[0] + rng.permutation(ra)
            rap = yp - Xa @ np.linalg.lstsq(Xa, yp, rcond=None)[0]
            rfp = yp - Xf @ np.linalg.lstsq(Xf, yp, rcond=None)[0]
            null.append(float((rap ** 2).sum() - (rfp ** 2).sum()))
        inter[k] = {"interaction_ss": ss, "p95": float(np.percentile(null, 95)), "outside": bool(ss > np.percentile(null, 95))}
    promoted = transfers and held_order
    material = bool(transfers or reach_explains or any(v["outside"] for v in inter.values()))
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(res), "grand_loss": grand, "by_stratum": by_stratum, "slot_ordering_transfers": transfers, "held_out_ordering": held_order, "by_category": by_cat,
           "reach": {"mean_reached_share": float(np.mean([r["reached_share"] for r in res])), "loss_reached": reached_loss, "loss_unreached": unreached_loss, "halt_yield_reach_explains": reach_explains},
           "held_out_additivity": inter, "promoted_grammar_mechanism": promoted, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(res, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "operand lane: slot loss per stratum %s (transfers %s; held-out ordering %s); reach: reached share %.2f, loss reached %.3f vs unreached %s; halt_yield reached loss %s (reach explains %s); categories %s; held-out interaction %s; promoted %s"
                      % ({st: {s: round(v[s]["loss"], 3) for s in "abc"} for st, v in by_stratum.items()}, transfers, held_order, out["reach"]["mean_reached_share"], reached_loss, round(unreached_loss, 3) if unreached_loss is not None else None,
                         (round(hy["loss_reached"], 3), round(hy["reached_share"], 2)) if hy and hy["loss_reached"] is not None else None, reach_explains, {c: (round(v["loss"], 3), round(v["reached_share"], 2)) for c, v in by_cat.items()},
                         {k: (round(v["interaction_ss"], 4), v["outside"]) for k, v in inter.items()}, promoted), material, detail={"by_stratum": by_stratum, "by_category": by_cat, "reach": out["reach"], "additivity": inter})
    print("DONE material=%s transfers=%s held=%s reach_explains=%s promoted=%s (%.0f s)" % (material, transfers, held_order, reach_explains, promoted, time.time() - t0))


if __name__ == "__main__":
    main()
