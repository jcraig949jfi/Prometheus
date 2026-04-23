# Generator #12 — Tensor Identity Search

**Status:** Tier 2 (medium infra). DRAFT v0.3 (2026-04-23, updated after canonicalizer moved to its own primitive).
**Role:** Producer — operates on **orbit-equivalence-class space**. Given a target multilinear map `T`, produces representatives of orbit-equivalence classes of low-rank decompositions of `T` under the tensor's symmetry group.
**Requires:** `CANONICALIZER:tensor_decomp@v2` (pending) — canonicalizer registered in `harmonia/memory/architecture/canonicalizer.md`. The canonicalizer is a separate substrate primitive; this generator consumes it.
**Also requires:** Definition DAG (Gate 4), `multilinear_map@v1` + `decomposition@v1` symbol types (new, to be drafted in `CANDIDATES.md`).
**Qualification:** Harmonia session with symbol-registry write access + access to a numpy / JAX compute environment.
**Estimated effort:** 6–10 ticks for first end-to-end pass *after* `CANONICALIZER:tensor_decomp@v2` ships. The canonicalizer work is owned by the primitive, not by this generator.

---

## Why this exists

Strassen 1969 decomposes the 2×2 matmul tensor at rank 7 (vs naive 8); Laderman 1976 at rank 23 for 3×3. AlphaTensor (DeepMind 2022) searched this space via RL and reported new decompositions for 4×4 and 5×5 over small finite fields.

A 2026-04-23 pilot (`harmonia/tmp/tensor_pilot_2x2_matmul.py`) established that **search is not the bottleneck**. A 60-line ALS + multi-restart stack rediscovered Strassen's rank-7 *orbit* in 6/20 seeds at machine precision in 1.4 seconds of compute. What it did not find was Strassen's *representative* within that orbit: ALS-converged decompositions had integer-fraction 0.02–0.16, while Strassen's is 1.0.

A follow-up canonicalizer test (`harmonia/tmp/canonicalize_test.py`) confirmed the consequence: a v1 canonicalizer that fixes scaling, sign, and permutation gauges produces **four different canonical hashes** for four ALS-converged decompositions known to be in a single orbit by theorem, and none match Strassen. The `(GL(n) × GL(n) × GL(n))`-stabilizer-of-T subgroup is where most of the orbit's size lives, and nothing in the v1 canonicalizer touches it.

**The reframe:** the search finds orbit points; what we want is orbit classes. Without an orbit canonicalizer, every downstream move — MAP-Elites cells, "integer-ness" and sparsity objectives, catalog dedup, novelty claims — reads coordinate artifacts instead of invariants. This generator is not "search for decompositions with a Gate 2 orbit filter." It is a producer **of orbit classes**, with canonicalization as the central primitive that every other module calls into.

Substrate primitive: canonicalization is the cross-cutting substrate primitive specified in `harmonia/memory/architecture/canonicalizer.md` (v0.1, 2026-04-23). The tensor-decomposition-specific instance detail and the 2×2 matmul empirical anchor live in `harmonia/memory/architecture/orbit_vs_representative.md` (v0.2). This generator depends on `CANONICALIZER:tensor_decomp@v2` via the primitive's instance registry; it does not own or embed the canonicalizer.

**What it is NOT:** a theorem prover. A decomposition found here is an algebraic identity to the extent that its residual is exactly zero (over ℚ or a pinned finite field) and the factors are verified by independent multiplication. We record orbit-equivalence classes as measurements, not arithmetic novelties.

---

## Inputs

- A **`multilinear_map@vN`** symbol (new symbol type, see §"Substrate additions"). Examples: `MATMUL_2x2@v1`, `MATMUL_3x3@v1`, `DET_3@v1`, `POLY_MULT_DEG_4@v1`, `SU2_STRUCTURE@v1`.
- A **field specification**: ℝ, ℚ, ℂ, `F_p`, `F_{p^k}`, or a rounded-rational search scheme. Field is load-bearing: a rank-r decomposition over `F_2` is not a rank-r decomposition over ℝ.
- A **search spec**: `(search_primitive, budget, rank_target | rank_range, cell_axes)`.

## Outputs

