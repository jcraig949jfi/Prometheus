"""PTE-C4 causal assays for competent GATE/FLIP champions (PREREG_PTE_C4 s6; DESCRIPTIVE per candidate).
usage: python assay_c4.py PLAN.json RUN_DIR OUT.json [device]
For every competent row (any arm): c3/assay_candidates.assay (256 fresh worlds; swap_v2 S0/S1/S2/Msum; S2 zeroed;
zero_comm; teacher/context off) PLUS, here:
  REG_ZERO      each state register S_i forced to 0 after every tick (locates the CONTEXT carrier for GATE: GATE twins
                share the context, so swaps locate only the cue carrier)
  LIB_NOP       all library-tagged lines -> NOP (from the saved population's lib tags at the champion's slot)
  LIB_CAUSAL    competence lost under LIB_NOP
Library tags come from pops/<job>.npz ("lib"), indexed by the row's champion (matched by genome equality)."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "c3"))
import numpy as np  # noqa: E402

import assay_candidates as AC  # noqa: E402
import run_c4 as RC  # noqa: E402
C = RC.C; R = RC.R


def main(plan_p, run_dir, out_p, device="cpu"):
    plan = json.load(open(plan_p)); cells = {c["cell_id"]: c for c in plan["cells"]}
    rows = [json.loads(l) for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")) for l in open(p) if l.strip()]
    res = []
    for r in [x for x in rows if x["success"]]:
        c = cells[r["cell_id"]]
        ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), r["rep"])
        env = RC.task_env(c, r["task"]); role = RC.ROLE[r["task"]]
        g = np.asarray(r["champion"], dtype=np.int64)
        npz = np.load(os.path.join(run_dir, "pops", r["job_id"].replace("|", "__") + ".npz"))
        idx = [i for i in range(npz["pop"].shape[0]) if np.array_equal(npz["pop"][i].astype(np.int64), g)]
        lib = npz["lib"][idx[0]] > 0 if idx else np.zeros(g.shape[:2], bool)
        cand = {"name": r["job_id"], "physics": ph.to_dict(), "env": env.to_dict(), "role": role,
                "genome": g.tolist(), "has_S2": ph.state_dim >= 3, "dup_mask": lib.tolist()}
        out = AC.assay(cand, device)
        out["ablations"]["lib_lines_nop"] = out["ablations"].pop("dup_lines_nop", None)
        from prometheus.ananke import assays
        seeds = assays.world_seeds(C.H_int(0xA55A8, int(r["search_seed"]) % (2 ** 31)), 256)
        rz = {}
        for i in range(ph.state_dim):
            def z(w, i=i):
                w.S[..., i] = 0
            pt, ep = AC._run_pt(ph, env, g, seeds, device, hooks_all=z)
            rz[f"S{i}"] = AC._comp(role, pt, ep)["status"]
        out["reg_zero"] = rz
        out["LIB_CAUSAL"] = (out["ablations"].get("lib_lines_nop") or {}).get("status") not in (None, "TRUE")
        out["n_lib_lines"] = int(lib.sum()); out["arm"] = r["arm"]; out["task"] = r["task"]
        print(r["job_id"], out["fresh_held"]["status"], out["swaps"], "reg_zero", rz, "lib_nop",
              (out["ablations"].get("lib_lines_nop") or {}).get("status"), "zero_comm", out["zero_comm"]["status"],
              "ctx/teacher_off", out.get("teacher_or_context_off", {}).get("status"), flush=True)
        res.append(out)
    C.jdump(out_p, res)


if __name__ == "__main__":
    main(*sys.argv[1:4], *(sys.argv[4:5] or ["cpu"]))
