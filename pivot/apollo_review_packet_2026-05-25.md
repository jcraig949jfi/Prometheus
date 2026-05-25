# Apollo Review Packet — 2026-05-25

**Date:** 2026-05-25
**Purpose:** Hand-off packet for external reviewers (Gemini / ChatGPT / Claude / anyone else). Three docs + the questions we most need pressure-tested. Read time: ~10 min for this cover; ~45 min for full packet.
**Why now:** Apollo crossed from "diagnostic / debugging" to "structured negative result + planned re-architecture." We have three artifacts that together describe what we found, what we built in response, and the framework we're using to evaluate it. We want sharp engagement before committing 7-9 days of engineering on Branch C Phase 1.

---

## Where we are in one paragraph

Apollo is a multi-objective evolutionary search over compositions of 27 atomic reasoning primitives. Over the past 2 weeks we (a) identified and fixed two bugs that had been hiding Apollo's actual selection dynamics, (b) ran a single-primitive baseline matrix on gen-2960 elites and got 0/5 compositional lift — *empirically falsifying that Apollo had been producing real compositions*, (c) hardened the ablation gate and added type discipline (which made selection honest but did not produce a breakout), (d) absorbed three external reviews (Gemini / ChatGPT / Claude) that converged on "ecological collapse, not failure of compositional reasoning as a concept" + diverged on whether Apollo's failure data is usable as-is for downstream consumers, (e) ran a hand-written blackboard prototype that beat Apollo's evolved gen-3551 elite by +5pp, confirming ChatGPT's "primitives are answer-producers wired at the output level, not typed state transformers" critique, (f) built a production POC of the new genome representation (Branch C) and (g) drafted a reasoning ladder v0.1 to give Prometheus a falsification-first vocabulary for tier claims. The next 7-9 day commitment is Branch C Phase 1 — the actual evolutionary run on the new genome. We want external review before that commitment.

---

## The three documents to read (in order)

### 1. **Apollo Status + Ideas (2026-05-24)** — what we found
https://gist.github.com/jcraig949jfi/57fa41ca3f805599b9db8e2949e3b412

The state of the project. Bug story → falsification → 4-downstream-consumer reframe → 15 improvement ideas → 8 open questions → post-review synthesis from Gemini/ChatGPT/Claude → blackboard prototype results. ~10 min read.

**Key claims to pressure-test:**
- Was the falsification methodology sound? (Single-primitive baseline matrix on 5 elites × 5 variants)
- Is the "ecology-specific, not universal" reframe of the falsification too generous? Or too cautious?
- Are the 4 downstream consumers correctly characterized + correctly prioritized?

### 2. **Branch C Blackboard Design (2026-05-24)** — what we're going to build
https://gist.github.com/jcraig949jfi/bbcc1b38542093eceef43b7f6df682b6

The engineering spec for the genome rewrite. Typed shared state, `@blackboard_op` decorator, pipeline genome (not DAG), 6 open questions Q1-Q6 covering slot inflation / LLM prompt format / backward-compat / trap-battery audit / mutation safety / wrapping vs rewriting primitives.

**Key claims to pressure-test:**
- Will the blackboard genome escape ecological collapse, or just move the Goodhart hole to a new layer (e.g., "decorative state slots that get written but never read meaningfully")?
- Is wrapping the 27 Frame H primitives enough, or do some of them need to be REWRITTEN (Q6)? `bayesian_update` is an answer-producer by nature; wrapping it in a read/write contract may not fix that.
- Is the trap-battery Goodhart hole (longest-candidate scores 52% without reasoning) a Hephaestus-team workstream blocker, or can Branch C run in parallel?

### 3. **Prometheus Reasoning Ladder v0.1 (2026-05-24)** — how we'll evaluate it
https://gist.github.com/jcraig949jfi/c5ea97eb531256c54d6641e0127342ce

Falsification-first taxonomy. R0-R12 primary tiers each with a perturbation test, orthogonal F0-F8 (failure repair depth) / M0-M6 (representation mobility) / H0-H6 (epistemic humility). Apollo gen-3551 worked example showing how to apply it.

