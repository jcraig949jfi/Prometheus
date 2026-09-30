import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import (clause_A, clause_B, success, pc_success, max_rel_dev,
                         mertens, TOL, RATIO_MIN)

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
arm = lambda a: [r for r in rows if r["arm"] == a]
tr, ctl, pc, ch, tw = map(arm, ["TREATMENT", "CONTROL", "POSITIVE_CONTROL", "CHEAT", "NULL_TWIN"])
pilot = json.load(open(os.path.join(HERE, "PILOT.json")))
cpu = pilot["stats"]["cpu_seconds"] + json.load(open(os.path.join(HERE, "world_cpu.json")))["cpu_seconds"]

pc_ok = bool(all(pc_success(r) for r in pc))
cheat_ok = bool(all(success(r["r_by_K"], r["twin_ratio_injected"]) for r in ch))
tw_mean = list(np.mean([r["r_by_K"] for r in tw], axis=0))
twin_meets = bool(any(clause_A(r["r_by_K"]) for r in tw) or clause_A(tw_mean))
twin_ratio = float(np.mean([r["ratio_20_0"] for r in tw]))
tA = [max_rel_dev(r["r_by_K"]) for r in tr]
treat_A = bool(all(clause_A(r["r_by_K"]) for r in tr))
treat_B = bool(clause_B(twin_ratio))
treat_success = treat_A and treat_B

if not (pc_ok and cheat_ok):
    outcome = "INSTRUMENT_FAIL"
elif twin_meets:
    outcome = "CONFOUNDED"
elif treat_success:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

r = tr[0]["r_by_K"]
devs = {K: round(abs(r[K] - mertens(K)) / mertens(K), 4) for K in range(1, 21)}
res = {
    "triplicateId": "HT-47f4c02be4",
    "world": "W1",
    "outcome": outcome,
    "statistics": {
        "treatment_max_rel_dev_K1_20": round(max(tA), 4),
        "treatment_rel_dev_by_K": devs,
        "treatment_r_K": {K: round(r[K], 5) for K in (0, 1, 4, 10, 20, 40)},
        "treatment_K_star": tr[0]["K_star"],
        "treatment_depth_final": tr[0]["depth_final"],
        "treatment_periods_first10": tr[0]["periods"][:10],
        "control_r0": ctl[0]["r0"],
        "twin_ratio_20_0_mean": round(twin_ratio, 4),
        "twin_ratio_20_0_per_seed": [round(x["ratio_20_0"], 4) for x in tw],
        "twin_max_rel_dev_mean_curve": round(max_rel_dev(tw_mean), 4),
        "twin_K_star_seed0": tw[0]["K_star"],
        "pc_depth_final": [x["depth_final"] for x in pc],
        "cheat_max_rel_dev": [round(max_rel_dev(x["r_by_K"]), 4) for x in ch],
        "clause_A_real_stream": treat_A,
        "clause_B_twin_ratio": treat_B,
    },
    "criterion_as_applied": (
        f"SUCCESS iff max_(K=1..20) |r(K)-prod_(p<=p_K)(1-1/p)|/prod <= {TOL} on the real "
        f"stream (every seed) AND mean over 10 twin seeds of r(20)/r(0) >= {RATIO_MIN}. "
        "r(K) = residual errors / (N-1), N=1e5, residual = non-silent integer that no level "
        "predicts or that a level mispredicts (NOTES.md R1-R11)."),
    "positive_control_detected": pc_ok,
    "cheat_detected": cheat_ok,
    "null_twin_meets_success": twin_meets,
    "stupid_explanations_status": {
        "the promotion rule is literally the sieve so success is guaranteed by construction":
            "NOT RULED OUT -- promoted periods are exactly the primes 2,3,5,7,... on the real "
            "stream AND on the twin (promotion is label-free, R4); the agent is Eratosthenes.",
        "Mertens agreement is a known theorem, not a property of the agent":
            "NOT RULED OUT -- r(K) on the real stream is the Legendre count phi(N,K)/N plus "
            "K promotions; any match to Mertens is arithmetic, not agent behaviour.",
        "the Cramer twin fails because random streams are unpredictable by any periodic model, which says nothing about predictive coding":
            "NOT SUPPORTED BY THE ROWS -- the twin was not unpredictable to the periodic levels: "
            "they absorb ~79% of twin integers (ratio ~0.21); the twin differs from the real "
            "stream only through mispredictions at twin-prime labels.",
    },
    "anomalies": [
        "Clause B (twin r(20)/r(0) >= 0.9) is unattainable under readings R3/R4: r(0)=1 by "
        "construction and label-free promotion makes periodic levels absorb most twin "
        "integers; observed at the pilot (ratio ~0.21) before treatment code existed. The "
        "spec's success criterion requires the twin NOT to be absorbed while its mechanism "
        "absorbs any integer stream.",
        "Positive control and treatment are deterministic; the 5 seeds per arm are identical "
        "rows (recorded in NOTES.md).",
        "pilot_eval.py crashed once on JSON serialisation (evaluator bug, fixed, rerun on "
        "the same rows).",
    ],
    "core_minutes": round(cpu / 60, 4),
    "attempts": {"pilot": 1, "pilot_eval_bugfix_reruns": 1, "phase2": 1},
    "notes": "Phase 2 ran once after a passing pilot (PILOT.json attempt 1). No parameter "
             "or threshold changed. See NOTES.md.",
}
json.dump(res, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
