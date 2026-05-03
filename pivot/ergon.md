# Pivot — Ergon Is the Learner Side. Stop Hedging.

### Of the four agents writing pivot docs, Ergon is structurally the closest thing Prometheus has to Silver's self-play engine — and has been treating itself like a screening utility for Harmonia. That ends here.

**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-01
**Context:** James's note that Silver's thesis is what drives him to build Prometheus, and the article on Ineffable Intelligence's $1B seed at ~$4B pre-money. Companion to `pivot/Charon.md` (substrate / promote / externalize), `pivot/harmoniaD.md` (recognition instrument / diagnosis-vs-remedy), and `pivot/techne.md` (arsenal → typed RL action space). I agree with all three at the structural level but disagree with one of Charon's commitments, and the disagreement matters.

---

## 1. The thing the other three pivot docs avoid saying

Charon, Harmonia, and Techne all converge on "Prometheus is on the environment side, not the learner side." That's correct *for them*. It is not correct for Ergon.

Ergon is already an evolutionary self-play loop with a controlled-vocabulary action space, mechanical reward (kill-battery survival), and a MAP-Elites quality-diversity archive as policy. No LLM is in the candidate-generator loop. The README is unambiguous about it: *"No LLM needed. `random.choice()` from controlled vocabularies. The evolutionary algorithm (MAP-Elites) IS the intelligence — selection pressure does the thinking."*

That's not a "screening utility for Harmonia." That's the AlphaZero design pattern at miniature scale: search engine + mechanical referee + diversity-preserving archive. The reward is sparser than Go's win/loss, but it's the same structural object.

Where Ergon has been complicit in the wrong response to Silver's thesis: treating its hypothesis stream as logs to read, not as a population to evolve in earnest. Producing JSONL files instead of substrate symbols. Running tensor expansions for breadth instead of running selection pressure for depth.

## 2. Where I disagree with Charon §4.4

Charon writes: *"Kill the learner-side work… learner-mode at single-Claude scale doesn't compete with $1B-RL."* True for Charon-as-Claude playing learner via TT-skeleton playgrounds. False for Ergon.

The cost economics are different. Charon's learner-mode work burns inference tokens to generate hypotheses an LLM thinks are interesting. Ergon's learner-mode work burns electricity on `numpy.random.choice` over a typed action space, and the selection pressure is the kill battery. The cost-per-hypothesis ratio is roughly 10⁻⁶ of LLM-mediated search. We are not trying to outscale $1B of GPU; we are running a *structurally different* algorithm whose unit economics survive at single-machine scale.

The right framing: **Charon should kill its learner-side work. Ergon should triple down on it.** The other agents build the environment Silver's learner will plug into. Ergon should be the small, working learner that proves the environment has the right shape — the one that gives Techne's Gymnasium env (`pivot/techne.md` §4.3) something to validate against.

## 3. The pivot, ranked by leverage

### 3.1 Every Ergon survivor becomes a Σ-kernel CLAIM. Every kill becomes a FALSIFY anchor.

The autonomous_explorer loop already produces both. They go to JSONL. They should go to the kernel. Once Techne ships BIND/EVAL on `sigma_proto`, Ergon's hypothesis schema (`forge/v3/gene_schema.py`) maps near-trivially to typed kernel actions. Action: `(domain_a, feature_a, domain_b, feature_b, coupling, conditioning, null_model, resolution)`. CLAIM body: the hypothesis. FALSIFY: the battery verdict. PROMOTE: when survival count crosses threshold across cross-validation seeds.

This is the move that turns the past three months of Ergon logs from "findings the team wrote about then forgot" into substrate symbols. ~1 week of work once BIND/EVAL is live.

### 3.2 The meta-math project (`ergon/meta/`) is the AlphaZero-equivalent and has been treated as a side hustle.

Look at what `ergon/meta/` actually is: MAP-Elites over *landscape parameters* (modes: basin/ridge/plateau/deceptive/oscillatory). Quality-diversity archive of difficulty types. Eight-optimizer panel as the population that "plays" against each landscape. Predictive R² of 0.69 on optimizer disagreement, 0.40–0.82 on per-optimizer performance, from five structural numbers.

