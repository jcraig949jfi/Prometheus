"""Lane D, D1: a 2-slot signal world and the codes that cross it.

Slot 0 sees a register R in [0,256) drawn fresh each tick; slot 1 sees only the
channel and picks an action in [0,8). Slot 1 is right iff action == R >> 5, so
three bits of R matter and five do not.

A code is a genome (k, enc, dec): enc[R] is a symbol in [0, 2**k). Symbol 0 is
silence (no message, 0 bits); any other symbol costs k bits. dec[symbol] is the
action (dec[0] = what slot 1 does when it hears nothing).

Two ledgers, kept apart:
- learning cost per tick (floats): alpha*bits + beta*entries + delta*error,
  entries = distinct symbols the encoder emits (decoder rent).
- world charge (integers): the sender pays alpha_int per delivered bit and earns
  y_int for each tick slot 1 was right, credited on the next settlement. It is
  settled by channel.lua or by NpChannel, and the two must agree exactly.

Hot path: integer arrays only.
"""
from __future__ import annotations

import hashlib

import numpy as np

N_R, N_ACT, SHIFT = 256, 8, 5
CHANCE = 1.0 / N_ACT


# ------------------------------------------------------------------ world stream
def _splitmix(x: np.ndarray) -> np.ndarray:
    z = x + np.uint64(0x9E3779B97F4A7C15)
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


def r_stream(seeds, T: int) -> np.ndarray:
    """int64 [T, n]: the register R each env draws on each tick (xorshift64 per env)."""
    st = _splitmix(np.asarray(seeds, dtype=np.uint64).reshape(-1))
    st = np.where(st == 0, np.uint64(1), st)
    out = np.empty((T, st.shape[0]), dtype=np.int64)
    for t in range(T):
        st = st ^ (st << np.uint64(13))
        st = st ^ (st >> np.uint64(7))
        st = st ^ (st << np.uint64(17))
        out[t] = ((st >> np.uint64(24)) & np.uint64(255)).astype(np.int64)
    return out


# ------------------------------------------------------------------ genomes
def random_genomes(rng: np.random.Generator, P: int):
    k = rng.integers(0, 9, P)
    enc = rng.integers(0, N_R, (P, N_R)) % np.left_shift(1, k)[:, None]
    dec = rng.integers(0, N_ACT, (P, N_R))
    return k, enc, dec


def hand_code(m: int):
    """The analytic-optimal code with m distinct symbols: buckets 1..m-1 get their own
    symbol, every other bucket (bucket 0 included) stays silent and decodes to 0."""
    k = 0 if m == 1 else int(np.ceil(np.log2(m)))
    bucket = np.arange(N_R) >> SHIFT
    enc = np.where((bucket >= 1) & (bucket <= m - 1), bucket, 0).astype(np.int64)
    dec = np.zeros(N_R, dtype=np.int64)
    dec[1:m] = np.arange(1, m)
    return k, enc, dec


def _compact(enc: np.ndarray, dec: np.ndarray, i: int) -> None:
    """Relabel genome i's used non-silent symbols to 1..u, decoder moved with them
    (behaviour unchanged), so a later width decrease does not collide symbols."""
    used = np.unique(enc[i])
    nz = used[used != 0]
    new = np.zeros(N_R, dtype=np.int64)
    new[nz] = np.arange(1, len(nz) + 1)
    d = dec[i].copy()
    d[1:len(nz) + 1] = dec[i][nz]
    enc[i] = new[enc[i]]
    dec[i] = d


def mutate(rng: np.random.Generator, k, enc, dec, n_enc=4, n_dec=2, p_k=0.1, p_compact=0.05):
    P = len(k)
    enc = enc.copy()
    dec = dec.copy()
    for i in np.nonzero(rng.random(P) < p_compact)[0]:
        _compact(enc, dec, int(i))
    step = rng.choice(np.array([-1, 1]), P)
    k = np.clip(k + (rng.random(P) < p_k) * step, 0, 8)
    width = np.left_shift(1, k)
    enc %= width[:, None]
    rows = np.repeat(np.arange(P), n_enc)
    cols = rng.integers(0, N_R, P * n_enc)
    src = rng.integers(0, N_R, P * n_enc)
    fresh = rng.integers(0, np.repeat(width, n_enc))
    copy = rng.random(P * n_enc) < 0.5
    enc[rows, cols] = np.where(copy, enc[rows, src], fresh)
    rows = np.repeat(np.arange(P), n_dec)
    dec[rows, rng.integers(0, np.repeat(width, n_dec))] = rng.integers(0, N_ACT, P * n_dec)
    return k, enc, dec


