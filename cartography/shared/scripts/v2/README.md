# Charon v2 — Depth Layer

## Why v2?

v1 (the 67 scripts in the parent directory) built the scalar layer:
- 21 datasets, 56 search functions, 39K concepts, 1.91M links
- Shadow tensor, MAP-Elites, explorer loop, 14-test battery
- Constant telescope, term factory, geometric probes

**v1's definitive finding:** After prime detrending, the scalar layer is empty.
Zero cross-dataset signal in conductors, determinants, discriminants, group counts.
96% of all apparent structure was shared prime factorization.

v2 targets the **depth layer** — data that primes can't pollute:
- Polynomial coefficient PATTERNS (not values)
- Formula function REFERENCES (semantic, not numerical)
- Symbol CO-OCCURRENCES (structural, not scalar)
- Sequence-to-sequence comparisons at matched objects

## Structure

```
v2/
  extractors/         — Pull depth features from existing data
    depth_extractor   — EC coefficients, knot polynomials, OEIS formulas, Fungrim symbols
                        26K concepts, 984K links from data already downloaded
  
  probes/             — Test cross-dataset depth bridges
    depth_probes      — Matched-object coefficient correlation (Alexander vs a_p)
    microscope        — Prime detrending + small-int filtering
    geometric_probes  — 13 structural tests (curvature, FFT, MI, Wasserstein, etc.)
  
  tensors/            — Build tensors on depth features  
    detrended_tensor  — SVD on prime-detrended residuals
    depth_tensor      — SVD on depth concepts (TODO)
```

## Key Files (still in parent v1 directory, working)

These Phase 2 scripts live in the v1 directory because the running terminals depend on that path:
- `depth_extractor.py` — 26K concepts, 984K links (7s)
- `depth_probes.py` — matched-object coefficient probes
- `microscope.py` — 3-layer prime decontamination
- `detrended_tensor.py` — parallel concept layer without primes
- `geometric_probes.py` — 13 structural probes
- `geometric_survey.py` — full survey runner
- `constant_telescope.py` — sleeper constant matching (39 constants × 68K)
- `growth_constant_scanner.py` — high-precision constant ID
- `term_extender.py` — OEIS term factory (22K terms produced)
- `reevaluator.py` — retest killed hypotheses on clean data

## What v1 Still Does

The 8 terminals + explorer loop run v1 scripts continuously:
- `research_cycle.py` — LLM-driven hypothesis generation
- `falsification_battery.py` — 14-test kill battery
- `search_engine.py` — 21 datasets, 56 searches
- `concept_index.py` — noun + verb concept extraction
- `shadow_tensor.py` — dark matter map (101K+ records)
- `explorer_loop.py` — zero-cost void scanner + bridge hunter + MAP-Elites

v1 generates hypotheses and fills the shadow tensor.
v2 analyzes the depth layer where the real bridges might live.

## The Honest Score

- Novel discoveries: **zero**
- Scalar layer: **empty** after prime detrending
- Depth layer: **26K concepts, 984K links** extracted, **first branch tested (null)**
- Remaining branches: Jones polynomials, L-function Euler factors, OEIS formula semantics
- OEIS contributions: **22,338 new terms** queued for submission
- Kills: **8** in one session, each improving the pipeline
- Key insight: mathematical function semantics (zeta, gamma, Dirichlet) bridge OEIS↔Fungrim
  at 16,774 sequences — structural, not numerical, immune to prime detrending
