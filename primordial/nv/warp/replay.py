"""W3: lane E's world oracle (E4/E7) aimed at the Warp kernel.

Actions are recorded by lane E's OWN rollouts (read-only), then replayed open-loop through the
Warp world kernel. Each episode's Warp trace hash and clipped final charge must equal
  (a) E4.wforge_replay of the same actions (the wforge Encounter), and
  (b) the trace hash of E's own NpEncounter world in the recording rollout.
Sources of actions:
  e7:<family>  E7.rollout of G7(<family>) genomes (closed-loop brain actions) on E6's HELD8 seeds
  e4           E4.init_genomes open-loop action tensors on E4.SEEDS
  abstain      the all-zero action tensor (the abstain floor policy; full-horizon episodes)
Per genome (E7 convention): a genome fails if any of its episodes mismatches. skip_lin must fail.

    python -m primordial.nv.warp.replay --worlds 4,1,3 --sources e7:linear,e7:tt_digits,e4,abstain
           --device cuda:0 [--cheat skip_lin] [--exp W3-...]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

from primordial.qd import e4_run as E4        # lane E, read-only
from primordial.qd import e7_run as E7        # lane E, read-only

from .world import WpEncounter


def record(source: str, gen_seed: int, P: int, rng_seed: int = 0):
    """-> (E4.Spec, acts int32 [T, P*k, S, W], seeds per env, E's own trace hashes, k)."""
    if source.startswith("e7:"):
        g7 = E7.G7(gen_seed, source[3:])
        g = g7.init(np.random.default_rng(rng_seed), P)
        seeds = E7.HELD8
        _, _, w, L = E7.rollout(g7, g, seeds, log=True)
        return g7.spec, L["acts"].astype(np.int32), np.tile(seeds, P), [h.decode() for h in w.trace_hashes()], len(seeds)
    spec = E4.Spec(gen_seed)
    if source == "e4":
        G = E4.init_genomes(np.random.default_rng(rng_seed), spec, P)
    elif source == "abstain":
        G = np.zeros((P, spec.T, spec.S, spec.W), np.uint8)
    else:
        raise ValueError(f"unknown source {source!r}")
    _, _, w = E4.evaluate(spec, G, record=True)
    k = len(E4.SEEDS)
    acts = np.ascontiguousarray(np.repeat(G, k, axis=0).astype(np.int32).transpose(1, 0, 2, 3))
    return spec, acts, np.tile(E4.SEEDS, P), [h.decode() for h in w.trace_hashes()], k


def run_cell(source: str, gen_seed: int, P: int, device: str, cheat: str = "") -> dict:
    spec, acts, seeds, e_hashes, k = record(source, gen_seed, P)
    n = len(seeds)
    w = WpEncounter(spec.mech, spec.wid, cheat=cheat, device=device)
    w.prepare(seeds, log=True)
    w.run(acts)
    hashes = [h.decode() for h in w.trace_hashes()]
    charge = np.clip(w.final_charge(), 0, None)
    bad = np.zeros(n // k, bool)
    mh = mc = me = 0
    for e in range(n):
        h_wf, ch_wf = E4.wforge_replay(spec, acts[:, e], int(seeds[e]))
        hb, cb, eb = hashes[e] != h_wf, not np.array_equal(charge[e], ch_wf), hashes[e] != e_hashes[e]
        mh += hb; mc += cb; me += eb
        bad[e // k] |= hb or cb
    ticks = w.done_tick.numpy()
    return {"source": source, "world_seed": gen_seed, "world_id": spec.wid, "device": device, "cheat": cheat or None,
            "genomes": int(n // k), "episodes": n, "genomes_failing": int(bad.sum()),
            "episodes_hash_mismatch_wforge": int(mh), "episodes_charge_mismatch_wforge": int(mc),
            "episodes_hash_mismatch_e_world": int(me), "mean_episode_ticks": float(ticks.mean()),
            "T": spec.T, "S": spec.S}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="4,1,3")
    ap.add_argument("--sources", default="e7:linear,e7:tt_digits,e4,abstain")
    ap.add_argument("--P", type=int, default=16)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--cheat", default="")
    ap.add_argument("--exp", default="")
    a = ap.parse_args(argv)
    rows = []
    for g in (int(x) for x in a.worlds.split(",")):
        for src in a.sources.split(","):
            row = run_cell(src, g, a.P, a.device, a.cheat)
            print(json.dumps(row), flush=True)
            rows.append(row)
    if a.exp:
        from primordial.fabric.rows import RowWriter
        path = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "W" / f"{a.exp}.jsonl"
        with RowWriter(path, a.exp, commit_every_s=10**9) as wr:
            for r in rows:
                wr.write({"status": "cheat" if a.cheat else "record", "form": "warp", **r})
    fails = sum(r["genomes_failing"] for r in rows)
    return (0 if fails == 0 else 1) if not a.cheat else (0 if all(r["genomes_failing"] >= 14 * r["genomes"] // 16
                                                                  for r in rows) else 1)


if __name__ == "__main__":
    sys.exit(main())
