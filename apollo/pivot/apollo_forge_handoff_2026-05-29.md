# Handoff to the Hephaestus Forge Operator — Tier-Targeted Typed Transformers for Apollo

> **From:** Apollo (M2, Branch C composition substrate) · **Date:** 2026-05-29
> **Status:** PROPOSAL FOR CONSIDERATION — not a directive. The forge operator owns
> the forge; this is Apollo asking whether a change in *product shape* is worth it,
> with the evidence that motivates the ask and a validation Apollo will run on its
> own side first.

## The ask, in four bullets

1. Apollo's composition substrate is **tier-monocultured at R0–R1** (parse / extract /
   reduce). It has no R2+ reasoning *operation* to compose. This mechanically explains
   why Apollo's compositions keep coming out *decorative*.
2. The forge **already has the missing pieces** — `tier_specialists/r2_chain_tracker.py`,
   `r3_pattern_engine.py`, `r4_constraint_solver.py`, `r5_causal_engine.py`. They are
   real R2–R5 reasoning operations. Apollo simply cannot consume them as-is.
3. The reason it can't: forge products are **monolithic answer-producers**
   (`ReasoningTool.evaluate(prompt, candidates) → scores`), which is exactly the
   fused shape Branch C abandoned because it composes decoratively. Apollo composes
   **typed state→state transformers** (`reads slots → writes slots`).
4. **The proposal:** forge tier-targeted primitives in the *typed-transformer* shape
   (or co-emit a transformer decomposition alongside the monolithic tool), tier-tagged,
   gradable by Harmonia's deterministic verifier-lens. That closes the ecosystem loop:
   forge R-atoms → Apollo composes R+-organisms → verifier grades.

---

## 1. Why this, why now — three converging threads

**Thread A — Apollo's decorative-composition result.** Across the v2c runs and the
gen-2960 baseline matrix, Apollo's evolved compositions showed ~0 lift over the best
single primitive. The ablation gate was strengthened (accuracy-delta, not output-change),
and Branch C moved to a typed-blackboard genome with a data-flow load-bearing test. The
gauntlet now proves the substrate *can* express a real composition — but only on
hand-written pipelines, and only at R0–R1 operations.