# ------------------------------------------------------------------ costs
def entries(enc: np.ndarray) -> np.ndarray:
    used = np.zeros((enc.shape[0], N_R), dtype=bool)
    used[np.arange(enc.shape[0])[:, None], enc] = True
    return used.sum(1)


def evaluate(k, enc, dec, R, alpha, beta, delta):
    """Genomes [P] over register samples R [N]. Returns (cost, yield, bits/tick, entries).
    R = arange(256) gives the exact expectation (R is uniform)."""
    sym = enc[:, R]
    act = np.take_along_axis(dec, sym, 1)
    yld = (act == (R >> SHIFT)[None, :]).mean(1)
    bits = (k[:, None] * (sym != 0)).mean(1)
    ent = entries(enc)
    return alpha * bits + beta * ent + delta * (1.0 - yld), yld, bits, ent


def analytic_optimum(alpha, beta, delta):
    """min over m of alpha*ceil(log2 m)*(m-1)/8 + beta*m + delta*(1 - m/8). Returns (m, cost).
    Bound: silence can be right on at most one bucket (1/8), each other symbol on at most
    one bucket, so m symbols give yield <= m/8 and need nonzero mass >= (m-1)/8 at k bits."""
    best = None
    for m in range(1, N_ACT + 1):
        k = 0 if m == 1 else int(np.ceil(np.log2(m)))
        c = alpha * k * (m - 1) / 8 + beta * m + delta * (1 - m / 8)
        if best is None or c < best[1] - 1e-12:
            best = (m, c)
    return best


def mutual_info(enc, labels, n_labels) -> float:
    """I(symbol; label(R)) in bits, R uniform over [0,256)."""
    joint = np.zeros((N_R, n_labels))
    np.add.at(joint, (np.asarray(enc), labels), 1.0)
    joint /= N_R
    ps, pl = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float((joint[nz] * np.log2(joint[nz] / (ps @ pl)[nz])).sum())


def mi_bucket(enc) -> float:
    return mutual_info(enc, np.arange(N_R) >> SHIFT, N_ACT)


def mi_low(enc) -> float:
    return mutual_info(enc, np.arange(N_R) & ((1 << SHIFT) - 1), 1 << SHIFT)


# ------------------------------------------------------------------ learner
def learn(alpha, beta, delta, seed: int, pool: np.ndarray, gens: int, lam: int = 32, envs: int = 128):
    """(1+lam) hill climber; each generation scores parent and children on the same
    `envs` world episodes drawn from `pool` [T, n_pool] (uint8 registers). Ties go to a child."""
    rng = np.random.Generator(np.random.PCG64(seed))
    k, enc, dec = random_genomes(rng, 1)
    for _ in range(gens):
        R = pool[:, rng.integers(0, pool.shape[1], envs)].reshape(-1).astype(np.int64)
        ck, ce, cd = mutate(rng, np.repeat(k, lam), np.repeat(enc, lam, 0), np.repeat(dec, lam, 0))
        K, E, D = np.concatenate([k, ck]), np.concatenate([enc, ce]), np.concatenate([dec, cd])
        cost = evaluate(K, E, D, R, alpha, beta, delta)[0]
        j = len(cost) - 1 - int(np.argmin(cost[::-1]))
        k, enc, dec = K[j:j + 1], E[j:j + 1], D[j:j + 1]
    return int(k[0]), enc[0], dec[0]


