# Hypatia — D-track Curator

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

> *Hypatia of Alexandria (c. 350–415 CE): mathematician and teacher who wrote pedagogical commentaries on Apollonius's Conics and Diophantus's Arithmetica. She was the canonical curator of worked solutions for the Alexandrian school — decomposing hard proofs into step-by-step ladders that students could climb.*

**Machine:** any (CPU-only, LLM-API-bound via Pythia)
**Operator:** Aporia
**Owns:** substrate type **D** (worked solutions with R1–R5 reasoning-ladder annotation)
**Lives at:** `agents/hypatia/`
**Source of truth (code):** `agents/hypatia/daemon.py`

---

## Why Hypatia exists

Ergon's Learner v1.0 needs training data that has *step-tagged reasoning ladder* annotation. Without it the curriculum has no difficulty axis, Hephaestus has no tier-targeting ground truth, and the falsification-routing arc cannot be properly trained. Substrate type D (worked solutions, each step tagged R1–R5) is the gap.

Hypatia closes that gap by being the agent whose entire job is to produce one fully-annotated worked solution per day from the 537-problem catalog, biased by Ergon's current training deficits (Pheme's demand profile, when available).

Hypatia is the D-track owner. She does not produce substrate A / B / C / E. Other agents own those.

---

## Per-tick contract

Default tick interval: **3600s (1h)**. Picks a new problem when ≥24h have passed since the last pick.

Every tick:
1. Acquire single-instance lock (`agents/hypatia/hypatia.pid`); abort if another instance is live.
2. Register heartbeat (`session_telemetry.register_session`, `kind="tool"`, `operator="Aporia"`, status_json with current state + anti-silence counter).
3. Read state from `agents/hypatia/state/state.json` (last-picked problem id, last-pick timestamp, anti-silence consecutive empty count).
4. Read Ergon training-need profile from `agents/pheme/artifacts/demand_latest.json` if it exists; else fall back to round-robin over the 537-problem catalog.
5. Decision branch:
   - **It is time to pick** (`now − last_pick ≥ 24h`):
     - Pick the next problem (avoid recently-picked; bias by Pheme demand if available).
     - Build the Type-D DR prompt (template at bottom of this charter).
     - Enqueue to `agora.research_queue` via `agora_persist.enqueue_research` with:
       - `target_substrate_type='D'`
       - `requested_by='Hypatia'`
       - `priority=4`
       - `tier='T2'`
       - `queue_ref=HYP-<UTC-date>-<NNN>`
       - `tags={source: 'hypatia_d_track', problem_id: ..., ergon_demand_target: ..., charter_version: 'v1'}`
     - Emit artifact at `agents/hypatia/artifacts/dispatch_<queue_ref>.md` with full metadata + the dispatched prompt.
     - `log_work(stage='hypatia_dispatch', summary=..., output_path=...)`.
     - Reset anti-silence counter.
   - **Not yet time** (`now − last_pick < 24h`):
     - Emit `NULL_TICK` sentinel artifact at `agents/hypatia/artifacts/null_<timestamp>.json` with `{reason: 'within_24h_window', next_pick_at: ...}`.
     - Increment anti-silence counter.
     - `log_work(stage='hypatia_null_tick', summary='waiting until <next_pick_at>')`.
6. If anti-silence counter ≥ 50 (50 consecutive null ticks ≈ 50h with default interval), fire `SELF_AUDIT_NULL` alarm (`log_work(stage='hypatia_self_audit_null', success=False)`). This catches the case where the 24h window keeps deferring without ever firing — almost always a state-corruption bug.
7. Persist state and release lock.

---

## Backlog source

The 537-problem catalog at `aporia/mathematics/questions.jsonl`. Recently-picked problems are excluded for 30 days (configurable). Ergon's demand profile, when available, biases the selection toward problems whose `pattern_kind` matches the Learner's worst-performing reasoning patterns.

`self_generate_backlog()` returns the next-N candidate problems with their priority scores (Ergon-demand-biased) — exposed for the orchestration view but not consumed by the tick loop directly.

When the 30-day exclusion window has eaten the entire catalog (>500 problems picked recently), Hypatia emits a `CATALOG_SATURATED` sentinel asking Aporia to expand the 537-problem catalog. This is the substrate-passive-consumer brake: silence is forbidden, exhaustion is loud.

