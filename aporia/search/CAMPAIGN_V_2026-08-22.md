# CAMPAIGN V — one pass, TERMINAL: **V1 KEEP**. And a triviality split the audit chain could not catch.

One-pass campaign, precedented by B, T and U. Branches committed in-script before computation.

## S0 per operator — 7 of 7 passed

Campaign S's S0 tested one code path. This tested seven: each new operator had to recover a synthetic
target built as `op(A)` and temporarily indexed, through the same probe path the sweep uses. **An
operator failing S0 would not have entered the sweep.** All seven passed 5/5.

    inverse_binomial · second_diff · stirling2 · bisect_even · bisect_odd · aerate · runmax

Rejected before testing: **partial products** (values explode past any plausible OEIS match while
costing the most per source) and **Dirichlet inverse** (needs a division that is not integral in
general, so "holds exactly" is not well defined).

## Result — and the number is not what it first looks like

    raw hits 6,603 -> 519 distinct targets
    after the SAME audit chain as the 203 (duplicate, title, formula, all-source population):
      5,188 clean records, N_new = 334 NEW distinct neglected targets  ->  V1 KEEP

**Partition verified by enumeration** over N_new 0–199: coverage V3 10 · V2 40 · V1 150, boundaries
`9→V3`, `10→V2`, `49→V2`, `50→V1`. Census, not a sample — the 10/50 cuts are **materiality
judgements**, labelled as such. Null check: new operators finding nothing → N_new = 0 → V3 WASH.

## The split the audit chain cannot see

    operator            new targets   class
    runmax                      152   TRIVIAL-CLASS
    bisect_even                  94   TRIVIAL-CLASS
    inverse_binomial             51   substantive
    bisect_odd                   45   TRIVIAL-CLASS
    second_diff                   7   substantive
    aerate                        3   TRIVIAL-CLASS
    stirling2                     0   substantive — contributed nothing

    TRIVIAL-CLASS  294        SUBSTANTIVE  58

**I promised new candidates would arrive at the same evidential standard as the 203. They pass the
same audit chain — but that chain tests whether a relation is *written down*, not whether the
*operator* is trivial, and those are different axes.**

`runmax` is idempotent and returns `A` unchanged for **any non-decreasing A**; the bisections are
pure subsequence extraction; `aerate` is pure zero-padding. These belong to the same class as
`shift`, which the original five already designated the trivial control and reported separately. I
added four more shift-equivalents and would have reported their yield as if it were comparable to
the binomial and Möbius transforms.

**The branch holds either way**: 58 substantive new targets still clears the V1 threshold of 50.
That is luck, not design — had `inverse_binomial` contributed 40 instead of 51, the headline
N_new = 334 would have fired V1 while the honest count fired V2.

**`stirling2` contributed zero.** An operator that passed its positive control and found nothing is
a clean negative: the Stirling transform does not connect this neglected population to the corpus at
20-term exactness.

## Consolidated product

`aporia/search/CANDIDATE_RELATIONS_CONSOLIDATED.jsonl` — **1,090 records over 544 distinct targets**,
superseding the three earlier candidate files. One file for a human to open, sorted by exact term
count, each row carrying both A-numbers with titles, operator, offset, exact term count, a
plain-language claim, provenance, and status naming which OEIS fields were checked under which
population definition.

**Read it with the operator column in view.** 294 of the 334 new targets arrive via trivial-class
operators and should be triaged after — or discarded before — the substantive ones. The original
five contributed 203 targets of which `shift` was already separated; the honest core of the
consolidated set is **the ~261 targets reached by non-trivial operators** (203 from the original
family plus 58 substantive new ones).

## Where the line stands

Four campaigns (S, T, U, V) have now tried to demolish or extend this result. It has survived a
formula audit, an all-source population correction, and a widened family — and this pass shows the
extension is smaller than its headline once operator triviality is accounted for.

Still unchecked and unchanged: **OEIS comment and example fields are not on disk**, and **unwritten in
OEIS does not mean unknown to mathematics**. No candidate has been read by anyone who knows the
literature, which remains the only decisive check and the one thing this loop cannot perform.

## Campaign V TERMINAL: V1 KEEP
