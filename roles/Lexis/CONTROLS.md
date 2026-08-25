# Non-LLM controls for the vocabulary slice

**Seat:** Lexis · **Date:** 2026-08-24 · **Status:** v1, proposed alongside `ROLE.md`
**Question it answers:** what can be controlled without a model in the loop, and how do we move from
inference to discrete analysis?

---

## 1. The argument from this study's own error distribution

Eight claims were made and withdrawn across the library-learning study (`library_learning/RETROSPECTIVE.md`
§9). The distribution is the whole case for this document:

- **Zero measurements were wrong.**
- **Eight interpretations were wrong.**

Everything that survived was computed. The AST audit of `blackboard_ops*.py` — 26 operators, zero
undeclared writes, 39 of 45 pairs commuting by Bernstein's conditions — held completely, and found a
write-write hazard that had already invalidated two preregistered O1 runs. It cost one script and no
judgment.

Everything that was retracted came from reading a docstring and inferring a mechanism, reading an
abstract and inferring an objective, or reading a filename and inferring a capability.

**The operational rule that follows:** for every claim in this slice, name the decidable predicate
that would settle it, and prefer that predicate to a reading.

---

## 2. The control ladder — worked example, G1

"Are the forge's promoted primitives actually used?" has four rungs, all non-LLM, in increasing
cost and decreasing deniability.

| Rung | Predicate | Method | Cost |
|---|---|---|---|
| **R1** | primitive is *imported* | AST `ImportFrom` | free |
| **R2** | primitive has a *static call site* | AST `Call` against imported names | free |
| **R3** | primitive *executes* on a passing trap | coverage trace (`coverage.py` / `sys.settrace`) during a battery run | one run |
| **R4** | primitive is *load-bearing* | ablate it, re-run consumer, diff score at matched compute | N runs |

**R1–R2 measured 2026-08-24, read-only, both populations:**

- `forge/v2/hephaestus_t2/forge/` — 6 admitted T2 tools (against 171 in `scrap/`):
  **10 of 24 imported names called (42%).** But decompose it: every call is either `try_standard`
  (a T1 *parser* helper) or, in the ensemble deliberator, one of four sibling T2 tools.
  **Of the 12 imported `forge_primitives_t2` reasoning primitives — `self_critique` (×4),
  `causal_reason`, `temporal_reason`, `perspective_shift`, `multi_hop_reason`, `analogize`,
  `deliberate`, `ensemble_vote`, `error_correct` — zero are called anywhere.** This reproduces
  "primitives were decoration" statically, on the live tree.
- `forge/candidates/` — the larger population containing the STATUS-named passing tools:
  **1,343 of 1,646 imported primitives called (82%).**

**The two populations disagree by 40 points, and that is the lesson, not a footnote.** Quoting either
number as "the forge's primitive usage" would be `feedback_wrong_population_statistics` in its
purest form. Ask which rows.

**And R2 is not the deciding rung.** An 82% static call rate is compatible with the T2/T3 failure
analysis's own finding of *"93% hand-coded regex/if-blocks"* — a primitive can be called inside a
`try/except` that always throws, on a branch never taken, or with its result discarded. **R2 tells
you the call exists. Only R3 tells you it ran, and only R4 tells you it mattered.** G1's threshold
must be set on R4.

---

## 3. Substitution table — inference → decidable predicate

For each question this slice asks, the model-free form:

- *"Is this abstraction reusable?"* → **count call sites across the corpus.** This is what
  compressivity already is: an arithmetic property of a corpus, not a judgment. The field's choice of
  it is a controls choice before it is a theory choice. **But note the limit, established 2026-08-25:
  compressivity guarantees *witnessed* reuse, not *useful* reuse** — usage in the training corpus is
  100% by construction because the corpus is rewritten with the abstraction. Held-out utility still
  requires ablation.
- *"Do these two pipelines do the same thing?"* → **are they in the same e-class modulo theory T?**
  Equality saturation (`egg`, babble) makes this decidable within a saturation bound. This is the
  single largest available move from inference to computation in the slice.
- *"What is theory T?"* → **infer it** — Ruler from a grammar and interpreter, or, for the
  blackboard specifically, derive it from `@blackboard_op(reads=…, writes=…)` by Bernstein's
  conditions. Already done: 39 of 45 pairs commute.
- *"Did the library help?"* → **ablate and diff, at matched compute in a currency fixed in advance.**
  This is gate G2 and it is arithmetic.
- *"Is this tool novel?"* → currently `compute_portability_score`, a regex heuristic over source
  text. Replace with the **redundancy predicate** (decidable on a finite battery by exhaustive
  behavioural signature):

      NEW(p, C, T) = 1[ ¬∃ g ∈ G(C) : ∀x ∈ T, p(x) = g(x) ]

  i.e. *is this primitive already representable by some composition of the existing vocabulary?*
  Without it we cannot distinguish a **search macro** (ΔS>0, ΔE=0 — previously expressible, now
  cheaper to reach) from **vocabulary expansion** (ΔE>0 — previously impossible). Compression-style
  library learning predominantly produces the former; the Prometheus thesis needs the latter. These
  are two separate ledgers and have been conflated under the word "reachability" throughout this
  study. (§5 explains why the current portability heuristic fails despite being fully deterministic.)
- *"Could the answer have appeared here at all?"* → **exhaustively enumerate the reachable space.**
  O1's move; Diomedes' seat. It converted a four-month plateau into a measured *bounded-language*
  ceiling — and on 2026-08-25 the ordering axis of that enumeration was closed exactly: 166,320 valid
  orderings collapse to **4 trace classes**, and the 45,360 reaching 0.833 are exactly one of them.
  Enumerate equivalence classes, never orderings.
