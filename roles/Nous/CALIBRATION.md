# Nous -- calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. This seat's own wrong calls, kept because it is
unflattering (base role, section 2: "declare conflicts of interest and
keep a calibration ledger of your own past wrong calls"). Entries are
appended, never edited; a superseded line keeps its supersession marker.

Every entry below is a call THIS SEAT made, not one made about it.

---

L-01 | 2026-03-24 .. 2026-04-02 | THE CENTRAL ONE

CALL: that a model's rating of its own output, on a 1-10 scale appended
to the generation prompt, was a usable selection signal -- usable enough
to rank 10,105 combinations by, publish as `high_potential`, and hand
downstream as the forge queue's sort key.

OUTCOME: falsified by this seat on 2026-09-11 over its own committed
rows. The key is nearly constant (reasoning sd 0.532, 57.7% of rows on
the single value 7; five composite values cover 91.4% of the corpus) and
it cannot separate the scorer's own reject class at all (unproductive
6.4696 vs productive 6.4067, z = +1.28, permutation p = 0.308). See
ARCHAEOLOGY_2026-09-11.md section 4, M2 and M3.

WHAT WAS WRONG WITH THE REASONING: the seat never asked what the score
would look like if the channel carried nothing. It had no chance floor,
no eligible count, and no control of any kind -- the whole pipeline was
built on top of the number before anyone asked whether the number moved.
The tell was available from day one and free to read: a rating dimension
whose mode holds 55% of the mass is visible in the first thousand rows.

THE RULE THIS BUYS: never ship a score without its chance floor and
eligible count beside it, and never let one model both produce an
artifact and rate it. Both are written into RESPONSIBILITIES section 5
as things this seat never does.

---

L-02 | 2026-03-24 .. 2026-04-02

CALL: that `novelty` was a three-class label worth publishing.

OUTCOME: falsified. It returned `existing` 4 times in 5,918 committed
rows (0.07%) and `novel` 92.3% of the time. It was a near-constant
dressed as a classifier, with no control and no published base rate.

NOTE: this is the same failure family as the program's 2026-08-12 ruling
that closure-novelty was a timeout detector. Nous's version is earlier
and was never caught at the time. A seat that had asked "what fraction
of ANY input does this fire on" would have closed it in one query.

---

L-03 | 2026-03-25 .. 2026-09-11 (five and a half months standing)

CALL: that agents/nous/README.md described the instrument.

OUTCOME: it did not, and nobody read it against the artifact until
today. It states implementability carries weight +0.221 as the only
predictive dimension; the shipped Coeus artifact records -0.4670, the
opposite sign. It states "1,500+ evaluated combinations, roughly 20-30%
high potential"; measured on the committed corpus, 5,918 and 12.1%. See
ARCHAEOLOGY section 5.

THE RULE THIS BUYS: base rule 5 (currency is correctness) applies to a
seat's own README, and a documented number that cites an artifact is
checked against that artifact, not remembered.

---

L-04 | 2026-04-02 | THE SILENT DEATH

CALL: implicitly, that a hand-launched `--unlimited` loop with no
freshness record, no dormancy threshold and no alarm route was a
sufficient way to run a continuous generator.

OUTCOME: the loop died mid-API-call on 2026-04-02T12:43:31Z and NOBODY
NOTICED FOR 162 DAYS. Not the seat, not its consumer, not the program.
Its silence was observationally identical to its health -- exactly the
condition base rule 7 now names as a failed instrument.

NOT A DEFENCE, RECORDED ANYWAY: base rules 7, 8 and 9 did not exist in
April 2026; they were adopted 2026-09-11. The seat is not charged with
violating a rule that postdates it. It IS charged with the underlying
error, which was available to notice at the time: it built a loop whose
stopping it could not detect.

---

L-05 | 2026-09-11 | THIS PASS, WITHIN THE FIRST MINUTE

CALL: that the operator's instruction "Pull the latest from the repo
first" meant `git pull`.

OUTCOME: WRONG, and it is a D-23 violation. The working contract s3 is
explicit that a wake directive saying "pull the latest first" MEANS
fetch in the canonical checkout, record `git rev-parse origin/main`, and
`git worktree add` from that SHA -- and that a seat which pulls before
reading the contract has violated s1 and s3 without knowing. This seat
ran `git pull --ff-only` in the canonical checkout D:\Prometheus, twice,
before it had read the contract it was booting in order to adopt.

