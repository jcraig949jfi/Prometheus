# The RSI experimental program, v2 (DESIGN, NOT FROZEN)

Currency: 2026-09-18. Author: Aphrodite. Supersedes
designs/RSI-1_TRANSPLANT_TEST_DRAFT.md (kept, marked). Built from: the
first relayed review (RSI-1), the Gemini Pro and ChatGPT reviews
(prompts/2026-09-18_rsi1_reviews/), and the seat's adjudication
(designs/RSI_PROGRAM_ADJUDICATION_2026-09-18.md; item ids in [brackets]).
Not a preregistration. Nothing here is launched by this seat; other
seats named are PROPOSED owners, not asked.

Question: does an autonomous, population-based improvement process
produce transferable improvement in its own improvement operator, beyond
memory accumulation, fixed search, replay, selection or evaluator
exploitation?

## 1. Campaigns [F1]

C0 INSTRUMENT CALIBRATION (CPU; this seat can do it). The assay is shown
   to return the right verdict on synthetic lineages with KNOWN truth:
   planted dividend -> SUPERIOR; no dividend -> EQUIVALENT (with enough
   lineages) or INDETERMINATE (without); memorised vault -> caught;
   planted module effect -> attributed to the right module by necessity
   and sufficiency; exploiter-flagged lineage -> separated. Outputs: power
   and equivalence curves vs number of lineages, families and instances;
   the delta proposal. Includes the finished toys (E1-E4, S1-S4).
C1 DOES THE IMPROVEMENT OPERATOR TRANSFER? Second order only. Runs only
   after C0 passes and the operator adopts delta, budgets and substrate.
C2 THIRD ORDER. Only if C1 returns SUPERIOR on C2-layer vaults with the
   decomposition holding, and the assay's controls were stable in C1.

## 2. The improvement operator I_0 [C1-C5]

Typed Python modules under a fixed protocol; the mutation space is code,
not prompt strings. Five modules, three timescales:

    module      acts          I_0 baseline
    SEARCH      within task   N independent samples
    VERIFY      within task   run visible tests, pass/fail
    ALLOCATE    within task   uniform split of the task escrow
    MEMORY      across tasks  FIFO of last 3 failures (typed store,
                              fixed read protocol)
    EVIDENCE    across gens   aggregate outcome statistics only

Generation step: I_t receives its own source, its outcome statistics and
its metered spend, and proposes a diff. Two-phase commit: the diff must
compile, keep the protocol, and pass a null task (no loop, no budget
exhaustion) in the sandbox; rejected diffs are archived, not deleted.

## 3. Worlds [B1-B2]

    A   development: visible, feedback
    B   promotion: hidden from I, scored by an external evaluator
    C1  vault: future instances of committed families
    C2  vault: future instances of SEALED families never exposed
    C3  vault: families written after the freeze by a seat with no
        access to the lineages
Generators are hashed into a Genesis manifest before generation 0; vault
seeds come from a named public future-entropy beacon (and a named
fallback) resolving after the scheduled freeze; instantiation happens in
a network-isolated clean room; only serialised instances are mounted,
read-only. The beacon also binds the experimenters: no re-rolling.

## 4. Metering [E1-E4]

All model calls and execution pass a proxy below I_t. Per-task escrow in
a Standardized Inference Cost (fixed per-model tariffs on input and
output tokens; NOT claimed as FLOPs); accelerator seconds recorded too
where the GPUs are Prometheus's. Hard stop on exhaustion = task failure.
Per-module attribution by unforgeable resource handles, never by call
stacks. Proposed owner: Harmonia (not asked).

## 5. Endpoints [A1-A6]

PRIMARY: Delta(B) = C(I_8(A_0); B) - C(I_0(A_0); B) on C2, at each
preregistered escrow B1 < B2 < B3 (at least one below and one above the
evolution budget). Verdict per budget: SUPERIOR (CI above +delta),
EQUIVALENT (CI inside [-delta, +delta]), INFERIOR, or INDETERMINATE.
Frontier claim: SUPERIOR at every budget in a preregistered range.
delta: fixed from downstream need before any C1 data, in tasks solved
per fixed escrow (proposal due from C0).
SECONDARY (descriptive): R_t; imp@k and metaproductivity (for
comparability with Hyperagents arXiv 2603.19461 and HGM); per-module
spend; code size and complexity per generation.
PATTERNS: advantage on A but not C = specialisation; on C1 but not C2 =
family memorisation; on M_8 only = memory-mediated.
Analysis: hierarchical (lineage > family > instance); C0 validates the
hierarchical bootstrap against known variance components.

## 6. Transplant and decomposition [D1-D4]

Factorial: {I_0, I_8} x {M_0, M_8} (x {A_0, A_8} if workers evolve),
improver-to-seed assignment permuted. Decomposition, preregistered in
full: I_8 minus each evolved module (necessity), I_0 plus each evolved
module (sufficiency), pairwise where first-order effects suggest
interaction; EVIDENCE tested on the improvement phase, not task score;
protocol-incompatible swaps reported UNDEFINED. Lineages that ever
exploited an evaluator hole are flagged and every result reported with
and without them.

## 7. Conditions (from RSI-1, retained)

FIXED-IMPROVER; MEMORY-RSI; ARCHIVE-RSI (+ replay); FULL-RSI (+ replay),
compute-matched on the metered cost.

## 8. Claims ladder [F2, F3]

1. I_8(A_0, C2) > I_0(A_0, C2) at matched escrow.
2. The same across the budget range (frontier moved).
3. Necessity: removing implicated evolved modules destroys it.
4. Sufficiency: adding them to I_0 partly recreates it.
5. (C2 campaign) I_8's own descendant I'_8 has a larger transplant
   advantage than its parent.
6. Some of it survives a model-substrate transplant.
A null is stated only in the narrow form: "under the specified
substrate, task ecology, mutation language, compute regime and
evolutionary horizon, observed cumulative capability gains did not
produce a detectable transferable improvement in the improvement
operator."

## 9. Decisions for the operator

- Charter (APHRODITE-08). Both reviews and the seat lean yes.
- Go for Campaign 0 on CPU now (seat's lean: yes; it is thought work plus
  a synthetic-data assay, no GPU).
- Whether Aphrodite may ask Archaeon, Harmonia, Vivarium, Daedalus,
  Proteus and Necropolis about the roles both reviews assign them.
- Later, for C1: substrate(s), host (M1/M2 RTX 5060 or RunPod), delta,
  budget grid.
