"""Cycle-1 append-only corrections and defects. Earlier evidence events are NOT rewritten; these are
added alongside them so a reader sees both the driver's frozen reading and the reconciler's."""
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
C = "cw01-2026-09-17"
DEFECTS = [
    {"id": "CW01-D070", "experiment_id": "cw01-loop1", "phase": "EXECUTE", "severity": "medium", "category": "world",
     "status": "OPEN", "defect_class": "B - latent world defect surfaced by a perturbation",
     "title": "world_e06 target generator can return an EMPTY band (graph None) for some attempt ids",
     "evidence": "P-A07 run 1 drew attempt_target under attempt id 'cw01-loop1-PA07|rr0.0' and one reuse band came back with graph=None; make_items then called tree_eval(None) and crashed (TypeError). e06 and P-A08 never hit it because their attempt ids happened to draw non-empty bands. world_e06._make_graph is not modified (frozen); the driver now draws ONE verified target for all rates.",
     "proposed_fix": "Not fixed in the frozen module. Any future e06 descendant must verify every band has a graph before use, or fix _make_graph in a NEW world version. Logged and continued.",
     "found_by": "P-A07 run 1 traceback"},
    {"id": "CW01-D071", "experiment_id": "cw01-loop1", "phase": "CLOSE_SCIENCE", "severity": "high", "category": "ruler",
     "status": "OPEN", "defect_class": "A - interpretation hazard on a frozen rule",
     "title": "P-B03 retention ratio is ill-conditioned in e01's world: useful computation above floor is ~5% of score",
     "evidence": "P-B03 (e07 damage in e01's world) reads NEGATIVE under its frozen ability-adjusted contrast (c -0.26, band [-0.12, +0.12]) while RAW retention is twice as high under weather (r STATIC 0.181, WEATHER 0.359) and intact score is 7% lower (0.0547 vs 0.0508). r = (S_dmg - F)/(S_int - F) divides by a margin of ~0.003 (e01's retention advantage), so a 7% change in S_int moves r by tens of percent; the covariate adjustment then extrapolates a steep within-arm r~S_int slope across a 0.004 gap and flips the sign. Damage fires (STATIC r 0.18) and the sham is bit-inert (max deviation 0.0), so the question IS posable here, which was the transplant's point.",
     "proposed_fix": "The frozen disposition stands as recorded (NEGATIVE under the preregistered statistic). For the record and the next cycle: report absolute retained score (S_dmg - F) alongside the ratio, and preregister a usefulness margin scaled to the world's own effect size; a re-pose with the absolute measure and a severity dose is the natural next perturbation of T-E07 in this world.",
     "found_by": "reconcile of P-B03 RESULT.json"},
]


def main():
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in DEFECTS:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": C}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    # corrective / supplementary evidence (append-only)
    L.append_evidence("T-X04", "P-A08", "RECONCILER NOTE: at phi 0.50 and 0.75 NEITHER substrate invades the other (both invaders go extinct): "
                      "contingent, founder-controlled dominance - one of the five regimes e06 required reachable. The axis runs TAPE-dominance (phi 0) "
                      "-> TREE-dominance (0.25) -> bistability (0.5, 0.75) -> TREE-dominance (1.0). Not mutual invasibility, but a third regime the driver's rule did not name.",
                      True, state="ACTIVE", state_reason="a bistable regime exists on the geometry axis; next: seeded-frequency sweep at phi 0.5 to map the separatrix")
    L.append_evidence("T-E06", "P-A08", "RECONCILER NOTE: contingent dominance located at intermediate target geometry (see T-X04); e06's reachability requirement "
                      "gains one regime (history-dependent dominance) even though coexistence is still unreached.", True)
    L.append_evidence("T-X08", "P-B09", "RECONCILER NOTE: the inversion is NOT schedule specialisation: lineages evolved under a TTL distribution show the same rel(7) 0.83 "
                      "and rel(30) 1.07 as fixed-TTL lineages, and their absolute scores at every TTL are within the band. The phenotype is intrinsic to the "
                      "channel economics (a faster-forgetting channel hurts any policy), so the 'tuned to one schedule' reading is falsified.",
                      True, state="TEMPORAL_STASIS", state_reason="the specialisation explanation is falsified and the remaining explanation (intrinsic channel economics) has no further perturbation available at this scale")
    L.append_evidence("T-E07", "P-B03", "RECONCILER NOTE (CW01-D071): raw retention DOUBLED under weather (0.181 -> 0.359) at a 7% intact cost; the frozen "
                      "ability-adjusted ratio reads NEGATIVE because the normalising margin is ~0.003. Both readings are on record; neither is promoted. "
                      "Material: the damage question is posable in e01's world (damage fires on evolved organisms, sham bit-inert).",
                      True)
    L.append_evidence("T-E09", "P-A11", "RECONCILER NOTE: on e07's task all four arithmetic chains converge to exactly the single-op ceiling (0.266) and scrambled "
                      "chains to the floor (0.161); the stateless linear optimum is 0.354. A 3-op digit chain cannot even reach a linear readout: the boundary "
                      "is the chain representation, not w13.", True)
    L.append_evidence("T-E08", "P-A01", "RECONCILER NOTE: under held-out selection the pilot is BIMODAL - 2 lineages 8/8 competent (held64 175-184), 2 lineages 0/8 "
                      "(156-160). Lineages either generalise fully or not at all; the eligibility surface is a lineage-level coin, not a representative-selection artefact.", True)
    L.append_evidence("T-X02", "P-A04", "RECONCILER NOTE: 128 train seeds raise held64 to 178.8 (vs 159.9 at 8 seeds) and competent reps to 5.3/8 (vs 4.0), inside the "
                      "tiny-n relabelling band (3 vs 4 lineages); 32 seeds gave 2.0/8 - the breadth response is noisy at this lineage count. Directionally supportive, not established.", False)
    L.append_evidence("T-X01", "P-A10", "RECONCILER NOTE: the hitchhiking floor is SELECTION STRENGTH - tournament 1 (pure drift) fixes at median 76.5 ~ N=96, tournament 2 at 55.5, "
                      "tournament 3 (as run) at 31, and 4 demes of 24 at 21.5 (small-deme drift). Every ecological noise floor in e06 was measured under 3x-accelerated fixation.", True)
    L.append_evidence("T-X09", "P-B04", "RECONCILER NOTE: with T2 impossible without T1 the K1 knockout is load-bearing in 4/4 (loss 0.08-0.11 vs sham 0.00) - the first executed "
                      "knockout in this lineage - yet p_factor still fixes first or simultaneously (foundation-first 1/4): both genes rise together because p_factor is "
                      "neutral until p_norm rises. Order is not the right ruler for a co-required pair; the knockout is.", True)
    print("appended D070, D071 and 9 reconciler evidence notes")


if __name__ == "__main__":
    main()
