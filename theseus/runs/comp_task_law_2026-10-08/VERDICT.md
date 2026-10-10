# THESEUS-37 verdict (prereg roles/Theseus/prereg/2026-10-08_law_necessity/, e77ae8d76)

Runs: LAW-ON = 36's TASK0-SEL v0_2t0_2026-10-08; LAW-OFF = PYTHONHASHSEED=0 python -m
theseus.synth.run_v0 --tag v0_2t0nl_2026-10-08 --quality task0 --no-law (all other flags
identical; the law is generated -- identical RNG draws -- but not inserted).
Eval: python -m theseus.synth.task_comp --tag comp_task_law_2026-10-08 --a v0_2t0_2026-10-08
--b v0_2t0nl_2026-10-08. LAW-ON rows recomputed identically to 36 (91 solvers, mean J .923975).

GATE: 1-part controls .195-.203; 2-part controls 1.0. PASSES.
PRIMARY H-LAW-NEEDED: D solvers LAW-ON 91/100 (mean J .924) vs LAW-OFF 52/100 (mean J .615);
one-sided Fisher p 3.9e-10. VERDICT: SUPPORTED -- under task selection, the collision-generated
k-ary interaction laws (the concept-tensor laws) are causally needed for the capability gain at
this budget. Without them, task selection reaches about the unselected baseline (36's REP-SEL
59/100; 36b unselected D 60/100).

Descriptive (knockouts on LAW-OFF solvers): essential-rule counts 0/1/2 = 16/22/14 (redundant
solutions 31% vs 51% LAW-ON). Essential parts without laws: evolved Tyche lenses (lensmap 13),
G0-provenance rules (diffuse 11, threshold 8, react 4), mutation inserts (coarse 6, remember 3,
recall 3, diffuse 1). With laws, 41/42 essential react rules are collision-generated laws.
Reading: when the ecology may generate its own interaction laws, task selection builds on them
and on redundant paths; when it may not, it falls back on human-derived G0 rules and evolved
lenses and reaches far fewer solvers.

Predictions: L1 gate RIGHT; L2 H-LAW-NEEDED supported RIGHT.
