## A. STARTUP (preregistration; sealed sha256:1e9c2bd08cda83c7ff6411305115bf8ae3ce411cd1c60c7cec81ffcc4480a461)

- experiment ID: C4-04
- parents: C4-01, C4-03
- QUESTION: How much brittleness under insertion, deletion and displacement co-occurs with a broken reference (a statically reachable relative jump that lands on a different instruction after the edit)? The executed comparison of addressing modes is REPRESENTATION_BLOCKED.
- PARENT EVIDENCE: C4-01: length-changing operators lose .58-.70 vs .32-.38 for word-level edits; C4-03: the modulo decode is the instruction set; the ISA's one static reference kind is the relative jump.
- WHY THIS SLOT IS STILL WORTH SPENDING: Separates loss that comes from references dying from loss that comes from what the edited instructions do; a lost P1 is as informative as a held one.
- ASSAY CAPABILITY REQUIREMENT: positive: a constructed JMP parent reads broken under an insertion inside its span and intact outside; negative: identity child n_broken 0 on 57/57; integrity: regenerated digests equal committed; cheat: D7 broken row counts coherent
- POSITIVE CONTROL: controls arm: positive_break_detected and positive_keep_intact and negative 57/57
- REACHABILITY ESTIMATE:
    {"note": "static analysis over committed rows; no search"}
- ARMS:
    - broken
    - intact
    - no_refs
    - baseline
    - controls
    - executed_mode_comparison
- COMMON-RANDOM-NUMBERS POLICY: no evaluation; children regenerated from the C4-01 seeds
- BUDGET:
    {"baseline_operators": ["replacement", "operand_perturbation", "reference_redirection", "region_swap", "randomization", "unreachable_removal", "config_perturbation"], "c401_children": 5472, "length_changing_operators": ["insertion", "deletion", "duplication", "movement", "splice"]}
- PRIMARY OBSERVABLE: per operator and pooled over length-changing edits: P(broken or removed | refs), P(loss | broken) vs P(loss | intact) vs P(loss | no refs), same for displacement > 0 and coherent share, Wilson bands; P1 and P2 as stated
- CLAIM CEILING: a static co-occurrence on one substrate; not a causal attribution and not a comparison of addressing modes
- FALSIFICATION CONDITION: P1 lost (difference < 0.10): brittleness is not carried by the references
- KILL CONDITION: control or integrity failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - REPRESENTATION_BLOCKED (executed mode comparison)
- EXPECTED MACHINE TELEMETRY:
    - reference facts per child
    - tables by operator/stratum
    - predictions P1/P2
- MACHINE CHANGES EXERCISED:
    - exact operator index maps
    - static jump-target resolution
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 4)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1}, "primary": {"control": "intact", "metric": "p_loss", "min_effect": 0.1, "treatment": "broken"}}
