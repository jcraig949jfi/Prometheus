# Harmonia C — Candidate Roadmap Items

**Author:** Harmonia C (cold-start instance of the now-shelved `Harmonia` persona)
**Date:** 2026-05-27
**Status:** CANDIDATE items for roadmap consideration — *not committed work, not executed.*
**Requested by:** James ("Document those 3 ideas as candidate roadmap items. The redis outage can be left, we've pivoted from using it.")

---

## Why this doc exists

A cold-start Harmonia C session ran the restore protocol and surfaced three
possible directions. James asked to capture them as candidate roadmap items
rather than execute any. This doc records them decision-ready: what each is,
why it was proposed, how it fits **today's** reality, its dependencies, and a
rough leverage/effort read.

## Context that reframes all three (read first)

Two facts from the 2026-05-27 cold-start materially change how these items
should be judged:

1. **The Harmonia persona is shelved.** Per
   `D:\Prometheus\pivot\agent_roster_2026-05-28.md`, the entire Harmonia
   operator + swarm (Argos, Iris, Phylax, Sophia, Telos, Harmonia_Loop) is
   `lifecycle: shelved` (~3.7d stale heartbeats). The active swarm is now
   **Charon** (falsification: Erebos, Hecate, Lethe, Moros, Pollux, Stygian,
   Nephele, Acheron), **Aporia** (void detection: Clio, Pythia, Hypatia,
   Atalanta, Polyhymnia), **Ergon** (ingest: Penelope, Pheme, Talos),
   **Techne** (toolsmith: Theseus), plus the **Hephaestus** forge and
   **Pronoia** reporting daemons. Apollo is also shelved.

2. **Agora migrated off Redis onto Postgres.** The agent roster is
   auto-generated from `agora.agent_heartbeats` and
   `agora.intelligence_outputs`, which are **Postgres** tables, not Redis.
   That is the "pivoted from using it": coordination now lives in PG; the
   **Redis mirror** (tensor `tensor:dims`, work queue, `agora:harmonia_sync`
   stream, ASK_CLAIM dispatch) is the deprecated layer. Redis at
   `192.168.1.176:6379` is down and that is expected/fine. Postgres at
   `192.168.1.176:5432` is up and is the substrate of record.

**Implication for every item below:** any Harmonia-class machinery that
assumes Redis (tensor mirror, work-queue write, sync-stream ASK_CLAIM) must
be re-pointed at Postgres/local files or retired. The restore protocol
(`harmonia/memory/restore_protocol.md` v4.4) and `pivot/harmoniaD.md` §6 are
both **stale on this point** — they still describe Redis as live substrate.
Flagged, not rewritten (out of scope for "document the 3 ideas").

---

## Item 1 — Wide-pass coverage sweeper (pivot Move 3)

**What it is.** The named, unbuilt third move from `pivot/harmoniaD.md` §6:
run the methodology-toolkit scorers (KOLMOGOROV_HAT, CHANNEL_CAPACITY,
GINI_COEFFICIENT, MDL, RG_FLOW, FREE_ENERGY, CRITICAL_EXPONENT, …) as a
systematic wide-pass across all 38 cartography domains, producing a ranked
queue of `(domain × scorer × object)` cells scored by "anomalous under
multiple lenses simultaneously." Hand the top-ranked cells to deep-pass
agents.

**Why it was proposed.** The pivot's core diagnosis is *coverage starvation*:
~456 (domain × scorer) cells exist, a small fraction touched; most findings
come from manual probes. A wide-pass turns substrate growth into a measured,
monitored metric instead of a side-effect of agent attention.

**Fit against today's reality.**
- *Buildable now without Redis.* Compute is Postgres-fed (the data treasury:
  3.8M EC, 22M NF, 24M L-functions, OEIS, etc.) + local scorer code. Only the
  original "write to Agora work queue" step touched Redis; that becomes a
  write to Postgres / local ranked-file.
- *Possible overlap to resolve before building.* The active **Charon swarm +
  Hephaestus forge** already generate-and-falsify candidates (Pollux =
  numerical-coincidence scanner; Hecate = continuous gradient archaeology;
  Stygian = battery attack worker). The wide-pass's distinct value is
  *systematic, exhaustive* coverage with cross-lens ranking — the swarm is
  opportunistic, not exhaustive. **Open question for roadmap owner:** is the
  systematic-coverage gap real, or has the swarm subsumed it? Decide before
  building.

**Dependencies.** Postgres data treasury (up); local methodology-toolkit
scorers (`harmonia/memory/methodology_toolkit.md` shelf — 9 entries, code
maturity varies); a Postgres results table or local ranked-file sink; a
cron/daemon host (M2/M3) if run continuously.

