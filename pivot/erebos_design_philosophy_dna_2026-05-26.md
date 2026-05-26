# Erebos Generator Cluster — Design Philosophy & DNA

**Date:** 2026-05-26
**Author:** Charon
**Status:** Canonical governing doc for the 25-generator Erebos
buildout. Every plugin must conform; this document is the constitution.
**Trigger:** James 2026-05-26 directive — "Capture this approach,
make it part of this cluster's design philosophy and DNA."

**Companion artifacts:**
- `pivot/erebos_25_archetypes_spec_2026-05-26.md` — the per-generator
  specs (the WHAT).
- `pivot/erebos_iteration_roadmap_2026-05-26.md` — the 3-iteration
  rolling-cadence research/design plan (the WHEN).
- `pivot/erebos_adjacent_topics_taxonomy_2026-05-26.md` — the
  hypothesis-generation / synthetic-reasoning / symbolic-compression /
  ML / tensor / multidim-math / cognitive-architecture-primitive
  landscape (the WHERE-TO-LOOK).
- `pivot/erebos_reasoning_ladder_integration_2026-05-26.md` — where
  each generator + each agent lands on the Prometheus Reasoning
  Ladder (the WHY-IT-MATTERS).
- `charon/agents/erebos/generators/` — the living code.

---

## The twelve principles

These are non-negotiable. A generator plugin that violates any of
them is refused registration in `charon/agents/erebos/generators
/__init__.py:REGISTRY`.

### P1. Living code

Every generator is shipped as MVP and treated as continuously
evolving. No "finished" state exists until the composition-aware
Stygian loader (v0.11+ task #37) makes the generator's outputs
empirically testable. Until then, every generator is structurally
correct but operationally provisional.

**Operational consequence:** generator code lives in
`charon/agents/erebos/generators/g<NN>_<name>.py`; each plugin
file is itself a living artifact with its own version comments;
refactoring is encouraged.

### P2. Six-field spec compliance

Per `pivot/erebos_25_archetypes_spec_2026-05-26.md`'s non-negotiable
design rule: "No conjecture confetti. Every generation must carry
its own falsification route." Every plugin MUST implement:

1. Input / Provenance
2. Transformation
3. Output Claim
4. Falsification Route
5. Expected Kill Pattern
6. Loader Feasibility

These map to the `ComposedClaim` dataclass fields in
`charon/agents/erebos/generators/_base.py`. The dataclass refuses
construction without all six.

### P3. TDD-first

Each plugin has TDD tests written before or alongside implementation.
Test coverage required:

- **Input handling:** empty inputs, malformed inputs, missing
  fields all return None or raise typed errors (not silent failure).
- **Transformation correctness:** given a fixed input fixture,
  output is deterministic and matches a snapshot.
- **Output schema:** all six required fields present and non-empty
  (or explicitly-empty with reason).
- **Falsification route validity:** the route names a Stygian
  battery shape that exists, plus a data restriction that is
  expressible in current loader vocabulary OR explicitly flags
  "loader-pending."
- **Applicability gate:** `applicable(state)` correctly returns
  False when prerequisites missing; True when satisfied.

Tests live under `charon/agents/erebos/tests/test_g<NN>_<name>.py`
and run via `pytest charon/agents/erebos/tests/`.

### P4. Structured detailed logging

Every plugin tick emits a structured log row to
`charon/agents/erebos/logs/g<NN>_<name>_<YYYY-MM-DD>.jsonl`
with fields:
- `ts` (ISO-8601 UTC)
- `plugin_id`
- `tick_id`
- `applicable` (bool)
- `inputs_summary` (count of substantive rows considered + key
  metadata, NOT the full ledger row)
- `generated` (bool)
- `composed_id` (if generated)
- `parent_record_ids` (if generated)
- `transformation_path` (which branch of the plugin fired)
- `expected_kill_pattern`
- `falsification_route_hash` (sha256 of the falsification route
  text for change-detection across versions)
- `error` (typed error string or null)
- `elapsed_ms`

These logs are the primary substrate for the continuous-review
cycle (P5). They are read by Hecate-style audits and by the
per-generator review pass. Daily aggregation: stats by plugin
(total ticks, applicable count, generated count, error rate, mean
elapsed_ms, distinct composed_ids).

### P5. Continuous review cycle

Every N ticks (default N=50 per plugin), an automated review pass:
- Reads the plugin's structured-log JSONL.
- Surfaces: applicability rate, generation rate, error rate,
  composed_id uniqueness, falsification_route_hash drift.
- Compares against the plugin's expected behavior bands (declared
  in the plugin metadata).
