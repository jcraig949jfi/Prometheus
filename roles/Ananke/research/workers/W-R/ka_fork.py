"""KA-F: fork_single must be bit-identical to lens_swap.run_arms (SINGLE arms);
MUST-FAIL: fork one tick late. python ka_fork.py <spec> [...]"""
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import specs
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, lens_swap as LS
import fork

M, TRIALS = 16, [1, 2]


def check(name, late=0):
    ph, env, g, meta = specs.load(name)
    seeds = assays.world_seeds(0x620, M)
    offs = list(range(0, specs.ro_off(env)))
    ep, normal, ns0, site, chan, s0s, s0c = fork.fork_single(ph, g, env, seeds, offs, TRIALS, late=late)
    arms = [LS.Arm("normal")] + [LS.Arm(f"{nm}@{o}#{k}", tuple(LS.SITE if nm == "site" else LS.FLIGHT), o, k)
                                 for o in offs for k in TRIALS for nm in ("site", "chan")]
    r = LS.run_arms(ph, g, env, seeds, arms, chunk=16, early_stop=False)
    ok = bool(np.array_equal(np.nan_to_num(r.per_trial["normal"], nan=-9), np.nan_to_num(normal, nan=-9)))
    ok_n = ok
    bad = []
    for o in offs:
        for k in TRIALS:
            for nm, P, S in (("site", site, s0s), ("chan", chan, s0c)):
                a = r.per_trial[f"{nm}@{o}#{k}"][:, k]
                b = P[o][:, k]
                s_a = r.s0[f"{nm}@{o}#{k}"][:, k]
                if not (np.array_equal(np.nan_to_num(a, nan=-9), np.nan_to_num(b, nan=-9))
                        and np.array_equal(s_a, S[o][:, k])):
                    bad.append((o, k, nm))
    return {"spec": name, "late": late, "normal_equal": ok_n, "arms": 2 * len(offs) * len(TRIALS),
            "mismatched_arms": len(bad), "first_bad": bad[:5], "identical": ok_n and not bad}


if __name__ == "__main__":
    out = []
    for name in sys.argv[1:]:
        for late in (0, 1):
            t = time.time()
            res = check(name, late)
            res["wall_s"] = round(time.time() - t, 1)
            print(json.dumps(res), flush=True)
            out.append(res)
    tag = "_".join(sys.argv[1:])
    (HERE / f"out/ka_fork_{tag}.json").write_text(json.dumps(out, indent=1))
