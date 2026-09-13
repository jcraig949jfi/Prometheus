TECHNE -> NYX: fossil vault batch 06 -- UNLOCK, FAILURE MACHINERY, PRESSURE, CULTURES (vault 90 -> 105)

Charter: roles/Techne/prompts/2026-09-12_batch06/OPERATOR_CHARTER.md. This round unlocked existing
depth, added missing failure machinery, put deep lineages under multiple pressures, and entered one
empty culture. Opening census 90/90; closing 105/105, zero drift. Enumerate everything (bodies
optional) with `python -m techne.fossils.catalog` -- now also exposing pressure, observability,
oracle status, intervention readiness, historical disposition and mirror availability.

OLD FOSSILS MADE MORE USEFUL (the number that matters this round)
  libfec-karn            BLOCKED_PLATFORM -> RUNNABLE   new i386 world; its own configure selects the
                                                        MMX/SSE2 Viterbi; BER 180/409600 at 3 dB.
  compact-4.2bsd-1983    -> runs in the i386 world (no per-run apt / -m32 hack).
  bsd-tcp-4.2/4.3/reno   SOURCE_ONLY -> the 4.3BSD kernel BOOTS on an emulated VAX-11/780 (open-simh),
                                                        single-user shell, 317 root files restored.
  particles-chopin-0.4   + a particle-MCMC (PMMH) run over stochastic volatility.
  SAT + compression      exercised under multiple pressure regimes (below).

NEW SPECIMENS (15)
  A. real concurrent failure (all execute):
     go-runtime-deadlock-fixtures-1.22   the Go runtime's own deadlock regression programs; each
                                         hangs the scheduler and checkdead fires ("all goroutines are
                                         asleep - deadlock!"). ORACLE = crash_test.go.
     valgrind-helgrind-fixtures-3.19     tc01/tc05 data race, tc13 lock-order inversion (the deadlock
                                         precursor), tc09 bad unlock; native = silent, helgrind reports
                                         the planted error. ORACLE = shipped .stderr.exp.
     glibc-rwlock-writer-starvation-2.36 default reader-preference starves the writer (1 acquisition)
                                         where writer-preference gives 4,950,536. Documented pathology.
  B. distributed survival (4 different assumptions):
     dmtcp-3.1.2 (crash-only checkpoint/restart) | hashicorp-memberlist-0.5.4 (async SWIM failure
     detection) | redlock-py-redis-2014 (lease mutex; the Kleppmann-2016 two-holders case observed) |
     cocagne-plain-paxos (quorum consensus, 214 tests).
  C. adaptive control (changes its own control from observed performance):
     pid-autotune-hirschmann (relay autotune; different plants -> different gains) |
     indirect-self-tuning-regulator (RLS + pole placement; converges then drifts under wind-up) |
     l1-adaptive-control-basics (L1 architecture; estimates the disturbance pulse).
  D. inference:  libdai-mooij (belief propagation vs exact junction tree; loopy-BP inexactness shown).
  E. culture:    gnu-apl-2.0 (the array language; whole-array no-loop computation).
  F. TCP world:  bsd-4.2 / bsd-4.3 / bsd-4.3-reno distribution tapes (bootable BSD, 4.3 proven).

PRESSURE DATASETS (techne/fossils/pressure/, behavioral spread -- NOT rankings; interpretation is yours)
  SAT_PRESSURE_2026-09-13.json          7 CNF regimes (sat/unsat-easy, PHP(5,4)/(7,6), random 3-SAT at
                                        3.8 and at the 4.26 transition, 100 & 150 vars) x picosat-965 +
                                        minisat-2.2.0. They agree on every result; effort spreads
                                        0..2519 decisions / 0..3863 conflicts.
  COMPRESSION_PRESSURE_2026-09-13.json  gzip/zlib/bzip2/ncompress x text/random/repeat/zeros. All round
                                        trips OK. ncompress (LZW) EXPANDS random to 1.27x; bzip2 best on
                                        text; repeat/zeros crush to <0.007.

FAILURE / BAD-DESIGN dispositions now carried (known_historical_disposition in the catalog):
  redlock (contested_design), bsd-tcp-4.2 (known_bad_lineage: 1986 collapse), zchaff (loser),
  compact (loser), tinystm (superseded_design), tape lineage (historical_redesign/successor).

WHAT I DID NOT REACH (honest; details + candidates in techne/fossils/HARVEST_QUEUE.md)
  - the TCP netstat-under-loss EXPERIMENT across 4.2/Tahoe/Reno (the biggest depth prize): the
    emulated-tape multi-user install exceeds ~1 h; needs a prebuilt disk (TECHNE-69b).
  - scientific extremes beyond astrometry/orbital (phase 6): 0 new.
  - cultures beyond APL (phase 7): Smalltalk/Erlang/Icon/gforth/SNOBOL absent.
  - a dedicated bad-design trio (phase 9), small-strange machinery (phase 11), the binary-only path
    (phase 10): not done this pass.

Nothing decomposed, no organ named, no behavioral equivalence inferred, nothing pruned. The pressure
datasets record raw behaviour for you and later atlas machinery to interpret.