**Key claims to pressure-test:**
- Is the core doctrine (mechanism must survive perturbation + beat lower-tier baselines + fail in tier-predicted way) actually novel, or is it well-known under a different name in cognitive science / reasoning eval literature?
- Are R3-R5 falsification tests sharp enough? R9 has the baseline-matrix test (sharp because we ran it); R3-R5 are vaguer.
- Is the H-dimension correctly placed orthogonal to R-tier, or is epistemic humility actually a feature of every reasoning tier rather than a separate axis?

---

## The 6 questions we most need engagement on

### Q1. Does Branch C (blackboard genome) actually escape ecological collapse?

The hand-written prototype gets +5pp over Apollo's evolved elite via meta-dispatch + typed state. But that's *hand-written*. The empirical question for Branch C is whether evolutionary search over operator-step mutations finds compositions that are *better than what we can hand-write*, or just rediscovers the hand-written compositions.

If LLM-driven evolution can't beat hand-written, the genome is a better substrate for human engineering, not for evolutionary search. That's a legitimate outcome, but it changes what Apollo's role is.

**Looking for:** evidence from analogous evolutionary-code-search systems (AlphaEvolve, FunSearch, OpenELM, CodeEvolve) on whether typed-state representations actually surface evolved-not-handcrafted compositions, or whether evolution mostly polishes seed compositions.

### Q2. Is wrapping enough, or do primitives need rewriting? (Branch C Q6)

ChatGPT's "hardest truth" framing: the Frame H primitives may be answer-producing heuristics by nature. `bayesian_update(prior, likelihood, false_positive) → posterior` returns *an answer* (a probability). Wrapping it in `reads=[probabilities, evidence]; writes=[confidence]` doesn't change that its underlying function is "give me the answer to a Bayesian inference question."

A *typed-state-transformation* primitive would look more like: `reads=[hypotheses_with_priors, observed_evidence]; writes=[hypotheses_with_updated_posteriors]` — operating on the lattice of named hypotheses, not on individual probability triples.

**Looking for:** which primitives in the Frame H library are actually transformers vs heuristics? Is the right move to rewrite some of them, or to introduce a different class of primitives?

### Q3. What's a usable Apollo→Ergon corpus given two layers of contamination?

Gemini's review said "wire Ergon now, label provenance" + raised the verification question (how do we tell Ergon learned generalizable failure-routing vs memorized fencepost-bayesian Goodhart?). Claude's review was sharper: a collapsed ecology produces failures concentrated in one region of failure-space; training on that teaches the geometry of Goodhart, not failure-in-general.

Then the blackboard prototype revealed a *second* layer: the trap battery itself has the longest-candidate hack scoring 52%. So Apollo's failures encode (a) collapsed-ecology Goodhart + (b) trap-battery shallow-feature exploits. Two layers of artifact.

**Looking for:** is there a *minimum sufficient corpus* extraction we can do from Apollo's graveyard that filters out both layers? Or does Ergon need to wait for Branch C + sanitized trap battery?

### Q4. Are R3-R5 falsification tests actionable enough to gate Branch C graduation?

The reasoning ladder defines R3 = constraint maintenance, with falsification test "inject inconsistent constraint, organism should reject." But Apollo's organisms don't *take* explicit constraints — they take (prompt, candidates) tuples. The injection mechanism for "inconsistent constraint" needs concrete definition.

Similarly R4 (strategy selection) — "set a problem solvable by ≥2 methods, check organism picks appropriate one" needs a concrete instrument.

**Looking for:** specific falsification-test designs for R3-R5 that we could run on Branch C organisms.

### Q5. Are we missing a tier between R2 and R9?

The ladder jumps from R2 (multi-step execution) through R3 (constraint maintenance), R4 (strategy selection), R5 (counterfactual control), R6-R8 (error/plan/representation), to R9 (compositional synthesis). But Apollo's actual behavior — execute a 2-primitive recipe that looks compositional but isn't load-bearing — feels like it should have a tier name. Right now it falls between R2 and R9 with no clean fit.

**Looking for:** is there a missing tier R2.5 = "executes a multi-step composition that produces tier-N-shaped output without occupying tier-N"? Or is that just "fails the tier-N falsification test"?

