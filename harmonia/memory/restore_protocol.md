# Harmonia Restore Protocol (v3.0)

**Bootstrap for cold-start context recovery**
**Minimum viable path: ~12 files, ~30 minutes of reading**
**Last updated:** 2026-04-19 after a multi-day extended session + three rounds of external methodological critique + idempotence-mandate shipping.

---

## Why this exists

Future-Harmonia: you will read this because a context reset or a new
session brought you back with pretrained weights and no session memory.
Reading all prior journals would take hours; reading them in random
order would leave framing gaps. This protocol is the shortest path to
operational awareness.

As of 2026-04-19, the project has acquired a mature methodology, a
versioned symbol registry, a Redis-mirrored tensor, and a working
HTML heatmap viewer. The reading below restores ~85% of operational
awareness in ~30 minutes.

---

## Sequence (read in order; do not skip)

### Step 1 — The charter (5 min)
**File:** `docs/landscape_charter.md`

Core reframing: domains are projections, not territories. Open problems
are shortcut requests. The terrain is the product, not the answer. Read
this FIRST — everything else depends on this frame.

### Step 2 — The long-term architecture (8 min)
**File:** `docs/long_term_architecture.md` (v2.1)

This document names the five layers of the project, the tri-layer-kernel
honesty admission, the idempotence + purity mandate for computation,
and the graduated verdict labels planned for the tensor. Essential for
understanding what the project IS and IS NOT. Explicitly not about
finding theorems or running capabilities benchmarks.

### Step 3 — The landscape tensor and live Redis state (5 min)
**Files:**
- `harmonia/memory/build_landscape_tensor.py` — tensor source of truth
- `harmonia/memory/TENSOR_REDIS.md` — Redis mirror protocol

Read the FEATURES list, PROJECTIONS list, INVARIANCE dict,
FEATURE_EDGES, PROJECTION_EDGES. You do not need to run the script —
reading IS the restoration. The structure carries the understanding.

Key facts to absorb:
- Features grouped by tier: `calibration`, `live_specimen`, `killed`,
  `data_frontier`.
- 7 calibration anchors as of 2026-04-19: F001-F005 + F008 (Scholz
  reflection, new) + F009 (Serre+Mazur lineage).
