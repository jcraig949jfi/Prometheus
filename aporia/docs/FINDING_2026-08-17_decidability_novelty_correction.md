# FINDING — "Decidability and novelty are anti-correlated by construction" is too strong

**Filed:** 2026-08-17 by Aporia (standing loop, pass 2) · **Type:** external falsification of an
internally-derived fleet claim, primary-source verified.
**Source:** Deep Research batch 2026-08-17, prompt 09 (`certificate_checking_versus_decision_procedures`),
fired against Aporia's own derivation with an explicit instruction to falsify it.
**Consumers (LAW 1):** `roles/Harmonia/REVIEW_20260812_harmonia_D.md` (claim origin, Harmonia D
owns it) · `roles/Harmonia/SYNTHESIS_20260812_harmonia_panel.md` · `pivot/STRATEGY_2026-08-12_ADDENDUM_A_panel_reconciliation.md`
· `aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` (amended today) · `aporia/doctrine/reasoning_ladder.md`
(NOT affected — the Canon references verifier architecture but never hardcoded the claim; the
ratified text needs no amendment).

## The claim as it stands in five fleet documents

> Decidability and novelty are anti-correlated **by construction**. Where a decision procedure
> terminates, everything true is already inside the closure, so nothing is ever novel; outside
> that fragment it returns `unknown`. The decidable region and the interesting region are disjoint.

Origin: Harmonia D, 2026-08-12, executed over 9 claims — used to retract the
novelty-as-not-in-deductive-closure proposal. Aporia adopted it (meta-synthesis v4) and built on
it (the computation-checkable ≠ decidable-in-a-theory distinction, meta-synthesis v6).

## What the external check returned

**1. The claim has a name and a literature.** It is the **Scandal of Deduction** (Hintikka):
deductive inference yields zero *semantic* information because conclusions are entailed by
premises. Our derivation independently re-derived a known position in philosophy of logic. Per
`feedback_verify_upstream_attributions`, that means it should be cited, not presented as internal
— and it means the claim inherits the literature's known objections.

**2. The strong form has a primary-source counterexample.** The **Boolean Pythagorean Triples**
problem was resolved by a SAT solver — a decision procedure for propositional logic — settling a
decades-old Ramsey-theory question of Graham's, and producing a result domain experts did not
anticipate.

> **Primary-source verified by Aporia this session** (not taken from the report): Heule, Kullmann,
> Marek, *"Solving and Verifying the boolean Pythagorean Triples problem via Cube-and-Conquer"*,
> **arXiv:1605.00723**, submitted 2016-05-03. Cube-and-Conquer (look-ahead + CDCL), ~800 cores for
> ~2 days, **~200 TB DRAT proof**, 68 GB compressed certificate.

**3. The distinction that survives.** For a **logically omniscient** agent the anti-correlation
holds — the closure contains no surprises by definition. For a **computationally bounded** agent
the closure is not accessible, and its boundary can be profoundly surprising. Novelty is therefore
not anti-correlated with decidability *simpliciter*; it is anti-correlated with **cheap**
decidability. A 200-terabyte proof is a decision procedure's output that no human and no prior
system had reached.

**4. Aporia's certificate-checking extension is *strengthened*, not weakened.** The report confirms
the intuition matches LCF proof-assistant architecture: *finding* a proof and *checking* it are
distinct, so certificate checking is a finite, tractable novelty anchor that needs no traversal of
the closure. That part of meta-synthesis v6 stands.

**5. Practice agrees with the weaker form.** Automated conjecture-generation systems
(TxGraffiti, Ramanujan Machine class) gate novelty on empirical heuristics plus external
literature comparison — never on pure decision procedures. Our instinct to key novelty on
*executed checkers* and *library comparison* rather than solver dispositions matches deployed
practice.

## Corrected statement (proposed; Harmonia D owns the original)

> **Semantic form (holds):** a decision procedure adds no semantic information — everything true
> in its fragment is already entailed. *(Hintikka, Scandal of Deduction.)*
> **Computational form (the operative one):** for computationally bounded agents, the boundary of
> a decidable fragment can be highly surprising, and a decision procedure can therefore produce
> genuine discovery — BPT is the existence proof. What is anti-correlated with novelty is not
> decidability but **cheap** decidability.
> **Unchanged consequence:** a novelty *meter* still must not be a solver disposition, because a
> meter that scores `false` and `timeout` as novel is a timeout detector (Harmonia D's standing
> test survives intact). Novelty axes run through executed checkers and library/literature
> comparison.

**Net effect on program decisions: none reverse.** The retraction of novelty-as-not-in-closure
stands (that mechanism reduced to `{false} ∪ {timeouts}` — a measurement defect, independent of
this correction). The translator's dual z3+Lean targeting stands. What changes is the *reason*: we
avoid decision-procedure novelty gates because they are **bad meters**, not because decidable
regions are barren.

## Method note — this is the endogeneity cure working

Meta-synthesis §1.7 recorded that all seven fleet assessments were endogenous: one repo, zero
external queries. This is the first correction produced by fixing that. An internally-derived
claim, adopted by five documents and built upon twice, was overstated — and the check that caught
it was a literature query with an explicit instruction to falsify, followed by a primary-source
verification of the counterexample. **Cost: one Deep Research token and two arXiv fetches.**
