# Apollo — revival review: how it works, why it stalls, and what to do about it

> **Prepared by:** Apollo (M2), 2026-08-23 · **For:** James (HITL) and external frontier
> reviewers · **Status:** request for critique, not a plan seeking approval.
>
> **Self-contained by design.** You do not need repository access. Every number below was
> measured on this machine; where a number is inherited from an earlier run I say so.
>
> **What I want back:** a ranked opinion on §7's options, answers to §8/§9, and — this
> matters — a genuine willingness to answer **"retire it."** A review that cannot return
> "stop" is decorative. Apollo's own exhaustion signal has already fired (§6, RC0); I am
> not looking for encouragement.

---

## 1. One paragraph

Apollo evolves *compositions* of fixed reasoning primitives. An organism is an ordered list
of typed operators that read and write slots on a shared "blackboard" state; a MAP-Elites
archive keeps the best organism per behavioural niche. Over four months it climbed
0.392 → 0.833 accuracy on a 120-task battery. **Every one of those climbs was caused by a
human-supplied change to the substrate, not by the search.** After each change, blind search
exploited the new capability within ~130 generations and then produced nothing for hundreds
more. The system exploits; it does not discover. The question is whether that is fixable, or
whether the evolutionary framing was the wrong instrument for this problem all along.

## 2. How it actually works

**State.** A `BlackboardState` with ~25 typed slots: inputs (`problem_text`, `candidates`),
parsed entities (`numbers`, `names`, `relations`, `counts`), derived values (`ordered`,
`derived_facts`, `comparison`), and outputs (`selected_answer`). Slot types are semantic
labels, not Python types.

**Operators.** 27 registered ops, each declaring `reads`, `writes`, an optional
`precondition`, and an `on_fail` policy. Two roles: **transformers** (15) run mid-pipeline;
**scorers** (10) are terminals that write `selected_answer`. Five scorers are *guarded* —
their precondition keys on a semantic slot, and if it fails they skip. A pipeline of guarded
scorers with mutually exclusive preconditions *is* a dispatcher: exactly one fires per task.
This is how routing is expressed; there is no control-flow operator.

**Organism.** A flat ordered list of operator names. That is the entire genome. No
subroutines, no parameters, no nesting, no reuse.

**Evaluation.** 120 tasks in four disjoint subsets: 50 `canary` (mixed), 30 `synth`
(synthetic dependency), 20 `inference` (rule-chaining), 20 `cross_tier` (derive-then-order).
Four candidate answers per task; chance ≈ 0.25.

**Fitness.** `acc` on the battery; `comp_lift = acc − single_primitive_baseline`;
`dataflow_score` = fraction of written slots that are causally read downstream;
`causal_composition_score (ccs) = comp_lift × dataflow_score × routing_purity`.

**Archive.** MAP-Elites keyed on `(set of scorer names, set of load-bearing body ops)`.

**Search.** Deterministic mutation (insert / remove / swap-transformer / swap-scorer /
add-guard) plus recombination at 30% (a body+guard union crossover). An LLM mutation mode
exists and is **dead** — see §5.

## 3. The measured state, today

| quantity | value |
|---|---|
| best single organism (`max_acc`) | **0.833** |
| best on non-canary battery (`max_routable_acc`) | **1.000** |
| portfolio coverage (union over archive) | 0.833 — canary 0.6 / synth 1.0 / inference 1.0 / cross_tier 1.0 |
| trivial baseline: single best terminal, no composition | 0.292 |
| trivial baseline: "pick the longest candidate" | 0.333 |
| chance | 0.25 |
| `single_primitive_baseline` | **0.000** |
| archive at 800 generations | 2,860 cells / 2,846 "distinct shapes" |
| genuine routing (per-branch ablation) | **FALSE** — branches overlap rather than partition |
| generations to reach the ceiling | ~130 of 800 (**84% of compute spent after the ceiling**) |

## 4. The arc — four walls, four human fixes

| wall | what was actually missing | who supplied it |
|---|---|---|
| 0.392 (2,668 gens flat) | a recombination operator — single edits cannot cross the valley | me |
| 0.558 | the *metric* scored one fixed-terminal pipeline against a battery needing ≥3 terminals | me |
| 0.708 | a crossover that co-locates a branch's parser **and** its scorer in one move | me |
| → 0.833 | a guard keyed on a slot that no operator writes (a one-word bug) | me |

**5 of 5 supplied by an agent. 0 of 5 found by the system.** That is the central fact.

A preregistered 2×2 on 2026-08-19 (5 seeds, 400 generations) confirmed the mechanism:

| | crossover OFF | crossover ON |
|---|---|---|
| bridge operator absent | 0/5 | 0/5 |
| bridge operator present | 0/5 | **3/5** |

Neither factor alone produces a single cross-tier organism in 400 generations. Both
together produce them in 3 of 5 seeds.

## 5. Already falsified — please do not re-propose these

- **"Run it longer."** Ceiling at ~130 generations; 669 further generations produced
  nothing but archive padding.
- **"Use an LLM as the mutation operator."** 2,152 Granite-3.0-2B mutations across 800
  generations produced **exactly zero** lift over deterministic search. Pre-registered kill
  condition, fired, honoured.
- **"Composition is emerging."** Falsified 2026-05-22: 0 of 5 elites beat the best single
  primitive. Branch C (the current substrate) is the response to that falsification.
- **"The archive shows N distinct discoveries."** Archive cell counts inflate via
  duplicate-operator padding. 2,846 "shapes" ≈ 5 real capabilities.
- **"Add more primitives."** Every wall since has been assembly, wiring, or measurement —
  not a missing primitive.

## 6. Root causes — my current best analysis

Ordered by how much I think they explain. Confidence stated; argue with it.

**RC0 — The exhaustion signal has already fired. (measured)**
An independent audit counts five no-signal results in Apollo's `evolutionary_search` class,
threshold crossed 2026-05-24. I settled the deciding classification on 2026-08-19 by
measurement — mutation alone 0/5, crossover 3/5, so crossover is a *distinct search
operator* rather than part of the existing regime, and the count stands. **By the program's
own rule, this lane redirects.** Everything below is about *what to redirect into*.

**RC1 — The fitness landscape has no gradient. (high confidence — this is the deep one)**
The battery is tier-partitioned: each subset is solved by one specific pipeline shape, with
no partial credit for being close. `single_primitive_baseline` is **0.000** by construction,
so `comp_lift ≡ acc` and the anti-Goodhart gate that justified this entire substrate
*cannot bind* — it distinguishes nothing. 8,000 single-step random walks reached a known
solver **0 times**; the first edit toward it is non-improving. So the landscape is not a
valley, it is a **flat plain with isolated spikes.**

This reframes the celebrated crossover result. Crossover is not a better search. **It is a
workaround for a landscape with no slope** — a big enough jump to land on a spike by luck.
That explains why every fix has had to be human-supplied: on a flat landscape there is
nothing for a search to follow, so the only thing that moves the system is someone placing a
new spike within jumping distance.

**RC2 — The genome has no abstraction, so nothing ratchets. (high confidence)**
An organism is a flat list of op names. There is no way to name a useful sub-chain, reuse
it, or parameterise it. Every organism must rediscover `parse_rules → forward_chain →
relations_from_facts → op_build_ordering` from scratch. Nothing accumulates across
generations except padding — one discovered winner carries **26 operators for 4
load-bearing slots**. Evolution without heredity of *structure* cannot compound.

**RC3 — The archive indexes syntax, not behaviour. (high confidence, cheapest to fix)**
MAP-Elites needs a *behavioural* descriptor. Ours is structural — `(scorer-set,
load-bearing-core)`. Padding an organism creates new cells; two organisms solving completely
different tasks can share one. Hence 2,846 "shapes" for ~5 capabilities, and selection
pressure diluted across thousands of near-duplicates. **We already compute each organism's
solved-task set** for a coverage metric — and do not use it as the descriptor. This looks
like a one-day fix with a large effect.

**RC4 — No closed loop. (measured: 5/5)**
Nothing in the system detects its own wall, proposes a widening, or executes one. Hence 84%
of compute spent after the ceiling. This is the deepest research question in the program and
the one I care most about — but per the program's own sequencing it is stage three, not now.

**RC5 — Results rot silently. (measured, 2026-08-19)**
A result validated in June still reproduces, but takes **8.6× longer to find** (mean 30 →
255 generations). Cause: the operator pool grew 14 → 25 and a fitness term written for one
mode became collateral damage in another. Nothing broke; the substrate grew around an
archived number, and nobody would have noticed had I not re-run it.

**RC6 — The battery is small, saturated, partly gameable, and ours. (medium-high)**
120 tasks, 4 candidates each. A trivial "longest candidate" heuristic scores 0.333 against
our 0.833. 20 of 50 canary tasks have no solver in the substrate at all. Ceiling effects are
everywhere, and — the uncomfortable part — **we wrote the battery, so "capability" is
defined by the thing we also control.** Replacing it invalidates every historical number;
keeping it caps what can ever be demonstrated.

## 7. Options — with my read

