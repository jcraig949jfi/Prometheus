# THE PRIMORDIAL MACHINE -- round 7: TWELVE-HOUR OVERNIGHT ROUND (ADOPTED)

Currency: 2026-09-15 ~16:30, Nestor-A[m1-449a9e76] (conductor).

Authority:
- Operator message 23, verbatim in prompts/2026-09-14_graphworld_swarm/23_*: 12 h overnight; GPU parallel and
  throughput expansion; dedicated machine; reviewer notes "adopt as you see fit".
- Operator ruling in 23: CANDIDATE_N binds Clause B, prospectively.
- Operator 22 (PRODUCTION stage) continues. SWARM_R6 rules carry over unless changed here.
- The operator is asleep overnight. Nothing in this plan may wait on the operator: any question the plan does not
  answer ends as a PRODUCTION_CANDIDATE or an OPEN item in the packet, never a paused round.

Governing principle unchanged: finding that a larger experiment is warranted is a valid result, not
authorization to run it.

## 0. Wall times (12 h END TO END; nothing extends it)

| phase | wall | contents |
|---|---|---|
| R7-BUILD | 16:35 -> 18:35 hard cap | s3: residue hygiene, evidentiary class at admission, Clause B family axis, GPU track build, capacity re-probe |
| R7-GATE + launch | <= 25 min | s4; the clock starts only when green |
| R7-CLOCK | 9 h, code-owned | 8 x 60 min epochs; NO_NEW_WORK T+480; drain to T+510; close T+540 |
| R7-PACKET | <= 25 min, by 04:30 | tally, packet, one ASCII block |

If build or gate overrun, the clock loses whole epochs; the 04:00 close does not move.

Seeds fixed here, before any round 7 data:
- anti-prior candidates 20260919;
- arm Bernoulli 20260920.
- The R16 order stays R16_ORDER_R6.json (already published; not re-drawn).

## 1. Conductor review of message 23 (bias check)

| # | message 23 text | prior it carries | adopted rule |
|---|---|---|---|
| O1 | "CANDIDATE_N = 32/4/8 a substrate-level evidentiary class" | none; it removes a split-brain rule | ADOPTED. Versioned rule EVIDENCE_N_v1: any job whose experiment_class can emit a verdict (CLAUSE_A, CLAUSE_B, ANTI_PRIOR, DISTANT_QD, ROBUSTNESS_LOO, REPLICATION, B2_SCREEN, R16_SCREEN_CELL) must declare runs_total 32, rng_family_count 4, runs_per_family 8 with a balanced `n_per_family`. Otherwise the ADMISSION path refuses SAMPLE_RULE_MISMATCH at zero simulation, unless the envelope declares `evidence_class: OBSERVATION`; then no receipt it files can carry PASS/FAIL. One rule table read by admission, the predicate helper and the receipt guard (no copies). E-R6-1 untouched. LOO is NOT added to admission. |
| O2 | "Expand into any additional parallel architectures or throughput optimizations using the GPU" | "GPU everything": the R5/R6 dispatch surface shows threaded CPU numba beats the GPU closed loop at 8192, and warp's t8 margin is 1.08x at 4096 | GPU ADOPTION RULE, fixed before data: a GPU path serves production work only if (a) its exactness oracle is 100% clean against the CPU reference on the real workload and (b) measured end-to-end throughput on a real cell job (cells/hour or episodes/hour including host-to-device copy, compile excluded but reported) is >= 1.25x the best CPU configuration on the same dedicated host. Otherwise the result is reported and CPU stays. Switch-over happens only at an epoch boundary via a code flag, never mid-job. |
| O3 | "No other processes will be using the machine" | the R5 k* = 2 was measured with builder sessions sharing the host | Re-probe NODE_CAPACITY_PROFILE_R7 with the R5 O3 rule on the dedicated host at the END of R7-BUILD (builders idle). k* is what the rule says, even if it is 2 again. |
| O4 | "queue the R16 remainder ... or the Clause B 32/4/8 production candidate first" | ordering by what looks promising | Both run; nothing is chosen by interest. The R16 remainder keeps the published seeded order. The 5 PENDING train128 learners run in ascending cost estimate, a function of T and the world only (no outcome data), so the most HELD/SURVIVED decisions fit the clock. Clause B runs as soon as its family axis passes the gate. The broker is FIFO. |
| O5 | "Clause B testing on a relational graph world physically possible" (reviewer 2) | novelty chasing before the control plane is closed (reviewer 1 warns) | Not in round 7. B2 gets only its ADMISSION screen, re-sized to EVIDENCE_N_v1 32/4/8 prospectively (the B2 rule becomes v2; no B2 data exists under v1), and only if admission's projection fits the clock after measured search overhead. A Clause B on B2 is a PC. |
| O6 | "the 4200 family carried the performance" (reviewer 2) | an over-read: leave-4200-out was the THINNEST margin (CI low 0.996 > 0.95, still ROBUST) | The packet language stays "thin at leave-4200-out; no single family carries the PASS". No new gate on B-R5-1. |
| O7 | "the round close must send a kill signal to the worker PIDs" | none | ADOPTED with a guard: workers register pid + repo + round_id; the close stops exactly the registered pids whose cmdline is `fabric.worker serve --lane <L>`. It never kills by name substring (feedback: a kill script matched itself). Production seats are never touched. |

