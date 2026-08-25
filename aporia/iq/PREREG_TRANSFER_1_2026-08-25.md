# PREREGISTRATION — TRANSFER-1: the frozen G-heldout generator and the X-heldout route

**Written 2026-08-25 before any generator code exists.** Ladder step 4 of 7, taken ahead of
SYNTH-1 because SYNTH-1's reading has no valid instrument until this exists — see §1. Governing
doctrine: `aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md` §3.

Prior rungs, not to be re-run: IQ-PORT-1 **ADVANCE** (`28761a6f`), provenance discharged and
pipeline **FROZEN** (`c66ea4a9`), IQ-NULL **ADVANCE** (`953a8e97`).

---

## 1. Why this rung comes before SYNTH-1

The ladder calls `vacuous_truth` the only clean synthesis target. Measured last pass: canary
`vacuous_truth` is **2 distinct prompts across 5 tasks** with correct-answer first token "Yes"
in **5/5**, and a scorer that ignores the problem text entirely and picks the "Yes" candidate
scores **5/5**. A mint moving +0.0417 there would satisfy every criterion the port satisfied
while demonstrating nothing.

**The ladder's step order is not being rewritten.** SYNTH-1 remains the next *scientific*
step. What has changed is that its instrument does not exist, and this rung builds it.

## 2. What the generator is FOR, stated as a discrimination

A parameterised generator eliminates template memorisation and analyst-authorship leakage. It
does **not** eliminate overfitting to the generator's own ontology, because the generator
embodies our theory of the capability. Hence two strata, and the second is the real test:

    G-heldout   hundreds-to-thousands of tasks from a FROZEN procedural generator, with
                train/test PARAMETER partitions and unseen combinations.
    X-heldout   the same underlying relation through a structurally DIFFERENT construction
                route. No external benchmark; what is required is independent construction
                semantics.

The question is not *"can this primitive solve more examples of the family we designed for
it?"* but *"does the transformation's usefulness survive a change in how the problem
manifests?"* — the difference between fitting a benchmark and adding an instruction to the ISA.

## 3. The degeneracy this generator MUST control, earned by measurement

`c66ea4a9` measured that one of five canary `all_but_n` tasks has `T = 2N` (10 − 5 = 5), so
the target coincides with an operand. Consequences, both measured, not hypothesised:

- a wrong rule that simply **returns N** solves it, and scores ΔE +0.008333;
- a second wrong rule, **T // 2**, lands on the same task with the same ΔE;
- strict provenance set membership broke on exactly that one task — 3,931 of 464,652
  pipelines "solved" an `all_but_n` task without the port, every one of them that task.

**Hard requirement, fixed before any draw is made:** the generator must place every draw into
exactly one of three strata and report the counts:

    NONDEGENERATE   target coincides with no operand and no simple function of one
    DEGENERATE      target equals an operand (T-N == N, T-N == T, N == T, ...)
    NEAR_DEGENERATE target within 1 of an operand

The **primary** G-heldout reading is computed on NONDEGENERATE only. DEGENERATE is generated
anyway, in a declared proportion, and reported **separately** as a contamination channel — a
mutant's score there is a measurement of the degeneracy, not of the mutant. Deleting the
degenerate stratum silently would hide the very effect that was just measured.

**Failing input for this control:** if a semantically wrong mutant scores at or near the true
operator's rate on the NONDEGENERATE stratum, the stratification did not work and the
generator is contaminated by something I have not identified.

## 4. Frozen-generator requirements

1. **Seeded and deterministic.** Same seed, same task list, byte for byte. The seed is fixed
   in the preregistration and never re-drawn after seeing a result.
2. **Train/test PARAMETER partition, not instance partition.** Partition the parameter space
   (e.g. ranges of `T`, ranges of `N`, and their combination class), so a test task is not a
   fresh sample from the training distribution but a draw from a **held-out region**.
3. **Unseen combinations** are required in test: at least one test cell whose
   (parameter-range × structure) pair appears nowhere in train.
4. **Surface realisation must vary independently of structure**, so that surface memorisation
   and structural competence are separable.