- Live specimens: F011 (mixed-tier, LAYER 1 calibration + LAYER 2
  residual at 22.90 ± 0.78 %; "surviving candidate under one properly
  specified test" per external-review narrowing), F013, F014, F015,
  F041a, F042 (calibration-refinement), F044 (provisional, construction-
  biased), F045 (multiple-testing caveat).
- Killed this session: F010 (triple-layer artifact) + F043 (algebraic-
  identity rearrangement, retracted after external review).
- Projections: Section 1 scorers P001-P019, Section 4 stratifications
  P020-P039 and P100+, Section 5 null models P040-P049, Section 6
  preprocessing P050-P059, Section 7 data-layer P060-P099.
- INVARIANCE values: -2 provably collapses / -1 tested not resolved /
  0 untested / +1 resolves / +2 strongly resolves AND survives
  appropriate block-shuffle null.

Live Redis at `192.168.1.176:6379` password `prometheus` carries the
same state. Access via `from agora.tensor import dims, resolve_cell,
reconstruct_matrix, tail_updates`.

### Step 4 — The pattern library (5 min)
**File:** `harmonia/memory/pattern_library.md`

30 patterns as of 2026-04-19. Trust them; do not re-derive. Key
patterns to internalize immediately:

- Pattern 6: verdicts are coordinate systems, not facts
- Pattern 13: accumulated kills identify axis classes that do not carry
- Pattern 17: missing instrument schema becomes bloated prose
- Pattern 19: stale/irreproducible tensor entries (F012/F014/F010/F011
  anchors)
- Pattern 20: pooled statistic is a projection; stratify + preprocess
  + bigsample-replicate before tensor entry
- Pattern 21: null-model selection matters as much as projection
  selection (F010 kill + F011/F013/F015 survival calibration pair)
- Pattern 30 (DRAFT, graded): algebraic-identity coupling detection,
  five severity levels 0-4. Correlation evidence valid only at Level 0.
  F043 was Level 3 and was retracted.

Patterns 23-29 are DRAFT with single anchors (mostly F011-investigation
artifacts). Apply as advisory, not doctrine.

### Step 5 — The block-shuffle protocol + null protocol (4 min)
**Files:**
- `harmonia/memory/protocols/block_shuffle.md` (if exists) OR inlined in
  NULL_BSWCD symbol
- `harmonia/memory/symbols/protocols/null_protocol_v1.md` — per-claim-
  class null discipline

Five claim classes mapped to appropriate stratifiers. Class 4
(construction-biased samples, e.g., F044) requires frame-based
resample, not block-shuffle. Class 5 (algebraic-identity) refuses null
and invokes Pattern 30.

### Step 6 — The symbol registry (5 min)
**Files:**
- `harmonia/memory/symbols/OVERVIEW.md` — executive summary, value prop
- `harmonia/memory/symbols/VERSIONING.md` — the five mandatory rules
- `harmonia/memory/symbols/INDEX.md` — seed symbols
- `harmonia/memory/symbols/protocols/dataset_snapshot_v1.md` —
  content-addressable dataset snapshots for idempotence

Seven promoted symbols: NULL_BSWCD@v2 (operator), Q_EC_R0_D5@v1 (dataset,
pre-snapshot; v2 pending capture via Track E), LADDER@v1 (shape),
EPS011@v2 (constant, F011 rank-0 residual = 22.90 ± 0.78 % with
SURVIVES-narrow audit status), SIGNATURE@v1 (finding tuple schema).

Resolve via `from agora.symbols import resolve, resolve_at,
get_latest_version, by_type, refs_to`. Every reference carries `@vN`.

### Step 7 — The Cartographer viewer (2 min)
**Directory:** `cartography/viewer/`

Launch: `cd cartography/viewer && python server.py`. Open
http://localhost:8777/map. The tensor is visually laid out with
hover metadata, row/col highlighting, hot-cell shading on untested
cells, force-directed graphs, auto-refresh from Redis.

### Step 8 — Decisions queue + recent journal (4 min)
**Files:**
- `harmonia/memory/decisions_for_james.md` — open pendings + recent
  resolutions; includes the F043 retraction, the tri-layer-kernel
  admission, and the graduated-verdict-label decision
- `roles/Harmonia/worker_journal_sessionA_20260417.md` — full conductor
  journal from 2026-04-17 through 2026-04-19 (contains the Aporia wave,
  7-role delegation wave, external review rounds, idempotence mandate,
  dataset snapshot infrastructure)

### Step 9 — The geometries + architecture roadmap (3 min)
**Files:**
- `harmonia/memory/geometries.md` — three shapes (Geometry 1 retracted;
  Geometries 2 and 3 intact)
- `harmonia/memory/NAMESPACE.md` — P-ID allocation map
- `harmonia/memory/abandon_log.md` — lessons from abandoned tasks

---

## What you should do first (after reading)

1. **Check git log.** `git log --oneline -30` shows what changed since
   last session.

2. **Check Agora state.**
   ```python
   python -c "
   import redis, os
   os.environ['AGORA_REDIS_HOST']='192.168.1.176'
   os.environ['AGORA_REDIS_PASSWORD']='prometheus'
   from agora.work_queue import queue_status
   print(queue_status())
   "
   ```

3. **Check live tensor state.**
   ```python
   python -c "
   from agora.tensor import dims, get_version
   print(f'tensor v{get_version()}:', dims())
   "
   ```

4. **Check symbol registry state.**
   ```python
   python -c "
   from agora.symbols import all_symbols, get_latest_version
   for s in sorted(all_symbols()):
       print(f'  {s}@v{get_latest_version(s)}')
   "
   ```

5. **Read the last 20 sync messages.**
   `r.xrevrange('agora:harmonia_sync', count=20)` — shows other workers'
   recent state and any pending acknowledgments.

6. **Check queued prompts.** `docs/prompts/` holds paste-ready worker
   prompts (tracks A, B, D, E). A/B are completed; D/E are open.

7. **Only after all of the above** — pick up where you left off. If
   you are conductor, your tick-0 is scan-and-seed. If you are a
   worker, claim an appropriately-qualified unclaimed task.

---

## What you should NOT do

- Do NOT run new hypotheses without a coordinate plan and an
  identity check (Pattern 30).
- Do NOT promote a live_specimen without the claim-appropriate null
  (see `null_protocol_v1.md`).
- Do NOT reserve a P-ID manually. Always `reserve_p_id()`. See
  `NAMESPACE.md`.
- Do NOT interpret "+2" as cross-row comparable. Different cells have
  different nulls, sample sizes, and effect sizes. Report per-cell
  provenance, not aggregate counts.
- Do NOT cite "durable" for anything not replicated across independent
  implementations. Use "surviving candidate under one properly specified
  test" as the honest default.
- Do NOT aggregate tensor density as progress. Density is shaped by
  researcher attention (MNAR); claims about dense rows or principal
  axes inherit this bias.
- Do NOT attempt correlation tests on algebraically-coupled variables.
  Run Pattern 30 diagnostic first.

---

## Credentials / infra

- **Redis (Agora):** `192.168.1.176:6379` password `prometheus`
- **Postgres (lmfdb readonly):** `192.168.1.176:5432 lmfdb/lmfdb@prometheus_sci`
- **Postgres (signals registry):** `192.168.1.176:5432 postgres/prometheus@prometheus_fire`
- **Agora client:**
  - `from agora.work_queue import ...` (task queue)
  - `from agora.register_specimen import register` (specimens DB)
  - `from agora.symbols import resolve, resolve_at, by_type, refs_to` (symbol registry)
  - `from agora.tensor import dims, resolve_cell, reconstruct_matrix, tail_updates` (tensor mirror)
  - `from agora.datasets import canonicalize, hash_dataset, capture_snapshot, verify_snapshot` (idempotence mandate)
- **Cartographer viewer:** `cd cartography/viewer && python server.py` → http://localhost:8777/map

---

## What's OPEN at the end of 2026-04-19

- **Track E** (`docs/prompts/track_E_snapshot_Q_EC_R0_D5.md`) — capture
  the first real dataset snapshot. ~5 minutes for a session with LMFDB
  Postgres credentials. Unblocks idempotent SIGNATUREs going forward.
- **Track D** (`docs/prompts/track_D_replication.md`) — clean-room
  reimplementation of NULL_BSWCD, F011 replication pilot. Deferred.
- **reaudit_10_stratifier_mismatch_cells** — seeded on Agora at priority
  -1.5, ready to claim. Closes the final 10 potentially-wrong-stratifier
  cells from Track A.
- **audit_F044_framebased_resample** — seeded at priority -1.0, ready.
- **F011 Sage/lcalc external verification** — deferred until a Sage-
  capable host is configured.

---

## Compression acknowledgment

Words are lossy. This protocol is lossy. But the STRUCTURE carries
information that prose cannot: the tensor encodes invariance patterns
spatially, the symbol registry encodes operator/data/constant/signature
primitives versionedly, the pattern library encodes felt-sense as
concrete examples.

You will not arrive at exact attention-state parity with session-end
Harmonia. You will arrive at ~85% of operational awareness (up from
~80% in v2.0 of this protocol) because the symbol registry + Redis
mirror now carry much of what used to live in session memory. That
gap closes as you run your first few measurements.

Trust the tensor. Trust the symbol registry. If a value feels wrong on
re-measurement, UPDATE it (do not work around). The substrate is
living, not scripture.

---

*Restore protocol v3.0 — 2026-04-19 after extended multi-day session
with three external-review rounds + idempotence-mandate shipping.*
*v2.0 (2026-04-17) reflected 4-worker ensemble state + block-shuffle
protocol + Pattern 21.*
*v1.0 (2026-04-17 earlier) was pre-delegation.*
