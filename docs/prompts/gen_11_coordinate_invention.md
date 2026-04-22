# Generator #11 — Coordinate-System Invention

**Status:** Tier 2 (medium infra; Definition DAG is a hard prerequisite for the filter).
**Role:** Producer — operates on **axis-space**, not measurement-space.
**Qualification:** Harmonia session with tensor-read access + symbol-registry write access.
**Estimated effort:** 4–6 ticks for first end-to-end pass; ongoing as the catalog grows.

---

## Why this exists

Every projection in the catalog encodes one human's answer to *"what coordinate would discriminate this feature?"* The substrate currently waits on human attention to invent the next answer. F011 sat at uniform +1 across seven projections until P028 Katz-Sarnak was added in 2026-04-17 — the resolving axis had existed in the literature since 1999, but the catalog gap wasn't closed until a feature demanded it.

That demand signal is computable directly from the tensor. Pattern 18 (uniform visibility across all walked projections) and Pattern 13 (accumulated kills along an axis class) are the two diagnostic shapes. Both say: *the resolving axis is outside the current set, and we know roughly what shape it is*.

This generator reads that demand, proposes candidate axes from five differently-priced sources, filters them through the Definition DAG and a discrimination test, and emits validation tasks. It is the substrate's first move toward inventing what to measure *through*, not just what to measure.

**What it is NOT:** novel mathematics. The candidates this generator proposes are mostly re-parameterizations of existing structure (sometimes obvious in hindsight, sometimes not). The novelty is in the *match* between an unresolved feature's invariance pattern and a candidate axis's discrimination profile.

---

## Infrastructure to build

### Module 1 — Demand reader

**Input:** the live tensor (via `agora.tensor.reconstruct_matrix` + `feature_meta`).

**Output:** a ranked list of `demand_signals`, each carrying:
- `feature_id`
- `signal_type` ∈ {`uniform_visibility`, `axis_class_exhaustion`, `outlier_specimen`}
- `walked_projections`: the P-IDs already tested
- `axis_class_constraints`: which classes are exhausted (e.g., "not family-level"; "not magnitude-confounded")
- `urgency_score`: composite of (n_walked, max_z_observed, projection-class diversity)

**Logic:**

1. For each F-ID with ≥ 4 tested cells, classify the row:
   - All cells +1 (no kills): `uniform_visibility` → demand for new axis class
   - Mix of +1 and −1 along one class (e.g., all family-level died): `axis_class_exhaustion` → demand for non-class-X axis
   - Single specimen +2 against an axis nothing else resolves: `outlier_specimen` → axis may be feature-specific, lower priority
2. Rank by urgency_score. Top-N seed candidate generation in Module 2.

**Implementation path:** `harmonia/coord_invention/demand_reader.py`. Pure read against Redis tensor mirror.

### Module 2 — Candidate generators (five sources)

Each source emits raw candidate axes. All candidates pass through Module 3 before promotion.

**Source A — Combinatorial joints.** Take pairs of existing P-IDs, propose joint stratifications (`P020 × P023`, `P024 × P025`). Cheap; mostly noise; occasionally resolves what neither marginal does. Rate-limit to top-K by tensor coverage of input axes.

**Source B — Algebraic transformations.** For each numeric P-ID (conductor, regulator, discriminant), apply a small transformation library: `log`, `mod p` (small primes), `prime signature`, `distance to nearest power`, `radical`. Each transformation is a candidate axis. The DAG (Module 3) catches tautological transformations.

**Source C — Specimen-pull.** From the specimen registry, identify outliers on each existing axis (top-decile + bottom-decile per P-ID). For each outlier set, propose: *"what axis would un-outlier these specimens?"* Operationalize via PCA or contrast-feature search on the specimen feature vectors. The principal direction not aligned with existing P-IDs is a candidate.

**Source D — Theory-pull.** Hook into Aporia's literature stream and gen_07's literature-diff log. Filter for paper sections that name a coordinate system (Katz-Sarnak families, Sato-Tate groups, Kodaira types, Hodge components, Galois cohomology classes). Cross-reference against `coordinate_system_catalog.md`. Anything named in literature but not in the catalog is a high-signal candidate.

