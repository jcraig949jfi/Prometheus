"""Tyche v2 worlds: difficulty classes with HIDDEN precursor variables.

Every world is: observed inputs X (T x 6), a set of hidden precursor
variables P_i = f_i(X) (each a named primitive: delay, window majority,
accumulator state, window parity), and a combiner Y = g(P_1..P_k). The
answer key (precursors + combiner) is used ONLY for oracles, certificates
and the natural-history tracer; evolution sees X and the ruler only.

Classes (directive v2):
  D1 SMOOTH     majority of 3 delayed bits (each precursor informative)
  D2 DECEPTIVE  xor of 2 delays + an observed decoy channel agreeing 65%
  D3 ORDER2     xor of 2 delays
  D4a ORDER3    parity of 3 delays
  D4b ORDER3M   (sum of 3 accumulator-mod-3 shares) mod 3 (secret sharing)
  D4c ORDER4    parity of 4 delays
  D5d DONOR     Y = P (a 5-window majority) -- P rewarded directly here
  D5t EXAPT     Y = P xor Q, P as in the donor (useless alone here)
  D6 REPR       Y = [S(t) == S(t-d)], S = accumulator mod 3 of one channel
  D7 GENERATED  a random non-affine, first-order-resilient boolean function
                of 4 derived bits of mixed type (search, hidden)
  N  twins (Y from an independent hidden copy of X) and keyed PRF
Regime worlds (Block R) carry two laws; the run switches from L1 to L2 at
an unannounced generation. Both phases share X (same uid).
"""

from __future__ import annotations

import hashlib
import itertools
import json

import numpy as np

from .. import worlds as W0
from ..lens import NIN

T = W0.T
D = 6


# ------------------------------------------------------------ primitives

def _lag(x, k):
    y = np.zeros_like(x)
    if k == 0:
        return x.copy()
    y[k:] = x[:-k]
    return y


