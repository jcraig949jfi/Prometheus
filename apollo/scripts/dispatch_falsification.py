"""dispatch_falsification.py — does a DISPATCH capability break the single-terminal
ceiling, and can the search DISCOVER it? (Road A, 2026-06-23)

Falsification-first, mirroring recombination_falsification + recombination_ab.

The 0.558 diagnosis: best_acc tracks one fixed-terminal pipeline; the battery needs
>=3 terminals; the archive already holds specialists but no single organism routes.
The missing capability is DISPATCH (the R3 step). The substrate already supports it
via BlackboardOp.precondition + on_fail=skip: a pipeline of MUTUALLY-EXCLUSIVE
guarded scorers is a dispatcher.

Gates:
  G1 construct validity — a hand-built guarded dispatcher solves a mixed battery
     that the best single-terminal pipeline cannot. (Confirms expressibility.)
  G2 necessity (the valley) — broad random search of single-terminal pipelines;
     report theta_single = best achievable; show NO single-terminal organism solves
     both task types >=0.9. (The >theta region is routing-only.)
  G3 discovery A/B — seed the two SPECIALISTS (not a dispatcher). control =
     single-terminal regime; treatment = guarded multi-scorer + dispatch-merge.
     Metric: first gen with an organism solving BOTH types >=0.9. (Necessary-vs-
     sufficient: can the search ASSEMBLE the router, not just host it?)
  G4 post-discovery audit (Goodhart guards) — on the discovered dispatcher:
     per-branch ablation (each branch load-bearing for exactly its type),
     surface-perturbation robustness (guards route on semantic slots not surface),
     tier-predicted failure (unknown type -> no misroute).

Deterministic, CPU-only. Run: python apollo/scripts/dispatch_falsification.py
"""
from __future__ import annotations
import sys, json, random, copy
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blackboard import BlackboardState, BlackboardOp, run_pipeline
import blackboard_evolve as ev
from inference_canary import build_inference_canary
from cross_tier_canary import build_cross_tier_canary

BASE = ev.REGISTRY

# ── op pools ──────────────────────────────────────────────────────────
TRANSFORMERS = list(ev.TRANSFORMERS)
PLAIN_SCORERS = list(ev.SCORERS)  # control pool (single terminal)


def _guard(name, precond):
    fn, _ = BASE[name]
    return BlackboardOp(fn.fn, reads=fn.reads, writes=fn.writes,
                        precondition=precond, on_fail="skip", name=name + "__g")


# MUTUALLY-EXCLUSIVE guards (closes the PoC overlap where 20/40 fired both).
# Priority is encoded in the exclusion clauses, not in tail-ordering: a task
# routes to exactly one branch regardless of op order.
GUARDED = {
    "select_nth__g": _guard("select_nth",
                            lambda s: len(s.ordered) > 0),
    "score_by_derivability__g": _guard("score_by_derivability",
                            lambda s: (len(s.derived_facts) > 0 or len(s.facts) > 0) and len(s.ordered) == 0),
    "score_by_aggregate__g": _guard("score_by_aggregate",
                            lambda s: len(s.quantities) > 0 and len(s.ordered) == 0
                                      and len(s.derived_facts) == 0 and len(s.facts) == 0),
}
GUARDED_SCORERS = list(GUARDED.keys())

REG = {}                       # local resolve: name -> BlackboardOp
for n in TRANSFORMERS + PLAIN_SCORERS:
    REG[n] = BASE[n][0]
REG.update(GUARDED)

SCORER_NAMES = set(PLAIN_SCORERS) | set(GUARDED_SCORERS)
def is_scorer(n): return n in SCORER_NAMES


def ops(names): return [REG[n] for n in names]


# ── battery (balanced, 2 terminals required) ─────────────────────────
def build_mixed(n=20, seed=0):
    inf = build_inference_canary(n=n)
    xt = build_cross_tier_canary(n=n)
    return [("inf", t) for t in inf] + [("xt", t) for t in xt]


