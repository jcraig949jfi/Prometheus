# CAMPAIGN X pass 2/3 — signature design + DEVELOPMENT retrieval

**Frozen split untouched.** The 50 frozen pairs were loaded only to be excluded. **No D1–D5
branch is adjudicated here** — those are read once, against frozen, in pass 3.
Scripts: `run_retrieval_dev.py`, `run_retrieval_dev2.py`. Results:
`retrieval_dev_results.json`, `retrieval_dev_supplement.json`.

## Two design decisions made before any number existed

**1. The pool of 358 was too small to mean anything.** Retrieving a target from 358 candidates
is not the task; the real corpus is 266,122. The pool was extended with **20,000 blinded
distractors** drawn from the corpus under the same non-degeneracy filter, keyed in a separate
id space (`D000123`) and never mapped back. This makes the test *harder*, touches no frozen
label, and is therefore legitimate mid-campaign. Final pool: **20,358**.

**2. The retrieval framing was underdetermined, and splitting it is the pass's main structural
move.** The standing prompt asked which framing is being tested. The honest answer is that
there are three, they test different claims, and reporting one number across them is how a
retrieval result gets over-read.

- **L0 — operator-aware exact.** Compute `op(A)`, hash-match it. **Circular by construction**:
  the benchmark pairs were *found* by exact hash matching, so this is ~100% by definition.
  Reported only to show the ceiling and prove the pool contains the targets.
- **L1 — operator-aware signature.** Compute `op(A)`, signature it, retrieve by distance.
  A **necessary condition**: can the signature identify a sequence it has literally been handed?
- **L2 — operator-agnostic.** Signature `A` itself; retrieve `B` with no operator known.
  **This is the substrate claim** — that behavioral representation places related objects near
  each other — and the only one that transfers to the Sleeping Beauties, where no operator exists
  to be applied.

Stated plainly: for a *known, finite* operator set, L0 is the correct production algorithm and
needs no signature at all. Signatures only earn their keep at L2.

## Signature (33 features, all from terms alone)

Growth class + fitted slopes (P21's battery, imported); log-ratio quantiles; sign density and
alternation rate; mod-p zero-density and residue entropy for p ∈ {2,3,5,7}; normalised
difference moments; leading-digit distribution. Committed in advance: only the scale-free
families (sign, mod-p, leading digit) have any prospect of surviving differencing or partial
summation.

## Development results — raw beside derived

Pool 20,358. 75 development positives. Chance top-10 = 10/20,358 = **0.00049**.

    L0 exact ceiling      75/75          (circular — sanity check only)
    L1 operator-aware     top1 0.747  top10 0.867  MRR 0.790  median rank 1
    L2 operator-agnostic  top1 0.000  top10 0.240  MRR 0.090  median rank 1,229
    baseline raw terms    top1 0.000  top10 0.160  MRR 0.062  median rank 1,392
    baseline shuffled     top1 0.000  top10 0.000  MRR 0.0005 median rank 11,990
    baseline growth/mag   top1 0.000  top10 0.053  MRR 0.031  median rank 631

The shuffled baseline at essentially zero is the pipeline's own negative control: nothing is
leaking through the harness.

## The L2 aggregate is inflated by its own control, and decomposing it is mandatory

`shift` was built in *deliberately* as the trivial control — `B` is `A` with one term removed, so
it is nearly the same object and any representation should find it.

    L2 shift (trivial control)   15 pairs   top10 0.800   median rank 3
    L2 four real operators       60 pairs   top10 0.100   median rank 2,502

**The entire aggregate 0.240 is the control.** Reporting it undecomposed would have been the
over-read this campaign exists to prevent. The real-operator number, 6 of 60, is ~200× chance and
so is not nothing — but it is not retrieval.

## Matched-negative false retrieval (head-to-head, immune to pool size)

Each positive's true target versus a decoy matched on growth class, magnitude and length:

    signature   21 / 74 decoys ranked above the true target   0.284
    raw terms   28 / 74                                        0.378
    chance                                                     0.500

The signature beats chance and beats raw terms, and errs on more than one pair in four.

## The finding that actually matters: the necessary condition fails first

**19 of 75 L1 queries missed.** Every L1 miss is a **signature collision** — the query sequence is
*exactly equal* to the target over ≥ 20 terms, and a distractor still ranks closer. Misses split
diff 2, partsum 2, binomial 3, moebius 3, shift 9, with median missed-rank ranging from 3 to 6,791.

This bounds everything downstream. **L2 cannot exceed L1**, and L1 is already losing a quarter of
the cases where the answer is handed to it. So the weak L2 result is confounded: it is consistent
with *both* "structural relations are not carried by this representation" *and* "this
33-dimensional representation cannot reliably tell two sequences apart." Those have opposite
consequences — the first kills the search, the second is an engineering problem — and the current
data does not separate them.

Instrument-first: the resolution of the instrument is the binding constraint, and it must be
measured before its verdict on the substrate is believed.

## Pre-committed supplement for pass 3 (written BEFORE frozen is touched)

D1–D5 stand exactly as preregistered and will be read first, unmodified. In addition, and
committed here so it cannot be fitted later, pass 3 will report the **L1 collision rate on the
frozen split** alongside the D-branch verdict, and:

- if frozen L1 ≥ 0.95 top-1, the L2 result is a clean read on the substrate claim;
- if frozen L1 mirrors development (~0.75), **any D4/D5 verdict is confounded by instrument
  resolution and must be stated as such rather than reported as a kill** — the campaign would then
  terminate REDESIGN (better representation, same frozen benchmark) rather than KILL.

## Campaign checkpoint

**Campaign X pass 2/3; frozen split untouched; checkpoint at pass 3.** No terminal state due.
