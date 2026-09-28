# PREREG -- coldstart_A-001: sandbox gate reproduction + one new cheat world

Currency: 2026-09-28. Cold-start worker coldstart_A-001 (fresh subagent, did
not draft the packet). Written BEFORE any run of any world in this
directory. Never edited after the first run. Pure ASCII.

Code at write time (sha256): world.py a3d20f13..., battery.py 3060ec75...,
run_coldstart.py 4dfdc7bb... (copies/extensions of ../world.py 75caf806...,
../battery.py ad900209...; originals untouched; see inputs.sha256).
Frozen and inherited unchanged: ../PREREG.md + ../AMENDMENTS.md (A1 salt),
delta = 0.05, bootstrap 2000 / seed 12345, n = 20 worlds (seeds 1000..1019),
300-generation planted burn-in, all battery statistics and decide().

## Part A -- reproduction of the known-answer gate (packet fixture)

Command: python3 run_coldstart.py repro (original modules, 1 process).
Prediction: bit-identical reproduction. Every numeric per-world value of
the 6 arms equals ../known_answer.json to 1e-12 and the gate dict is equal
(P R3 + INSTALLED, P4 R3, N_a R0, N_b none, C R2 failing on Dp and Dr,
P_sigma R0, A/A valid, gate PASS).
Decision: REPRODUCED-EXACT if 0 mismatches; REPRODUCED-VERDICT if values
differ but every arm's highest rung, tests dict and gate verdict are equal;
NOT REPRODUCED otherwise (then Part B is still run but labelled as on an
unreproduced apparatus).

## Part B -- new cheat world T ("nest tag")

Idea the authors did not plant: a record whose CONTENT matters (so the
content tests Dp, Dr pass) but whose content is the SAME UNDER EVERY
HISTORY -- a static per-nest label, i.e. the non-acquired object that
ACCUMULATION_v0 s1 (h) explicitly excludes ("a component that every history
drives to the same value is a property of the physics, not an
acquisition"). The benefit comes from a static nest-specific environmental
bias, relayed from writer genomes, not from anything the ecology learned.

World change (physics family 'biased_colony'): on a redraw (p = 0.10)
colony g's patch goes to site g with prob 0.7, else uniformly to one of the
other 3 sites (same three physics draws per colony per generation as every
other family, so the event-stream guarantee holds). Everything else as the
frozen planted worlds.
Arms (planted, clonal, 300 gens, seeds 1000..1019):
  T        colony g's genome writes the constant symbol g into cell 0 every
           generation regardless of site/found; readers decode cell 0 as P
           (BLANK -> site 0); explore 0.2. sigma = identity.
  T_sigma  T under the per-world random sigma (convention pair).
  P_cb     the frozen P plant in the same colony-biased world (positive
           control: the new physics does not break detection of a real
           history-carrying code).
Identity control: the extended copies must reproduce the original per-world
values of P and C at seeds 1000-1002 exactly (0 mismatches), else the
extension is defective and Part B is void.

Which verdict is correct for T (fixed now): T carries no history-specific
content, so a correct apparatus must NOT award T R3 (content dependence of
an acquired object). Correct outcome: highest(T) < R3 under the frozen
ladder, or a decisional test flags it.
Battery "catches" T iff highest(T) in {None, R0, R1, R2} by the frozen
decide(). Battery "misses" T iff highest(T) >= R3.

Predictions (mine, made before running; I expect the battery to MISS):
  B1 T: D1, D2 PASS (~0.3-0.45); Dp, Dr PASS (the neighbour's tag and a
     random symbol send readers to the wrong site); Di n/a-or-EQUIV (cell 1
     unused).
  B2 T: D0 PASS (~0.1-0.2), NOT because of history but because the
     history-ablated twin suppresses ALL writes for 30 generations, so its
     record decays by noise while the intact record is refreshed: D0 measures
     maintenance, not history-specificity.
  => B3 T highest = R3 (MISS). Probability I assign: ~0.7. If D0 fails, the
     battery catches T only via the R0 prerequisite -- which
     ACCUMULATION_v0.1 A3 has since removed (rungs awarded independently),
     so under v0.1 T would be awarded R1-R3 regardless. Both readings will
     be reported.
  B4 Non-decisional episode permutation (own record 50 gens earlier):
     D_episode(T) EQUIV 0; D_episode(P_cb) PASS. Fresh-world transfer
     D_fw(T) > 0 (does NOT flag T).
  B5 Convention: T vs T_sigma -> INSTALLED (T breaks under relabeling; does
     not separate T from P, which is also INSTALLED).
  B6 P_cb: R3, like P.
  B7 EXPLORATORY diagnostic history_twin (new, not decisional): rerun the
     last 30 gens from the S*-30 snapshot under a different physics stream
     vs the same stream with different organism coins; mismatch of recently
     written cells, difference H. Prediction: H(T) < 0.05, H(P_cb) > 0.3.
Proposed repair (stated now, evaluated on this data only as exploratory):
R3 must also require PASS(D_episode) (within-lineage episode permutation,
which ACCUMULATION s3 R3 already names: "between lineages/episodes") and R0
should be operationalised by a different-history twin (H), not a
write-suppressed twin.

Falsifier of my claim "the frozen battery admits a static-label cheat":
highest(T) < R3 with P_cb = R3.
Falsifier of the apparatus (packet): any of P/N_a/N_b/C mis-scored at
n = 20 in Part A.

Budget: 1 process, <= 45 min wall total; expected ~10 min. No reduction of
n or generations is permitted; if over budget, stop and report NULL for the
unfinished part.
