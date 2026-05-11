# Ergon Tensor Manifest

**File:** `tensor.npz`
**Size:** 28,352,304 B (27.0 MB)
**Last modified:** 2026-05-03 18:31:44 -0400
**Dimensions:** 4,755,770 objects x 208 features (verified via `numpy.load`)
**Domain count:** 23 (verified via `domain_boundaries` map in the .npz)
**Build script:** `F:\Prometheus\ergon\tensor_builder.py` (CLI: `python tensor_builder.py --domains core` produces this file by default; run from `ergon/` so default output path is `ergon/tensor.npz`).
**Build inputs:** Harmonia domain loaders. The `tensor_builder.py` module imports `DOMAIN_LOADERS` from `harmonia.src.domain_index` and concatenates each loader's `(N, D)` z-scored feature matrix. Each loader is itself sourced from local Postgres (`ec_curvedata`, `nf_fields`, `artin_reps`, `lfunc`, etc., per HANDOFF.md 2026-04-18 "Infrastructure" section), Redis caches, and local data files. Build is deterministic only at the loader level — subsampling within `build_tensor(max_per_domain=...)` uses `np.random.seed(hash(name) % 2**31)`.
**Provenance:** Last rebuilt 2026-05-03 18:31. Most recent commits touching `tensor*.npz` / `tensor_builder.py`:
- `3250f751` "Team backfill 2026-04-25 → 2026-05-04: accumulated multi-agent work" — covers the 2026-05-02/03 rebuild
- `ce8ef247` "Ergon: Explorer v3 — 23 domains with knots_eng + knots_topo" — established current 23-domain layout
- `427fd323` "Ergon: E-FP-1 + E-FP-3 fingerprint domains from Aporia report" — added `nf_cf` + `artin_ade`
- `56b98d89` "Ergon: Tensor builder v2 — 7 domains to 29, 58K objects to 5.08M" — v2 schema introduction
**Last validated:** 2026-05-10 (manifest created; dimensions and domain list confirmed via `numpy.load`)

## Companion files

- **`tensor_all.npz`** — 37,856,233 B (36.1 MB), 2026-05-02 20:54. Shape: 5,079,774 x 263, 29 domains. Built with `--domains all` (CORE + EXTENDED + DERIVED, where DERIVED adds dynamics, phase_space, spectral_sigs, operadic_sigs, padic_sigs, info_theoretic, fractional_deriv, functional_eq, resurgence). Use this when downstream analysis needs the derived signature features.
- **`tensor_extended.npz`** — 26,913,009 B (25.7 MB), 2026-05-02 20:54. Shape: 4,629,840 x 181, 20 domains. Built with `--domains extended` (CORE + EXTENDED, no DERIVED). The `tensor.npz` (`--domains core` default — 23 domains) actually overlaps with this set: the live `tensor.npz` includes all of `tensor_extended.npz`'s domains plus `artin_ade`, `knots_eng`, `knots_topo` (the 23 = 20 + 3 fingerprint/engineered domains). Confirm before retiring `tensor_extended.npz`.

## Schema

Per `tensor_builder.py` `CORE_DOMAINS` + `EXTENDED_DOMAINS` lists, the live `tensor.npz` 23 domains (in row order) are:

| Domain | Approx. n_objects | Approx. n_features | Source class |
|---|---|---|---|
| elliptic_curves | ~3.8M | 4 | core (Postgres `ec_curvedata`) |
| modular_forms | ~100K | 5 | core |
| number_fields | ~9K | 6 | core (Postgres `nf_fields`) |
| genus2 | ~66K | 7 | core |
| artin | ~100K | 5 | core (Postgres `artin_reps`) |
| ec_rich | ~100K | 16 | core (rich EC features) |
| knots | ~13K | 28 | core |
| maass | ~15K | 25 | core |
| lattices | ~39K | 6 | extended |
| polytopes | ~1K | 6 | extended |
| materials | ~10K | 6 | extended |
| space_groups | ~230 | 5 | extended |
| belyi | ~1K | 3 | extended |
| bianchi | ~100K | 5 | extended |
| groups | ~100K | 3 | extended |
| oeis | ~100K | 7 | extended |
| codata | ~286 | 10 | extended (physical constants) |
| pdg_particles | ~226 | 11 | extended (particle physics) |
| chemistry | ~50K | 12 | extended (QM9 molecules) |
| metabolism | ~108 | 11 | extended |
| artin_ade | ~100K | 11 | extended (Artin + ADE/Dynkin) |
| knots_eng | ~13K | 12 | extended (Mahler measure, roots of unity, PCA) |
| knots_topo | ~13K | 4 | extended (hyperbolic volume from SnapPy) |

Per-domain row offsets are stored in the `domain_boundaries` field of the .npz; per-(domain, feature) column indices are stored in `feature_col`. Feature names are placeholders of the form `f0`, `f1`, ..., `f{n-1}` per domain — semantic feature names are NOT stored in the tensor itself; they live in the source Harmonia loaders.

Counts above are nominal (from `tensor_builder.py` comments). Actual per-domain row counts at the 2026-05-03 build are recoverable via `domain_boundaries` — TBD: rebuild this table from the live tensor if exact counts are needed.

## Update protocol

- After any rebuild of `tensor.npz`: update **Size**, **Last modified**, **Dimensions**, **Domain count**, **Provenance** (add the new commit hash). If domain set changed, update Schema.
- After any rebuild of a companion file: update its row in the Companion files section.
- After feature changes (a domain's loader changes its z-score recipe or feature count): update the corresponding row in Schema and bump the **Last validated** date.
- After a known-bad rebuild: do NOT delete this file. Append a "Known issues" section at the bottom with date, commit hash, and the symptom. Roll the tensor back via git/backup before downstream use.
- After tensor archival or retirement: do NOT delete this file. Move that file's row to a "Retired tensors" section.

## Known issues

(none yet)

## Retired tensors

(none yet)
