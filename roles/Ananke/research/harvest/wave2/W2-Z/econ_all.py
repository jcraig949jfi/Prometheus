"""Exact single-site emission capacity for EVERY economy evolve row (all families), program-independent.
For k = non-NOP lines in the emitting site's rule (m = 0 nonzero state registers: optimistic) report
e_cue(k): expected emissions per trial when the site wishes to emit at awake ticks of the 2-tick cue window
          (one per trial), averaged over ALL trials of the episode (E0 = e_max transient included);
e_any(k): same with the wish open for the whole trial.
kmax90 = largest k with e_cue >= .9 * e_cue(0) ; e1 = e_cue(1) (the minimal possible emitter)."""
import gzip, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from prometheus.ananke.physics import Physics
from prometheus.ananke import envs
import econ
rows = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
out = []
for r in rows:
    if r["kind"] != "evolve" or r["physics"]["c_op"] == 0:
        continue
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    Pd = env.period(); cE = ph.c_emit * ph.copies()
    ec, ea = {}, {}
    for k in range(0, 17):
        a = econ.site_rates(ph.e_income, ph.e_max, cE, ph.c_op, ph.c_mem, k, 0, ph.update_mode, ph.update_period,
                            ph.update_p, Pd, 2, 1, env.trials)
        b = econ.site_rates(ph.e_income, ph.e_max, cE, ph.c_op, ph.c_mem, k, 0, ph.update_mode, ph.update_period,
                            ph.update_p, Pd, Pd, 1, env.trials)
        ec[k] = round(float(a.mean()), 3); ea[k] = round(float(b.mean()), 3)
    k90 = max([k for k in ec if ec[k] >= 0.9 * ec[0]] + [-1])
    o = {"cell": r["cell_id"], "family": env.family, "cE": cE, "inc_per_trial": ph.e_income * Pd, "Pd": Pd,
         "mode": ph.update_mode, "P": ph.update_period, "p": ph.update_p, "e_cue": ec, "e_any": ea, "kmax90": k90,
         "rules": ph.rules, "setrule": ph.setrule, "prog_len": ph.prog_len}
    out.append(o)
    print(o["cell"][:8], o["family"], "cE", cE, "inc/trial", o["inc_per_trial"], ph.update_mode, ph.update_period if ph.update_mode == "sync" else ph.update_p,
          "kmax90", k90, "e_cue k0/1/3/5/8/12:", [ec[k] for k in (0, 1, 3, 5, 8, 12)], "e_any k1/12:", ea[1], ea[12])
json.dump(out, open(HERE / "out" / "econ_all.json", "w"), indent=1)
