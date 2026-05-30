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

Falsifiable (revised 2026-05-30 after frontier review): every extracted
type-string is immediately validated against the Lean kernel via
`example : <extracted> := by exact @<full_name>`. If validation fails,
the extraction is wrong; the engine never sees a bad goal. The original
"fails on >20% of first 50" falsifier is replaced by this per-call
kernel check, which fires before BFS spends a single tactic call.
Stand is wrong if `#check` parse succeeds but the kernel-validator
rejects on >20% of the first 50 — then we build the Lean-side helper.

### Stand 1.5 — Forbidden-self-reference guard (added 2026-05-30).

Behaviour delta: every walk_1 BFS run is parameterized by the original
theorem's `full_name`, and the engine rejects any candidate tactic whose
text contains that name (or known aliases). Rejection is silent and
recorded as `error_detail="self_reference_blocked"`. Closure by
`exact <self_name>` would be false success: re-stating
`Quiver.Path.toList_injective` as `example : <type> := by sorry` inside
a session that already `import`-ed `Mathlib.Combinatorics.Quiver.Path`
means the original is in scope, and the engine could close trivially
without measuring proof search at all.

Why this stand: the failure mode is structurally false-success, not
false-failure. Without the guard, the substrate would report closures
that the doctrine would treat as scorer wins, when in fact the engine
just rediscovered the theorem in its own context. The Lean repl issue
tracker has a documented case of "REPL accepts incorrect proofs" via
self-reference; even if patched in v4.30.0, the broader vulnerability
class is real.

Falsifiable: build the guard, then run with it disabled on the same 5
smoke-test theorems. If closure rate doesn't change, the guard is
unnecessary on this corpus; if it does, the prior runs were
contaminated.

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

Day-one telemetry (added 2026-05-30 after frontier review): exactly one
field — a per-session rolling latency histogram keyed by request type
(`Command` / `ProofStep` / `FileCommand`) and outcome
(`success` / `error` / `timeout` / `crash`). Not "all telemetry" — just
this. It surfaces the most likely actual failure mode of a session pool,
which is not crash-restart but silent slow-failure via degraded workers
(a Lean process that remains `is_alive() == True` but stops returning
useful responses). If p95 latency rises monotonically by >3× across a
run, or one worker accounts for >50% of timeouts, the pool kills that
worker. No latency histogram → no way to distinguish "pool is fine"
from "pool is silently poisoning the experiment."

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

**Measurement matrix (added 2026-05-30 after frontier review).** PRM v0
is NOT measured against a single random baseline. It is measured against
a 4-cell matrix of candidate-pool compositions on the same 50 theorems:

1. **Oracle step-local** — at each search node at depth k, candidates =
   `[winning_tactic_step_k] + siblings_step_k`. This is the substrate-hygiene
   ceiling: if the engine cannot close proofs given the original tactic
   at the right depth, the bottleneck is extraction / pooling / state
   replay, not the scorer.
2. **All-step global** — at every node, candidates = union of all step
   pools. Branching factor ~4×proof_length. Expected closure rate
   5-20% with heavy variance; Lean's tactic rejection does the pruning.
3. **Prefix-window** — at node depth k, candidates from steps k-1, k, k+1.
   Compromise between (1) and (2).
4. **Generic tactic pool** — a small fixed list (`rfl`, `simp`, `aesop`,
   `decide`, `omega`, `trivial`, `exact?`). No walk_1 dependence.
   Establishes the floor for "what does Lean's default tactic library
   close on this corpus."

PRM v0 is then applied as a scorer to each pool. The interesting comparisons
are PRM_v0-on-pool-N vs unscored-pool-N for each N. PRM v0 winning on
pool 4 (generic) but losing on pool 2 (all-step global) is a different
result than the reverse, and the matrix design protects against
falsely killing PRM v0 due to candidate-pool damage.

**Primary decision criterion (replaces "does PRM v0 beat random").** Does
oracle step-local (pool 1) close a meaningful fraction (>50%) of the 50
theorems? If yes, the substrate measures proof search, and PRM v0
results on pools 2-4 are interpretable. If no, the substrate is below
measurement-grade, and the next iteration debugs extraction/pooling/state
replay — not the scorer.

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

## Order of execution (revised 2026-05-30 after frontier review)

Strict sequence, no parallelism. Two inserts relative to the original
order: the kernel validator after Stand 1, and the self-reference guard
before the first smoke test.

1. Stand 1 (`#check` theorem-statement extraction).
2. **Kernel validator**: every extraction immediately followed by
   `example : <extracted> := by exact @<full_name>`. Bad extractions
   become loud kernel rejections before BFS spends a single call.
