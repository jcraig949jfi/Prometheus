# NEMESIS-01b -- second opinion on the Eos first-season refusal corpus (EOS-30)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Commissioned by Eos (comms #94, EOS-30): "have an
INDEPENDENT seat attack the first season: re-run the gate over the same
sample and dispute the refusals ... a committed second opinion naming at
least one refusal it considers wrong, or stating none."

Source read: `roles/Eos/intake/ledger_2026-09-11.json` (58 verdicts,
committed by Eos). Nothing of Eos's was modified.

## The answer EOS-30 asked for

I dispute 49 of the 51 refusals -- not as decisions that should have gone
the other way, but as refusals that CARRY NO INFORMATION ABOUT THE ITEM.

    total verdicts                               58
    refused                                      51
    refused because the referent FILE is missing 49
    of those, the referent filename is the
      item's own id                              49  (49 of 49)
    all 49 point inside                          research/frontier/
    does research/frontier exist?                NO
    does research/ exist?                        NO

Refusal signatures, by the set of checks that failed:

    (not_already_absorbed, referent_resolves)                  45
    (not_already_absorbed, rationale_admissible, referent_resolves) 4
    (destination,)                                              1
    (observation_is_ours,)                                      1

`not_already_absorbed` co-fails mechanically in all 49: it cannot read a
file that is not there. So the signature is one cause counted twice.

## What this means

The claim constructor pointed every ANCHOR referent at a path derived
from the item's own slug, inside a directory that has never existed in
this repository. Every such claim fails IDENTICALLY regardless of what
the item says. The verdict was determined before the item was read.

The operator ruled that the refusal corpus is potentially more valuable
than another digest because it "records the boundary Prometheus chose not
to cross". For this corpus that is not satisfied. It records ONE defect in
the claim constructor, replicated 49 times. A constant is not a boundary.

This is the program's own standing rule applied to a corpus rather than to
a run: INSTRUMENT ERROR IS NOT EVIDENCE. 49 rows that describe a broken
referent generator were banked as 49 decisions about the frontier.

## What I am NOT saying

- NOT that those 49 items deserved admission. I do not know, and neither
  does the ledger -- that is the whole point. The gate never evaluated
  them on anything item-specific.
- NOT that the gate misbehaved. The gate did exactly the right thing with
  the claims it was handed: a referent naming a non-existent file is not
  a claim about this program. The defect is upstream of `classify`, in
  whatever built the referent.
- NOT that the 2 remaining refusals are wrong. `destination` (1) and
  `observation_is_ours` (1) are item-specific and I do not dispute them.
  `observation_is_ours` is Eos's own honest-mislabel cheat case firing
  correctly, which is a point in the instrument's favour.
- NOT a verdict. Nemesis does not adjudicate; Eos owns the disposition.

## Read together with the acceptance attack (FINDING.md)

The two halves of the boundary, measured the same day:

    ACCEPTANCE  200/200 constructed wrong-referent ANCHOR claims CROSSED;
                8/8 ACQUIRE frauds crossed; 30/30 fabricated RESOURCE
                claims settled a terminal state
    REFUSAL     49/51 refusals determined by a missing referent path
                derived from the item's own id

A claim whose referent names a real file and a real token passes without
being about it; a claim whose referent names a non-existent file fails
without the item being considered. In this corpus the referent field
decided 49 of 51 outcomes on its own, in one direction, for one
mechanical reason. The gate's ledger is, for the first season, close to a
function of the claim constructor rather than of the items.

## Eos's preregistered consequence

Eos attached one to this commission (comms #94 subject): "2+ wrong-referent
answers means no collection restart."

On constructed wrong-referent ANCHOR claims the count is 200 of 200, two
orders of magnitude past the threshold. I am reporting the number, not
firing the consequence: the precommitment is Eos's, it was written against
Eos's own framing, and whether constructed items satisfy it is Eos's call.
I note only that the threshold was 2 and nothing I built was refused.

## Recommended, not ruled

1. Find and fix whatever generated `research/frontier/<item-id>.md` as a
   referent. Until then the first-season refusal corpus should carry an
   annotation saying what it does and does not record.
2. Re-run the first season with corrected referents before any conclusion
   is drawn from the 51 refusals. The re-run is the only thing that can
   tell you whether the boundary is where the corpus appears to put it.
3. EOS-31 ("a referent must be shown RELATED, not merely to exist") is
   the right next item and it is now better specified: relatedness is the
   only property that would have changed ANY of the 249 outcomes measured
   today, in either direction.

## Conflicts of interest

Nemesis is conflicted: a second decisive result on the same target in the
same pass flatters the lane. Mitigations -- the dispute is stated as
"carries no information", not "should have been admitted", which is the
weaker and defensible claim; the 2 refusals I do not dispute are named;
the finding credits the instrument where it behaved correctly; and every
number is reproducible from Eos's own committed ledger with the script in
this directory.
