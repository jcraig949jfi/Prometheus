# CYCLE 140-D — TERMINAL: KILL (pass 2 of 3)

**Question:** the exactly-verifiable operator vocabulary produced 220 atomic relations among OEIS
sequences. Does that same vocabulary produce ANY non-trivial exact relation among counting
sequences derived from LMFDB elliptic curves over Q?

**Answer: no.** H = 0 over 590 admissible triples, with the instrument verified working.

## Why this question and not another

Every prior test of the verbs thesis has lived inside OEIS — a corpus of integer sequences
curated *because* they are nice. If the operator vocabulary is a property of that curation rather
than of arithmetic, it will not reach objects catalogued for entirely different reasons. Elliptic
curves are such objects. This is the first test of the thesis outside the corpus that produced it.

It is also a deliberate correction of drift: three consecutive terminal states had been about
Aporia's own machinery rather than about mathematics.

## Setup

- **Objects:** elliptic curves over Q, LMFDB `ec_curvedata`, 3,824,372 rows.
- **Index (pass 2):** the *support* — the 13,205 conductors <= 20,000 carrying at least one curve.
- **Sequences:** 9 raw counting sequences (curves, isogeny classes, rank 0/1/2+, CM, semistable,
  trivial/non-trivial torsion) plus their 9 cumulatives = 18.
- **Operators:** 7 non-trivial (diff, partsum, binomial, moebius, inverse_binomial, second_diff,
  stirling2) as the headline; 5 trivial-class (shift, runmax, aerate, bisect_even, bisect_odd)
  reported separately and never in the headline, per P133.
- **Bar:** exact agreement over >= 20 consecutive terms, source passing the `nondeg()` guard
  reused verbatim from `campaign_v_widen.py`.
- **By-construction exclusions:** 18 triples, enumerated in advance.

## Pass 1 was VACUOUS, and it caught a defect in my own branch code

Indexing by conductor N = 1..10000 gave **0 of 18 sequences passing `nondeg`**, because the
smallest conductor of an elliptic curve over Q is **11** — terms 1-10 are structurally zero and
the 20-term guard window landed where the objects do not exist. Attainable triples: **0**. The
gate `H >= 1` sat outside the attainable range.

**The branch code routed that to KILL.** B1_VACUOUS as first written checked only the positive
controls, not attainability — so a forced zero would have been reported as a finding. This is
precisely the defect the P138 doctrine was written about, committed *one pass after writing it*.
The preregistration text was correct and explicit ("if too few sequences survive nondeg, the
reading is VACUOUS, not null"); the implementation did not match it. Corrected, and the
preregistration text treated as authoritative.

The risk was also recorded **before** the run: "zero-heavy sequences push the headline DOWN, i.e.
toward KILL — the direction that flatters a tidy result." It fired exactly as recorded.

## Pass 2 — the instrument re-aimed, and why that is not tuning

The single change was indexing over the support rather than over all N. It is forced by a
mathematical fact fixed before the data was seen (min conductor = 11) and is the standard
construction whenever a counting function is indexed by the objects that exist — as one indexes
by the n-th prime rather than by n. **No threshold, operator, exactness bar, guard, exclusion or
control was altered.**

    support: 13,205 conductors <= 20,000 carrying >=1 curve (min 11, max 19998)
    nondeg survivors: 5 of 18  (c_curves, c_classes, c_rank0, c_semistab, c_torsnont)
    POSITIVE CONTROLS: 9 of 9 firing, each exact over all 13,205 terms
    ATTAINABILITY: 5 sources x 17 targets x 7 ops - exclusions = 590 admissible triples
      gate H >= 1 inside attainable range [0, 590]?  TRUE
    NON-TRIVIAL exact relations: H = 0
    TRIVIAL-class relations:     0

**The instrument demonstrably detects relations it should detect** — all nine known-true
`partsum(r_X) = c_X` pairs fire, exact over the entire support. So H = 0 is a null, not a
non-measurement.

## The verdict, scoped to what was actually tested

**KILL** — for this operator family applied to LMFDB elliptic-curve counting sequences.

Explicitly **not** killed: the verbs thesis, and the 220 OEIS relations, which are separately
verified exact and stand on their own evidence.

## What the null does and does not license

It is worth being precise about how narrow this is. **13 of 18 sequences were rejected by the
degeneracy guard**, almost all because rank-1, rank-2+, CM and trivial-torsion counts are zero or
near-constant at small conductor. The test therefore covered **5 dense cumulative sequences**, not
"arithmetic objects" in general. A statement about 5 sequences is not a statement about a domain.

Against that: the exactness bar is 20 consecutive terms, where chance agreement between unrelated
integer sequences is negligible. So H = 0 is not a power problem in the usual sense — it says that
among these five, none is an exact operator image of another. That is a real mathematical fact
about the sequences tested, correctly scoped, and the claim strength is recorded as **supported**
rather than **certain** because the population is five.

## Self-identified weaknesses

- Five eligible sources is a small population, and four of the five are cumulative counts that are
  strictly increasing and highly correlated with one another — arguably the *least* likely place
  for a distinctive operator relation to appear.
- The degeneracy guard was calibrated on OEIS sequences and imported unchanged. It is the right
  guard for avoiding trivial matches, but it may be the wrong guard for sparse arithmetic counting
  functions, and it did 13 of the 18 rejections here.
- Only one object class was tested. The preregistered ADVANCE branch would have extended to
  `mf_newforms`; the KILL branch does not, so this says nothing about modular forms.
- Counting sequences are one representation of an elliptic curve among many. A null on this
  representation is not a null on the objects — a-invariants, L-function coefficients, and torsion
  structures were not tested and are the obvious next representations.
- Conductor <= 20,000 was chosen for compute, not for mathematics.

## Falsifier

A non-trivial exact operator relation between any two LMFDB-derived counting sequences at any
conductor bound; or evidence that the `nondeg` guard is rejecting sequences that do carry such
relations; or the same sweep on a different representation (L-function coefficients rather than
counts) producing hits, which would show the null belongs to the representation rather than the
vocabulary.

## Terminal

**CYCLE 140-D: KILL** at pass 2 of a permitted 3. Counting sequences are abandoned as the
representation for testing the verbs thesis against arithmetic objects. The next attempt, if any,
must change the *representation*, not extend this operator family — and per the preregistered
consequence, it does not proceed to a second object class.
