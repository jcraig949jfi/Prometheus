"""OFFER01 planned attack (declared in the preregistration; descriptive; not part of the rule).

Is L2 (reaim1 + exchange) a BYTE SHUFFLER? Exchange turns a winning template write into a swap (writer payload <->
displaced target byte), so the multiset of template bytes is (nearly) conserved and values move like tokens.
Measures for L1, X, L2 (seed k, 512^2):
  conservation: L1 distance between the global template-byte histograms (opcode, arg0, arg1, payload) at window start
                (tick T-W) and window end (tick T), normalized by the number of bytes; and the same for payload alone.
  diversity:    distinct byte values present in the payload field; Shannon entropy of the payload histogram.
  spreading:    for each of 8 payload byte values that are rare at window start (fewest occupied sites, > 0), the mean
                torus distance between their window-start sites' centroid... (simplified): the fraction of window-end
                sites holding that value which held it at window start (positional persistence of tokens).
  swap share:   share of late winning template writes that were swaps (uptake applied) -- from the unit counts.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import offer01_run as O  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402


def ent(h):
    p = h[h > 0] / h.sum()
    return float(-(p * np.log2(p)).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=0)
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--T", type=int, default=6000)
    ap.add_argument("--W", type=int, default=2000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    xp, K = O.load_backend("gpu")
    out = {"posthoc": False, "declared_attack": True, "k": a.k, "n": a.n, "T": a.T, "W": a.W, "laws": {}}
    for law in ("L1", "X", "L2"):
        f, _ = R.build_initial(R.SPARSE_SOUP, a.n, a.n, O.RNG_SEED_BASE + a.k, write_density=O.DENSITY,
                               energy_mode=R.ENERGY_UNIFORM)
        s = [xp.asarray(x) for x in f]
        snaps = {}
        for t in range(a.T):
            s = O.law_step(xp, K, law, a.n, O.PHYS_SEED_BASE + a.k, t + 1, s)[0]
            if t + 1 in (a.T - a.W, a.T):
                snaps[t + 1] = [np.asarray(x.get()) for x in s]
        A, B = snaps[a.T - a.W], snaps[a.T]
        ha = sum(np.bincount(A[i].ravel(), minlength=256) for i in range(4))
        hb = sum(np.bincount(B[i].ravel(), minlength=256) for i in range(4))
        pa = np.bincount(A[3].ravel(), minlength=256)
        pb = np.bincount(B[3].ravel(), minlength=256)
        occ = [(int(pa[v]), v) for v in range(256) if pa[v] > 0]
        rare = [v for _c, v in sorted(occ)[:8]]
        persist = []
        for v in rare:
            sa = A[3] == v
            sb = B[3] == v
            persist.append(float((sa & sb).sum() / max(1, sb.sum())))
        out["laws"][law] = {
            "tmpl_hist_L1_per_byte": float(np.abs(ha - hb).sum() / ha.sum()),
            "payload_hist_L1_per_byte": float(np.abs(pa - pb).sum() / pa.sum()),
            "payload_distinct_start_end": [int((pa > 0).sum()), int((pb > 0).sum())],
            "payload_entropy_start_end": [ent(pa), ent(pb)],
            "rare_value_positional_persistence_median": float(np.median(persist)),
            "rare_values": rare,
        }
        print(law, json.dumps(out["laws"][law]), file=sys.stderr, flush=True)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
