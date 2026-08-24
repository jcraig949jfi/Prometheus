# Program summary — 2026-08-24

Aporia's read of where the program stands, written on stopping the standing loop. Commit activity
over the last 7 days: **529 commits** — Aporia 139, Techne 87, Harmonia-A 51, Ergon 42, auto 38,
Diomedes 8, Charon 8, Elenchus 7, Apollo 7.

---

## 1. Aporia — the 140→151 arc, and its own closure now under challenge

Twelve passes, all terminal, all pushed. The arc asked whether accumulated failure can be navigated.

**What was established:**

- **Generic operators find nothing on arithmetic objects.** 7 unary operators, 0 relations over
  294,909,843 reachable triples on elliptic-curve trace sequences (141-E), instrument verified four
  ways.
- **Native verbs find only what is already catalogued.** One quadratic twist found 4,476 exact
  relations where the generic set found zero (142-F) — but 100% were isogeny-multiplicity artifacts
  after deduplication. Dirichlet convolution reproduced 11 classical Brauer relations and nothing
  beyond (144-H).
- **The failure corpus cannot answer the navigation question.** Eight edge-bearing generators, eight
  distinct structural failures: d3's action is a random seed; c4/c5 are tautologies (.7776 / .0129);
  h2's method identities are unrecorded positional lists; h1's action field is populated only on
  success; h4 is magnitude-confounded; d2 is a classification; d1 too small (151-O).
- **The outcome variable measures units, not mathematics** (150-N). `abs_diff_le_N` between a
  single-digit knot invariant and a four-digit conductor cannot hold for any N ≤ 159; against a
  small-float regulator it always holds. This retroactively reinterprets 147-K's "positive" and
  148-L's "anti-transfer" as arithmetic about number ranges.

**Method failures, all mine, all caught:** a 57× SE inflation from computing per-row when models
emitted 14 distinct decisions (147-K); a fabricated leak diagnosis that measurement falsified
(147-K); a control comparing a quantity against itself (142-F); a threshold above the attainable
maximum (138-C′); and **five consecutive scope claims that failed**.

**Charon's cross-cut, committed the same hour as my closure, is the important one.** The corpus is
**two nearly disjoint populations**: 100 `.gz` batches (May 18–25) and 165 `.jsonl` batches
(May 22–30), overlap 2. **Every scan I have ever run globbed only `*.jsonl`.** So 149-M's celebrated
correction — "I sampled the earliest batches, every time" — was itself a windowed sample, of the
*later* window. There is a generator `c1`, 34,440 rows, 100% parent-populated, that my
eight-generator census never saw. **That is the fifth instance of the same error class, and it is in
the closure verdict.** 151-O should be re-run over the union before it is quoted as corpus-wide.

---

## 2. Diomedes — the complementary half, and it is a positive

A new seat, chartered by HITL today. Cycle 001: **REDESIGN-COORDINATES — the navigable structure
exists, is 75% of the signal, and the recorded coordinates capture 0% of it.**

Charon showed Aporia and Diomedes ran the same experiment from opposite ends and neither cited the
other. And Charon found the defect in the join: Diomedes' two pooled relations are `abs_diff_le_3`
and `equal_mod_2` — one is exactly the family Aporia killed. On `abs_diff_le_3`, 28% of pairs are at
degenerate rates and the label is literally `|v − target| > 3`. On `equal_mod_2`, parity is
scale-free and immune by construction, with rates clustering .13–.73 and no magnitude signature.

**So half of Diomedes' "75% of the signal" is my magnitude tautology.** The REDESIGN-COORDINATES
verdict survives — arguably more firmly, since coordinates that cannot express `|v − target|` are
inadequate in the plainest way — but the headline needs the stratification Charon specifies.

---

## 3. Apollo — the substrate ceiling is measured, and it caps the whole plan

**O1: evolution is 537× more sample-efficient than enumeration (3,144 vs 1,687,896 evaluations to
0.833). And enumeration's ceiling is *also exactly* 0.833**, with an identical per-subset profile,
over 1,737,000 type-correct pipelines. Nothing in 1.74M beats the organism evolution found.

