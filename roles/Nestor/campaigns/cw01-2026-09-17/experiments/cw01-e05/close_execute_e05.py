"""Record the e05 EXECUTE outcome in recoverable campaign state, and file the
defect that EXECUTE's own fixtures exposed in the frozen driver.

Facts are read out of RESULT.json rather than transcribed, the timestamp is the real
system clock, and the next defect id is derived from the ledger rather than guessed.

This records the CANONICAL lane only. The independent replication lane is still in
flight; its evidence is folded in at CLOSE SCIENCE, not here.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"
LEDGER = BASE / "DEFECTS.jsonl"


def git(*a):
    return subprocess.run(["git", "-C", str(BASE.parents[3])] + list(a),
                          capture_output=True, text=True).stdout.strip()


def next_defect_id(entries):
    """Derive the next id from the ledger. Never guess it."""
    n = 0
    for d in entries:
        m = re.match(r"CW01-D(\d+)", str(d.get("id", "")))
        if m:
            n = max(n, int(m.group(1)))
    return "CW01-D%03d" % (n + 1)


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    s = res["summary"]

    # ---------------------------------------------------------------- ledger
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    did = next_defect_id(entries)
    already = any("decorative" in str(d.get("title", "")).lower() for d in entries)
    if not already:
        entries.append({
            "id": did, "ts": now, "campaign_id": "cw01-2026-09-17",
            "experiment_id": "cw01-e05", "phase": "QUALIFY/EXECUTE",
            "severity": "medium", "category": "instrument",
            "status": "OPEN",
            "title": "decorative guard: require_controlled called with the same dict twice",
            "evidence": "execute_e05.nsa calls LN.require_controlled(dict(kw), dict(kw), 'nsa/%s' % law) "
                        "- the same value on both sides. The guard is named in the frozen verdict "
                        "contract's intervention_control_relationship field and passes on every run, "
                        "but cannot fail on any input. What actually prevents CW01-D038a is **kw being "
                        "threaded through superadditivity() into solo_values(); fixture F4 measures that "
                        "propagation instead of trusting the guard. Exposed while writing F4.",
            "proposed_fix": "Cannot be fixed in place: execute_e05.py is frozen under contract c80b5bfd "
                            "and any change voids attempt cw01-e05-a01. Remains OPEN by design. "
                            "lib/guardproof.py was promoted from this finding and is binding for e06-e10: "
                            "prove_refuses() fails closed when a fixture's bad case is indistinguishable "
                            "from its good case, and GuardLedger.require() refuses to let a driver rely on "
                            "a guard with no observed refusal on record.",
        })
        LEDGER.write_text("\n".join(json.dumps(d, ensure_ascii=True) for d in entries) + "\n",
                          encoding="utf-8")

    # ----------------------------------------------------------------- state
    st = json.loads(STATE.read_text(encoding="utf-8"))
    st["updated_local"] = now

    for e in st["experiments"]:
        if e["id"] == "cw01-e05":
            e["status"] = "COMPLETE"
            e["disposition"] = "NULL"
            a = e["attempts"][0]
            a.update({
                "phase": "CLOSE_SCIENCE",
                "disposition": "NULL",
                "ended_local": now,
                "wall_s": res["wall_s"],
                "rows": 726,
                "rows_commit": "b942af7aa",
                "result_commit": "5c4de507a",
                "_no_result_yet": None,
            })
            e["headline"] = {
                "disposition_reason": res["disposition_reason"],
                "beats_best_single": s["beats_best_single"],
                "m3_interaction_positive": s["m3_interaction_positive"],
                "superadditivity_clears_null": s["superadditivity_clears_null"],
                "ablation_all_load_bearing": s["ablation_all_load_bearing"],
                "did_points_mean": s["did_points_mean"],
                "superadditivity_mean_pct": s["superadditivity_mean_pct"],
                "ancestor_relative_pct_mean": s["ancestor_relative_pct_mean"],
                "backend_counterfactual": res["backend_counterfactual"]["detail"],
                "determinism": "a01 EXECUTE reproduced QUALIFY calibration exactly at recorded "
                               "precision (did 19.4280 vs 19.43; sa 12.7863 vs 12.79; null "
                               "[-7.5130,+8.1245] vs [-7.51,+8.12]; ablation 55.4894 vs 55.49)",
                "mechanism_of_null": "superadditivity and full load-bearing fail in EXACTLY the same "
                                     "two replicates (r03, r04) - one underlying fact, not two. Null "
                                     "band widths are comparable (13.4-17.5) while effect sizes span "
                                     "-4.8 to +28.2, so the failure is the drawn world, not measurement "
                                     "noise. In r03/r04 the best set is measurably SUB-additive.",
                "why_did_survived": "the disjunctive term is stable across all four worlds (-22.4 to "
                                    "-26.6) because it is dominated by coverage overlap, an arithmetic "
                                    "property; the conjunctive term swings 33 points. A within-set "
                                    "across-law contrast is robust to the world draw; a raw across-world "
                                    "magnitude is not. Retrospective vindication of D040/D041.",
                "freeze_boundary_value": "a01 - the replicate used for QUALIFY calibration - passes "
                                         "everything and reads COMPLETE alone. r03 and r04 refute it. "
                                         "The criterion was hashed and frozen before the first organism "
                                         "was evaluated, so the only available move was to report NULL.",
            }
            e["limitations"] = [
                "An 8-gene real-valued inclusion vector, not a rich program.",
                "Four replicates. The 2/4 split is a small-sample statement about how often these "
                "worlds compose, NOT an estimate of that rate.",
                "Per-replicate BEST/WORST sets differ ([0,2,4], [1,2,6], [0,4,5], [0,3,7]) because each "
                "attempt_id draws its own latent world. The contract's BEST/WORST bind a01 only.",
                "conjunctive_fraction was NOT swept in this attempt; WORLD.json declares it swept and "
                "the sweep is expansion, not minimal form.",
                "Two claims survive the NULL and must not be buried by it: mixtures beat the best single "
                "component 4/4, and the composition law benefits a well-chosen set more than a poor one "
                "4/4. What fails is the strictly stronger claim that a mixture exceeds the SUM OF ITS "
                "PARTS. In half these worlds the value is accumulation, not composition.",
                "Whether a world composes may be predictable from its capability structure BEFORE running "
                "it. This attempt did not test that; it would need a new pre-registration.",
            ]

    st["active"] = {
        "experiment_id": "cw01-e05",
        "attempt_id": "cw01-e05-a01",
        "phase": "CLOSE_SCIENCE",
        "phase_completed": ["RECONCILE", "PREFLIGHT", "INSTANTIATE", "QUALIFY", "EXECUTE"],
        "title": "Mixture of marginally useful organisms",
        "disposition": "NULL",
        "verdict_contract_sha256": res["verdict_contract_sha256"],
        "pending": "independent replication lane in flight on branch nestor/e05-replica-2026-09-18 "
                   "(worktree F:/Prometheus-worktrees/nestor-e05-replica). CLOSE SCIENCE folds in its "
                   "reconstruction evidence. VERIFY ABSENCE is deliberately deferred until that lane "
                   "finishes, because its live processes would otherwise read as stray residue.",
    }

    t = st["campaign_totals"]
    t["experiments_attempted"] = 5
    t["null"] = 2
    t["defects_logged"] = len(entries)
    t["defects_per_experiment"]["e05"] = 8
    if "lib/guardproof.py" not in t["reusable_components_landed"]:
        t["reusable_components_landed"].append("lib/guardproof.py")

    for a in ["experiments/cw01-e05/RESULT.json - disposition NULL, 4 replicates, frozen contract",
              "experiments/cw01-e05/MECHANISM_OF_NULL.md - why it is NULL and what survives it",
              "experiments/cw01-e05/rows/cw01-e05-a01.jsonl - 726 rows, committed b942af7aa",
              "lib/guardproof.py - a guard is not evidence until observed refusing; fails closed on a "
              "vacuous fixture whose bad case equals its good case"]:
        if a not in st["durable_artifacts"]:
            st["durable_artifacts"].append(a)

    st["factory_findings_so_far"].append(
        "e05 EXECUTE is the freeze boundary paying for itself. a01, the replicate whose numbers "
        "calibrated QUALIFY, passes every condition and reads COMPLETE on its own; r03 and r04 refute "
        "it. Because the contract was hashed and frozen before the first organism was evaluated, the "
        "criterion could not become an experimental object for the eighth time, and the only available "
        "move was to report NULL. Cost: a result I would have liked. Benefit: the result is true.")

    # ASCII-safe: a recovery reader's default platform encoding is not ours to choose
    # (CW01-D050 - ensure_ascii=False made this file crash a naive open() on Windows).
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")

    back = json.loads(STATE.read_text(encoding="utf-8"))
    print("ledger entries      : %d (new: %s)" % (len(entries), did if not already else "none, already filed"))
    print("e05 status          : %s / %s" % (back["experiments"][4]["status"],
                                             back["experiments"][4]["disposition"]))
    print("active.phase        : %s" % back["active"]["phase"])
    print("phase_completed     : %s" % back["active"]["phase_completed"])
    print("campaign totals     : attempted %d, complete %d, null %d, inconclusive %d, defects %d"
          % (back["campaign_totals"]["experiments_attempted"], back["campaign_totals"]["complete"],
             back["campaign_totals"]["null"], back["campaign_totals"]["inconclusive"],
             back["campaign_totals"]["defects_logged"]))
    print("durable_artifacts   : %d" % len(back["durable_artifacts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
