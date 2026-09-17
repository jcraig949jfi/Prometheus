# C2-SFE-03 -- falsify SFE-01's component effect (n=12, battery)

## A. STARTUP (preregistration; sealed sha256:3430e2d56734bea90c16b6fa3fcecc5389d61db5b00fff38abf75e31d9771159)

- experiment ID: C2-SFE-03
- parents: SFE-01
- QUESTION: Does seeding a W2_K2 4-bit search's generation 0 with component segments of an above-floor W1_d1 source population raise held-out competence over random segments (SFE-01, 2/3 vs 0/3 at n=3), and does the effect survive cheaper explanations (composition without order; opcodes without operands; any nonrandom same-distribution material)?
- PARENT EVIDENCE: SFE-01 attempt 2: components 2/3 footholds vs random-segment 0/3, neither 1/3, failure-tabu null; source elites 0.06-0.125 (immature, L-010). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.
- ASSAY CAPABILITY REQUIREMENT: baseline reaches >= 1 foothold in 3 seeds (else TARGET_UNREACHABLE); every seeded arm's material set non-empty
- POSITIVE CONTROL: baseline (own generation 0): expected 0.41 per seed; P(0 of 3) = 0.2035
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W1_d1": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.5615], "budgets": [[200, 60, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 3}}, "W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.156, 0.5087], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3043, "k": 7, "n": 23}}}
- ARMS:
    - baseline
    - components
    - random_segments
    - shuffled
    - opcode_matched
    - self_segments
    - position_front
    - other_lineage
    - mature_source
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 (gen0) for every arm; the splice position/choice stream keyed on the seed only, so arms differ in material, not in where it goes (position_front excepted by design)
- BUDGET:
    {"E": 4, "G": 6, "G_source": 8, "N": 24, "heldout_episodes": 48, "margin": 0.1, "seeds": [1, 2, 3]}
- PRIMARY OBSERVABLE: competence_heldout of the elite (48 held-out episodes) per arm x seed; primary comparison components vs random_segments
- CLAIM CEILING: SUPPORTED_POSITIVE only if components - random_segments >= 0.10 AND every kill attack (shuffled, opcode_matched, self_segments) survives by the same margin at n=3; otherwise WEAK_POSITIVE or CAPABLE_NEGATIVE
- FALSIFICATION CONDITION: components - random_segments < 0.10 => the SFE-01 effect does not replicate (CAPABLE_NEGATIVE); any kill arm within 0.10 of components => that cheaper explanation suffices
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (baseline 0/3)
    - UNDERPOWERED
    - IMMATURE_ARTIFACT recorded on immature sources (telemetry; the SFE-01 condition IS an immature source, so it does not gate)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - material summaries (k histogram, opcode category shares) per set
    - gen0 instruction-length mean per arm (length control)
    - source maturity per set
    - first_solved_gen per row
    - elite origins
    - reachability rows
- MACHINE CHANGES EXERCISED:
    - B (battery in decl + meas)
    - C (common_fill with N substitutions)
    - E (maturity on every population artifact)
    - G (mature sources run by the step API with a stop rule)
    - H
    - I
- decl (machine-read by archaeon.wse.states): {"artifact_policy": "maturity recorded on every material set; IMMATURE does not gate (the parent's condition is an immature source, D2-011)", "battery": [{"name": "shuffled", "rule": "components - shuffled >= 0.10 mean held-out", "type": "kill"}, {"name": "opcode_matched", "rule": "components - opcode_matched >= 0.10 mean held-out", "type": "kill"}, {"name": "self_segments", "rule": "components - self_segments >= 0.10 mean held-out", "type": "kill"}], "n_min": 3, "primary": {"control": "random_segments", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "components"}, "probes": ["position_front", "other_lineage", "mature_source"], "target": {"baseline_arm": "baseline", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): exchange_s=0.0, records_s=0.0, sources_s=0.16, targets_s=0.21, total_s=0.6
- decisions: D2-011: IMMATURE_ARTIFACT is telemetry here, not a gate: the SFE-01 effect under test was produced by an immature source; the mature_source probe measures whether maturity changes it
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3    mean    n
    baseline                 0.073   0.083   0.031   0.062    3
    random_segments          0.062   0.250   0.042   0.118    3
    self_segments            0.073   0.083   0.042   0.066    3

    arm / train_last            s1      s2      s3    mean    n
    baseline                 0.000   0.000   0.125   0.042    3
    random_segments          0.000   0.125   0.125   0.083    3
    self_segments            0.000   0.000   0.125   0.042    3

- footholds:
    arm                    footholds  first_solved_gen per row
    baseline               0/3        -,-,-
    random_segments        1/3        -,2,-
    self_segments          0/3        -,-,-

- typed states fired: ['TARGET_UNREACHABLE']
    TARGET_UNREACHABLE  {"band95_upper": 0.5615, "baseline_arm": "baseline", "reached": 0, "rows": 3, "table_class": "UNESTABLISHED"}
- disposition candidate (machine): TARGET_UNREACHABLE -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: SUPPORTED_POSITIVE only if components - random_segments >= 0.10 AND every kill attack (shuffled, opcode_matched, self_segments) survives by the same margin at n=3; otherwise WEAK_POSITIVE or CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-03

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: TARGET_UNREACHABLE (machine candidate TARGET_UNREACHABLE). 