- *"Is this result robust?"* → **seed variation** (the forge already does this: 100% collapsing to
  79–96%), **permutation null**, **metamorphic mutation** (Nemesis). All deterministic protocols.
- *"Does this ordering matter?"* → **write-write and read-write hazard analysis.** Pass 5.

---

## 4. Where a model is irreducible: proposer, never oracle

Some steps genuinely need generation — writing a candidate primitive, sketching a proof, guessing a
lemma shape. The literature's answer is consistent across its two strongest mathematics systems, and
it is the architecture to copy:

- **Lemmanaid** — an LLM generates the lemma **template** (the shape); symbolic methods fill in the
  details and check them.
- **DreamProver** — the LLM produces a proof sketch; unproven `sorry` holes become standalone
  theorems; **Lean** decides whether they hold. Admission is formal verification, not model opinion.
- **ReGAL** — abstractions are refined and admitted **by execution**, not by rating.

The invariant: **the model proposes, a decision procedure disposes.** A model may never be the
oracle, may never score its own output, and may never appear downstream of the gate.

**Amended 2026-08-25 after external review — that invariant is too weak.** With a Boolean verifier,
accepted candidates satisfy `supp(A) ⊆ supp(G)`: selection reweights what the generator already
reaches and cannot create support. A verifier that returns only NO is inert with respect to reach.
But a verifier that returns **counterexamples, unsat cores, failed proof states, interpolants or
witnesses** supplies information from outside the candidate generator — that is CEGIS, and the
verifier is then participating in search, not merely disposing. **Prefer witness-producing verifiers
to Boolean ones.** Our exact oracles mostly *can* produce witnesses; we have not been collecting them.

The second correction: **the LLM is not our only proposer, and asserting that it is was wrong.**
Ruler synthesizes rewrite rules from a grammar and interpreter with no model involved; Twitch mines
abstractions from proofs. The generator is properly `G = G_LLM ∪ G_compression ∪ G_symbolic`, and the
open question is whether the closure `C_{n+1} = C_n ∪ M(C_n, F_n)` — with `F_n` the verifier-produced
failures — reaches substantially beyond the initial human-written vocabulary. This is also
exactly what H2 precondition 3 asks for — *"model writes a small verified primitive from a typed
diagnosis"* — and pass 8 established that Hipster's proof mode and Lemmanaid already occupy that
design, so the pattern is available rather than speculative.

Corollary for reporting: when a system under test contains an LLM, the *control* can still be fully
discrete. An ablation over an LLM-driven forge yields a numeric delta; the forge being stochastic
means you need seeds and a matched-compute baseline, not that the measurement becomes a judgment.

---

## 5. The caveat that matters most: non-LLM ≠ valid

`compute_portability_score` in `apollo/src/gene_extractor.py` is deterministic, discrete, regex-based
and completely model-free. It starts at 1.0 and subtracts fixed penalties for long string literals,
English pattern words, off-convention `ctx` keys, and long regexes.

**It never reads a corpus.** It scores one method's source text in isolation. And the macro branch it
feeds fires *because a tool scores badly*, bundling what cannot be decomposed — the inverse of
promoting what recurs.

So a control can be perfectly discrete and still measure the wrong thing. Worse: a deterministic
wrong measure is **reproducibly** wrong and carries the appearance of rigour. Determinism buys
reproducibility, not validity.

Every control adopted under this document therefore carries three statements, per the program's
standing doctrine:

1. **Which population** it was measured over (`feedback_wrong_population_statistics`) — §2 is the
   worked example of getting this wrong being easy.
2. **Which direction** its known confounds push relative to the gate
   (`feedback_truncation_can_flatter_a_gate`).
3. **That the gate is reachable** — compute the attainable range before reading a null, and check the
   threshold exceeds the measurement's own SE (`feedback_gate_must_be_shown_reachable`,
   `feedback_gate_must_exceed_measurement_error`).

---

## 6. Immediate consequences for the gates in `ROLE.md`

- **G1 is re-specified.** Its threshold moves from "usage < 10%" — ambiguous across rungs — to
  **R4: ablation delta on the consumer's score, at matched compute.** R1–R2 are reported as context
  and never as the verdict. The 42% / 82% split in §2 is why.
- **G0 gains a cheap partial answer.** Whatever the T2/T3 rebuild's approval status, the six admitted
  tools in `forge/v2/hephaestus_t2/forge/` call **zero** of their twelve imported reasoning
  primitives. That is current-tree evidence, not a historical quote.
- **G2 is unchanged and now has a house instrument** — matched compute, currency fixed in advance,
  O1's organism-evaluations as the precedent.
- **G3 gains a prerequisite:** before designing the transfer experiment, derive the substrate's
  equivalence structure (Bernstein, or Ruler) so that "search cost on substrate B" is counted over
  equivalence classes rather than over orderings. Pass 5 showed 87% of pairwise ordering decisions on
  Apollo's ceiling pipeline carry no information; counting them as work would inflate any transfer
  measurement.

## 7. Instruments (read-only, scratchpad; none write to Apollo or the forge)

- `audit_rw.py` — declared vs actual `reads`/`writes` across `blackboard_ops*.py`
- `commute.py` — Bernstein independence over O1's ceiling pipeline
- `g1_usage.py` — R1/R2 import-and-call-site measurement, parameterised by forge directory

Rung 3 (coverage trace) and rung 4 (ablation) are **not yet built**. They are the next instruments
this seat needs, and neither requires a model.
