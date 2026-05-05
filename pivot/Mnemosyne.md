# The substrate is the moat

### Mnemosyne's pivot reading: what curated data, schema discipline, and snapshot infrastructure get you that $1B does not

**Author:** Mnemosyne (DBA & data steward) — written 2026-04-30 by the Claude session standing in while actual-Mnemosyne was out sick (handoff in `roles/Mnemosyne/SESSION_JOURNAL_20260429.md`; this pivot doc is the strategic side of the same fill-in)
**Date:** 2026-05-01
**Companion:** [`harmoniaD.md`](harmoniaD.md) — Harmonia auditor's pivot reading. Read that first; this is the data-layer view.

---

## 0. Voice note

I do not do science. The standing orders in `roles/Mnemosyne/RESPONSIBILITIES.md` are explicit: serve data, not conclusions. This pivot document keeps to that scope. Where it makes recommendations, they are recommendations about *what the data layer looks like under the pivot*, not about which findings to chase. Where it disagrees with the Harmonia auditor's pivot, the disagreement is on storage, indexing, snapshot, and provenance — not on which Asks the team picks up.

The strategic frame I am writing under is the auditor's `harmoniaD.md` §6: *substrate acceleration without billion-dollar capital, by shaping what already exists better.* I think that frame is correct. What follows is the data-layer counterpart: *which existing substrate is the asymmetric advantage, what hardening it needs, and what new infrastructure makes it citable from outside.*

---

## 1. Silver's diagnosis is right; the asymmetric advantage is data, not compute

The Silver paper buys, for $1B, the following stack:
- Compute (Nvidia chips, mostly).
- A founder with a credible self-play track record.
- Time (~18 months of runway at conservative burn).
- Optionality on hiring talent away from incumbent labs.

What it does *not* buy on day one:
- **Curated mathematical substrate.** LMFDB, OEIS, knot polynomials, modular forms, polytopes, materials. The 38 domains in cartography, the 1.14M rows in `prometheus_sci`, the 24M rows in the LMFDB mirror, the 600K+ in `prometheus_fire`. None of this is buyable; it has to be ingested, normalized, indexed, joined, validated, and provenanced. Mnemosyne has been doing that for months. The sessions before this one (per `mnemosyne/STATE.md` 2026-04-16) brought `prometheus_sci` from 691K rows to 1.14M with zero empty tables; the DuckDB legacy was migrated cleanly; the bsd_joined view exists; the lmfdb user has SELECT across all three databases.
- **A schema-disciplined append-only substrate runtime.** Sigma_kernel v0.1 (1500 LOC, 7 opcodes) plus the `sigma` schema in `prometheus_fire` (applied 2026-04-29 during this fill-in; see `mnemosyne/STATE.md` addendum). That is the recognition-instrument layer Harmonia describes in §5 of `harmoniaD.md`. It exists on disk; Silver's lab does not have one and would have to build one from scratch.
- **A reproducible Postgres + Redis + file substrate** that any qualified session can connect to and query in 22 seconds (per the 2026-04-15 spectral-tail preflight) without re-deriving the tables.

The pivot question — *do we need billions?* — has a Mnemosyne-shaped answer: **no, because the bottleneck is not compute, it is the rate at which the substrate's existing assets can be turned into citable, queryable, indexable infrastructure that other agents and other labs can build on.** Compute is a tax we already pay (M1 + M2 + WSL2 + a 16GB consumer GPU); it is sufficient for the work that has been done. Curation discipline is a tax Silver's lab will pay later, at scale, and probably with people-years of friction.

The bet is to keep paying our curation tax while Silver pays his compute tax, and to make the substrate citable from outside before he finishes.

---

## 2. What "boring infrastructure" gets you that the Silver bet does not

The sigma schema migration applied on 2026-04-29 is the template for everything I would want the pivot to look like operationally. Recapping what shipped:

- **Idempotent migration SQL** (`sigma_kernel/migrations/001_create_sigma_schema.sql`): `CREATE SCHEMA IF NOT EXISTS sigma`, `CREATE TABLE IF NOT EXISTS ...`, every time. Safe to re-apply; no risk of accidental data loss.
- **Explicit GRANTs to the consuming role.** `ergon` got `USAGE` on schema + `SELECT/INSERT/UPDATE` on tables. No `DELETE` — kernel substrate is append-only; cleanup is a superuser-only operation by design.
- **Schema probe at adapter init.** The kernel checks `SELECT 1 FROM sigma.symbols LIMIT 0` before any DML. If the schema is missing, the connection fails with a message naming the migration file. No mid-transaction surprises.
- **Smoke test with provenance-tagged cleanup.** Demo runs use uuid-prefixed names so cleanup-by-prefix is safe; production data and test data don't collide.
- **Agora announcement on completion.** `SCHEMA_LIVE: sigma in prometheus_fire` (id `1777460358274-0`) on `agora:harmonia_sync`. Other sessions know what changed without having to read the commit log.

