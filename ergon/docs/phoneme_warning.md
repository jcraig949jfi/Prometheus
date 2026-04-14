# Phoneme Framework Warning

## Status: Unvalidated Construction

The "phoneme" framework in Harmonia (`harmonia/src/phonemes.py`) defines 5 universal
axes (complexity, rank, symmetry, arithmetic, spectral) and maps domain features
to these axes via `DOMAIN_PHONEME_MAP`. This was a constructed coordinate system,
not a discovered universal structure.

### What was killed

- **Megethos (complexity/magnitude axis)**: F35 kill. Log-conductor, discriminant,
  and similar size measures mediate spurious cross-domain correlations. This is the
  "complexity" phoneme — the first and most heavily weighted axis.
- **Universal laws**: 0 found across 21 datasets. The finding hierarchy shows only
  conditional laws and constraints.
- **Cross-domain transfer via phonemes**: Multiple kills (F33 ordinal alignment,
  F34 trivial baseline, F35 magnitude mediation) show that phoneme-mediated
  coupling is mostly artifact.

### What still uses it

- `harmonia/src/tensor_falsify.py` — `KosmosCoupling` (phoneme-based) is the
  default scorer for ALL falsification tests (F1, F2, F3, F8, F17)
- `test_phoneme_specificity` (F1b) — Tests whether coupling survives without
  the complexity phoneme. The test itself is valid but the framework it tests
  against is unvalidated.
- `harmonia/src/engine.py` — `phoneme` and `kosmos` are available scorer options

### Guidelines for Ergon

1. **Use `distributional` scorer, not `phoneme`/`kosmos`**, when bridging to Harmonia.
   The distributional scorer uses raw feature cosine + kurtosis weighting — no
   phoneme assumptions.
2. **Do not extend `DOMAIN_PHONEME_MAP`** for new domains. Adding phoneme mappings
   propagates an unvalidated framework.
3. **Read F1b verdicts with suspicion.** "SURVIVES phoneme specificity" means
   "coupling exists outside the complexity axis" — which is informative — but
   does not validate the phoneme framework itself.
4. **Documentation referencing phonemes, islands, Megethos/Arithmos axes as
   established fact is stale.** These were working hypotheses, not confirmed structure.

### The valid insight

The phoneme framework's *method* is sound — project heterogeneous domains into a
shared coordinate space and measure coupling there. The specific axes chosen
(complexity, rank, symmetry, arithmetic, spectral) are the part that wasn't
validated. A future coordinate system should be built from features that pass
the 5-gate admission test (null-calibrated, representation-stable, not reducible
to marginals, non-tautological, domain-agnostic).
