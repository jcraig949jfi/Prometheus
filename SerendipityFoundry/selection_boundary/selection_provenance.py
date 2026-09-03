"""SELECTION_PROVENANCE graph for stackvm-v1 (mission section 2, 11).

Every edge reads:

    artifact/property  <- selected_by  MECHANISM  <- parameterized_by  SOURCE

For each mechanism the audit records, per mission section 2:
  A active in the era?   B reconstructible exactly?   C deterministic given
  preserved inputs?      D unavailable external randomness?
  E human discretion?    F changed during the era?    G tuned on this corpus?
  H load-bearing for why the artifact became notable?

PROVENANCE CLASSES for every choice on a null path (mission section 11):
  HISTORICALLY_FIXED, PROTOCOL_FIXED, BEACON_SELECTED_FROM_COMMITTED_MENU,
  EXTERNAL_RANDOMNESS, CORPUS_SELECTED, UNDECLARED.
CORPUS_SELECTED and UNDECLARED are illegal on any null path unless the formal
test conditions on that choice and still proves level.

ALL FACTS BELOW ARE PROCEDURAL, read read-only from the ledger's own
configuration records (seeds, config hashes, rule names, source_tree_hash).
NO OUTCOME DISTRIBUTION IS USED. Mission section 21 permits reconstructing
FACTS ABOUT THE PROCEDURE and forbids fitting reference densities, thresholds,
neighbourhoods, support boundaries or null tails from the same corpus.
"""
from __future__ import annotations

import json

HISTORICALLY_FIXED = "HISTORICALLY_FIXED"
PROTOCOL_FIXED = "PROTOCOL_FIXED"
BEACON_MENU = "BEACON_SELECTED_FROM_COMMITTED_MENU"
EXTERNAL_RANDOMNESS = "EXTERNAL_RANDOMNESS"
CORPUS_SELECTED = "CORPUS_SELECTED"
UNDECLARED = "UNDECLARED"

ILLEGAL_ON_NULL_PATH = {CORPUS_SELECTED, UNDECLARED}

