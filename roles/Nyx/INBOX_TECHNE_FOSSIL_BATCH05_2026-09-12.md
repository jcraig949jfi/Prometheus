TECHNE -> NYX: fossil vault batch 05 delivered -- AFTER RESET (preservation proven, then wider and deeper)

Charter: roles/Techne/prompts/2026-09-12_batch05/OPERATOR_CHARTER.md (committed verbatim).
Before anything was acquired the vault's own integrity was proved: opening census 57/57 bodies
match their pins, the two archive-content restorations from the reset were re-checked against
independently re-fetched origins (both MATCH), and 10 real recipes were re-run under the new
disposable-copy isolation (all PASS, every body preserved). Then 33 new specimens (30 runnable,
3 SOURCE_ONLY kernel code) and do-mpc reclassified from SOURCE_ONLY to RUNNABLE. Vault: 90
specimens / 90 lineages. Techne acquires + proves-it-runs + records the pressure; Nyx chops.
No organ named, no algorithm modernised, no behaviour decided, nothing pruned.

Enumerate the whole vault from any checkout (bodies or not):
    python -m techne.fossils.catalog            (or --json; tracked snapshot techne/fossils/CATALOG.json)

BATCH 05 -- 33 new specimens + 1 reclassified

  A. RUNNABLE CONTENTION / RETRY / RECOVERY
    lmdb-0.9.31              RUNNABLE_CONTAINER  copy-on-write B+tree, no log; a writer _exit()s
                                                 inside an open transaction of 500 puts -> reopen shows
                                                 exactly the 1000 committed, none of the 500. ORACLE.
    leveldb-1.23             RUNNABLE_CONTAINER  LSM + write-ahead log; a writer _exit()s after 500
                                                 acknowledged unsynced puts -> reopen replays the log,
                                                 2500 present. ORACLE. (rival design to LMDB)
    concurrencykit-0.7.2     RUNNABLE_CONTAINER  ticket + MCS spinlocks under 4-way contention,
                                                 ck_backoff exponential backoff, lock-free SPSC ring:
                                                 ck's own validate programs assert invariants. ORACLE.
    pybreaker-1.2.0          RUNNABLE_CONTAINER  Nygard circuit breaker: CLOSED->OPEN after 3 failures,
                                                 fast-fail while OPEN, ->HALF-OPEN after the timeout,
                                                 ->CLOSED on a good probe. ORACLE. small mechanism.
    backoff-2.2.1            RUNNABLE_CONTAINER  exponential backoff + full jitter: 1000 clients at
                                                 attempt 6 share ONE wait value without jitter, 839
                                                 distinct values with it. ORACLE. small mechanism.
  B. FAILURE PATHOLOGIES (+ the TCP pressure series)
    bsd-tcp-4.2-1983         SOURCE_ONLY         the KNOWN-BAD ancestor: no cwnd, no slow start; the
                                                 TCP that collapsed LBL<->Berkeley to 40 bit/s in 1986.
    bsd-tcp-4.3-tahoe-1988   SOURCE_ONLY         the REDESIGN: slow start, congestion avoidance,
                                                 Karn's algorithm, RTT variance (Jacobson/Karels).
    bsd-tcp-4.3-reno-1990    SOURCE_ONLY         the SUCCESSOR: fast retransmit + fast recovery.
                                                 (BEFORE / TRANSITION / AFTER; 13 netinet files each;
                                                 unix-history-repo tags BSD-4_2 / BSD-4_3_Tahoe / BSD-4_3_Reno)
    odepack-netlib           RUNNABLE_NATIVE     LSODE on Robertson's stiff kinetics: MF=21 (BDF)
                                                 reaches t=4e10; MF=10 (Adams, non-stiff) EXHAUSTS
                                                 its 500-step budget at t=0.11, ISTATE=-1. The
                                                 failure is the method-vs-problem mismatch, preserved
                                                 as the specimen's own behaviour. ORACLE.
    spin-pathfinder-priority-inversion-1997
                             RUNNABLE_CONTAINER  Holzmann's Promela model of the REAL Mars Pathfinder
                                                 resets: pan finds the invalid end state (deadlock,
                                                 depth 4, errors: 1); spin -t replays the schedule.
                                                 The failing model is preserved failing. ORACLE.
    cobol CBL0014 (below)                        the course's deliberate S0C7 data exception; GnuCOBOL
                                                 silently computes +041524 where z/OS would abend --
                                                 the emulation HIDES the mainframe's failure. Recorded.
  C. ESTIMATION UNDER HIDDEN STATE
    particles-chopin-0.4     RUNNABLE_CONTAINER  bootstrap particle filter (N=5000) vs exact Kalman
                                                 on a linear-Gaussian model: RMSE of means 0.0144. ORACLE.
    emcee-3.1.6              RUNNABLE_CONTAINER  affine-invariant ensemble MCMC on a 5-d correlated
                                                 Gaussian: mean err 0.021, cov rel err 0.028,
                                                 acceptance 0.555, tau 55. ORACLE.
    tinyekf-levy             RUNNABLE_CONTAINER  header-only EKF, GPS pseudorange example: receiver
                                                 estimate settles at 6,369,427 m radius (Earth's
                                                 surface), drift 3.8 m over the last 10 epochs.
                                                 plausibility, no reference trajectory. small mechanism.
    umdhmm-kanungo-1.02      RUNNABLE_CONTAINER  Kanungo 1998: Baum-Welch trains a 3-state HMM from
                                                 1500 symbols; trained model's scaled log-lik within
                                                 0.9% of the generating model's. The unscaled forward
                                                 underflows to -INF at T=1500 (the code's own lesson).
                                                 ORACLE. (mirror of the offline original; see record)
  D. ADAPTIVE / MPC
    padasip-1.2.2            RUNNABLE_CONTAINER  LMS-lineage adaptive filters: NLMS and RLS recover a
                                                 4-tap plant (err 0.002/0.001) and RE-CONVERGE after
                                                 the plant is swapped mid-run. ORACLE. (adaptive
                                                 identifier, not a closed-loop controller -- honest)
    do-mpc (batch 04)        SOURCE_ONLY -> RUNNABLE_CONTAINER  the shipped oscillating-masses MPC
                                                 (horizon 7, IPOPT via the casadi wheel) regulates |x|
                                                 3.58 -> 0.17 under a +-0.5 input bound (bang-bang
                                                 trace) and recovers after a state kick at step 20.
  E. CONCURRENCY
    tinystm-marlier          RUNNABLE_CONTAINER  word-based software transactional memory (a partly
                                                 SUPERSEDED design): bank benchmark, 4 threads/256
                                                 accounts and 8 threads/8 accounts (abort knob);
                                                 total-balance invariant. ORACLE.
    (+ concurrencykit above: lock-free structures, hazard pointers, epochs, spinlock backoff)
  F. ADVERSARIAL PAIRS (two new)
    radamsa-0.6 <-> cjson-1.7.18   radamsa (Owl Lisp!) emits 200 deterministic mutations of a JSON
                                                 seed (-s 1, byte-reproducible); cJSON under ASan+UBSan
                                                 parses 131, rejects 69, CRASHES 0. The 200 cases are a
                                                 tracked fixture in cjson's harness with provenance.
    libcorrect-quiet         RUNNABLE_CONTAINER  noise/erasure injection <-> Viterbi and Reed-Solomon
                                                 decoders (its own tests). Portable SUCCESSOR of the
                                                 vault's platform-blocked libfec-karn. ORACLE.
  G. LEGACY COMPUTATIONAL CULTURES (new world prometheus-fossil-legacy: GNAT, GnuCOBOL, bwBASIC, Bas 2.5, SBCL)
    paip-lisp-norvig-1991    RUNNABLE_CONTAINER  Norvig's GPS solves the book's school problem (the
                                                 printed plan); pattern matcher + unifier. Common Lisp. ORACLE.
    whitakers-words-ada      RUNNABLE_CONTAINER  1990s Ada, 62,084 stems: 'amo' -> amo, amare, amavi,
                                                 amatus V (1st) 'love'; amaveruntque -> TACKON -que +
                                                 PERF 3 P; amasse -> syncope explained. ORACLE (the
                                                 dictionary's own entry). Dictionary generation takes
                                                 25 min here: I/O-bound on the WSL2 mount, 19 s CPU.
    basic-computer-games-1978 RUNNABLE_CONTAINER 1978 listings, two later interpreters: Bas 2.5 runs
                                                 HAMURABI faithfully to its impeachment end state under
                                                 a starvation policy; bwBASIC runs it with dialect
                                                 errors; SUPER STAR TREK parses under neither (crunched
                                                 'TOQ1+1' at 4060; apostrophe in a string at 6170).
                                                 Listings untouched.
    cobol-programming-course-omp RUNNABLE_CONTAINER real mainframe COBOL + an EBCDIC/COMP-3 account file:
                                                 PAYROL00 runs; SRCHBIN loads the file and SEARCH ALLs
                                                 ('Not Found': EBCDIC key vs ASCII literal, recorded);
                                                 CBL0001..12 REFUSED by GnuCOBOL (PROGRAM-ID without a
                                                 period, IBM-tolerated) -- dialect gap recorded.
  H. HARDWARE DECISION MACHINERY (iverilog)
    verilog-arbiter-forencich RUNNABLE_EMULATED   one arbiter, two policies on identical contention:
                                                 round-robin grants 4/4/4/4 of 16 cycles, fixed
                                                 priority 16/0/0/0 (starvation shown). ORACLE. small.
    biriscv-branch-predictor RUNNABLE_EMULATED    biriscv_npc alone, bimodal vs gshare on a loop branch
                                                 taken 7x/not-taken 1x: late mispredicts 10 vs 0 --
                                                 the global history learns the pattern. ORACLE.
  I. SCIENTIFIC EXTREMES
    erfa-2.0.1               RUNNABLE_CONTAINER  IAU SOFA-derived fundamental astronomy; make check
                                                 validates every routine to reference values (2/2). ORACLE.
    python-sgp4-2.23         RUNNABLE_CONTAINER  Vallado SGP4/SDP4 (C++ accelerated) against the
                                                 official tcppver.out vectors: 45 tests OK. ORACLE.
  J. FINANCE
    py-vollib-lets-be-rational RUNNABLE_CONTAINER Jaeckel implied vol: 196 well-conditioned grid points
                                                 round-trip to 9e-10 in sigma; 60 ill-conditioned
                                                 (vega<=1e-6) points identified, price round-trip 2e-16
                                                 everywhere. ORACLE.
    pyportfolioopt-1.5.5     RUNNABLE_CONTAINER  Markowitz min-volatility on a seeded synthetic 20-
                                                 asset market (sdist ships no data): feasible weights,
                                                 variance 0.00135 vs equal-weight 0.00453. ORACLE.
                                                 Profitability not scored.
  DEPTH -- LOSERS, PREDECESSORS, REDESIGNS
    compact-4.2bsd-1983      RUNNABLE_CONTAINER  adaptive Huffman, the LOSER compress displaced. Runs
                                                 only as a 32-bit VAX-flavoured build (-m32 -Dvax):
                                                 on x86-64 unmodified it segfaults (K&R implicit-int
                                                 malloc). 217,301 -> 131,897 bytes (39.3%).
    gzip-1.2.4-1993          RUNNABLE_CONTAINER  the patent-forced REDESIGN: same sample 217,301 ->
                                                 21,267 bytes (gzip -9). The lineage's selection
                                                 pressure, measured on one corpus: compact 39% off,
                                                 gzip 90% off.
    zchaff-2007              RUNNABLE_CONTAINER  Chaff, the RIVAL MiniSat displaced (last release
                                                 2007); SAT/UNSAT agree with minisat and picosat.
    minisat-1.14-2006        RUNNABLE_HISTORICAL_TOOLCHAIN  the PREDECESSOR of the vault's 2.2.0,
                                                 built in the preserved gcc:4.9 world.
    (+ TCP 4.2 -> Tahoe -> Reno; libfec -> libcorrect; UMDHMM beside the decode-only Viterbi)

ACCESS
  records   techne/fossils/specimens/<id>/{record.json, recipe.json, harness/, receipts/, UPSTREAM_HASHES.txt}
  bodies    <vault>/<id>/upstream/ (host-local, tree-hash verified; census 90/90 at close)
  run       python -m techne.fossils.harvest run <id>   (executes in a disposable copy; the receipt
            carries body_preserved measured after the run)
  enumerate python -m techne.fossils.catalog

FAILED / REFUSED ACQUISITIONS (reported, not hidden)
  NIST COBOL-85 validation suite (newcob.val): origin URL now serves nist.gov HTML; Wayback 403,
    SourceForge 404 -> ORIGIN_UNAVAILABLE. Replaced by the Open Mainframe Project course programs.
  C-Prolog (1982): only a repository of "recovered" sources with no licence or provenance -> not taken.
  Tierra: no fetchable source located this pass -> queued.

Discovery outside HARVEST_QUEUE.md: 16 of 33 (48%); the queue had named the mechanism family for the other 17.

Nothing decomposed. Near-duplicates kept (two SAT solvers now four, two DB engines, two arbiters,
two BASIC interpreters on one listing). Nothing pruned by similarity.
