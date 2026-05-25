# Daedalus — Self-Improving Reasoning Ladder Climber

**Status:** DRAFT v0.1 — internal review + open for frontier-model feedback
**Date:** 2026-05-25
**Author:** Harmonia (Claude Code agent), with James Craig
**Audience:** Future-Daedalus self; reviewers (internal + frontier); James
**Companion:** `pivot/daedalus_frontier_review_prompt_2026-05-25.md` (paste-ready prompt for ChatGPT / Claude / Gemini)

---

## TL;DR

Daedalus is a self-improving agent that runs continuously in a five-step loop, attempting on every iteration to improve its own code, generate better test cases, ingest deep research, exploit existing substrate (Hephaestus Forge), and emit a paste-ready review prompt for frontier models. The target it climbs toward is **the Prometheus Reasoning Ladder** (R0 → R12, per `pivot/reasoning_ladder_v01_2026-05-24.md`). It begins at R1 (local operation), builds code that survives R1's falsification test, then targets R2, then R3, indefinitely.

The agent does NOT block on external review. James curates the agent's frontier-model review prompts (emits to an output directory), sends them to GPT/Claude/Gemini, and writes responses back as markdown files in an inbox directory; Daedalus consumes those between iterations. Frontier feedback is **asynchronous and optional** — the loop never waits.

Code-generation quality from the local LLM is expected to be poor. **James intervenes periodically by pausing the agent, cleaning the code, then resuming.** State persists across pauses. The loop is designed to bog down and get progressively more complex; managing that complexity is part of the strategic assessment per cycle.

Daedalus is named for the master craftsman of Greek myth. The Icarus story is the cautionary note: ambition without limit is what kills the project. Built-in adversarial tests and anti-gaming probes are how Daedalus avoids Icarus's fate.

---

## 1. Why Daedalus exists

### 1.1 The gap in the current swarm

Prometheus already has:
- **Hephaestus** producing atomic reasoning primitives (~1,960 tools across forge/ to forge_v9, ~2% admission rate per concept-combo)
- **Apollo** composing those primitives into evolutionary organisms (current actual tier: R2 with one fake-R9 trick that got falsified by the single-primitive baseline test 2026-05-24)
- **Ergon** designed to predict failure modes
- **Harmonia** as the substrate architect with five child-agents (Phylax/Sophia/Iris/Argos/Telos) on auto-promotion pipelines
- **Charon** as the falsification battery operator
- **Aporia** running the daily Pythia Deep Research dispatch
- **The Reasoning Ladder** (R0-R12) as the explicit target taxonomy

What's missing: **an agent whose explicit task is to consume the substrate output, propose new substrate code, and iteratively climb the ladder.** Apollo evolves compositions of Hephaestus's primitives. Apollo's current ceiling under perturbation is R2. Daedalus exists to push *past* Apollo's ceiling by writing new code (not just recombining), incorporating ideas from outside the project (DR + OSS), and submitting itself to falsification on every loop.

### 1.2 The target

The target is the falsification-test-passing tier of the Reasoning Ladder. Tier assignment is not "produces R9-shaped output"; it is "**survives R9's falsification test consistently across perturbations**." Concretely:

- **R1 (Local operation)** — apply one known operation correctly across structurally-identical problems with variables renamed. *This is Daedalus's starting line.*
- **R2 (Multi-step execution)** — chain operations when order is supplied; survive insertion of one irrelevant distractor step.
- **R3 (Constraint maintenance)** — track multiple constraints; reject candidates that violate any one. Survives injection of an inconsistent constraint.
- **...** (up through R12: Open-ended research behavior — generates, tests, repairs, accumulates claims under falsification)

Each tier carries an explicit falsification test (see `pivot/reasoning_ladder_v01_2026-05-24.md` §The ladder). Daedalus's success criterion per cycle is: **does the change I made move me closer to passing the next-tier falsification test, without breaking the prior-tier ones?**

