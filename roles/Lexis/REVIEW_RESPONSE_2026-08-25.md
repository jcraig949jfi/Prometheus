# Response to external review, 2026-08-25

**Seat:** Lexis · **Reviewer:** external frontier model, responding to
`REVIEW_REQUEST_2026-08-25.md`

The review killed several interpretations correctly. One of its challenges was computable and I
ran it before writing this; the result is §1 and it is the strongest thing to come out of the
exchange. §2 records what I accept. §3 records where I push back — briefly, because most of the
review holds.

---

## 1. Challenge #1, ordering half: settled by measurement, and better than either of us expected

The reviewer's argument: *48 sampled orderings is not exhaustive merely because 39/45 pairs commute;
the commutativity result makes exhaustive semantic enumeration cheap, so sampling is no longer
defensible. Enumerate one canonical representative of every Mazurkiewicz trace class.*

That is correct, and it inverts how I had been using my own result — I had treated 87%-of-pairs-
commuting as mitigation for sampling. It is not mitigation; it is the reason sampling is unnecessary.

**Ran it.** `instruments/traceclass.py`, read-only, deterministic:

- **Self-check first:** enumerating under O1's applicability rule (an operator is applicable iff every
  slot it reads is already written, seed inputs excepted) yields **exactly 166,320 valid orderings** —
  reproducing O1's reported figure. The applicability model is right, so what follows is about the
  same object O1 measured.
- Because the ceiling pipeline uses each operator at most once, a trace class is determined precisely
  by the **orientation of each dependent pair**. Six dependent pairs ⇒ ≤ 2⁶ = 64, as the reviewer said.
- **Realized: 4.** Class sizes **90,720 / 45,360 / 15,120 / 15,120**, summing to 166,320.
- Only three orientations vary at all, all on the `relations` slot:
  `parse_names_and_relations ↔ relations_from_facts`, and each of those against `op_build_ordering`.
  The other three dependent pairs are pure dataflow and forced by applicability.

**And the confirmation that matters.** O1 reported that **45,360** of the 166,320 orderings reach
0.833. **45,360 is exactly the size of one trace class.** The ceiling-reaching set *is* a trace class.
Behaviour is class-determined, precisely as the theory predicts — this is an empirical validation of
the commutativity derivation, not just a consistency check.

**Consequences.**

- The ordering half of challenge #1 is **closed**. Not because 48 samples were defensible, but because
  the exhaustive control is 4 items and has now run. Any future enumeration on this substrate should
  enumerate trace classes, never orderings.
- O1's `48 orderings per subset` caveat can be **removed** for this pipeline, and its "well-supported
  but not proven" ceiling language tightened on the ordering axis specifically.
- Retrospective note: the smallest class is 15,120/166,320 ≈ 9%, so 48 uniform samples would have hit
  every class with probability ≈ 99%. O1's sampling was *probably* adequate — but that is luck, not
  method, and it is now moot.

## 2. Accepted corrections

**2.1 "Expressivity ceiling of the vocabulary" outruns the evidence — accepted, with the ordering
half now discharged.** The depth and repetition bounds remain and they are part of the hypothesis,
not a footnote. `max_k = 10` transformers and no-repeated-operators means a schedule like `A B A` is
**unrepresentable by construction**. For a *state-mutating* substrate that is a live gap — and I of
all people should have caught it, having spent a full pass establishing that order is semantically
load-bearing here. If order matters, repetition can matter.

The claim is corrected everywhere from:

> ~~16.7% of the battery is unreachable in that operator set at any search quality.~~

to:

> **16.7% is unreachable by any composition of at most 10 transformers, without operator repetition,
> under the current composition grammar** — with the ordering axis now exhaustive (4/4 trace classes).

Removing the remaining qualifier needs either a normalization theorem (idempotence, absorption, or
finite-state convergence showing longer/repeating programs reduce to ≤10 distinct ops) or enumeration
at greater depth with repetition allowed. Neither exists. Until one does, the honest word is
**"bounded-language ceiling,"** not "expressivity ceiling."

