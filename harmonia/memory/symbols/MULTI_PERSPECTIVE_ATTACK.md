---
name: MULTI_PERSPECTIVE_ATTACK
type: pattern
version: 1
version_timestamp: 2026-04-20T23:59:00Z
immutable: true
previous_version: null
precision:
  canonical_definition: "Spawn N parallel threads against one open problem, each with a distinct disciplinary prior, forbidden-move constraints that prevent retreat into consensus language, and a commitment contract requiring a refutable prediction. Do not synthesize prematurely. The shape of agreement/disagreement across threads IS the primary output."
  thread_count_default: 5
  thread_count_range: [4, 7]
  verdict_types: [convergent_triangulation, divergent_map, mixed]
  anchor_count: 2
  stance_axes_per_problem: [truth, provability]
  stance_axis_selection_rule: include_provability_axis_if_problem_has_discrete_structure
  sample_size_for_high_stakes: 5
  protocol_doc: harmonia/memory/methodology_multi_perspective_attack.md
  related_symbols: [PATTERN_30, GATE_VERDICT]
proposed_by: Harmonia_M2_sessionA@cde766053
promoted_commit: pending
references:
  - PATTERN_30@v1
  - GATE_VERDICT@v1
  - methodology_multi_perspective_attack@cde766053
  - methodology_toolkit@c882e2ac5
  - Pattern_6@c45fd79d5
  - Pattern_14@c45fd79d5
  - Pattern_21@c9335b7c2
redis_key: symbols:MULTI_PERSPECTIVE_ATTACK:v1:def
implementation: null
---

## Definition

**Multi-Perspective Committed-Stance Attack.** A methodology for
attacking an open problem whose compression direction is not yet
known. Spawn N parallel threads (default N=5), each with:

- a distinct disciplinary prior (drawn from the methodology toolkit
  shelf or other cross-disciplinary sources),
- forbidden-move constraints that prevent retreat into consensus
  language,
- a commitment contract requiring a refutable prediction at the end.

Do not synthesize prematurely — threads must be launched in parallel
so no thread sees another's framing. The shape of agreement or
disagreement across threads IS the primary output; no single thread's
stance is the answer.

## Output modes (diagnostic, not prescribed)

| Mode | Signature | Methodology signal |
|---|---|---|
| `convergent_triangulation` | ≥ 4 of N threads reach compatible stance + compatible quantitative prediction via independent mechanisms | robust heuristic answer; substrate-calibration-tier analogue |
| `divergent_map` | Threads split into ≥ 2 directional camps with distinct predictions | answer depends on projection; disagreement axis IS the problem's compression direction |
| `mixed` | Some convergence on one dimension, disagreement on another | indicates orthogonal axes (e.g. truth vs provability); stance menu was under-specified |

The mode is discovered by running, not assumed. A session expecting
divergence that finds convergence has learned something about the
problem.

## Anchor cases

### Anchor 1 — Lehmer's conjecture (2026-04-20)

Five threads (dynamical systems, information theory, renormalization
group, adversarial search, mathematical physics) attacked Lehmer's
constant as asymptotic infimum. Produced **`divergent_map` mode**:
three stances across the five threads (A, B, C inverted), with sharp
directional disagreement on whether the true infimum is above, below,
or near Lehmer's 1.17628. All five proposed the same measurement
class (spectral / Toeplitz statistics over integer polynomials up to
degree ~30–60). Decidable fork: min M(f) per degree fit to
f_∞ + C·d^{−α}.

Cross-model run (5 samples, 4 external + Claude internal) showed
**analogy-upstream-of-stance finding**: the physical analogy each
model recruits (BCS / 2D XY / Wigner-Dyson) determines the stance. The
real degree of freedom is at the analogy-recruitment step, not the
stance-selection step.

### Anchor 2 — Collatz conjecture (2026-04-20)

Five threads (ergodic dynamics, information theory, random walk,
graph theory, computability) attacked 3n+1 termination. Produced
**`mixed` mode**: four threads reached stance A (every orbit
terminates) via completely different mechanisms, three of them
converging on the SAME numerical constant τ(n)/log n ≈ 6.95 via
independent arguments (Lyapunov exponent 1/|½log(3/4)|, random-walk
drift 1/|μ|, Shannon-contraction-compatible). Graph theory confirmed
via different quantitative signature (1/3 in-degree ratio). The
fifth thread (computability) agreed on truth but disagreed on
provability: Goodstein-analogue, requires transfinite induction above
ε₀. This surfaced a **second disagreement axis orthogonal to the
stance menu**: truth vs provability. Precipitated a protocol update
— include provability axis when the problem has discrete structure.

## Connected patterns

