# W2-AJ plan and pre-stated predictions (written before any TASK 2 run)

Written 2026-09-30, after TASK 1 (census) and BEFORE aj_edgecut.py was written or run.

## TASK 2: 4781b0a1 sensor-to-sensor edge cut

Native physics: ring 144, radius 3, sync period 2, fanout 8 sampled over 6 ports (plastic routing),
loss .1, cap 2 saturate. MAJ d=3, n_maj=5: the 5 sensors sit within ring distance 3 of the actuator,
so they form one cluster (e.g. w0: sensors 110,111,114,115,116, actuator 113).

Patch: topology.build is overridden (only while one World is constructed; restored in finally) with
a per-world-pair neighbour table. Engine semantics untouched. Because sensor placement differs per
world and the table is per physics, each mirror pair is run as its own B=2 World (16 pairs).
Env placement (envs.dist_matrix) is NOT patched: sensors and actuator stay at their native sites.

A cut edge u->v (port j of u) is redirected to a DUMP site = actuator + 72 (ring antipode). In
4781b0a1 a never-cued site can never emit (static: S1 = GT(S1+SENSE, CNT0) stays 0; dynamic: TASK 1
census never_emit = 0), so the dump is an exact sink. The port keeps its dist label and routing
weight; packets sent on it are simply lost to the task. Dump-site emissions are counted (must be 0).

Conditions (16 held pairs = first 32 held worlds, same as W2-AG ag_dict2.py):
- identity: patched path with the native table (must reproduce .7839 exactly, the unpatched value).
- CUT_SS: every directed edge sensor->sensor redirected to dump. Sensor->actuator edges and all
  other edges kept.
- CTRL_SN: the same number of directed edges per world, drawn at random from sensor->(non-sensor,
  non-actuator) edges, redirected to dump (matched loss of sensor out-ports).
- CTRL_NN: the same number per world drawn at random from edges whose source and target are both
  non-sensor, non-actuator sites within ring distance 6 of the actuator (local non-sensor edges).

PREDICTIONS (SR-03: the vote is carried only by reverberation between mutually adjacent cued sensors):
- CUT_SS: accuracy .500 with a degenerate interval (pair sd 0), as under DICT and the non-adjacent pair.
- CTRL_SN and CTRL_NN: indistinguishable from identity (about .78; predicted exactly .7839 for
  CTRL_NN and CTRL_SN if non-sensors are exact sinks, because redirecting a packet from one sink to
  another changes nothing the actuator reads).
- Falsifier of SR-03: CUT_SS lo99 > .55, i.e. direct sensor->actuator traffic alone carries the vote.
- Falsifier of the control logic: CTRL_* away from .7839, meaning the dump site or port redirection
  itself perturbs dynamics.

## DICT-k curve (if budget allows)
Cue exactly k of the 5 sensors (sense_val of the others zeroed), k = 1..5, two selections:
- ADJ: the k-subset with the MOST mutually adjacent pairs (ring distance <= 3);
- SPREAD: the k-subset with the FEWEST adjacent pairs.
Ties broken by lowest index. The number of adjacent pairs per subset is recorded.
Predictions:
- SR-03 (integration through reverberation): accuracy depends on adjacency, not only on k. SPREAD with
  zero adjacent pairs is exactly .500 for any k; accuracy rises with the number of adjacent pairs.
- A pure count step (k-threshold on direct traffic) predicts ADJ = SPREAD at each k, with a step at
  some k.
- k=1: .500 degenerate (W2-AG single_0); k=5: .7839.
