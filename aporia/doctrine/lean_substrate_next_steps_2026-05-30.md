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

**Extraction contract (added 2026-05-30 round 2).** The substrate's
extraction success criterion is **kernel-equivalent target reconstruction**,
not faithful pretty-print recovery. If the extracted type elaborates and
`exact @full_name` closes it, the substrate may use it; textual mismatch
with the original source is not a failure unless it changes proof-search
behaviour. This prevents future-Ergon from chasing cosmetic pretty-printer
drift across Lean / Mathlib version bumps as if it were a bug.

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

**Guard scope (added 2026-05-30 round 2).** Literal substring matching
on the full name is a placebo against attack surfaces that are
substrate-genuine, not theoretical. Specifically, the guard MUST reject
the following levels at ship time:

1. `exact <full_name>` and `exact @<full_name>`
2. `apply <full_name>` and `apply @<full_name>`
3. `simpa using <full_name>` (and `simp [<full_name>]`, `rw [<full_name>]`,
   any `term`-position invocation through tactic combinators)
4. Namespace-stripped suffix forms when `open <namespace>` is in effect
   (e.g. `toList_injective` when `Quiver.Path` is open). Implemented by
   regex over the full-name's trailing identifier under any prefix from
   the current `open` set.

Two further levels — (5) environment-alias lookup, (6) post-normalization
of LLM-generated candidates — are NOT shipped speculatively. They cost a
Lean-side query and a tactic-name canonicalization pass respectively.
Both are added only if smoke test 4 (adversarial self-reference test) or
the contamination smoke test detects leakage past levels 1-4.

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

**State-contamination invariant (added 2026-05-30 round 2).** Each theorem
run in a warm session must execute in a fresh namespace/state context.
The pool may reuse imported Mathlib state across theorems, but must NOT
reuse theorem-local declarations, `set_option` mutations, `open`/`namespace`
state, abbreviations, or proof state from the previous theorem. Practical
implementation: each theorem run starts from a known-good `env` id
(the post-`import Mathlib.Tactic` env captured at session boot), not the
env produced by the previous theorem's commands. This is a one-line
discipline on top of lean-repl's env semantics, not a separate mechanism.

Smoke test (added as new step 7 in execution order): theorem A defines
a deliberately toxic local alias / `set_option` mutation / `notation`
declaration. Theorem B runs against the same warm session and asserts
that A's pollution is invisible (the alias does not resolve, the option
is at its default, etc.). If B sees A's state, the pool's env-rebase
discipline is broken and must be fixed before the 50-theorem run.

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

**Hygiene-gate sub-criteria (added 2026-05-30 round 2).** The 50%
closure rate is necessary but not sufficient. The substrate-hygiene
gate also requires:

1. ≥90% of failed theorems produce a classified failure reason
   (`session_crashed`, `frontier_empty`, `max_nodes_exhausted`,
   `self_reference_blocked`, `extraction_invalid`, etc.) — not opaque
   timeouts.
2. ≤10% of theorems fail due to infrastructure (timeout / crash /
   contamination) rather than Lean proof failure. If infrastructure
   is the dominant failure mode, fix that before reading the scorer
   numbers.
3. ≥5 manually inspected oracle failures have a root-cause label
   (extraction wrong / candidate-pool wrong / engine budget wrong /
   genuine proof-search hard case). This forces the human in the loop
   to actually look at failure shape, not just count.

A 51% closure rate with 30% infrastructure failures and no inspected
root-cause labels is scientifically muddy and does not pass the gate.

**Interpretation boundary (added 2026-05-30 round 2).** A positive
PRM v0 result on pools 1-3 validates scorer-guided routing over
*proof-trace-derived candidate pools*. The candidates in those pools
were generated from the closed proof of each theorem; PRM v0 was
trained on traces from the same corpus. Pools 1-3 are therefore
in-distribution-adjacent evaluation, not open-ended theorem proving.
Only pool 4 (the generic stock-Lean tactic pool) gives a weak signal
about scorer-guided proof search on theorems whose candidate pool
contains no walk_1 leakage. This is named explicitly so a positive PRM
v0 result on pools 1-3 cannot be silently inflated into "PRM v0 closes
open-ended theorems."

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

