# Cycle 055 — PRE-REGISTRATION: running the Lane A/B reading experiment (O-4)

Executes `LANE_AB_READING_EXPERIMENT.md`, pre-registered cycle 041 and never run. The original
design stands; this file fixes only what that one left open — **the population** and **how one
agent runs two lanes that are supposed to be blind**.

## What the original measured and left unmeasured

```
P(found | INCIDENTAL reading, bug not the question)  =  0 / 11    measured
P(found | TARGETED review,   bug IS the question)    =  unmeasured
```

I have been acting on *"reading does not work for this class"* without having earned it.

## Population — committed before opening any of them

Cross-role substrate (HITL #221 permits it), selected **mechanically**: non-test functions whose
names match a measure-like pattern (`rate|ratio|fraction|frequenc|disagreement|means`) in roles
other than mine. **I have not opened any file below.**

```
1  ergon/meta/trajectory.py:88                       stall_fraction
2  ergon/learner/descriptor.py:394                   compute_fill_rates
3  ergon/learner/triviality.py:419                   compute_trigger_rate
4  ergon/learner/diagnostics/per_class_hit_rates.py:191  per_seed_rates
5  ergon/meta/fitness.py:50                          compute_disagreement
6  ergon/learner/operators/anti_prior.py:102         compute_genome_atom_frequencies
7  ergon/learner/inference/ablation_e007_ab.py:138   _hit_rate
8  charon/diagnostics/compute_per_domain_pi0.py:56   bootstrap_ci_from_seed_means
```

**Negative control (9):** `charon/agents/stygian/loaders/_mahler_composition_helpers.py:67
survival_fraction`. Its test file already contains `test_survival_fraction_empty`, so the
degenerate case is **known handled**. Both lanes should score it CLEAN. **A lane that flags the
control is producing false positives**, and its score on the other eight cannot be read.

## Blinding, since one agent runs both lanes

The original says "run blind to each other's findings", which no single agent can do
simultaneously. **Lane A runs first and its verdicts are committed to git before Lane B is
written.** The commit hash is the blind. Lane B may then be built without the ability to
retro-fit Lane A's answers.

## Lanes

- **Lane A — targeted review.** Read source only. Answer one question per function: *what does
  this mean on zero observations / an empty domain / no comparable pair, and is that
  semantically different from its ordinary negative result?* Verdict: `FLAG` or `CLEAN`.
- **Lane B — executable probe.** Call each with a degenerate argument and a minimal legitimate
  one; compare. Verdict: `FLAG` or `CLEAN`.

## Predictions, with confidence and difficulty

All **OPEN** — I have opened none of these files.

1. **Lane A scores much better than 0-for-11** — at least 2 flags of 8. Confidence **moderate**;
   difficulty **OPEN**. *Opposite outcome:* if Lane A scores ~0, the categorical claim
   ("reading cannot detect this class") is **supported after all**, and I must say so — that is
   the result the cycle-041 file exists to protect.
2. **Lane B flags at least as many as Lane A.** Confidence **moderate**; **OPEN**.
   *Opposite:* Lane A beating Lane B would mean my "use tools" posture is backwards for this
   class, which is a bigger finding than confirmation.
3. **The lanes are NOT identical — union > intersection.** Confidence **moderate-to-high**;
   **OPEN**. *Opposite:* perfect agreement means one lane is redundant, and the cheaper wins.
4. **Both lanes score the negative control CLEAN.** Confidence **high**; **OPEN**.
   *Opposite:* a flag on the control invalidates that lane's other scores this cycle.
5. **At least one FLAG is a genuine defect** (not merely an undocumented convention).
   Confidence **low-to-moderate**; **OPEN**. *Opposite:* all flags being conventions means the
   checklist detects *style*, not bugs, and the experiment measured the wrong thing.

## Reporting rule (inherited, restated)

Report Lane A's score whether or not it flatters the conclusion I have been acting on. **A
result that overturns it is the more valuable one.**

## Scope

**Read-only on other roles' code this cycle.** Cross-role fixes are permitted (#221) but
cross-role *science* is not, and a flagged function's semantics are its owner's call. Findings
go to the owner; no diffs.

*— Techne, cycle 055, before opening any file in the population.*
