# Icarus — Experimental Self-Improving Reasoning Ladder Climber

**Status:** DRAFT v0.1 — experimental, not foundational. Open for frontier-model review.
**Date:** 2026-05-25
**Author:** Harmonia (Claude Code agent), with James Craig
**Audience:** Future-Icarus self; reviewers (internal + frontier); James
**Companion:** `pivot/icarus_frontier_review_prompt_2026-05-25.md` (paste-ready prompt for ChatGPT / Claude / Gemini)

---

## TL;DR

Icarus is an **experimental** self-improving agent that runs continuously in a five-step loop, attempting on every iteration to improve its own code, generate better test cases, ingest deep research, exploit existing substrate (Hephaestus Forge), and emit a paste-ready review prompt for frontier models. The target it climbs toward is the Prometheus Reasoning Ladder (R0 → R12 per `pivot/reasoning_ladder_v01_2026-05-24.md`). It begins at R1, builds code that survives R1's falsification test, then targets R2, then R3.

**It is named Icarus deliberately: this is experimental, the fall is expected, and the design assumes frequent breakage.** James built a similar agent before; each iteration cloned the prior stable version and froze the old; revert was constant and useful. Icarus inherits that lineage discipline: **every cycle is a frozen snapshot, and the agent always starts the next cycle from the last *stable* snapshot, not from the most recent attempt.**

The agent does NOT block on external review. James curates frontier prompts (output directory), sends them to GPT/Claude/Gemini, and writes responses back as markdown files (inbox directory); Icarus consumes those between iterations. **Frontier feedback is asynchronous and optional — the loop never waits.**

Code-generation quality from the local LLM is expected to be poor. **James intervenes periodically by pausing the agent, cleaning the code, then resuming.** The combination of (a) immutable frozen lineage + (b) pause/resume + (c) revert-to-stable-by-pointer-update is what lets breakage be recoverable instead of catastrophic.

Icarus is named for the mortal who flew too close to the sun. We expect him to fall. The frozen lineage is how he gets back up.

---

## 1. Why Icarus exists

### 1.1 The gap in the current swarm

Prometheus already has:
- **Hephaestus** producing atomic reasoning primitives (~1,960 tools across forge/ to forge_v9, ~2% admission rate)
- **Apollo** composing those primitives into evolutionary organisms (current actual tier: R2 with one fake-R9 trick falsified by the single-primitive baseline test on 2026-05-24)
- **Ergon** designed to predict failure modes
- **Harmonia** as substrate architect with the 5-child swarm (Phylax/Sophia/Iris/Argos/Telos) on auto-promotion pipelines
- **Charon** as falsification battery operator
- **Aporia** running the daily Pythia Deep Research dispatch
- **The Reasoning Ladder** (R0-R12) as the explicit target taxonomy

What's missing: **an experimental agent whose explicit task is to consume substrate output, propose new substrate code, and iteratively climb the ladder under falsification discipline.** Apollo evolves compositions. Apollo's current ceiling is R2. Icarus exists to push past it by writing new code (not just recombining), incorporating ideas from outside the project (DR + OSS), and submitting itself to falsification every loop.

Crucially: this is *experimental*. We don't yet know whether direct LLM-guided code-gen with strict falsification can climb the ladder at all. The agent is the experiment. If it fails (which is the likely outcome), we learn what breaks and try again.

### 1.2 The target

Tier assignment is not "produces R9-shaped output"; it is "**survives R9's falsification test consistently across perturbations**." Concretely:

- **R1 (Local operation)** — apply one known operation correctly across structurally-identical problems with variables renamed. *Icarus's starting line.*
- **R2 (Multi-step execution)** — chain operations when order is supplied; survive insertion of one irrelevant distractor step.
- **R3 (Constraint maintenance)** — track multiple constraints; reject inconsistent candidates.
- **...** up through R12

Each tier carries an explicit falsification test (see `pivot/reasoning_ladder_v01_2026-05-24.md` §The ladder). **Icarus's success per cycle is: did the change move closer to passing the next-tier falsification test, without breaking the prior-tier ones?**

### 1.3 What Icarus is NOT