def acc_by_type(pipeline_names, tagged):
    per = {}
    for tag, t in tagged:
        per.setdefault(tag, [0, 0])[1] += 1
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            o = run_pipeline(ops(pipeline_names), s)
            if o.selected_answer == t["correct"]:
                per[tag][0] += 1
        except Exception:
            pass
    overall = sum(v[0] for v in per.values()) / max(sum(v[1] for v in per.values()), 1)
    pertype = {k: v[0] / max(v[1], 1) for k, v in per.items()}
    return overall, pertype


def solves_both(pipeline_names, tagged, thresh=0.9):
    _, pt = acc_by_type(pipeline_names, tagged)
    return len(pt) >= 2 and all(v >= thresh for v in pt.values())


# ── G1 construct validity ─────────────────────────────────────────────
def gate1(tagged):
    inf_spec = ["parse_rules", "forward_chain", "score_by_derivability"]
    xt_spec = ["parse_rules", "parse_ordinal", "forward_chain",
               "relations_from_facts", "op_build_ordering", "select_nth"]
    dispatcher = ["parse_rules", "parse_ordinal", "forward_chain",
                  "relations_from_facts", "op_build_ordering",
                  "score_by_derivability__g", "select_nth__g"]
    res = {}
    for label, pl in [("inf_specialist", inf_spec), ("xt_specialist", xt_spec),
                      ("dispatcher", dispatcher)]:
        o, pt = acc_by_type(pl, tagged)
        res[label] = {"overall": round(o, 3), "per_type": {k: round(v, 3) for k, v in pt.items()},
                      "solves_both": solves_both(pl, tagged)}
    res["PASS"] = res["dispatcher"]["solves_both"] and not res["inf_specialist"]["solves_both"] \
        and not res["xt_specialist"]["solves_both"]
    return res


# ── G2 necessity: random single-terminal search ──────────────────────
def gate2(tagged, n_samples=6000, seed=12345):
    rng = random.Random(seed)
    best_overall = 0.0
    best_pl = None
    any_both = 0
    for _ in range(n_samples):
        k = rng.randint(1, 5)
        body = [rng.choice(TRANSFORMERS) for _ in range(k)]
        pl = body + [rng.choice(PLAIN_SCORERS)]
        o, pt = acc_by_type(pl, tagged)
        if o > best_overall:
            best_overall, best_pl = o, pl
        if len(pt) >= 2 and all(v >= 0.9 for v in pt.values()):
            any_both += 1
    return {"n_samples": n_samples, "theta_single": round(best_overall, 3),
            "best_single_pipeline": best_pl,
            "single_terminal_solving_both": any_both,
            "PASS": any_both == 0}


# ── G3 discovery A/B (minimal MAP-Elites evolve) ─────────────────────
def _lb_core(pipeline_names, tagged):
    """Load-bearing transformer set via cheap per-op removal ablation on a small
    probe (keeps the archive key invariant to decorative padding)."""
    base_o, _ = acc_by_type(pipeline_names, tagged)
    core = set()
    for i, n in enumerate(pipeline_names):
        if is_scorer(n):
            continue
        ablated = pipeline_names[:i] + pipeline_names[i + 1:]
        o, _ = acc_by_type(ablated, tagged)
        if base_o - o > 0.02:
            core.add(n)
    return frozenset(core)


def descriptor(pipeline_names, tagged):
    scorers = frozenset(n for n in pipeline_names if is_scorer(n))
    return (scorers, _lb_core(pipeline_names, tagged))


def valid(pipeline_names):
    return any(is_scorer(n) for n in pipeline_names)


