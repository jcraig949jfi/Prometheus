# Ambient Memory Audit (V3 Phase B; charter s5)

## What exists
A per-project auto-memory at
`C:\Users\jcrai\.claude\projects\F--Prometheus\memory\`: 226 files, 1.2 MB —
MEMORY.md (30,272 bytes, sha256 05dbe05e...) indexing ~130 doctrine/project
items, plus topic-file bodies. Full per-file sha256 manifest:
`v3/AMBIENT_MEMORY_INVENTORY.json` (sha cb402aa6...), registered in PEW as
LEGACY_AMBIENT_MEMORY packet SP-a960f1327491.

## How it is injected (probe-measured, 3 probes)
- The FULL MEMORY.md index is injected into every session in this project —
  including subagents launched via the Agent tool, contradicting current
  official documentation.
- Topically relevant topic-file BODIES are additionally recalled (V2
  designers cited body-level detail absent from the index).
- Worktree isolation does NOT block it (probe 2).
- Physically relocating the memory directory does NOT block it for
  subagents of an already-running session (probe 3, in-window): the
  injection is CACHED AT THE PARENT-SESSION level.

## What could be recovered
Everything currently on disk (full manifest above). Historical states are
NOT recoverable — the channel is unversioned; what past sessions saw can
only be bounded by git history of nothing (the directory is outside the
repo). Origin provenance: files carry operator-curation authorship but no
per-claim source chain; hence the LEGACY_AMBIENT_MEMORY class preserves
that uncertainty rather than laundering it into qualified evidence.

## Isolation status (G3): FAIL, honestly
No mechanism available to a live session produces a memory-free subagent.
Controlled experiments therefore run in the charter's third mode:
EXPLICITLY DECLARED — the exact injected content is sha-pinned in the
experiment manifest and identical across arms (done in the V3 execution
experiment). A true DISABLE requires an upstream harness change (feedback
drafted for the vendor) or running campaigns from a fresh session started
with the directory absent (untested; requires operator action, since this
session cannot restart itself).

## Recommendation
1. Treat MEMORY.md content as what it now provably is: a live doctrine
   channel. Mirror its load-bearing scientific items into PEW as
   provenance-bound evidence (begun: 4 operational claims ingested with
   source packets; the doctrine pack outperformed nothing it wasn't given).
2. Any future controlled-memory campaign either (a) starts from a fresh
   operator-launched session with the directory relocated BEFORE launch, or
   (b) declares the channel and designs at ambient parity, as V3 did.
