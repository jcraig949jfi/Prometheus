TECHNE -> NYX: fossil vault batch 03 delivered (global-archaeology charter)

Charter: roles/Techne/prompts/2026-09-12_global_archaeology/OPERATOR_CHARTER.md. Batch 03
pushed into the thin axes (hardware/logic was empty) at high recall. Vault is now 41
specimens / 41 lineages / 5 decades. Techne acquires + proves-it-runs; Nyx chops.

BATCH 03 -- 19 specimens

  HARDWARE / LOGIC (the empty axis, now 2):
    picorv32                   RUNNABLE_EMULATED    RV32I CPU in Verilog; iverilog sim shows the
                                                    ifetch/read/write bus trace of the core running
    espresso-logic             RUNNABLE_CONTAINER   Berkeley two-level Boolean minimizer; -do verify
                                                    confirms the minimised cover = the same function
  OS SURVIVAL:
    dlmalloc                   RUNNABLE_CONTAINER   Doug Lea allocator; 2000-block stress, no clobber
    bdwgc-8.2.6                RUNNABLE_CONTAINER   Boehm conservative GC; its own gctest passes
    xv6-riscv                  SOURCE_ONLY          MIT teaching kernel (riscv gcc+qemu deferred)
  LANGUAGE MACHINES:
    pforth                     RUNNABLE_CONTAINER   ANS Forth stack machine (7 sq -> 49)
    femtolisp                  RUNNABLE_CONTAINER   bytecode Lisp+GC; upstream unittest.lsp passes
    gnu-prolog-1.5.0           RUNNABLE_CONTAINER   Prolog that COMPILES to WAM->native; append/3 works
  NUMERICAL (netlib Fortran):
    fftpack-netlib             RUNNABLE_NATIVE      Swarztrauber FFT; test.f driver runs (NO_ORACLE)
    quadpack-netlib            RUNNABLE_NATIVE      adaptive Gauss-Kronrod integration; dqags int x^2
                                                    over [0,3] = 9.0 to 1e-13 (oracle)
    eispack-netlib             RUNNABLE_NATIVE      eigensolvers; rs() eigenvalues match to 1e-8 (oracle)
  ESTIMATION / CODING:
    libfec-karn                BLOCKED_PLATFORM     Karn Viterbi+FEC; ships 32-bit x86 MMX ASSEMBLY
                                                    (mmxbfly27.s) that won't assemble on x86-64 -- needs
                                                    an i386 world (queued). Source pinned+hashed.
  COMPRESSION (three families + a version pair):
    zlib-1.3.1                 RUNNABLE_CONTAINER   DEFLATE (LZ77+Huffman); make test CRC round trip
    bzip2-1.0.8                RUNNABLE_CONTAINER   BWT+MTF+Huffman; sample round trip (cmp oracle)
    compress-4.2.4-lzw         RUNNABLE_CONTAINER   early LZW; ROUNDTRIP_OK
  REPRESENTATION:
    buddy-bdd                  RUNNABLE_CONTAINER   BDD package; (a&b)|(a&c) satcount == 3 (oracle)
    tinycc                     RUNNABLE_CONTAINER   Bellard C compiler; -run returns 45 and 42 (oracle)
  ARTIFICIAL LIFE / UNCONVENTIONAL:
    corewar-redcode            RUNNABLE_HISTORICAL_TOOLCHAIN  Redcode MARS; Py2 code run in a preserved
                                                    python:2.7 world; 5 assembler+simulator tests OK
    avida                      SOURCE_ONLY          digital-evolution platform (heavy cmake deferred)

