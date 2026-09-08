# WP-C1-e protocol: historical reproduction, prespecified

**Written and committed BEFORE the run. Nothing below may move afterwards.**
Herakles, 2026-09-08. Library at `herakles/evca/`, tests green at 50/50.

This is a QUALIFICATION report, not a CI gate. Its output is a statement
about whether this implementation, under the source's conventions, produces
the figures the sources printed. A failure here is a lead to diagnose, not a
broken build.

---

## 1. What is being compared

The six recovered genomes against the performance figures printed in the EvCA
review Table 1 and EvEmComp Table 1, at three lattice sizes: N = 149, 599,
999. Eighteen cells.

The published numbers are in `herakles/evca/genomes.py` under `published_P`
and are asserted against the specimen record by an existing test.

## 2. Conventions used for the primary run

Fixed here, from the source convention rather than from convenience.

    lattice            N = 149, 599, 999, ring, periodic
    neighbourhood      r = 3, leftmost neighbour as MSB
    update             synchronous, all cells
    UPDATE COUNT       steps = 2N, i.e. 298, 1198, 1998
    initial conditions each cell iid uniform, the unbiased ensemble
    accuracy           fraction of ICs in the correct uniform configuration
                       after `steps` updates
    seed               20260908, one generator per (rule, N) cell, derived as
                       seed = 20260908 + 1000 * lattice_index + rule_index

`steps = 2N` is the source's stated convention ("a maximum of about 2N time
steps"). The recovery verifier used 300 / 1200 / 2000, which is close but not
identical. That difference is one of the named suspects for the known `exp`
discrepancy, and it is addressed in the sensitivity arm below rather than by
choosing whichever value agrees better.

## 3. IC sample sizes, and why they differ by lattice

Chosen from a measured throughput of about 5e7 cell-updates per second, to
keep the whole run inside roughly twenty minutes.

    N      n_ics    cell-updates    binomial SE at p = 0.75
    ---    ------   -------------   -----------------------
    149    10000        4.5e8              0.0043
    599     4000        2.9e9              0.0068
    999     2000        4.0e9              0.0097

## 4. Uncertainty and multiplicity rule, prespecified

- **Uncertainty.** Accuracy is a binomial proportion over independent ICs.
  Standard error is `sqrt(p_hat * (1 - p_hat) / n_ics)`, computed from the
  observed proportion in that cell.
- **Multiplicity.** Eighteen cells are compared. Bonferroni correction at a
  family-wise level of 0.05 gives a per-cell two-sided level of
  `0.05 / 18 = 0.002778`, hence `z = 2.9912`.
- **Decision per cell.** REPRODUCED if
  `|measured - published| <= z * SE`, otherwise DISCREPANT.
- **Band half-widths implied**, at p = 0.75:
  N = 149 about 0.013, N = 599 about 0.020, N = 999 about 0.029.

**A declared conservatism.** The published figures carry NO stated
uncertainty in the specimen record, so this band accounts only for OUR
sampling error. The true comparison band should also carry the original
authors' sampling error, which would widen it by roughly a factor of
sqrt(2) if their sample was comparable. Our band is therefore TIGHTER than
the correct one, which biases this test toward declaring discrepancies.

**Consequence, stated in advance:** a DISCREPANT cell here is a LEAD, not a
finding of error in either the implementation or the source. A REPRODUCED
cell is the stronger statement, because it survives a band narrower than the
one the comparison deserves.

## 5. The sensitivity arm, and what it may and may not decide

`maj` is published at 0.000 for all three lattice sizes and is a degenerate
cell for a proportion test: p_hat = 0 gives SE = 0 and a band of zero width,
so any non-zero measurement is automatically DISCREPANT. This is stated now
rather than discovered later. For the three `maj` cells the decision rule is
replaced by an exact one: REPRODUCED if the measured count of correct ICs is
zero, otherwise the count is reported as-is with no test.

Separately, one diagnostic sweep at N = 149 only, over
`steps` in 149, 298, 596, 1192, for all six rules. Its purpose is to measure
how sensitive accuracy is to the horizon, because update count is the leading
suspect for the known `exp` difference of about 0.012.

**This sweep cannot change any REPRODUCED or DISCREPANT decision.** It is
reported beside them as diagnosis. Selecting the horizon that best matches
the published figure and then reporting that match would be moving the
tolerance after looking, which is the one thing this protocol exists to
prevent.

## 6. Named suspects for any discrepancy, listed before the run

In the order they will be checked, so the order is not chosen to suit the
result:

1. **Update count.** 2N versus the recovery's 300 / 1200 / 2000, and whether
   the source counted the initial configuration as an update.
2. **Accuracy definition.** State at T versus ever-reached by T. These differ
   unless both uniform configurations are fixed points; the library reports
   that per rule, and it will be recorded per cell.
3. **IC ensemble.** Unbiased iid uniform versus uniform over densities. These
   are different distributions and the second is also used in the literature.
4. **Transcription.** The two recorded recovery hazards, row pairing and the
   broken ligature map. Both produce plausible wrong tables.
5. **Implementation.** Covered by the independent oracle in C1-a, so this is
   the least likely and is checked last rather than first.

## 7. What this report will contain

Per cell: published, measured, n_ics, SE, band, decision, and the
uniform-fixed-point facts for that rule. Plus the sensitivity sweep, the
suspect walk-through for any DISCREPANT cell, and the exact command and
seeds to replay it.

## 8. What it will NOT contain

- No tolerance chosen after inspection.
- No horizon selected because it matched.
- No claim that a REPRODUCED cell validates the library beyond this ensemble,
  these lattice sizes and this horizon.
