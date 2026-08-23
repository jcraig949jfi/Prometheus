# CAMPAIGN T — one pass, TERMINAL: **ADVANCE** (T3). The candidate set survives its strongest check.

One-pass campaign, precedented by Campaign B (void audit, P107, complete in one pass). A campaign is
three passes *at most*, not at least, and this was a single decisive measurement on data in hand.

## Allocation, in one line

Three successors were on the table. **(a) strengthen the audit** won because it decides whether the
other two are worth doing: Campaign S's headline — 93.2% "genuine unstated" — was measured against
OEIS *titles only*, and its own terminal artifact recorded that as an **upper bound** because comment
and formula fields were not on disk. **They are.**
`cartography/oeis/data/oeis_formulas.jsonl` holds **523,463 formula lines**. Widening the operator
family (b) or fixing the connectivity definition (c) both produce *more* candidates; neither tells
you whether the candidates you have are worth a human's time.

*Third repo-search correction in three passes: the formulas were in the same directory as the
cross-references I also missed. I have now been wrong about what is on disk twice and right once,
after being told twice to search properly.*

## Pre-stated branches, committed in-script before computation

    T1 KILL-THE-SET   F >= 0.80   overwhelmingly rediscovery; the artifact is not worth triage.
                                  The METHOD claim survives untouched — this kills the list, not the sweep.
    T2 REDESIGN       0.30 <= F < 0.80   substantially contaminated; needs filtering first.
    T3 ADVANCE        F < 0.30    survives its strongest available check; worth triage.

`F` = fraction of the 259 distinct candidate targets whose relation to its partner is stated in an
OEIS **formula** field of either sequence.

**Partition verified by enumeration:** 1,001 points over F ∈ [0,1], zero unmapped, coverage
T3 300 · T2 500 · T1 201. Boundaries: `F=0.299 → T3`, `F=0.300 → T2`, `F=0.799 → T2`, `F=0.800 → T1`.

**On power, honestly:** this is a **census** of all 259 targets, not a sample, so there is no
sampling error and MDE is not the binding concept. Granularity is 1/259 = 0.0039, far finer than
either cut, so both are resolvable. The 0.30/0.80 thresholds are **materiality judgements** and are
labelled as such rather than dressed up as power-derived.

**Verdict-rule null check:** formulas stating nothing → F = 0 → T3; formulas stating everything →
F = 1 → T1. Extremes map to distinct branches; the rule discriminates.

**Detection bias declared before the number existed:** a relation counts as stated if *either*
partner's formula text names the other's A-number — any mention, not only a formula expressing this
operator. That is deliberately generous toward T1, so **F is an upper bound on statedness** and the
bias runs against the candidate set surviving.

## Result

    records: stated  11/633 = 0.0174
    targets: stated  11/259 = 0.0425      ->  T3 ADVANCE
    surviving: 248 distinct targets, 622 records

**Only 11 of 259 candidate relations are stated in a formula field.**

## The robustness check that mattered

**64.5% of the 259 targets have no formula entry at all** (92 have one, 167 do not). For those,
"not stated in a formula" is uninformative — there is no formula in which to state it. A headline F
computed over all 259 is therefore diluted by sequences the audit cannot speak to.

Recomputed on the **informative subpopulation** — the 183 targets where at least one partner *has* a
formula:

    F over ALL targets            11/259 = 0.0425   -> T3
    F over the INFORMATIVE subset 11/183 = 0.0601   -> T3

**Both readings fire the same branch.** Even where formulas exist, only 6% of these relations are
written in them. The verdict is robust to the coverage gap rather than resting on it.

## TERMINAL: ADVANCE — and what it now licenses

**248 distinct OEIS sequences carry a verified exact relation to a corpus sequence — holding over 20
to 45 terms — that is stated in neither sequence's title and in neither sequence's formula field.**

The claim is meaningfully stronger than Campaign S's, because the check that could most cheaply have
demolished it was run and it survived. What remains unchecked is narrower and named: **OEIS comment
and example fields are not on disk.** A relation stated in a comment would still count as unstated
here.

It remains a **candidate set for human triage**, not a set of discoveries. Nothing about "unwritten in
OEIS" implies "unknown to mathematics" — Campaign S's own top hit was a standard generating-function
identity, and that has not changed. What has changed is that the obvious cheap objection has been
tested and answered.

## The product

`aporia/search/sb_candidates_formula_survivors.jsonl` — **622 records over 248 distinct targets**,
each with both A-numbers and titles, operator, offset, exact term count, a plain-language claim,
provenance, and a status field naming exactly which OEIS fields were checked and which were not.

## Campaign T TERMINAL: ADVANCE
