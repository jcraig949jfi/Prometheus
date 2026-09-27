#!/usr/bin/env python3
"""S3 mutational cliff: D7 eligibility re-tabulation of C4-01 (stdlib only).

Reads the committed per-child rows of C4-01 attempt of record a02
(archaeon/campaign4/C4-01/attempts/a02/children.json.gz), verifies the
raw sha256 recorded in CHILDREN_DIGEST.json, and tabulates:
  - eligibility to improve (parent not degenerate, parent has headroom
    for D7 on its own environment: parent_reward + 1/16 < 1.0, and the
    edit actually applied);
  - outcome fractions among eligible edits (improved / neutral /
    deleterious / lethal), with Wilson and rule-of-three bounds.
Thresholds are C4's own (D4-003): band 1/16, viability floor 3/16.
"""
import gzip, hashlib, json, math, os, sys, collections as C

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
A02 = os.path.join(ROOT, "archaeon/campaign4/C4-01/attempts/a02")
BAND, FLOOR, MAXR, EPS = 1 / 16, 3 / 16, 1.0, 1e-9


def wilson_upper(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + s) / d


def exact_upper_zero(n, alpha=0.05):
    return 1 - alpha ** (1 / n)  # Clopper-Pearson one-sided for 0/n


def outcome(x):
    """improved > lethal > neutral > deleterious (on the parent env)."""
    pr = x["parent_reward"]
    r = x["evals"][x["parent_env"]]["reward_per_ask"]
    assert abs(r - x["classification"]["reward"]) < 1e-12
    if r > pr + BAND + EPS:
        return "improved"
    if x["D"] == "D2" or r <= EPS:
        return "lethal"  # degenerate (no/constant answer) or zero score
    if abs(r - pr) <= BAND + EPS:
        return "neutral"
    return "deleterious"


def main():
    dig = json.load(open(os.path.join(A02, "CHILDREN_DIGEST.json")))
    raw = gzip.open(os.path.join(A02, dig["gz"])).read()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == dig["raw_sha256"], "digest mismatch"
    rows = json.loads(raw)
    edits = [x for x in rows if not x["operator"].startswith("control_")]
    assert len(edits) == 5472, len(edits)

    out = {"source": os.path.relpath(A02, ROOT) + "/children.json.gz",
           "raw_sha256_verified": sha, "n_rows": len(rows), "n_edits": len(edits),
           "thresholds": {"band": BAND, "floor": FLOOR, "max_reward": MAXR}}

    # --- eligibility funnel
    by_parent = C.Counter()
    funnel = C.Counter()
    elig = []
    for x in edits:
        pr = x["parent_reward"]
        key = (x["stratum"], x["parent_env"], round(pr, 4), x["parent_degenerate"])
        by_parent[key] += 1
        if x["parent_degenerate"]:
            funnel["excluded_parent_degenerate"] += 1
        elif pr + BAND + EPS >= MAXR:
            funnel["excluded_parent_at_ceiling"] += 1
        elif not x["applied"]:
            funnel["excluded_could_not_apply"] += 1
        else:
            funnel["eligible"] += 1
            elig.append(x)
    out["edits_by_stratum_env_parentreward_degenerate"] = [
        {"stratum": k[0], "env": k[1], "parent_reward": k[2], "parent_degenerate": k[3], "edits": v}
        for k, v in sorted(by_parent.items())]
    out["funnel"] = dict(funnel)
    # loose variant: headroom = parent_reward < 1.0 (same set here; recorded)
    out["eligible_loose_parent_below_1"] = sum(
        1 for x in edits if not x["parent_degenerate"] and x["parent_reward"] < MAXR - EPS and x["applied"])
    out["eligible_incl_could_not_apply"] = funnel["eligible"] + funnel["excluded_could_not_apply"]
    out["n_eligible_parents"] = len({x["parent_id"] for x in elig})

    # --- outcomes among eligible
    n = len(elig)
    oc = C.Counter(outcome(x) for x in elig)
    out["eligible_outcomes"] = {k: {"count": oc.get(k, 0), "frac": oc.get(k, 0) / n,
                                    "wilson95_upper": wilson_upper(oc.get(k, 0), n)}
                                for k in ("improved", "neutral", "deleterious", "lethal")}
    out["eligible_D_labels"] = dict(C.Counter(x["D"] for x in elig))
    silent = sum(1 for x in elig if x["displacement"] == 0)
    exact_same = sum(1 for x in elig
                     if abs(x["evals"][x["parent_env"]]["reward_per_ask"] - x["parent_reward"]) < EPS)
    out["eligible_silent_displacement0"] = {"count": silent, "frac": silent / n}
    out["eligible_reward_exactly_unchanged"] = {"count": exact_same, "frac": exact_same / n}
    k = oc.get("improved", 0)
    out["improvement_upper95"] = {
        "k": k, "n": n,
        "rule_of_three": 3 / n if k == 0 else None,
        "clopper_pearson_one_sided": exact_upper_zero(n) if k == 0 else None,
        "wilson_two_sided_upper": wilson_upper(k, n),
        "pooled_5472_rule_of_three_for_contrast": 3 / 5472,
        "pooled_4866_applied_rule_of_three": 3 / 4866}
    # per-operator among eligible
    po = C.defaultdict(C.Counter)
    for x in elig:
        po[x["operator"]][outcome(x)] += 1
    out["eligible_by_operator"] = {o: dict(v) for o, v in sorted(po.items())}
    # also: all applied non-degenerate edits (incl. ceiling parents), for comparison
    nd = [x for x in edits if not x["parent_degenerate"] and x["applied"]]
    ocnd = C.Counter(outcome(x) for x in nd)
    out["applied_nondegenerate_all_parents_outcomes"] = {
        "n": len(nd), **{k2: ocnd.get(k2, 0) for k2 in ("improved", "neutral", "deleterious", "lethal")}}
    # exaptive (D6) among eligible: improvement elsewhere
    out["eligible_D6_exaptive"] = sum(1 for x in elig if x["D"] == "D6")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s3_result.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    json.dump(out, sys.stdout, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