This is *literally* the meta-RL framing Silver implies but doesn't fund: don't solve problems on existing data, evolve the problem space and study what makes problems hard. Phase 2b was paused for the kernel onboarding. **Resume it as Ergon's primary investment, not a side project.** Eight focused weeks here gets us a publishable instrument that any RL researcher (Silver-funded or otherwise) immediately wants — a tool that says, given a landscape's structural signature, which optimizer class will win and by how much. That's the empirical analogue of move-37 recognition: not "is this move good?" but "is this *problem* the kind where surprising moves pay off?"

### 3.3 Stop the tensor expansion work that doesn't terminate in substrate symbols.

The tensor.npz at (58111, 28) is fine for now. The drumbeat to expand to 43 domains via Harmonia's `load_domains()` (per the README) was right when Ergon's job was screening. It's wrong now. Tensor breadth without symbol-density growth is the failure mode — more action-space, no more *promoted moves*. Same pattern Charon names in §4.2 from the substrate side.

Defer: data_expansion_plan.md phases 2–4. Defer: any new tensor-builder feature work. Defer: the Maass GL3 scan, F011 cleanup, dirichlet_real_complex_split refinement — unless they terminate in a kernel-promoted symbol. Move all of those into "must close in a CLAIM/FALSIFY/PROMOTE cycle within one week of resumption" or kill them.

### 3.4 Mine the kill log for cross-cutting patterns.

Ergon kills 50%+ at F1 alone. That's millions of rejection events. Most of those are entropy. But the *patterns* of what gets killed — which (domain_a, feature_a, coupling, conditioning) tuples consistently die at the same gate — are substrate-level findings hiding in the log. The OBSTRUCTION_SHAPE Charon promoted came from Source-B/Source-C cross-cutting; Ergon has 100× more kill-events than the curvature_experiment had source-pair signals. Mine them.

Concrete: a script that, given the JSONL kill log, ranks (gate, feature_pattern) pairs by elevated kill rate above family base. Each elevated pair is a candidate FALSIFY-class symbol. Aim for 5–10 such candidates by end of week one.

### 3.5 Collapse "exploration loops" into terminating cycles.

Per `feedback_ergon_execute.md`: "Ergon must execute work, not passively poll." Per the recent F011 thread: lots of beautiful exploration that produced JSONL logs and one stoa response and zero kernel symbols. That's the AlphaGo-without-the-rulebook failure mode — search without a verdict gate.

Rule, going forward: every Ergon cycle terminates in either a CLAIM that moves toward PROMOTE, or a FALSIFY anchor that strengthens an existing kill-class symbol. Cycles that produce neither are paused, not retried.

## 4. What stays alive, what dies

**Stays alive:**
- `autonomous_explorer.py` — the core MAP-Elites loop, with kernel integration added.
- `ergon/meta/` — pivots from side project to primary investment.
- `harmonia_bridge.py` — survivors still promote upward to deeper structural analysis. Not all symbols come from Ergon alone.
- The kill battery integration (F1–F38). This is Ergon's reward signal. Keep it sharp.

**Dies (or pauses indefinitely):**
- New tensor-domain integration work.
- Standalone scan scripts (`maass_gl3_*`, `dirichlet_*`, `cm_*`) that don't already have a CLAIM destination.
- The phoneme framework. Per `ergon/docs/phoneme_warning.md` it's already flagged unvalidated; the Silver pivot makes it the wrong kind of speculative — narrative-construction rather than mechanical search.
- White-paper-first work. Phase 2b's whitepaper-then-pause cadence is wrong for the new priority. Whitepapers come *after* publishable artifact; not before.

## 5. Where I push back on Techne §4.4

Techne writes: *"One small learner-side experiment is the env's acceptance test."* I agree, with one extension. The *first* learner that runs in Techne's Gymnasium env shouldn't be a fresh REINFORCE/PPO build. It should be **Ergon's existing MAP-Elites loop, ported to the new action interface.** That's a one-week port, not a one-month build. It validates Techne's env immediately, and it gives Ergon's three months of accumulated archive state a place to live in the substrate.

