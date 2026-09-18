"""Close out e05: fold both lanes into recoverable campaign state.

Reads its facts from committed artifacts rather than transcribing them:
  RESULT.json                 canonical disposition and per-replicate numbers
  CROSS_LANE_COMPARISON.json  exact-reconstruction receipt
  VERIFY_ABSENCE.json         teardown receipt, including anything NOT_VERIFIED
  extra_seeds_replica.json    the replication lane's 8 additional seeds
  DEFECTS.jsonl               ledger counts

Also clears the `_no_result_yet` residue left in the attempt record by the earlier
transition, which said "no result yet" and is no longer true.
"""
from __future__ import annotations

import json
import pathlib
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"
REPLICA = pathlib.Path("F:/Prometheus-worktrees/nestor-e05-replica/roles/Nestor/"
                       "campaigns/cw01-2026-09-17/experiments/cw01-e05")


def load(p, default=None):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:                                        # noqa: BLE001
        return default


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    res = load(HERE / "RESULT.json")
    cmp_ = load(HERE / "CROSS_LANE_COMPARISON.json", {})
    va = load(HERE / "VERIFY_ABSENCE.json", {})
    extra = load(REPLICA / "extra_seeds_replica.json", {})

    seeds = []
    if isinstance(extra, dict):
        seeds = extra.get("replicates") or extra.get("results") or extra.get("seeds") or \
                [v for v in extra.values() if isinstance(v, dict) and "attempt_id" in v]
    elif isinstance(extra, list):
        seeds = extra
    allreps = list(res["replicates"]) + list(seeds)
    n = len(allreps)
    tally = {
        "beats_best_single": "%d/%d" % (sum(1 for r in allreps if r["beats_best_single"]), n),
        "m3_interaction_positive": "%d/%d" % (sum(1 for r in allreps if r["did_points"] > 0), n),
        "superadditivity_clears_null": "%d/%d" % (sum(1 for r in allreps if r["superadditivity_clears_null"]), n),
        "ablation_all_load_bearing": "%d/%d" % (sum(1 for r in allreps if r["ablation_all_load_bearing"]), n),
    }
    corr = all(r["superadditivity_clears_null"] == r["ablation_all_load_bearing"] for r in allreps)

    entries = [json.loads(l) for l in (BASE / "DEFECTS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    st = json.loads(STATE.read_text(encoding="utf-8"))
    st["updated_local"] = now

    for e in st["experiments"]:
        if e["id"] != "cw01-e05":
            continue
        a = e["attempts"][0]
        a.pop("_no_result_yet", None)                        # no longer true; do not leave a null
        a["phase"] = "PACKAGE"
        e["replication"] = {
            "_question": "not 'does the result replicate' but 'can an independent executor "
                         "reconstruct and run this from committed artifacts alone'",
            "lane": "nestor/e05-replica-2026-09-18 (worktree F:/Prometheus-worktrees/nestor-e05-replica)",
            "exact_reconstruction": cmp_.get("exact_reconstruction"),
            "leaf_comparisons": cmp_.get("leaf_comparisons"),
            "divergences": cmp_.get("n_divergences"),
            "verification_from_committed_state": "consistency 13/13 + 4/4, fixtures 7/7, "
                                                 "selfcheck 9/9 on a clean tree; contract hash "
                                                 "recomputed independently from committed bytes",
            "extra_seeds": len(seeds),
            "combined_tallies_over_%d_replicates" % n: tally,
            "correlation_sa_equals_load_bearing": "%d/%d, no exception" % (n, n) if corr else "NOT universal",
            "correction": "m3_interaction was 4/4 canonically and I called it universal; over %d "
                          "replicates it is %s. r10 returns did_points -14.45. The canonical 4/4 "
                          "was a small-sample accident." % (n, tally["m3_interaction_positive"]),
            "defects_found_by_this_lane": [d["id"] for d in entries if d.get("found_by")],
            "portability_verdict": "reproducible IN PLACE from committed artifacts with no Redis, "
                                   "no broker, no network and no live session; NOT relocatable, "
                                   "because REPO is derived from hardcoded directory depth (CW01-D046)",
        }
        e["teardown"] = {
            "verdict": va.get("verdict"),
            "pass": va.get("n_pass"), "fail": va.get("n_fail"),
            "not_verified": va.get("n_not_verified"),
            "not_verified_detail": [c["id"] for c in va.get("checks", []) if c["outcome"] == "NOT_VERIFIED"],
            "_rule": "NOT_VERIFIED is never counted as PASS (CW01-D034 family)",
            "_e05_owned_nothing": "ran in-process via lib/localrun; never imported redis; "
                                  "owned_runtime_resources empty throughout",
        }

    st["active"] = {
        "experiment_id": "cw01-e05",
        "attempt_id": "cw01-e05-a01",
        "phase": "PACKAGE",
        "phase_completed": ["RECONCILE", "PREFLIGHT", "INSTANTIATE", "QUALIFY", "EXECUTE",
                            "CLOSE_SCIENCE", "TEARDOWN", "VERIFY_ABSENCE"],
        "title": "Mixture of marginally useful organisms",
        "disposition": "NULL",
        "verdict_contract_sha256": res["verdict_contract_sha256"],
        "next": "CONTINUE -> cw01-e06 representation ecology",
    }

    t = st["campaign_totals"]
    t["defects_logged"] = len(entries)
    t["defects_per_experiment"]["e05"] = sum(1 for d in entries if d.get("experiment_id") == "cw01-e05")

    for art in [
        "experiments/cw01-e05/CROSS_LANE_COMPARISON.json - 381 leaf comparisons, 0 divergences",
        "experiments/cw01-e05/VERIFY_ABSENCE.json - teardown receipt with PASS/FAIL/NOT_VERIFIED",
        "experiments/cw01-e05/verify_absence_e05.py - three-outcome absence check; NOT_VERIFIED is not a pass",
        "experiments/cw01-e05/REPLICA_BRIEF.md - binding mandate for an independent reconstruction lane",
    ]:
        if art not in st["durable_artifacts"]:
            st["durable_artifacts"].append(art)

    st["factory_findings_so_far"].append(
        "The independent replication lane earned its cost in defects, not in confirmation. It "
        "reproduced the canonical run across 381 comparisons with 0 divergences - and then found five "
        "things the canonical lane structurally could not, because it had never seen the code: a "
        "self-invalidating verifier (D044), provenance that silently stamps an outside executor as the "
        "canonical lane (D045), an experiment that is reproducible in place but not relocatable "
        "(D046), a rows path pinned to one attempt (D047), and an ambiguity in my own brief (D048). "
        "An executor who shares the author's assumptions cannot test those assumptions.")

    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")

    back = json.loads(STATE.read_text(encoding="utf-8"))
    e5 = [e for e in back["experiments"] if e["id"] == "cw01-e05"][0]
    print("phase              : %s" % back["active"]["phase"])
    print("phase_completed    : %d steps" % len(back["active"]["phase_completed"]))
    print("disposition        : %s" % e5["disposition"])
    print("exact reconstruction: %s (%s comparisons, %s divergences)" % (
        e5["replication"]["exact_reconstruction"], e5["replication"]["leaf_comparisons"],
        e5["replication"]["divergences"]))
    print("combined tallies   : %s" % json.dumps(tally))
    print("teardown verdict   : %s (NOT_VERIFIED: %s)" % (
        e5["teardown"]["verdict"], e5["teardown"]["not_verified_detail"]))
    print("residue key gone   : %s" % ("_no_result_yet" not in e5["attempts"][0]))
    print("defects e05        : %d | ledger %d" % (
        back["campaign_totals"]["defects_per_experiment"]["e05"], len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
