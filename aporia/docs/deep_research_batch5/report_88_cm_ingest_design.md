# Report 88: CM EC Ingest Design for Axis 3b Classification

**Target agent:** Charon
**Date:** 2026-04-23
**Topic:** Mnemosyne CM-curve ingest pipeline to enable decisive Axis 3b symmetry-class test

## 1. Problem Statement

F011's Axis 3b test computes Spearman(nbp, gap-variance deficit) across Katz-Sarnak families. Five of six families resolved cleanly: Dirichlet real/complex (+1.0), EC rank-0 non-CM (+1.0), EC rank-1 (+1.0), G2C USp (-0.9). The **CM rank-0 EC** cell at n=2134 was inconclusive: nbp bins 1-4 were non-monotone, Spearman p=0.67. To decide whether CM EC sit in Orthogonal, Symplectic, or Unitary class, we need n ≥ 20K curves with the first ~40 positive zeros, with cell counts ≥ 50 per (cm_disc × nbp) stratum covering nbp ∈ {1,2,3,4,5}.

## 2. Current Data Inventory

LMFDB holds ~4M elliptic curves over Q from Cremona's `ecq`. The `ec_curvedata` table exposes `cm_disc` (null for non-CM; negative fundamental discriminant in {-3,-4,-7,-8,-11,-19,-43,-67,-163} for the 13 rational CM j-invariants). Rank-0 CM curves number in the low hundreds of thousands, but `lfunc_lfunctions` intersection is the bottleneck: only **~2134** CM rank-0 curves have stored zeros.

## 3. Ingest Pipeline Design

**Step 1 — Candidate selection.** Query `ec_curvedata` for `cm_disc IS NOT NULL AND rank = 0`, ordered by conductor. Expected count ~150K-250K; cap at first 25K. Stratify pull so each cm_disc value is proportionally represented (prevents -3 and -4 from saturating sample).

**Step 2 — Zero computation.** For each curve, compute first 40 positive imaginary parts of L-function zeros. Two backends:
- **PARI/GP `lfuninit` + `lfunzeros`** (Belabas-Cohen, PARI 2.13+): ~5-8 s/curve at conductor ≤ 10^6.
- **Sage `lcalc`** (Rubinstein 2005): similar cost; LMFDB's original backend.

Both implement Riemann-Siegel via functional equation (Dokchitser 2004, *Experimental Mathematics* 13, 137–149). Precision target: 20 digits.

**Step 3 — Storage.** Write to `prometheus_fire` as `cm_ec_zeros_v1(lmfdb_label, cm_disc, conductor, rank, nbp, zeros float8[40], computed_at, backend)`. Index on `(cm_disc, nbp)`. Request table registration through Mnemosyne per dual-Postgres protocol.

**Step 4 — Cross-validation.** For 2134 curves overlapping LMFDB's `lfunc_lfunctions`, compare first 20 zeros to 15-digit precision. Tolerance 1e-10 on max elementwise diff; flag mismatches.

## 4. Budget

Single-core: 7 s/curve × 20K = **~39 hours**. On 8-core Skullport (GNU parallel or PARI worker pool): **~5-6 hours wall**. On SpectreX5 (16-core): under 3 hours. Disk: 40 zeros × 8 bytes × 20K ≈ 6.4 MB raw, ~30 MB with indexes.

## 5. Diagnostic Plan

Post-ingest, bin each curve by (cm_disc, nbp). Target cell size ≥ 50. Compute gap-variance deficit per curve, then Spearman(nbp, deficit) within each cm_disc stratum.

Expected outcomes per Katz-Sarnak (1999) and Miller (2006, Experimental Mathematics 15):
- **All cm_disc → +ρ:** Orthogonal; consistent with self-dual motives, Katz-Sarnak placement.
- **All cm_disc → -ρ:** Symplectic; kill of textbook classification.
- **Mixed by cm_disc:** Sub-class structure tied to CM field Q(√(cm_disc)). -3 and -4 (extra units) may separate from seven with unit group {±1}.

## 6. Alternatives If Full Ingest Blocked

- **Minimum-viable.** Keep 2134 LMFDB + 500 smallest-conductor Cremona CM curves not in `lfunc_lfunctions`. n ~ 2634, per-cell ~ 30: underpowered.
- **Discriminant-focused.** n=500 per disc for {-3,-4,-7,-8} (n=2000 new + 2134 existing). Catches majority-class; misses rare tail.
- **Reuse CMFs.** Classical newforms of weight 2 with inner twists (`mf_newforms.has_inner_twist = true`) overlap heavily with CM EC L-functions; LMFDB stores more zeros per CMF. Join via isogeny class could lift to ~5K without recomputation.

## References

- Cremona, *Algorithms for Modular Elliptic Curves*, 2nd ed., CUP 1997.
- Katz & Sarnak, *Random Matrices, Frobenius Eigenvalues, and Monodromy*, AMS Colloq. Publ. 45, 1999.
- Dokchitser, "Computing special values of motivic L-functions", *Experimental Mathematics* 13 (2004), 137-149.
- Rubinstein, "Computational methods and experiments in analytic number theory", LMS Lecture Note Ser. 322, 2005.
- Miller, "Investigations of zeros near the central point of EC L-functions", *Experimental Mathematics* 15 (2006), 257-279.

**Word count: ~770**
