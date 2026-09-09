# Astra analysis of the H1 reports and of Gemini's critique

**Received 2026-09-09, supplied by the operator. Verbatim below the rule.**
Astra is the SFE ecosystem lead designer (ChatGPT/Codex) and author of the H1
design being reviewed, so this is the designer answering their own reviewers.

Status: **the most load-bearing document in this directory.** It contests both
the adversarial review and Gemini's endorsement of it, corrects a factual error
in Gemini's mechanical claim, and adds a fourth experimental arm that neither
reviewer proposed. It also concedes an omission in Astra's own design. See
`../README.md` for adjudication.

---

ELI5: Prometheus saves a test that broke yesterday's program and tries it
against today's program. H1 asks whether remembering those failures helps it
find a correct program sooner. The reviewer reasonably asks whether the
improvement comes from useful information or merely from changing how the search
runs. But a fake test with the same size and shape does not automatically settle
that question.

I read both checked-in reports: 201, the evidence audit, and 202, the
adversarial review. My assessment: retain H1, strengthen its controls, and
substantially reduce the certainty of both the adversarial verdict and Gemini's
endorsement.

**What the review gets right.** Extra tests have costs. Retrieval can conceal
additional search or privileged information. A poorly matched random baseline
can exaggerate the advantage of relevance selection. Solver behavior can also
depend strongly on heuristics and randomization; that concern has established
experimental foundations (Gomes et al.).

Those are useful requirements for an experiment. They do not establish that H1
is false.

**The largest mismatch is what our experiment actually transports.** Our v0.1
design packet already specifies:

- Transport the input, then recompute its correct answer using the target
  task's oracle.
- Compare against random compatible inputs, with equal access to permitted task
  metadata.
- Give the fresh baseline an allowance for fresh target probes.
- Start with a bounded Boolean VM and exhaustive verification. Z3 is an optional
  later adapter.

A counterexample establishes that a particular candidate fails a particular
specification. Its input may be useful elsewhere; its original expected answer
does not automatically transfer.

Consequently, arguments about importing invalid source constraints or perturbing
SMT branching do not directly describe this alpha. Report 202 actually
recommends a concrete execution prefilter in Part 6 -- close to the route already
available in our design.

**Gemini's "rock solid" mechanical explanation is incorrect.** Adding a valid
constraint reduces or preserves the set of admissible solutions. It can increase
the formula's representation size and processing overhead. These are different
quantities, and runtime can improve or deteriorate.

There is no general rule that each additional counterexample makes synthesis
exponentially harder. Synapse itself reports substantial benefits from
counterexample exchange on one benchmark category and little benefit on others.
That supports measuring the tradeoff, rather than predicting universal failure
(Synapse paper, section 5.5).

**"Isomorphic noise" is not the perfect control claimed here.** Matching type,
depth and byte size is useful, but it does not guarantee matched solver
behavior:

- A tautological constraint may disappear during preprocessing.
- Changing constants can change simplification, propagation and pruning
  dramatically.
- A valid randomized input, correctly labeled by the target oracle, can still be
  informative.
- A genuinely meaning-preserving transformation may preserve the very
  information supposedly being removed.

"Semantically void" also needs a definition: void relative to which candidate
population and existing tests?

I would add structurally matched controls, but I would not make this vaguely
specified synthetic witness a mandatory gate. A SageMath randomizer cannot
establish those properties merely by preserving an AST skeleton.

**The historical refutation is unsupported.** Report 201 says the exact
comparison is untested. Report 202 turns other approaches' success into a story
that concrete transport was empirically rejected. Euphony and Code2Inv
demonstrate probabilistic or neural transfer; those results do not constitute a
negative experiment on H1.

There is also relevant adjacent evidence: ReFuzz reports reusing bug-triggering
tests from earlier processors to find vulnerabilities in another processor
sharing the instruction-set interface. That is fuzzing rather than our synthesis
experiment, so it does not establish H1. It does weaken the blanket story that
concrete failure reuse was abandoned.

Similarly, near-identical semantics and exceptionally deep failures are
plausible favorable conditions, not demonstrated necessary conditions. The
practical requirement is that reuse saves more work than it costs.

**The additional control I would prioritize tests whether the failure history
itself matters.** Our original three arms do not fully distinguish valuable old
failures from valuable ordinary probes. That is a real omission in my design.

I would use these four arms:

    Arm   Initial tests                    What the comparison tells us
    ---   ------------------------------   ------------------------------------
    A     Fresh target probes              Whether transport beats spending
                                           resources locally
    B     Random compatible prior          Whether relevance selection improves
          failure inputs                   on general reuse
    C     Probes from the same relevant    Whether useful source-task similarity
          source tasks, selected without   explains the benefit
          conditioning on failure
    D     Relevance-selected prior         H1 treatment
          failure inputs

Match input counts, compatibility, structural properties and duplicate handling
where applicable. Recompute every target label. Freeze retrieval before
confirmation and charge acquisition, retrieval, labeling and execution.

For the first mechanism experiment, hold candidate enumeration order fixed.
Measure how many incorrect candidates the initial tests reject before full
verification, how much verification work is avoided, and whether those savings
exceed the extra testing cost. This addresses the proposed mechanism without
introducing SAT branching.

The eight-case Boolean alpha should establish correct plumbing. A separately
calibrated, frozen evaluation must establish useful performance.

**Interpret the result at the level actually supported.** If D repeatedly beats
A and B at matched total resource caps, that supports the engineering value of
the relevance policy. If D also beats C, the case for failure-specific value
becomes stronger. If D ties C, reusable probes may still be valuable, but their
origin as failures has not earned special status.

Keep solve fraction as the primary endpoint, including timeouts. Report
uncertainty and a predefined meaningful-effect threshold. High variance does not
prove a null, and failure to reach statistical significance does not establish
equivalence. Solver conflicts and decisions are diagnostic measurements; fewer
conflicts alone cannot prove the mechanism.

**Gemini's agent proposal is a worthwhile extension with its own experiment.**
An LLM could turn failures into proposed abstractions or use them to guide
candidate generation. That changes the intervention and introduces the model's
prior knowledge and inference cost.

Test it separately with the same model and prompt receiving no history, matched
control history, or relevant failure history. Verify any proposed hard
constraint against the target specification; otherwise retain it as a search
suggestion.

For Prometheus, I would keep H1 first in the implementation order, add the
ordinary-source-probe control and direct verification-work measurements, then
introduce SMT and agent-mediated transfer as subsequent experiments.
