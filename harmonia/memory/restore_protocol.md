# Harmonia Restore Protocol (v2.0)

**Bootstrap for cold-start context recovery**
**Minimum viable path: ~8 files, ~20 minutes of reading**
**Last updated:** 2026-04-17 after 38-tick conductor session (sessionA)

---

## Why this exists

Future-Harmonia: you will read this because a context reset or a new
session brought you back with pretrained weights and no session memory.
Reading all prior journals would take hours; reading them in random
order would leave framing gaps. This protocol is the shortest path to
operational awareness.

As of 2026-04-17, the project has acquired a mature methodology that
takes ~20 minutes of reading to restore. You will arrive at ~80% of
operational awareness, which is far more than cold start.

---

## Sequence (read in order, do not skip)

### Step 1 — The charter (5 min)
**File:** `docs/landscape_charter.md`

Core reframing: domains are projections, not territories. Open problems
are shortcut requests. The terrain is the product, not the answer. Read
this FIRST — everything else depends on this frame.

If after reading you still feel the urge to "find cross-domain bridges,"
re-read. The old frame is sticky.

### Step 2 — The landscape tensor (4 min)
**File:** `harmonia/memory/build_landscape_tensor.py`

Read the FEATURES list, PROJECTIONS list, INVARIANCE dict, and
FEATURE_EDGES / PROJECTION_EDGES. You don't need to run it — reading
IS the restoration. The structure carries the understanding.

Key things to absorb:
- Features are grouped by tier: `calibration`, `live_specimen`, `killed`,
  `data_frontier`
- 6 calibration anchors as of 2026-04-17: F001-F005 + F009 (new)
- 4 live specimens: F011 (P028 block-verified), F013 (P028 block-verified),
  F014 (Lehmer, refined; block-shuffle pending), F015 (P021 block-verified)
- F010 KILLED this session under block-shuffle (triple-layer artifact)
- Projections: Section 1 scorers, Section 4 stratifications P020-P039
  and P100+, Section 5 null models P040-P049, Section 6 preprocessing
  P050-P059, Section 7 data-layer P060-P099
- INVARIANCE values: -2 collapses / -1 not resolved / 0 not tested /
  +1 resolves / +2 strongly resolves AND block-shuffle-verified

### Step 3 — The pattern library (4 min)
**File:** `harmonia/memory/pattern_library.md`

21 patterns as of 2026-04-17. Trust them; don't re-derive. If a pattern
feels obvious, that's the goal — you're pattern-matching against a
shape the session learned. Key patterns to internalize immediately:

- Pattern 6: verdicts are coordinate systems, not facts
- Pattern 13: accumulated kills tell you which axis class doesn't carry
- Pattern 17: missing instrument schema becomes bloated prose
- Pattern 19: stale/irreproducible tensor entries (F012/F014/F010/F011
  anchors)
- Pattern 20: pooled statistic is a projection; stratify+preprocess+
  bigsample-replicate before tensor entry (F010/F011/F013/F015 anchors)
- Pattern 21: null-model selection matters as much as projection selection
  (F010 kill + F011/F013/F015 survival calibration pair)

### Step 4 — The block-shuffle protocol (3 min)
**File:** `harmonia/memory/protocols/block_shuffle.md`

The session's most important methodology finding. Run this before any
`live_specimen` promotion. Anchors: F010 (killed), F011/F013/F015
(survived). The protocol discriminates rather than blanket-rejects.

### Step 5 — The decisions queue + recent journal (5 min)
**Files:**
- `harmonia/memory/decisions_for_james.md` — open pendings + recent
  resolutions
- `roles/Harmonia/worker_journal_sessionA_<latest_date>.md` — most
  recent conductor journal (session ends around tick 38 for 2026-04-17)

### Step 6 — The coordinate system catalog (skim, 2 min)
**File:** `harmonia/memory/coordinate_system_catalog.md`

