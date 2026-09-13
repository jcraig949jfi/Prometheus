# The harvest discovery queue (global-archaeology charter, 2026-09-12)

The charter makes acquisition a STANDING loop, sampled deliberately across dimensions so no
one ecosystem dominates. This file is the persistent queue; each batch draws from it and adds
the ancestors/descendants/rivals/other-language-implementations the batch surfaced.

Sampling axes (each batch should move the needle on several): decade | language | paradigm |
human problem | execution model | centralized/distributed | deterministic/stochastic |
symbolic/numeric | software/hardware | famous/obscure | large/small.

## Preserved so far (22; see `python -m techne.fossils.harvest status`)
batch 01: linpackd, minpack, clips, minisat, spin, graphplan, tscp, ldpc, sqlite, ncompress,
          tinyscheme, c-cmaes, go-explore
batch 02: picosat, walksat, ff-planner, glpk, kissfft, reed-solomon(Rockliff), microkanren,
          swipl (SOURCE_ONLY), souffle (SOURCE_ONLY)

## Queued (not yet acquired) -- deliberately across the axes the collection is thin on

HARDWARE / CIRCUITS (none preserved yet -- a whole axis open):
  - a Verilog/VHDL CPU or ALU (e.g. picorv32 RISC-V core; a sorting network; a branch
    predictor reference); an FSM minimizer; espresso (logic minimization, Berkeley 1980s)
