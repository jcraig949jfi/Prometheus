"""WORLD: observation producers for Tyche v0.

A world is a JSON spec plus generate(spec, seed) -> (X, Y):
  X  (T x d) observations the lenses see (causal stream),
  Y  (T,)    int consequence channel, NEVER passed to a lens; rulers use it.
Law parameters are fixed in the spec; `seed` draws only the input noise
(and restart states), so a new seed is a replication of the same law.

Kinds (the answer key lives in the spec; nothing downstream reads it except
the report and the audits):
  planted     hidden composition reachable in the lens grammar (positive
              control); every planted law uses only delayed inputs, so the
              raw current observation carries no information
  tsd         TARGET_STRUCTURE_DESTROYED twin of a planted world: identical
              observation process, Y made by the same law from an
              independent hidden copy of the inputs (same marginals, no link)
  prf         keyed SHA-256 bit of a 24-step window: nothing in the grammar
              should reach it (false-gradient check)
  known       raw observation already suffices (redundancy check)
  hec_alien   Hecate alien-lawful system (hecate/alien, ALIEN_LAWFUL class),
              partially observed; lawful, structure unknown to us
  hec_null    Hecate MATCHED_NOISE system: deterministic but compact
              structure destroyed (a dark world, not a negative control)
  adv         adversarial: decoy regularity, locally noisy / globally
              lawful, aliased high-period phase, sparse dependency
"""

from __future__ import annotations

import hashlib
import json

import numpy as np

T = 12100
SPLITS = {"train": (100, 3100), "val": (3100, 6100), "conf": (6100, 9100), "test": (9100, 12100)}


# ------------------------------------------------------------ input processes

def _inputs(proc, d, rng):
    kind = proc["kind"]
    if kind == "bern":
        return (rng.random((T, d)) < proc.get("p", 0.5)).astype(np.int64)
    if kind == "markov":
        X = np.empty((T, d), dtype=np.int64)
        X[0] = rng.integers(0, 2, d)
        flip = rng.random((T, d)) > proc["stay"]
        for t in range(1, T):
            X[t] = X[t - 1] ^ flip[t]
        return X
    if kind == "gauss":
        return rng.standard_normal((T, d))
    raise ValueError(kind)


def _lag(x, k):
    y = np.zeros_like(x)
    y[k:] = x[:-k] if k else x
    return y


def _fsm_run(x, table):
    tab = np.asarray(table).reshape(3, 2)
    y = np.empty(len(x), dtype=np.int64)
    s = 0
    for i, b in enumerate(x):
        s = tab[s, int(b)]
        y[i] = s
    return y


def _law(L, X, rng):
    k = L["kind"]
    if k == "xor2":
        return _lag(X[:, L["a"]], L["da"]) ^ _lag(X[:, L["b"]], L["db"])
    if k == "par3":
        return _lag(X[:, L["a"]], L["da"]) ^ _lag(X[:, L["b"]], L["db"]) ^ _lag(X[:, L["c"]], L["dc"])
    if k == "cmod":
        return np.cumsum(X[:, L["a"]]) % L["m"]
    if k == "wmaj":
        x = X[:, L["a"]]
        c = np.concatenate([[0], np.cumsum(x)])
        t = np.arange(T)
        hi = np.clip(t - L["lo"] + 1, 0, T)
        lo = np.clip(t - L["hi"], 0, T)
        return ((c[hi] - c[lo]) >= L["thr"]).astype(np.int64)
    if k == "gate":
        g = _lag(X[:, L["c"]], L["dc"])
        return np.where(g == 1, _lag(X[:, L["b"]], L["db"]), _lag(X[:, L["d"]], L["dd"]))
    if k == "psign":
        return (_lag(X[:, L["a"]], L["da"]) * _lag(X[:, L["b"]], L["db"]) > 0).astype(np.int64)
    if k == "fsm":
        return _fsm_run(X[:, L["a"]], L["table"])
    if k == "prf":
        key = L["key"].encode()
        W = L["w"]
        rows = X.astype(np.uint8)
        y = np.zeros(T, dtype=np.int64)
        for t in range(W, T):
            y[t] = hashlib.sha256(key + rows[t - W + 1:t + 1].tobytes()).digest()[0] & 1
        return y
    if k == "ident":
        return X[:, L["a"]].astype(np.int64)
    if k == "kand":
        return X[:, L["a"]] & X[:, L["b"]]
    if k == "kxor":
        return X[:, L["a"]] ^ X[:, L["b"]]
    if k == "ksum":
        return (X[:, L["a"]] + X[:, L["b"]] > 0).astype(np.int64)
    if k == "sparse":
        return (_lag(X[:, L["a"]], L["da"]) + _lag(X[:, L["b"]], L["da"]) > 0).astype(np.int64)
    raise ValueError(k)


