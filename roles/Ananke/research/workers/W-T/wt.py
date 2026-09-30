"""W-T (T-INS-16): how far does W-S's first-broadcast latency rule (P8 / P8any) reach?

Reuses, by import from their paths (read-only): W-S probe.fork (fork runner + cue-flip twin log),
W-S analyze (pair_index, accuracy, shuffled), W-R specs.load (cell loader), W-R followdiff.follow_table
(follow census pattern table). Nothing in prometheus/ananke is edited.

P8 / P8any are copied VERBATIM from W-S posthoc.py (lines 'srcc = ...' to 'P8_srcfirst') and
posthoc_summary.py ('p8any = ...'); see PLAN.md s3.

Plants (known answer, DIRECT carrier source -> readout, sync update_period 2, the RELAY cells' physics
c16d5231 with prog_len raised to 24; RELAY d 3 delta 8, Pd 11):
  PF  first-broadcast plant: the source emits its cue (PAY0) on its one awake cue tick, then re-emits
      the latched cue on PAY1 on every later wake (cue-bearing DECOY traffic); every site sets
      S0 := sign(IN0_0) when IN0_0 != 0, so only the first broadcast carries the answer.
  P1  single-broadcast plant: as PF but no re-emission at all (the source emits once per trial).
  PL  latest-wins plant (MUST-FAIL for P8): the source re-emits the latched cue on PAY0 every wake,
      so the readout follows the LATEST arrivals, not the first broadcast.
  suffix J1 = lat_jitter 1 (cell physics), J0 = lat_jitter 0 (control).
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
WS_DIR = HERE.parent / "W-S"
WR_DIR = HERE.parent / "W-R"
for p in (str(REPO), str(WS_DIR), str(WR_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import torch

torch.set_num_threads(2)
from prometheus.ananke import assays, envs, lens_swap as LS, plants  # noqa: E402
import probe  # noqa: E402  (W-S)
import analyze as WSA  # noqa: E402  (W-S)
import specs as WRS  # noqa: E402  (W-R)
from followdiff import follow_table  # noqa: E402  (W-R)

OUT = HERE / "out"
NS = 0x640


# ------------------------------------------------------------------ plants
def _cue(rows):
    return rows + [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),
        ("SUB", "T2", "ZERO", "T0", 0),
        ("GT", "T2", "T2", "SENSE", 0),
        ("SUB", "T1", "T1", "T2", 0),        # T1 = cue sign*256 or 0
        ("MULQ", "T3", "T1", "T1", 0),       # T3 = 256 iff cue
    ]


_LATCH = [
    ("SUB", "T2", "T1", "S1", 0),
    ("MULQ", "T2", "T2", "T3", 0),
    ("ADD", "S1", "S1", "T2", 0),            # S1 := cue where cue (source latch)
]
_READ = [
    ("GT", "T0", "IN0_0", "ZERO", 0),
    ("GT", "T2", "ZERO", "IN0_0", 0),
    ("SUB", "T0", "T0", "T2", 0),            # arrival sign*256 or 0 (PAY0 only)
    ("MULQ", "T2", "T0", "T0", 0),
    ("SUB", "T1", "T0", "S0", 0),
    ("MULQ", "T1", "T1", "T2", 0),
    ("ADD", "S0", "S0", "T1", 0),            # S0 := sign(IN0_0) where IN0_0 != 0
]


def plant_lines(kind: str):
    if kind == "PF":        # first broadcast on PAY0, decoy re-emission of the latched cue on PAY1
        return _cue([]) + [
            ("MOV", "PAY0", "T1", 0, 0),
            ("CONST", "T0", 0, 7, 2),        # 256
            ("SUB", "T0", "T0", "T3", 0),    # 256 iff no cue this tick
            ("MULQ", "PAY1", "S1", "T0", 0), # old latch iff no cue (decoy)
        ] + _LATCH + [("MULQ", "EMIT", "S1", "S1", 0)] + _READ
    if kind == "P1":        # single broadcast
        return _cue([]) + [
            ("MOV", "PAY0", "T1", 0, 0),
            ("MOV", "EMIT", "T3", 0, 0),
        ] + _READ
    if kind == "PL":        # latest wins: re-emit the latched cue on PAY0 every wake
        return _cue([]) + _LATCH + [
            ("MOV", "PAY0", "S1", 0, 0),
            ("MULQ", "EMIT", "S1", "S1", 0),
        ] + _READ
    raise KeyError(kind)


def plant_spec(name: str):
    """name = PLANT_<PF|P1|PL>_J<0|1>"""
    _, kind, j = name.split("_")
    ph0, env, _g, _m = WRS.load("c16d5231")
    ph = dataclasses.replace(ph0, prog_len=24, lat_jitter=int(j[1]))
    g = plants.assemble(ph, plant_lines(kind))[None]
    return ph, env, g, {"plant": kind, "lat_jitter": int(j[1]), "physics": "c16d5231 with prog_len 24"}


def load(name):
    if name.startswith("PLANT"):
        out = plant_spec(name)
    else:
        out = WRS.load(name)
    torch.set_num_threads(2)
    return out


# ------------------------------------------------------------------ P8 (verbatim W-S logic)
def p8_features(d: set, a: int, s: int, tau: int):
    """d: set of cue-bearing copies (te, arr, v, jit, dist) to readout a (union over the pair's two worlds,
    te >= t0, arr <= ro). Verbatim W-S posthoc.py."""
    r = {}
    srcc = sorted(x for x in d if x[2] == s)
    if srcc:
        te1 = srcc[0][0]
        first = [x for x in srcc if x[0] == te1]
        r["te1_rel"] = te1 - tau
        r["n1_held"] = sum(x[1] <= tau for x in first)
        r["n1_flight"] = sum(x[1] > tau for x in first)
        r["P8_srcfirst"] = "S" if r["n1_flight"] == 0 else ("C" if r["n1_held"] == 0 else "M")
    else:
        r["P8_srcfirst"] = "U"
    return r


def p8any_of(p8: np.ndarray) -> np.ndarray:
    """Verbatim W-S posthoc_summary.py: C iff any first-emission copy in flight (M -> C), U -> S."""
    return np.where(p8 == "M", "C", np.where(p8 == "U", "S", p8))


def p8all_features(d: set, a: int, srcs, tau: int):
    """SECONDARY (MAJ, K sources): each source's own first cue emission; union of those copies."""
    first = []
    for s in set(srcs):
        sc = sorted(x for x in d if x[2] == s)
        if sc:
            first += [x for x in sc if x[0] == sc[0][0]]
    if not first:
        return "U"
    h = sum(x[1] <= tau for x in first)
    f = len(first) - h
    return "S" if f == 0 else ("C" if h == 0 else "M")