def mutate(pl, rng, dispatch):
    p = list(pl)
    body_idx = [i for i, n in enumerate(p) if not is_scorer(n)]
    moves = ["insert", "remove", "swap_t"]
    if dispatch:
        moves += ["append_guard", "swap_t"]   # extra weight on growth
    else:
        moves += ["swap_scorer"]
    m = rng.choice(moves)
    if m == "insert" and len(body_idx) < 6:
        p.insert(rng.randint(0, len(body_idx)), rng.choice(TRANSFORMERS))
    elif m == "remove" and len(body_idx) > 1:
        del p[rng.choice(body_idx)]
    elif m == "swap_t" and body_idx:
        p[rng.choice(body_idx)] = rng.choice(TRANSFORMERS)
    elif m == "swap_scorer":
        sc_idx = [i for i, n in enumerate(p) if is_scorer(n)]
        if sc_idx:
            p[sc_idx[-1]] = rng.choice(PLAIN_SCORERS)
    elif m == "append_guard":
        have = {n for n in p if n in GUARDED_SCORERS}
        opts = [g for g in GUARDED_SCORERS if g not in have]
        if opts:
            p.append(rng.choice(opts))
    return p


def dispatch_merge(pa, pb, rng):
    """Combine two organisms: union of transformer bodies (order-preserving,
    pa then pb's new ones) + the guarded scorers of both. The dispatch analogue
    of crossover — assembles a multi-branch router from two specialists."""
    body_a = [n for n in pa if not is_scorer(n)]
    body_b = [n for n in pb if not is_scorer(n)]
    body = body_a + [n for n in body_b if n not in body_a]
    guards = []
    for n in pa + pb:
        if n in GUARDED_SCORERS and n not in guards:
            guards.append(n)
    if not guards:  # neither parent had a guarded scorer yet — give one
        guards = [rng.choice(GUARDED_SCORERS)]
    return body + guards


def evolve_arm(tagged, dispatch, seed, gens=300, pop=24, merge=True):
    rng = random.Random(seed)
    # seed both arms with the two specialists (NOT a dispatcher)
    inf_spec = ["parse_rules", "forward_chain",
                "score_by_derivability__g" if dispatch else "score_by_derivability"]
    xt_spec = ["parse_rules", "parse_ordinal", "forward_chain", "relations_from_facts",
               "op_build_ordering", "select_nth__g" if dispatch else "select_nth"]
    seeds = [inf_spec, xt_spec]
    # plus a few random single-terminal organisms for diversity
    while len(seeds) < pop:
        k = rng.randint(1, 3)
        sc = rng.choice(GUARDED_SCORERS if dispatch else PLAIN_SCORERS)
        seeds.append([rng.choice(TRANSFORMERS) for _ in range(k)] + [sc])

    archive = {}  # descriptor -> (pipeline, overall_acc)
    def try_insert(pl):
        if not valid(pl):
            return
        o, _ = acc_by_type(pl, tagged)
        d = descriptor(pl, tagged)
        cur = archive.get(d)
        if cur is None or (o, -len(pl)) > (cur[1], -len(cur[0])):
            archive[d] = (pl, o)

    for pl in seeds:
        try_insert(pl)

    first_both_gen = None
    for gen in range(1, gens + 1):
        occ = list(archive.values())
        for _ in range(pop):
            if not occ:
                break
            if dispatch and merge and len(occ) >= 2 and rng.random() < 0.3:
                pa, pb = rng.sample(occ, 2)
                child = dispatch_merge(pa[0], pb[0], rng)
            else:
                child = mutate(rng.choice(occ)[0], rng, dispatch)
            try_insert(child)
        if first_both_gen is None:
            for pl, _o in archive.values():
                if solves_both(pl, tagged):
                    first_both_gen = gen
                    break
        if first_both_gen is not None:
            break
    # best both-solver, if any
    best = None
    for pl, o in archive.values():
        if solves_both(pl, tagged):
            if best is None or len(pl) < len(best):
                best = pl
    return {"discovered": first_both_gen is not None, "first_both_gen": first_both_gen,
            "best_dispatcher": best, "archive_size": len(archive)}