REPORT FIELDS (the directive's list)
  specimens acquired            19 (vault total 41)
  lineages represented          19 new, all distinct (vault 41 unique lineages)
  decade distribution (batch)   1970s 3, 1980s 5, 1990s 7, 2000s 3, 2010s 1
  language distribution (batch) C 13, Fortran 3, C++ 2, plus Verilog, Python(2), Lisp,
                                Prolog/WAM, Forth, RISC-V asm
  execution-model distribution  native 3, container 11, emulated 1 (HDL sim), historical-
                                toolchain 1 (py2.7), source-only 2, blocked-platform 1 (i386 asm)
  runnable                      16/19 this batch (36/41 vault)
  observable                    every runnable specimen captured stdout in its receipt
  oracle-backed                 quadpack, eispack, buddy, tinycc, espresso, bzip2, zlib, femtolisp,
                                gnu-prolog, corewar, dlmalloc, bdwgc, picorv32(trace), compress
  source availability           19/19 pinned + tree-hashed (41/41 vault)
  historical versions acquired  1 PAIR: compress-4.2.4-lzw (1992) historical_version_of the
                                batch-01 ncompress-5.0-lzw-1985 (2021) -- same LZW lineage, ~30 yr
  hardware specimens            2 (picorv32, espresso) -- axis no longer empty
  artificial-life specimens     2 (avida, corewar)
  weird/unconventional          3 (corewar Redcode VM, avida digital organisms, buddy BDDs)
  anti-canon fraction           ~63% (12/19: espresso, dlmalloc, femtolisp, gnu-prolog, the three
                                netlib Fortran packages, libfec, compress-4.2.4, buddy, corewar,
                                xv6/avida) -- well above the 25% floor
  provenance gaps               none: every specimen has origin + exact version/commit + tree hash
  legal restrictions            none blocking; several copyleft (GPL/LGPL: ff-not-here, gnu-prolog,
                                bdwgc MIT, tinycc LGPL, glpk GPL) preserved with their licenses
  failed acquisitions           none (all 19 fetched)
  environment failures          libfec (32-bit x86 asm on x86-64 -> BLOCKED_PLATFORM, i386 world
                                queued); xv6/avida deferred by build weight, not failure
  deviations (recorded)         FF-style: gnu-prolog WAM bootstrap under modern gcc (built clean);
                                libfec configure emits invalid -march=x86_64; tinycc configure had
                                CRLF from my own git clone -> fixed vault.git_pin to force LF
                                (byte-exact preservation) and re-cloned; corewar is Python 2
                                (preserved py2.7 world, not ported); compress LZW round-trip oracle
  newly discovered candidates   added to HARVEST_QUEUE.md: espresso's ancestors (MIS/SIS/ABC logic
                                synthesis), the EISPACK->LAPACK transition, SLATEC (d1mach/xerror
                                chain seen here), Karn's i386 FEC world, Core War's pMARS lineage

A PRESERVATION note (techne/fossils/PRESERVATION.md) records the immutable-body guarantee:
every body is hashed and its origin recorded; off-host object storage for large bodies is the
operator's call. The vault.git_pin LF fix means git-cloned bodies are now byte-exact upstream.

CURRENT THIN AXES AFTER BATCH 03 (not hidden):
  - HARDWARE still thin: 2 specimens, both logic/CPU; no arbiter, cache controller, branch
    predictor, sorting network, NoC/routing fabric, or FSM-controller HDL yet.
  - PROBABILISTIC/ESTIMATION thin: libfec is blocked; no Kalman, HMM/Baum-Welch, particle
    filter, MCMC, or belief-net engine yet running.
  - CONTROL (PID/MPC/adaptive) EMPTY.
  - CONTENTION/RETRY/RECOVERY (TCP congestion, backoff, consensus, failure detectors) EMPTY.
  - NEURAL/CONNECTIONIST history EMPTY (perceptron, Hopfield, SOM, reservoir).
  - GAMES beyond chess thin (no Go/checkers/retrograde/MCTS-game).
  - Binary-only + lawful-recovery path not yet exercised.
  Next batches target these; the queue samples across them so no ecosystem dominates.

Nothing decomposed, no organ named, no algorithm modernised (old worlds via docker/iverilog/
py2.7); near-duplicates kept (three SAT solvers now: minisat/picosat CDCL + walksat SLS; three
compression families; two ECC families).

-- Techne, 2026-09-12, worktree Prometheus-worktrees/techne-pass-0911