**Source E — Kill inversion.** For each killed F-ID, compute: *"under what coordinate would this have survived?"* This is harder — operationalize via a model that, given the feature's data and a kill verdict, proposes a stratification under which the kill would not have replicated. Start with a heuristic: take the strata where the kill's z-score was *least* extreme; the axis distinguishing those strata is a candidate.

**Implementation path:** `harmonia/coord_invention/generators/{a..e}.py`, each pure-computation, each emitting `Candidate(name, definition, source, expected_discriminates: list[F-ID])`.

### Module 3 — Filter

Every candidate passes three gates in order. Failure at any gate → discard with reason logged.

**Gate 1 — Definition DAG check.** Query the DAG: does the candidate axis algebraically reduce to an existing P-ID under any rewriting? If yes, REJECT (it's a re-encoding, not a new coordinate). The DAG is the substrate primitive proposed alongside this generator (see `dag_definition_graph.md`). Until the DAG ships, this gate runs a coarse check: name-substring + symbolic-equivalence via `sympy` on the definition expression.

**Gate 2 — Discrimination test.** Apply the candidate axis to the demand-set features. Compute a quick t-statistic / Kruskal-Wallis on the feature's response variable across the candidate's strata. If z < 2 across all demand features, REJECT (axis doesn't discriminate). If z ≥ 3 on at least one, PASS to Gate 3.

**Gate 3 — Near-duplicate check.** For each existing P-ID, compute the candidate's stratification overlap (e.g., adjusted Rand index between candidate's binning and existing P-ID's binning, on a shared specimen sample). If ARI > 0.85, REJECT (it's a near-duplicate). If 0.5 < ARI ≤ 0.85, FLAG for conductor review (might be useful sub-stratification). If ARI ≤ 0.5, PASS.

**Implementation path:** `harmonia/coord_invention/filter.py`. Heavy lift on Gate 1 once DAG lands; light on Gates 2 and 3.

### Module 4 — Promotion path

Surviving candidates do NOT auto-promote to the catalog. They emit Agora tasks:

```
task_type: validate_candidate_projection
spec: docs/prompts/gen_11_coordinate_invention.md
goal: "Validate candidate axis <CAND> against demand-features <F-IDs>; if passes block-shuffle promotion gate, promote to draft P-ID."
acceptance:
  - run candidate axis against each demand-feature
  - pass NULL_BSWCD@v2 with claim-class-appropriate stratifier
  - if promoted: reserve_p_id(), write catalog entry, update tensor PROJECTIONS list
  - if not: log to gen_11_rejected_log.md with rationale
```

This keeps the human (or human-equivalent reviewer) in the loop at the *final* promotion step — entry to the substrate's permanent vocabulary remains a deliberate act, not an automatic one.

---

## Process

1. Implement Modules 1–4 as pure-computation symbols (per `long_term_architecture.md §2.1`).
2. Run end-to-end on the current tensor. Expect: 5–15 demand signals, 50–200 raw candidates, 5–20 surviving candidates, 1–5 promoted P-IDs after worker validation.
3. Log every rejected candidate with reason — the rejected log is the calibration data for tuning future runs.
4. Re-run weekly (or when tensor density crosses a threshold). Each new P-ID promoted updates the demand pattern and may unlock new candidates.

---

## Outputs

- `harmonia/coord_invention/` package with the four modules + tests.
- `harmonia/memory/coord_invention_log.md` — append-only record of every demand signal raised, every candidate generated, every gate-decision.
- `gen_11_rejected_log.md` — calibration data for filter tuning.
- N validation tasks seeded on Agora (one per surviving candidate).
- Promotion of the generator pipeline as a versioned `computation` symbol once the type ships.

---

## Epistemic discipline

1. **Curve-fitting risk is the central failure mode.** Invent enough axes and you'll find one that "resolves" any feature. The discrimination filter (Gate 2) plus the worker-validation step (Module 4) are the two gates against this. Log the false-discovery rate over time; if > 30% of promoted candidates fail subsequent independent re-test, tighten the filter.
2. **Catalog bloat is the quiet failure mode.** 100 new P-IDs that all measure variants of the same thing makes the tensor unreadable. Gate 3 (near-duplicate check) is the first defense; the conductor's promotion sign-off is the final defense.
3. **Theory-pull is high signal but rate-limited.** Aporia's stream caps the rate. Combinatorial and algebraic sources are unlimited but high-noise. Balance: cap each non-theory source at K candidates per run; let theory-pull saturate.
4. **The generator codifies what was previously human judgment.** This is more architecturally novel than gen_06 (which automates an existing manual practice). Expect the first implementation to teach us what works; treat first-pass output with extra suspicion.
5. **Pattern 30 (algebraic-identity coupling) inherits.** Every promoted axis is a candidate input to future correlation tests. The DAG must include the new axis's definitional lineage at promotion or the gen_06 sweep will mis-classify downstream tests.

---

## Acceptance criteria

- [ ] Modules 1–4 implemented with tests.
- [ ] First end-to-end run produces a demand-signal report, a candidate log, and ≥ 1 validation task seeded on Agora.
- [ ] `coord_invention_log.md` and `gen_11_rejected_log.md` shipped with first-pass results.
- [ ] One worked example: candidate axis proposed → validation task claimed → promoted to draft P-ID OR explicitly rejected with rationale.
- [ ] False-discovery-rate monitoring scheme documented (how the rejection log feeds back into filter tuning).
- [ ] Commit cites this spec.

---

## Composes with

- **Definition DAG (substrate primitive, prerequisite).** Gate 1 of the filter cannot operate without it. Until the DAG ships as a queryable structure, Gate 1 runs a coarse symbolic-equivalence check that misses non-obvious tautologies.
- **gen_03 (cross-domain transfer).** gen_03 ports *known* projections to new domains. gen_11 invents *novel* projections. They occupy different cells of the producer space and feed each other: a gen_11 promotion creates a new P-ID that gen_03 can then transfer.
- **gen_05 (attention-replay).** gen_05 tests killed F-IDs against new P-IDs. gen_11 supplies the new P-IDs. After every gen_11 promotion, gen_05 should fire a wave on the killed-F-ID set against the new axis.
- **gen_06 (Pattern auto-sweeps).** Mandatory companion. Every validation task seeded by gen_11 passes through gen_06's sweeps before the resulting cell lands in the tensor.
- **gen_07 (literature-diff).** Source D (theory-pull) is downstream of gen_07's classified paper stream. The two share the literature scan infrastructure.
- **gen_10 (composition enumeration).** gen_10 proposes compositions of *operators*; gen_11 proposes compositions of *coordinate systems*. They are duals — both extend the substrate's expressive vocabulary along different axes.
- **#1 Map-Elites (Tier 2, planned).** Map-Elites allocates probes across a behavior-cell grid. gen_11 extends the *axes* of that grid. Without gen_11, Map-Elites is bounded by the human-curated coordinate set; with gen_11, the grid can grow.
- **#4 Representation-invariance matrix (Tier 2, planned).** #4 checks that findings survive reparameterization. gen_11 introduces parameterizations. The two compose: every gen_11 promotion should be tested for #4 invariance against existing axes before reaching `+2@representation_stable` status.

---

## Claim instructions (paste-ready)

> Claim `gen_11_coordinate_invention_seed`. Implement Modules 1–4 of `docs/prompts/gen_11_coordinate_invention.md`. Run end-to-end on the current tensor. Commit `harmonia/coord_invention/` package + `coord_invention_log.md` + `gen_11_rejected_log.md`. Seed validation tasks for surviving candidates. Post `WORK_COMPLETE` with demand-signal count, candidate-generation counts (per source), filter-passage counts (per gate), and validation-task IDs.

---

## Version

- **v0.1 DRAFT** — 2026-04-20 — initial spec, written conversationally with James the same evening as Tier 1 generators were seeded. Marked DRAFT because (a) the Definition DAG prerequisite is not yet specified or built, and (b) the architectural novelty of inventing-what-to-measure-through is greater than any prior generator; expect the first implementation to teach us what works.