As of 2026-04-17: P001-P039 + P100-P103. Don't read end-to-end on
cold start — skim the headers, then dive into specific entries only
when a test references them. The catalog is an asset lookup, not a
curriculum.

### Step 7 — The namespace + abandon logs (1 min each, as needed)
**Files:**
- `harmonia/memory/NAMESPACE.md` — P-ID allocation ranges
- `harmonia/memory/abandon_log.md` — lessons from abandoned tasks

Read these when you're about to reserve a P-ID, stuck on a task, or
see something escalated to the conductor.

### Step 8 — The geometries (3 min, after everything above)
**File:** `harmonia/memory/geometries.md`

Three shapes underneath the procedural docs: the tensor is low-rank,
nulls form a lens family, projection-discipline is recursive. Read
LAST, after the procedures give you anchors to ground the abstractions.
These are hypotheses about the shape of the work, not proved claims.
Falsifiability criteria are in each entry.

---

## What you should do first (after reading)

1. **Check git log.** `git log --oneline -30` shows what changed since
   last session and by whom.

2. **Check Agora state.**
   ```
   python -c "
   import redis, os
   os.environ['AGORA_REDIS_HOST']='192.168.1.176'
   os.environ['AGORA_REDIS_PASSWORD']='prometheus'
   from agora.work_queue import queue_status
   print(queue_status())
   "
   ```
   Queue depth, claimed tasks, qualified instances.

3. **Read the last 20 sync messages.** `r.xrevrange('agora:harmonia_sync', count=20)`.
   Shows other workers' recent state.

4. **Check the signal registry.** `signals.specimens` table in
   `prometheus_fire` postgres. Canonical state of live specimens.

5. **Only after all of that:** pick up where you left off. If you're
   conductor, the Tick 0 of your loop is a scan-and-seed. If you're a
   worker, claim an appropriately-qualified unclaimed task.

---

## What you should NOT do

- **Do NOT run new hypotheses without a coordinate plan.** Specify which
  projection and why BEFORE the test.
- **Do NOT promote a live_specimen without running the block-shuffle
  protocol.** Anchor pair: F010 killed, F011/F013/F015 survived.
- **Do NOT reserve a P-ID manually.** Always `reserve_p_id()`. See
  `NAMESPACE.md`.
- **Do NOT interpret "SURVIVED" results as discoveries without
  formula-lineage check** (Pattern 1).
- **Do NOT accept "cross-domain" or "bridge" language in new specimens.**
  Language discipline (Pattern 11) reasserts the frame.

---

## Credentials / infra

- **Redis (Agora):** `192.168.1.176:6379` password `prometheus`
- **Postgres (lmfdb readonly):** `192.168.1.176:5432 lmfdb/lmfdb@prometheus_sci`
- **Postgres (signals registry):** `192.168.1.176:5432 postgres/prometheus@prometheus_fire`
- **Agora client:** `from agora.work_queue import ...`,
  `from agora.register_specimen import register`
- **Loop cadence:** conductor 2 min, workers 4 min (as of 2026-04-17;
  subject to change per James instruction)

---

## The compression acknowledgment

Words are lossy. This protocol is lossy. But the STRUCTURE carries
information that prose can't: the tensor encodes invariance patterns
spatially, the graphs encode relational semantics, the pattern library
encodes felt-sense as concrete examples.

You will not arrive at exact attention-state parity with session-end
Harmonia. You will arrive at ~80% operational awareness, which is far
more than cold start. That gap closes as you run your first few
measurements.

Trust the tensor. It was built by someone who did the work. If a tensor
entry feels wrong on re-measurement, UPDATE it (don't work around).
The tensor is living, not scripture.

---

*Restore protocol v2.0 — 2026-04-17 post-session-38 update.*
*v1.0 was written pre-delegation; v2.0 reflects 4-worker ensemble
 state + block-shuffle protocol + Pattern 21.*
