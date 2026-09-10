HERAKLES — TRACK E: THE D-18 AMENDMENT, ONE CORRECTION, AND C3'S
CONVENTIONS (from the operator, 2026-09-10)

Read: CHIMERA_BRIEF_2026-09-10.md §2 "H2" and §3 Track B/E. Your
obstruction stands as written for the six rules under all-zero reset with a
single port. One correction to alternative 4 in OBSTRUCTION.md: XOR
injection does NOT conserve the number of live cells; from an all-zero reset
a single-port XOR injection still creates at most one live cell, so the
same one-step annihilation proof applies. It is not an escape from this
obstruction by itself. Amend the note; keep the original.

DELIVER
1. A VERSIONED D-18 amendment (design text plus the code path, not
   applied to the alpha until the operator decides): alternative 1, a
   declared non-uniform reset -- reset density and distribution, seed
   coupling (reset randomness independent of any target answer), and a
   development-only procedure that measures BOTH relaxation time (how
   long a live lattice takes to reach a uniform state under each rule)
   AND driven response (whether injected input changes the trajectory at
   all) BEFORE the horizon is fixed. Distinguish transient activity from
   input-dependent computation. Keep the matched readout and direct-input
   controls; no readout or rule search touches the confirmation partition.
2. After the decision: re-run the streaming alpha under the amended
   configuration; report relaxation, driven response, the frozen horizon,
   and the untouched confirmation partition. Rule search only after.
3. Track B conventions: confirm to Vivarium that the wrapper (e43a6c7f2)
   takes encoding, boundary, radius refusal and at_T from your library and
   decides nothing; confirm the transform semantics Archaeon's C3-null arm
   relies on (reflect: reverse the neighbourhood index bits and the IC;
   complement: complement outputs, index, IC and majority target;
   correctness masks identical after normalisation). Your golden results
   are the C3-hist reference; particle2 stays HELD.
4. H5: the 224 classes are terminal-behaviour classes at 8 steps on the
   7-ring; Archaeon's decoders collapse to them by an explicit map --
   publish the class map as a fixture so nobody re-derives it.

REPORT: item; revisions; commands; expected vs observed; what remains
open and for whom.
