# C2-SFE-05 -- retention replay with a proven-capable stream

## A. STARTUP (preregistration; sealed sha256:fef4d022f6e2797ec95f397450a748636f1311cc4a09c73b58c4f67d24737211)

- experiment ID: C2-SFE-05
- parents: SFE-02
- QUESTION: Gate: does a stream of every organism a W2_K2 4-bit search evaluates (run 5 generations past its first solver) contain an organism scoring >= 0.5 on at least one SEALED future query cell (W0, W1_d1, W1_d4, W1_d16, W3_K2)? Science (capable seeds only): do the four retention policies under one cap (8 items) differ in prospective solve fraction on the sealed queries?
- PARENT EVIDENCE: SFE-02: streams of 1024 and 4096 W1_d1 organisms held nothing above threshold (twice INCONCLUSIVE). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE; W0 4-bit COMMON by ~G35; sub-solutions of W2_K2 solvers score 0.5 on W0-like cells (C2-SFE-03/04).
- ASSAY CAPABILITY REQUIREMENT: per seed: max over the stream's top-64 (by source score) of held-out reward on any sealed query >= 0.50, checked BEFORE freezing archives; experiment: >= 3 capable seeds (else UNDERPOWERED); no capable seed => STREAM_BELOW_THRESHOLD
- POSITIVE CONTROL: the stream's own top-64 organisms on the sealed queries (the uncapped ceiling); the threshold 0.50 is sealed here and never changed
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.2153, 0.5577], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3704, "k": 10, "n": 27}}}
- ARMS:
    - top_k
    - uniform
    - behavioral
    - hybrid
- COMMON-RANDOM-NUMBERS POLICY: one stream per seed shared by every policy (policy-independent by construction); policies are deterministic given the stream and the seed
- BUDGET:
    {"E": 4, "G_cap": 6, "N": 24, "caps": {"bytes": 2400, "items": 8}, "edges": [[0.5, 1.5, 2.5], [4.5, 5.5, 6.5, 7.5], [0.25, 0.5, 0.75]], "queries": ["W0", "W1_d1", "W1_d4", "W1_d16", "W3_K2"], "query_episodes": 24, "reserve": 2, "seeds": [1, 2, 3], "solve_threshold": 0.5, "stop_rule": "5 generations past the first solver"}
- PRIMARY OBSERVABLE: solve_fraction (queries solved by direct reuse / queries) per policy x capable seed; behavioral vs top_k
- CLAIM CEILING: weak at best (<= 6 capable seeds, 5 queries); a capable negative = diversity-preserving retention does not beat top_k prospectively
- FALSIFICATION CONDITION: behavioral - top_k < 0.20 (one query of five) over capable seeds => CAPABLE_NEGATIVE for the diversity hypothesis
- TYPED FAILURE CONDITIONS:
    - STREAM_BELOW_THRESHOLD (no capable seed)
    - UNDERPOWERED (< 3 capable seeds)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - per-seed capability + ceiling per query
    - stream length and first solver generation
    - source maturity
    - archive digests
    - best held-out per query per policy
    - reachability rows (stream runs as treated: stop rule)
- MACHINE CHANGES EXERCISED:
    - B (STREAM_BELOW_THRESHOLD from a pre-freeze check)
    - G (stop rule)
    - E (archives carry maturity)
    - F
    - I
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "primary": {"control": "top_k", "metric": "solve_fraction", "min_effect": 0.2, "treatment": "behavioral"}, "sealed_queries_digest": "sha256:d4e08aa87383fb78c230178e2cf3c9b41367b126bf95f661571a39fe79075a27", "stream": {"threshold": 0.5}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=STREAM_BELOW_THRESHOLD
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): records_s=0.0, replay_s=3.7, streams_s=0.15, total_s=4.0
- decisions: D2-013: capability is checked per seed on the sealed queries BEFORE freezing; the comparison uses capable seeds only; the threshold is sealed
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / solve_fraction        s1      s2      s3    mean    n
    behavioral               0.000   0.000   0.000   0.000    3
    hybrid                   0.000   0.000   0.000   0.000    3
    top_k                    0.000   0.000   0.000   0.000    3
    uniform                  0.000   0.000   0.000   0.000    3

    arm / n_solved              s1      s2      s3    mean    n
    behavioral                   0       0       0   0.000    3
    hybrid                       0       0       0   0.000    3
    top_k                        0       0       0   0.000    3
    uniform                      0       0       0   0.000    3

- typed states fired: ['STREAM_BELOW_THRESHOLD']
    STREAM_BELOW_THRESHOLD  {"stream_max_score": 0.125, "threshold": 0.5}
- disposition candidate (machine): STREAM_BELOW_THRESHOLD -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak at best (<= 6 capable seeds, 5 queries); a capable negative = diversity-preserving retention does not beat top_k prospectively

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-05

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: STREAM_BELOW_THRESHOLD (machine candidate STREAM_BELOW_THRESHOLD). 
