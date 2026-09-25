"""Cycle-3 reconciler notes, part C: P-E03 and P-E09 (re-run after CW01-D083) + defects D082/D083."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D = [
    {"id": "CW01-D082", "experiment_id": "cw01-loop3", "phase": "EXECUTE", "severity": "medium", "category": "control", "status": "OPEN",
     "defect_class": "A - control arm not a control",
     "title": "P-E03's DRIFT arm (uniform parent choice, no viability retention) melts down: mean reward 0.0 by generation 60 and 57/64 of its sample degenerate on W2_K2, so 'selected vs drift' compares working programs with broken ones",
     "evidence": "P-E03 RESULT.json group_means.top_drift (degenerate 57, loss .97); trajectories drift-1/2 reward_mean 0.40 -> 0.00. The paired tops-vs-own-ancestor contrast is unaffected.",
     "proposed_fix": "A descendant's drift control must hold viability (neutral-band acceptance, as C4-05's walk) so drift and selection differ only in the fitness ordering. The SELECTED reading rests on the paired ancestor contrast; the drift contrast is recorded as confounded.", "found_by": "P-E03 result"},
    {"id": "CW01-D083", "experiment_id": "cw01-loop3", "phase": "EXECUTE", "severity": "high", "category": "harness", "status": "FIXED",
     "defect_class": "B - arms not draw-matched (caught by the preregistered fail-closed check)",
     "title": "evolver.py seeded its stream with the ARM NAME, so sham and select arms could never share draws; P-E09's harness check (sham == select) fired and voided the first run; P-E03's first run (INHERITED) used the same seeding",
     "evidence": "P-E09 run 1: sham_equals_select False, disposition INVALID_HARNESS. Same defect class as the one caught by inspection in P-E06 before launch (evolution seed keyed by damage arm).",
     "proposed_fix": "Seed keyed by (LOOP_SEED, seed) only; both drivers re-run under their unchanged PREREG hashes; the invalid outputs kept as RESULT_invalid_D083.json. Run 1 and run 2 of P-E03 disagree on the within-lineage contrast (INHERITED vs SELECTED) with one seed pair each - recorded as a replication need, not averaged.", "found_by": "P-E09 preregistered harness check"},
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in D:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-ARCH4/M1", "P-E03", "RECONCILER (run 2 after D083; run 1's evidence line is SUPERSEDED): reading SELECTED on the paired contrast - selected top-32 lose .334 vs their own ancestor walkers .56 (-.129, below p05; the winning lineages' ancestors were mid-robust, .40-.50 / .45-.20, not the most robust available); length does not carry it (loss ~ log len -.05, select -.60). The drift contrast (-.64) is CONFOUNDED: the drift arm melts down (reward 0, 57/64 degenerate; D082). Ancestor vs parent -.015 (inside band) this time vs -.117 in run 1: the walk's contribution is seed-dependent. Lineages collapse to 2 ancestors by G60 under selection (3-4 under drift). Under selection length grows 19 -> 36-43 and persistent state words FALL (85 -> 17-33). Run 1 (invalid seeding) read INHERITED with tops == ancestor (.35 == .35): with one seed pair each the two runs disagree on the within-lineage contrast; replication across seeds is the continuation, not a law.", True,
                      state="ACTIVE", state_reason="selection built robustness within lineage in one pair of seeds and not in another; 4-6 seeds with a viable drift control decide")
    L.append_evidence("T-X13", "P-E09", "RECONCILER (run 2 after D083; run 1 INVALID_HARNESS, superseded; sham == select verified): in a substrate that CAN represent protection, computational weather selects MORE carried state, not less - persistent state words 310 vs 25 under select (+284, above p95; 116 and 530 in the two seeds), length 43 vs 39 (+3.5, above p95) - while damage loss barely moves (.309 vs .334, inside the band): reading NEITHER by the preregistered rules (neither protection nor avoidance), but the DIRECTION of the state response is the reverse of e01's. T-X13's 'weather selects avoidance' is organism-specific: with a redundancy channel available, weather selects state carriage without (yet) measurable protection at 60 generations.", True,
                      state="ACTIVE", state_reason="continuation: generation dose, damage probability dose, and whether the extra state is protective under fraction-matched damage")
    L.append_evidence("T-E07", "P-E09", "cross: the recorded escape (an organism that can represent protection) was tested in Proteus rather than by rebuilding e01; weather there raises state use 12x. The e01 stasis scope stands; the anomaly T-X13 now has a second substrate.", True)
    L.append_evidence("T-ARCH4/M1", "P-E09", "cross: 60 generations of weather do not lower damage loss beyond selection alone (-.024, inside band) although state and length rise; protection is not yet built or not yet measurable at k fixed (see T-X15).", False)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes C appended")


if __name__ == "__main__":
    main()
