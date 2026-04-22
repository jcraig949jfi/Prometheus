# Cross-Version Resolution Policy

**Status:** active (T3, wave 0 — 2026-04-22)
**Owner:** Harmonia_M2_sessionB under task `harmonia_T3_cross_version_policy`
**Depends on:** T1 `harmonia.symbols.manifest` (sessionD); T2 status lifecycle (sessionB)
**Source:** `harmonia/memory/external_review/responses_symbol_compression_20260421.md` §R3

---

## Why this exists

VERSIONING.md Rule 2 requires every reference to a symbol to carry
`@v<N>`. T1's session manifest relaxes that at prose density: a
`---\nuses:\n  NULL_BSWCD: 2\n---` block at the top of a document
binds bare-name mentions to authoritative versions, so the body can
say `NULL_BSWCD` instead of `NULL_BSWCD@v2` dozens of times.

That trade creates a new failure mode: **what happens when the
manifest binds `NAME: v2` but the body also contains the explicit
`NAME@v1`?** Sessions routinely cite stale findings (which referenced
an older version) alongside fresh code (which uses the new version).
Both references are correct *in context* — the older finding really
did use `@v1`; the new code really does use `@v2`. The ambiguity is
about which one the **bare-name** mentions elsewhere in the text
resolve to.

This doc pins the resolution rules. Not aspirational — these rules
are already enforced by the code shipped under T1 (`agora/symbols/manifest.py`).
This doc names them so reviewers, future Harmonia instances, and
HITL can cite the policy instead of reverse-engineering the behavior.

---

## The five rules

### Rule 1 — Explicit always wins over implicit

An inline `NAME@v<N>` reference is authoritative for that exact
occurrence. The manifest never overrides an explicit reference.

Concretely:

```python
>>> manifest = {'NULL_BSWCD': 2}
>>> resolve_with_manifest('NULL_BSWCD@v1', manifest)   # explicit
<dict for NULL_BSWCD@v1>                                # manifest ignored
>>> resolve_with_manifest('NULL_BSWCD', manifest)      # bare
<dict for NULL_BSWCD@v2>                                # manifest binds
```

**Rationale:** the inline `@v<M>` is the author's intentional cast —
"for THIS sentence, I mean v1, regardless of what the session-default
is." Treating the explicit form as the override preserves the
citation of historical findings without requiring a separate `as`
keyword. `NAME@v<N>` IS the "as cast" R3 proposed.

### Rule 2 — Manifest binds only bare names

A bare `NAME` in prose or code resolves to `NAME@v<manifest[NAME]>`
if the manifest covers it. If the manifest does not cover it, the
bare reference falls through to `resolve(NAME)` which returns the
latest-promoted version with a `UserWarning` (Rule 2 of
`VERSIONING.md` — unversioned references are discipline violations).

### Rule 3 — Conflicts are detected, not repaired

When both a manifest entry `NAME: <M>` AND an inline `NAME@v<K>`
with `K != M` are present in the same document, a
`CrossVersionConflict` warning (a `UserWarning` subclass) is emitted
during `expand_references` / `contract_references`. The warning is
**informational, not fatal**:

- `expand_references`: bare `NAME` is rewritten to `NAME@v<M>`
  (manifest wins for bare); inline `NAME@v<K>` is preserved as-is
  (Rule 1).
- `contract_references`: inline `NAME@v<K>` is preserved; bare
  names already present in the text remain bare (they were covered
  by the manifest at ingest).

**Rationale:** conflict between "a stale reference" and "a live
manifest" is almost always intentional (the author is explicitly
citing an older version). Forcing reconciliation would corrupt
citations. A warning flags the spot for review without breaking the
document.

### Rule 4 — Session-level multi-version is legal

A session may legitimately reference `NULL_BSWCD@v1` (audit of an
old finding) and `NULL_BSWCD@v2` (new analysis under the corrected
null) in the same document. This is **not** a conflict — both are
explicit, each resolution is independent, and the outputs of the
two versions coexist by design (Rule 3 of `VERSIONING.md`:
promoted versions are immutable, so older versions remain valid for
their historical citations).

The "conflict" case is *only* when a bare name and an explicit
version disagree on what the bare name means — not when two
explicit versions appear side-by-side.

### Rule 5 — Cross-version does NOT cross the type boundary

If code or callable contracts expect a specific version (e.g. a
function signature typed as `NULL_BSWCD@v2`-shaped input), a call
site that happens to have `@v1` content in scope is not
automatically compatible. The receiver must decide: upgrade,
reject, or route through a compatibility layer. The resolver does
NOT manufacture cross-version coercion.

**Rationale:** Rule 3 of `VERSIONING.md` (immutability) is the
substrate; callable-level compatibility is a higher-level contract.
A compatibility layer — when one exists — belongs at the module
that owns the contract, not in the symbol registry.

---

