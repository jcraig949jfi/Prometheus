## A. STARTUP (preregistration; sealed sha256:3dc2a098e06e22c060b68b05355cca5a4b5edf64dec79240df23fabc99458556)

- experiment ID: C4-06
- parents: C4-05, C3-SFE-01
- QUESTION: Can separately accumulated neutral changes (the depth-16 C4-05 walkers) combine into a capability ordinary one-step search rarely reaches (a W2_K2 held-out summit >= 0.90)? Does the existing recombination machinery turn latent structure into useful computation or multiply damage?
- PARENT EVIDENCE: C4-05: 188/188 walkers reach depth 16 inside the band, structural diversity .76, held-out exaptation .043; C3-SFE-01: 0/24 confirmed W2_K2 summits; shelf COMMON.
- WHY THIS SLOT IS STILL WORTH SPENDING: The one C4 slot that tests whether accumulated neutral structure is a stepping stone or dead weight; the C3 valley question with new geometry.
- ASSAY CAPABILITY REQUIREMENT: starting population's best W2_K2 held-out < 0.90 (measured 0.53125); mutation_only reaches the shelf in >= 3 of 6 seeds; walker digests equal C4-05's (188/188); determinism (self-test); crossing detector reads the field (cheat)
- POSITIVE CONTROL: mutation_only arm: shelf_reached >= 1 on >= 3 of 6 seeds
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.4329, 0.8188], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_shelf_gens": [13, 19, 24, 27, 27, 33, 33, 49, 65, 84, 84, 99, 99], "first_solved_gens": [13, 19, 27, 27, 35, 49, 65, 84, 84, 95, 95, 99, 99], "first_summit_gens": [], "freq": 0.65, "freq_shelf": 0.65, "freq_summit": 0.0, "k": 13, "k_shelf": 13, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 7, "SHELF": 13, "SUMMIT": 0}, "n": 20, "n_censored_runs": 2, "shelf_hist": {"0.2": 5, "0.4": 2, "0.5": 11, "0.6": 1, "0.8": 1}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16], [200, 100, 16], [200, 300, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.4912, "k": 28, "k_summit": 0, "k_summit_any": 0, "n": 57}}}
- ARMS:
    - mutation_only
    - recombination
- COMMON-RANDOM-NUMBERS POLICY: identical cell seeds, identical init_pop (the walkers), identical evolver rng stream; the arms differ only in the mate passed to descend()
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "floor": 0.1875, "heldout_episodes": 48, "probe_every": 10, "seeds": [1, 2, 3, 4, 5, 6], "shelf_min": 0.45, "summit_min": 0.9, "walkers": 188}
- PRIMARY OBSERVABLE: crossings per arm (held-out >= 0.90 at a probe) and first_crossing_gen; viable share and mean reward by birth kind (mutation / mated_splice / mated_no_splice); structural novelty per generation; distinct held-out elite behaviours; traces
- CLAIM CEILING: at n=6 per arm: a count of crossings and a birth-kind damage table on one substrate; no mechanism
- FALSIFICATION CONDITION: P1 lost: crossings(recombination) - crossings(mutation_only) < 2 => recombination does not cross more at this budget; INCONCLUSIVE if neither arm crosses and the shelf control holds
- KILL CONDITION: starting population already crosses (negative control) or shelf control fails -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - per-arm per-seed traces and probes
    - birth-kind table
    - structural novelty by generation
    - crossing manifests
- MACHINE CHANGES EXERCISED:
    - descend_fn override (mate=None)
    - walker regeneration + digest verification
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 6)
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "mutation_only", "metric": "shelf_reached", "min": 1, "min_rows": 3}, "primary": {"control": "mutation_only", "metric": "crossing", "min_effect": 0.3333333333333333, "treatment": "recombination"}, "target": {"baseline_arm": "*", "reach_metric": "crossing", "reach_min": 1, "reachability_class": "OBSERVED_UNREACHABLE_AT_BUDGET"}}
