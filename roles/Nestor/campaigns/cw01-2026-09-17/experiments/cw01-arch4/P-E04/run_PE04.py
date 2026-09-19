"""P-E04 [deformation A, T-ARCH4/M1]: NEW COORDINATES for the damage surface.

(i) OPERAND ROLE MAP: a single operand hit (k=2 instructions, one site) by operand SLOT (a: register
field, b, c) x opcode CATEGORY of the hit instruction (static; the dynamic-reach axis of the candidate
is dropped: the frozen VM exposes no per-instruction execution trace - translation loss recorded).
(ii) FIXED-k PAIRWISE SITE INTERACTION: k=4 as two 2-instruction windows at anchor sites i, j (4
evenly spaced anchors, 6 pairs) vs each site alone (k=2): loss(i+j) against 1-(1-loss_i)(1-loss_j).
(iii) HELD-OUT FAMILIES: delete k=4 at 1 and 4 sites scored on W0_heldout, W1_d1, W1_d4, W2_K2d1.
Programs: viable parents, walker-16, C4-08 tops; modulo decode; 4 draws. Computational scope:
integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from itertools import combinations

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops, damage, reduced_class   # noqa: E402

PID, TID = "P-E04", "T-ARCH4/M1"
HELD = {"W0_heldout": A.ENVS["W0_heldout"], "W1_d1": A.ENVS["W1_d1"], "W1_d4": A.ENVS["W1_d4"], "W2_K2d1": A.with_knobs(A.WorldSpec("W2_K2", K=2, value_bits=4), name="W2_K2d1", delay=1)}
DRAWS = 4


def hit_operand(m, i, slot, rng):
    c = json.loads(json.dumps(m))
    c["genome"][i * A.IW + 1 + slot] = int(rng.next_u32())
    return c


def job(j):
    p = j["program"]
    env = p["env"]
    eps = {env: A.episodes(env)}
    heps = {k: A.episodes_for(spec, A.CAMPAIGN_SEED, "train", 1, A.C1.E) for k, spec in HELD.items()}
    pm = A.canonical(p["manifest"])
    n = CM.n_instr(pm)
    pev = A.eval_all(pm, eps | heps)
    if pev[env]["answered_share"] == 0.0 or n < 8:
        return {"pid": p["organism_id"], "skipped": True}
    role, pair_rows, held_rows = [], [], []
    # (i) role map: two adjacent instructions, one operand slot each, at 4 anchors
    anchors = [int(round(a * n / 4)) % n for a in range(4)]
    for a in anchors:
        for slot in (0, 1, 2):
            for d in range(1, DRAWS + 1):
                rng = A.SplitMix64(A.seed_from("nestor.pe04.role", A.LOOP_SEED, p["organism_id"], a, slot, d))
                c = hit_operand(hit_operand(pm, a, slot, rng), (a + 1) % n, slot, rng)
                cev = A.eval_all(c, eps)
                disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
                role.append({"slot": "abc"[slot], "category": A.CATEGORY[pm["genome"][a * A.IW] % A.N_OPCODES], "loss": int(reduced_class(cev, pev, disp, env) in ("D2", "D3")), "disp": disp})
    # (ii) pairwise: single 2-windows at anchors vs pairs
    single = {}
    for a in anchors:
        ls = []
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("nestor.pe04.single", A.LOOP_SEED, p["organism_id"], a, d))
            c = damage(pm, "delete", [[a, (a + 1) % n]], rng, "modulo")
            cev = A.eval_all(c, eps)
            ls.append(int(reduced_class(cev, pev, A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"]), env) in ("D2", "D3")))
        single[a] = float(np.mean(ls))
    for a, b in combinations(anchors, 2):
        ls = []
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("nestor.pe04.pair", A.LOOP_SEED, p["organism_id"], a, b, d))
            c = damage(pm, "delete", [[a, (a + 1) % n], [b, (b + 1) % n]], rng, "modulo")
            cev = A.eval_all(c, eps)
            ls.append(int(reduced_class(cev, pev, A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"]), env) in ("D2", "D3")))
        joint = float(np.mean(ls))
        indep = 1 - (1 - single[a]) * (1 - single[b])
        pair_rows.append({"i": a, "j": b, "loss_i": single[a], "loss_j": single[b], "loss_ij": joint, "independence": indep, "epistasis": joint - indep})
    # (iii) held-out families
    for s in (1, 4):
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("nestor.pe04.held", A.LOOP_SEED, p["organism_id"], s, d))
            wins = [[(anchors[i] + t) % n for t in range(4 // s)] for i in range(s)] if s == 4 else [[(anchors[0] + t) % n for t in range(4)]]
            c = damage(pm, "delete", wins, rng, "modulo")
            cev = A.eval_all(c, eps | heps)
            row = {"s": s, "loss": int(reduced_class(cev, pev, A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"]), env) in ("D2", "D3"))}
            for k in HELD:
                row[k + "_delta"] = cev[k]["reward_per_ask"] - pev[k]["reward_per_ask"]
                row[k + "_exapt"] = int(cev[k]["reward_per_ask"] >= pev[k]["reward_per_ask"] + A.C1.BAND and cev[k]["reward_per_ask"] >= A.C1.FLOOR)
            held_rows.append(row)
    return {"pid": p["organism_id"], "set": p["stratum"], "n_instr": n, "role": role, "pairs": pair_rows, "held": held_rows, "skipped": False}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "scope": CM.SCOPE, "claim_type": "parameterized-dose-surface",
                         "coordinates": {"role": "operand slot (a/b/c) x static opcode category of the hit instruction; k=2 adjacent instructions at 4 anchors; DYNAMIC REACH DROPPED (no per-instruction trace in the frozen VM) - translation loss",
                                         "pairwise": "k=4 as two 2-windows at anchor pairs (6) vs each window alone; epistasis = loss_ij - [1-(1-loss_i)(1-loss_j)]",
                                         "held_out": "delete k=4 at 1 / 4 sites scored on W0_heldout, W1_d1, W1_d4, W2_K2d1 (reward delta, exaptation)"},
                         "draws": DRAWS, "programs": "viable parents, walker-16, C4-08 tops (n >= 8 instructions)",
                         "material_rule": "role: any slot or category marginal differs from the grand mean with a disjoint Wilson band; pairwise: mean epistasis outside its sign-flip band; held-out: exaptation rate on any family >= .05 with Wilson lower bound > 0",
                         "continuation": ["triples", "role map under trap-NOP", "reach via a HALT probe"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = [r for r in ex.map(job, [{"program": p} for p in programs]) if not r.get("skipped")]
    role = [x for r in rows for x in r["role"]]
    grand = float(np.mean([x["loss"] for x in role]))

    def wilson(k, n, z=1.96):
        if n == 0:
            return (0.0, 0.0)
        p = k / n
        den = 1 + z * z / n
        c = (p + z * z / (2 * n)) / den
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        return (float(c - h), float(c + h))
    by_slot = {s: {"n": len([x for x in role if x["slot"] == s]), "loss": float(np.mean([x["loss"] for x in role if x["slot"] == s])), "wilson": wilson(sum(x["loss"] for x in role if x["slot"] == s), len([x for x in role if x["slot"] == s]))} for s in "abc"}
    cats = sorted({x["category"] for x in role})
    by_cat = {c: {"n": len([x for x in role if x["category"] == c]), "loss": float(np.mean([x["loss"] for x in role if x["category"] == c])), "wilson": wilson(sum(x["loss"] for x in role if x["category"] == c), len([x for x in role if x["category"] == c]))} for c in cats}
    role_material = any(v["wilson"][0] > grand or v["wilson"][1] < grand for v in list(by_slot.values()) + [v for v in by_cat.values() if v["n"] >= 40])
    pairs = [x for r in rows for x in r["pairs"]]
    epi = CM.paired_signflip([x["epistasis"] for x in pairs])
    epi_by_prog = CM.paired_signflip([float(np.mean([x["epistasis"] for x in r["pairs"]])) for r in rows if r["pairs"]])
    held = [x for r in rows for x in r["held"]]
    held_summ = {}
    for k in HELD:
        for s in (1, 4):
            xs = [x for x in held if x["s"] == s]
            ke = sum(x[k + "_exapt"] for x in xs)
            held_summ["%s|s%d" % (k, s)] = {"n": len(xs), "delta": float(np.mean([x[k + "_delta"] for x in xs])), "exapt": ke / len(xs), "wilson": wilson(ke, len(xs)), "loss": float(np.mean([x["loss"] for x in xs]))}
    held_material = any(v["exapt"] >= 0.05 and v["wilson"][0] > 0 for v in held_summ.values())
    material = bool(role_material or (epi and (epi["above_p95"] or epi["below_p05"])) or held_material)
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(rows), "grand_loss": grand, "role_by_slot": by_slot, "role_by_category": by_cat, "epistasis": {"per_pair": epi, "per_program": epi_by_prog, "n_pairs": len(pairs)},
           "held_out": held_summ, "flags": {"role": role_material, "held": held_material}, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "surface coordinates: operand loss by slot %s (grand %.3f); by category %s; pairwise epistasis %s (per program %s); held-out %s"
                      % ({k: (round(v["loss"], 3), v["n"]) for k, v in by_slot.items()}, grand, {k: (round(v["loss"], 3), v["n"]) for k, v in by_cat.items()},
                         (round(epi["mean_diff"], 3), epi["above_p95"], epi["below_p05"], epi["n"]) if epi else None, (round(epi_by_prog["mean_diff"], 3), epi_by_prog["above_p95"], epi_by_prog["below_p05"]) if epi_by_prog else None,
                         {k: (round(v["delta"], 3), round(v["exapt"], 3)) for k, v in held_summ.items()}), material, detail={"slot": by_slot, "category": by_cat, "epistasis": epi, "held": held_summ})
    print("DONE material=%s (%.0f s) slot %s | cat %s | epi %s | held %s" % (material, time.time() - t0, {k: round(v["loss"], 3) for k, v in by_slot.items()}, {k: round(v["loss"], 3) for k, v in by_cat.items()}, epi and round(epi["mean_diff"], 3), {k: round(v["exapt"], 3) for k, v in held_summ.items()}))


if __name__ == "__main__":
    main()
