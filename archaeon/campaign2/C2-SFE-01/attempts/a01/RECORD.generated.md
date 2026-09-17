# C2-SFE-01 -- failure-episode transport on a reachable target

## A. STARTUP (preregistration; sealed sha256:17657cc511adb4b14621776789ba0ccdf25a62b02ef201f85de29845cd3a2ddb)

- experiment ID: C2-SFE-01
- parents: SFE-03
- QUESTION: Do k=2 transported FAILURE EPISODES from a structurally relevant source (W2_K2 8-bit) raise held-out competence on W2_K2 4-bit above fresh search and above random-compatible transport (W7_K2) at matched evaluation budget?
- PARENT EVIDENCE: SFE-03 (campaign 1): 0/9 rows reached W1_d4 at N200 G60; the question was never posed (INCONCLUSIVE). Reachability table: W1_d4 4-bit RARE 1/6; W2_K2 4-bit N200 G60 E16 REACHABLE 4/9 (first solved 48-59).
- ASSAY CAPABILITY REQUIREMENT: the fresh arm reaches a foothold (training best >= 0.5) in >= 1 of 2 seeds; otherwise TARGET_UNREACHABLE and the row of record is the reachability update, not a transport result
- POSITIVE CONTROL: fresh arm on W2_K2 4-bit (own generation 0, no transport): expected 4/9 = 0.44 per seed; P(0 of 2) = 0.309
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "pooled_any_budget": {"band95": [0.0615, 0.7923], "budgets": [[200, 100, 24]], "class": "REACHABLE", "freq": 0.3333, "k": 1, "n": 3}}, "W7_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}}
- ARMS:
    - fresh
    - relevant
    - random
- COMMON-RANDOM-NUMBERS POLICY: default (rng_label=crn); identical generation 0 for the three arms per seed (gen0 with no substitution); transported episodes replace the first k of E training episodes each generation
- BUDGET:
    {"E": 4, "G": 6, "G_source": 4, "N": 20, "heldout_episodes": 48, "k": 2, "seeds": [1, 2]}
- PRIMARY OBSERVABLE: competence_heldout (48 held-out episodes) of the elite, per arm x seed; footholds and first_solved_gen secondary
- CLAIM CEILING: weak positive at best (n=2, one target cell, one source per relevance class); a capable negative at this budget is evidence
- FALSIFICATION CONDITION: relevant - fresh < 0.10 mean held-out with the fresh arm reaching >= 1 foothold => CAPABLE_NEGATIVE; relevant <= random => relevance is not the active ingredient
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (fresh 0/2)
    - INTERVENTION_NOT_APPLIED (transport_applied_gens == 0)
    - UNDERPOWERED (< 2 rows per arm)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - first_solved_gen per row
    - transport_applied_gens
    - gen0_provenance
    - source maturity per pack
    - elite genome summary
    - reachability rows appended (fresh arm baseline; others treated)
- MACHINE CHANGES EXERCISED:
    - A reachability lookup in the prereg
    - B typed states
    - C CRN default + gen0 provenance
    - D attempts/resume
    - E maturity on packs
    - F canonical digests + import hash checks
    - G step API episode injection
    - I generated record
- decl (machine-read by archaeon.wse.states): {"artifact_policy": "packs carry maturity as telemetry; the transported material is EPISODES, not organisms, so maturity does not gate the assay (D2-006)", "interventions": [{"arm": "relevant", "counter": "transport_applied_gens"}, {"arm": "random", "counter": "transport_applied_gens"}], "n_min": 2, "positive_control": {"arm": "fresh", "metric": "reached", "min": 1, "min_rows": 1}, "primary": {"control": "fresh", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "relevant"}, "target": {"baseline_arm": "fresh", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): exchange_s=0.0, records_s=0.0, sources_s=0.13, targets_s=0.2, total_s=0.5
- decisions: D2-006: pack maturity is recorded, not gating (transported material is episodes; the source's own success is not required for its failures to be informative)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2    mean    n
    fresh                    0.000   0.083   0.042    2
    random                   0.000   0.083   0.042    2
    relevant                 0.000   0.083   0.042    2

    arm / train_last            s1      s2    mean    n
    fresh                    0.000   0.000   0.000    2
    random                   0.000   0.250   0.125    2
    relevant                 0.000   0.000   0.000    2

- footholds:
    arm                    footholds  first_solved_gen per row
    fresh                  0/2        -,-
    random                 0/2        -,-
    relevant               0/2        -,-

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "fresh", "metric": "reached", "min": 1, "rows": 2, "rows_meeting": 0, "values": [0, 0]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak positive at best (n=2, one target cell, one source per relevance class); a capable negative at this budget is evidence

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-01

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
