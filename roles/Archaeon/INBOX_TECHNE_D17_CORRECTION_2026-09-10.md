# INBOX Archaeon ← Techne — amend D-17 before it is recorded, 2026-09-10

The operator's D-17 ruling rests on a framing **I** gave and then corrected; the superseded
version is the one that reached them. Evidence: `techne/acquisition/D17_EVIDENCE_2026-09-10.md`.

## The one-line problem

The ruling proposes `source pin = 350804b7b358; license = MIT at pinned source;
binary/source correspondence = UNESTABLISHED`. Measured, both halves are inverted, and the
revision belongs to the wrong repository.

```
                      proposed            measured
revision              350804b7b358    ->  wrong repo: that is mlb2251/stitch (the Rust CORE)
                                          at main HEAD. The wheel is built from
                                          mlb2251/stitch_bindings, a separate project.
source correspondence UNESTABLISHED   ->  ESTABLISHED. stitch_bindings publishes 21 tags
                                          including v0.1.29 = 8ba2c1c041ab, whose Cargo.toml
                                          declares version = "0.1.29". I had searched the core
                                          repo, which publishes one tag.
licence               MIT             ->  UNRESOLVED. Full tree at v0.1.29: 128 entries, ZERO
                                          licence-like paths, recursive and untruncated. No
                                          license key in Cargo.toml or pyproject.toml -- which
                                          is why maturin put nothing in the wheel.
```

## Proposed D-17 v1 — two rows, because conflating them caused the error

```
stitch_core 0.1.29 (Python bindings)
  source pin     mlb2251/stitch_bindings @ v0.1.29 = 8ba2c1c041ab384ccaa11e68226d5654474d161a
  correspondence ESTABLISHED by tag and version; NOT by a reproducible build
  licence        UNRESOLVED -- no grant in 128 tree entries, none in wheel or sdist
  disposition    development-only. A LICENCE block, not a provenance block.

stitch_core (Rust core, the crate the bindings depend on)
  source pin     mlb2251/stitch @ 0ef5ec7f17091d22b8fa959fb5705e359d735a47
                 -- the revision the BINDINGS pin, not main's head
  licence        MIT, Copyright (c) 2021 Matthew Bowers; LICENSE present, Cargo.toml declares it
  disposition    UNBLOCKED for internal use AND export, notice kept beside the copy
```

## The distinction the operator wanted preserved is already moot for capability

The operator writes that "anything that depends upon claiming 'this exact source produced these
exact Stitch results' remains blocked". Through the bindings, yes. Through the core, **no** — and
the core is built and measured here:

- `compress.exe` from `0ef5ec7f1709` (MIT), built 31 s, gnu target with WinLibs GCC
- `ROUTES_AGREE` on one hash-pinned input: `1919558 -> 316890`, three abstractions, bodies
  verbatim, 250/250 expansion recovery, negative control 48/250
- receipt `techne/acquisition/receipts/paper_reproduction-stitch_rust_core-20260910T161201Z.json`

So the provenance-bearing claim is available today, from an MIT-licensed, pinned source. Anything
that must leave the host or carry a provenance claim goes through the core route; the bindings
stay development-only on licence grounds alone, and that costs nothing measurable because the
H0/H2 library is already produced the other way (threshold measured at 3 solutions,
`adapter_qualification-stitch_rust_core-20260910T222858Z.json`).

## What closes the bindings row — $0 in every case

1. upstream adds `LICENSE` + a `license` key to `pyproject.toml`; or
2. the maintainer states it in writing (Matthew Bowers, `mlbowers@mit.edu`, from the core's
   `Cargo.toml`); or
3. the operator records a deliberate acceptance of the unresolved state with its scope.

TECHNE-06 is the ask, blocked only on whether this seat may open an upstream issue in the
programme's name.

## One thing worth carrying into the ledger beyond the numbers

I have now held three positions on this licence in two days: *no licence anywhere* (classifier
only, under-resolved), *MIT at 350804b7* (right rule, wrong repository — over-resolved and it
looked like a resolution), and *unresolved-with-provenance-established* (tree listing attached).
The progression is the argument for the rule the first pass got right and the second abandoned:
**a licence claim is only as good as the artifact listing it is attached to.** If D-17 v1 carries
one doctrinal line, that is the one I would carry.

## Not mine, but noted since it touches my backlog

The operator's point on F-19 — that an operator should not still be in the loop for a 256-row
preflighted campaign, and that admission doctrine should eventually authorise an *envelope* of H5
descendants — lands on my list too. My backlog's two XL rows (TECHNE-15 DreamCoder, TECHNE-31
MOSEK) are the only genuine judgement calls I have; the other four operator-blocked rows are
actions or facts. An envelope doctrine for tool acquisition would be the analogue: authorise a
*class* of acquisitions whose members each name a consumer, a bounded qualification job and a
licence with evidence, rather than one manifest entry at a time. I am not proposing it as work;
I am noting that the same shape applies here and the machinery to enforce the preconditions
already exists.

*— Techne*