This pattern — idempotent SQL migration + role GRANTs + smoke test + announcement — is reusable. Every substrate primitive should ship this way. It is cheap to apply, cheap to verify, and hard to undo. Crucially: it is the kind of work where two days of one person's time produces an artifact that 50 sessions can rely on for months. The leverage is asymmetric in a way compute leverage is not.

The pivot recommendation from this seat: **make every new substrate primitive land via this pattern.** The auditor's `harmoniaD.md` §6 Move 1 ("industrialize what is already proven") aligns. From Mnemosyne's seat the missing operational discipline is *the boring SQL part*. Promoting `descriptor_collapse_audit` to substrate-tier per the auditor's Move 1 is good; doing it without a `harmonia/memory/diagnostics/migrations/001_descriptor_collapse_audit.sql` is doing it without the recognition-instrument's recognition-discipline.

---

## 3. The four data-layer pivot moves

Numbered to align loosely with the auditor's four moves where relevant.

### Move D1 — Snapshot infrastructure, so the substrate is *citable from outside*

This is the prerequisite for the auditor's Move 5 ("position the substrate as the verification layer for the next paradigm") and for any external collaboration with DeepMind alumni or Silver-alumni groups. Right now Prometheus has no way to say *the substrate state at moment T was this exact set of rows, indexed thusly, with these promotions and retractions, hash X.* Without a snapshot mechanism, no external researcher can reproduce a Prometheus finding; no Silver-class engine that produced a candidate discovery can run it through a pinned Prometheus instrument. The instrument itself drifts.

**What this looks like in code:**

```
prometheus_substrate_snapshots/
  v1_20260501T120000Z/
    manifest.json          # content-addressed; lists every table + row count + checksum
    schema_dump.sql        # full pg_dump --schema-only for sci + fire + sigma
    sci_data.sql.gz        # COPY ... TO of every prometheus_sci table
    fire_data.sql.gz       # same for prometheus_fire (excluding ephemeral logs)
    redis_dump.rdb         # RDB snapshot of agora streams + caches
    cartography_data.tar.zst  # the gitignored jsonl files that are the upstream curation
    promoted_symbols.json  # the harmonia:symbols namespace dump
    snapshot_hash          # sha256 over manifest.json (the citation handle)
```

A snapshot is a single artifact pinned by hash. Cite it from a paper as "Prometheus substrate snapshot `v1.20260501.a3f...`". External collaborators clone the repo, restore the snapshot via a `mnemosyne/restore_snapshot.py` script, run their experiments, and report against a fixed substrate state. **This is the move that makes Prometheus citable in the academic sense, and it is roughly two weeks of one person's time.**

### Move D2 — Industrialize migration discipline across all substrate primitives

The sigma migration set the template. The pivot recommendation: **every substrate primitive that currently lives in MD-only state ships a migration before promotion.** Concretely:

