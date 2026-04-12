# State — 2026-04-12 Evening (Harmonia Session)

## What was built

Harmonia — tensor train exploration engine. Top-level directory `harmonia/`.

- 20 mathematical domains, 509K objects
- 4 coupling scorers (cosine, distributional, alignment, phoneme)
- Mathematical Phonemes: 5 universal coordinates (complexity, rank, symmetry, arithmetic, spectral)
- Tensor-speed falsification battery (6 tests in ~2s)
- MAP-Elites landscape explorer
- Known-truth calibration: 100% sensitivity, 75% accuracy

## Key findings

1. **Pairwise bonds:** 78/153 nonzero. NF<->EC rank 6 (strongest). 14 connected domains, 6 islands.
2. **Deep structure:** Every 4+ domain combination has rank >= 3. Saturates at mean 7.6 in layer 6.
3. **Meta-entanglement:** Battery and dissection strategies are entangled with object domains (rank 15).
4. **Validated inference:** SG <-> EC (symmetry = rank) passes 5/5 battery tests. Modularity rediscovered blind.
5. **Islands need work:** bianchi, groups, belyi, oeis, charon_landscape decouple — need richer features.

## Current precision tier

**Harmonia itself:** WORKING THEORY (battery-validated structure, calibrated against known truths, one clean 5/5 validation)

**Individual inferences:**
- SG <-> EC: VALIDATED (5/5)
- MF <-> Dirichlet, NF <-> Genus2: PROBABLE (4/5)
- Lattices <-> Dirichlet, Materials <-> EC: POSSIBLE (3/5)

## What's next

- Fix 6 island domains (richer features → phoneme alignment)
- Add phonemes 6-10 (periodicity, locality, genus, finiteness, duality)
- Per-phoneme null models for specificity
- Scorer ensemble (require multi-scorer agreement)
- Load high-precision Dirichlet zeros (184K objects)
- Integration with full battery (battery_unified.py)
