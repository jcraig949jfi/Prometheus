# THESEUS-13: synthetic concepts from the 36 task-selected solvers (2026-10-08)

Command: python -m theseus.synth.syn_concepts --workers 4 (defaults: --run v0_2t0_2026-10-08,
--evaldir theseus/runs/comp_task_2026-10-08, --max 20). Archive:
theseus/archive/syn_concepts_v0_2t0_2026-10-08.jsonl (20 records, each with executable
definition, fingerprint reference, lineage, lens and world dependencies, assays, and known
failure modes = the single rules whose removal breaks it).

Selection (mechanical): solvers of the composition-necessary task with J >= .9 AND an
essential rule that is a collision-generated law; top 20 by J.
Admission (replication on a fresh task seed, J_ch0_k8_seed1 >= .9): 20/20 admitted (all 1.0).
Transfer assays: larger alphabet (V 8, sensor readout) >= .9 in 14/20 (min .44); full-state
readout V 8, k 8 >= .9 in 18/20 (min .525).

Precise language (all 20): no direct raw-human parent; minimum ancestry depth to G0 = 2 (8),
3 (5), 4 (7); generation 6-20; an essential step is a collision-generated k-ary interaction law;
interpretation not attempted. Not claimed: freedom from human priors (the op set, compiler and
task are human-designed), novelty of mechanism (no known-mechanism reproduction attempted on
this task), or that the concepts are useful beyond this task family.
Status: archived as eligible tensor matter; re-injection into an ecology as collision parents
is a backlog item (THESEUS-39).
