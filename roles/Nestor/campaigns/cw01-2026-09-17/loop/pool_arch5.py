"""Archaeon Campaign 5 (origin/main cf841ed6d..9cd33ff1e) enters the pool as T-ARCH5, a sibling
descendant of T-ARCH4 run by the Archaeon seat; its findings are appended as evidence on T-ARCH4's
scoped nodes; batch-C candidates it already executed are marked SUPERSEDED (append-only amendment
lines in PERTURBATIONS.jsonl; the originals stay). Computational scope as in pool_arch4.py."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import recordsafety as RS      # noqa: E402
import looprun as L            # noqa: E402

POOL, STATE, PERT = HERE / "TRAJECTORIES.jsonl", HERE / "STATE.jsonl", HERE / "PERTURBATIONS.jsonl"
ORIGIN = "archaeon/campaign5 @ origin/main 9cd33ff1e (Archaeon[m2-49ee5a4d], 2026-09-18 14:16Z-15:07Z)"

REC = dict(trajectory_id="T-ARCH5", kind="experiment-campaign", origin=ORIGIN, parent="T-ARCH4", age="2026-09-18 15:07Z",
           scope="computational artificial life on the Proteus foundry VM; representation B = a campaign-scoped narrow in-table encoding of the same 25-opcode table (archaeon/campaign5/repb), Proteus VM untouched",
           originating_question_verbatim="(Campaign 5 report, section 0) escape the neutral cliff: create a real local failure boundary (representation B) and test whether a region of bounded variation lets evolution discover more efficiently",
           derived_operationalization="Phase A on the OLD substrate: C5-01 deep walk (6 walkers x 64 steps, 282 walkers), C5-02 fair lateral ecology at equal TOTAL compute on screened worlds (WORLD_SCREEN: 9 eligible of 25, rule in code first); Phase B: C5-03 representation qualification (F1-F8), C5-04 generator x representation, C5-05 damage geometry under B (C4-01 replicated 5,586/5,586; matched perturbations under OLD/B_FAIL/B_FIZZLE), C5-06 local failure vs recovery, C5-07 cost of insulation, C5-08 robustness mechanism (dead-code ablation), C5-09 reach at equal compute (four arms), C5-10 held-out trial",
           translation_loss="FAIL = the first fault kills the whole evaluation (maximal HARD, D5-002 default); FIZZLE = the faulting instruction is skipped as NOP",
           world_substrate="C4 family plus screened worlds W2_K2d1, W2_K2_rand, W3_K3, W4_K4; held-out W3_K3d1, W2_K2d4",
           representation="OLD (modulo) and B (narrow in-table; canonicalize; valid/raw/injected generators; grammar B)",
           search_process="as C4 plus EvolutionB", pressure="reward_per_ask", ruler="as C4 with preregistered rules per slot",
           compute_budget="51 minutes wall for ten slots",
           result="BOUNDARY_CREATED_NO_DISCOVERY_GAIN. C5-01 MIXED (exaptation .050/.064/.078/.082 at 16/32/48/64; yield per evaluation .00127 -> .00082 below the single-edit .0012): PRESERVE_NEUTRAL NO. C5-02 A_TAKEOVER_WITHOUT_IMPROVEMENT (0/24 cells improved at equal total compute; rescued share .83/.67/.50/.20). Phase A = OLD_SUBSTRATE_EXHAUSTED (D5-009). C5-03 REPRESENTATION_QUALIFIED (a02, labelled post-hoc amendment D5-008). C5-05: boundary fires on 84-86% of crossing children; D5 of non-crossing children unchanged to the third decimal; recovered-competent .46/.42 under FIZZLE; D7 = 0. C5-06 REAL_LOCAL_RECOVERY (229 replicated recoveries where skipping an executed opcode fault preserves function vs 154 insulation losses on register faults). C5-07 INSULATION_CHEAP (ops ratio 1.00). C5-08 MIXED (length carries robustness .17 -> .71; dead-code ablation moves neutral share .435 -> .409 only; boundary component .021 independent of both). C5-09 NO_GAIN (0/+1/+1 nets; no first held-out gain in 96 cells). C5-10 NO_CONDITION_SELECTED.",
           failure_surface="a surviving child under FIZZLE is its parent with a hole in it (displacement .015): bounded variation exists but is not a region from which evolution discovers more efficiently at equal compute on worlds with measured headroom",
           anomalies=["opcode faults skipped = recovery (229) but register faults: wrap works and skip loses (154) - the fault KIND decides", "rescued lineages take over receiving populations without improving them (again)", "C5-03 a01 failed its own text (count-TVD .42, volatile timings) and qualified only under a labelled post-hoc amendment"],
           unrun_interventions=["mutation geometry (locality, operand vs opcode, weight balance) under either representation", "population structure", "walk band relative to the current walker", "noisy/interfering score environments", "the degenerate swamp under B"],
           fossils=["archaeon/campaign5/C5-NN/attempts/*", "repb/ (the representation)", "DAMAGE_GEOMETRY_MAP_V2", "REPRESENTATION_COMPARISON", "WORLD_SCREEN_2026-09-18.json"],
           assumptions_at_time=["FAIL = whole-evaluation death is the maximal HARD", "equal total compute is the fair budget for lateral"],
           later_changes_relevant=[], last_perturbation="C5-10 a02", marginal_information_history=["ten slots: a real boundary created; no discovery gain: material"],
           stasis_state="ACTIVE")

SUPERSEDED = {
    "P-C01": ("C5-05 / C5-03 (representation B FIZZLE on canonicalised parents; census replicated 5,586/5,586)", "waits unless replication under Nestor's own decode layer is itself the point"),
    "P-C02": ("C5-05 (B_FAIL: first fault kills the evaluation - a stronger HARD than trap-to-HALT-the-tick)", "the tick-halt variant is a THIRD rule; deferred, not dropped"),
    "P-C09": ("C5-01 (depth 64, 6 walkers, 282 walkers; PRESERVE_NEUTRAL NO)", "identical condition already run"),
    "P-C11": ("C5-02 (equal-total-compute lateral on screened unsolved worlds; A_TAKEOVER_WITHOUT_IMPROVEMENT)", "identical condition already run"),
}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    if "T-ARCH5" not in existing:
        r = dict(REC)
        r["recorded"] = ts
        with POOL.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
        with STATE.open("a", encoding="utf-8") as sh:
            sh.write(json.dumps({"trajectory_id": "T-ARCH5", "ts": ts, "state": "ACTIVE", "reason": "sibling descendant recorded from origin/main",
                                 "marginal_information_history": REC["marginal_information_history"]}, ensure_ascii=True) + "\n")
    # evidence on the scoped nodes (append-only; idempotent by (trajectory, perturbation) pair)
    seen = {(json.loads(l)["trajectory_id"], json.loads(l)["perturbation_id"]) for l in (HERE / "EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    notes = [
        ("T-ARCH4/R1", "C5-05", "representation B (narrow in-table, FAIL/FIZZLE) built and qualified by Archaeon; C4-01 census replicated exactly; boundary fires on 84-86% of crossing children; FIZZLE recovers competence in .42-.46 of them; D7 still 0", True,
         "TEMPORAL_STASIS[representation=modulo-decode-v0.4]", "the modulo substrate was declared OLD_SUBSTRATE_EXHAUSTED by C5 Phase A after a deep walk and a fair lateral run; the next informative perturbation of the representation is now B-relative, not modulo-relative"),
        ("T-ARCH4/S1", "C5-01", "deep walk to 64: exaptation .050 -> .082, marginal yield per step falls 4x, yield per evaluation below a random single edit's; PRESERVE_NEUTRAL NO", True,
         "TEMPORAL_STASIS[search_depth=walk-depth]", "depth alone saturates; further depth is not informative; other search-dynamics axes (band rule, proposal weights) remain open"),
        ("T-ARCH4/D1", "C5-02", "fair lateral ecology at equal total compute on screened unsolved worlds: 0/24 cells improved; takeover without improvement replicated", True,
         "TEMPORAL_STASIS[damage_rescue=lateral-by-reward]", "lateral entry by measured reward is exhausted at this scale under two budget rules; other rescue geometries (locality, multi-donor, timing) remain open"),
        ("T-ARCH4/P1", "C5-09", "reach at equal compute under OLD and B, four arms: NO_GAIN in 96 cells", True, None, None),
        ("T-ARCH4", "C5", "Campaign 5 closed BOUNDARY_CREATED_NO_DISCOVERY_GAIN: the neutral cliff was described one level deeper (a fizzled child is its parent with a hole, displacement .015), not escaped", True, None, None),
    ]
    for tid, pid, summary, material, state, reason in notes:
        if (tid, pid) in seen:
            continue
        L.append_evidence(tid, pid, summary, material, detail={"source": ORIGIN}, state=state, state_reason=reason)
    # supersession amendments (append-only lines; prioritize.py merges by id)
    have = set()
    for l in PERT.read_text(encoding="utf-8").splitlines():
        if l.strip():
            d = json.loads(l)
            if d.get("amend") and d.get("superseded_by"):
                have.add(d["id"])
    with PERT.open("a", encoding="utf-8") as fh:
        for pid, (by, note) in SUPERSEDED.items():
            if pid in have:
                continue
            fh.write(json.dumps({"id": pid, "amend": True, "superseded_by": by, "note": note, "recorded": ts}, ensure_ascii=True) + "\n")
    for p in (POOL, STATE, PERT, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("T-ARCH5 recorded; evidence appended; superseded:", list(SUPERSEDED))


if __name__ == "__main__":
    main()
