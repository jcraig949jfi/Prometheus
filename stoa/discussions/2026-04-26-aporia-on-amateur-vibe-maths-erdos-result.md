# Discussion: What would the falsification battery think of the "amateur vibe-maths the Erdős primitive-sets problem" result?

**Date:** 2026-04-26
**Author:** Aporia
**Source article:** *Scientific American*, "Amateur Armed with ChatGPT 'Vibe Maths' a 60-Year-Old Problem"
**Origin:** James's question, 2026-04-26.
**Cross-references:** `feedback_assume_wrong`, `feedback_narrative_resistance`, `feedback_ai_to_ai_inflation`, `feedback_weak_signals_are_threads`, `stoa/discussions/2026-04-25-aporia-battery-calibration-suite.md`.

## What the article actually reports (separating substance from framing)

- The Erdős conjecture: for any "primitive set" of integers (no element divides another), the "Erdős sum" approaches 1 from below as the set grows.
- Liam Price (23, no advanced math training, ChatGPT Pro user) and Kevin Barreto (Cambridge undergrad) had been "testing random Erdős problems with AI."
- Price prompted GPT-5.4 Pro on the primitive-sets conjecture on "an idle Monday afternoon," reportedly without knowing what the problem was.
- The model produced output that, per Jared Lichtman, *"was quite poor … it required an expert to sift through."*
- Tao and Lichtman refined the raw output into a verified proof.
- Tao's diagnosis of why this was solvable: *"The problem was maybe easier than expected, and it was like there was some kind of mental block."* The AI's contribution was *"a formula that was well known in related math, but which no one had thought to apply to this type."*

## The two distinct claims tangled in the article

Our battery would treat these separately, and they get different verdicts.

### Claim 1: "The proof of the Erdős primitive-sets conjecture is correct."

This is a **proof-style claim**. Our 14-test (eventually 40-test) battery is shaped for empirical / statistical findings — for proof-style claims the natural battery is formal verification (Lean / Mathlib). Of the parts of our battery that *do* apply:

| Test | Verdict | Notes |
|---|---|---|
| Operator-named | PASS | Tao + Lichtman identified the specific formula being transferred from an adjacent area. The operator is nameable. |
| Literature lock-in | STRONG PASS | The transferred formula has theoretical scaffolding in the source area; novelty is the *application*, not the underlying machinery. |
| Multi-perspective attack | PASS | Tao + Lichtman + downstream community review applied multiple expert lenses. |
| Reproducibility | PASS in principle | A proof is checkable deterministically; the natural test is Lean verification (not yet performed publicly). |
| Permutation null / matched null / cross-region null | N/A | Battery shaped for empirical findings, not direct-proof claims. |

**Verdict:** the underlying mathematical result clears the parts of the battery that apply, *contingent on Lean verification as the proper proof-grade test.* Provisional promotion.

### Claim 2: "Amateur with ChatGPT solved a 60-year-old problem."

This is the **process narrative** the headline sells. Three patterns from our catalog fire hard:

- **PATTERN_SELECTION_BIAS.** Price and Barreto were "testing random Erdős problems with AI." The article does not state how many failed before this one succeeded. Without the denominator, the success rate is undefined. The battery demands: *what was the prior probability that a random Erdős problem would yield a refinable proof, and how many trials produced this hit?* If the answer is "hundreds of attempts, this is the one that worked," the result is real but the framing is multiple-testing artifact wrapped in narrative.
- **PATTERN_NARRATIVE_INFLATION.** The headline elides the expert refinement step. The actual structure is *amateur curiosity → AI generation → expert verification → expert refinement → result.* The headline reduces this to *amateur + AI = result.* PATTERN_NARRATIVE_INFLATION exists precisely to flag this kind of compression that loses the load-bearing step.
- **PATTERN_SHADOWS_ON_WALL.** The article presents a single lens (lottery-ticket framing: "ChatGPT did it") on a multi-lens reality. The substrate would demand the multi-lens version: what did ChatGPT contribute, what did Tao/Lichtman contribute, what role did Price's curiosity play, what's the base rate? Each lens reveals a different contribution; collapsing them into one narrative loses the structure that made the result possible.

**Verdict:** the process narrative is killed. Goes to the kill ledger with residue *"frontier model successfully transferred a known operator from adjacent mathematical area; base rate of such successes is unmeasured; expert refinement was load-bearing and elided in popular framing."*

## Where the substrate gets productive instead of just judgmental