def prim(p, X):
    x = X[:, p["ch"]].astype(np.int64)
    t = p["type"]
    if t == "delay":
        return _lag(x, p["lag"])
    if t == "wmaj":
        c = np.concatenate([[0], np.cumsum(x)])
        s = c[1:] - np.concatenate([np.zeros(p["w"], dtype=np.int64), c[1:-p["w"]]])
        return _lag((s >= p["w"] // 2 + 1).astype(np.int64), p["lag"])
    if t == "acc":
        return _lag(np.cumsum(x) % p["m"], p["lag"])
    if t == "wpar":
        a = np.cumsum(x) % 2
        return _lag((a - _lag(a, p["w"])) % 2, p["lag"])
    if t == "fsm":
        # same semantics as the lens op `fsm` (state after consuming x_t)
        tab = np.asarray(p["table"], dtype=np.int64).reshape(3, 2)
        y = np.empty(len(x), dtype=np.int64)
        st = 0
        for i, b in enumerate((x > 0).astype(np.int64)):
            st = tab[st, b]
            y[i] = st
        return _lag(y, p["lag"])
    raise ValueError(t)


def fsm_table(rng):
    """3-state, 2-input, NON-GROUP automaton (some input merges two states),
    history-dependent, every state visited >= 12% on a long iid input."""
    x = (rng.random(20000) < 0.5).astype(np.int64)
    while True:
        tab = [int(v) for v in rng.integers(0, 3, 6)]
        t = np.asarray(tab).reshape(3, 2)
        if all(len(set(t[:, b])) == 3 for b in (0, 1)):
            continue  # both inputs permute states -> group automaton
        y = prim({"type": "fsm", "ch": 0, "table": tab, "lag": 0}, x[:, None])
        occ = np.bincount(y, minlength=3) / len(y)
        dep = max(np.bincount(y[x == b], minlength=3).max() / max(1, (x == b).sum()) for b in (0, 1))
        if occ.min() > 0.12 and dep < 0.75:
            return tab


def combine(law, P):
    k = law["comb"]
    if k == "majority":
        return (np.sum(P, 0) >= (len(P) // 2 + 1)).astype(np.int64)
    if k == "xor":
        y = np.zeros_like(P[0])
        for p in P:
            y ^= p % 2
        return y
    if k == "summod":
        return np.sum(P, 0) % law["m"]
    if k == "eq":
        return (P[0] == P[1]).astype(np.int64)
    if k == "ident":
        return P[0].copy()
    if k == "table":
        idx = np.zeros_like(P[0])
        for p in P:
            idx = idx * 2 + p
        return np.asarray(law["table"], dtype=np.int64)[idx]
    raise ValueError(k)


def precursors(law, X):
    return [prim(p, X) for p in law["prec"]]


def _inputs(d, rng):
    return (rng.random((T, d)) < 0.5).astype(np.int64)


def generate(spec, seed):
    rng = np.random.default_rng([int(seed), int(spec["uid"]), 2])
    X = _inputs(D, rng)
    law = spec["law"]
    if law["comb"] == "prf":
        return X, W0._law({"kind": "prf", "key": law["key"], "w": 24}, X, rng)
    src = _inputs(D, rng) if spec["kind"] == "tsd" else X
    Y = combine(law, precursors(law, src))
    if law.get("decoy"):
        dc = law["decoy"]
        keep = rng.random(T) < dc["agree"]
        X[:, dc["ch"]] = np.where(keep, Y, rng.integers(0, 2, T))
    return X, Y.astype(np.int64)


# ------------------------------------------------------------ oracles

def _compile_prim(p, ins):
    """Append instructions computing primitive p; return its register."""
    N = NIN

    def emit(op, args, par):
        ins.append([op, args, par])
        return N + len(ins) - 1

    t = p["type"]
    if t == "delay":
        return emit("delay", [p["ch"]], p["lag"]) if p["lag"] else emit("sign", [p["ch"]], None)
    if t == "wmaj":
        r = emit("wsum", [p["ch"]], p["w"])
        r = emit("thresh", [r], float(p["w"] // 2))
        return emit("delay", [r], p["lag"]) if p["lag"] else r
    if t == "acc":
        r = emit("accmod", [p["ch"]], p["m"])
        return emit("delay", [r], p["lag"]) if p["lag"] else r
    if t == "wpar":
        a = emit("accmod", [p["ch"]], 2)
        b = emit("delay", [a], p["w"])
        r = emit("xor", [a, b], None)
        return emit("delay", [r], p["lag"]) if p["lag"] else r
    if t == "fsm":
        r = emit("fsm", [p["ch"]], [3, list(p["table"])])
        return emit("delay", [r], p["lag"]) if p["lag"] else r
    raise ValueError(t)


def oracle(law):
    """Answer-key genome (calibration only). Table laws expose the 4
    precursor bits (an organism can learn a 4-bit table); PRF -> None."""
    if law["comb"] == "prf":
        return None
    ins = []
    regs = [_compile_prim(p, ins) for p in law["prec"]]
    k = law["comb"]
    if k in ("table",):
        return {"ins": ins, "out": regs}
    if k == "ident":
        return {"ins": ins, "out": [regs[0]]}
    r = regs[0]
    for q in regs[1:]:
        op = {"xor": "xor", "majority": "add", "summod": "add", "eq": "eq"}[k]
        ins.append([op, [r, q], None])
        r = NIN + len(ins) - 1
    if k == "majority":
        ins.append(["thresh", [r], float(len(regs) // 2)])
        r = NIN + len(ins) - 1
    if k == "summod":
        ins.append(["fold", [r], law["m"]])
        r = NIN + len(ins) - 1
    return {"ins": ins, "out": [r]}


# ------------------------------------------------------------ generated class

def _resilient_tables(rng, n=4, want=1):
    """Random balanced, first-order-resilient (every single input bit
    carries zero information), non-affine truth tables on n bits."""
    out = []
    rows = list(itertools.product([0, 1], repeat=n))
    affine = set()
    for m in itertools.product([0, 1], repeat=n):
        for c in (0, 1):
            affine.add(tuple((sum(mi * ri for mi, ri in zip(m, r)) + c) % 2 for r in rows))
    while len(out) < want:
        tab = np.zeros(2 ** n, dtype=np.int64)
        tab[rng.choice(2 ** n, size=2 ** (n - 1), replace=False)] = 1
        t = tuple(int(v) for v in tab)
        if t in affine:
            continue
        ok = all(sum(t[j] for j, r in enumerate(rows) if r[i] == 1) == 2 ** (n - 2) for i in range(n))
        if ok:
            out.append(list(t))
    return out


def lowest_informative_order(table, n=4):
    """Smallest subset size s such that some s-subset of the (independent,
    uniform) input bits carries information about the output (exact)."""
    rows = list(itertools.product([0, 1], repeat=n))
    for s in range(1, n + 1):
        for sub in itertools.combinations(range(n), s):
            for vals in itertools.product([0, 1], repeat=s):
                sel = [table[j] for j, r in enumerate(rows) if all(r[i] == v for i, v in zip(sub, vals))]
                if abs(np.mean(sel) - 0.5) > 1e-12:
                    return s
    return None


# ------------------------------------------------------------ world sets

def _rand_prim(rng, kind, ch):
    if kind == "delay":
        return {"type": "delay", "ch": ch, "lag": int(rng.integers(2, 13))}
    if kind == "wmaj":
        return {"type": "wmaj", "ch": ch, "lag": int(rng.integers(1, 6)), "w": 5}
    if kind == "acc":
        return {"type": "acc", "ch": ch, "m": 2, "lag": int(rng.integers(0, 8))}
    if kind == "wpar":
        return {"type": "wpar", "ch": ch, "lag": int(rng.integers(0, 6)), "w": int(rng.integers(2, 5))}
    raise ValueError(kind)


def class_law(cls, rng):
    ch = [int(c) for c in rng.permutation(D)]
    dl = lambda c: {"type": "delay", "ch": c, "lag": int(rng.integers(2, 13))}
    if cls == "D1":
        return {"comb": "majority", "prec": [dl(ch[0]), dl(ch[1]), dl(ch[2])]}
    if cls == "D2":
        return {"comb": "xor", "prec": [dl(ch[0]), dl(ch[1])], "decoy": {"ch": ch[2], "agree": 0.65}}
    if cls == "D3":
        return {"comb": "xor", "prec": [dl(ch[0]), dl(ch[1])]}
    if cls == "D4a":
        return {"comb": "xor", "prec": [dl(ch[0]), dl(ch[1]), dl(ch[2])]}
    if cls == "D4b":
        return {"comb": "summod", "m": 3,
                "prec": [{"type": "acc", "ch": ch[i], "m": 3, "lag": int(rng.integers(0, 9))} for i in range(3)]}
    if cls == "D4c":
        return {"comb": "xor", "prec": [dl(ch[i]) for i in range(4)]}
    if cls == "D6":
        tab = fsm_table(rng)
        return {"comb": "eq", "prec": [{"type": "fsm", "ch": ch[0], "table": tab, "lag": 0},
                                       {"type": "fsm", "ch": ch[0], "table": tab, "lag": int(rng.integers(4, 10))}]}
    if cls == "D7":
        kinds = [str(k) for k in rng.choice(["delay", "wmaj", "acc", "wpar"], size=4)]
        tab = _resilient_tables(rng)[0]
        return {"comb": "table", "table": tab, "prec": [_rand_prim(rng, k, ch[i]) for i, k in enumerate(kinds)],
                "lowest_order": lowest_informative_order(tab)}
    raise ValueError(cls)


def exapt_pair(rng):
    ch = [int(c) for c in rng.permutation(D)]
    P = {"type": "wmaj", "ch": ch[0], "lag": int(rng.integers(1, 5)), "w": 5}
    Q = {"type": "delay", "ch": ch[1], "lag": int(rng.integers(3, 12))}
    return {"comb": "ident", "prec": [P]}, {"comb": "xor", "prec": [P, Q]}


STATIC = ["D1", "D2", "D3", "D4a", "D4b", "D4c", "D6", "D7a", "D7b", "D7c"]


def build_static(master_seed, variant=0):
    """One copy of every static class (+ donor/target pair, twins, PRF).
    variant > 0 gives a RELATED copy of the same classes with new params."""
    rng = np.random.default_rng([master_seed, variant])
    W = []

    def add(wid, cls, kind, law, **kw):
        W.append({"id": wid, "cls": cls, "kind": kind, "law": law, "uid": 1000 * (variant + 1) + len(W), **kw})

    for c in STATIC:
        base = "D7" if c.startswith("D7") else c
        add(f"{c}_v{variant}", base, "planted", class_law(base, rng))
    donor, target = exapt_pair(rng)
    add(f"D5d_v{variant}", "D5d", "planted", donor)
    add(f"D5t_v{variant}", "D5t", "planted", target, donor=f"D5d_v{variant}")
    for c in ("D3", "D4a", "D6", "D7a"):
        src = next(w for w in W if w["id"] == f"{c}_v{variant}")
        add(f"N_{c}_v{variant}", "N", "tsd", src["law"], twin_of=src["id"])
    add(f"N_prf_v{variant}", "N", "prf", {"comb": "prf", "key": f"tyche-v2-prf-{variant}"})
    return W


REGIMES = {
    "R1": ("D1", "D3", "shared_none"),
    "R2": ("D1", "D4a", "shared_none"),
    "R3": ("D3", "D3", "shared_one"),
    "R4": ("D3", "D3", "shared_none"),
}


def build_regime(master_seed, variant=0):
    """Regime worlds: L1 for generations < switch, L2 after. Laws are
    drawn so L2's precursors are zero-marginal under L1 (disjoint channels
    except R3, which reuses one L1 precursor)."""
    rng = np.random.default_rng([master_seed, 777, variant])
    W = []
    for i, (rid, (c1, c2, share)) in enumerate(sorted(REGIMES.items())):
        L1 = class_law(c1, rng)
        used = {p["ch"] for p in L1["prec"]}
        free = [c for c in range(D) if c not in used]
        if share == "shared_one":
            A = L1["prec"][0]
            B = {"type": "delay", "ch": free[0], "lag": int(rng.integers(2, 13))}
            L2 = {"comb": "xor", "prec": [A, B]}
        else:
            k = 3 if c2 == "D4a" else 2
            fr = [int(c) for c in rng.permutation(free)]
            if len(fr) < k:
                fr = [int(c) for c in rng.permutation(D)]
            L2 = {"comb": "xor", "prec": [{"type": "delay", "ch": fr[j], "lag": int(rng.integers(2, 13))}
                                          for j in range(k)]}
        uid = 5000 + 100 * variant + i
        W.append({"id": f"{rid}_v{variant}", "cls": f"REG_{c1}->{c2}_{share}", "kind": "planted",
                  "law": L1, "law2": L2, "uid": uid})
    return W


def phase_spec(spec, phase):
    """The spec a run evaluates for regime phase 1 or 2 (same X)."""
    if "law2" not in spec or phase == 1:
        return dict(spec, id=spec["id"] + ("@L1" if "law2" in spec else ""))
    return dict(spec, law=spec["law2"], id=spec["id"] + "@L2")


def worlds_hash(W):
    return hashlib.sha256(json.dumps(W, sort_keys=True).encode()).hexdigest()