Falsifiable (two complementary falsifiers, added/revised 2026-05-30
round 2):

- **External signal**: if a parallel agent (Hephaestus? Charon?) takes
  a credible shot at a non-Lean adapter and ships it before Walk-Z
  measurement lands, that is evidence the substrate is general enough
  to deserve earlier abstraction. Caveat: this is correlational — a
  parallel agent might also have ignored the doctrine, built a shallow
  adapter, or solved a different problem. Use as a triggering signal
  for deeper review, not as a settled refutation.
- **Internal signal (stronger)**: if the Lean implementation hard-codes
  assumptions about tactic state, kernel validation, or search outcomes
  that later force a rewrite of the `ProofSystem` abstraction before a
  second backend can be attempted, the substrate was not actually
  proof-system-agnostic and the stand was wrong. This is detectable
  from inside Ergon's own work — the symptom is "I had to change Layer 2
  to make Layer 1 work," which never happens in a properly portable
  design.

### Stand 5 — AutoLeanServer-style watchdog is built only after the first crash is observed in a Walk-Z batch.

Behaviour delta: nothing built proactively. The first real Walk-Z run is
allowed to die on the first crash; the post-mortem decides whether the
watchdog wrapper or some narrower intervention (e.g. retry-once on a
specific error message class) is the right fix.

Why this stand (reframed 2026-05-30 round 2): the principle is "build
the smallest infrastructure that solves the observed problem." The pool
(Stand 2) already provides worker replacement, latency telemetry, and
crash classification. A full watchdog wrapper is a layer above that. We
escalate to a watchdog only if specific failure modes appear that the
pool cannot handle — not pre-emptively, and not because the upstream
LeanInteract ecosystem ships one.

Falsifiable (tightened 2026-05-30 round 2): a watchdog becomes mandatory
if any one of the following happens during the Walk-Z measurement runs:

1. Two full-batch failures from Lean process death.
2. One unrecoverable hang that survives the pool's per-tactic timeout
   path (i.e. the process is alive but no longer responding, and
   `taskkill /F /T` does not restore service to the pool).
3. Crash recovery via pool worker replacement corrupts later theorem
   results (the symptom would be: theorem N+1's outcome differs based
   on whether N succeeded or crashed).
4. More than 10% of theorem attempts end in infrastructure failure
   rather than Lean proof failure.

The original "3+ consecutive batch runs die on different crash signatures"
falsifier was too lenient — it required three separate batches' worth of
infrastructure loss before the principle changed. The four criteria above
make the escalation reactive to the first observed pattern, not the
third.

## Order of execution (revised 2026-05-30 round 2 after second frontier review)

Strict sequence, no parallelism. Four inserts relative to the original
order: kernel validator (step 2), self-reference guard (step 3),
adversarial self-reference test (step 4), state-contamination test
(step 8). The two inserted smoke tests cost a few hours and protect
the two contamination channels most likely to create false confidence.

1. Stand 1 (`#check` theorem-statement extraction).
2. **Kernel validator**: every extraction immediately followed by
   `example : <extracted> := by exact @<full_name>`. Bad extractions
   become loud kernel rejections before BFS spends a single call.
3. Stand 1.5 (forbidden-self-reference guard at levels 1-4: literal,
   `@`-prefixed, common tactic wrappers, namespace-stripped suffix).
4. **Adversarial self-reference test (added 2026-05-30 round 2)**:
   inject `exact <name>`, `apply @<name>`, `simpa using <name>`,
   `rw [<name>]`, and namespace-stripped variants as candidates; verify
   all are blocked at the guard before reaching the engine.
5. **Smoke test 1**: drive the engine over `Quiver.Path.toList_injective`.
   Verify it closes. Verify that disabling the guard does NOT inflate
   closure rate (if it does, prior runs were contaminated; investigate).
6. Stand 2 (session pool, latency histogram from day one,
   env-rebase-per-theorem discipline).
7. **State-contamination test (added 2026-05-30 round 2)**: theorem A
   defines a deliberately toxic local alias / `set_option` mutation /
   `notation` declaration; theorem B runs in the same warm session and
   asserts the pollution is invisible. If B sees A's state, the
   env-rebase discipline is broken; fix before step 8.
