"""C-R5-01 (DISTANT_QD): drawn cell affine_plastic / signal_world_d1 / corruption / numpy / metered_stream
(draw seed 1697858559309454776, round 5 pilot).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. No closed-loop definition of
affine_plastic, corruption or metered_stream on signal_world_d1 existed; the definitions below are fixed before any run.
signal_world_d1 is not a screened graphworld world: no floor suite, no clause A claim (landscape rows only).

  world     lane D's D1 signal world (primordial.lingua.signal): T = 64 ticks, slot 0 sees R in [0, 256) drawn fresh per
            tick (signal.r_stream), slot 1 hears only the channel and acts in [0, 8); right iff act == R >> 5.
  channel   metered_stream = D1's own settlement (signal.NpChannel order): credit y_int for last tick's right action
            lands, then a send of k bits is charged alpha_int * k if the sender can pay; an unaffordable send is not
            delivered (slot 1 hears silence 0). D1 audit constants alpha_int 2, y_int 3, start 8. Fitness = final charge.
  brain     affine_plastic (C7b's representation: affine maps whose CONSTANTS adapt on surprise). Genome 8 bytes
            [k, a_e, c_e, a_d, c_d, 0, 0, 0], k = byte % 9.
            encoder  sym = ((a_e * R + c_e) & 255) >> (8 - k)   (k = 0: silence)
            decoder  act = (a_d * heard + c_d + shift) & 7
            plastic  slot 1 counts its right actions over windows of 8 ticks; support < SURPRISE_SUPPORT (0.5, from
                     brain.affine_plastic) is a surprise and refits the constant: shift = (shift + 1) & 7.
            The analytic D1 code (k 3, a_e 1, c_e 0, a_d 1, c_d 0) is expressible; no target is held by the brain.
  pressure  corruption on the channel, receiver side: at each tick, with p = 1/RATE (RATE 16, C-R2-05's rate), the heard
            symbol (silence included) is XORed with v & (2^k - 1). flip = r_stream(seed + 2^40) % RATE == 0 and
            v = r_stream(seed + 2^41), so the noise is a function of the episode seed only (common across genomes and
            identical in the scalar reference).
  arms      cell (RATE 16) vs control (RATE 0), same code, same GA stream.
  search    (mu + lambda) GA, mu = lambda = 64, parents uniform, byte mutation p 0.2 per field (k +-1 clipped; other
            fields: half uniform byte, half +-1), keep top 64 by (TRAIN fitness desc, genome bytes asc). TRAIN = episode
            seeds 0..127, HELD = 10,000,000..10,000,255. GENS fixed from a no-rows timing check (disclosed).
  sample    RNG families (4200, 2101, 3303, 5501), run seeds 0..7 each: runs_total 32, rng_family_count 4,
            runs_per_family 8 per arm. GA stream PCG64([family, run_seed, arm, 5101]).
  reader    top1_train: the single best genome by TRAIN fitness; value = its mean final charge per HELD episode.
  primary   median over the 32 runs of HELD charge (cell) >= median (control) - 0.5 * IQR (control).
  oracles   family 4200 run seed 0, each arm, on HELD[:32], genomes = top1 + planted (k 3, a_e 1, c_e 0, a_d 1, c_d 1:
            always wrong until refit) + planted spender (k 8, a_e 1: sends 8 bits every tick):
            world   vectorised log hash (R, sym, delivered bits, act, charge) == scalar per-episode reference: 0 mismatched
            conserve honest final charge == start + y_int * rights - alpha_int * delivered bits: 0 violations;
                    cheat free_unaffordable (delivers unaffordable sends free) flagged on >= 90% of episodes where the
                    honest run had an unaffordable send (>= 1 such episode required)
            plastic cheat skip_plastic (shift never updates) changes the hash on >= 90% of episodes where the scalar
                    reference refit (>= 1 required)
            corrupt cell arm: cheat no_corrupt changes the hash on >= 90% of episodes where the scalar reference with
                    and without noise differ (>= 1 required)

  worker:  job = primordial.cohorts.c.r5_01_affine_plastic_d1_corruption_metered:job
  dev:     python -m primordial.cohorts.c.r5_01_affine_plastic_d1_corruption_metered dev   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.brain.affine_plastic import SURPRISE_SUPPORT
from primordial.lingua import signal as S

EXP = "C-R5-01-affine-plastic-d1-corruption-metered"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "affine_plastic", "world": "signal_world_d1", "pressure": "corruption", "substrate": "numpy",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="corruption_rate0")
T = 64
ALPHA_INT, Y_INT, START = 2, 3, 8
RATE = 16
WINDOW = 8
GLEN, POP = 8, 64
TRAIN = np.arange(128)
HELD = 10_000_000 + np.arange(256)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
GENS = 400      # no-rows dev check 0.0141 CPU-s / 0.0134 wall-s per gen: largest of {100, 200, 400, 800} whose 64-run
                # projection stays <= half the PILOT ceilings (600 CPU-s, 450 wall-s); 800 projects 686 wall-s
NOISE_FLIP, NOISE_VAL = 1 << 40, 1 << 41
PLANTED_REFIT = np.array([3, 1, 0, 1, 1, 0, 0, 0], np.uint8)
PLANTED_SPENDER = np.array([8, 1, 0, 1, 0, 0, 0, 0], np.uint8)
HAND = np.array([3, 1, 0, 1, 0, 0, 0, 0], np.uint8)


def noise(seeds, rate):
    s = np.asarray(seeds, np.uint64)
    flip = (S.r_stream(s + np.uint64(NOISE_FLIP), T) % rate == 0) if rate else np.zeros((T, len(s)), bool)
    return flip, S.r_stream(s + np.uint64(NOISE_VAL), T)


def decode(G):
    G = np.asarray(G, np.int64)
    return G[:, 0] % 9, G[:, 1], G[:, 2], G[:, 3], G[:, 4]


def rollout(G, seeds, rate, cheat="", log=False) -> dict:
    """G uint8 [P, GLEN] over episodes seeds [E]; env index p * E + e."""
    P, E = len(G), len(seeds)
    n = P * E
    k, ae, ce, ad, cd = (np.repeat(x, E) for x in decode(G))
    R = np.tile(S.r_stream(seeds, T), (1, P))
    fl, nv = noise(seeds, rate)
    FL, NV = np.tile(fl, (1, P)), np.tile(nv, (1, P))
    mask = (1 << k) - 1
    charge, credit = np.full(n, START, np.int64), np.zeros(n, np.int64)
    shift, win = np.zeros(n, np.int64), np.zeros(n, np.int64)
    refits, unaff, rights, bits_sent = (np.zeros(n, np.int64) for _ in range(4))
    L = np.zeros((T + 1, n, 5), np.int64) if log else None
    for t in range(T):
        r = R[t]
        sym = np.where(k > 0, ((ae * r + ce) & 255) >> (8 - k), 0)
        bits = k * (sym != 0)
        c = charge + credit
        cost = ALPHA_INT * bits
        send = bits > 0
        ok = send & (c >= cost)
        deliver = send if cheat == "free_unaffordable" else ok
        unaff += send & ~ok
        charge = c - np.where(ok, cost, 0)
        heard = np.where(deliver, sym, 0)
        dbits = np.where(deliver, bits, 0)
        bits_sent += dbits
        if cheat != "no_corrupt":
            f = FL[t] & (k > 0)
            heard = np.where(f, heard ^ (NV[t] & mask), heard)
        act = (ad * heard + cd + shift) & 7
        right = act == (r >> 5)
        rights += right
        credit = Y_INT * right
        if log:
            L[t, :, 0], L[t, :, 1], L[t, :, 2], L[t, :, 3], L[t, :, 4] = r, sym, dbits, act, charge
        win += right
        if (t + 1) % WINDOW == 0:
            if cheat != "skip_plastic":
                s = win < WINDOW * SURPRISE_SUPPORT
                shift = (shift + s) & 7
                refits += s
            win[:] = 0
    charge = charge + credit
    out = {"fit": charge.reshape(P, E).sum(1), "charge": charge.reshape(P, E), "rights": rights.reshape(P, E),
           "bits": bits_sent.reshape(P, E), "refits": refits.reshape(P, E), "unaff": unaff.reshape(P, E)}
    if log:
        L[T, :, 4] = charge
        out["L"] = L
        out["hashes"] = [hashlib.sha256(np.ascontiguousarray(L[:, i]).tobytes()).digest() for i in range(n)]
    return out


def ref_episode(g, seed, rate):
    """Scalar reference: one genome, one episode, plain Python ints. -> (log hash, refits)."""
    k = int(g[0]) % 9
    ae, ce, ad, cd = (int(x) for x in g[1:5])
    R = S.r_stream([seed], T)[:, 0]
    fl, nv = noise([seed], rate)
    charge, credit, shift, win, refits = START, 0, 0, 0, 0
    log = np.zeros((T + 1, 5), np.int64)
    for t in range(T):
        r = int(R[t])
        sym = (((ae * r + ce) & 255) >> (8 - k)) if k else 0
        bits = k if sym else 0
        c = charge + credit
        ok = bits > 0 and c >= ALPHA_INT * bits
        charge = c - (ALPHA_INT * bits if ok else 0)
        heard, dbits = (sym, bits) if ok else (0, 0)
        if k and bool(fl[t, 0]):
            heard ^= int(nv[t, 0]) & ((1 << k) - 1)
        act = (ad * heard + cd + shift) & 7
        right = act == (r >> 5)
        log[t] = (r, sym, dbits, act, charge)
        credit = Y_INT if right else 0
        win += int(right)
        if (t + 1) % WINDOW == 0:
            if win < WINDOW * SURPRISE_SUPPORT:
                shift, refits = (shift + 1) & 7, refits + 1
            win = 0
    log[T, 4] = charge + credit
    return hashlib.sha256(log.tobytes()).digest(), refits


def mutate(rng, G):
    G = G.copy()
    P = len(G)
    m = rng.random((P, 5)) < 0.2
    k = G[:, 0].astype(np.int64) % 9
    k2 = np.clip(k + rng.choice(np.array([-1, 1]), P), 0, 8)
    rnd = rng.integers(0, 256, (P, 4))
    pm = rng.choice(np.array([-1, 1]), (P, 4))
    coin = rng.random((P, 4)) < 0.5
    cur = G[:, 1:5].astype(np.int64)
    G[:, 0] = np.where(m[:, 0], k2, k).astype(np.uint8)
    G[:, 1:5] = np.where(m[:, 1:], np.where(coin, rnd, (cur + pm) & 255), cur).astype(np.uint8)
    return G


def select(G, f):
    rank = np.unique(G, axis=0, return_inverse=True)[1].reshape(-1)
    o = np.lexsort((rank, -f.astype(np.int64)))[:POP]
    return G[o], f[o]


def run(family, rs, arm_i, rate, gens):
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 5101]))
    pop = rng.integers(0, 256, (POP, GLEN), dtype=np.uint8)
    pop[:, 5:] = 0
    fit = rollout(pop, TRAIN, rate)["fit"]
    pop, fit = select(pop, fit)
    for _ in range(gens):
        kids = mutate(rng, pop[rng.integers(0, POP, POP)])
        kf = rollout(kids, TRAIN, rate)["fit"]
        pop, fit = select(np.concatenate([pop, kids]), np.concatenate([fit, kf]))
    return pop, fit


def oracles(top1, rate, cell_arm: bool) -> dict:
    seeds = HELD[:32]
    G = np.stack([top1, PLANTED_REFIT, PLANTED_SPENDER])
    E = len(seeds)
    hon = rollout(G, seeds, rate, log=True)
    refs = [[ref_episode(g, int(s), rate) for s in seeds] for g in G]
    world_bad = sum(hon["hashes"][p * E + e] != refs[p][e][0] for p in range(len(G)) for e in range(E))
    L = hon["L"]
    corrects = (L[:T, :, 3] == (L[:T, :, 0] >> S.SHIFT)).sum(0)
    viol = int((L[T, :, 4] != START + Y_INT * corrects - ALPHA_INT * L[:T, :, 2].sum(0)).sum())

    def caught(cheat, eligible):
        ch = rollout(G, seeds, rate, cheat=cheat, log=True)
        Lc = ch["L"]
        idx = [p * E + e for p in range(len(G)) for e in range(E) if eligible(p, e)]
        if cheat == "free_unaffordable":
            cc = (Lc[:T, :, 3] == (Lc[:T, :, 0] >> S.SHIFT)).sum(0)
            flag = Lc[T, :, 4] != START + Y_INT * cc - ALPHA_INT * Lc[:T, :, 2].sum(0)
            hits = sum(bool(flag[i]) for i in idx)
        else:
            hits = sum(ch["hashes"][i] != hon["hashes"][i] for i in idx)
        return {"eligible": len(idx), "caught": int(hits), "share": round(hits / len(idx), 4) if idx else 0.0}

    unaff = hon["unaff"]
    out = {"world_mismatched_episodes": int(world_bad), "episodes": len(G) * E, "conservation_violations": viol,
           "free_unaffordable": caught("free_unaffordable", lambda p, e: unaff[p, e] > 0),
           "skip_plastic": caught("skip_plastic", lambda p, e: refs[p][e][1] > 0)}
    ok = world_bad == 0 and viol == 0
    for name in ("free_unaffordable", "skip_plastic"):
        ok = ok and out[name]["eligible"] > 0 and out[name]["share"] >= 0.9
    if cell_arm:
        clean = [[ref_episode(g, int(s), 0)[0] for s in seeds] for g in G]
        out["no_corrupt"] = caught("no_corrupt", lambda p, e: clean[p][e] != refs[p][e][0])
        ok = ok and out["no_corrupt"]["eligible"] > 0 and out["no_corrupt"]["share"] >= 0.9
    out["ok"] = bool(ok)
    return out


def describe(g, rate) -> dict:
    o = rollout(g[None], HELD, rate)
    return {"genome": [int(x) for x in g[:5]], "k": int(g[0]) % 9,
            "held_charge_per_episode": float(o["charge"].mean()), "held_yield": float(o["rights"].mean() / T),
            "held_bits_per_tick": float(o["bits"].mean() / T), "held_refits_per_episode": float(o["refits"].mean()),
            "held_unaffordable_per_episode": float(o["unaff"].mean())}


def job(ctx, gens: int = GENS):
    arms = (("cell", RATE, CELL), ("control", 0, CELL_CTRL))
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in range(2)]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False}
    if not st["ref"]:
        refs = {name: {arm: describe(g, rate) for arm, rate, _ in arms}
                for name, g in (("hand_d1_code", HAND), ("silence", np.zeros(GLEN, np.uint8)),
                                ("planted_refit", PLANTED_REFIT))}
        ctx.emit({"kind": "reference", "exp_id": EXP, "gens": gens, "pop": POP, "rate": RATE, "window": WINDOW,
                  "alpha_int": ALPHA_INT, "y_int": Y_INT, "start": START, "genomes": refs, "status": "control",
                  "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        arm, rate, cell = arms[ai]
        t0, c0 = time.perf_counter(), time.process_time()
        pop, fit = run(fam, rs, ai, rate, gens)
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genomes_evaluated": POP * (gens + 1), "genome_bytes": GLEN, "reader": "top1_train",
               "train_fit_top1": int(fit[0]), **describe(pop[0], rate),
               "status": "record" if arm == "cell" else "control"}
        if fam == FAMILIES[0] and rs == 0:
            o = oracles(pop[0], rate, arm == "cell")
            row["oracles"] = o
            st["clean"] = st["clean"] and o["ok"]
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held_charge_per_episode"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    q = {a: [float(x) for x in np.percentile(st["held"][a], [25, 50, 75])] for a in st["held"]}
    bar = q["control"][1] - 0.5 * (q["control"][2] - q["control"][0])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if q["cell"][1] >= bar else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": EXP, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "held_charge_median_cell": round(q["cell"][1], 4), "iqr_cell": round(q["cell"][2] - q["cell"][0], 4),
              "held_charge_median_control": round(q["control"][1], 4),
              "iqr_control": round(q["control"][2] - q["control"][0], 4), "bar": round(bar, 4),
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: signal_world_d1 is not a screened world (no floor suite)",
              "status": "record" if st["clean"] else "cheat", "ts": round(time.time(), 3)})


def dev() -> None:
    """No rows: oracle eligibility on random + planted genomes, and CPU per GA generation."""
    rng = np.random.Generator(np.random.PCG64(77))
    g = rng.integers(0, 256, GLEN, dtype=np.uint8)
    g[5:] = 0
    out = {"oracles_cell_random_top1": oracles(g, RATE, True), "oracles_control_hand": oracles(HAND, 0, False),
           "hand": describe(HAND, RATE), "hand_clean": describe(HAND, 0)}
    c, t = time.process_time(), time.perf_counter()
    run(4200, 0, 0, RATE, 10)
    out["cpu_s_per_gen"] = round((time.process_time() - c) / 10, 4)
    out["wall_s_per_gen"] = round((time.perf_counter() - t) / 10, 4)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"dev": dev}[sys.argv[1]]()