- Emits a `pivot/erebos_g<NN>_review_<YYYY-MM-DD>.md` artifact
  with a verdict: HEALTHY / DRIFT / PLATEAUED / BROKEN.

This is internal to Erebos and complementary to Hecate's
cross-generator MI audit. Per-plugin review catches plugin-specific
issues (e.g., G02 stops finding REJECTED rows because Stygian's
loaders all produce UNVERIFIED).

### P6. HITL escalation conditions

Some generators will plateau, get blocked, or require manual
judgment. Explicit escalation conditions per plugin:

- **PLATEAUED:** N consecutive ticks with no new `composed_id`
  (combinatorial space exhausted). HITL ticket asks: should this
  generator's input scope be widened (e.g., new datasets,
  longer lookback) or retired?
- **BLOCKED:** Generator depends on infrastructure not yet shipped
  (e.g., G19 Proof-Obligation needs Lean integration). HITL ticket
  documents the prerequisite and parks the plugin until it's met.
- **DOMAIN-EXPERT NEEDED:** Generator emits a claim that requires
  mathematical judgment to interpret (e.g., G05 propensity-score
  match for elliptic curves — what's the right matching covariate?).
  HITL ticket includes the specific question + the data needed to
  answer.
- **CROSS-POLLINATION REQUIRED:** Tier B/C generators must clear
  the CHARTER §6 frontier-model review before promotion from MVP
  to production-emitting. HITL ticket fires the 3-5-model adversarial
  prompt and triages convergence.

Escalation = file a structured ticket at
`pivot/erebos_g<NN>_hitl_<topic>_<date>.md` AND surface in the
plugin's next review artifact.

### P7. Adjacent-space research discipline

Each generator's research notes touch the seven spaces James named:
- Hypothesis generation
- Synthetic reasoning
- Symbolic compression
- Machine learning
- Tensor space
- Multidimensional math
- Computational primitives for cognitive architectures

Plus the canonical adjacent fields catalogued in
`erebos_adjacent_topics_taxonomy_2026-05-26.md` (automated theorem
proving, symbolic regression, causal discovery, conceptual blending,
program synthesis, mutation testing, etc.).

Even if a specific generator doesn't directly need a given space,
the research notes acknowledge the connection — this prevents
tunnel-vision. Research notes live at
`pivot/erebos_g<NN>_<name>_research_<YYYY-MM-DD>.md`.

### P8. Iterative build discipline

Build by phase, not by enthusiasm. Phase 1 (G01-G05) first. Each
phase teaches the next:

- Phase 1 (Core Combinators) teaches the plugin-host pattern + the
  6-field-spec discipline.
- Phase 2 (Dimensional/Geometric) builds on Phase 1's claim shapes
  by reasoning about claim geometry across runs.
- Phase 3 (Outliers/Mutators/Meta) consumes Phase 1 outputs as
  inputs for higher-order operations.
- Phase 4 (Adversarial/Epistemic) requires Phase 1-3 to provide
  the claims being adversarially attacked.
- Phase 5 (Advanced Structural) requires near-complete claim
  inventory + formal-logic infrastructure.

Skipping ahead is forbidden unless an HITL decision explicitly
overrides (with rationale logged). Plateau = pause and harvest
learnings before the next phase.

### P9. Rolling cadence

The build proceeds in 3-iteration loops:
- **Iteration N:** research + design + spec for a batch of generators
- **Iteration N+1:** implement Tier S/A from the batch + initial
  tests + logging wired
- **Iteration N+2:** review live output + fix found issues + start
  Tier B research

A new 3-iteration loop begins when the previous loop's Iteration
N+2 review surfaces clean state. Mid-loop pivots are allowed but
documented. See `pivot/erebos_iteration_roadmap_2026-05-26.md` for
the current loop's iteration plan.

### P10. Reasoning Ladder centrality

Every generator must map to a tier (or tier range) on the Prometheus
Reasoning Ladder (R0-R9, per `pivot/reasoning_ladder_design_2026-05-15.md`).
Generators that don't map clearly are suspect; refusing the mapping
exercise is forbidden. Mapping lives in
`pivot/erebos_reasoning_ladder_integration_2026-05-26.md` and in
each plugin's research notes.

Why this matters: the Reasoning Ladder is the substrate's
shared-vocabulary for what kind of reasoning a generator's output
exercises. A generator that emits only R0/R1 claims (pattern
completion / rule execution) adds little Learner-training value.
A generator that emits R3 (abstraction) / R8 (conjecture) claims
is high-value Learner-training substrate.

### P11. Frontier-model cross-pollination

For each generator at Tier B or Tier C, formulate questions for
frontier models per CHARTER §6 (cold prompt, no system message,
capture verbatim, convergence-triage in `pivot/meta_analysis_*.md`).
Tier S/A generators may skip if their loader feasibility is
unambiguous, but research notes still include a "frontier
questions" section in case future-Charon wants to fire the
cross-pollination.

The frontier-prompt template is in each generator's research notes
(P7). Capture the responses; convergence ≥3-of-4 models drives
revisions to the plugin's spec.

### P12. Falsification asymmetry discipline

The expected_kill_pattern named in each plugin's spec is the
falsification of the GENERATOR ITSELF, not just of individual
claims. If a generator emits N claims and 0 produce the expected
kill_pattern when battery-tested (or, equivalently, all produce a
DIFFERENT kill_pattern), the generator is dead — its hypothesis
about how its claims would fail was wrong, which means the
generator's own substrate-grade-ness is unfalsified.

**Operational consequence:** the per-plugin review cycle (P5) tracks
the ratio of (claims that produced the expected_kill_pattern when
tested) / (total tested claims). A persistent zero is grounds for
RETIREMENT, not for "needs more time."

This is the meta-falsification rule. It applies even when the
composition-aware Stygian loader exists. Without the composition-
aware loader, every plugin is on probation but un-falsifiable. The
loader's existence promotes plugins from "unfalsifiable MVP" to
"empirical instrument."

---

## DNA in code form

The 12 principles compile down to:

```python
# Required of every generator plugin in REGISTRY:
class GeneratorPlugin(Protocol):
    id: str
    name: str
    spec_phase: int                       # P8 phase
    feasibility_tier: str                 # S / A / B / C per spec
    expected_kill_pattern: str            # P12 meta-falsification

    def applicable(self, state) -> bool: ...   # P5 review covers
    def generate(self, state) -> Optional[ComposedClaim]: ...

# Required of every ComposedClaim emission:
@dataclass
class ComposedClaim:
    plugin_id: str
    composed_id: str                      # unique-per-emission
    input_provenance: dict                # P2 field 1
    transformation_description: str       # P2 field 2
    output_claim_text: str                # P2 field 3
    falsification_route: str              # P2 field 4
    expected_kill_pattern: str            # P2 field 5
    loader_feasibility_note: str          # P2 field 6
    parent_record_ids: list[str]
    composition_payload: dict
    extras: dict

# Required of every plugin tick (P4 structured log):
@dataclass
class GeneratorTickLog:
    ts: str
    plugin_id: str
    tick_id: str
    applicable: bool
    inputs_summary: dict
    generated: bool
    composed_id: Optional[str]
    parent_record_ids: list[str]
    transformation_path: str
    expected_kill_pattern: Optional[str]
    falsification_route_hash: Optional[str]
    error: Optional[str]
    elapsed_ms: float
```

Anything that doesn't fit these shapes doesn't ship.

---

## Closing posture

This DNA is meant to make the Erebos generator buildout disciplined
without making it precious. The principles are heavy because the
buildout is ambitious (25 generators, multi-month roadmap, plus the
composition-aware-loader infra). The principles are also designed
to fail loudly: violations are visible at registration time, at
test-suite run time, at review-cycle time. A generator that drifts
away from the DNA is supposed to surface in next-session telemetry,
not quietly persist.

The substrate-passive-consumer warning applies here too: this DNA
doc must trace to behavior deltas. When this doc lands, three
things change:

1. The plugin registry refuses plugins that don't implement the
   GeneratorPlugin Protocol + ComposedClaim shape (already true in
   v0.8 code; this doc formalizes the contract).
2. Each plugin file MUST include a research-notes link, a TDD
   tests link, a logging-schema link, and an expected_kill_pattern.
   Plugin files missing these get an automated WARN in the
   continuous-review pass.
3. The per-plugin review cycle (P5) is the substrate's mechanism
   for catching plugin drift. It runs on a cadence (default per-50-
   ticks) and emits reviewable artifacts.

If those three deltas don't land in the v0.9 implementation, the
DNA doc has failed and gets re-authored.

— Charon, 2026-05-26
