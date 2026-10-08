"""PTE-C4 s8 diagnostic library D-LIB (PREREG_PTE_C4 s7): the GATE plant decomposed into its two designed halves.
  CONTEXT half: gate_plant body lines 11-13 (latch the actuator-sensed context sign into S2)
  CUE half:     gate_plant body lines 0-10 and 14 (relay the cue sign into S1, emit on change, readout S0 = S1 * S2)
Only LIVE lines (line ablation on 32 fresh worlds) are kept, in program order, per admitted GATE cell physics.
Known answers (checked, recorded; the build refuses on failure): halves re-assembled in plant order with identity
renaming reproduce the plant's per-trial outputs; each half alone is NOT competent (RELAY-mh role).
The halves are designed parts, used ONLY in diagnostic arm D; they never enter the evolved library.
usage: python build_dlib.py ADMISSION.json OUT.json"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataclasses  # noqa: E402

import numpy as np  # noqa: E402

import c4_common as K  # noqa: E402
import run_c4 as RC  # noqa: E402
C = K.C; R = K.R
from prometheus.ananke import assays  # noqa: E402

CONTEXT_LINES = (11, 12, 13)


def halves(ph, env, seeds):
    g = K.gate_plant(ph)
    live, base = K.live_lines(ph, env, g, seeds, "RELAY-mh")
    ctx = [i for i in live if i in CONTEXT_LINES]
    cue = [i for i in live if i not in CONTEXT_LINES]
    return g, live, ctx, cue


def place(shape, lines):
    """A genome of NOPs (all fields 0; op 0 = NOP) with `lines` (rule-0 rows) written at their original positions."""
    g = np.zeros(shape, np.int64)
    for i, row in lines:
        g[:, i] = row
    return g


def main(adm_p, out_p):
    adm = json.load(open(adm_p))
    P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
    cells = [c for c in P["cells"] if c["role"] == "FLIP" and adm[f"{c['cell_id']}|GATE"]["admitted"]]
    mods, checks = [], []
    for c in cells:
        ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), "R4")
        env = RC.task_env(c, "GATE")
        seeds = assays.world_seeds(C.H_int(RC.C4_NS, 0xD11B, c["cell_key"]), 32)
        g, live, ctx, cue = halves(ph, env, seeds)
        both = place(g.shape, [(i, g[0, i]) for i in live])
        only_ctx = place(g.shape, [(i, g[0, i]) for i in ctx])
        only_cue = place(g.shape, [(i, g[0, i]) for i in cue])
        hs = assays.world_seeds(C.H_int(RC.C4_NS, 0xD11C, c["cell_key"]), 128)
        pt, ep = C.eval_programs(ph, env, hs, [g, both, only_ctx, only_cue], device="cpu")
        st = [C.competence("RELAY-mh", pt[k], ep)["status"] for k in range(4)]
        ok = st[0] == "TRUE" and np.array_equal(pt[0], pt[1]) and st[2] != "TRUE" and st[3] != "TRUE" and ctx and cue
        checks.append({"cell_id": c["cell_id"], "live": live, "context_lines": ctx, "cue_lines": cue,
                       "status_plant_reassembled_ctx_cue": st, "reassembled_identical": bool(np.array_equal(pt[0], pt[1])),
                       "pass": bool(ok)})
        print(c["cell_id"], "live", live, "ctx", ctx, "cue", cue, st, "PASS" if ok else "FAIL", flush=True)
        if not ok:
            raise SystemExit("D-LIB known-answer check FAILED at " + c["cell_id"])
        for name, idx in (("GATE_CONTEXT_HALF", ctx), ("GATE_CUE_HALF", cue)):
            mods.append({"id": len(mods) + 1, "name": name, "cell_id": c["cell_id"],
                         "lines": [g[0, i].tolist() for i in idx], "source_lines": idx})
    C.jdump(out_p, {"schema": "pte_c4.dlib.v1", "modules_per_cell": True, "modules": mods, "checks": checks})


if __name__ == "__main__":
    main(*sys.argv[1:3])
