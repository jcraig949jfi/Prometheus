# Cartography -- Parallel Exploration Tracks
## Born from Charon's methodology, applied beyond number theory

---

## Structure

```
cartography/
  charon/          -> F:\Prometheus\charon (L-functions, existing)
  graph/           Track 1: LMFDB relationship graph analysis
  classify/        Track 2: Relationship type classification
  oeis/            Track 3a: OEIS sequence landscape
  mathlib/         Track 3b: Lean mathlib dependency graph
  atlas/           Track 3c: ATLAS finite group representations
  shared/          Cross-domain tools (landscape methods, stripping)
  convergence/     Cross-domain analysis (when baselines are established)
```

## Methodology (from Charon sprint, April 1-5 2026)

Every track follows the same protocol:
1. Ingest structured data with provenance
2. Compute invariants / feature vectors
3. Build landscape (geometric embedding or graph)
4. Strip confounders (normalization tests FIRST)
5. Read whatever structure survives stripping

### Phase 1 checks (before ANY interpretation):
- Mean-spacing / mean-centering normalization test
- Confound sweep (what single variable explains the effect?)
- Multiple representations (at least two metrics/methods)

### Done-done criteria:
- Measured under multiple normalizations
- Confounds eliminated or identified
- Kill tests documented
- Explanation quantitatively consistent
- Literature position established
- One-sentence statement without hedging

## Convergence Rules

Tracks operate independently until baselines are established with
precision. No cross-track analysis until each track has its own
done-done findings. Premature convergence is premature narration.

When tracks DO converge, the convergence point must be:
- Measurable (not metaphorical)
- Reproducible (not one-off)
- Survived stripping (not a shared confound)
