"""H3-X: is the arg1 cycle deficit driven by perturbation of arg1 writes?

POST HOC, labelled so. `aeth02_closure.py` at 256^2 found realized cycles
0.37x both nulls, with the deficit concentrated in opcode-field cycle
edges (0.006x null) and -- NOT predicted by H3-P2 -- arg1-field cycle
edges (0.002x null). In the relaxation probe, opcode cycle edges vanish
within ~10 ticks of a direction shuffle, while arg1 cycle edges decay
slowly and are still falling at +60.

Two mechanisms, both read off the frozen text:

  OPCODE  a cycle member is written every tick by its predecessor; an
          opcode-field write stores the predecessor's payload, which
          deactivates the member unless payload == WRITE. Deterministic:
          needs no perturbation.
  ARG1    an arg1-field write sets the member's own target-field selector.
          Every single-bit perturbation of an arg1 value changes it mod 5
          (freeze candidate s9, falsification gate K2), so each perturbed
          arg1 write re-picks which field the member itself writes, and
          sooner or later picks a destructive one (opcode/arg0) for the
          next member. Driven by perturbation.

TEST. From one stationary snapshot, shuffle directions among active
emitters (the closure's Null B) and relax forward 100 ticks, once with
perturbation ON and once OFF (`mut_numer` is a run parameter; the law is
unchanged). Repeat from several shuffles. Count cycle edges by field.

PREDICTION: arg1 cycle edges at +100 retain far more of their +1 count
with perturbation OFF than ON; opcode cycle edges collapse in BOTH.
FALSIFIED IF: arg1 retention(OFF) <= 1.5 x retention(ON), or opcode
retention(OFF) > 0.25 (then the opcode mechanism is not deterministic).
"""

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth02_closure as C              # noqa: E402
from observatory import aeth02_falsifiers as F           # noqa: E402

HORIZONS = (1, 5, 10, 20, 50, 100)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--warmup", type=int, default=2500)
    ap.add_argument("--shuffles", type=int, default=4)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    n = a.n
    seed, rng_seed = F.B_SEED0 + a.seed_index, F.B_RNG0 + a.seed_index
    base = F.run(n, a.warmup, seed=seed, rng_seed=rng_seed, track_runs=False)
    tick = base["tick"]
    arms = {}
    for name, mut in (("perturbation_on", F.MUT_NUMER), ("perturbation_off", 0)):
        par = F.params(seed, mut)
        rng = np.random.default_rng(0x3A1 + a.seed_index)   # same shuffles both arms
        acc = {h: [0] * 5 for h in HORIZONS}
        for _ in range(a.shuffles):
            _c, _pf, cur = C.shuffle_null(base["fields"], tick + 1, par, rng)
            for k in range(1, max(HORIZONS) + 1):
                cur, obs = F.step(cur, tick + k, par)
                if k in HORIZONS:
                    nxt = G.realized_map(np, obs, n, n)
                    _on, _cnt, pf = C.cycle_stats(nxt, C.field_of_source(obs, n))
                    acc[k] = [x + y for x, y in zip(acc[k], pf)]
        arms[name] = {str(h): dict(zip(C.FIELDS, acc[h])) for h in HORIZONS}

    def retention(arm, field):
        first = arms[arm]["1"][field]
        return arms[arm]["100"][field] / float(first) if first else None

    ret = {arm: {f: retention(arm, f) for f in C.FIELDS} for arm in arms}
    arg1_on, arg1_off = ret["perturbation_on"]["arg1"], ret["perturbation_off"]["arg1"]
    falsified = (arg1_off is None or arg1_on is None
                 or arg1_off <= 1.5 * max(arg1_on, 1e-9)
                 or (ret["perturbation_off"]["opcode"] or 0) > 0.25)
    out = {"n": n, "warmup": a.warmup, "shuffles": a.shuffles,
           "seed_index": a.seed_index, "semantics": "aeth01.v1",
           "post_hoc": True, "cycle_edges_by_field": arms,
           "retention_1_to_100": ret, "falsified": falsified}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"retention_1_to_100": ret, "falsified": falsified}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