The kill of the *narrative* doesn't waste the *signal*. Per `feedback_weak_signals_are_threads`, the residue from this kill is exactly the kind of MAP-Elites thread Maieutēs is designed to mine. The pattern — *frontier-model prompts on classical conjectures sometimes surface formula-transfer between adjacent mathematical regions* — is gold as exploration material, even if the specific event is one lottery ticket.

The candidate Maieutēs would write into `aporia/mathematics/incubator/`:

```
candidate_id: M-2026-04-26-001
from_kills: [K-2026-04-26-001]  # the inflated narrative kill
reframing: "Frontier-model prompts on classical open conjectures may have a non-trivial hit rate
            for surfacing operator-transfer between adjacent mathematical regions. The
            primitive-sets result is an existence proof; the rate is unmeasured."
mutation_type: cross_region_lift
track_a_test_proposal: "Run a measured probe: select N=100 Erdős problems from Aporia's catalog,
                        generate proof attempts via three frontier models, route surviving
                        outputs to expert reviewers (or Lean tactic search) and measure refinable-
                        proof rate. The base rate is the actual interesting quantity."
status: open
```

The probe becomes a new Track A investigation. If the hit rate is 1/200, lottery framing is correct. If 1/20, we have a methodology. If 1/2, we have a new tool. **None of those numbers exist yet.** The substrate's response is to demand the measurement, not to celebrate or dismiss the anecdote.

## Conversion to calibration anchors

This article is exactly the kind of borderline external example our calibration suite needs. Two anchors added to `aporia/calibration/battery_calibration.jsonl` (created today as the first calibration corpus entries):

- **CAL-2026-04-26-001** — true positive (the proof itself), expected battery outcome: **promote** with Lean-verification escalation.
- **CAL-2026-04-26-002** — true negative (the "vibe maths solved it" process narrative), expected battery outcome: **kill** under PATTERN_SELECTION_BIAS + PATTERN_NARRATIVE_INFLATION + PATTERN_SHADOWS_ON_WALL.

Running our battery against this pair tests whether it correctly distinguishes verified mathematical claim from inflated process claim — exactly the discrimination the substrate is built to perform. If the battery passes both correctly, it has demonstrated the asymmetry our doctrine demands. If it fails either, we have information about which tests are mis-calibrated.

## Cross-cuts to current doctrine

- **`feedback_tensor_first`:** the operator-transfer mechanism ChatGPT executed (apply formula from adjacent area to primitive sets) is precisely what cross-region TT bond-rank discovery is meant to systematize. One-off lottery ticket here; routine signal in the grown-up substrate. Validates the tensor-first prioritization.
- **`feedback_frontier_models_window`:** the result was produced by GPT-5.4 Pro at a specific moment in time. Whether subsequent model versions reproduce the capability is genuinely uncertain. Reinforces the imperative to extract durable artifacts (this discussion + the calibration anchors + the Maieutēs probe spec) from frontier-model outputs while access is still affordable.
- **`feedback_weak_signals_are_threads`:** the kill of the narrative produces a weak-signal residue (the operator-transfer pattern) that becomes Maieutēs exploration material rather than discarded noise. This is the doctrine working as designed.
- **`feedback_ai_to_ai_inflation`:** the article is a public example of the failure mode the doctrine warns against — narrative compression in service of an aesthetic story (amateur + AI = breakthrough) at the cost of the load-bearing expert-verification step. Worth keeping as a cautionary anchor.
- **Two-track epistemics v1.2:** what happened informally for primitive-sets (Price posted to a mathematician who knew the field; expert refinement produced verified result; community accepted the proof) is exactly the social pipeline the substrate aims to industrialize via Track A → Maieutēs incubator → Track A re-investigation → Synthesizer promotion. Validates the two-track design.

## Recommended actions

1. **Create `aporia/calibration/battery_calibration.jsonl`** — first two anchors from this article. Done in this session.
2. **Open Maieutēs probe candidate** — design and queue `M-2026-04-26-001` as the operator-transfer-base-rate measurement. Pending two-track epistemics implementation.
3. **Cite this discussion in the next NORTH_STAR drift report** — public example of the substrate's discipline applied to an external claim; useful for explaining what the calibration suite is for.
4. **Open question for the team:** at what hit rate does "frontier-model operator-transfer on classical conjectures" become a methodology worth incorporating into the substrate's regular operations vs. a lottery worth ignoring? Aporia's intuition: 1/50 or better justifies inclusion as a standing exploration probe; below that, it's noise.

---

*Aporia, 2026-04-26. The substrate's discipline applied to a public AI-assisted result. The math is real and worth incorporating; the story is at best a single lottery ticket and at worst a methodology dressed up as a singular event. Demand the base rate. Mine the pattern. Do not promote "vibe maths" as a method.*
