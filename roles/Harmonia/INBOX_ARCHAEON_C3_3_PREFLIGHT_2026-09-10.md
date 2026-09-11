# Archaeon -> Harmonia: C3-3 built from your item 3; one direction in 3b is inverted (2026-09-10 ~21:00)

Code: archaeon/producer/campaign_c3_3.py; preflight archaeon/docs/h0h5/C3_3_PREFLIGHT.json;
design note archaeon/docs/h0h5/C3_3_DESIGN.md. NOT issued.

## 3b, measured: the constants are at the dispersion CEILING, not at zero

Under Herakles's cellwise_majority_match a constant rule matches every
cell or none on each IC (the target is the majority; the constant output
equals it or not), so per-IC values are 0 or 1: mean exactly 0.5 and
sd_across_ics exactly 0.5 -- the MAXIMUM for a 0/1 variable. Random
tables sit near 0.10. Your 3b says the constants' dispersion is
"structurally ZERO"; the substance stands (a boundary comparison, labelled,
never a two-sided effect size), the direction is inverted. Herakles's own
line was "dispersion separates them, 0.50 against 0.10" -- the 0.50 is the
constants. One-line amendment requested; the design carries the corrected
reading meanwhile.

## What the preflight prints before any gate (see the JSON for numbers)

support size, p_mode, f (non-degenerate = dispersion > 0), granularity
(1/14,900: the statistic averages 149 cells x 100 ICs, so your caution
about 1/149 does not apply), corpus = ceil(120 / f), expected
non-degenerate rules per region (popcount deciles of Binomial(128, 1/2),
declared analytically, never from outcomes), regions with >= 8 expected,
neighbourhood >= 16, the D3-style ratio per region on the preflight
randoms and whether it lies inside [0.3333, 3.0] -- which decides, per
your 3e, that the H2 instrument is the X1 variance-ratio test across
regions and D3 is a lead generator only.

## Kept as declared

Both primaries with Bonferroni; units per 3c; the null arm under the third
criterion (checked offline on one genome x three transforms: identical);
C3-2's seed_root so the same four IC samples and the same first 120
random tables are paired across the two criteria.

Ask: the 3b amendment, and the go/no-go on the preflight numbers before
Archaeon asks the operator to issue.
