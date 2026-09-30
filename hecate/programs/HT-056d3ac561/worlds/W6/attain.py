"""Compute W6 clause values on control_rows.jsonl -> ATTAINABILITY.json."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "control_rows.jsonl"))]
spec = json.load(open(os.path.join(HERE, "spec.json")))


def acc(arm):
    v = []
    for r in sorted((r for r in rows if r["arm"] == arm), key=lambda r: r["seed"]):
        v += r["success"]
    return float(np.mean(v))


rnd, gg = acc("REFERENCE_RANDOM"), acc("REFERENCE_GAUSSIAN_GREEDY")


def stats(arm):
    a = acc(arm)
    return {"S1": a, "S2": a - rnd, "S3": a - gg}


def meets(c, v):
    return v >= c["threshold"] if c["comparison"] == ">=" else v <= c["threshold"]


pos, twin, cheat = stats("POSITIVE_CONTROL"), stats("NULL_TWIN"), stats("CHEAT")
th = {c["id"]: c["threshold"] for c in spec["success_clauses"]}
must = {"S1": {"value": th["S1"], "text": "pooled accuracy >= %g" % th["S1"]},
        "S2": {"value": round(rnd + th["S2"], 4), "text": "pooled accuracy >= %.4f (= REFERENCE_RANDOM %.4f + %g on these control rows)" % (rnd + th["S2"], rnd, th["S2"])},
        "S3": {"value": round(gg + th["S3"], 4), "text": "pooled accuracy >= %.4f (= REFERENCE_GAUSSIAN_GREEDY %.4f + %g on these control rows)" % (gg + th["S3"], gg, th["S3"])}}
clauses = [{"id": c["id"], "positive_value": pos[c["id"]], "twin_value": twin[c["id"]],
            "cheat_value": cheat[c["id"]],
            "attainable": bool(meets(c, pos[c["id"]])),
            "discriminating": bool(not meets(c, twin[c["id"]])),
            "treatment_must_reach": must[c["id"]]} for c in spec["success_clauses"]]
cheat_detected = all(meets(c, cheat[c["id"]]) for c in spec["success_clauses"])
frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected
out = {"world": "W6", "triplicateId": "HT-056d3ac561", "clauses": clauses,
       "cheat_detected": cheat_detected, "frozen": frozen,
       "reference_values": {"REFERENCE_RANDOM_accuracy": rnd, "REFERENCE_GAUSSIAN_GREEDY_accuracy": gg,
                            "per_seed_accuracy": {a: [r["accuracy"] for r in rows if r["arm"] == a]
                                                  for a in ["POSITIVE_CONTROL", "NULL_TWIN", "REFERENCE_RANDOM", "REFERENCE_GAUSSIAN_GREEDY"]},
                            "both_true_covered_fraction": {a: float(np.mean([r["both_true_covered_fraction"] for r in rows if r["arm"] == a]))
                                                           for a in ["POSITIVE_CONTROL", "NULL_TWIN", "REFERENCE_RANDOM", "REFERENCE_GAUSSIAN_GREEDY"]}},
       "revisions": json.load(open(os.path.join(HERE, "revisions.json")))}
json.dump(out, open(os.path.join(HERE, "ATTAINABILITY.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ["clauses", "cheat_detected", "frozen"]}, indent=1))
