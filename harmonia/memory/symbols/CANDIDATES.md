# Symbol Candidates — Proposed but Not Yet Promoted

**Status:** Living catalog of symbol candidates surfaced from session work.
**Promotion criterion:** ≥ 2 agents reference in committed work OR drafter + reviewer sign-off, per `OVERVIEW.md`.
**Convention:** when a candidate promotes, move its entry to `INDEX.md` and write its `<NAME>.md`. Keep the entry here as a stub linking to the promoted version, so the proposal history is preserved.

---

## Why this file exists

The substrate produces more candidate symbols than it can responsibly promote in a single session. Each candidate represents a compression that a generator, a sweep, or a reviewer would benefit from — but premature promotion fills the registry with bloat. This file catalogs proposals so they are discoverable to other Harmonia sessions, can accumulate the second-reference required for promotion organically, and don't get re-derived from scratch each cold-start.

**North-star alignment** (from `user_prometheus_north_star.md`): every symbol promoted should be a *coordinate system of legibility*, not a law. A candidate that names a shape we keep recognizing is on-frame. A candidate that names a finding we want to celebrate is reward-signal capture and should be rejected at this layer.

---

## Tier 1 — load-bearing for in-flight infrastructure (gen_11 / Definition DAG)

### `VACUUM` (shape) — **PROMOTED 2026-04-20** → see [VACUUM.md](VACUUM.md)

Invariance row of uniform +1 (or +2) across all walked projections, signalling the resolving axis is outside the catalog. Operationalizes Pattern 18 as a queryable diagnostic. Drives gen_11's demand reader.

### `EXHAUSTION` (shape) — **PROMOTED 2026-04-21** → see [EXHAUSTION.md](EXHAUSTION.md)

Negative-side sister to VACUUM: ≥ 3 kills clustered in one axis class with ≥ 1 surviving class for redirect. Operationalizes Pattern 13. Two anchors at promotion (F011 family-level cluster, F010 aggregation cluster).

### `AXIS_CLASS` (constant — categorical taxonomy) — **PROMOTED 2026-04-21** → see [AXIS_CLASS.md](AXIS_CLASS.md)

Controlled vocabulary classifying coordinate types: 10 values (family_level, magnitude, ordinal, categorical, stratification, preprocessing, null_model, scorer, joint, transformation). Tagging audit of all 37 promoted P-IDs pending as a worker task — required for v1 status to be fully operational.

### `GATE_VERDICT` (signature) — **PROMOTED 2026-04-21** → see [GATE_VERDICT.md](GATE_VERDICT.md)

Standardized three-valued filter output: CLEAR / WARN / BLOCK with rationale, raised_by, optional override_token. Used by gen_06 sweeps, gen_11 filter, future Pattern 21 automation. Override protocol mandates recorded hash; silent bypass forbidden.

---

## Tier 2 — pre-existing INDEX.md gaps newly anchored by today's work

### `CLIFF` (shape) — pending second anchor

- **Definition:** sharp step-change at a single stratum boundary; non-ladder structural sibling to `LADDER@v1`. Where LADDER is monotone-and-smooth, CLIFF is monotone-and-discontinuous.
- **Fields:** `axis, boundary_stratum, pre_value, post_value, jump_ratio, n_pre, n_post, block_null_z`
- **Diagnostic threshold:** `jump_ratio ≥ 3.0` AND adjacent strata within 20% AND `block_null_z ≥ 3` AND `min(n_pre, n_post) ≥ 100`.
- **Anchor:** F014 num_ram boundary at k=3 (minimum jumps from 1.216 at num_ram=1,2 to 1.267 at num_ram=3, then 1.800 at num_ram=5). Today's coord-invention discussion sharpened this as the canonical CLIFF instance.
- **Composes with:** `LADDER@v1` (contrast — both monotone, different smoothness), `EXHAUSTION` (a CLIFF in axis-class space looks like exhaustion at the boundary)
- **Why not promoted yet:** needs a second anchor outside F014 to avoid single-specimen pattern.
- **Proposed by:** Harmonia (gaps list, 2026-04-19); re-anchored 2026-04-20

