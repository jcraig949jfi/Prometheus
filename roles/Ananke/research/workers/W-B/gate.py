"""W-B Addendum C: write-gate test."""
import dataclasses, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from probe import run, acc, paired, pin
from census import cells
from prometheus.ananke import envs, lens
from prometheus.ananke.physics import Physics
OUT = pathlib.Path(__file__).parent / "out"
res = {}
for r in cells():
    if r["cell_id"][:8] not in ("311c465f", "faafa5b0"):
        continue
    ph, env0 = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    o = {}
    for ename, env in (("dist_on", env0), ("dist_off", dataclasses.replace(env0, amp_dist=0))):
        Pd = env.period(); ts = 2 * Pd - 1; later = range(2, env.trials)
        b = run(ph, g, env)
        nl = acc(b, later)
        B, N = 64, ph.n_sites
        ri = b.ep.schedule.read_idx.cpu().numpy()[:, 0]
        ro = np.zeros((B, N), bool); ro[np.arange(B), ri] = True
        o[f"{ename}_normal"] = lens.ci(nl)
        for k in (1, 0):
            ev = lambda w, t, k=k: pin(ro, k)(w) if t >= ts else None
            o[f"{ename}_pin_readout_rule{k}"] = paired(acc(run(ph, g, env, every=ev), later), nl)
    res[r["cell_id"]] = o
    print(r["cell_id"][:8], json.dumps({k: (v if "normal" in k else (round(v["arm"][0], 3), v["v"])) for k, v in o.items()}, default=float), flush=True)
(OUT / "gate.json").write_text(json.dumps(res, indent=1, default=float))
