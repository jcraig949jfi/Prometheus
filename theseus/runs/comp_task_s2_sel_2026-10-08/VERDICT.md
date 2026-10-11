# THESEUS-38 verdict, H-SEL-SOLVE-S2 (prereg roles/Theseus/prereg/2026-10-08_replicate_36_37/, f4d41ca6d)

Fresh master seed 20261009; otherwise identical to 36.
Runs (PYTHONHASHSEED=0, common flags in the prereg):
  S2-TASK0 v0_2t0_s2_2026-10-08 (--quality task0)
  S2-REP   v0_2tr_s2_2026-10-08 (--quality rep)
Eval: python -m theseus.synth.task_comp --tag comp_task_s2_sel_2026-10-08
--a v0_2t0_s2_2026-10-08 --b v0_2tr_s2_2026-10-08 --workers 4.

GATE (re-run inside): 1-part controls .195-.203 (<= .40); 2-part controls 1.0 (>= .80). PASSES.

PRIMARY: D solvers (J >= .6), 100 viable DEEP+VERY_DEEP children per run:
  S2-TASK0 78/100 (mean J .821) vs S2-REP 63/100 (mean J .711); one-sided Fisher p .0147.
VERDICT: SUPPORTED. Task selection raises the share of deep descendants that solve the
composition-necessary task on a second master seed.

Size: the effect is about half the 36 effect. Seed 20260930 gave 91 vs 59 (+32 points);
seed 20261009 gives 78 vs 63 (+15 points). The control rate replicated (59 -> 63) and the
selected rate shrank (91 -> 78). This is the winner's-curse pattern again (ledger 2026-10-08,
R2): the first-seed size should not be quoted alone.

Attribution (single-rule knockouts on every solver, essential = drop >= .2;
python -m theseus.synth.ko_prov):
  essential-rule counts 0/1/2/3: S2-TASK0 34/30/14/0, S2-REP 18/23/20/2
  no single essential rule (redundant solutions): S2-TASK0 34/78 (44%), S2-REP 18/63 (29%)
    (36: 51% vs 36%; the same direction on both seeds)
  essential-rule provenance:
    S2-TASK0: law 38, G0 9, mutation edit 9, lens 2
    S2-REP:   law 43, mutation edit 19, lens 5, mutation 2
  solvers with a collision-law essential rule: S2-TASK0 32/78, S2-REP 35/63
  law-essential rules that write the sensor channel (the release): S2-TASK0 23, S2-REP 22
Reading, replicated on both seeds: the essential steps are mostly collision-generated k-ary
laws, many of which perform the release. Selection raises capability chiefly by adding
redundant solutions, not by raising the law-carried share.

Predictions: M1 (H-SEL-SOLVE-S2 SUPPORTED, p .75) RIGHT.
