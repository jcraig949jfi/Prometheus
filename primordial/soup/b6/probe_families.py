"""B6b pre-build probe: do lane C's njit row kernels reproduce lane E7's numpy forward action-for-action?

E7 (primordial/qd/e7_run.rollout, read-only) calls fam.forward (numpy). The fused kernel would call
C's row kernels. Before building, roll out E7's own path with log=True on real brains (init and
mutated), then re-run the row kernel on every logged obs row and compare with the logged action.

  linear   linear_act_row(obs_row, W, b, stride) fed the RAW int64 obs (E7 casts int64 -> float32,
           so a negative charge bucket stays negative; masking to uint16 would change it)
  tt_feat  tt_feat_act_row(obs_row, al, G, Wo, stride, v, u) fed uint16-masked obs (top digit is
           invariant under 16-bit two's-complement masking)
Each mismatch is classified against fam.ref_logits (float64): tie = not a clear row (gm.clear_rows).

usage: python -m primordial.soup.b6.probe_families --worlds 1,3,4 --P 64 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json

import numpy as np
from numba import njit

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7


@njit(nogil=True, boundscheck=False)
def _linear_rows(obs, gidx, W, b, out):
    for i in range(obs.shape[0]):
        out[i] = gm.linear_act_row(obs[i], W[gidx[i]], b[gidx[i]], 1)


@njit(nogil=True, boundscheck=False)
def _tt_feat_rows(obs, gidx, al, G, Wo, out):
    r = al.shape[1]
    v = np.empty(r, dtype=np.float32)
    u = np.empty(r, dtype=np.float32)
    for i in range(obs.shape[0]):
        out[i] = gm.tt_feat_act_row(obs[i], al[gidx[i]], G[gidx[i]], Wo[gidx[i]], 1, v, u)


def probe(gs: int, fam_name: str, P: int, mutate_steps: int) -> dict:
    g7 = E7.G7(gs, fam_name)
    rng = np.random.default_rng([4242, gs, len(fam_name)])
    g = g7.init(rng, P)
    for _ in range(mutate_steps):
        g = g7.mutate(rng, g)
    seeds = E7.TRAIN if hasattr(E7, "TRAIN") else np.arange(9100, 9108)
    _, _, _, L = E7.rollout(g7, g, seeds, log=True)
    obs_all, idx_all, live_all = L["obs"], L["idx"], L.get("live")
    T, n, S, D = obs_all.shape
    k = len(seeds)
    genv = np.repeat(np.arange(P), k)
    gidx = np.broadcast_to(genv[None, :, None], (T, n, S)).reshape(-1).astype(np.int64)
    obs = obs_all.reshape(-1, D)
    want = idx_all.reshape(-1).astype(np.int64)
    keep = live_all.reshape(-1) if live_all is not None else np.ones(len(want), bool)
    obs, gidx, want = obs[keep], gidx[keep], want[keep]
    got = np.empty(len(want), np.int64)
    p = g[0]
    if fam_name == "linear":
        W, b = (np.ascontiguousarray(x, np.float32) for x in p)
        _linear_rows(np.ascontiguousarray(obs, np.int64), gidx, W, b, got)
    else:
        al, G, Wo = (np.ascontiguousarray(x, np.float32) for x in p)
        _tt_feat_rows(np.ascontiguousarray(obs & 0xFFFF, np.uint16), gidx, al, G, Wo, got)
    mism = np.nonzero(got != want)[0]
    ties = 0
    for i in mism[:2000]:
        ref = g7.fam.ref_logits(g7.fam.one(p, int(gidx[i])), obs[i:i + 1])
        ties += int(not gm.clear_rows(ref)[0])
    return {"world_seed": gs, "family": fam_name, "P": P, "mutate_steps": mutate_steps, "rows": int(len(want)),
            "negative_obs_rows": int((obs < 0).any(1).sum()), "mismatches": int(len(mism)),
            "mismatch_ties": ties, "mismatch_clear": int(min(len(mism), 2000) - ties)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,3,4")
    ap.add_argument("--P", type=int, default=64)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for gs in (int(x) for x in a.worlds.split(",")):
        for fam in ("linear", "tt_feat"):
            for steps in (0, 50):
                r = probe(gs, fam, a.P, steps)
                rows.append(r)
                print(json.dumps(r), flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
