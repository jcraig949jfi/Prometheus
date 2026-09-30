"""PLAN s3 runs. Usage: python run_z.py <worker id>   (1 torch thread, CPU only)
Claims groups in PLAN s2 order (out/claims/<gid>, O_EXCL); per group re-runs W-O's SINGLE-trial design
(W-O runner.load / sct_offset / fork_single, W-O arm set) on world_seeds(0x680, 512); saves per-trial pair-mean
arrays (out/pairs/<gid>.npz, uint8 = 4 x pair mean, 255 = not scored) and appends one JSON line per group to
out/runs_w<id>.jsonl. Budget guard: addendum Z5."""
import json
import os
import sys
import time
import traceback

import numpy as np
import torch

import zcommon as Z

torch.set_num_threads(1)
import runner as R  # noqa: E402  (W-O)
import audit as A  # noqa: E402  (W-O arm_names)
from prometheus.ananke import assays, lens  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402

BUDGET_S = 7.3 * 3600
CL = Z.OUT / "claims"
PD = Z.OUT / "pairs"


def arm_pairs(npt, spt, trials):
    """-> per-trial pair means a_t, s_t [P, ntr] (NaN where not both scored) and over-trial a, s, K (swap_rel path)."""
    keep = np.zeros(npt.shape[1], bool)
    keep[list(trials)] = True
    n = np.where(keep[None], npt, np.nan)
    s = np.where(keep[None], spt, np.nan)
    both = ~np.isnan(n) & ~np.isnan(s)
    nb, sb = np.where(both, n, np.nan), np.where(both, s, np.nan)
    a, b = sr.pair_means(nb), sr.pair_means(sb)
    ok = ~np.isnan(a) & ~np.isnan(b)
    K = int(round(both.sum() / max(1, 2 * int(ok.sum()))))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        at = np.nanmean(nb.reshape(nb.shape[0] // 2, 2, -1), 1)[:, trials]
        st = np.nanmean(sb.reshape(sb.shape[0] // 2, 2, -1), 1)[:, trials]
    return at, st, a[ok], b[ok], K, int(both.sum()), ok


def enc(x):
    return np.where(np.isnan(x), 255, np.round(x * 4)).astype(np.uint8)


def run_group(k, rows):
    src, loader, sp, off, tset, fam = k
    ph, env, g = R.load(loader, sp)
    o = R.sct_offset(env) if off == "" else int(off)
    sd = assays.world_seeds(Z.NS, Z.M)
    trials = list(range(env.trials)) if tset == "all" else list(range(1, env.trials))
    labels = sorted({r["arm"] for r in rows})
    arms = {lab: A.arm_names(lab) for lab in labels}
    if not any(arms[l] == R.SITE for l in labels):
        arms["site_all"] = R.SITE
    if not any(arms[l] == R.FLIGHT for l in labels):
        arms["channel_all"] = R.FLIGHT
    ep, npt, apt, _, _ = R.fork_single(ph, g, env, sd, arms, o, trials)
    res = {"group": list(k), "gid": Z.gid(k), "offset_used": o, "trials": trials, "M": len(sd), "ns": hex(Z.NS),
           "arms": {}}
    arrs = {"trials": np.asarray(trials, np.int16)}
    for lab in arms:
        at, st, a, b, K, cells, ok = arm_pairs(npt, apt[lab], trials)
        lb = Z.label_arm(a, b, K)
        v = R.verdicts(npt, apt[lab], trials)   # W-O absolute + W-N ungated, for reference only
        res["arms"][lab] = {"label": lb["label"], "certificate": lb["certificate"], "transfer": lb["transfer"],
                            "P": lb["P"], "K": K, "cells": cells, "normal": lb["normal"], "DF": lb["DF"],
                            "DN": lb["DN"], "zci": lb["zci"], "attain": lb["attain"], "ident": lb["ident"],
                            "reach_tabulated": lb["reach_tabulated"], "abs": v["abs"], "swap": v["swap"],
                            "recorded": lab in labels, "pairs_ok": int(ok.sum())}
        arrs[f"a__{lab}"], arrs[f"s__{lab}"] = enc(at), enc(st)
    np.savez_compressed(PD / f"{Z.gid(k)}.npz", **arrs)
    return res


def spent_and_pending(cost):
    import glob
    done_cpu, done = 0.0, set()
    for fn in glob.glob(str(Z.OUT / "runs_w*.jsonl")):
        for line in open(fn):
            if line.strip():
                x = json.loads(line)
                done_cpu += x.get("cpu_s", 0.0)
                done.add(x["gid"])
    pend = 0.0
    for f in os.listdir(CL):
        if f not in done:
            pend += json.loads((CL / f).read_text())["pred_s"]
    return done_cpu, pend


def main(wid):
    CL.mkdir(parents=True, exist_ok=True)
    PD.mkdir(parents=True, exist_ok=True)
    first, rest = Z.order()
    G = Z.groups()
    cost = Z.wo_cost()
    out = Z.OUT / f"runs_w{wid}.jsonl"
    for k in first + rest:
        gid = Z.gid(k)
        if (Z.OUT / "STOP").exists():
            break
        if (CL / gid).exists():
            continue
        pred = cost.get(k, 400.0)
        done_cpu, pend = spent_and_pending(cost)
        if done_cpu + pend + pred > BUDGET_S:
            msg = f"w{wid}: budget stop at {gid} (done {done_cpu:.0f}s pend {pend:.0f}s pred {pred:.0f}s)"
            (Z.OUT / "STOP").write_text(msg)
            print(msg, flush=True)
            break   # PLAN order strict: no later (cheaper) group is launched
        try:
            fd = os.open(CL / gid, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.write(fd, json.dumps({"w": wid, "pred_s": pred, "t": time.time()}).encode())
        os.close(fd)
        t0, c0 = time.time(), time.process_time()
        try:
            res = run_group(k, G[k])
        except Exception as e:
            res = {"group": list(k), "gid": gid, "error": repr(e), "tb": traceback.format_exc()}
        res["wall_s"], res["cpu_s"], res["pred_s"] = round(time.time() - t0, 1), round(time.process_time() - c0, 1), pred
        res["w"] = wid
        with out.open("a") as f:
            f.write(json.dumps(res, default=float) + "\n")
        print(f"w{wid} {gid} {k[0]} {k[2][:8]} o={k[3]} "
              f"{ {a: (v['label'], v['transfer']) for a, v in res.get('arms', {}).items()} } "
              f"cpu={res['cpu_s']} pred={pred}", flush=True)
    print(f"w{wid}: done", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]))