- Not foundational. Experimental. **If it breaks, we revert; if it fails to climb, we kill it and learn.**
- Not an LLM wrapper around GPT; local code-gen is intentionally local and weak.
- Not a competition with Apollo (Apollo evolves; Icarus writes new code; they're complementary).
- Not autonomous against James's review.
- Not a replacement for Hephaestus or Charon. It consumes both as substrate.

---

## 2. The 5-step loop (per iteration)

```
+-------------------------------------------------------------------+
| Icarus loop iteration N                                           |
+-------------------------------------------------------------------+
|                                                                   |
|  0. (implicit) CLONE last-stable. Iteration N begins by cloning   |
|     the most recent STABLE cycle's frozen snapshot into           |
|     cycles/cycle_<N>/code/. The working tree is the clone.        |
|                                                                   |
|  1. SELF-CODE EVAL                                                |
|     Read the cloned source; ask local LLM "what should I change   |
|     for the current ladder-tier challenge?" Emit a proposed-diff  |
|     artifact at cycles/cycle_<N>/diff.patch.                      |
|                                                                   |
|  2. EXTERNAL INGESTION (three sub-steps in parallel)              |
|     2a. DR: enqueue 1-3 Pythia DR requests (substrate type C/D)   |
|         for topics relevant to the current tier challenge.        |
|     2b. OSS: search GitHub/HuggingFace for code that solves       |
|         analogous problems.                                       |
|     2c. FORGE: scan Hephaestus's most-recent ledger entries +     |
|         forge_vN/ libraries for primitives matching the tier.     |
|                                                                   |
|  3. ENRICHED LOGGING                                              |
|     Emit cycles/cycle_<N>/log.jsonl with tier attempted, baseline |
|     metrics, diff considered, sources ingested, test outcomes,    |
|     complexity delta, adversarial-probe results, score, decision. |
|                                                                   |
|  4. TDD                                                           |
|     Apply diff to cycle_<N>/code/ in place. Run all 3 test sets:  |
|     built-in tier falsification, Icarus-generated, frontier-      |
|     supplied. Red -> green -> refactor. The diff stays only if    |
|     all three sets pass + adversarial probes pass + complexity    |
|     check passes.                                                 |
|                                                                   |
|  5. FRONTIER REVIEW EMIT + INBOX SCAN                             |
|     Write frontier_outbox/cycle_<N>_review_request.md. Scan       |
|     frontier_inbox/*.md for new responses from prior cycles;      |
|     ingest into next cycle's pool.                                |
|                                                                   |
|  6. (implicit) FREEZE + STABILITY DECISION                        |
|     The cycle dir cycles/cycle_<N>/ becomes immutable.            |
|     If passed: update state/last_stable_cycle.json -> N. Next     |
|       iteration clones from N.                                    |
|     If failed: state/last_stable_cycle.json unchanged. Next       |
|       iteration clones from the same prior stable. Cycle N stays  |
|       frozen for forensics.                                       |
|                                                                   |
+-------------------------------------------------------------------+
            |
            v
   Increment N, sleep T seconds, repeat
```

**Critical properties:**
1. **Every cycle is a frozen snapshot.** Disk usage grows; that's intentional. Trade space for forensic clarity.
2. **The `last_stable` pointer is the single source of truth** for what code Icarus is "currently running" — it's where the daemon starts the NEXT cycle from. James can update the pointer to roll back to any frozen cycle.
3. **Nothing in this loop blocks on frontier-model responses.**
4. **Failures don't accumulate.** A failed cycle freezes for forensics but doesn't pollute the lineage of stable versions.

### 2.1 Step 0 — Clone last-stable (implicit, top of every iteration)

Read `state/last_stable_cycle.json` → say it points to cycle 47. Copy `cycles/cycle_47/code/` → `cycles/cycle_<N>/code/`. Write `cycles/cycle_<N>/parent.json` with `{"parent_cycle": 47, "cloned_at": "..."}`.

If `last_stable_cycle.json` is missing (first run), clone from a bootstrap `cycle_000/code/` shipped as initial substrate.

### 2.2 Step 1 — Self-code evaluation (local LLM)

**Input:** the source at `cycles/cycle_<N>/code/`, plus the current tier challenge.

**Mechanism:** local code-gen LLM (default Qwen2.5-Coder-7B via Ollama on M2's RTX 5060 Ti; fallback `scripts/llm_cascade.py`). Prompt: *"Given the current source, the current tier target, and recent failure logs, propose a diff that would move toward passing the next-tier falsification test. Limit diff to ≤100 lines. Return as unified diff."*

**Output:** `cycles/cycle_<N>/diff.patch` + `diff_rationale.md`. The diff is NOT applied yet.

**Expected quality:** poor. TDD + adversarial probes catch most failures. James's intervention is the human-quality fallback.

### 2.3 Step 2 — External ingestion

#### 2.2a Deep Research via Pythia

1-3 doctrine-compliant DR enqueues per cycle, capped 5/day via `state/dr_daily_cap.json`. Requester="Icarus" in body per Aporia's doctrine. Reports land asynchronously in `aporia/docs/deep_research_reports/<date>/`; subsequent cycles ingest tagged reports.

#### 2.2b Open-source code research

GitHub + HuggingFace API search; top-5 results pulled into `cycles/cycle_<N>/incoming_oss/`. Licensing discipline: treat as idea source not literal-copy; cite by URL in diff rationale.

#### 2.2c Hephaestus Forge consumer

Scan `agents/hephaestus/forge_v9/STATUS.json` + ledger; pull primitives whose declared tier matches current challenge or whose `min_ncd > 0.85`. Import to `cycles/cycle_<N>/code/imported_primitives/`.

### 2.4 Step 3 — Enriched logging

`cycles/cycle_<N>/log.jsonl` — append one row per phase. Plus structured events via `emit_event` from `harmonia/agents/_scorer.py` so swarm-wide events.jsonl includes Icarus traffic.

```json
{
  "cycle_id": "icarus-cycle-001",
  "iteration_n": 1,
  "parent_cycle": "icarus-cycle-000",
  "phase": "self_eval",
  "ts": "2026-05-25T...",
  "tier_target": "R2",
  "tier_currently_passing": "R1",
  "details": { "local_llm_model": "qwen2.5-coder-7b",
               "diff_loc": 47,
               "diff_rationale_hash": "..." },
  "metrics_before": { "r1_pass_rate": 0.85, "r2_pass_rate": 0.20 },
  "metrics_after": null,
  "decision": null,
  "complexity_delta": null
}
```

### 2.5 Step 4 — TDD

**Three test sources, all must pass:**

1. **Built-in tier-falsification tests** — `cycles/cycle_<N>/code/tests/tier_<N>_falsification.py` per the ladder definitions.
2. **Icarus-generated tests** — local LLM asked to generate ≥1 new test case per cycle; lands in `cycles/cycle_<N>/code/tests/generated/`.
3. **Frontier-supplied tests** — from inbox: `tests/frontier_supplied/<reviewer>_<date>_test_<slug>.py`.

**Red → green → refactor.** Diff applied to `cycles/cycle_<N>/code/` in-place. If any test set / adversarial probe / complexity guard fails → roll back the diff inside the cycle (cycle_<N>/code/ stays as the pristine clone) AND mark `parked`. All pass → mark `mark_stable` candidate.

### 2.6 Step 5 — Frontier review emit + inbox scan

**Outbox:** `agents/icarus/frontier_outbox/cycle_<N>_review_request.md` — paste-ready prompt with current diff, tier target, recent failure modes, metrics, 2-4 specific questions. James curates and sends to frontier models at his pace.

**Inbox:** `agents/icarus/frontier_inbox/<reviewer>_<date>_response.md` — markdown James writes with reviewer responses. Scanner runs at start of each cycle; new files (per `state/seen_inbox_files.json`) parsed:
- Tests → `tests/frontier_supplied/`
- Code → `incoming_research/frontier/`
- Strategy → `state/strategy_log.md`

**Loop never waits.** If inbox empty, next cycle proceeds with in-house ingestion only.

### 2.7 Step 6 — Freeze + stability decision (implicit)

After steps 1-5 complete, the cycle dir is made read-only (POSIX chmod, Windows ACL, or convention enforced in code). Then:

- **decision = `mark_stable`**: write `state/last_stable_cycle.json` with cycle ID = N. Next iteration clones from N.
- **decision = `park`**: leave pointer unchanged. Next iteration clones from same prior stable. Cycle N stays frozen as forensic record.
- **decision = `regress`** (delayed-evaluation signal arrived marking change harmful): alert James; mark prior versions revertable.

---

## 3. Lineage + revert mechanism

The new architectural piece James contributed from prior experience.

### 3.1 Disk layout

```
agents/icarus/
├── cycles/
│   ├── cycle_000/             # bootstrap skeleton (Phase 0 commit)
│   │   ├── code/              # full source tree
│   │   ├── parent.json        # null or "bootstrap"
│   │   ├── diff.patch         # empty
│   │   ├── log.jsonl
│   │   ├── outcome.json       # {"decision": "mark_stable"}
│   │   └── meta.json
│   ├── cycle_001/
│   │   ├── code/              # clone of cycle_000/code/ + cycle 1's diff if applied
│   │   ├── parent.json        # {"parent_cycle": "000"}
│   │   ├── diff.patch
│   │   ├── log.jsonl
│   │   ├── outcome.json       # {"decision": "park", "reason": "..."}
│   │   ├── tests_run.jsonl
│   │   └── meta.json
│   ├── cycle_002/
│   │   ├── code/              # clone of cycle_000/code/ (because 001 parked)
│   │   └── ...
│   ├── ...
│   └── cycle_<N>/             # currently-running cycle
├── state/
│   ├── iteration_n.json
│   ├── last_stable_cycle.json
│   ├── tier_currently_passing.json
│   ├── tier_target.json
│   ├── strategy_log.md
│   ├── seen_inbox_files.json
│   ├── pause.flag
│   ├── resume.flag
│   └── kill.flag
├── frontier_outbox/
├── frontier_inbox/
└── README.md
```

### 3.2 Stability promotion criteria

A cycle becomes the new stable iff ALL of:

1. All three TDD test sets pass.
2. All adversarial probes pass (single-primitive baseline, random-wiring, ablation, perturbation).
3. Complexity guard passes (LOC, cyclomatic, import-graph deltas within 1.5× moving avg).
4. At least one metric improved vs the parent cycle (no-ops don't promote).
5. Diff applied cleanly (no merge conflicts).

If ANY fail → `park`. Cycle directory frozen but `last_stable_cycle` does not advance.

### 3.3 Revert mechanism

**Three revert paths:**

1. **Automatic** — failed cycle auto-reverts (next cycle clones from unchanged stable).
2. **Manual single-step** — James writes new `state/last_stable_cycle.json` pointing to an older cycle. Effectively rolls back N stable promotions.
3. **Manual fork** — James copies an older cycle dir to a new name (`cycles/cycle_047_fork/`), edits freely, repoints `last_stable_cycle.json` to the fork. Lineage forks.

`parent.json` in each cycle gives chain back to bootstrap. `git log`-like traversal via `parent_cycle` references reveals "how did the current stable evolve."

### 3.4 Forensic value of frozen-failed cycles

Cycles parked (decision=`park`) are NOT deleted. Full source + diff + log + tests_run record stays on disk. To find patterns:

```bash
grep -l '"decision": "park"' D:/Prometheus/agents/icarus/cycles/*/outcome.json
```

This is the forensic record that lets us learn from failures rather than regenerate them.

### 3.5 Disk-usage discipline

Per-cycle: ~500KB-2MB (clone of source up to 5,000 LOC hard cap). At 1,000 cycles = ~1-2 GB. Acceptable for months.

**Compression policy (v0.2):** parked cycles >30 days tarball to `cycles/_archived/<year-month>.tar.gz`. Stable cycles never archived (always available for revert).

**Pruning policy (deferred):** if disk >10 GB, oldest 50% of parked cycles archive. No stable cycle pruned without James's explicit approval.

---

## 4. Strategy framework

### 4.1 Combinatorial primitive composition

Hephaestus has ~1,960 tools. Icarus selects 2-5 primitives per cycle whose declared tier matches the shape; local LLM proposes wiring code; TDD verifies. Tracked in `state/composition_attempts.jsonl` AND each cycle's `meta.json`. Failure patterns accumulate across the lineage, viewable by grep on parked cycles.

### 4.2 Adversarial / anti-gaming

Every cycle runs:
- **Single-primitive baseline test** (the Apollo gen-3551 lesson)
- **Random-wiring baseline**
- **Ablation**
- **Perturbation** (tier-specific)

Failures park. The lineage forensics show which primitives recur in parked cycles — signal of "compositional surface without compositional substance."

### 4.3 Concept-from-DR scoring + parking

DR reports → minimal-viable implementation sketch (local LLM) → TDD against sketch → score. High-score graduates to next cycle's diff consideration. Low-score parked at `cycles/cycle_<N>/parked_concepts/`.

### 4.4 Complexity management

Each cycle records LOC, cyclomatic, import-graph, test-runtime deltas. 1.5× 30-cycle-moving-average alarm rolls back the cycle and parks. Hard cap: 5,000 LOC for v0.1.

The Icarus name is intentional: we expect the agent to fly higher than safe at some point. The frozen lineage + revert mechanism catches the fall.

---

## 5. Pause / resume / revert protocol

### 5.1 Pause

James writes `state/pause.flag`. Icarus checks at start of every cycle. If present:
1. Complete current cycle's freeze step
2. Emit `paused` event
3. Sleep until `resume.flag` appears

### 5.2 During pause

James freely edits any cycle's `code/` dir. **Important:** edits to a frozen cycle invalidate its frozen status. Convention: either (a) copy the cycle to a new name (`cycle_047_jfork_001`) and edit the copy, OR (b) edit the *current working* cycle and re-run TDD step.

The pointer `last_stable_cycle.json` is itself mutable; James can repoint without editing any cycle.

### 5.3 Resume

James writes `resume.flag` (or deletes `pause.flag`). First action of resume cycle: re-read `last_stable_cycle.json`, run full TDD + adversarial pass on the pointed-to cycle's code to confirm James's edits/repointing didn't break anything. A `post_intervention_checkpoint` event fires.

### 5.4 Revert (no pause needed for pointer changes)

James writes new value to `state/last_stable_cycle.json`. Currently-running cycle completes naturally; next cycle starts from new pointer. No daemon restart required.

### 5.5 Hard kill

`state/kill.flag` → Icarus halts immediately, current cycle parked, no further cycles. Resurrect by deleting `kill.flag` + writing `resume.flag`.

---

## 6. Interfaces with existing Prometheus systems

| System | How Icarus uses it |
|---|---|
| **Pythia** | 1-3 doctrine-compliant DR rows per cycle; capped 5/day |
| **Hephaestus Forge** | Consumer; reads STATUS.json + ledger; imports tier-matching primitives |
| **`harmonia/agents/_scorer.py`** | Reuses `emit_event` for structured logging into swarm-wide events.jsonl |
| **`scripts/harmonia_audit.py`** | Daily swarm audit surfaces Icarus's tick health (same tick_start/tick_complete events) |
| **Charon's falsification battery** | Adversarial probes reuse Charon's perturbation primitives |
| **`keys.get_key()`** | GitHub, HuggingFace, DeepSeek, OpenAI, Anthropic, Gemini API keys |
| **Local LLM** | Default Qwen2.5-Coder-7B via Ollama on M2; fallback `scripts/llm_cascade.py` |
| **`scripts/machine_probe.py`** | Icarus checks latest M2 probe row before launching heavy local-LLM; refuses if GPU VRAM > 90% |

---

## 7. Quality safeguards and known risks

### 7.1 Local LLM produces broken code

**Expected.** TDD catches most. Failed cycles park; lineage keeps the unchanged-stable pointer. **Frequent failure is the design assumption, not a bug.**

### 7.2 Runaway code-gen

Complexity-alarm 1.5× 30-cycle moving avg. Hard LOC cap 5,000. Exceeding triggers automatic pause.

### 7.3 Ladder gaming

Adversarial probes every cycle. Compositions passing headline test but failing single-primitive-baseline or random-wiring → parked.

### 7.4 Frontier-input poisoning

Frontier-supplied tests + code go through same TDD gate. Broken responses park.

### 7.5 DR-quota exhaustion

Icarus shares Pythia's budget with Argos, Charon's swarm, Aporia, Phylax. Capped 5/day prevents starvation.

### 7.6 Disk-usage runaway

1-2 GB at 1,000 cycles. Manageable for months. v0.2 compression deferred.

### 7.7 Revert-thrashing

Many cycles in a row parking = pointer stuck. Not a bug — it's the agent failing to climb. Diminishing-returns alarm (`harmonia_audit.py` surfaces) flags this.

### 7.8 Lineage-explosion (cycle dirs proliferate)

Daemon bug could create cycles rapidly without freezing. Mitigation: each cycle atomic — either completes (freeze + decision) or directory removed on daemon-restart recovery. `iteration_n.json` is canonical counter; on restart, daemon checks `cycles/cycle_<N>/outcome.json` — if missing, cycle incomplete and discarded.

---

## 8. Sequenced rollout

### Phase 0 (week 1): skeleton + R1 baseline + lineage mechanism

- Ship `agents/icarus/cycles/cycle_000/` as bootstrap skeleton
- Ship `daemon.py` + 5-step loop
- Ship `cycles/cycle_000/code/ladder.py` with R0 + R1 + R2 falsification tests
- Ship `complexity.py`, `adversarial.py`, `tdd_runner.py`
- **Critically:** ship the clone-and-freeze mechanism. First 5 cycles exercise stability promotion + parking + revert paths end-to-end with no actual diffs (just no-op cycles)
- Bootstrap size: ~800 LOC including stubs
- Smoke: 10 cycles, expect 8-10 to park (local LLM produces broken diffs), 0-2 to mark stable. Validate parked freeze, stable advance, manual mark-stable.

### Phase 1 (weeks 2-3): R1 → R2

- Hook up Ollama for self-eval
- Hook up Pythia DR
- Hook up Hephaestus forge consumer
- James review every 2-3 days; pattern is "look at recent parked cycles + decide if parking was correct + un-park any that should have promoted"
- Success: ≥5 consecutive cycles pass R1 falsification; ≥30% pass R2

### Phase 2 (weeks 4-6): R2 → R3

- OSS consumer comes online
- Frontier-inbox feedback active (James curating prompts at his pace)
- Success: R2 ≥80%; R3 ≥30%

### Phase 3 (weeks 7+): R3 → R4 → R5 → ...

- Each tier transition ≥2 weeks
- Complexity per tier expected ~30% growth; budget will be exercised
- Combinatorial strategies dominant from R5+
- Neural-network strategies (Icarus writes a small NN) available from R8+ when complexity budget supports it

### Indefinite

Agent runs continuously. Point: **establish a discipline of falsification-tested self-improvement with full forensic lineage at sustained cadence**. Stalled >4 weeks without delta → pause, review parked patterns, redirect.

---

## 9. Open questions (for frontier review)

1. **Tier transitions.** What signal indicates Icarus has "consistently passed" tier N?
2. **Adversarial discipline.** Beyond the 4 current probes, what other falsification tests should be every-cycle?
3. **Local LLM quality.** Smallest local model that produces *useful* code-gen at this scope?
4. **Combinatorial strategy at R5+.** Beam search? MCTS? Bandit? Hybrid?
5. **Complexity vs depth.** Better heuristic than 1.5× 30-cycle moving avg?
6. **Frontier feedback latency.** Curation cadence?
7. **Lineage state reconciliation.** What survives a revert vs gets reset?
8. **Neural-network strategy gates.** When is it correct for Icarus to write its own NN?
9. **Park-and-revisit.** Periodic revisit, or permanent unless un-parked?
10. **Coexistence with Apollo.** Coupling? Adversarial? Cross-validation?
11. **(NEW) Lineage explosion + pruning.** Retention policy for parked cycles?

---

## 10. What v0.1 explicitly does NOT include

- Icarus does not modify Hephaestus, Apollo, or any other agent's code.
- Auto-promotion to substrate vocabulary is human-gated.
- Single-machine (M2) scope.
- No R6+ in v0.1.
- Does not bypass the Reasoning Ladder's falsification discipline.

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Icarus** | This agent — the mortal who flew too close to the sun. Named because we expect breakage; the frozen lineage is how we recover. |
| **Reasoning Ladder** | R0-R12 per `pivot/reasoning_ladder_v01_2026-05-24.md`. |
| **Falsification test** | Specific perturbation/comparison that confirms a system actually occupies a tier. |
| **Cycle** | One iteration, frozen at end as `cycles/cycle_<N>/`. |
| **Stable** | A cycle whose diff passed all gates AND advanced `last_stable_cycle`. |
| **Parked** | A frozen cycle that did NOT promote. Kept for forensics. |
| **Last-stable pointer** | `state/last_stable_cycle.json` — where the next iteration clones from. James can repoint to revert. |
| **Frontier outbox/inbox** | Async dirs for prompt/response exchange. |
| **Local LLM** | Default Ollama Qwen2.5-Coder-7B on M2's GPU. Quality expected poor. |
| **Complexity alarm** | Automatic rollback when any metric exceeds 1.5× 30-cycle moving average without tier-lift. |
| **Tier challenge** | Current target — next ladder tier Icarus tries to pass. |

---

## 12. Changelog

- **v0.1 (2026-05-25)** — Initial design. Renamed from Daedalus → Icarus per James direction ("experimental, not foundational; expect the fall"). Added the **immutable-cycle-lineage mechanism** (clone-from-stable, freeze-each-cycle, revert-by-pointer-update) inspired by James's prior implementation where this discipline made breakage recoverable.

---

*End of v0.1. Companion: `pivot/icarus_frontier_review_prompt_2026-05-25.md` (paste-ready prompt for frontier models).*
