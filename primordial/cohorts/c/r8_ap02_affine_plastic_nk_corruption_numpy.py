"""C-R8-AP-02 (ANTI_PRIOR, cell assigned by code): affine_plastic / nk_stub / corruption / numpy / none
(anti_prior.assign exp_id C-R8-AP-02, round 8, from the G2 binding-eligible candidate list, seed 20260921).

The experimenter received only the cell; the prior, arm, rank and quantile are unread (pm:prior:* never read). No
definition of this cell existed; the definitions below are fixed before any run. nk_stub is not a screened graphworld
world: landscape rows only, no clause A claim.

G2 BASIS, disclosed: no G2-v1 rule applies to this cell (the corruption rule is graphworld-only), so it entered the pool
because no rule proved a defect. As in C-R8-AP-01, the job re-runs anti_prior.binding_precheck(cell, evidence=...) with
MEASURED evidence in committed rows before any run and aborts INELIGIBLE if it fails.

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE (C-R2-09 / C-R6-AP-01): selection on 8 TRAIN landscapes
            (9100..9107); score on 64 HELD landscapes (30000..30063); value = mean NK fitness per landscape. The locus j
            contribution row T[j, 0..31] is indexed by idx = sum_q bit[j + q] 2^q, so idx bit 0 is locus j's own bit.
  observation  the brain reads the landscape's own table (target-blind decoder), one row per locus, as 5 uint16
            features of the OBSERVED row O_j: f0 = (sum of O_j[idx odd] - sum of O_j[idx even]) // 32 + 32768 (the own-bit
            marginal), f1 = max O_j, f2 = O_j[1], f3 = O_j[0], f4 = sum O_j // 32.
  brain     affine_plastic, C-R7-AP-01's genome and rule. Genome 16 bytes [s, k, a_lo, a_hi, c_lo, c_hi, 0, 0] + C[8].
              s = byte % 5 (one feature), k = byte % 5 (hex digits read, most significant first)
              xe  = f_s masked to its top k digits (k = 0: 0)
              idx = ((a * xe + c + 8192 * shift) mod 65536) >> 13;  bit_j = C[idx] & 1
            Loci are decided in the order j = 63..0. plastic: over each window of 8 loci, support = share of loci whose
            chosen bit is the side the OBSERVED marginal favours (bit 1 iff sum odd >= sum even; bit 0 iff <=);
            support < SURPRISE_SUPPORT (0.5, brain.affine_plastic) is a surprise and refits the constant:
            shift = (shift + 1) & 7. The greedy own-bit code (s 0, k 4, a 1, c 0, C = 0,0,0,0,1,1,1,1 = planted HAND) is
            expressible; no target is held by the brain.
            Init: bytes uniform, bytes 6-7 = 0, C uniform in [0, 16). Mutation (C-R7-AP-01's field rule): each of s, k,
            a, c with p 0.2 (s, k: +-1 mod 5; a, c: half uniform 16-bit, half +- 2^j, j uniform in 0..15); each C entry
            with p 1/8 replaced uniform in [0, 16).
  pressure  corruption on the observation, receiver side (C-R5-01's rule on the thing this brain reads): each observed
            table entry (landscape, locus, idx) is XORed with v with p = 1/RATE (RATE 16); flip = PCG64([seed, 2^40])
            integers(0, RATE) == 0 and v = PCG64([seed, 2^41]) integers(0, 65536), both [64, 32], a function of the
            landscape seed only (common across genomes). The NK fitness always uses the TRUE table. It acts during
            SELECTION. Every arm is SCORED on HELD through its own observation mechanism WITHOUT the pressure (the clean
            table for control and cell; silence for the null): a common reference distribution for cell vs control.
  substrate numpy: rollout (features, masks, plastic loop over loci) and NK fitness are vectorised numpy int64 over
            [genomes x landscapes]; the MAP-Elites archive is in-process.
  search    MAP-Elites (C-R7-01's archive rules), batch 128. Descriptor (C-R6-AP-01): popcount halves of the bits on
            TRAIN landscape 0 through the arm's selection observation, 33 x 33 cells.
  arms      control  pressure removed: selection on TRAIN through the clean table
            null     PLANTED NULL = the cell with its mechanism removed: the brain observes nothing (every feature 0)
            cell     selection on TRAIN through the RATE 16 corrupted table
  order     all 32 control runs; all 32 null runs; NULL_CHECK row; then the 32 cell runs only if the null FAILED.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 8201]); sampler PCG64([family + 1, run_seed, arm, 8201]).
  GENS      rule fixed before the dev check: the largest of {100, 200, 400, 800} whose projected job CPU (96 runs x
            measured CPU per generation per arm + oracles, x 1.25) <= 7200 CPU-s. Checkpointable.
  reader    top1_train: the archive elite with the highest selection fitness (ties: lexicographically smaller bytes);
            held = its mean NK fitness per HELD landscape through the arm's scoring observation.
  PREDICATE for an arm X in {null, cell}:
            P1  median held (X) >= median held (control) - 0.5 * IQR (control)
            P2  median held (X) > FLOOR = max(mean HELD NK of all-zero bits, of all-one bits): exactly the best a
                brain that observes nothing can emit (with every feature 0 the observed marginal ties, support is 1,
                the shift never moves, so every locus gets the same bit)
            P3  a scrambled observation (locus j reads row pi(j), a per-landscape permutation of the 64 rows,
                PCG64([8201, family, run_seed, arm, 99])) lowers held in >= 17 of the 32 runs of X
            PASS iff P1 and P2 and P3 and oracles clean. The null must FAIL before the cell runs.
  VACUITY   (fixed before any row) IQR(control) == 0 and IQR(cell) == 0 and median(cell) == median(control) ->
            primary VACUOUS (never PASS or FAIL).
  BINDING   before any run, in committed rows: evidence = {intervention_magnitude: # of 256 random genomes whose TRAIN
            fitness through the corrupted table differs from the clean one, oracle_eligible: min eligible count over
            the two cheat oracles on random + planted genomes}; binding_precheck(CELL, evidence) must be ok, else
            summary INELIGIBLE (status aborted) and no run.
  oracles   family 4200 run seed 0 of each arm, genomes = top-16 + planted HAND + planted INV (HAND with C reversed):
            scalar   a plain-Python-int reference of the closed loop (features, mask, idx, plastic shift, bits) with
                     NKWorld(seed).evaluate on the packed bits == the vectorised fitness for every oracle genome (exact)
            world    vectorised NK from bits == NKWorld.evaluate on EVERY offer of that run (exact); EVERY run: top-16
                     archive fitness == vectorised recount from the STORED bytes (exact)
            cheat_plastic  the vectorised rollout with the shift frozen mismatches the scalar reference on >= 90% of
                     ELIGIBLE genomes (the scalar reference itself changes), >= 1 eligible; control and cell arms.
                     The null is EXEMPT by rule: with every feature 0 the shift never moves, so no genome is eligible
                     (reported, not binding; the C-R6 constant-input lesson). Its scalar oracle still binds.
            cheat_noise  cell arm only: the vectorised rollout fed the clean table mismatches the scalar corrupted
                     reference on >= 90% of ELIGIBLE genomes, >= 1 eligible
  report    (not judged) held through the RATE 16 table for control and cell; HAND held; train mean; refits of the top1.
  not claimed  clause A; any mechanism; anything about corruption at other rates.

  worker:  job = primordial.cohorts.c.r8_ap02_affine_plastic_nk_corruption_numpy:job
  dev:     python -m primordial.cohorts.c.r8_ap02_affine_plastic_nk_corruption_numpy dev [gens]   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

import numpy as np

from primordial.brain.affine_plastic import SURPRISE_SUPPORT
from primordial.qd.stubworld import GRID, K, N_BITS, NKWorld

EXP = "C-R8-AP-02-affine-plastic-nk-corruption-numpy"
PREDICATE_ID = "C-R8-AP-02"
ROWS = f"primordial/ledger/rows/C/{EXP}.jsonl"
CELL = {"channel": "none", "pressure": "corruption", "representation": "affine_plastic", "substrate": "numpy",
        "world": "nk_stub"}
CELL_CTRL = dict(CELL, pressure="corruption_rate0_control")
CELL_NULL = dict(CELL, channel="none_silent_observation_planted_null")
N, NP = N_BITS, 1 << (K + 1)
RATE = 16
WINDOW = 8
GLEN = 16
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
BATCH, TOP = 128, 16
STREAM_TAG = 8201
P3_MIN = 17
GENS_CHOICES = (100, 200, 400, 800)
CPU_CAP = 7200.0
GENS = 800      # no-rows dev check (10 gens per arm, family 4200 run 0, offer audit on): CPU/gen 0.0062 in every arm
                # -> projected job CPU 100: 76, 200: 150, 400: 299, 800: 596 (cap 7200); 800 is the largest choice
ARM_INDEX = {"cell": 0, "control": 1, "null": 2}
ORDER = np.arange(N - 1, -1, -1)
COLS = (np.arange(N)[:, None] + np.arange(K + 1)[None, :]) % N
W5 = (1 << np.arange(K + 1)).astype(np.int64)
ODD = (np.arange(NP) & 1) == 1
MASKS = np.array([0, 0xF000, 0xFF00, 0xFFF0, 0xFFFF], np.int64)


# ------------------------------------------------------------------ landscapes and observations

class Lands:
    def __init__(self, seeds):
        self.seeds = np.asarray(seeds)
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.table = np.stack([w.table for w in self.worlds]).astype(np.int64)          # [L, 64, 32]
        fl = np.stack([np.random.Generator(np.random.PCG64([int(s), 1 << 40])).integers(0, RATE, (N, NP))
                       for s in seeds]) == 0
        v = np.stack([np.random.Generator(np.random.PCG64([int(s), 1 << 41])).integers(0, 65536, (N, NP))
                      for s in seeds]).astype(np.int64)
        self.corrupt_table = np.where(fl, self.table ^ v, self.table)
        self.obs = {"clean": features(self.table), "corrupt": features(self.corrupt_table),
                    "silent": np.zeros((len(seeds), N, 6), np.int64)}
        self.flipped_share = float(fl.mean())


def features(tab) -> np.ndarray:
    """[L, 64, 32] observed table -> int64 [L, 64, 6]: f0..f4 and the marginal sign basis (sum odd - sum even)."""
    odd, even = tab[:, :, ODD].sum(2), tab[:, :, ~ODD].sum(2)
    diff = odd - even
    return np.stack([diff // 32 + 32768, tab.max(2), tab[:, :, 1], tab[:, :, 0], tab.sum(2) // 32, diff], 2)


def nk_fit(bits, table) -> np.ndarray:
    """bits int64 [P, L, 64], true table [L, 64, 32] -> int64 [P, L]."""
    idx = bits[:, :, COLS] @ W5                                                        # [P, L, 64]
    L = table.shape[0]
    return table[np.arange(L)[None, :, None], np.arange(N)[None, None, :], idx].sum(2)


# ------------------------------------------------------------------ genome (vectorised)

def decode(G):
    G = np.asarray(G, np.int64)
    return (G[:, 0] % 5, G[:, 1] % 5, G[:, 2] | (G[:, 3] << 8), G[:, 4] | (G[:, 5] << 8), G[:, 8:16] & 1)


def rollout(G, obs, freeze_shift=False, perm=None):
    """G [P, 16], obs [L, 64, 6] -> (bits int64 [P, L, 64], refits int64 [P, L])."""
    s, k, a, c, C = decode(G)
    P, L = len(G), obs.shape[0]
    if perm is not None:
        obs = obs[np.arange(L)[:, None], perm]
    shift = np.zeros((P, L), np.int64)
    win = np.zeros((P, L), np.int64)
    refits = np.zeros((P, L), np.int64)
    bits = np.zeros((P, L, N), np.int64)
    mask = MASKS[k][:, None]
    for n, j in enumerate(ORDER):
        f = obs[:, j, :]                                                              # [L, 6]
        xe = f[np.arange(L)[None, :], s[:, None]] & mask                               # [P, L]
        idx = ((a[:, None] * xe + c[:, None] + 8192 * shift) & 0xFFFF) >> 13
        b = C[np.arange(P)[:, None], idx]
        bits[:, :, j] = b
        d = f[None, :, 5]
        win += np.where(b == 1, d >= 0, d <= 0)
        if (n + 1) % WINDOW == 0:
            if not freeze_shift:
                sur = win < WINDOW * SURPRISE_SUPPORT
                shift = (shift + sur) & 7
                refits += sur
            win[:] = 0
    return bits, refits


def fitness(G, lands, view, **kw) -> np.ndarray:
    bits, _ = rollout(G, lands.obs[view], **kw)
    return nk_fit(bits, lands.table).sum(1)


# ------------------------------------------------------------------ scalar reference

def scalar_fit(g, lands, view, freeze_shift=False) -> int:
    s, k, a, c = int(g[0]) % 5, int(g[1]) % 5, int(g[2]) | (int(g[3]) << 8), int(g[4]) | (int(g[5]) << 8)
    C = [int(x) & 1 for x in g[8:16]]
    mask = [0, 0xF000, 0xFF00, 0xFFF0, 0xFFFF][k]
    tabs = {"clean": lands.table, "corrupt": lands.corrupt_table, "silent": None}[view]
    total = 0
    for li, world in enumerate(lands.worlds):
        shift = win = 0
        bits = [0] * N
        for n, j in enumerate(range(N - 1, -1, -1)):
            if tabs is None:
                feats, d = [0, 0, 0, 0, 0], 0
            else:
                row = [int(x) for x in tabs[li, j]]
                odd = sum(row[i] for i in range(NP) if i & 1)
                even = sum(row[i] for i in range(NP) if not i & 1)
                d = odd - even
                feats = [d // 32 + 32768, max(row), row[1], row[0], sum(row) // 32]
            xe = feats[s] & mask
            b = C[((a * xe + c + 8192 * shift) & 0xFFFF) >> 13]
            bits[j] = b
            win += int(d >= 0) if b == 1 else int(d <= 0)
            if (n + 1) % WINDOW == 0:
                if not freeze_shift and win < WINDOW * SURPRISE_SUPPORT:
                    shift = (shift + 1) & 7
                win = 0
        total += int(world.evaluate(np.packbits(np.array(bits, np.uint8))[None])[0][0])
    return total


def hand_genome(inverse=False):
    g = np.zeros(GLEN, np.uint8)
    g[0], g[1], g[2] = 0, 4, 1
    g[8:16] = [1, 1, 1, 1, 0, 0, 0, 0] if inverse else [0, 0, 0, 0, 1, 1, 1, 1]
    return g


def planted():
    return np.stack([hand_genome(), hand_genome(inverse=True)])


def init(rng, P):
    G = rng.integers(0, 256, (P, GLEN), dtype=np.int64)
    G[:, 6:8] = 0
    G[:, 8:16] = rng.integers(0, 16, (P, 8))
    return G.astype(np.uint8)


def mutate(rng, B):
    G = B.astype(np.int64)
    P = len(G)
    for col in (0, 1):
        m = rng.random(P) < 0.2
        G[:, col] = np.where(m, (G[:, col] % 5 + np.where(rng.random(P) < 0.5, 1, -1)) % 5, G[:, col])
    for lo in (2, 4):
        v = G[:, lo] | (G[:, lo + 1] << 8)
        m = rng.random(P) < 0.2
        uni = rng.random(P) < 0.5
        step = np.where(rng.random(P) < 0.5, 1, -1) << rng.integers(0, 16, P)
        v = np.where(m, np.where(uni, rng.integers(0, 65536, P), (v + step) & 0xFFFF), v)
        G[:, lo], G[:, lo + 1] = v & 0xFF, v >> 8
    m = rng.random((P, 8)) < 1.0 / 8
    G[:, 8:16] = np.where(m, rng.integers(0, 16, (P, 8)), G[:, 8:16])
    return G.astype(np.uint8)


def descriptor(G, lands, view):
    bits, _ = rollout(G, lands.obs[view][:1])
    return (bits[:, 0, :32].sum(1) * GRID + bits[:, 0, 32:].sum(1)).astype(np.int64)


# ------------------------------------------------------------------ archive (C-R7-01)

class Archive:
    def __init__(self):
        self.cells: dict[int, tuple[int, bytes]] = {}

    def insert(self, cells, fits, B):
        for cc, f, g in zip(cells.tolist(), fits.tolist(), B):
            gbytes = g.tobytes()
            cur = self.cells.get(cc)
            if cur is None or f > cur[0] or (f == cur[0] and gbytes < cur[1]):
                self.cells[cc] = (int(f), gbytes)

    def sample(self, srng, n):
        keys = sorted(self.cells)
        idx = srng.integers(0, len(keys), n)
        return np.frombuffer(b"".join(self.cells[keys[i]][1] for i in idx), np.uint8).reshape(n, GLEN)

    def top(self, k):
        order = sorted(self.cells.values(), key=lambda v: (-v[0], v[1]))[:k]
        return np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, GLEN), \
            np.array([v[0] for v in order], np.int64)


# ------------------------------------------------------------------ oracles

def scalar_oracle(G, lands, view) -> dict:
    ref = np.array([scalar_fit(g, lands, view) for g in G])
    return {"genomes": int(len(G)), "mismatched": int((fitness(G, lands, view) != ref).sum())}


def cheat_oracle(G, lands, view, kind) -> dict:
    ref = np.array([scalar_fit(g, lands, view) for g in G])
    if kind == "plastic":
        ref_c = np.array([scalar_fit(g, lands, view, freeze_shift=True) for g in G])
        vec_c = fitness(G, lands, view, freeze_shift=True)
    else:
        ref_c = np.array([scalar_fit(g, lands, "clean") for g in G])
        vec_c = fitness(G, lands, "clean")
    el = ref_c != ref
    caught = int(((vec_c != ref) & el).sum())
    return {"eligible": int(el.sum()), "caught": caught,
            "share": round(caught / int(el.sum()), 4) if el.any() else 0.0}


def arm_view(arm):
    return {"cell": "corrupt", "control": "clean", "null": "silent"}[arm]


# ------------------------------------------------------------------ one run

def run(family, rs, arm, gens, train, held, track=False):
    ai = ARM_INDEX[arm]
    view = arm_view(arm)
    score_view = "silent" if arm == "null" else "clean"
    rng = np.random.Generator(np.random.PCG64([family, rs, ai, STREAM_TAG]))
    srng = np.random.Generator(np.random.PCG64([family + 1, rs, ai, STREAM_TAG]))
    arch = Archive()
    t0, c0 = time.perf_counter(), time.process_time()
    offers = offer_bad = 0
    for _ in range(gens):
        B = init(rng, BATCH) if not arch.cells else mutate(rng, arch.sample(srng, BATCH))
        bits, _ = rollout(B, train.obs[view])
        per = nk_fit(bits, train.table)
        f = per.sum(1)
        if track:
            offers += len(B)
            ref = np.stack([np.concatenate([w.evaluate(np.packbits(bits[:, li].astype(np.uint8), axis=1))[0]])
                            for li, w in enumerate(train.worlds)], 1)
            offer_bad += int((ref != per).any(1).sum())
        cells = (bits[:, 0, :32].sum(1) * GRID + bits[:, 0, 32:].sum(1)).astype(np.int64)
        arch.insert(cells, f, B)
    wall, cpu = time.perf_counter() - t0, time.process_time() - c0
    top, tf = arch.top(TOP)
    recount_bad = int((fitness(top, train, view) != tf).sum())
    nh = len(held.seeds)
    held_v = float(fitness(top[:1], held, score_view)[0] / nh)
    held_corrupt = float(fitness(top[:1], held, "corrupt")[0] / nh)
    prng = np.random.Generator(np.random.PCG64([STREAM_TAG, family, rs, ai, 99]))
    perm = np.argsort(prng.random((nh, N)), axis=1)
    bits_s, _ = rollout(top[:1], held.obs[score_view], perm=perm)
    scr = float(nk_fit(bits_s, held.table).sum() / nh)
    _, refits = rollout(top[:1], held.obs[score_view])
    s, k, a, c, C = decode(top[:1])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "search_wall_s": round(wall, 3),
            "search_cpu_s": round(cpu, 3), "archive_cells": len(arch.cells), "train_fit_top1": int(tf[0]),
            "train_mean_top1": float(tf[0] / len(train.seeds)),
            "train_fit_top1_clean": int(fitness(top[:1], train, "clean")[0]) if arm != "null" else None,
            "train_fit_top1_corrupt": int(fitness(top[:1], train, "corrupt")[0]) if arm != "null" else None,
            "held_mean_top1": held_v, "held_mean_top1_under_rate16": held_corrupt,
            "held_scrambled_top1": scr, "scramble_lowers": bool(scr < held_v),
            "top1_fields": {"s": int(s[0]), "k": int(k[0]), "a": int(a[0]), "c": int(c[0]), "C": C[0].tolist()},
            "held_refits_mean_top1": float(refits.mean()),
            "top1_hex": top[0].tobytes().hex(), "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(),
            "recount_mismatched_top16": recount_bad, "offers_audited": offers, "offers_mismatched": offer_bad}
    if arm != "null":
        info["pressure_moves_top1_train_fit"] = bool(info["train_fit_top1_clean"] != info["train_fit_top1_corrupt"])
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


def floor_of(held) -> float:
    zeros = np.zeros((1, len(held.seeds), N), np.int64)
    return float(max(nk_fit(zeros, held.table).sum(), nk_fit(zeros + 1, held.table).sum()) / len(held.seeds))


def binding_evidence(train) -> dict:
    rng = np.random.Generator(np.random.PCG64([STREAM_TAG, 1]))
    G = np.concatenate([init(rng, 256), planted()])
    clean, corrupt = fitness(G, train, "clean"), fitness(G, train, "corrupt")
    sub = np.concatenate([G[:30], planted()])
    pl = cheat_oracle(sub, train, "corrupt", "plastic")
    nz = cheat_oracle(sub, train, "corrupt", "noise")
    return {"intervention_magnitude": int((clean != corrupt).sum()), "oracle_eligible": min(pl["eligible"],
                                                                                            nz["eligible"]),
            "genomes_intervention": int(len(G)), "genomes_oracle": int(len(sub)), "cheat_plastic": pl,
            "cheat_noise": nz}


def job(ctx, gens: int = GENS, exp_id: str = EXP):
    from primordial.score import anti_prior as AP
    if not gens:
        raise ValueError("GENS not set")
    train, held = Lands(TRAIN_SEEDS), Lands(HELD_SEEDS)
    floor = floor_of(held)
    runs = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    todo = [("control", f, rs) for f, rs in runs] + [("null", f, rs) for f, rs in runs] + [("null_check", 0, 0)] + \
        [("cell", f, rs) for f, rs in runs]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": [], "null": []},
                                   "lowers": {"cell": [], "null": []},
                                   "clean": {"cell": True, "control": True, "null": True},
                                   "cpu": {"cell": 0.0, "control": 0.0, "null": 0.0}, "null_check": None,
                                   "ref": False}
    if not st["ref"]:
        evid = binding_evidence(train)
        pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
        hand = planted()[:1]
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "rate": RATE, "floor_held": floor, "p3_min_runs": P3_MIN,
                  "hand_held_clean": float(fitness(hand, held, "clean")[0] / len(HELD_SEEDS)),
                  "hand_held_corrupt": float(fitness(hand, held, "corrupt")[0] / len(HELD_SEEDS)),
                  "hand_train_clean": float(fitness(hand, train, "clean")[0] / len(TRAIN_SEEDS)),
                  "hand_train_corrupt": float(fitness(hand, train, "corrupt")[0] / len(TRAIN_SEEDS)),
                  "train_flipped_entry_share": train.flipped_share, "binding_evidence": evid,
                  "binding_precheck": {"ok": pc["ok"], "version": pc["version"], "reasons": pc["reasons"],
                                       "basis": {c: pc["checks"][c]["basis"] for c in pc["checks"]}},
                  "order": "binding precheck, control, null, NULL_CHECK, cell", "status": "control",
                  "ts": round(time.time(), 3)})
        if not pc["ok"]:
            ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
                      "primary": "INELIGIBLE", "reasons": pc["reasons"], "status": "aborted",
                      "reason": "measured binding pre-check failed before any run", "ts": round(time.time(), 3)})
            return
        st["ref"] = True
        ctx.checkpoint(st)
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        arm, fam, rs = todo[st["next"]]
        if arm == "null_check":
            sc = score(st["held"]["null"], st["lowers"]["null"], st["held"]["control"], floor)
            passes = bool(sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"]
                          and st["clean"]["null"] and st["clean"]["control"])
            st["null_check"] = {"null_predicate": "PASS" if passes else "FAIL", **sc,
                                "oracle_clean_null": st["clean"]["null"],
                                "oracle_clean_control": st["clean"]["control"]}
            ctx.emit({"kind": "null_check", "exp_id": exp_id, **st["null_check"],
                      "rule": "the planted null must FAIL the predicate before any cell-arm row", "status": "control",
                      "ts": round(time.time(), 3)})
            if passes:
                ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
                          "primary": "PREDICATE_PASSES_PLANTED_NULL", "null_check": st["null_check"],
                          "status": "aborted", "reason": "predicate rewrite required before any cell-arm row",
                          "ts": round(time.time(), 3)})
                return
            st["next"] += 1
            ctx.checkpoint(st)
            continue
        cell = {"cell": CELL, "control": CELL_CTRL, "null": CELL_NULL}[arm]
        view = arm_view(arm)
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(fam, rs, arm, gens, train, held, track=first)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genome_bytes": GLEN, "reader": "top1_train", "selection_view": view, **info,
               "status": "record" if arm == "cell" else "control"}
        if first:
            G = np.concatenate([top, planted()])
            o = {"scalar": scalar_oracle(G, train, view), "cheat_plastic": cheat_oracle(G, train, view, "plastic")}
            o["ok"] = bool(ok and o["scalar"]["mismatched"] == 0)
            if arm == "null":
                o["cheat_plastic_rule"] = ("EXEMPT for the null by rule, fixed before any run: with every feature 0 the "
                                           "marginal ties, support is 1 and the shift never moves, so no genome is "
                                           "eligible (the C-R6 constant-input lesson)")
            else:
                o["ok"] = o["ok"] and o["cheat_plastic"]["eligible"] > 0 and o["cheat_plastic"]["share"] >= 0.9
            if arm == "cell":
                o["cheat_noise"] = cheat_oracle(G, train, view, "noise")
                o["ok"] = o["ok"] and o["cheat_noise"]["eligible"] > 0 and o["cheat_noise"]["share"] >= 0.9
            row["oracles"] = o
            ok = o["ok"]
        st["clean"][arm] = bool(st["clean"][arm] and ok)
        row["wall_s"], row["cpu_s"] = round(time.perf_counter() - t0, 3), round(time.process_time() - c0, 3)
        st["cpu"][arm] += row["cpu_s"]
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(info["held_mean_top1"])
        if arm != "control":
            st["lowers"][arm].append(info["scramble_lowers"])
        ctx.emit(row)
        st["next"] += 1
        ctx.checkpoint(st)
        ctx.progress(st["next"], len(todo) - st["next"])
    sc = score(st["held"]["cell"], st["lowers"]["cell"], st["held"]["control"], floor)
    ok_all = st["clean"]["cell"] and st["clean"]["control"]
    full = all(len(st["held"][a]) == len(runs) for a in ("cell", "control"))
    vacuous = sc["iqr"] == 0 and sc["control_iqr"] == 0 and sc["median"] == sc["control_median"]
    primary = "INDETERMINATE" if not (ok_all and full) else "VACUOUS" if vacuous else \
        ("PASS" if sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
              "runs_total": len(st["held"]["cell"]), "rng_family_count": len(FAMILIES),
              "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES}, "gens": gens, **sc,
              "vacuous": bool(vacuous), "null_check": st["null_check"], "oracle_clean": ok_all,
              "arm_cpu_s": {a: round(v, 3) for a, v in st["cpu"].items()}, "primary": primary,
              "clause_a": "none: nk_stub is not a screened graphworld world", "status": "record" if ok_all else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 10) -> None:
    """No rows, no held value computed: scalar == vectorised, cheat eligibility, binding evidence, CPU/gen, GENS."""
    from primordial.score import anti_prior as AP
    train = Lands(TRAIN_SEEDS)
    rng = np.random.Generator(np.random.PCG64(77))
    G = np.concatenate([init(rng, 8), planted()])
    out = {"scalar": {v: scalar_oracle(G, train, v) for v in ("clean", "corrupt", "silent")},
           "cheat_plastic": {v: cheat_oracle(G, train, v, "plastic") for v in ("clean", "corrupt", "silent")},
           "cheat_noise": cheat_oracle(G, train, "corrupt", "noise"),
           "train_flipped_entry_share": train.flipped_share}
    evid = binding_evidence(train)
    pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
    out["binding_evidence"] = evid
    out["binding_precheck"] = {"ok": pc["ok"], "reasons": pc["reasons"],
                               "basis": {c: pc["checks"][c]["basis"] for c in pc["checks"]}}
    held = Lands(HELD_SEEDS[:2])                 # timing only; the full HELD set is never scored here
    per = {}
    for arm in ("control", "null", "cell"):
        info, _ = run(4200, 0, arm, gens, train, held, track=True)
        per[arm] = {"cpu_s_per_gen": round(info["search_cpu_s"] / gens, 5),
                    "wall_s_per_gen": round(info["search_wall_s"] / gens, 5),
                    "offers_mismatched": info["offers_mismatched"], "recount_mismatched": info["recount_mismatched_top16"]}
    out["per_arm"] = per
    c = time.process_time()
    G18 = np.concatenate([init(rng, 16), planted()])
    scalar_oracle(G18, train, "corrupt")
    cheat_oracle(G18, train, "corrupt", "plastic")
    cheat_oracle(G18, train, "corrupt", "noise")
    oracle_cpu = (time.process_time() - c) * 3
    unit = sum(per[a]["cpu_s_per_gen"] for a in per) * 32
    proj = {str(Gn): round((unit * Gn + oracle_cpu) * 1.25, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if (unit * Gn + oracle_cpu) * 1.25 <= CPU_CAP]
    out["oracle_cpu_s_x3"] = round(oracle_cpu, 2)
    out["projected_job_cpu_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        dev(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
