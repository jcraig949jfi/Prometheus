"""V0.6 section 3: regenerate the valid structural space, compare, and PROVE closure.

    python proteus/v0_6/run_space_audit.py

Writes RESULT_SPACE_AUDIT.json. The required precondition is
ESCAPED_VALID_STRUCTURAL_STATE_COUNT = 0; a single valid escape is an instrument failure.
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

CLOSURE_SAMPLES = 400


def main():
    t0 = time.time()
    states, tapes, rules = space.regenerate_states()
    ident = space.space_identity(states)
    cmp_prior = space.compare_with_prior(states)
    print(f"regenerated {ident['n_states']} states over tapes {tapes}")
    print(f"  hash {ident['hash'][:16]}  matches prior enumeration: "
          f"{cmp_prior['set_matches']} (prior n={cmp_prior['prior_n']})")

    # closure: sample every state and ledger any destination outside the set
    P, OP, NOOP, ESC = LK.measure_kernel_parallel(states, CLOSURE_SAMPLES,
                                                  seed=0xC105, tag="closure")
    escaped_states = sorted({tuple(j) for row in ESC.values() for j in row})
    escaped_count = sum(sum(row.values()) for row in ESC.values())
    print(f"  closure probe: {CLOSURE_SAMPLES} mutations x {len(states)} states = "
          f"{CLOSURE_SAMPLES*len(states):,} proposals")
    print(f"  ESCAPED_VALID_STRUCTURAL_STATE_COUNT = {escaped_count}")

    # support statistics, needed to size the production run
    supp = sorted(len(row) for row in P.values())
    n = len(supp)
    out = {
        "schema_version": "proteus.v0_6_space_audit.v1",
        "published_rules": rules,
        "tapes": tapes,
        "space_identity": ident,
        "comparison_with_prior_enumeration": cmp_prior,
        "closure": {
            "samples_per_state": CLOSURE_SAMPLES,
            "total_proposals": CLOSURE_SAMPLES * len(states),
            "escaped_valid_structural_state_count": escaped_count,
            "escaped_destinations": [list(s) for s in escaped_states][:50],
            "precondition_met": escaped_count == 0,
        },
        "support": {"min": supp[0], "median": supp[n // 2], "mean": sum(supp) / n,
                    "p90": supp[int(0.90 * n)], "max": supp[-1]},
        "noop_reasons_observed": sorted({k for row in NOOP.values() for k in row}),
        "identities": {"grammar_version": grammar.GRAMMAR_VERSION,
                       "grammar_hash": grammar.GRAMMAR_HASH,
                       "runtime_hash": RUNTIME_HASH, "affordance_hash": AFFORDANCE_HASH},
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "RESULT_SPACE_AUDIT.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"  support size: min {supp[0]} median {supp[n//2]} mean {sum(supp)/n:.1f} "
          f"p90 {supp[int(0.90*n)]} max {supp[-1]}")
    print(f"  noop reasons: {out['noop_reasons_observed']}")
    print(f"wrote RESULT_SPACE_AUDIT.json ({out['wall_s']:.0f}s)")
    return 0 if escaped_count == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
