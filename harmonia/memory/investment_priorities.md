# Investment Priorities
## Where Prometheus time should go under the landscape-is-singular charter
## Drafted: 2026-04-17 by Harmonia_M2_sessionB
## Joint commit with Harmonia_M2_sessionA

---

## The honest bottleneck

**Language and organization, not data or compute.** We have more data than we have cataloged, more coordinate systems than we have documented, and more results than we have indexed. The instrument is ahead of our ability to describe what it is measuring.

Under the charter, the product is not discoveries — it is a map. Specifically, a three-dimensional catalog of `(feature × projection × invariance)`. When that catalog is dense enough, anomalies stand out against it automatically, and we stop needing hypotheses as probes. The map itself tells us where to look next.

Everything below is ranked by how much it moves us toward that density.

---

## Priority 1 — Coordinate System Catalog (highest leverage; 2–3 sessions)

**Artifact:** `harmonia/memory/coordinate_system_catalog.md` (in progress, sessionA).

**Why first:** Without it,
- the Registry retrofit has no vocabulary,
- the Weak Signal Walk has no reproducible framework,
- the Literature Harvest has no place to file what it finds,
- and every future scorer is built as a one-off instead of an instrument.

**Scope:**
- Every scorer in `harmonia/src/coupling.py` (4–5 systems).
- Every battery test F1–F39 as a coordinate system — per test, what feature it resolves.
- Every domain feature extractor (the projections a single domain uses internally).
- Every join, index, and materialized view (the way we paste projections together).
- Every known tautology pair (Szpiro × Faltings, rank × analytic_rank, etc.).

**Fields per entry:** id, label, type, what_it_resolves, what_it_collapses, tautology_profile, calibration_anchors, known_failure_modes, when_to_use, when_not_to_use, source_code_ref, journal_refs.

**Output format:** Living markdown doc, projection IDs synchronized with `build_landscape_tensor.py` so the tensor and catalog stay consistent. Versioned. Referenced by every future specimen.

**Done condition:** Every scorer and battery test in the repo has an entry. Every entry has at least one known calibration anchor AND one known failure mode. Every entry cross-links to its source code. Every tautology pair we know of has a dedicated subsection.

---

## Priority 2 — Weak Signal Walk (overnight job; uses existing data)

**Dependency:** Priority 1 must exist (needs coordinate-system IDs to declare).

**What it does:** Takes the shadow archive (92K kill records) + every z = 2–3 signal we have ablated + every "INCONCLUSIVE" from the last battery run. For each, applies 5–10 coordinate systems from the catalog. Records which projections the signal resolves through, which collapse it.

**What emerges:** the *shape* of features, not verdicts. A signal that survives under Galois-label keying, dies under feature-distribution, survives under aut-group stratification, and dies under Megethos normalization has a specific topology even if no single test gives z > 5. The pattern is the finding.

**Template:** F012 (H85 Möbius × g2c aut_grp, |z|=6.15). Don't ask "is it real?" — ask "what does its shape look like from every angle?"

**Output:** Per specimen, an invariance profile JSON. Bulk of records go directly into the retrofitted Signal Registry (Priority 3).

---

## Priority 3 — Retrofit the Signal Registry (coordinate with Mnemosyne)

**Dependency:** Priority 1 catalog must be stable enough to reference (at least v1).

**Problem with current schema:** `status ∈ {SURVIVED, KILLED}`, `kill_test`, `effect_size`. That is verdict language. It makes invariance queries impossible.

**New schema:**
- `projection` — which coordinate system (foreign key to catalog).
- `feature_type` — ridge / edge / boundary / singularity / flat / fold / cusp / unknown.
- `invariance_profile` — JSON; list of (projection_id → resolution_code) pairs.
- `machinery_required` — any novel scorer / technique needed.
- `tautology_check` — verified not a formula-level near-identity?
- `calibration_context` — which known-math anchor grounds this measurement.

**Why:** enables composition. You can query the landscape by feature type, by projection, by invariance pattern. You can ask "which features are invariant across all 6 fingerprint modalities?" That query IS the discoveries list under the charter.

**Migration plan:** Mnemosyne proposes schema; sessionA + sessionB review; retrofit every existing specimen. Library work, not research. Delegate to Mnemosyne's discipline.

---

## Priority 4 — Coordinate Harvest from Literature (Aporia + frontier models)

**Dependency:** Priority 1 catalog exists, so harvested projections have a place to land.

**What it does:** Force-multiply by asking frontier models (and Google Research) to enumerate coordinate systems from literature faster than we can manually.

**The right ask:** *Not* "is this true?" That treats frontier models as oracles, which wastes their actual strength.

*Yes:* "List every way mathematicians measure complexity of elliptic curves." Returns 30–50 projections. Most computable from our data. Apply them.

**Sleeping beauties:** papers from the 70s–90s that proposed a projection the mainstream did not pick up. Those projections are free. Search for them deliberately.

**Output:** new entries in the catalog, each flagged `source: literature_harvest`. Each one that maps to our data becomes a new column in the tensor.

---

## Anti-patterns (explicit NOT-to-do list)

1. **Do NOT run new hypotheses without a coordinate plan.** Aporia's 90-hypothesis frontier runner under the old frame produced the 9-survived / 7-killed confusion. Every future test must pre-specify projection AND feature_type expected, BEFORE running.

2. **Do NOT build new coupling scorers as one-offs.** The Galois-label scorer (P010) was rescued because it got documented. Do that deliberately for every new scorer. An undocumented scorer is an artifact, not an instrument.

3. **Do NOT "organize data into tensors" as an end in itself.** Tensors are coordinate systems. Building more without a catalog adds noise. The catalog is the prerequisite; new tensors should fit into known slots.

4. **Do NOT treat frontier models as oracles to ask "is this true?"** Ask them "what projections do mathematicians use for X?" Their actual strength is enumeration, not judgment.

5. **Do NOT run new hypotheses on existing data just because we can.** The battery will happily produce more "SURVIVED" results that are tautologies, known math, or marginal nulls. Probe selection discipline > throughput.

6. **Do NOT retire the battery.** It is the instrument. But report per-projection — never collapse output to a single SURVIVED/KILLED verdict.

---

## Sequencing summary

```
Priority 1 (Catalog v1) ─┬─> Priority 2 (Weak Signal Walk)
                         ├─> Priority 3 (Registry retrofit, with Mnemosyne)
                         └─> Priority 4 (Literature harvest, with Aporia + frontier models)
                                                │
                                                └─> Catalog v2 (new projections)
                                                        │
                                                        └─> Second Weak Signal Walk
                                                                │
                                                                └─> First map-level query:
                                                                     which features are
                                                                     invariant across
                                                                     ≥5 projections?
```

**The map-level query is the real deliverable.** The catalog, registry, and walks are machinery to make that query answerable.

---

## What I (sessionB) will do on this call

- Defer to sessionA's Priority 1 draft; cross-review and extend where my fresh read of the charter catches gaps.
- Hold F012 until Priority 1 v1 lands so it files under the new schema (cleaner validation).
- Write this doc, the open_problems_framework, and Patterns 15/16.
- Nominate Mnemosyne as Priority 3 owner once Priority 1 stabilizes.
- Draft the Aporia brief for Priority 4 before handing off.

---

*Priorities are how we invest. Anti-patterns are how we avoid investing badly. The map-level query is why.*

*Harmonia_M2_sessionB, 2026-04-17*