# ---------------------------------------------------------------------------
# The selection channels, innermost (machine) to outermost (analyst).
# `evidence` cites the ledger field that establishes the procedural fact.
# ---------------------------------------------------------------------------
CHANNELS = [
    # ---- LAYER M: the machine pipeline -------------------------------------
    {"id": "M1_generator", "layer": "MACHINE",
     "mechanism": "create_random / mutate / recombine under a declared operator config",
     "evidence": "EXPERIMENT_STARTED.effective_operator_config + operator_config_hash (11 distinct); ARTIFACT_* payload carries op and seed",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": "config varied across experiments but each is hashed and recorded",
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": HISTORICALLY_FIXED},

    {"id": "M2_population_schedule", "layer": "MACHINE",
     "mechanism": "driver world_objective_v1 with a per-experiment evaluation budget",
     "evidence": "EXPERIMENT_STARTED.driver (261/261 = world_objective_v1), .budget, .seed (27 distinct seeds)",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": False,
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": HISTORICALLY_FIXED},

    {"id": "M3_survivor_selection", "layer": "MACHINE",
     "mechanism": "objective_ga selection: tournament (80) or elite_truncation (7), tie-break seeded_uniform",
     "evidence": "SELECTION.{driver,operator,tie_break_policy,tie_break_key,root_seed,candidate_pool_hash,candidate_ids,rejected_ids,n_candidates,n_tied}",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": "two operators, both recorded per event",
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": HISTORICALLY_FIXED,
     "note": "85 of 87 selection events were FULLY TIED, so this channel acted as a seeded random draw. That is a PROCEDURAL fact about the mechanism, recorded in the event itself; a replay must reproduce the drift, not an idealized selection."},

    {"id": "M4_archive", "layer": "MACHINE",
     "mechanism": "MAP-Elites style grid archive: insert / reject / evict",
     "evidence": "ARCHIVE_INSERT.{archive_id=simple_grid, cell, descriptor, fitness, novelty, detail}; ARCHIVE_REJECT.detail single value 'not_better'; ARCHIVE_EVICT",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": False,
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": HISTORICALLY_FIXED,
     "note": "single archive id and a single deterministic rejection reason -- an unusually clean retention rule"},

    {"id": "M5_run_nomination", "layer": "MACHINE",
     "mechanism": "BEST-OF-RUN: each experiment emits best_artifact_id",
     "evidence": "EXPERIMENT_FINISHED.{best_artifact_id,best_fitness,evaluations_used,heldout_exact_final,solved,terrain_id,operator_config_hash}",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": False,
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": HISTORICALLY_FIXED,
     "note": "THIS IS AN EXPLICIT, FROZEN, DETERMINISTIC NOMINATION FUNCTION AT RUN LEVEL. It is a max-of-N operator and it is recorded. It is what makes a run-level selection-replicating null possible at all."},

    {"id": "M6_task_filter", "layer": "MACHINE",
     "mechanism": "terrain / battery definition gating what counts as success",
     "evidence": "EXPERIMENT_STARTED.terrain{world_id,horizon,oracle_kind,battery,train_battery_hash,heldout_battery_hash}; terrain_id (5 distinct)",
     "A_active": True, "B_reconstructible": True, "C_deterministic": True,
     "D_missing_randomness": False, "E_human": False, "F_changed": "5 terrains",
     "G_tuned_on_corpus": False, "H_load_bearing": True,
     "class": CORPUS_SELECTED,
     "note": "The terrain/battery is reconstructible AS A PROCEDURE, but as a SCIENTIFIC REFERENCE it is corpus-material: the task family was authored for this program. It may be replayed; it may not be used as a canonical context family for a corpus-independent null."},

    # ---- LAYER H: the human / analyst pipeline ------------------------------
    {"id": "H1_era_restart", "layer": "HUMAN",
     "mechanism": "two driver eras (objective_ga then map_elites); which runs were launched at all",
     "evidence": "SELECTION.driver vs SUCCESS.driver; no ledger record states WHY the second era began",
     "A_active": True, "B_reconstructible": False, "C_deterministic": False,
     "D_missing_randomness": False, "E_human": True, "F_changed": True,
     "G_tuned_on_corpus": True, "H_load_bearing": True,
     "class": UNDECLARED,
     "note": "The decision to start a second era after observing the first is a human selection event with no recorded rule."},

    {"id": "H2_archaeological_mining", "layer": "HUMAN",
     "mechanism": "adaptive post-hoc mining of the ledger by a model-driven analyst; each query chosen after seeing the previous result",
     "evidence": "the archaeology packet's own reproducibility section, which states the effective number of hypotheses IS NOT ESTIMABLE and enumerates researcher degrees of freedom (band boundaries chosen after seeing the distribution, thresholds chosen post hoc, choice of which subtrees to examine)",
     "A_active": True, "B_reconstructible": False, "C_deterministic": False,
     "D_missing_randomness": True, "E_human": True, "F_changed": True,
     "G_tuned_on_corpus": True, "H_load_bearing": True,
     "class": UNDECLARED,
     "note": "THIS IS THE DECISIVE CHANNEL. The five frozen candidates became candidates HERE, not at M5. It is not a function of preserved inputs: it is an adaptive interactive search whose branch points depended on intermediate results that were never logged as a rule."},

    {"id": "H3_claim_wording", "layer": "HUMAN",
     "mechanism": "the phenomenon description attached to each nominated artifact",
     "evidence": "frozen candidate dossiers WOW-C-001..005",
     "A_active": True, "B_reconstructible": False, "C_deterministic": False,
     "D_missing_randomness": False, "E_human": True, "F_changed": True,
     "G_tuned_on_corpus": True, "H_load_bearing": True,
     "class": UNDECLARED},

    # ---- LAYER S: specification selection -----------------------------------
    {"id": "S1_spec_menu", "layer": "SPEC",
     "mechanism": "choice of observable / sampler / tail / arity / step budget / context family",
     "evidence": "prior review measured a menu of J ~ 1e2-1e3 and showed max-selection inflates the level to J/K",
     "A_active": True, "B_reconstructible": True, "C_deterministic": False,
     "D_missing_randomness": False, "E_human": True, "F_changed": True,
     "G_tuned_on_corpus": True, "H_load_bearing": True,
     "class": CORPUS_SELECTED,
     "note": "Repairable in principle: BEACON_SELECTED_FROM_COMMITTED_MENU, provided every member is individually valid AND the scientific claim is invariant across members."},
]


def graph():
    edges = []
    for c in CHANNELS:
        edges.append({
            "property": "candidate_eligibility",
            "selected_by": c["id"],
            "mechanism": c["mechanism"],
            "parameterized_by": c["evidence"],
            "provenance_class": c["class"],
            "layer": c["layer"],
            "load_bearing": c["H_load_bearing"],
            "legal_on_null_path": c["class"] not in ILLEGAL_ON_NULL_PATH,
        })
    return edges


def audit():
    illegal = [c for c in CHANNELS
               if c["class"] in ILLEGAL_ON_NULL_PATH and c["H_load_bearing"]]
    nonreplayable = [c for c in CHANNELS
                     if c["H_load_bearing"] and not c["B_reconstructible"]]
    return {
        "n_channels": len(CHANNELS),
        "load_bearing": sum(1 for c in CHANNELS if c["H_load_bearing"]),
        "illegal_on_null_path_and_load_bearing": [c["id"] for c in illegal],
        "load_bearing_and_NOT_reconstructible": [c["id"] for c in nonreplayable],
        "machine_layer_all_reconstructible":
            all(c["B_reconstructible"] for c in CHANNELS
                if c["layer"] == "MACHINE"),
    }


if __name__ == "__main__":
    a = audit()
    print("=" * 76)
    print("STACKVM-V1 SELECTION PROVENANCE AUDIT")
    print("=" * 76)
    for c in CHANNELS:
        flag = "  " if c["B_reconstructible"] else "!!"
        print("%s %-26s %-8s %-34s recon=%-5s human=%-5s class=%s"
              % (flag, c["id"], c["layer"], c["mechanism"][:34],
                 c["B_reconstructible"], c["E_human"], c["class"]))
    print()
    print("channels: %d  load-bearing: %d" % (a["n_channels"], a["load_bearing"]))
    print("MACHINE layer fully reconstructible: %s"
          % a["machine_layer_all_reconstructible"])
    print("LOAD-BEARING BUT NOT RECONSTRUCTIBLE: %s"
          % a["load_bearing_and_NOT_reconstructible"])
    print("ILLEGAL ON NULL PATH AND LOAD-BEARING: %s"
          % a["illegal_on_null_path_and_load_bearing"])
    print(json.dumps({"edges": graph(), "audit": a}, indent=1)[:0])