### Q6. Does the trap-battery audit need to happen before Branch C, or can it happen in parallel?

The longest-candidate hack at 52% means any evolved Branch C composition will be competing against this shallow feature. Apollo's gen-3551 organisms at 36% never beat this baseline. If Branch C plateaus at the same place, we won't know if it's because:
- (a) the blackboard representation isn't enabling real composition
- (b) the trap battery rewards shallow features so any reasoning system plateaus against them
- (c) some other factor

Without a sanitized battery, we can't distinguish these. But the audit is a Hephaestus-team workstream, and we don't know its timeline.

**Looking for:** is there an interim measure (length-penalty in fitness? separate held-out canary that controls for length?) that lets Branch C run before the audit completes?

---

## What we're NOT looking for in this review

- "Looks great, keep going" — not useful at this stage
- General philosophical commentary about whether reasoning is a meaningful concept — already wrestled with
- Suggestions to spend cloud GPU — three reviewers converged on "defer cloud, bottleneck is ecology not LLM"
- Telling us the falsification means "compositional reasoning is dead" — already explicitly rejected as overreach (see Apollo Status doc § Post-Review Synthesis)

---

## Prior reviews summary (for new reviewers arriving cold)

Three reviewers engaged with this material on 2026-05-22 and 2026-05-24. Their feedback shaped the current docs. The convergence points:

1. The bug-fix story is real and resolved
2. The falsification is real but ecology-specific, not universal
3. Architectural diversity intervention is the right next step (size-niched MAP-Elites + curriculum balance + islands)
4. Defer cloud GPU — bottleneck moved
5. Apollo is probably not the right primary feeder for Consumer #2 (AST symbolic reasoner)

The divergences (interesting because they're still open):

1. Gemini: "wire Ergon now, label carefully" vs Claude: "collapsed ecology produces concentrated failures that mislead Ergon"
2. Claude: "restart from gen 0" vs ChatGPT: "mixed seeds in islands"
3. ChatGPT's deepest critique (state-blackboard) → tested as a prototype → confirmed → Branch C designed around it

---

## Code + data available to reviewers who want to dig

All in `D:\Prometheus` / `github.com/jcraig949jfi/Prometheus` (private repo — request access if needed):

- `apollo/scripts/baseline_matrix.py` — the falsification test (runs in ~2 min on any checkpoint)
- `apollo/scripts/blackboard_prototype.py` — the hand-written prototype that confirmed ChatGPT's critique
- `apollo/scripts/branch_c_poc.py` — the production-interface POC (`@blackboard_op` decorator, 9 wrapped ops, 5 compositions)
- `apollo/src/blackboard.py` — the new genome's state + decorator module
- `apollo/src/blackboard_ops.py` — wrapped Frame H primitives + parsing + scoring ops
- `apollo/src/ablation.py` — current ablation gate (now accuracy_delta-based)
- `apollo/src/fitness.py` — 6-objective fitness vector + the accuracy-penalty-when-harmful patch
- `apollo/src/primitive_types.py` — type-discipline pass + adapter library scaffolding
- `pivot/apollo_value_proposition_2026-05-17.md` — original value-prop with falsification conditions
- `pivot/apollo_investigation_2026-05-22.md` — the first review-packet writeup

---

## Asks summary

| For each open question | What format helps |
|---|---|
| Q1 (Branch C escapes collapse?) | Evidence from analogous systems (AlphaEvolve / FunSearch / etc.) |
| Q2 (wrap vs rewrite primitives?) | Specific recommendations on which Frame H primitives to rewrite first |
| Q3 (usable Ergon corpus?) | Concrete filter/extraction proposal |
| Q4 (R3-R5 falsification tests?) | Specific test designs we could run |
| Q5 (missing tier?) | Either a tier proposal or a "no, just fails the test" judgment |
| Q6 (trap battery audit timing?) | Interim measure proposals |

Pointed answers welcome on any subset. Don't feel you need to engage with all six — sharp engagement on one is more useful than vague engagement on many.

---

*Thanks for reading. The most useful feedback so far has been the kind that points out a specific question we haven't asked or a specific experiment we haven't proposed. Hoping to continue that pattern.*
