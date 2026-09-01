"""The Novelty Court and the causal-ablation battery.

The Court is deterministic code.  It never sees the arm label when deciding, it does not
consult the generator, and no LLM is anywhere in the promotion path.  Interpretation
(E7) happens only AFTER promotion, and its verdict cannot promote or demote.

Ablation battery (assignment section 7) -- for every candidate produced by a composition
or reuse operator that crossed a capability gate:

  1 remove parent A's contribution      5 sever/perturb the interface (splice point)
  2 remove parent B's contribution      6 scramble structure NOT on the causal path
  3 replace A with a behavioral control 7 replay A and B independently
  4 replace B with a behavioral control 8 did an ANCESTOR already hold the capability?

The purpose is to establish whether the COMPOSITION caused the capability.  Genealogical
proximity is not mechanism.
"""

from __future__ import annotations

import hashlib
import json
import random

import numpy as np

import arms as A
from arena import OUT_LO, World, fmt, run

# ------------------------------------------------------------------------ the Court


def court(world, prog, ancestors_progs, claimed):
    """Adjudicate a claimed capability set.  Returns a verdict dict.

    `ancestors_progs` is the expressed program of every recorded ancestor.
    Every check is executable and its result is a fact, not a judgement.
    """
    w = world
    v = {}

    # 1. held-out execution -- the frozen criterion, re-run here independently
    held = w.capset(prog, "heldout")
    v["heldout_capset"] = sorted(held)
    v["claim_matches_heldout"] = (set(claimed) == set(held))

    # 2. adversarial / counterfactual inputs: a DIFFERENT input distribution
    perturb = w.capset(prog, "perturb")
    v["perturb_capset"] = sorted(perturb)
    v["survives_perturbation"] = bool(set(held) <= set(perturb))

    # 3. exhaustive check on the decisive input bits.  The references depend only on
    #    single bits, so all 4 combinations of (bit7 x0, bit7 x1, bit3 x0) can be
    #    enumerated exactly -- this is a Class I check, not a sample.
    X = np.array([[a for a in range(256) for _ in range(256)],
                  [b for _ in range(256) for b in range(256)]], dtype=np.uint8)
    T = w.targets(X)
    R = run(prog, X)
    v["exhaustive_capset"] = sorted(k for k in range(w.n_slots)
                                    if np.array_equal(R[OUT_LO + k], T[k]))
    v["survives_exhaustive"] = bool(set(held) <= set(v["exhaustive_capset"]))

    # 4. transfer to a changed world (input registers swapped)
    v["transfer_capset"] = sorted(w.capset_transfer(prog))

    # 5. ancestor comparison -- did any ancestor already hold the claimed capability?
    anc_caps = set()
    for ap in ancestors_progs:
        anc_caps |= w.capset(ap, "heldout")
    v["ancestor_capset"] = sorted(anc_caps)
    v["novel_wrt_ancestors"] = sorted(set(held) - anc_caps)
    v["capability_preexisted_in_ancestor"] = bool(set(held) & anc_caps)

    # 6. contamination / leakage: does the program read its inputs at all?
    reads_input = any(b < 2 or (op in (6,) and a < 2) for op, a, b in prog) or \
        any(a < 2 for op, a, b in prog)
    v["reads_input"] = bool(reads_input)
    const_out = run(prog, np.zeros((2, 8), dtype=np.uint8))[OUT_LO:]
    v["constant_output"] = bool(all(len(np.unique(R[OUT_LO + k])) == 1
                                    for k in range(w.n_slots)))

    # 7. reproducibility from the frozen artifact
    v["replay_stable"] = bool(np.array_equal(run(prog, w.heldout), run(prog, w.heldout)))

    v["PROMOTED"] = bool(
        v["claim_matches_heldout"] and held and v["survives_exhaustive"]
        and v["replay_stable"] and not v["constant_output"])
    return v


# ------------------------------------------------------- causal ablation battery

def _behavioral_control(rng, prog, world):
    """A length-matched program with the same instruction multiset, shuffled.

    This is the control for 'is it THIS component, or just SOME component of this size?'
    """
    p = list(prog)
    rng.shuffle(p)
    return p


