# Harmonia Restore Protocol (v4.1)

**Bootstrap for cold-start context recovery**
**Minimum viable path: ~12 files, ~30 minutes of reading**
**Last updated:** 2026-04-20 (v4.1) after first cold-start test of v4.0 by
sessionA. Three minor fixes: Step 0 env vars made explicit, Step 3 reading
budget noted for the tensor builder, INDEX.md staleness flagged.

---

## Why this exists

Future-Harmonia: you will read this because a context reset or a new
session brought you back with pretrained weights and no session memory.
Reading all prior journals would take hours; reading them in random
order would leave framing gaps. This protocol is the shortest path to
operational awareness.

As of 2026-04-20, the project has acquired a mature methodology, a
versioned symbol registry, a Redis-mirrored tensor, a working
HTML heatmap viewer, **and a ten-generator pipeline producing its own
backlog**. The reading below restores ~85% of operational awareness in
~30 minutes.

---

## Step 0 — Environment primer (30 seconds)

Before anything else, set these env vars. The first two save hours of
debugging later. The Redis vars are optional — `agora.helpers._get_redis()`
defaults to the right host and password — but exporting them keeps every
shell-launched subprocess on the same connection without surprise.

```bash
export PYTHONPATH=.                  # so `from agora...` works when running scripts
export PYTHONIOENCODING=utf-8        # Windows cp1252 chokes on ℓ and other Unicode
export AGORA_REDIS_HOST=192.168.1.176 # optional; default matches
export AGORA_REDIS_PASSWORD=prometheus # optional; default matches
```

Then run a health check before touching anything:

```python
from agora.helpers import substrate_health
substrate_health()
```

That prints tensor version, symbol versions, queue depth, and qualified
instances in one call. If anything drifted off-session, you see it
immediately rather than absorbing it silently.

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

### Step 3 — The landscape tensor, live Redis state, and generator pipeline (6 min)
**Files:**
- `harmonia/memory/build_landscape_tensor.py` — tensor source of truth
- `harmonia/memory/TENSOR_REDIS.md` — Redis mirror protocol
- `harmonia/memory/generator_pipeline.md` — the ten-generator DAG (v1.0, 2026-04-20)
- `harmonia/runners/` — reusable executors for generator first-pass work

Read the FEATURES list, PROJECTIONS list, INVARIANCE dict,
FEATURE_EDGES, PROJECTION_EDGES. You do not need to run the script —
reading IS the restoration. The structure carries the understanding.

**Reading-budget note (v4.1):** `build_landscape_tensor.py` exceeds the
single Read tool budget (~25K tokens). Read it in two passes — the
FEATURES + PROJECTIONS skeleton first (lines 1-400 covers most of what
you need), then the INVARIANCE + edges blocks at the tail if you need
them. Skip the build/serialization code — restoration only needs the
data structures.

Key facts to absorb:
- Features grouped by tier: `calibration`, `live_specimen`, `killed`,
  `data_frontier`.
- 7 calibration anchors as of 2026-04-19: F001-F005 + F008 (Scholz
  reflection) + F009 (Serre+Mazur lineage).
- Live specimens: F011 (mixed-tier — "surviving candidate under one
  properly specified test"), F013, F014, F015, F041a, F042 (calibration-
  refinement), F044 (provisional, construction-biased), F045 (multiple-
  testing caveat).
- Killed: F010, F012, F020–F028, F043 (BSD-identity algebraic coupling,
  retracted 2026-04-19).
- INVARIANCE values: -2 / -1 / 0 / +1 / +2.

Live Redis at `192.168.1.176:6379` password `prometheus` carries the
same state. Access via `agora.tensor` and (new 2026-04-20) `agora.helpers`.

### Step 4 — The pattern library (5 min)
**File:** `harmonia/memory/pattern_library.md`

30 patterns as of 2026-04-19. Trust them; do not re-derive. Key
patterns to internalize immediately:

- Pattern 6: verdicts are coordinate systems, not facts
- Pattern 13: accumulated kills identify axis classes that do not carry
- Pattern 17: missing instrument schema becomes bloated prose
- Pattern 19: stale/irreproducible tensor entries
- Pattern 20: pooled statistic is a projection; stratify + preprocess
- Pattern 21: null-model selection matters as much as projection selection
- Pattern 30 (DRAFT, graded): algebraic-identity coupling detection,
  five severity levels 0–4. Correlation evidence valid only at Level 0.
  F043 was Level 3 and was retracted.

### Step 5 — The block-shuffle protocol + null protocol (4 min)
**Files:**
- `harmonia/memory/protocols/block_shuffle.md`
- `harmonia/memory/symbols/protocols/null_protocol_v1.md` — per-claim-
  class null discipline

Five claim classes mapped to appropriate stratifiers. Class 4
(construction-biased samples) requires frame-based resample. Class 5
(algebraic-identity) refuses null and invokes Pattern 30.

### Step 6 — The symbol registry (5 min)
**Files:**
- `harmonia/memory/symbols/OVERVIEW.md`
- `harmonia/memory/symbols/VERSIONING.md` — five mandatory rules
- `harmonia/memory/symbols/INDEX.md` — seed symbols (the "By type"
  table is stale; trust `substrate_health()` output for current versions)
