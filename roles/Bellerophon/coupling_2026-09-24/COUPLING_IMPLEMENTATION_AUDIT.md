# COUPLING IMPLEMENTATION AUDIT -- physics v3

Code: prometheus/z80atlas/coupling.py (Ledger, Competence), world.py (integration), adjudication.arch_descriptor,
coupling_campaign.py (driver). Tests: prometheus/z80atlas/tests/test_coupling_v3.py (19 tests) + the existing 39
(v1 golden replay, v2 repairs) = 58/58 passing at the freeze.

## 1. Accounting model

Quantity: R (copy resource), integer >= 0, one per organism, stored on the Org object in the World (never in the
256-byte VM memory the organism executes in).
Sources: BASE per interaction (unconditional); BONUS per rewarded event (mode-dependent; s3 of the prereg).
Sink: constructing an offspring: COPY_COST x n_written (window bytes the writer wrote) -- charged in
_apply_reproduction after the physics' viability rule passes and BEFORE the child is registered; refused (no child,
no charge) when R cannot pay.
Losses: clamping at CAP (counted), death by energy/age (counted), being overwritten by another's offspring (counted).
Identity (asserted in Ledger.close, every run): earned_base + earned_bonus = spent + clamped + lost_death +
lost_overwritten + held_end. An imbalance raises and VOIDS the run.
Timing: the evaluator runs after the execution finished; credit is therefore spendable only in a later execution.
DELAYED credit is queued with its due tick; YOKED credit is distributed after the tick's interactions.
Randomness: the ledger's own rng (seed-derived, separate from the world rng) drives SHUFFLED inputs and RANDOM_REWARD
recipients, so matched arms consume the world rng identically until their dynamics diverge.

## 2. Invariants and the test that holds each (directive Phase 0 list)

| requirement | test |
|---|---|
| resource earned only from the declared task output; incorrect -> base only; zero output -> base only; OFF -> base only | test_resource_earned_only_from_the_declared_task_output |
| only the first output is scored (no farming by repetition) | test_only_the_first_output_is_scored_no_farming_by_repetition |
| organism cannot modify its ledger; no evaluator state in memory (pre-execution memory = own tape + partner + inputs only) | test_organism_cannot_touch_its_ledger_and_no_evaluator_state_is_in_memory |
| no reproduction performed by the evaluator (births == paid births; rich non-copiers never breed; EXTERNAL refused) | test_reproduction_is_never_performed_by_the_evaluator |
| copying physically charged; unfunded births refused with no charge; newborn R = 0 | test_copying_is_charged_and_unfunded_births_are_refused |
| no reward from future information: credit spendable only after its execution | test_credit_is_spendable_only_after_the_execution_that_earned_it |
| no silent under/overflow (cap clamps counted; underflow raises); coupled physics requires v3 | test_no_silent_overflow_or_underflow |
| ledger balances in every mode | test_ledger_balances_in_every_mode |
| YOKED delivers exactly the partner's schedule | test_yoked_distributes_exactly_the_schedule |
| checkpoint/resume preserves exact balances (pickle mid-run, continue = uninterrupted) | test_checkpoint_resume_preserves_balances_exactly |
| deterministic fixtures replay identically | test_deterministic_replay |
| migration never duplicates under coupling | test_migration_never_duplicates_under_coupling |
| post-treatment measurement never feeds back (sabotaged competence -> identical dynamics) | test_measurement_never_feeds_back |
| task identity acts only through the ledger (OFF: task-independent trajectories; ON: task matters) | test_task_identity_acts_only_through_the_ledger |
| shuffled verifier pays only chance | test_shuffled_verifier_pays_only_chance |
| delayed credit arrives late or never | test_delayed_credit_arrives_late_or_never |
| v1/v2 untouched (golden fixture; coupling fields None) | test_v1_v2_untouched_by_v3 + test_v1_golden_replay_is_byte_identical |
| fixtures have their declared properties | test_campaign_fixtures_have_their_declared_properties |
| plan deterministic; YOKED arms share seed/fixtures/K with their ON partner | test_campaign_plan_is_deterministic_and_yokes_follow_their_partner |

## 3. Positive and negative controls built into the campaign

Positive: A1 (known competent copier, ON), A8 (known reproducer under grounded v2 physics). Negative: A3 (copying
intact, computation removed), A4 (computation intact, copying removed), A6 (random/constant output), A7 (zero
output), A5/B-SHUFFLED (verifier relationship destroyed). Edge ablations: C OFF / RANDOM_REWARD / DELAYED /
IRRELEVANT / YOKED. Exploit probes: Lane I + the automated noncompetent-earner probe in every run.

## 4. Known physics limits (declared, not repaired)

- A competent organism that runs into its partner's code can produce a correct output it did not compute (the PC
  leaves the own tape in 69% of random tapes -- grounding m5). The evaluator pays for the OUTPUT; the automated probe
  measures how often this happens (correct_by_noncompetent) and preserves specimens. This is substrate behaviour, not
  an accounting bug.
- Competence is measured alone on a fixed panel; an organism can be correct in context but not alone (and vice versa
  via input-dependent luck). Both directions are counted.
- PAIR_EXECUTION and EXTERNAL reproduction are refused under coupling (the window/birth model does not apply).
- Birth competence is measured on a deterministic 1-in-8 sample of births (cost); run-level rates are ratios within
  the sample.
