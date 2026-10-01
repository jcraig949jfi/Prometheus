"""W2-N fresh-namespace replicate runs (CPU, eager, 2 threads). Reuses W-O runner/audit and W-Z zcommon BY IMPORT
(read-only): identical specimen loading, offset, trial set and SINGLE-trial fork as AUDIT3; only the world-seed
namespace and M differ, and only the named arm(s) are run (the normal run is always computed).

Usage:
  python n_runs.py ka  <gid> <arm> <M>          known-answer: namespace 0x680, compare with the first M/2 pairs of
                                                 W-Z out/pairs/<gid>.npz (world_seeds(ns, M) is a prefix of
                                                 world_seeds(ns, 512)); exits 3 on any mismatch
  python n_runs.py run <gid> <arm> <M> <ns_hex> fresh namespace; saves out/runs/<gid>_<arm>_<ns>_M<M>.npz
"""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
import json  # noqa: E402
import pathlib  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
WK = HERE.parents[2] / "workers"
sys.path.insert(0, str(WK / "W-Z"))
torch.set_num_threads(2)
assert torch.cuda.is_available() is False
import zcommon as Z  # noqa: E402
import runner as R  # noqa: E402  (W-O)
import audit as A  # noqa: E402  (W-O)
import run_z as RZ  # noqa: E402  (W-Z arm_pairs / enc)
torch.set_num_threads(2)
from prometheus.ananke import assays  # noqa: E402

OUTR = HERE / "out" / "runs"
OUTR.mkdir(parents=True, exist_ok=True)


def group_key(gid):
    for k in Z.groups():
        if Z.gid(k) == gid:
            return k
    raise KeyError(gid)


def run(gid, arm, M, ns):
    k = group_key(gid)
    src, loader, sp, off, tset, fam = k
    ph, env, g = R.load(loader, sp)
    o = R.sct_offset(env) if off == "" else int(off)
    sd = assays.world_seeds(ns, M)
    trials = list(range(env.trials)) if tset == "all" else list(range(1, env.trials))
    arms = {arm: A.arm_names(arm) if arm not in ("site_all", "channel_all") else
            (R.SITE if arm == "site_all" else R.FLIGHT)}
    t0, c0 = time.time(), time.process_time()
    ep, npt, apt, _, _ = R.fork_single(ph, g, env, sd, arms, o, trials, device="cpu")
    at, st, a, b, K, cells, ok = RZ.arm_pairs(npt, apt[arm], trials)
    return {"k": k, "offset": o, "trials": trials, "at": at, "st": st, "a": a, "s": b, "K": K, "ok": ok,
            "wall": time.time() - t0, "cpu": time.process_time() - c0}


def main():
    mode, gid, arm, M = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    if mode == "ka":
        r = run(gid, arm, M, Z.NS)
        z = np.load(WK / "W-Z" / "out" / "pairs" / f"{gid}.npz")
        P = M // 2
        ra, rs = z[f"a__{arm}"][:P], z[f"s__{arm}"][:P]
        ea, es = RZ.enc(r["at"]), RZ.enc(r["st"])
        same = bool(np.array_equal(ra, ea) and np.array_equal(rs, es))
        rec = {"mode": "ka", "gid": gid, "arm": arm, "M": M, "ns": hex(Z.NS), "pairs_compared": P,
               "exact_match": same, "n_diff_a": int((ra != ea).sum()), "n_diff_s": int((rs != es).sum()),
               "wall_s": round(r["wall"], 1), "cpu_s": round(r["cpu"], 1)}
        print(json.dumps(rec), flush=True)
        with open(HERE / "out" / "ka.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        sys.exit(0 if same else 3)
    ns = int(sys.argv[5], 16)
    r = run(gid, arm, M, ns)
    fn = OUTR / f"{gid}_{arm}_{ns:x}_M{M}.npz"
    np.savez_compressed(fn, a=RZ.enc(r["at"]), s=RZ.enc(r["st"]), K=r["K"], offset=r["offset"])
    rec = {"mode": "run", "gid": gid, "arm": arm, "M": M, "ns": hex(ns), "K": r["K"], "P": int(r["ok"].sum()),
           "a_mean": float(r["a"].mean()), "s_mean": float(r["s"].mean()),
           "wall_s": round(r["wall"], 1), "cpu_s": round(r["cpu"], 1)}
    print(json.dumps(rec), flush=True)
    with open(HERE / "out" / "runs.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