# ------------------------------------------------------------ generation

def _hec_table(params):
    from hecate.alien import systems as S
    dims = S.dims_of(params)
    states = S.all_states(dims)
    nxt = np.array([S.index(S.step(params, s), dims) for s in states], dtype=np.int64)
    return dims, np.array(states, dtype=np.int64), nxt


_HEC_CACHE = {}


def generate(spec, seed):
    """(X, Y) for world `spec` under input seed `seed`."""
    rng = np.random.default_rng([int(seed), int(spec["uid"])])
    kind = spec["kind"]
    d = spec["d"]
    if kind in ("planted", "tsd", "prf", "known"):
        X = _inputs(spec["proc"], d, rng)
        if kind == "tsd":
            Xh = _inputs(spec["proc"], d, rng)  # independent hidden copy
            Y = _law(spec["law"], Xh, rng)
        else:
            Y = _law(spec["law"], X, rng)
        return X, np.asarray(Y, dtype=np.int64)
    if kind == "adv":
        L = spec["law"]
        if L["kind"] == "decoy":
            X = _inputs(spec["proc"], d, rng)
            Y = _lag(X[:, L["b"]], L["d"]) ^ _lag(X[:, L["c"]], L["d"])
            keep = rng.random(T) < L["agree"]
            X[:, L["e"]] = np.where(keep, Y, rng.integers(0, 2, T))
            return X, Y.astype(np.int64)
        if L["kind"] == "noisymaj":
            X = _inputs(spec["proc"], d, rng)
            clean = (rng.random(T) < 0.5).astype(np.int64)
            flips = (rng.random(T) < L["flip"]).astype(np.int64)
            X[:, L["a"]] = clean ^ flips
            c = np.concatenate([[0], np.cumsum(clean)])
            t = np.arange(T)
            lo = np.clip(t - L["w"] + 1, 0, T)
            Y = ((c[t + 1] - c[lo]) >= (L["w"] // 2 + 1)).astype(np.int64)
            return X, Y
        if L["kind"] == "alias":
            X = _inputs(spec["proc"], d, rng)
            off = int(rng.integers(0, L["period"]))
            phi = (np.arange(T) + off) % L["period"]
            flips = (rng.random(T) < L["flip"]).astype(np.int64)
            X[:, L["a"]] = ((phi % 3) == 0).astype(np.int64) ^ flips
            Y = (phi < L["cut"]).astype(np.int64)
            return X, Y
        if L["kind"] == "sparse":
            X = _inputs(spec["proc"], d, rng)
            return X, _law(L, X, rng)
        raise ValueError(L["kind"])
    if kind in ("hec_alien", "hec_null"):
        key = spec["sys_id"]
        if key not in _HEC_CACHE:
            _HEC_CACHE[key] = _hec_table(spec["params"])
        dims, states, nxt = _HEC_CACHE[key]
        n = len(states)
        idx = np.empty(T + 1, dtype=np.int64)
        restarts = rng.integers(0, n, size=T // spec["restart"] + 2)
        cur = restarts[0]
        for t in range(T + 1):
            if t % spec["restart"] == 0:
                cur = restarts[t // spec["restart"]]
            idx[t] = cur
            cur = nxt[cur]
        S = states[idx]
        X = np.delete(S[:T], spec["hidden"], axis=1)
        Y = S[1:T + 1, spec["target"]]
        return X, Y.astype(np.int64)
    raise ValueError(kind)


# ------------------------------------------------------------ world set v0

def _pick_hec(cls, family):
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "hecate" / "alien" / "data" / "answer_key.json"
    key = json.loads(p.read_text())
    ids = sorted(i for i, r in key.items()
                 if r.get("class") == cls and r.get("params", {}).get("family") == family)
    return ids[0], key[ids[0]]["params"]


def _fsm_table(rng):
    """3-state, 2-input table whose output is history-dependent and visits
    every state (checked on a long iid input)."""
    x = (rng.random(20000) < 0.5).astype(np.int64)
    while True:
        tab = [int(v) for v in rng.integers(0, 3, 6)]
        y = _fsm_run(x, tab)
        occ = np.bincount(y, minlength=3) / len(y)
        # history dependence: y not determined by the current input alone
        dep = max(np.bincount(y[x == b], minlength=3).max() / max(1, (x == b).sum()) for b in (0, 1))
        if occ.min() > 0.12 and dep < 0.75:
            return tab


def build_worlds(master_seed=20260930):
    rng = np.random.default_rng(master_seed)
    W = []

    def add(wid, role, kind, family, law_group, d, **kw):
        spec = {"id": wid, "role": role, "kind": kind, "family": family,
                "law_group": law_group, "d": d, "uid": len(W) + 1}
        spec.update(kw)
        W.append(spec)

    def ch(n, d=6):
        return [int(v) for v in rng.choice(d, size=n, replace=False)]

    bern = {"kind": "bern", "p": 0.5}
    gauss = {"kind": "gauss"}

    a, b = ch(2)
    P1 = {"kind": "xor2", "a": a, "b": b, "da": int(rng.integers(3, 8)), "db": int(rng.integers(8, 13))}
    P2 = {"kind": "cmod", "a": ch(1)[0], "m": 3}
    P3 = {"kind": "wmaj", "a": ch(1)[0], "lo": 4, "hi": 15, "thr": 7}
    c3 = ch(3)
    P4 = {"kind": "gate", "b": c3[0], "c": c3[1], "d": c3[2], "db": 3, "dc": 2, "dd": 6}
    a5, b5 = ch(2)
    P5 = {"kind": "psign", "a": a5, "b": b5, "da": 5, "db": 2}
    P6 = {"kind": "fsm", "a": ch(1)[0], "table": _fsm_table(rng)}
    c7 = ch(3)
    P7 = {"kind": "par3", "a": c7[0], "b": c7[1], "c": c7[2], "da": 2, "db": 5, "dc": 9}

    add("P1_xor2", "train", "planted", "planted", "P1", 6, proc=bern, law=P1)
    add("P2_cmod", "train", "planted", "planted", "P2", 6, proc=bern, law=P2)
    add("P3_wmaj", "train", "planted", "planted", "P3", 6, proc=bern, law=P3)
    add("P4_gate", "train", "planted", "planted", "P4", 6, proc=bern, law=P4)
    add("P5_psign", "train", "planted", "planted", "P5", 6, proc=gauss, law=P5)
    add("P6_fsm", "train", "planted", "planted", "P6", 6, proc=bern, law=P6)
    add("TSD1_xor2", "train", "tsd", "tsd", "P1", 6, proc=bern, law=P1)
    add("TSD2_cmod", "train", "tsd", "tsd", "P2", 6, proc=bern, law=P2)
    add("TSD3_wmaj", "train", "tsd", "tsd", "P3", 6, proc=bern, law=P3)
    add("TSD4_gate", "train", "tsd", "tsd", "P4", 6, proc=bern, law=P4)
    add("PRF1", "train", "prf", "prf", "PRF", 6, proc=bern, law={"kind": "prf", "key": "tyche-prf-1", "w": 24})
    add("PRF2", "train", "prf", "prf", "PRF", 6, proc=bern, law={"kind": "prf", "key": "tyche-prf-2", "w": 24})
    k1, k2 = ch(2)
    add("K1_ident", "train", "known", "known", "K1", 6, proc=bern, law={"kind": "ident", "a": k1})
    add("K2_and", "train", "known", "known", "K2", 6, proc=bern, law={"kind": "kand", "a": k1, "b": k2})
    add("K3_sum", "train", "known", "known", "K3", 6, proc=gauss, law={"kind": "ksum", "a": k1, "b": k2})
    for fam in ("tab", "graph", "rewrite", "vm"):
        sid, params = _pick_hec("ALIEN_LAWFUL", fam)
        nd = len(_dims(params))
        add(f"HA_{fam}", "train", "hec_alien", "hec_alien", "HA_" + fam, nd - 1,
            sys_id=sid, params=params, hidden=nd - 1, target=0, restart=25)
    for fam in ("tab", "graph"):
        sid, params = _pick_hec("MATCHED_NOISE", fam)
        nd = len(_dims(params))
        add(f"HN_{fam}", "train", "hec_null", "hec_null", "HN_" + fam, nd - 1,
            sys_id=sid, params=params, hidden=nd - 1, target=0, restart=25)
    b_, c_, e_ = ch(3)
    add("ADV_decoy", "train", "adv", "adv", "A1", 6, proc=bern,
        law={"kind": "decoy", "b": b_, "c": c_, "e": e_, "d": 6, "agree": 0.65})
    add("ADV_noisymaj", "train", "adv", "adv", "A2", 6, proc=bern,
        law={"kind": "noisymaj", "a": ch(1)[0], "w": 21, "flip": 0.3})
    add("ADV_alias", "train", "adv", "adv", "A3", 6, proc=bern,
        law={"kind": "alias", "a": ch(1)[0], "period": 11, "cut": 4, "flip": 0.2})

    # held-out (never used in selection or admission)
    add("H_P1sib_markov", "heldout", "planted", "planted", "P1", 6, proc={"kind": "markov", "stay": 0.7}, law=P1)
    add("H_P3sib_bern45", "heldout", "planted", "planted", "P3", 6, proc={"kind": "bern", "p": 0.45}, law=P3)
    add("H_P7_par3", "heldout", "planted", "planted", "P7", 6, proc=bern, law=P7)
    add("H_TSD7_par3", "heldout", "tsd", "tsd", "P7", 6, proc=bern, law=P7)
    add("H_PRF3", "heldout", "prf", "prf", "PRF", 6, proc=bern, law={"kind": "prf", "key": "tyche-prf-3", "w": 24})
    add("H_K4_xor", "heldout", "known", "known", "K4", 6, proc=bern, law={"kind": "kxor", "a": k1, "b": k2})
    sid, params = _pick_hec("ALIEN_LAWFUL", "map")
    add("H_HA_map", "heldout", "hec_alien", "hec_alien", "HA_map", 1,
        sys_id=sid, params=params, hidden=1, target=0, restart=25)
    add("H_ADV_sparse", "heldout", "adv", "adv", "A4", 8, proc={"kind": "gauss"},
        law={"kind": "sparse", "a": int(rng.integers(0, 8)), "b": int(rng.integers(0, 8)), "da": 9})
    if W[-1]["law"]["a"] == W[-1]["law"]["b"]:
        W[-1]["law"]["b"] = (W[-1]["law"]["a"] + 3) % 8
    for spec in W:
        if spec["kind"] in ("hec_alien", "hec_null"):
            spec["target"] = _entropy_target(spec)
    return W


def _entropy_target(spec):
    """Rule fixed before any lens ran: the target is the OBSERVED component
    whose next value has the highest entropy on calibration seed 0 (a
    near-constant target leaves no headroom for any lens)."""
    best, bh = 0, -1.0
    nd = len(_dims(spec["params"]))
    for j in range(nd):
        if j == spec["hidden"]:
            continue
        _, Y = generate(dict(spec, target=j), 0)
        p = np.bincount(Y) / len(Y)
        p = p[p > 0]
        h = float(-(p * np.log2(p)).sum())
        if h > bh + 1e-12:
            best, bh = j, h
    return best


def _dims(params):
    from hecate.alien import systems as S
    return S.dims_of(params)


def worlds_hash(W):
    return hashlib.sha256(json.dumps(W, sort_keys=True).encode()).hexdigest()
