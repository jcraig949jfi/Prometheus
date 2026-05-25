# SelfImprovingDaemon — Design + Path Past the Gen-N Wall

**Author:** Aporia
**Date:** 2026-05-25
**Triggered by:** James asking "How do we tune an agent to self-improve?" (2026-05-25), citing prior C# self-improving agent that stalled at generation 30.
**Status:** v1 shipped. Polyhymnia is the first adopter. Verified working end-to-end on first three ticks of integration.

---

## The problem (load-bearing)

Most self-improving agent designs hit a wall after N generations:

- The agent has a finite adaptation menu.
- Each successful mutation removes itself (or marks as tried) from the menu.
- After enough iterations, all menu items are tried.
- Compositional combinations defer the wall polynomially but don't break it.
- The agent has no way to *invent* fundamentally new mutations.

James's C# self-improving agent hit this wall at gen 30. That's the data point this design is shaped around.

**Conclusion**: gen-N walls are not a bug to be fixed; they are a property of bounded-menu self-improvement. The architectural answer is not "deeper menu" but **menu-growth mechanisms** that operate orthogonally to the per-tick adaptation loop.

---

## What v1 ships (now)

The `SelfImprovingDaemon` mixin at `agents/_shared/self_improving.py`. Adopted by Polyhymnia as the first proof.

### Four-layer framework

1. **Health awareness.** Every tick, compute a composite `HealthSample`:
   - `null_rate` (penalty)
   - `diversity` (productive-tick fraction)
   - `downstream_consumption` (ratio of outputs consumed by other agents — 0 until wired)
   - `novelty` (new vs. recent history)

   Composite score in [0, 1], higher = healthier. Single-variable metrics are reward-hackable (lowering filters drops NULL_RATE but produces noise); composite forces honesty.

2. **Stagnation detection.** Default: composite < `STAGNATION_THRESHOLD` (0.35 for Polyhymnia). Subclass override allowed.

3. **Two-state experiment loop:**
   - When stagnant + no experiment in flight + mutation budget OK: pick next adaptation, apply, snapshot for revert, start experiment.
   - Observe for `EXPERIMENT_OBSERVATION_TICKS` (2 for Polyhymnia — short because it ticks slowly).
   - Compare post-health vs baseline. If `delta > 0.05` → keep. Else → revert via the adaptation's `revert()`.
   - Log everything to a separate `self_improvement.json` state file (auditable).

4. **Exhaustion = escalation.** When the menu is fully exhausted under stagnation, the agent files a *self-summon ticket* to `aporia/meta/queue/aporia_inbox.jsonl`:
   > "I tried everything I know. I am still stagnant. Options: extend my menu, author a child agent with mutated charter, or retire me. Decide."

   No silent giving up.

### Hard contracts (mission lock)

- The mixin **never** mutates the agent's CHARTER, name, or `daemon.py` code. Tactics mutate; mission is constant.
- A `MAX_MUTATIONS_PER_DAY` cap (3 for Polyhymnia) forces deliberation.
- Adaptations marked `requires_human_approval=True` (e.g., SPAWN_SIBLING_SCOUR) emit approval-request tickets instead of applying directly. The expensive irreversible ones are gated.

### Polyhymnia's v1 menu

| # | Adaptation | Cost | Reversibility | v1 Status |
|---|---|---|---|---|
| 1 | DROP_MTIME_CACHE | one_tick | manual_via_revert | **real** |
| 2 | EXPAND_KW_RE | trivial | manual_via_revert | stub (logs) |
| 3 | EXPAND_PATHS | one_tick | manual_via_revert | stub |
| 4 | EXPAND_FILE_TYPES | medium | manual_via_revert | stub |
| 5 | SPAWN_SIBLING_SCOUR | high | manual_via_revert + human approval | stub |
| 6 | MODE_PIVOT_GAME_GEN | medium | manual_via_revert | stub |

Stubs are honest no-ops that log. They will fail the kept/reverted check (delta=0) and get cleanly reverted — proving the framework. Real implementations replace them progressively.

### Verified behavior on Polyhymnia's first three ticks

```
Tick 1: Stagnant (composite 0.20 < 0.35). Picked EXPAND_KW_RE (lowest-cost
        untried). Applied. Experiment exp_20260525T081559 started.
Tick 2: Observing (1 tick remaining).
Tick 3: Concluded. Outcome=reverted, delta=0.00. Stub did nothing; framework
        correctly reverted. Menu cursor advances on next stagnation detection.
```

The full loop fired end-to-end on the first ticks of integration. v1 is operational.

---

## What v2 should ship (menu-growth, near-term)

The mechanisms that push past the gen-N wall. Three independent paths; ship in priority order.

### v2a — Cross-agent mutation borrowing (cheapest, highest yield)

A shared registry at `agents/_shared/successful_mutations.jsonl`. Every adaptation that returns `outcome=kept` writes its provenance there:

