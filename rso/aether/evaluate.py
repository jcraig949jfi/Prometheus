"""C-018-T030 evaluator: every verdict is re-derived from the recorded arrays (and, for native units, Aether's own attributed
tree). No producer field is read as a verdict: B and N are recomputed from the tree, targets from the tree / recipe, t0
identity from the stored t0 states, divergence from first-divergence ticks, content from stored features with Aether's own
decoder (Aether/V2B/REACH01/R1/r1_reduce.py:35 decode, :63 stats).

TRUST BOUNDARY. The first-divergence arrays are this adapter's observation of native execution, not the engine's labels.
They are bound to the meta by arrays_sha256; for native units they must agree site-for-site with Aether's independently
produced tree (tree_check); and their correctness as a description of Aether's law needs a native REPLAY (confirm.py replays a
preregistered sample bit-exactly). Ancestry cannot be verified without re-executing the engine: a clamp is an intervention.
v1.1.0 (C-018-T041; PREREGISTRATION s10): tree_check adds the native tree invariants and the clamp-world fidelity checks
(B1); NOT_INTERVENTIONAL is decided before control vacuity (it needs no non-ancestor); `need` and the reach band count
EVALUABLE units with a preregistered minimum and an ANCESTRY_UNEVALUABLE status (B2); content over the CONFIRMED units' own
seeds (B3) and the targets' first-tick distribution (B7) are reported beside the registered quantities.
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
EVALUABLE = ("CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL")      # units on which the ancestry question was asked
EVALUABLE_MIN = 8                                           # v1.1.0 (B2): fewer evaluable units -> ANCESTRY_UNEVALUABLE


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
    out = {"cls": None, "removed_B": None, "removed_N": None, "targets": [], "I": [], "r_int": 0, "agreement": None,
           "ftick_B": None, "ftick_N": None}
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
    out["ftick_B"], out["ftick_N"] = int(imp[B]), None if N is None else int(imp[N])
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
    elif out["removed_B"] < REMOVED_MIN:
        out["cls"] = "NOT_INTERVENTIONAL"
    elif vac:
        out["cls"] = "CONTROL_VACUOUS"
    else:
        out["cls"] = "CONFIRMED" if out["removed_N"] <= NONANC_MAX else "NONSPECIFIC"
    return out


def tick_profile(ticks):
    """First-divergence ticks of a unit's targets (B7): min / quartiles / max and how many came after ticks 200 and 300.
    'Never diverges in CUT_B' means 'not within H ticks'; late targets make a removal partly a delayed-divergence reading."""
    if not ticks:
        return None
    q = np.percentile(np.asarray(ticks, float), [0, 25, 50, 75, 100])
    return {"n": len(ticks), "min_q1_med_q3_max": [round(float(x), 1) for x in q],
            "after_200": sum(1 for t in ticks if t > 200), "after_300": sum(1 for t in ticks if t > 300)}


def tree_invariants(tree, n):
    """Structural invariants of a native prop01 tree (prop01_run.py:181-210: an attributed site's parent is a 4-neighbour
    that diverged BEFORE it, gen = parent gen + 1). Problems as strings. A tamper that respects them is invisible here;
    only the replayed tree (confirm.analyse) closes that form (Pallas B1)."""
    par, ft, gen = (dict(zip(tree["site"], tree[k])) for k in ("parent", "ftick", "gen"))
    bad = {"parent not in tree": 0, "parent not 4-adjacent": 0, "parent not earlier": 0, "gen != parent gen + 1": 0}
    for s, p in par.items():
        if p < 0:
            continue
        if p not in par:
            bad["parent not in tree"] += 1
            continue
        dy, dx = (min(abs(u - v), n - abs(u - v)) for u, v in zip(divmod(s, n), divmod(p, n)))
        bad["parent not 4-adjacent"] += dy + dx != 1
        bad["parent not earlier"] += not ft[p] < ft[s]
        bad["gen != parent gen + 1"] += gen[s] != gen[p] + 1
    return ["tree invariant: %s at %d sites" % (k, v) for k, v in bad.items() if v]


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
    bad += tree_invariants(tree, meta["n"])
    for w, site in (("cutB", B), ("cutN", N)):     # a clamp world was really run: the impulse is in it at t0 and the
        f = a["ftick_" + w]                         # clamped site never diverges in it
        if site is not None and not (f[meta["origin"]] == 0 and f[site] < 0):
            bad.append("%s array is not a clamp of site %s (origin tick %d, site tick %d)" % (w, site, f[meta["origin"]], f[site]))
    return bad


def binding_problems(meta, a):
    return [] if meta.get("arrays_sha256") == A.arrays_sha256(a) else ["arrays_sha256 does not match the stored arrays"]


def evaluate_unit(meta, a):
    ok, ratio = light_cone(meta, a)
    r = ancestry(meta, a)
    return {"kind": meta["kind"], "law": meta.get("law"), "fixture": meta.get("fixture"), "seed": meta["seed"],
            "t0_sites": len(t0_sites(a)), "light_cone_ok": ok, "max_radius_over_tick": ratio,
            "problems": binding_problems(meta, a) + tree_check(meta, a),
            **{k: r[k] for k in ("cls", "removed_B", "removed_N", "r_int", "agreement", "ftick_B", "ftick_N")},
            "n_targets": len(r["targets"]), "n_I": len(r["I"]),
            "targets_ftick": tick_profile([int(a["ftick_impulse"][s]) for s in r["targets"]])}


# ---------------------------------------------------------------- content (P3), Aether's decoder on stored features
def decode(units, null=False):
    """units: [(seed, H, D)] -> {seed: acc[t, r]} held-out (leave-one-seed-out), r1_reduce.decode unchanged."""
    acc = RD.decode([(s, {}, H, D) for s, H, D in units], null=null)
    return {s: np.asarray(v) for s, v in acc.items()}


def excess_all(acc):
    """Mean over seeds of Aether's Dstat: accuracy - 1/8 over radii 2..6 and every tick."""
    return float(np.mean([v["Dstat"] for v in RD.stats(acc).values()])) if acc else None


