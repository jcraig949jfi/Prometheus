"""Phase 0 step 1: verify the exact LT adjudicator and the SOUNDNESS of
Knowledge.answer (never non-None and wrong) on random partial states."""
import json, random, sys, time
sys.path.insert(0, '.')
from lt import *

def brute_answers(w: World) -> dict:
    a = w.a_star; E = w.effects
    R = w.R_adm
    # AB by simulation: crossing set as (u,b) recovered from the crossing indicator
    cross = [dot(a, w.transition(2, x)) != dot(a, x) for x in range(256)]
    # find (u,b) with cross[x] == (dot(u,x)^b)
    ub = None
    for u in range(256):
        for b in (0, 1):
            if all(cross[x] == bool(dot(u, x) ^ b) for x in range(256)):
                assert ub is None; ub = [u, b]
    out = {"A": a, "B": [w.P2, w.c2], "C": R, "AB": ub,
           "AC": [r for r in R if dot(a, E[r]) == 1],
           "BC": [r for r in R if all(w.transition(2, x ^ E[r]) == w.transition(2, x) ^ E[r] for x in range(256))]}
    for k, x0 in enumerate(w.abc_x0):
        sols = []
        for r in R:
            if dot(a, w.transition(2, x0) ^ E[r]) != dot(a, x0): sols.append([r, "after"])
            if dot(a, w.transition(2, x0 ^ E[r])) != dot(a, x0): sols.append([r, "before"])
        out[f"ABC{k}"] = sols
    return out

t0 = time.time()
rng = random.Random(1)
n_worlds = 40; unsound = 0; checks = 0; det_full = 0
report = {"worlds": n_worlds, "invariant_unique": 0, "answers_match_bruteforce": 0,
          "full_knowledge_correct": 0, "partial_soundness_checks": 0, "partial_unsound": 0,
          "portal_preserves_astar": 0}
for ws in range(n_worlds):
    w = generate_world(ws)
    inv = common_invariants(w)
    assert inv == [w.a_star], (ws, inv)
    report["invariant_unique"] += 1
    ans = w.answers(); bf = brute_answers(w)
    assert all(canon(ans[t]) == canon(bf[t]) for t in TASK_TYPES), ws
    report["answers_match_bruteforce"] += 1
    if mat_apply(mat_T(w.P2), w.a_star) == w.a_star and dot(w.a_star, w.c2) == 0:
        report["portal_preserves_astar"] += 1
    # full knowledge -> all tasks CORRECT
    K = Knowledge(w.effects, w.abc_x0)
    K.obs_free = [(j, x, w.transition(j, x)) for j in FREE_OPS for x in range(256)]
    K.obs_portal = [(x, w.transition(2, x)) for x in range(256)]
    K.obs_adm = [(r, w.admissible(r)) for r in range(64)]
    assert all(adjudicate(w, t, K.answer(t)) == "CORRECT" for t in TASK_TYPES), ws
    report["full_knowledge_correct"] += 1
    # random partial states: answer must be None or CORRECT
    for trial in range(30):
        K = Knowledge(w.effects, w.abc_x0)
        nf, npo, na = rng.randrange(0, 12), rng.randrange(0, 11), rng.randrange(0, 12)
        for _ in range(nf):
            j = FREE_OPS[rng.randrange(2)]; x = rng.randrange(256); K.obs_free.append((j, x, w.transition(j, x)))
        for _ in range(npo):
            x = rng.randrange(256); K.obs_portal.append((x, w.transition(2, x)))
        for _ in range(na):
            r = rng.randrange(64); K.obs_adm.append((r, w.admissible(r)))
        for t in TASK_TYPES:
            v = adjudicate(w, t, K.answer(t)); report["partial_soundness_checks"] += 1
            if v == "WRONG": report["partial_unsound"] += 1; print("UNSOUND", ws, t, nf, npo, na)
report["elapsed_s"] = round(time.time() - t0, 1)
print(json.dumps(report, indent=1))
json.dump(report, open("results/step1_adjudicator.json", "w"), indent=1)
