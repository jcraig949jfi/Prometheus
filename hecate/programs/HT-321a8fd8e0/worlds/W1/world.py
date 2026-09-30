"""HT-321a8fd8e0 / W1: code-decoded outcome rule vs coalition manipulation.

See IMPLEMENTATION_NOTES.md. Writes rows.jsonl (one row per arm x seed),
run_meta.json, attempts.json -- all in this directory.
"""
import itertools
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 31
KMSG = 16
NPAR = 15
KS = list(range(1, 9))
N_COAL = 200
SEEDS = list(range(20))
ARM_CODE = {"TREATMENT": 1, "CONTROL": 2, "NULL_TWIN": 3, "POSITIVE_CONTROL": 4, "CHEAT": 5}
CONTROL_MATRIX_SEED = 1001


# ---------------- GF(32) and BCH(31,16) ----------------
def gf32_tables():
    prim = 0b100101  # x^5 + x^2 + 1
    exp = [0] * 62
    log = [0] * 32
    v = 1
    for i in range(31):
        exp[i] = v
        log[v] = i
        v <<= 1
        if v & 0b100000:
            v ^= prim
    for i in range(31, 62):
        exp[i] = exp[i - 31]
    return exp, log


def gf_mul(a, b, exp, log):
    if a == 0 or b == 0:
        return 0
    return exp[log[a] + log[b]]


def minimal_poly(i, exp, log):
    coset = sorted({(i * 2 ** j) % 31 for j in range(5)})
    poly = [1]  # coefficients, lowest degree first, in GF(32)
    for c in coset:
        root = exp[c]
        new = [0] * (len(poly) + 1)
        for d, a in enumerate(poly):
            new[d + 1] ^= a
            new[d] ^= gf_mul(a, root, exp, log)
        poly = new
    assert all(a in (0, 1) for a in poly)
    return sum(a << d for d, a in enumerate(poly))


def gf2_polymul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def gf2_polymod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def bch_generator():
    exp, log = gf32_tables()
    g = 1
    for i in (1, 3, 5):
        g = gf2_polymul(g, minimal_poly(i, exp, log))
    return g


def popcount64(x):
    x = x.astype(np.uint64)
    c = np.zeros(x.shape, dtype=np.int64)
    for s in range(0, 64, 8):
        c += BYTE_POP[((x >> np.uint64(s)) & np.uint64(0xFF)).astype(np.int64)]
    return c


BYTE_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.int64)


def byte_tables(col_values, nbits):
    """Linear map GF(2)^nbits -> ints given image of each unit vector."""
    nbytes = (nbits + 7) // 8
    tabs = np.zeros((nbytes, 256), dtype=np.int64)
    for b in range(nbytes):
        for v in range(256):
            acc = 0
            for j in range(8):
                i = 8 * b + j
                if (v >> j) & 1 and i < nbits:
                    acc ^= col_values[i]
            tabs[b, v] = acc
    return tabs


def apply_linear(tabs, x):
    x = np.asarray(x, dtype=np.int64)
    out = np.zeros(x.shape, dtype=np.int64)
    for b in range(tabs.shape[0]):
        out ^= tabs[b][(x >> (8 * b)) & 0xFF]
    return out


class BCHRule:
    def __init__(self):
        g = bch_generator()
        assert g.bit_length() - 1 == NPAR, "deg g != 15"
        self.g = g
        self.syn_tabs = byte_tables([gf2_polymod(1 << i, g) for i in range(N)], N)
        # systematic encoding tables: message bit j -> codeword
        enc_cols = []
        for j in range(KMSG):
            shifted = 1 << (j + NPAR)
            enc_cols.append(shifted ^ gf2_polymod(shifted, g))
        self.enc_tabs = byte_tables(enc_cols, KMSG)
        allcw = apply_linear(self.enc_tabs, np.arange(1 << KMSG))
        assert np.all(apply_linear(self.syn_tabs, allcw) == 0)
        w = popcount64(allcw[1:])
        self.dmin = int(w.min())
        assert self.dmin == 7, f"dmin={self.dmin}"
        # coset leader table
        leader = np.full(1 << NPAR, -1, dtype=np.int64)
        leader_wt = np.full(1 << NPAR, -1, dtype=np.int64)
        wt = 0
        while (leader < 0).any():
            pats = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(N), wt)],
                            dtype=np.int64)
            s = apply_linear(self.syn_tabs, pats)
            _, first = np.unique(s, return_index=True)
            sf = s[first]
            new = leader[sf] < 0
            leader[sf[new]] = pats[first[new]]
            leader_wt[sf[new]] = wt
            wt += 1
        self.leader = leader
        self.covering_radius = int(leader_wt.max())
        self.n_agents = N

    def honest(self, rng, n):
        m = rng.integers(0, 1 << KMSG, size=n, dtype=np.int64)
        return apply_linear(self.enc_tabs, m), m

    def outcome(self, r):
        s = apply_linear(self.syn_tabs, r)
        cw = r ^ self.leader[s]
        return cw >> NPAR