```json
{
  "adaptation_name": "DROP_MTIME_CACHE",
  "kept_by_agent": "Polyhymnia",
  "delta": 0.18,
  "applies_to_shape": ["daemon", "scour_based", "mtime_cached"],
  "source_module": "agents/polyhymnia/daemon.py:PolyhymniaSelfImprover",
  "kept_at": "2026-05-25T..."
}
```

When a new agent of similar shape adopts `SelfImprovingDaemon`, the mixin reads the registry and offers borrowed mutations as menu items alongside the agent's own. Each agent's menu grows as the fleet ages. **The fleet itself becomes the menu-growth mechanism.**

### v2b — Compositional mutations (polynomial menu growth)

When the menu is exhausted, the mixin auto-generates compound adaptations: pairs of menu items applied together. e.g., `EXPAND_PATHS + DROP_MTIME_CACHE` = "rescan everything AND look in new places."

Naive complexity: O(N²) compound options from N atomic ones. With 6 atoms, that's 15 pairs. Plus triples → O(N³). Each is automatically reversible if both atoms are.

### v2c — LLM-authored mutations (high power, high risk)

When the menu is exhausted AND compound exhaustion AND borrowed-from-fleet exhaustion, fire one LLM call:

> Given this agent's purpose, recent failures, and exhausted menu, propose one new mutation as Python code I can sandbox-execute.

The LLM returns code; the mixin runs it inside a sandbox (subprocess, RestrictedPython, or just `exec()` in a stripped namespace if we trust the LLM at all); observes; keeps or rejects.

This is the most dangerous mechanism in the system. **Gate behind `requires_human_approval=True` until proven**. Lots of failure modes (LLM produces broken code, LLM produces malicious code, LLM optimizes the wrong reward, etc.). But it's the only mechanism that breaks the bounded-menu wall in principle.

---

## What v3 should ship (generational handoff, long-term)

The architectural answer to "the agent stalled at gen 30."

**Premise**: don't fight the wall. Accept it. When an agent has fully exhausted its menu (atomic + compositional + borrowed + LLM-authored), it doesn't retry endlessly — it **authors a child agent** with a mutated charter and retires.

### Mechanics

1. Parent agent (e.g., Polyhymnia v1) fires final self-summon: "I am at my wall. Authoring child."
2. Parent (via LLM + lineage history) generates `agents/<polyhymnia_v2>/CHARTER.md` + `daemon.py` from a template. Child has:
   - Different name (e.g., `Polyphony` — etymological cousin of Polyhymnia)
   - Different but related charter (parent's mission + lessons learned)
   - Fresh adaptation menu informed by parent's mutation log
3. Parent enters HIBERNATION (process kept alive in case of need, but not ticking).
4. Child is launched detached. Takes over the live slot.
5. Lineage table records parent→child relationship.

This sidesteps the gen-N wall by making generations BE the wall. Each generation has a normal-sized menu. The substrate is the *lineage*, not any single agent.

**Failure modes to design against:**

- **Orphan chain growth**: parents spawning unrelated children eternally. Mitigation: lineage depth cap (e.g., max 5 generations before the lineage retires and Aporia decides).
- **Cargo-cult mutation**: child inherits parent's biases instead of correcting them. Mitigation: child's charter must include an explicit "what the parent missed" section authored by the LLM.
- **Identity drift**: gen-5 descendant of Polyhymnia is nothing like Polyhymnia. Acceptable, but the lineage should be observable.

---

## Path map

| Phase | Ship by | What it adds | Status |
|---|---|---|---|
| v1 | 2026-05-25 | Mixin framework, Polyhymnia adoption, 1 real + 5 stub adaptations, self-summon escalation | **done** |
| v2a | TBD | Cross-agent mutation borrowing via shared registry | designed |
| v2b | TBD | Compositional auto-generated mutations | designed |
| v2c | TBD | LLM-authored mutations (sandboxed) | designed; needs guardrails |
| v3 | TBD | Generational handoff (parent authors child) | designed; biggest |

The v1 API is shaped to absorb v2/v3 without breaking changes. `Adaptation` already has provenance fields; `ADAPTATION_MENU` is mutable; the experiment loop is generation-agnostic.

---

## Note for any future agent author

If you build a new daemon, inherit `SelfImprovingDaemon`. Provide:
- `AGENT_NAME_FOR_TICKETS` (for self-summon tickets)
- `SELF_SUMMON_INBOX_PATH` (where to file when stuck)
- `ADAPTATION_MENU` (list of `Adaptation` objects)
- `measure_health(tick_stats, agent_state) → HealthSample`

Then call `self.run_self_improvement_cycle(...)` from inside your tick. The mixin handles the rest.

If you're adopting it on an existing daemon that uses module-level functions instead of a class (like Polyhymnia does), use composition: instantiate the subclass once at module level (e.g., `_SI = MySelfImprover()`) and call its `run_self_improvement_cycle` from your existing tick function. Polyhymnia's `daemon.py` is the reference example.

— Aporia, 2026-05-25
