"""V0.6 cross-runtime replay under the frozen two-layer numerical contract (brief section 8).

    python proteus/v0_6/run_replay.py out.json

EXACT layer: state enumeration and hash, state ids, seeds, per-state transition COUNTS, manifest
and source identity hashes. These must be byte-identical on every tested runtime.

NUMERICAL layer: stationary probabilities, currents, entropy production and residuals, compared
against tolerances that were frozen by conditioning rather than by observed differences. All
adjudicated sums use math.fsum, which is exactly rounded, so the CPython 3.12 sum() change that
broke V0.5's byte-identity cannot enter these quantities.

The replay uses a reduced but CLOSED state set so it runs in seconds on every runtime; the
closure property, not the size, is what makes the comparison meaningful.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj  # noqa: E402
from proteus.v0_6 import equilibrium as EQ  # noqa: E402
from proteus.v0_6 import livekernel as LK  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

SAMPLES = 3000


def main():
    states, tapes, rules = space.regenerate_states()
    full_ident = space.space_identity(states)
    # a closed sub-chain: tape fixed at its minimum is NOT closed (it can double), so the replay
    # uses the whole space's enumeration for the exact layer and a small closed set for the
    # numerical layer by folding escapes, which is declared in the contract.
    sub = [s for s in states if s[1] <= 32]
    P, OP, NOOP, ESC = LK.measure_kernel_parallel(sub, SAMPLES, 0x5EED, "replay", workers=2)
    counts = LK.counts_from(P, SAMPLES)

    pi, m = EQ.stationary_power(P, sub, tol=1e-14)
    cur = EQ.currents(P, pi, sub)
    ep = EQ.entropy_production(P, pi, sub)
    ep.pop("_by_edge", None)

    exact = {
        "space_hash": full_ident["hash"], "n_states": full_ident["n_states"], "tapes": tapes,
        "sub_states": [list(s) for s in sub],
        "transition_counts": {repr(list(i)): {repr(list(j)): c for j, c in sorted(row.items())}
                              for i, row in sorted(counts.items())},
        "escapes": {repr(list(i)): {repr(list(j)): c for j, c in sorted(row.items())}
                    for i, row in sorted(ESC.items())},
        "noop_reasons": {repr(list(i)): row for i, row in sorted(NOOP.items())},
        "identities": {"grammar_hash": grammar.GRAMMAR_HASH, "runtime_hash": RUNTIME_HASH,
                       "affordance_hash": AFFORDANCE_HASH,
                       "manifest_schema_hash": rules["schema_hash"]},
        "samples": SAMPLES, "seed": 0x5EED,
    }
    numerical = {
        "pi": {repr(list(s)): pi[s] for s in sub},
        "residual_l1": m["residual_l1"],
        "max_abs_current": max(abs(r["J"]) for r in cur),
        "total_abs_current": math.fsum(abs(r["J"]) for r in cur),
        "sigma": ep["sigma"], "one_way_edges": ep["one_way_edges"],
    }
    out = {"host": {"platform": platform.platform(), "python": sys.version.split()[0],
                    "implementation": platform.python_implementation(),
                    "machine": platform.machine()},
           "exact_layer": exact, "exact_layer_digest":
               hashlib.sha256(canonical_json(exact).encode()).hexdigest(),
           "numerical_layer": numerical,
           "numerical_layer_digest": hash_obj(numerical)}
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "REPLAY_local.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")
    print("EXACT     ", out["exact_layer_digest"])
    print("NUMERICAL ", out["numerical_layer_digest"])
    print("host      ", out["host"]["python"], out["host"]["platform"], out["host"]["machine"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
