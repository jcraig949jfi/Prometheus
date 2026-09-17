# C2-SFE-03 -- falsify SFE-01's component effect (n=12, battery)

## A. STARTUP (preregistration; sealed sha256:b8c6f2fd0a97da9e26d1c965ce795b32a6f29717581ad08f918f3756f1948ec3)

- experiment ID: C2-SFE-03
- parents: SFE-01
- QUESTION: Does seeding a W2_K2 4-bit search's generation 0 with component segments of an above-floor W1_d1 source population raise held-out competence over random segments (SFE-01, 2/3 vs 0/3 at n=3), and does the effect survive cheaper explanations (composition without order; opcodes without operands; any nonrandom same-distribution material)?
- PARENT EVIDENCE: SFE-01 attempt 2: components 2/3 footholds vs random-segment 0/3, neither 1/3, failure-tabu null; source elites 0.06-0.125 (immature, L-010). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.
- ASSAY CAPABILITY REQUIREMENT: baseline reaches >= 1 foothold in 12 seeds (else TARGET_UNREACHABLE); every seeded arm's material set non-empty
- POSITIVE CONTROL: baseline (own generation 0): expected 0.41 per seed; P(0 of 12) = 0.0017
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W1_d1": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.5615], "budgets": [[200, 60, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 3}}, "W2_K2": {"at_budget": {"band95": [0.2161, 0.6399], "class": "REACHABLE", "first_solved_gens": [35, 39, 48, 49, 50, 54, 59], "freq": 0.4118, "k": 7, "n": 17}, "at_budget_any_foundry": {"band95": [0.2161, 0.6399], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.4118, "k": 7, "n": 17}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.156, 0.5087], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3043, "k": 7, "n": 23}}}
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
    {"E": 16, "G": 60, "G_source": 100, "N": 200, "heldout_episodes": 48, "margin": 0.1, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
- PRIMARY OBSERVABLE: competence_heldout of the elite (48 held-out episodes) per arm x seed; primary comparison components vs random_segments
- CLAIM CEILING: SUPPORTED_POSITIVE only if components - random_segments >= 0.10 AND every kill attack (shuffled, opcode_matched, self_segments) survives by the same margin at n=12; otherwise WEAK_POSITIVE or CAPABLE_NEGATIVE
- FALSIFICATION CONDITION: components - random_segments < 0.10 => the SFE-01 effect does not replicate (CAPABLE_NEGATIVE); any kill arm within 0.10 of components => that cheaper explanation suffices
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (baseline 0/12)
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
- decl (machine-read by archaeon.wse.states): {"artifact_policy": "maturity recorded on every material set; IMMATURE does not gate (the parent's condition is an immature source, D2-011)", "battery": [{"name": "shuffled", "rule": "components - shuffled >= 0.10 mean held-out", "type": "kill"}, {"name": "opcode_matched", "rule": "components - opcode_matched >= 0.10 mean held-out", "type": "kill"}, {"name": "self_segments", "rule": "components - self_segments >= 0.10 mean held-out", "type": "kill"}], "n_min": 12, "primary": {"control": "random_segments", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "components"}, "probes": ["position_front", "other_lineage", "mature_source"], "target": {"baseline_arm": "baseline", "reach_metric": "reached", "reach_min": 1, "reachability_class": "REACHABLE"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 3; artifacts 26; imports 25; records 108; errors 0
- import hash checks: 25/25 ok
- timings (s): exchange_s=7.66, records_s=28.86, sources_s=82.96, startup_s=0.21, targets_s=369.62, teardown_s=0.56, total_s=491.3
- decisions: D2-011: IMMATURE_ARTIFACT is telemetry here, not a gate: the SFE-01 effect under test was produced by an immature source; the mature_source probe measures whether maturity changes it
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    baseline                 0.323   0.292   0.562   0.510   0.292   0.344   0.104   0.333   0.542   0.271   0.531   0.531   0.386   12
    components               0.552   0.531   0.094   0.510   0.250   0.031   0.531   0.052   0.010   0.531   0.302   0.531   0.327   12
    mature_source            0.552   0.542   0.531   0.500   0.646   0.510   0.542   0.521   0.323   0.531   0.406   0.312   0.493   12
    opcode_matched           0.552   0.531   0.531   0.208   0.083   0.229   0.542   0.031   0.031   0.042   0.042   0.438   0.272   12
    other_lineage            0.094   0.062   0.094   0.510   0.531   0.510   0.240   0.531   0.542   0.531   0.531   0.531   0.392   12
    position_front           0.062   0.292   0.510   0.510   0.042   0.510   0.542   0.521   0.531   0.531   0.531   0.292   0.406   12
    random_segments          0.552   0.531   0.604   0.042   0.250   0.510   0.312   0.031   0.323   0.531   0.052   0.083   0.319   12
    self_segments            0.552   0.531   0.531   0.208   0.375   0.510   0.104   0.031   0.031   0.271   0.042   0.531   0.310   12
    shuffled                 0.094   0.062   0.542   0.208   0.531   0.031   0.104   0.312   0.562   0.531   0.531   0.083   0.299   12

    arm / train_last            s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    baseline                 0.188   0.188   0.469   0.531   0.344   0.344   0.188   0.250   0.531   0.281   0.562   0.562   0.370   12
    components               0.531   0.500   0.094   0.531   0.344   0.125   0.500   0.125   0.125   0.531   0.188   0.562   0.346   12
    mature_source            0.531   0.625   0.500   0.531   0.500   0.531   0.500   0.562   0.219   0.531   0.406   0.281   0.477   12
    opcode_matched           0.531   0.500   0.500   0.406   0.156   0.156   0.500   0.125   0.062   0.062   0.156   0.562   0.310   12
    other_lineage            0.094   0.125   0.094   0.531   0.531   0.531   0.312   0.500   0.531   0.531   0.625   0.562   0.414   12
    position_front           0.062   0.188   0.500   0.531   0.156   0.531   0.500   0.562   0.531   0.531   0.562   0.281   0.411   12
    random_segments          0.531   0.500   0.375   0.125   0.312   0.531   0.312   0.125   0.219   0.531   0.062   0.125   0.312   12
    self_segments            0.531   0.500   0.500   0.406   0.438   0.531   0.188   0.125   0.062   0.281   0.156   0.562   0.357   12
    shuffled                 0.094   0.125   0.469   0.406   0.531   0.125   0.188   0.250   0.531   0.531   0.562   0.125   0.328   12

- footholds:
    arm                    footholds  first_solved_gen per row
    baseline               6/12       -,-,35,-,-,49,-,39,32,-,13,19
    components             6/12       24,-,-,49,-,-,48,-,44,15,-,26
    mature_source          11/12      30,25,35,14,21,-,5,30,57,47,14,58
    opcode_matched         5/12       36,-,-,7,-,-,-,-,51,55,24,-
    other_lineage          8/12       -,37,59,-,26,31,24,33,39,-,-,31
    position_front         8/12       -,-,39,18,5,33,11,23,-,-,15,24
    random_segments        5/12       47,-,13,-,-,-,46,-,-,43,31,-
    self_segments          6/12       54,33,34,-,-,-,-,-,36,52,35,-
    shuffled               5/12       -,11,-,-,-,27,7,49,-,-,30,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.3186, "effect": 0.0087, "min_effect": 0.1, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 5, "treatment_mean": 0.3273}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: SUPPORTED_POSITIVE only if components - random_segments >= 0.10 AND every kill attack (shuffled, opcode_matched, self_segments) survives by the same margin at n=12; otherwise WEAK_POSITIVE or CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

The SFE-01 component claim did not survive n=12. Assay capable: baseline 6/12 footholds (first solved 13-49), consistent with the table's 7/17. PRIMARY: components - random_segments = +0.009 held-out (paired wins 5/12), footholds 6/12 vs 5/12; the machine candidate CAPABLE_NEGATIVE is accepted. The kill battery was therefore moot but is reported: shuffled 5/12 (components - shuffled = +0.03), opcode_matched 5/12 (+0.06), self_segments 6/12 (+0.02): composition without order, opcodes without operands, and the target's own generation-0 material all do what the components do, which is nothing distinguishable from random segments. Every inserted arm sits at or below baseline (0.27-0.33 vs 0.39): inserting 2-4 instructions into every generation-0 organism (gen-0 mean length 6.4 -> 8.9 instructions) costs a little at this budget, which is the genome-length effect the battery controlled by inserting the same lengths everywhere. Probes (preregistered as probes, not scored): position_front 8/12 (0.41), other_lineage 8/12 (0.39): a component's lineage identity and its insertion position do not matter. mature_source 11/12 (0.49): components cut from W0 4-bit sources that SOLVED their own cell (10/12 solved by generation 31, one at 99) seed footholds in 11 of 12 seeds. EXPLORATORY reading of the mature probe, with the cheaper explanation stated first: 8 of the 11 mature-source footholds end at held-out 0.50-0.55 and only one exceeds 0.60; a W0 solver answers ONE of W2_K2's two streams for exactly half credit, so the mature material transports a direct sub-solution, and the 0.5 foothold criterion counts it. That is direct reuse of a solved neighbour (the SFE-10 producer finding again), not evidence that 'maturity' improves search material in general. Must NOT be claimed: that components help (they do not, at n=12); that mature components make W2_K2 SOLVABLE (no arm's elite exceeded 0.65 held-out; the full two-stream solution was not reached by anyone in 108 runs).

## D. TEARDOWN (generated)

- worlds: {"source-immature": "TERMINATED", "source-mature": "TERMINATED", "target": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-03

Zero engine errors; 3 worlds; 25 artifacts (12 component sets with maturity, 12 random sets, 1 mature pool) all imported and hash-verified; 108 records; 132 reachability rows appended. The battery outcomes were computed by the harness from rows and consumed by the machine (meas.battery). Findings for the ledger: (1) the foothold criterion 'training best >= 0.5' on a K=2 cell is satisfied by a ONE-STREAM solution (half credit); every foothold in this experiment, baseline included, sits on the 0.5-0.56 shelf, so 'reached' on W2_K2 means 'reached the half-credit shelf', and the reachability table's classes inherit that meaning -- the row's best_train_max already exposes it, and a per-cell solve threshold (1 - eval_resolution for a FULL solve) is a policy the table should carry (KEEP_POLICY + LANDSCAPE); (2) the mature W0 sources were run with a stop rule (three generations past the first solver) and are recorded as 'treated' rows for reachability, which loses ten valid 'W0 4-bit reached by generation g' measurements -- the table should accept a stopped run as a baseline reach at its stop generation (TO_MACHINERY); (3) W1_d1 4-bit reached 3/12 at G100 (40, 77, 31): a new budget row that campaign 1 never measured.

## F. LANDSCAPE / GRADIENT NOTES

W2_K2 4-bit N200 G60 E16 has a HALF-CREDIT SHELF at 0.5: 47 of 108 runs ended their training best on 0.50-0.56 and none above 0.65; the plateau exit campaign 1 called 'narrow' leads to the one-stream solution, and the second stream was never solved at this budget by any arm, seeded or not. W0 4-bit N200: 10/12 sources solved (first solved 0, 12, 16, 17, 18, 19, 20, 27, 31, 99): COMMON by generation ~35. W1_d1 4-bit N200 G100 E16: 3/12 baseline (31, 40, 77). Seeding with a solved W0 organism's segments lands on the W2_K2 half-credit shelf in 11/12 seeds within 5-58 generations: the W0 -> W2_K2 gradient of SFE-10 is a gradient to the shelf, not to the summit.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). SFE-01's component effect does not replicate at n=12 (components - random_segments = +0.009; 6/12 vs 5/12; baseline 6/12); the campaign-1 weak positive is retired. The mature-source probe (11/12) is exploratory and has a cheaper explanation (transported W0 sub-solution = half credit on a K=2 cell).
