"""P1 mobility observatory (V2-B DEV-2): is a law's medium ENDOGENOUSLY MOBILE, as opposed to frozen,
noise-driven, trivially cycling, or residue being shuffled?

Same world as the twin and provenance assays (scouts sparse soup, B-balanced energy, n=128, warm-up 1500 with
perturbation ON). Then a followed window of T ticks in arm OFF (no injected perturbation: all change is endogenous)
or ON (injected perturbation: a contrast that does NOT qualify as endogenous mobility, per the operator directive).
The window is followed under the prov0 shadow (so the per-tick physics self-check applies) and reports:

- turnover_early / turnover_late: mean per-tick share of the 4*n^2 TEMPLATE bytes whose value CHANGED, over the first
  and last 100 ticks. Same-value rewrites are not mobility. A frozen medium decays toward 0.
- revisit_share: of the sites whose template state changed this tick, the share returning to a state they held in
  the previous L=8 ticks (excluding the immediately previous one). Flags trivial cycling or flip-flops.
- residue_share: share of template bytes still holding their warm-up-end (INIT) node at the end.
- mean_age: mean age, in ticks, of the stored template nodes at the end (INIT counts as age = window length).
- chain_share: of ALL winning template writes in the window (prov0 does not store the replaced value, so same-value
  rewrites are included), the share whose value parent was itself written inside the window. Dynamic chains, not
  recycled residue.
- mut_share: share of winning writes that carry a perturbation flip (0 in OFF by construction).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth03_propagation as PR           # noqa: E402
from observatory import aeth03_scouts as S                 # noqa: E402
from observatory import aeth03_variants as V               # noqa: E402
from observatory import aeth_prov as P                     # noqa: E402

REVISIT_L = 8
EDGE = 100

# P1 classification thresholds (frozen with the TEST-2 preregistration; calibrated on DEV seed 100 only).
P1_RULE = {"turnover_min": 0.002, "persistence_min": 0.5, "revisit_max": 0.25, "counter_max": 0.5,
           "active_min": 0.10}


class MobilityMeter:
    """Incremental P1 measures over a sequence of template states (4 uint8 fields, H x W). Pure function of the
    sequence: it never touches the physics."""

    def __init__(self, fields0):
        self.prev = [f.astype(np.int16) for f in fields0[:4]]
        self.prev_delta = [np.zeros_like(x) for x in self.prev]
        self.prev_changed = [np.zeros(x.shape, bool) for x in self.prev]
        self.hist = [_site_state(fields0)]
        self.turnover = []
        self.changes = self.counter_changes = 0
        self.revisits = self.changed_sites = 0
        self.ever = np.zeros(fields0[0].shape, bool)

    def update(self, fields):
        cur = [f.astype(np.int16) for f in fields[:4]]
        h, w = cur[0].shape
        ch_total = 0
        for i in range(4):
            changed = cur[i] != self.prev[i]
            delta = (cur[i] - self.prev[i]) & 0xFF
            ch_total += int(changed.sum())
            # a counter: this byte changed by the same step as at its previous tick's change
            self.counter_changes += int((changed & self.prev_changed[i] & (delta == self.prev_delta[i])).sum())
            self.prev_delta[i] = np.where(changed, delta, self.prev_delta[i])
            self.prev_changed[i] = changed
            self.prev[i] = cur[i]
        self.changes += ch_total
        self.turnover.append(ch_total / (4.0 * h * w))
        st = _site_state(fields)
        moved = st != self.hist[-1]
        self.ever |= moved
        self.changed_sites += int(moved.sum())
        if moved.any():
            back = np.zeros_like(moved)
            for prev in self.hist[-REVISIT_L:-1]:
                back |= (st == prev)
            self.revisits += int((moved & back).sum())
        self.hist.append(st)
        if len(self.hist) > REVISIT_L + 1:
            self.hist.pop(0)

    def metrics(self):
        t = self.turnover
        early, late = float(np.mean(t[:EDGE])), float(np.mean(t[-EDGE:]))
        return {"turnover_early": early, "turnover_late": late,
                "persistence": late / early if early > 0 else 0.0,
                "revisit_share": self.revisits / self.changed_sites if self.changed_sites else 0.0,
                "counter_share": self.counter_changes / self.changes if self.changes else 0.0,
                "active_site_share": float(self.ever.mean()),
                "turnover_series_10": [float(np.mean(t[i:i + 10])) for i in range(0, len(t), 10)]}


def classify(m, rule=P1_RULE):
    """P1 class of one arm's metrics: the FIRST failing clause names the class."""
    if m["turnover_late"] < rule["turnover_min"]:
        return "FROZEN"
    if m["persistence"] < rule["persistence_min"]:
        return "DECAYING"
    if m["revisit_share"] > rule["revisit_max"]:
        return "CYCLING"
    if m["counter_share"] > rule["counter_max"]:
        return "COUNTER"
    if m["active_site_share"] < rule["active_min"]:
        return "LOCALISED"
    return "ENDOGENOUSLY_MOBILE"


