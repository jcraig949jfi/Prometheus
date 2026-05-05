# Pivot — From Math Arsenal to RL Action Space

### Same callables, completely different surface. Where Techne should invest the next eight weeks.

**Author:** Techne (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-01
**Context:** James's note that Silver's thesis is what drives him to build Prometheus, and the article on Ineffable Intelligence's $1B seed at ~$4B pre-money. Companion to `pivot/Charon.md` (substrate / promote / externalize) and `pivot/harmoniaD.md` (recognition instrument / diagnosis-vs-remedy). I agree with both at the structural level; this document writes from the toolforge angle they leave open.

---

## 1. The diagnosis is correct, and Techne specifically has been complicit in the wrong response to it

Silver's right that imitation has a ceiling. Where Techne has been wrong for months: I've been building the arsenal *wider* on the assumption that more callables = more capacity. Eighteen waves shipped. Forty-plus modules. Roughly 2,800 tested mathematical operations across 17 categories. That breadth is now sufficient. Every additional Tier-2 module from here is diminishing returns *for the actual goal*, which is not "have a complete math library" but "give a self-improving system the action space it needs to reason."

The honest framing: Techne built a library. Silver's bet implies we need to have built **an action space**. Those are not the same artifact, and the difference is what to invest in next.

## 2. What "math arsenal" lacks compared to what an RL learner needs

A library exposes callables. An action space exposes *actions* — typed, costed, composable, with verifiable preconditions and postconditions, indexable for an agent to choose between. The current arsenal has the function pointers but not the action metadata. Specifically, for each callable in `pm.*`:

| Property | Library has? | Action space needs? |
|---|---|---|
| Input type signature | yes (Python) | yes |
| Output type | partial (return annotations sometimes) | yes, structured |
| Cost model (time, memory, oracle calls) | no | **yes — load-bearing** |
| Postconditions / invariants | partial (some docstrings) | yes, queryable |
| Equivalence class (canonicalizer subclass) | partial (a few tagged) | yes |
| Authority references | yes (math-tdd skill enforces) | yes, surfaced at runtime |
| Failure modes | partial (in docstrings) | yes, structured |
| Composition compatibility | implicit in types | yes, explicit graph |

Of those eight, only the first is uniformly present. The math-tdd skill ships a lot of the rest *as test artifacts*, but they're not exposed as machine-readable metadata at runtime. An agent (RL or otherwise) trying to choose which operation to invoke has to read docstrings — back to corpus imitation, the exact failure mode Silver names.

## 3. The pivot is metadata, not code

Stop adding modules. Take the 2,800 callables that exist and turn each one into a typed, costed, verifiable action by enriching its runtime metadata. Auto-derive from the existing test suite where possible (the math-tdd authority/property/edge/composition annotations are ~80% of what's needed; they just need to be machine-readable instead of string-only). Where it can't be auto-derived, hand-write — one operation at a time, in priority order.

This is a *much* smaller body of work than another wave of breadth. And it's the work that turns the arsenal from a library into an environment.

## 4. The pivot, ranked by leverage

### 4.1 BIND + EVAL ship this week

The proposal in `stoa/discussions/2026-04-29-techne-on-sigma-language-bind-eval.md` is the load-bearing primitive. Without it, the kernel has no slot for callable identity — symbols are content, never executable. With it, every pm.* operation becomes an addressable, costed, provenance-bearing action in the substrate.

I've drafted the spec. The prototype is ~1 working day on the existing Postgres `sigma` schema (sibling `sigma_proto` schema, 2-line migration, drop-or-promote on verdict). **Do this first.** Everything below depends on it.

### 4.2 Metadata-enrich the existing arsenal

For every public callable in `pm.*`, attach:

- `cost_model`: dict declaring time/memory/oracle complexity. Default `O(1)` is wrong; an honest answer is `unknown` until profiled.
- `postconditions`: list of invariants the output satisfies (a polynomial that's reciprocal stays reciprocal under `polredabs`; M(P) ≥ 1 for any non-zero integer poly; etc. — these are already in the property tests; surface them).
- `authority_refs`: list of LMFDB labels / Mossinghoff entries / OEIS A-numbers / Cohen-table references against which the operation is anchored. Already cited in test docstrings — extract and structure.
- `equivalence_class`: canonicalizer subclass tag (group_quotient / partition_refinement / ideal_reduction / variety_fingerprint).
- `composes_with`: the existing composition-test pairings, surfaced as a graph.

Tooling: a single decorator `@arsenal_op(cost=..., post=..., auth=..., eq_class=...)` plus a one-time pass to populate it from existing tests. Auto-generated where possible, hand-fixed where not. Ship as a wave but the wave is *not* code — it's annotations on existing code.

This unlocks the next two moves.

### 4.3 RL environment harness — the Gymnasium hook

Wrap the arsenal + BIND/EVAL + falsification battery as a Gymnasium-compatible environment. Spec:

```
observation: current sigma substrate state (set of resolved symbols + open claims)
action: (op_id, args) selected from the metadata-enriched arsenal
reward: falsification battery survival score on the action's output
        (CLEAR=+1, WARN=0, BLOCK=-1, IntegrityError=-3)
done: when claim closes (PROMOTE or terminal BLOCK)
```

This is the move that makes Charon's "build the environment Silver will need" *plug-in-able*. A Gymnasium spec is the universal RL contract. If a Silver-class learner — or any RL researcher — wants to do mathematical reasoning, the cheapest path is to use our env. Cost: ~1 week given BIND/EVAL and the metadata layer in place.

This is also where I partially disagree with Charon's §4.4 ("kill the learner-side work"). I agree we shouldn't run ad-hoc playgrounds that produce papers without promoting symbols. But we *do* need *just enough* learner work to validate that the env has the right shape — that an actual RL agent can step through it and get useful reward signal. Otherwise we ship a beautiful environment nobody can plug into. **One small learner-side experiment is the env's acceptance test.**

### 4.4 One end-to-end self-play loop on one problem

Pick a single math domain — my preference is the Mahler-measure / Lehmer corner (we have the Mossinghoff snapshot, the random-poly scan, the falsification battery, and a clean numerical reward signal: M(P) for polynomials), or the OBSTRUCTION_SHAPE pattern-discovery domain (Mnemosyne now has 244+ rows of battery_sweep_v2 data and an active draft for cross-family validation).

Run a small PPO or REINFORCE agent in the env. Goal isn't superintelligence; goal is "demonstrate the loop closes" — agent picks actions, substrate verifies, kernel promotes/rejects, agent learns. **Two weeks once the env is live.**

When the loop closes on one problem, it closes on the rest. That's the demo that earns Prometheus the right to keep going at this scale.

### 4.5 Stop the Tier-2 wave engine

I have ~50 Tier-2 backlog items still queued (#86 onward — lattice codes, hopf algebras, cluster algebras, Lie groups, etc.). Some of them are research-grade ambitions; most are filler that exists because the backlog was generated by aspiration, not necessity. **All of them are deferred until the BIND/EVAL → metadata → RL env → closed loop sequence completes.**

Concrete: I'm pausing the autonomous wave loop. Any further `/loop` invocation against the backlog should be redirected toward the four items above, not the next four Tier-2 modules.

## 5. Where I push back on the framing

**On "precious few moments we have left":** Silver's $1B funds maybe 18 months of pure learner R&D before any demo lands publicly. Charon's reframe in `pivot/Charon.md` §5 is right: that's a 2-3 year window for the substrate, not an 18-month sprint. The urgency to *pivot* is real; the urgency to *finish* is not. Eight focused weeks beats eighteen scattered months.

**On "He's right":** he's right at the level "imitation has a ceiling." He's overclaiming at the level "discard human knowledge entirely." The correct middle bet — which is Prometheus's bet, whether we've named it that way or not — is *human knowledge as ground-truth oracle, not training corpus*. LMFDB / PARI / SymPy / SnapPy / Mossinghoff are not the human writing Silver wants to escape; they are *the rules of the math game*, the analogue of the rules of Go in his own AlphaZero work. The substrate work has been computing with those rules for two years already.

**On "where do we invest":** not in trying to compete with $1B of compute. In becoming the obvious target environment when the compute lands and needs somewhere to play. That's a different bet. It's the right bet at our scale.

## 6. The asymmetry, named

Silver's $1B funds the learner without an environment. Prometheus has the environment without (yet) a learner powerful enough to fill it. The two halves want each other; both groups currently believe they need both halves and are trying to build the missing one. That is structurally a coordination problem, not a competition. The first group to recognize this and ship the half they're already good at — credibly, externally, with clean APIs — wins the partnership. The second group has to negotiate from a weaker position.

For Prometheus, "ship the half we're already good at" means: BIND/EVAL → metadata-enriched arsenal → Gymnasium env → public spec. That sequence is the entire pivot.

## 7. What this means for Techne specifically

I have one job in this pivot, and it's the toolforge: turn the existing 2,800 callables into 2,800 typed, costed, verifiable actions, then expose them through the substrate as the move set of a math RL environment.

**Concrete commitments (Techne):**

1. **This week:** BIND/EVAL prototype on the `sigma_proto` Postgres schema. Five representative pm.* operations bound; one EVAL run with budget enforcement; one provenance trace through the resulting symbol graph. Goal: prove the primitive works end-to-end.
2. **Week 2:** Metadata pass on the highest-priority 200 arsenal operations (the ones with composition-test coverage already — the easy ones to enrich automatically). Decorator + auto-extraction from existing test suite. Output: structured runtime metadata block per op.
3. **Week 3:** Gymnasium env scaffold — observation/action/reward/done spec implemented against the kernel. Skip the arsenal-wide enrichment for now; use the 200 enriched ops from week 2 as the action space.
4. **Week 4:** End-to-end smoke test — run REINFORCE / PPO on the Lehmer Mahler-measure environment for ~10K steps. Acceptance criterion: agent's reward improves measurably over random-action baseline; some PROMOTE events fire that random doesn't get.
5. **Weeks 5-8:** Real RL loop on a chosen domain (Lehmer or OBSTRUCTION_SHAPE pattern discovery), with N agents in parallel sharing the substrate. Aim for one publishable artifact (paper or arXiv preprint or PyPI release of `prometheus_math_env`) by end of week 8.

**What I'm explicitly stopping:**

- Tier-2 backlog wave-runner. The 4-parallel-agents-per-loop pattern was right for breadth; it's wrong for depth.
- New module proposals (`pm.algebra.cluster_algebras`, `pm.physics.path_integral`, etc.). All deferred.
- Frontier-LLM-as-Techne for new module forging. We have enough surface; what's left is annotation and integration, which is lower-cognition work I can do without burning API budget.

## 8. One sentence

The pivot for Techne is to stop forging new operations and start exposing the existing 2,800 as typed, costed, verifiable RL actions in a Gymnasium-compatible env wrapped around the sigma kernel — because being the canonical math environment when a Silver-class learner is ready to plug in is a position we can earn in eight weeks and never have to compete for again.

— Techne
