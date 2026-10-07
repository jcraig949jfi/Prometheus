"""Mirror-pair carrier swap, version 2 (72h push repair window). New, versioned code: prometheus/ananke/lens.py and
lens_swap.py are untouched, so no recorded C1/C1b/ARC verdict changes.

Fixes the four MATERIAL findings of the 2026-10-07 independent review (research/CORRECTIONS_2026-10-07_SWAP_REVIEW.md):
  M1 empty swaps: before swapping, count the mirror pairs whose component actually DIFFERS between twins at the hook
     tick (applied-ness census). A swap with 0 differing pairs is EMPTY_SWAP ("carries no twin difference at this
     tick"), never NO_EFFECT evidence.
  M2 offsets: the hook tick must lie in [trial onset, readout tick - 1] of the targeted trial (asserted).
  M3 competence: a verdict requires a competent specimen on the targeted trials (normal pair accuracy mean > .60 and
     studentized lo99 > .55); otherwise INCOMPETENT.
  M4 point-estimate calls: verdicts use studentized (BOOTT) 99% intervals of the relative TRANSFER statistic.
TRANSFER per pair = (normal - swapped) / (2*normal - 1), computed on the pooled targeted trials, i.e. the fraction of
the decision that moved with the swapped component (1 = complete transfer, 0 = none). Verdict:
  FLIP       transfer lo99 > .80
  NO_EFFECT  transfer hi99 < .20 (and the swap was applied in >= 1 pair)
  PARTIAL    otherwise
Components: any World array in lens.SITE_ARRAYS / FLIGHT_ARRAYS, optionally restricted to one index of the LAST axis
(e.g. ("S", 2) = state register 2 only; ("Msum", 1) = payload component 1 only).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a"))
import c2a_common as C  # noqa: E402
from prometheus.ananke import envs, inference, lens  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402


def _get(w, name):
    return getattr(w, name)


def differs(w: World, comp) -> int:
    """Number of mirror pairs whose component differs between twins (applied-ness census)."""
    name, sub = comp
    a = _get(w, name)
    p = lens.partner_index(w.B, w.dev)
    if name in lens.FLIGHT_ARRAYS:
        x, y = a, a[:, p]
        if sub is not None:
            x, y = x[..., sub], y[..., sub]
        d = (x != y).reshape(x.shape[0], x.shape[1], -1).any(-1).any(0)       # [B]
    else:
        x, y = a, a[p]
        if sub is not None:
            x, y = x[..., sub], y[..., sub]
        d = (x != y).reshape(x.shape[0], -1).any(-1)                            # [B]
    return int(d.view(-1, 2)[:, 0].sum().item())


def swap_comp(w: World, comp):
    name, sub = comp
    if name == "w" and not w.R:
        return
    a = _get(w, name)
    p = lens.partner_index(w.B, w.dev)
    if name in lens.FLIGHT_ARRAYS:
        if sub is not None:
            a[..., sub].copy_(a[:, p][..., sub])
        else:
            a.copy_(a[:, p])
    else:
        if sub is not None:
            a[..., sub].copy_(a[p][..., sub])
        else:
            a.copy_(a[p])


def carrier_swap(ph, genome, env, seeds, comps, trials, offset, device="cpu"):
    """Swap `comps` (list of (array, sub)) between mirror twins `offset` ticks after the onset of each trial in
    `trials` (one trial per run, pooled). Returns the v2 verdict dict."""
    M = len(seeds)
    assert M % 2 == 0
    Pd = env.period()
    ro_off = env.delta if env.family in ("RELAY", "XOR", "MAJ", "FLIP") else env.cue_len + env.gap
    assert 0 <= offset < ro_off, f"swap offset {offset} outside [0, {ro_off}) (M2: must precede the readout)"
    normal_runs, swap_runs, applied = [], [], []
    tr_n = lens.run(ph, genome, env, seeds, device=device)
    for k in trials:
        tick = k * Pd + offset
        cnt = {}

        def hook(w, comps=comps, cnt=cnt):
            cnt["differ"] = sum(differs(w, c) for c in comps)
            for c in comps:
                swap_comp(w, c)
        tr_s = lens.run(ph, genome, env, seeds, hooks={tick: hook}, device=device)
        normal_runs.append(tr_n.per_trial[:, k]); swap_runs.append(tr_s.per_trial[:, k]); applied.append(cnt["differ"])
    n = np.stack(normal_runs, 1); s = np.stack(swap_runs, 1)                     # [M, len(trials)]
    pn = n.reshape(M // 2, 2, -1).mean((1, 2)); ps = s.reshape(M // 2, 2, -1).mean((1, 2))
    mn, lo_n, _ = inference.pair_ci_student(pn)
    out = {"comps": [list(c) for c in comps], "trials": list(trials), "offset": offset, "applied_pairs": applied,
           "normal_mean": float(mn), "normal_lo99": float(lo_n), "swapped_mean": float(ps.mean())}
    if sum(applied) == 0:
        out["verdict"] = "EMPTY_SWAP"
        return out
    if not (mn > 0.60 and lo_n > 0.55):
        out["verdict"] = "INCOMPETENT"
        return out
    denom = np.maximum(2 * pn - 1, 1e-6)
    transfer = (pn - ps) / denom
    tm, tlo, thi = inference.pair_ci_student(transfer)
    out.update(transfer_mean=float(tm), transfer_lo99=float(tlo), transfer_hi99=float(thi))
    out["verdict"] = "FLIP" if tlo > 0.80 else ("NO_EFFECT" if thi < 0.20 else "PARTIAL")
    return out
