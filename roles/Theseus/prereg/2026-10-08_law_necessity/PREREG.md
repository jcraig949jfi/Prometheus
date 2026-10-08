# THESEUS-37 preregistration -- are the collision-generated laws causally needed for capability?

Currency: 2026-10-08. Committed before the run.

## Why

36 (47498bbe0): task selection raises deep solvers of the composition-necessary task to 91/100,
and where a solver has an essential rule it is mostly a collision-generated k-ary interaction
law (41/42 essential react rules). Knockouts show the laws are used; they do not show the
ecology NEEDS them (other parts could take over if laws never existed).

## Design

LAW-OFF: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2t0nl_2026-10-08
--quality task0 --no-law --g0-readers --cond-ops --aligned-binding --ecology-only
--elite-grids pca --pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150 --seed-select 1.5
--workers 4 (identical to 36's TASK0-SEL run v0_2t0_2026-10-08 except --no-law: the law is
generated, so every RNG draw is unchanged, but not inserted).
Eval: python -m theseus.synth.task_comp --tag comp_task_law_2026-10-08
--a v0_2t0_2026-10-08 --b v0_2t0nl_2026-10-08 (same J, solver threshold and knockouts; the
36 J rows for v0_2t0 are recomputed identically -- deterministic).

## Decision rule

GATE as 36. PRIMARY H-LAW-NEEDED: D solver share LAW-ON (a) > LAW-OFF (b), one-sided Fisher
p < .05 -> SUPPORTED (the generated laws are causally needed for the capability at this
budget); LAW-OFF share >= LAW-ON share -> NOT SUPPORTED (the ecology finds other routes);
else INDETERMINATE. Descriptive: LAW-OFF solvers' essential ops.

## Predictions

L1 gate passes.                                 p = 0.9
L2 H-LAW-NEEDED SUPPORTED.                      p = 0.55

Compute: one ecology-only run with task0 J (~45 min) + eval (~40 min).