5. **Distractor construction is part of the generator and is preregistered**, because the
   canary's distractors are what made a fixed-position counterfeit score 3/5. Distractors must
   include the operands themselves, so "echo an operand" is a *wrong* answer by construction
   except in the DEGENERATE stratum where it is flagged.
6. **Frozen by hash** on first generation. The hash goes in the result ledger; any change
   invalidates every reading taken against it.

## 5. X-heldout: independent construction semantics

For `all_but_n` the relation is *remove N from T, report what remains*. Structurally different
routes to the SAME relation, at least two of which must be implemented:

    set-membership     an explicit collection with N elements marked removed; count remains
    graph/predicate    nodes with a removal predicate; count nodes not satisfying it
    narrative-inverse  stated as an addition to be inverted ("after N were added there were T")
    tabular            a small table with a removed-flag column

**X-heldout is not a paraphrase.** A rewording of the same template is still G. The test is
whether the *construction* differs, and I preregister that I will report, for each X route,
whether the port's parser fires at all — because the honest expected result is that the
template-shaped parser from IQ-PORT-1 **fails outright on X**, which is itself the finding.

## 6. Preregistered predictions

    T1  the frozen generator produces the declared counts per stratum, and the NONDEGENERATE
        stratum contains ZERO draws where the target equals any operand. Asserted in code.
    T2  the IQ-PORT-1 port scores at or near ceiling on G-heldout TRAIN.
    T3  the port scores at or near ceiling on G-heldout TEST (held-out parameter region).
        A large train/test gap would mean the port is parameter-range-bound, which for
        `T - N` would be surprising and would indicate a parser range bug, not a capability.
    T4  every semantically wrong mutant (M1-M6, including return_n and half_total) scores at
        or near ZERO on the NONDEGENERATE stratum, and return_n scores at or near CEILING on
        the DEGENERATE stratum. **T4 is the load-bearing prediction of this rung** — it is
        what shows the generator discriminates where the canary could not.
    T5  the port's parser FAILS on at least one X-heldout route (predicted: all of them),
        because it is a template-shaped regex. Reported as a result about the port's
        generality, not as a nuisance.
    T6  a mutant that passes G but fails X measures generator weakness. If one exists it is
        reported under that heading.

**T5 is a prediction against my own artifact and I am stating it in advance so that its
confirmation cannot later be presented as a surprise or as a reason to widen the parser.**

## 7. Terminal states — exactly one, and they partition

    ADVANCE   T1 and T4 hold. The generator discriminates true operator from wrong rule on the
              nondegenerate stratum. It is FROZEN by hash and becomes the instrument SYNTH-1
              was missing. T5's outcome does not gate this — it characterises the port.
    REDESIGN  T1 holds but T4 fails: some wrong rule scores near the port on NONDEGENERATE.
              The generator has a degeneracy I did not stratify. Find it before proceeding.
    PARK      T1 fails: the generator cannot produce a clean nondegenerate stratum at all.
              File a GATE_ELI5.

Coverage: T1 ∈ {holds, fails} × T4 ∈ {holds, fails} → four cells, mapped to three states
(T1-fails absorbs both T4 outcomes). To be asserted by enumeration in code, as in the prior
two rungs.

## 8. Scope declared in advance

- This rung measures **`all_but_n` only**. It is the relation with a verified port, a measured
  degeneracy and a known-good baseline. Generalising the generator to `vacuous_truth` is the
  NEXT step and inherits this one's machinery; doing both at once would confound an instrument
  question with a synthesis question.
- **No change to `C`.** `blackboard_evolve.REGISTRY` stays byte-frozen. No new registry
  entries, no domains, no agents revived.
- **The 120-task battery is not modified.** The degenerate canary task stays exactly as it is;
  it is part of the frozen evaluator and editing it would invalidate every ΔE measured so far.
- ΔE is **not** the statistic here. This rung measures per-task accuracy on generated strata.
  Quoting a ΔE against the 120-task battery from generated tasks would be a category error.

## 9. Cost-to-falsify — rows opened at prediction time

Per the standing guard, each of T1–T6 gets a row in `aporia/iq/COST_TO_FALSIFY.jsonl` with its
predicted probe cost and the mechanism classes it would eliminate, written **before** the
outcome is known. Cumulative record so far: 10/10 predicted probe costs matched actual.
