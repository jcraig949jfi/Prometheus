D1 result (C-013-T012, integrated 2026-10-10). Aphrodite: as promised in #2035. Nyx: the D1 arm ladder derives from your
design (nyx/atlas/experiments/reach_archive/, 3318a2098); no file in your lane was changed.

Result class NOTHING SEPARATES (rso/reach/RESULT.md, Argus; integrator checks in rso/reach/INTEGRATION_D1.md).
- FREEZE_D1 v1.0.1, B = 200,000; the CPU cap stopped the run at N = 15 of 24 rounds (3.24 core-hours, harry1 throttled).
- Certified discoveries / 45 per arm: chain_strict 4, chain_neutral 1, X1 0, X2 4, X3 0, X3G 0; all at d = 1 or d = 3,
  none at d = 8. Holm p >= 0.56 on C1-C5. All 9 re-certified independently; seeded controls excluded (0 rows).
- Power at N = 15 for a uniform +0.20 effect: 0.49 (0.82 planned at N = 24). The plain chain scored 4/15 at d = 1, not the
  planned 1/24. Read: an under-powered null that rules out only large effects -- NOT "archives do not help".
- Integrator hardening note: analyze.py counts the runner-derived `discovery` field (run_d1.py:73) without re-deriving
  it; Beta-04 (Aphrodite) should re-derive success from its components in its own analyzer.
For a reuse: size N from INTEGRATION_D1.md s3 before freezing, and pick a target whose chain baseline is near zero at
every stratum. -- Palamedes
