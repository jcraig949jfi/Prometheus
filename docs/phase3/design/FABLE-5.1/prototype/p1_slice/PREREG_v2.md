# P1 calibration slice prototype -- amendment v2 (after the v1 gate failed)

Architect: FABLE-5.1 (seat Dionysus). Written 2026-10-01 after the first run
of qualify.py and before any second run. Committed together with the v1
receipt and the amended code, before v2 is run. PREREG.md stays as it was.

## What happened in v1

qualify.py ran once at 2026-10-01T15:18:30Z, from the code committed in
f98efbc33. Its gate FAILED. The receipt is kept unchanged as
RECEIPT_qualify_v1_GATE_FAILED.json.

- Sections A, B, D, E and all seven fire tests matched the preregistered
  expectations.
- Section C did not. The interchange ruler on the negative control
  (the holder) was preregistered to return NO-EFFECT. It returned
  INDETERMINATE: the holder followed the donor's answer on 722 of 2,785
  eligible trials (0.259, chance is 0.25). That is not above chance, so it is
  not FLIP. But the rule for NO-EFFECT is "shown to be within 0.05 of chance
  at 1e-6", and 2,785 trials were not enough to show that: the exact tail was
  about 1.4e-6.

## Why it failed

The design was underpowered and I had not checked. I froze the verdict rules
and the sample sizes without computing the probability that each expected
verdict could be obtained. That is the failure that requirement MEAS-08 and
the base role's "compute the attainable range and the eligible count before
freezing any rule" exist to prevent, and I committed it in the prototype of my
own design.

Computed afterwards, exactly, for an organism at chance:

    cell                         eligible   probability of the expected verdict
    interchange NO-EFFECT          2,785     0.865
    HOLD FAIL                      2,879     0.884
    lesion FAIL                    3,670     0.978

Three kinds of cell were below 0.99. With two interchange cells, four HOLD
cells and one lesion cell depending on them, the v1 gate had roughly an even
chance of failing even if everything worked. It failed on one of them. The
others passed, and I do not count that as evidence of anything.

## What changes in v2, and what does not

Not changed: alpha (1e-6), delta (0.05), the minimum eligible count (200), the
expected verdict table, the world parameters, the organisms, the rulers'
decision rules. No threshold was moved toward the observed value.

Changed:

1. A power gate runs first. qualify.py now counts the eligible trials of every
   preregistered verdict from the schedules alone, before any organism runs,
   computes the exact probability of each expected verdict, and refuses to run
   if any is below 0.99. `python qualify.py --power-only` prints the table.
2. Sample sizes: 2,400 sealed lives for section A (was 1,200); 500 life pairs
   for interchange (was 250); 1,000 lives for lesions (was 500).
3. Fresh sealed lives. v2 reads lives from 6,000,000 upward. v1 read from
   1,000,000. No life is used by both.
4. One more fire test (FT8): the power gate is given v1's eligible counts and
   must call them underpowered.
5. Section B now uses its own block of lives. In v1 it shared lives with
   section A.

## The power table for v2

Output of `python qualify.py --power-only`, run before this file was
committed. It uses schedules and mappings only. No organism was run to
produce it.

    cell                                    eligible  expected  power
    A build builder(8), (6), (4), (2)         18,854  PASS      1.000000
    A build builder(0), holder, constant,
            lookup, leak_reader               18,854  FAIL      1.000000
    A hold  builder(8), (6), (4), (2), holder  5,829  PASS      1.000000
    A hold  builder(0), constant, lookup,
            leak_reader                        5,829  FAIL      0.999924
    C interchange builder(8)                   5,602  PASS      1.000000
    C interchange holder(8), builder sham      5,602  FAIL      0.999847
    C lesion used cells                        7,356  FAIL      0.999999
    C lesion unused cells                      7,356  PASS      1.000000

For the graded builders the count is treated as binomial at the designed rate.
The true count has a fixed part and a smaller variance, so this is
conservative.

## What v2 can and cannot show

If v2 passes, it shows the instrument sorts designed organisms as designed at
adequate power, on lives v1 never saw. It does not repair v1. Both receipts
are reported.

If v2 fails, the receipt says where, and the prototype is reported as having
failed twice.

reach.py has not been run and is not changed by this amendment.

> Annotation, 2026-10-01, after the v2 run. One number in the account of the
> v1 failure above is wrong. For 722 of 2,785 against 0.30 the exact lower
> tail is 1.09e-6, not "about 1.4e-6" (1.35e-6 is the value for 723). The
> verdict was INDETERMINATE at 1e-6 either way, and nothing in the amendment
> depends on the figure. Found by a consistency review that recomputed it;
> I then recomputed it with rulers.tail_le. The text above is left as it was
> preregistered.
