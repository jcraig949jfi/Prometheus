# H1 — Failure transport between tasks

**Directory opened 2026-09-09 by Aporia at the operator's direction.**
Everything gathered so far on H1: the literature research, the two external
critiques of that research, and the adjudication between them.

    research/    201 evidence audit, 202 adversarial review (Deep Research)
    feedback/    Gemini critique, Astra analysis -- both 2026-09-09
    design/      ARMS.md (the comparison), DEFERRED_REGISTER.md (alpha scope)
    CITATIONS.md verification status of every citation in this directory

The shared H0-H5 build contract (`DESIGN_astra_v0.1_H0-H5.md`) sits one level
up, in `aporia/docs/hypotheses/`, because it governs all six hypotheses and
filing it under H1 would misplace it. Its H1 sections are quoted where relevant
in `design/ARMS.md`.

---

## The claim

When a search fails on one task and the failure is recorded as a concrete
witness, supplying that stored witness to a later search on a RELATED task
improves the later search — relative both to supplying nothing and to supplying
a witness drawn at random.

## Status

    prior-art audit (201)      UNTESTED
    adversarial review (202)   severe objections, verdict word not emitted
    Gemini on 202              endorses it, calls the confound fatal
    Astra on 202 and Gemini    contests both; retains H1; adds arm C for beta
    Astra deferred register    alpha keeps THREE arms; arm C is H1-R01, beta

**Net: H1 is retained, alpha is unchanged, arm C is deferred to beta, and the
headline objection in my own external review has been scoped out of the alpha.**

---

## The correction that matters most, and it lands on my own review

My external review block for H1 led with the SMT branching confound: injecting
any constraint perturbs VSIDS heuristics, solver runtimes are heavy-tailed, and
a semantically useless constraint that routes the solver around a pathological
branch manufactures a large artefactual win.

**That objection does not describe the alpha.** Astra's v0.1 design specifies a
bounded Boolean VM with exhaustive verification over all eight inputs of a
3-input task, a fixed seeded candidate enumeration order, and Z3 only as an
optional later adapter. There is no SMT solver in the alpha to perturb, and
enumeration order is held fixed by design.

I reviewed the hypothesis as stated to me and did not check it against the
build contract, which the operator had not yet supplied. The objection is real
for a later SMT-backed stage and should be retained for that stage. It is not a
reason to change the alpha, and my review overstated its reach.

## The second correction: what is actually transported

Both reviewers assumed the experiment transports the source task's expected
answer along with the input. It does not. The design transports **the input
only**, and recomputes its correct label with the **target** task's oracle.

That removes the "importing invalid source constraints" objection at the root.
A counterexample shows that one candidate fails one specification; its input may
be useful elsewhere, its original expected answer is not claimed to transfer.

## The third correction: Gemini's mechanical claim is wrong

Gemini calls the constraint-bloat argument "rock solid." Astra's rebuttal is
correct on the logic and I adopt it:

> Adding a valid constraint reduces or preserves the set of admissible
> solutions. It can increase the formula's representation size and processing
> overhead. These are different quantities, and runtime can improve or
> deteriorate.

There is no general law that each added counterexample makes synthesis
exponentially harder. Synapse itself reports substantial benefit from
counterexample exchange in one benchmark category and little in others, which
argues for measuring the tradeoff rather than predicting universal failure.

## The fourth: "isomorphic noise" is not the gold standard

Gemini calls the isomorphic noise control "brilliant" and "the gold standard."
Astra's objections are specific and I find them sound:

- a tautological constraint may vanish during preprocessing
- changing constants can change simplification, propagation and pruning
- a valid randomised input, correctly labelled by the **target** oracle, can
  still be genuinely informative — so it is not a null arm
- a meaning-preserving transformation may preserve the very information it is
  supposed to remove
- "semantically void" is undefined until you say void **relative to which
  candidate population and which existing tests**

Verdict: keep structurally matched controls as a diagnostic. Do **not** make an
under-specified synthetic witness a mandatory gate, and do not accept a
SageMath AST-skeleton randomiser as establishing the required properties.

## Where I agree with the adversarial review, still

- **The historical refutation is unsupported**, and I flagged this before Astra
  did: 202 argues from conspicuous absence, not from a documented null. Euphony
  and Code2Inv demonstrate that probabilistic and neural transfer work; they are
  not negative experiments on concrete transport. Astra adds ReFuzz, which
  reuses bug-triggering tests across processors sharing an ISA — fuzzing, not
  synthesis, so it does not establish H1, but it does weaken the abandonment
  story further.
- **Retrieval can smuggle in extra search or privileged information**, and must
  be charged and frozen.
- **A poorly matched random arm inflates the apparent value of relevance.**

## The disagreement that is still open

Whether structural matching of the control witness is a **mandatory gate**
(Gemini, and my review, say yes) or a **diagnostic among several** (Astra says
this). Astra's objections show the control is not sufficient; they do not show
it is worthless. Unresolved, and it should be resolved before beta rather than
argued after a result.

---

## What changed in the design as a result — and what did NOT

Astra concedes a real omission: the three arms cannot separate *failure-specific*
value from ordinary *source-task similarity* value. Arm C fixes it, and neither I
nor Gemini proposed it.

**But alpha does not change.** Astra's `design/DEFERRED_REGISTER.md` decides:
keep the H1 alpha scope and its three arms unchanged, and take up arm C in beta
as H1-R01. Alpha closes on plumbing and blinding — a failure pack round-tripping
through SFE/Vivarium, three arms executing, oracle-parity, source-label,
budget-exhaustion and accounting checks passing. **A positive transfer effect is
not an alpha exit requirement.**

The register also states the rule that governs this whole directory:

> Do not reopen alpha merely because another literature review proposes a
> stronger control.

That is aimed squarely at documents like the ones filed here, and it is correct.
I revised `ARMS.md` once already for exactly that reason — I wrote it from
Astra's analysis before Astra's scoping decision arrived, and had it briefly
saying the four-arm design superseded the three. It does not.

## The caution to carry out of this directory

Astra, on the reports in `research/`:

> The reports motivate checks; their agreement, disagreement or severity labels
> do not constitute an H1 experimental result.

And on why the reviews misfired in places:

> The adversarial review assessed a reconstructed hypothesis; future reviews
> should receive the exact versioned protocol.

Both are right. The fix for the next round is mechanical: send reviewers the
versioned protocol rather than a reconstruction.

## Reading order for someone new

1. `design/DEFERRED_REGISTER.md` — the authority on alpha scope
2. `design/ARMS.md` — the comparison, alpha and beta arms
3. `feedback/2026-09-09_astra_analysis.md` — the designer's rebuttal, and arm C
4. `research/202_h1_adversarial_review.md` — the objections, read with the two
   scoping corrections above in hand
5. `research/201_h1_evidence_audit.md` — the prior-art audit, UNTESTED
6. `feedback/2026-09-09_gemini_critique.md` — endorsement plus the
   agentic-translation extension, which is a separate experiment (H1-R06)
7. `CITATIONS.md` — what has actually been verified
