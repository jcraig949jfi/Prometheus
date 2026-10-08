"""PTE-C4 transplant (PREREG_PTE_C4 s6; DESCRIPTIVE). usage: python transplant_c4.py PLAN_C4_T.json RUN_DIR OUT.json [--device cuda]
For every competent arm-C champion whose library lines are causal (lib_ablation != TRUE): its LIVE library-derived
lines (program order) are written into the free region (lines 16..) of EVERY gen-0 genome of 8 recipient searches
(fresh R4 populations, seeds H(C4_NS, 0x7A5, donor job, r)); the GA (OPD, M32) runs 12 generations; 8 controls use the
same seeds without the transplant. Reported: competent recipients vs controls, on the recipients' own held worlds."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import run_c4 as RC  # noqa: E402
K = RC.K; R = RC.R; C = RC.C
from prometheus.ananke import assays  # noqa: E402
from prometheus.ananke.search import HELD_NS, SearchSpec  # noqa: E402


def recipient(ph, env, task, sseed, lines, device):
    orig = R.init_population

    def seeded(g, pop, ph_, free):
        p = orig(g, pop, ph_, free)
        if lines is not None:
            L0 = ph_.prog_len - free
            b = min(len(lines), free)
            p[:, :, L0:L0 + b] = np.asarray(lines[:b])[None, None]
        return p
    R.init_population = seeded
    try:
        sp = SearchSpec(**dict(RC.BASE_SPEC, gens=12, M=32))
        e = RC.evolve(ph, env, sseed, sp, device, "R4", "OPD", [])
    finally:
        R.init_population = orig
    champ = e["pop"][e["ci"]]
    hs = assays.world_seeds(C.H_int(sseed, HELD_NS), C.M_HELD)
    pt, ep = C.eval_programs(ph, env, hs, [champ], device=device)
    return C.competence(RC.ROLE[task], pt[0], ep)["status"]


def main(plan_p, run_dir, out_p, device="cuda"):
    import glob
    plan = json.load(open(plan_p)); cells = {c["cell_id"]: c for c in plan["cells"]}
    rows = [json.loads(l) for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")) for l in open(p) if l.strip()]
    donors = [r for r in rows if r.get("arm") == "C" and r["success"] and r["lib_lines"] > 0
              and (r.get("lib_ablation") or {}).get("status") != "TRUE" and r.get("live_lib_lines")]
    out = []
    for r in donors:
        c = cells[r["cell_id"]]
        ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), "R4")
        env = RC.task_env(c, r["task"])
        champ = np.asarray(r["champion"])
        lines = [champ[0, i].tolist() for i in sorted(r["live_lib_lines"])]
        rec = {"donor": r["job_id"], "n_lines": len(lines), "seeded": [], "control": []}
        for k in range(8):
            sseed = C.H_int(RC.C4_NS, 0x7A5, r["job_id"], k)
            rec["seeded"].append(recipient(ph, env, r["task"], sseed, lines, device))
            rec["control"].append(recipient(ph, env, r["task"], sseed, None, device))
        rec["k_seeded"] = rec["seeded"].count("TRUE"); rec["k_control"] = rec["control"].count("TRUE")
        print(rec["donor"], rec["k_seeded"], "/8 vs control", rec["k_control"], "/8", flush=True)
        out.append(rec)
    C.jdump(out_p, {"n_donors": len(donors), "transplants": out})


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(*a[:3], device="cuda" if "--device" not in sys.argv else sys.argv[sys.argv.index("--device") + 1])
