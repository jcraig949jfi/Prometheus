"""S-M2b gap sweep (addendum in SPIKES_2026-09-27_LOG.md, committed first)."""
import dataclasses
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, c1b_run, lens, search  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
GAPS = [4, 6, 8, 10, 12, 16, 24]
SEEDS = assays.world_seeds(0x5E2, 64)


def champions():
    ph, env, g, row = c1b_run.load("4ab2ba014aac967e")
    cache = OUT / "champions_m2.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return ph, env, {k: np.asarray(v, dtype=np.int64) for k, v in d.items()}
    sp = search.SearchSpec(**{k: v for k, v in row["search"].items()
                              if k in {f.name for f in dataclasses.fields(search.SearchSpec)}})
    out = {"4ab2ba01": g}
    for k in (1, 2, 3):
        ev = search.evolve(ph, env, H_int(c1b.SEARCH_NS, 0, 0, k), sp, device="cuda")
        out[f"fresh{k}"] = np.asarray(ev["champion"], dtype=np.int64)
    cache.write_text(json.dumps({k: v.tolist() for k, v in out.items()}))
    return ph, env, out


if __name__ == "__main__":
    ph, env, champs = champions()
    res = {}
    for name, g in champs.items():
        res[name] = {}
        for gap in GAPS:
            e = dataclasses.replace(env, gap=gap)
            tr = lens.run(ph, g, e, SEEDS, device="cuda")
            res[name][gap] = lens.ci(lens.trial_acc(tr, range(e.trials)))
        print(name, " ".join(f"g{gp}:{v[0]:.2f}[{v[1]:.2f}]" for gp, v in res[name].items()), flush=True)
    lo16 = [res[n][16][1] for n in res]
    verdict = ("TUNED" if sum(x < 0.60 for x in lo16) >= 3 else
               "OPEN-ENDED" if sum(x >= 0.75 for x in lo16) >= 3 else "MIXED")
    res["_verdict"] = verdict
    (OUT / "s_m2b.json").write_text(json.dumps(res, indent=1))
    print("verdict", verdict)
