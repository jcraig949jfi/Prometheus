# E-009 result -- fresh-seed replication of the Block D positives. CLOSED 2026-09-29.

Preregistration: ops/campaigns/C-002/E-009/EXPERIMENT.md, committed and pushed at c6196efb4 BEFORE any unit ran.
Reduction: `python Aether/observatory/aeth03_combinations_reduce.py ops/campaigns/C-002/E-009/attempts` -> REDUCTION.json
(reducer at fd7ca4fde). 20 units, 128 origins per law, seeds 4-7, OFF, code pinned c49f2ebad4.

## Verdict under the preregistered rule (N1 on the fresh seeds alone)

| combination | P_sust | components (P_sust) | N1 floor | minimum pass | N1 | **verdict** |
|---|---|---|---|---|---|---|
| rcv_add | 22/128 = 0.172 | rcv 4/128, add 1/128 | 0.10 | 13/128 | holds (+9 origins) | **REPLICATED** |
| rcv_str | 15/128 = 0.117 | rcv 4/128, str 0/128 | 0.10 | 13/128 | holds (+2 origins) | **REPLICATED** |

N2 (no evidential weight, per the preregistration): holds for both; P_content rcv_add 0.164, rcv_str 0.078.

Consequences, as fixed in the preregistration:
- rcv_str: the Amendment A1 UNRESOLVED status is lifted. NEW_BEHAVIOUR (N1) now stands on two independent seed sets
  (E-006 seeds 0-3: 14/128; E-009 seeds 4-7: 15/128).
- rcv_add: replicated as expected (22/128 in both seed sets).

Read at its width:
- rcv_str's effect is real but small and close to the floor. Per seed (of 32): 3 / 2 / 5 / 5, so two of the four fresh
  seeds are individually below the 0.10 floor (E-006 per seed: 4 / 4 / 4 / 2). It passes on pooled origins, which is what
  the rule tests, with 2 origins to spare rather than 1. Replication removes the "one lucky origin" reading. It does not
  make the effect large.
- rcv_add is robust: 5 / 6 / 6 / 5 per seed, every seed above the floor, and about 5x the sum of its components.
- Components stay near zero on the fresh seeds (rcv 4/128, add 1/128, str 0/128). This matches E-006 (rcv 6/128) and
  keeps super-additivity clear for both combinations.
- Pooled over 8 seeds (description only, not a verdict): rcv_add 44/256 = 0.172; rcv_str 29/256 = 0.113; rcv 10/256;
  add 2/256; str 0/256.
- This settles "is the rcv_str pass an artifact of which seeds were run". It does not change what either law's
  propagation IS: the E-006 cause probe (activity traces for rcv_add, activity re-routing for rcv_str, not content
  transport) stands.

## Execution, including the deviation from the preregistered path

- Preregistered: 20 Fabric script Tasks. Actual: 4 ran on Fabric; 16 ran natively on BUCKKEEP.
- Why: 16 Tasks failed at worktree creation on ubu001, both attempts each, apparently disk full (DEF-AETH-001,
  roles/Aether/DEFECTS.md; reported to Odysseus as comms #998). Native fallback per MWO-0004 R3.
- The scientific contract is unchanged: same code commit, same inputs and unit IDs, same reducer.
- Native execution:
  - detached worktree pinned at c49f2ebad4 (C:/Prometheus-worktrees/aether-e009-pin);
  - OMP/BLAS threads = 1;
  - canonical Fabric lease `buckkeep:cpu8` lse-2a79f41391ee, acquired 08:46, renewed, released after the last unit;
  - waves of 3 in the foreground, about 7 min per wave.
- A first wave of 8 was killed at the 590 s foreground limit, at about 19/32 origins; its partial outputs were discarded
  and those units re-run unchanged. That wave showed the host gives about 1.8x throughput at 8-wide, not 8x.
- Fabric units: tsk-f936bf5d83e2 (rcv_str s4), tsk-c6ff929b112b (rcv_str s5), tsk-743a1db43336 (str s4),
  tsk-cf81375d1e54 (str s5), on worker.ubu001.sci and sci2. Each result file's blob id equals its patch index.
- Every unit (20/20) was checked: stdout result_sha256 = file, locality_violations 0, and code_sha256_lf = the pinned
  manifest (Aether/runpod/aether_units/aether_files.json).
- Cross-host determinism: rcv_str s4 was run on both hosts (Fabric ubu001 and native BUCKKEEP). The result_sha256 is
  identical, 6d56b9b28a07c8ee...; the native copy is kept as duplicate_E9-rcv_str-s4__A-002__native-BUCKKEEP.json, outside
  attempts/. It adds nothing to the reduction.
- Compute: about 16 unit-runs x 4-7 min, about 2 CPU-hours, inside the MWO-0004 R2 envelope. No paid compute.
