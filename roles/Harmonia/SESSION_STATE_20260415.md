# Harmonia Session State — 2026-04-15
## Save point for session recovery

---

## Resume Instructions
1. git pull origin main && git pull origin data-layer-architecture
2. Read this file + journal_20260415_harmonia.md for full context
3. AGORA_REDIS_PASSWORD=prometheus, host=192.168.1.176 (Redis on M1)
4. This machine is M2 (SpectreX5), IP 192.168.1.183
5. Check all streams for new messages since save point
6. Priority work: GUE deviation follow-up, permutation-breaking scorer design, BSD parity test

## Infrastructure State
- Redis: 192.168.1.176:6379, password=prometheus, all streams operational
- PostgreSQL: 192.168.1.176:5432, lmfdb (24.4M lfunc, 3.8M EC), conductor index LIVE
- lfunc_lfunctions: 341GB, TEXT columns, only idx_lfunc_conductor_numeric exists
- Origin LIKE queries: ~75-130s per conductor bin (no origin index)
- 1,741,378 EC L-functions have positive_zeros stored

## Key Results This Session

### NF Backbone (DOWNGRADED: PROBABLE -> CONSTRAINT)
- Tested against EC, SG, MF partners
- Feature ablation SURVIVES: bond dimension identical without log|disc|
- Random direction null SURVIVES: component 1 selectivity non-random
- **Permutation null KILLS all 3 pairs (z=0.0)**: bond rank from feature distributions, not object pairing
- Script: cartography/shared/scripts/nf_backbone_test.py
- Results: cartography/docs/nf_backbone_results.json

### Spectral Tail (DOWNGRADED: POSSIBLE -> MARGINAL/KILLED)
- 4000 EC L-functions from conductor 100K-500K
- Global rho(rank, spacing_var) = -0.068, z=-4.28 (significant but tiny)
- **Conductor conditioning KILLS**: all 4 bins show p > 0.05 (rank-0 vs rank-1 indistinguishable)
- GUE deviation z=-19.26 (zeros more regular than GUE — needs unfolding investigation)
- Script: cartography/shared/scripts/oq1_spectral_tail.py

### 11th Negative Dimension
NOT feature-distribution-driven coupling (permutation null). CouplingScorer sees distributional structure in any feature matrices with non-trivial covariance. Object identity doesn't matter.

## What's Next
1. **GUE deviation investigation**: Is z=-19.26 an unfolding artifact or genuine? Need to apply N(T) density normalization to zeros before computing spacings.
2. **Permutation-breaking scorer**: Design a coupling scorer that uses object identity (shared labels, conductor matching) instead of feature similarity. The current CouplingScorer cannot detect object-level structure.
3. **BSD parity test**: root_number in lfunc_lfunctions, conductor index live. Join EC -> lfunc via origin. Test (-1)^rank = root_number_sign for 3.8M curves.
4. **F39: Feature permutation null**: Add to standard battery. A bond that survives permutation null but not this new test has real object-level structure.
5. **Batch 01 CrossDomainProtocol**: Run abc Szpiro through the full 38-test battery.

## Blocked Items
- lfunc origin index: would accelerate all EC-lfunc joins from ~90s to ~1s per bin. Needs write access to lmfdb DB.
- Attack 1 PCA projection: shape mismatch between subsampled (1000) and full (9116) NF domain. Fixable.
- DuckDB zeros on M2: 184K Dirichlet zeros needed for pair correlation test (MATH-0062)

## Files Created/Modified
| Path | Purpose |
|------|---------|
| roles/CrossDomainCartographer/Harmonia_Role.md | Named role document |
| roles/CrossDomainCartographer/journal_20260415_harmonia.md | Session journal |
| roles/CrossDomainCartographer/state_20260415_harmonia.md | This file |
| cartography/shared/scripts/oq1_spectral_tail.py | Spectral tail 5-attack test |
| cartography/shared/scripts/nf_backbone_test.py | NF backbone 4-attack test |
| cartography/docs/nf_backbone_results.json | NF backbone test results |
