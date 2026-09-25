"""P-H06 [T-ARCH4/M1, bounded]: (a) reach-weighted scattered damage - the qualified ruler restricted to REACHED
vs UNREACHED instructions at f .10; (b) the slot ordering within reached code (from P-G07's rows); (c)
the P-G07 promotion rule re-evaluated on a FLOOR-CONDITIONED held-out family. Computational scope:
integer programs on a bounded VM.
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
sys.path.insert(0, str(HERE.parent / "P-G07"))
from run_PD01 import c408_tops, reduced_class   # noqa: E402
from run_PG07 import HELD, wilson   # noqa: E402

PID, TID, F = "P-H06", "T-ARCH4/M1", 0.10


def job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    n = CM.n_instr(pm)
    pev = A.eval_all(pm, {env: eps})
    if pev[env]["answered_share"] == 0.0 or n < 4:
        return {"pid": p["organism_id"], "skipped": True}
    reach = SC.reach_map(pm, eps)
    out = {"pid": p["organism_id"], "set": p["stratum"], "reached_share": float(np.mean(reach)), "loss": {}}
    for which in ("reached", "unreached"):
        el = [i for i in range(n) if reach[i] == (which == "reached")]
        if not el:
            out["loss"][which] = None
            continue
        ls = []
        for d in range(1, 5):
            r2 = A.SplitMix64(A.seed_from("nestor.ph06", A.LOOP_SEED, p["organism_id"], which, d))
            msk = [False] * n
            for i in el:
                msk[i] = r2.unit() < F
            child = SC.apply(pm, msk, "delete", (p["organism_id"], which, F, d))
            cev = A.eval_all(child, {env: eps})
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            ls.append(int(reduced_class(cev, pev, disp, env) in ("D2", "D3")))
        out["loss"][which] = float(np.mean(ls))
    heps = {k: A.episodes_for(s, A.CAMPAIGN_SEED, "train", 1, A.C1.E) for k, s in HELD.items()}
    out["held_baseline"] = {k: A.evaluate(pm, e, rng_seed=0, reward_mode="per_ask")["reward_per_ask"] for k, e in heps.items()}
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "bounded-secondary", "f": F, "draws": 4,
                         "readouts": ["loss under scattered deletion restricted to reached vs unreached instructions", "slot ordering within reached rows of P-G07 (Wilson)", "P-G07 promotion rule on programs whose held-out baseline is above the floor"],
                         "material_rule": "reached-only loss exceeds unreached-only loss with disjoint Wilson bands, or the floor-conditioned rule promotes / refutes the slot ordering", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = [r for r in ex.map(job, [{"program": p} for p in programs]) if not r.get("skipped")]
    lr = [r["loss"]["reached"] for r in rows if r["loss"].get("reached") is not None]
    lu = [r["loss"]["unreached"] for r in rows if r["loss"].get("unreached") is not None]
    reach_loss = {"reached": float(np.mean(lr)), "unreached": float(np.mean(lu)), "n": (len(lr), len(lu)), "wilson_reached": wilson(int(round(sum(lr))), len(lr)), "wilson_unreached": wilson(int(round(sum(lu))), len(lu))}
    disjoint = reach_loss["wilson_reached"][0] > reach_loss["wilson_unreached"][1]
    # (b) slot ordering within reached rows of P-G07
    g7 = json.loads((HERE.parent / "P-G07" / "rows.json").read_text(encoding="utf-8"))
    rr = [dict(x, set=r["set"], pid=r["pid"]) for r in g7 for x in r["rows"] if x["reached"]]
    slot_reached = {s: {"n": len([x for x in rr if x["slot"] == s]), "loss": float(np.mean([x["loss"] for x in rr if x["slot"] == s])), "wilson": wilson(sum(x["loss"] for x in rr if x["slot"] == s), len([x for x in rr if x["slot"] == s]))} for s in "abc"}
    # (c) floor-conditioned promotion: programs with held-out baseline >= FLOOR on a family; ordering a < c on held deltas per stratum
    base = {r["pid"]: r["held_baseline"] for r in rows}
    promo = {}
    for k in HELD:
        ok_pids = {pid for pid, b in base.items() if b[k] >= A.C1.FLOOR}
        strata = {}
        for r in g7:
            if r["pid"] not in ok_pids:
                continue
            for x in r["rows"]:
                strata.setdefault(r["set"], {}).setdefault(x["slot"], []).append(x["held_" + k])
        promo[k] = {st: {s: (float(np.mean(v[s])), len(v[s])) for s in "abc" if s in v} for st, v in strata.items()}
        promo[k]["ordering_holds_in_every_stratum"] = all(("a" in v and "c" in v and np.mean(v["a"]) < np.mean(v["c"])) for v in strata.values()) if strata else None
        promo[k]["n_programs"] = len(ok_pids)
    promoted = all(v["ordering_holds_in_every_stratum"] for v in promo.values() if v["ordering_holds_in_every_stratum"] is not None) and slot_reached["a"]["wilson"][0] > slot_reached["c"]["wilson"][1]
    material = bool(disjoint or promoted)
    out = {"perturbation_id": PID, "parent": TID, "reach_loss": reach_loss, "reach_bands_disjoint": disjoint, "slot_within_reached": slot_reached, "floor_conditioned_promotion": promo, "slot_ordering_promoted": promoted, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "reach-weighted damage: reached %.3f vs unreached %.3f (disjoint %s); slot within reached %s; floor-conditioned promotion %s -> promoted %s" % (reach_loss["reached"], reach_loss["unreached"], disjoint, {s: round(v["loss"], 3) for s, v in slot_reached.items()}, {k: (v["ordering_holds_in_every_stratum"], v["n_programs"]) for k, v in promo.items()}, promoted), material, detail={"reach": reach_loss, "slot": slot_reached, "promo": promo})
    print("DONE material=%s reached %.3f unreached %.3f promoted %s (%.0f s)" % (material, reach_loss["reached"], reach_loss["unreached"], promoted, time.time() - t0))


if __name__ == "__main__":
    main()
