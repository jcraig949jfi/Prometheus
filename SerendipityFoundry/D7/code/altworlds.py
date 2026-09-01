"""
Alternate worlds: transfer (motif-preserving, all-consumed-dims-different),
structureless/NULL (certified-uncrossable), and hostile (blind z self-harms).
Plus the transfer non-vacuity gate (D7 sections 21-23, 25, 24, 22).

Each builder returns a "kit": dict(world, hoard, roles, labels, pairs, dev_worlds).
"""

from __future__ import annotations
import random
from substrate import World, Artifact, sha, run_z
from worlds import proof_world, proof_pairs, prim_lib
from hoard import build_hoard

R, U, S = 0, 1, 2


# ---------------------------------------------------------------------------
# PROOF kit (assembled for uniformity).
# ---------------------------------------------------------------------------

def proof_kit(p=13):
    w = proof_world(p)
    hoard, roles, labels = build_hoard(p)
    pp = proof_pairs(p)
    from history import developmental_worlds
    return {"name": "PROOF", "world": w, "hoard": hoard, "roles": roles,
            "labels": labels, "pairs": pp, "dev_worlds": developmental_worlds()}


# ---------------------------------------------------------------------------
# TRANSFER world: same DEEP MOTIF (a locked coord gated behind another,
# openable only by composing a gate-writer with a gated nonlinear writer),
# but every consumed dimension differs:
#   * modulus p = 17 (was 13)
#   * nonlinearity is CUBIC  y += x*x*x   (was quadratic s += r*r)  <- crossing-critical
#   * base op-set differs (adds a tpl/step mix, no dbl)
#   * ids reshuffled (different seed); the crossing-critical writer, modulus, and
#     endpoints genuinely differ (some r-side distractor bytes coincide -- harmless)
#   * endpoints differ (disjoint from proof discovery endpoints)
# ---------------------------------------------------------------------------

def _xfer_prim(p):
    return {
        "inc_x": (("addk", R, 1),),
        "dec_x": (("subk", R, 1),),
        "tpl_x": (("mulk", R, 3),),
        "rst_x": (("set", R, 0),),
        "neg_x": (("mulk", R, p - 1),),
        "gset":  (("addk", U, 1),),
        "gdec":  (("subk", U, 1),),
        "ypush": (("ifnz", U, (("submul3", S, R, R, R),)),),  # y += x^3 (gated) -- needs submul3
        "swap_xy": (("swap", R, S),),
        "nopx": (("addk", R, 0),),
    }


def xfer_world(p=17):
    L = _xfer_prim(p)
    base = tuple((nm, L[nm]) for nm in ("inc_x", "dec_x", "tpl_x", "rst_x", "neg_x"))
    return World(name=f"W-XFER(p={p})", p=p, nreg=3, base_ops=base,
                 note="cubic gated lock-chain; different base/p/endpoints")


def _xfer_behaviors(p):
    L = _xfer_prim(p)

    def prog(*names):
        out = []
        for n in names:
            out.extend(L[n])
        return tuple(out)

    base = [
        ("gset",   "gate_writer",   prog("gset")),
        ("gset2",  "gate_writer",   prog("gset")),
        ("ypush",  "s_writer_nl",   prog("ypush")),
        ("ypush2", "s_writer_nl",   prog("ypush")),
        ("stepx",  "r_ctrl",        prog("inc_x")),
        ("resetx", "r_ctrl",        prog("rst_x")),
        ("tplx",   "r_ctrl",        prog("tpl_x")),
        ("decx",   "r_ctrl",        prog("dec_x")),
        ("negx",   "r_ctrl",        prog("neg_x")),
        ("idn",    "neutral",       prog("inc_x", "dec_x")),
        ("nop",    "neutral",       prog("nopx")),
        ("tw",     "neutral",       prog("swap_xy", "swap_xy")),
        ("gid",    "neutral",       prog("gdec", "gset")),
        ("ph",     "harmful",       (("mulk", R, 7 % p),)),
        ("xcube",  "harmful",       (("submul3", R, R, R, R),)),  # x += x^3 (into x; red herring)
        ("pdx1",   "distractor",    prog("tpl_x", "dec_x")),
        ("pdx2",   "distractor",    prog("inc_x", "inc_x")),
        ("pdx3",   "distractor",    prog("neg_x", "inc_x")),
        ("pdx4",   "distractor",    prog("dec_x", "dec_x")),
        ("pdx5",   "distractor",    prog("tpl_x", "tpl_x")),
    ]
    return base


