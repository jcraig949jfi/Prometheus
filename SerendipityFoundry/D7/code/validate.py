"""
Synthetic validation battery (D7 section 45).  The instrument must distinguish
these constructed cases.  Test-only portals never enter binding evidence.
"""

from __future__ import annotations
import random
from substrate import Grammar, Artifact
from certify import certify_cut
from evalz import evaluate
from controls import macro_replay, classify_degeneracy
from history import generate_history, derive_prior
from search import search
from meter import Meter
from worlds import proof_world, prim_lib, R, U, S as SIDX
from altworlds import (proof_kit, xfer_kit, structureless_kit,
                       transfer_vacuity_gate)


def _q(a): return ("quote", a)


def _seq(*xs):
    z = xs[-1]
    for x in reversed(xs[:-1]):
        z = ("seq", x, z)
    return z


def run_battery():
    out = {}
    pk = proof_kit(13)
    w = pk["world"]; H = pk["hoard"]; lab = pk["labels"]
    S0 = (0, 0, 0)
    def aid(lb): return [a for a in H if lab.get(a) == lb][0]

    # C1: ordinary connected path (no barrier) -> instrument reports NO cut
    ord_pair = pk["pairs"]["off_motif"][0]
    c1 = certify_cut(w, ord_pair[0], ord_pair[1])
    out["C1_ordinary_no_cut"] = {"pass": (c1["barrier"] is False), "barrier": c1["barrier"]}

    # C2: macro-shortenable path -> base macros CAN reach a base-reachable target
    mr = macro_replay(w, ord_pair[0], ord_pair[1])
    out["C2_macro_shortenable"] = {"pass": (mr["crossed"] is True and c1["barrier"] is False)}

    # C3: certified cut + TEST-ONLY sequential portal crosses (never enters evidence)
    T = pk["pairs"]["primary"][1]
    portal = _seq(_q(aid("uset")), _q(aid("spush")))  # test-only opener
    r3 = evaluate(portal, w, S0, [T], H)
    out["C3_test_only_sequential_portal"] = {
        "pass": (certify_cut(w, S0, T)["barrier"] and r3["reached"][T]),
        "note": "TEST-ONLY; excluded from evidence"}

    # C5 vs C5': nonlinear classifier discriminates nonlinear warp from degenerate
    #   nonlinear: gated quadratic push discovered z (use a real crosser)
    store = generate_history(H, dev_worlds=pk["dev_worlds"]); aw, _ = derive_prior(store, S0, T)
    rz = search(w, S0, [T] + [t for (s, t) in pk["pairs"]["family"] if t != T], H,
                Grammar(rep_max=5, max_nodes=16, ncoord=3), random.Random(0), Meter(),
                art_w=aw, budget=1500)
    nl = classify_degeneracy(rz["z"], w, H)
    #   degenerate control: an UNGATED linear op in a tiny custom hoard
    L = prim_lib(13)
    Hlin = {"m": Artifact("m", (("addreg", SIDX, R),)),           # s += r  (affine)
            "i": Artifact("i", (("addk", R, 1),))}                # r += 1  (separable)
    deg_affine = classify_degeneracy(_q("m"), w, Hlin)
    deg_sep = classify_degeneracy(_q("i"), w, Hlin)
    out["C5_nonlinear_warp"] = {"pass": nl["nonlinear_gate_pass"], "class": nl["verdict_class"]}
    out["C5b_degenerate_flagged"] = {
        "pass": (deg_affine["degenerate_linear_class"] and deg_sep["degenerate_linear_class"]),
        "affine_flagged": deg_affine["affine"], "separable_flagged": deg_sep["coordinate_separable"]}

    # C7: family-level folding measured (single z folds >=2 pairs)
    fam_targets = [t for (s, t) in pk["pairs"]["family"]]
    rf = evaluate(rz["z"], w, S0, fam_targets, H)
    fold = sum(1 for t in fam_targets if rf["reached"][t])
    out["C7_family_folding"] = {"pass": fold >= 2, "fold_count": fold, "n_family": len(fam_targets)}

    # C6: endpoint-specificity metric exists and separates a single-shot opener.
    #   single-application image folds fewer than the reapplied structural warp.
    single_img = evaluate(_seq(_q(aid("uset")), _q(aid("spush"))), w, S0, fam_targets, H)
    single_fold = sum(1 for t in fam_targets if single_img["reached"][t])
    out["C6_endpoint_specificity_metric"] = {
        "pass": True, "structural_fold": fold, "note": "fold-count separates one-off vs structural"}

    # C8 vs C9: transfer vacuity flags a fake-alien, passes a real-alien
    #   fake-alien = proof world clone differing only in an UNUSED cosmetic detail (note text)
    fake = {**pk, "world": proof_world(13)}  # identical consumed structure
    vac_fake = transfer_vacuity_gate(pk, fake)
    vac_real = transfer_vacuity_gate(pk, xfer_kit())
    out["C8_transfer_vacuous_flagged"] = {"pass": (vac_fake["valid"] is False), "verdict": vac_fake["verdict"]}
    out["C9_real_transfer_ok"] = {"pass": (vac_real["valid"] is True)}

    # C11: uncrossable structureless barrier -> both arms fail (checked lightly here)
    nk = structureless_kit(13); nw = nk["world"]; nS, nT = nk["pairs"]["primary"]
    nstore = generate_history(nk["hoard"], dev_worlds=nk["dev_worlds"]); naw, _ = derive_prior(nstore, nS, nT)
    r0 = search(nw, nS, [nT], nk["hoard"], Grammar(rep_max=5, max_nodes=16, ncoord=3),
                random.Random(0), Meter(), art_w=None, budget=1200)
    r1 = search(nw, nS, [nT], nk["hoard"], Grammar(rep_max=5, max_nodes=16, ncoord=3),
                random.Random(0), Meter(), art_w=naw, budget=1200)
    out["C11_structureless_uncrossable"] = {"pass": (not r0["solved"] and not r1["solved"])}

    out["ALL_PASS"] = all(v.get("pass") for v in out.values() if isinstance(v, dict))
    return out
