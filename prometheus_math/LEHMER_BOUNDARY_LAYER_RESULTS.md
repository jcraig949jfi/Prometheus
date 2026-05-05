# Lehmer Brute-Force Boundary-Layer Clustering

**Author:** Techne (toolsmith)
**Forged:** 2026-05-04
**Forged for:** Charon kill-space gradient field seed (Aporia G3)
**Inputs (read-only):**
- `prometheus_math/_lehmer_brute_force_results.json` (17 unverified entries)
- `prometheus_math/_lehmer_brute_force_path_a_results.json` (mpmath dps=60 reverification)
- `prometheus_math/_lehmer_brute_force_path_b_results.json` (sympy symbolic factorization)
- `prometheus_math/_lehmer_brute_force_path_c_results.json` (tighter Mossinghoff + Lehmer × Φ_n product matching)

**Driver:** `prometheus_math/lehmer_boundary_layer.py`
**Tests:** `prometheus_math/tests/test_lehmer_boundary_layer.py`
**Output JSON:** `prometheus_math/_lehmer_boundary_layer_results.json`

---

## 1. Setup and the question

The Charon brute-force pass on the deg-14 ±5 palindromic Lehmer band returned 17 entries with `verification_failed=True` at `dps=30` (mpmath returned NaN; numpy's `M_numpy` was the only reading). Three independent rescue paths agreed on a coarse **15 / 2** split:

- **15 cyclotomic-noise entries** — true `M = 1` exactly; numpy float-noise put them in the band.
- **2 Lehmer × Φ_n^k entries** — entries 2 and 14 (0-indexed); Lehmer × Φ_1^4 (orientation `+x`) and Lehmer × Φ_2^4 (orientation `-x`) — these are `x → -x` reflection equivalents of one base polynomial.

Path A, B, C all produce the same coarse classification. **The question for this pass:** *within* those classes, what is the finer boundary-layer structure? If a future near-miss classifier (the kill-space gradient field idea) needs labeled training data, what are the labels?

---

## 2. Per-entry feature table

Eight numeric features per entry, extracted from the four JSONs:

| key                            | source        | meaning |
|--------------------------------|---------------|---------|
| `log10_M_minus_1_clamped`      | brute-force   | `log10(M_numpy − 1)`, clamped at −8 |
| `residual_M_after_cyc`         | brute-force   | original brute-force residual after cyclotomic factor strip |
| `n_distinct_factors`           | path B        | number of distinct irreducible factors |
| `n_distinct_cyclotomic_idx`    | path B        | number of distinct Φ_n indices |
| `max_multiplicity`             | path B        | largest multiplicity across factors |
| `max_factor_degree`            | path B        | largest single-factor degree |
| `min_factor_degree`            | path B        | smallest single-factor degree (constant 1 here) |
| `n_non_cyclotomic_factors`     | path B        | 0 for class 1 (C3), 1 for class 2 (C2) |

| idx | `M_numpy`  | path_c | n_dist | n_cyc_idx | max_mult | max_deg | cyc_n_indices    | sub_cluster |
|----:|-----------:|:------:|-------:|----------:|---------:|--------:|:-----------------|:------------|
|   0 |  1.00314   | C3     |    4   |     4     |    6     |    4    | [1, 2, 4, 8]     | 2 (size 12) |
|   1 |  1.00437   | C3     |    3   |     3     |    6     |    6    | [1, 2, 7]        | 0 (size 2)  |
|   2 |  **1.17653** | **C2** |    2   |     1     |    4     |   10    | [1]              | —           |
|   3 |  1.00284   | C3     |    4   |     4     |    6     |    4    | [1, 2, 4, 5]     | 2 (size 12) |
|   4 |  1.00430   | C3     |    4   |     4     |    6     |    2    | [1, 2, 3, 4]     | 2 (size 12) |
|   5 |  1.00271   | C3     |    4   |     4     |    6     |    4    | [1, 2, 3, 5]     | 2 (size 12) |
|   6 |  1.00325   | C3     |    4   |     4     |    6     |    2    | [1, 2, 3, 4]     | 2 (size 12) |
|   7 |  1.00399   | C3     |    4   |     4     |    6     |    2    | [1, 2, 3, 4]     | 2 (size 12) |
|   8 |  1.00118   | C3     |    3   |     3     |    5     |    2    | [1, 2, 4]        | 1 (size 1)  |
|   9 |  1.00394   | C3     |    4   |     4     |    6     |    2    | [1, 2, 4, 6]     | 2 (size 12) |
|  10 |  1.00271   | C3     |    4   |     4     |    6     |    4    | [1, 2, 6, 10]    | 2 (size 12) |
|  11 |  1.00325   | C3     |    4   |     4     |    6     |    2    | [1, 2, 4, 6]     | 2 (size 12) |
|  12 |  1.00437   | C3     |    3   |     3     |    6     |    6    | [1, 2, 14]       | 0 (size 2)  |
|  13 |  1.00284   | C3     |    4   |     4     |    6     |    4    | [1, 2, 4, 10]    | 2 (size 12) |
|  14 |  **1.17653** | **C2** |    2   |     1     |    4     |   10    | [2]              | —           |
|  15 |  1.00430   | C3     |    4   |     4     |    6     |    2    | [1, 2, 4, 6]     | 2 (size 12) |
|  16 |  1.00314   | C3     |    4   |     4     |    6     |    4    | [1, 2, 4, 8]     | 2 (size 12) |

The `min_factor_degree` is uniformly 1 across all 17 entries (every polynomial has at least one linear cyclotomic factor — Φ_1 = `x − 1` or Φ_2 = `x + 1`), and `n_non_cyclotomic_factors` is 0 for the 15 C3 entries and 1 for the 2 C2 entries; both are zero-variance within a sub-class so they collapse out of the sub-clustering basis.

---

## 3. Top-level clustering (all 17 entries)

KMeans on z-scored features (`n_init=20`, fixed seed). Tested k ∈ {2, 3, 4}; chose best k by silhouette, breaking ties toward smaller k for parsimony.

| k | silhouette | cluster sizes |
|---|-----------:|---------------|
| 2 | **0.8653** | `{0: 15, 1: 2}`     ← chosen |
| 3 | 0.7237     | `{0: 12, 1: 2, 2: 3}` |
| 4 | 0.7756     | `{0: 12, 1: 2, 2: 2, 3: 1}` |

**Best k = 2, silhouette = 0.865.** The clean 15 / 2 split survives every clustering attempt — the `n_non_cyclotomic_factors` axis alone produces a wide gap in z-score space that no other feature can wash out. This is consistent with all three rescue paths' coarse classification.

### Cluster 0 — Cyclotomic-noise (size 15)
- All entries: path_c = `C3` (all-cyclotomic), `n_non_cyclotomic_factors = 0`.
- `M_numpy` ∈ [1.0012, 1.0044] (just above the 1.0001 brute-force noise floor).
- Cyclotomic Φ_n union: **{1, 2, 3, 4, 5, 6, 7, 8, 10, 14}**.
- Representative: `[1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1]` (entry 0; Φ_1^6 · Φ_2^2 · Φ_4 · Φ_8).

### Cluster 1 — Lehmer × Φ_n^k (size 2)
- Both entries: path_c = `C2`, `n_non_cyclotomic_factors = 1` (the Lehmer factor itself), `max_factor_degree = 10`.
- `M_numpy ≈ 1.17653` — essentially the Lehmer constant 1.17628…
- Φ-skeletons: {1: 4} and {2: 4}.
- Representatives: entry 2 (Lehmer × Φ_1^4, orientation `+x`) and entry 14 (Lehmer × Φ_2^4, orientation `−x`).
- These are `x → −x` reflection equivalents of one base polynomial — the cluster is genuinely a single object viewed twice.

---

## 4. Sub-clustering within the C3 noise class (15 entries)

Re-ran KMeans on the 15 C3 entries with zero-variance columns dropped, k ∈ {2, 3, 4, 5}.

| k | silhouette | cluster sizes |
|---|-----------:|---------------|
| 2 | 0.5204     | `{12, 3}` |
| 3 | **0.5486** | `{12, 2, 1}`     ← chosen |
| 4 | 0.4203     | `{6, 6, 2, 1}` |
| 5 | 0.4335     | `{5, 4, 3, 2, 1}` |

**Sub-best k = 3, silhouette = 0.549.** The silhouette is moderate, not strong — at n=15 this is descriptive structure rather than a robust clustering claim. But the three sub-clusters are **structurally interpretable**:

### Sub-cluster A — "Standard quad-factor noise" (size 12)
- Entries 0, 3, 4, 5, 6, 7, 9, 10, 11, 13, 15, 16.
- `n_distinct_factors = 4`, `n_distinct_cyclotomic_idx = 4`, `max_multiplicity = 6`.
- Φ_n indices appearing in this sub-cluster's union: {1, 2, 3, 4, 5, 6, 8, 10}.
- Skeleton shape: Φ_1 with mult 2 or 6 + Φ_2 with mult 2 or 6 + two small distinct Φ_n's with mult 1.
- This is the "vanilla" cyclotomic-noise pattern — most of the deg-14 ±5 palindromic noise lives here.

### Sub-cluster B — "High-degree single-factor" (size 2)
- Entries 1, 12.
- `n_distinct_factors = 3`, `max_factor_degree = 6` (Φ_7 with degree 6 in entry 1; Φ_14 with degree 6 in entry 12).
- These two share a structural quirk: instead of four small cyclotomic factors, they have **one big Φ_n factor** (Φ_7 or Φ_14 — both have φ(n) = 6) absorbing most of the polynomial.
- Φ_7 and Φ_14 are related: Φ_14(x) = Φ_7(−x). Like the C2 cluster, this is a `x → −x` reflection pair.

### Sub-cluster C — "High-multiplicity Φ_4" (singleton, size 1)
- Entry 8: `[1, 0, 3, 0, 1, 0, -5, 0, -5, 0, 1, 0, 3, 0, 1]` (the only even-degree-only polynomial in the table).
- Φ-skeleton: {1: 2, 2: 2, **4: 5**}. Max multiplicity is 5 (vs the 6 dominant elsewhere) but it's on Φ_4 instead of Φ_1 or Φ_2.
- This is the only entry where a non-Φ_1/Φ_2 cyclotomic dominates the multiplicity. It sits alone because its multiplicity profile is structurally unlike anything else in the table.

---

## 5. Cluster → kill-vector signature mapping

For each top-level cluster, the structurally-valid mock kill-vector signature (using only fields available in the four JSONs):

| cluster | size | `out_of_band` | `has_cyc_factor` | `is_lehmer_product` | `is_pure_cyclotomic` | `verification_failed_at_dps30` | `mossinghoff_proximity_match` |
|--------:|-----:|:------:|:------:|:------:|:------:|:------:|:------:|
|  0 (C3) | 15   | True   | True   | False  | True   | True   | False  |
|  1 (C2) |  2   | False  | True   | True   | False  | True   | True   |

Every member of each cluster shares the same kill-vector (uniform within cluster — verified in `test_composition_kill_vector_signature_structurally_valid`). This is the seed for "boundary-layer aware navigation": when the future kill-space gradient field needs to recognise these failure modes, the cluster label *is* the near-miss type.

---

## 6. Boundary-layer structure as a labeled training set

Distilled into a one-page summary for downstream classifiers:

| label                                          | n  | structural signature |
|------------------------------------------------|----|----------------------|
| **C2-Lehmer-product (reflection pair)**        |  2 | `M ≈ 1.176`, `n_noncyc=1`, `max_deg=10`, Φ-skeleton ∈ {Φ_1^4, Φ_2^4} |
| **C3a — standard quad-factor noise**           | 12 | `M ∈ [1.001, 1.005]`, four distinct Φ_n with mult-pattern {2 or 6, 2 or 6, 1, 1} |
| **C3b — high-degree single-factor noise**      |  2 | `M ∈ [1.004, 1.005]`, three factors with one of degree 6 (Φ_7 or Φ_14, another reflection pair) |
| **C3c — high-mult Φ_4 noise (singleton)**      |  1 | `M ≈ 1.0012`, even-degree-only, Φ-skeleton {Φ_1^2, Φ_2^2, Φ_4^5} |

**Two observations worth noting:**
1. **Reflection pairs are the main internal symmetry.** The two C2 entries are an `x → −x` reflection pair (Φ_1 ↔ Φ_2). The two C3b entries are also an `x → −x` reflection pair (Φ_7 ↔ Φ_14). Half the "duplication" in the table is just this involution.
2. **The 12-member core is structurally homogeneous.** Sub-cluster C3a is one shape with rotating choice of the third/fourth small Φ_n. The boundary layer's cyclotomic-noise face is much narrower than the raw count of 15 suggests — there is essentially **one** noise shape with parameter choices, plus three structural exceptions (one reflection pair + one singleton).

---

## 7. Honest framing

- **n = 17 is small.** Silhouette 0.87 at the top level is robust; silhouette 0.55 at the sub-level is descriptive. Don't read these as predictive scores — they are pinning the shape of a labeled dataset, not validating a model.
- **The numeric clustering recovers what the symbolic paths already tell us.** This pass adds value only in (a) producing structural labels that downstream tooling can train against, and (b) exposing the sub-structure within C3 that the coarse 15/2 split hides.
- **The kill-vector signatures here are mocks.** They use only the fields available in the four JSONs. The full Aporia G3 / Charon kill-space components are richer; this pass produces a structurally-valid seed, not the final mapping.
- **Reflection pairs may double-count.** Two of the four "structural shapes" are `x → −x` reflection equivalents. An invariance-aware downstream classifier should fold reflection equivalents into one label before training.

---

## 8. Pointers

- Driver: `prometheus_math/lehmer_boundary_layer.py`
- Output JSON: `prometheus_math/_lehmer_boundary_layer_results.json`
- Tests: `prometheus_math/tests/test_lehmer_boundary_layer.py` (18 tests passing)
- Sibling Lehmer modules: `lehmer_brute_force.py`, `lehmer_path_a.py`, `lehmer_brute_force_path_c.py`