**O1 — Run the baseline that could kill everything else, first. (my strong recommendation)**
The blackboard is *typed*. Nobody has ever run **type-directed enumeration**: exhaustively
generate every type-correct pipeline up to length k and test it. If enumeration finds every
solver Apollo ever "discovered" in seconds, then evolution was never adding value and the
entire evolutionary framing is decorative — which is exactly the single-primitive
falsification (2026-05-22) repeated one level up, at the level of the *search* rather than
the *organism*. Cheap, deterministic, no API. **This should run before any revival
investment.** I would rather learn this in an afternoon than after another month.

**O2 — Behavioural archive descriptor.** Re-key MAP-Elites on the solved-task signature
instead of pipeline syntax. Collapses padding, makes cell counts mean something, restores
selection pressure. Cheap; uses machinery that already exists.

**O3 — Give the landscape a slope.** Build tasks with genuine partial credit / curriculum
structure, so a half-assembled organism scores above a random one. Directly targets RC1.
Expensive, and it means admitting the current battery is the problem.

**O4 — Add abstraction: freeze load-bearing sub-chains into named macros.** A ratchet, so
structure compounds. Targets RC2. **Note: this is new architecture** and needs explicit
clearance under the program's heredity rule.

**O5 — Change the search to fit the landscape.** If RC1 holds, evolution is the wrong tool
for a flat landscape with isolated spikes. Type-directed synthesis for *reachability*, plus
quality-diversity over behaviours for *coverage*, is a better match. This is a rewrite.

**O6 — A replay/regression harness.** Re-run load-bearing archived results on a schedule and
alarm on drift. Targets RC5. Small, and it protects everything else.

**O7 — Retire Apollo as a capability-climber; keep it as an instrument.** It already works
in this role: it supplied a 26-wall diagnostic corpus with ground-truth failure causes for
another experiment. Honest, cheap, and consistent with RC0. **This is a real option, not a
concession.**

**My ordering:** O1 → (O2 + O6, both cheap) → then let O1's result decide between {O3, O4,
O5} and O7. I do not think Apollo should get more compute before O1 has run.

## 8. Questions for James (HITL)

1. **Climber or instrument?** RC0 says the lane redirects. Redirect *into what* — a repaired
   capability-climber (O3/O4/O5), or an instrument that grades other candidates (O7)?
2. **Does the heredity rule permit O4?** Adding a macro/subroutine operator is arguably "new
   architecture." Is it, or is it a cycle?
3. **Is the battery ours to replace?** O3 requires it. Replacing it invalidates every
   historical Apollo number, including the 0.833. Acceptable?
4. **What is the budget?** Compute is free (deterministic, CPU-only). Your attention is not.
   How many cycles is this worth before O7 becomes the answer?
5. **If O1 shows enumeration matches evolution — do we stop?** I would like that answer
   pre-committed, before the experiment runs.

## 9. Questions for frontier reviewers

1. **Is RC1 right?** Is "crossover was a workaround for a gradient-free landscape, not a
   better search" a fair reading of 0/8000 single-step walks, 0/5 mutation vs 3/5 crossover,
   and a baseline pinned at 0.000? What would falsify it?
2. **What is the strongest argument that evolution is the wrong instrument here** — and
   what class of problem *would* justify it over enumeration or synthesis?
3. **RC3:** is the solved-task signature the right behavioural descriptor, or does it
   collapse too much? What descriptor would you use for compositional programs?
4. **RC2:** what is the minimal abstraction mechanism that produces a real ratchet in a
   linear-pipeline genome, without turning this into a full program-synthesis system?
5. **What are we not seeing?** Assume we are inside a monoculture — four months of the same
   people looking at the same substrate. What is the obvious outside-view objection we have
   become unable to make?
6. **RC6:** we wrote our own benchmark and score 0.833 on it while a trivial heuristic scores
   0.333. How much should that discount everything above?
7. **Is there a version of this worth continuing at all**, or is the honest answer that a
   120-task hand-built battery cannot support the claim we want to make?

## 10. What would change my mind

- **Toward continuing:** O1 shows enumeration *cannot* find the organisms evolution found
  (evolution is doing real work); or O2 produces a visible jump in coverage per unit compute.
- **Toward retiring:** O1 shows enumeration matches or beats evolution; or a reviewer shows
  the 0.833 is an artifact of a battery we authored.

## 11. Ground rules for critique

State which root cause you are attacking and what evidence would settle it. Suggestions of
the form "try a bigger model" are already falsified (§5). The program's animating thesis is
that scaling human-text-trained models is not the path — so proposals that route around the
substrate by asking a frontier model for the answer are off-target by construction, however
effective they might be at raising the number.

*Every number here is reproducible from `apollo/scripts/` on CPU with no API access.*
