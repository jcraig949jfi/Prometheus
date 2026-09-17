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

The question SFE-03 could not pose was posed: the target was reachable (fresh 2/6 footholds at generations 35 and 49, held-out 0.32 mean; pooled W2_K2 4-bit N200 G60 E16 now 6/15) and every transported arm applied its transport in all 60 generations (transport_applied_gens = 60/60 on 12/12 rows; packs 8/8 episodes each; 12/12 import hash checks). The machine candidate CAPABLE_NEGATIVE is accepted, with the direction stated: relevant transport HURT. relevant - fresh = -0.160 held-out (paired: relevant beat fresh in 1 of 6 seeds), relevant 0/6 footholds vs fresh 2/6; random-compatible transport did not hurt (-0.026, 1/6 footholds). The preregistered falsification condition (relevant - fresh < 0.10 with a reaching fresh arm) fired; the secondary (relevant <= random) also fired: relevance is not the active ingredient, and at this dose it is a cost. Exploratory (not preregistered, not claimed): (i) the relevant packs are FIXED 8-bit episodes occupying half the training battery every generation; the random packs are also fixed but from an unrelated structure (ASK2 combine) and were harmless, so fixedness alone does not explain the harm; (ii) in 4 of 6 seeds the relevant arm's elite ended below 0.06 held-out with training best <= 0.16 for all 60 generations: the population never found a foothold on EITHER family, consistent with the 8-bit failure episodes selecting against the 4-bit solution path (value width is the one knob that differed). Source maturity: relevant sources solved their own cell in 2/6 seeds (first solved 25, 56); the two transport arms from SOLVED sources (s1, s2) were not better (0.312, 0.052). Must not be claimed: that failure transport cannot help at a smaller dose or with matched value width; that W7_K2 transport is neutral in general (n=6).

## D. TEARDOWN (generated)

- worlds: {"source-random": "TERMINATED", "source-relevant": "TERMINATED", "target": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-01

No instrument defects on the attempt of record (a02; a01 was the dry run). Machine behaved: the reachability lookup chose the target; the prereg was sealed and published before any search; typed states were computed (none fired); the disposition was emitted; 30 reachability rows appended (12 source, 18 target). Bench notes for the ledger: (1) transported episodes are FIXED across generations while fresh episodes rotate; the loop should be able to draw transported episodes from a pack LARGER than k per generation (a rotating transport) so dose and fixedness separate -- KEEP_POLICY/TO_MACHINERY; (2) the relevance rule left value_bits free; the table should carry per-knob relevance so a harness can declare which knobs may differ -- FRICTION; (3) the prereg's positive control and target both key on the fresh arm, so a fresh 0/6 would have fired TARGET_UNREACHABLE and POSITIVE_CONTROL_FAILED together (redundant but harmless).

## F. LANDSCAPE / GRADIENT NOTES

W2_K2 4-bit N200 G60 E16: fresh footholds at 35 and 49 (campaign 1: 48, 50, 54, 59); the plateau-with-late-exit shape holds (best 0.19-0.47 for 30+ generations, then the step). The relevant-transport arms show a different shape: a low flat (best <= 0.16 in 4/6 seeds for all 60 generations) -- a floor, not a plateau, below the fresh arm's plateau. The random-transport arms climb like fresh (best 0.34-0.53) and one exits at 51. Reachability additions: W2_K2 8-bit N200 G60 E16 baseline 2/6 (25, 56) -- the 8-bit cell is reachable at G60, which campaign 1 never measured at that budget; W7_K2 4-bit N200 G60 E16 0/6 (OBSERVED_UNREACHABLE_AT_BUDGET).

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable (fresh 2/6), transport applied on every row, n=6 per arm; relevant failure-episode transport at k=8/16 lowers held-out competence on W2_K2 4-bit by 0.16 (1/6 paired wins) and yields 0/6 footholds; random-compatible transport is neutral. The SFE-03 question is answered at this dose and budget: no.
