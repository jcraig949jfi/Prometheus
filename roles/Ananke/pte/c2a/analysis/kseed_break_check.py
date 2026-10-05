"""POST-HOC, DESCRIPTIVE (not a preregistered test). Was each KSEED start genome actually broken?

For every KSEED job: regenerate the perturbed plant (run.kseed_genome, deterministic) and score it with the
frozen competence ruler on THAT search's held worlds (H(search_seed, HELD_NS), 128). Classes:
  NEUTRAL_EDIT   start genome already TRUE (the edit did not break competence)
  BROKEN         start genome FALSE/INDETERMINATE
Joined with the search outcome: recovered-from-broken vs never-broken. Runs the frozen code (pinned worktree).
usage: python kseed_break_check.py PLAN.json RUN_DIR OUT.json [device]
"""
import glob, json, sys
sys.path.insert(0, "F:/Prometheus-worktrees/ananke-c2a-pinned/roles/Ananke/pte/c2a")
import numpy as np
import c2a_common as C
import run as R
from prometheus.ananke import assays, envs
from prometheus.ananke.search import HELD_NS

plan = json.load(open(sys.argv[1])); dev = sys.argv[4] if len(sys.argv) > 4 else "cuda"
cells = {c["cell_id"]: c for c in plan["cells"]}
rows = {}
for p in glob.glob(sys.argv[2] + "/rows_w*.jsonl"):
    for l in open(p):
        r = json.loads(l); rows[r["job_id"]] = r
out = []
for jid, r in sorted(rows.items()):
    if not r["arm"].startswith("KSEED"):
        continue
    c = cells[r["cell_id"]]
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    plant = np.asarray(c["plant_genome"], dtype=np.int64)
    k = int(r["arm"].split("-")[1])
    g, edits = R.kseed_genome(plant, k, c["cell_key"], r["idx"])
    assert edits == r["kseed_edits"], jid            # regeneration matches the run record
    hs = assays.world_seeds(C.H_int(r["search_seed"], HELD_NS), C.M_HELD)
    pt, ep = C.eval_programs(ph, env, hs, [g], device=dev)
    s = C.competence(c["role"], pt[0], ep)
    out.append({"job_id": jid, "cell_id": r["cell_id"], "k": k, "start_status": s["status"],
                "start_acc": s["all"]["mean"], "search_success": r["success"], "champ_acc": r["champ_acc"],
                "champ_line_dist": r["basin"]["champ_line_dist"]})
    print(jid, s["status"], round(s["all"]["mean"], 3), "->", r["success"], flush=True)
C.jdump(sys.argv[3], out)