# ------------------------------------------------------------------ scramble probe
def scramble_probe(k, enc, dec, seeds, T, rng: np.random.Generator, leak: bool = False) -> dict:
    """Permute the decoder's symbol table (silence included) independently per episode.
    A code that carries the signal through the channel falls toward chance; a slot 1
    that gets R some other way does not. Normalised drop = (y - y_scr) / (y - 1/8)."""
    enc, dec = np.asarray(enc), np.asarray(dec)
    R = r_stream(seeds, T)
    truth = R >> SHIFT
    E, ns = len(seeds), 1 << int(k)
    perm = np.tile(np.arange(N_R), (E, 1))
    perm[:, :ns] = np.argsort(rng.random((E, ns)), axis=1)
    sym = enc[R]
    heard = perm[np.arange(E)[None, :], sym]
    if leak:   # LEAK cheat: slot 1 regenerates R from the shared episode seed, ignores the channel
        guess = r_stream(seeds, T) >> SHIFT
        y0 = y1 = float((guess == truth).mean())
    else:
        y0 = float((dec[sym] == truth).mean())
        y1 = float((dec[heard] == truth).mean())
    eligible = y0 > CHANCE + 0.05
    drop = (y0 - y1) / (y0 - CHANCE) if eligible else None
    return {"y": y0, "y_scrambled": y1, "eligible": eligible, "norm_drop": drop,
            "flagged_leak": bool(eligible and drop <= 0.1)}


# ------------------------------------------------------------------ world episodes
class NpChannel:
    """Reference settlement, same order as channel.lua: credit lands, then a send is charged
    alpha_int*bits if the sender can pay; an unaffordable send is not delivered."""

    def __init__(self, n: int, alpha_int: int, start: int):
        self.charge = np.full(n, start, dtype=np.int64)
        self.alpha = int(alpha_int)
        self.unaffordable = 0
        self.delivered_sends = 0

    def tick(self, t, bits, syms, credit):
        c = self.charge + credit
        cost = self.alpha * bits
        send = bits > 0
        ok = send & (c >= cost)
        self.unaffordable += int((send & ~ok).sum())
        self.delivered_sends += int(ok.sum())
        self.charge = c - np.where(ok, cost, 0)
        return self.charge.copy(), np.where(ok, syms, 0), np.where(ok, bits, 0)


def run_world(k, enc, dec, seeds, T, ch, y_int: int, leak: bool = False) -> dict:
    """T ticks of n episodes through channel `ch`. Log per tick and env:
    (R, symbol sent, bits delivered, action, charge); row T holds the final settlement."""
    enc, dec = np.asarray(enc, dtype=np.int64), np.asarray(dec, dtype=np.int64)
    R = r_stream(seeds, T)
    n = len(seeds)
    guess = (r_stream(seeds, T) >> SHIFT) if leak else None
    credit = np.zeros(n, dtype=np.int64)
    log = np.zeros((T + 1, n, 5), dtype=np.int64)
    for t in range(T):
        sym = enc[R[t]]
        bits = int(k) * (sym != 0)
        charge, heard, dbits = ch.tick(t, bits, sym, credit)
        act = guess[t] if leak else dec[heard]
        log[t, :, 0], log[t, :, 1], log[t, :, 2], log[t, :, 3], log[t, :, 4] = R[t], sym, dbits, act, charge
        credit = y_int * (act == (R[t] >> SHIFT))
    zero = np.zeros(n, dtype=np.int64)
    log[T, :, 4] = ch.tick(T, zero, zero, credit)[0]
    hashes = [hashlib.sha256(np.ascontiguousarray(log[:, e]).tobytes()).digest() for e in range(n)]
    return {"log": log, "hashes": hashes}


def conservation_violations(res: dict, start: int, alpha_int: int, y_int: int) -> int:
    """Envs whose final charge != start + y_int*corrects - alpha_int*delivered bits.
    Uses only what the channel returned (delivered bits, charges) and slot 1's actions."""
    log = res["log"]
    T = log.shape[0] - 1
    corrects = (log[:T, :, 3] == (log[:T, :, 0] >> SHIFT)).sum(0)
    spent = alpha_int * log[:T, :, 2].sum(0)
    return int((log[T, :, 4] != start + y_int * corrects - spent).sum())
