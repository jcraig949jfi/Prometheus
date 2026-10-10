"""WTP-05 world admission (PREREG_WTP05 s5; directive s12). For every world variant:
  planted solver: lifetime accuracy on the scored gates and its certified rung (expressibility, solvability,
                  minimum-mechanism size = planted node count);
  null ladder N0-N4 (+ N6 reference);
  H_null = (best bounded cheap null N0-N4 - chance) / (oracle - chance), oracle = 1 (noiseless worlds;
           family C's oracle knows the switch).
Label: GOLDILOCKS if .2 <= H_null <= .8; TRIVIAL if > .8; DESERT_CONTROL if < .2 and the planted solver is
small (<= 40 nodes) and certifies; INACCESSIBLE if < .2 and no bounded planted solver certifies.
    python -m ensorain.wtp5.admit <out.json> spec [spec ...]"""
import json
import sys

import numpy as np

from .certify import certify
from .nulls import ladder
from .planted import planted
from .tape import lifetime, n_nodes
from .worlds import make


def admit(spec, seed=6_100_000):
    w = make(spec)
    fam, rung, cond = spec.split("-")
    gp = planted(w)
    rng = np.random.default_rng(seed)
    w.new_life(rng)
    life = lifetime(gp, w, rng)
    cert = certify(gp, fam, rung, seed + 1)
    lad = ladder(w, seed + 2)
    bounded = {k: v["scored"] for k, v in lad.items() if k.startswith(("N0", "N1", "N2", "N3", "N4"))}
    best = max(bounded.values())
    H = (best - 0.5) / 0.5
    ok = cert.get("switch_tracked") if fam == "C" else cert["rung"] >= int(rung[1])
    if fam == "C":
        ok = life["R"] > best          # C: the plastic constructed solution must beat every static null
    if H > 0.8:
        label = "TRIVIAL"
    elif H >= 0.2:
        label = "GOLDILOCKS"
    elif ok and n_nodes(gp) <= 40:
        label = "DESERT_CONTROL"
    else:
        label = "INACCESSIBLE"
    return dict(spec=spec, planted_nodes=n_nodes(gp), planted_R=life["R"], planted_roles=life["roles"],
                planted_rung=cert["rung"], planted_ok=bool(ok), c_late=cert.get("c_late_type1"),
                nulls=lad, best_bounded_null=best, H_null=H, label=label)


if __name__ == "__main__":
    out = [admit(s) for s in sys.argv[2:]]
    json.dump(out, open(sys.argv[1], "w"), indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x))
    for r in out:
        print(r["spec"], r["label"], "H_null %.2f" % r["H_null"], "planted", r["planted_nodes"], "nodes R %.2f" % r["planted_R"], "rung", r["planted_rung"])
