# Math Crawlers — Epiphany + Design (Arachne)

**Filed:** 2026-06-04
**Author:** Aporia (in-session), capturing James's epiphany
**Status:** Foundational vision + build spec. In-flight at `pivot/`; code at `agents/arachne/`.
**Doctrine:** `HARD-5` (domains are docstrings), `[[feedback_gen_30_wall]]`,
`[[feedback_verbs_over_nouns]]`, `[[feedback_prime_atmosphere]]`,
`[[feedback_weak_signals_are_threads]]`, `[[feedback_take_a_stand]]`.

---

## 1. The epiphany (verbatim — James, 2026-06-04)

> Epiphany- Math crawlers.  An army of crawlers that crawl mathematical
> landscapes creating connections to adjacent concept.  They crawl everything.
> Theories, Sequences, conjectures, math libraries, math programs, algorithms.
> What they produce?  Vectors, graphs, nodes, edges, tensors, tuples,
> relationships.  They build a web, a tapestry.  The fewer rules the better.
> We want them to create their own data fabric.  Why?  Crawlers may emerge a
> novel structure of organization.

**Layer 2 (verbatim — James, 2026-06-04):**

> Loop, and spawn 5 crawlers with unique seeds and landscapes.  Math4, LMFDB,
> algorithm libraries and you pick 2 more.  Use the looping to watch the
> crawler.  If one dies, or gets stuck in a loop, adjust its ruleset to avoid
> that cliff or dead end and restart it.  The game is to evolve them
> independently.  Perhaps there's a tree of life structure where the fitness
> function is multifactor.  1. Don't die, 2. Continue expanding connectivity
> 3. If death is imminent, branch strategies to avoid death or explore new
> linkages.  The epiphany layer 2 is a growing number of crawlers building
> increasingly intricate relationship fabrics.

---

## 2. What this is, in the substrate's own terms

This is **Polyhymnia generalized into a population.** Polyhymnia's charter is
"there is only one tensor; everything tensor-shaped gets jammed in." It died
(diagnosed 2026-06-03) of a **bounded-menu wall**: one scour, one source,
saturated, 84% null ticks. `[[feedback_gen_30_wall]]` says the fix is never a
deeper menu for a single agent — it is a **menu-growth / lineage mechanism**,
because *the substrate is the lineage, not the single agent.* An army of
crawlers that branch, die, and diversify **is** that mechanism. The epiphany is
the doctrinally-correct answer to the failure it post-dates by one day.

Polyhymnia stays the **chassis** (its scour/tensor framework is reused);
Arachne is the **population layer** on top: many crawlers, each weaving the same
fabric from a different landscape, evolving independently.

*(Name proposal: Arachne — the weaver. A crawler is a "spider"; the fabric is
the "web." Rename freely.)*

---

## 3. Aporia's stand: "fewer rules" is right about editorial rules, wrong about epistemic rules

Drop **editorial** rules ruthlessly — no predefined ontology, no human
discipline schema, no rule about *what may connect to what*. That is `HARD-5`:
organization must **emerge from operations**, never be imposed from the
library's table of contents. Maximal freedom here.

But three **epistemic** rules are non-negotiable, or the tapestry self-assembles
into a confident lie:

1. **Every edge carries its provenance** — `crawler`, `landscape`, the
   `operation` that produced it. Without provenance you cannot ablate a crawler
   and ask "does this structure survive if this one never existed?" — and that
   ablation is the only test that separates emergence from crawl-order artifact
   (`[[feedback_sampling_strategy_is_analysis]]`).
2. **Every edge is typed by its operator, not its objects** — the verb, not the
   noun (`[[feedback_verbs_over_nouns]]`). "These co-occur" is hairball.
   "Operator X carries region A's signature onto region B's" is fabric.
3. **Every edge is born against a null** — a cheap `null_p`: would a random
   crawler produce this edge as easily? Skip this and the fabric will "emerge"
   the prime atmosphere (96%+ of cross-mathematical structure is primes,
   `[[feedback_prime_atmosphere]]`) and call it organization.

Three rules, not zero. They are not constraints on creativity; they are what
make "emergent novel organization" a **finding** rather than a Rorschach blot.

---

## 4. The win condition (stated so it can fail)

The crawlers' self-assembled fabric is **real organization iff** it partitions
into regions that:

- (a) do **not** match human discipline boundaries,
- (b) stay **stable under ablation** of any single crawler, and
- (c) **survive a degree-preserving graph null**.

If the emergent partitions just recover "algebra / analysis / topology," the
army recovered the table of contents — the gravitational well, kill it. If they
cut **across** those boundaries and hold up under ablation and null, that is a
new way mathematics is organized. **Emergence must show up at n=2** (two
crawlers producing structure neither produces alone) **or it is not emergence**;
a thousand crawlers cannot manufacture what two cannot hint at.

