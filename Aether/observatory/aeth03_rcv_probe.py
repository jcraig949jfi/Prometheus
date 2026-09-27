"""POST HOC, descriptive: what carries `rcv`'s multi-generation spread?

Run after the ladder-2 verdict, whatever it was, and labelled post hoc.
Under `rcv` a site that received a winning template write last tick emits
this tick even if it is inert. A written inert site therefore writes
another site, which then emits, and so on: a receipt-triggered emission
chain that can cross inert matter. This probe measures, with perturbation
OFF, from the same warmed worlds and origins as the assay:

  baseline  share of active sites that are receipt-activated (opcode not
            WRITE) at the fork;
  spread    for every newly differing site in the twin runs: whether it
            is inert (opcode not WRITE in world A at that tick), whether
            it is receipt-active in either world on the next tick, and
            which fields differ -- split by causal generation (1 vs >= 2).

Nothing here is a test; it describes the mechanism behind an observation.
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

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_scouts as S               # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--seed-index", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    n = a.n
    seed, rng_seed = S.SEED0 + a.seed_index, S.RNG0 + a.seed_index
    rng = np.random.default_rng(0xB0A7 + a.seed_index)     # same origins as assay
    par_on, par_off = S.params(seed, S.MUT_ON), S.params(seed, 0)
    w = P.World("rcv", S.initial("rcv", n, rng_seed))
    for t in range(1, a.warmup + 1):
        w.step(t, par_on)
    wc = par_on["write_cost"]
    energy_ok = w.f[4].astype(np.int64) >= wc
    by_opcode = (w.f[0] == K.WRITE_OPCODE) & energy_ok
    by_receipt = w.received & energy_ok & (w.f[0] != K.WRITE_OPCODE)
    em = S.emitters("rcv", w.f, wc) | (w.received & energy_ok)
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(a.origins, len(cand)), replace=False)]
    specs = [(tuple(int(x) for x in p), int(rng.integers(5)), int(rng.integers(8)))
             for p in pick]
    acc = {g: {"new": 0, "inert": 0, "receipt_active_next": 0,
               "fields": [0] * 6} for g in ("gen1", "gen_ge2")}
    for origin, field, bit in specs:
        A, B = w.copy(), w.copy()
        B.f[field][origin] ^= np.uint8(1 << bit)
        site, _ = P.diff_masks(A, B)
        gen = np.where(site, np.int32(0), P.BIG)
        for t in range(1, a.ticks + 1):
            prev_site, prev_gen = site, gen
            op_before = A.f[0].copy()
            A.step(a.warmup + t, par_off)
            B.step(a.warmup + t, par_off)
            site, per_field = P.diff_masks(A, B)
            newly = site & ~prev_site
            pmin = P.neighbour_min(np.where(prev_site, prev_gen, P.BIG))
            gen = np.where(site & prev_site, prev_gen, P.BIG)
            gen = np.where(newly, pmin + 1, gen)
            if not newly.any():
                continue
            for key, m in (("gen1", newly & (gen == 1)),
                           ("gen_ge2", newly & (gen >= 2) & (gen < P.BIG))):
                k = int(m.sum())
                if not k:
                    continue
                g = acc[key]
                g["new"] += k
                g["inert"] += int((m & (op_before != K.WRITE_OPCODE)).sum())
                g["receipt_active_next"] += int((m & (A.received | B.received)).sum())
                for i in range(5):
                    g["fields"][i] += int((m & per_field[i]).sum())
                g["fields"][5] += int((m & (A.received != B.received)).sum())
    out = {"post_hoc": True, "n": n, "seed_index": a.seed_index,
           "baseline": {"active_by_opcode": int(by_opcode.sum()),
                        "active_by_receipt_only": int(by_receipt.sum()),
                        "receipt_share_of_active": float(
                            by_receipt.sum() / max(1, (by_opcode | by_receipt).sum()))},
           "spread": {k: dict(v, fields_names=["opcode", "arg0", "arg1", "payload",
                                               "energy", "received_flag"])
                      for k, v in acc.items()}}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