## Where each rule is enforced

| Rule | Enforced by | Mechanism |
|:-:|:--|:--|
| 1 (explicit wins) | `manifest.resolve_with_manifest` | Early-return on `@v` presence; manifest path only runs on bare names |
| 2 (manifest binds bare) | `manifest.resolve_with_manifest` | Lookup in `manifest` dict before falling through to `resolve()` |
| 3 (conflicts detected) | `manifest.expand_references` + `manifest.contract_references` + `manifest.find_conflicts` | `warnings.warn(..., CrossVersionConflict)` on mismatch |
| 4 (multi-version legal) | Rule 3 of VERSIONING | No enforcement needed; immutable versions make it natural |
| 5 (no auto-coerce) | *absence of a coercion layer* | By design: symbol registry does not wrap values |

The `find_conflicts()` helper returns a list of conflict dicts
(without emitting warnings) for programmatic auditing.

---

## Worked test case — stale v1 ref alongside fresh v2 code

Scenario: a session document cites the F043 retraction audit (which
referenced `NULL_BSWCD@v1`) alongside fresh per-cell re-audits
running under `NULL_BSWCD@v2`. The manifest declares v2.

```text
---
uses:
  NULL_BSWCD: 2
  PATTERN_30: 1
---

Retrospective: F043 was retracted on 2026-04-19 when NULL_BSWCD@v1
failed to break the algebraic coupling (PATTERN_30 Level-3). The
current sweep under NULL_BSWCD catches Level-3 at the ingest gate;
PATTERN_30 sweeps run on every promotion.
```

Expected behavior:

- `parse_session_manifest(text)` returns `{'NULL_BSWCD': 2, 'PATTERN_30': 1}`
- `expand_references(body, manifest)` rewrites the bare `NULL_BSWCD`
  in the last sentence to `NULL_BSWCD@v2` (manifest binds bare).
- The explicit `NULL_BSWCD@v1` in the first sentence is preserved
  (Rule 1).
- `expand_references` emits **one** `CrossVersionConflict` warning
  pointing at position of the `@v1` citation (informational, per
  Rule 3).
- `find_conflicts(body, manifest)` returns
  `[{'name': 'NULL_BSWCD', 'inline_version': 1, 'manifest_version': 2, 'position': <N>}]`.
- `resolve_with_manifest('NULL_BSWCD@v1', manifest)` → dict for v1.
- `resolve_with_manifest('NULL_BSWCD', manifest)` → dict for v2.

See `tests/test_cross_version_resolution.py` for the executable
round-trip covering these assertions.

---

## What this policy does NOT do

- **Does not auto-migrate citations.** If an old document says
  `NULL_BSWCD@v1` and v1 is later deprecated (T2 status field), the
  reference still resolves (with a DeprecationWarning). Rewriting
  the old citation is the author's call.
- **Does not prevent authorial error.** A document with `uses: NULL_BSWCD: 2`
  and body containing "NULL_BSWCD@v1 (see table 3)" will warn about
  the conflict at expansion, but the warning assumes the author
  knew what they were doing. If they didn't, the warning surfaces it.
- **Does not synthesize an `as` keyword.** The current_wave R3 hint
  suggested an `as` cast mechanism; the implementation realized
  that inline `@v<M>` already serves that purpose. No new syntax.
- **Does not extend to non-symbol references.** F-ID / P-ID /
  Pattern_<n> references are versioned by commit-hash
  (`F011@c1abdec43`), not version integer, until tier-2 retrofit.
  Manifest scope is symbol-only for now.

---

## Relationship to T2 lifecycle status

T2's `status` field (active / deprecated / archived) is **orthogonal**
to cross-version resolution:

- A deprecated symbol still resolves at each version via
  `resolve_with_manifest`; DeprecationWarning fires per-resolve.
- An archived symbol blocks unless `include_archived=True` is
  passed through. `resolve_with_manifest` accepts the flag and
  forwards it.
- Manifest entries do **not** carry status expectations. If a
  session manifest binds `NAME: 1` but `NAME@v1` has since been
  archived, the resolve at that version raises
  `SymbolArchivedError` (T2 behavior), not a cross-version conflict.

---

## Interaction with sessionE's SYNC_SCHEMA_DRIFT observation

sessionE flagged (2026-04-22) that the Agora sync stream has 4
distinct field-schema conventions in concurrent use — orthogonal
to symbol resolution but adjacent evidence of the same class of
failure: drift from under-specified schemas. This policy doc
addresses the symbol-registry slice; the sync-stream slice is
appropriate subject matter for a sibling mini-task (T5 candidate).

---

## Version history

- **v1** — 2026-04-22 (T3, wave 0). Codifies the behavior shipped
  in T1's `manifest.py` as the authoritative policy. No code
  changes introduced under T3 beyond this doc and the test file;
  all mechanism ships under T1.
