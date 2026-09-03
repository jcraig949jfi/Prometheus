"""NEGATIVE CONTROL for the replay contract: could it have failed?

A passing replay proves nothing unless the compared quantities are actually runtime-sensitive.
This re-runs the identical replay computation with math.fsum replaced by the builtin sum inside
the equilibrium module, on each runtime. CPython 3.12 changed builtins.sum to compensated
(Neumaier) summation for floats; 3.11 did not. If the digests STILL agree, the replay is
insensitive and its PASS is uninformative. If they disagree, the contract has demonstrated power.

    python proteus/v0_6/run_replay_sensitivity.py out.json

Bounded: the same tol and max_iters on both runtimes, so a capped solve is still an
apples-to-apples comparison of the two runtimes' arithmetic.
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

from proteus.foundry.identity import canonical_json  # noqa: E402
from proteus.v0_6 import equilibrium as EQ  # noqa: E402
from proteus.v0_6 import livekernel as LK  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

SAMPLES, TOL, MAX_ITERS = 3000, 1e-12, 200_000


class _NoFsum:
    """math with fsum swapped for the builtin sum -- the arithmetic V0.5 actually used."""

    def __getattr__(self, k):
        return getattr(math, k)

    fsum = staticmethod(sum)


def main():
    EQ.math = _NoFsum()
    states, _tapes, _rules = space.regenerate_states()
    sub = [s for s in states if s[1] <= 32]
    P, _OP, _NOOP, _ESC = LK.measure_kernel_parallel(sub, SAMPLES, 0x5EED, "replay", workers=2)
    pi, m = EQ.stationary_power(P, sub, tol=TOL, max_iters=MAX_ITERS)
    cur = EQ.currents(P, pi, sub)
    ep = EQ.entropy_production(P, pi, sub)
    ep.pop("_by_edge", None)
    num = {"pi": {repr(list(s)): pi[s] for s in sub}, "residual_l1": m["residual_l1"],
           "max_abs_current": max(abs(r["J"]) for r in cur),
           "total_abs_current": sum(abs(r["J"]) for r in cur),
           "sigma": ep["sigma"], "one_way_edges": ep["one_way_edges"]}
    out = {"host": {"python": sys.version.split()[0],
                    "implementation": platform.python_implementation(),
                    "platform": platform.platform()},
           "fsum_disabled": True, "n_sub_states": len(sub),
           "tol": TOL, "max_iters": MAX_ITERS, "iterations": m["iterations"],
           "converged": m["residual_l1"] <= TOL,
           "numerical_layer": num,
           "numerical_layer_digest": hashlib.sha256(canonical_json(num).encode()).hexdigest()}
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "SENSITIVITY_local.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"{out['host']['python']:<8} digest {out['numerical_layer_digest']} "
          f"iters {m['iterations']} residual {m['residual_l1']:.3e} sigma {num['sigma']:.17g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
