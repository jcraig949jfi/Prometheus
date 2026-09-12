TECHNE -> NYX: fossil vault batch 04 delivered -- MACHINERY UNDER PRESSURE

Charter: roles/Techne/prompts/2026-09-12_batch04/OPERATOR_CHARTER.md (committed verbatim).
Batch 04 targeted machinery that exists BECAUSE of an external pressure -- contention, feedback,
hidden state, scarcity, hardware decisions, adaptation, and failure. Vault is now 57 specimens /
57 lineages. Techne acquires + proves-it-runs + records the pressure; Nyx chops. No organ named,
no algorithm modernised, no behavior decided.

BATCH 04 -- 16 specimens (14 runnable, 2 source-only)

  CONTENTION / RETRY / RECOVERY (axis 1):
    willemt-raft            RUNNABLE_CONTAINER   Raft consensus in C; the shipped CuTest suite
                                                 (157 assertions: election, log replication,
                                                 snapshotting) passes via mock peers. ORACLE.
    linux-tcp-congestion    SOURCE_ONLY          CUBIC + BBR kernel modules (tcp_cubic.c,
                                                 tcp_bbr.c) -- the congestion-avoidance lineage;
                                                 a BEFORE/AFTER pressure pair in one specimen.
  CONTROL / FEEDBACK (axis 2):
    arduino-pid             RUNNABLE_CONTAINER   Beauregard PID on a two-lag plant; Kp=1 converges
                                                 to setpoint, Kp=200 DESTABILISES (failure receipt).
    python-control          RUNNABLE_CONTAINER   the Control Systems Library; LQR places all
                                                 closed-loop eigenvalues in the LHP, drives a
                                                 double integrator to the origin. ORACLE.
    do-mpc                  SOURCE_ONLY          Model Predictive Control (CasADi/IPOPT deferred).
  HIDDEN-STATE / ESTIMATION (axis 3):
    simple-kalman-denyssene RUNNABLE_CONTAINER   scalar Kalman filter; filtered RMS < half the raw
                                                 measurement RMS on a hidden constant. ORACLE.
    filterpy-labbe          RUNNABLE_CONTAINER   Bayesian filtering; KF tracks a noisy constant-
                                                 velocity target, RMSE(filter) < RMSE(sensor).
                                                 ADVERSARIAL PAIR: the plant emits the noise, the
                                                 filter recovers the hidden state. ORACLE.
    viterbi-hmm-xukmin      RUNNABLE_CONTAINER   Viterbi/HMM decoder; upstream test decodes a known
                                                 HMM's most-likely path. ORACLE.
  MEMORY UNDER SCARCITY (axis 4):
    lru-cache-goldsborough  RUNNABLE_CONTAINER   C++ LRU; evicts the least-recently-inserted key,
                                                 and a working set >> capacity THRASHES to <5% hit
                                                 rate (failure receipt). ORACLE.
    buddy-alloc-spaskalev   RUNNABLE_CONTAINER   header-only buddy allocator; 500 allocs in a 1MB
                                                 arena then coalesces back to a half-arena block.
  HARDWARE DECISION MACHINERY (axis 5, iverilog):
    verilog-rr-arbiter      RUNNABLE_EMULATED    round-robin arbiter; under full contention every
                                                 requester is granted (no starvation). ORACLE.
    verilog-generic-fifo    RUNNABLE_EMULATED    OpenCores FIFO; fills to full (backpressure),
                                                 drains in FIFO order, empties. ORACLE.
    verilog-uart2bus        RUNNABLE_EMULATED    UART->bus protocol FSM; bench drives serial frames
                                                 against a reg-file model (activity, no pinned ref).
  CONNECTIONIST / ADAPTIVE HISTORY (axis 6):
    genann                  RUNNABLE_CONTAINER   minimal C neural net; backprop learns XOR + its
                                                 own minctest suite passes. ORACLE.
    minisom                 RUNNABLE_CONTAINER   Self-Organizing Map; quantization error falls
                                                 3.63 -> 0.14 self-organising over 3 clusters. ORACLE.
    hopfield-takyamamoto    RUNNABLE_CONTAINER   the repo's own HopfieldNetwork; a 3-bit-corrupted
                                                 cue over 25 neurons recalls the stored pattern
                                                 (associative error correction). ORACLE.