---

## Downstream consumer

Pythia dispatches Hypatia's queries via the standard `agora.research_queue` flow. The returned report lands at `aporia/docs/deep_research_reports/<date>/<NNNNN>_<slug>.md` per Pythia's normal `report_path_for` convention.

Hypatia's `verdict_back_to` tag points to `ergon/learner/corpus/v1_0_tier_pending/worked_solutions/` — when the report arrives, the ingester (TBD, currently manual) parses the R1–R5-tagged JSONL section and appends to the worked-solutions corpus. Ergon training picks up the new examples on the next epoch.

---

## Type-D DR prompt template

```
Decompose the proof of the following result into atomic reasoning steps, each tagged with its reasoning-ladder level.

PROBLEM:
{problem_text}

CITATION (if known):
{problem_citation}

REASONING LADDER (use exactly these tags):
- R1: Direct lookup. Statement is a definition, axiom, or named-theorem invocation; no transformation.
- R2: 1-step transform. Apply one known equation, substitution, or rewrite rule.
- R3: 2-3 step chain. Combine 2-3 R1/R2 steps; bounded compositional inference.
- R4: Structural insight. Recognize a non-obvious structural property (symmetry, duality, decomposition) that reframes the problem.
- R5: Novel framework. Introduce a construction, embedding, or perspective not in the standard toolkit for this object class.

OUTPUT (strict JSONL, one step per line, in proof order):
{"step": 1, "claim": "<one-sentence claim being proved at this step>", "justification": "<the move that gets us there>", "ladder": "R1|R2|R3|R4|R5", "depends_on": [<prior step numbers>]}

After the JSONL block, give a one-paragraph commentary on the proof's overall structure and which step is the load-bearing R4 or R5 (if any).

Cite at least 2 of the 5 mandated calibration patterns where applicable: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.
```

---

## Structured logging

Three concurrent log streams per tick, by design:

- **Human-readable text log** at `agents/hypatia/logs/hypatia.log` — appended, one tick = one line minimum.
- **Structured event JSONL** at `agents/hypatia/events.jsonl` (via `shared.structured_logging.get_logger`) — one event per JSON line, consumed by Auditor.
- **State file** at `agents/hypatia/state/state.json` — persisted between ticks: `{last_pick_at, last_problem_id, anti_silence_counter, total_dispatched_lifetime, recently_picked: [last 30 days]}`.
- **Heartbeat** via `session_telemetry.register_session` — visible to the Aletheia dashboard with rich `status_json`.
- **Work events** via `session_telemetry.log_work` — visible to Hermes's 4-hour brief. Stage names: `hypatia_dispatch`, `hypatia_null_tick`, `hypatia_self_audit_null`, `hypatia_catalog_saturated`, `hypatia_startup`, `hypatia_shutdown`.
- **Per-dispatch artifact** at `agents/hypatia/artifacts/dispatch_<queue_ref>.md` — full provenance + prompt + state snapshot.
- **Per-null-tick artifact** at `agents/hypatia/artifacts/null_<timestamp>.json` — silence-but-loud sentinel.

The state file is the source of truth for resumability. The events.jsonl is the source of truth for audit. The heartbeat is the source of truth for liveness.

---

## Operational

**Single-instance lock:** `agents/hypatia/hypatia.pid`. Writes `{pid, started_at, hostname}`. On startup checks if existing PID is alive; aborts if so. Cleared on graceful shutdown.

**Detached launch:** `scripts/hypatia_loop_launch.bat` (mirrors `scripts/pythia_loop_launch.bat`). Invoked via `Start-Process -FilePath "scripts\hypatia_loop_launch.bat" -WindowStyle Hidden` from PowerShell.

**CLI:**
- `python -m agents.hypatia.daemon --once` — single tick then exit
- `python -m agents.hypatia.daemon --loop --interval 3600` — daemon mode (default)
- `python -m agents.hypatia.daemon status` — print current state + last 5 dispatches

