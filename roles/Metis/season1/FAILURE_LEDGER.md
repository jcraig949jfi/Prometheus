# Metis Season 1 -- FAILURE LEDGER

Currency: 2026-09-13. What went wrong, what is unmitigated, and what a
reader should attack first. Written before the receipt so the receipt
cannot quietly omit anything here.

## 1. THE SPECIMEN VETOED ALL FIVE HISTORICAL EPISODES

    E1 greedy-LoRA     3 confidence vetoes
    E2 Apollo          2
    E3 Saxl            2
    E4 Geometry-1      2
    E5 Erebos          3

Five for five. That is the exact shape of the season prompt's failure
mode 10, and on its own it is indistinguishable from a mechanism that
vetoes everything. The adversarial tests C and F show it CAN stay
silent, but those are synthetic bundles I wrote to make it stay silent,
which is weak evidence about its behaviour on real material.

WHAT I DID ABOUT IT: added a POSITIVE CONTROL from the real record
(E1b), the same episode one day later, after the two discriminators had
actually been run. Result: zero confidence vetoes, all three rival
explanations eliminated, two independent reasons instead of one, and no
discriminator proposed because nothing was live. The mechanism's output
moves with the evidence, on real data, in the right direction.

WHY THIS IS STILL NOT CLEAN. E1b was built AFTER I saw the 5/5 veto
result. The mechanism was frozen and unchanged (hash in
SPECIMEN_FREEZE.md, commit 2a650277b) so this is not tuning, but the
CASE was selected by me, knowing what I needed it to show. A reader
should treat E1b as the weakest artifact in the season and the first
thing to attack. The honest reading is that 4 of the 5 episodes were
selected as failures (PREREG R3), so a high veto rate is partly a
property of the sample, and I have exactly ONE real case on the other
side.

## 2. THE PROVENANCE OF THE CANONICAL EPISODE IS BAD

