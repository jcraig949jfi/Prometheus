"""C-R7-01 (DISTANT_QD): drawn cell bitset / signal_world_d1 / held_out_seeds / torch_gpu / none
(draw seed 12023959209616145102, bus 1789509643458-0, round 7).

Cohort C builds the drawn cell; it does not choose it. No definition of this cell existed; the definitions below are
fixed before any run. signal_world_d1 is not a screened world: no floor suite, no clause A claim. A ruling
1789509847892-0: the GPU arbiter is infrastructure (E runs nv.gpuq from nestor-r7-e); this job runs as ONE gpuq job.

  world     lane D's D1 signal world (primordial.lingua.signal): T = 64 ticks; slot 0 sees R in [0, 256) drawn per tick
            (signal.r_stream(episode seed)); slot 1 hears the channel and acts in [0, 8); right iff act == R >> 5.
  channel   none (C-R5-AP-01's definition): slot 0's symbol reaches slot 1 unmetered and uncorrupted (no ledger, no
            cost). Fitness = right actions summed over the selection episodes. The task is a pure function of R, so
            fitness is exact from the genome's action table weighted by the episodes' register histogram.
  brain     bitset: the genome IS a 792-bit string (99 bytes, bit order little within each byte): encoder enc[R] = 3
            bits x 256 entries, decoder dec[s] = 3 bits x 8 entries; act = dec[enc[R]]. A lookup table in bits; no
            floats. Init: bytes uniform. Mutation E1's rule: every bit flips with p = 1 / 792.
  pressure  held_out_seeds: selection sees TRAIN = episode seeds 0..7 (8 episodes, 512 registers; the TRAIN8 size of
            C-R7-AP-01 / E6); the score is HELD = episodes 10,000,000..10,000,255 (256 episodes, 16,384 registers,
            C-R5-01's HELD). A table cannot learn register values TRAIN never shows (about 13.5% of the 256 values).
  substrate torch_gpu: every selection fitness is computed on CUDA (bit unpack, gathers, compare, histogram dot product,
            int64). numpy is the reference only. The search (streams, archive) is on CPU. Runs as a gpuq child in
            nv-venv-u; no Redis in the child, so the MAP-Elites archive is in-process (cell -> (fitness, bytes);
            replace iff fitness higher, or equal with lexicographically smaller bytes; parents uniform over filled cells
            in sorted cell order by the sampler stream). Descriptor (C-R5-AP-01): (distinct symbols emitted - 1) * 8 +
            (distinct actions used - 1), 64 cells. Batch 128.
  arms      control  pressure removed: selection IN-SAMPLE on HELD, channel on
            null     PLANTED NULL = the cell with its mechanism removed: slot 1 hears silence (symbol 0) every tick
            cell     selection on TRAIN, channel on
  order     all 32 control runs; all 32 null runs; NULL_CHECK row; then the 32 cell runs only if the null FAILED (else
            summary PREDICATE_PASSES_PLANTED_NULL and stop).
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 7301]); sampler PCG64([family + 1, run_seed, arm, 7301]).
  GENS      rule fixed before the dev check: the largest of {100, 200, 400, 800} whose projected job wall (96 runs x
            measured wall per run per arm + oracles, x 1.25) <= 480 s (80% of the 600 s GPU lease cap); if 100 does not
            fit, INFEASIBLE in one lease (aborted row + PRODUCTION_CANDIDATE with the measured cost).
  reader    top1_train: the archive elite with the highest selection fitness (ties: lexicographically smaller bytes);
            held = its right share on HELD (rights / 16,384), under its arm's channel.
  PREDICATE for an arm X in {null, cell} (the same code scores both):
            P1  median held (X) >= median held (control) - 0.5 * IQR (control)
            P2  median held (X) > FLOOR = the best input-invariant yield on HELD (max over a of the HELD share of
                R >> 5 == a; exact from the HELD histogram)
            P3  the scrambled channel (a per-episode permutation of the 8 symbols, silence included; D1 scramble_probe's
                form, PCG64([7301, family, run_seed, arm, 99])) lowers held in >= 17 of the 32 runs of X
            PASS iff P1 and P2 and P3 and oracles clean. The null must FAIL before the cell runs.
  oracles   family 4200 run seed 0 of each arm, genomes = top-16 + planted HAND (D1's hand_code(8): enc = bucket,
            dec = identity) + planted DEC1 (HAND with dec[0] = 1):
            gpu      GPU fitness == numpy reference on EVERY offer of the run (exact); EVERY run: top-16 archive fitness
                     == numpy recount from the STORED bytes (exact)
            cheat    GPU with the DECODER's bit order reversed mismatches the reference on >= 90% of ELIGIBLE genomes
                     (the numpy reference itself changes under the reversal), >= 1 eligible. Structural in every arm:
                     HAND (dec 1 <-> 4, 3 <-> 6) with the channel on, DEC1 (dec[0] 1 -> 4) with the silent null.
                     Disclosed: the first draft reversed the ENCODER; the no-rows dev check showed 0 eligible genomes
                     with the channel off (the null never reads enc), so it was changed before any predicate or row.
            world    control and cell arms: D1's closed-loop run_world (NpChannel alpha 0, start 0, y_int 1) over the
                     TRAIN episodes: summed final charge == histogram fitness for every oracle genome (exact). The null
                     arm is EXEMPT by this rule (run_world has no silent channel); its gpu and cheat oracles still bind.
  report    (not judged) hand-code and constant-policy yields on TRAIN and HELD; train yield; unseen-register share of
            TRAIN; symbols / actions used by the top1; wall per arm.
  not claimed  clause A (no floor suite); any mechanism.

  gpuq:  fn = primordial.cohorts.c.r7_01_bitset_d1_heldout_torch_gpu:job, venv u
  dev:   <nv-venv-u python> -m primordial.cohorts.c.r7_01_bitset_d1_heldout_torch_gpu dev   (no rows; take the lease)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

import numpy as np

from primordial.lingua import signal as S

EXP = "C-R7-01-bitset-d1-heldout-torch-gpu"
PREDICATE_ID = "C-R7-01"
ROWS = f"primordial/ledger/rows/C/{EXP}.jsonl"
CELL = {"representation": "bitset", "world": "signal_world_d1", "pressure": "held_out_seeds", "substrate": "torch_gpu",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="in_sample_heldout_control")
CELL_NULL = dict(CELL, channel="none_silent_planted_null")
T = 64
NR, NA, SH = S.N_R, S.N_ACT, S.SHIFT
SB = 3
NBITS = NR * SB + NA * SB
GLEN = (NBITS + 7) // 8
TRAIN = np.arange(8)
HELD = 10_000_000 + np.arange(256)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
BATCH, TOP = 128, 16
STREAM_TAG = 7301
P3_MIN = 17
GENS_CHOICES = (100, 200, 400, 800)
WALL_CAP = 480.0
# No-rows dev check (nv-venv-u, under the O5 lease, 20 gens per arm on family 4200 run 0): wall/gen control 0.00358,
# null 0.00307, cell 0.00318 s -> projected job wall 100: 39.5, 200: 78.8, 400: 157.4, 800: 314.7 (cap 480) -> GENS 800.
# floor_held 0.12835693359375; TRAIN leaves 32 of 256 register values unseen; GPU == reference on random + HAND.
GENS = 800
ARM_INDEX = {"cell": 0, "control": 1, "null": 2}
W3 = np.array([1, 2, 4], np.int64)
TRUTH = np.arange(NR) >> SH


def hist(seeds) -> np.ndarray:
    return np.bincount(S.r_stream(np.asarray(seeds), T).ravel(), minlength=NR).astype(np.int64)


def floor_of(h) -> float:
    return float(max(h[TRUTH == a].sum() for a in range(NA)) / h.sum())


# ------------------------------------------------------------------ genome (numpy reference)

def unpack(B, reverse_dec=False):
    B = np.asarray(B, np.uint8)
    bits = np.unpackbits(B, axis=1, bitorder="little")[:, :NBITS].astype(np.int64)
    P = len(B)
    enc = bits[:, :NR * SB].reshape(P, NR, SB) @ W3
    dec = bits[:, NR * SB:].reshape(P, NA, SB) @ (W3[::-1] if reverse_dec else W3)
    return enc, dec


def pack(enc, dec):
    P = len(enc)
    eb = ((enc[:, :, None] >> np.arange(SB)) & 1).reshape(P, NR * SB)
    db = ((dec[:, :, None] >> np.arange(SB)) & 1).reshape(P, NA * SB)
    return np.packbits(np.concatenate([eb, db], 1).astype(np.uint8), axis=1, bitorder="little")


def hand_genome(dec0=None):
    _, enc, dec = S.hand_code(8)
    dec = np.asarray(dec[:NA], np.int64).copy()
    if dec0 is not None:
        dec[0] = dec0
    return pack(np.asarray(enc, np.int64)[None], dec[None])[0]


def planted():
    return np.stack([hand_genome(), hand_genome(dec0=1)])


def init(rng, P):
    return rng.integers(0, 256, (P, GLEN), dtype=np.uint8)


def mutate(rng, B):
    bits = np.unpackbits(B, axis=1, bitorder="little")
    flip = (rng.random(bits.shape) < 1.0 / NBITS).astype(np.uint8)
    return np.packbits(bits ^ flip, axis=1, bitorder="little")


def ref_fit(B, h, channel="on", reverse_dec=False):
    enc, dec = unpack(B, reverse_dec)
    heard = enc if channel == "on" else np.zeros_like(enc)
    act = np.take_along_axis(dec, heard, 1)
    return ((act == TRUTH[None, :]) * h[None, :]).sum(1).astype(np.int64)


def descriptor(B, channel="on"):
    enc, dec = unpack(B)
    heard = enc if channel == "on" else np.zeros_like(enc)
    act = np.take_along_axis(dec, heard, 1)
    syms = np.array([len(np.unique(e)) for e in enc])
    acts = np.array([len(np.unique(a)) for a in act])
    return ((syms - 1) * 8 + (acts - 1)).astype(np.int64)


# ------------------------------------------------------------------ GPU evaluator

class GPUEval:
    def __init__(self):
        import torch
        self.torch = torch
        self.dev = torch.device("cuda")
        self.shifts = torch.arange(8, device=self.dev, dtype=torch.int64)
        self.w = torch.tensor(W3, device=self.dev)
        self.wr = torch.tensor(W3[::-1].copy(), device=self.dev)
        self.truth = torch.tensor(TRUTH, device=self.dev)
        self._h = {}

    def fit(self, B, h, channel="on", reverse_dec=False):
        torch = self.torch
        key = h.tobytes()
        if key not in self._h:
            self._h[key] = torch.tensor(h, device=self.dev)
        ht = self._h[key]
        Bt = torch.from_numpy(np.ascontiguousarray(B)).to(self.dev).to(torch.int64)
        P = Bt.shape[0]
        bits = ((Bt[:, :, None] >> self.shifts) & 1).reshape(P, GLEN * 8)[:, :NBITS]
        enc = (bits[:, :NR * SB].reshape(P, NR, SB) * self.w).sum(-1)
        dec = (bits[:, NR * SB:].reshape(P, NA, SB) * (self.wr if reverse_dec else self.w)).sum(-1)
        heard = enc if channel == "on" else torch.zeros_like(enc)
        act = torch.gather(dec, 1, heard)
        out = ((act == self.truth).to(torch.int64) * ht).sum(1)
        return out.cpu().numpy().astype(np.int64)


# ------------------------------------------------------------------ in-process archive

class Archive:
    def __init__(self):
        self.cells: dict[int, tuple[int, bytes]] = {}

    def insert(self, cells, fits, B):
        for c, f, g in zip(cells.tolist(), fits.tolist(), B):
            gb = g.tobytes()
            cur = self.cells.get(c)
            if cur is None or f > cur[0] or (f == cur[0] and gb < cur[1]):
                self.cells[c] = (int(f), gb)

    def sample(self, srng, n):
        keys = sorted(self.cells)
        idx = srng.integers(0, len(keys), n)
        return np.frombuffer(b"".join(self.cells[keys[i]][1] for i in idx), np.uint8).reshape(n, GLEN)

    def top(self, k):
        order = sorted(self.cells.values(), key=lambda v: (-v[0], v[1]))[:k]
        return np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, GLEN), \
            np.array([v[0] for v in order], np.int64)


# ------------------------------------------------------------------ probes and oracles

def scrambled_yield(g, seeds, channel, seed):
    enc, dec = unpack(g[None])
    enc, dec = enc[0], dec[0]
    R = S.r_stream(np.asarray(seeds), T)                                           # [T, E]
    E = R.shape[1]
    rng = np.random.Generator(np.random.PCG64(seed))
    perm = np.argsort(rng.random((E, NA)), axis=1)
    sym = enc[R] if channel == "on" else np.zeros_like(R)
    heard = perm[np.arange(E)[None, :], sym]
    act = dec[heard]
    return float((act == (R >> SH)).sum() / R.size)


def world_oracle(G, seeds, h) -> dict:
    bad = 0
    for g in G:
        enc, dec = unpack(g[None])
        ch = S.NpChannel(len(seeds), alpha_int=0, start=0)
        res = S.run_world(3, enc[0], dec[0], np.asarray(seeds), T, ch, y_int=1)
        bad += int(int(res["log"][T, :, 4].sum()) != int(ref_fit(g[None], h)[0]))
    return {"genomes": int(len(G)), "mismatched": bad}


def cheat_oracle(ev, G, h, channel) -> dict:
    ref = ref_fit(G, h, channel)
    ref_c = ref_fit(G, h, channel, reverse_dec=True)
    gpu_c = ev.fit(G, h, channel, reverse_dec=True)
    el = ref_c != ref
    caught = int(((gpu_c != ref) & el).sum())
    return {"eligible": int(el.sum()), "caught": caught,
            "share": round(caught / int(el.sum()), 4) if el.any() else 0.0}


# ------------------------------------------------------------------ one run

def run(ev, family, rs, arm, gens, htrain, hheld, track=False):
    ai = ARM_INDEX[arm]
    sel_h = hheld if arm == "control" else htrain
    channel = "off" if arm == "null" else "on"
    rng = np.random.Generator(np.random.PCG64([family, rs, ai, STREAM_TAG]))
    srng = np.random.Generator(np.random.PCG64([family + 1, rs, ai, STREAM_TAG]))
    arch = Archive()
    t0 = time.perf_counter()
    offers = offer_bad = 0
    for _ in range(gens):
        B = init(rng, BATCH) if not arch.cells else mutate(rng, arch.sample(srng, BATCH))
        f = ev.fit(B, sel_h, channel)
        if track:
            offers += len(B)
            offer_bad += int((ref_fit(B, sel_h, channel) != f).sum())
        arch.insert(descriptor(B, channel), f, B)
    wall = time.perf_counter() - t0
    top, tf = arch.top(TOP)
    recount_bad = int((ref_fit(top, sel_h, channel) != tf).sum())
    total_held = float(hheld.sum())
    held = float(ref_fit(top[:1], hheld, channel)[0] / total_held)
    scr = scrambled_yield(top[0], HELD, channel, [STREAM_TAG, family, rs, ai, 99])
    enc, dec = unpack(top[:1])
    act = dec[0][enc[0]] if channel == "on" else np.full(NR, dec[0][0])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "search_wall_s": round(wall, 3),
            "archive_cells": len(arch.cells), "train_fit_top1": int(tf[0]),
            "train_yield_top1": float(ref_fit(top[:1], htrain, channel)[0] / htrain.sum()),
            "held_yield_top1": held, "held_scrambled_top1": scr, "scramble_lowers": bool(scr < held),
            "symbols_used_top1": int(len(np.unique(enc[0]))), "actions_used_top1": int(len(np.unique(act))),
            "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(), "recount_mismatched_top16": recount_bad,
            "offers_audited": offers, "offers_mismatched": offer_bad}
    return info, top


def score(held, lowers, control, floor) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    n_low = int(sum(lowers))
    return {"median": float(q[1]), "iqr": float(q[2] - q[0]), "control_median": float(qc[1]),
            "control_iqr": float(qc[2] - qc[0]), "bar": bar, "floor": floor, "P1_parity": bool(q[1] >= bar),
            "P2_above_floor": bool(q[1] > floor), "P3_scramble_lowers_runs": n_low, "P3_uses_channel": n_low >= P3_MIN,
            "n": len(held)}


def job(emit, checkpoint_path=None, gens: int = GENS, exp_id: str = EXP):
    ev = GPUEval()
    htrain, hheld = hist(TRAIN), hist(HELD)
    floor = floor_of(hheld)
    hand = hand_genome()
    plants = planted()
    emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
          "genome_bytes": GLEN, "floor_held": floor, "p3_min_runs": P3_MIN,
          "train_unseen_registers": int((htrain == 0).sum()),
          "hand_yield": {"train": float(ref_fit(hand[None], htrain)[0] / htrain.sum()),
                         "held": float(ref_fit(hand[None], hheld)[0] / hheld.sum())},
          "order": "control, null, NULL_CHECK, cell", "status": "control", "ts": round(time.time(), 3)})
    held = {"cell": [], "control": [], "null": []}
    lowers = {"cell": [], "null": []}
    clean = {"cell": True, "control": True, "null": True}
    runs = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    null_check = None
    for arm in ("control", "null", "null_check", "cell"):
        if arm == "null_check":
            sc = score(held["null"], lowers["null"], held["control"], floor)
            passes = bool(sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"]
                          and clean["null"] and clean["control"])
            null_check = {"null_predicate": "PASS" if passes else "FAIL", **sc,
                          "oracle_clean_null": clean["null"], "oracle_clean_control": clean["control"]}
            emit({"kind": "null_check", "exp_id": exp_id, **null_check,
                  "rule": "the planted null must FAIL the predicate before any cell-arm row", "status": "control",
                  "ts": round(time.time(), 3)})
            if passes:
                emit({"kind": "summary", "exp_id": exp_id, "cell": CELL, "primary": "PREDICATE_PASSES_PLANTED_NULL",
                      "null_check": null_check, "status": "aborted",
                      "reason": "predicate rewrite required before any cell-arm row", "ts": round(time.time(), 3)})
                return
            continue
        cell = {"cell": CELL, "control": CELL_CTRL, "null": CELL_NULL}[arm]
        channel = "off" if arm == "null" else "on"
        sel_h = hheld if arm == "control" else htrain
        for fam, rs in runs:
            first = fam == FAMILIES[0] and rs == 0
            t0 = time.perf_counter()
            info, top = run(ev, fam, rs, arm, gens, htrain, hheld, track=first)
            ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
            row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
                   "genome_bytes": GLEN, "reader": "top1_train", **info,
                   "status": "record" if arm == "cell" else "control"}
            if first:
                G = np.concatenate([top, plants])
                o = {"cheat_reverse_dec": cheat_oracle(ev, G, sel_h, channel)}
                o["ok"] = bool(ok and o["cheat_reverse_dec"]["eligible"] > 0 and o["cheat_reverse_dec"]["share"] >= 0.9)
                if arm != "null":
                    o["world"] = world_oracle(G, TRAIN, htrain)
                    o["ok"] = o["ok"] and o["world"]["mismatched"] == 0
                else:
                    o["world"] = "EXEMPT by rule (run_world has no silent channel)"
                row["oracles"] = o
                ok = o["ok"]
            clean[arm] = bool(clean[arm] and ok)
            row["wall_s"] = round(time.perf_counter() - t0, 3)
            row["ts"] = round(time.time(), 3)
            held[arm].append(info["held_yield_top1"])
            if arm != "control":
                lowers[arm].append(info["scramble_lowers"])
            emit(row)
    sc = score(held["cell"], lowers["cell"], held["control"], floor)
    ok_all = clean["cell"] and clean["control"]
    full = all(len(held[a]) == len(runs) for a in ("cell", "control"))
    primary = "INDETERMINATE" if not (ok_all and full) else \
        ("PASS" if sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"] else "FAIL")
    emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL, "runs_total": len(held["cell"]),
          "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
          "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES}, "gens": gens, **sc, "null_check": null_check,
          "oracle_clean": ok_all, "primary": primary, "clause_a": "none: signal_world_d1 has no floor suite",
          "status": "record" if ok_all else "cheat", "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 20) -> None:
    """No rows: oracle eligibility (random + HAND), GPU == reference, wall per run per arm at `gens`, GENS by the rule."""
    ev = GPUEval()
    htrain, hheld = hist(TRAIN), hist(HELD)
    rng = np.random.Generator(np.random.PCG64(77))
    G = np.concatenate([init(rng, TOP), planted()])
    out = {"floor_held": floor_of(hheld), "train_unseen_registers": int((htrain == 0).sum()),
           "gpu_eq_ref_random": bool(np.array_equal(ev.fit(G, htrain), ref_fit(G, htrain))),
           "cheat_on": cheat_oracle(ev, G, htrain, "on"), "cheat_off": cheat_oracle(ev, G, htrain, "off"),
           "world": world_oracle(G, TRAIN, htrain)}
    ev.fit(init(rng, BATCH), htrain)
    per = {}
    for arm in ("control", "null", "cell"):
        t = time.perf_counter()
        info, _ = run(ev, 4200, 0, arm, gens, htrain, hheld, track=True)
        per[arm] = {"wall_s_per_gen": round((time.perf_counter() - t) / gens, 5), "offers_mismatched":
                    info["offers_mismatched"], "recount_mismatched": info["recount_mismatched_top16"]}
    out["per_arm"] = per
    t = time.perf_counter()
    cheat_oracle(ev, G, htrain, "on")
    world_oracle(G, TRAIN, htrain)
    oracle_wall = (time.perf_counter() - t) * 3
    unit = sum(per[a]["wall_s_per_gen"] for a in per) * 32
    proj = {str(Gn): round((unit * Gn + oracle_wall) * 1.25, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if (unit * Gn + oracle_wall) * 1.25 <= WALL_CAP]
    out["projected_job_wall_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 20) if sys.argv[1] == "dev" else None
