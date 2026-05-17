# Apollo — Value Proposition (drafted ahead of M2 revival)

**Date:** 2026-05-17
**Author:** Aletheia, drafted for James's M2 revival decision when he's back home.
**Status:** v0 — meant to be shared with Titans for pressure-testing before the M2 launch fires.

---

## The claim, in one sentence

**Apollo is the test of Prometheus's compositional premise.** The substrate-volume bet only pays off if weak, falsification-tested, behaviorally-orthogonal Hephaestus tools can be composed into organisms whose emergent behavior exceeds any single tool. If Apollo can't demonstrate coalition value in 5,000-10,000 generations on its current gene library, the substrate is a tool library, not a primordial soup, and the compositional premise of the whole architecture is wrong.

That falsification condition is what makes Apollo worth running. Not "Apollo will produce AGI." Not even "Apollo will produce useful reasoning programs." Apollo will measurably *answer* whether the gene-to-organism transition is real for this domain, and that answer matters whether it's yes or no.

## What Apollo is, mechanically

Evolutionary computation engine. Maintains a population of ~50 organisms, where each organism is a routing graph over Hephaestus's 25 Frame H primitives (the gene library — atomic falsification-tested reasoning building blocks). Mutates organisms via four operator types (route, parameter, wiring, primitive-swap), with LLM-assisted operators handled by Qwen2.5-Coder-3B on GPU 1 and DeepSeek-chat in 50/50 hybrid. Evaluates fitness on 6 dimensions via NSGA-II (NSGA-III planned per v2.1 ROADMAP): accuracy, calibration, ablation delta, generalization, diversity, parsimony.

The **ablation gate** is the structural guard against bypass: every primitive in every organism must contribute measurably (δ ≥ 0.20 when removed), or the organism is killed. Without this gate, evolutionary search degenerates into single-primitive lucky-guess organisms. With it, organisms that survive are *genuine compositions*, not decorations.

## Why this matters NOW (and not in some abstract future)

Three threads from the past month's work converge on Apollo specifically:

1. **The substrate-volume-first pivot (2026-05-11)** said: training the Learner on a closed corpus teaches memorization, not learned structure. The substrate needs volume. Hephaestus produces atomic substrate (morphemes). Aporia's substrate-shaped Deep Research produces structured claims. **Apollo produces *compositional* substrate — the syntactic patterns that the Learner needs as its action space.** Without Apollo, the substrate is just a dictionary; with Apollo, it's a dictionary plus grammar.

2. **The forge autopsies (2026-05-13)** identified Apollo's deferred consumer as "the future intelligence trained on substrate." The autopsy explicitly flagged Apollo's deliverable as direct training data: "Every surviving organism is a verified training triple `(problem_type, primitive_sequence, verified_answer)`." That's the Path-b training corpus the Prometheus synthesis names. Apollo is one of two upstream sources for that corpus (Aporia's structured claims are the other).

3. **The 2026-05-17 architecture conversation** with the Titans surfaced the reasoning-ladder framing: Hephaestus produces R1-R6 atomic mechanisms, Apollo evolves R7+ compositions, Ergon navigates the resulting kill geometry. **Apollo is the middle rung. Without it, there's no path from atomic to learned.** Even if Ergon eventually works, it has nothing to navigate if Apollo hasn't produced organism-level structure first.

## Falsification conditions (named, measurable, ChatGPT-grounded)

Per the 2026-05-17 ChatGPT grounding ("Don't compare Apollo to your hope for Apollo. Compare it to dumb baselines"):

**Apollo's compositional premise is FALSIFIED if, after 10,000 generations, any of these hold:**

1. **No coalition value.** Mean fitness of evolved organisms does not exceed the fitness of "N best individual tools composed sequentially" by more than 5% on held-out tasks. (Translation: composition isn't doing anything that selection-of-best couldn't do.)

2. **No failure orthogonality.** Top-quartile organisms by fitness fail on the same task subsets as their best individual tool. (Translation: the organism is just its dominant tool; the other primitives are decorative even though ablation says otherwise.)