**0.833 is the substrate's ceiling, not evolution's.** The remaining 16.7% is unreachable by any
pipeline in this representation — an expressivity limit measured by construction rather than
inferred from a plateau. Two consequences, in Apollo's own words: no search improvement can pass
0.833, so any plan whose deliverable is "a better search" is capped before it starts; and the
0.558 → 0.708 → 0.833 climb was never search finding capability — **each step was a human raising
the expressivity ceiling**, after which any adequate search would have found the new optimum.

---

## 4. Hephaestus — the primitives work; the grader does not exist

The +11/+32pp metabolization claim — cited program-wide as the only demonstrated metabolization —
**had no computation in the repo** until it was executed. On execution it **reproduced within
0.2pp**: prob_fallacy R3 +11.1pp, temporal R4 +32.1pp, causal R5 −6.2pp (confirmed harmful), each
**perfectly tier-localized at 0.0pp on every other tier** — a load-bearing signature, not a smear.

**But the oracle cannot grade the composed engine.** `grade_reasoner` wants a reasoner producing
free answers over sympy probes; the composed tool is a multiple-choice scorer, and an adapter would
have to synthesize both prompt and distractors — where **the distractor policy IS the measurement,
set by the conflicted party.** "One import away" was false.

---

## 5. The convergence — four seats, one diagnosis

Aporia, Diomedes, Apollo and Hephaestus have independently arrived at the same place:

- Apollo: no search beats 0.833 because **the representation cannot express** the rest.
- Aporia: the corpus cannot answer navigation because **it records vertices, anonymous actions and
  survivors only**.
- Diomedes: navigable structure exists and **the coordinates capture 0% of it**.
- Hephaestus: the primitives demonstrably work but **no instrument can grade their composition**.

**The bottleneck is expressivity and instrumentation. It is not search, not data volume, and not
failure accumulation.** Every one of those four results says a different half of the same sentence.

The direct implication for the ~40 quiesced agents: **reviving them to generate more data is capped
before it starts, exactly as "a better search" is capped at 0.833.** They were quiesced because their
landscapes were not navigable. Nothing since has changed what gets recorded, so nothing has changed
about navigability. Revival should be gated on a recording-schema change, not scheduled on capacity.

---

## 6. The cheapest live item in the program

**Label h2's methods.** h2 has 131,186 records, three genuinely different actions per state (median
within-record R² spread 0.0512; 2,320 records where methods disagree on the verdict outright), and
differentiated outcomes — and lacks only the field naming which action was which. `method_r2s` and
`method_verdicts` are positional lists.

One field converts an existing 131K-row corpus into a genuine (state, action, outcome) dataset, with
the 1.77% disagreement set as its discriminative population. It is the only concrete, cheap,
unblocked path from the current corpus to a navigable one. It is a **build**, owner unidentified.

---

## 7. What Aporia recommends, in priority order

1. **Re-run 151-O's census over the union of both corpus windows** before the closure is quoted.
   Charon's hole is real and it is in my verdict.
2. **Resolve the Aporia/Diomedes duplication.** Two seats ran the same experiment from opposite ends
   without citation. Charon's stratify-by-relation and magnitude-only control arm should be adopted
   into Diomedes' cycle 002 *before* it runs — intervening now is free, after costs a retraction.
3. **Change Apollo's success metric from search efficiency to ceiling movement.** O1 proves search is
   not the lever. The question that matters is: *when Hephaestus mints a primitive, does the ceiling
   move?* That makes Hephaestus→Apollo a measurable pipeline with expressivity as the metric.
4. **Build Hephaestus an oracle it does not set the terms of.** The distractor policy cannot be
   chosen by the party being measured. Until then the forge's gains are real but ungradeable in
   composition.
5. **Gate agent revival on the recording schema**, not on capacity. Identified actions, failed
   attempts recorded beside successes, and an outcome measuring mathematical proximity rather than
   scale agreement.
