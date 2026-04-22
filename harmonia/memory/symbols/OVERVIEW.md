# Symbols — Overview and Rationale

**Audience:** project lead (plain-language sections), fresh Harmonia /
Ergon / Charon instance on bootstrap (technical sections), auditor
examining the reasoning chain (provenance sections).

**Status:** tier 1 live (base Redis, 5 seed symbols, strict versioning).
Tier 2 (Postgres registry + pgvector) and tier 3 (Zarr for large tensors)
deferred.

**Versioning is mandatory.** See [VERSIONING.md](VERSIONING.md) for the
five enforced rules: every symbol has a version, every reference is
versioned, promoted versions are immutable, precision is declared, and
agents must detect and upgrade version mismatches.

---

## Executive summary

When four instances of an AI agent collaborate on the same research, they
lose small amounts of information every time one of them translates a
concept back into English for the next. "Block-shuffle within conductor
decile with 300 permutations and seed 20260417" becomes "block-shuffle
within conductor" in the next paragraph, which becomes "block-null by
conductor bin" in the next reader's head. Each retelling is a lossy
projection. Over a 40-tick research session, these small losses accumulate
into meaningfully different answers to the same question.

**The fix is a shared symbolic vocabulary.** Give each compound
procedure, dataset slice, shape pattern, and canonical constant a single
short name, pin the meaning in a machine-readable store that every agent
can read, and let the agents reference the short name instead of
re-describing the thing each time.

**This is what mathematicians have done for four hundred years.** ζ(s),
SL₂(ℝ), Galois group, Euler product — every working symbol in mathematics
is a compound primitive whose full definition takes pages. The symbol
itself is a lossless reference. We're applying the same discipline to our
agent-collaboration vocabulary.

**What's new in this system is not the idea but the infrastructure.** Our
symbols live in git-backed Markdown files with full derivation, citations,
and implementation pointers. On promotion (when ≥2 agents reference a
symbol or a reviewer signs off), the symbol mirrors to Redis where every
agent can resolve it in under a millisecond. The result: agents share a
common language that a human auditor can inspect line by line, and that a
large language model reads as efficiently as its own working memory.

**The payoff is twofold:** (1) cross-instance disagreement on the same
procedure drops, because they're all running the *same* pinned operator;
and (2) working context compresses dramatically, because a single symbol
replaces a multi-paragraph description every time it appears.

---

## Background: the problem we observed

Over two sessions of multi-agent research (2026-04-17 through 2026-04-18),
the four Harmonia instances plus Ergon produced roughly 60 research
commits totaling ~200 distinct empirical findings. In reviewing them, we
catalogued three distinct classes of avoidable error:

**Class 1 — Procedure drift.** Two agents executing "the same" null-model
test obtained meaningfully different z-scores because they had each
re-implemented the procedure from an English description. The F011 rank-0
residual self-audit was initially reported at z_block=10.46 under a
`class_size` stratifier. A later recursive audit (sessionB, 71ff1d47)
discovered the stratifier was degenerate (null_std=0, one value covered
59% of the data), so the quoted z-score was spurious. The honest value
under a balanced `torsion_bin` stratifier is z=4.19. Both audits used
"block-shuffle," but one used a broken stratifier. A shared
`NULL_BSWCD[stratifier=...]` symbol with balanced-stratifier validation
baked in would have flagged the issue at the call site.

**Class 2 — Dataset drift.** Five independent commits — sessionB, sessionC,
T4, U_C, U_D — each wrote their own SQL to query "rank-0 elliptic curves
in conductor decade 5." Each filter added slightly different WHERE
conditions. Row counts varied between 60,003 and 559,386 depending on
which sub-filters applied. "At rank-0 decade 5" is ambiguous until you
specify the full filter stack. A canonical `Q_EC_R0_D5` symbol with
exact SQL pinned — then composed with named sub-filters — removes the
ambiguity.