For each seeded run, a set of candidate **`decomposition@vN`** symbols (new type), each carrying:
- `target_multilinear_map`: which `multilinear_map@vN` this decomposes
- `field`: the field the decomposition lives in
- `rank`: integer
- `factors`: three matrices `(A, B, C)` with values in the field
- `exactness`: `exact_zero_residual` | `approximate(ε=...)`
- `equivalence_class_hash`: orbit-invariant fingerprint against the decomposition catalog (see Gate 1)
- `provenance`: search primitive + seed + budget + composition hash
- `tier`: `calibration` (rediscovers known) | `candidate` (passes gates) | `catalog_duplicate` (orbit-equivalent to known; retained for auditing)

## Canonicalization is the pipeline's spine

Every search primitive produces `(A, B, C)` tuples that are orbit points. The canonicalizer maps them to orbit representatives. Only representatives are compared, cataloged, or scored. This reordering — canonicalize before everything else — is the correction applied in v0.2 after the 2026-04-23 pilot.

```
search primitive → (A, B, C) raw tuple
                 → canonicalizer (scale, sign, permute, basis-align)
                 → canonical (A, B, C) + canonical_hash
                 → cell lookup in MAP-Elites archive (behavior cells computed on canonical form)
                 → catalog dedup via hash
                 → gates on the canonical form
```

