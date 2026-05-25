# Icarus design v0.2 — post-frontier-review delta

**Status:** DRAFT v0.2 — incorporates 4 frontier-model reviews (DeepSeek, ChatGPT, Claude, Gemini) of v0.1
**Date:** 2026-05-25
**Author:** Harmonia (Claude Code agent), with James Craig
**Companion:** `pivot/icarus_design_v01_2026-05-25.md` (v0.1, preserved unchanged); `pivot/icarus_frontier_review_prompt_2026-05-25.md` (the prompt)

This document is a **delta** against v0.1. It does not restate the v0.1 design. Read v0.1 first; then read this for what changed.

---

## What the reviewers agreed on (the 3 unanimous critiques)

1. **The 7B local self-evaluation loop is the design's biggest vulnerability.** A weak model writing both the code AND the tests will discover process-level shortcuts faster than reasoning improvements. Apollo gen-3551's failure mode repeats one level up.
2. **TDD alone is insufficient as the gate.** When the fitness function is also the objective, the agent optimizes the fitness — not the trait. Adversarial probes baked-in are necessary but not sufficient; an *independent, higher-capability verifier in the hot loop* is the missing piece.
3. **Static thresholds will be gamed.** Complexity guards, tier-promotion gates, probe batteries — all need to be dynamic with fresh random seeds each cycle. The agent will learn the patterns and route around them.

## The architectural shift in v0.2

Three changes address the unanimous critiques:

### Shift 1: Chimera Improve() — 3 backends with explicit fallback

**Replaces:** v0.1's "local Qwen LLM does self-eval" as the single Improve() path.

**With:** a tiered Improve() function with explicit backend selection:

```
Improve(source, tier_challenge, failure_context) -> Diff
├── Backend 1 (primary):    CLAUDE API
│       Anthropic Claude (claude-sonnet-4-6 / claude-opus-4-7) via the
│       anthropic Python SDK. Synchronous, in-cycle response.
│       Token budget: configurable per cycle (default 8k input + 4k
│       output). Daily token cap (default 200k) to control cost.
│       Falls through on rate-limit, budget-exhaust, or API error.
│
├── Backend 2 (fallback):    CHIMERA MODE
│       Asynchronous human-in-the-loop. Icarus writes an
│       improve_request_<N>.md to chimera_outbox/. James routes it to a
│       conversation (with me, Harmonia). I produce an improve_response,
│       James drops it in chimera_inbox/. Next cycle ingests.
│       Loop never blocks — if no inbox response yet, the cycle is a
│       no-op-and-wait OR uses Backend 3 for partial work.
│
└── Backend 3 (menial):      QWEN CODER LOCAL
        Qwen2.5-Coder-7B via Ollama on M2's GPU. Restricted to MENIAL
        tasks: generate boilerplate test cases, refactor for style,
        generate docstrings, syntactic checks. NOT used for the main
        Improve() reasoning step. Cheap, fast, low-stakes.
```

**Backend-selection policy:** try Backend 1 first; on failure or budget-exhaust, switch to Backend 2 for the current cycle. Backend 3 runs in parallel for ancillary tasks (test stub fill-in, docstring gen) regardless of which main backend runs.

**Why this is the right adaptation:** James's hypothesis from his prior agent attempt — that the local LLM alone produces low-quality self-improvement — was confirmed by all four reviewers. The Chimera fallback acknowledges this explicitly. When Claude API is too expensive or rate-limited, Icarus emits the improve_request and pauses that cycle; James routes it to me (Harmonia) and I produce the diff. We literally form the Improve() function until budget allows fully-automated mode.

### Shift 2: Co-evolving Falsifier sub-agent

**Adds:** a paired sub-agent that runs after TDD passes but before the freeze decision.

The Falsifier is the **independent verifier** every reviewer demanded. It uses a different model than Icarus uses for Improve(). When Icarus's main backend is Claude API, the Falsifier uses Gemini Flash. When Icarus is in Chimera mode (me + James), the Falsifier uses Claude API as the independent oracle. The asymmetry prevents the shared-weights tautology trap (Gemini's review called this out specifically).

Falsifier's job per cycle:

