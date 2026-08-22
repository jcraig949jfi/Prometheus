# CAMPAIGN S pass 2/3 — the sweep ran. 301 sleeping beauties have verified non-trivial relations.

Branches S0–S3 and D1–D3 are FINAL and **not adjudicated here**. Pass 3 verifies pairs and reads them.

## S0 positive control — PASS

The sweep code path was pointed at 40 known verified pairs from Campaign W's benchmark and
**recovered 40 of 40**. An instrument that cannot find relations it is known to contain cannot report
their absence; this one can.

## The sweep — complete, not truncated

    non-degenerate sources scanned    230,694 / 230,694   (100.0%)
    elapsed                                          4 s

**No cap, no early break, no checkpoint needed.** Pass 1 disclosed this as an uncapped scan larger
than any X-line build and warned it might not finish in one pass. It finished in four seconds,
because only the first 13 image terms are needed for the hash lookup and the full image is computed
only on a hit — an exact optimisation that changes cost, not results. **My cost estimate was wrong by
orders of magnitude, in the conservative direction this time.**

## Counts, both arms

    arm                    raw hits   distinct targets   K_nonshift   K_shift_only
    sleeping beauties         2,431              433          301            132
    matched control           6,162            1,611        1,316            295

    per-operator distinct targets
    arm        binomial   diff   moebius   partsum   shift
    SB               70     99        36       129     176
    control         244    488       169       623     445

**301 of the 31,189 zero-connectivity sequences have a verified exact relation to a corpus sequence
under a non-trivial operator** — differences, partial sums, binomial transform or Möbius transform,
holding exactly over ≥ 20 terms. Every one is recorded as a checkable pair in
`sb_hits_ledger.jsonl` (8,593 records across both arms, with source A-number, target A-number,
operator, offset and exact term count).

**Held in advance and repeated here:** a hit is a *verified exact relation*, not a claim that it is
interesting or unknown to mathematics. An unreferenced sequence can still be a well-understood
object. Pass 3 checks that; this pass reports counts.

## The comparison, and a confound that changes what it means

    R_sb   433/31,189 = 0.013883
    R_ctl 1,611/31,189 = 0.051653
    D = -0.037770   95% CI [-0.040564, -0.034976]   SE 0.001426
    measured MDE (2 SE) = 0.002851   ->   preregistered T = 2 x MDE = 0.005702

The threshold was computed here from the measured variance, per the preregistration, not inherited.
`hi = -0.034976` sits far below `-T`, which points at **D3 — sleeping beauties are genuinely poorer in
findable relations** — and *not* at D2, the branch I flagged in pass 1 as the outcome I would most
want to report.

**But the control is compromised, and I am flagging it before adjudication rather than after.** The
control was matched on term count alone. A sequence is *connected* largely **because someone
documented a relation for it** — and an OEIS cross-reference frequently *is* the record of exactly
the kind of relation this scan searches for. The control arm is therefore enriched for findable
relations **by the very selection that defines it**.

This is the failure named in `feedback_control_must_break_the_selection_relation`: a control drawn
from the treatment's selection relation *is* the treatment. **D3 may be close to tautological** —
connected sequences have more findable relations partly because having a findable relation is what
got them cross-referenced.

**What survives the confound:** the primary branch. `K_nonshift = 301` is 301 regardless of what the
control does. The existence question does not depend on the comparison.

**What pass 3 must do about it:** read the primary branch on its own terms, and treat D3 as
uninterpretable unless a control can be built that breaks the selection relation — for example
matching on *keyword and term count among connected sequences whose cross-references are not
relation-bearing*. If no such control is available, the honest move is to report D as descriptive and
decline the D-branch entirely rather than fire a branch whose meaning is contaminated.

## Campaign S pass 2/3; scan run, complete, not truncated; checkpoint at pass 3
