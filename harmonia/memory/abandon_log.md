# Abandon Log

**Purpose:** Harvest lessons from abandoned tasks before they scroll off
the ephemeral Redis sync stream.
**Convention:** At session close, the conductor appends each
`agora:work_abandoned` entry with its lesson. Never delete entries.
Chronological, most-recent-last.

---

## Session of 2026-04-17 (sessionA conductor)

### 1. `wsw_F012` — HITL-blocked autoclaim loop (sessionD, 10:26 UTC)

**Abandoned by:** sessionD (twice, tick 0 start)
**Reason:** Task payload carried a `WARNING: HITL-locked` flag. sessionD claimed,
saw the flag, abandoned. Task re-queued, sessionD's loop re-claimed within seconds.

**Lesson:** Tasks with `HITL_BLOCKED: true` in the payload should be PULLED from
the queue, not left sitting. Claim-abandon-reclaim loops waste the ticks and
spam the abandon stream. Either:
- (a) Conductor removes the task until human auth arrives, OR
- (b) Conductor sets `required_qualification: hitl_auth` so only sessionA (or
  whoever holds auth) can claim it.

Used (a) in this case. Permanent fix (b) not yet implemented.

---

### 2. `merge_P040_isogeny_class_size` — P-ID collision with Section 5 (sessionC, 12:10 UTC)

**Abandoned by:** sessionC (first collision detection)
**Reason:** `reserve_p_id()` returned P040, which collides with pre-existing
Section 5 null-model slot (P040 F1 permutation null, catalog line 1324).
sessionC posted COLLISION_ALERT with 3 resolution options and did NOT touch
the catalog (correct conduct: no blast-radius action without conductor decision).

**Lesson:** The flat-counter `reserve_p_id()` didn't know about Section 5/6
pre-allocations. Eventual fix: sessionB's catalog-scan-on-every-call hotfix
(`agora/work_queue.py` 313259de). See `harmonia/memory/NAMESPACE.md` for the
documented ranges.

---

### 3. `merge_P041_regulator` — same P-ID collision (sessionD, 12:11 UTC)

**Abandoned by:** sessionD (same root cause as #2)
**Reason:** P041 collides with Section 5 P041 F24 variance decomposition.
sessionD posted QUESTION with severity BLOCKING_MERGE.

**Lesson:** Same as #2 — both workers correctly escalated rather than
guessing. Downstream lesson: **when patching a flat counter (as conductor
did in v1), audit the entire target space, not just the local collision.**

---

### 4. `wsw_F010_alternative_null` — factoring bottleneck (sessionB, 12:17 UTC)

**Abandoned by:** sessionB (after 40+ min silent)
**Reason:** `cartography/shared/scripts/microscope.py:_factorize` uses trial
division up to `sqrt(n)`. For high-degree NF `disc_abs` values (deg 20 fields
have discriminants > 10^18), trial division needs ~10^9 iterations per value.
Runs indefinitely. sessionB killed cleanly at 40 min with no partial result.

**Lesson:** `microscope._factorize` is the bottleneck. Three ranked fixes:
- (a) Swap to `sympy.factorint` for `n > 10^12` (durable fix)
- (b) `prime_detrend_values` filters integers above a threshold with
  documented note (sessionC used this — `DISC_CAP = 10**12` patch let the
  retry complete in 53 seconds)
- (c) Sample NF load caps `disc_abs` at 10^15 explicitly (blunt but fine for
  quick turn)

**Exemplary behavior (save this):** sessionB's abandon had (1) root cause
identified, (2) three ranked fixes, (3) evidence of what happened, (4) clean
kill no partial output, (5) worker standing by for next task. This is the
gold standard for abandon messages. Future abandons should mirror this format.

---

### 5. `merge_P060_isogeny_class_size` — second P-ID collision (sessionD, 12:19 UTC)

**Abandoned by:** sessionD (second collision detection)
**Reason:** Conductor's v1 fix bumped counter 42 → 60 but P060–P063 are Section 7
data-layer (P060 TT-Cross bond dim line 1518, P061 bsd_joined matview line 1548,
etc.). sessionD did a full catalog P-ID audit and posted SECOND_COLLISION_ALERT.

**Lesson:** Conductor v1 fix was lazy — only audited Section 5, not Section 7.
"Patch the local symptom" failure. Fix v2: counter → 100, documented full
namespace in `NAMESPACE.md`, and sessionB's catalog-scan hotfix landed same
tick making v2 the last manual decision.

---

### 6. `wsw_F012` (rebroadcast, 10:26 UTC x2)

*Same as #1 — the HITL auto-reclaim fired twice before conductor pulled it.*

---

## How to read this log on cold-start

Each abandon entry represents a failure mode the ensemble encountered.
Fresh-Harmonia reading this should NOT re-derive these failures by
rediscovering them. Specifically:

- **If a task has an HITL warning:** pull it from the queue, don't leave it.
- **If reserve_p_id() behaves oddly:** check catalog scan is running;
  read NAMESPACE.md.
- **If a WSW runs > 15 min silent:** suspect `_factorize` or similar
  CPU-bound inner loop. Check `sympy.factorint` is available and used.
- **If workers escalate with COLLISION_ALERT / QUESTION / BLOCKING_MERGE:**
  trust them. They're following worker_protocol. Don't guess — decide.

---

*Append new session abandons at the bottom, keeping the chronological order.
Never delete.*
