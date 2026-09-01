"""
The messy artifact hoard (D7 section 10) for the lock-chain proof world.

Central relational property (by construction):
  * `uset` writes coord u  -> visible in SINGLE-artifact (marginal) history.
  * `spush` is GATED (if u!=0: s += r*r); with every solo/base probe starting at
    u=0, spush is INERT -> it looks like a neutral distractor in marginal history.
  * Only a PAIR of the two distinct roles (a gate-writer and a gated s-writer)
    makes coord s move.  The single-application emergent effect lives ONLY in the
    pairwise/interaction (relational) history.  (In the Gz closure BOTH orders can
    cross once iterated -- uset;spush directly, and spush;uset because a later
    application fires the gate that an earlier application opened.  Either way it
    takes two DISTINCT artifacts; no single artifact crosses.)
So a bag-of-artifacts learner (H0) undervalues spush; only intact relational
structure (H2) exposes the (uset, spush) synergy.  No artifact bundles a
u-write with a spush, so NO single artifact crosses.
"""

from __future__ import annotations
import random
from substrate import Artifact, sha
from worlds import prim_lib, R, U, S


def _pads(L):
    """Pure-r distractors (never touch u or s): varied but harmless."""
    combos = [
        ("inc_r", "inc_r"), ("dec_r", "dec_r"), ("dbl_r", "inc_r"),
        ("tpl_r", "dec_r"), ("inc_r", "dbl_r"), ("neg_r", "inc_r"),
        ("dbl_r", "dbl_r"), ("tpl_r", "tpl_r"), ("inc_r", "tpl_r"),
        ("dec_r", "dbl_r"), ("rst_r", "inc_r"), ("neg_r", "dec_r"),
        ("dbl_r", "dec_r"),
    ]
    out = []
    for i, names in enumerate(combos):
        prog = tuple(x for n in names for x in L[n])
        out.append((f"pad{i+1}", "distractor", prog))
    return out


def _behaviors(p):
    L = prim_lib(p)

    def prog(*names):
        out = []
        for n in names:
            out.extend(L[n])
        return tuple(out)

    base = [
        # ---- the two irreducible crossing ingredients ----
        ("uset",      "gate_writer",   prog("uset")),          # writes u (marginally visible)
        ("uset_dup",  "gate_writer",   prog("uset")),
        ("spush",     "s_writer_nl",   prog("spush")),         # gated; inert alone (marginally invisible)
        ("spush_dup", "s_writer_nl",   prog("spush")),
        # ---- r-controllers (steer r before firing spush) ----
        ("step",      "r_ctrl",        prog("inc_r")),
        ("step_dup",  "r_ctrl",        prog("inc_r")),
        ("reset",     "r_ctrl",        prog("rst_r")),
        ("decr",      "r_ctrl",        prog("dec_r")),
        ("dbl",       "r_ctrl",        prog("dbl_r")),
        ("tpl",       "r_ctrl",        prog("tpl_r")),
        # ---- neutral ----
        ("ident",     "neutral",       prog("inc_r", "dec_r")),
        ("noop",      "neutral",       prog("nopish")),
        ("twiddle",   "neutral",       prog("swap_rs", "swap_rs")),  # double swap = identity
        ("ident2",    "neutral",       prog("neg_r", "neg_r")),
        ("u_ident",   "neutral",       prog("udec", "uset")),        # net identity on u
        # ---- harmful / derailing (r-side red herrings) ----
        ("flip",      "harmful",       prog("neg_r")),
        ("scram",     "harmful",       prog("dbl_r", "dbl_r", "dbl_r")),
        ("p_spec",    "harmful",       (("mulk", R, 5 % p),)),       # p-dependent
        ("rsquare",   "harmful",       (("submul", R, R, R),)),      # r += r*r (into r; red herring)
    ]
    return base + _pads(L)


def build_hoard(p=13, seed=20260827, include_linear=False):
    behs = _behaviors(p)
    if include_linear:
        L = prim_lib(p)
        behs = behs + [("spush_lin", "s_writer_lin", L["spush_lin"])]
    rng = random.Random(seed)
    order = list(range(len(behs)))
    rng.shuffle(order)
    hoard, roles, labels = {}, {}, {}
    for new_i, orig_i in enumerate(order):
        label, cat, prog = behs[orig_i]
        aid = f"a{new_i:02d}"
        hoard[aid] = Artifact(aid=aid, prog=prog, origin=f"seed:{label}")
        roles[aid] = cat
        labels[aid] = label
    return hoard, roles, labels


def hoard_fingerprint(hoard):
    return sha(["HOARD", sorted([[a, list(map(list, art.prog))]
                                 for a, art in hoard.items()])])
