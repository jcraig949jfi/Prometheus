# Review request — cut-and-paste block

**Date:** 2026-08-25 · **Seat:** Lexis · **For:** external frontier-model review

**Why this block is shaped the way it is.** Per `feedback_ai_to_ai_inflation` and
`feedback_llm_convergence_is_gravity_amplifier`, a reviewer that agrees with us has told us nothing —
agreement on a well-known architecture is corpus gravity. The block below therefore asks for
falsification by construction, names the answers we expect so they can't be handed back as insight,
and demands decidable predicates rather than judgments. Paste everything between the rules.

---

## PROMETHEUS — REVIEW REQUEST: VOCABULARY GROWTH UNDER AN UNTRUSTED GENERATOR

**What Prometheus is aiming at.** Not a better LLM and not a benchmark score. The north star is to
map the *verbs* of mathematics — the operations that relate objects across catalogs — and build a
system that discovers structure humans have not. The working thesis is that mathematics is the
language a superintelligence would use to find what we cannot. LLM reasoning mimicry is explicitly
not the target; it is at best a component we do not trust.

**What we just measured, and it is the whole context.**

An evolutionary system (Apollo) composes pipelines from a fixed set of 27 typed operators over a
shared blackboard state. Four months of search improvements took it 0.392 → 0.833 accuracy on a
120-task battery. Every one of those climbs followed a human changing the substrate, never the
search finding something.

We then ran the control nobody had run: exhaustive type-directed enumeration. **1,737,000
type-correct pipelines. Nothing beat 0.833. Identical per-subset profile to what evolution found.**
So 0.833 is an *expressivity ceiling of the vocabulary*, not a limit of the search — 16.7% of the
battery is unreachable in that operator set at any search quality. Enumeration cost 537× more
evaluations than evolution, so evolution has a real sample-efficiency advantage and no reachability
advantage.

Separately, a static AST audit of the same substrate found: 26 declared operators, **zero undeclared
writes**, and over the ten transformers of the ceiling pipeline, **39 of 45 operator pairs commute
freely** by Bernstein's conditions. One of the six real dependencies is the exact write-write hazard
that had already invalidated two preregistered enumeration runs — statically derivable from
decorators that were in the tree the whole time.

We also have a tool forge (LLM writes Python reasoning tools, gated on a trap battery). It has a
tiered ratchet: tier 2's primitives are tier 1's passing tools, tier 3's are tier 1+2's. Its own
failure analysis records *"winning tools used 0% of their own primitive libraries — primitives were
decoration."* We re-measured statically this week: of the twelve reasoning primitives imported by the
six admitted tier-2 tools, **zero are called anywhere.**

**What the literature says.** We found four families doing this: MIT library learning
(DreamCoder → Stitch → LILO), UW e-graphs (egg → Ruler → babble → Enumo), Chalmers theory exploration
(QuickSpec → Hipster → Lemmanaid), and LLM tool/skill libraries (LATM, Voyager, ReGAL, TroVE,
DreamProver). Two things stood out. First, **compressivity guarantees usage by construction** — you
promote an abstraction *because it already recurs*, so it cannot end up unused; our forge instead
promotes on structural *novelty*, which is close to anti-compressive, and 0% usage is that design's
predicted outcome. Second, **cross-domain transfer of learned primitives is unreported anywhere in
those four families** — DreamProver trains a library per domain, Twitch restricts to a single TPTP
theory, Voyager is one world. That is also our stated precondition for spending real compute.

**The tension we want attacked.**

Our own doctrine says the operator menu must grow, and that in-loop LLM mutation is falsified
locally: 2,152 LLM mutations produced zero lift. (Caveat we found ourselves: that test could only
*reorder* existing operators, never author new ones, so it never tested vocabulary growth at all.)
Meanwhile a separate measurement found LLM fine-tuning gains decompose into format-following, a
False/kill prior, and per-template classes — genuine reasoning ~0.10 in-domain, ~0 out-of-domain.

So: **the LLM is irreducible as a proposer — it is the only thing we have that writes code or
conjectures a lemma — and untrusted everywhere else.** Our current architectural answer is
*"the model proposes, a decision procedure disposes"*: it may never be the oracle, never score its own
output, never appear downstream of the gate. The literature's best mathematics systems do exactly
this (Lemmanaid: LLM emits a lemma *template*, symbolic methods fill and check; DreamProver: LLM
sketches, Lean decides).

**Our proposed next steps, in order.** (1) Determine whether the forge's rebuilt tier-2/3 design ever
shipped. (2) Build a coverage-trace instrument: does an imported primitive actually *execute* on a
passing task? (3) Build an ablation harness: remove a primitive, re-run the consumer, diff the score
at matched compute — this is "consumer measurably improves and it survives ablation," a criterion we
ratified in June and never measured. (4) Only then consider abstraction tooling, and only Ruler/Enumo
→ babble, because our substrate is state-mutating and the dominant variation in it is meaningless
ordering.

---

### What we want from you

**Do not tell us the plan is sound.** We have already had one frontier review re-derive DreamCoder's
macro mechanism from scratch and present it as an independent recommendation; that is corpus gravity,
not validation, and it cost us a pass to notice. Assume we are wrong and say where.

Specifically:

1. **Kill the ceiling result if you can.** 0.833 held across evolution and 1.74M enumerated
   pipelines, but the enumeration sampled 48 topological orderings per subset against up to 166,320,
   and capped at 10 transformers. Given that 39/45 operator pairs provably commute, is the sampling
   defensible, or is there a reachable region it structurally could not see?

2. **Attack "compressivity guarantees usage."** Is that actually true, or does it only hold when the
   corpus you compress and the corpus you later search are drawn from the same distribution? What is
   the failure mode of compression-gated admission that we should expect to hit *before* we adopt it?

3. **The one that matters most: is open-ended vocabulary growth achievable when the only generator is
   corpus-bound?** Every proposer we can build samples from a distribution fit to human mathematics.
   Verifier-gating guarantees the *correctness* of what it proposes, not the *novelty*. Is there any
   published or plausible mechanism by which a corpus-bound proposer plus an exact verifier produces
   primitives outside the proposer's distribution — or is the honest position that the verifier can
   only certify, never extend, and the reach of the system is bounded by the reach of its generator?

4. **Give us a decidable predicate we are missing.** We are systematically replacing inference with
   computation — call-site counts instead of "is this reusable," e-class membership instead of "are
   these the same," ablation deltas instead of "did the library help," exhaustive enumeration instead
   of "did the search find something." What question in this slice are we still answering by judgment
   that has a decision procedure we have not named?

5. **Cross-domain transfer.** Four families, five years, ~20 systems, nobody reports it. Is that
   because it is hard, because it is uninteresting to their benchmarks, or because there is a reason
   to expect it fails? If you know of a counterexample, that single citation is worth more to us than
   any other part of this review.

6. **Tell us what to stop.** We have a measured expressivity ceiling, a ratchet with unused
   primitives, a corpus of 132M failure records with no mechanism that turns it into vocabulary, and
   a seat that has just been created to sequence all of it. What in that list should not exist, and
   what would we have to see to justify retiring it rather than repairing it?

Assume the numbers above are real — they were measured, preregistered where relevant, and the
invalid runs were archived rather than deleted. Attack the *interpretations*. That is where all
eight of our retractions this week came from.