# ------------------------------------------------------------------ run
def run(name, M, ns, offsets, tag, log=print):
    ph, env, g, meta = load(name)
    seeds = assays.world_seeds(ns, M)
    trials = list(range(1, env.trials))
    Pd = env.period()
    t = time.time()
    res = probe.fork(ph, g, env, seeds, offsets, trials, kinds=("site", "chan"),
                     log=lambda s: log(f"{name} {s} {time.time() - t:.0f}s"))
    wall = time.time() - t
    ep = res["ep"]
    P = M // 2
    src_all = ep.schedule.sense_idx.numpy()
    src = src_all[:, 0]
    rows = {k: [] for k in ("pair", "trial", "o", "q", "pat_frozen", "ok_frozen", "pat_follow", "ok_follow",
                            "P8", "P8all", "te1_rel", "n1_held", "n1_flight", "n_cue_a", "n_src_a",
                            "n_src_first", "n_src_later", "n_relay_a", "n_relay_flight", "n_emit_src",
                            "n1_pay0", "has_pay0_a")}
    for k in trials:
        wi = WSA.pair_index(res["cue_logs"][k], M)
        cl = res["cue_logs"][k]
        t0 = k * Pd
        ro = int(ep.ro_tick[0, k])
        for o in offsets:
            site, s0s = res["res"]["site"][o]
            chan, s0c = res["res"]["chan"][o]
            tabF = LS.pair_trial_table(res["normal"], site, chan, s0s, s0c, [k])
            tabW = follow_table(res["ns0"], s0s, s0c, ep.scored, [k])
            tau = t0 + o
            for p in range(P):
                if not (tabF["ok"][p, k] or tabW["ok"][p, k]):
                    continue
                a, s = int(res["ro_site"][2 * p]), int(src[2 * p])
                d = set()
                for m in (2 * p, 2 * p + 1):
                    d |= {x for x in wi[m].get(a, ()) if x[0] >= t0 and x[1] <= ro}
                f = p8_features(d, a, s, tau)
                srcc = [x for x in d if x[2] == s]
                te1 = min(x[0] for x in srcc) if srcc else None
                # plant ground truth helper: did any source copy to a carry PAY0 != 0 (first broadcast)?
                pay0 = 0
                n1p = 0
                if name.startswith("PLANT"):
                    for m in (2 * p, 2 * p + 1):
                        sel = (cl["p"] == m) & (cl["v"] == s) & (cl["te"] >= t0)
                        for side, rk, dk in (("A", "recA", "dlA"), ("B", "recB", "dlB")):
                            pk = "payA" if side == "A" else "payB"
                            mm = sel & (cl[rk] == a) & cl[dk].astype(bool) & (cl[pk] != 0)
                            pay0 = max(pay0, int(mm.sum() > 0))
                            if te1 is not None:
                                n1p = max(n1p, int((mm & (cl["te"] == te1)).sum()))
                vals = {"pair": p, "trial": k, "o": o, "q": tau % 2,
                        "pat_frozen": str(tabF["pat"][p, k]), "ok_frozen": int(tabF["ok"][p, k]),
                        "pat_follow": str(tabW["pat"][p, k]), "ok_follow": int(tabW["ok"][p, k]),
                        "P8": f["P8_srcfirst"], "P8all": p8all_features(d, a, src_all[2 * p], tau),
                        "te1_rel": f.get("te1_rel", -999), "n1_held": f.get("n1_held", 0),
                        "n1_flight": f.get("n1_flight", 0), "n_cue_a": len(d), "n_src_a": len(srcc),
                        "n_src_first": f.get("n1_held", 0) + f.get("n1_flight", 0),
                        "n_src_later": sum(1 for x in srcc if te1 is not None and x[0] > te1),
                        "n_relay_a": sum(1 for x in d if x[2] != s),
                        "n_relay_flight": sum(1 for x in d if x[2] != s and x[0] <= tau < x[1]),
                        "n_emit_src": len({x[0] for x in srcc}), "n1_pay0": n1p, "has_pay0_a": pay0}
                for kk, v in vals.items():
                    rows[kk].append(v)
    arr = {k: np.array(v) for k, v in rows.items()}
    np.savez_compressed(OUT / f"rows_{tag}.npz", **arr)
    meta_out = {"spec": name, "meta": meta, "M": M, "ns": hex(ns), "offsets": offsets, "trials": trials, "Pd": Pd,
                "physics": ph.to_dict(), "env": env.to_dict(), "wall_s": wall, "n_rows": int(len(arr["pair"])),
                "normal_acc": float(np.nanmean(res["normal"][:, trials]))}
    (OUT / f"meta_{tag}.json").write_text(json.dumps(meta_out, indent=1, default=str))
    log(f"{name} done {wall:.0f}s rows {len(arr['pair'])} normal_acc {meta_out['normal_acc']:.3f}")
    return arr, meta_out


if __name__ == "__main__":
    name, M, ns = sys.argv[1], int(sys.argv[2]), int(sys.argv[3], 16)
    offsets = [int(x) for x in sys.argv[4].split(",")]
    tag = sys.argv[5] if len(sys.argv) > 5 else f"{name}_M{M}_ns{ns:x}"
    run(name, M, ns, offsets, tag, log=lambda s: print(s, flush=True))
