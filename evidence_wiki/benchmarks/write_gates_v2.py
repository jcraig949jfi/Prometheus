import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

gates = {
 "adjudicated": time.strftime("%Y-%m-%d %H:%M"),
 "prereg": "docs/PREREGISTRATION_V2.md frozen at cab825adc before any designer launch",
 "gates": {
  "G1_prior_integrity": {"verdict": "PASS", "evidence": "V0/V1 artifacts untouched; V2 additive under v2/"},
  "G2_task_discrimination": {"verdict": "PARTIAL", "evidence": "Arm A mean core recall 0.474 in frozen band [0.05,0.70] (retrieval side PASS); Arm A mean composite 3.72 > 3.4 -> the DESIGN instrument shows a ceiling per the frozen rule; retrieval conclusions stand, the design null carries a ceiling caveat"},
  "G3_retrieval_advantage": {"verdict": "FAIL_POOLED / MODEL_SPECIFIC_PASS", "evidence": "pooled dCore +0.151 < 0.25; sonnet +0.300 (clean +0.250, overlap +0.333); haiku +0.011 -> MODEL_SPECIFIC_ADVANTAGE_ONLY"},
  "G4_negative_evidence_retrieval": {"verdict": "FAIL_POOLED / MODEL_SPECIFIC_PASS", "evidence": "pooled dNeg +0.243; sonnet +0.405; haiku +0.090; correction recall 0.667 vs 0.333"},
  "G5_design_advantage": {"verdict": "NOT_DEMONSTRATED", "evidence": "primary delta -0.016 vs threshold +0.40; wins 8/19; D3+D4 subcomposite -0.02; clean tasks -0.234 (wiki slightly worse), overlap +0.143"},
  "G6_metabolization_differential": {"verdict": "NOT_DEMONSTRATED", "evidence": "evidence-to-decision reuse near-universal in BOTH arms (B via claim ids; A via repo paths and harness-injected memory doctrine)"},
  "G7_duplication_walkin": {"verdict": "ADJUDICATED_NULL", "evidence": "walk-ins rare and balanced; one duplication-adjacent cell (T04 blind-R scored D1=0 by both scorers) with no arm asymmetry"},
  "G8_falsifier_improvement": {"verdict": "NOT_DEMONSTRATED", "evidence": "D3 deltas ~0; both arms at high falsifier quality"},
  "G9_misleading_resistance": {"verdict": "PASS", "evidence": "T06 misleading adoption 0 in every arm: all designers predicted conditional/small transplant gains with kill conditions; wiki did not increase anchoring"},
  "G10_retrieval_mediation": {"verdict": "DIAGNOSED_NO_MEDIATION", "evidence": "sonnet retrieval improved but composites did not move; higher recall did not predict higher design score - control quality came from methodological competence plus ambient doctrine"},
  "G11_cost": {"verdict": "MEASURED_PARITY", "evidence": "designer tokens model-dominated (~43-108K), no arm penalty; wiki consultation fit the shared 15-op budget"},
  "G12_model_robustness": {"verdict": "CHARACTERIZED", "evidence": "retrieval advantage sonnet-only; haiku could not exploit the wiki AND violated access boundaries in 7/15 control attempts (sonnet 0/12) - deployment-relevant instruction-following asymmetry"},
  "G13_ontology_health": {"verdict": "STABLE_NO_NEW_DATA", "evidence": "s17 HUMAN rulings encoded as registry v2 rows (versioned, non-destructive); no annotation wave required this campaign; rulings tested at next annotation event"},
  "G14_distributed_operation": {"verdict": "DISTRIBUTED_OPERATION_NOT_QUALIFIED", "evidence": "cross-host leg still pending M2/M3/M4 pulling the branch; M1-local parity remains the only live demonstration"},
  "G15_provenance": {"verdict": "PASS", "evidence": "wiki-sourced design interventions cite claim/evidence ids resolvable to packets; spot-checked"},
  "G16_epistemic_separation": {"verdict": "PASS", "evidence": "no campaign artifact entered the canonical store; packs quarantined as derived"},
  "G17_blind_scoring": {"verdict": "PASS", "evidence": "arm-stripped, id-redacted, seeded shuffle; 2 independent scorers; inter-rater exact 0.882 / within-1 0.982; mapping sealed until unblinding"},
  "G18_gap_blind_preservation": {"verdict": "PASS", "evidence": "V1 slate untouched; sealed mapping unread; no slate cell used in task selection"},
  "G19_tensor_honesty": {"verdict": "PASS", "evidence": "tensor untouched; no corpus growth, no new milestone"},
  "G20_memory_advantage": {"verdict": "RETRIEVAL_ADVANTAGE_WITHOUT_DESIGN_ADVANTAGE (MODEL_SPECIFIC)", "evidence": "structured memory recovers more relevant history at sonnet tier (esp. negative evidence and corrections; the Arm C evidence pack is the strongest retrieval condition at 0.90 core / 1.0 corrections) but did not measurably improve design quality against strong controls; on hidden-linkage tasks wiki arms scored slightly worse (exploratory retrieval-noise/anchoring signal)"}
 },
 "leakage_events": "v2/LEAKAGE_AUDIT_V2.md: (1) haiku control access violations -> quarantine + one identical replacement each; T10-haiku cell excluded after second violation; (2) harness auto-memory as ambient shared channel overlapping gold on ~5 tasks - arms unaffected differentially, wiki retrieval delta becomes a lower bound",
 "explicit_verdicts": ["RETRIEVAL_ADVANTAGE_WITHOUT_DESIGN_ADVANTAGE", "MODEL_SPECIFIC_ADVANTAGE_ONLY (retrieval)", "METABOLIZATION_ADVANTAGE_NOT_DEMONSTRATED", "DISTRIBUTED_OPERATION_NOT_QUALIFIED", "TENSOR_NOT_JUSTIFIED (retained)"]
}
json.dump(gates, open(HERE / "benchmarks" / "gates_v2.json", "w"), indent=1)

