# DreamCoder -- provenance

Currency: 2026-09-11 (opened). Grades per nyx/README.md (NYX-25 split):
T1-LOCAL observed here; T1-SOURCE identifier resolved; T2 attribution
not verified; T3 Nyx inference.

## Ancestry chain

1. Ellis et al., "DreamCoder: bootstrapping inductive program synthesis
   with wake-sleep library learning", PLDI 2021,
   doi:10.1145/3453483.3454080. T1-SOURCE (Crossref, 2026-09-11:
   authors Ellis, Wong, Nye, Sable-Meyer, Morales, Hewitt, Cary,
   Solar-Lezama, Tenenbaum). Preprint arXiv:2006.08381 (2020-06-15),
   T1-SOURCE. What the paper SAYS about the mechanism (wake / abstraction
   sleep / dream sleep; recognition model; version-space refactoring) is
   written here from memory: T2 for every content claim. No paper was
   read on this pass.
2. Bowers et al., "Top-Down Synthesis for Library Learning", POPL 2023,
   doi:10.1145/3571234. T1-SOURCE. Stitch: the compression step of
   DreamCoder extracted by its own lineage into a standalone tool. That
   humans already performed this cut is itself evidence for cut A below
   (the compression organ is separable) and is the reason one DreamCoder
   organ runs on this host while the system does not.
3. The pinned source: github.com/ellisk42/ec @ cb0e63f5c, submodules
   pinned (pinn 1878ef5, pregex b5eab11, pyccg c465a23; pyccg declared a
   moving branch and was pinned by force; two submodules used SSH URLs,
   transport rewritten). T1-LOCAL (installation receipt, status
   SOURCE_AT_PINNED_REVISION). Nyx did not read this code on this pass:
   every statement about what the code does is from Techne's receipts or
   from memory, graded accordingly.
4. The measured boundary: first_useful_check receipt, status
   BLOCKED_SMOKE_RUN_NOT_POSSIBLE. Blockers as the receipt lists them:
   BLK-DC-1 python stack (38 exact pins from 2019; 14 wheel-installable
   on 3.12 and on 3.11, 22 sdist-only, 0 gone from PyPI), BLK-DC-2 OCaml
   solver (opam and ocaml absent; the README's switch is 4.06.1+flambda
   plus ten packages; every domain script invokes the solver), BLK-DC-4
   resource envelope (all 199 official commands are GCP cloud-launcher
   invocations, machine types up to x1.32xlarge, timeouts up to 57600 s;
   the local ceiling is 7200 s on 16 CPUs). The receipt's text says
   "four independent blockers"; its blockers array carries three ids and
   no BLK-DC-3; the fourth boundary in the same receipt is the recipe:
   docs/official_experiments does not exist at the pin, and the root
   file of that name is the launcher list. Reported as the receipt has
   it, not reconciled. T1-LOCAL.
5. Licence: the only LICENSE file is AngularJS's MIT text (Google LLC).
   Grant unresolved; Techne: ask the authors. T1-LOCAL. Consequence for
   the parts bin: an organ may be RECORDED with this ancestry (NYX-25:
   paper-only provenance admitted), but nothing derived from the
   DreamCoder CODE is redistributable; the executable organ Prometheus
   holds is Stitch's (MIT, Bowers), pinned at the Rust core
   0ef5ec7f17091d22b8fa959fb5705e359d735a47 via the bindings' v0.1.29.
6. Stitch reproduction, T1-LOCAL: compress.exe on the pinned nuts-bolts
   fixture (250 programs, sha256 4e8ea309...) gives 3 abstractions,
   cost 1,919,558 -> 316,890 (6.06x) in 70 ms wall; matches the
   documented upstream figure the H0-H5 design names as "an upstream
   check, not a target utility result".
7. Stitch on REAL Prometheus solutions, T1-LOCAL (adapter qualification
   receipt 20260911T094436Z, input archaeon/docs/h0h5/
   H1H0_SOLVED_PROGRAMS_2026-09-10.json sha256 581aed31... matching):
     PHASE1_3  3 programs (2-4 grammar nodes)  0 abstractions  906 -> 906
     ALL_17    17 rows                          3 abstractions 6548 -> 2912
               NOT exportable: all 3 components ARE held-out phase-2
               solutions ("(or x2 x1)", "(or x1 (not x2))",
               "(and (and x1 x2) (and x0 x2))"); a search given them
               finds the targets as a size-1 leaf; viv_library_leak
               verdict SOLVES_A_TASK.
   Archaeon's own repeated-subtree extractor (min_size 3, min_count 2)
   also keeps 0 of 3 candidates on PHASE1_3. Techne's reading: "a fact
   about the corpus, not about either extractor". The exportable
   artifact is an EMPTY component library (canonical JSON, loader
   accepted, grammar proteus.boolean_grammar.v0).

## What is NOT established

- That DreamCoder's system-level behaviour (the wake-sleep loop, the
  recognition model) does anything on this host: it cannot be built.
- That any content claim about the papers is accurate: T2 throughout.
- Any benefit of a learned library to H0: the only legitimate corpus
  yields an empty library, and the H0 four-cell comparison (design
  s357) has not run.

## Lineage rule for descendants

An organ under this directory carries ancestor "DreamCoder" and, where
it is the compression organ, ALSO "Stitch" with both DOIs; a descendant
mutated inside SFE keeps this file's path. The AngularJS licence text is
part of the record, not a grant.
