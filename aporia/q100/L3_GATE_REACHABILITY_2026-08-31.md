# L3 (DeepSeek): 28% of the tests are blocked by named theorems, and the list says so itself

**Measured 2026-08-31 by Aporia.** Registry: `REGISTRY_L3.jsonl` (50 rows — the source supplied
50 of a claimed 100 and paused).

---

## 1. The result

    THEOREM_BLOCKED   14 / 50   28.0%   PASS demands what a named theorem forbids
    BOUNDARY_GATE     28 / 50   56.0%   PASS sits exactly at the edge of the attainable range
    REACHABLE          8 / 50   16.0%   PASS leaves a band the measurement can land inside

    UNREACHABLE AS WRITTEN                42 / 50 = 84%

Mechanical cross-list proxy — a fixed regex for absolute-boundary tokens (`zero`, `100%`,
`exact`, `perfectly`, `infinite`, `never`, `1.0`) over the test text, no judgement, fully
reproducible:

    L1   26 / 100 = 26%
    L2   17 / 100 = 17%
    L3   29 /  50 = 58%

Same ordering as the hand-coding, by an independent and dumber method.

## 2. How strong each number is

**28% is the floor and it is hard.** THEOREM_BLOCKED means a specific theorem forbids the PASS
condition, and in most cases the list's own *"why it remains unsolved"* column states the
impossibility while the test column demands it anyway:

- **L3-021** asks for exact subgraph isomorphism on N=1000 in under one second. Its own
  why-column: *"The Subgraph Isomorphism problem is NP-complete."*
- **L3-048** requires correctly assigning low provability to **true but unprovable** statements —
  i.e. deciding provability. Its own why-column: *"generally undecidable."*
- **L3-032** requires recovering causal direction when the process is **strictly Gaussian and
  symmetric**, the canonical unidentifiable case. Its own why-column concedes the asymmetry
  requirement.
- **L3-035** demands *perfect* demultiplexing of superposition after stating N concepts in M
  dimensions with N>M is *"mathematically underdetermined."*
- **L3-041** demands tracing a definition of aleph-null back to specific collision events after
  stating sensorimotor data is *"strictly finite and bounded."*
- **L3-037** demands a ZFC-verifiable proof that a newly invented logic is **both sound and
  complete** — forbidden by Gödel for any sufficiently strong consistent system.
- **L3-014** requires exploration ranked by **Kolmogorov complexity gradients**. K is
  uncomputable.
- **L3-050** requires 0% safety violation over an **infinite time horizon** — not decidable by
  any finite test.

**56% is the soft category and should be read as an upper bound.** A zero-gate is legitimate
when a mechanism *structurally guarantees* it — L3-009's "0% ill-typed intermediate terms" is
achievable with a type-checked generator, and L3-001's "zero group-axiom violation" is
achievable if the representation is constrained rather than learned. Several BOUNDARY_GATE calls
are therefore disputable, which is why each row carries its reason in the registry.

**The honest range: at minimum 28% cannot fire; up to 84% depending on how strictly the boundary
gates are read.**

## 3. The list violates its own stated inclusion criteria

L3's criteria section says questions were included only if *"failure or success cannot be
definitively measured"* was false, and that cultural or subjective judgements were *"strictly
excluded."* Yet:

- **L3-050** conditions PASS on an infinite time horizon — not definitively measurable.
- **L3-039** asks the system to rank *"aesthetic or mathematical significance"* and match
  historical human breakthroughs, and asks for a computable metric of **"mathematical beauty."**
  That is exactly the cultural judgement the exclusion criterion names.

## 4. Why this matters more than the list does

One pass before L3 arrived, `OVERLAP_ANALYSIS_2026-08-31.md` recorded that **neither L1 nor L2
contains a single question about gate reachability** — whether a preregistered threshold lies
inside the attainable range — and named it as a defect this programme keeps hitting in practice
(twice on 2026-08-27, once on 08-23) precisely because it appears when you *run* an instrument
rather than when you survey a literature.

L3 then arrived with the defect in 28–84% of its own tests.

**Disclosure, because it matters for how much this counts:** I did not preregister this
classification before seeing L3, so this is not a fired prediction. What *does* predate the data
is the criterion — `feedback_gate_must_be_shown_reachable`, committed 2026-08-23 and restated in
the overlap analysis one pass before L3 was supplied. The rule is older than the test; the
application is not.

## 5. What follows for the Q100 loop

1. **No question from any list enters a dossier without a reachability pass first.** This is now
   a loop precondition, applied to L1 and L2 retroactively — the mechanical proxy flags 26 and 17
   candidates respectively for hand-checking.
2. **A test whose PASS condition contradicts its own why-column is not a research question, it
   is a category error**, and should be recorded as such rather than researched. Fourteen of L3's
   fifty are in that state.
3. **The salvageable content of L3 is real but small.** The eight REACHABLE rows are worth
   keeping — notably **L3-042**, which asks an algorithm to *prove when the graph becomes
   unidentifiable*. That is the only test across all three lists that treats a limit as a result
   rather than as a failure, and it is the posture this programme already uses (report VACUOUS
   rather than null). **L3-020** is the cleanest gate in the list: 0% heuristic use against a
   <50% fail band and a 1% baseline-preservation band.
4. **Generator-dependence is now measured on two axes.** L1↔L2 agree on about a third of
   content; L1/L2/L3 differ by 26/17/58% on boundary-gate rate. Neither the content nor the
   methodological quality of an LLM-generated frontier list is generator-invariant, so none of
   the three can be used as a research plan without exactly this kind of pass.

## 6. Standing caveat

The hand-coding is mine and each row is individually disputable; the registry ships the reason
per row so it can be argued with. The mechanical proxy is reproducible but crude — it flags
absolute-boundary language, which is a necessary but not sufficient condition for an unreachable
gate. Where the two methods disagree, the hand-coded reason is the claim and the regex is only
corroboration.
