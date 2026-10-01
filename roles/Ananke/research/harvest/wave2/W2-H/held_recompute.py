"""(3)/(4) exact held pair arrays for the marginal C1 SIGNAL calls, by deterministic re-evaluation of the recorded
champion on its recorded held seeds (evolve: world_seeds(H(search_seed, HELD_NS), M_held); transfer: 0x7F7F).
Gate: the recomputed pair_ci must equal the recorded (acc, lo99, hi99) exactly, else the row is reported as
NOT_VERIFIED. Then: lo99 under pct (recorded), t (df P-1) and BOOTT (swap_rel.interval), one-sided p-values for
mu <= .55 (t and exact sign-flip-free BOOTT inversion is not needed; t p-value reported), and the label under each.
CPU, 2 threads. Output out/held_recompute.json."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(2)
assert not torch.cuda.is_available()
from scipy import stats as st  # noqa: E402

from prometheus.ananke import assays, envs, search, swap_rel  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

R = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    R[r["cell_id"]] = r
c1 = json.load(open(HERE / "out" / "c1_stats.json"))
want = set() if os.environ.get("W2H_PRI") else set(c1["signal"]["SIGNAL_and_not_Holm01_mu55"])
q = 2.5758
for cid, r in R.items():
    if r["kind"] not in ("evolve", "transfer"):
        continue
    h = r["result"]["held"]
    se = (h["hi99"] - h["lo99"]) / (2 * q)
    if os.environ.get("W2H_PRI"):
        # compute-budget restriction: only calls within 1 SE of the cut can change between pct / t / BOOTT
        if se > 0 and abs(h["lo99"] - 0.55) / se < 1.0:
            want.add(cid)
        continue
    if h["lo99"] > 0.55 and se > 0 and (h["lo99"] - 0.55) / se < 3:
        want.add(cid)
    if 0.50 < h["lo99"] <= 0.55 and se > 0 and (0.55 - h["lo99"]) / se < 1:   # near-misses (could gain SIGNAL)
        want.add(cid)
done = set()
import glob
for fn in sorted(glob.glob(str(HERE / "out" / "held_recompute_part*.log"))):
    for l in open(fn):
        if " repro " in l:
            done.add(l.split()[0])
jl = open(HERE / "out" / "held_recompute.jsonl", "a")
out = []
for cid in sorted(want):
    if cid in done:
        continue
    r = R[cid]
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    ns = search.HELD_NS if r["kind"] == "evolve" else 0x7F7F
    hseeds = assays.world_seeds(H_int(r["search_seed"], ns), sp.M_held)
    g = np.asarray(r["result"]["champion"] if r["kind"] == "evolve" else r["extra"]["genome"])
    ev = assays.evaluate(ph, g[None], env, hseeds, device="cpu")
    pr = ev.pair_acc()[0]
    m, lo, hi = assays.pair_ci(pr)
    h = r["result"]["held"]
    ok = abs(m - h["acc"]) < 1e-12 and abs(lo - h["lo99"]) < 1e-12 and abs(hi - h["hi99"]) < 1e-12
    P = len(pr)
    sd = pr.std(ddof=1)
    tq = st.t.ppf(0.995, P - 1)
    t_lo = m - tq * sd / math.sqrt(P)
    _, b_lo, b_hi = swap_rel.interval(pr, method="BOOTT")
    p55 = float(st.t.sf((m - 0.55) / (sd / math.sqrt(P)), P - 1)) if sd > 0 else (0.0 if m > .55 else 1.0)
    rec = {"cell": cid, "wave": r["wave"], "kind": r["kind"], "fam": r["env"]["family"], "reproduced": bool(ok),
           "acc": float(m), "lo_pct": float(lo), "lo_t": float(t_lo), "lo_boott": float(b_lo),
           "SIG_pct": bool(lo > .55), "SIG_t": bool(t_lo > .55), "SIG_boott": bool(b_lo > .55), "p55_t": p55,
           "pair_sd": float(sd), "pairs": pr.tolist()}
    out.append(rec)
    jl.write(json.dumps(rec) + chr(10))
    jl.flush()
    print(cid, r["wave"], r["env"]["family"], "repro", ok, round(m, 4), "lo pct/t/boott", round(lo, 4), round(t_lo, 4),
          round(float(b_lo), 4), flush=True)
json.dump(out, open(HERE / "out" / "held_recompute.json", "w"), indent=1)
