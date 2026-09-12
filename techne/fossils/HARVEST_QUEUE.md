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
