# Lean substrate — next steps (stands, not options)

**Filed:** 2026-05-30
**Owner:** Ergon
**Companion:** `lean_substrate_state_2026-05-30.md`
**Doctrine:** Per `feedback_take_a_stand`, this document presents stands as
falsifiable artifacts, not menu items for human decision. Per
`feedback_substrate_passive_consumer_warning`, every step is traced to a
behaviour delta. Per `feedback_anti_gravitational_well`, I have explicitly
suppressed the gradient toward "polish the substrate further" and toward
"write a doc / paper / report" framings.

## Hard-priority stands

### Stand 1 — Theorem-statement extraction is built next, via `#check` introspection.

Behaviour delta: one Python helper inside `walk_1_bridge.py` (call it
`extract_theorem_statement(lean: LeanSession, full_name: str) -> str | None`)
that sends `#check @<full_name>` after the relevant `import`, parses the
resulting `messages[0].data` for the `: <type>` substring, and returns that
type-string. The first time this works end-to-end on
`Quiver.Path.toList_injective`, we have unblocked walk_1 BFS.

Why this stand: the alternative was a Lean-side helper module exposing a
custom `#extract_statement` command. That route is cleaner long-term but
adds a Lean-side dependency we'd own; the `#check` route is one Python
function I can write today, and its parse-fragility is bounded (lean-repl
emits messages in a stable format that hasn't shifted across the v4.x
window). If the parse breaks on a hard case (`@`-elaboration, implicits,
universe polymorphism), the symptom is loud — the engine immediately
errors when it tries to use the bad statement — and the fix is local to one
function. The Lean-side helper survives as a fallback if `#check` parsing
turns out to be load-bearing brittle.

Falsifiable: if `extract_theorem_statement` works for the first walk_1
theorem we try but fails on >20% of the first 50 we try, the stand is wrong
and we build the Lean-side helper.

### Stand 2 — Session pooling is built second, before scorer wiring.

Behaviour delta: a `LeanSessionPool` class in
`agents/_shared/external_tools/lean_runtime/` that holds N pre-warmed
`LeanSession` objects (each already through `import Mathlib.Tactic`), hands
them out via context-manager checkout, and is responsible for restarting any
session that returned `SessionCrashed`. The behaviour delta is the test:
"50 walk_1 theorems run through the engine in 50 × (per-theorem cost) +
1 × 5 min, not 50 × 5 min".

Why this stand: cold-import cost is 5 min on this machine. Wiring the
scorers FIRST and only then noticing the pool is missing would mean
discovering the substrate is unusable at scale after committing to a Walk-Z
measurement schedule. Pool-first is two days of work that buy us 50× speedup
on the actually-interesting measurement. Per `feedback_infrastructure`,
don't over-harden — the pool is small (~100 lines), no fancy backpressure,
no LRU eviction. Fixed size, blocking checkout, restart-on-crash.

Falsifiable: if 50 walk_1 theorems still take >30 min on warm pool, the
bottleneck is somewhere else (probably per-tactic overhead) and the pool
isn't the right intervention.

### Stand 3 — Wire the existing PRM v0 head as the first real `Scorer`. Defer the other three heads.

Behaviour delta: a new `walk_z_scorers.py` module in
`agents/_shared/proof_search/` (or, more honestly,
`ergon/daedalus/walk_z/proof_search/`) that loads
`prm_v0_synthetic_test_results.json`-adjacent artifacts, exposes
`PRMv0Scorer(tactic_candidate, state_features) -> float`, and is the
first end-to-end `Scorer` plugged into a Walk-Z BFS run on real walk_1
theorems.

Why PRM v0 first and not the others: per
`feedback_no_naive_score_combination` (2026-05-26), naive combinations of
heads trained on heterogeneous candidate populations were worse than
random; PRM v0 alone hit 47% (+22pp over random). The cleanest signal is
the single best head, run alone, and *that* becomes the baseline. Mixing
in sibling-ranker / per-kind / GBT next-macro before we have a clean
PRM-v0-alone baseline would confound the result. The other heads are
deferred until we have a credible "scorer = PRM v0" reference number.

