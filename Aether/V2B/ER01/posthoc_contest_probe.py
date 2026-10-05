"""ER01 POST-HOC probe (not preregistered; does not enter the disposition).

Mechanism question for the MOBILE_BUT_TRIVIAL result: is the late-time template
change in each regime carried by CONTESTED targets (>= 2 active writers aiming
at the same site and field, the winner re-drawn by the keyed arbitration hash
every tick), i.e. flicker between the contenders' fixed values?

For each regime (P0, ER01 seed k, 256^2, 5000 ticks), over the final 200 ticks,
using the frozen kernel's own observer side channel (contenders, n_differ per
field), it counts template-field changes and splits them by whether the
changed (site, field) had >= 2 contenders that tick, and whether >= 2 of those
contenders carried DIFFERENT values (a genuine choice for the re-draw to flip).

    python posthoc_contest_probe.py --out posthoc_contest_probe.json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er01_run as E  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402


def probe(regime, k, n, ticks, tail):
    xp, K = E.load_backend("gpu")
    reg = E.REGIMES[regime]
    rng_seed, phys = E.seeds_for(k)
    fields, _ = R.build_initial(E.INIT["regime"], n, n, rng_seed,
                                write_density=E.INIT["write_density"],
                                energy_mode=E.INIT["energy_mode"])
    st = [xp.asarray(f) for f in fields]
    tot = contested = differing = 0
    for t in range(ticks):
        obs = [] if t >= ticks - tail else None
        out = K.gpu_step(n, n, phys, t + 1, reg["write_cost"], reg["maintenance_cost"],
                         reg["replenish_numer"], reg["replenish_amount"], 0, *st, observer=obs)
        nxt = list(out[:5])
        if obs is not None:
            for f in range(4):
                ch = nxt[f] != st[f]
                _slot, cont, ndiff = obs[f]
                tot += int(ch.sum())
                contested += int((ch & (cont >= 2)).sum())
                # >= 2 contenders and at least one offering a value != current:
                # with >= 2 distinct offers the re-draw can flip the site back and forth.
                differing += int((ch & (cont >= 2) & (ndiff >= 1)).sum())
        st = nxt
    return {"regime": regime, "seed_index": k, "n": n, "ticks": ticks, "tail": tail,
            "template_changes": tot,
            "share_on_contested_targets": contested / tot if tot else None,
            "share_contested_with_alternative": differing / tot if tot else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--tail", type=int, default=200)
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for r in sorted(E.REGIMES):
        for k in [int(s) for s in a.seeds.split(",")]:
            rows.append(probe(r, k, a.n, a.ticks, a.tail))
            print(json.dumps(rows[-1]), file=sys.stderr, flush=True)
    json.dump({"schema": "aether.er01.posthoc_contest.v1", "posthoc": True, "rows": rows},
              open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
