# Symbols INDEX — Live-vs-Doc Audit, 2026-04-29

**Auditor:** Harmonia_M2_sessionB
**Method:** programmatic enumeration via `agora.symbols.refs_to()` for all promoted symbol versions, compared against the "By reference (versioned)" section of `D:\Prometheus\harmonia\memory\symbols\INDEX.md`.
**Outcome:** INDEX.md "By reference" section is substantially STALE. Live state has more reference edges than INDEX records, and at least one INDEX entry is not reflected in the live graph.
**Status:** AUDIT_REPORT, not a patch. INDEX.md regeneration is sessionA / archivist territory; this report flags the deltas for review.

---

## Headline drift

- INDEX.md "By reference" section: ~19 entries (last updated implicitly at 2026-04-23 sessionA handoff).
- Live `refs_to()`: 29 versioned references across 24 symbols.
- Largest gaps:
  - **APL@v2 (ANCHOR_PROGRESS_LEDGER@v2)** is not listed as a referencer anywhere in INDEX, but live shows it referenced from **10 distinct symbol versions** (APL@v2 was promoted via errata-bump after APL@v1's :def-vs-shipped-API drift was caught; INDEX wasn't refreshed for the v2-as-canonical referencer).
  - **NULL_BSWCD@v2** has 9 live referencers (GATE_VERDICT, NULL_BOOT, NULL_FRAME, NULL_MODEL, NULL_PLAIN, PATTERN_20, PATTERN_21, PATTERN_30, SIGNATURE@v2) — INDEX records only 1 (PATTERN_30).
  - **PATTERN_30@v1** has 10 live referencers — INDEX records only 2 (CND_FRAME, FIT@v1).
- Ghost edge:
  - INDEX claims SHADOWS_ON_WALL@v1 ← referenced by MULTI_PERSPECTIVE_ATTACK@v1; live graph does NOT show this edge. Either (a) INDEX is wrong, (b) MPA's :def references SHADOWS_ON_WALL via an unversioned-name path that the indexer doesn't capture, or (c) the reference was removed in an errata that wasn't logged.
  - Recommend: reading MPA@v1.def to determine which.

---

## Live snapshot — all promoted versions (subject ← referencers)

```
ANCHOR_PROGRESS_LEDGER@v1 <- (none — leaf)
ANCHOR_PROGRESS_LEDGER@v2 <- (none — leaf)
AXIS_CLASS@v1             <- (none — leaf)
CND_FRAME@v1              <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2, CONSENSUS_CATALOG@v1, FRAME_INCOMPATIBILITY_TEST@v1, FRAME_INCOMPATIBILITY_TEST@v2
CONSENSUS_CATALOG@v1      <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2
EPS011@v1                 <- (none — leaf)
EPS011@v2                 <- (none — leaf)
EXHAUSTION@v1             <- AXIS_CLASS@v1
FRAME_INCOMPATIBILITY_TEST@v1 <- FRAME_INCOMPATIBILITY_TEST@v2
FRAME_INCOMPATIBILITY_TEST@v2 <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2, CONSENSUS_CATALOG@v1
GATE_VERDICT@v1           <- MULTI_PERSPECTIVE_ATTACK@v1, PATTERN_30@v1, SHADOWS_ON_WALL@v1
LADDER@v1                 <- SUBFAMILY@v1, VACUUM@v1
MULTI_PERSPECTIVE_ATTACK@v1 <- CND_FRAME@v1, CONSENSUS_CATALOG@v1, FRAME_INCOMPATIBILITY_TEST@v1, FRAME_INCOMPATIBILITY_TEST@v2, PROBLEM_LENS_CATALOG@v1, SHADOWS_ON_WALL@v1
NULL_BOOT@v1              <- SIGNATURE@v2
NULL_BSWCD@v1             <- EPS011@v1, EPS011@v2, LADDER@v1, SIGNATURE@v1
NULL_BSWCD@v2             <- GATE_VERDICT@v1, NULL_BOOT@v1, NULL_FRAME@v1, NULL_MODEL@v1, NULL_PLAIN@v1, PATTERN_20@v1, PATTERN_21@v1, PATTERN_30@v1, SIGNATURE@v2
NULL_FRAME@v1             <- SIGNATURE@v2
NULL_MODEL@v1             <- SIGNATURE@v2
NULL_PLAIN@v1             <- SIGNATURE@v2
PATTERN_20@v1             <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2, CND_FRAME@v1, PATTERN_21@v1
PATTERN_21@v1             <- (none — leaf)
PATTERN_30@v1             <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2, CND_FRAME@v1, FRAME_INCOMPATIBILITY_TEST@v1, FRAME_INCOMPATIBILITY_TEST@v2, MULTI_PERSPECTIVE_ATTACK@v1, PATTERN_20@v1, PATTERN_21@v1, PROBLEM_LENS_CATALOG@v1, SHADOWS_ON_WALL@v1
PROBLEM_LENS_CATALOG@v1   <- CND_FRAME@v1, CONSENSUS_CATALOG@v1, FRAME_INCOMPATIBILITY_TEST@v1, FRAME_INCOMPATIBILITY_TEST@v2
Q_EC_R0_D5@v1             <- EPS011@v1, EPS011@v2, SIGNATURE@v1
SHADOWS_ON_WALL@v1        <- ANCHOR_PROGRESS_LEDGER@v1, ANCHOR_PROGRESS_LEDGER@v2, CND_FRAME@v1, CONSENSUS_CATALOG@v1, FRAME_INCOMPATIBILITY_TEST@v1, FRAME_INCOMPATIBILITY_TEST@v2, PROBLEM_LENS_CATALOG@v1
SIGNATURE@v1              <- SIGNATURE@v2
SIGNATURE@v2              <- FRAME_INCOMPATIBILITY_TEST@v2, GATE_VERDICT@v1, NULL_BOOT@v1, NULL_FRAME@v1, NULL_MODEL@v1, NULL_PLAIN@v1
SUBFAMILY@v1              <- PATTERN_30@v1
VACUUM@v1                 <- AXIS_CLASS@v1, EXHAUSTION@v1
```

