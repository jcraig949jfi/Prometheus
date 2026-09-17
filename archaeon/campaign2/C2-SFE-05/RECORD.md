# C2-SFE-05 -- retention replay with a proven-capable stream

## A. STARTUP (preregistration; sealed sha256:da2674ad9b361d6615bea66f24b0a1d4c2ce7b6e7fdcb40875a92cac87624397)

- experiment ID: C2-SFE-05
- parents: SFE-02
- QUESTION: Gate: does a stream of every organism a W2_K2 4-bit search evaluates (run 5 generations past its first solver) contain an organism scoring >= 0.5 on at least one SEALED future query cell (W0, W1_d1, W1_d4, W1_d16, W3_K2)? Science (capable seeds only): do the four retention policies under one cap (32 items) differ in prospective solve fraction on the sealed queries?
- PARENT EVIDENCE: SFE-02: streams of 1024 and 4096 W1_d1 organisms held nothing above threshold (twice INCONCLUSIVE). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE; W0 4-bit COMMON by ~G35; sub-solutions of W2_K2 solvers score 0.5 on W0-like cells (C2-SFE-03/04).
- ASSAY CAPABILITY REQUIREMENT: per seed: max over the stream's top-64 (by source score) of held-out reward on any sealed query >= 0.50, checked BEFORE freezing archives; experiment: >= 3 capable seeds (else UNDERPOWERED); no capable seed => STREAM_BELOW_THRESHOLD
- POSITIVE CONTROL: the stream's own top-64 organisms on the sealed queries (the uncapped ceiling); the threshold 0.50 is sealed here and never changed
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "first_solved_gens": [13, 19, 32, 35, 39, 48, 49, 50, 54, 59], "freq": 0.4762, "k": 10, "n": 21}, "at_budget_any_foundry": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.4762, "k": 10, "n": 21}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.2153, 0.5577], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3704, "k": 10, "n": 27}}}
- ARMS:
    - top_k
    - uniform
    - behavioral
    - hybrid
- COMMON-RANDOM-NUMBERS POLICY: one stream per seed shared by every policy (policy-independent by construction); policies are deterministic given the stream and the seed
- BUDGET:
    {"E": 16, "G_cap": 70, "N": 200, "caps": {"bytes": 9600, "items": 32}, "edges": [[0.5, 1.5, 2.5], [4.5, 5.5, 6.5, 7.5], [0.25, 0.5, 0.75]], "queries": ["W0", "W1_d1", "W1_d4", "W1_d16", "W3_K2"], "query_episodes": 24, "reserve": 8, "seeds": [1, 2, 3, 4, 5, 6], "solve_threshold": 0.5, "stop_rule": "5 generations past the first solver"}
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

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=STREAM_BELOW_THRESHOLD
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 32; imports 0; records 24; errors 0
- timings (s): records_s=6.62, replay_s=22.33, startup_s=0.05, streams_s=50.79, teardown_s=0.17, total_s=80.9
- decisions: D2-013: capability is checked per seed on the sealed queries BEFORE freezing; the comparison uses capable seeds only; the threshold is sealed
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / solve_fraction        s1      s2      s3      s5      s6    mean    n
    behavioral               0.400   0.400   0.400   0.200   1.000   0.480    5
    hybrid                   0.400   0.400   0.400   0.200   1.000   0.480    5
    top_k                    0.400   0.400   0.400   0.200   1.000   0.480    5
    uniform                  0.400   0.400   0.400   0.200   0.000   0.280    5

    arm / n_solved              s1      s2      s3      s5      s6    mean    n
    behavioral                   2       2       2       1       5   2.400    5
    hybrid                       2       2       2       1       5   2.400    5
    top_k                        2       2       2       1       5   2.400    5
    uniform                      2       2       2       1       0   1.400    5

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.48, "effect": 0.0, "min_effect": 0.2, "n_control": 5, "n_treatment": 5, "paired": 5, "paired_wins": 0, "treatment_mean": 0.48}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: weak at best (<= 6 capable seeds, 5 queries); a capable negative = diversity-preserving retention does not beat top_k prospectively

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

