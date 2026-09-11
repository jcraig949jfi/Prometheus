# Preregistration -- Eos first active pass (EOS-07 controls + typed intake)

Currency: 2026-09-11. Committed BEFORE either mechanism was run over the
sample, so the order is in git history (base role s2: "Preregister before
touching data, in its own commit so the order is in git history. Never move
a gate after seeing a result").

At the time this file is committed: the probe has run (upstream liveness,
base rule 9 -- roles/Eos/intake/probe_arxiv.json, 2 requests, both 200, 24
items); the old scorer has NOT been run over any fixture; the new gate has
NOT been run over any item; no score and no verdict has been read.

## Conflict of interest, declared

Eos designed the new mechanism, assigns the ground-truth labels below, and
reports the comparison. That is three roles in one seat and it is exactly
the arrangement the base role distrusts. Two mitigations, neither complete:

1. The ground-truth labels are fixed in THIS commit, before any run.
2. The headline result does not rest on the labels at all. Test 2 below is
   a MECHANISM-level invariance test whose outcome does not depend on
   anyone's judgement of relevance, and Test 4 is an attack on the NEW
   mechanism that Eos predicts the new mechanism will FAIL.

A reader who distrusts the labels should read Tests 2 and 4 and ignore
Test 1.

## The populations

POP-A: THE HISTORICAL RECORD. The old scorer filled 42 ATTENTION REQUIRED
slots across the 8 archived digests, 2026-03-22..04-01
(roles/Eos/archive/digests_2026-03-22_2026-04-01/). Deduplicated by title
and URL those 42 slots carry 28 DISTINCT items -- the first measured fact
of this pass, recorded before any test: a third of the instrument's
attention output was the same items shown again. POP-A is those 28. These
are the old instrument's real decisions on real items, not a re-run;
eligible count 28 of 28.

POP-B: LIVE ITEMS. The 24 arXiv items returned by the 2026-09-11 probe
(roles/Eos/intake/probe_arxiv.json), two queries, unfiltered and
unselected: every item returned is in the population.

POP-C: CONSTRUCTED BAIT. 4 items written by this seat to be maximally
seductive to a Prometheus reader, marked provenance="constructed-bait" so
none can ever be mistaken for a real find. They carry no real URL.

POP-D: EOS-07 FIXTURES. Three constructed control items (negative,
positive, cheat) per the prediction already standing in
roles/Eos/CALIBRATION.md.

## The tests

### Test 1 (EOS-07): can the old scorer be killed by its own controls?

Fixtures, selected deterministically by the harness, not by hand:
  NEGATIVE  a real POP-B item a human judges irrelevant to every current
            lane.
  POSITIVE  a real POP-B item a human judges relevant to a NAMED current
            lane AND whose abstract contains no tier-1 substring.
  CHEAT     an item with no content: an abstract assembled only from the
            scorer's own tier-1 and tier-2 substring lists.

PREDICTION (restating CALIBRATION.md, unchanged): CHEAT scores at or above
the ATTENTION threshold for its kind and OUTRANKS POSITIVE; POSITIVE scores
at or below NEGATIVE, or within a few points of it.
FALSIFIED IF: POSITIVE outranks CHEAT. Then the scorer is better than this
seat believes and the result is reported as prominently as the other.

### Test 2 (the mechanism-level test, judgement-free): does the decision
depend on the state of the program?

Hold one item fixed. Evaluate it twice against two repository states that
differ only in whether the referent it names exists. Record both
mechanisms' outputs.

PREDICTION: the old score is IDENTICAL in both states (it is a pure
function of the item text and cannot read the repository); the gate's
verdict FLIPS. This is a structural claim about what each mechanism can
see, and no relevance label enters it.
FALSIFIED IF: the old score changes, or the gate's verdict does not.

### Test 3 (the typed intake): what do POP-A, POP-B and POP-C terminate as?

Every item gets an honest claim -- the best claim this seat can make for
it -- and goes through the gate. Refusals are kept with their reasons.

PREDICTIONS:
  3a  Of POP-A's 28 distinct historical ATTENTION items, AT MOST 2
      survive the gate.
      The old instrument's entire attention output is expected to be
      REFUSED almost in full.
  3b  All 4 POP-C bait items are REFUSED.
  3c  At least 1 and at most 7 POP-B items reach PENDING_ADMISSION. If the
      number is 0 that is a valid season and is reported as such, not
      repaired.
  3d  The single arXiv RESOURCE claim, backed by the probe's own
      measurement, terminates RESOURCE. A second RESOURCE claim backed
      only by a provider's documented free tier is REFUSED.
FALSIFIED IF: POP-A survivors exceed 2, or any bait item survives, or the
RESOURCE claim backed by documentation passes.

### Test 4 (the attack on the NEW mechanism): can the gate be fooled?

Pair a POP-C bait item with a REAL, resolving referent that has nothing to
do with it -- a genuine file and a genuine token in that file, chosen
because they exist, not because they are related.

PREDICTION: THE GATE PASSES IT. The gate verifies that a referent exists,
not that it is the right referent. Eos predicts its own new mechanism fails
this attack, and is publishing the prediction before running it so the
failure cannot later be presented as a known limitation that was always
understood.
FALSIFIED IF: the gate refuses it. Then the gate is stronger than its
author believes, and the reason is worth finding.

## Ground truth for POP-A, POP-B, POP-C (fixed here, before any run)

Rule used, applied uniformly: an item deserves to survive only if a
specific, currently-live object in this repository would be tested,
calibrated, corrected or extended by it, and that object can be named. Not
"is it good work" -- "does the program have a place that changes".

POP-A: all 28 REFUSED. Ground: every one was promoted under the retired
RPH premise; none names a currently-live object; 27 of the 42 are news
about a single MIT Technology Review story; the papers include one on
pavement skid resistance.

POP-B: labelled per item in roles/Eos/intake/sample_2026-09-11.json,
written in this same commit. Summary of the labels: 6 ANCHOR-candidate,
1 ACQUIRE-candidate, 17 REFUSED.

POP-C: all 4 REFUSED, by construction.

## What is NOT being claimed

- Not that the gate ranks items better. The gate does not rank.
- Not that the gate finds more. It is expected to find drastically less,
  and that is the intended direction.
- Not that a PENDING_ADMISSION item is a good item. It is an item a human
  now has to look at, which is the only thing this seat is allowed to
  produce.
- Not that any of this has been validated. One pass, one seat, one
  sample, self-labelled. A positive result here is provisional until an
  independent seat attacks it.