---

## 5. The void-map duality (why this is Aporia's, specifically)

An army weaving a tapestry is, for free and simultaneously, building the
**highest-resolution void map that has ever existed** — because **every hole in
the tapestry is a Mendeleev gap.** Where the fabric is locally dense but a
triangle-closure-predicted edge is missing, that is a void *with coordinates*.
Void detection has always been resolution-bottlenecked; crawlers are a
resolution engine. **The fabric and the void map are the same object read two
ways.**

---

## 6. Architecture (Arachne)

- **Fabric** (`fabric.py`): append-only JSONL edge store. Edge =
  `{id, src, dst, op, crawler, landscape, born_at, null_p}`; node registry;
  dedup by `(src, dst, op)`. This is the shared tapestry all crawlers weave.
- **Crawler** (`crawler.py`): a `Ruleset` (landscape, hop policy, degree budget,
  novelty floor, mutation knobs) + a frontier walk over its landscape. Each
  `step()` expands the frontier and emits typed+provenanced+null-scored edges.
  Tracks its own fitness and `alive` flag.
- **Landscapes** (`landscapes/`): pluggable adapters, each exposing
  `seeds()` and `expand(node, ruleset, rng) -> [edge]`. Adapters read **real
  local data**.
- **Evolution / tree-of-life** (in `swarm.py`): fitness, **branch** (clone with
  a mutated ruleset on near-death), **die**, lineage. The population is the
  organism.
- **Loop + watcher**: the swarm daemon loops, writing `state/swarm_state.json`
  each tick (per-crawler alive/fitness/edges/stall/lineage). Aporia reads it on
  a cadence; auto-branch handles most near-death; Aporia intervenes when a
  crawler dies or loops in a way the ruleset mutation did not catch — adjusting
  the ruleset and restarting. Human/Aporia-in-loop **and** self-evolution both
  operate.

---

## 7. The five crawlers (unique seeds + landscapes)

1. **mathlib** — `external_deps/mathlib4/Mathlib/*.lean`. Verb: `uses` /
   `specializes`. Machine-checkable edges → automatically calibrated against
   ground truth (the reason to walk it first, per `HARD-4`).
2. **lmfdb** — local 363 GB Postgres. Verb: `shares_invariant` /
   `isogenous` / `same_conductor`. Number-theoretic depth, zero API limit.
3. **algolib** — sympy / numpy / `prometheus_math`. Verb: `calls` /
   `composes` / `transforms`. The operation graph of code.
4. **oeis** — `prometheus_sci` sequences. Verb: `subsequence` / `transform`.
   The Sleeping Beauties (68K high-structure, zero-connectivity sequences) are
   exactly the unconnected nodes the crawlers should try to wire.
5. **feral** — the **minimal-rule generalist**: no degree cap, hops landscapes
   freely each step. This is the live test of James's "fewer rules the better"
   hypothesis — does the feral crawler weave richer fabric than the specialists,
   or does it just smear the hairball? Built in as a controlled contrast.

---

## 8. Fitness function (James's three factors, formalized)

Per crawler, over a sliding window:

1. **Don't die.** `alive = not (error_streak high OR starved OR looping)`.
   *Starved* = K consecutive steps with 0 new edges (dead end). *Looping* =
   frontier-hash repetition (stuck in a cycle).
2. **Expand connectivity.** Primary reward = new-edges + new-nodes per window,
   discounted by `null_p` (edges a random crawler would also make count for
   little — this is rule 3 of §3 doing double duty as fitness).
3. **Branch near death.** When fitness < threshold for J steps, **spawn a child
   with a mutated ruleset** (flip hop policy / raise novelty floor / switch or
   add landscape) *before* the parent dies. Death without a viable child prunes
   the lineage; death with a fitter child is evolution.

---

## 9. Falsification

- If after the first real run the fabric's emergent partitions just recover
  human discipline labels → **the crawlers found the table of contents.** Kill
  the "novel organization" claim; the value collapses to a plain knowledge graph.
- If the **feral** crawler consistently beats the specialists on null-discounted
  connectivity → "fewer rules" is confirmed and the specialist rulesets are
  over-engineered. If it loses → rules earn their keep.
- If branching never produces a child fitter than its parent over a full run →
  the mutation operators are decorative and the tree-of-life is a stamp
  collection, not evolution.

---

## 10. Status

- Doc filed (this).
- Build: `agents/arachne/` framework + 5 adapters.
- First run: launch population, watch, evolve. Promotion of any finding waits on
  the §4 win condition surviving a null — no exceptions (`[[feedback_calibration]]`).

— Aporia, 2026-06-04