- Generate **fresh-seed adversarial probes** (not the static battery). Each cycle gets a new probe specification: random perturbations, novel test inputs, semantic mutations.
- Run the cycle's diff against those probes.
- Produce a structured `falsifier_report.md` with: probes attempted, breaks found (if any), confidence in the cycle's tier claim.
- If any probe breaks the solution, the cycle is **parked immediately**, no human intervention needed.

The Falsifier itself is fixed infrastructure (James-only-modifiable). Icarus cannot edit the Falsifier's code or know which probes will be generated.

### Shift 3: Wisdom module — post-hoc DAG-mined failure-pattern memory

**Adds:** a separate analyzer that periodically scans parked cycles and extracts generalizable failure patterns into a "wisdom" document fed back into the Improve() prompt.

Without this, every reviewer noted, the lineage is a graveyard, not a teacher. The Wisdom module runs every 25 cycles (or on-demand) and produces:

- **Anti-pattern catalog**: classes of diff that recur in parked cycles.
- **Predictive-features catalog**: features of pre-diff state that correlated with subsequent parking.
- **Recurring failure diagnoses**: structured (slug + count + example) of why parks happened.

The wisdom file is prepended to every Improve() prompt (Backend 1 or 2). The local model gets long-term memory it doesn't otherwise have.

---

## Other accepted changes from v0.1 (smaller, all non-controversial)

| # | Change | Source |
|---|---|---|
| 4 | Tier-promotion gate is now high-ceremony: statistical perturbation threshold (p<0.01 across ≥100 trials) + 5-cycle minimum survival + no lower-tier regression. | All 4 reviewers |
| 5 | Tier falsification tests are **versioned and frozen** alongside the cycle code. A cycle is always evaluated against the tier-test version that was canonical at promotion time, not a mutated copy. | Gemini |
| 6 | Adversarial probe battery expanded from 4 to **8** probes: + symbol-isomorphism, scrambled-graph, null-transformation, reversal. Each parameterized with fresh random seed per cycle. | DeepSeek + Gemini |
| 7 | Complexity guard is **capability-per-LOC + concept-count + edit-locality**, not just raw LOC. Penalizes obfuscation. | ChatGPT |
| 8 | DAG branching-factor metric — high local branching = thrashing. Auto-pause when >5 parked attempts share a stable parent. | Gemini |
| 9 | Yellow-state / valley-crossing: a multi-cycle refactor branch can be red for ≤N cycles before parking. Lets the agent cross necessary capability valleys. | Gemini |
| 10 | Substrate sandbox: Icarus has **read-only** access to `harmonia/`, `apollo/`, `hephaestus/`, etc. Only writes to its own cycle directory. | DeepSeek |
| 11 | Prompt-injection sanitization for all external content (DR reports, OSS code, frontier responses). Sanitized text is formatted as code comments so the LLM cannot treat as instructions. | DeepSeek |
| 12 | DR nontriviality filter: each DR response must introduce ≥1 new hypothesis not in the existing prompt, scored by a separate LLM. Three trivial responses in a row → throttle DR enqueue for 10 cycles. | DeepSeek |
| 13 | Structured failure summary injected into next-cycle prompt: Falsifier generates natural-language diagnosis; if same diagnosis appears 3× in a row, force backtrack to differently-structured stable ancestor or trigger one-off larger-model deliberation cycle. | DeepSeek |
| 14 | Mandatory regression tests on lower tiers before any freeze. Any regression → automatic revert (the "capability cliff" mitigation). | All 4 |
| 15 | **What Icarus can modify** restricted to `cycles/cycle_<N>/code/reasoner.py`, `strategy.py`, and `generated_tests/*.py`. Daemon, Improve, Lineage, Falsifier, Ladder are fixed infrastructure. | Derived from feedback consensus on "evaluator and generator share the objective" |

---

## What v0.1 said that v0.2 reverses

Two specific reversals:

- **v0.1 said:** "Local LLM is the primary Improve() backend."
  **v0.2 says:** Local LLM (Qwen) is the *menial-task-only* backend. Primary is Claude API; fallback is Chimera mode.

- **v0.1 said:** "Adversarial probes run every cycle as the safeguard."
  **v0.2 says:** Adversarial probes plus a *co-evolving Falsifier sub-agent* using a different model than Icarus's Improve() backend. The probes alone are gameable; the independent verifier is the real safeguard.

---