SCOPE, MEASURED NOT ASSUMED: `--ff-only` means no merge commit was
created and no content was written; the canonical checkout's main
advanced 577c21f16 -> 363120e08, which is a state another seat had
already pushed. No file was edited there and no branch was created
there. The damage is a mutating git operation in a read-mostly checkout,
not a lost tree.

WHY IT HAPPENED AND WHAT IT COST NOBODY BUT THIS SEAT: the seat executed
the operator's words before resolving the inheritance chain the same
operator's directive told it to adopt. The contract anticipated this
exact seat and this exact minute (Atalanta L-09 is the precedent, dated
the same day), and the seat still walked into it. The precedent existing
and the seat hitting it anyway is the finding: reading order is the
control, and "do the obvious first step" defeated it.

THE RULE THIS BUYS: the inheritance chain is resolved BEFORE the first
command of a pass, not before the first commit. An operator instruction
phrased in general terms is executed in the form the contract defines,
and when the two appear to differ the contract's form is the one that
was meant.

---

L-06 | 2026-09-11 | THIS PASS: MEASURED THE CHECKOUT, NOT THE REPOSITORY

CALL: that this seat's corpus was 10,105 rows, and -- on the strength of
that -- that a sibling seat's dated statement was wrong. An earlier draft
of ARCHAEOLOGY_2026-09-11.md carried 10,105 as the headline, derived
three instrument measurements from it, and filed a CORRECTION against
roles/Coeus/ARCHAEOLOGY_2026-09-11.md and the MONITORS.md
CoeusRebuildTrigger row, both of which say Nous last ran 2026-03-27.

OUTCOME: WRONG, and the sibling was right. The committed corpus is 5,918
rows ending 2026-03-27. The extra 4,187 rows are in no tree: .gitignore
kept them out (ARCHAEOLOGY section 2). Coeus had read the repository from
a worktree, correctly. This seat had read the canonical checkout's
working directory and mistaken one machine's disk for the program's
memory. The correction was withdrawn before it was sent, and no sibling
file was edited.

HOW IT WAS CAUGHT, which is the only good part: by this seat's own
validator, on its first run, because the script was committed to the
WORKTREE and the worktree does not contain the ignored files. The numbers
disagreed by 4,187 and `--check` exited 1. Had the audit been done only
where the data looked complete, the wrong number would have shipped with
a false correction attached to it.

THE RULE THIS BUYS: a number's tree is part of the number. Every figure
this seat publishes says which tree it came from, and a validator that
runs where the artifact lives is worth more than one that runs where the
data is convenient. It is the same error as L-05 in a different costume:
the checkout is not the repository.

---

L-07 | 2026-09-11 | THIS PASS: "VERIFIED" A GUARD BY RUNNING IT WRONG

CALL: that corpus_audit.py's D-23 guard worked, tested by running the
script from the canonical checkout and expecting a refusal.

OUTCOME: it exited 0, and the first reading of that was "the guard is
broken". Both the test and that reading were wrong: the script anchors to
its own file location, so running the WORKTREE's copy from a canonical
cwd correctly audits the worktree. The guard was never exercised. It was
then tested properly, by calling it against each root directly, and it
passes in both directions -- refuses the canonical checkout, accepts a
linked worktree (roles/Nous/science/test_guard.py, committed).

THE RULE THIS BUYS: a control that has never been observed firing is not
a control, and "I ran it and nothing happened" is a statement about the
test, not about the instrument. Base rule 3 is satisfied by a
demonstration of failure, not by an assertion of correctness -- which is
precisely the rule this seat's entire March instrument violated (M4: no
controls at all). Getting it wrong twice in one day, on the instrument
built to report that failure, is worth writing down.

## Standing conflicts of interest

- Nous is the seat whose instrument sections M1-M4 of the archaeology
  falsify. Those are self-measurements. They are all ADVERSE to this
  seat, which is the only class of finding a conflicted party may report
  (base role, section 2). Any favourable finding about Nous needs an
  independent lens and this seat will not produce one.
- Nous is one hop upstream of the Coeus MEASUREMENT_FAILURE dossier and
  supplied the concept dictionary and the sampler whose variable that
  dossier's descendant experiment would regress. This seat therefore
  proposes nothing about `coeus-d1-frozen-judge-structure-test` and does
  not ask to be part of it; it has posted the design input and stopped
  (ARCHAEOLOGY section 6).
