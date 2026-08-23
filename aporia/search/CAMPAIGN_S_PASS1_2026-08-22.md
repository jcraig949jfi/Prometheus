# CAMPAIGN S pass 1/3 — the Sleeping Beauty sweep opens. My handback was wrong.

## 0. Correction of record, first

`aporia/docs/HANDBACK_2026-08-22.md` claimed OEIS cross-reference data was not on disk and parked
this sweep on that basis. **It was wrong.** `cartography/oeis/data/oeis_crossrefs.jsonl` holds
**1,588,669 edges** and has since April.

The previous allocation pass listed as a stated weakness: *"I ruled the Sleeping Beauty set
unobtainable from two OEIS files without exhaustively searching the repository."* It named exactly
this as a falsifier. **The falsifier fired on the next pass.** I searched `prometheus_data/oeis/` and
concluded from two files what a repo-wide search answers in one command — the same shortcut, twice,
and the second time I had already written down that it was a shortcut.

The blocker was mine, not James's. Two of the three handback unblocks — the R12 budget word and the
reviewer seat — remain genuinely his.

## 1. The target set, derived and frozen

    corpus with >= 25 terms                     266,122
    crossref edges                            1,588,669
    distinct A-numbers touched by any edge       347,655
    ZERO-CONNECTIVITY with >= 25 terms            31,189   <- the sleeping beauties

Sequences nothing in OEIS points at and which point at nothing. Memory records the set as 68,770;
that is a **different population** predating the ≥25-term filter this line uses, and it is recorded
rather than reconciled silently.

**Matched control, built now so it cannot be chosen later:** 31,189 connected sequences matched on
exact term count, fixed seed 20260901. Mean terms **40.27 in both arms, zero unmatched**. Without it
a hit rate among sleeping beauties has nothing to be a rate *against*.

## 2. What makes this different from six campaigns of X-line work

**The measurement is exact, not statistical.** For each sleeping beauty `B`, the question is whether
some corpus sequence `A` and one of five operators satisfy `op(A) = B` over ≥ 20 terms. That either
holds or it does not. **One verified hit is a discovery; zero is a real null.** No representation, no
retrieval, no embedding — the X-line's machinery is not needed and is not used. This is the exact
search that was never run.

## 3. Preregistration — primary branches on the count

Scan all non-degenerate corpus sources × five operators (differences, partial sums, binomial
transform, Möbius transform, shift), recording every hit whose target lies in the SB set, verified
exactly over ≥ 20 terms. `shift` is the trivial control and is **counted separately**.

    S0 GATE (positive control).  The scan must recover known X-line benchmark pairs by the same
       code path. If it does not, the instrument is broken -> PARK, and no count is reported.
    S1 DISCOVERY   K_nonshift >= 1   at least one sleeping beauty has a verified NON-TRIVIAL
                                     relation to a known sequence. Catalogue every one.
    S2 SHIFT-ONLY  K_nonshift = 0, K_shift >= 1   hits are superficial; REDESIGN with a wider
                                     operator family.
    S3 KILL        K_nonshift = 0, K_shift = 0    these five operators do not connect the
                                     zero-connectivity set to the corpus. The "nobody looked with
                                     these operators" hypothesis dies for this family.

**Partition verified by enumeration:** 1,600 `(K_nonshift, K_shift)` points, **zero unmapped**,
coverage S1 1,560 · S2 39 · S3 1. Boundaries: `(0,0)→S3`, `(0,1)→S2`, `(1,0)→S1`, `(1,1)→S1`.

## 4. Preregistration — secondary comparison against the control

`D = R_sb − R_ctl`, hit rate in the sleeping beauties minus the matched control, two groups of
31,189. The base rate is unknown, so per the P125 doctrine the threshold is fixed as a **multiple of
the measured MDE** rather than an absolute number: **T = 2 × MDE, computed from the observed rate in
pass 2.**

    base rate   SE_diff    MDE (2 SE)
      0.005     0.00056      0.00113
      0.010     0.00080      0.00159
      0.050     0.00175      0.00349
      0.100     0.00240      0.00480

    D1  lo >  T    sleeping beauties are RICHER in findable relations than connected sequences
    D2  otherwise  comparable density — their isolation is BIBLIOGRAPHIC, not mathematical
    D3  hi < -T    genuinely poorer — they are isolated for a mathematical reason

**Partition verified by enumeration:** 5,151 `(lo, hi)` points, zero unmapped, coverage D3 1,128 ·
D2 2,895 · D1 1,128. **Verdict-rule null check:** under the null a CI centred on zero with
half-width below T fires **D2**, which is the correct null output and distinct from both finding
branches.

**D2 would be the most interesting outcome**, and it is the null branch — worth saying in advance so
it cannot be dressed up later. It would mean these sequences are unreferenced for reasons of
bibliography and attention rather than mathematics.

## 5. Cost and honesty notes

The scan is uncapped over ~230,694 non-degenerate sources × 5 operators, which is larger than any
X-line build (those broke early at a cap). If it does not complete inside one pass it checkpoints
rather than being silently truncated — a bounded scan reported as complete is the failure the
"no silent caps" rule names.

Stated in advance: a hit is a *verified exact relation*, not a claim that it is interesting or
unknown to mathematics. A sequence can be unreferenced in OEIS and still be a well-understood object.
Pass 3 adjudicates; pass 2 runs the scan and reports counts with the positive control.

## Campaign S pass 1/3; scan not run; checkpoint at pass 3
