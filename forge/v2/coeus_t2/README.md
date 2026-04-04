# Coeus T2 -- Coverage Tracking System

Coeus T2 tracks which T2 reasoning categories have passing tools, measures
tool diversity, and feeds gap analysis to Nous for prioritized concept mining.

Named after the Titan of intellect and foresight.

## Files

| File | Purpose |
|------|---------|
| `coverage_snapshot.json` | Current coverage state (auto-updated) |
| `enrichments/` | Per-tool enrichment data (future) |
| `src/` | Update scripts (future) |

## Schema: `coverage_snapshot.json`

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Semver for schema compatibility |
| `timestamp` | ISO-8601 | When snapshot was generated |
| `source` | string | Glob pattern for input verdict files |
| `thresholds` | object | Frozen thresholds at snapshot time |

### `summary`

Aggregate counts: total/covered/uncovered categories, passing tool count,
gem vs non-gem breakdown, coverage percentage.

### `categories`

Keyed by category name (from `T2_CATEGORIES` in `trap_generator_t2.py`).
Each entry:

```json
{
  "status": "covered | uncovered",
  "passing_tools": ["tool_id", ...],
  "best_score_any_tool": 0.975,
  "best_tool_any": "tool_id",
  "note": "human-readable context"
}
```

**"covered"** means at least one tool with `verdict=PASS` also passes that
specific per-category check. A tool can score 97.5% overall and still fail
an individual category.

### `passing_tools`

Array of tools with `verdict=PASS`. Each entry includes:

- `overall_score`, `seed_stability`, `categories_passed/failed`
- `primitive_stack` -- all primitives called (from ablation keys)
- `load_bearing_primitives` -- primitives where `load_bearing=true`
- `dominant_primitives` -- primitives with highest `budget_share`

### `near_miss_tools`

Tools that score >= `pass_threshold` but have `verdict=FAIL_BATTERY`.
Included because they may be gem-forging candidates or carry useful
primitives for the next generation.

### `diversity`

Pairwise Jaccard overlap of primitive stacks between all passing tools.
The overlap matrix entry:

```json
{
  "shared_primitives": [...],
  "union_size": 22,
  "jaccard_overlap": 0.273,
  "passes_diversity_check": true
}
```

`overall_diversity_index` = 1 - max(jaccard_overlap). Higher is better.
Threshold from `thresholds.py`: `max_callgraph_overlap = 0.40`.

### `gap_analysis`

- **`uncovered_categories`**: Categories where zero passing tools pass the
  per-category check. Ordered by priority (hardest gaps first).
- **`weakly_covered_categories`**: Categories with only 1 passing tool
  covering them (single-point-of-failure).
- **`nous_feed`**: Priority-ordered list of categories + strategy notes
  for the next Nous concept-mining run.

## How to update

The snapshot should be regenerated after each eval batch completes.

**Manual update:**

1. Run the T2 eval pipeline against new/updated tools
2. Read all `forge/verdicts/t2_*_verdict.json` files
3. Rebuild `coverage_snapshot.json` with the schema above
4. Commit alongside the new verdict files

**Automated update (planned):**

The `src/` directory will contain a `coeus_t2.py` script that:
1. Scans `forge/verdicts/t2_*_verdict.json`
2. Loads `forge/thresholds.py` for current thresholds
3. Computes per-category coverage from `per_category` fields in verdicts
4. Computes Jaccard diversity from ablation keys
5. Writes `coverage_snapshot.json`

This mirrors the T1 pattern in `agents/hephaestus/src/hephaestus.py` where
Coeus is triggered every N forges via `--coeus-interval`.

## Coverage semantics

A category is **covered** when at least one tool with `verdict=PASS` also
has `per_category.<category>.pass = true` in its verdict.

This is stricter than "any tool scores above threshold" -- a tool can score
97.5% overall while still failing a specific category (e.g., both gems fail
`causal_confounding_hard`). The per-category gate ensures genuine capability
coverage, not just aggregate performance.

## Current state (2026-04-03)

- 12 T2 categories in the cross-eval battery
- 2 passing tools (both gems from Claude Code forge)
- 10/12 categories covered by at least one gem
- 2 categories fully uncovered: `causal_confounding_hard`, `simpson_paradox`
- 2 categories at single-tool coverage: `causal_counterfactual`, `liar_detection`
