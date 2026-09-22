"""P-C05 [T-ARCH4/M1, one-axis-census]: OPERAND-only vs OPCODE-only single-word edits on the viable parents
(P-D01's damage operator, k = 1, 8 draws per parent per family, modulo decode), classified by P-D01's
reduced classes on W2_K2 (loss = D2/D3), with displacement and the W1_d1 held-out change. Is the damage
cliff an opcode phenomenon? Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARCH = HERE.parents[1] / "cw01-arch4"
sys.path.insert(0, str(ARCH))
import common as CM            # noqa: E402
import evolver as EV           # noqa: E402
sys.path.insert(0, str(ARCH / "P-D01"))
from run_PD01 import damage, windows, reduced_class   # noqa: E402
A, L = CM.A, CM.L
PID, TID = "P-C05", "T-ARCH4/M1"
ENV, DRAWS = EV.ENV, 8


def job(p):
    eps = {ENV: A.episodes(ENV), "HELD": A.episodes_for(EV.HELD, A.CAMPAIGN_SEED, "train", 1, A.C1.E)}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    n = CM.n_instr(pm)
    rows = []
    for kind in ("opcode", "operand"):
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("nestor.pc05", A.LOOP_SEED, p["organism_id"], kind, d))
            wins = windows(n, 1, 1, "even", rng)
            child = damage(pm, kind, wins, rng, "modulo")
            cev = A.eval_all(child, eps)
            disp = A.C1.displacement(cev[ENV]["_answers"], pev[ENV]["_answers"])
            D = reduced_class(cev, pev, disp, ENV)
            rows.append({"kind": kind, "draw": d, "D": D, "loss": int(D in ("D2", "D3")), "disp": disp, "held_delta": cev["HELD"]["reward_per_ask"] - pev["HELD"]["reward_per_ask"]})
    return {"organism_id": p["organism_id"], "stratum": p["stratum"], "n_instr": n, "r0": pev[ENV]["reward_per_ask"], "rows": rows,
            **{"%s_%s" % (kind, k): float(np.mean([r[k] for r in rows if r["kind"] == kind])) for kind in ("opcode", "operand") for k in ("loss", "disp", "held_delta")}}


def main():
    t0 = time.time()
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "one-axis-census", "parents": len(parents), "families": ["opcode (word 0 := random uint32)", "operand (one of words 1..3 := random uint32)"], "k": 1, "draws": DRAWS, "decode": "modulo",
                         "readouts": "loss share (D2/D3), displacement, W1_d1 held-out change; paired opcode - operand per parent with a sign-flip test", "material_rule": "material if the paired loss difference's 95 percent band excludes 0", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(8) as ex:
        rows = list(ex.map(job, parents))
    diffs = [r["opcode_loss"] - r["operand_loss"] for r in rows]
    sf = CM.paired_signflip(diffs)
    summary = {"n_parents": len(rows), "opcode_loss": float(np.mean([r["opcode_loss"] for r in rows])), "operand_loss": float(np.mean([r["operand_loss"] for r in rows])),
               "opcode_disp": float(np.mean([r["opcode_disp"] for r in rows])), "operand_disp": float(np.mean([r["operand_disp"] for r in rows])),
               "opcode_held_delta": float(np.mean([r["opcode_held_delta"] for r in rows])), "operand_held_delta": float(np.mean([r["operand_held_delta"] for r in rows])), "paired_loss_diff": sf,
               "by_stratum": {s: {"opcode_loss": float(np.mean([r["opcode_loss"] for r in rows if r["stratum"] == s])), "operand_loss": float(np.mean([r["operand_loss"] for r in rows if r["stratum"] == s]))} for s in sorted({r["stratum"] for r in rows})}}
    material = bool(sf and (sf["above_p95"] or sf["below_p05"]))      # the sign-flip band is (p05, p95); fixed after run 1 read False from a missing key (D091)
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "single-word edits: opcode loss %.3f vs operand loss %.3f (paired %s); displacement %.3f vs %.3f; held delta %.3f vs %.3f; by stratum %s" % (
        summary["opcode_loss"], summary["operand_loss"], sf, summary["opcode_disp"], summary["operand_disp"], summary["opcode_held_delta"], summary["operand_held_delta"], summary["by_stratum"]), material, detail=summary)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:800])


if __name__ == "__main__":
    main()
