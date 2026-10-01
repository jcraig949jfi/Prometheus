"""Compute W5 clause values on control_rows.jsonl -> ATTAINABILITY.json
(clauses + cheat check).  Revisions list is maintained in REVISIONS below."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "control_rows.jsonl"))]
spec = json.load(open(os.path.join(HERE, "spec.json")))


def pooled(arm, key):
    v = []
    for r in rows:
        if r["arm"] == arm:
            v += r[key]
    return np.array(v, float)


def stats(arm):
    lat = pooled(arm, "latencies")
    ref = pooled("REFERENCE_NIS", "latencies")
    return {"S1": float(np.median(lat)),
            "S2": float(pooled(arm, "fa_flags").mean()),
            "S3": float(np.median(lat) / np.median(ref))}


def meets(c, v):
    return v <= c["threshold"] if c["comparison"] == "<=" else v >= c["threshold"]


pos, twin, cheat = stats("POSITIVE_CONTROL"), stats("NULL_TWIN"), stats("CHEAT")
ref_med = float(np.median(pooled("REFERENCE_NIS", "latencies")))
th = [c["threshold"] for c in spec["success_clauses"]]
must = {"S1": {"value": th[0], "text": "pooled median latency <= %g steps" % th[0]},
        "S2": {"value": th[1], "text": "pooled pre-change false-alarm fraction <= %g" % th[1]},
        "S3": {"value": round(th[2] * ref_med, 3), "text": "pooled median latency <= %.2f steps (= %g x REFERENCE_NIS median %.1f on these control rows; the rerun REFERENCE_NIS must reproduce 18.0)"
              % (th[2] * ref_med, th[2], ref_med)}}
clauses = []
for c in spec["success_clauses"]:
    clauses.append({"id": c["id"], "positive_value": pos[c["id"]], "twin_value": twin[c["id"]],
                    "cheat_value": cheat[c["id"]],
                    "attainable": bool(meets(c, pos[c["id"]])),
                    "discriminating": bool(not meets(c, twin[c["id"]])),
                    "treatment_must_reach": must[c["id"]]})
cheat_detected = all(meets(c, cheat[c["id"]]) for c in spec["success_clauses"])
frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected
REVISIONS = json.load(open(os.path.join(HERE, "revisions.json")))
out = {"world": "W5", "triplicateId": "HT-056d3ac561", "clauses": clauses,
       "cheat_detected": cheat_detected, "frozen": frozen,
       "reference_values": {"REFERENCE_NIS_median_latency": ref_med,
                            "REFERENCE_NIS_fa_fraction": float(pooled("REFERENCE_NIS", "fa_flags").mean()),
                            "NO_REOPEN_median_latency": float(np.median(pooled("NO_REOPEN", "latencies"))),
                            "per_seed_median_latency": {a: [r["median_latency"] for r in rows if r["arm"] == a]
                                                        for a in ["POSITIVE_CONTROL", "NULL_TWIN", "REFERENCE_NIS", "NO_REOPEN"]},
                            "nis_threshold": rows[0]["nis_threshold"]},
       "revisions": REVISIONS}
json.dump(out, open(os.path.join(HERE, "ATTAINABILITY.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ["clauses", "cheat_detected", "frozen"]}, indent=1))
