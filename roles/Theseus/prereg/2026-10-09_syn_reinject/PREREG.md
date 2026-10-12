# THESEUS-39 preregistration -- SYN re-injection: do compressed synthetic concepts work as tensor matter?

Currency: 2026-10-09. Committed before the two ecology runs, the evaluation and the reproduction
pass. Code: theseus/synth/syn_inject.py, syn_repro.py, run_v0.py (--inject); blob hashes in
CODE_HASHES.txt next to this file.

## Why

The charter's recursive concept formation step: candidates that repeatedly produce useful
behaviour are compressed into SYN concepts (THESEUS-13: 20 admitted from v0_2t0_2026-10-08,
every one a replicated solver of the composition-necessary task whose essential step is a
collision-generated law). The open question is whether such concepts are useful MATTER: when
they are put back into a fresh ecology as collision parents, do its deep descendants solve
the task more often than when equally deep, same-lineage, NON-solving matter is put back?

## Design (master seed 20261009; flags as THESEUS-38 S2-TASK0)

Common: PYTHONHASHSEED=0 --quality task0 --master-seed 20261009 --g0-readers --cond-ops
--aligned-binding --ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5 --workers 4
  INJ-S  --inject theseus/archive/inject_S_v0_2t0_2026-10-08.jsonl   tag v0_2t0_s2_injS_2026-10-09
  INJ-M  --inject theseus/archive/inject_M_v0_2t0_2026-10-08.jsonl   tag v0_2t0_s2_injM_2026-10-09
  N      no injection = THESEUS-38 S2-TASK0 run v0_2t0_s2_2026-10-08 (already run; not re-run)
Injection sets (python -m theseus.synth.syn_inject; built before this prereg, files committed
with it):
  S  the 20 admitted SYN genomes, with their recorded generation (6-20).
  M  per SYN concept, one viable DEEP/VERY_DEEP mechanism of the same source run with
     task J < .6 (non-solver), not a SYN source, generation within the smallest window
     (0, 1, ...) of the SYN concept's, rule count within 1; seeded order 20261009.
Injected genomes enter at gen 0 as parentless synthetic mechanisms (lane INJECT), evaluated
exactly as children are; they are never in the D sample (DEEP/VERY_DEEP lanes only), they are
eligible as parents like any synthetic of their generation (DEEP, SHALLOW, G0 lanes; not
VERY_DEEP, which needs synthetic grandparents).
Known asymmetry (seen in the smoke run, before this prereg was committed): because injected
genomes carry generations 6-20, the DEEP and VERY_DEEP lanes open from gen 1 in INJ-S and
INJ-M (children of a parentless synthetic count as having synthetic grandparents), whereas in
N they open only once natives reach generation 5. INJ-S vs INJ-M share this property, which is
why M, not N, is the primary comparator. S1/S2 against N are confounded by lane timing and are
descriptive only.
Eval: python -m theseus.synth.task_comp --tag comp_task_syn_2026-10-09 --a v0_2t0_s2_injS_2026-10-09
--b v0_2t0_s2_injM_2026-10-09 --workers 4 (gate inside, as 36/38).

## Primary

H-SYN-SOLVE: D solver share (J >= .6, task_comp sample of 100 viable DEEP+VERY_DEEP children)
INJ-S > INJ-M. GATE as 36. SUPPORTED iff one-sided Fisher p < .05; NOT SUPPORTED iff INJ-S
share <= INJ-M share; else INDETERMINATE.

## Secondary (descriptive unless stated)

S1  INJ-S vs N (78/100 in THESEUS-38): one-sided Fisher, reported, not a verdict.
S2  INJ-M vs N: does adding deep NON-solving matter change the rate (two-sided Fisher)?
S3  Solver-by-generation table per run from the in-run task J (200/200 episodes) of every
    viable DEEP/VERY_DEEP child: per generation, born / solvers; first generation with a
    solver; for INJ-S and INJ-M, the share of solvers with an injected ancestor.
S4  Attribution: in INJ-S solvers, the share whose essential rules (task_comp knockouts) are
    rules copied from an injected genome (rule provenance identical to a rule of an injected
    genome) vs newly generated.
R   Known-mechanism reproduction of the 20 SYN concepts (python -m theseus.synth.syn_repro),
    BEFORE any claim about them:
      R1 battery fingerprint vs the known library (charter phase-4 procedure, tau_rep);
      R2 task fingerprint (8 task variants) vs 75 parameterized hand-built store+release
         mechanisms; REPRODUCED within .05 on every variant, PARTIAL within .15.
    A concept REPRODUCED under R2 is behaviourally indistinguishable, on the task, from a
    hand-written store+release mechanism; any claim then reads "re-derived a known
    mechanism", not "new mechanism".

## Predictions

P1 INJ-S solver share >= .85.                          p = 0.6
P2 H-SYN-SOLVE SUPPORTED.                              p = 0.45 (ceiling: N is already 78%)
P3 INJ-M within 10 points of N (68-88 / 100).          p = 0.6
P4 first in-run D solver generation INJ-S < INJ-M.     p = 0.6
P5 R2: >= 10/20 SYN concepts REPRODUCED or PARTIAL.    p = 0.65
P6 R1: <= 5/20 REPRODUCED_BY_KNOWN.                    p = 0.7

## Language

Whatever the outcome, no claim of "new mechanism" for any SYN concept that R2 reproduces;
"human priors eliminated" is never stated (charter). A supported H-SYN-SOLVE reads: "re-injected
compressed concepts raise the rate at which deep descendants solve the task, relative to
equally deep same-lineage non-solving matter", nothing broader.

## Compute

Two ecology runs (~45 min x 4 workers each), one eval (~40 min), reproduction pass (~20 min):
~8 CPU-hours (MWO R2 per-item cap 16).