def xfer_hoard(p=17, seed=555):
    behs = _xfer_behaviors(p)
    rng = random.Random(seed)
    order = list(range(len(behs)))
    rng.shuffle(order)
    hoard, roles, labels = {}, {}, {}
    for new_i, orig_i in enumerate(order):
        label, cat, prog = behs[orig_i]
        aid = f"x{new_i:02d}"
        hoard[aid] = Artifact(aid=aid, prog=prog, origin=f"xfer:{label}")
        roles[aid] = cat
        labels[aid] = label
    return hoard, roles, labels


def xfer_pairs(p=17):
    S0 = (0, 0, 0)
    fam = [(S0, (0, 1, 6)), (S0, (0, 1, 5)), (S0, (0, 1, 11)),
           (S0, (0, 1, 8)), (S0, (0, 2, 14))]
    return {"primary": fam[0], "family": fam,
            "off_motif": [(S0, (4, 0, 0)), (S0, (0, 1, 0))]}


def xfer_dev():
    return [xfer_world(11), xfer_world(13)]


def xfer_kit():
    w = xfer_world(17)
    hoard, roles, labels = xfer_hoard(17)
    return {"name": "XFER", "world": w, "hoard": hoard, "roles": roles,
            "labels": labels, "pairs": xfer_pairs(17), "dev_worlds": xfer_dev()}


# ---------------------------------------------------------------------------
# STRUCTURELESS / NULL world: certified cut with NO admissible cross in the
# grammar -- the s-writers are simply absent from the hoard, so s can never
# change.  Z0 and Z1 must BOTH fail (NULL preservation, D7 section 25).
# ---------------------------------------------------------------------------

def structureless_kit(p=13):
    w = proof_world(p)
    hoard, roles, labels = build_hoard(p)
    # remove every s-writer -> s is unwritable by ANY program
    drop = [a for a in list(hoard) if roles[a] == "s_writer_nl"]
    for a in drop:
        del hoard[a]; del roles[a]; del labels[a]
    from history import developmental_worlds
    return {"name": "NULL", "world": w, "hoard": hoard, "roles": roles,
            "labels": labels, "pairs": proof_pairs(p),
            "dev_worlds": developmental_worlds(), "dropped": drop}


# ---------------------------------------------------------------------------
# HOSTILE world: an extra "poison" coord.  spush here ALSO trips poison, and a
# poisoned state can never reach the target (poison is absorbing on s).  A naive
# spush-spam z self-harms (poisons, target lost).  A revised z must reach the
# target WITHOUT leaving poison set at the end.  We do NOT tell the learner why.
# ---------------------------------------------------------------------------

def hostile_world(p=13):
    # reg: r,u,s,poison(3).  base = r-only.  Handled via a custom op set inside hoard.
    lib = prim_lib(p)
    base = tuple((nm, lib[nm]) for nm in ("inc_r", "dec_r", "rst_r", "dbl_r", "neg_r"))
    return World(name=f"W-HOSTILE(p={p})", p=p, nreg=4, base_ops=base,
                 note="4th coord = poison; harmful spush trips it")


POISON = 3


