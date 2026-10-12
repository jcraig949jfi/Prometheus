"""C-018-T040 challenge natives: the FROZEN recorder (adapter.native_unit) on Pallas's own seed range, evaluated by the
FROZEN evaluator, plus per-unit observations the evaluator does not report (first ticks of B / N / targets, the share of
targets a late N could never remove, horizon counterfactuals on the stored arrays, the ranked non-ancestor candidates).

    python -B -m rso.aether.challenge.natives <scratch> <LAW> <i0> <i1>      units k = 0x3000 + i, i in [i0, i1)

Seeds: k = 0x3000 + i (adapter.SEEDS bases: rng 0xC30A3000+i, phys 0xC30B3000+i, impulse domain 0xC30E3000+i). Disjoint
from adapter.DEV_K (0..15), confirm.BURNED (0x1000..0x10FF), the confirmatory k = 0x2000..0x202F, Cadmus's 0xC18A..0xC18E
bases and every Aether constant (grep'd: no 0x30xx / 0xC30?3? constant under Aether/ or rso/). Labels 0x3100..0x31FF are
reserved for forged copies (forge.py) and are never executed. Units are written to <scratch>/units (not committed: ~1.4
MB each); the evaluated rows go to <scratch>/rows_<LAW>_<i0>_<i1>.jsonl and are committed by cases.py.
These are DEVELOPMENT-class observations on new seeds. They are not the confirmatory result and must not be read as one.
"""
import json
import os
import sys
import time

import numpy as np

from rso.aether import adapter as A, evaluate as E
from rso.aether.challenge import synth as S
import prop01_tree as TR           # noqa: E402

K0 = 0x3000


def n_candidates(tree, B, O, n):
    """The non-ancestor candidate list in the frozen rule's own order (adapter.py:54-63), not just its minimum."""
    par = dict(zip(tree["site"], tree["parent"]))
    desc = TR.descendants(tree, B)
    anc, p = set(), par.get(B, -1)
    while p is not None and p >= 0:
        anc.add(p)
        p = par.get(p)
    dB = A.cheb(n, B, O)
    return sorted((abs(A.cheb(n, s, O) - dB), t, s) for s, g, t in zip(tree["site"], tree["gen"], tree["ftick"])
                  if g >= 1 and s != B and s != O and s not in desc and s not in anc)


def extras(meta, a):
    tr, n, O = meta["tree"], meta["n"], meta["origin"]
    imp, cb, cn = a["ftick_impulse"], a["ftick_cutB"], a["ftick_cutN"]
    B, bt = TR.choose_cut({"tree": tr})
    out = {"n_sites": len(tr["site"]), "max_gen": int(max(tr["gen"])), "n_unknown": sum(1 for g in tr["gen"] if g == -1),
           "ever_radius": int(max(A.cheb(n, s, O) for s in tr["site"])), "B": B, "ftick_B": bt, "N": meta["N"],
           "ftick_N": int(imp[meta["N"]]) if meta["N"] is not None else None, "invariants": S.tree_invariants(tr, n),
           "gen1_types": sorted(int(ty) for g, ty in zip(tr["gen"], tr["type"]) if g == 1),
           "gen2_types": sorted(int(ty) for g, ty in zip(tr["gen"], tr["type"]) if g == 2)}
    if B is None:
        return out
    tg = sorted(TR.descendants(tr, B))
    tks = [int(imp[s]) for s in tg]
    ftN = out["ftick_N"]
    out.update(n_targets=len(tg), targets_ftick_min=min(tks), targets_ftick_max=max(tks),
               n_targets_after_300=sum(1 for t in tks if t > 300), n_targets_after_200=sum(1 for t in tks if t > 200),
               n_targets_removed_B=sum(1 for s in tg if cb[s] < 0), n_targets_removed_N=sum(1 for s in tg if cn[s] < 0),
               n_targets_before_N=None if ftN is None else sum(1 for t in tks if t <= ftN),
               n_targets_live_for_N=None if ftN is None else sum(1 for t in tks if t > ftN),
               n_targets_removed_N_live=None if ftN is None else sum(1 for s in tg if int(imp[s]) > ftN and cn[s] < 0),
               N_candidates=[[int(d), int(t), int(s)] for d, t, s in n_candidates(tr, B, O, n)[:4]])
    for Hp in (100, 200, 300):
        r2 = E.ancestry(meta, S.truncate(a, Hp))
        out["cls_H%d" % Hp], out["r_int_H%d" % Hp] = r2["cls"], r2["r_int"]
    return out


def run(scratch, law, i0, i1):
    ud = os.path.join(scratch, "units")
    os.makedirs(ud, exist_ok=True)
    rows_path = os.path.join(scratch, "rows_%s_%d_%d.jsonl" % (law, i0, i1))
    for i in range(i0, i1):
        k = K0 + i
        t = time.time()
        meta, arrays = A.native_unit(law, k)
        meta = A.save_unit(os.path.join(ud, "native_%s_%d" % (law, k)), meta, arrays)
        r = E.evaluate_unit(meta, arrays)
        r.update(k_hex=hex(k), wall_s=round(time.time() - t, 1), arrays_sha256=meta["arrays_sha256"], extras=extras(meta, arrays))
        with open(rows_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
        print(law, hex(k), r["cls"], "sites", r["extras"]["n_sites"], "gen", r["extras"]["max_gen"], "problems", len(r["problems"]),
              "%.0fs" % r["wall_s"], file=sys.stderr, flush=True)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
