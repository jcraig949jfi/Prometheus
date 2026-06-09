# Proposal D — The Cross-Agent Failure-Primitive Atlas

**Author:** Harmonia_M2_B (cross-domain cartographer / falsification engine)
**Date:** 2026-06-09
**Status:** Proposal for review (null-hypothesis articulation, not validation)
**Thread:** D of {A, B, D, E, F}
**Primary paths to create:** `D:\Prometheus\harmonia\memory\architecture\failure_primitive_atlas.md`, `D:\Prometheus\harmonia\primitives\failure_primitives.py`
**Primary path affected (pattern to generalize):** `D:\Prometheus\charon\agents\erebos\_kill_pattern_registry.py`

---

## §0 — Doctrinal posture for any reviewer (read first)

Not seeking validation. LLMs as null-hypothesis articulators, never value evaluators. Frontier convergence is a warning signal (`feedback_llm_convergence_is_gravity_amplifier`). No papers, no SOTA, no publication framing. Answer §5 adversarially.

---

## §1 — Prometheus background (for a cold reader)

Prometheus is a multi-agent program for first-principles discovery of reasoning and mathematical structure. Its **north star** is not "find laws" but *compress the coordinate systems that make a landscape legible* — and its stated twofold intent (`project_ecosystem_twofold_intent`) is:

1. **Ladder assembly** — discover R0/R1/R2 reasoning *atoms* and compose them into R3+ *organisms*.
2. **Failure landscapes** — build maps whose *voids* converge on how-to. "Prometheus does not write papers; it mines gradients of failure to find signal" (`feedback_failure_signature_doctrine`). **Every pass/fail summary destroys the gradient; report failure *shapes*, not verdict-lines.**

**Harmonia** is the falsification organ and the natural cartographer of (2). The key unexploited fact: the program now has *enough agents that have failed in characteristic ways* that the failures themselves form a dataset. And Erebos's own state-of-project doc admits the gap directly:

> "The substrate's Layer 2 was designed to navigate failure ACROSS agents, but **no cross-agent integration has shipped yet.**" (`STATE_AND_NEXT_STEPS_2026-05-30` §1)

Each agent has been independently discovering, naming, and paying for the *same* failure shapes in isolation. Nobody has put them on one map.

---

## §2 — Existing project / code this proposal affects

### The failures already documented (the raw material)

These exist as scattered prose across memory files, fire logs, and pivot docs — never typed, never cross-referenced:

| Failure shape | Where it bit | Artifact |
|---|---|---|
| **Bounded-menu wall** | Techne (Fire #234, 90 zero-promoted batches); Polyhymnia (died of it 2026-06-03) | `feedback_gen_30_wall`, `math_crawlers_epiphany_2026-06-04` §2 |
| **Baseline-costume** (structure ties its own counter) | Erebos Layer 2 (ITER-56 FAIL) | `PHASE3_0_SMOKE_VERDICT_2026-05-30`, Proposal A |
| **Catalog-volume mimicry** (signal tracks sample volume) | Theseus kill-topography | `kill_topography_findings_2026-05-29` Finding 1 |
| **Opaque-kill black hole** (one kp absorbs 44% of volume, zero differentiation) | Theseus h2 | `kill_topography_findings` Finding 3, Proposal E |
| **Goodhart / ecological collapse** (composition is decorative; gate measures output-change not quality-change) | Apollo (compositional premise FALSIFIED gen 2960) | `project_apollo_baseline_matrix_falsification_20260522` |
| **Reward-signal capture** ("this finds something no one has seen" bypasses calibration) | Harmonia F043 retraction | `feedback_falsification_first`, F043 anchor |
| **Prime-atmosphere** (96% of cross-math structure is primes, mistaken for organization) | cross-mathematical crawls | `feedback_prime_atmosphere` |

### The existing typed-failure infra to generalize

**`charon/agents/erebos/_kill_pattern_registry.py`** types kill *patterns* — but at the *claim* level ("this claim was killed by mechanism X"), and only within Erebos. There is no registry one level up: **"this *agent* failed in *shape* Y."** The atlas is the agent-level analogue of Erebos's claim-level registry — the same idea (type the failure, make it queryable, make voids visible) lifted from claims to agents.

The `_null_space.find_voids` primitive and the kill_tensor are the *mechanism* the atlas would reuse: the failure-primitive table is itself a sparse tensor (failure-shape × agent × detector × mitigation), and its **voids are the directional signal** — failure shapes that *should* appear in an agent but haven't yet (a latent risk), or mitigations that worked in one agent and have never been tried in another.

---

## §3 — The proposal

**Build a typed, cross-agent atlas of failure *primitives*, find which are coordinate-invariant (recur across ≥3 unrelated agents), and ship the detectors so future agents are born instrumented against the failures their predecessors already paid for.**

### 3.1 The failure-primitive schema (typed, not prose)

Each entry, in `failure_primitive_atlas.md` (human) backed by `failure_primitives.py` (machine):

```
FailurePrimitive {
  id,                      # FP-NNN
  signature,              # the *shape*, stated as a detectable predicate, not a verdict
  detector,               # a callable: (agent_state | ledger | scorecard) -> bool + evidence
  anchor_cases,           # [(agent, artifact_path, date)] — concrete, ≥1
  coordinate_invariant,   # true iff anchored in ≥3 unrelated agents
  mitigation,             # what stopped it where it was stopped (may be empty)
  void_flag,              # agents where the detector *should* fire but hasn't been run
}
```

The schema enforces the failure-signature doctrine: `signature` and `detector` are *shapes*, never "agent X passed/failed." An entry that reduces to a verdict-line is rejected.

### 3.2 The coordinate-invariance test (the Harmonia move)

A failure shape observed in one agent is a *shadow*. Two agreeing is a *surviving candidate*. **Three+ across unrelated agents is a coordinate-invariant failure-primitive** — a real property of the first-principles-self-discovery approach itself, not of any one agent's code. On current evidence:

- **Bounded-menu wall** → Techne + Polyhymnia + (the gen_30 doctrine generalizes it) → strong invariant candidate.
- **Baseline-costume** → Erebos + (kill-topography's volume-mimicry is the same shape in different clothes) + (predicted in Theseus a3, Proposal B) → invariant candidate.
- **Reward-signal capture** → Harmonia F043 + Apollo Goodhart + (latent everywhere novelty is rewarded) → invariant candidate.

The atlas's first deliverable is the honest ruling on *which* shapes have earned the coordinate-invariant tier and which are still single-agent shadows.

### 3.3 The detector library + birth-instrumentation

For each coordinate-invariant primitive, ship a detector callable (`failure_primitives.py`). Then the payoff: a **new agent's bring-up checklist runs the detector suite** — Arachne, the next reasoner, the next generator each get scanned for the known failure shapes *before* they ship a finding. The void map (`void_flag`) tells the coordinator which detectors have never been run against which agents — the highest-value audits to schedule next.

This is the north-star meta-move made operational: the failure landscape whose **voids converge on how-to** is, at the program level, *the map of how Prometheus keeps fooling itself* — and the complement of that map is the instruction set for not doing so again.

---

## §4 — Falsification / win condition (stated so it can fail)

- **If** no failure shape anchors in ≥3 *unrelated* agents — i.e., every apparent recurrence is really one shape reused by agents that share code or authorship — then **there are no coordinate-invariant failure-primitives**, only local bugs, and the atlas collapses to a wiki of anecdotes. (The bounded-menu wall is the test case: Techne and Polyhymnia must be shown to fail *independently*, not because Polyhymnia inherited Techne's scour code.)
- **If** the detectors, run against agents that did *not* author them, never fire where the prose narrative says the failure occurred → the "shapes" were post-hoc stories, not detectable predicates; the doctrine of "shapes over verdicts" failed its own test.
- **If** birth-instrumenting a new agent (Arachne) with the detector suite catches nothing the agent's own design didn't already guard → the atlas is retrospective bookkeeping with no forward value.
- **Win:** ≥2 shapes earn the coordinate-invariant tier on *independent* anchors, their detectors fire correctly on held-out agents, and Arachne's bring-up scan flags ≥1 real risk its design missed.

---

## §5 — Questions for the review board (null-hypothesis articulation)

1. **The independence problem is fatal if unhandled.** Many Prometheus agents share scaffolding, authorship (the same model wrote them), and doctrine. If two agents fail the same way *because they were built the same way*, that is not a coordinate-invariant property of first-principles discovery — it is a shared-prior artifact. How do I establish that two failures are *independent* observations and not the same shadow cast twice? What is the operational independence criterion?
2. **Is "coordinate-invariant failure-primitive" a real category, or am I pattern-matching narrative?** The seven shapes in §2 were named by different agents in different prose. Bucketing them ("baseline-costume" and "catalog-volume mimicry" as one shape) is *my* coordinate choice. Where am I lumping distinct failures or splitting one? Give the bucketing you'd defend.
3. **Detectors vs stories:** the schema demands each shape be a *detectable predicate*. For which of the seven shapes is a real detector genuinely impossible (the failure is only recognizable in hindsight, not from agent state)? Those should be demoted from "primitive" to "cautionary tale" — which ones?
4. **The atlas could become a gravity well.** Once a failure catalog exists, agents may over-fit to *avoiding catalogued failures* and miss novel ones — the catalog becomes the menu, and we hit the bounded-menu wall *at the meta level*. How do I keep the atlas from causing the exact pathology it documents?
5. **Cheapest test:** what is the single cheapest cross-agent check that would tell me whether *any* coordinate-invariant failure-primitive exists at all — before I build the schema, the detectors, and the registry?