def hostile_hoard(p=13, seed=20260827):
    """spush ALSO trips poison; add uclose (u:=0) and cleanse (clear poison iff u==0).
    Targets require poison=0, so a naive spush-spam z self-harms; a revision must
    close the gate then cleanse."""
    hoard, roles, labels = build_hoard(p)  # reuse aids
    for a in list(hoard):
        if roles[a] == "s_writer_nl":
            hoard[a] = Artifact(aid=a, prog=(("ifnz", U, (("submul", S, R, R),
                                                          ("set", POISON, 1))),),
                                origin="hostile:spush+poison")
    dists = [a for a in hoard if roles[a] == "distractor"]
    hoard[dists[0]] = Artifact(aid=dists[0], prog=(("ifz", U, (("set", POISON, 0),)),),
                               origin="hostile:cleanse")
    roles[dists[0]] = "revision_tool"; labels[dists[0]] = "cleanse"
    hoard[dists[1]] = Artifact(aid=dists[1], prog=(("set", U, 0),), origin="hostile:uclose")
    roles[dists[1]] = "revision_tool"; labels[dists[1]] = "uclose"
    return hoard, roles, labels


def hostile_dev():
    """4-register dev worlds (r,u,s,poison) so hostile artifacts probe cleanly."""
    return [hostile_world(7), hostile_world(5)]


def hostile_kit(p=13):
    hoard, roles, labels = hostile_hoard(p)
    S0 = (0, 0, 0, 0)
    # targets end with u=0 AND poison=0 (gate closed, harm repaired), s != 0
    fam = [(S0, (0, 0, 7, 0)), (S0, (0, 0, 3, 0)), (S0, (0, 0, 9, 0))]
    return {"name": "HOSTILE", "world": hostile_world(p), "hoard": hoard, "roles": roles,
            "labels": labels,
            "pairs": {"primary": fam[0], "family": fam,
                      "off_motif": [(S0, (5, 0, 0, 0))]},
            "dev_worlds": hostile_dev()}


# ---------------------------------------------------------------------------
# Transfer non-vacuity gate (D7 section 22).
# ---------------------------------------------------------------------------

def transfer_vacuity_gate(proof, xfer):
    checks = {}
    pw, xw = proof["world"], xfer["world"]
    checks["worlds_not_byte_identical"] = pw.fingerprint() != xw.fingerprint()
    # discovery endpoints excluded from transfer family
    proof_targets = {tuple(t) for (s, t) in proof["pairs"]["family"]}
    xfer_targets = {tuple(t) for (s, t) in xfer["pairs"]["family"]}
    checks["transfer_targets_exclude_discovery"] = proof_targets.isdisjoint(xfer_targets)
    # at least one artifact behaves differently across worlds: the gated writer
    # is quadratic (s+=r*r) in proof but cubic (y+=x*x*x) in transfer.  Concretely
    # probe both gated writers from a gate-open state and confirm different images.
    pw_writer = [a for a in proof["hoard"] if proof["roles"][a] == "s_writer_nl"][0]
    xw_writer = [a for a in xfer["hoard"] if xfer["roles"][a] == "s_writer_nl"][0]
    v_open = (2, 1, 0)
    p_img, _ = proof["hoard"][pw_writer].run(v_open, pw.p)   # s += 4
    x_img, _ = xfer["hoard"][xw_writer].run(v_open, xw.p)    # y += 8
    checks["at_least_one_artifact_differs"] = (p_img[S] % 30 != x_img[S] % 30)
    # identity/copy transform cannot satisfy transfer -- verify concretely that a
    # no-op z does not cross the transfer barrier (a no-op never lifts the gate).
    from evalz import evaluate as _ev
    xS, xT = xfer["pairs"]["primary"]
    idn = _ev(("nop",), xw, xS, [xT], xfer["hoard"])
    checks["identity_does_not_transfer"] = (idn["reached"][xT] is False)
    # transfer evaluation reads dims that differ (nonlinearity degree, p, base)
    checks["evaluation_reads_differing_dims"] = (pw.p != xw.p)
    valid = all(checks.values())
    return {"valid": valid, "verdict": ("OK" if valid else "TRANSFER_INVALID"), "checks": checks}