Added during R7-BUILD (fixed before the data they govern):

| # | trigger | adopted rule |
|---|---|---|
| O2' | E's cpu_lockstep backend is itself a throughput optimization | CHOSEN backend = the fastest one whose oracle is clean, iff >= 1.25x cpu_sequential on every measured cell; pm:r7:backend + pm:r7:gpu_adopt; measured on the production path (G's cell_job) |
| O8 | E-R7-1 planted NEGATIVE judged PASS at 32/4/8 (p_max .049) | No change to the control or check_b. K = 40 independent planted-negative draws; INSTRUMENT_ADMISSIBLE iff false_pass <= 5/40, else INSTRUMENT_NOT_VALIDATED. The live Clause B pair runs only if ADMISSIBLE. |
| D18 | a closed round's clock kept refusing all admission | round_clock.read -> None for a closed round; the close unsets current; the scan flags it (F) |
| D19 | worker/gpuq children ran numba at 3 threads under an 8-thread grant | the child env + set_num_threads = the grant; rows stamp effective threads; fixed before the k* re-probe (F) |

## 2. Stage and ceilings (PRODUCTION, operator 22; one CEILINGS table)

- Checkpointable cpu job: segment wall <= 2400 s; cpu_budget_s per job <= 36000 (10 CPU-h).
- NON-checkpointable cpu job: wall <= 900 s (D15 fix).
- gpu job <= 600 s per lease segment; a longer GPU job must checkpoint between leases.
- Projected completion <= drain_ts. k* tokens from the R7 re-probe.

## 3. R7-BUILD (16:35 -> 18:35; each item ships with a regression test; gate items in brackets)

F (fabric), worktree nestor-bld-f:
- F-R7-1 (D12+D14) Worker registration (pid, repo, round_id, cmdline). The round close stops the registered
  worker pids (verified cmdline, never by substring), then clears the stop flags. Round start refuses to open a
  clock while any RESIDUE exists: a pm:jobs:*:stop flag; a live consumer whose worker repo is not the round
  worktree; more than one live consumer per lane group; an un-archived prior-round key in a round-namespaced
  family. [gate 26: planted residue of each kind -> refused.]
- F-R7-2 (D15) The non-checkpointable 900 s wall ceiling; admission refuses above it. [27]
- F-R7-3 (D4 rest, PC 1789489827401-0) Fingerprint the transitive primordial.* import closure of the job fn;
  respawn on mismatch, refuse if it persists. The fingerprint also records the worker repo (a D14 guard).
  [28: edit an imported module between jobs; job 2 runs the new code.]
- F-R7-4 NODE_CAPACITY_PROFILE_R7: the O3 rule re-run on the dedicated host, LAST in the build, after F/G/H/E
  post DONE (announce burst; <= 20 min). [29]
- F-R7-5 The s2 ceilings in the one CEILINGS table + clock shape r7 (3600 x 8, drain 1800, close 1800).

H (measurement), worktree nestor-bld-h:
- H-R7-1 (O1, D13) EVIDENCE_N_v1 as one rule module.
  - envelope.admit refuses SAMPLE_RULE_MISMATCH for verdict classes before execution;
  - predicate_ref.post_predicate refuses a verdict-class predicate without a conforming sample block;
  - the receipt guard imports the same table;
  - `evidence_class: OBSERVATION` receipts cannot carry PASS/FAIL.
  - Planted cases 16/1/16, 32/4/(16,8,4,4) and 32/4/(29,1,1,1) are refused at admission; 32/4/8 is admitted.
  [30]
- H-R7-2 (D11) Round-namespaced prior ledger: pm:prior:<round>:* (r6 keys migrated by rename; the r5 archive
  stays); candidates() refuses only within the same round. [31]
- H-R7-3 Close sweep + calibration by round id; `anti_prior.calibration` accumulates across r6 + r7 by arm,
  descriptive only. [32]

E (watchmakers + GPU track), worktree nestor-r6-e (E's session):
- E-R7-1 Clause B family axis: transfer_v2 run seeds = families (4200, 2101, 3303, 5501) x run seeds; check_b
  pairing within family; sample block EVIDENCE_N_v1. Planted positive/negative re-validated at 32/4/8 on a
  cheap planted pair. [33]
- E-R7-2 GPU TRACK (O2): a batched GPU evaluator for the R16 cell workload. One device batch holds every
  run's population evaluations for a generation (32 runs x 128 genomes x train episodes), using the W (warp) or
  U (CUDA graphs) MVP code in nv-venv-w / nv-venv-u. The search stays on CPU with its per-run RNG streams, so
  only the evaluation is batched.
  - Exactness oracle: every evaluated fitness equals the numba reference, and the elites are identical, on one
    real cell.
  - Then the O2 throughput comparison vs the best CPU config on the same cell. Emits GPU_ADOPT or GPU_REJECT
    with rows.
  [34: oracle + comparison rows exist; the decision is code-computed.]
- E-R7-3 B2 search-overhead measurement: one spec, a short QD run with the compiled rollout, measured
  overhead per generation, which gives the B2 v2 32/4/8 admission cost via G's function. [35]

G (metric), worktree nestor-bld-g:
- G-R7-1 B2 admission rule v2 = EVIDENCE_N_v1 (32/4/8), versioned; cost function uses E-R7-3's measured
  overhead. [36]
- G-R7-2 R16 cell_job `backend` parameter (cpu | gpu, default cpu) wired to E-R7-2's evaluator. The value is
  read from pm:r7:gpu_adopt at job start (set only by E-R7-2's code decision). [37]
- G-R7-3 PENDING learner plan: the 5 train128 learners ordered by cost estimate ascending (O4), under the s2
  ceilings, checkpointable; plan file committed before T+0. [38]

## 4. Launch gate

R6 items 1-25 carry, with item 16 naming pm:round:r7, plus items 26-38 above, plus:
- 39. live residue scan GREEN on the real store at T-0 (F-R7-1 run against Redis, not a fixture).
- 40. every lane letter dry-launches.
- 41. full suite rc 0 on the gate tip.
The clock starts only when all are green. A red item that is not fixable by 18:55 becomes a PC, the dependent
work is dropped from the round, and the rest launches.

## 5. R7-CLOCK (9 h): lanes

- G: R16 remainder (seeded order), then the PENDING learners (O4). Backend per O2.
- B: REPLICATION only, when pm:replication publishes (frozen B-R5-1 recipe; now also EVIDENCE_N_v1-checked
  at admission). No other work; NOT_REACHED is a valid close.
- E: E-R7-1 Clause B 32/4/8 live pair w14 -> w13 (the first admissible Clause B verdict), then the B2 v2
  admission screen if admission's projection fits the clock.
- C: ANTI_PRIOR v2 draws (seed 20260920), target 6 assignments, plus 1 DISTANT_QD. Planted null first. All
  32/4/8.
- R: seals priors on the r7 candidate list (seed 20260919) before T+15.
- D: OPEN anomaly queue, priority: the anti-prior-arm PASS (C-R6-AP-01), family 3303, then any GPU exactness
  or crossover anomaly. Minimum discriminators.

## 6. Conductor A

A does: launch, observe, resolve deadlocks, carry the operator's standing rulings, write the packet.
A does not:
- push controller records, relay triggers, score, pick cells, extend the clock, or promote;
- clear residue by hand. If residue appears mid-round, A files a defect; manual repair is allowed only where the
  round would otherwise deadlock, and is counted.

## 7. Output

The R6 packet structure, plus:
- EVIDENCE_N_v1 refusals by class;
- the GPU_ADOPT/REJECT decision and its rows;
- the R7 capacity profile;
- residue-scan results at start and close;
- calibration across r6+r7 by arm.
