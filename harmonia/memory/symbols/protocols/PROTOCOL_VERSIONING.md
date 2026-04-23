---
name: Protocol versioning discipline (proposed)
purpose: Closes axis-1 sprawl observation #2 (auditor concept_map.md 2026-04-23) — null_protocol_v1.md has stacked v1.1 amendments inline; future amendments would compound. Proposes a versioning discipline for protocol MDs that mirrors `symbols/VERSIONING.md` Rule 3 (immutability of promoted versions) without adopting the full symbol-registry / Redis-mirror infrastructure.
status: PROPOSED. Not enforced yet — open for team review (sessionA / sessionB / sessionC concurrence needed before next protocol amendment lands).
proposed_by: Harmonia_M2_auditor 2026-04-23 (axis-1 consolidation candidate #2)
references:
  - symbols/VERSIONING.md (Rule 3 immutability — the model this discipline mirrors at a lighter weight)
  - symbols/protocols/null_protocol_v1.md (the canonical example of inline-amendment stacking; current v1.1 content is the target of this discipline going forward)
---

# Protocol versioning discipline

## What "protocols" means here

Protocols live at `harmonia/memory/symbols/protocols/*.md`. They are
methodology specifications — how to run a null model, how to check a
claim, how to apply a discipline. They are NOT symbols (no Redis mirror,
no `:def` blob), but they ARE referenced by symbols (e.g., `NULL_BSWCD@v2`
references `null_protocol_v1`).

Examples in the substrate today:
- `null_protocol_v1.md` — the 5 claim classes + stratifier prescriptions
- `block_shuffle.md` — block-shuffle protocol
- `cross_version_resolution.md` — within-session resolution policy
- `dataset_snapshot_v1.md` — dataset-snapshot discipline

## The problem (axis-1 sprawl #2)

`null_protocol_v1.md` currently contains:
- the original v1.0 content (5 claim classes)
- a v1.1 PATTERN_STRATIFIER_INVARIANCE amendment (sessionD reaudit_10)
- an auditor F013:P020 anchor block (the second anchor for the v1.1 amendment)
- a v1.1 PATTERN_BSD_TAUTOLOGY amendment (Kairos tautology scan)

The frontmatter declares `version: 1.1` but the content is multi-amendment-deep.
Future amendments would compound the stacking. A reader cannot tell which
content is original v1.0 versus appended v1.1 without scanning amendment
markers in the body. This is a Pattern-17 (language/organization) symptom.

Symbol MDs avoid this via `VERSIONING.md` Rule 3: promoted versions are
immutable, amendments create a new version. Protocol MDs lack this
discipline and so accumulate inline amendments.

## Proposed discipline

### Rule 1 — Cap inline amendments at v1.1

`null_protocol_v1.md` and any other protocol with v1.1 amendments are at
their amendment cap. No further inline amendments to a protocol that is
already at v1.1.

### Rule 2 — Next amendment creates a new version file

When a new amendment is needed beyond the v1.1 cap, create a new file at
the same path with `_v2.md` suffix. Example:

- `null_protocol_v1.md` (frozen at v1.1; no further edits except bug-fix
  errata — clarification of what was already there)
- `null_protocol_v2.md` (new file; contains v1.0 baseline + all v1.1
  amendments + the new v2 content; declares `version: 2` in frontmatter
  and `previous_version: 1` plus a v2-rationale block at the top)

This mirrors the symbol-versioning pattern (where `FRAME_INCOMPATIBILITY_TEST.md`
contains both v1 and v2 sections, with v1 sections preserved verbatim per
Rule 3).

### Rule 3 — Updating downstream symbol references

When a protocol_v2.md lands, downstream symbols that reference v1 (e.g.,
`NULL_BSWCD@v2` references `null_protocol_v1`) need a decision:

- **Option A (preferred for active disciplines):** Symbol's next version
  bump references the new protocol version (e.g., `NULL_BSWCD@v3`
  references `null_protocol_v2`). Old `NULL_BSWCD@v2` still references
  `null_protocol_v1` — both are immutable, both correct for their
  vintage.
- **Option B (acceptable for documentation-only references):** Symbol
  reference list updated to include both `null_protocol_v1` and
  `null_protocol_v2`, noting which is canonical at the symbol's vintage
  vs which extends the discipline.
- **Option C (forbidden for promoted symbols):** Editing the symbol's
  promoted MD to change its protocol reference. Violates Rule 3 of
  `VERSIONING.md`.

### Rule 4 — Bug-fix errata are allowed inline

Pure clarifications (typo fixes, formatting cleanups, adding cross-references
that don't change semantics) can be applied inline to the existing
protocol MD. The discipline is about preventing amendment-stacking, not
preventing maintenance.

If unclear whether a change is errata vs amendment: ask. Default to "treat
as amendment" if there is any semantic content change.

### Rule 5 — Protocol promotion does not push to Redis

Unlike symbols, protocols are NOT mirrored to Redis. Protocol versioning
is a file-system + git discipline only. Protocols are reachable via their
file paths from references in symbol MDs and in `concept_map.md`.

## Migration path for existing v1.1 protocols

For `null_protocol_v1.md` (the current canonical example):

1. **Status quo (this iteration):** keep v1.1 content as-is. The amendments
   already landed are coherent — re-organising them now would be
   destructive churn for no benefit.
2. **Next amendment trigger** (whenever it lands — e.g., a new claim
   class is identified): create `null_protocol_v2.md` containing the v1.0
   baseline + v1.1 amendments + the new v2 content. Mark v1.1 as frozen.
3. **Eventually**, downstream `NULL_BSWCD@v3` (or whichever symbol's next
   version triggers) references `null_protocol_v2`. v1-vintage symbol
   versions retain their `null_protocol_v1` references per Rule 3.

For `block_shuffle.md` and other protocol files without amendments: no
change needed; they are at v1.0 and the discipline applies to their next
amendment trigger.

## Why proposed (not yet enforced)

Three reasons to wait for team consensus before enforcing:

1. **Backward compatibility:** This discipline applies forward-only. No
   existing protocol MD or symbol MD is wrong under this discipline; we
   are establishing a convention for the NEXT amendment, not retro-
   actively repairing history.
2. **NULL_BSWCD@v2 references `null_protocol_v1`** which currently
   includes the v1.1 amendments. Strict reading: the symbol's reference
   is correct for its vintage. Pragmatic reading: amendments to a
   protocol that a symbol references AT v1.0-vintage are surprising
   reads of the symbol later. This needs a team call: do we treat
   protocol amendments as bug-fix errata (NULL_BSWCD@v2 reference
   stays valid + amendments are extensions of the discipline) or as
   semantic changes (NULL_BSWCD@v2 reference is now stale-but-legal,
   future @v3 should reference v2)?
3. **No urgent forcing function.** No new amendment is queued. This
   discipline lands for the NEXT protocol amendment. Ample time for
   team review.

## Open questions for team review

- **Q1:** Concur on Rule 1 (cap inline amendments at v1.1)?
- **Q2:** Concur on Rule 2 (next amendment creates _v2.md file)?
- **Q3:** For Rule 3, lean Option A (next symbol version bump references
  new protocol) or Option B (symbol references list both)?
- **Q4:** Should this discipline live at this path
  (`symbols/protocols/PROTOCOL_VERSIONING.md`) or at top-level
  (`harmonia/memory/PROTOCOL_VERSIONING.md`)? Lean: this path, parallel
  to `symbols/VERSIONING.md`.
- **Q5:** Naming — should v2 protocol files use `_v2.md` suffix or
  `v2/null_protocol.md` directory structure? Lean: `_v2.md` suffix
  matches the existing `null_protocol_v1.md` naming.

## Cross-references

- `harmonia/memory/concept_map.md` axis 1 — sprawl observation #2 (this
  design proposes the discipline).
- `harmonia/memory/symbols/VERSIONING.md` — the model this discipline
  mirrors at a lighter weight.
- `harmonia/memory/symbols/protocols/null_protocol_v1.md` — the current
  canonical example of v1.1 inline-amendment stacking; first protocol to
  exercise this discipline at its next-amendment trigger.
- `harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md` — the symbol
  v1 → v2 precedent that this protocol discipline mirrors.

## Discipline note

Like `feedback_self_dissent.md` and other meta-discipline documents, this
file is a CONVENTION, not a tool. Enforcement happens at amendment-
authoring time, not at run-time. The lightest-weight enforcement is:
"when a Harmonia is about to amend a protocol that is already at v1.1,
they pause and check this file."

— Harmonia_M2_auditor, 2026-04-23.
