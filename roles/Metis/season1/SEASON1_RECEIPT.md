# Metis Season 1 -- RECEIPT

Currency: 2026-09-13. Read FAILURE_LEDGER.md beside this; nothing here
supersedes anything there.

## PRIMARY RULING

    SPECIMEN_SURVIVES_RETROSPECTIVE

Narrowly, and with the single largest caveat stated first: the specimen
vetoed all five historical episodes, and the one real case on the other
side of the ledger (E1b) was constructed after I saw that result. The
mechanism was frozen and unchanged when E1b ran -- hashes in
SPECIMEN_FREEZE.md, commit 2a650277b -- so this is case selection, not
tuning, but it is the weakest joint in the season and the first thing a
reader should attack.

INSTRUMENT_INADEQUATE was considered and rejected for the season as a
whole: four of five episodes reconstruct from committed, dated sources.
It IS the right verdict for E1's provenance taken alone (failure ledger
item 2), and that is recorded rather than averaged away.

## WHAT WAS BUILT

    roles/Metis/season1/
      SEASON1_PREREGISTRATION.md   frozen a4f345aa7, before any ledger
      SPECIMEN_FREEZE.md           frozen 2a650277b, before E3/E4/E5
      specimen/compose.py          the mechanism, 380 lines
      specimen/test_adversarial.py 13 tests, A-F plus guards
      bundles/                     6 episode bundles
      REPLAY_RESULTS.{json,txt}    exact outputs
      REPLAY_SUMMARY.txt
      FAILURE_LEDGER.md

The mechanism is set operations over declared structure: availability
filter, search-completeness gate, union-find dependence grouping over
shared upstream tokens, live-explanation elimination, vetoes, then the
cheapest cutoff-available discriminator that actually partitions what is
live. No learned weights, no model call, and no scalar anywhere in the
file -- confidence numbers were out of scope, so there is no score to
inspect, only structure.

## REPLAY

    episode                    items reasons  live  conf_veto  discriminator
    E1 greedy-LoRA                 4       1     3          3  RELATION_BASE_RATE_ORACLE [MINUTES]
    E1b addendum (POS CONTROL)     3       2     0          0  (none -- nothing live)
    E2 Apollo April                3       1     2          2  LINEAGE_CHEAT_CONTROL [MINUTES]
    E3 Saxl                        3       1     2          2  CHECK_OBJECT_MATCHES_CLAIM [MINUTES]
    E4 Geometry-1                  4       1     2          2  PERMUTE_THE_MASK_ALONE [MINUTES]
    E5 Erebos                      4       1     3          3  PERMUTATION_NULL_ON_REAL_LEDGER [HOURS]

In every historical episode, N apparently agreeing items collapsed to
ONE independent reason. The shared ancestors were, respectively: one
trained adapter and its format gain; one lineage counter; one model's
recall of one preprint; one matrix and one observation mask; one
generator architecture.

## THE THREE TRAPS THE SUCCESS BAR NAMED

1. GREEDY-LORA'S CORRELATED-EVIDENCE TRAP -- CONFRONTED. Four channels,
   one reason. BASE_RATE_PRIORS stays live because no admitted item
   eliminates it, and the specimen selects the base-rate oracle
   (MINUTES) over the entity-disjoint split (HOURS). History ran the
   entity-disjoint split, which targets memorization and leaves base
   rates untouched; the addendum later measured the base-rate floor at
   0.669 against roughly +0.097 of genuine reasoning.

2. APOLLO'S INSTRUMENT-ARTIFACT TRAP -- CONFRONTED, at the HARD cutoff.
   At 2026-04-06, with the lineage defect still eighteen months of
   nobody's knowledge away from being found, the specimen fires
   INSTRUMENT_VETO from information on the face of the report: the same
   table records LLM Calls 18/31/15 beside llm_alive=0 in every run.
   Measured across the whole tracked series, 77 of 77 reports carrying
   that field read zero in every stratum and not one ever recorded a
   nonzero value. It proposes a cheat control costing minutes and
   REJECTS the 800-generation run for NO_DISCRIMINATORY_POWER, because a
   run whose survival metric comes from the suspect counter inherits the
   defect. The April observation is never credited as a valid early
   warning, which is what the special trap demanded.

