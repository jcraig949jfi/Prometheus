# C2-SFE-01 -- failure-episode transport on a reachable target

## A. STARTUP (preregistration; sealed sha256:37fd00a04f1a50b60d1645e280ab02b15969f5c1f343eba3f9a6fd7c5a8df968)

- experiment ID: C2-SFE-01
- parents: SFE-03
- QUESTION: Do k=8 transported FAILURE EPISODES from a structurally relevant source (W2_K2 8-bit) raise held-out competence on W2_K2 4-bit above fresh search and above random-compatible transport (W7_K2) at matched evaluation budget?
- PARENT EVIDENCE: SFE-03 (campaign 1): 0/9 rows reached W1_d4 at N200 G60; the question was never posed (INCONCLUSIVE). Reachability table: W1_d4 4-bit RARE 1/6; W2_K2 4-bit N200 G60 E16 REACHABLE 4/9 (first solved 48-59).
- ASSAY CAPABILITY REQUIREMENT: the fresh arm reaches a foothold (training best >= 0.5) in >= 1 of 6 seeds; otherwise TARGET_UNREACHABLE and the row of record is the reachability update, not a transport result
- POSITIVE CONTROL: fresh arm on W2_K2 4-bit (own generation 0, no transport): expected 4/9 = 0.44 per seed; P(0 of 6) = 0.029
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "pooled_any_budget": {"band95": [0.0362, 0.6245], "budgets": [[20, 4, 4], [200, 100, 24]], "class": "RARE", "freq": 0.2, "k": 1, "n": 5}}, "W7_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "pooled_any_budget": {"band95": [0.0, 0.6576], "budgets": [[20, 4, 4]], "class": "UNESTABLISHED", "freq": 0.0, "k": 0, "n": 2}}}
- ARMS:
    - fresh
    - relevant
    - random
- COMMON-RANDOM-NUMBERS POLICY: default (rng_label=crn); identical generation 0 for the three arms per seed (gen0 with no substitution); transported episodes replace the first k of E training episodes each generation
- BUDGET:
    {"E": 16, "G": 60, "G_source": 60, "N": 200, "heldout_episodes": 48, "k": 8, "seeds": [1, 2, 3, 4, 5, 6]}
- PRIMARY OBSERVABLE: competence_heldout (48 held-out episodes) of the elite, per arm x seed; footholds and first_solved_gen secondary
- CLAIM CEILING: weak positive at best (n=6, one target cell, one source per relevance class); a capable negative at this budget is evidence
- FALSIFICATION CONDITION: relevant - fresh < 0.10 mean held-out with the fresh arm reaching >= 1 foothold => CAPABLE_NEGATIVE; relevant <= random => relevance is not the active ingredient
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (fresh 0/6)
    - INTERVENTION_NOT_APPLIED (transport_applied_gens == 0)
    - UNDERPOWERED (< 6 rows per arm)
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
- decl (machine-read by archaeon.wse.states): {"artifact_policy": "packs carry maturity as telemetry; the transported material is EPISODES, not organisms, so maturity does not gate the assay (D2-006)", "interventions": [{"arm": "relevant", "counter": "transport_applied_gens"}, {"arm": "random", "counter": "transport_applied_gens"}], "n_min": 6, "positive_control": {"arm": "fresh", "metric": "reached", "min": 1, "min_rows": 1}, "primary": {"control": "fresh", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "relevant"}, "target": {"baseline_arm": "fresh", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 3; artifacts 13; imports 12; records 18; errors 0
- import hash checks: 12/12 ok
- timings (s): exchange_s=4.21, records_s=5.09, sources_s=49.05, startup_s=0.41, targets_s=83.07, teardown_s=0.49, total_s=143.6
- decisions: D2-006: pack maturity is recorded, not gating (transported material is episodes; the source's own success is not required for its failures to be informative)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3      s4      s5      s6    mean    n
    fresh                    0.323   0.292   0.344   0.104   0.333   0.542   0.323    6
    random                   0.062   0.052   0.510   0.104   0.531   0.521   0.297    6
    relevant                 0.312   0.052   0.302   0.271   0.031   0.010   0.163    6

    arm / train_last            s1      s2      s3      s4      s5      s6    mean    n
    fresh                    0.188   0.344   0.344   0.188   0.250   0.531   0.307    6
    random                   0.094   0.125   0.438   0.156   0.438   0.344   0.266    6
    relevant                 0.219   0.094   0.281   0.312   0.062   0.125   0.182    6

- footholds:
    arm                    footholds  first_solved_gen per row
    fresh                  2/6        -,-,35,-,-,49
    random                 1/6        -,-,-,-,51,-
    relevant               0/6        -,-,-,-,-,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.3229, "effect": -0.1597, "min_effect": 0.1, "n_control": 6, "n_treatment": 6, "paired": 6, "paired_wins": 1, "treatment_mean": 0.1632}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: weak positive at best (n=6, one target cell, one source per relevance class); a capable negative at this budget is evidence

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"source-random": "TERMINATED", "source-relevant": "TERMINATED", "target": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-01

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
