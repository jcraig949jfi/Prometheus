"""C-018-T030 evaluator: every verdict is re-derived from the recorded arrays (and, for native units, Aether's own attributed
tree). No producer field is read as a verdict: B and N are recomputed from the tree, targets from the tree / recipe, t0
identity from the stored t0 states, divergence from first-divergence ticks, content from stored features with Aether's own
decoder (Aether/V2B/REACH01/R1/r1_reduce.py:35 decode, :63 stats).

TRUST BOUNDARY. The first-divergence arrays are this adapter's observation of native execution, not the engine's labels.
They are bound to the meta by arrays_sha256; for native units they must agree site-for-site with Aether's independently
produced tree (tree_check); and their correctness as a description of Aether's law needs a native REPLAY (confirm.py replays a
preregistered sample bit-exactly). Ancestry cannot be verified without re-executing the engine: a clamp is an intervention.
"""
import math

import numpy as np

from rso.aether import adapter as A
from rso.aether.demand import fixtures as F
import prop01_tree as TR           # noqa: E402  (Aether, unmodified; path set by fixtures)
import r1_reduce as RD             # noqa: E402

REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3          # SELECTION.md / demand PREREG thresholds, unchanged
MARGIN, NULL_MAX = 0.05, 0.03                               # content margin (TEST-4-like) and null sanity bound
CLASSES = ("MULTI_SOURCE", "NO_CUT", "INSUFFICIENT", "CONTROL_VACUOUS", "CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL")


def t0_sites(a):
    return [int(s) for s in np.flatnonzero(np.any(a["snap"] != a["imp"], axis=0).ravel())]


def light_cone(meta, a):
    """P1 guard: every divergent site's Chebyshev distance to the t0 set <= its first-divergence tick."""
    n = meta["n"]
    src = [divmod(s, n) for s in t0_sites(a)]
    ft = a["ftick_impulse"]
    idx = np.flatnonzero(ft > 0)
    if not src or not len(idx):
        return True, 0.0
    d = F.cheb_to_set(n, src).ravel()[idx]
    ratio = d / ft[idx]
    return bool((d <= ft[idx]).all()), round(float(ratio.max()), 3)


def _sites(meta):
    """(B, N, targets) re-derived: native from Aether's tree (choose_cut, descendants, the non-ancestor rule); fixture from
    the recipe recorded with the unit (a fixture's sites ARE its recipe)."""
    if meta["kind"] != "native":
        return meta["B"], meta["N"], list(meta["targets"])
    tree = meta["tree"]
    B, _ = TR.choose_cut({"tree": tree})
    if B is None:
        return None, None, []
    return B, A.choose_nonancestor(tree, B, meta["origin"], meta["n"]), sorted(TR.descendants(tree, B))


def ancestry(meta, a):
    n, O = meta["n"], meta["origin"]
    out = {"cls": None, "removed_B": None, "removed_N": None, "targets": [], "I": [], "r_int": 0, "agreement": None}
    if t0_sites(a) != [O]:
        out["cls"] = "MULTI_SOURCE"
        return out
    B, N, targets = _sites(meta)
    if B is None:
        out["cls"] = "NO_CUT"
        return out
    imp, cb, cn = a["ftick_impulse"], a["ftick_cutB"], a["ftick_cutN"]
    tg = [s for s in targets if imp[s] >= 0]
    out["targets"] = tg
    vac = N is None or imp[N] < 0
    I = [int(s) for s in np.flatnonzero((imp >= 0) & (cb < 0) & ((cn >= 0) if not vac else True)) if s not in (B, N, O)]
    out["I"] = I
    out["r_int"] = max((A.cheb(n, s, O) for s in I), default=0)
    if tg:
        out["removed_B"] = round(sum(1 for s in tg if cb[s] < 0) / len(tg), 4)
        out["removed_N"] = None if vac else round(sum(1 for s in tg if cn[s] < 0) / len(tg), 4)
        out["agreement"] = round(len(set(tg) & set(I)) / len(tg), 4)
    if len(tg) < TARGETS_MIN:
        out["cls"] = "INSUFFICIENT"
    elif vac:
        out["cls"] = "CONTROL_VACUOUS"
    elif out["removed_B"] >= REMOVED_MIN:
        out["cls"] = "CONFIRMED" if out["removed_N"] <= NONANC_MAX else "NONSPECIFIC"
    else:
        out["cls"] = "NOT_INTERVENTIONAL"
    return out