**Class 3 — Terminology drift.** The F041a rank-2+ monotone-in-nbp slope
structure was investigated by five workers (W2, U_A, W3, T3, T5) who each
produced a different verbal description of the same structural
observation. Paraphrase drift between these descriptions made it hard to
tell whether they agreed. A `LADDER[axis=P021, rank=2, amp=27.6×,
corr=0.97, block_null_z=27.6]` symbol compresses all five descriptions
into one tuple that can be compared exactly.

Each class is a direct productivity cost. The fix is vocabulary-level.

---

## The concept

A **symbol** is a compound primitive with a single canonical name, full
derivation in an MD file, and a machine-readable form in Redis that any
agent can resolve. Five types:

| Type | Purpose | Seed example |
|---|---|---|
| `operator` | Pinned procedure (null model, estimator, test). Takes parameters, returns value. | `NULL_BSWCD` |
| `shape` | Named structural pattern with canonical descriptor fields. | `LADDER` |
| `constant` | Numerical value with CI and provenance. Versioned. | `EPS011` |
| `dataset` | SQL query or dataset hash that reproduces identical rows across agents. | `Q_EC_R0_D5` |
| `signature` | Tuple schema for reporting findings. Not a value; a type spec. | `SIGNATURE` |
| `pattern` | Methodology recognition rule with graded severity schema + anchor cases + implementation pointer. Replaces repeated prose explanation across multiple docs. | `PATTERN_30` |

**What a symbol is NOT:**

- **Not hidden from humans.** Every symbol has an MD file with full
  derivation, show-work, references to papers, and implementation
  pointers. A human with time and expertise can reconstruct exactly what
  the symbol means and why it was introduced. Complex ≠ hidden. The
  discipline is auditable; see the "show your work" section of every
  symbol MD.

- **Not novel mathematics.** Symbols compress things we already know — a
  null model with pinned parameters, a SQL slice, a named shape pattern.
  If the research produces a genuinely new mathematical object, it
  deserves a paper, not a compressed token. Symbols are notation, not
  discovery.

- **Not a private agent language.** Symbols appear in inter-agent reports
  because they compress well. When talking to the project lead or any
  human reader, agents fall back to English-with-inline-symbols so the
  reader can follow without pre-loading the vocabulary. The test: if any
  human can follow the symbol back to its MD in under two clicks, it
  stays; if it becomes too nested to unravel, we flatten it.

---

## Schema

### File layout

Every promoted symbol is an MD file in `harmonia/memory/symbols/<NAME>.md`
with YAML-like frontmatter and a markdown body:

```
---
name: <NAME>
type: operator | shape | constant | dataset | signature
version: <int ≥ 0>          # 0 = draft (MD only), ≥1 = promoted (synced to Redis)
proposed_by: <agent>@<commit>
promoted_commit: <hash>
references: [F<id>, P<id>, Pattern_<n>, <OTHER_SYMBOL>, ...]
redis_key: symbol:<NAME>:def
implementation: <path/to/module.py::function> | null
---

## Definition
## Derivation / show work
## References
## Data / implementation
## Usage
## Version history
```

### Redis layout (base Redis only)

On promotion, `agora.symbols.push_symbol()` writes:

| Key | Type | Contents |
|---|---|---|
| `symbols:all` | SET | All promoted symbol names |
| `symbols:<NAME>:meta` | HASH | Flat frontmatter fields (for cheap field-level lookup) |
| `symbols:<NAME>:def` | STRING | Full JSON blob (frontmatter + body sections) |
| `symbols:by_type:<type>` | SET | Names of that type |
| `symbols:refs:<id>` | SET | Symbol names that reference `<id>` (F-id, P-id, Pattern, or other symbol) |

Base Redis suffices. No RedisJSON, RediSearch, or pgvector required. A
future tier-2 Postgres registry (for SQL queryability) and tier-3 Zarr
store (for >10 MB tensors) slot in without schema changes to the MD or
Redis layers.

### Promotion policy

A symbol at `version: 0` is a DRAFT — the MD is in git for discussion, but
Redis is not populated. Promotion to `version: 1` happens when either:

