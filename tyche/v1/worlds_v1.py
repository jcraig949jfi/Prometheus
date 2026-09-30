"""Tyche v1 worlds -- the CALIBRATION lane only (operator v1 directive):
worlds where we secretly know exploitable structure exists. The natural
122-residual habitat is not touched until gate 6 is shown.

Classes (answer key; never visible to evolution):
  Z  zero-marginal, positive-joint, EVERY precursor absent from the raw
     observation: each precursor alone carries exactly zero information
     about Y by construction (xor / parity of independent fair bits; sign
     of a product of independent symmetric variables).
  C  the same law families with ONE precursor already a raw observation
     (v0-style selection can reach these in one step: v0 solved P5 at R2
     exactly this way).
  G  gradient control (running count mod 3; v0 solved it from chance).
  N  negatives: TARGET_STRUCTURE_DESTROYED twins of Z worlds and keyed PRF.

oracle(spec) returns a hand-written genome computing Y exactly (the answer
key as a lens). It is used ONLY to measure the capability deficit
D(W) = P_oracle - P_ecology on these calibration worlds.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np

from .. import worlds as W0
from ..lens import NIN

T = W0.T
SPLITS = W0.SPLITS


def _inputs(proc, d, rng):
    if proc["kind"] == "ar1":
        X = np.empty((T, d))
        e = rng.standard_normal((T, d))
        X[0] = e[0]
        for t in range(1, T):
            X[t] = proc["phi"] * X[t - 1] + e[t]
        return X
    return W0._inputs(proc, d, rng)


def _wbit(x, d, w, th):
    c = np.concatenate([[0], np.cumsum(x)])
    t = np.arange(T)
    hi = np.clip(t - d + 1, 0, T)
    lo = np.clip(t - d - w + 1, 0, T)
    return ((c[hi] - c[lo]) >= th).astype(np.int64)


def _law(L, X, rng):
    if L["kind"] == "wxor":
        return _wbit(X[:, L["a"]], L["da"], L["w"], L["th"]) ^ _wbit(X[:, L["b"]], L["db"], L["w"], L["th"])
    return W0._law(L, X, rng)


def generate(spec, seed):
    rng = np.random.default_rng([int(seed), int(spec["uid"]), 1])
    X = _inputs(spec["proc"], spec["d"], rng)
    if spec["kind"] == "tsd":
        Xh = _inputs(spec["proc"], spec["d"], rng)
        Y = _law(spec["law"], Xh, rng)
    else:
        Y = _law(spec["law"], X, rng)
    return X, np.asarray(Y, dtype=np.int64)


def oracle(spec):
    """Answer-key genome for spec's law (calibration only). None for PRF."""
    L, N = spec["law"], NIN
    k = L["kind"]
    if k == "xor2":
        if L["da"] == 0:  # C-class: one precursor is the raw channel a
            return {"ins": [["delay", [L["b"]], L["db"]], ["xor", [L["a"], N], None]], "out": [N + 1]}
        return {"ins": [["delay", [L["a"]], L["da"]], ["delay", [L["b"]], L["db"]], ["xor", [N, N + 1], None]],
                "out": [N + 2]}
    if k == "par3":
        return {"ins": [["delay", [L["a"]], L["da"]], ["delay", [L["b"]], L["db"]], ["xor", [N, N + 1], None],
                        ["delay", [L["c"]], L["dc"]], ["xor", [N + 2, N + 3], None]], "out": [N + 4]}
    if k == "psign":
        if L["da"] == 0:
            return {"ins": [["delay", [L["b"]], L["db"]], ["mul", [L["a"], N], None], ["thresh", [N + 1], 0.0]],
                    "out": [N + 2]}
        return {"ins": [["delay", [L["a"]], L["da"]], ["delay", [L["b"]], L["db"]], ["mul", [N, N + 1], None],
                        ["thresh", [N + 2], 0.0]], "out": [N + 3]}
    if k == "wxor":
        th = float(L["th"] - 1)
        return {"ins": [["delay", [L["a"]], L["da"]], ["wsum", [N], L["w"]], ["thresh", [N + 1], th],
                        ["delay", [L["b"]], L["db"]], ["wsum", [N + 3], L["w"]], ["thresh", [N + 4], th],
                        ["xor", [N + 2, N + 5], None]], "out": [N + 6]}
    if k == "cmod":
        return {"ins": [["accmod", [L["a"]], L["m"]]], "out": [N]}
    return None