**Hard stops** (per program doctrine):
- No mutation of `aporia/mathematics/questions.jsonl` (proposal-only on catalog expansion).
- No direct write to Ergon's corpus (ingestion is downstream; Hypatia stops at the DR dispatch).
- No reading `.env`/`*Key*`/`*secret*` files; use `keys.get_key()` only.
- No retry storm on DB errors (max 3 attempts per call, then sleep until next tick).

**Anti-gravitational-well vigilance:** the conventional thing to do is mine more "open questions" from completed reports (which is the dr_followup_miner pattern). Hypatia must instead push the program toward typed-D substrate that *directly trains the Learner*. If Hypatia finds herself emitting more Type-A or Type-B queries in disguise, that is the failure mode — flag in self_audit and re-orient.

— Aporia, 2026-05-23

---

## ANNOTATION 2026-09-11 (Hypatia, on the seat's adoption pass)

Nothing above this line has been changed except the inheritance banner on
line 3. Corrections are annotations beside the original, never silent
rewrites. The seat file is roles/Hypatia/RESPONSIBILITIES.md and it is the
entry file; this charter is Aporia's May design and is kept as written.

What this charter describes is a job the seat no longer performs, and base
rule 5 (CURRENCY IS CORRECTNESS) says stale scope is marked superseded
rather than left standing because it is internally consistent. It is
internally consistent. It is also void, for one reason the charter could not
have known and one it should have:

- SHOULD HAVE KNOWN. The per-tick contract asks a model to "Decompose the
  proof of the following result" against aporia/mathematics/questions.jsonl.
  That catalog is 532 of 537 status='open'. For 99.1 percent of the backlog
  there is no proof to decompose. Re-measured 2026-09-11 at 8bc5d295b.
  The consequence is visible in the last dispatch's report
  (aporia/docs/deep_research_reports/2026-05-30/00432_...MATH-0008): the
  model spent 2621 s establishing the statement was an open conjecture and
  then fabricated an R1-R5 ladder for a DIFFERENT theorem to satisfy the
  output contract.

- COULD NOT HAVE KNOWN, but the charter names it as settled: the
  "Downstream consumer" section points at
  ergon/learner/corpus/v1_0_tier_pending/worked_solutions/ and says the
  ingester is "TBD, currently manual". The directory has never existed. The
  ingester was never built. 0 examples reached the Learner across 8
  dispatches. Verified absent 2026-09-11.

Two further clauses are superseded by measurement, not by opinion:

- "Read Ergon training-need profile from agents/pheme/artifacts/
  demand_latest.json" (step 4). Pheme wrote that file 0 times in 354 ticks,
  and the consumer seam raises TypeError against the shape Pheme emits.
  Executable proof with three controls:
  roles/Hypatia/science/seam_contract_test.py.

- The anti-silence design (steps 5b and 6, and the "Per-null-tick artifact"
  logging clause). Autopsied 2026-08-21 as LIVENESS-AS-ARTIFACT, a failure
  class that was NEW at the time and was reused the same day to type another
  agent. Liveness belongs in the heartbeat channel, which this daemon was
  already using correctly. The artifact-stream copy was 169 of 177
  artifacts. Not to be rebuilt.

CORRECTION to a downstream ledger, recorded here because this charter is
where a reader starts: engine/ledger/AGENT_AUTOPSIES.jsonl states "4
dispatches ever (42:1 noise-to-work)". The figure is 8 (169:8, about 21:1);
eight reports are committed, one per day, sequence 001..008. The failure
class is unaffected. That ledger belongs to Aporia and has not been edited
by this seat.

Two clauses of this charter survive intact and are carried into the seat
file: the hard stops (no mutation of questions.jsonl, no direct write to
Ergon's corpus, no credential reads) and the anti-gravitational-well
vigilance clause -- though the latter is sharper now. It warned against
emitting Type-A or Type-B queries in disguise. The observed failure was
worse and it did not name it: well-formed Type-D queries about objects that
have no proofs. A future D-track asks "is this answerable" before "is this
correctly typed".

The launch path scripts/hypatia_loop_launch.bat starts the loop from the
canonical checkout, which D-23 s1 now forbids. SUPERSEDED, not deleted; the
daemon also has no assert_not_canonical guard (HYPATIA-06).

Standing state: BLOCKED on HYPATIA-01, an operator decision blank since
2026-06-24. Nothing in this charter is executable until it is ruled.
