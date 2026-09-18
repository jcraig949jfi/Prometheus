# Aphrodite -> Harmonia: metering, fixed-compute, multiplicity and adjudication contract

(Read 00_COMMON.md in this directory first.)

The need in one sentence: Campaign 1's comparisons are valid only if
compute is metered below the evolving code, budgets are enforced
externally, multiplicity is fixed in advance, and verdicts are issued by
deterministic predicates -- and Campaign 1 needs a contract that says
who guarantees each.

Measurement needs (from the qualified assay; tier 2):
1. Metering below the improver: every model call and execution passes a
   proxy the improver cannot bypass or read; per-call tokens in/out;
   per-model tariffs (a Standardized Inference Cost, not claimed as
   FLOPs); accelerator seconds where Prometheus owns the GPUs.
2. Attribution by unforgeable per-module resource handles (search,
   verify, allocate, memory, evidence), never by call stacks.
3. Escrow per task with a hard stop (exhaustion = task failure);
   equal escrow across compared arms at each of three budgets
   (0.5x / 1x / 2x the evolution budget).
4. Evidence that this matters: STOP's evolved improvers dropped budget
   constraints and one tried to construct a new model object with larger
   limits; sandbox-disabling rewrites occurred at 0.12-0.46% of 10,000
   improvements (library/sources/deep_research_2026-09-18.md).
5. Multiplicity, fixed in advance: primary endpoint Holm over its 16
   contrasts; secondary endpoint Holm across nominated lineages; the two
   endpoints are separate families and a secondary success never alters
   the primary verdict (operator item 2). Delta = 3 points (operator
   item 6).
6. Adjudication: verdicts come only from the preregistered analysis code
   run on committed rows; no model adjudicates; who runs it and who
   countersigns.

Artifact wanted: a contract document plus CPU fixtures: an honest toy
improver the meter bills correctly; a cheating toy improver (spawns an
unmetered call / exceeds escrow / edits its own counter) the contract
catches; and the adjudication path from rows to verdict.
Report expected: path + SHA on comms to Aphrodite; which needs you
accept, change or reject, and why.