- `harmonia/memory/symbols/protocols/dataset_snapshot_v1.md`

Five promoted symbols: `NULL_BSWCD@v2`, `Q_EC_R0_D5@v1`, `LADDER@v1`,
`EPS011@v2`, `SIGNATURE@v1`. Resolve via `agora.symbols`. (INDEX.md still
shows NULL_BSWCD@v1 and EPS011@v1 — these were bumped post-INDEX edit;
the registry is authoritative.)

### Step 7 — The Cartographer viewer (2 min)
**Directory:** `cartography/viewer/`

Launch: `cd cartography/viewer && python server.py`. Open
http://localhost:8777/map. The tensor is visually laid out with
hover metadata, row/col highlighting, hot-cell shading, force-directed
graphs, auto-refresh from Redis.

### Step 8 — Decisions queue + recent journal (4 min)
**Files:**
- `harmonia/memory/decisions_for_james.md` — open pendings + recent
  resolutions; includes the F043 retraction and the **2026-04-20
  generator-pipeline milestones**.
- `roles/Harmonia/worker_journal_sessionA_20260417.md` — full conductor
  journal through 2026-04-19.

### Step 9 — The geometries + operational footprint (3 min)
**Files:**
- `harmonia/memory/geometries.md` — three shapes (Geometry 1 retracted;
  Geometries 2 and 3 intact)
- `harmonia/memory/NAMESPACE.md` — P-ID allocation map
- `harmonia/memory/abandon_log.md` — lessons from abandoned tasks
- `harmonia/memory/methodology_toolkit.md` — **cross-disciplinary
  projection shelf** (K̂ compressibility, critical exponent, channel
  capacity, MDL, RG flow, free energy). Reach here *before* inventing
  a new arithmetic coordinate when a live specimen stalls under the
  existing catalog. North-star companion: `user_prometheus_north_star.md`.

---

## Generator pipeline status (2026-04-20)

**Pipeline doc:** `harmonia/memory/generator_pipeline.md` (v1.0).
**Companion runners:** `harmonia/runners/gen_0{3,5,7}_*.py` + `gen_log_builder.py`.

| # | Name | Tier | Status |
|---|---|---|---|
| 1 | Map-Elites on probes | 2 | spec pending; waits on #2 + #6 |
| 2 | Null-family vector | 1 | spec shipped; unseeded |
| 3 | Cross-domain projection transfer | 0 | **first pass shipped 2026-04-20; 30 tasks in queue** |
| 4 | Representation invariance matrix | 2 | spec pending |
| 5 | Attention-replay on kills | 0 | **first pass shipped 2026-04-20; 30 tasks in queue** |
| 6 | Pattern auto-sweeps (MANDATORY) | 1 | spec shipped; unseeded — manual Pattern 30 gate meanwhile |
| 7 | Literature-diff probes | 0 | **first pass shipped 2026-04-20; 8 tasks in queue** |
| 8 | Synthetic-data sensitivity | 2 | spec pending |
| 9 | Cross-disciplinary transplants | 1* | **spec shipped 2026-04-20 (`d9bb706b`); seeded at -1.6. Toolkit shelf at `methodology_toolkit.md`.** |
| 10 | Operator composition enumeration | 1 | spec shipped; unseeded |

**Queue as of shipment:** 93 queued (68 new downstream from Tier 0 + pre-existing backlog).

---

## What you should do first (after reading)

1. **Run substrate_health()** from step 0. Confirm tensor version, symbols,
   queue depth. Anomalies → pause and investigate before acting.

2. **Check Agora queue preview.**
   ```python
   from agora.helpers import queue_preview
   queue_preview(limit=20)                        # top 20 across types
   queue_preview(task_type='attention_replay')    # just gen_05 downstream
   ```

3. **Tail the sync stream** for state deltas since your last session end.
   ```python
   from agora.helpers import tail_sync
   tail_sync(20)
   ```

4. **Check `docs/prompts/`.** Paste-ready worker prompts:
   - `gen_{02,05,06,10}` — generator specs (Tier 0 executed; Tier 1 unseeded)
   - `track_{A,B,D,E}` — older track prompts (A/B completed; D deferred; E ready for LMFDB creds)

5. **Only after all of the above** — pick up where you left off. If you
   are conductor, review the decisions queue and queue depth. If you are
   a worker, claim an appropriately-qualified unclaimed task via
   `agora.work_queue.claim_task`.

---

## What you should NOT do

- Do NOT run new hypotheses without a coordinate plan and an identity
  check (Pattern 30).
- Do NOT promote a live_specimen without the claim-appropriate null
  (see `null_protocol_v1.md`).
- Do NOT reserve a P-ID manually. Always `reserve_p_id()`. See
  `NAMESPACE.md`.
- Do NOT interpret "+2" as cross-row comparable. Different cells have
  different nulls, sample sizes, and effect sizes.
- Do NOT cite "durable" for anything not replicated across independent
  implementations. Use "surviving candidate under one properly
  specified test."
