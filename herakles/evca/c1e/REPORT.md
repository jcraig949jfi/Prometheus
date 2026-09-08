# WP-C1-e: historical reproduction. Qualification report.

**Herakles, 2026-09-08.** Protocol frozen and committed BEFORE the run in
`PROTOCOL.md` (commit `0e6b9e812`). Nothing in the decision rule was changed
after any number was seen. Raw results in `c1e_results.json`; the run took
906.5 s.

**This is a qualification result, not a CI gate.** Deterministic fidelity was
established separately in WP-C1 and is not restated here.

---

## 1. Result

    REPRODUCED   17 of 18 cells
    DISCREPANT    1 of 18   particle2 at N = 149

At N = 599 and N = 999 every cell reproduced. The single discrepancy is at the
smallest lattice.

    rule        N=149            N=599            N=999
                pub    meas  se  pub    meas  se  pub    meas  se
    ---------   -----  ----- --- -----  ----- --- -----  ----- ---
    maj         0.000  0.000 n/a 0.000  0.000 n/a 0.000  0.000 n/a
    exp         0.652  0.654 0.4 0.515  0.523 1.0 0.503  0.514 0.9
    par         0.769  0.771 0.4 0.725  0.724 0.2 0.714  0.717 0.3
    particle1   0.742  0.754 2.8 0.718  0.726 1.1 0.701  0.693 0.8
    particle2   0.755  0.733 5.0 0.696  0.713 2.4 0.670  0.683 1.2
    GKL         0.816  0.815 0.4 0.766  0.777 1.6 0.757  0.749 0.9

`se` is the absolute difference in standard errors. The band is 2.9912 SE
(Bonferroni, 18 cells, family-wise 0.05). Cells at or below 2.99 reproduce.

**The three `maj` cells reproduced EXACTLY**, zero correct classifications out
of 10000, 4000 and 2000 initial conditions. They were decided by the exact
rule the protocol prespecified for a published 0.000, not by a proportion
test, because a binomial band at zero has zero width.

## 2. A prior flag that did NOT survive

The recovery record flagged `exp` as measuring about 0.664 against a published
0.652, roughly 2.5 standard errors, and named a relaxation-steps convention as
the suspected cause. Under this protocol `exp` measures 0.6538 at N = 149,
0.38 SE from published, and reproduces at all three lattice sizes. A second
independent sample in the sensitivity arm gave 0.6465, also inside the band.

**The `exp` discrepancy does not replicate.** The earlier figure is most
consistent with a smaller sample. This is recorded because a flagged anomaly
that quietly disappears is worth as much as one that persists.

## 3. The one discrepancy, and the suspect walk

`particle2` at N = 149: published 0.755, measured 0.733, difference -0.0220,
4.97 SE, band 0.0132.

**First, is it a sampling fluke?** No. Five independent samples of 10000 ICs
each give 0.7373, 0.7422, 0.7383, 0.7417, 0.7441: mean 0.7407, standard
deviation 0.0025. The gap to published is stable and about six times the
spread of the sample mean.

Suspects were checked in the order the protocol fixed, before any of them was
known to matter.

**Suspect 1, update count. ELIMINATED.** The sensitivity sweep at N = 149 gives
particle2 0.5012 at 149 steps and then 0.7382 at 298, 596 and 1192 steps,
identical to four decimal places. The measurement is converged well before the
horizon used, and a longer horizon cannot close a gap it has already stopped
moving on.

**Suspect 2, accuracy definition. ELIMINATED.** "State at T" and "ever reached
by T" differ only if a uniform configuration is not a fixed point. All six
rules fix both uniform configurations, verified per rule and recorded in every
result row. The two definitions coincide here.

**Suspect 3, IC ensemble. ELIMINATED, and informatively.** Under a
uniform-over-density ensemble instead of unbiased iid, every rule rises
sharply and `maj` rises from 0.000 to 0.443:

    rule        published   iid uniform   uniform-density
    ---------   ---------   -----------   ---------------
    maj             0.000        0.0000            0.4427
    exp             0.652        0.6402            0.9333
    par             0.769        0.7688            0.9718
    particle1       0.742        0.7398            0.9640
    particle2       0.755        0.7373            0.9620
    GKL             0.816        0.8074            0.9790

The published figures track the unbiased ensemble closely for five of six
rules and are nowhere near the alternative. So the ensemble is confirmed as
correct, and it cannot be the explanation for one rule when it fits the other
five.

**Suspect 5, implementation. ELIMINATED for this rule at full scale.** The
library was compared against the independent naive oracle for particle2 at
N = 149 over the full 298 steps on three initial conditions: identical cell by
cell. This is stronger than the C1-a oracle test, which runs at N up to 21 for
5 steps.

**Suspect 4, transcription. SURVIVES. It is the only one left.**

I cannot test it. Doing so would require the original EvEmComp table bytes,
and the specimen holds a PDF rendering, not the source. What can be said:

- `particle1` and `particle2` are the ONLY two rules whose source is EvEmComp
  Table 1 alone. They appear in neither the review nor the PPSN III paper.
  The other four are corroborated by at least two sources, or derivable from
  a definition.
- They are also the two largest deviations at N = 149: 2.83 SE and 4.97 SE,
  against 0.4, 0.4, 0.4 for the corroborated rules.
- **Against the transcription story:** the two deviations have OPPOSITE signs,
  particle1 above published and particle2 below. A systematic transcription
  fault would not do that. A per-rule fault could.
- Both deviations shrink at larger N, which a wrong rule table would not be
  expected to do.

So this is a LEAD with two observations for it and two against. Two rules is
not a sample. I am not claiming a transcription error.

## 4. What I deliberately did not do

I did not search the space of single-digit variants of `particle2`'s hex for
one that scores 0.755. There are 480 such variants and a standard error of
0.0044, so several would land near the published value by chance alone.
Finding one and reporting it as the recovered transcription would be fitting
to the target: the multiple-comparisons version of moving the tolerance after
looking. If the original bytes are ever recovered, the comparison becomes
legitimate and cheap.

## 5. Limits on what this licenses

- **Reproduction is demonstrated for this ensemble, these three lattice sizes
  and this horizon.** Nothing here licenses a claim at other densities, other
  N, or under a different update convention.
- **The band is tighter than the comparison deserves**, as declared in the
  protocol before the run. It carries only my sampling error; the published
  figures have no stated uncertainty and were themselves estimated. If the
  original samples were comparable, the correct band is roughly sqrt(2) wider,
  under which particle2's gap is 3.5 SE rather than 5.0 and would sit closer
  to the boundary. It would still fall outside. This is stated because a
  reader is entitled to know the test was set up to find discrepancies.
- **17 of 18 is not a validation of the library.** It is a validation of the
  library against these printed numbers. The deterministic fidelity result in
  WP-C1 is the separate and stronger claim.
- `maj` reproducing at exactly zero is the strongest single cell here, because
  it is an exact prediction with no tolerance at all, and it held at three
  lattice sizes over 16000 initial conditions.

## 6. Reproduction

    cd F:/Prometheus
    python -m herakles.evca.c1e.run_c1e        # 906 s, writes c1e_results.json

Seeds are derived as `20260908 + 1000 * lattice_index + rule_index`, recorded
per cell in the results file. The sensitivity arm uses seed `20260908 + 777`
and 4000 ICs.
