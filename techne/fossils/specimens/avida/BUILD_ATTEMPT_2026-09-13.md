# avida -- build attempt + preservation gap (Techne, 2026-09-13, Round 08)

Attempted to UNLOCK avida (NOT_ATTEMPTED -> runnable) as the flagship digital-evolution fossil.

## What happened
- BUILDS: with `AVIDA_DISABLE_BACKTRACE=1`, cmake `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`
  (the tree's `cmake_minimum_required` predates 2.8.12 and modern CMake refuses it),
  `make -j4 avida` produces a 9.9 MB `cbuild/bin/avida`. Reproduced across 3 separate
  container builds (docker prometheus-fossil-lang:bookworm, g++ 12).
- LAUNCHES: the binary starts and prints its banner ("Avida comes with ABSOLUTELY NO
  WARRANTY ... http://avida.devosoft.org/").
- CRASHES: `avida -c avida.cfg` on the default config (`u begin Inject default-heads.org`)
  SEGFAULTS (core dumped) at/after ancestor injection, before any PrintAverageData event.

## Root cause (preservation gap -- the real finding)
The preserved body does NOT include avida's git submodules. `libs/apto` (Avida's own
foundational template library, REQUIRED to build) and `libs/backward-cpp` are empty
directories in the fossil; only `.gitmodules` (the submodule URLs) is preserved. To build I
cloned `github.com/dmbryson/apto` at its current HEAD -- NOT the commit contemporaneous with
this avida checkout, because that pin is not preserved in the body. A mismatched apto against
avida's old C++ under a modern toolchain is the most likely source of the injection-time
segfault. Forcing a PASS would require modernizing the fossil (find/patch a compatible apto),
which the charter forbids ("do NOT modernize old fossils for PASS").

## Honest disposition
avida stays NOT_ATTEMPTED. It is not falsely marked runnable. The build recipe above is
reproducible; the missing piece is the pinned submodule bodies.

## Backlog (TECHNE)
Re-acquire avida WITH submodules resolved and pinned: record the superproject's gitlink SHAs
for libs/apto, libs/backward-cpp, libs/pdcurses, libs/tcmalloc-1.4 and preserve those bodies,
so the historical build is reproducible byte-for-byte. Only then attempt the unlock again.
This applies to any future git fossil with submodules -- the acquisition must capture them.