The assay SFE-02 twice failed to make capable became capable in 5 of 6 seeds, checked on the sealed queries BEFORE any archive was frozen: streams of 8,200-14,000 organisms from W2_K2 4-bit searches (stopped 5 generations past the first solver or at the 70-generation cap) contained an organism scoring 1.0 on the sealed W0 query in every capable seed, even in the four seeds whose source never solved W2_K2 itself (source elites 0.28-0.44) -- the half-credit W2_K2 organism IS a W0 solver. Seed 4 (source elite 0.09) was below threshold on every query and was excluded by the gate as preregistered. The retention question was then posed for the first time: over the 5 capable seeds, top_k = behavioral = hybrid = 0.48 solve fraction (identical per seed: 2/5, 2/5, 2/5, 1/5, 5/5), uniform 0.28 (identical to the others in seeds 1-5, 0/5 in seed 6). The machine candidate CAPABLE_NEGATIVE is accepted for the diversity hypothesis: behavioral - top_k = 0.00 (paired wins 0/5). The shape behind the tie: the solvers a 32-item archive needs are either ABUNDANT in the stream (the W0 solver / W2_K2 half-credit organism, retained by every policy including uniform random retention) or RARE late arrivals (seed 6, first W2_K2 solver at generation 49: retained organisms solving W1_d1 0.83, W1_d4 0.96, W1_d16 0.92 and W3_K2 0.67, kept by every score-aware policy and missed by uniform). Diversity-preserving retention neither adds nor loses prospective value against top_k under this cap because every score-aware policy keeps the same few solvers. Must NOT be claimed: that retention policy never matters (one source cell, five queries, cap 32, n=5); that behavioural archives are useless (they tie, they do not lose).

## D. TEARDOWN (generated)

- worlds: {"retention": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-05

Zero engine errors; 1 world; 32 artifacts (sealed queries, 6 stream manifests with capability + ceilings, 24 archives with the stream population's maturity block); 24 records; 6 reachability rows (treated: stop rule). The pre-freeze capability check is the machine change that made this experiment possible; it ran as a typed-state input (STREAM_BELOW_THRESHOLD fired correctly in the dry run and not here). Bench notes: (1) source MATURITY (solved own cell) is the wrong gate for a retention stream -- four capable streams came from unsolved sources; the sealed-query ceiling is the right one (KEEP_POLICY, recorded); (2) top_k retained 22 and 30 items in two seeds under the byte cap while the others held 32: the count and byte caps interact as Techne's finding said (bounds reported per archive); (3) h3_replay's solve fraction and the harness's own count from best-per-query agree on every row (solve_fraction_h3 == solve_fraction).

## F. LANDSCAPE / GRADIENT NOTES

A W2_K2 4-bit search's evaluated organisms contain a W0 solver long before (and whether or not) the search reaches W2_K2's half-credit shelf: 5/6 streams had one, at source elite 0.28-0.56. Seed 6's stream held organisms solving W1_d1 (0.83), W1_d4 (0.96) and W1_d16 (0.92) by direct reuse: a W2_K2 lineage reached cells that are RARE or unreached by direct search at comparable budgets (W1_d4 1/14 at G60; W1_d16 never searched at 4-bit). That is a corridor: evolving for two-stream recall produces delayed-recall competence as a by-product in some lineages. W3_K2 sits at 0.42-0.67 for every capable stream (the ask_mode=one half-credit). Stream telemetry: source_score_max 0.41-0.59 across seeds; stop rule fired in 2 seeds (35 and 49).

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Stream capability proven on the sealed queries before freezing (5/6 seeds); the retention comparison was posed for the first time and diversity-preserving policies tie top_k exactly (0.48 vs 0.48, 0/5 paired wins); uniform random retention loses only where solvers are rare (seed 6). SFE-02's question is answered at this cap and stream: no prospective advantage for diversity.