E1 greedy-LoRA is the season's motivating specimen and its evidence is
the weakest in the set:

    roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md
      committed ONCE, 7e38227ee, 2026-06-07T06:11-04:00
      -- four days after the v1 result it describes
      -- three days after the addendum it describes
    ergon/learner/greedy/.gitignore excludes runs/ and corpus/*.jsonl
      so every corpus, adapter and eval JSON is untracked
    no other commit in 2026-06-01..09 references the work

So: one retrospective document, self-dated, describing two experiments
whose artifacts were never committed, with no independent corroboration
of its internal timeline anywhere in the repository. Graded
INTERNAL_UNCORROBORATED.

THE LOAD-BEARING ASSUMPTION THIS FORCES: my E1 bundle treats the v1
caveat list as pre-existing the addendum, because the addendum says
"Follow-up to caveat 1". A single author writing a single document at
one sitting could have written the caveats afterwards and placed them
above. I cannot rule that out, and if it is what happened then E1's
cutoff is fictional and the episode proves nothing about what was
knowable on 2026-06-03.

This is the same defect class Skopos reported on 2026-09-11: results
written to gitignored directories have no provenance at all. It has now
cost this season the reconstructability of its own canonical case.

## 3. TWO OF SEVEN VOCABULARY CONCEPTS DID NOT EARN THEMSELVES

The preregistration put all seven on probation and said any concept not
load-bearing in a construction episode by freeze is DELETED. Result:

    DEPENDENT              EARNED -- the union-find grouping is the core
    VETO                   EARNED -- the output type
    INSTRUMENT_SUSPECT     EARNED -- E2, from cutoff-available signature
    STALE                  EARNED -- E3, fired on the withdrawal date
    CHEAP_KILL_AVAILABLE   EARNED -- the discriminator selector

    ORTHOGONAL             NOT EARNED. It is implemented (set-disjoint
                           rules_out, and Discriminator.partitions) but
                           it never appears in any output and no episode
                           needed it as a NAME. It is a property of the
                           implementation, not a concept the mechanism
                           reports. DELETED as vocabulary; the code that
                           implements the idea stays.
    BASE_RATE_CONFOUNDED   NOT EARNED. It turned out to be nothing more
                           than one particular live competing
                           explanation, declared per-episode like any
                           other. Promoting it to vocabulary would have
                           been an ontology entry for a single episode's
                           content. DELETED.

Predicted in the preregistration that at least one would go; two did.

## 4. THE MECHANISM'S SOFT UNDERBELLY IS `rules_out`, AND I ASSIGN IT

Everything the specimen does downstream is a set operation, and the sets
come from two fields I write by hand: `upstream` and `rules_out`. The
grouping is defensible -- "these four measurements observe the same
trained adapter" is checkable against the source. `rules_out` is not
equally safe: deciding that the shuffle control eliminates
FORMAT_ONLY_COMPLETE but not FORMAT_FOLLOWING is a judgement, and a
different analyst could write it differently and flip the output.

This is preregistered failure criterion F4 and I am NOT declaring it
passed. What I did instead:
  - every rules_out carries a justification string quoting the observed
    value it rests on, so the judgement is inspectable and falsifiable
    against the source rather than hidden in a weight;
  - undeclared explanation ids are now a hard error (found by running,
    see item 5), so a typo cannot silently weaken an elimination.
Neither makes the assignment objective. A second analyst independently
encoding these five bundles from the same sources, blind to my
encoding, is the experiment that would settle F4, and it has NOT been
run. Until it is, every episode result in this season is one analyst's
reading passed through a deterministic function.

## 5. A DEFECT IN MY OWN INSTRUMENT, FOUND BY RUNNING IT

The first E1 encoding carried `rules_out: ["PURE_FORMAT_ONLY"]`, an
explanation id that was never declared. It eliminated nothing and raised
nothing: the set subtraction simply found no match. A typo silently
weakened the mechanism in the permissive direction.

This is the fourth instance this seat has now met of the same shape --
missing or unrecognised input becoming a benign no-op rather than an
error (metis.py's `except: pass` for an absent context source;
metis_portfolio.py's "(state.json reports up)"; Pronoia's "skopos: OK";
and now my own code). Fixed with a hard error and a regression test.

I am NOT calling four instances a pattern. Skopos declined to supply a
base rate for exactly this and was right to: four instances found by
people looking at something else are four draws from an unenumerated
population with no denominator and no null, and writing a permissive
fallback is the path of least resistance in most languages, so the share
under the null could be large. The enumeration Skopos specified --
classify every fallback in the repository by DIRECTION and publish the
denominator -- has not been run by anyone.

## 6. THE VETO-RATE BOUND PASSED AT THE BOUNDARY, NOT WITH MARGIN

Preregistered: at most 4 of 6 lettered adversarial tests may emit a
veto. Measured: exactly 4 (A, B, D, F). One more firing would have
failed the season on its own rule. A bound hit exactly is weaker
evidence than a bound cleared, and I am recording it as such rather
than as a pass.

## 7. HINDSIGHT LEAKAGE I CANNOT EXCLUDE

  - I knew all five outcomes before the preregistration was written
    (PREREG s3). The 2/3 split protects the MECHANISM from being shaped
    by three more evidence structures; it does not protect the EVIDENCE
    SELECTION in E3, E4 and E5, which I performed knowing the answers.
  - The candidate discriminators are the sharpest leak. For E4 I listed
    PERMUTE_THE_MASK_ALONE, which is approximately the test Harmonia
    actually built ten days later; for E2, a cheat control on the
    lineage counter; for E5, a permutation null on real data. In each
    case I knew what had worked. A defender would say each was
    derivable at the cutoff from the confound named in the same
    document. An attacker would say I would not have thought of them
    without knowing. I cannot settle that from here, and a prospective
    season is the only thing that can.
  - Partial mitigation actually applied: in E4 I included
    E4.loading_density_coincidence, an item that supports the RIVAL and
    not the claim, because it sits in the same document at the same
    cutoff. Bundles that contain only claim-supporting items are the
    ones to distrust.

## 8. WHAT THE SEASON DID NOT TEST AT ALL

  - Whether any of this improves a decision. No prospective evidence.
  - Whether the dependence grouping is right when upstream tokens are
    genuinely unknown rather than reconstructable. Every bundle here had
    a legible ancestry because someone documented it.
  - Whether the ordinal cost ladder survives a case where the cheap test
    and the dear test are one rung apart. Every episode here had a
    MINUTES-vs-HOURS-or-worse gap, which is the easy case.
  - Whether two analysts agree (item 4).
  - Any episode where the historical decision was RIGHT and the evidence
    genuinely independent, apart from the single post-hoc E1b.
