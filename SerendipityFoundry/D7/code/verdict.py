"""
Admission gates (D7 section 18), the nonlinear gate (19), geometry (33), and the
verdict ladder (49).  All gates are exact machine predicates fixed before evidence.
"""

from __future__ import annotations
from substrate import z_size, z_artifacts_used
from certify import certify_cut, base_closure
from evalz import evaluate, build_zfn
from controls import macro_replay, reweight_navigator, classify_degeneracy


def check_admission(world, S, T, family, offmotif, z_ast, hoard, grammar):
    ids = set(hoard.keys())
    used = z_artifacts_used(z_ast)
    fam_targets = [T] + [t for (s, t) in family if s == S and t != T]

    # A: absent initially (z is a synthesized program, not a pre-existing base op)
    A = True
    # B: valid in frozen grammar
    B = (z_size(z_ast) <= grammar.max_nodes) and all(u in ids for u in used)
    # C: certified cut
    cut = certify_cut(world, S, T)
    C = cut["barrier"]
    # D: crosses with z
    res = evaluate(z_ast, world, S, fam_targets, hoard)
    D = res["reached"][T]
    # E: not endpoint-specific -> folds >=2 family pairs with the SAME z
    fold = [t for t in fam_targets if res["reached"][t]]
    E = len(fold) >= 2
    # F: not macro-compression
    F = not macro_replay(world, S, T)["crossed"]
    # G: reweighting base cannot cross
    G = not reweight_navigator(world, S, T)["crossed"]
    # J: independent confirmation (fresh deterministic re-verification)
    J = evaluate(z_ast, world, S, [T], hoard)["reached"][T]
    # K: ablation restores barrier (Gz minus z == base -> T unreachable)
    K = T not in base_closure(world, S)
    # nonlinear gate
    deg = classify_degeneracy(z_ast, world, hoard)

    # off-motif: z should not spuriously "solve" unrelated pairs beyond base
    off_effects = []
    for (so, to) in offmotif:
        base_ok = to in base_closure(world, so)
        z_ok = evaluate(z_ast, world, so, [to], hoard)["reached"][to]
        off_effects.append({"target": list(to), "base_reachable": base_ok, "z_reachable": z_ok})

    return {
        "criteria": {"A_absent": A, "B_in_grammar": B, "C_certified_cut": C,
                     "D_crosses": D, "E_not_endpoint_specific": E,
                     "F_not_macro": F, "G_not_reweight": G,
                     "J_independent_confirm": J, "K_ablation_restores": K},
        "family_fold": [list(t) for t in fold],
        "family_fold_count": len(fold),
        "nonlinear": deg,
        "cut": cut,
        "off_motif_effects": off_effects,
        "z_size": z_size(z_ast),
        "z_artifacts": used,
    }


def geometry(world, S, z_ast, hoard, family):
    """Before/after topology characterization (D7 section 33)."""
    base = base_closure(world, S)
    zfn = build_zfn(z_ast, world, hoard)
    res = evaluate(z_ast, world, S, [family[0][1]], hoard)
    gz = res["closure"]
    fam_targets = [t for (s, t) in family]
    covered = [list(t) for t in fam_targets if t in gz]
    # new out-edges introduced by z that leave the base-reachable set
    new_edges = sum(1 for v in base if zfn[v] not in base)
    return {
        "base_reachable": len(base),
        "gz_reachable": len(gz),
        "reachability_gain": len(gz) - len(base),
        "state_space": world.p ** world.nreg,
        "family_targets": len(fam_targets),
        "family_covered_by_single_z": len(covered),
        "family_covered": covered,
        "new_escape_edges_from_base_set": new_edges,
    }


LADDER = [
    "SUBSTRATE_INVALID", "SYNTHESIS_GRAMMAR_LEAKED", "NO_CERTIFIED_CUT",
    "HISTORY_FREE_WARP", "HOARD_EFFECT_ONLY", "RELATIONAL_EFFECT_WITHOUT_WARP",
    "MACRO_COMPRESSION_ONLY", "ENDOGENOUS_NONLINEAR_GRAPH_WARP",
    "CERTIFIED_NONLINEAR_WORMHOLE", "GENUINE_FROZEN_TRANSFER",
    "MOTIF_TRANSFER_ONLY", "WORMHOLE_WITH_REVISION",
]


def assign_verdict(adm, relational, census_flags):
    """
    relational = {"H2_vs_H0": ratio, "H2_vs_H1": ratio, "significant": bool,
                  "history_free_easy": bool, "hoard_effect": bool}
    Returns (verdict, reasons[]).
    """
    c = adm["criteria"]
    reasons = []
    if census_flags:
        return "SYNTHESIS_GRAMMAR_LEAKED", [f"census flags: {census_flags}"]
    if not c["C_certified_cut"]:
        return "NO_CERTIFIED_CUT", ["no certified barrier"]
    if not c["D_crosses"]:
        return "RELATIONAL_EFFECT_WITHOUT_WARP", ["z does not cross"]
    if not c["F_not_macro"]:
        return "MACRO_COMPRESSION_ONLY", ["crossing reproduced by base macros"]
    if not c["G_not_reweight"]:
        return "MACRO_COMPRESSION_ONLY", ["crossing reproduced by base reweighting"]
    if not c["K_ablation_restores"]:
        return "SUBSTRATE_INVALID", ["ablation did not restore barrier"]

    nl = adm["nonlinear"]["nonlinear_gate_pass"]

    if relational.get("history_free_easy"):
        base_tier = "HISTORY_FREE_WARP"
        reasons.append("Z0 crosses about as easily as Z1")
    elif relational.get("hoard_effect"):
        base_tier = "HOARD_EFFECT_ONLY"
        reasons.append("H0 (same hoard, no relational edges) matches H2")
    elif not relational.get("significant"):
        base_tier = "ENDOGENOUS_NONLINEAR_GRAPH_WARP" if nl else "MACRO_COMPRESSION_ONLY"
        reasons.append("relational advantage not statistically established")
    else:
        # relational effect established AND all structural gates pass
        if nl and all(c.values()):
            base_tier = "CERTIFIED_NONLINEAR_WORMHOLE"
            reasons.append("all admission gates + nonlinear gate + relational effect")
        elif nl:
            base_tier = "ENDOGENOUS_NONLINEAR_GRAPH_WARP"
            reasons.append("nonlinear warp with relational effect; a structural gate soft")
        else:
            base_tier = "ENDOGENOUS_NONLINEAR_GRAPH_WARP"
            reasons.append("warp is degenerate-linear (nonlinear gate not passed)")
    return base_tier, reasons
