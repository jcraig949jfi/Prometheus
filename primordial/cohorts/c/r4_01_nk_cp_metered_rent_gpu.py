"""C-R4-01: drawn cell cp / nk_stub / decoder_rent / torch_gpu / metered_stream (draw seed 6451292431859625233).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. nk_stub is not a graphworld
world: landscape rows only, no clause A claim (SWARM_R4 s3). Definitions fixed before any run:

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE (C-R2-09): selection on 8 train landscapes
            (9100..9107), score = mean raw NK fitness per landscape on 64 held-out landscapes (30000..30063).
  brain     cp (c3's CP family: weights x per-mode factors). Locus j's contribution row has 32 entries indexed by the
            5 neighbourhood bits i_t (t=0 is bit j itself), so a weight over it is a 2x2x2x2x2 tensor, here CP rank
            R=4: W[i] = sum_r lam_r prod_{t in mask} U[t,r,i_t]. The genome also holds a 5-bit ATTEND mask: modes
            outside it are not read (the brain gets the row averaged over those bits; equivalently U = [.5,.5]).
            feature = floor(marginal mean / 4096) / 15 (top nibble). s_j = <W, feat_j> + b; bit_j = [s_j > 0].
            Genome 45 float32 (lam 4, U 40, b 1) + mask byte, padded to 184 bytes. Decoder holds no target.
  channel   metered_stream (C-R2-08's D1 settlement rule and constants): loci are read in order j = 0..63, one tick
            each, through a ledger apart from world fitness. Tick: ledger += CREDIT; cost = ALPHA * 4 bits *
            2^|mask| (nibbles read); if ledger >= cost the row is delivered and ledger -= cost, else silence
            (features 0, so s_j = b). ALPHA = 2, CREDIT = 16, START = 32.
  pressure  decoder_rent: selection fitness = sum over train landscapes of (NK - LAMBDA * active components),
            active = lam_r != 0, LAMBDA = 16384 (C-R2-02's constant). Held-out is scored without rent.
  arms      cell (meter + rent) vs control (same brain, every row delivered, no rent).
  substrate torch_gpu: decode, meter mask, scores and NK fitness on CUDA; numpy is the reference only.
  budget    300 gens x 128 per arm, 8 run seeds, LuaArchive with seeded sampler (9400 + 10 * run_seed + arm),
            GA stream PCG64([4401, run_seed, arm]); mutation: float gene + N(0, .2) with p = 1/8, then lam_r := 0 with
            p = 1/16, mask bits flip with p = 1/8. Init N(0, 1), mask uniform. Descriptor: popcount halves of the bits
            on train landscape 0 (33x33). Elites saved to HOT.
  primary   median over run seeds of held-out NK per landscape (cell, top-16) >= median (control) - 0.5 * IQR(control)
  oracles   world  numpy NKWorld(seed).evaluate == torch fitness on every offer of run seed 0 (both arms) and every
                   final elite x train landscape of every run; cheat K=3 window mismatches >= 90% of seed-0 elite x
                   landscape rows that are not all-zero (C-R2-09 rule).
            brain  float64 numpy reference (marginals by np.mean over unread axes, attended factors only, scalar
                   ledger) == torch bits on seed-0 top-16 x train landscapes (loci with |s_ref| < 1e-3 are ties and
                   excluded, counted); cheat skip_last_component (lam_3 dropped in torch) mismatches the honest
                   reference on >= 90% of ELIGIBLE rows = rows where the float64 reference with lam_3 dropped changes
                   a non-tie bit (eligible count reported, >= 1 required). Rule fixed before the predicate, after a
                   no-rows check on random genomes: "lam_3 != 0" rows flipped a bit only 27-35% of the time.
            meter  scalar ledger replay == torch delivery table for all 32 masks x 64 ticks; cheat free_unaffordable
                   (always deliver) mismatches on every mask with cost > CREDIT (26 of 32).
  report    random-bits and greedy (bit_j = [mean row | i_0=1 > mean row | i_0=0]) held-out references, attended
            modes, active components, delivered share, rent per landscape, train per landscape.

  worker:  python -m primordial.fabric.worker submit C primordial.cohorts.c.r4_01_nk_cp_metered_rent_gpu:job
             --exp C-R4-01-nk-cp-metered-rent-gpu --rows primordial/ledger/rows/C/C-R4-01-nk-cp-metered-rent-gpu.jsonl
             --ttl-cpu-s 600
  ledger:  python -m primordial.cohorts.c.r4_01_nk_cp_metered_rent_gpu qd     (QD ledger rows from the committed rows)
  dev:     python -m primordial.cohorts.c.r4_01_nk_cp_metered_rent_gpu dev    (no rows: eligibility counts only)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
import torch

from primordial.qd.stubworld import GRID, K, N_BITS, N_CELLS, NKWorld

EXP = "C-R4-01-nk-cp-metered-rent-gpu"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP
N, M, E, R, BATCH, TOP = N_BITS, 5, 32, 4, 128, 16
NF, GLEN = 45, 184
ALPHA, CREDIT, START, LAMBDA = 2, 16, 32, 16384
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
CELL = {"representation": "cp", "world": "nk_stub", "pressure": "decoder_rent", "substrate": "torch_gpu",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="none_control", channel="none")
DEV = torch.device("cuda")
IBITS = (np.arange(E)[:, None] >> np.arange(M)[None, :]) & 1                  # [32, 5] entry -> i_t
POP = np.array([bin(m).count("1") for m in range(E)])


def cost(mask: int) -> int:
    return ALPHA * 4 * (1 << int(POP[mask]))


def meter_table(free: bool = False) -> np.ndarray:
    """Scalar ledger replay -> delivered bool [32 masks, 64 ticks]."""
    D = np.zeros((E, N), bool)
    for m in range(E):
        led, c = START, cost(m)
        for j in range(N):
            led += CREDIT
            ok = led >= c
            if ok:
                led -= c
            D[m, j] = ok or free
    return D


def marginal_feats(tables: np.ndarray) -> np.ndarray:
    """tables int64 [L, 64, 32] -> float32 [L, 64, 32 masks, 32] (marginal nibble / 15, expanded over unread bits)."""
    L = len(tables)
    t5 = tables.astype(np.float64).reshape(L, N, 2, 2, 2, 2, 2)              # axis 2 + (4 - t) holds bit t
    out = np.empty((L, N, E, E), np.float32)
    for m in range(E):
        ax = tuple(2 + 4 - t for t in range(M) if not (m >> t) & 1)
        mean = t5.mean(axis=ax, keepdims=True) if ax else t5
        nib = np.floor(np.broadcast_to(mean, t5.shape) / 4096.0) / 15.0
        out[:, :, m] = nib.reshape(L, N, E)
    return out


class Landscapes:
    def __init__(self, seeds):
        self.seeds = seeds
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.tables = np.stack([w.table for w in self.worlds])                 # [L, 64, 32]
        self.t_tables = torch.from_numpy(self.tables).to(DEV)
        self.t_feats = torch.from_numpy(marginal_feats(self.tables)).to(DEV)  # [L, 64, 32, 32]


def split(g: np.ndarray):
    f = np.frombuffer(np.ascontiguousarray(g[:, :NF * 4]).tobytes(), "<f4").reshape(len(g), NF)
    lam, U, b = f[:, :R], f[:, R:R + M * R * 2].reshape(-1, M, R, 2), f[:, -1]
    return lam, U, b, (g[:, NF * 4] & 31).astype(np.int64)


def join(lam, U, b, mask) -> np.ndarray:
    P = len(lam)
    f = np.concatenate([lam, U.reshape(P, -1), b[:, None]], 1).astype("<f4")
    out = np.zeros((P, GLEN), np.uint8)
    out[:, :NF * 4] = np.frombuffer(f.tobytes(), np.uint8).reshape(P, NF * 4)
    out[:, NF * 4] = mask
    return out


T_IBITS = torch.from_numpy(IBITS).to(DEV)
T_METER = torch.from_numpy(meter_table()).to(DEV)
T_FREE = torch.ones((E, N), dtype=torch.bool, device=DEV)


def weights(lam, U, mask, skip_last=False):
    """-> W float32 [P, 32] on DEV."""
    lam = torch.from_numpy(lam.copy()).to(DEV)
    if skip_last:
        lam[:, R - 1] = 0
    U = torch.from_numpy(U.copy()).to(DEV)                                     # [P, 5, R, 2]
    att = ((torch.from_numpy(mask).to(DEV)[:, None] >> torch.arange(M, device=DEV)) & 1).bool()
    Ue = torch.where(att[:, :, None, None], U, torch.full_like(U, 0.5))
    prod = torch.ones((len(lam), R, E), device=DEV)
    for t in range(M):
        prod = prod * Ue[:, t, :, T_IBITS[:, t]]                               # [P, R, 32]
    return (lam[:, :, None] * prod).sum(1)


def decide(g, land, metered, skip_last=False, meter_free=False):
    """genomes -> (bits bool [P, L, 64], s float32 [P, L, 64]) on DEV."""
    lam, U, b, mask = split(g)
    W = weights(lam, U, mask, skip_last)
    tm = torch.from_numpy(mask).to(DEV)
    X = land.t_feats[:, :, tm]                                                 # [L, 64, P, 32]
    s = torch.einsum("ljpe,pe->plj", X, W)
    if metered:
        s = s * (T_FREE if meter_free else T_METER)[tm][:, None, :]
    s = s + torch.from_numpy(b.copy()).to(DEV)[:, None, None]
    return s > 0, s


def nk_fit(bits, land, window=K + 1):
    """bits bool [P, L, 64] -> int64 [P, L]."""
    bi = bits.long()
    idx = sum(torch.roll(bi, shifts=-t, dims=-1) << t for t in range(window))
    P, L = bits.shape[:2]
    tab = land.t_tables[None].expand(P, L, N, E)
    return torch.gather(tab, -1, idx[..., None]).squeeze(-1).sum(-1)


def evaluate(g, land, metered, rent):
    bits, _ = decide(g, land, metered)
    fit = nk_fit(bits, land)
    active = (split(g)[0] != 0).sum(1)
    rent_pl = LAMBDA * active if rent else np.zeros(len(g), np.int64)
    fit_np = fit.cpu().numpy()
    sel = fit_np.sum(1) - rent_pl * fit_np.shape[1]
    b0 = bits[:, 0].cpu().numpy()
    cells = (b0[:, :32].sum(1) * GRID + b0[:, 32:].sum(1)).astype(np.uint32)
    return sel, cells, fit_np, rent_pl, bits


def ref_fit(bits: np.ndarray, land) -> np.ndarray:
    """bits bool [P, L, 64] -> numpy reference int64 [P, L]."""
    P, L = bits.shape[:2]
    out = np.empty((P, L), np.int64)
    for l in range(L):
        out[:, l] = land.worlds[l].evaluate(np.packbits(bits[:, l].astype(np.uint8), axis=1))[0]
    return out


def ref_decide(g, land, metered, skip_last=False):
    """float64 scalar-ish reference -> (bits bool [P, L, 64], s float64 [P, L, 64])."""
    lam, U, b, mask = split(g)
    if skip_last:
        lam = lam.copy()
        lam[:, R - 1] = 0
    D = meter_table()
    P, L = len(g), len(land.worlds)
    s = np.zeros((P, L, N))
    for p in range(P):
        att = [t for t in range(M) if (mask[p] >> t) & 1]
        for l in range(L):
            t5 = land.tables[l].astype(np.float64).reshape(N, 2, 2, 2, 2, 2)
            unread = tuple(1 + 4 - t for t in range(M) if t not in att)
            mg = np.floor((t5.mean(axis=unread, keepdims=True) if unread else t5) / 4096.0) / 15.0
            mg = mg.reshape(N, -1)                                             # [64, 2^|att|], C order over att axes
            # row index in C order of the kept axes (highest t first) -> bits of att
            order = sorted(att, reverse=True)
            w = np.zeros(1 << len(att))
            for ci in range(1 << len(att)):
                it = {t: (ci >> (len(order) - 1 - k)) & 1 for k, t in enumerate(order)}
                w[ci] = sum(float(lam[p, r]) * np.prod([float(U[p, t, r, it[t]]) for t in att]) for r in range(R))
            sj = mg @ w
            if metered:
                sj = sj * D[mask[p]]
            s[p, l] = sj + float(b[p])
    return s > 0, s


def init(rng, P):
    lam = rng.standard_normal((P, R)).astype(np.float32)
    U = rng.standard_normal((P, M, R, 2)).astype(np.float32)
    b = rng.standard_normal(P).astype(np.float32)
    return join(lam, U, b, rng.integers(0, E, P))


def mutate(rng, g):
    lam, U, b, mask = (x.copy() for x in split(g))
    f = np.concatenate([lam, U.reshape(len(g), -1), b[:, None]], 1)
    f += (rng.random(f.shape) < 1.0 / 8) * rng.normal(0, 0.2, f.shape).astype(np.float32)
    lam, U, b = f[:, :R], f[:, R:R + M * R * 2].reshape(-1, M, R, 2), f[:, -1]
    lam = np.where(rng.random(lam.shape) < 1.0 / 16, np.float32(0), lam)
    flips = ((rng.random((len(g), M)) < 1.0 / 8) << np.arange(M)).sum(1)
    return join(lam, U, b, mask ^ flips)


def references(held):
    rr = np.random.Generator(np.random.PCG64(5))
    rbits = rr.integers(0, 2, (256, 1, N)).astype(bool).repeat(len(held.worlds), 1)
    random_mean = float(ref_fit(rbits, held).mean())
    t = held.tables
    greedy = (t[:, :, 1::2].mean(2) > t[:, :, 0::2].mean(2))[None]
    return random_mean, float(ref_fit(greedy, held).mean())


def world_cheat(bits, land):
    fit_ref = ref_fit(bits.cpu().numpy(), land)
    ch = nk_fit(bits, land, window=K).cpu().numpy()
    elig = bits.cpu().numpy().any(axis=2)
    n = int(elig.sum())
    return (float((ch != fit_ref)[elig].mean()) if n else 0.0), n, int(elig.size - n)


def brain_oracle(g, land, metered):
    tb, ts = decide(g, land, metered)
    rb, rs = ref_decide(g, land, metered)
    tb = tb.cpu().numpy()
    ties = np.abs(rs) < 1e-3
    row_bad = ((tb != rb) & ~ties).any(axis=2)
    cb = decide(g, land, metered, skip_last=True)[0].cpu().numpy()
    # eligible: rows where the REFERENCE itself changes a non-tie bit when lam_3 is dropped (no torch involved)
    rb3, rs3 = ref_decide(g, land, metered, skip_last=True)
    elig = ((rb3 != rb) & ~ties & ~(np.abs(rs3) < 1e-3)).any(axis=2)
    n = int(elig.sum())
    cheat_share = float(((cb != rb) & ~ties).any(axis=2)[elig].mean()) if n else 0.0
    return {"rows": int(row_bad.size), "mismatched_rows": int(row_bad.sum()), "tie_loci": int(ties.sum()),
            "cheat_skip_last_share": round(cheat_share, 4), "cheat_eligible_rows": n}


def meter_oracle():
    ref, free = meter_table(), meter_table(free=True)
    honest_bad = int((T_METER.cpu().numpy() != ref).sum())
    elig = [m for m in range(E) if cost(m) > CREDIT]
    caught = sum(int((free[m] != ref[m]).any()) for m in elig)
    return {"cells": E * N, "mismatched": honest_bad, "cheat_eligible_masks": len(elig), "cheat_caught_masks": caught,
            "clean": honest_bad == 0 and caught == len(elig) and len(elig) > 0}


def job(ctx, gens: int = 300, run_seeds: str = "0-7", port: int = 6392):
    import redis
    from primordial.qd.archive import LuaArchive
    lo, hi = (int(x) for x in run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=port)
    train, held = Landscapes(TRAIN_SEEDS), Landscapes(HELD_SEEDS)
    random_mean, greedy_mean = references(held)
    mo = meter_oracle()
    ctx.emit({"kind": "reference", "random_bits_mean_per_held_landscape": random_mean,
              "greedy_i0_mean_per_held_landscape": greedy_mean, "meter_oracle": mo, "status": "control"})
    arms = (("cell", True, True, CELL), ("control", False, False, CELL_CTRL))
    heldv = {"cell": [], "control": []}
    clean = mo["clean"]
    for rs in range(lo, hi + 1):
        for ai, (arm, metered, rent, cell) in enumerate(arms):
            t0 = time.perf_counter()
            arch = LuaArchive(r, f"c-r4-01-{arm}-{rs}", GLEN, sampler_seed=9400 + 10 * rs + ai)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([4401, rs, ai]))
            offers = offer_bad = 0
            for _ in range(gens):
                par = arch.sample(BATCH)
                g = init(rng, BATCH) if len(par) == 0 else mutate(rng, par)
                sel, cells, fit, _, bits = evaluate(g, train, metered, rent)
                if rs == lo:
                    offers += fit.size
                    offer_bad += int((ref_fit(bits.cpu().numpy(), train) != fit).sum())
                arch.insert(cells, sel.astype(np.int32), g, np.zeros((BATCH, 2), np.uint32))
            el = arch.dump()
            arch.clear()
            order = sorted(el.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
            eg = np.frombuffer(b"".join(v[1] for _, v in order), np.uint8).reshape(-1, GLEN)
            ef = np.array([v[0] for _, v in order], np.int64)
            np.save(HOT / f"{arm}_r{rs}_elites.npy", eg)
            sel_e, _, fit_e, rent_e, bits_e = evaluate(eg, train, metered, rent)
            ref_e = ref_fit(bits_e.cpu().numpy(), train)
            elite_bad = int((sel_e != ef).sum()) + int((fit_e != ref_e).sum())
            top = eg[:TOP]
            _, _, fh, rent_h, _ = evaluate(top, held, metered, rent)
            lam, _, _, mask = split(top)
            row = {"kind": "run", "arm": arm, "cell": cell, "run_seed": rs, "gens": gens, "genomes": gens * BATCH,
                   "genome_bytes": GLEN, "archive_cells": len(el), "coverage": round(len(el) / N_CELLS, 4),
                   "train_per_landscape_top16": float(fit_e[:TOP].mean()),
                   "held_per_landscape_top16": float(fh.mean()),
                   "held_minus_random": float(fh.mean() - random_mean),
                   "held_minus_greedy": float(fh.mean() - greedy_mean),
                   "rent_per_landscape_top16": float(np.mean(rent_h)),
                   "attended_modes_median": float(np.median(POP[mask])),
                   "attended_modes_top1": int(POP[mask[0]]), "mask_top1": int(mask[0]),
                   "active_components_median": float(np.median((lam != 0).sum(1))),
                   "delivered_share_median": float(np.median(meter_table()[mask].mean(1))) if metered else 1.0,
                   "elites_mismatched": elite_bad, "offers_audited": offers, "offers_mismatched": offer_bad,
                   "status": "record" if arm == "cell" else "control"}
            clean = clean and elite_bad == 0 and offer_bad == 0
            if rs == lo:
                share, n_el, n_zero = world_cheat(bits_e, train)
                row["cheat_k3_window_mismatch_share_eligible"] = round(share, 4)
                row["cheat_k3_eligible_rows"], row["cheat_k3_all_zero_rows"] = n_el, n_zero
                bo = brain_oracle(top, train, metered)
                row["brain_oracle"] = bo
                clean = (clean and n_el > 0 and share >= 0.9 and bo["mismatched_rows"] == 0
                         and bo["cheat_eligible_rows"] > 0 and bo["cheat_skip_last_share"] >= 0.9)
            row["wall_s"] = round(time.perf_counter() - t0, 2)
            heldv[arm].append(row["held_per_landscape_top16"])
            ctx.emit(row)
    st = {a: tuple(float(x) for x in np.percentile(heldv[a], [25, 50, 75])) for a in heldv}
    bar = st["control"][1] - 0.5 * (st["control"][2] - st["control"][0])
    n = min(len(heldv["cell"]), len(heldv["control"]))
    ctx.emit({"kind": "summary", "cell": CELL, "n_runs": n, "random_bits_mean": random_mean,
              "greedy_i0_mean": greedy_mean,
              "held_median_cell": round(st["cell"][1], 1), "iqr_cell": round(st["cell"][2] - st["cell"][0], 1),
              "held_median_control": round(st["control"][1], 1),
              "iqr_control": round(st["control"][2] - st["control"][0], 1),
              "bar": round(bar, 1), "oracle_clean": clean,
              "primary": "INDETERMINATE" if not clean else ("PASS" if n >= 8 and st["cell"][1] >= bar else "FAIL"),
              "clause_a": "none (nk_stub is not a screened graphworld world)",
              "status": "record" if clean else "cheat"})


def qd() -> None:
    from primordial.fabric.rows import RowWriter
    from primordial.ops import qd_ledger
    rows = [json.loads(x) for x in ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
    summ = [x for x in rows if x.get("kind") == "summary"][-1]
    runs = [x for x in rows if x.get("kind") == "run"]
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for arm, cell, status in (("cell", CELL, summ["status"]), ("control", CELL_CTRL, "control")):
            v = [x["held_per_landscape_top16"] for x in runs if x["arm"] == arm]
            p25, p50, p75 = np.percentile(v, [25, 50, 75])
            q.write({"cell": cell, "mechanism": f"nk_cp_rank4_attend_mask_{arm}_train8_landscapes_300gens",
                     "fitness": {"held64_median": None, "held_per_landscape_median": round(float(p50), 1),
                                 "iqr": round(float(p75 - p25), 1), "random_bits_mean": round(summ["random_bits_mean"], 1),
                                 "greedy_i0_mean": round(summ["greedy_i0_mean"], 1), "n_runs": len(v)},
                     "footprint": {"genome_bytes": GLEN},
                     "oracle": ("clean (numpy NK == torch on seed-0 offers + all elites, K=3 caught; float64 cp reference "
                                "== torch bits, skip_last caught; ledger replay exact, free_unaffordable caught)")
                               if summ["oracle_clean"] else "NOT clean",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


def dev() -> None:
    """No rows: random genomes only, to count cheat eligibility before the predicate is posted."""
    rng = np.random.Generator(np.random.PCG64(99))
    train = Landscapes(TRAIN_SEEDS)
    g = init(rng, 64)
    out = {"meter_oracle": meter_oracle()}
    for metered in (True, False):
        bits = decide(g, train, metered)[0]
        share, n_el, n_zero = world_cheat(bits, train)
        out[f"metered={metered}"] = {"k3_share": round(share, 4), "k3_eligible": n_el, "k3_all_zero": n_zero,
                                     "brain": brain_oracle(g[:16], train, metered),
                                     "offers_mismatched": int((ref_fit(bits.cpu().numpy(), train)
                                                               != nk_fit(bits, train).cpu().numpy()).sum())}
    t = time.perf_counter()
    for _ in range(10):
        evaluate(mutate(rng, g.repeat(2, 0)), train, True, True)
    out["eval_s_per_gen"] = round((time.perf_counter() - t) / 10, 4)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"qd": qd, "dev": dev}[sys.argv[1]]()