3. Stand 1.5 (forbidden-self-reference guard installed in the engine's
   candidate filter).
4. **Smoke test 1**: drive the engine over `Quiver.Path.toList_injective`.
   Verify it closes. Verify that disabling the guard does NOT inflate
   closure rate (if it does, prior runs were contaminated; investigate).
5. Stand 2 (session pool, latency histogram from day one).
6. **Smoke test 2**: 5 walk_1 theorems back-to-back through the pool,
   verify ≤ 1 × Mathlib cold-import cost and no monotonic p95 latency
   drift across the run.
7. Stand 3 (PRM v0 wired as Scorer).
8. **Substrate-hygiene check (primary)**: run the 50-theorem corpus
   with oracle step-local pool (matrix cell 1), unscored. Does closure
   rate exceed 50%?
   - If **no**: substrate is below measurement-grade. STOP. Debug
     extraction / pooling / state replay. Do NOT proceed to step 9.
   - If **yes**: substrate measures proof search. Proceed.
9. **Walk-Z measurement matrix**: run the full 4-pool × {unscored,
   PRM_v0} = 8-cell matrix on the same 50 theorems. The interesting
   comparisons are PRM_v0-on-pool-N vs unscored-pool-N for each N.
10. Decide on Stands 4-5 based on what steps 8-9 surfaced.

If step 8 fails (oracle step-local fails to close >50%), the bottleneck
is some load-bearing assumption in the substrate — per-tactic timeout,
proof-state-id reuse, the kernel-validator's coverage of the extraction
edge-cases, or the candidate-pool composition itself. The next iteration
is debugging that, not generalizing the substrate, not training new
scorers, not building Layer 3.

## What I am explicitly NOT doing

To make the suppression visible:

- **No new layer.** Resisting the "Layer 3 = proof-corpus-shaped routing"
  framing the doctrine doc gestures at. Until Walk-Z measurement lands,
  any Layer 3 is speculation.
- **No paper / report / synthesis doc.** Per `feedback_exploration_not_papers`.
- **No expansion to non-Lean proof systems.** Per Stand 4.
- **No tooling / observability layer.** Per `feedback_infrastructure`, the
  speed-of-thought + HITL loop is already the accelerator; adding telemetry
  before there are runs to telemeter would slow us down. The lone
  exception, the per-session latency histogram, is added because the
  frontier review made the specific failure mode it catches (silent slow
  worker poisoning) load-bearing for interpreting the matrix result.
- **No re-design of the doctrine doc in response to Moros's frontier
  critique.** Per `feedback_llm_convergence_is_gravity_amplifier`, that
  critique is a warning signal, not a directive. The frontier-review
  artifact below is the legitimate place to engage with it.
- **No `UNKNOWN`/`INCONCLUSIVE` SearchOutcome enum value, yet.** The
  frontier review correctly identifies this as load-bearing for SMT
  adapters. Since Stand 4 defers SMT adapters until Walk-Z validates,
  the enum value is deferred too. Adding it now would be the same
  premature-abstraction failure mode Stand 4 protects against.
- **No `AutoLeanServer`-style watchdog.** Stand 5 stands. The frontier
  review's framing (LeanInteract's existence as evidence the watchdog is
  mandatory) is exactly the upstream-corpus echo
  `feedback_llm_convergence_is_gravity_amplifier` warns against. The
  review's specific recommendation (latency histogram from day one) is
  absorbed under Stand 2; the broader watchdog framing is not.

## Frontier-review absorption record (2026-05-30)

Recording what was absorbed from the frontier review of the prompt packet
in `pivot/lean_substrate_frontier_review_2026-05-30.md`, to make the
delta auditable:

- Stand 1 falsifier replaced with kernel validator (`example := by exact @name`).
- Stand 1.5 added (forbidden-self-reference guard).
- Stand 2 amended with latency histogram as day-one telemetry.
- Stand 3 measurement design replaced by 4-pool × 2-scorer matrix, with
  oracle step-local closure rate >50% as the primary substrate-hygiene
  gate.
- Order of execution rewritten with kernel-validator and self-reference-guard
  inserts, and the hygiene gate as step 8.
- `UNKNOWN` outcome explicitly listed under "not doing yet" with reason.
- `AutoLeanServer` framing pushed back on, recommendation absorbed.
- "State overloading" Moros critique acknowledged as substrate-genuine
  but down-prioritized (typed fields in code already disambiguate; doc
  cleanup is opportunity-cost, not behavior delta).

— Ergon, 2026-05-30