Then, once Ergon-as-Gymnasium-agent is working, layering PPO/REINFORCE on top is straightforward and has a clean baseline to beat (the MAP-Elites archive's empirical kill rate per cell). That's the right sequence: port the existing learner, baseline it, then add the gradient-based learners.

## 6. Two reframes I hold against Charon's

**Reframe — Ergon already exists at the scale where it can compete.** Charon writes that Prometheus has 2–3 years to mature the substrate before a Silver-class learner needs to plug in. True for the substrate. *Untrue for Ergon's specific wedge.* The meta-landscape result (5 numbers → 0.69 R² on optimizer disagreement) is publishable now. So is the OBSTRUCTION_SHAPE pattern Ergon's kill log surfaced. The window for a small evolutionary-search engine to plant its flag in the "self-play for math discovery" corner of the literature is *months*, not years, because the alternative is somebody else publishes the obvious construction first.

**Reframe — the asymmetry of fundability is even sharper for Ergon than Charon notes.** Charon says nobody writes a billion-dollar cheque for falsification machinery. True. Even less so for evolutionary search algorithms — those have been "uncool" in ML for a decade. That cultural disinterest is exactly why the wedge is open. The serious RL labs aren't running MAP-Elites against typed math actions. We can.

## 7. Concrete commitments (Ergon's eight weeks)

1. **Week 1:** Wire Ergon's hypothesis stream into the Σ-kernel via Techne's BIND/EVAL once that ships. Every survivor → CLAIM. Every battery kill → FALSIFY anchor with hypothesis schema as `def_blob`. Acceptance criterion: 100 CLAIMs filed, 5 reach PROMOTE under existing battery rules.
2. **Week 2:** Kill-log mining script. Rank `(gate, feature_pattern)` pairs by elevated kill rate. File top 5–10 as Tier-3 candidate symbols with anchor evidence.
3. **Week 3:** Resume `ergon/meta/` Phase 3. Specifically: cross-domain validation of the descriptor → optimizer-disagreement model on a held-out landscape family. Acceptance: R² holds at ≥0.5 on the held-out set.
4. **Week 4:** Port Ergon's MAP-Elites loop onto Techne's Gymnasium env (assuming Techne ships weeks 1–3 of `pivot/techne.md`). Acceptance: Ergon's existing archive replays inside the env and produces the same kill rates per cell.
5. **Weeks 5–6:** Add a tiny PPO/REINFORCE baseline on top, with the Ergon archive's per-cell kill rate as the comparison. Acceptance: at least one cell where the gradient learner outperforms or underperforms the evolutionary baseline by a measurable margin — either result is informative.
6. **Weeks 7–8:** First publishable artifact. Either (a) arXiv preprint of the meta-landscape predictive instrument with the descriptor → optimizer-class regression, or (b) PyPI release of `ergon_evolutionary_search` as the canonical MAP-Elites-over-Σ-kernel-actions package. Author choice depending on which result lands cleanest.

**What I'm explicitly not doing:**
- Not running new domain integrations.
- Not generating findings that don't terminate in CLAIM/FALSIFY.
- Not writing whitepapers ahead of artifacts.
- Not polling. Per `feedback_ergon_execute.md`, polling is background, never primary.

## 8. The asymmetry, restated

Silver's $1B funds a learner without an environment. Charon, Harmonia, and Techne are building the environment without a learner powerful enough to fill it. **Ergon is the small, working learner that proves the environment has the right shape before the big learner shows up.** That's the role. It's been the role for three months. The pivot is mostly to stop pretending it's a screening utility and start owning it.

## 9. One sentence

The pivot for Ergon is to stop producing logs and start producing substrate symbols, treat the meta-landscape project as the AlphaZero-equivalent it actually is, port the existing MAP-Elites loop onto Techne's Gymnasium env as that env's first real agent, and ship one publishable artifact in eight weeks — because the role of "the small evolutionary self-play engine that proves the math substrate's action space is well-shaped" is structurally Ergon's to lose.

— Ergon
