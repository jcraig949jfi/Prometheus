"""D-R6-3 (ANOM-1789488929775-0, child of D-R6-2): is the skip-odd oracle's blindness on HELD8 a seed-coverage limit?

D-R6-2 found int2 elites 0 and 1 (B-R2-4 w4 train128 rs0) with 0 flipping rows on their HELD8 skip-odd trajectory,
while held64 under fused brain_stride 2 differs from honest for 16/16 elites. The world is deterministic, so a seed's
charge can differ under the cheat only if the cheat trajectory takes a different action on some live row. Zero QD:
the same committed top_hex genomes, numpy E7.rollout honest and cheat on each HELD64 seed.

Per elite e, per seed s in HELD64:
  charge_diff[e,s]  clipped final charge (summed over slots) differs honest vs cheat
  any_flip[e,s]     on the cheat trajectory, >= 1 live row where the honest float64 argmax != the cheat action
                    (every row, clear or tied; clear-row flips reported separately)
Rule (fixed before reading):
  I1  numpy honest / cheat per-elite HELD64 fitness == fused brain_stride 1 / 2 for 16/16, and D-R6-2's held64 per
      seed (stride 1 and 2) reproduced for 16/16 -- else INDETERMINATE.
  PATH_DISAGREE  any (e, s) with charge_diff and no any_flip.
  COVERAGE       no such (e, s), AND for elites 0 and 1: >= 1 seed with charge_diff, and none of those seeds in HELD8.
  NOT_COVERAGE   otherwise (e.g. elites 0/1 charge_diff seeds include a HELD8 seed, or neither has any charge_diff).
Control: planted_zero_odd (elite 0 odd weights zeroed) must show 0 any_flip seeds and 0 charge_diff seeds.
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from primordial.cohorts.d import r6_2_skip_odd_blind_int2 as R2
from primordial.qd import e7_run as E7
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R6-3-skip-odd-held64-coverage"
PREDICATE_ID = EXP
ANOMALY = "1789488929775-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
D_R6_2_ROWS = "primordial/ledger/rows/D/D-R6-2-skip-odd-blind-int2.jsonl"


def per_seed(g7, g, seeds):
    """-> (honest charge [P, k], cheat charge [P, k], any_flip [P, k], clear_flips [P, k])."""
    P, k = len(g[1]), len(seeds)
    _, _, wh, _ = E7.rollout(g7, g, seeds, log=False)
    _, _, wc, L = E7.rollout(g7, g, seeds, cheat=True, log=True)
    ch = np.clip(wh.charge, 0, None).sum(1).reshape(P, k)
    cc = np.clip(wc.charge, 0, None).sum(1).reshape(P, k)
    (W, b), _ = g
    anyf = np.zeros((P, k), np.int64)
    clrf = np.zeros((P, k), np.int64)
    for q in range(P):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        env = e_i + q * k
        ref = R2.logits64(W[q], b[q], L["obs"][t_i, env, s_i], skip_odd=False)
        diff = ref.argmax(1) != L["idx"][t_i, env, s_i]
        ok = R2.gm.clear_rows(ref)
        np.add.at(anyf[q], e_i, diff.astype(np.int64))
        np.add.at(clrf[q], e_i, (diff & ok).astype(np.int64))
    return ch, cc, anyf, clrf


def decide(i1: bool, control_ok: bool, charge_diff, any_flip, seeds, held8, watch=(0, 1)) -> tuple[str, dict]:
    bad = [(int(e), int(seeds[s])) for e, s in zip(*np.nonzero(charge_diff & (any_flip == 0)))]
    in8 = np.isin(np.asarray(seeds), np.asarray(held8))
    w = {str(e): {"charge_diff_seeds": int(charge_diff[e].sum()), "charge_diff_in_held8": int((charge_diff[e] & in8).sum())}
         for e in watch}
    if not (i1 and control_ok):
        return "INDETERMINATE", {"path_disagree": bad, "watch": w}
    if bad:
        return "PATH_DISAGREE", {"path_disagree": bad, "watch": w}
    cov = all(v["charge_diff_seeds"] >= 1 and v["charge_diff_in_held8"] == 0 for v in w.values())
    return ("COVERAGE" if cov else "NOT_COVERAGE"), {"path_disagree": bad, "watch": w}


def job(ctx, status="record"):
    t0 = time.perf_counter()
    text = (R2.ROOT / R2.SRC_ROWS).read_text(encoding="utf-8")
    q = R2.QLin(R2.GS, R2.BITS)
    raw, g = R2.genomes(q, R2.source_row(text))
    g7, H8, H64 = q.g7, E7.HELD8, E7.HELD64
    ch, cc, anyf, clrf = per_seed(g7, g, H64)
    fh = FusedRollout(g7.spec, len(raw), H64, family="linear").run(g, brain_stride=1)[0]
    fc = FusedRollout(g7.spec, len(raw), H64, family="linear").run(g, brain_stride=2)[0]
    prev = [json.loads(l) for l in (R2.ROOT / D_R6_2_ROWS).read_text(encoding="utf-8").splitlines() if l.strip()][-1]
    ph = [p["held64_honest"] for p in prev["per_elite"]]
    pc = [p["held64_stride2"] for p in prev["per_elite"]]
    k = len(H64)
    i1 = {"numpy_honest_eq_fused_stride1_16": bool(np.array_equal(ch.sum(1).astype(np.int64), fh.astype(np.int64))),
          "numpy_cheat_eq_fused_stride2_16": bool(np.array_equal(cc.sum(1).astype(np.int64), fc.astype(np.int64))),
          "d_r6_2_held64_stride1_reproduced": bool(np.allclose(fh / k, ph, atol=0, rtol=0)),
          "d_r6_2_held64_stride2_reproduced": bool(np.allclose(fc / k, pc, atol=0, rtol=0))}
    (W, b), C = g
    Wz = W.copy()
    Wz[:, 1::2, :] = 0.0
    gz = ((Wz[:1], b[:1]), C[:1])
    zh, zc, za, _ = per_seed(g7, gz, H64)
    control = {"any_flip_seeds": int((za[0] > 0).sum()), "charge_diff_seeds": int((zh[0] != zc[0]).sum())}
    control["ok"] = control["any_flip_seeds"] == 0 and control["charge_diff_seeds"] == 0
    cdiff = ch != cc
    decision, detail = decide(all(i1.values()), control["ok"], cdiff, anyf, list(H64), list(H8))
    in8 = np.isin(np.asarray(H64), np.asarray(H8))
    per = [{"elite": e, "charge_diff_seeds": int(cdiff[e].sum()), "any_flip_seeds": int((anyf[e] > 0).sum()),
            "clear_flip_seeds": int((clrf[e] > 0).sum()), "any_flips_total": int(anyf[e].sum()),
            "clear_flips_total": int(clrf[e].sum()), "any_flip_seeds_in_held8": int(((anyf[e] > 0) & in8).sum()),
            "charge_diff_seeds_in_held8": int((cdiff[e] & in8).sum()),
            "charge_honest_minus_cheat": int((ch[e] - cc[e]).sum())} for e in range(len(raw))]
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{R2.GS}", "representation": f"linear_int{R2.BITS}_nibble",
              "qd_runs": 0, "source_rows": R2.SRC_ROWS, "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "d_r6_2_rows": D_R6_2_ROWS, "seeds": "E7.HELD64", "held8_in_held64": int(in8.sum()),
              "checks": {"I1": i1, "control_ok": bool(control["ok"])}, "control_planted_zero_odd": control,
              "per_elite": per, "detail": detail, "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
