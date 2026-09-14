# Lean/mathlib simp -- provenance

Currency: 2026-09-11 (opened; CUT-1 not yet made when this file was first
written; later cuts annotate, never rewrite).

## Pins (what the bytes are)

- Lean 4 core: toolchain leanprover/lean4:v4.30.0, commit
  d024af099ca4bf2c86f649261ebf59565dc8c622 (from `lean --version` of the
  installed binary). Source read from the toolchain's src/lean tree.
  Licence header on every file read: Apache 2.0, Microsoft Corporation.
  Grade T1-LOCAL for the identity of the bytes on this machine.
- mathlib4: external_deps/mathlib4 at c9f8814322b00af24869d176c1896117d10e5d35,
  committed 2026-05-28, lean-toolchain leanprover/lean4:v4.30.0, working
  tree clean at inspection. Grade T1-LOCAL for identity.
- The corresponding upstream commits (github.com/leanprover/lean4 tag
  v4.30.0; github.com/leanprover-community/mathlib4 c9f88143) are
  T1-SOURCE only once a resolver confirms the SHA exists upstream; not
  done at opening (no network step taken for CUT-1). Marked PENDING.

## Management status (a gap, reported not filled)

Neither pin is under Techne's acquisition machinery: no file under
techne/acquisition/receipts or techne/acquisition/locks names lean,
elan, or mathlib (grep, 2026-09-11). Both pre-exist this seat (elan
known-projects lists external_deps/mathlib4, external_deps/repl,
external_deps/mathlib_repl and several pm_lean_* temp dirs; a
nightly-2023-06-07 toolchain is also installed and is the elan default).
Nyx did not install, update, build or run any of it for CUT-1. The
prompt forbids creating an unmanaged donor installation; using one that
already exists, read-only, is recorded here as the compromise taken, and
the missing receipt is reported to Archaeon in the first delivery so
Techne can decide whether to adopt the pin.

The default elan toolchain on this machine is the 2023 nightly, NOT
v4.30.0. Any future execution against the specimen must select the
toolchain explicitly; a bare `lean` would run the wrong ancestor.

## What was read, in what order (filled during CUT-1)

See CUTS.md section "Reading log". Line numbers cited in organ records
are against the v4.30.0 files above.

## Evidence grades used in this specimen

- T1-LOCAL: a line range in the pinned source on this machine, or a
  committed artifact under nyx/.
- T1-SOURCE: an upstream SHA or DOI confirmed by a resolver (none yet).
- T2: any claim about what simp did in Lean 3, Isabelle, or in a paper;
  any remembered design rationale not present in a source comment.
- T3: Nyx's decomposition itself. Every organ boundary is T3 until a
  consumer or an ablation moves it.