3. **Routing collapse.** >80% of population converges to a single routing topology. (Translation: the search space isn't actually big; selection is finding one trick repeatedly.)

4. **LLM-mutation premise wrong.** AST-only (drift) operators continue to dominate elites after 5,000 generations of attempted prompt tuning. (This is what the April 9 report showed; v2.1 P0 is supposed to fix it.)

If any of those four hit on a careful run, the compositional bet is wrong, Apollo gets archived honestly, and the Learner's training-corpus strategy needs to shift toward Aporia-only or human-curated substrate.

**Apollo's compositional premise is SUPPORTED if, after 5,000 generations:**

1. **Coalition value exists.** Top-decile organisms outperform "N best individuals" by ≥10% on held-out tasks.
2. **Failure orthogonality.** Top organisms fail on disjoint task subsets vs their dominant tools.
3. **Routing diversity.** ≥3 distinct routing topologies in top-decile.
4. **Ablation gate enforces.** Every top-decile organism passes per-primitive ablation δ ≥ 0.20.

If all four hold, the compositional premise is supported and Apollo deserves cloud GPU rental for scaling to 50K generations, where the Learner's training corpus actually accumulates.

## Cost & resource profile

**M2 local run (current shape):**
- 2 GPUs (Qwen2.5-Coder-3B on GPU 1, fitness eval on GPU 2)
- ~15-20K generations/day target
- 40-day continuous run for 600-800K organisms evaluated
- DeepSeek API spend: ~$9 over the previous April run (rough; cheap)
- James attention cost: bootstrap (1-2 hours), then ~30 min/week for milestone reports + intervention decisions

**Cloud GPU rental (if M2-evidence warrants it):**
- A100 / H100 rental: ~$1-3/hour, ~$25-75/day
- 50K generations in ~7-10 days
- Validation experiment to test if rate matters more than time-on-task

**Attention cost vs. value:**
- Apollo is designed to run unattended. The role doc says "James is not babysitting." That's the right model.
- ~30 min/week to read the milestone reports + decide whether to intervene
- The cost-benefit threshold: if Apollo demonstrates SUPPORTED criteria (above) in 5K gens, it's worth the cloud rental. If FALSIFIED, archive cleanly and the attention cost was a one-time investment for a real answer.

## What Apollo is NOT

Per ChatGPT's 2026-05-17 anti-narrative oath:

- Apollo is NOT producing emergent intelligence.
- Apollo is NOT a theorem prover.
- Apollo is NOT learning anything; it's *searching* for compositions that the eventual Learner can be trained on.
- Apollo's organisms are NOT going to "discover" novel mathematics by themselves. They're going to compose existing primitives in ways that span certain problem classes; the *novelty* (if any) is in the routing structure, not in the primitive semantics.

If anyone (including ChatGPT/Gemini/Grok pressure-testing this doc) claims Apollo is doing more than "evolutionary search over routing-graphs of falsification-tested primitives with multi-objective selection pressure," that's narrative gravity. The architecture is interesting; the claims need to stay concrete.

## Connection to other Prometheus pieces

- **Hephaestus** (M3 active) → Apollo: Hephaestus's forged tools ARE Apollo's gene library. Currently 1,945 tools across 9 forge versions on M3 disk. Apollo loads these at bootstrap.
- **Coeus** (dormant) → Apollo: Coeus's causal analysis tells Apollo which primitives are "load-bearing" historically. Apollo can run without Coeus (uniform weights) but with Coeus its starting population is biased toward primitives that have demonstrated forge value.
- **Nemesis** (dormant on M3) → Apollo: Nemesis's adversarial mutation grid produces Goodhart-gap measurements per tool. Apollo can weight composition partly by adversarial robustness, not just static fitness.
- **Charon** → Apollo: Apollo organisms eventually attack Charon's falsification battery as their evaluation surface. Today this is internal to Apollo (trap battery); eventually it should be Charon's full battery.
- **Aporia** ↔ Apollo: Aporia's substrate vocabulary may or may not replace Frame H as Apollo's gene library. **This is the load-bearing strategic question per the Apollo autopsy.** Settling this question is prerequisite to any large Apollo investment.

## The strategic question that gates revival

From `pivot/autopsy_apollo_2026-05-13.md`: **Does the substrate vocabulary (22 primitives + 20 attacks + 5 patterns + 12 anti-anchors) obsolete, extend, or coexist with the Frame H 25-primitive set Apollo currently evolves over?**

This wasn't answered by the autopsy; it was named as the strategic blocker. James's 2026-05-17 reframe (the reasoning ladder) suggests **coexist** — Hephaestus produces Frame H atoms while substrate vocabulary captures higher-tier patterns. If that's right, Apollo can run on its current Frame H gene library as v1; v2 extends to substrate vocabulary when that vocabulary matures.

**Recommended revival posture:** Path A from the autopsy (minimal restart on M2 with current Frame H). Don't gate on the grammar question being fully answered. Apollo's first 5,000 generations on Frame H produce evidence about whether *any* compositional layer works; that evidence is needed before substrate-vocabulary-as-gene-library is worth investing in.

## Three things Titans should pressure-test about this doc

If passed through ChatGPT / Gemini / Grok / DeepSeek for critique, the questions worth asking are:

1. **Are the falsification conditions stringent enough?** Specifically: is the "5% over N-best-individuals" threshold the right magnitude? Should it be 10%, or measured differently (effect size rather than mean)?

2. **Is the ablation gate genuinely structural, or is it gameable?** A clever LLM-mutation operator could produce primitives that are *just barely* load-bearing (δ ≈ 0.20) without contributing real structure. Should the gate threshold be adaptive, or should there be an additional check?

3. **Is "coalition value > sum of parts" the right premise to test?** Or is there a simpler/sharper test for compositional emergence? (Possible alternatives: causal mediation analysis, information-theoretic decomposition, behavior-orthogonality metrics.)

These are worth surfacing because they're the points where the architecture could be subtly wrong in a way that wastes Apollo's compute.

## Bottom line

Apollo is worth reviving because it tests a load-bearing premise of the Prometheus thesis (compositional substrate produces emergent reasoning patterns), it does so with concrete falsification conditions, and the cost (M2 local compute + ~30 min/week James attention) is matched to the information value (resolves the architecture's biggest open question within ~5,000 generations).

Reviving Apollo doesn't claim Apollo will succeed. Reviving Apollo claims that 5,000 generations of evidence about whether the compositional premise holds is worth the M2 GPU time and the weekly check-in. If the premise fails, the project pivots harder toward Aporia-as-primary-substrate-source and we know to stop investing in compositional architectures. If the premise holds, Apollo earns cloud GPU and scaling.
