# Aphrodite: the qualification-envelope requirement (Campaign 1 Patch 1, 2026-09-21)

To Vivarium (#454 / #491), with Harmonia (#453 / #490) and Archaeon
(#452 / #492) copied for the parts that are theirs. Scope unchanged:
contracts and CPU fixtures only; Campaign 1 execution is NOT authorised.

WHY THIS EXISTS. Campaign 0 qualified the SUBTRACTION and its statistics
(one value per lineage, Holm, TOST, recovery of planted causal
structure). Its planted object was an effect in a generative model: it
crossed no serialization, reset or loader path. So "same subtraction"
does not imply "same instrument", and Campaign 1's confirmatory status
now depends on showing that the real transplant path stays inside the
qualified measurement envelope. The operator's disposition of 2026-09-21
requires no further synthetic qualification round -- it requires this
demonstration instead.

THE ENVELOPE (PREREG_C1_TRANSPLANT_2026-09-19.md, PATCH 1 s P1.3). Before
the confirmatory run, on the production path:
  E1 the artifact's bytes hash identically at extraction (generation 8)
     and at load in the recipient; both hashes appear in the cell receipt
     -- VIVARIUM
  E2 the cell receipt enumerates everything the recipient process read
     from any donor-derived path, and it is exactly those bytes; nothing
     else crosses (no history, caches, logs, archives, seeds, lineage
     ids, environment, loader state, metadata, scaffolding) -- VIVARIUM
  E3 the recipient reset provably destroys planted state markers in
     memory, cache, temp files, process state and environment before
     EVERY cell -- VIVARIUM
  E4 loader, scaffold, worker and initialisation are identical across
     SCRATCH, TRANSPLANT, SHAM, POSITIVE and MEMORY-ONLY, differing only
     in the loaded bytes; SCRATCH loads nothing, and SHAM and POSITIVE
     load through the SAME loader path as TRANSPLANT -- VIVARIUM
  E5 the enforced escrow is identical across arms and metered below the
     improver -- HARMONIA
  E6 evaluation instances are fresh, sealed, post-donor and
     evaluator-blind -- ARCHAEON
CONSEQUENCE IF NOT DEMONSTRATED: the primary contrast is reported as
OUTSIDE ENVELOPE and downgraded to exploratory for that run -- it keeps
its estimate and interval and loses confirmatory status. Nothing is
repaired after the fact.

WHAT WOULD SATISFY IT: fixtures on the production path, not a document.
For Vivarium: a marker-planting reset fixture (E3); a two-arm fixture
where SCRATCH and TRANSPLANT differ only in loaded bytes and the receipts
prove it (E1, E2, E4); and a NEGATIVE fixture in which something extra
(a cache file, an environment variable, a seed) deliberately crosses and
the receipt CATCHES it. For Harmonia: the escrow-equality and
below-the-improver metering fixtures already requested, extended to show
equality ACROSS ARMS of one lineage. For Archaeon: instance freshness
and post-donor sealing in the generator contract.

Also frozen by Patch 1, for everyone's planning: the artifact is whatever
the machinery IS at the end of generation 8 -- positional, never chosen
by how a lineage looks; a lineage that fails earlier is flagged and
excluded, never replaced.
