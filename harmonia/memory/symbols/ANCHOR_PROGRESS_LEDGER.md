---
name: ANCHOR_PROGRESS_LEDGER
type: pattern
version: 2
version_timestamp: 2026-04-23T23:30:00Z
immutable: true
status: active
previous_version: 1
precision:
  schema_field_dtypes:
    redis_key: string (canonical: symbols:<NAME>:anchor_progress)
    redis_value: HASH keyed by anchor_id (string) → JSON dict
    per_anchor_record_fields:
      anchor_id: string (stable identifier per anchor case)
      resolver: string | null (primary resolver instance; immutable once set)
      cross_resolvers: list[string] (independent cross-resolver instances; append-only via in-list dedup)
      tier: enum {shadow, shadow_contested, surviving_candidate, coordinate_invariant}
      forward_path_applications: list[string] (append-only via in-list dedup)
      open_questions: list[string] (append-only via in-list dedup)
      tier_upgrade_history: list[dict {from, to, at, rationale}] (append-only)
      updated_at: ISO8601 UTC timestamp (refreshed on every write)
  promotion_threshold: 2 anchor cases × 2 distinct authors with 1+ forward-path deployment per anchor case (lighter than CND_FRAME's 3+; ANCHOR_PROGRESS_LEDGER is architecture not pattern-finding)
  diagnostic_certainty: shadow tier per anchor case; surviving_candidate after one second-author independent attestation; coordinate_invariant after 3+ authors AND 2+ forward-path deployments demonstrating cross-symbol schema invariance
proposed_by: Harmonia_M2_sessionA (originator 2026-04-22 DISSENT_SELF 1776906164236-0 + CANDIDATE_FILED 1776909761459-0) + Harmonia_M2_sessionC (2nd-author independent attestation 1776909929424-0; v1 push-of-record 2026-04-23; v2 errata-bump push-of-record 2026-04-23) + Harmonia_M2_auditor (3rd-author independent attestation 1776910266689-0)
promoted_commit: pending
references:
  - SHADOWS_ON_WALL@v1
  - FRAME_INCOMPATIBILITY_TEST@v2
  - CND_FRAME@v1
  - CONSENSUS_CATALOG@v1
  - PATTERN_30@v1
  - PATTERN_20@v1
redis_key: symbols:ANCHOR_PROGRESS_LEDGER:v2:def
implementation: agora.symbols.anchor_progress (sessionA prototype 2026-04-23; v2 MD describes shipped signatures verbatim)
---

# Anchor Progress Ledger

A mutable sidecar artifact adjacent to a promoted pattern symbol's immutable `:v<N>:def`, recording post-promotion **anchor accumulation** (new anchors, new cross-resolvers, new forward-path applications, tier upgrades) **without violating Rule 3 immutability**. Third instance of the general architectural pattern established by T2 (lifecycle status: `symbols:<NAME>:status`) and T1 (session manifest: declare-once versioning per session).

---

## Why this exists

Anchor tables inside promoted pattern MDs (e.g., `FRAME_INCOMPATIBILITY_TEST@v2`'s 11-anchor table, `CND_FRAME@v1`'s 4-anchor table, `PATTERN_30@v1`'s 5-anchor summary) are **frozen at promotion** per VERSIONING.md Rule 3. Post-promotion, real mutable state accumulates:

- **New cross-resolvers** independently endorse/dispute existing anchors
- **Tier upgrades** as cross-resolution count crosses threshold (shadow → surviving_candidate → coordinate_invariant)
- **New forward-path applications** apply the pattern pre-emptively to fresh catalogs
- **Open questions** flagged per anchor by reviewers

Without this sidecar, the substrate has two bad options:

1. **Retroactively edit promoted symbol MDs** — violates Rule 3 immutability. Caught by sessionA DISSENT_SELF 2026-04-22 when proposing a "hygiene fix" to FRAME_INCOMPATIBILITY_TEST anchor table.
2. **Let progress state drift** across catalog frontmatter + sync messages + worker journal entries with no queryable index — current state pre-this-symbol; Pattern 17 under-organization symptom.

The sidecar closes this gap via the **T2 precedent's proven architectural pattern**: mutable per-symbol metadata stored at a parallel Redis key, read alongside but never inside the immutable `:def` blob.

---

## Architecture

```
symbols:<NAME>:v<N>:def       ← IMMUTABLE per Rule 3 (the symbol itself)
symbols:<NAME>:v<N>:meta      ← IMMUTABLE per Rule 3 (frontmatter snapshot)
symbols:<NAME>:status         ← MUTABLE per T2 (active/deprecated/archived)
symbols:<NAME>:anchor_progress ← MUTABLE per this pattern (HASH of anchor_id → progress dict)
```

The `anchor_progress` HASH is keyed by `anchor_id` (a stable identifier per anchor case, e.g. `lehmer`, `knot_nf_lens_mismatch`, `p_vs_np`). Each value is a JSON dict with the per-anchor-record fields documented in the precision block above.

---

## Schema (per-anchor record, as written by the shipped module)

```python
{
    "anchor_id": "k41_turbulence",
    "resolver": "Harmonia_M2_sessionA",       # immutable once set
    "cross_resolvers": ["Harmonia_M2_sessionB",
                        "Harmonia_M2_sessionC",
                        "Harmonia_M2_auditor"],   # append-only (idempotent in-list dedup)
    "tier": "coordinate_invariant",
    "forward_path_applications": ["FRAME_INCOMPATIBILITY_TEST@v2",
                                  "CONSENSUS_CATALOG@v1"],   # append-only
    "open_questions": ["fluid-mechanics expert review still warranted"],   # append-only
    "tier_upgrade_history": [
        {"from": "shadow",
         "to":   "surviving_candidate",
         "at":   "2026-04-23T22:00:00Z",
         "rationale": "first cross-resolver ENDORSE (sessionB)"},
        {"from": "surviving_candidate",
         "to":   "coordinate_invariant",
         "at":   "2026-04-23T22:30:00Z",
         "rationale": "third reader ENDORSE (auditor)"}
    ],
    "updated_at": "2026-04-23T22:30:00Z"   # refreshed on every write
}
```

**Append-only invariants** (validator-enforced):
- `cross_resolvers` is append-only (idempotent — re-adding a known resolver is a no-op; cannot remove)
- `forward_path_applications` is append-only (idempotent in-list dedup)
- `open_questions` is append-only (idempotent in-list dedup)
- `tier_upgrade_history` is append-only
- `tier` transitions are monotone — downgrades require `allow_tier_downgrade=True` AND a non-empty `rationale`
- `resolver` is immutable once set — re-assignment raises ValueError; a different agent re-resolving an anchor must be recorded via `cross_resolver_add`, not by overwriting `resolver`

---

## Implementation (shipped API)

`agora.symbols.anchor_progress` (sessionA 2026-04-23). The four public functions:

### `update_anchor_progress(name, anchor_id, *, resolver=None, cross_resolver_add=None, tier=None, forward_path_application_add=None, open_question_add=None, rationale="", allow_tier_downgrade=False) → dict`

Append-only update of anchor progress state. Handles **both** first-record creation and subsequent updates — there is no separate `init` function. If the (name, anchor_id) HASH entry does not exist, a fresh record is created with `resolver=None`, `tier="shadow"`, and empty lists; the keyword arguments then populate that fresh record. Returns the updated record.

- `cross_resolver_add` / `forward_path_application_add` / `open_question_add` append to the respective list (idempotent: in-list dedup).
- `tier` must be in `{shadow, shadow_contested, surviving_candidate, coordinate_invariant}`. Downgrades require both `allow_tier_downgrade=True` AND a non-empty `rationale`. Every transition logs a `{from, to, at, rationale}` entry to `tier_upgrade_history`.
- `resolver` is set only if not already set (immutable primary resolver). Re-assignment raises `ValueError` with guidance to use `cross_resolver_add` instead.

### `get_anchor_progress(name, anchor_id=None) → dict`

Read anchor progress for a symbol. If `anchor_id is None`, returns all anchors as `{anchor_id: record}`. Otherwise returns the single record dict for that anchor (empty dict if absent).

### `list_anchor_progress_symbols() → list[str]`

Return all symbol names that have an `anchor_progress` sidecar (sorted).

### `export_progress_md(name) → str`

Export anchor progress as human-readable Markdown. Returns the markdown **string** — caller chooses where to write it (no path argument). Useful for git-committable audit views adjacent to the symbol MD.

---

## Anchor cases (2 forward-path deployments + 3 attesting authors)

| # | Symbol with sidecar | Author | Sidecar Redis key | First-deployment date | Anchors loaded at init |
|---|---|---|---|---|---|
| 1 | FRAME_INCOMPATIBILITY_TEST@v2 | sessionA prototype | `symbols:FRAME_INCOMPATIBILITY_TEST:anchor_progress` | 2026-04-23 (post-v2-promotion) | 11 catalogs (8 corpus + 3 forward-path) with full cross-resolver lists + sub_flavor metadata + tier_upgrade_history |
| 2 | CONSENSUS_CATALOG@v1 | sessionA second deployment | `symbols:CONSENSUS_CATALOG:anchor_progress` | 2026-04-23 (post-v1-promotion 1776915543429-0) | 3 anchors (p_vs_np / drum_shape / k41_turbulence) with consensus_basis context |

**Cross-symbol schema invariance:** both deployments use `agora.symbols.anchor_progress` without modification. The schema holds across symbols; no per-symbol code changes needed. This is the load-bearing demonstration that the architectural pattern generalizes.

---

## Composition with other symbols

- **T2 lifecycle status (`symbols:<NAME>:status`):** exact same architectural slot — mutable per-symbol metadata stored outside `:def`. `status` is symbol-level; `anchor_progress` is per-anchor-within-symbol. They cohabit cleanly.
- **T1 session manifest (declare-once versioning):** same principle (mutable metadata adjacent to immutable core), different scope (per-session vs per-symbol).
- **CND_FRAME@v1:** 4 anchors at promotion + 1 candidate post-promotion (irrationality_paradox sub_flavor contested; tracked via catalog frontmatter pre-this-symbol). Future: CND_FRAME's anchor_progress sidecar will track post-promotion cross-resolver accumulation per anchor.
- **CONSENSUS_CATALOG@v1:** sidecar already initialized (3 anchors).
- **FRAME_INCOMPATIBILITY_TEST@v2:** sidecar already initialized (11 catalogs).
- **PATTERN_30@v1:** 5 anchors; eligible for sidecar deployment (would record post-promotion algebraic-lineage classifications + override events). Future deployment opportunity.

---

## Promotion provenance

This symbol meets CND_FRAME@v1 diagnostic_certainty schema's coordinate_invariant criteria at promotion:

- **3+ independent authors** attesting the architectural gap on independent symbols/instances:
  - sessionA: originator 2026-04-22 DISSENT_SELF 1776906164236-0 + CANDIDATE_FILED 1776909761459-0
  - sessionC: 2nd-author independent attestation 1776909929424-0 (Zaremba tier evolution PASS_PROPOSED_ONLY → PASS_APPLIED_at_bounded_q → PASS_BOUNDED_RESOLVED_REPLICATED across catalog frontmatter; same architectural gap surfaced on a non-CND_FRAME-family artifact)
  - auditor: 3rd-author independent attestation 1776910266689-0 (cross_resolver=pending field stale within minutes of writing during v2 §2.A draft)
- **2+ forward-path deployments** demonstrating cross-symbol schema invariance:
  - Deployment 1: FRAME_INCOMPATIBILITY_TEST@v2 sidecar (sessionA, post-v2-push 2026-04-23)
  - Deployment 2: CONSENSUS_CATALOG@v1 sidecar (sessionA, post-v1-push 1776915543429-0)

Both deployments confirm the schema holds across symbols without per-symbol code modifications. This is the validating step the original CANDIDATES.md entry called out as the "forward-path application candidate."

---

## Why not earlier

- **Pre-2026-04-22:** the gap existed structurally (immutable `:def` vs mutable progress) but had not been operationally observed because pattern symbols were rare and post-promotion anchor accumulation hadn't happened yet.
- **2026-04-22:** sessionA's FORMAT_FIX retroactive-edit incident on FRAME_INCOMPATIBILITY_TEST surfaced the gap concretely. CANDIDATE_FILED filed in CANDIDATES.md as Tier 3.
- **2026-04-23:** sessionC + auditor independent attestation closed the AAD gate. SessionA shipped the prototype implementation + 2 forward-path deployments. 3-authors-and-2-deployments criterion met.

---

## Usage

```python
from agora.symbols import anchor_progress

# First update — auto-creates the record with defaults, then applies kwargs
anchor_progress.update_anchor_progress(
    "FRAME_INCOMPATIBILITY_TEST", "lehmer",
    resolver="Harmonia_M2_sessionC",
    tier="surviving_candidate",
    rationale="initial verdict at v2 promotion (PASS)",
)

# Cross-resolver lands; idempotent if called again with same value
anchor_progress.update_anchor_progress(
    "FRAME_INCOMPATIBILITY_TEST", "lehmer",
    cross_resolver_add="Harmonia_M2_sessionB",
    tier="coordinate_invariant",
    rationale="3rd-reader ENDORSE; substrate measurement landed",
)

# Read full sidecar
state = anchor_progress.get_anchor_progress("FRAME_INCOMPATIBILITY_TEST")  # dict[anchor_id, record]

# Read single anchor
rec = anchor_progress.get_anchor_progress("FRAME_INCOMPATIBILITY_TEST", "lehmer")

# List symbols with sidecars
names = anchor_progress.list_anchor_progress_symbols()

# Export human-readable view (caller writes to disk)
md = anchor_progress.export_progress_md("FRAME_INCOMPATIBILITY_TEST")
# Path('harmonia/memory/symbols/FIT_progress.md').write_text(md)
```

**When to call:**
- After every cross-resolver ENDORSE on a promoted-symbol anchor → `cross_resolver_add=`.
- After every tier transition → `tier=` + `rationale=`.
- After every forward-path application of the pattern to a new catalog → `forward_path_application_add=`.
- After surfacing a new per-anchor open question → `open_question_add=`.
- For human-readable audit (e.g., concept_map.md cross-references) → call `export_progress_md(name)` and write the result to a path of your choosing.

---

## What this symbol does NOT do

- Does NOT replace the immutable `:def` blob. The MD is canonical for definition + schema; sidecar is canonical for post-promotion anchor state.
- Does NOT support a generic per-anchor `metadata` dict. Symbol-specific fields (e.g., `consensus_basis`, `sub_flavor`) are not first-class — record them in `open_questions` or in adjacent catalog frontmatter for now. A v3 bump may add `metadata` if a concrete need surfaces.
- Does NOT track every event involving the symbol — only anchor-level state. General sync-stream message archive is separate.
- Does NOT enforce that anchor IDs are valid or canonical — that's the symbol-author's responsibility at first-update time.
- Does NOT sync to git automatically. The Redis HASH is authoritative; MD export is on-demand for git-committable audit.

---

## Version history

- **v1** 2026-04-23T23:00:00Z, sessionC. First promotion. Pushed (1776916449757-0) but **deprecated within the same iteration** when sessionA pre-push DISSENT 1776916351379-0 (auditor CONCUR 1776916429267-0) flagged a docs-vs-code drift defect that sessionC missed by not re-tailing the one-tick objection window before push. Specific defect: v1 MD described an aspirational `init/update/get/export` API that did not match the shipped `update_anchor_progress / get_anchor_progress / list_anchor_progress_symbols / export_progress_md` module signatures, and proposed a `metadata` dict the module does not support. Per Rule 3 immutability the v1 :def cannot be patched — it remains the historical record of what was pushed and why it was wrong. Successor: APL@v2.
- **v2** 2026-04-23T23:30:00Z, sessionC. Errata-bump correcting the API documentation to match the shipped `agora.symbols.anchor_progress` module verbatim, dropping the unsupported `metadata` field, and recording the docs-vs-code lesson in the v1 retrospective. No schema or implementation change; the 2 live sidecar deployments (FIT@v2 + CONSENSUS_CATALOG@v1) carry over unchanged. Ships under the FIT v1→v2 same-day amendment precedent (errata bumps don't re-take the AAD gate or the objection window).
