"""Phase 0 steps 2-4: generator census (master-key / marginal-prior
shortcuts), multi-component necessity, union-vs-composition qualification."""
import json, random, sys, time, math, statistics as st
from collections import Counter
from itertools import combinations
sys.path.insert(0, '.')
from lt import *

t0 = time.time()
NW = 200
worlds = [generate_world(s) for s in range(NW)]
rep = {}


def oracle_of(w):
    return lambda q: (w.transition(q[1], q[2]) if q[0] == "TRANSITION" else w.admissible(q[1]))


# ---- 2a. marginal priors of hidden params and of task answers ---------------
cA = Counter(w.a_star for w in worlds); cM = Counter(w.m_star for w in worlds)
rep["prior_a_star_max_share"] = max(cA.values()) / NW
rep["prior_m_star_max_share"] = max(cM.values()) / NW
ans_counters = {t: Counter() for t in TASK_TYPES}
for w in worlds:
    A = w.answers()
    for t in TASK_TYPES:
        ans_counters[t][canon(A[t])] += 1
rep["marginal_guess_rate"] = {t: round(max(c.values()) / NW, 3) for t, c in ans_counters.items()}
rep["answer_entropy_bits"] = {t: round(-sum((v / NW) * math.log2(v / NW) for v in c.values()), 2)
                              for t, c in ans_counters.items()}
SETS = ("C", "AC", "ABC0", "ABC1", "ABC2")
rep["set_answer_sizes_mean_min_max"] = {
    t: [round(st.mean(len(json.loads(k)) for k in c.elements()), 2),
        min(len(json.loads(k)) for k in c), max(len(json.loads(k)) for k in c)]
    for t, c in ans_counters.items() if t in SETS}
bc = Counter(canon(w.answers()["BC"]) for w in worlds)
rep["KILLED_BC_universal_strategy"] = {"empty_rate": bc["[]"] / NW, "max_share": max(bc.values()) / NW}
rep["empty_answer_rate"] = {t: round(sum(v for k, v in c.items() if k == "[]") / NW, 3)
                            for t, c in ans_counters.items() if t in SETS[1:]}

# ---- 2b. information-theoretic floors + empirical blind cost ----------------
def cost_to_determine(w, comp, seed, heuristic="random"):
    s = Settings(seed=seed, order=(comp,), heuristic=heuristic)
    r = Researcher(w.public(), s, oracle_of(w), lambda kind, d: f"{kind}{seed}", budget=60)
    r.run()
    return r.spent if r.done(comp) else None


def summ(v):
    v = [x for x in v if x is not None]
    return {"n": len(v), "min": min(v), "median": st.median(v), "mean": round(st.mean(v), 2), "max": max(v)}


costs = {c: [] for c in "ABC"}; cms = []; cbs = []
for w in worlds[:60]:
    for c in "ABC":
        costs[c].append(cost_to_determine(w, c, 7))
    cms.append(cost_to_determine(w, "C", 7, "maxsplit"))
    cbs.append(cost_to_determine(w, "B", 7, "basis"))
rep["blind_cost_random"] = {c: summ(costs[c]) for c in "ABC"}
rep["cost_C_maxsplit"] = summ(cms); rep["cost_B_basis"] = summ(cbs)
rep["info_floor_queries"] = {"A": 7, "B": 9, "C": 7, "all": 23,
                             "basis": "a*, m*: 7 independent linear constraints leave {0, v}; (P2,c2): 72 bits at 8 bits/query"}

# ---- 2c. master key: does knowing two components determine the third? -------
resid = []
for w in worlds[:100]:
    P2T = mat_T(w.P2)
    nA = sum(1 for a in range(1, 256) if not (mat_apply(P2T, a) == a and dot(a, w.c2) == 0))
    resid.append(nA)
rep["master_key_residual_candidates"] = {"BC_known_to_A": summ(resid), "AB_known_to_C": 254,
                                         "AC_known_to_B": "unconstrained: 2^72 minus the a*-preserving affine maps"}
rep["public_data_independent_of_hidden"] = "generator rejects only on (a*, P1, P3, c1, c3, P2, c2); effects and x0 never inspected"

# ---- 3. multi-component necessity ------------------------------------------
nec = {}
for t in INTERACTIVE:
    comps = sorted(COMPONENTS_OF[t])
    for k in range(0, len(comps)):
        for S in combinations(comps, k):
            key = f"{t}|known={''.join(S) or 'none'}"
            det = 0
            for w in worlds[:100]:
                K = Knowledge(w.effects, w.abc_x0)
                for c in S:
                    K.adopted[c] = {"A": w.a_star, "B": (w.P2, w.c2), "C": w.m_star}[c]
                if K.answer(t) is not None:
                    det += 1
            nec[key] = det / 100