def _site_state(f):
    """One uint64 per site packing the four template bytes."""
    return (f[0].astype(np.uint64) | (f[1].astype(np.uint64) << np.uint64(8))
            | (f[2].astype(np.uint64) << np.uint64(16)) | (f[3].astype(np.uint64) << np.uint64(24)))


def mobility(variant, n=128, warmup=1500, ticks=400, seed_index=0, arm="off"):
    seed, rng_seed = S.SEED0 + seed_index, S.RNG0 + seed_index
    t0 = time.time()
    w = PR.World(variant, S.initial(variant, n, rng_seed))
    par_on = S.params(seed, S.MUT_ON)
    for t in range(1, warmup + 1):
        w.step(t, par_on)
    if variant == "rcv_sfz":
        w.extra["aim_energy"] = w.f[4].copy()
    par = S.params(seed, 0 if arm == "off" else S.MUT_ON)
    pv = P.Provenance(variant, w.f, received_value=w.extra.get("received_value"))
    n_init = pv.n
    f = [x.copy() for x in w.f]
    rec, rv = w.extra.get("received"), w.extra.get("received_value")
    meter = MobilityMeter(f)
    for k in range(1, ticks + 1):
        t = warmup + k
        obs, kw = [], {}
        if variant in V.RCV_FAMILY:
            kw["received"] = rec
        if variant == "fwd":
            kw["received_value"] = rv
        if "aim_energy" in w.extra:
            kw["aim_energy"] = w.extra["aim_energy"]
        out = V.step(variant, H=n, W=n, tick=t, opcode=f[0], arg0=f[1], arg1=f[2], payload=f[3], energy=f[4],
                     observer=obs, **kw, **par)
        post = list(out[:5])
        pv.step(t, f, post, obs, par, received=rec if variant in V.RCV_FAMILY else None)
        meter.update(post)
        f = post
        if variant in V.RCV_FAMILY:
            rec = out[5]["received"]
        if variant == "fwd":
            rv = out[5]["received_value"]
    op = pv.column("op"); p1 = pv.column("p1"); tk = pv.column("tick"); val = pv.column("value")
    new = np.arange(n_init, pv.n)
    cur = np.concatenate([c.ravel() for c in pv.cur])
    age = np.where(cur < n_init, ticks, (warmup + ticks) - tk[cur])
    newv = new[(op[new] & 3) > 0]
    par_t = np.where(p1[newv] >= 0, tk[np.maximum(p1[newv], 0)], 0)
    chain = float(np.mean(par_t > warmup)) if newv.size else 0.0
    mut = float(np.mean((op[newv] & P.OP_MUT) != 0)) if newv.size else 0.0
    m = meter.metrics()
    out = {"instrument": "aeth_mobility", "prov_version": P.PROV_VERSION, "variant": variant,
            "semantics_id": V.SEMANTICS_ID[variant], "n": n, "warmup": warmup, "ticks": ticks,
            "seed_index": seed_index, "arm": arm}
    out.update(m)
    out.update({"p1_class": classify(m),
            "residue_share": float(np.mean(cur < n_init)), "mean_age": float(np.mean(age)),
            "chain_share": chain, "mut_share": mut, "writes_in_window": int(newv.size),
            "wall_seconds": round(time.time() - t0, 1)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--law", required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--arm", choices=("off", "on"), default="off")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = mobility(a.law, a.n, a.warmup, a.ticks, a.seed_index, a.arm)
    body = json.dumps({k: v for k, v in res.items() if k != "wall_seconds"}, sort_keys=True, separators=(",", ":"))
    res["result_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, sort_keys=True)
    print(json.dumps({k: res[k] for k in ("variant", "arm", "seed_index", "p1_class", "turnover_early",
                                          "turnover_late", "revisit_share", "counter_share", "active_site_share",
                                          "residue_share", "chain_share", "result_sha256", "wall_seconds")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
