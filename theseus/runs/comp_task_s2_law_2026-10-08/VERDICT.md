# THESEUS-38 verdict, H-LAW-NEEDED-S2 (prereg roles/Theseus/prereg/2026-10-08_replicate_36_37/, f4d41ca6d)

Fresh master seed 20261009; otherwise identical to 37.
Runs (PYTHONHASHSEED=0, common flags in the prereg):
  LAW-ON  v0_2t0_s2_2026-10-08   (--quality task0)
  LAW-OFF v0_2t0nl_s2_2026-10-08 (--quality task0 --no-law)
Eval: python -m theseus.synth.task_comp --tag comp_task_s2_law_2026-10-08
--a v0_2t0_s2_2026-10-08 --b v0_2t0nl_s2_2026-10-08 --workers 2.
The LAW-ON rows are identical to those in comp_task_s2_sel_2026-10-08: 78 solvers, mean J .821.

GATE: 1-part controls .195-.203; 2-part controls 1.0. PASSES.

PRIMARY: D solvers (J >= .6), 100 viable DEEP+VERY_DEEP children per run:
  LAW-ON 78/100 (mean J .821) vs LAW-OFF 66/100 (mean J .708); one-sided Fisher p .0414.
VERDICT: SUPPORTED. Under task selection, removing the collision-generated k-ary laws lowers
the share of deep solvers on a second master seed.

Size: about a third of the 37 effect. Seed 20260930 gave 91 vs 52 (+39 points); seed
20261009 gives 78 vs 66 (+12 points). The test is just under the threshold. A third seed
would be needed before quoting any size beyond "positive on both seeds".

Attribution (knockouts on every solver; python -m theseus.synth.ko_prov):
  essential-rule counts 0/1/2/3: LAW-ON 34/30/14/0, LAW-OFF 21/14/27/4
  essential-rule provenance:
    LAW-ON:  law 38, G0 9, mutation edit 9, lens 2
             (32/78 solvers rest on a law; 23 law rules write the sensor channel)
    LAW-OFF: mutation edit 54, G0 20, lens 6 (no laws exist)
  LAW-OFF essential op sets are led by coarse+threshold 9, coarse 6, coarse+react 5,
  coarse+coarse 4.
Reading, replicated: when the ecology may generate its own interaction laws, solvers build
on them. When it may not, it falls back on mutation-edited rules, human-derived G0 rules and
evolved lenses, and more of its solvers need two or more essential parts (31/66 vs 14/78).
The capability cost of removing the laws is smaller on this seed.

Predictions:
  M2 (H-LAW-NEEDED-S2 SUPPORTED, p .7) RIGHT.
  M3 (both SUPPORTED, p .55) RIGHT: the pair is REPLICATED by the preregistered rule.
    With the H-SEL-SOLVE-S2 verdict, both 36 and 37 hold in direction and significance on a
    second seed, at roughly half and a third of their first-seed sizes.
