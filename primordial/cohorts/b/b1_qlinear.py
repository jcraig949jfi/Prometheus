"""B-R2-1: int4 linear closed-loop brain + nibble codebook, clause A vs the w4 train128_held64 front.

  python -m primordial.cohorts.b.b1_qlinear [--world 4] [--run-seeds 0-7] [--gens 800] [--batch 128] [--port 6391]

Genome: lane C's linear family (W [D, A], b [A]) with every parameter an integer code in [-8, 7],
plus lane E's A x W action codebook (row 0 = abstain), all packed as nibbles.
w4: D=8, A=8 -> 72 codes + 24 codebook values = 96 nibbles = 48 bytes (baseline float32 linear: 312).
Argmax of a linear map is invariant to a global positive scale, so the decoder is the codes cast to
float32 and nothing else: no scale, no table, no access to the target.

Evaluation reuses E10's closed condition exactly (E7.G7 linear, B6b FusedRollout, 800 x 128 genomes
on train seeds 9100..9227, top-16 by train fitness scored per seed on E6's 64 held-out seeds);
only the genome space and its mutation differ. Library code is read-only.

Oracles (run seed 0, E7 numpy code on HELD8): world honest 0/16 failing, skip_lin >= 14/16;
brain honest 0 mismatched clear rows, cheat (skip-odd) >= 14/16; and fused == E7.rollout fitness
per elite on HELD8 (integer weights make ties likelier, the fused kernel and numpy argmax must agree).
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.brain import genomes as gm
from primordial.cohorts.e.oracles import brain_oracle_cheats
from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger as QL
from primordial.qd import e7_run as E7
from primordial.qd import e8_run as E8
from primordial.qd import e9_run as E9
from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b6.fused import FusedRollout

EXP = "B-R2-1-int4-linear-nibble-w4-train128"
ROOT = QL.ROOT
ROWS = ROOT / "primordial" / "ledger" / "rows" / "B" / f"{EXP}.jsonl"
TRAIN = E8.seeds_n(128)
HELD64, HELD8, TOP = E7.HELD64, E7.HELD8, E7.TOP
LO, HI = -8, 7


class QLin:
    """int4 linear params + nibble codebook; decodes to E7.G7(gs, 'linear')'s (params, codebook)."""

    def __init__(self, gen_seed: int, bits: int = 4, acts: int = E7.A):
        self.g7 = E7.G7(gen_seed, "linear")
        if acts != E7.A:
            # fewer codebook rows: the fused kernel reads A from W.shape[1] and indexes codebook[p, idx];
            # E7.rollout is A-generic; brain_oracle's ref_logits reads fam.A, so the family is rebuilt.
            self.g7.fam = gm.FAMILIES["linear"](self.g7.D, acts)
            self.g7.pb, self.g7.cb = self.g7.fam.nbytes, acts * self.g7.W
            self.g7.glen = (self.g7.pb + self.g7.cb + 3) // 4 * 4
        self.D, self.A, self.W = self.g7.D, acts, self.g7.W
        self.nw, self.nb, self.nc = self.D * self.A, self.A, self.A * self.W
        self.bits = bits
        self.lo, self.hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
        self.nq = self.nw + self.nb
        self.nbits = self.nq * bits + self.nc * 4
        # padded to a multiple of 4 like E4/E7 glen (LuaArchive tie-break reads 4-byte words); bits=4 unchanged
        self.glen = ((self.nbits + 7) // 8 + 3) // 4 * 4
        # bits=4 reproduces B-R2-1/2/3 exactly: init scale 3, mutation step 1.5
        self.s0, self.s1 = 3.0 * (1 << (bits - 1)) / 8, max(0.6, 1.5 * (1 << (bits - 1)) / 8)

    def init(self, rng, P):
        Q = np.clip(np.rint(self.s0 * rng.standard_normal((P, self.nq))), self.lo, self.hi).astype(np.int8)
        C = rng.integers(0, 16, size=(P, self.A, self.W), dtype=np.uint8)
        C[:, 0] = 0
        return Q, C

    def mutate(self, rng, g, rate: float = 0.05):
        Q, C = g
        m = rng.random(Q.shape) < rate
        Q = np.clip(Q + m * np.rint(self.s1 * rng.standard_normal(Q.shape)), self.lo, self.hi).astype(np.int8)
        cm = rng.random(C.shape) < 1.0 / (self.A * self.W)
        C = np.where(cm, rng.integers(0, 16, C.shape, dtype=np.uint8), C)
        C[:, 0] = 0
        return Q, C

    def pack(self, g) -> np.ndarray:
        """Little-endian bitstream: nq codes of `bits` bits (offset by -lo), then nc 4-bit codebook values."""
        Q, C = g
        P = len(Q)
        sh = np.arange(self.bits, dtype=np.uint8)
        qb = (((Q.astype(np.int16) - self.lo).astype(np.uint8)[:, :, None] >> sh) & 1).reshape(P, -1)
        cb = ((C.reshape(P, -1)[:, :, None] >> np.arange(4, dtype=np.uint8)) & 1).reshape(P, -1)
        bitsarr = np.zeros((P, self.glen * 8), np.uint8)
        bitsarr[:, :self.nbits] = np.concatenate([qb, cb], 1)
        return np.packbits(bitsarr, axis=1, bitorder="little")

    def unpack(self, B: np.ndarray):
        P = len(B)
        bt = np.unpackbits(np.ascontiguousarray(B, np.uint8), axis=1, bitorder="little")
        nqb = self.nq * self.bits
        qv = (bt[:, :nqb].reshape(P, self.nq, self.bits) << np.arange(self.bits, dtype=np.uint8)).sum(-1)
        Q = (qv.astype(np.int16) + self.lo).astype(np.int8)
        cv = (bt[:, nqb:self.nbits].reshape(P, self.nc, 4) << np.arange(4, dtype=np.uint8)).sum(-1)
        C = cv.astype(np.uint8).reshape(P, self.A, self.W).copy()
        return Q, C

    def decode(self, g):
        """-> E7.G7 linear genome ((W [P, D, A], b [P, A]) float32, codebook)."""
        Q, C = g
        f = Q.astype(np.float32)
        return (f[:, :self.nw].reshape(-1, self.D, self.A).copy(), f[:, self.nw:].copy()), C


def score(q: QLin, raw, seeds) -> float:
    return float(FusedRollout(q.g7.spec, len(raw), seeds, family="linear").run(q.decode(q.unpack(raw)))[0].mean()
                 / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--world", type=int, default=4); p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--gens", type=int, default=0, help="0 = the pressure's round 1 setup (E10 800, E9 200)")
    p.add_argument("--batch", type=int, default=128)
    p.add_argument("--pressure", choices=("train128", "train8"), default="train128")
    p.add_argument("--port", type=int, default=6391); p.add_argument("--tag", default="full")
    p.add_argument("--no-ledger", action="store_true", help="smoke: rows as dev, no QD ledger row")
    p.add_argument("--bits", type=int, default=4, choices=(2, 3, 4), help="weight code width (codebook stays 4)")
    p.add_argument("--acts", type=int, default=E7.A, choices=(2, 4, 8), help="codebook rows (row 0 = abstain)")
    p.add_argument("--brain-cheat", choices=("skip_odd", "powered"), default="skip_odd",
                   help="binding brain-oracle cheat: E7 skip-odd, or E-T3 ablate_top + shift_action")
    a = p.parse_args()
    gs, status = a.world, ("dev" if a.no_ledger else "record")
    global EXP, ROWS, TRAIN
    # train128 = E10 closed condition (seeds 9100..9227, 800 gens); train8 = E9 (E6.TRAIN, 200 gens)
    TRAIN = E8.seeds_n(128) if a.pressure == "train128" else E7.TRAIN
    a.gens = a.gens or (800 if a.pressure == "train128" else 200)
    pname = f"{a.pressure}_held64"
    if a.acts != E7.A:
        EXP = f"B-R2-6-int{a.bits}-a{a.acts}-linear-nibble-w{gs}-{a.pressure}"
    elif a.bits == 4:
        EXP = f"B-R2-1-int4-linear-nibble-w{gs}-{a.pressure}"
    else:
        EXP = f"B-R2-4-int{a.bits}-linear-nibble-w{gs}-{a.pressure}"
    ROWS = ROWS.with_name(f"{EXP}.jsonl")
    r = redis.Redis(host="127.0.0.1", port=a.port)
    q = QLin(gs, a.bits, a.acts)
    held = []
    oracle_clean = None
    with RowWriter(ROWS, EXP, commit_every_s=120) as rw:
        for rs in E9.parse_seeds(a.run_seeds):
            t0 = time.perf_counter()
            arch = LuaArchive(r, f"b-r2-1-{gs}-{rs}-{a.tag}-b{a.bits}-a{a.acts}", q.glen, UNSEEDED)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([2101, rs, gs]))
            fr = FusedRollout(q.g7.spec, a.batch, TRAIN, family="linear")
            for _ in range(a.gens):
                par = arch.sample(a.batch)
                g = q.init(rng, a.batch) if len(par) == 0 else q.mutate(rng, q.unpack(par))
                fit, cells = fr.run(q.decode(g))[:2]
                arch.insert(cells, fit, q.pack(g), np.zeros((a.batch, 2), np.uint32))
            qd_wall = time.perf_counter() - t0
            el = arch.dump()
            raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                                np.uint8).reshape(-1, q.glen)
            arch.clear()
            row = {"exp_id": EXP, "tag": a.tag, "status": status, "gen_seed": gs, "run_seed": rs,
                   "train_seeds": len(TRAIN), "genomes": a.gens * a.batch, "genome_bytes": q.glen,
                   "cells": len(el), "qd_wall_s": round(qd_wall, 1),
                   "train_per_seed": score(q, raw, TRAIN), "held64_per_seed": score(q, raw, HELD64),
                   "top_hex": [bytes(x).hex() for x in raw]}
            if rs == 0:
                top = q.decode(q.unpack(raw))
                wo, wc = E7.world_oracle(q.g7, top, HELD8), E7.world_oracle(q.g7, top, HELD8, "skip_lin")
                bo, bc = E7.brain_oracle(q.g7, top, HELD8), E7.brain_oracle(q.g7, top, HELD8, cheat=True)
                fused_fit = FusedRollout(q.g7.spec, len(raw), HELD8, family="linear").run(top)[0]
                np_fit = E7.rollout(q.g7, top, HELD8)[0]
                ex = int((fused_fit != np_fit).sum())
                row.update(world_oracle_honest=wo, world_oracle_skip_lin=wc, brain_oracle_honest=bo,
                           brain_oracle_cheat=bc, fused_vs_numpy_elites_differing=ex)
                oracle_clean = (wo["elites_failing"] == 0 and wc["elites_failing"] >= 14
                                and bo["mismatched_rows"] == 0 and bc["elites_mismatching"] >= 14 and ex == 0)
                if a.brain_cheat == "powered":
                    # E-T3 cheats (B-R2-8 rule): ablate_top >= 14/16 (input-invariant elites never count as
                    # caught), shift_action floor 16/16, honest 0; skip-odd is recorded but not binding.
                    pc = brain_oracle_cheats(q.g7, top, HELD8)
                    row["brain_oracle_powered"] = pc
                    oracle_clean = (wo["elites_failing"] == 0 and wc["elites_failing"] >= 14 and ex == 0
                                    and bo["mismatched_rows"] == 0 and pc["honest"]["mismatched_rows"] == 0
                                    and pc["shift_action"]["elites_caught"] == pc["elites"]
                                    and pc["ablate_top"]["elites_caught"] >= 14)
                row["oracle_rule"] = a.brain_cheat
                row["oracle_clean"] = oracle_clean
            row["wall_s"] = round(time.perf_counter() - t0, 1)
            held.append(row["held64_per_seed"])
            print(json.dumps({k: v for k, v in row.items() if k != "top_hex"}), flush=True)
            rw.write(row)
    if a.no_ledger or not held:
        return
    med = float(np.median(held))
    iqr = float(np.percentile(held, 75) - np.percentile(held, 25))
    verdict = QL.check(QL.load(), f"w{gs}", pname, med, iqr, q.glen, len(held), bool(oracle_clean))
    cell = {"cell": {"representation": f"linear_int{q.bits}_nibble" + ("" if q.A == E7.A else f"_a{q.A}"), "world": f"w{gs}", "pressure": pname,
                     "substrate": "numba_fused", "channel": "none"},
            "mechanism": f"closed_loop_linear_int{q.bits}_nibble_codebook" + ("" if q.A == E7.A else f"_a{q.A}"),
            "fitness": {"held64_median": round(med, 4), "iqr": round(iqr, 4), "n_runs": len(held),
                        "held64_by_run_seed": held},
            "footprint": {"genome_bytes": q.glen, "params": q.nw + q.nb},
            "oracle": (("clean (world hash+charge, brain ref logits, fused==numpy; skip_lin + skip-odd fail)"
                        if a.brain_cheat == "skip_odd" else
                        "clean (world hash+charge, brain ref logits, fused==numpy; skip_lin fails; E-T3 ablate_top"
                        " >=14/16 + shift_action 16/16)")
                       if oracle_clean else "NOT clean (see rows run_seed 0)"),
            "baseline": False, "cohort": "B", "status": "record" if oracle_clean else "cheat",
            "clause_a": verdict, "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}}
    with RowWriter(QL.CELLS, EXP, commit_every_s=10**9) as w:
        w.write(cell)
    print(json.dumps({"median": med, "iqr": iqr, "bytes": q.glen, "runs": len(held), "verdict": verdict}), flush=True)


if __name__ == "__main__":
    main()