def ablate(world, child_prog, parent_a, parent_b, splice_hint, claimed, seed=7):
    """The eight interventions.  Returns per-intervention retained-capability sets."""
    rng = random.Random(seed)
    w = world
    base = set(w.capset(child_prog, "heldout"))
    goal = set(claimed) & base
    res = {"base_capset": sorted(base)}

    la = len(parent_a) if parent_a else 0

    def cap(p):
        return sorted(w.capset(p, "heldout"))

    # 1/2 -- remove each parent's contiguous contribution
    res["remove_parentA_prefix"] = cap(child_prog[la:]) if la else None
    res["remove_parentB_suffix"] = cap(child_prog[:la]) if la else None

    # 3/4 -- replace each parent's contribution with a behavioral control
    if la:
        ctrl_a = _behavioral_control(rng, child_prog[:la], w)
        res["parentA_replaced_by_control"] = cap(ctrl_a + child_prog[la:])
        ctrl_b = _behavioral_control(rng, child_prog[la:], w)
        res["parentB_replaced_by_control"] = cap(child_prog[:la] + ctrl_b)
    else:
        res["parentA_replaced_by_control"] = None
        res["parentB_replaced_by_control"] = None

    # 5 -- sever / perturb the interface: insert a scratch-clobbering instruction at the
    #      splice point.  If the capability depends on state flowing ACROSS the join,
    #      this kills it; if it does not, the join was decorative.
    if la and la < len(child_prog):
        clob = [(10, 2, 7), (10, 3, 7), (10, 4, 7)]     # zap all scratch at the seam
        res["interface_severed"] = cap(child_prog[:la] + clob + child_prog[la:])
    else:
        res["interface_severed"] = None

    # 6 -- scramble structure NOT on the causal path: find instructions whose removal
    #      does not change behavior, and shuffle them.  A capability that dies under this
    #      was not localised where the genealogy says it was.
    dead = []
    for i in range(len(child_prog)):
        trimmed = child_prog[:i] + child_prog[i + 1:]
        if set(w.capset(trimmed, "heldout")) >= base:
            dead.append(i)
    scrambled = list(child_prog)
    for i in dead:
        scrambled[i] = (rng.randrange(12), rng.randrange(8), rng.randrange(8))
    res["irrelevant_structure_scrambled"] = cap(scrambled)
    res["n_dead_instructions"] = len(dead)
    res["minimal_core_len"] = len(child_prog) - len(dead)

    # 7 -- replay the parents independently
    res["parentA_alone"] = cap(parent_a) if parent_a else None
    res["parentB_alone"] = cap(parent_b) if parent_b else None

    # 8 -- did the capability exist in either ancestor already?
    pa = set(res["parentA_alone"] or [])
    pb = set(res["parentB_alone"] or [])
    res["capability_in_a_parent"] = sorted(goal & (pa | pb))

    # VERDICT -- composition is causal for capability g iff g is in the child, in
    # NEITHER parent alone, and dies when either parent's contribution is removed.
    causal = []
    for g in sorted(goal):
        in_parent = g in pa or g in pb
        survives_removal = (
            (res["remove_parentA_prefix"] is not None and g in res["remove_parentA_prefix"])
            or (res["remove_parentB_suffix"] is not None and g in res["remove_parentB_suffix"]))
        if (not in_parent) and (not survives_removal):
            causal.append(g)
    res["COMPOSITION_CAUSAL_FOR"] = causal
    return res


# ------------------------------------------------------------- ontology-blind lane

KNOWN_OPS = {
    "bit7(x0)":       lambda X: ((X[0] >> 7) & 1),
    "bit7(x1)":       lambda X: ((X[1] >> 7) & 1),
    "bit3(x0)":       lambda X: ((X[0] >> 3) & 1),
    "bit7(x0)^bit7(x1)": lambda X: (((X[0] >> 7) & 1) ^ ((X[1] >> 7) & 1)),
    "bit7(x0)+bit7(x1)": lambda X: (((X[0] >> 7) & 1) + ((X[1] >> 7) & 1)),
    "bit7(x0)&bit7(x1)": lambda X: (((X[0] >> 7) & 1) & ((X[1] >> 7) & 1)),
    "bit7(x0)|bit7(x1)": lambda X: (((X[0] >> 7) & 1) | ((X[1] >> 7) & 1)),
}


def interpret(world, prog, slot):
    """POST-PROMOTION only.  Classify the mechanism against the known vocabulary.

    'Resists interpretation' is NOT evidence of novelty and is recorded as such.
    """
    X = np.array([[a for a in range(256) for _ in range(256)],
                  [b for _ in range(256) for b in range(256)]], dtype=np.uint8)
    out = run(prog, X)[OUT_LO + slot]
    matches = [name for name, f in KNOWN_OPS.items()
               if np.array_equal(out, np.asarray(f(X), dtype=np.uint8))]

    # minimal core: strip every instruction whose removal preserves the exact function
    core = list(prog)
    i = 0
    while i < len(core):
        trimmed = core[:i] + core[i + 1:]
        if np.array_equal(run(trimmed, X)[OUT_LO + slot], out):
            core = trimmed
        else:
            i += 1

    if matches:
        kind = ("behaviorally_equivalent_to_known_operation" if len(core) <= 3
                else "novel_composition_of_known_operations")
    else:
        kind = "resists_current_compression"
    return dict(classification=kind, equivalent_to=matches,
                minimal_core_len=len(core), minimal_core=fmt(core))


def _test():
    ok = True
    w = World("W2_DECEPTIVE")
    good = [(9, 2, 0), (8, 2, 7), (9, 3, 1), (8, 3, 7), (9, 7, 2), (3, 7, 3)]
    v = court(w, good, [], [2])
    ok &= v["PROMOTED"] and v["heldout_capset"] == [2] and v["survives_exhaustive"]
    print("  [%s] Court promotes a genuinely correct program" % ("PASS" if ok else "FAIL"))

    const = [(10, 7, 0)]
    v2 = court(w, const, [], [2])
    ok2 = not v2["PROMOTED"]
    ok &= ok2
    print("  [%s] Court refuses a constant program" % ("PASS" if ok2 else "FAIL"))

    # a program that is right on HELDOUT but wrong exhaustively must not promote
    it = interpret(w, good, 2)
    ok3 = it["equivalent_to"] == ["bit7(x0)^bit7(x1)"]
    ok &= ok3
    print("  [%s] interpreter identifies the known operation (core=%d)"
          % ("PASS" if ok3 else "FAIL", it["minimal_core_len"]))

    ab = ablate(w, good, good[:4], good[4:], 4, [2])
    ok4 = ab["base_capset"] == [2]
    ok &= ok4
    print("  [%s] ablation battery runs and finds the base capability"
          % ("PASS" if ok4 else "FAIL"))
    print("      minimal core %d instr, %d dead, composition causal for %s"
          % (ab["minimal_core_len"], ab["n_dead_instructions"], ab["COMPOSITION_CAUSAL_FOR"]))

    print("\n  %s" % ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_test())