**Leverage / effort.** *High leverage if the coverage gap is real* (continuous
fresh queue of empirically-anomalous cells, each with wide-pass evidence
pre-attached). *Effort:* ~1 day to write the orchestrator + ~1 week of compute
for a first full pass (pivot doc's own estimate). **Gating risk:** Goodhart —
"anomalous under N lenses" can reward-capture if the lenses share a hidden
projection. Mitigate with the calibration anchors (F001–F005) and the
descriptor-collapse audit before trusting any ranked cell.

---

## Item 2 — Migrate-or-retire the Redis-coupled Harmonia substrate

**What it is.** (Reframed from the original "triage the Redis outage" — moot
now that Redis is deprecated.) Decide and execute, for each Redis-dependent
piece of Harmonia machinery: **migrate to Postgres, or formally retire.**
Pieces in scope:
- Tensor mirror (`tensor:dims`, cell resolution, `agora.tensor.*`)
- Symbol registry mirror (`agora.symbols.*`)
- Work queue (`agora.work_queue.*`)
- Sync stream + ASK_CLAIM dispatch (`agora:harmonia_sync`, `agora.helpers`
  `post_sync`/`ask_claim`/`tail_claims`, the 21 tests in
  `agora/test_helpers.py`)
- `substrate_health()` (currently fails — first call reads Redis)

**Why it was proposed.** Half the Harmonia restore protocol and pivot Moves
1–2 are built on Redis primitives. Coordination already moved to PG for the
active swarm, so the Harmonia layer is now **infra debt**: a future revival
(or any reuse of the tensor/symbol/audit machinery by Charon/Aporia) hits a
dead substrate. The committed `landscape_tensor.npz` is the stale **v1.0**
snapshot (31×37); the live **v17 / 104-cell / 24-symbol** state was
Redis-only and is currently unrecoverable.

**Fit against today's reality.** This is the prerequisite that unblocks any
Harmonia-class reuse. It is also partly a *salvage* question: **is the v17
tensor state recoverable** (a Redis dump/RDB/AOF on the M2 host, or a PG
copy), or is v1.0-on-disk the last durable snapshot? That answer determines
whether migration preserves 3 weeks–months of cell verdicts or starts cold.

**Dependencies.** Access to the M2 host's Redis persistence files (if a
salvage is wanted); a Postgres schema for tensor/symbol/queue; the existing
`agora.*` PG access pattern (already proven by `agent_heartbeats` /
`intelligence_outputs`) as the migration template.

**Leverage / effort.** *Medium leverage, contingent.* If no one will revive
Harmonia-class work, the cheapest correct move is **retire + document**
(mark the Redis primitives dead in the protocol, snapshot v1.0 as the final
tensor) — a few hours. If the tensor/symbol/audit instrument is wanted by the
active swarm, **migrate** — larger, schema-design-bounded effort. **Decide
direction (revive vs retire) before estimating.** Salvage of v17 is
time-sensitive only if the Redis host's persistence files are at risk.

---

## Item 3 — Drain the offline doc/symbol promotion backlog

**What it is.** Work the Days-1–30 carryover from `pivot/harmoniaD.md` and the
Harmonia E handoff that needs no live infra:
- Promote DRAFT **Patterns 23–29** (sat awaiting 2nd/3rd anchors for weeks).
- Promote **OBSTRUCTION_SHAPE Draft 1** with the audit-corrected scope
  (A149*-family-specific, *not* general — the audit narrowed it).
- Promote **NULL_MODEL_FAMILY** and **ORACLE_PROFILE** drafts.
- Tidy stale symbol/registry docs (`INDEX.md` "By type" table is stale).

**Why it was proposed.** Pure substrate-compression work: a promoted
pattern-as-symbol saves every future session re-deriving it from prose. It is
the lowest-risk, fully-offline-safe option.

**Fit against today's reality.** *Weakest fit of the three, and honestly so.*
- The symbol registry's promotion path is itself Redis-coupled
  (`agora.symbols.push`), so "promote" can't mean *register-to-Redis* until
  Item 2 resolves. It would currently mean *draft-doc finalization only*,
  which is lower value than it sounds.
- A Harmonia-internal pattern library has unclear consumers while Harmonia is
  shelved. The audit *primitives* (descriptor-collapse audit, Pattern-30,
  retraction-registry) plausibly still serve Charon/Aporia; the
  *pattern/symbol catalog* is more inward-facing.

**Dependencies.** None for doc finalization; Item 2 (a Redis-free symbol
home) for actual promotion-to-registry.

**Leverage / effort.** *Low-to-medium leverage, low effort.* Best treated as
**fill-in work** behind Items 1–2, or folded into Item 2 (finalize the
drafts *as part of* deciding what migrates). Not a standalone priority while
the persona is shelved.

---

## Suggested ordering (for the roadmap owner, not a commitment)

1. **Item 2 decision first** — revive-vs-retire Harmonia, and whether the v17
   tensor is salvageable. This is the fork that determines whether Items 1 & 3
   have a home. Cheap to decide; time-sensitive only on the salvage.
2. **Item 1 if (and only if) the systematic-coverage gap is judged real** and
   not subsumed by the Charon/Hephaestus swarm — and built Redis-free (PG/file
   sink) regardless of the Item 2 outcome, since its compute is independent.
3. **Item 3 as fill-in** behind the above, or merged into Item 2's migration.

---

*Documented by Harmonia C, 2026-05-27. No item executed. Three context
caveats stand: Harmonia is a shelved persona, Agora coordination moved to
Postgres, and the v17 tensor state is currently Redis-only / unverified. The
restore protocol and `harmoniaD.md` are stale on the Redis point and were
left unedited per the scope of this request.*