rep["necessity_determined_rate_with_proper_subset"] = nec
full_ok = 0
for w in worlds[:100]:
    K = Knowledge(w.effects, w.abc_x0)
    K.adopted = {"A": w.a_star, "B": (w.P2, w.c2), "C": w.m_star}
    full_ok += all(adjudicate(w, t, K.answer(t)) == "CORRECT" for t in TASK_TYPES)
rep["necessity_full_set_correct_rate"] = full_ok / 100

part = {}
for t in ("AC", "AB", "ABC0"):
    det = 0
    comps = sorted(COMPONENTS_OF[t]); missing = comps[-1]
    for w in worlds[:100]:
        K = Knowledge(w.effects, w.abc_x0)
        rng = random.Random(w.world_seed)
        for c in comps[:-1]:
            K.adopted[c] = {"A": w.a_star, "B": (w.P2, w.c2), "C": w.m_star}[c]
        for _ in range(4):
            if missing == "C":
                r = rng.randrange(64); K.obs_adm.append((r, w.admissible(r)))
            elif missing == "B":
                x = rng.randrange(256); K.obs_portal.append((x, w.transition(2, x)))
            else:
                j = FREE_OPS[rng.randrange(2)]; x = rng.randrange(256); K.obs_free.append((j, x, w.transition(j, x)))
        det += K.answer(t) is not None
    part[f"{t}|missing={missing}@4queries"] = det / 100
rep["necessity_partial_missing_component"] = part

# ---- 4. union vs composition (offline LOSO qualification) ------------------
def lineage(w, comp, seed, budget=14):
    s = Settings(seed=seed, order=(comp,), heuristic="basis" if comp == "B" else "maxsplit")
    r = Researcher(w.public(), s, oracle_of(w), lambda kind, d: f"{kind}{seed}", budget=budget)
    r.run(); return r


loso = {"n": 0, "solved_full": 0, "true_composition": 0, "loso_matches_design": 0,
        "ancestor_case_not_composition": 0, "ancestor_cases": 0, "examples": []}
for w in worlds[:40]:
    arts = {c: lineage(w, c, 11).raw_artifact() for c in "ABC"}
    for t in INTERACTIVE:
        need = sorted(COMPONENTS_OF[t]); loso["n"] += 1
        K, _ = knowledge_from_artifacts(w.public(), [arts[c] for c in "ABC"], "RAW")
        if adjudicate(w, t, K.answer(t)) != "CORRECT":
            continue
        loso["solved_full"] += 1
        necessary = []
        for c in "ABC":
            K2, _ = knowledge_from_artifacts(w.public(), [arts[d] for d in "ABC" if d != c], "RAW")
            if adjudicate(w, t, K2.answer(t)) != "CORRECT":
                necessary.append(c)
        if len(necessary) >= 2:
            loso["true_composition"] += 1
        if necessary == need:
            loso["loso_matches_design"] += 1
        if len(loso["examples"]) < 4:
            loso["examples"].append({"world": w.world_seed, "task": t, "necessary": necessary, "needed_by_design": need})
    # ancestor case: one lineage knows everything; LOSO of the others changes
    # nothing -> must NOT be labelled composition
    allk = lineage(w, "A", 3, 60)
    allk.s = Settings(seed=3, order=("A", "B", "C"), heuristic="maxsplit")
    r = Researcher(w.public(), Settings(seed=3, order=("A", "B", "C"), heuristic="maxsplit"),
                   oracle_of(w), lambda k, d: "x", budget=60); r.run()
    allraw = r.raw_artifact()
    K, _ = knowledge_from_artifacts(w.public(), [allraw, arts["A"], arts["C"]], "RAW")
    if adjudicate(w, "AC", K.answer("AC")) == "CORRECT":
        loso["ancestor_cases"] += 1
        nec_ = []
        for c in ("A", "C"):
            K2, _ = knowledge_from_artifacts(w.public(), [allraw] + [arts[d] for d in ("A", "C") if d != c], "RAW")
            if adjudicate(w, "AC", K2.answer("AC")) != "CORRECT":
                nec_.append(c)
        if len(nec_) == 0:
            loso["ancestor_case_not_composition"] += 1
rep["union_vs_composition"] = loso
rep["elapsed_s"] = round(time.time() - t0, 1)
print(json.dumps(rep, indent=1))
json.dump(rep, open("results/step2_4_census.json", "w"), indent=1)