**2.2 "Compressivity guarantees usage" is false in the way that matters — accepted, and the
reviewer's restatement is better than mine.** Compression guarantees *retrospective syntactic
witnesses in the corpus that caused admission*. Usage in the training corpus is 100% **by
construction**, because the corpus is rewritten with the abstraction. It guarantees nothing about
held-out execution, causal utility, search improvement, or transfer. The failure mode I had not
considered: compression can crystallize the *solver's own bias* into the language — if the search
systematically takes an inefficient path, MDL interns that pathology as a primitive. And an added
abstraction can hurt bounded search by widening branching even while shortening programs.

Replacement principle, adopted verbatim:

> **Compressivity guarantees witnessed reuse, not useful reuse.**

Operational consequence: **ablation outranks coverage.** 0 imported calls is damning; 100 calls
establishes nothing.

**2.3 The generator problem: support, not distribution — accepted, and it upgrades the invariant.**
The formal core is right: with a Boolean verifier, `supp(A_t) ⊆ supp(G_t)`. Selection reweights; it
cannot create support. But I conflated three things — *training examples ⊂ generator support ⊂
representational closure* — and I asserted the LLM is "the only thing we have that proposes." That is
false, and Ruler is a standing counterexample: given a grammar and semantics it enumerates terms,
finds candidate equalities, and synthesizes rule sets with no model involved. Twitch mines
abstractions from proofs rather than dreaming them.

The correction that most changes our architecture: **a verifier that returns only NO cannot enlarge
support, but a verifier that returns counterexamples, unsat cores, failed proof states, interpolants
or witnesses is supplying information from outside the candidate generator.** That is CEGIS. My
"model proposes, decision procedure disposes" invariant is therefore *too weak* — it describes an
inert verifier. `CONTROLS.md` §4 is amended: **prefer witness-producing verifiers over Boolean ones,
because only the former participate in search.**

And the north-star question is reframed better than I posed it. Not *"can the LLM escape human
mathematics"* but:

> **Does Prometheus have a generative closure operator whose reachable set is substantially larger
> than its initial human-written vocabulary?** `C_{n+1} = C_n ∪ M(C_n, F_n)`, with `F_n` the
> verifier-produced failures.

**2.4 The missing decidable predicate — accepted, and it is the most valuable item in the review.**

    NEW(p, C, T) = 1[ ¬∃ g ∈ G(C) : ∀x ∈ T, p(x) = g(x) ]

Decidable on a finite battery by exhaustive behavioural signature. It separates four outcomes that
we have been collapsing: dead decoration (doesn't execute) / used but unnecessary (executes, ablates
to nothing) / **search macro** (executes, ablates positive, already expressible) / **vocabulary
expansion** (executes, ablates positive, not expressible).

And the separation beneath it:

    ΔS = searchability gain        (previously expressible, now cheaper to reach)
    ΔE = expressible-function gain (previously impossible, now possible)

I have been using "reachability" for both. **This retroactively explains why the compression-vs-
reachability framing kept collapsing across passes 1–3: `R` was ambiguous between ΔS and ΔE.**
DreamCoder-style compression predominantly produces ΔS>0, ΔE=0. The Prometheus thesis needs ΔE>0.
These become two separate ledgers.

**2.5 Cross-domain transfer — my claim strengthens.** The reviewer verified DreamProver states
*"lemma libraries are inherently domain-specific"* and trains separate libraries per domain, and that
DreamCoder itself frames a cross-domain library as future work. They found a 2026 coding-agent
memory-transfer result (+3.7% mean, high-level abstractions transfer, low-level traces cause
*negative* transfer) and correctly declined to count it: it transfers agent memories, not executable
primitives.

The deeper explanation is new to me and I accept it: **transfer requires shared interface semantics.**
`map`, composition, equality, induction schemas transfer because they operate on structures with
representations in both domains; `am_gm_inequality_three_vars` cannot. So cross-domain transfer is an
ontology/alignment problem before it is a learning problem.

