"""D-R6-2 (ANOM-1789418707943-0): why does the skip-odd brain cheat go blind on int2 linear brains?

B-R2-4 (w4 train128, int2 linear + nibble codebook, 32 B, run seed 0 top-16) recorded E7.brain_oracle(cheat=True)
catching 13/16 elites; the 3 blind elites do not have more zero odd weights than the rest. Two explanations:
  SAMPLE_MISS      the cheat does flip the action on some live rows, but E7's 256-row sample per elite missed them
  GENUINE_IGNORE   on the cheat trajectory the action never depends on the odd features (the cheat has no power)
Zero QD: the 16 genomes are B's committed top_hex. The census reads EVERY live row of the cheat trajectory (float64
logits, gm.clear_rows) instead of a 256-row sample.

Rule (fixed before reading):
  I1  the recomputed oracle reproduces B's row exactly (cheat: 13 elites mismatching, 709 rows, 4096 clear; honest 0
      mismatched) and fused == numpy fitness on HELD8 for 16/16 -- else INDETERMINATE.
  blind set = elites with 0 sampled mismatches in the recomputed cheat oracle.
  per blind elite: census flips >= 1 -> SAMPLE_MISS; 0 -> GENUINE_IGNORE.
  decision SAMPLE_MISS / GENUINE_IGNORE when every blind elite agrees, MIXED otherwise.
Controls: planted_zero_odd (elite 0 with its odd-feature weights zeroed) must census 0 flips and score equal under
brain_stride 2; honest_census (honest trajectory, honest vs honest argmax) must find 0 flips.
Reported, not judged: held64 per seed honest vs brain_stride 2 for all 16, odd |W| mass fraction, flips per elite.

    worker.submit("D", "primordial.cohorts.d.r6_2_skip_odd_blind_int2:job", EXP, ROWS, 600, envelope={...PRODUCTION...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.cohorts.b.b1_qlinear import QLin
from primordial.qd import e7_run as E7
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R6-2-skip-odd-blind-int2"
PREDICATE_ID = EXP
ANOMALY = "1789418707943-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC_ROWS = "primordial/ledger/rows/B/B-R2-4-int2-linear-nibble-w4-train128.jsonl"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
GS, BITS = 4, 2
B_ORACLE = {"cheat": {"elites": 16, "elites_mismatching": 13, "mismatched_rows": 709, "clear_rows": 4096},
            "honest_mismatched_rows": 0}


def source_row(text: str) -> dict:
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    return [x for x in rows if int(x.get("run_seed", -1)) == 0 and x.get("brain_oracle_cheat")][-1]


def genomes(q: QLin, row: dict):
    raw = np.frombuffer(b"".join(bytes.fromhex(h) for h in row["top_hex"]), np.uint8).reshape(-1, q.glen)
    return raw, q.decode(q.unpack(raw))


def logits64(W, b, obs, skip_odd: bool) -> np.ndarray:
    """float64 linear logits for one genome (E7 Linear.logits maths, cheat zeroes the centred odd features)."""
    xs = obs.astype(np.float64) / 65535.0 - 0.5
    if skip_odd:
        xs[:, 1::2] = 0.0
    return xs @ W.astype(np.float64) + b.astype(np.float64)


def census(g7, g, seeds, cheat: bool) -> list[dict]:
    """Every live row of the (cheat or honest) trajectory: rows where the honest float64 argmax (clear rows only)
    differs from the action the trajectory's own forward took."""
    _, _, _, L = E7.rollout(g7, g, seeds, cheat=cheat, log=True)
    (W, b), _ = g
    k, P = len(seeds), len(g[1])
    out = []
    for q in range(P):
        live = L["live"][:, q * k:(q + 1) * k]
        t_i, e_i, s_i = np.nonzero(live)
        e_i = e_i + q * k
        obs = L["obs"][t_i, e_i, s_i]
        ref = logits64(W[q], b[q], obs, skip_odd=False)
        ok = gm.clear_rows(ref)
        flips = (ref.argmax(1) != L["idx"][t_i, e_i, s_i]) & ok
        out.append({"live_rows": int(len(t_i)), "clear_rows": int(ok.sum()), "flips": int(flips.sum())})
    return out


def odd_mass(W) -> list[float]:
    a = np.abs(W.astype(np.float64))
    return [float(a[q, 1::2].sum() / max(a[q].sum(), 1e-12)) for q in range(len(W))]


def fused_per_seed(g7, g, seeds, stride: int) -> np.ndarray:
    return FusedRollout(g7.spec, len(g[1]), seeds, family="linear").run(g, brain_stride=stride)[0] / len(seeds)


def decide(i1: bool, controls_ok: bool, blind: list[int], cen: list[dict]) -> str:
    if not (i1 and controls_ok) or not blind:
        return "INDETERMINATE"
    kinds = {"SAMPLE_MISS" if cen[e]["flips"] >= 1 else "GENUINE_IGNORE" for e in blind}
    return kinds.pop() if len(kinds) == 1 else "MIXED"


