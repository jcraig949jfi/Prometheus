"""Campaign 6 base: identity, paths, harness. Plan: archaeon/campaign6/PLAN.md."""
from __future__ import annotations

from pathlib import Path

from archaeon.campaign3.c3base import Experiment3, FIELDS_3

C6 = Path(__file__).resolve().parent
CAMPAIGN_SEED = 20260923
CAMPAIGN_6 = {"root": C6, "client": "cmp6-archaeon", "config": C6 / "config.local.json", "ledger_prefix": "L6", "campaign": "cmp6", "seed": CAMPAIGN_SEED}

LANES = ("HUMAN_DIRECTED", "LLM_PROPOSED", "PROCEDURAL", "EVOLUTION_GENERATED", "MIXED")
PRESSURE_KINDS = ("EXOGENOUS_PRESSURE", "ENDOGENOUS_PRESSURE")
TIERS = ("T0", "T1", "T2", "T3")
DETECTORS = ("behavioral_novelty", "lineage_discontinuity", "unexpected_transfer", "structural_reuse", "environmental_modification",
             "niche_divergence", "regime_persistence", "unexplained_gain", "unexpected_causal_dependence", "detector_disagreement", "classifier_failure")
DETECTOR_OUTCOMES = ("FIRE", "QUIET", "UNABLE")
REPLAYS = ("A_exact", "B_lineage", "C_world_seed", "D_mutation_rollback", "E_mechanism_ablation", "F_heldout_transfer", "G_pressure_perturbation")
UNKNOWN = "UNKNOWN_MECHANISM"


def harness():
    class Experiment6(Experiment3):
        CAMPAIGN = CAMPAIGN_6
        FIELDS = FIELDS_3
    return Experiment6
