"""FLIP balanced-accuracy (B) certificate: per-trial FLIP decomposition and the B > .75 inference reading.

Promoted from W2-S (w2s_common.flip_eval, t1_balanced.py; theorem in copy_class_enum.py, REPORT F3).

FLIP: y_k = m_k x_k with the mapping m constant within a block and alternating between blocks. Split scored
trials by whether the cue changed from the previous trial (chg) or not (same). A COPY-class policy (answer from
the previous teacher/answer without inferring m, e.g. RELAY_LATCH) is exactly 1/2 on changed-cue trials, so
  B = (acc_same + acc_chg) / 2  <=  .75   for every copy-class policy (an EXPECTATION bound),
while overall accuracy is not bounded by .75 (it rises with the share of same-cue trials: RELAY_LATCH scores
.766 overall at 996716ac where changed cues are 47% of trials). The sound certificate is the pair-CI lower
bound: B lo99 > .75 (W2-S F3c). FLIP_CHANGE (changed-cue lo99 > .55) is NOT a sound inference certificate
(an anti-copy policy passes it); keep it only for known-code plants whose same-cue branch is the teacher hold.

Caveat (W2-S F6): B > .75 is unattainable wherever reach q < 1; at weak-reach physics no reading can be
certified as inference. Check the ceiling (audit.ceilings, flip 'joint_episode') before reading a FAIL as
evidence of absence.
"""
from __future__ import annotations

import numpy as np

from prometheus.explib.outcomes import FAIL, NOT_VERIFIED, PASS, Check

from . import runner

B_BAR = 0.75


def flip_eval(ph, genome, env, seeds, ctrl=None, detail: bool = True, device: str = "cpu") -> dict:
    """runner.run semantics + the FLIP per-trial decomposition (keys as W2-S: acc/lo99/hi99, chg*, same*,
    bal* (= B), chg_frac, src (answer-source table), tab (by mapping sign x change), ro_zero_frac)."""
    pairs, corr, ep, trace = runner.run(ph, genome, env, seeds, ctrl=ctrl, device=device)
    M = len(seeds)
    o = {"M": M, **runner.ci(pairs), "pairs": pairs.tolist()}
    if not detail or env.family != "FLIP":
        return o
    B, tr = ep.y.shape
    Pd = env.period()
    sv = ep.schedule.sense_val.numpy()
    x = np.sign(sv[np.arange(tr) * Pd][:, :, 0]).T            # cue sign incl. mirror sign [B, tr]
    y = ep.y
    m = y * x
    if not np.all(np.abs(x) == 1):
        raise ValueError("FLIP cue sign is not +-1 at a trial onset: the decomposition does not apply")
    blk = np.arange(tr) // env.block
    same_blk = blk[1:] == blk[:-1]
    if not np.all(m[:, 1:][:, same_blk] == m[:, :-1][:, same_blk]):   # m block-constant: checks the x derivation
        raise ValueError("FLIP mapping is not block-constant under the derived cue signs")
    sc = ep.scored
    chg = np.zeros_like(sc)
    chg[:, 1:] = x[:, 1:] != x[:, :-1]

    def pooled(mask):
        num = (corr * mask).reshape(M // 2, 2, tr).sum((1, 2))
        den = mask.reshape(M // 2, 2, tr).sum((1, 2))
        keep = den > 0
        return num[keep] / den[keep]

    pc, ps = pooled(sc & chg), pooled(sc & ~chg)
    c = runner.ci(pc)
    o["chg"], o["chg_lo99"], o["chg_hi99"] = c["acc"], c["lo99"], c["hi99"]
    s = runner.ci(ps)
    o["same"], o["same_lo99"], o["same_hi99"] = s["acc"], s["lo99"], s["hi99"]
    o["chg_frac"] = float((sc & chg).sum() / sc.sum())
    if len(pc) == len(ps) == M // 2:
        b = runner.ci((pc + ps) / 2)
        o["bal"], o["bal_lo99"], o["bal_hi99"] = b["acc"], b["lo99"], b["hi99"]
    ans = np.sign(trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot])
    yp = np.zeros_like(y)
    yp[:, 1:] = y[:, :-1]
    xp = np.zeros_like(x)
    xp[:, 1:] = x[:, :-1]
    o["src"] = {nm: {"=x_k": float((ans == x)[msk].mean()), "=y_prev": float((ans == yp)[msk].mean()),
                     "=-y_prev": float((ans == -yp)[msk].mean()), "=x_prev": float((ans == xp)[msk].mean()),
                     "=0": float((ans == 0)[msk].mean())}
                for nm, msk in (("chg", sc & chg), ("same", sc & ~chg))}
    tab = {}
    for mv in (1, -1):
        for cg in (False, True):
            k = sc & (m == mv) & (chg == cg)
            tab[f"m{'+' if mv > 0 else '-'}_{'chg' if cg else 'same'}"] = \
                round(float(corr[k].mean()), 4) if k.any() else None
    o["tab"] = tab
    o["ro_zero_frac"] = float((ans[sc] == 0).mean())
    return o


def b_certificate(o: dict, bar: float = B_BAR) -> Check:
    """PASS iff B lo99 > bar. NOT_VERIFIED when B is undefined (a pair without both trial types, or a
    non-FLIP evaluation): never a pass."""
    if "bal_lo99" not in o:
        return Check("FLIP_B", NOT_VERIFIED, "B undefined (non-FLIP, or a pair lacks same- or changed-cue trials)")
    return Check("FLIP_B", PASS if o["bal_lo99"] > bar else FAIL,
                 {"B": o["bal"], "lo99": o["bal_lo99"], "hi99": o["bal_hi99"], "bar": bar,
                  "chg": o["chg"], "same": o["same"], "overall": o["acc"]})


def flip_change(o: dict, bar: float = 0.55) -> Check:
    """W2-L FLIP_CHANGE (changed-cue lo99 > .55). Valid only for known-code plants with a teacher-hold same-cue
    branch; reported for comparison, never as an inference certificate."""
    if "chg_lo99" not in o:
        return Check("FLIP_CHANGE", NOT_VERIFIED, "no changed-cue decomposition")
    return Check("FLIP_CHANGE", PASS if o["chg_lo99"] > bar else FAIL, {"chg": o["chg"], "lo99": o["chg_lo99"]})