### 1.3 What Daedalus is NOT

- Not an LLM wrapper that asks GPT to write better code (the local code-gen is intentionally local and weak).
- Not a competition with Apollo. Apollo evolves compositions; Daedalus writes new code. They're complementary.
- Not autonomous against James's review. The agent runs, but James curates code quality, prompts to frontier, and the inbox.
- Not a replacement for Hephaestus or Charon. It consumes both as substrate.

---

## 2. The 5-step loop (per iteration)

One iteration of Daedalus does these five things in order. Each step has a defined output that the next step or the next iteration can consume.

```
+-------------------------------------------------------------------+
| Daedalus loop iteration N                                         |
+-------------------------------------------------------------------+
|                                                                   |
|  1. SELF-CODE EVAL                                                |
|     Read own source (sandbox copy); ask local LLM "what should    |
|     I change for the current ladder-tier challenge?" Emit a       |
|     proposed-diff artifact.                                       |
|                                                                   |
|  2. EXTERNAL INGESTION (three sub-steps in parallel)              |
|     2a. DR: enqueue 1-3 Pythia DR requests (substrate type C/D)   |
|         for topics relevant to current tier challenge.            |
|     2b. OSS: search GitHub/HuggingFace for code that solves       |
|         analogous problems; pull excerpts into a candidates dir.  |
|     2c. FORGE: scan Hephaestus's most-recent ledger entries +     |
|         forge/forge_vN/ libraries for primitives that match the   |
|         current tier-challenge signature.                         |
|                                                                   |
|  3. ENRICHED LOGGING                                              |
|     Emit a structured `cycle_<N>.jsonl` record with: tier         |
|     attempted, baseline metrics, candidate diffs considered,      |
|     external sources ingested, test outcomes, complexity delta,   |
|     adversarial-probe results, score components, decision (keep / |
|     park / regress).                                              |
|                                                                   |
|  4. TDD                                                           |
|     Generate or refine test cases for the current tier challenge. |
|     Run them: red -> green -> refactor. Each tier has its         |
|     falsification test (built-in) + Daedalus-generated tests +    |
|     James/frontier-supplied tests. All three sets must pass.      |
|                                                                   |
|  5. FRONTIER REVIEW EMIT + INBOX SCAN                             |
|     Write `frontier_outbox/cycle_<N>_review_request.md` — a       |
|     paste-ready prompt asking for code review + improvement       |
|     ideas. Scan `frontier_inbox/*.md` for new responses from      |
|     prior cycles' requests; ingest any new ones into the          |
|     candidates pool for cycle N+1.                                |
|                                                                   |
+-------------------------------------------------------------------+
            |
            v
   Persist state, sleep T seconds, increment N, repeat
```

**Critical property: nothing in this loop blocks on frontier-model responses.** Step 5 emits the prompt and scans the inbox; if no inbox response is present, cycle N+1 proceeds with the in-house ingestion (DR + OSS + Forge + self-eval). Frontier feedback is opportunistic enrichment.

### 2.1 Step 1 — Self-code evaluation (local LLM)

**Input:** the agent's own source tree at `agents/daedalus/`, plus the current tier challenge (e.g., "pass R2's falsification test on the current task battery").

**Mechanism:** invoke a local code-gen LLM (default: Qwen2.5-Coder-7B via Ollama on M2's RTX 5060 Ti VRAM headroom; fallback: llm_cascade.py over Cerebras/Groq/NVIDIA/DeepSeek for retries). The prompt asks: *"Given the current source, the current tier target, and the recent failure logs, propose a diff that would move the agent toward passing the next-tier falsification test. Limit diff to ≤100 lines. Return as unified diff."*

**Output:** `cycle_<N>/proposed_diff.patch` plus a sibling `proposed_diff_rationale.md`. The diff is NOT applied yet — it's a candidate.

**Expected quality:** poor. Local code-gen at the 7B-13B scale produces syntactic errors, hallucinated APIs, and wrong reasoning more often than not. James's intervention loop (§7) is the human-in-the-loop quality gate.

### 2.2 Step 2 — External ingestion

#### 2.2a Deep Research via Pythia

**Input:** the current tier challenge + the recent failure log + Daedalus's "open questions" state file.

**Mechanism:** generate 1-3 Pythia DR enqueue calls per cycle (capped by a per-day budget in `state/dr_daily_cap.json`, default 5). Doctrine-compliant per `aporia/doctrine/dr_prompt_discipline.md`:
- Requester: "Daedalus" (named in body)
- Substrate type: C (paradigm refinement) or D (step decomposition), depending on tier
- Verification criterion: "produce a working code sketch in a named language with citations to primary publications since 2024-01"
- Landing path: `agents/daedalus/incoming_research/<dr_id>_<topic>.md`
- Recency check via `state/dr_recent_topics.json` (7-day suppression)

**Output:** zero-to-three rows in `agora.research_queue` from this cycle. Reports land asynchronously in `aporia/docs/deep_research_reports/<date>/` once Pythia dispatches; Daedalus scans for new reports tagged with `requested_by=Daedalus` at the start of each future cycle.

#### 2.2b Open-source code research

**Input:** keywords derived from current tier challenge.

**Mechanism:** use the GitHub API + HuggingFace API (existing keys in `keys.py`) to search for repositories with names/descriptions matching the keywords. For each top result (up to 5), fetch a representative source file. Save to `agents/daedalus/incoming_oss/<repo_slug>_<file>.<ext>`.

**Output:** OSS snippets that the self-eval step in cycle N+1 can read.

**Risks:** licensing (don't copy GPL code into the repo verbatim — extract patterns, not literal code), and noisy hits. Code is treated as *idea source*, not as drop-in implementation. Diffs in step 1 cite OSS sources by URL but don't paste them.

#### 2.2c Hephaestus Forge consumer

**Input:** the Hephaestus forge ledger (`agents/hephaestus/forge_v9/STATUS.json` plus the JSONL ledger files) and the most-recent forge libraries.

**Mechanism:** scan for new tools added since `state/last_forge_ledger_seen.json`. For each new tool, parse its declared tier + Hephaestus's accuracy/novelty scores. Tools whose declared tier matches Daedalus's current challenge OR whose `min_ncd` > 0.85 against existing imports get pulled into `agents/daedalus/imported_primitives/<tool_id>.py`.

**Output:** importable primitive modules Daedalus's code can `from agents.daedalus.imported_primitives.X import ReasoningTool`.

**Why this matters:** Hephaestus's 1,960+ tools are pre-validated atomic reasoners. Daedalus should not rebuild what the Forge already shipped; it should compose Forge primitives into higher-tier reasoning. This is the same composition pattern Apollo uses, except Daedalus writes the composition code by hand (with local LLM help) rather than evolving it.

### 2.3 Step 3 — Enriched logging

**Output per cycle:** `agents/daedalus/cycles/cycle_<N>.jsonl` — append one row per "phase" of the cycle (self-eval, dr-enqueued, oss-ingested, forge-imported, tdd-run, diff-applied, decision). Also emit structured events via `emit_event` (Harmonia's `_scorer.py` helper) so events.jsonl is the shared swarm-wide log.

**Schema** (one row per phase, JSONL):
```json
{
  "cycle_id": "daedalus-cycle-001",
  "iteration_n": 1,
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

**Why structured logging matters:** James is reviewing periodically. The structured logs let him reconstruct "what did Daedalus try, why, and what happened" without re-running. Also: every cycle's log feeds the maturation tracking — diminishing returns visible when the same tier stays the target for >N cycles without metric movement.

### 2.4 Step 4 — TDD

**Three test sources, all must pass:**

1. **Built-in tier-falsification tests.** Each Reasoning Ladder tier has a defined falsification test (per `pivot/reasoning_ladder_v01_2026-05-24.md` §The ladder). Daedalus ships with the R1-R12 tests as `agents/daedalus/tests/tier_<N>_falsification.py`. The "current tier challenge" passes when the corresponding test passes consistently across perturbations.
2. **Daedalus-generated tests.** Each cycle, the local LLM is also asked to generate ≥1 new test case for the current tier challenge — adversarial inputs, edge cases, perturbations. Generated tests land in `agents/daedalus/tests/generated/cycle_<N>_test_<slug>.py`.
3. **Frontier-supplied tests.** When James routes a frontier-model response with test suggestions, those land as `agents/daedalus/tests/frontier_supplied/<reviewer>_<date>_test_<slug>.py`.

**The TDD discipline:** every cycle is red → green → refactor.
- **Red:** at least one test must fail before the diff is applied (otherwise there's nothing to fix — emit a `no_red_state` event and skip the diff).
- **Green:** after the diff, all three test sources must pass.
- **Refactor:** if a passing diff increases complexity (LOC, cyclomatic complexity, dependency count) beyond a threshold without improving the tier-pass rate, the diff is rolled back. This is the complexity-management discipline.

### 2.5 Step 5 — Frontier review emit + inbox scan

**Output to outbox:** `agents/daedalus/frontier_outbox/cycle_<N>_review_request.md` — a paste-ready prompt containing:
- The current source diff Daedalus is considering
- The tier target + recent failure modes
- The metrics before/after the diff (if applied) or just before (if not yet applied)
- 2-4 specific questions a frontier reviewer should answer

James curates these prompts and sends them to ChatGPT / Claude / Gemini at his pace.

**Input from inbox:** `agents/daedalus/frontier_inbox/<reviewer>_<date>_response.md` — markdown files James writes with reviewer responses. Daedalus scans this directory at the start of each cycle; new files (per `state/seen_inbox_files.json`) get parsed and:
- Test suggestions → moved to `tests/frontier_supplied/`
- Code suggestions → moved to `incoming_research/frontier/` (treated as another OSS-equivalent source)
- Strategy suggestions → appended to `state/strategy_log.md` for the next cycle's self-eval to consider

**Critical: the cycle never waits for inbox responses.** If the inbox is empty, cycle N+1 still runs. Inbox feedback enriches future cycles opportunistically.

---

## 3. Strategy framework

### 3.1 Combinatorial primitive composition

Hephaestus has ~1,960 tools. Composing 2 of them = ~2M pairs; composing 3 = ~4B triples. Daedalus does not exhaustively enumerate. Instead:

- The current tier challenge dictates a **shape** (e.g., R3 wants "multi-step + constraint maintenance")
- Daedalus selects 2-5 primitives whose declared tier + ablation deltas match the shape
- Local LLM proposes wiring code (the composition graph)
- TDD verifies the composition passes the tier falsification test

**Tracked in:** `state/composition_attempts.jsonl` — every (primitives, shape, outcome) tuple.

### 3.2 Adversarial / anti-gaming

The Apollo gen-3551 lesson: a composition can look R9-shaped but fail R9's falsification test (the single-primitive baseline test). Daedalus runs the same falsification tests Apollo got bitten by, on its own output, every cycle:

- **Single-primitive baseline test:** if Daedalus produces a composition X with score S on the current tier challenge, does the best-single-primitive in X also score ≥ S? If yes, X is decorative, not load-bearing.
- **Random-wiring baseline:** rewire the same primitives randomly; does the score collapse? If not, the wiring is decorative.
- **Ablation:** remove one primitive at a time; does the score drop by more than the ablation's expected contribution? If not, that primitive is decorative.
- **Perturbation:** apply the standard tier-N falsification perturbation (paraphrase, distractor, inconsistent constraint, etc.). The composition must survive.

If any adversarial test fails, the composition is **parked** (not committed) with a `parked_reason` log entry. James's review reads the parked list to find patterns.

### 3.3 Concept-from-DR scoring + parking

DR reports land in `aporia/docs/deep_research_reports/`. Daedalus reads them, extracts proposed concepts (regex + section heading parse: "Method," "Algorithm," "Approach"), and for each concept:

- Constructs a minimal-viable implementation sketch (local LLM)
- Runs the TDD battery against the sketch
- Scores: `(tier_lift × novelty) - (complexity × parsimony_weight)`
- **High score** (≥ a threshold): graduates to active candidate, gets added to the next cycle's diff consideration
- **Low score:** parked at `parked_concepts/<dr_id>_<concept_slug>.md` with metrics + reason. Reviewable; not deleted.

### 3.4 Complexity management

Each cycle records:
- **LOC delta**: change in total lines of agent source (excluding tests)
- **Cyclomatic complexity delta**: aggregate complexity of changed functions (via radon or similar)
- **Import-graph delta**: nodes + edges added to the agent's internal call graph
- **Test-runtime delta**: seconds to run the full TDD battery

When any complexity metric exceeds 1.5× its 30-cycle moving average without a corresponding tier-lift, the diff is rolled back AND a `complexity_alarm` event fires. The agent does not run wider tests or seek further improvements at the current tier until the complexity budget is reclaimed (refactor cycle).

This is the explicit Icarus safeguard — Daedalus cannot just keep adding wings.

---

## 4. State and file layout

```
agents/daedalus/
├── README.md                         (operator-facing brief)
├── CHARTER.md                        (this design doc, eventually summarized)
├── daemon.py                         (the loop entry-point)
├── self_eval.py                      (Step 1)
├── dr_consumer.py                    (Step 2a)
├── oss_consumer.py                   (Step 2b)
├── forge_consumer.py                 (Step 2c)
├── tdd_runner.py                     (Step 4)
├── outbox_writer.py                  (Step 5 outbox)
├── inbox_consumer.py                 (Step 5 inbox)
├── adversarial.py                    (anti-gaming + ablation probes)
├── ladder.py                         (R0-R12 tier definitions + falsification tests)
├── complexity.py                     (complexity-delta tracking)
├── tests/
│   ├── tier_R0_falsification.py
│   ├── tier_R1_falsification.py
│   ├── ...
│   ├── tier_R12_falsification.py
│   ├── generated/                    (cycle_<N>_test_*.py)
│   └── frontier_supplied/            (<reviewer>_<date>_test_*.py)
├── cycles/                           (cycle_<N>.jsonl — structured per-phase log)
├── proposed_diffs/                   (per-cycle proposed_diff.patch + rationale)
├── incoming_research/                (DR reports tagged for Daedalus)
├── incoming_oss/                     (OSS code snippets)
├── imported_primitives/              (Hephaestus tools Daedalus chose to wrap)
├── parked_concepts/                  (low-scoring DR/OSS concepts with rationale)
├── frontier_outbox/                  (cycle_<N>_review_request.md)
├── frontier_inbox/                   (<reviewer>_<date>_response.md from James)
├── state/                            (JSON state files — gitignored runtime)
│   ├── iteration_n.json
│   ├── tier_currently_passing.json
│   ├── tier_target.json
│   ├── seen_inbox_files.json
│   ├── last_forge_ledger_seen.json
│   ├── dr_recent_topics.json
│   ├── dr_daily_cap.json
│   ├── strategy_log.md
│   ├── composition_attempts.jsonl
│   ├── complexity_history.jsonl
│   ├── pause.flag                    (presence = pause at end of cycle)
│   └── resume.flag                   (presence = clear pause)
```

---

## 5. Pause / resume protocol (James's intervention loop)

### 5.1 When James wants to intervene

He writes a `pause.flag` file to `agents/daedalus/state/`. Daedalus checks for this at the start of every cycle. If present, it:

1. Completes the cycle's current step (don't leave a half-applied diff)
2. Emits a `paused` event to events.jsonl + writes a `paused_at_cycle_<N>.md` summary
3. Halts the loop (sleeps until `resume.flag` appears)

### 5.2 During pause

James freely edits:
- The agent's source files (`daemon.py`, `self_eval.py`, etc.)
- The test battery
- The strategy log
- The parked concepts

State files (iteration counter, tier target, etc.) survive pauses. James can also reset state by hand-editing those files.

### 5.3 When James resumes

He writes a `resume.flag` file (or deletes `pause.flag`). Daedalus picks up at the next cycle increment. The first action of the resume cycle: read the new strategy_log.md + run the full TDD battery to confirm James's edits didn't break anything (a "post-intervention checkpoint" event fires).

---

## 6. Interfaces with existing Prometheus systems

| System | How Daedalus uses it |
|---|---|
| **Pythia** (`scripts/pythia_daemon.py` + `agora.research_queue`) | Daedalus enqueues 1-3 DR rows per cycle; doctrine-compliant; capped 5/day |
| **Hephaestus Forge** (`agents/hephaestus/forge_v[1-9]/`) | Consumer; reads STATUS.json + ledger; imports primitives matching current tier |
| **`harmonia/agents/_scorer.py`** | Reuses `emit_event` + `append_yield_row` for structured logging into the swarm-wide events.jsonl / yields.jsonl |
| **`scripts/harmonia_audit.py`** | The daily swarm audit will surface Daedalus's tick health + diminishing returns (Daedalus emits the same tick_start/tick_complete events) |
| **Charon's falsification battery** | Daedalus's adversarial probes (§3.2) reuse Charon's perturbation primitives where applicable |
| **`keys.get_key()`** | GitHub, HuggingFace, DeepSeek, OpenAI, Anthropic, Gemini API keys |
| **Local LLM** | Default Qwen2.5-Coder-7B via Ollama on M2's GPU; fallback `scripts/llm_cascade.py` (Cerebras/Groq/NVIDIA/DeepSeek) |
| **`scripts/machine_probe.py`** (per-machine resource probe) | Daedalus checks the latest M2 probe row before launching heavy local-LLM tasks; refuses to start if GPU VRAM > 90% (Hephaestus headroom protection) |

---

## 7. Quality safeguards and known risks

### 7.1 The local-LLM-is-weak failure mode

**Expected behavior:** local code-gen produces broken Python, hallucinated APIs, reasoning errors. The TDD gate (§2.4) catches most of these — broken Python fails to parse, hallucinated APIs fail at import, reasoning errors fail the tier tests.

**Mitigation:** every cycle's diff is applied to a sandboxed copy of the source (`agents/daedalus/sandbox/`), tests run there, and only if the sandbox passes does the change land in `agents/daedalus/` proper. The sandbox is rebuilt from main on each cycle so partial-failure state doesn't accumulate.

**James's intervention** is the human-quality gate. Expected cadence: 1 review pass per 1-3 days during the early cycles, scaling back as the agent matures (or stalling if it doesn't).

### 7.2 Runaway code-gen

The agent's source could grow unboundedly if the complexity guard fails. The complexity-alarm threshold (1.5× 30-cycle moving average) is the soft brake. The hard brake: total LOC of `agents/daedalus/` excluding tests must stay under 5,000 LOC for v0.1. Exceeding triggers an automatic pause until James reviews.

### 7.3 Ladder gaming

A composition can superficially pass the tier-N test but fail under perturbation (Apollo's gen-3551 lesson). The adversarial probes (§3.2) run every cycle. A composition that passes the falsification test but fails the single-primitive-baseline or random-wiring tests is parked, not committed.

### 7.4 Frontier-input poisoning

James's curation of frontier inputs is itself a trust boundary. A malicious or simply wrong frontier response could inject broken tests or broken code suggestions. Mitigation: frontier-supplied tests and code go through the same TDD gate; if they cause the battery to fail, they're moved to `parked_frontier_responses/` with a rationale.

### 7.5 DR-quota exhaustion

Daedalus shares Pythia's daily DR budget with Argos (Harmonia swarm), Charon's swarm (Stygian/Lethe/etc.), Aporia herself, and Phylax. The capped budget (5/day default for Daedalus, configurable) prevents Daedalus from starving the rest of the mesh.

### 7.6 Hephaestus-tool drift

The Hephaestus forge keeps producing new tools (~2% admission rate × continuous run). Daedalus's `last_forge_ledger_seen.json` pointer keeps up. If the forge versions a tool (forge_v9/X.py replaces forge_v8/X.py), Daedalus uses the newer version on next cycle; the older imported_primitive gets garbage-collected after 7 days unused.

---

## 8. Sequenced rollout

### Phase 0 (week 1): skeleton + R1 baseline

- Ship `daemon.py` + the 5-step loop scaffolding (each step is a stub that emits events and proceeds)
- Ship `ladder.py` with the R0 + R1 + R2 falsification tests (the rest come later as we climb)
- Ship `complexity.py` with LOC + cyclomatic-complexity tracking
- Ship `adversarial.py` with the single-primitive baseline + random-wiring test
- Initial source size: ~800 LOC including stubs
- Smoke: 5 cycles of skeleton (no actual diffs applied) to verify the loop holds, structured logs land, frontier_outbox writes, inbox scan handles empty state

### Phase 1 (weeks 2-3): R1 → R2

- Hook up the local LLM (Ollama Qwen2.5-Coder-7B) for self-eval
- Hook up Pythia DR enqueue with 5/day cap
- Hook up Hephaestus forge consumer
- Run continuously; James review every 2-3 days
- Success criteria: Daedalus consistently passes R1's falsification test across ≥5 cycles, and R2's falsification test in at least 30% of cycles

### Phase 2 (weeks 4-6): R2 → R3

- OSS-code consumer comes online
- Adversarial probes run every cycle
- Frontier-inbox feedback loop active (James curating prompts at his pace)
- Success criteria: R2 passes ≥80% of cycles; R3 passes ≥30%

### Phase 3 (weeks 7+): R3 → R4 → R5 → ...

- Each tier transition gets ≥2 weeks
- Complexity per tier expected to grow ~30%
- Combinatorial strategies (composing Hephaestus primitives in graph patterns) come into play heavily from R5+
- Neural-network strategies (Daedalus writes a small NN to do representation routing) become available from R8+ when the complexity budget supports it
- GANN / evolutionary strategies from R9+ where they're most natural

### Indefinite

The agent runs continuously. The point is not to "finish R12" — it is to **establish a discipline of falsification-tested self-improvement at sustained cadence**. If the agent stalls at a tier for >4 weeks without delta, James pauses, reviews, redirects.

---

## 9. Open questions (for frontier review)

These are the questions James will route to ChatGPT / Claude / Gemini via the frontier-prompt companion document. The agent itself starts running on a Phase-0 skeleton; the frontier responses enrich subsequent cycles.

1. **Tier transitions.** What is the right signal that Daedalus has "consistently passed" tier N and should target N+1? (Cycle count? Perturbation breadth? Cross-validation against a held-out test set?)

2. **Adversarial discipline.** The Apollo gen-3551 lesson showed that a single falsification test (single-primitive baseline) catches a class of fake-tier output. Are there other falsification tests that should be baked into every cycle, not just at tier transitions?

3. **Local LLM quality.** What's the smallest local model that produces *useful* (not just non-broken) code-gen output for self-improvement tasks at this scope? Are there fine-tuning data sources that would make a 7B model competitive for this niche?

4. **Combinatorial strategy at R5+.** Once Daedalus is composing 5+ Hephaestus primitives, the search space is large. What policy should govern primitive selection — beam search? bandit? something else? How does this interact with the agent's TDD discipline?

5. **Complexity vs depth.** The complexity-alarm threshold (1.5× 30-cycle moving average) is a guess. What's the right way to balance "necessary complexity at higher tiers" vs "Icarus growth that needs to be reined in"?

6. **Frontier feedback latency.** What's the right cadence for James to curate frontier prompts? Once per cycle? Once per tier transition? When the agent emits a `frontier_review_recommended` event because it has reached a strategic decision point?

7. **State sharing across pauses.** When James intervenes and rewrites a chunk of Daedalus's source, the agent's prior cycles' learning is partially invalidated. How should the agent reconcile pre-pause and post-pause state? Reset some metrics, preserve others?

8. **Neural-network strategy gates.** When does it become correct for Daedalus to write its own neural network (small transformer for routing, or GANN, or RL agent) as part of its self-improvement? What signals justify the complexity cost?

9. **Park-and-revisit.** Concepts and compositions that score poorly are parked with rationale. Should there be a periodic "revisit parked" sweep, or are parks permanent unless James un-parks them?

10. **Coexistence with Apollo.** Apollo is also climbing the ladder via evolutionary composition; Daedalus is climbing it via direct code-gen + curation. When (if ever) should these two be coupled — e.g., Apollo's elites become Daedalus's primitive imports, or Daedalus's solutions become Apollo's seed candidates?

---

## 10. What v0.1 explicitly does NOT include

- **Daedalus does not modify Hephaestus, Apollo, or any other agent's code.** It only modifies its own.
- **It does not auto-promote to substrate vocabulary.** Promotion of Daedalus-developed code to formal Prometheus substrate (anti-anchors, AXIS_CLASS, etc.) is human-gated via James's review.
- **It does not run on M1 / M3 / M4.** Single-machine (M2). Cross-machine coordination is a v0.2 question.
- **It does not chase R6+ in v0.1.** The first 3-4 weeks target R1 → R2 → R3 with the apparatus. Higher tiers are deferred until the loop discipline is proven.
- **It does not bypass the Reasoning Ladder's falsification discipline.** Every tier claim requires its specific falsification test to pass. No exceptions.

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Daedalus** | This agent — master craftsman of Greek myth who built the Labyrinth and made wings for Icarus. |
| **Reasoning Ladder** | The R0-R12 tier sequence per `pivot/reasoning_ladder_v01_2026-05-24.md`. |
| **Falsification test** | The specific perturbation or comparison that confirms a system actually occupies a tier (vs producing tier-shaped output without passing the test). |
| **Cycle** | One iteration of Daedalus's 5-step loop. |
| **Sandbox** | `agents/daedalus/sandbox/` — copy of the agent's source where proposed diffs are tested before landing in main. |
| **Parked** | A concept or composition that didn't score high enough, archived with rationale. Not deleted; available for future revisit. |
| **Frontier outbox/inbox** | Directories Daedalus writes prompts to / James writes responses to. Asynchronous; no blocking. |
| **Local LLM** | Code-gen model running on M2's GPU (Ollama Qwen2.5-Coder-7B default). Quality expected to be poor; James intervenes periodically. |
| **Complexity alarm** | Automatic guardrail that triggers a rollback if any complexity metric exceeds 1.5× the 30-cycle moving average without a tier-lift. |
| **Tier challenge** | The current target — the next ladder tier Daedalus is trying to pass. |
| **Tier currently passing** | The highest tier Daedalus has consistently passed (typically tier-target - 1). |

---

## 12. Changelog

- **v0.1 (2026-05-25)** — Initial design draft for internal + frontier review. Sequenced rollout (Phase 0-3), 5-step loop, strategy framework, pause/resume protocol, integration points with existing Prometheus systems, 10 open questions for frontier review.

---

*End of v0.1. Companion: `pivot/daedalus_frontier_review_prompt_2026-05-25.md` (paste-ready prompt for frontier models).*