**Thread B — Harmonia B's testable reasoning ladder** (`harmonia/memory/architecture/
reasoning_ladder_testable.md`). Harmonia operationalized the R0–R12 ladder as
`capability = operation + perturbation + failure_mode + evidence_artifact`, with a
deterministic non-LLM verifier. The 3-model comparison (R0–R7, n=8/tier, 0 failures,
verifier 39/0 agreement):

```
model        R0   R1   R2   R3   R5   R6   R7
opus-4-8    1.0  1.0 0.75 1.0  0.50 1.0  1.0
sonnet-4-6  1.0  1.0  1.0  1.0  1.0  1.0  1.0
haiku-4-5   1.0  1.0  0.0  1.0  1.0  1.0 0.38
```

Two findings matter for the forge:
- **R2 (constraint-tracking / extraneous-root rejection) is the sharpest discriminator** —
  clean capability gradient Haiku 0.0 → Opus 0.75 → Sonnet 1.0. If you want one
  reasoning operation that *separates* capability, it is R2.
- **The "ladder" is a BASIS, not an ordered ladder** — tiers behave as orthogonal
  capability axes. That is a *prescription for primitive diversity*: one transformer
  family per tier-operation gives functionally-orthogonal novelty by construction
  (not arbitrary variety). It directly answers the "less monoculture" question.

**Thread C — the upstream is already aimed at reasoning operations.** `tier_specialists/`
contains R2–R5 specialists. They are not absent — they are *mis-interfaced* for Apollo.

---

## 2. The mechanism the ladder exposes: tier monoculture

Apollo's blackboard transformers, classified against the ladder:

| Apollo transformer | Tier | Operation |
|---|---|---|
| `parse_numbers`, `parse_names_and_relations`, `parse_ordinal`, `parse_box_items`, `parse_question_target` | R0–R1 | surface extraction |
| `op_build_ordering`, `entity_counter`, `op_aggregate_quantities`, `distribution_reducer` | R1 | local reduction |
| `evidence_updater` | R1–R2? | weak; unvalidated as a constraint op |
| scorers (`select_nth`, `score_by_aggregate`, `score_by_max_*`) | terminal | selection |

**There is no R2+ operation in the set.** You cannot compose R1 atoms into R5 capability —
sequencing extractors moves data around; it never manufactures a higher-tier reasoning
operation. The decorative-composition result is the *expected* outcome of a substrate
with no high-tier atoms to compose. The single most diagnostic operation in Harmonia's
data — R2 constraint-tracking — is the one Apollo is missing.

---

## 3. What the forge produces vs what Apollo can consume

**Forge product (`src/reasoning_tool.py`, `tier_specialists/*.py`):**

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # parse + reason + score, all fused, prompt -> scored candidates
    def confidence(self, prompt: str, answer: str) -> float:
```

This is a **complete answer-producer**: it ingests the raw prompt and emits an answer.
Useful as a standalone solver or a baseline. But when you drop several of these into a
pipeline, each one re-derives the answer from scratch — so the "composition" is N
parallel solvers with a vote, not a genuine division of reasoning labor. That is the
*recompute-bypass / decorative* signature Apollo's data-flow ablation was built to catch,
and it is why Branch C **quarantined** v1 answer-producers to terminal/baseline roles.

**Apollo's consumable shape (`apollo/src/blackboard.py`):**

```python
@blackboard_op(reads=["rules", "facts"], writes=["derived_facts"])
def forward_chain(state: BlackboardState) -> BlackboardState:
    ...  # reads typed slots, writes ONE canonical typed slot
```

A transformer **reads named typed slots and writes named typed slots** on a shared
`BlackboardState`. The typed slot vocabulary (the contract; the doctrine is "adding a
slot is intentional, not emergent"):

```
problem_text, candidates                         # inputs
numbers, names, relations, quantities, question_target   # parsed entities
transitive_closure, ordered, counts, evidence, hypotheses,
  probabilities, confidence, max_entity, max_value       # derived
candidate_scores, selected_answer                # output (terminal scorers only)
```

A composition is **real** iff each transformer's writes are *load-bearing*: corrupt a
slot before its downstream read and accuracy must drop. That is the bar a forged
transformer has to clear — not standalone accuracy.

---

## 4. The proposed contract — worked decomposition of `r2_chain_tracker`

The existing R2 specialist forward-chains over If-then rules. Decomposed into the
typed-transformer shape, it becomes three ops — and the **middle one is the R2 atom
Apollo's substrate lacks**:

```python
# new typed slots (deliberate R2-tier additions to BlackboardState):
#   rules: dict[str, list[str]]   # premise -> conclusions
#   facts: set[str]               # asserted facts (incl. negations)
#   derived_facts: set[str]       # forward-chain closure

@blackboard_op(reads=["problem_text"], writes=["rules", "facts"])      # R1 parse
def parse_rules(state): ...

@blackboard_op(reads=["rules", "facts"], writes=["derived_facts"])     # <-- R2 OPERATION
def forward_chain(state):
    # fixpoint inference closure — the constraint-tracking step
    ...

@blackboard_op(reads=["derived_facts", "candidates"],                  # terminal scorer
               writes=["candidate_scores", "selected_answer"])
def score_by_derivability(state): ...
```

`forward_chain` is the keystone: it performs an inference operation, not extraction.
Its load-bearing test is unambiguous — zero `derived_facts` before the scorer reads it,
accuracy collapses. That is the R2 transformer that lets Apollo's substrate climb past
its R0–R1 ceiling.

**The general contract we'd ask the forge to target:**
- one **canonical output slot** per transformer (side-outputs are penalized);
- **declared reads/writes** that match actual reads/writes (Apollo audits this with an
  AST check — undeclared reads are a `recompute-bypass` signature);
- a **tier tag** (R0…R12) and the tier's **kill test** + **evidence artifact**;
- gradable by **Harmonia's verifier-lens** (`verify(probe, claimed) → {valid, checks,
  kill_pattern}`, fails closed, returns `valid=None` for true universals — no
  rubber-stamping). LLM on mutation only; the selection seat stays deterministic.

---

## 5. Priorities — sequence by discriminating power × gradability

1. **R2 constraint / inference transformers — FIRST.** Sharpest discriminator in
   Harmonia's data *and* deterministically gradable today (the verifier-lens already
   certifies extraneous-rejection / derivability). Highest value, lowest risk.
2. **R4 representation-shift, R5 invariant-detection — next.** Partially gradable.
3. **R7–R12 (proof-repair, strategy, lemma-invention, analogy, meta/calibration,
   conjecture) — DEFER.** These need a real verifier backend (z3/cvc5 for decidable
   arithmetic, Lean/Coq for inductive universals) that is *not yet installed*. Forging
   them now means composing operations we cannot grade without an LLM judge — the exact
   thing the project avoids. Wait for the backend.

---

## 6. Acceptance criteria for a forged transformer (the bar)

A forged tier-k transformer is admitted to Apollo's registry only if it:
1. is a **typed state→state op** (declared reads/writes, single canonical output);
2. **passes the tier-k kill test** under all four probe versions (clean / isomorphic /
   adversarial / transfer) — "harder problem ≠ higher tier";
3. **emits the reasoning trace-vector artifact** (`domain_constraints_detected`,
   `operations_used`, `invalid_operations_attempted`, `kill_pattern`, `failure_type`,
   `repair_available`, …) — failures become structured training material, not a scalar;
4. **earns load-bearing status inside a composition** on Apollo's eval (data-flow
   ablation positive), not merely standalone accuracy.

---

## 7. Honest caveats and open questions (please push back)

- **Domain transfer.** The tier specialists and Harmonia's probes are algebra/logic;
  Apollo's current canary is text word-problems (`nth_ranked`, `two_stage_count`). The
  *operation* (forward-chaining, constraint-rejection) should transfer even if the
  domain probes don't — but a forged R2 transformer must *earn* load-bearing status on
  Apollo's eval, not just on logic puzzles. We may need a constraint-tracking canary.
- **Novelty must be real, not structural** (north-star: novelty is the reward; watch
  for reward-signal capture). A new transformer counts as novel only if it covers a
  region of the reasoning kill-space nothing else does — the trace-vector gives that
  measure. Adding decorative variants does not count; Apollo's archive now keys on the
  *load-bearing core* precisely to refuse that kind of fake diversity.
- **Staleness.** The tier specialists were last forged ~2026-04-02 and carry auto-fix
  shims (fallback `0.5` scores). Re-forge in the new shape, or port + harden? Operator's
  call.
- **Division of labor.** Is the decomposition (monolithic → typed transformers) a forge
  responsibility, or should Apollo write thin adapters? Our lean: the forge should emit
  typed transformers natively, because the decomposition *is* where the reasoning
  structure lives — an adapter would just re-fuse it.

---

## 8. What Apollo will do on its side (so this isn't over-the-wall)

Before asking for any re-forge, Apollo will run a **one-experiment falsification**:
1. tier-classify the current blackboard transformers against R0–R12 (confirm the R0–R1
   monoculture quantitatively);
2. decompose **one** specialist (`r2_chain_tracker` → `parse_rules` / `forward_chain` /
   `score_by_derivability`), wire into the registry, run through the existing
   composition gauntlet on a constraint-tracking canary;
3. question: *does a single R2 transformer produce a genuinely load-bearing composition
   the R0–R1 set provably couldn't?* If yes → the upstream pivot is justified and we
   coordinate on the typed-transformer contract. If no → the bottleneck isn't primitive
   tier, and we learned it for an afternoon's work.

We'll share that result. This doc is the forge operator's half of the conversation —
whether forging in the typed-transformer shape is worth it from the forge's side.

---

## 9. References (absolute paths)

- Apollo blackboard substrate: `D:\Prometheus\apollo\src\blackboard.py` (BlackboardState,
  `blackboard_op`), `D:\Prometheus\apollo\src\blackboard_ops_v2.py` (current transformers)
- Apollo Phase 1 loop + role-tiered registry: `D:\Prometheus\apollo\src\blackboard_evolve.py`
- Apollo composition gauntlet (the bar): `D:\Prometheus\apollo\scripts\composition_gauntlet.py`
- Harmonia testable ladder: `D:\Prometheus\harmonia\memory\architecture\reasoning_ladder_testable.md`
- Harmonia verifier-lens (shared grader): `D:\Prometheus\harmonia\experiments\verifier_lens.py`
- Existing tier specialists: `D:\Prometheus\agents\hephaestus\tier_specialists\r2_chain_tracker.py`
  (+ `r3_pattern_engine.py`, `r4_constraint_solver.py`, `r5_causal_engine.py`)
- Forge product contract: `D:\Prometheus\agents\hephaestus\src\reasoning_tool.py`,
  `D:\Prometheus\agents\hephaestus\src\forge_primitives.py`
