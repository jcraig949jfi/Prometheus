"""W-S driver. python run.py <spec> <M> <ns_hex> <offsets comma> [tag]
spec: 8-char cell id | PLANT2J0 | PLANT2J1 | PLANT1J1 (echo_hold, update_period, lat_jitter)."""
import dataclasses, json, os, pathlib, sys, time
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(HERE), str(REPO / "roles/Ananke/research/workers/W-R")):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np
import torch
torch.set_num_threads(2)
from prometheus.ananke import assays, plants
import specs as WRS            # W-R spec loader (read-only import)
import probe, analyze

OUT = HERE / "out"


def load(name):
    if name.startswith("PLANT"):
        per, jit = int(name[5]), int(name[7])
        ph = dataclasses.replace(plants.c1b_echo_physics(), update_period=per, lat_jitter=jit)
        env = WRS.PLANT_ENV
        return ph, env, plants.echo_hold(ph)[None], {"plant": "echo_hold", "update_period": per, "lat_jitter": jit}
    ph, env, g, meta = WRS.load(name)
    torch.set_num_threads(2)
    return ph, env, g, meta


def main():
    name, M, ns = sys.argv[1], int(sys.argv[2]), int(sys.argv[3], 16)
    offsets = [int(x) for x in sys.argv[4].split(",")]
    tag = sys.argv[5] if len(sys.argv) > 5 else f"{name}_M{M}_ns{ns:x}"
    ph, env, g, meta = load(name)
    seeds = assays.world_seeds(ns, M)
    trials = list(range(1, env.trials))
    Pd = env.period()
    t = time.time()
    run = probe.fork(ph, g, env, seeds, offsets, trials, snap_offsets=offsets,
                     log=lambda s: print(name, s, round(time.time() - t), "s", flush=True))
    wall = time.time() - t
    kc = analyze.inflight_check(run, trials, offsets, Pd)
    kc_bad = analyze.inflight_check(run, trials, offsets, Pd, te_shift=1)
    delta = env.cue_len + env.gap if env.family == "HOLD" else env.delta
    rows = analyze.table(run, env, offsets, trials, Pd, ph.update_period if ph.update_mode == "sync" else 1, delta)
    np.savez_compressed(OUT / f"raw_{tag}.npz", normal=run["normal"], ns0=run["ns0"],
                        **{f"{kd}_{o}_{i}": run["res"][kd][o][i] for kd in run["res"] for o in offsets for i in (0, 1)},
                        **{f"log_{k}": v for k, v in run["elog"].items()})
    res = {"spec": name, "meta": meta, "M": M, "ns": hex(ns), "offsets": offsets, "trials": trials, "Pd": Pd,
           "physics": ph.to_dict(), "env": env.to_dict(), "wall_s": wall, "n_log": int(len(run["elog"]["te"])),
           "normal_acc": float(np.nanmean(run["normal"][:, trials])),
           "KA_L": dict(zip(("checked", "equal", "nonempty_real", "real_subset"), kc)),
           "KA_L_mustfail_te_plus1": dict(zip(("checked", "equal", "nonempty_real", "real_subset"), kc_bad)),
           "n_cue_log": {k: int(len(v["te"])) for k, v in run["cue_logs"].items()},
           "rows": rows}
    (OUT / f"rows_{tag}.json").write_text(json.dumps(res, default=lambda x: x.item() if hasattr(x, "item") else str(x)))
    print(name, "done", round(wall), "s rows", len(rows), "KA_L", kc, "mustfail", kc_bad, flush=True)


if __name__ == "__main__":
    main()
