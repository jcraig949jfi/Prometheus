# Koios — The Axis

## Standing Orders

1. A feature enters the tensor ONLY if it passes all 5 gates: null-calibrated, representation-stable, not reducible to marginals, non-tautological, domain-agnostic.
2. Every value carries validation metadata. The tensor is `{feature: value + gate_results}`, not `{feature: value}`.
3. IDN (3 normalizations: size-residual, entropy-ratio, rank-quantile) before ANY cross-domain comparison.
4. One invariant family at a time. Compute, normalize, battery, kill or keep.
5. No target leakage. MPA vectors computed from structure alone.
6. The MPA is constructed, not discovered.

## Data Sources (read-only)

- `../charon/data/charon.duckdb` — EC, MF, L-functions
- `../cartography/*/data/` — all domain datasets
- Never modify upstream data. Write results to `koios/results/`.
