"""W-M application: mixture census (EVERY and SINGLE modes) per spec.
python apply.py <spec> [<spec> ...]; spec = 8-char cell id | E2 | E1."""
import dataclasses, gzip, json, os, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(HERE))
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, c1b_run
import lens_ins6 as L
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def full_ids():
    ids = {}
    with gzip.open(REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt") as f:
        for l in f:
            r = json.loads(l)
            if r["kind"] == "evolve":
                ids[r["cell_id"][:8]] = r["cell_id"]
    return ids


def spec(name):
    if name in ("E1", "E2"):
        sys.path.insert(0, str(REPO / "roles/Ananke/research/designed_echoes"))
        import design
        torch.set_num_threads(2)
        key = {"E1": "E1_canon", "E2": "E2_pipe2"}[name]
        gap = {"E1": 7, "E2": 11}[name]      # design.stage_instruments best gaps (instruments.json)
        ph, g, _ = design.build(key)
        env = dataclasses.replace(design.ENV0, gap=gap)
        return ph, env, g, assays.world_seeds(0x5F1, 64), {"design": key, "gap": gap}
    ph, env, g, row = c1b_run.load(full_ids()[name])
    return ph, env, g, assays.world_seeds(0x5EE, 64), {"cell": row["cell_id"], "wave": row.get("wave")}


def ro_off(env):
    return (env.cue_len + env.gap) if env.family == "HOLD" else env.delta


if __name__ == "__main__":
    for name in sys.argv[1:]:
        ph, env, g, seeds, meta = spec(name)
        offs = list(range(-1, ro_off(env)))
        trials = list(range(1, env.trials))
        res = {"spec": name, **meta, "family": env.family, "env": env.to_dict(), "ro_off": ro_off(env),
               "offsets": offs, "trials": trials}
        for mode in ("every", "single"):
            t = time.time()
            raw = {}
            r = L.mixture_scan(ph, g, env, seeds, offs, mode, trials, chunk=16, raw=raw)
            np.savez_compressed(OUT / f"raw_{name}_{mode}.npz",
                                **{f"{o}__{k}": v for o, d in raw.items() for k, v in d.items()})
            res[mode] = {"normal": r["normal"], "offsets": {str(o): c for o, c in r["offsets"].items()},
                         "wall_s": time.time() - t}
            print(name, mode, round(time.time() - t), "s",
                  " ".join(f"{o}:{c['class'][:4]}/{c['follow']['class'][:4]}" for o, c in r["offsets"].items()), flush=True)
        (OUT / f"census_{name}.json").write_text(json.dumps(res, indent=1, default=float))