def evaluable(rows):
    return sum(1 for r in rows if r["cls"] in EVALUABLE)


def need(n_evaluable):
    """v1.1.0 (B2): CONFIRMED units required for P2 = max(3, ceil(10% of the EVALUABLE units)); v1.0.0 counted every unit,
    NO_CUT included, so a population that tested nothing could read NEITHER."""
    return max(3, math.ceil(0.1 * n_evaluable))


def reach_band(rows):
    """Largest radius r (<= 6) such that >= need(evaluable) units are CONFIRMED with interventional reach >= r; 0 if none.
    P2 at depth means reach_band >= 2."""
    need_ = need(evaluable(rows))
    band = 0
    for r in range(1, 7):
        if sum(1 for x in rows if x["cls"] == "CONFIRMED" and x["r_int"] >= r) >= need_:
            band = r
    return band


def conditioned_excess(acc, band):
    """Content asked only where interventional ancestry is demonstrated: mean over held-out seeds of (accuracy - 1/8) over
    radii 2..min(band, 6) and every tick. None if band < 2. (Ancestry is measured at Aether's impulse origin, content at
    Aether's r1 grid origins of the same worlds: the joint reading is at the radius-band level, not per site.)"""
    if band < 2 or not acc:
        return None
    return float(np.mean([(np.asarray(a)[:, 1:min(band, 6)] - 0.125).mean() for a in acc.values()]))


# ---------------------------------------------------------------- per-law summary and disposition
def law_summary(rows, acc, acc_null):
    cls = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    ev = [r for r in rows if r["cls"] in EVALUABLE]
    pooled = sum(r["agreement"] * r["n_targets"] for r in ev) / sum(r["n_targets"] for r in ev) if ev else None
    band = reach_band(rows)
    conf = [r for r in rows if r["cls"] == "CONFIRMED"]
    return {"n_units": len(rows), "evaluable": len(ev), "evaluable_min": EVALUABLE_MIN, "need": need(len(ev)),
            "classes": cls, "reach_band": band,
            "content_excess_cond_confirmed_seeds": conditioned_excess({r["seed"]: acc[r["seed"]] for r in conf
                                                                       if r["seed"] in acc}, band),
            "confirmed_targets_ftick": {str(r["seed"]): r.get("targets_ftick") for r in conf},
            "nonspecific_N_before_B": sum(1 for r in rows if r["cls"] == "NONSPECIFIC" and r.get("ftick_N") is not None
                                          and r["ftick_N"] < r["ftick_B"]),
            "confirmed_r2": sum(1 for r in rows if r["cls"] == "CONFIRMED" and r["r_int"] >= 2),
            "pooled_agreement": None if pooled is None else round(pooled, 4),
            "agreement_category": agreement_category(pooled),
            "content_excess_cond": conditioned_excess(acc, band), "content_excess_all": excess_all(acc),
            "null_excess": excess_all(acc_null),
            "light_cone_violations": sum(1 for r in rows if not r["light_cone_ok"])}


def agreement_category(x):
    if x is None:
        return None
    return "AGREE" if x >= 0.8 else "DISAGREE" if x <= 0.5 else "MIXED"


def disposition(s):
    """PREREGISTRATION s6 / s10, in this order: completeness, record consistency, instrument qualification, decoder null,
    fewer than EVALUABLE_MIN evaluable units (ANCESTRY_UNEVALUABLE), then P2 at radius >= 2 (>= need(evaluable) CONFIRMED
    units with r_int >= 2) crossed with P3 (excess >= MARGIN)."""
    if s["completeness"] in ("INCOMPLETE", "REFUSED"):
        return s["completeness"]
    if not s["records_ok"]:
        return "REFUSED_RECORD_INCONSISTENT"
    if not s["qualified"]:
        return "DETECTION_UNQUALIFIED"
    L = s["law"]
    if L["null_excess"] is None or abs(L["null_excess"]) >= NULL_MAX:
        return "DETECTION_UNQUALIFIED"
    if L["evaluable"] < EVALUABLE_MIN:
        return "ANCESTRY_UNEVALUABLE"
    p2 = L["confirmed_r2"] >= need(L["evaluable"])
    if p2:
        c = L["content_excess_cond"]
        return "ANCESTRY_WITH_CONTENT" if c is not None and c >= MARGIN else "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT"
    c = L["content_excess_all"]
    return "CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY" if c is not None and c >= MARGIN else "NEITHER"


def label(disposition_, L):
    """Every printed label carries the evaluable count beside it (REPORT s4.4 item 1)."""
    return "%s [evaluable %d of %d units; minimum %d; need %d CONFIRMED at r >= 2]" % (
        disposition_, L["evaluable"], L["n_units"], EVALUABLE_MIN, L["need"])