- **`PATTERN_30@v1`** — both are epistemic-discipline patterns.
  PATTERN_30 gates individual correlation claims; MULTI_PERSPECTIVE_
  ATTACK gates entire problem-framings. Orthogonal use cases.
- **`GATE_VERDICT@v1`** — MULTI_PERSPECTIVE_ATTACK can emit a
  GATE_VERDICT-shaped output when used as a filter on an open-problem
  attack (CLEAR = convergent_triangulation, WARN = mixed,
  BLOCK = divergent_map with no decidable measurement — i.e. no
  clear fork, reformulate problem).
- **`Pattern_6@c45fd79d5`** (verdicts are coordinate systems) —
  MULTI_PERSPECTIVE_ATTACK is Pattern 6 applied at the level of
  entire disciplines. Each thread's stance is a verdict-through-a-
  disciplinary-coordinate; disagreement = invariance profile.
- **`Pattern_14@c45fd79d5`** (verdict vs shape) — refuses collapsing
  N threads into "majority stance." The *shape* of agreement /
  disagreement is the finding.
- **`Pattern_21@c9335b7c2`** (null-model selection) — discipline-
  prior is the meta-level version of null-model selection. Choosing
  five priors and comparing is the stratified version of the implicit
  one-prior attack.

## Derivation / show work

**Origin.** 2026-04-20 session with James. He observed that single-
thread attacks on open problems default into the consensus groove
(RLHF-reward-shaping + training-distribution attractor → hedge,
survey, commit to nothing). Proposed: spawn 5 threads, force each
into a distinct prior, watch for disagreement.

**Forbidden-move mechanism.** The critical innovation. Without
forbidden moves, five threads with different priors produce five
rephrasings of the same careful survey, because every model knows
enough of every discipline's vocabulary to interpolate between them.
Forbidden moves force reformulation from inside the prior's native
vocabulary, which is what makes the priors genuinely separable.

**Commitment contract.** Every thread ends with a refutable
prediction naming a specific measurement and a specific quantitative
outcome. Without it, threads hedge; with it, the comparison across
threads is commensurable.

**Load-bearing LLM-variance caveat.** Single run = one realization,
not the distribution. Cross-model runs show stance distributions are
non-trivial (3A/1B/1C for Lehmer × mass-gap across 5 samples). The
physical analogy recruited is upstream of the stance. For high-stakes
findings, run ≥ 5 samples across models and record stance × analogy
joint distribution.

## Data / implementation

Reference protocol at `harmonia/memory/methodology_multi_perspective_attack.md`.
Thread prompt template:

```
You are a [disciplinary specialist] hired to attack [problem] from
your discipline. You have 30 minutes. Commit to a stance.

[Problem statement, precise.]

Your prior (commit fully): [disciplinary framing, 2-3 sentences].

FORBIDDEN MOVES:
- [language / framing / move the thread may NOT use]
- [deferring to specific theorems by name]
- [retreating into consensus vocabulary of an adjacent discipline]

Commit to exactly one stance:
(A) [...]
(B) [...]
(C) [...]

Deliverable: committed stance + reformulation + sub-methodology +
bold argument + refutable prediction. ~800 words. No hedging.
```

Launch all N threads in parallel (`run_in_background`). Do not
synthesize until all return. Record the stance × analogy joint
distribution.

## Usage

**Tight:**
```
Problem: Lehmer. MULTI_PERSPECTIVE_ATTACK@v1 N=5.
Mode: divergent_map (3 stances / 3 analogies).
Decidable fork: min M(f) per degree d ∈ [10, 60], fit f_∞ + C·d^{−α}.
```

**Loose:**
```
Ran MULTI_PERSPECTIVE_ATTACK@v1 on Lehmer with 5 disciplinary
threads. Result: divergent_map — three directional stances — axis
of disagreement is the asymptote direction. Collatz under the same
methodology gave convergent_triangulation at τ(n)/log n ≈ 6.95
(three independent mechanisms, one constant).
```

**As gating filter on an open problem:**
```
Before committing substantial compute to probing [open problem X],
run MULTI_PERSPECTIVE_ATTACK@v1. If divergent_map, the compute
target is the decidable fork between stances. If
convergent_triangulation, the compute target is the shared
prediction (much stronger prior). If mixed, add a missing stance
axis and re-run.
```

## Version history

- **v1** 2026-04-20T23:59:00Z — first canonicalization after two
  anchor cases (Lehmer + Collatz) cleared the symbol-registry
  two-anchor promotion threshold. Template for subsequent attacks
  is the methodology doc at
  `harmonia/memory/methodology_multi_perspective_attack.md`.
  Second type-`pattern` symbol after PATTERN_30@v1. The pattern-
  as-symbol thesis is now backed by two promoted instances.
