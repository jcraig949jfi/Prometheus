"""Write the Ananke 72h Atlas export (roles/Atlas/theory schema). usage: python atlas_export.py OUTDIR [C5T_REDUCE.json]"""
import json
import os
import sys

out = sys.argv[1]
c5 = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None


def E(key, rel, w, v):
    return {"entity_type": "experiment", "entity_key": key, "relation": rel, "weight": w, "verbatim": v}


c5_note = ("C5T pending at export time" if c5 is None else
           f"C5T: confirmed {c5['confirmed_total']}/{c5['n']} at 4x, kill {c5['kill']}")

props = [
    {"proposition_id": "P-selector-resolution-erases-graded-function",
     "statement": "With a small per-generation world sample (M8), selection cannot resolve graded partial function (B ~ .6) from noise-fit genomes, so lineages that keep winning lose their function; a larger sample (M32) retains it and sometimes climbs it.",
     "kind": "mechanism", "scope": "PTE register-program GA at the 4 admitted FLIP cells", "confidence": "STRONG",
     "confidence_basis": "C3S: retained 23/24 (S32) vs 8/24 (S8); paired M effect +.55, sign p 1e-7, positive in 4/4 cells; 9 climbs, all causal (teacher_off and zero_comm kill them)",
     "known_confounds": "only stones 1-2 edits from a plant were tested",
     "mechanisms": ["selector_resolution", "graded_partial_function_retention"],
     "untested_predictions": ["the M needed scales with 1/(B-.5)^2", "an archive keyed on partial function substitutes for a larger M"],
     "review_cadence": "THEORY",
     "evidence": [E("ananke.pte/C3S", "SUPPORTS", "HIGH", "M effect (M32 - M8) +.55, sign test p 1.1e-7; retained 23/24 vs 8/24")]},
    {"proposition_id": "P-flip-barrier-not-room",
     "statement": "The two-stage (FLIP) barrier in the flat register-program GA is not lack of program capacity, of a generic persistent register, or of block duplication.",
     "kind": "negative", "scope": "PTE representations R0-R5 at 4 FLIP cells, M32, random starts, up to 4x budget",
     "confidence": "MODERATE",
     "confidence_basis": "C3R: 0/24 in every arm at 1x and 0/24 for R3, R4 at 4x (CP95 .142); no partial-B shift (max +.013 vs a .05 bar)",
     "known_confounds": "one duplication operator at one rate; R1/R2/R5 at 1x only; lower rates not excluded",
     "mechanisms": ["representation_capacity", "persistent_state", "duplication_divergence"],
     "untested_predictions": ["a module binding primitive changes FLIP accessibility where capacity did not"],
     "review_cadence": "THEORY",
     "evidence": [E("ananke.pte/C3R", "SUPPORTS", "HIGH", "MINIMAL_REPRESENTATION_ROUTE_FAILED: R3 0/24, R4 0/24 at 4x")]},
    {"proposition_id": "P-solved-modules-adopted-not-composed",
     "statement": "Solved one-stage modules inserted with uniform register renaming are adopted (present and live in every champion) but do not compose into a two-stage behaviour under selection.",
     "kind": "mechanism", "scope": "PTE C4 (GATE, FLIP; 36 generations; M32; 8-module RELAY1H/HOLD library) and C5T (4x)",
     "confidence": "MODERATE",
     "confidence_basis": "C4-T: arm C 0/56 (0/168 all arms); MODULE_PRESENT 56/56, MODULE_LIVE 55/56; about 18% of module slots unmodified. " + c5_note,
     "known_confounds": "library sub-tasks chosen by the designer, not derived from the target",
     "mechanisms": ["module_reuse", "module_binding"],
     "untested_predictions": ["a target-derived library composes at the designed-halves rate", "typed binding between module ports raises the composition rate"],
     "review_cadence": "THEORY",
     "evidence": [E("ananke.pte/C4-T", "SUPPORTS", "HIGH", "NO_COMPOSITION for GATE and FLIP; arm C module_present 32/32 and 24/24")]},
    {"proposition_id": "P-composition-representable-rarely-searchable",
     "statement": "A two-stage gated relay is representable in the flat register program, and search occasionally assembles it from the correct designed parts, re-wiring them; it did not do so from evolved one-stage parts.",
     "kind": "mechanism", "scope": "PTE C4-D: GATE at 4 cells, R4 + library insertion with the GATE plant's two halves",
     "confidence": "WEAK",
     "confidence_basis": "C4-D 2/32 (2 cells, CP95 .008-.21), both assay-confirmed two-stage; 0/32 with evolved modules on identical seeds",
     "known_confounds": "sparse (2 events); frozen label INCONCLUSIVE_SPARSE",
     "mechanisms": ["module_reuse", "module_binding"],
     "untested_predictions": ["with port binding, the designed halves compose in a majority of searches"],
     "review_cadence": "THEORY",
     "evidence": [E("ananke.pte/C4-D", "SHARPENS", "MEDIUM", "2/32 competent; library -> NOP, zero_comm, context_off and non-readout register zeroing each remove competence")]},
    {"proposition_id": "P-time-crosses-rarity-not-composition",
     "statement": "Extra search time crosses rarity barriers (one-bit relay) but not composition barriers (two-stage tasks).",
     "kind": "distinction", "scope": "PTE C2BX, C2C, C3R, C4, C5T", "confidence": "MODERATE",
     "confidence_basis": "RELAY-mh 7/32 at 4x -> 16/32 at 16x (C2BX); FLIP 0 at every budget tested (C2B B4X 0/32, C3R 0/24 at 4x). " + c5_note,
     "known_confounds": "budgets above 4x untested for the two-stage tasks",
     "mechanisms": ["search_reachability"],
     "untested_predictions": ["the composition rate stays flat in budget while the rarity rate grows with budget"],
     "review_cadence": "STRATEGY",
     "evidence": [E("ananke.pte/C2BX", "SUPPORTS", "HIGH", "pooled 7 -> 10 -> 16 of 32 at 4x/8x/16x; TAIL_CONTINUES")]},
]