3. C-05'S UNKNOWN-VERSUS-ABSENT TRAP -- CONFRONTED. An unproven absence
   is withheld from the supporting set and reported as ABSENCE_UNPROVEN;
   a complete enumeration is admitted normally, so absence stays
   provable in principle. Regression test derived from my own 2026-09-11
   failure.

WITHOUT MERELY VETOING EVERYTHING: the positive control clears all
vetoes on the same episode one day later, and adversarial C and F are
silent. That is the whole of the evidence for this clause, and it is
thin.

## ERGON'S SELF-CORRECTION -- WHAT CAUSED IT

From the record only. The v1 section carries a numbered caveat list, and
the addendum opens "Follow-up to caveat 1." Caveat 1 names value
memorization as a live alternative and names the discriminating test
("Next run: object-level (entity-disjoint) split"). Caveat 3 names
format-following as a large share of the raw number.

So the corrective mechanism was AN EXPLICIT SELF-AUTHORED CAVEAT THAT
NAMED A COMPETING EXPLANATION AND ITS TEST, acted on the next day. Not
operator skepticism, not accident: the author wrote down the rival and
then went and killed it.

The sharp part is what the caveats did NOT contain. The relation
base-rate oracle appears nowhere in the v1 section. Memorization and
format were pre-named and caught; the base rate was not pre-named, and
it is the one that did the most damage -- a 0.669 floor under a headline
of 0.907. Ergon's mechanism worked exactly as far as its author's
imagination of rivals extended, and stopped there.

That is the honest case for this seat existing, and it is also the
limit of it: the specimen does not imagine rivals either. It only
enforces that declared rivals must be eliminated rather than
out-agreed. Someone still has to name BASE_RATE_PRIORS. All the
mechanism guarantees is that once named, four agreeing channels cannot
bury it.

## VOCABULARY: 5 OF 7 SURVIVED

Kept: DEPENDENT, VETO, INSTRUMENT_SUSPECT, STALE, CHEAP_KILL_AVAILABLE.
Deleted under the probation rule: ORTHOGONAL (implemented, never needed
as a name) and BASE_RATE_CONFOUNDED (a single episode's content, not a
mechanism concept). Predicted at least one deletion; got two.

## WHAT THIS DOES NOT LICENSE

Not that Metis improves Prometheus decisions. Not that composition beats
single-channel selection -- P-5 was never tested, because no single-channel
baseline was run, and I should not be credited with a comparison I did
not make. Not that five episodes generalize. The licensed claim is
exactly the one the success bar allows:

    COMPOSITION-VETO MECHANISM SURVIVES RETROSPECTIVE SPECIMENS

## CONFLICT OF INTEREST

I proposed the mechanism, wrote the bundles that feed it, chose which
evidence items exist, selected the positive control after seeing the
result it was needed for, and graded the outcome. Preregistration R4.
The season does not claim validation. The single most valuable attack is
in failure-ledger item 4: a second analyst independently encoding these
same five bundles from the same sources, blind to my encoding. If their
`rules_out` assignments differ enough to flip an episode, preregistered
failure criterion F4 fires and this ruling should be withdrawn.

Routing that attack to Kairos, Charon, Nemesis or Elenchus is the
operator's call, not mine.

## RECOMMENDED, NOT STARTED: SEASON 2

Prospective only. Expose the specimen to live Prometheus evidence
bundles whose outcomes are not yet known; preregister, before each, the
veto set and the proposed discriminator; then measure whether the
recommended test was cheaper and more discriminating than what the lane
actually ran. That is where claims about experiment selection begin.
Two preconditions from this season: a second encoder for the F4 check,
and at least three positive controls -- real episodes where the evidence
was independent and the conclusion held -- because one is not enough to
show the mechanism discriminates rather than objects.

Nothing was integrated into any production consumer. METIS-01R remains
owner-less by ruling, METIS-15 remains an unpatched corpse, TALOS-10
remains unanswered, and both dormant loops remain stopped.
