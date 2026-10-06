"""AIM01 POST-HOC probe (NOT preregistered; does not change the frozen disposition).

Self-attack on the REAIM_NONTRIVIAL_CANDIDATE result. EFFECT reads arg0 as (arg0 - c), where c counts re-aims. A writer
X whose arg0 is repeatedly reset by a neighbour to the same raw value P, re-aiming in between (raw P -> P+1 -> P ...),
produces an EFFECT change at every reset, and those EFFECT states drift with c, so they look "novel" while the RAW
byte merely cycles. That is a re-aim/reset counting cycle, a trivial dynamic the frozen attack could miss. This
probe measures the medium WITHOUT arg0 at all:

  nonaim = (opcode, arg1, payload) only -- fields the law never touches.
  ever_nonaim, late_turnover_nonaim, frozen_strict_nonaim (last LATE ticks), novelty_nonaim (tail 64, memory 16).
  arg0_reset_share: among late EFFECT arg0 changes, the share whose new RAW arg0 equals a raw value the site held in
                    its previous 16 ticks (a reset to a recently held value).

Same seeds, laws, densities and kernel as production; 512^2; shorter horizon (support saturates < 50 ticks and is
stationary to 30k in production, so 5000 ticks with a 1000-tick late window measures the same steady state).

    python posthoc_nonaim_probe.py --out production/posthoc_nonaim_probe.json
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aim01_run as A  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402


def probe(law, dens, k, n, T, late, tail=64, depth=16):
    xp, K = A.load_backend("gpu")
    fields, _ = R.build_initial(R.SPARSE_SOUP, n, n, A.RNG_SEED_BASE + k,
                                write_density=A.DENSITIES[dens], energy_mode=R.ENERGY_UNIFORM)
    s = [xp.asarray(f) for f in fields]
    phys = A.PHYS_SEED_BASE + k
    c = xp.zeros((n, n), dtype=xp.uint8)
    pk = lambda st: (st[0].astype(xp.uint32) << 16) | (st[2].astype(xp.uint32) << 8) | st[3].astype(xp.uint32)  # noqa: E731
    ever_na = xp.zeros((n, n), dtype=bool)
    ever_eff = xp.zeros((n, n), dtype=bool)
    late_na = xp.zeros((n, n), dtype=bool)
    late_na_count = 0
    ring_na, ring_a0 = [], []
    tail_ch = tail_nov = 0
    a0_late = a0_reset = 0
    t0 = time.time()
    for t in range(T):
        nxt, reaim, tgt = A.law_step(xp, K, law, n, phys, t + 1, s)
        c2 = c if reaim is None else c + reaim.astype(xp.uint8)
        ch_na = (nxt[0] != s[0]) | (nxt[2] != s[2]) | (nxt[3] != s[3])
        e_prev = (s[1].astype(xp.int16) - c.astype(xp.int16)) % 256
        e_next = (nxt[1].astype(xp.int16) - c2.astype(xp.int16)) % 256
        ch_a0 = e_prev != e_next
        ever_na |= ch_na
        ever_eff |= ch_na | ch_a0
        if t >= T - tail - depth:
            ring_na = (ring_na + [pk(s)])[-depth:]
        if t >= T - late - depth:
            ring_a0 = (ring_a0 + [s[1]])[-depth:]
        if t >= T - late:
            late_na |= ch_na
            late_na_count += int(ch_na.sum())
            seen = xp.zeros((n, n), dtype=bool)
            for r in ring_a0:
                seen |= (r == nxt[1])
            a0_late += int(ch_a0.sum())
            a0_reset += int((ch_a0 & seen).sum())
        if t >= T - tail:
            cur = pk(nxt)
            seen = xp.zeros((n, n), dtype=bool)
            for r in ring_na:
                seen |= (r == cur)
            tail_ch += int(ch_na.sum())
            tail_nov += int((ch_na & ~seen).sum())
        s, c = nxt, c2
    N = n * n
    return {"law": law, "dens": dens, "seed": k, "n": n, "ticks": T, "late": late,
            "ever_nonaim": int(ever_na.sum()) / N, "ever_eff": int(ever_eff.sum()) / N,
            "late_turnover_nonaim": late_na_count / (late * N),
            "frozen_strict_nonaim": 1 - int(late_na.sum()) / N,
            "novelty_nonaim": tail_nov / tail_ch if tail_ch else None,
            "arg0_late_eff_changes": a0_late, "arg0_reset_share": a0_reset / a0_late if a0_late else None,
            "final_digest": A.digest(s), "seconds": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--late", type=int, default=1000)
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--only", default=None, help="law:dens:seed for one unit (driver use)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.only:
        law, dens, k = a.only.split(":")
        rows = [probe(law, dens, int(k), a.n, a.ticks, a.late)]
    else:
        rows = [probe(law, d, k, a.n, a.ticks, a.late) for law in ("L0", "L1") for d in ("D25", "D50", "D75")
                for k in [int(x) for x in a.seeds.split(",")]]
    json.dump({"schema": "aether.aim01.posthoc_nonaim.v1", "posthoc": True, "rows": rows}, open(a.out, "w"), indent=1)
    for r in rows:
        print(json.dumps(r), file=sys.stderr)


if __name__ == "__main__":
    main()
