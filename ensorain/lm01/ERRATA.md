# WTP-LM01 errata (NOT frozen; descriptive text only; no verdict rule is affected)

E-1 (2026-09-29; source: Artemis R-16, comms #882, verified by Ensorain against ensorain/lm01/dev/fixture_reservoir.json
at freeze ee8cbe0c8).
- The prereg v0.3.2 s12 inherits the v0.3.1 dev-findings list, which says both declared self-signal eviction rules LOSE
  to random on the eviction positive-control world. That was true under the pre-#677 fixture.
- The committed v0.3.2 fixture (after the one-ALS-convergence rule) shows random -0.126, keep_worst -0.182,
  residual_reservoir +0.023 (oracle +0.506, gap +.63). residual_reservoir BEATS random there; only keep_worst loses.
- The frozen s7 already states gap +.63. The v0.3.1 review packet (ensorain/LM01_PREREG_REVIEW_2026-09-26.md) quotes the
  old +.91 and "both lose"; that packet is superseded.
- Also noted (Artemis R-16, not yet independently checked):
  - residual_reservoir shows a noise-retention dose-response;
  - keep_worst acts partly as recency (FIFO beats it by ~0.7 AC on F3);
  - the fixture compares per-arm medians, not paired differences;
  - "random" eviction is distribution matching, not neutral, in non-stationary worlds.
  These are LM02 design inputs. The campaign's E6 reading (analysis.py) already uses paired CIs.