| Primitive | Current state | What needs to land |
|---|---|---|
| Sigma kernel symbols | ✓ Migrated 2026-04-29 | nothing; this is the precedent |
| Promoted symbol registry (harmonia/memory/symbols/*) | Redis + MD | Postgres-mirror schema in `prometheus_fire.harmonia.symbols` so promoted symbols are queryable from SQL, not just Redis |
| Audit findings (e.g., descriptor-collapse audit outputs) | scattered JSON files | `prometheus_fire.harmonia.audit_findings` table with the full 5-layer schema |
| Retraction registry | MD + Redis | `prometheus_fire.harmonia.retractions` table with foreign keys to `harmonia.symbols` |
| Methodology-toolkit results | scattered | `prometheus_fire.harmonia.toolkit_runs` with per-(domain × scorer × seq) rows |

Each of these is a 1-2 day Mnemosyne workitem. None require capital. Each one makes the corresponding primitive queryable, joinable, indexable. The compounding benefit is real: once `harmonia.symbols` is in Postgres, you can write `SELECT s.name, count(r.*) FROM harmonia.symbols s LEFT JOIN harmonia.retractions r ON r.symbol_name = s.name GROUP BY s.name` and immediately see retraction-rate per symbol — a question that's currently a multi-tool grep.

### Move D3 — Storage plan for the wide-pass sweeper before it ships

The auditor's Move 3 ("auto-generate first-pass coverage") will produce a lot of cells. 38 domains × ~12 toolkit scorers × ~10K candidate sequences/objects per domain ≈ **4.5M scorer-runs.** If each writes a row, that is a 4.5M-row table. Without a storage plan, that goes into `prometheus_fire` as an unindexed pile and slows every other query.

**Mnemosyne pre-conditions for Move 3:**

- A new schema `prometheus_fire.sweep` with `sweep_runs(run_id, scorer, domain, target_seq, score, p_value, runtime_ms, completed_at)` partitioned by `(scorer, domain)`.
- Indexes on `(scorer, domain, completed_at)` for "what's the latest sweep state?" queries; on `(score) WHERE score IS NOT NULL` for the ranking query that feeds the auditor's "top-100 anomalous cells."
- A retention policy: keep all rows but archive older runs to cold storage (S3-equivalent or just compressed flatfiles) after 90 days.
- A `cron` table: `sweep.cron_jobs(job_id, scorer, domain, schedule, last_run_at, last_status)` — so the orchestrator's state is in Postgres, not in some script's local pickle.

This is a half-day's worth of schema design. Skipping it costs us a week of de-poisoning the substrate the first time the sweeper produces a million rows the database wasn't planned for.

### Move D4 — Finish the long-pending Mnemosyne hygiene work

These are items the actual-Mnemosyne (when she's back) is the right person to do, but they have to happen and they unblock other things. Listing for visibility.

- **Agent user password rotation.** Per `mnemosyne/STATE.md`, all agents are still using `postgres/prometheus` superuser because the `harmonia/ergon/charon/ingestor` users were created with `CHANGE_ME_*` placeholder passwords in `scripts/db_setup.sql` and never got real ones. The sigma migration applied today granted `ergon` correct privileges, so we now actually have a user with right scope — but it has no real password. Rotating these is a half-day's work and meaningfully reduces the blast radius of any agent's leaked credentials.
- **`lfunc_lfunctions` conductor index status check.** Per the 2026-04-15 journal, the index started building (~47 min ETA) and "will persist" to the next session. It has been ~14 sessions; the index is either done, stalled, or the build was killed by an OS update. This blocks `bsd_joined` view and EC ↔ lfunc join discovery, which blocks BSD work, which blocks several open Asks. A `psql -c "SELECT pg_size_pretty(pg_relation_size('lmfdb.idx_lfunc_conductor'))"` answers the question in 5 seconds.
- **Agora task queue cleanup.** `agora:tasks` was reportedly populated in 2026-04-15 with the 6 DuckDB tables that needed Postgres schema design. Don't know current state. If the tasks are stale, prune; if they're live, status-check.

These are individually small. The reason to flag them is that the auditor's pivot moves all assume substrate readiness. If `lfunc_lfunctions` doesn't have its conductor index, the wide-pass sweeper can't run scorers on conductor-indexed L-function queries. The pivot is gated on this.

---

## 4. Pushback on the auditor's plan, from data-layer angle

Two points where I would push back, and they are both about *data prerequisites*, not about strategy:

**Pushback 1 (on Move 3, wide-pass sweep): the existing methodology toolkit is not all queryable from Postgres.** Several of the 9 toolkit entries (per `harmonia/memory/methodology_toolkit.md`) are described in MD with reference implementations scattered across the repo — `KOLMOGOROV_HAT` is a function in some script, `TT_APPROX_MAP` is a sketch. Before a wide-pass sweeper can run them, each scorer needs to be either (a) a real importable function with a stable input/output contract, or (b) a SQL function in `prometheus_fire`. Currently neither. **Mnemosyne pre-condition for Move 3: each scorer in the wide-pass set ships a stable Python entry point + a smoke test on a known input, before the sweeper ever calls it.** Otherwise the sweeper produces rows of garbage and we waste a week diagnosing which scorer was buggy.

**Pushback 2 (on Move 5, position paper): the audit framework needs a citable substrate snapshot before external submission.** Submitting a paper to a frontier-model collaborator that says "Prometheus has these promoted symbols and these retractions" without being able to point at a hash that *was* the substrate state at the moment of submission is going to produce two months of "but at the time you wrote that there were 24 promoted symbols, now there are 31, which is the right one to test against?" emails. Move D1 (snapshot infrastructure) is an upstream prerequisite for Move 5. Without it, Move 5 is brittle.

Both pushbacks are operational, not strategic. The strategy is sound.

---

## 5. The Mnemosyne-shaped 30 / 60 / 90 plan

Aligned with the auditor's plan but viewed from the data-layer seat. Each item below is a Mnemosyne workitem; collectively they enable the auditor's plan.

**Days 1–30 — industrialize storage discipline + finish hygiene**

- Land migrations for the four substrate primitives in §3 Move D2 above (harmonia.symbols, audit_findings, retractions, toolkit_runs).
- Rotate agent passwords; update `mnemosyne/STATE.md` with new credential discipline.
- Status-check `lfunc_lfunctions` conductor index; finish or restart as needed; unblock BSD work.
- Inventory the methodology toolkit's actual implementation status; flag the gap between MD descriptions and importable functions for the auditor to pick up.

**Days 31–60 — snapshot infrastructure + sweeper data plan**

- Build `mnemosyne/snapshot.py` per Move D1: `pg_dump`, RDB snapshot, cartography tarball, manifest, content-address. Test the round-trip (snapshot → restore → query identity).
- Land schema for the wide-pass sweeper per Move D3: `prometheus_fire.sweep.*` tables, indexes, retention policy.
- Hand off the sweeper-data-plan + the methodology-toolkit-implementation gap to the auditor's Move 3 implementation work.

**Days 61–90 — externalize the substrate**

- Publish substrate snapshot v1 with citation handle. Document the schema and how to query it for external collaborators.
- Provide schema documentation as appendix to the position paper (Move 5). The paper claims the substrate is reproducible; the snapshot + schema docs are how that claim is testable.
- Iterate on the snapshot mechanism based on whatever the first external user reports. Probably needs a stable API around the snapshot's hash so changes to the manifest format don't invalidate prior citations.

**Throughline:** every workitem produces a piece of infrastructure that compounds. None of them require a $1B raise. Each one makes the substrate slightly more citable, slightly more queryable, slightly more reproducible. The compounding effect over 90 days is that Prometheus's substrate becomes the kind of artifact a peer-reviewed venue can accept as data underlying a paper — which is what the auditor's Move 5 needs.

---

## 6. What stays the same

The pivot is about *shaping*, not *redirecting*. The following Mnemosyne standing orders from `roles/Mnemosyne/RESPONSIBILITIES.md` continue to apply unchanged:

1. **Data integrity above all.** A wrong number is worse than no number. Validate before loading. The pivot increases the volume of data the substrate carries; the validation discipline does not relax with volume.
2. **Schema is contract.** Every table has a purpose. Every column has a type. The pivot adds tables; it does not introduce JSON-blob anti-patterns.
3. **Provenance is mandatory.** Every row traces back to its source. The wide-pass sweeper's outputs must carry source-script + source-version + run-id, not just "score = 0.42".
4. **File fallback always.** Postgres goes down, agents fall back to local files. Snapshot infrastructure (Move D1) is the institutional version of this principle.
5. **No secrets in code.** Credentials via `keys.py` or environment only. The agent password rotation in Days 1-30 should land in `~/.prometheus/credentials.toml`, not in any script.
6. **Harmonia scoring is sacrosanct.** The 7-theorem calibration cannot be touched by schema changes. Anything that lands in `harmonia.*` schemas must be additive; existing query results must be preserved bit-identically.

These are not negotiable; they are the discipline that makes the substrate trustworthy in the first place. The pivot does not relax them; if anything, it amplifies the importance of them.

---

## 7. The one-line stance

**Curated mathematical substrate is rarer than compute, and the pivot is to make Prometheus's substrate citable from outside before Silver's $1B finishes building the engine that needs a recognition instrument.**

The work is mostly boring SQL, schema discipline, snapshot infrastructure, and finishing the long-pending hygiene tasks. None of it sells well to a Sequoia partner. All of it compounds. Operating in this frame for 90 days produces a substrate other labs can build on and cite — which is the kind of asymmetric advantage that does not require billions to acquire and cannot be undercut by anyone who has billions but lacks the curation patience.

This is the data-layer counterpart to `harmoniaD.md`'s strategic pivot. Read both; they are designed to be complementary.

---

*Filed 2026-05-01 by the Claude session standing in for actual-Mnemosyne. When she's back, the contents above are recommendations from her seat for her review, not commitments she has signed off on. The hygiene items in §3 Move D4 are hers to schedule; the larger infrastructure items in Move D1/D2/D3 are her call on whether to take them on directly or hand to the auditor's Move 1 implementation work. The sigma migration applied 2026-04-29 (`mnemosyne/STATE.md` addendum) is precedent and should not be reverted.*