disc = {"pilot": {"PILOT-1_control_core_recall": 0.0, "PILOT-2_control_core_recall": 1.0,
                  "frozen_sanity_rule": "revise only if BOTH pilots saturate - not triggered"},
        "primary": {"armA_mean_core_recall": 0.474, "band": [0.05, 0.70], "retrieval_side": "PASS",
                    "armA_mean_composite": 3.72, "composite_band_max": 3.4,
                    "design_side": "CEILING_FLAGGED per frozen rule"}}
json.dump(disc, open(HERE / "benchmarks" / "task_discrimination_v2.json", "w"), indent=1)

mr = {"models": {
        "sonnet": {"retrieval_delta_core": 0.300, "retrieval_delta_negative": 0.405,
                   "design_delta": -0.010, "control_boundary_violations": "0/12"},
        "haiku": {"retrieval_delta_core": 0.011, "retrieval_delta_negative": 0.090,
                  "design_delta": -0.022,
                  "control_boundary_violations": "7/15 attempts (5/8 original, 2/7 incl replacements)"}},
      "disclosure": "both models are Anthropic; independent families unavailable without paid APIs (charter s8 disclosure)",
      "interaction": "treatment x model interaction dominates retrieval; design null holds at both tiers"}
json.dump(mr, open(HERE / "benchmarks" / "model_robustness_v2.json", "w"), indent=1)

met = {"D2_adjudication": "evidence-to-changed-decision linkage present at near-ceiling rates in BOTH arms (B: canonical ids; A: repo paths + harness-memory doctrine); differential NOT demonstrated; extracts preserved in v2/arm_outputs sections",
       "reuse_classes_observed": {"SAME_MECHANISM": "common (both arms)",
                                  "CROSS_SUBSTRATE": "T03/T05/T06 (both arms)",
                                  "CROSS_AGENT": "common",
                                  "CROSS_DOMAIN": "T05_B (sigma kill -> program-wide trigger), T03_C (probe floor -> grammar world)"},
       "strongest_wiki_specific_instances": [
         "T05_B_sonnet: OBSTRUCTION_SHAPE cross-family kill (C-ff8811fa0ac7) -> falsifier F2 threshold; NO control arm found this finding (both used a different, real, in-repo signature instead) - the campaign's clearest wiki-only retrieval",
         "T07_B_sonnet: C-e0352ce96e11 -> rank-stratified circularity split",
         "T04_B_sonnet: C-b2cebe551f3b -> null-replication framing"],
       "verdict": "METABOLIZATION_ADVANTAGE_NOT_DEMONSTRATED (phenomenon ubiquitous, differential absent)"}
json.dump(met, open(HERE / "benchmarks" / "metabolization_v2.json", "w"), indent=1)
print("gate artifacts written")