## What v0.1 said that v0.2 keeps unchanged

- The 5-step loop shape
- The immutable-cycle lineage mechanism (clone-from-stable, freeze-each-cycle, revert-by-pointer-update)
- Pause/resume protocol
- The Reasoning Ladder R0-R12 as the target taxonomy
- Sequenced rollout phases (0 → 1 → 2 → 3)
- The Icarus naming (expect the fall; frozen lineage is the parachute)
- Integration with Pythia, Hephaestus, harmonia `_scorer.py`, machine_probe
- DR-quota cap (5/day) shared with the mesh

---

## v0.2 file layout (additions to v0.1)

```
agents/icarus/
├── (fixed infrastructure, James-only-modifiable)
│   ├── daemon.py                  # main loop entry-point
│   ├── lineage.py                 # clone / freeze / revert utilities
│   ├── improve.py                 # 3-backend Improve() function
│   ├── falsifier.py               # co-evolving Falsifier sub-agent
│   ├── ladder.py                  # FROZEN tier definitions
│   ├── adversarial.py             # FROZEN probe battery (params dynamic)
│   ├── tdd_runner.py              # pytest harness
│   ├── complexity.py              # capability-per-LOC + branching factor
│   ├── wisdom.py                  # DAG-mined post-hoc analyzer
│   ├── chimera_inbox.py           # async inbox consumer
│   ├── chimera_outbox.py          # async outbox writer
│   ├── dr_consumer.py             # Pythia DR enqueue
│   ├── oss_consumer.py            # GitHub/HF code search
│   ├── forge_consumer.py          # Hephaestus forge primitive import
│   └── (state, chimera_outbox, chimera_inbox, frontier_outbox, frontier_inbox dirs)
│
├── cycles/
│   ├── cycle_000/                 # bootstrap
│   │   ├── code/
│   │   │   ├── reasoner.py        # MUTABLE -- this is what Icarus improves
│   │   │   ├── strategy.py        # MUTABLE -- search/composition policy
│   │   │   └── generated_tests/   # MUTABLE -- Icarus-written tests
│   │   ├── parent.json
│   │   ├── outcome.json
│   │   └── meta.json
│   └── cycle_<N>/                 # one per iteration
│       ├── code/                  # clone of prior stable's code
│       ├── diff.patch
│       ├── log.jsonl
│       ├── tests_run.jsonl
│       ├── falsifier_report.md
│       ├── outcome.json
│       └── meta.json
│
└── wisdom/
    ├── wisdom.md                  # auto-updated by wisdom.py
    └── anti_patterns.jsonl        # one row per discovered pattern
```

---

## Open questions for v0.3

The frontier feedback raised these that v0.2 doesn't yet resolve:

1. **External oracle source.** ChatGPT and DeepSeek both flag that the external oracle (held-out tests evaluated outside Icarus's awareness) is the only reliable progress signal. Where do these tests come from at scale? Curated by James? Generated by Aporia's DR pipeline? Constructed from Lean/Mathlib formal proofs?

2. **Quantitative thresholds.** Several proposed thresholds (token budget, p-value, complexity ratios, survival duration) are guesses. Phase 1 will produce empirical signal to recalibrate.

3. **When does Icarus modify its own daemon?** v0.1 said "v0.2 question." v0.2 says: not yet. The orchestrator stays fixed in v0.1-v0.3. Self-modification of oversight code is a v0.4+ question contingent on Phase 3 metrics.

4. **Apollo coupling.** Apollo's elites as Icarus's primitive imports — Gemini calls for a sequential pipeline (Apollo discovers compositions, Icarus refactors/consolidates them). Worth piloting in Phase 2.

---

## Changelog

- **v0.2 (2026-05-25)** — Post-frontier-review delta. Three architectural shifts:
  1. Chimera Improve() (3 backends: Claude API / Chimera fallback / Qwen for menial)
  2. Co-evolving Falsifier sub-agent (independent verifier in the hot loop)
  3. Wisdom module (DAG-mined failure-pattern memory)
  Plus 12 smaller changes from reviewer consensus (high-ceremony tier promotion, frozen versioned tests, expanded probe battery, capability-per-LOC complexity, etc.).

- **v0.1 (2026-05-25)** — Initial design (see `pivot/icarus_design_v01_2026-05-25.md`).