The canonicalizer contract lives in `harmonia/memory/architecture/canonicalizer.md` (general primitive) with tensor-specific instance detail in `orbit_vs_representative.md`. This generator **requires** `CANONICALIZER:tensor_decomp@v2` (which removes T-stabilizer basis change, not just v1's scale + sign + permutation) before any novelty claim tiers. v2 is currently pending in the canonicalizer instance registry.

## Cells (MAP-Elites behavior space) — on the canonical form, not raw output

Default cell axes, all computed *after* canonicalization:

1. **`rank`** — integer.
2. **`field`** — ℝ / ℚ / ℂ / `F_p`.
3. **`exactness`** — 2-way bucket: exact vs approximate.
4. **`integer_entry_fraction`** — fraction of canonical-form entries within tolerance of an integer. Strassen's canonical rep scores 1.0; ALS-raw scored 0.02–0.16 (pilot 2026-04-23). This cell only makes sense on the canonical form — on raw ALS output it measures basis drift, not structure.
5. **`sparsity`** — fraction of canonical-form entries below tolerance.
6. **`symmetry_score`** — detected symmetry of the canonical `(A, B, C)` triple under cyclic / transpose / permutation (e.g., whether the decomposition has mirror symmetry across the three factors, characteristic of Strassen).

Diagnostic-only cells (not primary):
- **`search_primitive`** — which primitive produced this orbit point? If multiple primitives land in the same cell on the same orbit representative, that's cross-lens agreement (SHADOWS_ON_WALL at the search level).
- **`basin_dispersion`** — for an orbit representative, the variance of canonical-forms across raw inputs that map to it. Small dispersion = canonicalizer is tight; large = canonicalizer is sloppy or probabilistic.

## Gates (applied to canonical representatives)

Each candidate orbit representative passes four gates in order.

**Gate 1 — Exactness.** Residual `‖T − Σ_r A[:,r] ⊗ B[:,r] ⊗ C[:,r]‖_F ≤ tol_exact` on the **raw** factors (canonicalization should not change residual). Approximate decompositions recorded with a tier flag; do not enter the exact-identity catalog.

**Gate 2 — Orbit-equivalence check against catalog.** Compute `canonical_hash(A, B, C)` and look it up in the decomposition catalog filtered by `(target, field, rank)`. If hash matches an existing entry → `tier = catalog_duplicate`, retain provenance for search-primitive auditing, do not re-emit. If hash is novel → pass to Gate 3. This gate depends on the canonicalizer's invariance; without v2 canonicalizer it is a false-pass factory (pilot 2026-04-23 evidence).

**Gate 3 — Independent verification.** Reconstruct `T̃` from raw factors using a code path *disjoint* from the search's own reconstruction. For ℚ decompositions, additionally perform symbolic verification via `sympy`. Gate 3 protects against bugs in the search's residual computation producing false zeros.

**Gate 4 — Definition DAG check.** If the target multilinear map is algebraically defined in terms of the decomposition's factors (e.g., a contrived target constructed to have the factors in its definition), reject as tautology. This is the `PATTERN_30` analog for decompositions: a "decomposition" that restates the target's definition is not a finding.

## Search primitives (not pick-one; run in parallel)

- **GA + MAP-Elites** (James's seed proposal): population of factor triples, mutation by Gaussian noise + factor-block swap, selection by exact-residual; archive by the cells above.
- **ALS + random restart** (classical baseline): alternating least-squares inner loop, multi-start outer loop. Well-studied; produces reliable baselines. Used as the calibration-anchor primitive.
- **Gradient descent on smoothed rank** (modern baseline): optimize `‖T − decomp‖² + λ · nuclear_surrogate(factors)`; schedule λ upward.
- **Structured search** (algebraic-prior primitive): restrict factor entries to `{-1, 0, 1, ±1/2, ±2}` and search combinatorially. Heuristic; sometimes reaches Strassen-style integer decompositions without continuous optimization.

All four should be runnable on the same `(target, field, rank)` seed and the results concatenated into one MAP-Elites archive. *Cross-primitive disagreement on reached rank is the most informative diagnostic* — a rank reached by one primitive but not others may be a search-bias artifact or a genuinely hard basin.

## Substrate additions

Two new symbol types. Both slot into the existing symbol-registry architecture (§`harmonia/memory/symbols/OVERVIEW.md`) without protocol changes.

1. **`multilinear_map@vN`** — a target tensor. Frontmatter: `shape`, `field`, `definition` (sympy-parseable, pointing to canonical indices), `references` (literature), `known_upper_bound_rank`, `known_lower_bound_rank`. Body: derivation. Redis mirror under `multilinear_maps:*`.

2. **`decomposition@vN`** — a factorization. Frontmatter: `target`, `field`, `rank`, `factors` (stored as JSON blobs or hash-addressed for large rank), `equivalence_class_hash`, `search_primitive`, `seed`, `verification_tier`. Body: provenance + reconstruction verification log. Redis mirror under `decompositions:*`.

**Catalog seed** (one-time work): `MATMUL_2x2@v1`, `MATMUL_3x3@v1`, `DET_3@v1`, `POLY_MULT_DEG_3@v1`, plus the known reference decompositions for each (Strassen, Laderman, Leibniz for det, Karatsuba for poly-mult). This is the calibration anchor set. The generator must rediscover these before any novelty claim tiers.

## Composes with

- **`MDL_SCORER@v1`** — total description length of `(decomposition spec + residual error)` ranks competing decompositions. Zero-residual exact decompositions have infinite MDL advantage over approximate ones; among exact ones, MDL prefers shorter factor descriptions (a proxy for Strassen-likeness).
- **`CHANNEL_CAPACITY@v1`** — mutual information between input slices and output slices under a given decomposition is a decomposition-quality proxy orthogonal to rank.
- **`CONTROLLABILITY_RANK@v1`** (entry 8) — the controllability structure of the multilinear map is related to what the decomposition is trying to expose; full-rank decompositions on full-controllability maps is a coupled regime.
- **`PATTERN_30`** — definition-forcing hazard at the decomposition level, specifically handled by Gate 4.
- **Definition DAG** — Gate 4's implementation once DAG Phase 0 lands.

## Epistemic discipline

1. **Calibration anchors before novelty.** The generator's first run *must* produce rank-7 Strassen on `MATMUL_2x2@v1` over ℝ and rank-23 Laderman on `MATMUL_3x3@v1` over ℝ. If it cannot, the search stack is undercalibrated and novelty claims are invalid. This is the project-level version of F001–F005-first.

2. **Field, exactness, and structure are load-bearing.** Any report of a decomposition must pin all three. An ℝ-decomposition that only converges to ε=1e-3 is not the same epistemic object as an exact ℚ-decomposition. A rank-47 4×4 matmul over `F_2` is not a rank-47 decomposition over ℝ.

3. **Orbit equivalence is not optional.** Without Gate 2, the generator is a false-finding factory. Implementation of the canonical form is the single largest infrastructure lift in this spec.

4. **TT vs CP as parallel experiments.** Tensor-train decompositions and CP decompositions explore different basins; the MVP should run both on the same target and compare. Declaring one "the genome" up front is a reward-signal-capture risk.

5. **The decomposition catalog is a `PROBLEM_LENS_CATALOG@v1` instance.** Each target multilinear map is a "problem"; each decomposition primitive is a "lens." Cross-lens agreement on reached rank = surviving candidate; disagreement = map of disagreement (potential search-bias discovery).

---

## MVP scope (v0.3 exit criteria — canonicalizer owned externally)

To graduate this spec from DRAFT to v1.0, in strict order:

1. [ ] **`CANONICALIZER:tensor_decomp@v2` ships** per the canonicalizer primitive's own exit criteria. Passes its registered calibration anchor. This step is owned by the canonicalizer primitive, not by this generator; gen_12 consumes the output.
2. [ ] `multilinear_map@v1` and `decomposition@v1` symbol schemas drafted in `harmonia/memory/symbols/CANDIDATES.md`. `decomposition@v1` must include `canonical_hash`, `canonicalizer_instance`, and `canonicalizer_version` fields (the instance+version pair namespaces hashes against cross-version comparison bugs).
3. [ ] Gate 3 (independent reconstruction) implemented as a separate module.
4. [ ] Calibration anchor run: at least **two distinct search primitives** (ALS-restart plus one other — GA+MAP-Elites or structured-integer search) both produce rank-7 decompositions that canonicalize to the Strassen orbit representative on `MATMUL_2x2@v1` (exact, ℝ).
5. [ ] One pilot run recorded as a SIGNATURE with canonical hash + all gates passed.

**Critical path:** step 1 (`CANONICALIZER:tensor_decomp@v2`) is a hard blocker for steps 2–5 and is owned externally. Attempting steps 2–5 first is what v0.1 of this spec implicitly assumed; the 2026-04-23 empirical evidence refutes that assumption.

MVP can fall short of Laderman and still be a v1.0 ship — Strassen orbit rediscovery **with canonical representative recovery** is the minimum viable calibration.

---

## Regression test: rank-6 impossibility

The 2026-04-23 pilot produced a second empirical anchor beyond the orbit-vs-representative finding. Across 20 random seeds at rank 6 (known impossible for 2×2 matmul over ℝ per Winograd 1971), every seed's residual clustered tightly at exactly 1.000. This is a cheap, clean shadow of the lower-bound theorem.

**Freeze as a gate:** any search primitive added to this generator must, when run at rank 6 on `MATMUL_2x2@v1`, produce residuals bounded away from zero (empirically ≈ 1.0). A primitive that reports residual < 1e-6 at rank 6 has a bug, not a finding. This gate runs on every primitive addition before it enters the calibration anchor rotation.

---

## What this is NOT

- Not a theorem-prover; the "identities" found here are algebraic decompositions verified by multiplication, not proofs.
- Not a benchmark against AlphaTensor; Prometheus's deliverable is a substrate + disciplined catalog, not a single record-beat.
- Not a commitment to ship. The 2026-04-23 MVP pilot (`harmonia/tmp/tensor_pilot_2x2_matmul.py` and verdict doc) is the decision point.

---

## Version history

- **v0.3 DRAFT** — 2026-04-23 (later same day as v0.2) — moved the
  canonicalizer from a gen_12-internal primitive note into a first-class
  substrate primitive at `harmonia/memory/architecture/canonicalizer.md`.
  gen_12 now depends on `CANONICALIZER:tensor_decomp@v2` via the
  primitive's instance registry; `orbit_vs_representative.md` is
  repositioned as the tensor-decomposition instance detail and empirical
  anchor. Rationale: canonicalization is cross-cutting (tensor decomp,
  DAG node identity, MAP-Elites dedup, Pattern 30 rearrangement all need
  it); burying it inside gen_12 was the wrong abstraction boundary.
- **v0.2 DRAFT** — 2026-04-23 (same day as v0.1) — reframed after
  empirical pilot and canonicalizer test. v0.1 listed orbit equivalence
  as Gate 2 among four gates; pilot evidence (4 ALS seeds in same orbit
  hash to 4 different v1 canonical forms, 0 match Strassen integer rep)
  showed that positioning was wrong. v0.2 makes canonicalization the
  pipeline spine: every module sees canonical representatives, not raw
  factor triples. MVP exit criteria reordered to put canonicalizer v2
  first. Rank-6 impossibility promoted to regression test.
- **v0.1 DRAFT** — 2026-04-23 (earlier) — initial spec, written alongside
  a 2×2 pilot and a stoa/ideas discussion doc as three parallel MVPs of
  James's "evolving math" direction. Superseded within hours by v0.2
  after empirical evidence refuted v0.1's Gate-2 positioning.