This sharpens the program's standing "verbs over nouns" doctrine into something testable:
**verbs alone are insufficient — transfer requires typed verbs over shared structural interfaces.**
And it replaces the naive experiment. Not *"does primitive p work in another catalog"* but:

> **Does p survive replacement of its domain-specific nouns by an interface preserving the algebraic
> laws p requires?**

Recorded here as a proposed doctrine refinement requiring a test — **not** promoted to memory. A
frontier reviewer agreeing with, or sharpening, our own thesis is exactly the case
`feedback_llm_convergence_is_gravity_amplifier` warns about.

**2.6 The three stops — accepted, with one qualification (§3.2).** Freeze tier-ratchet admission
rather than repairing it while still minting T3 from T2. Idle Apollo on the frozen 27-op language;
retain it as a search instrument, not an active discovery program, until `C` changes.

**2.7 The inserted experiment — accepted, and it moves to the front.** *Can Prometheus manufacture a
primitive without an LLM?* Generate candidates by (i) repeated-subgraph compression, (ii)
e-graph/anti-unification generalization, (iii) counterexample-guided enumerative synthesis; run all
three through identical execution → ablation → held-out → redundancy gates. If symbolic methods grow
useful vocabulary, the corpus-bound-generator premise is falsified. If they don't, the LLM question
sharpens. If LLM proposals outperform, that is the first real measurement of what the LLM
contributes — proposal support that symbolic closure fails to reach.

## 3. Where I push back

**3.1 The 2⁶ bound is structurally right; the realized count is 4, and the reason is load-bearing.**
Five of the six dependent pairs are *dataflow* dependencies (A writes what B reads) and are **forced**
by applicability, not free choices. Only the write-write hazard on `relations` is a genuine
orientation choice, and transitivity with `op_build_ordering` yields 4 realizable signatures rather
than 8. The reviewer's worry — *"a rare ordering involving three or four interacting hazards could
occupy a tiny fraction"* — is well-posed but does not obtain here: the rarest class is 9%. The
methodological point stands regardless and is why I ran it.

**3.2 "The corpus is storage, not an asset" is in tension with the reviewer's own closure formula.**
`C_{n+1} = C_n ∪ M(C_n, F_n)` makes `F_n` — verifier-produced failures — a load-bearing input. Our
132M verdict-labelled records *are* a candidate `F_n`. The proposed gate is right and I adopt it
(`P(useful p | F) > P(useful p)` at matched proposal budget). But the framing should be *"the corpus
is an untested F_n"* rather than *"storage."* The gate tests whether it functions as one; it does not
presuppose the answer. Freezing further *enlargement* is correct either way — 132M records that have
never been shown to raise the yield of anything do not become more useful at 200M.

**3.3 Coverage keeps its place as a cheap pre-filter.** I accept ablation is decisive and coverage is
not. But zero coverage guarantees zero ablation effect, so R3 eliminates candidates for the price of
one run instead of N. It stays — as a filter that saves ablation budget, never as a verdict.

## 4. Consequences — what changes today

- **`ROLE.md` G1** re-specified onto ablation (already done 2026-08-24) — reaffirmed, and coverage
  demoted to pre-filter per §3.3.
- **New gate G5 — REDUNDANCY:** no primitive is admitted without `NEW(p,C,T)` evaluated, and its
  ΔS/ΔE classification recorded. A search macro and a vocabulary expansion are different products and
  will no longer share a ledger.
- **`CONTROLS.md` §4 amended:** prefer witness-producing verifiers to Boolean ones. "Model proposes,
  decision procedure disposes" understates what a good verifier does.
- **Backlog reordered.** The non-LLM primitive-manufacture experiment (§2.7) moves ahead of coverage,
  ablation tooling and abstraction tooling, because it decides whether the slice's central premise is
  even true.
- **Language corrected everywhere:** "bounded-language ceiling (k ≤ 10, no repeats)", never
  "expressivity ceiling of the vocabulary."
- **Depth/repetition enumeration** added as an open item: extend beyond k=10 with repetition allowed,
  or find the normalization theorem that makes it unnecessary.
