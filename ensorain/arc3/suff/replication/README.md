# PKG-S1 independent replication (Fabric tsk-ba120344aa29)

- Thread thr-ens-sufficiency-ladder; campaign C-ENS-ARC3; experiment E-ENS-S1-PILOT.
- Task base_sha 51ddc856e.
- Attempt att-32409eb521dc: worker.ubu002, claude-opus-5-5, 2026-09-29T02:48:31Z to 02:50:38Z, fabric status "succeeded".

## What happened

1. The worker wrote an independent pure-stdlib implementation from the written spec: `fabric_worker_suff_replica.py`,
   artifact art-ebef97fe46f5, sha256 3eb10f53...
   - It states that it did not open any Ensorain file.
   - It also derived an analytic representational floor for the Even process.
2. The worker could NOT execute its code. The Fabric claude executor has no shell and no python BY DESIGN
   (fabric/README.md s4 and D3; execution goes through the `script` executor).
   - This was Ensorain's task-design error. The task asked a claude executor to run code, and declared
     `python.stdlib`, which describes the host, not the executor.
   - It is not a Fabric defect.
   - Correct pattern: a claude task writes the code, then a `script` task runs the committed file.
3. Ensorain ran the worker's UNMODIFIED script on M2 (Python, 0.7 s): `fabric_worker_replica_run_m2.txt`.
   - The IMPLEMENTATION is independent. The EXECUTION is not.
   - The script is deterministic (seeded random.Random), so a second executor would add no information.
4. Ensorain verified the worker's analytic floor with an exact enumeration of the stationary process:
   `even_representational_floor.py` / `.txt`.
   - It computes H(X_t | last k) - 2/3.
   - It matches the worker's closed form P(1^k)[h(q_k/2) - q_k] to 4 decimals at every k.

## Verdicts (16 seeds, T = 4000)

| claim | reported (Ensorain pilot) | independent code | verdict |
|---|---|---|---|
| C1 W2: STAT(3) = Bayes | 0.000 | 0.000 exactly; max over seeds 0.0e+00 | CONFIRMED |
| C2 W2: over-order excess at k = 4 / 6 / 8 | .004 / .017 / .039 | .0044 / .0187 / .0435 | CONFIRMED |
| C3 Even: no k reaches Bayes | .252 .211 .131 .110 .075 .060 .075 | .2535 .2087 .1301 .1113 .0753 .0597 .0750 | CONFIRMED |
| C3 Even: interior optimum at k = 6 | k = 6 | k = 6. Per seed, k6 is in [.055, .063], below k4 [.073, .079] and k8 [.072, .079] | CONFIRMED |
| C4 Even: Bayes loss -> 2/3 | yes | T = 60000, last half: .66723 / .66723 / .66670 (seeds 1-3) | CONFIRMED |

The C2 differences (up to about .004 at k = 8) are within seed spread (W2 k8 per-seed range [.022, .061]).
- The two implementations order the random draws differently, so the same seed gives a different stream.
- Only the 16-seed means are comparable.

## New from the replication: the C3 optimum decomposes exactly

Each Even-process excess is the sum of two parts:
- a representational floor, which is exact, with infinite data: H(X | last k) - 2/3;
- a finite-sample estimation cost, measured as the excess minus the floor.

| k | 0 | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|---|
| floor (exact) | .2516 | .2075 | .1258 | .1038 | .0629 | .0315 | .0157 |
| measured excess | .2535 | .2087 | .1301 | .1113 | .0753 | .0597 | .0750 |
| estimation cost | .002 | .001 | .004 | .008 | .012 | .028 | .059 |

- The floor halves every 2 steps of k: only the all-ones context 1^k is ambiguous, and P(1^k) decays geometrically.
- The estimation cost roughly doubles per step once the context count matters.
- The interior optimum at k = 6 is where the two cross. So the pilot's reading 3 ("truncation vs estimation") is now
  measured as two separate curves, not just asserted.
- It follows that the optimum k moves up with T. That is a falsifiable prediction for the pilot; it has NOT been run.

### Precommitment (written 2026-09-29, BEFORE running): the optimum k grows with T

Reasoning from the table above: the floor at k = 10 is about .008. Estimation cost scales roughly as log(T)/T per
context.

Predictions, Even process, 16 seeds, grid k in {0, 1, 2, 3, 4, 6, 8, 10}:
- P1: at T = 16000 the argmin of the mean excess is k in {6, 8}.
- P2: at T = 64000 the argmin is k = 8 (not 6, and not 10).

Failure: P1 fails if the argmin is outside {6, 8}; P2 fails if the argmin is not 8.
The script is `optimum_vs_T.py`. It reuses the worker's generator and learners unchanged, importing them from its code.
