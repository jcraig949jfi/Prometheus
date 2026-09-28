"""Post-hoc instrument check (LOG A7): is site_acc + chan_acc = 1 forced by the
mirror-pair design? Compare per (pair, trial): site-swap outcome in world B vs
channel-swap outcome in world A (A = 2p, B = 2p+1)."""
import sys, pathlib, json
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.resolve().parents[4]))
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, c1b_run
import traj, main as M
ids = M.full_ids()
seeds = assays.world_seeds(0x5EE, 64)
res = {}
for c, o in (("2dccdaa5", 5), ("369f5a5b", 8), ("4781b0a1", 8), ("4ab2ba01", 5), ("78f3b0ec", 10)):
    ph, env, g, _ = c1b_run.load(ids[c])
    arms = [("normal", None, 0), ("site", traj.SITE, o), ("chan", traj.FLIGHT, o)]
    ep, pt, trs = traj.run_arms(ph, g, env, seeds, arms, device="cpu")
    sc = ep.scored.copy(); sc[:, 0] = False
    s, ch = pt["site"], pt["chan"]
    # pair identity: site outcome of B vs 1 - chan outcome of A, and vice versa
    idA = np.mean((s[1::2] == 1 - ch[0::2])[sc[0::2]])
    idB = np.mean((s[0::2] == 1 - ch[1::2])[sc[0::2]])
    # readout values: S0 of B under site swap vs S0 of A under chan swap
    ro = ep.ro_tick
    vB = trs["site"][ro[1::2], np.arange(1, 64, 2)[:, None], 0]
    vA = trs["chan"][ro[0::2], np.arange(0, 64, 2)[:, None], 0]
    res[c] = {"o": o, "family": env.family, "frac_trials_identity_A": float(idA), "frac_trials_identity_B": float(idB),
              "frac_equal_S0_readout": float(np.mean((vB == vA)[sc[0::2]]))}
    print(c, res[c], flush=True)
(HERE / "out" / "identity_check.json").write_text(json.dumps(res, indent=1))