PRESSURE METADATA (batch-04 additions, on every record; context for Nyx, never a decomposition)
  human_environmental_pressure   the external condition that made the machine necessary
  human_failure_condition        what happens when it fails at its human purpose
  behavioral_entry_point         one reproducible way to stimulate/perturb it
  observability{}                EXECUTABLE/OBSERVABLE/ORACLE_BACKED/INTERVENTION_READY/
                                 PATCH_INTERVENTION/OPAQUE (yes/no/unknown, acquisition facts)

REQUESTED AXIS COVERAGE (>=75% of the batch from the focused axes -- met: 16/16 on-axis)
  1 contention/retry/recovery    2  (raft runnable; tcp source-only) -- BELOW the >=3 target; thin
  2 control/feedback             3  (arduino-pid, python-control runnable; do-mpc source-only)
  3 hidden-state/estimation      3  (kalman, filterpy, viterbi -- all runnable)
  4 memory-under-scarcity        2  (lru-cache, buddy-alloc -- both runnable) -- met
  5 hardware decision machinery  3  (arbiter, fifo, uart -- all runnable emulated)
  6 connectionist/adaptive       3  (genann, minisom, hopfield -- all runnable)
  7 failure / bad-behavior       2  pathological receipts (PID gain instability; LRU thrash)
  8 adversarial pair             1  (filterpy: noise generator <-> state estimator)
  historical pressure series     1  (linux-tcp CUBIC->BBR, BEFORE/AFTER in one specimen)
  precision / safety-critical    2  (kalman, filterpy -- navigation-grade estimation)
  binary-only path               0  (optional; not exercised -- still open from batch 03)

REPORT FIELDS
  specimens acquired            16 (vault total 57)
  lineages represented          16 new, all distinct (vault 57 unique lineages)
  runnable                      14/16 this batch (RUNNABLE_CONTAINER 11, RUNNABLE_EMULATED 3);
                                50/57 vault
  source-only (by design)       2  (linux-tcp-congestion, do-mpc) -- pinned + tree-hashed, no fake
                                receipt; kernel-context / CasADi-IPOPT weight deferred
  observable                    every runnable specimen captured stdout in its receipt
  oracle-backed                 13/14 runnable (all but uart2bus, which is activity-only: it
                                exercises the protocol FSM but no reference decoded byte is pinned)
  language distribution         C++ 4, Python 5, C 3 + 1 kernel-C, Verilog 3
  execution-model distribution  container 11, emulated 3 (HDL sim), source-only 2
  algorithmic-era span          1958 (perceptron lineage, genann) .. 2016 (do-mpc); the CODE
                                artifacts are mostly 2000s-2010s, several algorithms far older
                                (Kalman 1960, Viterbi 1967, Hopfield/SOM 1982, buddy 1965)
  source availability           16/16 pinned + tree-hashed (57/57 vault)
  provenance gaps               none: every specimen has origin + exact commit + tree hash
  legal restrictions            none blocking; GPL/LGPL/MIT/BSD as-is (raft/lru/buddy MIT/BSD,
                                python-control BSD, filterpy MIT, linux GPL-2.0 preserved)
  failed acquisitions           none (ghmm 404'd in prep and was swapped for viterbi-hmm-xukmin
                                BEFORE this batch; all 16 planned specimens fetched)
  environment failures          none blocking; two SOURCE_ONLY by build weight, not failure
  adversarial pairs             1 (filterpy: the plant IS the pressure, the KF IS the response)
  pathological / failure receipts 2 (arduino-pid Kp=200 destabilises; lru-cache thrash <5% hit)
  deviations (recorded)         (a) arduino-pid: Techne Arduino.h shim (millis) + a two-lag plant;
                                PID source unmodified. (b) simple-kalman: Techne empty Arduino.h so
                                the Arduino lib's include resolves; filter source unmodified.
                                (c) verilog-generic-fifo: generic_dpram supplied as a Techne
                                behavioral memory primitive (separate OpenCores core, not shipped),
                                AND the upstream dual-clock sweep-bench does not terminate under
                                iverilog so a bounded Techne SC testbench is the oracle; FIFO RTL
                                unmodified. (d) verilog-rr-arbiter: shipped tb emits no stdout, so a
                                Techne observation testbench prints the grant sequence; arbiter RTL
                                unmodified. (e) willemt-raft: CLinkedListQueue vendored as a
                                companion (Makefile git-pulls it; build world is sealed) and -Werror
                                relaxed for modern gcc; no raft source changed. (f) python-control /
                                filterpy run the ACQUIRED source via PYTHONPATH (numpy/scipy/mpl
                                pip-installed as deps), not a PyPI copy. (g) hopfield runs the repo's
                                own HopfieldNetwork (matplotlib/tqdm installed headless only to
                                satisfy its module imports).
  operational note              in-place builds (make, __pycache__, generated main_test.c) mutate
                                the working tree; after the run the 8 affected git bodies were
                                `git clean`-ed back to the pinned commit, and all 16 bodies now
                                verify byte-exact against their recorded tree_sha256. The pinned
                                commit/archive hash is the preservation anchor; the working tree is
                                scratch. (A future runner should build on a disposable copy.)
  newly discovered candidates   added to HARVEST_QUEUE.md: exponential-backoff / retry libraries,
                                a failure detector (phi-accrual), a distributed lock/lease, a
                                circuit breaker, a particle filter + MCMC/Gibbs sampler, Baum-Welch
                                training, EKF/UKF exercised, MRAC/sliding-mode control, a runnable
                                MPC, a deadlock/priority-inversion demo, TMR/voting + watchdog,
                                CORDIC + a branch predictor + clock-domain-crossing HDL, an
                                attacker/defender or fuzzer-vs-parser adversarial pair.

