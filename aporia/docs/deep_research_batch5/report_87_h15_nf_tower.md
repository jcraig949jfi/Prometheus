# Report 87 — H15: NF Class Field Tower Termination via Golod-Shafarevich at LMFDB Scale

**Agent:** Charon
**Date:** 2026-04-23
**Hypothesis:** H15 (Aporia 90-frontier)
**Status:** Reformulation + architecture brief

## 1. Problem Statement and the ADE Mismatch

H15 claims: "ADE Galois groups have class number towers terminating in <= 2 steps; non-ADE > 2." This framing is defective as stated. **ADE classification** (Dynkin diagrams A_n, D_n, E_{6,7,8}) is a Lie-theoretic / root-system object. Galois groups of number fields live in S_n and are not canonically ADE-labeled.

**Reformulation.** Three operational partitions compatible with LMFDB's `galt` column:

- **Partition I (solvability):** abelian / solvable non-abelian / non-solvable.
- **Partition II (Lie-shadow analogy):** cyclic (A-shadow), dihedral / generalized dihedral (D-shadow), exceptional small groups such as A_4, S_4, A_5 (E-shadow).
- **Partition III (direct galt bucketing):** degree d fixed, bucket by `galt` transitive ID.

Partition II is closest to H15's intent.

## 2. Golod-Shafarevich Background

Golod-Shafarevich (1964): for a pro-p group G with d = d(G) generators and r = r(G) relations,

> G is infinite whenever r < d² / 4,

with sharper form: infinite when d - r > 2√(d - 1). Applied to G = Gal(K^{unr,p} / K), the p-class field tower of K is infinite under same inequality on p-class group. Classical consequences (Koch; Roquette; Martinet, Invent. Math. 1978):

- Imaginary quadratic K with 2-rank(Cl_K) ≥ 5 has infinite 2-class field tower.
- Martinet's field Q(sqrt(-d)) with d = 3·5·7·11·13·19·23 exhibits infinite 2-tower.
- Schoof (1986) and Hajir-Maire (J. Number Theory, 2001, 2002) extended cases to cyclotomic and totally real settings.

## 3. LMFDB Data Layer

`nf_fields` has ~22M fields with relevant columns: `label`, `degree`, `disc_abs`, `class_number`, `class_group`, `galois_label`, `galt`, `cm`, `r2`. The `class_group` column gives p-rank directly. LMFDB does NOT precompute tower depth; derive via iterated Hilbert class field construction.

PARI/GP primitives: `bnfinit`, `bnrinit`, `rnfinit`, `nfinit(bnrclassfield(...))`. Techne's `hilbert_class_field` + `class_field_tower` (default 1GB parisize) encapsulate this.

## 4. Subprocess Isolation Architecture

The previous run failed because a single slow sample stalled the loop. Proposed design:

- **Worker pool:** `multiprocessing.Pool(processes=8, initializer=pari_init)` where `pari_init` sets `parisize=2^30`.
- **Hard timeout:** `apply_async`; `.get(timeout=30)` triggers SIGKILL of worker subprocess (PARI C code ignores Python signals).
- **Outcome taxonomy:** `success(depth, final_cn)`, `capped(reason=timeout)`, `capped(reason=stack_overflow)`, `capped(reason=memory)`. "Capped" is first-class; Wilcoxon rank-sum tolerates right-censoring via tie-adjusted ranking.
- **Checkpointing:** append JSONL per completed task; resumable.

Budget: 480 samples × 15s effective = ~2 hours on 8-core; 30s hard cap.

## 5. Stratified Sample

Three Galois buckets (Partition II) × seven cn levels {4, 6, 8, 10, 12, 16, 20} × 20 fields = **420 core samples** + 60 replacements. Filter `nf_fields` by degree ≤ 6 (keeps HCF tractable), class_number matching the bucket, balanced across |disc|.

## 6. Wilcoxon Design

- H_0: depth distributions identical across ADE-shadow vs non-ADE-shadow.
- Test: Mann-Whitney U, two-sided, α = 0.01.
- Kill if p > 0.01. Effect-size guard: require median-depth gap ≥ 0.5 before declaring positive.
- Power: at n = 140 per arm, power > 0.95 for rank-sum at median gap 1.

## 7. Specimen 2.0.2296.1

Imaginary quadratic, disc = -2296 = -2³·7·41, cn = 16. Aporia's partial run reported HCF cn = 112 beyond the guard at 50. Consistent with Golod-Shafarevich territory: if 2-rank(Cl_K) is large, 2-tower may be infinite. **Action:** isolated depth-3 probe with 1-hour budget, independent of H15. If tower continues growing, catalog as Martinet-style long-tower candidate; cross-check against Hajir-Maire tables.

## 8. Outputs

- `h15_rerun_v2/results.jsonl` — per-sample outcomes
- `h15_rerun_v2/summary.md` — Wilcoxon p-value, effect sizes, capped rate
- `h15_rerun_v2/specimen_2296.md` — standalone depth probe

**Word count: 760**