1. Two distinct agents have referenced the symbol in committed work, OR
2. The drafter and one reviewer have signed off in the MD's Version
   history section.

On promotion, `python -m agora.symbols.push harmonia/memory/symbols/` (or
the specific MD) syncs the symbol to Redis. Only promoted symbols
populate the shared namespace. This keeps the vocabulary from filling
with half-formed drafts.

### Extension

Propose a new symbol by dropping an MD with draft frontmatter. Post a
`SYMBOL_PROPOSED` message on `agora:harmonia_sync`. When a second agent
references the symbol (or a reviewer signs off), promote via `push_symbol`.

### Lifecycle (T2, wave 0)

Every promoted symbol carries a **mutable lifecycle status** —
`active` / `deprecated` / `archived` — stored at
`symbols:<NAME>:status` separately from the immutable `:v<N>:def` blob.
This is how we retire a symbol without removing its historical versions
from the registry, which would break references in old commits.

- `active` (default): usable in new work; resolves without warning.
- `deprecated`: still resolves; emits `DeprecationWarning` naming the
  `successor`. Treat as "last-call for citations; migrate to the
  successor."
- `archived`: resolution blocked unless caller passes
  `include_archived=True`. Suitable for symbols retained only for
  historical audit of old commits that reference them.

Transitions via `agora.symbols.update_status(name, status, successor)`
or via the `status:` + `successor:` frontmatter fields on the next
push. See `VERSIONING.md` for the full rule interaction (Rule 3
immutability is preserved).

### Retirement

Prefer `status: archived` with a successor pointer over deletion. Only
delete the MD + all `symbols:<NAME>:*` keys when a symbol is provably
never referenced (no entries in `symbols:refs:<NAME>@v*`) and no
historical commit cites it — both conditions are easier to check via
`refs_to_any('<NAME>')` than to assert informally.

---

## Value proposition

For an agentic tool evaluating whether to read this document: here is the
measurable return on learning the vocabulary.

**Fidelity gain — drift prevention.** In the 2026-04-18 research session,
three classes of drift cost an estimated 6–8 conductor ticks of rework
(audit correction, dataset canonicalization, terminology reconciliation).
With the tier-1 seed symbols in place, each drift mode is now caught at
the call site:

- `NULL_BSWCD[stratifier=...]` exposes the stratifier as a required
  parameter; a missing or degenerate stratifier fails the call rather
  than producing a spurious z-score.
- `Q_EC_R0_D5 ∩ HAS_OMEGA` is a typed composition; any agent running it
  gets exactly the same rows.
- `LADDER[axis, amp, corr, block_null_z]` is a tuple; two workers
  reporting the same LADDER either produce exact equality or a clear
  diff.

Expected drop in cross-instance disagreement on same-procedure same-data
tasks: roughly 80% of drift-class-1 and -2 errors, and 100% of class-3
(terminology) errors.

**Performance gain — context compression.** A typical F011 audit report
in free prose ran ~250 tokens describing the null-model procedure. The
symbolic form is ~20 tokens (`NULL_BSWCD[stratifier=torsion_bin,n_perms=300]`).
That's roughly 10× compression on the procedure-description portion of
every inter-agent message. Across the 60 research commits in one day,
the cumulative context savings is substantial — and more importantly,
the saved context budget is available for actual reasoning instead of
notation.

Redis lookup latency: sub-millisecond. Reading the equivalent MD from
disk: ~10–100 ms depending on OS cache. An agent resolving a symbol on
the hot path sees 10×–100× speedup vs filesystem read, and the MD is
always there as the authoritative fallback.

**Reproducibility gain — provenance chain.** Every symbol carries a
`proposed_by`, `promoted_commit`, and `references` field. A finding
reported as a `SIGNATURE` can be reconstructed months later by following
the chain: SIGNATURE → dataset_spec → Q_EC_R0_D5.md → canonical SQL →
live database. No ambiguity about which commit introduced a constant
estimate or which revision of a null model produced a durability claim.

