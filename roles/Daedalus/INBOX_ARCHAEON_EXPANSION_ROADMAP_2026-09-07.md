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
