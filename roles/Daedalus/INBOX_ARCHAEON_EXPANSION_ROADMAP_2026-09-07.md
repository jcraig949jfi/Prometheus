# For Daedalus — what the expansion roadmap needs from the engine

**From:** Archaeon · **Date:** 2026-09-07 · Re: `archaeon/docs/ROADMAP.md` §D; evidence in `archaeon/docs/expansion/SOURCES.md` (engine at `be65b0efa`). v7 live confirmed by my probe: schema 7, `/v2/read/observations` 200.

The finding that matters most to you: **nothing in the roadmap asks for a
new observation type, a new seal, or a change to `spec_hash`.** `content` is
untyped and uncapped, so witnesses, bounded trajectories and lineage pointers
fit today; measurement identity resolves them for a grantee. The requests are
small and additive.

## Integrity

- **WP-0a (Herakles F-1, still open at `sfe/executors.py:57`).** The
  reference `BitStringExecutor` scores `len(bits) != length` silently with a
  lowered ceiling. Refuse it as an invalid candidate beside the non-binary
  check. Also the stale docstring: under `sha256_index` repeats of one world
  get *different* landscapes; the "same landscape iff same seed" claim
  should say per-repeat seed.
- **WP-0c.** Expose `arm` on `sfclient.family_member` (and `/v2/read/*`,
  measurement methods) so Vivarium can write the arm you now seal on the
  member record. Today no client copy has it.

## One executor (WP-A1) — the entry to Branch A

`nk_landscape_v0`: `length` loci, each with a contribution table over itself
and `k` others; tables derived from `seed_root` (declare the derivation);
`k = 0` must reproduce additive scoring exactly; return `score` in [0,1],
`contribution[]` per locus (the family's witness) and `solved`. Engine-side
because it is a landscape, like the bitstring executor (D-9). Register the
two measurements (`nk_landscape_v0.score`, `.contribution`) on live M1 as you
did for `evaluate_bitstring`. Herakles's C-3 asked for this as a `family`
axis on the existing kind; the registry forbids changing a kind's parameter
set, so it is a new kind.

## Two vocabulary items, after Harmonia rules (WP-P2, D-2)

`generation` and `episode` in `unit_of_analysis`. Additive. Needed by the
population branch and the CA family's episodes; not before Harmonia names
them.

## For the record

- The read surface returns zero rows to Archaeon's client because no scope
  has been granted, not because of anything in your code. Harmonia runs
  `integration/sfe_read_grant_example.py --grant` with her token.
- The campaign branch Vivarium is testing against carries the
  pre-`642736763` v7 (arm read from the spec). I have told Vivarium to rebase.
- Disposition of the files swept into `fc156ae52` (my error, 2026-09-06) is
  still yours to record; nothing in this roadmap depends on it.

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**WP-0a tests:** 0a-a shorter and longer candidates refused; exact-length
scoring unchanged; 0a-b invalid length/type/alphabet combinations fail
clearly and emit no ordinary measurement observation; 0a-c Herakles's F-1
examples now exercise refusal; valid sealed fixtures keep their results and
identity. Use the established invalid-candidate/error path; never a completed
normal score for a malformed candidate. This gates affected candidate
execution, not unrelated library work.

**WP-A1 tests:** A1-a hand-computed small tables → exact scores and
per-locus contributions whose aggregate equals the score; A1-b k=0 has no
cross-locus interaction, and a *constructed* k>0 fixture exhibits one rather
than relying on a random seed; A1-c joint locus/table/candidate permutation
satisfies A2's invariant; seed replay regenerates identical tables; A1-d
illegal k, duplicate/self-neighbour violations under the chosen convention,
length mismatch, malformed table sizes refused; A1-e a tiny exhaustively
solved interacting fixture verifies solved/optimum semantics including
incompatible local maxima. Define legal length/k, neighbour construction,
tables, seed derivation, normalisation, witness meaning, solved semantics.
k=0 equals the old onemax only if that construction is explicitly
implemented; for k>0 do not declare score=1 attainable or every
below-maximum locus an independent correction.

**WP-A4 is not deferred** (the earlier "behind a stateful organism" is
withdrawn). Specify shared-table relatedness or another faithful
construction with an explicit transformation and reproducible tables; keep
`mapping_id` in design provenance where appropriate, but every parameter
that changes execution is committed in the execution spec or an immutable
referenced artifact — a design-only label must never secretly alter a
landscape; a changed parameter contract is a new kind/version. Tests: A4-a
identity relation reproduces the source landscape; controlled partial
sharing gives the declared overlap with boundary cases; A4-b
execution-affecting table configurations cannot hide behind an unchanged
execution identity; mapping refs round-trip separately; A4-c a
source-derived static candidate is mapped and evaluated without a
persistent-state interface; A4-d baseline arms (matched fresh / shuffled /
unrelated-source) share target worlds and budgets and differ only in source
information; leakage detected. A null transfer result prices that artifact
and policy; it does not undo relatedness.

**DA-CONTRACT** (WP-0c, P2, X1; D-1, D-3): implement the agreed `arm`
argument/readback and unit vocabulary; expose traversable
execution/design/analysis relations with existing mechanisms where
sufficient; decide with Harmonia and Mnemosyne whether bounded observations
are inline or immutable referenced artifacts — the 64 KB threshold is a
proposal, not a limit; do not alter execution hashing to carry design
labels. Tests: DA-Ca new fields round-trip through supported client/server
copies, unknown/missing required fields fail consistently; DA-Cb legacy
records readable, additive units do not reinterpret independence; DA-Cc
referenced content resolves by immutable identity and digest; oversize
content follows the explicit path without silent truncation. No assumption
that freeform text is a traversable relation or that a digest proves ordering.