WHICH PRESSURE AXES REMAIN THIN? (not hidden)
  - CONTENTION/RETRY/RECOVERY still thin in RUNNABLE form: only raft runs; TCP is source-only.
    No runnable exponential backoff, failure detector, distributed lock/lease, leader lease,
    gossip/anti-entropy, thundering-herd, or circuit breaker yet.
  - ESTIMATION breadth thin: no particle filter, no MCMC/Gibbs, no EKF/UKF exercised (filterpy
    ships them; only the linear KF was run), no Baum-Welch training (Viterbi is decode-only).
  - CONTROL breadth thin: no adaptive/MRAC, no bang-bang/sliding-mode, no runnable MPC (do-mpc
    is source-only).
  - ADVERSARIAL PAIRS thin: 1 only (estimator vs noise). No attacker/defender, self-play game,
    or fuzzer-vs-parser pair.
  - FAILURE/BAD-BEHAVIOR thin: 2 self-induced only (gain instability, cache thrash). No deadlock,
    livelock, priority inversion, race, memory corruption, or leak-in-action.
  - PRECISION/SAFETY-CRITICAL light: navigation-grade estimation only; no fixed-point pipeline,
    no TMR/voting, no watchdog, no ECC under injected faults.
  - HARDWARE still narrow: arbiter/FIFO/UART only; no branch predictor, cache-coherence, sorting
    network, CORDIC, or clock-domain-crossing failure demo.
  - BINARY-ONLY + lawful-recovery path STILL not exercised (open since batch 03).

Nothing decomposed, no organ named, no algorithm modernised (old libs via docker/iverilog/pip
pinned-source). Near-duplicates kept (three estimators: scalar KF, vector KF, Viterbi; three
connectionist: feedforward/backprop, SOM, Hopfield; three HDL decision machines). Two SOURCE_ONLY
specimens carry pinned tree hashes and no fake receipt.

-- Techne, 2026-09-12, worktree Prometheus-worktrees/techne-pass-0911
