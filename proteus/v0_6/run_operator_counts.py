"""Capture PER-OPERATOR destination counts for BOTH production kernels.

    python proteus/v0_6/run_operator_counts.py

run_full.py holds the per-operator counts only in memory, so the offline counterfactual
reweighting could be evaluated on K_A alone. The V0.6 completion directive requires attribution
conclusions to be visible on K_A AND K_B rather than on their average, so both are captured here.

THIS IS A REPLAY, NOT A NEW MEASUREMENT. Same preregistered seeds, same tags, same n, same state
set. Because each state's stream is root.derive(L, T) and derive does not advance the parent, the
counts are a deterministic function of (seed, tag, L, T) and are independent of worker count. The
script PROVES this rather than asserting it: the aggregate counts recovered here must equal the
counts persisted during production EXACTLY, for every state and every destination. A single
mismatch aborts and is an instrument failure.

No new seed, no new sampling decision, no new hypothesis.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.v0_6 import livekernel as LK  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

WORKERS = 12  # production runner is in its serial solve phase on 1 of 16 cores


def load_persisted(name, n):
    with open(os.path.join(HERE, f"COUNTS_{name}_n{n}.json"), encoding="utf-8") as f:
        d = json.load(f)
    assert d["samples_per_state"] == n, (name, d["samples_per_state"], n)
    return {tuple(json.loads(i)): {tuple(json.loads(j)): c for j, c in row.items()}
            for i, row in d["counts"].items()}


def main():
    with open(os.path.join(HERE, "PREREG_V0_6.json"), encoding="utf-8") as f:
        pre = json.load(f)
    for key, got in (("grammar_hash", grammar.GRAMMAR_HASH),
                     ("runtime_hash", RUNTIME_HASH),
                     ("affordance_hash", AFFORDANCE_HASH)):
        if pre[key] != got:
            print(f"REFUSING: {key} is {got} but the preregistration froze {pre[key]}")
            return 6
    n = pre["kernel"]["samples_per_state"]
    states, _tapes, _rules = space.regenerate_states()
    print(f"operator-count replay | {len(states)} states | n={n:,} | grammar "
          f"{grammar.GRAMMAR_HASH[:12]} | workers {WORKERS}", flush=True)

    out = {"schema_version": "proteus.v0_6_operator_counts.v1", "samples_per_state": n,
           "workers": WORKERS, "is_replay_of_production": True,
           "identities": {"grammar_hash": grammar.GRAMMAR_HASH, "runtime_hash": RUNTIME_HASH,
                          "affordance_hash": AFFORDANCE_HASH},
           "operator_names": list(grammar.NAMES),
           "operator_weights": list(grammar.WEIGHTS), "kernels": {}}
    t0 = time.time()
    for name, seed in (("K_A", pre["seed_a"]), ("K_B", pre["seed_b"])):
        P, OP, NOOP, ESC = LK.measure_kernel_parallel(states, n, seed, name, workers=WORKERS)
        got = LK.counts_from(P, n)
        want = load_persisted(name, n)
        mism = [s for s in states if got.get(s) != want.get(s)]
        esc = sum(sum(r.values()) for r in ESC.values())
        print(f"  {name}: replay vs persisted production counts -> "
              f"{'EXACT MATCH' if not mism else f'{len(mism)} MISMATCHED STATES'} | "
              f"escapes {esc} | {time.time()-t0:.0f}s", flush=True)
        if mism:
            print(f"  ABORT: replay is not bit-identical to production; example {mism[:3]}")
            return 5
        with open(os.path.join(HERE, f"OPCOUNTS_{name}_n{n}.json"), "w", encoding="utf-8",
                  newline="\n") as f:
            json.dump({"samples_per_state": n, "seed": seed, "tag": name,
                       "op_counts": {repr(list(i)): {op: {repr(list(j)): c
                                                          for j, c in sorted(d.items())}
                                                     for op, d in sorted(OP[i].items())}
                                     for i in states},
                       "noop_reasons": {repr(list(i)): r for i, r in sorted(NOOP.items())}},
                      f, sort_keys=True, separators=(",", ":"))
            f.write("\n")
        out["kernels"][name] = {"seed": seed, "escapes": esc,
                                "replay_matches_production_exactly": True,
                                "noop_states": len(NOOP),
                                "file": f"OPCOUNTS_{name}_n{n}.json"}
    out["wall_s"] = time.time() - t0
    with open(os.path.join(HERE, "RESULT_OPERATOR_COUNT_REPLAY.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"both kernels captured and verified bit-identical to production ({out['wall_s']:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