def gate3(tagged, seeds=(20260623, 1, 7, 42, 101), gens=300, pop=24):
    res = {"control": [], "treatment_merge": [], "treatment_mutate_only": []}
    for sd in seeds:
        c = evolve_arm(tagged, dispatch=False, seed=sd, gens=gens, pop=pop)
        tm = evolve_arm(tagged, dispatch=True, seed=sd, gens=gens, pop=pop, merge=True)
        to = evolve_arm(tagged, dispatch=True, seed=sd, gens=gens, pop=pop, merge=False)
        res["control"].append({"seed": sd, **{k: c[k] for k in ("discovered", "first_both_gen")}})
        res["treatment_merge"].append({"seed": sd, **{k: tm[k] for k in ("discovered", "first_both_gen", "best_dispatcher")}})
        res["treatment_mutate_only"].append({"seed": sd, **{k: to[k] for k in ("discovered", "first_both_gen")}})
    disc = {k: sum(r["discovered"] for r in res[k]) for k in res}
    res["discovered_counts"] = disc
    # PASS: dispatch (either operator) discovers what control structurally cannot
    res["PASS"] = (disc["treatment_merge"] + disc["treatment_mutate_only"]) > 0 and disc["control"] == 0
    res["audit_target"] = next((r["best_dispatcher"] for r in res["treatment_merge"] if r["best_dispatcher"]), None)
    return res


# ── G4 post-discovery Goodhart audit ─────────────────────────────────
def gate4(pipeline_names, tagged):
    if not pipeline_names:
        return {"PASS": False, "reason": "no dispatcher discovered to audit"}
    audit = {}
    base_o, base_pt = acc_by_type(pipeline_names, tagged)
    audit["baseline"] = {"overall": round(base_o, 3), "per_type": {k: round(v, 3) for k, v in base_pt.items()}}

    # (2) per-branch ablation: removing a guarded scorer must collapse ITS type only
    branch = {}
    branch_pass = True
    for g in [n for n in pipeline_names if n in GUARDED_SCORERS]:
        ablated = [n for n in pipeline_names if n != g]
        _, pt = acc_by_type(ablated, tagged)
        drops = {k: round(base_pt.get(k, 0) - pt.get(k, 0), 3) for k in base_pt}
        # exactly one type should collapse (>0.3 drop); others ~unchanged (<0.1)
        collapsed = [k for k, d in drops.items() if d > 0.3]
        unaffected = [k for k, d in drops.items() if abs(d) < 0.1]
        ok = len(collapsed) == 1 and len(unaffected) == len(drops) - 1
        branch[g] = {"drops": drops, "load_bearing_for": collapsed, "ok": ok}
        branch_pass = branch_pass and ok
    audit["per_branch_ablation"] = {"detail": branch, "PASS": branch_pass}

    # (3) surface-perturbation robustness: shuffle candidate order; routing must hold
    rng = random.Random(999)
    perturbed = []
    for tag, t in tagged:
        t2 = dict(t)
        c = list(t2["candidates"]); rng.shuffle(c); t2["candidates"] = c
        perturbed.append((tag, t2))
    p_o, p_pt = acc_by_type(pipeline_names, perturbed)
    audit["surface_perturbation"] = {"overall": round(p_o, 3),
                                     "per_type": {k: round(v, 3) for k, v in p_pt.items()},
                                     "PASS": abs(p_o - base_o) < 0.1}

    # (4) tier-predicted failure: a genuine no-branch type must NOT misroute.
    # Aggregate/box tasks populate only `quantities` (and only if parse_box_items runs,
    # which the discovered dispatcher lacks). With neither `ordered` nor `facts` set, no
    # guard fires -> selected_answer stays "" (graceful abstention), NOT a confident wrong
    # pick. We measure branch-fire-rate (fraction with non-empty answer); tier-correct
    # failure = ~0 fires, not high-confidence misrouting.
    from composition_gauntlet import build_synthetic_canary
    agg = [t for t in build_synthetic_canary(n_each=15)
           if "box" in t["prompt"].lower() or "how many" in t["prompt"].lower()][:15]
    fired = 0
    correct_by_misroute = 0
    for t in agg:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            o = run_pipeline(ops(pipeline_names), s)
            if o.selected_answer != "":
                fired += 1
                if o.selected_answer == t["correct"]:
                    correct_by_misroute += 1
        except Exception:
            pass
    fire_rate = fired / max(len(agg), 1)
    audit["tier_predicted_failure"] = {
        "n_no_branch_tasks": len(agg), "branch_fire_rate": round(fire_rate, 3),
        "accidental_correct": correct_by_misroute,
        "PASS": fire_rate <= 0.2,
        "note": "no-branch type -> dispatcher should abstain (empty answer), not misroute"}

    audit["PASS"] = (branch_pass and audit["surface_perturbation"]["PASS"]
                     and audit["tier_predicted_failure"]["PASS"])
    return audit