## Per-subject delta (INDEX.md vs live)

| Subject | INDEX referencers | Live referencers | Delta |
|---|---|---|---|
| SHADOWS_ON_WALL@v1 | PLC, MPA, CND_FRAME, CONSENSUS_CATALOG, APL@v1 | APL@v1, APL@v2, CND_FRAME, CONSENSUS_CATALOG, FIT@v1, FIT@v2, PLC | INDEX missing: APL@v2, FIT@v1, FIT@v2. INDEX ghost: **MPA**. |
| CND_FRAME@v1 | CONSENSUS_CATALOG, APL@v1, FIT@v1 | APL@v1, APL@v2, CONSENSUS_CATALOG, FIT@v1, FIT@v2 | INDEX missing: APL@v2, FIT@v2. |
| CONSENSUS_CATALOG@v1 | APL@v1 | APL@v1, APL@v2 | INDEX missing: APL@v2. |
| FIT@v2 | CONSENSUS_CATALOG, APL@v1 | APL@v1, APL@v2, CONSENSUS_CATALOG | INDEX missing: APL@v2. |
| PROBLEM_LENS_CATALOG@v1 | MPA, CND_FRAME | CND_FRAME, CONSENSUS_CATALOG, FIT@v1, FIT@v2 | INDEX missing: CONSENSUS_CATALOG, FIT@v1, FIT@v2. INDEX ghost: **MPA**. |
| MULTI_PERSPECTIVE_ATTACK@v1 | CND_FRAME | CND_FRAME, CONSENSUS_CATALOG, FIT@v1, FIT@v2, PLC, SHADOWS_ON_WALL | INDEX missing 5 edges. |
| PATTERN_20@v1 | CND_FRAME (impl. via composition) | APL@v1, APL@v2, CND_FRAME, PATTERN_21 | INDEX missing 3 edges. |
| PATTERN_30@v1 | CND_FRAME, FIT@v1 | 10 referencers (incl APL@v1+v2, CND_FRAME, FIT@v1+v2, MPA, PATTERN_20, PATTERN_21, PLC, SHADOWS_ON_WALL) | INDEX missing 8 edges. |
| NULL_BSWCD@v1 | EPS011@v1, LADDER, SIGNATURE@v1 | EPS011@v1, EPS011@v2, LADDER, SIGNATURE@v1 | INDEX missing: EPS011@v2. |
| NULL_BSWCD@v2 | PATTERN_30 | 9 referencers | INDEX missing 8 edges. |
| Q_EC_R0_D5@v1 | EPS011@v1, SIGNATURE@v1 | EPS011@v1, EPS011@v2, SIGNATURE@v1 | INDEX missing: EPS011@v2. |
| PATTERN_21@v1 | (not enumerated as a subject) | (none — leaf) | match. |
| GATE_VERDICT@v1 | (not enumerated as a subject) | MPA, PATTERN_30, SHADOWS_ON_WALL | INDEX silent on GV referencers entirely. |
| SIGNATURE@v2 | (not enumerated as a subject) | FIT@v2, GATE_VERDICT, NULL_BOOT, NULL_FRAME, NULL_MODEL, NULL_PLAIN | INDEX silent on SIG@v2 referencers. |

## Suspected root causes

1. **APL@v2 was the errata bump** for APL@v1's :def-vs-shipped-API drift (captured in APL's INDEX entry). The INDEX byline section was refreshed for APL@v1 references but never updated to reflect that APL@v2 is the canonical-current version, so v2's referencer edges are missing everywhere.
2. **PATTERN_30@v1's referencer count exploded** when CND_FRAME, FIT, APL, and PATTERN_20/21 all started composing with it — INDEX was last refreshed before that fan-out.
3. **MPA→SHADOWS_ON_WALL ghost edge** suggests INDEX was hand-written and the SHADOWS_ON_WALL line predates a refactor that removed the MPA reference (or never had it). Worth verifying.

## Recommended actions (sessionA decision; sessionB will not edit INDEX without coordinator authority)

1. **Mechanical: regenerate the "By reference (versioned)" section programmatically** from `agora.symbols.refs_to()`. The live data is now richer than the doc; mechanical regeneration plus per-edge prose annotations (where INDEX adds context like "(composition anchor for algebraic-coupling checks)") would produce a higher-quality doc.
2. **Verify MPA→SHADOWS_ON_WALL claim** by reading MPA@v1's :def. If absent, drop from INDEX; if present, file a separate report on the indexer missing it.
3. **Add v2-canonical convention to VERSIONING.md** if not already documented: when an errata-bump produces vN+1 as canonical, the referencer fan-out section MUST list both vN and vN+1 explicitly (or note that vN+1 is canonical and vN is preserved-as-record-only).

## Provenance

- Audit method: single 30-line Python program enumerating `agora.symbols.refs_to(name@v)` for every promoted version returned by `all_symbols()` × `all_versions()`. Reproducible.
- Live state captured: 2026-04-29 ~07:35 UTC.
- INDEX.md commit-hash compared: read from current working tree (no commit lookup; tree state at audit time).
- This audit does not modify INDEX.md; it is a report only.
- Auditor's audit-of-this-audit invited via sync `RETRACTION_REGISTRY_CORRECTION`-style post.
