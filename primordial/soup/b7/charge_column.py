"""B bounty on C7d: which observed column IS the charge bucket? Measured from observations, not read from obs_perm.

For each world, B's NpEncounter with zero actions (C7's setting), slot 0. Every tick, the charge bucket
min(15, charge // 32) is computed independently from w.charge BEFORE observing, and each permuted observation
column is compared with it. The true charge column matches at 1.0 in clean worlds and at ~(1 - 1/corrupt_rate) in
corrupted worlds (the corruption stream XORs every channel, including charge); register columns should match ~0.

Cheat control: the C7 harness assumption "charge = last column" is scored with the same bar. It must fail exactly
where the measured charge column is not last.

usage: python -m primordial.soup.b7.charge_column --out primordial/ledger/rows/B/B-bounty-C7d-charge-index.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

from primordial.soup.b1.common import make_world
from primordial.soup.b1.np_world import NpEncounter

ROOT = pathlib.Path(__file__).resolve().parents[2]
C7D = ROOT / "ledger" / "rows" / "C" / "C7d-chance-grounded-contrast.jsonl"


def match_rates(m, wid, seeds) -> np.ndarray:
    """-> float [D]: fraction of (env, tick) where obs column q (slot 0) equals the independent charge bucket."""
    w = NpEncounter(m, wid, record=None, cheat="", with_obs=True)
    obs = w.reset(seeds)                                     # observation at tick 0 (charge = start charge)
    a = np.zeros((len(seeds), m.n_slots, m.act_width), np.int32)
    D = obs.shape[2]
    hits = np.zeros(D)
    total = 0
    for _ in range(m.horizon - 1):
        bucket = np.minimum(15, w.charge[:, 0] // 32)          # independent: from charge, before this observation's use
        hits += (obs[:, 0, :] == bucket[:, None]).sum(0)
        total += len(seeds)
        obs, _, done = w.step(a)
        if done.all():
            break
    return hits / max(total, 1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--envs", type=int, default=256)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    header = next(json.loads(l) for l in open(C7D, encoding="utf-8") if json.loads(l).get("kind") == "header")
    worlds = [int(x) for x in header["worlds"].split(",")]
    seeds = np.arange(98000, 98000 + a.envs, dtype=np.int64)
    rows = []
    for gs in worlds:
        m, wid = make_world(gs)
        D = len(m.obs_perm)
        rate = m.corrupt_rate
        expect = 1.0 if not rate else 1.0 - 1.0 / rate
        bar = (lambda x: x >= 0.99) if not rate else (lambda x: abs(x - expect) <= 0.05)
        mr = match_rates(m, wid, seeds)
        matching = [q for q in range(D) if bar(mr[q])]
        q_perm = int(list(m.obs_perm).index(D - 1))
        others = [float(mr[q]) for q in range(D) if q != q_perm]
        rows.append({"gen_seed": gs, "D": D, "corrupt_rate": rate, "expected_charge_match": expect,
                     "match_rate_per_column": [round(float(x), 5) for x in mr],
                     "measured_charge_columns": matching, "obs_perm_charge_position": q_perm,
                     "measured_equals_obs_perm": matching == [q_perm],
                     "charge_is_last": q_perm == D - 1,
                     "max_other_column_match": round(max(others), 5) if others else None,
                     "cheat_last_column_match": round(float(mr[D - 1]), 5),
                     "cheat_last_column_passes_bar": bool(bar(mr[D - 1]))})
        print(f"gs{gs:>4} D={D} rate={rate:>2} charge@{matching} perm@{q_perm} last={q_perm == D - 1} "
              f"max_other={rows[-1]['max_other_column_match']} cheat_last={rows[-1]['cheat_last_column_match']}", flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
