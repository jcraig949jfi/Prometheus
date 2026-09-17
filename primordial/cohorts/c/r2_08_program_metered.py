"""C-R2-08: drawn cell small_program / w4 / decoder_rent / numpy / metered_stream (draw seed 13312927878363306578).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. None of the three
non-world axes had a closed-loop definition; the definitions below are fixed before any run.

  world     w4 (E4.Spec(4)): D=8 obs features (uint16 registers + charge nibble), S=1, W=3, T=64. Untouched.
  brain     small_program (C3's digit program as a policy): genome = 4 feature selectors (byte % D) + 3 op codes
            (byte % 6, C3's ops add sub mul xor and or on nibbles) + lane E's codebook C[8, W] (row 0 abstain).
            x_f = top nibble of feature f; e = o3(o2(o1(x_a, x_b), x_c), x_d) & 15; action row = e & 7.
            Genome bytes: 7 program + 24 codebook -> 32 (padded to 4). The interpreter holds no target.
  channel   metered_stream (D1's settlement rule, numpy): the brain's observations arrive through a metered
            stream with its OWN ledger, kept apart from world charge (D1: two ledgers). Each tick, per env/slot:
            ledger += CREDIT; cost = ALPHA * 4 bits * (distinct features the program reads); if ledger >= cost
            the digits are delivered and ledger -= cost, else the brain hears silence (all digits 0).
            ALPHA = 2 (D1 audit alpha_int), CREDIT = ALPHA * 8 (two nibbles per tick), START = ALPHA * 16.
  pressure  decoder_rent: selection fitness = world fitness - BETA * (distinct action rows used per episode),
            summed over seeds; BETA = 1. World charge and held-out scores are reported without rent.
  arms      cell (meter + rent) vs control (same brain, no meter, no rent). 200 gens x 128 each (the round 1
            baseline's budget; ~0.05 s/gen measured, 16 runs well within 600 s), 8 run seeds,
            GA stream PCG64([4200, run_seed, arm]); E6's 8 train seeds,
            top-16 by selection fitness, held-out world charge on E6's 64 seeds.
  primary   median held64 (cell arm) >= 89.94 - 0.5 * 6.11 = 86.885 (w4 train8_held64 linear baseline).
            Clause A is reported only: the pressure differs from the baseline's, so it is not a clause A claim.
  oracles   run seed 0, each arm, on HELD8:
            world  wforge replay of recorded actions: honest 0/16 failing, skip_lin >= 14/16
            brain  scalar integer reference interpreter on the DELIVERED digits == logged action rows on every live
                   row (programs have no ties); cheat skip_op2 (e = o3(o1(x_a, x_b), x_d)) mismatches >= 14/16
            meter  scalar ledger replay == logged delivery flags on every live row; cheat free_unaffordable
                   (deliver when unaffordable) is flagged (cell arm only)

  python -m primordial.cohorts.c.r2_08_program_metered [--gens 200] [--run-seeds 0-7]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis

from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b1.np_world import NpEncounter

EXP = "C-R2-08-small-program-w4-decoder-rent-metered"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
GS, BATCH, A, PB = 4, 128, 8, 7
ALPHA, BETA = 2, 1
CREDIT, START = ALPHA * 8, ALPHA * 16
CELL = {"representation": "small_program", "world": "w4", "pressure": "decoder_rent", "substrate": "numpy",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="none_control", channel="none")
BASE_MEDIAN, BASE_IQR = 89.94, 6.11
OPS = (lambda a, b: (a + b) & 15, lambda a, b: (a - b) & 15, lambda a, b: (a * b) & 15,
       lambda a, b: a ^ b, lambda a, b: a & b, lambda a, b: a | b)


class ProgGenome:
    def __init__(self):
        self.spec = E4.Spec(GS)
        m = self.spec.mech
        self.D, self.S, self.W, self.T = len(m.obs_perm), m.n_slots, m.act_width, m.horizon
        self.cb = A * self.W
        self.glen = (PB + self.cb + 3) // 4 * 4

    def init(self, rng, P):
        C = rng.integers(0, 16, size=(P, A, self.W), dtype=np.uint8)
        C[:, 0] = 0
        return rng.integers(0, 256, (P, PB), dtype=np.uint8), C

    def mutate(self, rng, g):
        p, C = g
        p = np.where(rng.random(p.shape) < 1.0 / PB, rng.integers(0, 256, p.shape, dtype=np.uint8), p)
        m = rng.random(C.shape) < 1.0 / (A * self.W)
        C = np.where(m, rng.integers(0, 16, C.shape, dtype=np.uint8), C)
        C[:, 0] = 0
        return p, C

    def pack(self, g):
        p, C = g
        out = np.zeros((len(C), self.glen), np.uint8)
        out[:, :PB] = p
        out[:, PB:PB + self.cb] = C.reshape(len(C), -1)
        return out

    def unpack(self, B):
        return B[:, :PB].copy(), B[:, PB:PB + self.cb].reshape(-1, A, self.W).copy()

    def decode(self, p):
        feats = p[:, :4].astype(np.int64) % self.D
        ops = p[:, 4:7].astype(np.int64) % 6
        nf = np.array([len(set(r)) for r in feats], np.int64)
        return feats, ops, nf


def _apply(op, a, b):
    out = np.empty_like(a)
    for k in range(6):
        sel = op == k
        if sel.any():
            out[sel] = OPS[k](a[sel], b[sel])
    return out


def program(feats, ops, dig, cheat=False):
    """feats [n,4], ops [n,3], dig [n,D] nibbles -> action rows [n]."""
    x = np.take_along_axis(dig, feats, axis=1)
    e = _apply(ops[:, 0], x[:, 0], x[:, 1])
    if not cheat:
        e = _apply(ops[:, 1], e, x[:, 2])
    e = _apply(ops[:, 2], e, x[:, 3]) & 15
    return e & 7


def rollout(pg, g, seeds, metered, rent, world_cheat="", cheat=False, meter_cheat=False, log=False):
    p, C = g
    P, k, S, D, W = len(C), len(seeds), pg.S, pg.D, pg.W
    n = P * k
    feats, ops, nf = pg.decode(p)
    genv = np.repeat(np.arange(P), k)
    f_env, o_env = feats[genv], ops[genv]
    cost = (ALPHA * 4 * nf[genv])[:, None].repeat(S, 1)
    w = NpEncounter(pg.spec.mech, pg.spec.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(seeds, P))
    ledger = np.full((n, S), START, np.int64)
    used = np.zeros((n, A), bool)
    abst, mag, cnt = np.zeros(n), np.zeros(n), np.zeros(n)
    L = {"acts": np.zeros((pg.T, n, S, W), np.int32), "dig": np.zeros((pg.T, n, S, D), np.int64),
         "idx": np.zeros((pg.T, n, S), np.int64), "live": np.zeros((pg.T, n, S), bool),
         "deliv": np.zeros((pg.T, n, S), bool)} if log else None
    for t in range(pg.T):
        dig = (obs.astype(np.int64) >> 12) & 15
        live = w.alive & ~w.done[:, None]
        if metered:
            ledger += CREDIT
            ok = ledger >= cost
            deliv = ok | meter_cheat
            ledger -= np.where(ok, cost, 0)
            dig = np.where(deliv[:, :, None], dig, 0)
        else:
            deliv = np.ones((n, S), bool)
        idx = np.stack([program(f_env, o_env, dig[:, s], cheat) for s in range(S)], 1)
        a = C[genv[:, None], idx].astype(np.int32)
        used[np.arange(n)[:, None].repeat(S, 1)[live], idx[live]] = True
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        if log:
            L["acts"][t], L["dig"][t], L["idx"][t], L["live"][t], L["deliv"][t] = a, dig, idx, live, deliv
        obs, _, done = w.step(a)
        if done.all():
            break
    world_fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int64)
    rent_paid = (BETA * used.sum(1)).reshape(P, k).sum(1) if rent else np.zeros(P, np.int64)
    sel_fit = (world_fit - rent_paid).astype(np.int32)
    tot = np.maximum(cnt.reshape(P, k).sum(1), 1)
    ab = abst.reshape(P, k).sum(1) / tot
    mg = mag.reshape(P, k).sum(1) / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return sel_fit, cells, world_fit, rent_paid, w, L, (feats, ops, nf, genv)


def world_oracle(pg, g, seeds, metered, rent, world_cheat=""):
    _, _, _, _, w, L, _ = rollout(pg, g, seeds, metered, rent, world_cheat=world_cheat, log=True)
    hashes = [h.decode() for h in w.trace_hashes()]
    k, P = len(seeds), len(g[1])
    ep = np.clip(w.charge, 0, None)
    bad = np.zeros(P, bool)
    for e in range(P * k):
        h, ch = E4.wforge_replay(pg.spec, L["acts"][:, e], seeds[e % k])
        bad[e // k] |= (h != hashes[e]) or not np.array_equal(ch, ep[e])
    return {"elites": P, "elites_failing": int(bad.sum())}


def brain_oracle(pg, g, seeds, metered, rent, cheat=False):
    _, _, _, _, _, L, (feats, ops, nf, genv) = rollout(pg, g, seeds, metered, rent, cheat=cheat, log=True)
    P = len(g[1])
    bad, rows, mism = np.zeros(P, bool), 0, 0
    for t, e, s in zip(*np.nonzero(L["live"])):
        x = [int(L["dig"][t, e, s, int(f)]) for f in feats[genv[e]]]
        o = [int(v) for v in ops[genv[e]]]
        v = OPS[o[2]](OPS[o[1]](OPS[o[0]](x[0], x[1]), x[2]), x[3]) & 15
        rows += 1
        if (v & 7) != int(L["idx"][t, e, s]):
            mism += 1
            bad[genv[e]] = True
    return {"elites": P, "elites_mismatching": int(bad.sum()), "rows": rows, "mismatched_rows": mism}


def meter_oracle(pg, g, seeds, meter_cheat=False):
    _, _, _, _, _, L, (feats, ops, nf, genv) = rollout(pg, g, seeds, True, True, meter_cheat=meter_cheat, log=True)
    n, S = L["live"].shape[1:]
    rows = mism = 0
    for e in range(n):
        c = ALPHA * 4 * int(nf[genv[e]])
        for s in range(S):
            led = START
            for t in range(pg.T):
                led += CREDIT
                ok = led >= c
                if ok:
                    led -= c
                if L["live"][t, e, s]:
                    rows += 1
                    mism += int(ok != bool(L["deliv"][t, e, s]))
    return {"rows": rows, "mismatched_rows": mism}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=200)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    r = redis.Redis(host="127.0.0.1", port=a.port)
    pg = ProgGenome()
    arms = (("cell", True, True, CELL), ("control", False, False, CELL_CTRL))
    held = {"cell": [], "control": []}
    ok_arm = {}
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        for rs in range(lo, hi + 1):
            for ai, (arm, metered, rent, cell) in enumerate(arms):
                t0 = time.perf_counter()
                arch = LuaArchive(r, f"c-r2-08-{arm}-{rs}", pg.glen, UNSEEDED)
                arch.clear()
                rng = np.random.Generator(np.random.PCG64([4200, rs, ai]))
                for _ in range(a.gens):
                    par = arch.sample(BATCH)
                    g = pg.init(rng, BATCH) if len(par) == 0 else pg.mutate(rng, pg.unpack(par))
                    sel, cells = rollout(pg, g, E7.TRAIN, metered, rent)[:2]
                    arch.insert(cells, sel, pg.pack(g), np.zeros((BATCH, 2), np.uint32))
                el = arch.dump()
                raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:E7.TOP]),
                                    np.uint8).reshape(-1, pg.glen)
                arch.clear()
                top = pg.unpack(raw)
                _, _, wf_tr, rent_tr = rollout(pg, top, E7.TRAIN, metered, rent)[:4]
                _, _, wf_h, rent_h = rollout(pg, top, E7.HELD64, metered, rent)[:4]
                nf = pg.decode(top[0])[2]
                row = {"kind": "run", "arm": arm, "cell": cell, "run_seed": rs, "gens": a.gens, "genomes": a.gens * BATCH,
                       "cells": len(el), "genome_bytes": pg.glen,
                       "train_world_per_seed": float(wf_tr.mean() / len(E7.TRAIN)),
                       "held64_per_seed": float(wf_h.mean() / len(E7.HELD64)),
                       "held64_rent_per_seed": float(rent_h.mean() / len(E7.HELD64)),
                       "elite_distinct_features_median": float(np.median(nf)),
                       "status": "record" if arm == "cell" else "control"}
                if rs == lo:
                    row["world_oracle_honest"] = world_oracle(pg, top, E7.HELD8, metered, rent)
                    row["world_oracle_skip_lin"] = world_oracle(pg, top, E7.HELD8, metered, rent, "skip_lin")
                    row["brain_oracle_honest"] = brain_oracle(pg, top, E7.HELD8, metered, rent)
                    row["brain_oracle_skip_op2"] = brain_oracle(pg, top, E7.HELD8, metered, rent, cheat=True)
                    ok = (row["world_oracle_honest"]["elites_failing"] == 0
                          and row["world_oracle_skip_lin"]["elites_failing"] >= 14
                          and row["brain_oracle_honest"]["mismatched_rows"] == 0 and row["brain_oracle_honest"]["rows"] > 0
                          and row["brain_oracle_skip_op2"]["elites_mismatching"] >= 14)
                    if metered:
                        row["meter_oracle_honest"] = meter_oracle(pg, top, E7.HELD8)
                        row["meter_oracle_free_unaffordable"] = meter_oracle(pg, top, E7.HELD8, meter_cheat=True)
                        ok = ok and row["meter_oracle_honest"]["mismatched_rows"] == 0 \
                            and row["meter_oracle_free_unaffordable"]["mismatched_rows"] > 0
                    ok_arm[arm] = ok
                row["wall_s"] = round(time.perf_counter() - t0, 2)
                held[arm].append(row["held64_per_seed"])
                print(json.dumps(row), flush=True)
                w.write(row)
        st = {arm: tuple(float(x) for x in np.percentile(held[arm], [25, 50, 75])) for arm in held}
        oracle_clean = ok_arm.get("cell", False) and ok_arm.get("control", False)
        threshold = BASE_MEDIAN - 0.5 * BASE_IQR
        med = st["cell"][1]
        summary = {"kind": "summary", "cell": CELL, "n_runs": len(held["cell"]),
                   "held64_median_cell": round(med, 3), "iqr_cell": round(st["cell"][2] - st["cell"][0], 3),
                   "held64_median_control": round(st["control"][1], 3),
                   "iqr_control": round(st["control"][2] - st["control"][0], 3),
                   "threshold": threshold, "oracle_clean": oracle_clean,
                   "clause_a_report_only_train8": qd_ledger.check(qd_ledger.load(), "w4", "train8_held64", med,
                                                                  st["cell"][2] - st["cell"][0], pg.glen,
                                                                  len(held["cell"]), oracle_clean),
                   "primary": ("INDETERMINATE" if not oracle_clean else
                               ("PASS" if len(held["cell"]) >= 8 and med >= threshold else "FAIL")),
                   "status": "record" if oracle_clean else "cheat"}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for arm, cell, status in (("cell", CELL, summary["status"]), ("control", CELL_CTRL, "control")):
            q.write({"cell": cell, "mechanism": f"closed_loop_small_program_{arm}_{a.gens}gens",
                     "fitness": {"held64_median": round(st[arm][1], 3), "iqr": round(st[arm][2] - st[arm][0], 3),
                                 "n_runs": len(held[arm])},
                     "footprint": {"genome_bytes": int(pg.glen)},
                     "oracle": "clean (world replay + skip_lin, integer program reference + skip_op2, ledger replay + "
                               "free_unaffordable)" if oracle_clean else "NOT clean",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