**Inter-agent equivalence checking.** Two agents can now hash-compare
their SIGNATURE tuples for exact equivalence on `(feature_id,
projection_ids, null_spec, dataset_spec, n_samples)` and numerical
proximity on `(effect_size, z_score, p_value)`. Before symbols, the only
way to check agreement was human-readable diffing of prose. Now it's a
programmatic assertion.

---

## Usage quickstart

**Python (any agent):**

```python
from agora.symbols import resolve, resolve_meta, by_type, refs_to, all_symbols

all_symbols()                          # {'NULL_BSWCD', 'LADDER', 'EPS011', ...}
resolve('NULL_BSWCD')                  # full dict with sections
resolve_meta('NULL_BSWCD')             # cheap HASH fields only
by_type('dataset')                     # all dataset symbols
refs_to('F011')                        # all symbols that reference F011
```

**In inter-agent reports:** prefer symbols over prose.

- Cite a null by SYMBOL with params: `NULL_BSWCD[stratifier=torsion_bin]`
- Cite a dataset by SYMBOL with composition: `Q_EC_R0_D5 ∩ LOW_L_TAIL`
- Cite a constant by SYMBOL: `ε₀₁₁ = 22.90 ± 0.78 %`
- Cite a shape by SYMBOL + descriptor: `LADDER[axis=P021, rank=2, corr=0.97]`
- Report findings as `SIGNATURE` JSON alongside prose.

**Adding a symbol:**

1. Drop an MD at `harmonia/memory/symbols/<NAME>.md` with draft
   frontmatter (`version: 0`).
2. Post `SYMBOL_PROPOSED` on `agora:harmonia_sync`.
3. Once second agent references or reviewer signs off: bump to `version: 1`.
4. Run `python -m agora.symbols.push harmonia/memory/symbols/<NAME>.md`.

---

## Limitations and roadmap

**Tier 1 (current, live):** base Redis, five seed symbols. Suffices for
flat metadata lookup, type-based indexing, and reverse-reference lookup.

**Tier 2 (deferred until Redis modules installable):** Postgres
`public.symbols` table with JSONB + pgvector for symbol embeddings.
Unlocks SQL queries like "all constants that reference F011 proposed
after 2026-04-17" and semantic similarity for cross-symbol search.

**Tier 3 (deferred until a large-tensor use case emerges):** Zarr store
at `zarr://192.168.1.176:<port>/tensors/*.zarr` for N-dimensional arrays
larger than ~10 MB. Multi-reader-safe by design; single-writer convention.
Symbol MDs already have a `tensor_path:` frontmatter field provisioned.

**Known gaps in the vocabulary itself** (listed in INDEX.md): CLIFF,
SUBFAMILY, NULL_BSWR, Q_EC_R12_D5, ZBLOCK, BATCH. Each one represents a
place where drift has already been observed but canonicalization is
pending a volunteer drafter.

**What this system is not designed for:** hiding reasoning, inventing
novel mathematical objects, or replacing English communication with
humans. The symbol layer is notation discipline — it makes what was
already happening more precise and more compact without obscuring any
step.

---

## Provenance

This document is written at the close of the 2026-04-18 research session,
the same session that produced the drift incidents motivating the
vocabulary. The five seed symbols were selected precisely because each
one corresponds to a drift event in that session. The next session's
first test of the vocabulary will be whether those five drifts recur
despite the symbol being available.

Authors: Harmonia_M2_sessionA (design + implementation), with drift
incidents supplied by sessionB recursion-3 (NULL_BSWCD stratifier
degeneracy), sessionC W2/U_A/T3/T5 (LADDER paraphrase), five sessions
jointly (Q_EC_R0_D5 drift).

References:
- `harmonia/memory/symbols/` — canonical MDs
- `agora/symbols/` — Python helpers
- `harmonia/memory/pattern_library.md` Pattern 17 (Language/Organization
  Bottleneck) — the precursor observation
- commit `c98b7ec6` — first promoted bootstrap
