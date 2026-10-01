"""W-Z (T-SWAP-AUDIT3, plan 6f25dc642) shared bookkeeping: group list, order, row map, labelling.

Reuses by import (never edits): W-O runner/audit/inventory (specimen loading, arms, offsets, group key),
prometheus.ananke.swap_rel (REL4 H2 rule), W-U swap_rel3 (REL3 p_min table, paired z CI / transfer class).
"""
from __future__ import annotations

import collections
import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
WK = HERE.parent
REPO = HERE.parents[4]
for p in (str(REPO), str(WK / "W-O"), str(WK / "W-U")):
    if p not in sys.path:
        sys.path.insert(0, p)
OUT = HERE / "out"
NS = 0x680
M = 512


def _gkey(src, sp, off):
    import hashlib
    return hashlib.sha256(f"{src}|{sp}|{off}".encode()).hexdigest()


def inventory():
    return list(csv.DictReader(open(WK / "W-O" / "out" / "inventory.csv")))


def rel3_rows():
    return {r["vid"]: r for r in csv.DictReader(open(WK / "W-U" / "out" / "rel3_733.csv"))}


def wo_rows():
    return {r["vid"]: r for r in csv.DictReader(open(WK / "W-O" / "out" / "rerun_table.csv"))}


def groups():
    """W-O audit.groups() semantics: key (source, loader, specimen, offset, trial_set, family) -> inventory rows."""
    g = collections.OrderedDict()
    for r in inventory():
        k = (r["source"], r["loader"], r["specimen"], r["offset"], r["trial_set"], r["family"])
        g.setdefault(k, []).append(r)
    return g


def wo_cost():
    """W-O measured t_single (1 thread, s) per group key (used only for budgeting)."""
    import glob
    c = {}
    for fn in glob.glob(str(WK / "W-O" / "out" / "rerun_s*.jsonl")):
        for line in open(fn):
            if line.strip():
                x = json.loads(line)
                if "error" not in x:
                    c[tuple(x["group"])] = x["t_single"]
    return c


def order():
    """PLAN s2: all groups containing an AMBIGUOUS row (sha256 order), then the rest (sha256 order)."""
    g = groups()
    r3 = rel3_rows()
    amb = {k for k, rows in g.items() if any(r3[r["vid"]]["status"] == "AMBIGUOUS" for r in rows)}
    key = lambda k: _gkey(k[0], k[2], k[3])  # noqa: E731
    first = sorted(amb, key=key)
    rest = sorted((k for k in g if k not in amb), key=key)
    return first, rest


def gid(k) -> str:
    return _gkey(k[0], k[2], k[3])[:16]


def pmin_rel3(K: int):
    t = json.loads((WK / "W-U" / "out" / "rel3_table.json").read_text())
    d = t["designs"].get(f"P256_K{K}")
    return None if d is None else dict(d["p_min"])


def label_arm(a, s, K, P_design=256):
    """a, s [P] pair means (over the design's scored trials). -> REL4 label dict + transfer class for FLIP_REL."""
    from prometheus.ananke import swap_rel as sr
    import swap_rel3 as r3
    P = int(len(a))
    pm = None
    if P == 256:
        pm = pmin_rel3(K)
    out = sr.from_pairs(a, s, K, p_min=pm)
    zc = r3.z_ci(np.asarray(a, float), np.asarray(s, float))
    out["zci"] = zc
    out["transfer"] = zc["class"] if out["label"] == "FLIP_REL" else ""
    out["p_min_used"] = pm
    return out


def group_class(labels_with_transfer):
    """PLAN s4 group class from [(label, transfer)] over the arms of a group."""
    labs = [l for l, _ in labels_with_transfer]
    fl = [t for l, t in labels_with_transfer if l == "FLIP_REL"]
    if fl:
        if "COMPLETE" in fl:
            return "CARRIER-NAMED"
        if all(t == "PARTIAL" for t in fl):
            return "CARRIER-PARTIAL"
        return "CARRIER-OVERSHOOT"   # addendum Z3: FLIP_REL arms only PARTIAL/OVERSHOOT, >= 1 OVERSHOOT (plan silent)
    if any(l in ("NO_EFFECT_REL", "CHANCE_REL") for l in labs):
        return "NO-CARRIER-FOUND"
    return "UNDECIDED"
