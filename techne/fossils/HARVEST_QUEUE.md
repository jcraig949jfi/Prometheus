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
- Tooling: a runner mode that builds on a disposable copy of upstream/tree so in-place builds
  never dirty the preserved body (this batch git-clean'd 8 bodies back to the pin post-run).
