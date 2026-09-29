# GO_FINAL addendum 6 (2026-09-29): SF2 ruling (bootstrap resampling scheme; affects MARKS only)
- **C7.4:** "decision statistics use a run-clustered bootstrap over the 9 distinct simulations".
- **Conforming scheme:** resample the 9 simulations with replacement, recompute each class over the loci of the drawn
  simulations, drop resamples where the class is empty, and report the drop count.
- s4 v2.2 resamples each class's OWN simulations. That conditions on class membership, so it is a deviation from C7.4.
- **RULING:** it affects only the MARGINAL/SINGLE_CLUSTER MARKS (C4.4: the gates use point estimates). Therefore:
  * no repair cycle;
  * the reviewed file is not edited;
  * the marks are reported with the note "per-class resampling (SF2), not C7.4-literal".
- The self class's upper bound (0.488) is near the floor. Its MARGINAL/not-MARGINAL mark is therefore UNSETTLED. Its gate is
  FAIL either way (point estimate 0.321).
- **SF1** (the superseded R-e/R-f docstring text): noted; it is superseded by V1/V4.