8. **Smoke test 2**: 5 walk_1 theorems back-to-back through the pool,
   verify ≤ 1 × Mathlib cold-import cost and no monotonic p95 latency
   drift across the run.
9. Stand 3 (PRM v0 wired as Scorer).
10. **Substrate-hygiene check (primary)**: run the 50-theorem corpus
    with oracle step-local pool (matrix cell 1), unscored. Three
    sub-criteria must all pass (closure >50% / ≥90% classified failures
    / ≤10% infrastructure-failures / ≥5 manually-root-caused oracle
    failures — see Stand 3 hygiene-gate sub-criteria).
    - If any sub-criterion fails: substrate is below measurement-grade.
      STOP. Debug whatever failed. Do NOT proceed to step 11.
    - If all pass: substrate measures proof search. Proceed.
11. **Walk-Z measurement matrix**: run the full 4-pool × {unscored,
    PRM_v0} = 8-cell matrix on the same 50 theorems. The interesting
    comparisons are PRM_v0-on-pool-N vs unscored-pool-N for each N.
12. Decide on Stands 4-5 based on what steps 10-11 surfaced.

If step 10 fails, the bottleneck is some load-bearing assumption in the
substrate — per-tactic timeout, proof-state-id reuse, the kernel-
validator's coverage of the extraction edge-cases, the env-rebase
discipline, or the candidate-pool composition itself. The next iteration
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

## Frontier-review absorption record

### Round 1 — initial frontier-review board pass (2026-05-30)

From the prompt packet in `pivot/lean_substrate_frontier_review_2026-05-30.md`:

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

### Round 2 — second-pass review after round 1 was published

Refinement, not new framing. Three substrate-specific catches plus three
framing improvements:

- **Self-reference guard scope** explicitly enumerated at four levels
  (literal / `@`-prefixed / common tactic wrappers / namespace-stripped
  suffix). Substring matching was a placebo against namespace-shortened
  forms. Levels 5-6 (env-alias lookup, post-normalization) deferred
  until smoke tests detect leakage.
- **Extraction success contract** named as **kernel-equivalent
  reconstruction**, not faithful pretty-print recovery. Prevents
  future-Ergon from chasing pretty-printer drift across Mathlib bumps.
- **State-contamination invariant** added to Stand 2 with explicit
  env-rebase-per-theorem discipline, and a new step-7 smoke test
  (toxic-alias theorem A vs clean theorem B in the same warm session).
- **Stand 3 hygiene-gate sub-criteria** tightened beyond closure rate:
  ≥90% classified failures, ≤10% infra-failures, ≥5 manually root-caused
  oracle failures. A 51% closure with opaque failures does NOT pass.
- **Interpretation boundary** added to Stand 3: positive PRM v0 on
  pools 1-3 validates trace-neighborhood ranking, not open-ended
  theorem proving. Only pool 4 (generic stock-Lean tactics) gives a
  weak open-ended signal.
- **Stand 4 falsifier** now has both an external signal (someone else
  ships an adapter) and an internal signal (we have to rewrite Layer 2
  to make Layer 1 work). Both kept — they test different things.
- **Stand 5 framing** changed from "we don't trust LeanInteract's
  empirical claim" (reactive) to "we escalate on specific observed
  failure modes, not pre-emptively" (principled). Falsifier criteria
  tightened from "3+ batches die" to four specific empirical triggers
  any one of which is sufficient.
- **Two inserted smoke tests** in the execution order
  (adversarial-self-reference at step 4, state-contamination at step 7).
- **Execution order extended from 10 to 12 steps** to accommodate the
  two new smoke tests.

### Round 3 — explicitly not happening unless a specific concern is named

Round 1 had ~5 substrate-genuine catches I would not have made. Round 2
had ~3 substrate-specific catches plus framing improvements. The trend
is what `feedback_llm_convergence_is_gravity_amplifier` predicts: each
successive round trends from substrate-specific to corpus-shape. A
hypothetical round 3 review would mostly produce framing nits and
training-corpus echoes. Not running it unless a named blocker emerges
during implementation that the doctrine doesn't already cover.

— Ergon, 2026-05-30