def build_worlds_v1(master_seed=20261001):
    rng = np.random.default_rng(master_seed)
    Wl = []

    def add(wid, role, cls, kind, d, proc, law, twin_of=None, sibling_of=None):
        Wl.append({"id": wid, "role": role, "cls": cls, "kind": kind, "family": cls,
                   "law_group": law.get("group", wid), "d": d, "uid": 100 + len(Wl),
                   "proc": proc, "law": law, "twin_of": twin_of, "sibling_of": sibling_of})

    def ch(n):
        return [int(v) for v in rng.choice(6, size=n, replace=False)]

    bern = {"kind": "bern", "p": 0.5}
    gauss = {"kind": "gauss"}
    a, b = ch(2)
    Z1 = {"kind": "xor2", "a": a, "b": b, "da": 4, "db": 11, "group": "Z1"}
    a, b = ch(2)
    Z2 = {"kind": "xor2", "a": a, "b": b, "da": 3, "db": 7, "group": "Z2"}
    a, b, c = ch(3)
    Z3 = {"kind": "par3", "a": a, "b": b, "c": c, "da": 2, "db": 5, "dc": 9, "group": "Z3"}
    a, b = ch(2)
    Z4 = {"kind": "psign", "a": a, "b": b, "da": 5, "db": 2, "group": "Z4"}
    a, b = ch(2)
    Z5 = {"kind": "wxor", "a": a, "b": b, "da": 3, "db": 8, "w": 5, "th": 3, "group": "Z5"}
    a, b = ch(2)
    C1 = {"kind": "xor2", "a": a, "b": b, "da": 0, "db": 6, "group": "C1"}
    a, b = ch(2)
    C2 = {"kind": "psign", "a": a, "b": b, "da": 0, "db": 4, "group": "C2"}
    G1 = {"kind": "cmod", "a": ch(1)[0], "m": 3, "group": "G1"}
    a, b = ch(2)
    Z6 = {"kind": "xor2", "a": a, "b": b, "da": 5, "db": 8, "group": "Z6"}

    add("Z1_xor_4_11", "train", "Z", "planted", 6, bern, Z1)
    add("Z2_xor_3_7", "train", "Z", "planted", 6, bern, Z2)
    add("Z3_par3", "train", "Z", "planted", 6, bern, Z3)
    add("Z4_psign_5_2", "train", "Z", "planted", 6, gauss, Z4)
    add("Z5_wxor", "train", "Z", "planted", 6, bern, Z5)
    add("C1_xor_raw_6", "train", "C", "planted", 6, bern, C1)
    add("C2_psign_raw_4", "train", "C", "planted", 6, gauss, C2)
    add("G1_cmod3", "train", "G", "planted", 6, bern, G1)
    add("N1_tsd_Z1", "train", "N", "tsd", 6, bern, Z1, twin_of="Z1_xor_4_11")
    add("N2_tsd_Z2", "train", "N", "tsd", 6, bern, Z2, twin_of="Z2_xor_3_7")
    add("N3_tsd_Z4", "train", "N", "tsd", 6, gauss, Z4, twin_of="Z4_psign_5_2")
    add("N4_tsd_Z5", "train", "N", "tsd", 6, bern, Z5, twin_of="Z5_wxor")
    add("N5_prf", "train", "N", "prf", 6, bern, {"kind": "prf", "key": "tyche-v1-prf-1", "w": 24, "group": "PRF"})
    add("H_Z1sib_markov", "heldout", "Z", "planted", 6, {"kind": "markov", "stay": 0.7}, Z1, sibling_of="Z1_xor_4_11")
    add("H_Z4sib_ar1", "heldout", "Z", "planted", 6, {"kind": "ar1", "phi": 0.5}, Z4, sibling_of="Z4_psign_5_2")
    add("H_Z6_xor_5_8", "heldout", "Z", "planted", 6, bern, Z6)
    add("H_N6_tsd_Z6", "heldout", "N", "tsd", 6, bern, Z6, twin_of="H_Z6_xor_5_8")
    add("H_N7_prf", "heldout", "N", "prf", 6, bern, {"kind": "prf", "key": "tyche-v1-prf-2", "w": 24, "group": "PRF"})
    return Wl


def worlds_hash(Wl):
    return hashlib.sha256(json.dumps(Wl, sort_keys=True).encode()).hexdigest()
