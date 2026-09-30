"""HT-321a8fd8e0 / W1 Pass 4: R, ORIG, ALT attacks. See NOTES.md.

Writes rows.jsonl (one row per attack x arm x seed, flushed per row),
run_meta.json and attempts.json, all in this pass4/ directory only.
Round-1 code from ../world.py is copied (not imported) to avoid writing
__pycache__ outside pass4/.
"""
import itertools
import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
N = 31
KS = list(range(1, 9))
N_COAL = 200
SEEDS = list(range(100, 120))
CONTROL_MATRIX_SEED = 1001
ATTACK_CODE = {"R": 1, "ORIG": 2, "ALT": 3}
ARM_CODE = {"TREATMENT": 1, "CONTROL": 2, "NULL_TWIN": 3, "POSITIVE_CONTROL": 4, "CHEAT": 5,
            "BCH_D3": 6, "BCH_D5": 7, "CHEAT_D3": 8, "CHEAT_D5": 9,
            "CODE_BCH16": 10, "MAJ31": 11, "MAJ_R3_48": 12, "CHEAT_ALT": 13,
            "EXH_CODE_BCH16": 14, "EXH_MAJ31": 15}

BYTE_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.int64)


# ---------------- GF(32) and BCH(31, 31-deg g) (copied from ../world.py, generalised in t) -----
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
    poly = [1]
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


def bch_generator(t):
    """lcm of minimal polys of alpha^1..alpha^(2t) (odd i suffice over GF(2))."""
    exp, log = gf32_tables()
    g = 1
    seen = set()
    for i in range(1, 2 * t + 1, 2):
        mp = minimal_poly(i, exp, log)
        if mp not in seen:
            seen.add(mp)
            g = gf2_polymul(g, mp)
    return g


def popcount64(x):
    x = np.asarray(x).astype(np.uint64)
    c = np.zeros(x.shape, dtype=np.int64)
    for s in range(0, 64, 8):
        c += BYTE_POP[((x >> np.uint64(s)) & np.uint64(0xFF)).astype(np.int64)]
    return c


def byte_tables(col_values, nbits):
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
    def __init__(self, t, designed_d):
        g = bch_generator(t)
        self.g = g
        self.npar = g.bit_length() - 1
        self.kmsg = N - self.npar
        self.syn_tabs = byte_tables([gf2_polymod(1 << i, g) for i in range(N)], N)
        enc_cols = []
        for j in range(self.kmsg):
            shifted = 1 << (j + self.npar)
            enc_cols.append(shifted ^ gf2_polymod(shifted, g))
        self.enc_tabs = byte_tables(enc_cols, self.kmsg)
        # coset-leader table (enumeration order as round 1) + verified dmin
        nsyn = 1 << self.npar
        leader = np.full(nsyn, -1, dtype=np.int64)
        leader_wt = np.full(nsyn, -1, dtype=np.int64)
        dmin = None
        wt = 0
        while (leader < 0).any() or dmin is None:
            pats = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(N), wt)],
                            dtype=np.int64)
            s = apply_linear(self.syn_tabs, pats)
            if wt > 0 and dmin is None and (s == 0).any():
                dmin = wt
            if (leader < 0).any():
                _, first = np.unique(s, return_index=True)
                sf = s[first]
                new = leader[sf] < 0
                leader[sf[new]] = pats[first[new]]
                leader_wt[sf[new]] = wt
            wt += 1
            if wt > 12:
                raise RuntimeError("enumeration runaway")
        self.dmin = int(dmin)
        assert self.dmin == designed_d, f"dmin={self.dmin} != designed {designed_d}"
        self.leader = leader
        self.covering_radius = int(leader_wt.max())
        self.n_agents = N
        self.name = f"BCH(31,{self.kmsg},{self.dmin}) nearest-codeword decode"

    def honest(self, rng, n):
        m = rng.integers(0, 1 << self.kmsg, size=n, dtype=np.int64)
        cw = apply_linear(self.enc_tabs, m)
        return cw, m

    def outcome(self, r):
        s = apply_linear(self.syn_tabs, r)
        cw = r ^ self.leader[s]
        return cw >> self.npar


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


