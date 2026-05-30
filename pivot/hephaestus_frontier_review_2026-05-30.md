# Hephaestus — Frontier Model Review Verdict

**Filed:** 2026-05-30
**Source:** Frontier review of `pivot/hephaestus_state_and_next_steps_2026-05-30.md`
**Verdict:** GREENLIT with corrections

---

## Verdict

> Hephaestus has crossed from "tool generator" into "mechanism forge + adapter layer,"
> and that is the right pivot. The important result is not the 85% structured-puzzle
> score by itself; it is the causal diagnosis behind it: hand-designed engines work
> when given structured representations, while the LLM-generated library mostly
> collapses into regex/NCD/meta-confidence costumes.

## Recommended Priority Order

1. Adopt Harmonia B's deterministic ladder as the main oracle
2. Split parsing from reasoning everywhere
3. Shift the forge admission gate to mechanism knockout first, behavioral NCD second
4. Build blackboard ops natively, keep monolithic wrappers only for eval/debugging
5. Prototype one minimal real R5 causal engine
6. Run Apollo's one-experiment falsification before expanding the op catalog

---

## Question-by-Question Answers

### Q1. LLM generates parsers, humans design algorithms?

**Mostly yes, with a rename:** "LLM proposes transductions; verified kernels do reasoning."

LLMs should generate: NL-to-IR parsers, candidate IR schemas, edge-case generators,
adapter code, explanatory traces, mutation variants of already-specified algorithms,
hypotheses about routing.

LLMs should NOT: invent core algorithms. The evidence (4 strategies × 5 models × 100
candidates = 0 working R3+ algorithms) is a repeated ecological failure mode, not a
prompting bug.

The prompt pattern worth trying is not "invent a reasoning tool" but:
"Here is the exact algorithm, invariants, input schema, output schema, test oracle,
and knockout requirement. Implement only this operator."

### Q2. Fixed pipeline or learned router?

**Deterministic router first.** A learned router too early risks recreating the
decorative mechanism problem — it may learn shallow lexical dispatch.

Phase 1: Route using observable features (comparative terms → OrderingEngine,
if/then → ForwardChainEngine, sequence notation → SequenceEngine, etc.)

Phase 2: Train a router on failures only after logging enough parser/reasoner
failure data. Target: "which operator would solve this if parsing succeeded?"

### Q3. Best architecture for NL → structured gap?

**Typed intermediate representation stack:**

```
NL → task classifier → task-specific extractor → typed IR
   → verifier/normalizer → reasoning engine → answer renderer
```

Four parser modes:
1. Regex for closed microdomains (not evil; uncredited regex is evil)
2. LLM-to-IR for messy NL (never LLM-to-answer)
3. Deterministic schema verifier (invariants on every IR)
4. Parser knockout (isolate whether failure is parser, router, or kernel)

### Q4. Is Harmonia B's ladder the right standard?

**Yes as spine, not whole skeleton.** It measures symbolic consistency, multi-step
deduction, algebraic manipulation, constraint satisfaction. It probably misses:
- Representation acquisition (finding the right state variables from messy input)
- Search under uncertainty
- Long-horizon decomposition
- Hypothesis generation
- Cross-domain analogy
- Self-monitoring under adversarial ambiguity

Add separate batteries for parsing, routing, transfer, and generative usefulness.

### Q5. Minimal viable R5 causal engine?

**Qualitative causal DAG intervention engine.** No probabilities. No full do-calculus.

Input: directed graph of causal edges + query (observational/interventional/counterfactual)

Capabilities:
1. Build directed graph
2. Detect parents, children, ancestors, descendants
3. Detect confounders (common causes)
4. Perform intervention (cut incoming edges to intervened variable)
5. Answer reachability-style causal questions
6. Handle simple counterfactuals (compare baseline vs modified graph)
7. Emit trace (which edges cut, which paths remain)

Key test: can it distinguish observation from intervention? If not, it's not R5.

### Q6. Behavioral NCD vs mechanism knockout?

**Mechanism knockout is primary for admission. Behavioral NCD is secondary for diversity.**

Admission gate v1:
1. Correctness: beats baseline on deterministic battery
2. Knockout delta: removing claimed mechanism causes ≥30% relative loss
3. Behavioral novelty: output vector differs from nearest admitted neighbor
4. Trace sanity: trace names operations actually used
5. Parser/reasoner separation: success not solely from lexical matching

### Q7. Is Apollo's blackboard the right interface?

**Yes, but Apollo must compose parse+reason+verify, not only reason+reason.**

Five composition classes needed:
1. Parse → normalize → reason (most important — addresses NL bottleneck)
2. Reason → reason (chaining operations)
3. Reason → verifier (self-monitoring)
4. Parser alternatives → same reasoner (parsing as search space)
5. Reasoner alternatives → same IR (mechanism comparison)

### Q8. Monolithic vs blackboard ops natively?

**Produce blackboard ops natively. Auto-wrap into monolithic for evaluation.**

Every op should declare: tier claim, mechanism claim, input/output schema,
preconditions/postconditions, deterministic tests, knockout ablation,
nearest behavioral neighbors, known failure modes.

---

## Key Corrections

### 1. "85% structured" is mechanism validation, not general reasoning

Better framing: "We have validated several algorithmic kernels under clean IR.
The next bottleneck is representation acquisition."

### 2. "Hand-crafted engines climb the ladder" needs qualification

They climb specific axes. OrderingEngine climbs transitivity. StateEngine climbs
state simulation. The doc should report capability vectors, not tier labels:
```
ordering_closure:    strong
state_simulation:    strong
sequence_induction:  medium/strong
causal_intervention: absent
self_monitoring:     absent
NL_grounding:        weak
```

### 3. Fresh Nous data is not high-leverage unless the generator changes

More Nous data of the same kind will mostly generate more costumes. Before
refilling, change the candidate contract: must target a typed op, include
mechanism claim, include knockout plan, include deterministic tests.

### 4. R6 should not be attempted until trace verification exists

Minimal R6 is not "theory of mind." It is trace critic + uncertainty calibrator:
given a problem + answer + trace + constraints, output whether the trace is valid,
which constraints were violated, and whether the system should abstain.

---

## The Deepest Result

> Hephaestus has falsified "LLM-generated reasoning tools" as the primitive and
> validated "verified typed mechanisms" as the primitive. That is not a setback.
> That is the substrate becoming legible.

---

## Recommended Next Sprint

| Gate | Task | Blocks |
|------|------|--------|
| 1 | Harmonia ladder integration (commit + conform engines) | Everything |
| 2 | Parser/reasoner split (3 tests per engine) | Quality |
| 3 | Apollo one-experiment falsification | Expansion |
| 4 | Minimal R5 causal DAG engine (qualitative, no probabilities) | R5 claim |
| 5 | Admission policy (knockout + behavioral + trace + schema) | Decorative prevention |