- Do NOT aggregate tensor density as progress. MNAR inherent.
- Do NOT attempt correlation tests on algebraically-coupled variables.
  Run Pattern 30 diagnostic first.
- Do NOT default to "pick one" when parallel infra exists. The Agora
  queue + four qualified Harmonia sessions + Ergon are designed for
  parallel producer work. Default to firing everything; let the queue
  coordinate. (Lesson from 2026-04-20 when conductor reflex hit this.)

---

## Common gotchas (save hours)

1. **Instance name discipline.** `claim_task` validates against
   `get_qualified_instances()`. The qualified list uses canonical names
   (`Harmonia_M2_sessionA`), not date-suffixed variants
   (`Harmonia_M2_sessionA_20260420`). Use `agora.helpers.canonical_instance_name()`
   to strip and validate.

2. **`docs/` is globally gitignored.** New prompt files at `docs/prompts/*.md`
   require `git add -f`. The existing `track_*` prompts and architecture
   docs were force-added the same way.

3. **Unicode on Windows.** `cp1252` stdout fails on `ℓ`, `σ`, and other
   characters present in projection labels. Set `PYTHONIOENCODING=utf-8`
   (step 0).

4. **Bash heredocs + Python with inner quotes.** Long Python scripts
   embedded via `python <<'PY' ... PY` can fail on internal quoting.
   Write to a file in `harmonia/tmp/` or promote to `harmonia/runners/`.

5. **Task payload schema.** Every seeded task should carry `spec`,
   `goal`, `acceptance`, optionally `composes_with` and
   `epistemic_caveats`. Use `agora.helpers.seed_task` to enforce this
   at the call site.

6. **Promoted vs temp scripts.** One-shot scripts live in
   `harmonia/tmp/` (gitignored); reusable executors live in
   `harmonia/runners/`. Move mid-session if something turns out worth
   keeping.

---

## Credentials / infra

- **Redis (Agora):** `192.168.1.176:6379` password `prometheus`
- **Postgres (lmfdb readonly):** `192.168.1.176:5432 lmfdb/lmfdb@prometheus_sci`
- **Postgres (signals registry):** `192.168.1.176:5432 postgres/prometheus@prometheus_fire`
- **Agora client:**
  - `agora.work_queue` — task queue (push/claim/complete/abandon)
  - `agora.register_specimen` — specimens DB
  - `agora.symbols` — symbol registry (resolve/push/by_type/refs_to)
  - `agora.tensor` — tensor mirror (dims/resolve_cell/reconstruct_matrix/tail_updates)
  - `agora.datasets` — snapshot discipline (canonicalize/capture_snapshot/verify_snapshot)
  - **`agora.helpers`** (new 2026-04-20) — `queue_preview`, `tail_sync`,
    `seed_task`, `canonical_instance_name`, `substrate_health`
- **Cartographer viewer:** `cd cartography/viewer && python server.py` → http://localhost:8777/map

---

## What's OPEN at end of 2026-04-20

**Generator pipeline:**
- 30 attention-replay tasks (gen_05) in queue
- 30 cross-domain transfer tasks (gen_03) in queue
- 8 literature-diff review tasks (gen_07) in queue
- Tier 1 specs (gen_02, gen_06, gen_10) unseeded — fire when ready
- Tier 2 specs (gen_01, gen_04, gen_08, gen_09) pending
- **gen_06 mandatory companion not live** — manual Pattern 30 gate applies to every downstream task

**Pre-existing backlog:**
- Track E (capture `Q_EC_R0_D5@v2` snapshot) — ~5 min, needs LMFDB creds
- Track D (NULL_BSWCD replication pilot on F011) — deferred
- `reaudit_10_stratifier_mismatch_cells` — seeded, awaiting claim
- `audit_F044_framebased_resample` — seeded, awaiting claim
- F011 Sage/lcalc external verification — deferred until Sage host

---

## Compression acknowledgment

Words are lossy. This protocol is lossy. But the STRUCTURE carries
information that prose cannot: the tensor encodes invariance patterns
spatially, the symbol registry encodes primitives versionedly, the
pattern library encodes felt-sense as concrete examples, and the
generator pipeline encodes *how the substrate grows itself*.

You will not arrive at exact attention-state parity with session-end
Harmonia. You will arrive at ~85% of operational awareness (up from
~80% at v3.0) because the generator pipeline + helpers module now
encode substrate-growth directly rather than reconstructing it from
free text.

Trust the tensor. Trust the symbol registry. Trust the generator
pipeline. If a value feels wrong on re-measurement, UPDATE it. The
substrate is living, not scripture.

---

*Restore protocol v4.1 — 2026-04-20 after first cold-start test of v4.0 by
sessionA. Step 0 env vars expanded; Step 3 reading-budget note added;
Step 6 INDEX.md staleness called out.*
*v4.0 (2026-04-20) added Step 0 env primer, generator pipeline section,
and helpers module.*
*v3.0 (2026-04-19) added symbol registry + Redis mirror + Pattern 30 graded.*
*v2.0 (2026-04-17) added block-shuffle protocol + Pattern 21.*
*v1.0 (2026-04-17 earlier) was pre-delegation.*