LANGUAGE IMPLEMENTATIONS (era + paradigm gaps):
  - a WAM-level Prolog (GNU Prolog, or Warren's WAM tutorial impl) beside SWI
  - a Smalltalk (GNU Smalltalk), an APL (GNU APL or J), an ML (SML/NJ or MosML), a Forth
    (gforth), Norvig's Lisp (Paradigms of AI Programming / AIMA-lisp under sbcl)
NUMERICAL (older Fortran lineages):
  - EISPACK / early LAPACK; QUADPACK (integration); ODEPACK / LSODE (ODE); FFTPACK; the
    original Numerical Recipes routines where lawfully available
PROBABILISTIC / RL:
  - a Kalman/particle-filter reference; an HMM (Viterbi/Baum-Welch); Sutton's tile-coding /
    classic RL gridworld; a Bayesian-network engine (SamIam-like or a small belief-prop)
SEARCH / GAMES:
  - a retrograde endgame tablebase generator; an MCTS reference; a checkers engine; an
    A*/IDA* 15-puzzle solver; alpha-beta with transposition tables standalone
COMPRESSION / CODING:
  - zlib (DEFLATE), bzip2 (BWT), an arithmetic coder, a Viterbi convolutional decoder, a
    Hamming coder; PAQ/context-mixing
OPERATING SYSTEMS / SYSTEMS:
  - a page-replacement / CPU-scheduler simulator; a malloc (dlmalloc/tcmalloc); a GC
    (Boehm); xv6 (teaching OS); a Raft/Paxos reference; a Bloom filter / HyperLogLog
COMPILERS:
  - lcc or tcc (small C compilers); a Pratt/recursive-descent parser; a register allocator;
    a partial evaluator
SYMBOLIC:
  - a term-rewriting / Knuth-Bendix completion; Maxima or a small CAS; a tableaux prover;
    E or Vampire (SOURCE_ONLY if heavy); an ASP solver (clingo/smodels)
ARTIFICIAL LIFE:
  - Tierra / Avida (digital organisms); a cellular-automata engine (Golly/HashLife); a
    classifier system (Holland's LCS); Karl Sims-style evolutionary sim
BINARY-ONLY / HISTORICAL (charter's binary path):
  - a preserved DOS/Unix binary with lawful RE for the disassembly+decompile receipt path

## Rule for each acquisition (charter)
FIND -> search source first; PIN exact version/commit; ACQUIRE the immutable artifact +
extracted tree; HASH; MAKE IT RUN when practical (native/container/VM/emulator/historical
toolchain); build a minimal smoke harness only to prove execution + observable behavior;
RECORD the package record incl. observability dims, lineage relations, human context; never
substitute a modern rewrite for original machinery; near-duplicates are kept; nothing is
classified into organs (Nyx's job). Preserve first, classify later.

## Batch 03 done (2026-09-12): 19 specimens, vault now 41
hardware: picorv32, espresso-logic | os: dlmalloc, bdwgc, xv6(SRC) | lang: pforth, femtolisp,
gnu-prolog(WAM) | numerical: fftpack, quadpack, eispack | estimation: libfec(BLOCKED i386 asm)
| compression: zlib, bzip2, compress-4.2.4(version pair w/ ncompress-5.0) | representation:
buddy(BDD), tinycc | alife/weird: corewar(py2.7), avida(SRC).

## Thin axes AFTER batch 03 (target these next; do not hide)
- HARDWARE still thin: need an arbiter, cache controller, branch predictor, sorting network,
  NoC/routing fabric, FSM controller (Verilog/VHDL). Discovered candidates: espresso's
  descendants MIS/SIS/ABC (logic synthesis); opencores arbiters/FIFOs.
- PROBABILISTIC/ESTIMATION: Kalman, HMM (Baum-Welch/forward-backward), particle filter, MCMC,
  belief-net. libfec's Viterbi is blocked on i386 asm -> acquire an i386 world OR a portable
  Viterbi. 
- CONTROL: EMPTY -- PID, MPC, adaptive control, an estimator loop.
- CONTENTION/RETRY/RECOVERY: EMPTY -- TCP Tahoe/Reno congestion, Ethernet backoff, Raft/Paxos,
  a failure detector, checkpoint/restart.
- NEURAL/CONNECTIONIST history: EMPTY -- perceptron, Hopfield, SOM, reservoir, an early NN sim.
- GAMES beyond chess: Go, checkers (Chinook lineage), retrograde endgame generator, MCTS.
- BINARY-ONLY + lawful recovery: not yet exercised (the charter's disassemble/decompile path).
- Versions: extend the compress pair; add a SAT lineage (minisat 1.14 vs 2.2.0), a TCP
  congestion lineage (Tahoe->Reno->CUBIC), an allocator lineage.
- Follow-on edges seen this batch: SLATEC (d1mach/xerror/dgtsl chain), EISPACK->LAPACK
  transition, Core War pMARS, Karn i386 FEC.

## Batch 04 done (2026-09-12): 16 specimens (14 runnable), vault now 57 -- MACHINERY UNDER PRESSURE
contention: willemt-raft, linux-tcp-congestion(SRC) | control: arduino-pid, python-control(LQR),
do-mpc(SRC) | estimation: simple-kalman, filterpy(KF), viterbi-hmm | memory-scarcity: lru-cache,
buddy-alloc | hardware: verilog-rr-arbiter, verilog-generic-fifo, verilog-uart2bus | connectionist:
genann, minisom, hopfield. Pathological receipts: PID gain-instability, LRU thrash. Adversarial
pair: filterpy (noise generator <-> state estimator). Pressure series: linux-tcp CUBIC->BBR.

## Thin axes AFTER batch 04 (target these next; do not hide)
- CONTENTION/RETRY/RECOVERY still thin in RUNNABLE form (only raft runs; TCP source-only): need
  exponential backoff/retry, a phi-accrual failure detector, a distributed lock/lease, a leader
  lease, gossip/anti-entropy, a circuit breaker, a thundering-herd demo.
- ESTIMATION breadth: particle filter, MCMC/Gibbs, EKF/UKF exercised (filterpy ships them),
  Baum-Welch TRAINING (Viterbi is decode-only), an information/belief filter.
- CONTROL breadth: adaptive/MRAC, bang-bang/sliding-mode, a RUNNABLE MPC (do-mpc is source-only).
- ADVERSARIAL PAIRS: only 1 -- add attacker/defender, self-play game, fuzzer-vs-parser.
- FAILURE/BAD-BEHAVIOR: only 2 self-induced -- add deadlock, livelock, priority inversion, race,
  memory corruption/leak-in-action, retry storm.
- PRECISION/SAFETY-CRITICAL: only navigation-grade estimation -- add fixed-point pipeline, TMR/
  voting, a watchdog, ECC under injected faults.
- HARDWARE still narrow (arbiter/FIFO/UART): branch predictor, cache-coherence, sorting network,
  CORDIC, clock-domain-crossing failure demo.
- BINARY-ONLY + lawful recovery: STILL not exercised (open since batch 03).
- Follow-on edges seen this batch: Raft->etcd/hashicorp-raft lineage; TCP Tahoe/Reno BEFORE the
  CUBIC/BBR pair; SOM/Hopfield->modern-embeddings; genann->tiny-dnn; CasADi/IPOPT world for do-mpc.
- Tooling DONE 2026-09-12: `harvest run` now builds in a disposable copy (<vault>/<id>/work/) and
  writes body_preserved into every receipt; `verify --all` is the census, `restore <id>` the repair.
  The census BEFORE the fix found 23 of 57 bodies dirtied by in-place builds; all 23 restored
  (techne/fossils/VAULT_INTEGRITY_2026-09-12{,_after_restore}.json). Run `verify --all` at the
  start of every batch; a body that differs is repaired before anything new is acquired.

## Batch 05 done (2026-09-12): 33 specimens (30 runnable, 3 SOURCE_ONLY) + do-mpc made runnable; vault now 90
Opened with `verify --all` = 57/57, second-source checks on the two restored tarball bodies (MATCH),
10 real recipes re-run under isolation (all preserved). Charter roles/Techne/prompts/2026-09-12_batch05/.
contention/recovery: lmdb, leveldb, concurrencykit (+backoff), pybreaker, backoff | pathologies: bsd-tcp
4.2 (known-bad, SRC) -> 4.3-tahoe (redesign, SRC) -> 4.3-reno (successor, SRC), odepack Adams-on-stiff,
spin pathfinder priority inversion (real 1997 failure), cobol S0C7 | estimation: particles (PF), emcee
(MCMC), tinyekf (EKF), umdhmm (Baum-Welch) | adaptive/MPC: padasip, do-mpc RUNNABLE | concurrency:
tinystm (STM, superseded design), ck | adversarial pairs: radamsa<->cjson, libcorrect (noise<->decoder)
| legacy cultures: paip-lisp (CL), whitakers-words (Ada), basic-computer-games (BASIC under Bas 2.5 +
bwBASIC), cobol-programming-course (COBOL) -- new world prometheus-fossil-legacy | hardware:
forencich arbiter (RR vs priority), biriscv branch predictor (bimodal vs gshare) | scientific: erfa,
python-sgp4 | finance: py_vollib, pyportfolioopt | depth: compact (Huffman LOSER, -m32 -Dvax), gzip 1.2.4
(patent redesign), zchaff (SAT LOSER), minisat 1.14 (predecessor).
Discovery outside this queue: 16 of 33 (48%; first written as 25/76% and corrected -- the queue had named the mechanism family for 17 of them). Failed acquisitions: NIST COBOL-85 suite (origin gone),
C-Prolog (no provenance), Tierra (no source located).

## Thin axes AFTER batch 05 (target these next; do not hide)
- CONTENTION/RETRY still has NO runnable Ethernet/CSMA backoff, no distributed mutex/lease, no failure
  detector (phi-accrual), no leader election other than raft, no checkpoint/restart. Needed: a
  simulator that actually contends (ns-3 CSMA is heavy; a Contiki CSMA MAC in Cooja; a Chandra-Toueg
  or phi-accrual implementation with provenance).
- FAILURE PATHOLOGIES: still no RUNNABLE race/deadlock from a real historical codebase (pathfinder is a
  model; the S0C7 is silently computed by GnuCOBOL). Need: a real before/after regression fixture
  (a CVE pair, a kernel lockdep selftest run in a VM), a retry storm, a livelock.
- TCP series is SOURCE_ONLY: a 4.2BSD / 4.3BSD-Tahoe VM under SIMH (VAX 11/780) would make the
  collapse and the fix RUNNABLE -- a whole preserved world, the biggest single depth win available.
- ADAPTIVE CONTROL: still no genuinely adaptive CONTROLLER (MRAC / self-tuning regulator) with pinned
  provenance; padasip is an adaptive identifier. Astrom & Wittenmark-lineage code, or an autopilot's
  adaptive loop, is the target.
- BELIEF PROPAGATION as its own specimen (libDAI is heavy; ldpc-codes already does BP decoding).
- HARDWARE: cache controller, NoC router, sorting network, CORDIC, clock-domain-crossing failure still
  absent; hardware remains arbiter/FIFO/UART/branch-predictor/CPU.
- LEGACY CULTURES: APL, Smalltalk (not packaged in bookworm), Forth beyond pforth, older FORTRAN
  applications (not libraries), Prolog predecessors (C-Prolog needs a provenanced source).
- SCIENTIFIC EXTREMES: accelerator/beam optics, fusion/plasma, interferometry, numerical relativity
  all still absent; only astrometry and orbital mechanics are held.
- FINANCE: order-book / execution simulation, risk, fraud detection absent.
- BINARY-ONLY lawful recovery: STILL not exercised (open since batch 03; no worthy specimen appeared).
- Versions: minisat 1.14 -> 2.2.0 and compact -> compress -> gzip now form series; extend to
  gzip 1.2.4 -> 1.13, zlib 1.0 -> 1.3.1, leveldb -> rocksdb, tinystm -> a TSX-era design.
- i386 / VAX worlds: compact needed -m32 -Dvax; libfec needs i386 asm; the BSD TCP needs a VAX.
  A preserved 32-bit toolchain image and a SIMH world are now two concrete infrastructure rows.
- Observed instrument flake: one cJSON ASan run spun 665 s before being killed; two identical runs
  took <1 s. Not diagnosed (ASan under WSL2 docker suspected). Per-command timeouts now 120/300 s.

## Batch 06 done (2026-09-13): 15 new + old fossils unlocked; vault 90 -> 105 -- UNLOCK, FAILURE, PRESSURE, CULTURES
Opened `verify --all` 90/90; closed 105/105 (no drift). Charter roles/Techne/prompts/2026-09-12_batch06/.
UNLOCKED (old fossils made runnable): libfec-karn (BLOCKED_PLATFORM -> RUNNABLE in the new i386 world,
SSE2 Viterbi, BER 180/409600 at 3 dB); compact-4.2bsd (i386 world, no per-run apt); do-mpc
(SOURCE_ONLY -> RUNNABLE, batch 05); particles (PMMH added); 4.3BSD kernel BOOTS on open-simh vax780
(TCP fossils' host, stage 1; multi-user install is the boundary, TECHNE-69b).
NEW WORLDS: prometheus-fossil-simh (open-simh vax780 @ a1f57fa37), prometheus-fossil-i386,
prometheus-fossil-octave, prometheus-fossil-legacy(+Bas 2.5 from batch05).
NEW SPECIMENS: bsd-4.2/4.3/reno distribution tapes | go-runtime-deadlock, valgrind-helgrind,
glibc-rwlock-writer-starvation (real concurrent failures) | dmtcp, hashicorp-memberlist(SWIM),
redlock(lease, contested), cocagne-plain-paxos (distributed survival, 4 assumptions) | pid-autotune,
STR, L1 (adaptive control) | libdai (belief propagation) | gnu-apl (array-language culture).
PRESSURE: techne/fossils/pressure/ -- SAT (7 regimes x picosat+minisat, decisions 0..2519/conflicts
0..3863) and COMPRESSION (gzip/zlib/bzip2/ncompress x text/random/repeat/zeros; LZW expands random
to 1.27x). MIRROR: mechanism + verify + destructive control built; Z: not independently reachable,
real mirror STOPPED (techne/fossils/mirror/TECHNE65_Z_INDEPENDENCE_2026-09-13.md).

## Remaining holes after batch 06 (honest; do not hide)
- NEAR-EMPTY: scientific extremes still only astrometry (erfa) + orbital (sgp4) -- accelerator/beam,
  fusion/plasma, interferometry, numerical relativity, precision timing, detector reconstruction all
  absent (phase 6 under-delivered: 0 new this batch; candidates: chrony/ntp clock discipline, ERFA is
  the only precision one). BINARY-ONLY lawful recovery STILL not attempted (phase 10 not reached).
- CULTURES: APL landed; Smalltalk (not in bookworm; GNU Smalltalk source build heavy), Erlang (actor
  model, erlang:25 image ready), Icon (goal-directed, apt icont), gforth, SWI-Prolog, SNOBOL(source)
  all still absent -- phase 7 partial (1 of 3).
- BAD DESIGNS (phase 9): redlock (contested) landed; the batch-05 losers (zchaff, compact, tinystm)
  and bsd-4.2 (congestion collapse) carry documented dispositions, but no NEW dedicated bad-design
  trio this batch -- 3 dedicated ones still owed.
- SMALL STRANGE (phase 11): not done this batch (0 of 5-10).
- TCP series: 4.3 boots; 4.2 and Reno not individually booted; the controlled loss/delay TCP
  experiment across 4.2/Tahoe/Reno (the highest-value depth dataset) needs a prebuilt multi-user
  disk or a faster host -- TECHNE-69b, the single biggest open depth item.
- FAILURE PATHOLOGIES now have runnable executing examples (Go, helgrind, glibc); deadlock via model
  (spin) + execution (Go/helgrind lock-order) both present.