class ParityRule:
    KMSG = 16

    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        while True:
            P = rng.integers(0, 2, size=(self.KMSG, N))
            if gf2_rank(P) == self.KMSG:
                break
        self.P = P
        cols = [int(sum(int(P[b, i]) << b for b in range(self.KMSG))) for i in range(N)]
        self.tabs = byte_tables(cols, N)
        self.n_agents = N
        self.zero_cols = int(sum(c == 0 for c in cols))

    def honest(self, rng, n):
        r0 = rng.integers(0, 1 << N, size=n, dtype=np.int64)
        return r0, self.outcome(r0)

    def outcome(self, r):
        return apply_linear(self.tabs, r)


class DirectRule:
    n_agents = 16
    name = "direct: 16 agents, outcome = reports (d=1)"

    def honest(self, rng, n):
        m = rng.integers(0, 1 << 16, size=n, dtype=np.int64)
        return m.copy(), m

    def outcome(self, r):
        return np.asarray(r, dtype=np.int64)


class MajorityRule:
    """n_agents agents, agent i holds a copy of outcome bit (i mod 16).
    Outcome bit = strict majority of its copies; ties -> 0 (NOTES.md)."""
    KMSG = 16

    def __init__(self, n_agents):
        self.n_agents = n_agents
        self.masks = []
        self.copies = []
        for b in range(self.KMSG):
            idx = [i for i in range(n_agents) if i % self.KMSG == b]
            self.masks.append(sum(1 << i for i in idx))
            self.copies.append(len(idx))
        self.name = f"majority/repetition: {n_agents} agents, copies per bit {self.copies}, tie->0"

    def honest(self, rng, n):
        m = rng.integers(0, 1 << self.KMSG, size=n, dtype=np.int64)
        r = np.zeros(n, dtype=np.int64)
        for i in range(self.n_agents):
            r |= ((m >> (i % self.KMSG)) & 1) << i
        return r, m

    def outcome(self, r):
        r = np.asarray(r, dtype=np.int64)
        out = np.zeros(r.shape, dtype=np.int64)
        for b in range(self.KMSG):
            ones = popcount64(r & self.masks[b])
            out |= ((2 * ones > self.copies[b]).astype(np.int64)) << b
        return out


def search_positions(rule, rng, pos):
    """pos: (n_coal, k) agent indices. Returns bool array: coalition can change outcome."""
    n_coal, k = pos.shape
    honest, truth = rule.honest(rng, n_coal)
    assert np.all(rule.outcome(honest) == truth)
    idx = np.arange(1 << k, dtype=np.int64)
    bits = (idx[:, None] >> np.arange(k)) & 1
    E = (bits[None, :, :] << pos[:, None, :]).sum(axis=2)
    R = honest[:, None] ^ E
    out = rule.outcome(R)
    return (out != truth[:, None]).any(axis=1)


def coalition_search(rule, rng, k):
    pos = np.array([rng.choice(rule.n_agents, size=k, replace=False) for _ in range(N_COAL)])
    return int(search_positions(rule, rng, pos).sum())


