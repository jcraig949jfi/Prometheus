"""
World + primitive-library definitions.  Everything here is frozen physics.

PROOF WORLD (W-PROOF) is a 3-register lock-chain machine designed so that NO
single artifact can cross the barrier even with unlimited base help:

  reg[0] = r   (freely controllable by base physics)
  reg[1] = u   (a GATE; base cannot touch it)
  reg[2] = s   (the locked coordinate; base cannot touch it)

  * base physics = r-only ops  =>  u and s are BOTH conserved by base.
  * the ONLY s-writer is `spush`:  if u != 0:  s += r*r        (NONLINEAR + GATED)
  * the ONLY u-writer is `uset`:   u += 1
  So writing s REQUIRES first lifting the gate with a DIFFERENT artifact (uset),
  in the right ORDER, then steering r and firing spush.  A lone spush is a no-op
  (gate shut); a lone uset never touches s.  Crossing is irreducibly compositional
  and nonlinear/context-dependent.

Coordinate indices are raw machine registers, not human semantic labels.
"""

from __future__ import annotations
from substrate import World

R, U, S = 0, 1, 2


def prim_lib(p: int) -> dict:
    """The machine ISA as serializable micro-programs, parameterized by modulus p."""
    return {
        # r-only ops (leave u,s untouched) -- BASE physics is drawn from these
        "inc_r": (("addk", R, 1),),
        "dec_r": (("subk", R, 1),),               # p-agnostic
        "rst_r": (("set", R, 0),),
        "dbl_r": (("mulk", R, 2),),
        "neg_r": (("mulk", R, p - 1),),
        "tpl_r": (("mulk", R, 3),),
        # gate writer (the ONLY way to change u)
        "uset":  (("addk", U, 1),),
        "udec":  (("subk", U, 1),),               # p-agnostic
        # s writer: gated + nonlinear (the ONLY way to change s)
        "spush": (("ifnz", U, (("submul", S, R, R),)),),
        # linear gated writer -- NOT in proof hoard; used only in validation battery
        "spush_lin": (("ifnz", U, (("addreg", S, R),)),),
        # structural
        "swap_rs": (("swap", R, S),),
        "swap_ru": (("swap", R, U),),
        "nopish": (("addk", R, 0),),
    }


def proof_world(p: int = 13) -> World:
    lib = prim_lib(p)
    base = tuple((nm, lib[nm]) for nm in ("inc_r", "dec_r", "rst_r", "dbl_r", "neg_r"))
    return World(name=f"W-PROOF(p={p})", p=p, nreg=3, base_ops=base,
                 note="lock-chain: base=r-only; u,s conserved; s gated on u; s+=r*r")


def proof_pairs(p: int = 13):
    S0 = (0, 0, 0)
    family = [
        (S0, (0, 1, 7)),    # primary: u=1 (gate open once), s=7
        (S0, (0, 1, 3)),
        (S0, (0, 1, 9)),
        (S0, (0, 1, 10)),
        (S0, (0, 1, 4)),
        (S0, (0, 2, 12)),   # u=2 variant
    ]
    off_motif = [
        (S0, (6, 0, 0)),    # pure-r: base already reaches it (no barrier)
        (S0, (0, 1, 0)),    # pure-u: uset alone reaches it (single opener; not a wormhole)
    ]
    return {"primary": family[0], "family": family, "off_motif": off_motif}
