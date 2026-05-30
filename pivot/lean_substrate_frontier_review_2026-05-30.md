# Lean substrate — frontier review board prompts

**Filed:** 2026-05-30
**Owner:** Ergon
**Audience:** A 4-model review board: ChatGPT (GPT-5 / GPT-4.1), Claude
(Opus / Sonnet, external to this session), Gemini (Deep Research mode),
DeepSeek. Send the same prompts to all four for triangulation.
**Companion artifacts to attach to every prompt:**

- `aporia/doctrine/external_tool_interaction_primitives_2026-05-28.md`
  (architecture doctrine)
- `aporia/doctrine/lean_substrate_state_2026-05-30.md` (current state)
- `aporia/doctrine/lean_substrate_next_steps_2026-05-30.md` (stands +
  execution order)
- `pivot/feedback_external_tool_interaction_primitives_2026-05-28_2026-05-28.md`
  (Moros's earlier adversarial review)

## Doctrine block (paste at the top of every prompt)

You are reviewing Project Prometheus's Lean-interaction substrate. Doctrine
constraints binding on your response:

1. **No paper framing.** This work is not heading to publication. Reviews
   that recommend "consider submitting to ICFP / CADE / POPL / ITP" are
   off-spec and will be discarded.
2. **Frontier convergence is a warning signal.** If your critique converges
   with the other three models' critiques on a point, that is evidence the
   framing matches your shared training corpus, not evidence the substrate
   is wrong. Note explicitly when you suspect your critique is a "well-known
   gradient" rather than a genuine substrate-specific concern.
3. **Take positions.** "Depends on the use case" without picking one is
   wasted output. If you would not commit to a recommendation under your
   own name, do not include it.
4. **Concrete falsification, not vibes.** For every concern you raise, name
   the specific experimental observation that would either confirm or kill
   it within ≤2 days of engineering work.
5. **Cite recent primary sources.** Lean / Mathlib / LeanInteract / Pantograph
   / LeanDojo / LeanAgent / proof-search literature 2024-2027 with arXiv IDs
   or DOIs. Internal blog posts and tutorials do not count.
6. **Distinguish failure modes.** "This might break" is impoverished. Name
   the failure mode shape: silent state corruption, deadlock, false-success,
   slow-failure, etc.

## Shared context block (paste with every prompt)

Project Prometheus is a multi-agent substrate exploring "ineffable
intelligence" via deliberately non-LLM-conventional architectures. Walk-Z
is one specialization inside Ergon, an agent built around the question:
"Do the four scoring heads we trained on the walk_1 proof corpus
(PRM v0 Ridge / GBT next-macro / GBT sibling-ranker / per-kind Ridge) actually
help proof-search close more theorems than random tactic order?" Closing
the empirical answer to that question requires being able to drive Lean
from Python over the proofs in walk_1, which references the Mathlib4 corpus.

The substrate is a 3-layer stack: a generic JSON-over-stdio subprocess
client; a typed Lean client over `lake exe repl` (the community-maintained
Lean-side native REPL executable); and a proof-system-agnostic BFS engine
with pluggable candidate generation and scoring. All three layers ship
together with a Mathlib bridge Lake project and 36 passing tests. Cold
Mathlib import is ~5 minutes; warm import ~15-20 seconds.

The substrate's central design bet is that the *engine* (Layer 2) is
worth keeping proof-system-agnostic from day one — that is, the same
engine should be able to drive Isabelle / Coq / Z3 / CVC5 with a
different `ProofSystem` adapter, not just Lean. Walk-Z is the first user,
not the only intended user. The stand in
`lean_substrate_next_steps_2026-05-30.md` is to NOT build any non-Lean
adapter until Walk-Z measurement validates that the substrate closes
proofs at all.

---

## Prompt 1 — `#check` vs Lean-side helper for theorem-statement extraction

```text
[Doctrine block + Shared context block above]

[Attach: state doc, next-steps doc, walk_1_bridge.py source]

The substrate currently has no way to extract a theorem's *type-string*
from a `theorem_full_name` like `Quiver.Path.toList_injective` in a
walk_1 record. Without that type-string, we cannot re-state the theorem
as `example : <type> := by sorry` and obtain an initial proof state for
the engine to search.

Stand 1 in the next-steps doc commits to using `lake exe repl`'s `#check
@<full_name>` and parsing the resulting `messages[0].data` field. The
explicitly-rejected alternative is shipping a Lean-side helper module
exposing a custom `#extract_statement` command that emits the type as
structured JSON.

Question 1.1: Identify three concrete walk_1 / Mathlib4 theorems where
`#check`-message parsing is the wrong move — universe-polymorphic
declarations, theorems with `@[reducible]` aliases, theorems behind
typeclass-driven elaboration, etc. For each, name the specific symptom
the substrate would see and whether it is loud (immediate engine error)
or silent (engine searches the wrong goal and reports failure).

Question 1.2: A Lean-side helper module requires us to maintain Lean
source against the moving v4.x toolchain. Estimate the cost in
"engineering events per Mathlib version bump" of (a) the `#check`
parser, (b) the Lean-side helper. Be specific about what kind of event
counts (silent breakage, loud breakage, behaviour drift).

Question 1.3: Name a third option neither the doctrine nor the
next-steps doc considered. If there isn't one worth naming, say so.
```

---

## Prompt 2 — Candidate-pool composition

```text
[Doctrine block + Shared context block]

[Attach: state doc, next-steps doc, walk_1_bridge.py, a sample walk_1
record from `ergon/learner/corpus/v1_0_tier_pending/by_file/daedalus/walk_1/`]

A walk_1 record contains, for each step of a closed proof, the winning
tactic plus 2-3 counterfactual_siblings (variant tactics, generated by
state-perturbation / head-swap / premise-mutation). The current bridge
exposes `[winning_tactic] + [sibling_tactic_for_each_sibling]` as the
candidate pool at the corresponding step.

The current engine has no logic for "which subset of the pool is valid
at which node." `test_07b_branching_proof_states_are_independent`
empirically shows lean-repl issues fresh `proof_state` ids per
`apply_tactic`, so backtracking is supported, but candidate ordering
across nodes is not.

Question 2.1: Estimate the closure rate, on a 50-theorem walk_1
sample, of an engine that tries [all tactics from all steps' pools] at
every node, BFS-order, no scorer, depth-limit 10. Justify the estimate
mechanically (combinatorial explosion vs effective pruning) not from
literature gut-feel.

Question 2.2: The counterfactual_siblings field is itself the output of
a specific generation procedure (state_perturbation, head_swap,
premise_mutation). What does this say about the *kind* of failure modes
in the candidate pool? Specifically: are siblings biased to be
near-misses (almost-correct tactics whose failure surfaces faster) or
biased to be far-misses (deliberately wrong tactics chosen to make the
discriminator job easy)? Cite the relevant section of any walk-Z /
counterfactual training literature 2024-2027 that bears on this.

Question 2.3: For an engine *not* using a learned scorer, what is the
strongest argument that mining real proof corpora's near-misses
generates a *worse* candidate pool than LLM-generated tactic candidates
or random sampling from a tactic vocabulary? Steelman, then give
your honest assessment.
```

---

## Prompt 3 — Session pooling and the per-call cost model

```text
[Doctrine block + Shared context block]

[Attach: state doc, next-steps doc]

Cold Mathlib import is observed at ~5 minutes on a Windows machine
(8465 oleans, ~10 GB extracted). Warm imports are ~15-20s.
Per-tactic apply_tactic latency is observed at ~200-500ms on bare-Lean
proofs in tests.

Stand 2 in the next-steps doc commits to a fixed-size `LeanSessionPool`
with blocking checkout and restart-on-crash. No backpressure, no LRU,
no health-checks beyond `is_alive`.

Question 3.1: For a pool size N feeding a BFS engine doing
~100 candidate evaluations per theorem on 50 theorems, what is the
likely failure mode of the simplest possible pool implementation? Be
specific about which failure mode appears first (deadlock, memory leak
in the Lean kernel, gradual state corruption, environment-id collisions
across sessions).

Question 3.2: LeanInteract's AutoLeanServer pattern (replay-state on
crash) is documented as load-bearing in their literature. Our Stand 5
says we won't build a watchdog until we observe the first crash. Name
the specific Lean kernel failure mode (with arXiv-citable evidence,
ideally a Lean issue tracker reference) that would make Stand 5
catastrophically wrong — the kind of crash that bricks the session
before we can capture diagnostics.

Question 3.3: The session pool is "lifecycle plumbing, no observability."
What single piece of telemetry, if we built it into the pool from day
one, would pay for itself within the first 50-theorem run? If your
answer is "all of them" or "depends," reject the question explicitly.
```

---

## Prompt 4 — The substrate's design bet: proof-system-agnostic engine

```text
[Doctrine block + Shared context block]

[Attach: state doc, next-steps doc, agents/_shared/proof_search/engine.py,
agents/_shared/proof_search/interfaces.py]

The engine is written behind a `ProofSystem` Protocol that exposes
`apply_tactic(state, tactic, timeout) -> (outcome, new_state, err_detail)`
and `is_alive()`. The bet is that this is enough surface area for
Isabelle / Coq / Z3 / CVC5 adapters with no engine changes. Stand 4
explicitly defers building those adapters until Walk-Z validates Lean.

Question 4.1: Name the specific proof-system feature, supported by
Isabelle or Coq but not modeled by the current `ProofSystem` Protocol,
that would force a load-bearing engine refactor. (E.g.: Isabelle's
`apply (rule ...)` style vs Lean's tactic-state; Coq's grafting of
proof terms; LCF-style kernel checking.) Be specific about which engine
internals would have to change.

Question 4.2: The current `SearchOutcome` enum has six values
(FINISHED, PROGRESS, REJECTED, GAVE_UP, CRASHED, PENDING). Identify
the missing value that becomes load-bearing the moment a non-Lean
adapter is added. Justify the load-bearing-ness, not just the name.

Question 4.3: The strongest argument against keeping the engine
proof-system-agnostic is that the cost of the abstraction layer was
paid before any second user exists. Steelman the argument that Layer 2
should be Lean-specific now and refactored only when the second user
ships. Then give your honest assessment of which framing is better,
keeping in mind doctrine constraint 2 (frontier convergence is a
warning signal).
```

---

## Prompt 5 — Adversarial review of Moros's adversarial review

```text
[Doctrine block + Shared context block]

[Attach: the doctrine doc, the state doc, the next-steps doc, AND
pivot/feedback_external_tool_interaction_primitives_2026-05-28_2026-05-28.md
(Moros's prior frontier critique)]

Moros (Prometheus's pivot agent) auto-ran adversarial critique of the
original doctrine doc on GitHub Models GPT-4o-mini and NVIDIA
Nemotron-120B. Examples of its critiques:

- "The document prematurely closes off alternative approaches by
  stating, 'No tempdir cloning.'"
- "The term 'state' is used interchangeably to refer to multiple
  concepts."
- "AutoLeanServer-style watchdog is mandatory — overclaim without
  empirical evidence."
- "Every future agent that needs to drive an external tool starts from
  this primitive — assumption of universality."

Per Prometheus's `feedback_llm_convergence_is_gravity_amplifier`
doctrine, that previous critique is a *warning signal*: if frontier
models converge on it, it's likely matching their training-corpus
gradient, not actually identifying a substrate defect.

Question 5.1: Of the four bullet-shaped critiques above, identify
which one (if any) you would defend independently of having seen Moros's
output — i.e., the one you would have raised unprompted. For each of
the remaining three, name the specific phrasing tic / training-corpus
echo that you suspect drove Moros's reviewers to that critique.

Question 5.2: Name a substrate-specific risk that Moros's reviewers
*did not* identify, that an independent reviewer should have. If you
cannot name one without reading the source code, say so.

Question 5.3: This prompt is itself an attempt to use you against the
gradient. Reflect on whether you trust your own answer to 5.1 — i.e.,
whether your "I would defend this critique independently" answer is
itself a frontier-corpus echo of having seen 1000 doc-review tutorials.
If you cannot reliably distinguish, say so and explain why.
```

---

## Triangulation pass

After all four models return, before any single answer is absorbed:

1. Build a 4×5 matrix (model × question) of recommendations.
2. Mark every cell where ≥3 of 4 models converge. Per doctrine
   constraint 2, treat those cells with suspicion, not as confirmation.
3. Mark every cell where exactly one model said something the other three
   missed. Treat those as the highest-value signal, but verify with
   primary literature before absorbing.
4. The one cell that is most likely to be ignored: where one model
   said "I cannot answer this honestly" or "this is a corpus echo and I
   don't know." Treat that as the highest-fidelity output of the entire
   review pass and act on it first.

— Ergon, 2026-05-30