class ParityRule:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        while True:
            P = rng.integers(0, 2, size=(KMSG, N))
            if gf2_rank(P) == KMSG:
                break
        self.P = P
        cols = [int(sum(int(P[b, i]) << b for b in range(KMSG))) for i in range(N)]
        self.tabs = byte_tables(cols, N)
        self.n_agents = N
        self.zero_cols = int(sum(c == 0 for c in cols))

    def honest(self, rng, n):
        r0 = rng.integers(0, 1 << N, size=n, dtype=np.int64)
        return r0, self.outcome(r0)

    def outcome(self, r):
        return apply_linear(self.tabs, r)


class DirectRule:
    def __init__(self):
        self.n_agents = KMSG

    def honest(self, rng, n):
        m = rng.integers(0, 1 << KMSG, size=n, dtype=np.int64)
        return m.copy(), m

    def outcome(self, r):
        return np.asarray(r, dtype=np.int64)


def gf2_rank(M):
    M = M.copy() % 2
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = [i for i in range(r, rows) if M[i, c]]
        if not piv:
            continue
        M[[r, piv[0]]] = M[[piv[0], r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
        if r == rows:
            break
    return r


def coalition_search(rule, rng, k):
    """Return number of the N_COAL coalitions that can change the outcome."""
    honest, truth = rule.honest(rng, N_COAL)
    assert np.all(rule.outcome(honest) == truth)
    pos = np.array([rng.choice(rule.n_agents, size=k, replace=False) for _ in range(N_COAL)])
    idx = np.arange(1 << k, dtype=np.int64)
    bits = (idx[:, None] >> np.arange(k)) & 1  # (2^k, k)
    E = (bits[None, :, :] << pos[:, None, :]).sum(axis=2)  # (N_COAL, 2^k) flip patterns
    R = honest[:, None] ^ E  # all 2^k report vectors on coalition positions
    out = rule.outcome(R)
    changed = (out != truth[:, None]).any(axis=1)
    return int(changed.sum())


def main():
    att_path = os.path.join(HERE, "attempts.json")
    attempts = 1
    if os.path.exists(att_path):
        attempts = json.load(open(att_path))["attempts"] + 1
    json.dump({"attempts": attempts}, open(att_path, "w"))

    t0 = time.process_time()
    bch = BCHRule()
    t_setup = time.process_time() - t0
    control_rule = ParityRule(CONTROL_MATRIX_SEED)

    rows_path = os.path.join(HERE, "rows.jsonl")
    common = {"n": N, "msg_bits": KMSG, "ks": KS, "n_coalitions": N_COAL,
              "bch_generator_poly": bin(bch.g), "bch_dmin": bch.dmin,
              "bch_covering_radius": bch.covering_radius, "attempt": attempts}
    with open(rows_path, "w") as f:
        for arm in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL", "CHEAT"]:
            for seed in SEEDS:
                ts = time.process_time()
                row = {"arm": arm, "seed": seed, **common}
                if arm == "CHEAT":
                    counts = {str(k): (0 if k <= 3 else N_COAL) for k in KS}
                    row["rule"] = "none (success injected into observable)"
                else:
                    if arm == "TREATMENT":
                        rule = bch
                        row["rule"] = "BCH(31,16,7) nearest-codeword decode"
                    elif arm == "CONTROL":
                        rule = control_rule
                        row["rule"] = "random-parity fixed matrix"
                        row["matrix_seed"] = CONTROL_MATRIX_SEED
                        row["zero_columns"] = rule.zero_cols
                    elif arm == "NULL_TWIN":
                        rule = ParityRule(2000 + seed)
                        row["rule"] = "random-parity per-seed matrix"
                        row["matrix_seed"] = 2000 + seed
                        row["zero_columns"] = rule.zero_cols
                    else:
                        rule = DirectRule()
                        row["rule"] = "direct: 16 agents, outcome = reports (d=1)"
                        row["n_agents_arm"] = KMSG
                    rng = np.random.default_rng([ARM_CODE[arm], seed])
                    counts = {str(k): coalition_search(rule, rng, k) for k in KS}
                row["rng_seed"] = [ARM_CODE[arm], seed]
                row["success_counts"] = counts
                row["cpu_seconds"] = time.process_time() - ts
                f.write(json.dumps(row) + "\n")
                f.flush()
    total = time.process_time() - t0
    json.dump({"setup_cpu_seconds": t_setup, "total_cpu_seconds": total,
               "core_minutes": total / 60.0, "attempts": attempts,
               "bch_covering_radius": bch.covering_radius},
              open(os.path.join(HERE, "run_meta.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