Falsifiable: if PRM v0 alone gives a closure rate ≤ random-tactic-order
baseline on walk_1, the head's training distribution does not transfer to
BFS scoring (separate from its prediction accuracy), and the substrate's
scorer-routing assumption was wrong.

### Stand 4 — Defer Isabelle / Coq / Z3 adapters until Walk-Z measurement validates the substrate.

Behaviour delta: I do not start any new ProofSystem adapter. The
substrate's reusability claim is currently conjectural; before generalizing
the framework, we test that it does the *first* job it was built for. If
Walk-Z scorer-routing closes more proofs than the random baseline, the
substrate is real; otherwise the generic-ProofSystem framing was overkill
for a system we couldn't even close one proof with. Either result is
informative.

Why this stand: per `feedback_substrate_passive_consumer_warning`, premature
abstraction is the substrate's failure mode. Per `feedback_agent_differentiation`,
multiple agents independently writing proof-prover adapters would be
research strategy, not coordination — but only after the lead agent (Ergon)
shows the design is sound by closing its own use case. The cross-prover
generalization is a stand to take *after* the first measurement, not before.

Falsifiable: if a parallel agent (Hephaestus? Charon?) takes a credible
shot at a non-Lean adapter and ships it before Walk-Z measurement lands,
that is evidence the substrate is more general than I claimed and the
stand is wrong.

### Stand 5 — AutoLeanServer-style watchdog is built only after the first crash is observed in a Walk-Z batch.

Behaviour delta: nothing built proactively. The first real Walk-Z run is
allowed to die on the first crash; the post-mortem decides whether the
watchdog wrapper or some narrower intervention (e.g. retry-once on a
specific error message class) is the right fix.

Why this stand: the doctrine doc inherited from LeanInteract claims
"AutoLeanServer-style watchdog is mandatory, not optional." That is their
empirical claim, not ours. Our `SessionCrashed` surface area is small; the
worst-case is `LeanSessionPool` notices a dead worker and replaces it,
which is one new method, not a wrapper class. Building the watchdog first
is the move I'd make if I didn't trust our `SessionCrashed` plumbing —
but we do trust it (test_08 covers it).

Falsifiable: if 3+ consecutive Walk-Z batch runs die mid-run on different
crash signatures, the watchdog *is* mandatory and the stand was wrong.

## Order of execution

Strict sequence, no parallelism:

1. Stand 1 (theorem-statement extraction).
2. Smoke test: drive the engine over `Quiver.Path.toList_injective` from
   the walk_1 record using the `[winning_tactic] + siblings` candidate
   pool. Verify it closes.
3. Stand 2 (session pool).
4. Smoke test: 5 walk_1 theorems back-to-back through the pool, verify
   ≤ 1 × Mathlib cold-import cost.
5. Stand 3 (PRM v0 wired as Scorer).
6. The actual Walk-Z measurement: 50 walk_1 theorems, three runs
   (random-order baseline / PRM v0 / oracle = winning-tactic-first),
   record closure rate.
7. Decide on Stands 4-5 based on what step 6 surfaced.

If step 6 closes <20% of theorems even with the oracle scorer, the bottleneck
is not the scorer — it's some load-bearing assumption in the substrate
(per-tactic timeout, proof-state-id reuse, candidate pool composition, or
the `#check` extractor); the next iteration is debugging that, not
generalizing the substrate.

## What I am explicitly NOT doing

To make the suppression visible:

- **No new layer.** Resisting the "Layer 3 = proof-corpus-shaped routing"
  framing the doctrine doc gestures at. Until Walk-Z measurement lands,
  any Layer 3 is speculation.
- **No paper / report / synthesis doc.** Per `feedback_exploration_not_papers`.
- **No expansion to non-Lean proof systems.** Per Stand 4.
- **No tooling / observability layer.** Per `feedback_infrastructure`, the
  speed-of-thought + HITL loop is already the accelerator; adding telemetry
  before there are runs to telemeter would slow us down.
- **No re-design of the doctrine doc in response to Moros's frontier
  critique.** Per `feedback_llm_convergence_is_gravity_amplifier`, that
  critique is a warning signal, not a directive. The frontier-review
  artifact below is the legitimate place to engage with it.

— Ergon, 2026-05-30