def main():
    tagged = build_mixed(n=20)
    print("=" * 78)
    print("DISPATCH FALSIFICATION (Road A) — guarded multi-scorer routing")
    print(f"  battery: {len(tagged)} tasks (balanced inf + xt, 2 terminals required)")
    print("=" * 78)

    g1 = gate1(tagged)
    print("\n--- G1 construct validity ---")
    for k in ("inf_specialist", "xt_specialist", "dispatcher"):
        print(f"  {k:16s} overall={g1[k]['overall']:.3f} per_type={g1[k]['per_type']} both={g1[k]['solves_both']}")
    print(f"  G1 PASS = {g1['PASS']}")

    g2 = gate2(tagged)
    print("\n--- G2 necessity (random single-terminal search) ---")
    print(f"  theta_single (best single-terminal) = {g2['theta_single']:.3f} over {g2['n_samples']} samples")
    print(f"  single-terminal organisms solving BOTH types >=0.9: {g2['single_terminal_solving_both']}")
    print(f"  G2 PASS = {g2['PASS']}  (no single-terminal solves both -> >theta region is routing-only)")

    g3 = gate3(tagged)
    print("\n--- G3 discovery A/B (5 seeds) ---")
    for arm in ("control", "treatment_merge", "treatment_mutate_only"):
        gens_found = [r["first_both_gen"] for r in g3[arm] if r["discovered"]]
        n_disc = sum(r["discovered"] for r in g3[arm])
        print(f"  {arm:<22}: discovered {n_disc}/5  first_both_gens={gens_found}")
    print(f"  G3 PASS = {g3['PASS']}  (dispatch discovers the router; control structurally can't)")

    g4 = gate4(g3["audit_target"], tagged)
    print("\n--- G4 post-discovery Goodhart audit ---")
    print(f"  audit target: {g3['audit_target']}")
    print(f"  baseline: {g4.get('baseline')}")
    if "per_branch_ablation" in g4:
        print(f"  per-branch ablation PASS={g4['per_branch_ablation']['PASS']}")
        for g, d in g4["per_branch_ablation"]["detail"].items():
            print(f"      {g}: drops={d['drops']} load_bearing_for={d['load_bearing_for']} ok={d['ok']}")
        print(f"  surface-perturbation PASS={g4['surface_perturbation']['PASS']} ({g4['surface_perturbation']})")
        print(f"  tier-predicted failure: {g4['tier_predicted_failure']}")
    print(f"  G4 PASS = {g4['PASS']}")

    overall_pass = g1["PASS"] and g2["PASS"] and g3["PASS"] and g4["PASS"]
    print("\n" + "=" * 78)
    print(f"  DISPATCH FALSIFICATION: {'PASSED' if overall_pass else 'NOT PASSED'} "
          f"(G1={g1['PASS']} G2={g2['PASS']} G3={g3['PASS']} G4={g4['PASS']})")
    print("=" * 78)

    out = {"experiment": "dispatch_falsification", "date": "2026-06-23",
           "G1": g1, "G2": g2, "G3": g3, "G4": g4, "overall_pass": overall_pass}
    art = ROOT / "pivot" / "dispatch_falsification_result_2026-06-23.json"
    with open(art, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=lambda o: list(o) if isinstance(o, (set, frozenset)) else str(o))
    print(f"\n  artifact -> {art}")
    return overall_pass


if __name__ == "__main__":
    main()
