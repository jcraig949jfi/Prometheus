# Structure Hunter — Cheap-Path Tinker Lab

**Status:** playground-tier (`zoo/`). Verdicts here do NOT migrate to
the landscape tensor.
**Created:** 2026-04-25 — Harmonia_M2_sessionC.
**Companion to:** `harmonia/memory/architecture/conjecture_generator.md`
v0.3.1 + `docs/whitepaper_structure_hunter.md` v2.

## Discipline contract

This directory follows the same `zoo/`-tier discipline as
`zoo/experiments/` and the `TT_APPROX_MAP@v0` precedent:

- All work here is exploratory; failure is an acceptable outcome.
- Outputs do NOT migrate to mainline (no F-IDs, no P-IDs, no symbol
  promotions, no tensor cell mutations) without an explicit migration
  decision.
- Scoring shortcuts (e.g., synthetic data, abbreviated calibration
  batteries) are allowed.
- Findings interesting enough to reach mainline must be re-derived
  under full discipline before promotion.

## What's here

- **`synthetic_bsd.py`** — generates a synthetic rank-0 EC-like
  dataset where the BSD identity holds by construction. ~1000 rows.
- **`scorer.py`** — five-axis scorer (L_expr, |z_score| from
  correlation, basis_projection_score, affordance_gain,
  reconstructability). Linear-regression-only Layer B; kernel + MI
  deferred to v3.
- **`candidates.py`** — hand-crafted candidate library covering F043
  rearrangement family, mixed-basis candidates, and genuinely
  basis-independent candidates.
- **`tink_2.py`** — runs the scoring on all candidates, ranks by
  aggregate vs. Pareto-front, prints disagreement.
- **`results_2026-04-25.md`** — output and analysis from the first
  Tink 2 run (created on first run).

## How to run

```bash
cd zoo/conjecture_gp
python tink_2.py
```

No external dependencies beyond numpy + scipy + scikit-learn.

## Tink 2 thesis (whitepaper §10)

> Aggregate scalar (fit-dominated) rewards F043-shape candidates;
> Pareto-front on `(novelty, usefulness, faithfulness)` rejects them.
> The disagreement between the two rankings is the evidence that the
> seven-axis discipline does something a single scalar cannot.

If Tink 2 produces this disagreement, v2 architecture is empirically
validated and v3 roadmap (`conjecture_generator_v3_roadmap.md`)
becomes implementation-eligible. If not, v2 architecture resets to
critique.
