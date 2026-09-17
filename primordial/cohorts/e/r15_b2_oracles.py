"""E-R15-2 oracles: graphworld_b2 controllable adapter (operator 15 R15-2, predicate bus 1789455548741-0).

  O1  GraphBLAS == Cypher == reference trajectory hash (and charges) on 32 specs (b2.oracle.specs) x 2 action streams
      (uniform random table PCG64([1501, j]); the obs-reading forager): 64/64 per form.
  O2  skip-mutation cheat (action read, AT mutation not applied) in gb and cy: hash != reference on every spec where a
      live prey received a moving action; charge differs on >= 1 spec.
  O3  planted controllability (adapter.PLANTED, HELD64 episode seeds 30000..30063): the forager's median per-seed charge
      has bootstrap CI low > max(abstain median, best constant median (constant selected on TRAIN8 9100..9107),
      uniform-random median of 8 policy seeds' medians).
Rows at every status; F9 checkpoint per spec.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r15_b2_oracles:job --exp E-R15-2-b2-adapter-oracles \\
        --rows primordial/ledger/rows/E/E-R15-2-b2-adapter-oracles.jsonl --ttl-cpu-s 600 --kwargs '{}'
"""
from __future__ import annotations

import numpy as np

from primordial.metric.ci import median_ci
from primordial.soup.b2 import adapter as AD
from primordial.soup.b2.oracle import specs

HELD64 = np.arange(30000, 30064)
TRAIN8 = np.arange(9100, 9108)


def _random_policy(seed, S):
    rng = np.random.Generator(np.random.PCG64(seed))
    return lambda o, t: rng.integers(0, AD.A, S)


def job(ctx, n_specs=32, forms=("gb", "cy"), held=tuple(HELD64.tolist()), train=tuple(TRAIN8.tolist()), dev=False):
    status = lambda ok: ("dev" if dev else ("record" if ok else "control"))
    st = ctx.load_checkpoint() or {"o12": {}, "o3": None}
    for j, s in enumerate(specs(n_specs)):
        if str(j) in st["o12"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        res = []
        streams = {"random": AD.table_policy(AD.random_table(s, [1501, j])), "forager": AD.forager}
        for name, pol in streams.items():
            ref = AD.episode("ref", s, pol)
            for form in forms:
                got = AD.episode(form, s, pol)
                row = {"kind": "o1", "spec": j, "L": s.L, "n": s.n, "stream": name, "form": form,
                       "equal_hash": got["hash"] == ref["hash"], "equal_charges": got["charges"] == ref["charges"],
                       "charge": got["charge"], "ref_charge": ref["charge"], "moving_actions": ref["moving_actions"]}
                ctx.emit({**row, "status": status(row["equal_hash"])})
                res.append(row)
            if name == "random":
                for form in forms:
                    ch = AD.episode(form, s, pol, cheat="skip_mutation")
                    row = {"kind": "o2", "spec": j, "stream": name, "form": form, "cheat": "skip_mutation",
                           "moved": ref["moving_actions"] > 0, "detected_hash": ch["hash"] != ref["hash"],
                           "charge_differs": ch["charge"] != ref["charge"], "charge": ch["charge"],
                           "ref_charge": ref["charge"]}
                    ctx.emit({**row, "status": "cheat"})
                    res.append(row)
        st["o12"][str(j)] = res
        ctx.checkpoint(st)
    if st["o3"] is None:
        if ctx.should_pause():
            ctx.pause(st)
        fg = AD.rollout(AD.planted, AD.forager, held)
        ab = AD.rollout(AD.planted, AD.abstain, held)
        const_train = {a: float(np.median(AD.rollout(AD.planted, AD.constant(a), train))) for a in range(AD.A)}
        best_a = max(range(AD.A), key=lambda a: (const_train[a], -a))
        const_held = AD.rollout(AD.planted, AD.constant(best_a), held)
        S = AD.PLANTED["n_prey"]
        rand_meds = [float(np.median([AD.episode("ref", AD.planted(sd), _random_policy([1502, ps, sd], S))["charge"]
                                      for sd in held])) for ps in range(8)]
        lo, hi = median_ci(fg.tolist())
        floors = {"abstain": float(np.median(ab)), "best_constant": float(np.median(const_held)),
                  "uniform_random_median": float(np.median(rand_meds))}
        st["o3"] = {"kind": "o3", "world": AD.PLANTED, "held_seeds": [int(held[0]), int(held[-1])], "n": len(held),
                    "forager_median": float(np.median(fg)), "forager_ci95": [lo, hi], "floors": floors,
                    "best_constant_action": best_a, "constant_train_medians": const_train,
                    "random_policy_medians": rand_meds, "pass": bool(lo > max(floors.values()))}
        ctx.emit({**st["o3"], "status": status(st["o3"]["pass"])})
        ctx.checkpoint(st)
    rows = [r for v in st["o12"].values() for r in v]
    o1 = {f: {"hash_equal": sum(r["equal_hash"] and r["equal_charges"] for r in rows if r["kind"] == "o1" and r["form"] == f),
              "of": sum(1 for r in rows if r["kind"] == "o1" and r["form"] == f)} for f in forms}
    o2 = {f: {"moved_specs": sum(r["moved"] for r in rows if r["kind"] == "o2" and r["form"] == f),
              "detected_on_moved": sum(r["detected_hash"] for r in rows if r["kind"] == "o2" and r["form"] == f and r["moved"]),
              "charge_differs_specs": sum(r["charge_differs"] for r in rows if r["kind"] == "o2" and r["form"] == f)}
          for f in forms}
    checks = {"O1": all(v["hash_equal"] == v["of"] == 2 * n_specs for v in o1.values()),
              "O2": all(v["detected_on_moved"] == v["moved_specs"] > 0 and v["charge_differs_specs"] >= 1 for v in o2.values()),
              "O3": st["o3"]["pass"]}
    ctx.emit({"kind": "summary", "status": "dev" if dev else "record", "n_specs": n_specs, "forms": list(forms),
              "o1": o1, "o2": o2, "o3": {k: st["o3"][k] for k in ("forager_median", "forager_ci95", "floors", "pass")},
              "checks": checks, "predicate_pass": all(checks.values())})