def tree_check(meta, a):
    """Native only: Aether's attributed tree must describe exactly the divergence this recorder observed, and the recorded
    B / N must be what the rules give on that tree (they are recomputed, never trusted)."""
    if meta["kind"] != "native":
        return []
    tree, ft, bad = meta["tree"], a["ftick_impulse"], []
    obs = set(int(s) for s in np.flatnonzero(ft >= 0))
    if set(tree["site"]) != obs:
        bad.append("tree sites != observed divergent sites (%d vs %d)" % (len(tree["site"]), len(obs)))
    wrong = [s for s, t in zip(tree["site"], tree["ftick"]) if s < len(ft) and int(ft[s]) != t]
    if wrong:
        bad.append("tree first ticks differ from observed at %d sites" % len(wrong))
    roots = [s for s, g in zip(tree["site"], tree["gen"]) if g == 0]
    if roots != [meta["origin"]] or t0_sites(a) != [meta["origin"]]:
        bad.append("origin: tree roots %s, t0 sites %s, recorded %s" % (roots, t0_sites(a)[:3], meta["origin"]))
    B, N, _ = _sites(meta)
    if B != meta["B"]:
        bad.append("recorded B %s != choose_cut %s" % (meta["B"], B))
    if N != meta["N"]:
        bad.append("recorded N %s != non-ancestor rule %s" % (meta["N"], N))
    return bad


def binding_problems(meta, a):
    return [] if meta.get("arrays_sha256") == A.arrays_sha256(a) else ["arrays_sha256 does not match the stored arrays"]


def evaluate_unit(meta, a):
    ok, ratio = light_cone(meta, a)
    r = ancestry(meta, a)
    return {"kind": meta["kind"], "law": meta.get("law"), "fixture": meta.get("fixture"), "seed": meta["seed"],
            "t0_sites": len(t0_sites(a)), "light_cone_ok": ok, "max_radius_over_tick": ratio,
            "problems": binding_problems(meta, a) + tree_check(meta, a),
            **{k: r[k] for k in ("cls", "removed_B", "removed_N", "r_int", "agreement")},
            "n_targets": len(r["targets"]), "n_I": len(r["I"])}


# ---------------------------------------------------------------- content (P3), Aether's decoder on stored features
def decode(units, null=False):
    """units: [(seed, H, D)] -> {seed: acc[t, r]} held-out (leave-one-seed-out), r1_reduce.decode unchanged."""
    acc = RD.decode([(s, {}, H, D) for s, H, D in units], null=null)
    return {s: np.asarray(v) for s, v in acc.items()}


def excess_all(acc):
    """Mean over seeds of Aether's Dstat: accuracy - 1/8 over radii 2..6 and every tick."""
    return float(np.mean([v["Dstat"] for v in RD.stats(acc).values()])) if acc else None


def conditioned_excess(acc, r_int):
    """Mean over units with interventional reach r_int >= 2 of (accuracy - 1/8) over radii 2..min(r_int, 6), all ticks.
    The content question is asked only where interventional ancestry reaches. None if no unit qualifies."""
    vals = [float((acc[s][:, 1:min(r, 6)] - 0.125).mean()) for s, r in r_int.items() if r >= 2 and s in acc]
    return float(np.mean(vals)) if vals else None


# ---------------------------------------------------------------- per-law summary and disposition
def law_summary(rows, acc, acc_null):
    cls = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    evaluable = [r for r in rows if r["cls"] in ("CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL")]
    pooled = (sum(r["agreement"] * r["n_targets"] for r in evaluable) / sum(r["n_targets"] for r in evaluable)
              if evaluable else None)
    r_int = {r["seed"]: (r["r_int"] if r["cls"] == "CONFIRMED" else 0) for r in rows}
    return {"n_units": len(rows), "classes": cls, "confirmed_r2": sum(1 for v in r_int.values() if v >= 2),
            "pooled_agreement": None if pooled is None else round(pooled, 4),
            "agreement_category": agreement_category(pooled),
            "content_excess_cond": conditioned_excess(acc, r_int), "content_excess_all": excess_all(acc),
            "null_excess": excess_all(acc_null),
            "light_cone_violations": sum(1 for r in rows if not r["light_cone_ok"])}


def agreement_category(x):
    if x is None:
        return None
    return "AGREE" if x >= 0.8 else "DISAGREE" if x <= 0.5 else "MIXED"


def disposition(s):
    """PREREGISTRATION s6, in this order: completeness, record consistency, instrument qualification, decoder null, then
    P2 at radius >= 2 (>= max(3, ceil(10% of units)) CONFIRMED units with r_int >= 2) crossed with P3 (excess >= MARGIN)."""
    if s["completeness"] in ("INCOMPLETE", "REFUSED"):
        return s["completeness"]
    if not s["records_ok"]:
        return "REFUSED_RECORD_INCONSISTENT"
    if not s["qualified"]:
        return "DETECTION_UNQUALIFIED"
    L = s["law"]
    if L["null_excess"] is None or abs(L["null_excess"]) >= NULL_MAX:
        return "DETECTION_UNQUALIFIED"
    p2 = L["confirmed_r2"] >= max(3, math.ceil(0.1 * L["n_units"]))
    if p2:
        c = L["content_excess_cond"]
        return "ANCESTRY_WITH_CONTENT" if c is not None and c >= MARGIN else "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT"
    c = L["content_excess_all"]
    return "CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY" if c is not None and c >= MARGIN else "NEITHER"
