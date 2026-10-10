"""WTP-05 sub-assay E2 (PREREG_WTP05 s9): can a COUPLED two-axis physical change revive the dead WTP-04
families F01, F06, F11?  Reuses the frozen WTP-04 harness unchanged (families, axis transforms,
habit.unit, habit.classify, score4.cell_label). Grid per family: memory band {.1, .25, .5, 1.0} x
  change  {static, drift.3/p800, drift.3/p200}
  price   {x.01, x.1, x1}           (read/write/probe/rollout prices, as WTP-04 information_cost)
  noise   {0, .1, native}
The second axis' native level (static / x1 / native) is in every grid, so the single-axis memory row is
measured in the same run. COUPLED REVIVAL = a PAYS cell (m, x) where neither (m, native) nor (native band, x)
pays. Rows: ensorain/runs/wtp05/revival/<name>.jsonl."""
import argparse
import collections
import copy
import json
import multiprocessing as mp
import os
import time

import psutil

from ensorain.wtp4.axes import _set, _mul, _drift, INFO_COSTS
from ensorain.wtp4.families import families
from ensorain.wtp4.habit import unit, classify
from ensorain.wtp4.score4 import cell_label, PAYS

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp05", "revival")
FAMS = ("F01", "F06", "F11")
BANDS = (0.1, 0.25, 0.5, 1.0)
SECOND = {
    "change": [("static", _drift(None)), ("p800", _drift(800)), ("p200", _drift(200))],
    "price": [("x0.01", _mul(INFO_COSTS, 0.01)), ("x0.1", _mul(INFO_COSTS, 0.1)), ("x1", copy.deepcopy)],
    "noise": [("sd=0", _set(("observation", "noise_sd"), 0.0)), ("sd=0.1", _set(("observation", "noise_sd"), 0.1)),
              ("native", copy.deepcopy)],
}
NATIVE2 = {"change": "static", "price": "x1", "noise": "native"}


def points():
    """-> [(pair, band label, second label, transform)] incl. the native-band column."""
    out = []
    for pair, levels in SECOND.items():
        for b in ("native",) + BANDS:
            for lab, f2 in levels:
                f1 = copy.deepcopy if b == "native" else _set(("memory", "band"), b)
                out.append((pair, str(b), lab, (lambda g, f1=f1, f2=f2: f2(f1(g)))))
    return out


def _job(a):
    fid, pair, b, lab, seed = a
    f = next(x for x in families() if x["fid"] == fid)
    tf = next(t for (p, bb, l, t) in points() if (p, bb, l) == (pair, b, lab))
    return dict(fid=fid, pair=pair, band=b, level=lab, **unit(tf(f["g"]), seed))


def run(name, seeds, workers=3):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["fid"], r["pair"], r["band"], r["level"], r["seed"]) for r in map(json.loads, open(path))}
    todo = [(f, p, b, l, s) for f in FAMS for (p, b, l, _) in points() for s in seeds if (f, p, b, l, s) not in done]
    print(f"{name}: {len(todo)} jobs", flush=True)
    t0 = time.time()
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=20) as pool, open(path, "a") as fh:
        it, pending, n = iter(todo), [], 0
        while True:
            while len(pending) < 2 * workers and psutil.virtual_memory().available / 2 ** 30 >= 3.0:
                j = next(it, None)
                if j is None:
                    break
                pending.append(pool.apply_async(_job, (j,)))
            if not pending:
                break
            fh.write(json.dumps(pending.pop(0).get()) + "\n")
            fh.flush()
            n += 1
            if n % 20 == 0:
                print(f"  {n}/{len(todo)} {time.time() - t0:.0f}s", flush=True)
    print(f"{name}: done {n} in {time.time() - t0:.0f}s", flush=True)


def score(name):
    rows = [json.loads(l) for l in open(os.path.join(OUT, f"{name}.jsonl"))]
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r["fid"], r["pair"], r["band"], r["level"])].append(classify(r)["label"])
    C = {k: cell_label(v) for k, v in cells.items()}
    out = dict(name=name, cells={"|".join(k): v for k, v in sorted(C.items())}, families={})
    for fid in FAMS:
        pays = [k for k, v in C.items() if k[0] == fid and v in PAYS]
        coupled = []
        for (f, pair, b, lab) in pays:
            if b == "native" or lab == NATIVE2[pair]:
                continue
            m_only = C.get((f, pair, b, NATIVE2[pair]))
            x_only = C.get((f, pair, "native", lab))
            if m_only not in PAYS and x_only not in PAYS:
                coupled.append(dict(pair=pair, band=b, level=lab, label=C[(f, pair, b, lab)], m_only=m_only, x_only=x_only))
        single = [dict(pair=p, band=b, level=l, label=C[(f, p, b, l)]) for (f, p, b, l) in pays
                  if b == "native" or l == NATIVE2[p]]
        out["families"][fid] = dict(n_cells=sum(1 for k in C if k[0] == fid), n_pays=len(pays), single_axis_pays=single,
                                    coupled_revival=coupled,
                                    verdict="COUPLED_REVIVAL" if coupled else ("SINGLE_AXIS_REVIVAL" if single else "NOT_REVIVED"),
                                    labels=dict(collections.Counter(v for k, v in C.items() if k[0] == fid)))
    json.dump(out, open(os.path.join(OUT, f"{name}_score.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "score"))
    ap.add_argument("name")
    ap.add_argument("--seeds", default="41005001,41005002")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.name, [int(s) for s in a.seeds.split(",")], a.workers)
    else:
        print(json.dumps({k: (v["verdict"], v["n_pays"], v["labels"]) for k, v in score(a.name)["families"].items()}, indent=1))
