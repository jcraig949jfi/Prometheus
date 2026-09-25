"""Close cw01-e07 in CAMPAIGN_STATE.json: disposition, totals derived from the ledger,
ASCII-safe write, then the recordsafety gates (portability + tally agreement) fail closed."""
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
STATE = CAMPAIGN / "CAMPAIGN_STATE.json"
LEDGER = CAMPAIGN / "DEFECTS.jsonl"


def main():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    disp = json.loads((HERE / "DISPOSITION.json").read_text(encoding="utf-8"))
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    exp = next(e for e in st["experiments"] if e["id"] == "cw01-e07")
    exp["status"] = "COMPLETE"
    exp["attempts"] = [{"attempt_id": "cw01-e07-a01", "phase": "QUALIFY",
                        "disposition": "INCONCLUSIVE / DESIGN UNREACHABLE",
                        "started_local": "2026-09-18 07:40:00", "ended_local": now,
                        "executed_under_frozen_contract": False, "gate_runs": 2}]
    exp["disposition"] = "INCONCLUSIVE"
    exp["headline"] = {
        "reason": "pre-QUALIFY gate refused the world twice (P1, P4); the one permitted correction (lifetimes_per_eval 2->8) did not admit it; no lineage was evolved under weather",
        "P1_damage_fires": False, "P2_sham_inert": True, "P3_non_lethal": "vacuous PASS",
        "P4_separable": False, "P5_blind": True,
        "accumulator_AURC_at_primary": 0.956, "accumulator_rho0_at_primary": 0.80,
        "P1_attainable_only_at_f_ge": 0.44,
        "pilot_intact_vs_accumulator": "0.37-0.43 vs 0.74; state dependence ~0.05-0.09",
        "gate_credibility": "5/5 known-broken fixtures refused for the expected predicate, in both runs",
        "not_null_because": "the causal comparison was never posed; NULL would claim a finding about the world that was not earned",
    }
    exp["limitations"] = disp["limitations_and_residuals"]
    exp["what_a_future_attempt_would_need"] = disp["what_a_future_attempt_would_need"]

    st["active"] = {"experiment_id": "cw01-e07", "attempt_id": "cw01-e07-a01",
                    "phase": "CLOSED_BEFORE_EXECUTE",
                    "disposition": "INCONCLUSIVE / DESIGN UNREACHABLE",
                    "phase_completed": ["RECONCILE", "PREFLIGHT", "INSTANTIATE", "QUALIFY"],
                    "next": "CONTINUE -> cw01-e08 rank-tax tensor evolution"}
    st["updated_local"] = now
    st["owned_runtime_resources"] = []

    st["durable_artifacts"] += [
        "experiments/cw01-e07/PREREGISTRATION.md - science fixed before code; Amendment 1 (pre-data fixture corrections), Amendment 2 (the one correction after refusal, thresholds untouched)",
        "experiments/cw01-e07/WORLD.json - declarative; every gate threshold read from here",
        "experiments/cw01-e07/world_e07.py - organism, damage family, bit-identical sham, schedules, vectorised runner, robustness (ratio of means), ANCOVA contrast with exact relabelling null",
        "experiments/cw01-e07/gate_e07.py - P1-P5 admissibility gate + five known-broken fixtures; refused the world twice, refused all fixtures twice",
        "experiments/cw01-e07/GATE_E07_run1.json, GATE_E07.json - both gate runs",
        "experiments/cw01-e07/PROBE_E07.json, PROBE2_E07.json, PROBE3_E07.json - probes A-G: P1 attainability curve, state dependence, evolvability at the real budget, diagonal recurrence, three search-regime features",
        "experiments/cw01-e07/DISPOSITION.json - INCONCLUSIVE / DESIGN UNREACHABLE with what a future attempt needs",
    ]
    st["factory_findings_so_far"].append(
        "e07 was refused by its own admissibility gate in ~2 s per run, twice, before any lineage was evolved under weather; the full EXECUTE (96 lineages) would have reached the same INCONCLUSIVE at far greater cost. The refusal exposed two independent defects, and the one-correction budget could address only one: a preregistered magnitude threshold frozen without its attainable range (D058) and a search that never reaches state-dependent computation (D059). Seven cheap probes (~4 s) chose the correction, refuted my own meltdown reading of a noisy trajectory, and produced a measured list of what a future attempt needs. The doctrine that survives: a gate threshold must ship with the reference probe's attainability curve, computed before freezing.")

    # totals DERIVED from the ledger at write time AND enforced by the gate at check time
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    per = collections.Counter(d.get("experiment_id") for d in entries)
    tot = st["campaign_totals"]
    tot["experiments_attempted"] = 7
    tot["inconclusive"] = 3
    tot["defects_logged"] = len(entries)
    tot["defects_per_experiment"] = {str(k).replace("cw01-", ""): v for k, v in sorted(per.items())}
    tot["science_defects"] = tot.get("science_defects", 0) + 2      # D058, D059

    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(STATE)
    RS.require_ascii_safe(HERE / "DISPOSITION.json")
    v = RS.require_tally_consistent(STATE, LEDGER)
    print("CAMPAIGN_STATE closed for e07 | tally %s (%d) | ascii PASS" % (v["outcome"], v["derived"]["total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
