# Gemini Deep Research deck — 2026-09-17

One prompt. Operator-specified topic (not a queue pull): recent reported successes in
recursive self-improvement and their mechanisms. Requested to support Aphrodite (M4),
who is running a self-improvement sandbox.

Substrate-grade gate: the prompt cites three of the five mandated patterns
(PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_PRIME_GRAVITATIONAL_OVERFIT).

### Prompt 1: Recursive self-improvement 2024-2026 — which reported successes survive an attribution audit, and what is the mechanism

```
1. BRIEF SUMMARY

I need a mechanism-keyed inventory of reported recursive self-improvement (RSI) in AI
systems from January 2024 to today, separating results that survive an attribution audit
from results where something other than the self-improvement loop produced the gain. The
consumer is a small research programme that must decide which mechanisms are worth
reproducing on a single-machine bench. Headline numbers from runs we cannot reproduce are
of no use to us; MECHANISMS, with the evidence that they are real, are.

2. FLAGGED FINDINGS — what we currently believe, and where we may be wrong

Treat each of these as a hypothesis to CONFIRM OR REFUTE with primary sources, not as
context to agree with. If the evidence contradicts one, say so plainly and show the rows.

  (a) Most reported RSI is improvement WITHIN A FIXED CAPABILITY ENVELOPE: search,
      scaffolding, prompt or agent-graph optimisation over a frozen base model. The
      weights do not change and the reachable set of behaviours does not grow.
  (b) Reported gains frequently shrink or vanish under genuinely held-out evaluation,
      and especially under transfer to a task family not used during the loop.
  (c) The loop rarely beats a simple equal-compute baseline (best-of-N sampling,
      random restarts, or one-shot generation at the same token budget).
  (d) Compounding is the rare part. Many "loops" report a single round of improvement,
      or a second round whose gain is not conditional on the first.
  (e) Genuine weight-level self-improvement — self-generated data, self-filtered, trained
      on, producing a measured held-out gain that compounds across two or more rounds with
      NO human relabelling between rounds — is rare and may be absent in the public record.

3. PROBLEM STATEMENT

Operational definition to apply. A system qualifies as RSI if it modifies its own
artifacts — weights, code, scaffold/agent graph, training data, or evaluator — and shows a
MEASURED capability gain on tasks held out from that modification process, where the gain
COMPOUNDS over at least two self-directed iterations with no human intervention between
rounds.

Inventory every candidate instance 2024-01 to today, and classify each by which artifact
is modified:
    TIER S  scaffold / prompt / agent graph (frozen weights)
    TIER D  training data (self-generated, self-filtered)
    TIER W  weights (self-directed training or merging)
    TIER E  the evaluator, reward model or verifier itself
State explicitly which tier each instance reaches, and whether it meets the compounding
condition or fails it.

4. STATUS AND BOUNDS

For every instance, give: the number of compounding rounds actually reported; the
magnitude of gain per round and whether it saturates; the exact held-out protocol; the
compute budget; whether any human touched the loop between rounds; and what the authors
themselves claim versus what they measured. Where a number is a projection or an
extrapolation rather than a measurement, label it as such. Where the run is at a scale
no small lab can reproduce (very large agent swarms, frontier-scale training), say so
explicitly rather than reporting the number alone.

5. LITERATURE — PRIMARY SOURCES ONLY

Verify, correct, or delete each of the following candidate lines. I may have misnamed or
misattributed some of them; that is expected, and correcting me is part of the task. Do
not preserve a name I gave if the real work is named otherwise.
    - self-taught / bootstrapped reasoning (STaR-style self-training on filtered rationales)
    - self-improving program generation via a scaffolding optimiser (STOP-style)
    - automated design of agentic systems (ADAS-style meta-agent search)
    - evolutionary code and algorithm discovery with an LLM proposer (AlphaEvolve-style,
      FunSearch lineage)
    - self-modifying agents in the Goedel-machine tradition (Darwin Goedel Machine)
    - automated research pipelines (AI Scientist lineage)
    - RL on self-generated, verifier-filtered data; self-play for reasoning
    - test-time training and continual weight update schemes
    - self-generated curricula and open-endedness (POET, OMNI-EPIC lineage)
    - model merging and self-distillation loops
    - 2025-2026 results with very large agent populations or swarms
For each surviving item: full primary citation with arXiv ID or DOI, authors, date, venue,
and whether it is peer-reviewed, preprint only, or a company technical report.

MANDATORY: flag retractions, withdrawals, and post-publication corrections EXPLICITLY. We
have twice been burned by exactly this — once by a citation pointing at the wrong paper,
and once by treating a problem as solved on the strength of a preprint that was withdrawn
within three days for mathematical gaps. If a claim rests on a withdrawn or corrected
source, that fact is more important to us than the claim.

6. ATTACK VECTORS — the audit to run on every instance

  (i)   EQUAL-COMPUTE BASELINE. Was the loop compared against best-of-N, random restarts
        or one-shot generation at the SAME total compute? A loop that wins only against a
        single sample has not been shown to work. This is PATTERN_BASE_RATE_NEGLECT: the
        improvement must be read against the base rate of the cheap alternative, not
        against zero.
  (ii)  ATTRIBUTION. Did the gain come from the self-improvement loop, or from a stronger
        base model swapped in mid-study, human curation of the candidate pool, a changed
        evaluation harness, or a changed prompt? This is PATTERN_CONDUCTOR_CONFOUND — a
        third variable driving the outcome that the causal story credits to the loop.
        Name the alternative explanation for each instance and say whether the authors
        intervened on it.
  (iii) SELECTION ON THE REPORTED BENCHMARK. Was the improvement selected using the same
        benchmark it is reported on? This is PATTERN_PRIME_GRAVITATIONAL_OVERFIT: fitting
        the measurement instrument rather than the underlying capability. State what was
        held out, in what sense, and whether the held-out set was ever used for selection.
  (iv)  COMPOUNDING. Is round-2 gain conditional on round-1 having happened, or is this
        one-shot improvement presented as a loop? Ask whether the authors ran the ablation
        that would distinguish them.
  (v)   EVALUATOR VALIDITY. Where the system generates or modifies its own evaluator,
        reward model or verifier, what stops it from satisfying the evaluator rather than
        improving? Report any measured evidence of evaluator gaming, and any structural
        mitigation that was shown to work.
  (vi)  WHAT ACTUALLY TRANSFERRED. Any evidence of the gain holding on a task family
        outside the loop's own distribution.

7. CROSS-REFERENCES AND REQUIRED DELIVERABLE

Deliver an inventory table with one row per instance and these columns: system; date;
tier (S/D/W/E); rounds that genuinely compound; held-out protocol; equal-compute baseline
present (yes/no/partial); the strongest alternative explanation for the gain; smallest
faithful reproduction; primary source.

Then three sections:
  A. CLAIMS THAT FAILED THE AUDIT — which reported successes do not survive (i)-(vi),
     and precisely which check they fail.
  B. SMALLEST FAITHFUL REPRODUCTION — for each surviving MECHANISM, the minimum scale at
     which the mechanism itself (not the headline number) can be tested: single GPU,
     ten or fewer agents, order 10^3 evaluations. Separate mechanisms that are testable
     small from mechanisms that are STRICTLY scale-dependent, and for the latter state
     what specifically breaks at small scale.
  C. WHAT A LEGITIMATE ATTEMPT WOULD COST — for the most credible mechanism, the resources
     a serious small-scale attempt would need: compute, evaluation budget, task population
     size, and the human effort that the published versions actually required but did not
     foreground.

Every claim must be attributable to a primary source or marked as your inference. Where
the evidence is absent rather than negative, say "not measured" rather than "no effect".
```
