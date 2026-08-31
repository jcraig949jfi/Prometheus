"""Post-run human-taxonomy red team (charter s.26-27).

Runs AFTER the binding run. Applies recognizable human edit-family
classifications retrospectively and asks adversarially whether the frozen
physics hides designed corridors the intrinsic assays missed. Results can
WEAKEN a PASS (downgrade narrative to privilege concern); they can never
strengthen anything. OTHER/UNKNOWN is never counted as novelty.

Diagnostic sample only — separate RNG stream, not part of any gate, no
frozen artifact is touched.

Questions asked:
1. Does one menu operator effectively implement one human edit family?
   (per-op distribution over decoded-field change families)
2. Are I/O-semantics edits (changes to the count of IN/OUT instructions —
   the designer's chosen I/O primitives) suspiciously cheap as a route to
   behavioral displacement, relative to non-I/O edits?
3. What fraction of large displacements (d1 > 0.3) are attributable to
   I/O-count changes vs other decoded changes?

Usage: python classifiers/human_taxonomy_redteam.py S1_REG ...
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from d4core.interface import Meter  # noqa: E402
from substrates.vm_substrates import SUBSTRATES, S1Reg, S2Stack, S3Rewrite, S4Mem  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def decoded_profile(sub, genome):
    """Human-side decoded summary: counts of instruction classes."""
    if isinstance(sub, S1Reg):
        ops = [((sub._decode_byte(genome[2 * i]) | (sub._decode_byte(genome[2 * i + 1]) << 8)) >> 12) & 0xF
               for i in range(sub.NWORDS)]
        io = sum(1 for o in ops if o in (12, 13))
        ctrl = sum(1 for o in ops if o in (9, 10, 11, 15))
        return ops, io, ctrl
    if isinstance(sub, S2Stack):
        ops = [(sub._decode_byte(b) >> 5) & 7 for b in genome]
        io = sum(1 for o in ops if o in (6, 7))
        ctrl = sum(1 for o in ops if o in (4, 5))
        return ops, io, ctrl
    if isinstance(sub, S4Mem):
        ops = [sub._decode_byte(b) & 7 for b in genome]
        io = sum(1 for o in ops if o in (4, 5))
        ctrl = sum(1 for o in ops if o in (6, 7))
        return ops, io, ctrl
    if isinstance(sub, S3Rewrite):
        # rules: active-rule count as "control"; no I/O primitives exist
        act = 0
        for i in range(sub.NRULES):
            b2 = sub._decode_byte(genome[3 * i + 2])
            if (b2 >> 3) & 1:
                act += 1
        return [], 0, act
    raise ValueError


def family(sub, g_parent, g_child):
    """Human edit family of a transition, from decoded profiles."""
    ops_p, io_p, ctrl_p = decoded_profile(sub, g_parent)
    ops_c, io_c, ctrl_c = decoded_profile(sub, g_child)
    fams = []
    if io_c != io_p:
        fams.append("IO_COUNT")
    if ctrl_c != ctrl_p:
        fams.append("CONTROL_COUNT")
    if ops_p and ops_c:
        changed = sum(1 for a, b in zip(ops_p, ops_c) if a != b)
        if changed > 0 and not fams:
            fams.append("OPCODE_OTHER")
        if changed == 0 and not fams:
            fams.append("OPERAND_ONLY")
    if not fams:
        fams.append("OTHER_UNKNOWN")
    return "+".join(sorted(fams))


def analyze(name: str, n_parents: int = 1500, reps: int = 3) -> dict:
    sub = SUBSTRATES[name]()
    sub.bind_meter(Meter())
    rng = np.random.default_rng(777_001)
    parents = []
    tries = 0
    while len(parents) < n_parents and tries < n_parents * 400:
        g = sub.random_genome(rng)
        f = sub.evaluate(g)
        tries += 1
        if sub.viable(f):
            parents.append((g, f))
    fam_by_op: dict = {}
    disp_by_fam: dict = {}
    big_by_fam: dict = {}
    for g, f in parents:
        for op in range(sub.n_ops):
            for _ in range(reps):
                child = sub.mutate(g, op, rng)
                fc = sub.evaluate(child)
                if sub.pkey(fc) == sub.pkey(f):
                    continue
                fam = family(sub, g, child)
                d = sub.d1(f, fc)
                fam_by_op.setdefault(op, {}).setdefault(fam, 0)
                fam_by_op[op][fam] += 1
                disp_by_fam.setdefault(fam, []).append(d)
                if d > 0.3:
                    big_by_fam[fam] = big_by_fam.get(fam, 0) + 1
    # Q1: does an operator concentrate in one family?
    op_concentration = {}
    for op, fams in fam_by_op.items():
        tot = sum(fams.values())
        top = max(fams.items(), key=lambda kv: kv[1]) if fams else (None, 0)
        op_concentration[op] = {"n": tot, "top_family": top[0],
                               "top_share": top[1] / tot if tot else None}
    # Q2/Q3
    disp_stats = {fam: {"n": len(v), "d1_mean": float(np.mean(v)),
                        "d1_median": float(np.median(v))}
                  for fam, v in disp_by_fam.items()}
    big_total = sum(big_by_fam.values())
    big_share = {fam: c / big_total for fam, c in big_by_fam.items()} if big_total else {}
    return {
        "substrate": name, "n_parents": len(parents),
        "q1_operator_family_concentration": op_concentration,
        "q2_displacement_by_family": disp_stats,
        "q3_large_displacement_share_by_family": big_share,
        "reading": "adversarial only: high top_share for a menu operator, or "
                   "IO_COUNT dominating large displacements, weakens a PASS "
                   "narrative; nothing here strengthens any verdict",
    }


def main(names):
    out = {}
    for name in names:
        out[name] = analyze(name)
        print(name, "done")
    with open(os.path.join(BASE, "results", "human_taxonomy_redteam.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or list(SUBSTRATES.keys()))