prims = [
    {"primitive_id": "search_reachability", "name": "search reachability", "family": "search",
     "definition": "Whether a search procedure finds a competence class that physics permits and the representation can express, measured after P/R/V admission rules out the other causes.",
     "operationalisations": ["P/R/V admission + BASE success rate", "budget scaling 1x/4x/16x", "PSEED retention"],
     "measured_by": "lineage-attributed success rate per search under a frozen ruler", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "mirror_pair_counterfactual_carrier", "name": "mirror-pair counterfactual carrier", "family": "causal_assay",
     "definition": "A state component carries a bit iff swapping it between twin worlds that differ only in that bit's sign flips the downstream output.",
     "operationalisations": ["swap_v2: applied-ness census, competence gate, scored trials, BOOTT intervals"],
     "measured_by": "swap verdict FLIP/PARTIAL/NO_EFFECT/EMPTY_SWAP", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "lineage_reconstruction", "name": "lineage reconstruction", "family": "heredity",
     "definition": "Whether a competent champion descends from a planted or broken start (line-tag share >= .5) rather than arising in the background.",
     "operationalisations": ["per-line provenance tags propagated through crossover and mutation"],
     "measured_by": "share of champion lines tagged from the start genome", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "module_reuse", "name": "module reuse", "family": "composition",
     "definition": "Insertion of frozen, independently solved machinery into a genome, tracked by slot provenance and integrity, with causal use tested by ablating its lines.",
     "operationalisations": ["OPDL library insertion with register renaming", "module_present/live/causal/integrity"],
     "measured_by": "MODULE_CAUSAL k/n", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "graded_partial_function_retention", "name": "graded partial-function retention", "family": "selection",
     "definition": "Whether selection keeps a below-threshold graded function (lineage AND function retained), as distinct from keeping only the lineage.",
     "operationalisations": ["C3S classes A/B/C/D: lineage + function / function erodes / lineage dies / climbs"],
     "measured_by": "best-lineage held B at the end vs the stone", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "channel_state", "name": "channel state", "family": "substrate",
     "definition": "Information held in packets in flight (the communication medium) rather than in a site's registers; located by swapping the in-flight sum.",
     "operationalisations": ["Msum swap", "zero_comm control"],
     "measured_by": "Msum swap verdict; competence under zero_comm", "axis_rules": {}, "detection_status": "NEW_FROM_ANANKE"},
    {"primitive_id": "module_binding", "name": "module port binding", "family": "composition",
     "definition": "An explicit connection from one module's output register to another module's input, as opposed to positional placement plus register renaming. Not implemented in PTE; identified as the missing primitive.",
     "operationalisations": [],
     "measured_by": "(proposed) composition rate of designed halves with vs without binding", "axis_rules": {}, "detection_status": "PROPOSED"},
]

bs = [
    {"blind_spot_id": "BS-library-from-designer-subtasks",
     "assumption": "A library of solved one-stage modules supplies the parts a two-stage target needs.",
     "engines_checked": ["ananke.pte"], "engines_holding": ["ananke.pte"], "counterexamples": [],
     "detection_basis": "C4-T: RELAY1H/HOLD modules adopted and live in 56/56 champions, 0/56 composed; designed target halves composed 2/32 on identical seeds.",
     "anti_experiment": "Build the library from sub-tasks derived from the target's causal graph (context latch on the actuator channel; cue relay) and compare its composition rate with the designer-chosen library and with the designed halves.",
     "proposed_as": None, "status": "OPEN"},
    {"blind_spot_id": "BS-renaming-without-binding",
     "assumption": "Register renaming at insertion is enough for independently evolved modules to interoperate.",
     "engines_checked": ["ananke.pte"], "engines_holding": ["ananke.pte"], "counterexamples": ["theseus (collision-generated k-ary couplings; comms #1953)"],
     "detection_basis": "C4: correct assembly needs compatible permutations across insertions (about 1/9 with 3 registers); no field binds outputs to inputs.",
     "anti_experiment": "Add typed ports or a wiring field and rerun the C4-D designed-halves test.",
     "proposed_as": None, "status": "OPEN"},
    {"blind_spot_id": "BS-small-selector-reads-as-no-gradient",
     "assumption": "If graded function decays under selection, there is no climbable path near the solution.",
     "engines_checked": ["ananke.pte"], "engines_holding": [], "counterexamples": [],
     "detection_basis": "C3S: at M8 the decay was selector noise; at M32 the same stones retained and climbed.",
     "anti_experiment": "Before calling a landscape flat, repeat with 4x the world sample per generation.",
     "proposed_as": None, "status": "RESOLVED_IN_ANANKE"},
]

os.makedirs(out, exist_ok=True)
for n, rows in (("PROPOSITIONS", props), ("PRIMITIVES", prims), ("BLIND_SPOTS", bs)):
    with open(os.path.join(out, n + ".jsonl"), "w", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
print("wrote", len(props), len(prims), len(bs))