def job(ctx, status="record"):
    t0 = time.perf_counter()
    text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
    row = source_row(text)
    q = QLin(GS, BITS)
    raw, g = genomes(q, row)
    g7, H8, H64 = q.g7, E7.HELD8, E7.HELD64
    bc = E7.brain_oracle(g7, g, H8, cheat=True)
    bo = E7.brain_oracle(g7, g, H8)
    per_elite_cheat = [E7.brain_oracle(g7, ((g[0][0][e:e + 1], g[0][1][e:e + 1]), g[1][e:e + 1]), H8, cheat=True)
                       for e in range(len(raw))]
    fused8 = FusedRollout(g7.spec, len(raw), H8, family="linear").run(g)[0]
    np8 = E7.rollout(g7, g, H8)[0]
    i1_parts = {"cheat_equal_B": {k: bc[k] for k in B_ORACLE["cheat"]} == B_ORACLE["cheat"],
                "honest_zero": bo["mismatched_rows"] == B_ORACLE["honest_mismatched_rows"],
                "fused_eq_numpy_16": int((fused8 != np8).sum()) == 0}
    i1 = all(i1_parts.values())
    # blind set from the SAME oracle call B ran (sample depends on elite order), cross-read per elite
    cen = census(g7, g, H8, cheat=True)
    sampled = [None] * len(raw)
    _, _, _, L = E7.rollout(g7, g, H8, cheat=True, log=True)
    rng = np.random.Generator(np.random.PCG64(0))
    k = len(H8)
    for e in range(len(raw)):
        t_i, e_i, s_i = np.nonzero(L["live"][:, e * k:(e + 1) * k])
        if len(t_i) == 0:
            sampled[e] = 0
            continue
        pick = rng.choice(len(t_i), size=min(E7.N_ORACLE_ROWS, len(t_i)), replace=False)
        t_i, e_i, s_i = t_i[pick], e_i[pick] + e * k, s_i[pick]
        ref = g7.fam.ref_logits(g7.fam.one(g[0], e), L["obs"][t_i, e_i, s_i])
        ok = gm.clear_rows(ref)
        sampled[e] = int(((ref.argmax(1) != L["idx"][t_i, e_i, s_i]) & ok).sum())
    oracle_replay_equal = sum(v > 0 for v in sampled) == bc["elites_mismatching"] and sum(sampled) == bc["mismatched_rows"]
    blind = [e for e in range(len(raw)) if sampled[e] == 0]
    # controls
    (W, b), C = g
    Wz = W.copy()
    Wz[:, 1::2, :] = 0.0
    gz = ((Wz[:1], b[:1]), C[:1])
    cz = census(g7, gz, H8, cheat=True)[0]
    fz_h, fz_c = fused_per_seed(g7, gz, H64, 1)[0], fused_per_seed(g7, gz, H64, 2)[0]
    hon = census(g7, g, H8, cheat=False)
    controls = {"planted_zero_odd": {"census": cz, "held64_honest": float(fz_h), "held64_stride2": float(fz_c),
                                     "ok": cz["flips"] == 0 and float(fz_h) == float(fz_c)},
                "honest_census": {"flips_total": int(sum(x["flips"] for x in hon)), "ok": sum(x["flips"] for x in hon) == 0}}
    controls_ok = controls["planted_zero_odd"]["ok"] and controls["honest_census"]["ok"]
    decision = decide(i1 and oracle_replay_equal, controls_ok, blind, cen)
    h64_h, h64_c = fused_per_seed(g7, g, H64, 1), fused_per_seed(g7, g, H64, 2)
    mass = odd_mass(W)
    per = [{"elite": e, "sampled_mismatches": sampled[e], "per_elite_oracle_mismatched_rows": per_elite_cheat[e]["mismatched_rows"],
            **cen[e], "label": ("SAMPLE_MISS" if cen[e]["flips"] else "GENUINE_IGNORE") if e in blind else "CAUGHT",
            "odd_abs_weight_fraction": round(mass[e], 4), "held64_honest": float(h64_h[e]),
            "held64_stride2": float(h64_c[e]), "held64_equal": bool(h64_h[e] == h64_c[e])} for e in range(len(raw))]
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{GS}", "pressure": "train128_held64",
              "representation": f"linear_int{BITS}_nibble", "genome_bytes": int(q.glen), "qd_runs": 0,
              "source_rows": SRC_ROWS, "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "source_run_seed": 0, "oracle_seeds": "E7.HELD8", "sample_rows_per_elite": E7.N_ORACLE_ROWS,
              "recomputed_oracle": {"cheat": bc, "honest": bo, "fused_vs_numpy_differing": int((fused8 != np8).sum())},
              "checks": {"I1": i1_parts, "I1_all": bool(i1), "oracle_replay_equal": bool(oracle_replay_equal),
                         "controls_ok": bool(controls_ok)},
              "blind_elites": blind, "controls": controls, "per_elite": per,
              "summary": {"blind_n": len(blind), "blind_census_flips": [cen[e]["flips"] for e in blind],
                          "caught_n": len(raw) - len(blind),
                          "held64_equal_under_stride2": int(sum(x["held64_equal"] for x in per))},
              "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
