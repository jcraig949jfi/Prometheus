"""W-B Addendum B: Y6 readout-site rule time course by trial phase and y sign; Y7 S0 writers."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from probe import run
from census import cells
from disasm import disasm
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics
OUT = pathlib.Path(__file__).parent / "out"
want = set(sys.argv[1:])
res = {}
for r in cells():
    if r["cell_id"][:8] not in want:
        continue
    ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    Pd = env.period()
    b = run(ph, g, env, record_r=True)
    B = b.r.shape[1]
    ri = b.ep.schedule.read_idx.cpu().numpy()[:, 0]
    rr = b.r[:, np.arange(B), ri]                    # [T,B]
    T = rr.shape[0]
    o = {"Pd": Pd, "ro_phase": int(b.ep.ro_tick[0, 0] % Pd), "cue_len": env.cue_len}
    for sgn in (1, -1):
        prof = np.zeros(Pd); cnt = np.zeros(Pd)
        for k in range(2, env.trials):
            m = b.ep.y[:, k] == sgn
            for ph_ in range(Pd):
                t = k * Pd + ph_
                if t < T:
                    prof[ph_] += (rr[t, m] != 0).sum(); cnt[ph_] += m.sum()
        o[f"nonzero_rule_share_by_phase_y{sgn:+d}"] = [round(float(x), 3) for x in prof / np.maximum(cnt, 1)]
    o["rules_at_readout_hist"] = {int(k): int(v) for k, v in zip(*np.unique(rr[2 * Pd:], return_counts=True))}
    o["s0_writers"] = [l for l in disasm(ph, g).splitlines() if " S0 " in l[:22] or l.startswith("---")]
    res[r["cell_id"]] = o
    print(r["cell_id"][:8], json.dumps(o), flush=True)
(OUT / "phase.json").write_text(json.dumps(res, indent=1))
