# C4-04 -- addressing damage (static reference resolution; executed mode comparison = REPRESENTATION_BLOCKED)

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

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 13; errors 0
- timings (s): startup_s=0.05, teardown_s=0.04, total_s=1.3
- decisions: D4-008: references = statically reachable control instructions' relative offsets; BROKEN = the new target's 4-word content differs from the old target's; operator index maps are exact copies of the grammar's word moves; LD/ST register addressing is data-dependent and not counted
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / p_loss             sNone    mean    n
    baseline                 0.517   0.517    1
    broken                   0.639   0.639    1
    controls                     -       -    0
    executed_mode_comparis       -       -    0
    intact                   0.552   0.552    1
    no_refs                  0.745   0.745    1

    arm / p_disp             sNone    mean    n
    baseline                     -       -    0
    broken                   0.602   0.602    1
    controls                     -       -    0
    executed_mode_comparis       -       -    0
    intact                   0.445   0.445    1
    no_refs                  0.364   0.364    1

    arm / p_coherent         sNone    mean    n
    baseline                     -       -    0
    broken                   0.172   0.172    1
    controls                     -       -    0
    executed_mode_comparis       -       -    0
    intact                   0.121   0.121    1
    no_refs                  0.099   0.099    1

    arm / n                  sNone    mean    n
    baseline                  2852  2852.000    1
    broken                     588  588.000    1
    controls                    57  57.000    1
    executed_mode_comparis       0   0.000    1
    intact                     802  802.000    1
    no_refs                    624  624.000    1

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.5524, "effect": 0.0871, "min_effect": 0.1, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 1, "treatment_mean": 0.6395}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: a static co-occurrence on one substrate; not a causal attribution and not a comparison of addressing modes

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"addressing": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-04

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
