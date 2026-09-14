"""E-T1: Domain A -> B transfer harness (contract clause B instrument, SWARM_R2 s3 E).

  python -m primordial.cohorts.e.transfer --recipient 4 [--donor 2] [--family linear]
         [--run-seeds 0-7] [--gens 200] [--batch 128] [--train 8] [--tag full]

A genome evolved in world A is grafted into world B WITHOUT MODIFICATION (the same packed
bytes), and B's MAP-Elites loop runs from it at a budget equal to from-scratch. A graft is
only defined between worlds whose genome layout is identical (same family shapes, same
codebook A x W); an incompatible pair is an `aborted` row, never a reshaped graft.

Gen 0 in B is `batch` genomes: the SAME batch - K fresh init fillers in every condition
(common random numbers), and K = 16 condition slots:
  scratch        K more fresh init genomes (E9's loop)
  graft          the donor's top-K from A                                  (status record)
  rand_graft     CHEAT: K fresh init genomes of the same shape (distribution-equal to scratch
                 by construction: it measures the instrument's false-alarm rate, nothing more)
  shuffle_graft  CHEAT: the donor top-K with each tensor's entries and the codebook's non-abstain
                 entries permuted independently (value marginals kept, structure gone)
  self_graft     CONTROL: a donor evolved in B itself on a disjoint run seed; a planted positive
                 that the instrument must see as acceleration
After gen 0 every condition draws mutations from the same run-seed RNG stream.

Why not tiling or best-so-far (smoke 2026-09-14, w2->w4, 1 run seed): a batch of K tiled genomes
lost to 128 distinct ones (rand_graft AUC 142 vs 151: a diversity loss, not a transfer signal),
and best-so-far train fitness hit its ceiling at gen 1 for the shuffle cheat and the self-graft.

Measures per (condition, run seed):
  held_auc   PRIMARY. mean over geometric checkpoints (gens 1..G) of the archive top-K's mean
             held-out fitness per seed (E6's 64 seeds); geometric spacing weights early gens
  train_auc  mean over all gens of the archive top-K's mean train fitness per seed
  gens_to    first gen whose top-K train mean >= the scratch median final value (G + 1 = never)
  zero_shot  the K slot genomes alone on the held-out seeds (inference, no search in B)
  held64     final top-K held-out mean per seed
Acceleration of X = paired difference X - scratch over run seeds, one-sided exact sign-flip
permutation p (2^n flips).

Integrity: sha256 of the donor bytes saved in A == the K slot bytes at B gen 0; the fused
rollout's fitness of the grafted genomes == lane E's numpy rollout (E7.rollout), exactly.
Oracles (first run seed, graft final top-K, E7 numpy code on HELD8): world honest 0 failing,
skip_lin failing; brain 0 mismatched clear rows, cheat mismatching.

Library code (primordial/brain, qd, soup) is imported read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import time

import numpy as np

from primordial.qd import e7_run as E7
from primordial.qd.archive import reduce_batch
from primordial.soup.b6.fused import GRID, FusedRollout

EXP = "E-T1-transfer-harness"
ROWS_DIR = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "E"
HELD64, HELD8 = E7.HELD64, E7.HELD8
TOP = 16
N_CHECK = 8
CONDITIONS = ("scratch", "graft", "rand_graft", "shuffle_graft", "self_graft")
STATUS = {"scratch": "record", "graft": "record", "rand_graft": "cheat", "shuffle_graft": "cheat",
          "self_graft": "control"}


# ------------------------------------------------------------------ archive

class NpArchive:
    """In-process MAP-Elites archive with LuaArchive's total order (higher fit, then the
    lexicographically smaller genome) and SEEDED sampling with replacement (LuaArchive's
    ZRANDMEMBER is unseeded, so a transfer run could not be replayed)."""

    def __init__(self, glen: int, n_cells: int = GRID * GRID):
        self.glen = glen
        self.fit = np.zeros(n_cells, np.int64)
        self.g = np.zeros((n_cells, glen), np.uint8)
        self.occ = np.zeros(n_cells, bool)

    def insert(self, cells, fits, genomes) -> int:
        c, f, g, _ = reduce_batch(np.asarray(cells), np.asarray(fits), np.asarray(genomes),
                                  np.zeros((len(cells), 2), np.uint32))
        wins = 0
        for ci, fi, gi in zip(c.astype(np.int64), f.astype(np.int64), g):
            if self.occ[ci]:
                of = self.fit[ci]
                if fi < of:
                    continue
                if fi == of:
                    d = np.nonzero(gi != self.g[ci])[0]
                    if len(d) == 0 or gi[d[0]] > self.g[ci, d[0]]:
                        continue
            self.occ[ci], self.fit[ci], self.g[ci] = True, fi, gi
            wins += 1
        return wins

    def sample(self, rng, n: int) -> np.ndarray:
        idx = np.nonzero(self.occ)[0]
        if len(idx) == 0:
            return np.empty((0, self.glen), np.uint8)
        return self.g[idx[rng.integers(0, len(idx), n)]].copy()

    def top_fit_mean(self, k: int = TOP) -> float:
        f = np.sort(self.fit[self.occ])
        return float(f[-k:].mean()) if len(f) else 0.0

    def top(self, k: int = TOP) -> np.ndarray:
        idx = np.nonzero(self.occ)[0]
        rank = np.unique(self.g[idx], axis=0, return_inverse=True)[1].reshape(-1)
        o = np.lexsort((rank, -self.fit[idx]))[:k]
        return self.g[idx[o]].copy()

    def as_dict(self) -> dict[int, tuple[int, bytes]]:
        return {int(c): (int(self.fit[c]), self.g[c].tobytes()) for c in np.nonzero(self.occ)[0]}

    def __len__(self) -> int:
        return int(self.occ.sum())


# ------------------------------------------------------------------ grafts

def layout(g7: E7.G7) -> tuple:
    return (g7.fam.name, tuple(g7.fam.shapes()), E7.A, g7.W, g7.pb, g7.cb, g7.glen)


def compatible(ga: E7.G7, gb: E7.G7) -> tuple[bool, str]:
    la, lb = layout(ga), layout(gb)
    if la == lb:
        return True, ""
    return False, f"layout differs: donor {la} vs recipient {lb}"


def shuffle_genomes(g7: E7.G7, raw: np.ndarray, rng) -> np.ndarray:
    """Permute, per genome, each parameter tensor's entries and the codebook's non-abstain
    entries independently. Values keep their multiset; the parameter <-> action binding is gone."""
    p, C = g7.unpack(raw)
    P = len(C)
    out_p = []
    for x in p:
        flat = x.reshape(P, -1).copy()
        for i in range(P):
            flat[i] = flat[i, rng.permutation(flat.shape[1])]
        out_p.append(flat.reshape(x.shape))
    C = C.copy()
    body = C[:, 1:].reshape(P, -1)
    for i in range(P):
        body[i] = body[i, rng.permutation(body.shape[1])]
    C[:, 1:] = body.reshape(P, E7.A - 1, g7.W)
    return g7.pack((tuple(out_p), C))


def sha(raw: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest()


def checkpoints(gens: int, n: int = N_CHECK) -> np.ndarray:
    """1-based generations at which the held-out score is taken (geometric, last = gens)."""
    return np.unique(np.rint(np.geomspace(1, gens, n)).astype(int))


# ------------------------------------------------------------------ search

def evolve(g7: E7.G7, family: str, seeds: np.ndarray, gens: int, batch: int, rng, gen0: np.ndarray | None = None,
           held: np.ndarray | None = None):
    """E9's loop on an NpArchive. gen0 (packed bytes [batch, glen]) replaces the init batch.
    -> (archive, top-K train mean per seed per gen, held-out top-K per checkpoint or None)."""
    arch = NpArchive(g7.glen)
    fr = FusedRollout(g7.spec, batch, seeds, family=family)
    ck = set(checkpoints(gens).tolist()) if held is not None else set()
    curve = np.zeros(gens)
    hcurve = []
    for t in range(gens):
        if t == 0:
            g = g7.unpack(g7.pack(g7.init(rng, batch)) if gen0 is None else gen0)
        else:
            g = g7.mutate(rng, g7.unpack(arch.sample(rng, batch)))
        fit, cells = fr.run(g)[:2]
        arch.insert(cells, fit, g7.pack(g))
        curve[t] = arch.top_fit_mean() / len(seeds)
        if t + 1 in ck:
            hcurve.append(score(g7, family, arch.top(), held))
    return arch, curve, (np.array(hcurve) if held is not None else None)


def score(g7: E7.G7, family: str, raw: np.ndarray, seeds: np.ndarray) -> float:
    fit = FusedRollout(g7.spec, len(raw), seeds, family=family).run(g7.unpack(raw))[0]
    return float(fit.mean() / len(seeds))


def gens_to(curve: np.ndarray, target: float) -> int:
    """First generation (1-based) whose value reaches target; len(curve) + 1 = never."""
    hit = np.nonzero(curve >= target)[0]
    return int(hit[0]) + 1 if len(hit) else len(curve) + 1


def signflip_p(d) -> float:
    """One-sided exact paired permutation p for mean(d) > 0."""
    d = np.asarray(d, float)
    obs = d.mean()
    flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
    return float(((flips * np.abs(d)).mean(1) >= obs - 1e-12).mean())


def parse_seeds(s: str) -> list[int]:
    if "-" in s:
        lo, hi = s.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in s.split(",")]


def default_donor(recipient: int, family: str, search: range = range(1, 65)) -> int | None:
    gb = E7.G7(recipient, family)
    for w in search:
        if w != recipient and compatible(E7.G7(w, family), gb)[0]:
            return w
    return None


# ------------------------------------------------------------------ one recipient world

def run_pair(donor: int, recipient: int, family: str, run_seeds, gens: int, batch: int, n_train: int,
             tag: str, writer, oracles: bool = True, log=print) -> dict:
    ga, gb = E7.G7(donor, family), E7.G7(recipient, family)
    train = np.arange(9100, 9100 + n_train, dtype=np.int64)
    base = {"tag": tag, "family": family, "donor_world": donor, "recipient_world": recipient,
            "gens": gens, "batch": batch, "train_seeds": n_train, "genome_bytes": gb.glen, "top_k": TOP,
            "checkpoints": checkpoints(gens).tolist()}
    ok, why = compatible(ga, gb)
    if not ok or batch <= TOP:
        writer.write(dict(base, status="aborted", reason=why or f"batch {batch} <= top_k {TOP}"))
        return {"aborted": why or "batch too small"}
    per = {c: [] for c in CONDITIONS}
    curves = {c: [] for c in CONDITIONS}
    for rs in run_seeds:
        t0 = time.perf_counter()
        # donors: A on its own train seeds; self-donor: B on a disjoint run-seed stream
        dA = evolve(ga, family, train, gens, batch, np.random.Generator(np.random.PCG64([1701, rs, donor])))[0].top()
        dB = evolve(gb, family, train, gens, batch,
                    np.random.Generator(np.random.PCG64([1702, rs + 1000, recipient])))[0].top()
        srng = np.random.Generator(np.random.PCG64([1703, rs, recipient]))
        filler = gb.pack(gb.init(np.random.Generator(np.random.PCG64([1705, rs, recipient])), batch))
        slots = {"scratch": filler[:TOP].copy(), "graft": dA,
                 "rand_graft": gb.pack(gb.init(srng, TOP)),
                 "shuffle_graft": shuffle_genomes(gb, dA, srng), "self_graft": dB}
        donor_sha = sha(dA)
        for cond in CONDITIONS:
            gen0 = filler.copy()
            gen0[:TOP] = slots[cond]
            rng = np.random.Generator(np.random.PCG64([1704, rs, recipient]))   # common stream per run seed
            arch, curve, hcurve = evolve(gb, family, train, gens, batch, rng, gen0, held=HELD64)
            top = arch.top()
            row = dict(base, status=STATUS[cond], condition=cond, run_seed=rs, cells=len(arch),
                       held_auc=float(hcurve.mean()), held_curve=[round(float(x), 3) for x in hcurve],
                       train_auc=float(curve.mean()), train_final=float(curve[-1]),
                       zero_shot_held64=score(gb, family, gen0[:TOP], HELD64),
                       held64=float(hcurve[-1]), slot_sha256=sha(gen0[:TOP]))
            if cond == "graft":
                row["donor_sha256"] = donor_sha
                row["graft_bytes_unmodified"] = row["slot_sha256"] == donor_sha
                np_fit = E7.rollout(gb, gb.unpack(dA), train)[0]
                fu_fit = FusedRollout(gb.spec, TOP, train, family=family).run(gb.unpack(dA))[0]
                row["graft_fused_eq_numpy"] = bool(np.array_equal(np_fit, fu_fit))
                if oracles and rs == run_seeds[0]:
                    tg = gb.unpack(top)
                    row["world_oracle_honest"] = E7.world_oracle(gb, tg, HELD8)
                    row["world_oracle_skip_lin"] = E7.world_oracle(gb, tg, HELD8, "skip_lin")
                    row["brain_oracle_honest"] = E7.brain_oracle(gb, tg, HELD8)
                    row["brain_oracle_cheat"] = E7.brain_oracle(gb, tg, HELD8, cheat=True)
            per[cond].append(row)
            curves[cond].append(curve)
            writer.write(row)
        log(f"w{donor}->w{recipient} rs={rs} " + " ".join(
            f"{c}:hauc={per[c][-1]['held_auc']:.1f}/z={per[c][-1]['zero_shot_held64']:.1f}" for c in CONDITIONS)
            + f" ({time.perf_counter() - t0:.1f}s)")
    target = float(np.median([r["train_final"] for r in per["scratch"]]))
    summ = dict(base, status="record", condition="summary", run_seeds=list(run_seeds),
                scratch_train_final_median=target)
    col = lambda c, k: np.array([r[k] for r in per[c]])
    for c in CONDITIONS:
        summ[c] = {"held_auc_median": float(np.median(col(c, "held_auc"))),
                   "train_auc_median": float(np.median(col(c, "train_auc"))),
                   "held64_median": float(np.median(col(c, "held64"))),
                   "zero_shot_median": float(np.median(col(c, "zero_shot_held64"))),
                   "gens_to": [gens_to(cv, target) for cv in curves[c]]}
        if c != "scratch":
            for k in ("held_auc", "train_auc", "zero_shot_held64", "held64"):
                d = col(c, k) - col("scratch", k)
                summ[c][f"{k}_diff_mean"] = float(d.mean())
                summ[c][f"{k}_p"] = signflip_p(d)
    writer.write(summ)
    return summ


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipient", type=int, required=True)
    ap.add_argument("--donor", type=int, default=0, help="0 = first shape-compatible world in 1..64")
    ap.add_argument("--family", default="linear")
    ap.add_argument("--run-seeds", default="0-7"); ap.add_argument("--gens", type=int, default=200)
    ap.add_argument("--batch", type=int, default=128); ap.add_argument("--train", type=int, default=8)
    ap.add_argument("--tag", default="full"); ap.add_argument("--exp", default=EXP)
    ap.add_argument("--skip-oracles", action="store_true")
    a = ap.parse_args(argv)
    from primordial.fabric.rows import RowWriter
    donor = a.donor or default_donor(a.recipient, a.family)
    with RowWriter(ROWS_DIR / f"{a.exp}.jsonl", a.exp) as w:
        if donor is None:
            w.write({"status": "aborted", "tag": a.tag, "recipient_world": a.recipient, "family": a.family,
                     "reason": "no shape-compatible donor world in 1..64"})
            return 1
        s = run_pair(donor, a.recipient, a.family, parse_seeds(a.run_seeds), a.gens, a.batch, a.train, a.tag, w,
                     oracles=not a.skip_oracles)
    print(json.dumps(s, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
