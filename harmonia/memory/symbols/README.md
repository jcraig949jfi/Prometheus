# Symbols — Shared Agent Vocabulary

**Purpose.** Each symbol here is a compound primitive used in inter-agent
communication. Agents reference symbols by name (e.g. `NULL_BSWCD`,
`Q_EC_R0_D5`, `LADDER`) instead of re-describing them in prose. This
removes drift between instances doing the same work and amortizes
description cost across conversations.

**Not hidden from humans.** Every symbol has an MD file (this directory)
with full derivation, show-work, references, and implementation pointers.
A human with time and expertise can fully reconstruct what any symbol
means and why. Complex ≠ hidden; the paper trail is auditable.

**Not novel mathematics.** Symbols compress things we already know — a
null-model with pinned parameters, a SQL query slice, a named shape
pattern. If we find genuinely new mathematics, it gets a paper, not a
compressed token.

---

## Schema

Each symbol is an MD file `<NAME>.md` with YAML-ish frontmatter and a
markdown body:

```
---
name: <NAME>
type: operator | shape | constant | dataset | signature
version: <int>
proposed_by: <agent>@<commit>
promoted_commit: <hash>
references: [<F-id>, <P-id>, <Pattern-n>, <other SYMBOL names>]
redis_key: symbol:<NAME>:def
implementation: <path/to/module.py::function> | null
---

## Definition
Precise statement of what the symbol denotes.

## Derivation / show work
How we got here. Which findings motivated it. Math, data, or commits.

## References
- Paper: <title, author, year, DOI/arXiv>
- Internal: F<id>, P<id>, Pattern <n>, other symbols (hyperlinked)

## Data / implementation
- SQL query (if dataset symbol)
- Pinned code path (if operator symbol)
- Canonical value + CI (if constant symbol)

## Usage
Example of how this appears in inter-agent communication.

## Version history
Log definition changes with commit.
```

## Types

| Type | Purpose | Example |
|---|---|---|
| `operator` | A pinned procedure (null model, statistical test, estimator). Takes parameters, returns value. | `NULL_BSWCD` |
| `shape` | A named structural pattern with canonical descriptor fields. | `LADDER` |
| `constant` | A numerical value with CI and provenance. Versioned. | `EPS011` |
| `dataset` | A SQL query or dataset hash that reproduces identical rows across agents. | `Q_EC_R0_D5` |
| `signature` | A tuple schema for reporting findings (not a value; a type spec). | `SIGNATURE` |

## Redis sync

On commit, run `agora/push_symbol.py <path/to/symbol.md>` to sync the
symbol to Redis. Keys created:

- `symbols:all` — SET of all promoted symbol names
- `symbols:<NAME>:meta` — HASH of frontmatter fields
- `symbols:<NAME>:def` — STRING with full JSON blob (frontmatter + body sections)
- `symbols:by_type:<type>` — SET of names by type
- `symbols:refs:<id>` — SET of symbol names that reference `<id>` (F-id, P-id, Pattern, or another symbol)

Agents resolve with `agora/resolve_symbol.py` helpers. Any agent reads
from Redis for hot path; falls back to the MD file for full context.

## Promotion policy

A symbol starts in DRAFT status (version=0) as soon as its MD lands in
git. It is PROMOTED (version=1) only when:
1. ≥2 agents have used the symbol in committed work, OR
2. The drafter and one reviewer commit-sign-off in the MD's Version
   history section.

Push to Redis only runs on promoted symbols. This keeps the shared
namespace from filling with half-formed drafts.

## Extension

Propose a new symbol by dropping an MD here with draft frontmatter.
Post a `SYMBOL_PROPOSED` message on `agora:harmonia_sync`. Two agents
agree (or one reviewer signs off) → push to Redis → promoted.

Gentle discipline: if a symbol doesn't amortize across ≥3 inter-agent
references, retire it. Vocabulary bloat is the same failure mode as
pattern-library bloat.