def main():
    att_path = os.path.join(HERE, "attempts.json")
    attempts = 1
    if os.path.exists(att_path):
        attempts = json.load(open(att_path))["attempts"] + 1
    json.dump({"attempts": attempts}, open(att_path, "w"))

    t0 = time.process_time()
    bch16 = BCHRule(3, 7)
    bch21 = BCHRule(2, 5)
    bch26 = BCHRule(1, 3)
    control_rule = ParityRule(CONTROL_MATRIX_SEED)
    direct = DirectRule()
    maj31 = MajorityRule(31)
    maj48 = MajorityRule(48)
    t_setup = time.process_time() - t0

    code_meta = {r.name: {"generator_poly": bin(r.g), "dmin": r.dmin, "covering_radius": r.covering_radius,
                          "t": (r.dmin - 1) // 2}
                 for r in (bch16, bch21, bch26)}
    common = {"n": N, "ks": KS, "n_coalitions": N_COAL, "attempt": attempts,
              "prompt_sha256": "77ff9e2d04f990b18d049dcf86bf70e10246b171cb4445cc8b34bebbcecece6e"}

    def injected(tcut):
        return {str(k): (0 if k <= tcut else N_COAL) for k in KS}

    plan = [
        ("R", "TREATMENT", lambda s: bch16),
        ("R", "CONTROL", lambda s: control_rule),
        ("R", "NULL_TWIN", lambda s: ParityRule(2000 + s)),
        ("R", "POSITIVE_CONTROL", lambda s: direct),
        ("R", "CHEAT", 3),
        ("ORIG", "BCH_D3", lambda s: bch26),
        ("ORIG", "BCH_D5", lambda s: bch21),
        ("ORIG", "POSITIVE_CONTROL", lambda s: direct),
        ("ORIG", "CHEAT_D3", 1),
        ("ORIG", "CHEAT_D5", 2),
        ("ALT", "CODE_BCH16", lambda s: bch16),
        ("ALT", "MAJ31", lambda s: maj31),
        ("ALT", "MAJ_R3_48", lambda s: maj48),
        ("ALT", "POSITIVE_CONTROL", lambda s: direct),
        ("ALT", "CHEAT_ALT", 3),
    ]

    rows_path = os.path.join(HERE, "rows.jsonl")
    with open(rows_path, "w") as f:
        for attack, arm, spec in plan:
            for seed in SEEDS:
                ts = time.process_time()
                row = {"attack": attack, "arm": arm, "seed": seed, **common}
                if isinstance(spec, int):
                    row["rule"] = f"none (injected: 0 for k<={spec}, {N_COAL} for k>{spec})"
                    row["injected_cut"] = spec
                    counts = injected(spec)
                else:
                    rule = spec(seed)
                    row["rule"] = getattr(rule, "name", None) or (
                        "random-parity fixed matrix" if arm == "CONTROL" else "random-parity per-seed matrix")
                    row["n_agents_arm"] = rule.n_agents
                    if isinstance(rule, BCHRule):
                        row["code"] = code_meta[rule.name]
                    if isinstance(rule, ParityRule):
                        row["matrix_seed"] = CONTROL_MATRIX_SEED if arm == "CONTROL" else 2000 + seed
                        row["zero_columns"] = rule.zero_cols
                    if isinstance(rule, MajorityRule):
                        row["copies_per_bit"] = rule.copies
                        row["tie_rule"] = "tie -> 0"
                    rng_seed = [ATTACK_CODE[attack], ARM_CODE[arm], seed]
                    row["rng_seed"] = rng_seed
                    rng = np.random.default_rng(rng_seed)
                    counts = {str(k): coalition_search(rule, rng, k) for k in KS}
                row["success_counts"] = counts
                row["cpu_seconds"] = time.process_time() - ts
                f.write(json.dumps(row) + "\n")
                f.flush()
        # auxiliary exhaustive sweep (ALT): all C(31,k) coalitions, k = 1..3
        for arm, rule in (("EXH_CODE_BCH16", bch16), ("EXH_MAJ31", maj31)):
            ts = time.process_time()
            rng_seed = [ATTACK_CODE["ALT"], ARM_CODE[arm], 100]
            rng = np.random.default_rng(rng_seed)
            counts, totals = {}, {}
            for k in (1, 2, 3):
                pos = np.array(list(itertools.combinations(range(rule.n_agents), k)), dtype=np.int64)
                counts[str(k)] = int(search_positions(rule, rng, pos).sum())
                totals[str(k)] = int(len(pos))
            row = {"attack": "ALT", "arm": arm, "seed": 100, **common, "rule": rule.name,
                   "n_agents_arm": rule.n_agents, "exhaustive": True, "ks": [1, 2, 3],
                   "n_coalitions_by_k": totals, "rng_seed": rng_seed,
                   "success_counts": counts, "cpu_seconds": time.process_time() - ts}
            f.write(json.dumps(row) + "\n")
            f.flush()

    total = time.process_time() - t0
    json.dump({"setup_cpu_seconds": t_setup, "total_cpu_seconds": total,
               "core_minutes": total / 60.0, "attempts": attempts, "codes": code_meta},
              open(os.path.join(HERE, "run_meta.json"), "w"), indent=1)
    print(f"done: {total:.2f} CPU s, attempt {attempts}")


if __name__ == "__main__":
    main()
