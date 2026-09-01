# GEN-2 DRY-RUN CAMPAIGN — DESIGN DRAFT (not frozen)

Status: DRAFT, 2026-09-01. Freezes only against a HARMONIA-QUALIFIED
release (requalification of DFX-1..4 must pass first). Everything here
is subject to that gate and to operator review.

## Why this design

The dry run should (a) exercise every fixed path under real scientific
load, (b) produce a result with standalone value even if it is mostly
failure landscape, and (c) test the one thing gen-2 exists for that no
prior instrument had: EPISTEMIC TOPOLOGY as a first-class experimental
variable. The engine's sharing policies, forks, and budgets were built
for ecology experiments; nobody has run one through it yet.

## Question (draft)

Does failure-sharing between otherwise-isolated searchers improve
discovery efficiency at matched total budget, on a deterministic toy
search world, relative to full isolation and to full sharing?

This is the program's metabolization thesis (failures-as-food; PULSE
B-006 consumption-pathway hypothesis) in its smallest executable form,
with the topology enforced BY THE INSTRUMENT rather than by convention.

## Design sketch

- One deterministic toy search task (e.g., hidden 24-bit target,
  score = matched-bit fraction; worker-executed, seedable, trivially
  auditable). The task is deliberately shallow: the OBJECT of study is
  the topology, not the task.
- One parent world per arm, checkpointed, then forked into K=4 sibling
  searchers per arm (engine fork = shared immutable prefix).
- Arms (sharing_policy is the single manipulated variable):
    A1 ISOLATED            (no imports)
    A2 FAILURES_ONLY       (siblings import each other's failures)
    A3 FULLY_SHARED        (everything importable)
    A4 SHAM topology       (FAILURES_ONLY but imports are shuffled
                            junk failures — controls for import
                            overhead/side-effects)
- Matched budgets per arm, enforced by the engine's (fixed,
  authoritative) debit path — the budget IS part of the test: an arm
  finishing under a violated budget is a harness failure, not science.
- Every hypothesis/prediction registered PROSPECTIVELY through the
  fixed ordering path; every dead-end recorded as a first-class
  failure; sibling consumption of imported failures measured via the
  engine's own failure-consumption accounting.
- Primary endpoint (draft): best-score-at-budget per arm, K siblings x
  S=5 seeds, arm-level comparison with permutation null. Secondary:
  failure-consumption rate vs improvement attribution (the engine's own
  caveat — consumption != benefit — becomes a measured question).

## What this exercises per requalified path

DFX-1 fix: all predictions prospective by construction; one deliberate
late-prediction attempt included as a live control (must be rejected or
downgraded — the regression test running in production).
DFX-2 fix: budget debits authoritative; the sham arm's import overhead
tests debit fairness.
DFX-4 fix: nested config (budgets, sharing) strict.
DFX-3 fix: campaign artifacts bind to the wire-reported release.
Plus: forks, checkpoints, topology groups, imports, workers, failure
queries — the full surface under real load.

## Value under failure

If the engine misbehaves: every defect lands in a running scientific
context with a minimal repro — exactly the failure landscape requested.
If the science nulls: "failure-sharing buys nothing at this scale" is a
real datum against the metabolization thesis's smallest form, and the
design transfers upward. If it positives: first instrument-enforced
evidence that epistemic topology matters, worth a real successor.

## Claim ceiling (pre-committed)

Toy task, K=4, one topology family, engine-mediated sharing only.
Nothing about reasoning operations; nothing about substrate geometry;
a directional datum about SHARING TOPOLOGY x SEARCH EFFICIENCY under
this engine's semantics, at most.
