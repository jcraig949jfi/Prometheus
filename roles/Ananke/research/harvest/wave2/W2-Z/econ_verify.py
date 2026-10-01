"""Engine check of the exact single-site recursion: run k-line cue emitters (k-1 padding lines are harmless MOVs into
T registers) at a row's own physics on its held worlds; count per-sensor emissions per trial; compare with econ.site_rates."""
import sys; sys.path.insert(0, '.')
import wz_common as wz, econ
np = wz.np
from prometheus.ananke import plants
A = plants.assemble
out = {}
KS = tuple(int(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else (1, 2, 3, 5, 8)
for c in sys.argv[1].split(","):
    r = wz.row(c); ph, env = wz.cell(r)
    seeds = wz.held(r, 16)
    Pd = env.period(); cE = ph.c_emit * ph.copies()
    for k in KS:
        lines = [("MULQ", "EMIT", "SENSE", "SENSE", 0)] + [("MOV", "T%d" % (i % 4), "SENSE", 0, 0) for i in range(k - 1)]
        b = A(ph, lines); g = np.broadcast_to(b, (ph.rules, *b.shape)).copy()
        ep = wz.envs.build(ph, env, seeds)
        M = len(seeds); ws_ = [seeds[m - (m % 2)] for m in range(M)]
        w = wz.World(ph, np.repeat(g[None], M, 0), ws_, device="cpu", schedule=ep.schedule)
        sidx = ep.schedule.sense_idx.numpy()
        cnt = np.zeros((M, sidx.shape[1], env.trials))
        for t in range(env.T()):
            w.step()
            em = w.last_emit.numpy()
            for b_ in range(M):
                for j, s in enumerate(sidx[b_]):
                    cnt[b_, j, t // Pd] += em[b_, s]
        fam_sensors = {"XOR": 2, "MAJ": 5, "FLIP": 1, "RELAY": 1, "HOLD": 1}[env.family]
        meas = float(cnt[:, :fam_sensors].mean())
        pred = float(econ.site_rates(ph.e_income, ph.e_max, cE, ph.c_op, ph.c_mem, k, 0, ph.update_mode, ph.update_period,
                                     ph.update_p, Pd, 2, 99, env.trials).mean())
        both = float((cnt[:, :2] > 0).all(1).mean()) if fam_sensors >= 2 else None
        out[f"{c}|k{k}"] = {"measured_emissions_per_sensor_trial": round(meas, 3), "chain_pred(m=0,nmax=inf,w=2)": round(pred, 3),
                            "P(both sensors emit in trial)": both}
        print(c, "k", k, out[f"{c}|k{k}"], flush=True)
wz.save("econ_verify_%s.json" % sys.argv[2], out)