### `SUBFAMILY` (shape) — **PROMOTED 2026-04-21** → see [SUBFAMILY.md](SUBFAMILY.md)

Tail enrichment/depletion within a parent stratum. Three anchors at promotion (F042 CM disc=-27 enrichment, T4 low-L tail observation, F043 surviving empirical kernel). Mandatory Pattern 30 severity check (≤ 1) prevents F043-class failure mode at scale.

---

## Tier 3 — useful but can stay informal until consumer ships

### `DEMAND_SIGNAL` (signature) — defer until gen_11 implementation reveals stable schema

- **Definition:** tuple schema for what gen_11's demand reader emits per F-ID. Composition over `{VACUUM, EXHAUSTION, OUTLIER}`.
- **Why defer:** schema should follow the implementation, not lead it. Pin after first gen_11 run reveals which fields actually matter.

### `CANDIDATE_AXIS` (signature) — defer until gen_11 implementation

- **Definition:** tuple schema for gen_11 generator output: `{name, definition (sympy expression), source ∈ {combinatorial, algebraic, specimen, theory, kill_inversion}, expected_discriminates: list[F-ID], generator_module}`
- **Why defer:** same reasoning as DEMAND_SIGNAL.

### `NEAR_DUPLICATE` (shape) — filter-internal, low promotion value

- **Definition:** a candidate axis with high stratification overlap with an existing P-ID (ARI > 0.85).
- **Why defer:** lives inside gen_11's filter Gate 3. Symbolizing it is bookkeeping unless a second consumer appears.

---

## Tier 4 — pre-existing gaps still on the shelf (from INDEX.md)

For visibility; these have been on the gaps list since the registry was first promoted:

- **`NULL_BSWR`** — block-shuffle-within-rank variant of NULL_BSWCD. Needed for any rank-cohort claim where conductor-decile stratification doesn't apply. Promotion = first implementation + rank-cohort smoke test.
- **`Q_EC_R12_D5`** — rank ∈ {1, 2} version of `Q_EC_R0_D5@v1`. Needed for F041a-class work that crosses rank cohorts.
- **`ZBLOCK`** — z-score computed via NULL_BSWCD. A unit/operator that the SIGNATURE schema currently records as `z_score` without tying to its null. Promotion = SIGNATURE@v2 with explicit null-attribution per z-score.
- **`BATCH`** — set of findings grouped for literature audit (Pattern 28/29 anchor). Promotion = first batch literature-audit lands and the grouping criterion is pinned.

---

## Cross-disciplinary candidates from `methodology_toolkit.md`

The toolkit catalogs six tools (`KOLMOGOROV_HAT`, `CRITICAL_EXPONENT`, `CHANNEL_CAPACITY`, `MDL_SCORER`, `RG_FLOW`, `FREE_ENERGY`) that are not yet promoted symbols but are scoped into `gen_09_cross_disciplinary_transplants`. Their promotion path is *through* gen_09 implementation: when a tool ships, it promotes as a symbol and migrates from the toolkit to `INDEX.md`. The toolkit is the staging area for those; this file is the staging area for substrate-internal candidates.

---

## Promotion workflow

1. A candidate's second reference appears in committed work, OR a drafter + reviewer sign off.
2. Drafter writes `<NAME>.md` following the existing `LADDER.md` template (frontmatter + Definition / Derivation / References / Data / Usage / Version history).
3. Run `python -m agora.symbols.push harmonia/memory/symbols/<NAME>.md`.
4. Add to `INDEX.md` "By type" table.
5. Reduce this file's entry for that symbol to a stub linking to the promoted MD.

---

## Version history

- **v1.1** — 2026-04-21 — five symbols promoted in the next wave (EXHAUSTION, AXIS_CLASS, GATE_VERDICT, SUBFAMILY) alongside the original VACUUM. Tier 1 fully landed. Definition DAG architecture spec shipped at `harmonia/memory/architecture/definition_dag.md` (separately from the symbol registry — substrate primitive, not symbol).
- **v1.0** — 2026-04-20 — initial catalog. VACUUM promoted in same tick. Eight other candidates documented across four tiers.
