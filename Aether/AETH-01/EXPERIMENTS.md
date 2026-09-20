# AETH-01 -- initialization regimes and spontaneous/seeded separation

Status: DRAFT. Depends on PHYSICS_SPEC_DRAFT.md and ECONOMICS.md.
Covers Design Task 5 only; the parameter-space phase map that RUNS
these regimes is HABITABILITY.md.

## Initialization regimes

Each regime is a recipe for the initial H*W*5 byte buffer plus the run
parameters (WRITE_COST, MAINTENANCE_COST, REPLENISH_NUMER,
REPLENISH_AMOUNT, MUT_NUMER). All randomized regimes draw from an
explicit, seeded, reproducible PRNG stream logged in provenance
(REQUIREMENTS.md) -- "random" never means "unrecorded."

1. **Random soup.** Every field of every cell drawn i.i.d. uniformly
   from its valid range (opcode uniform over 256 values -- i.e. WRITE
   at ~1/256 density; energy uniform 0-255). No structure at t=0.
   Purpose: the least-informative baseline; almost certainly DEAD or
   HOMOGENIZED, itself a required data point.

2. **Sparse soup.** As random soup, but opcode drawn so WRITE appears
   at a swept low density (e.g. 1-5%), all other cells RESERVED_INERT
   with random non-WRITE opcode byte; arg0/arg1/payload still uniform
   random for WRITE cells. Purpose: isolate the effect of active-cell
   density independent of the full 1/256 baseline; a central sweep
   axis for HABITABILITY.md.

3. **Structured positive control (SEEDED).** A hand-authored small
   pattern known, by direct inspection of its own opcode/arg0/arg1
   values, to cause at least one cell to repeatedly copy a specific
   payload into a specific neighbor field over multiple ticks (a
   minimal deterministic "template copier"), placed in an otherwise
   inert or sparse-soup background. Purpose: (a) confirms the
   observatory's detectors can recognize a KNOWN true positive; (b) a
   deliberately simple instrument, not a claim about spontaneous
   capability.

4. **Adversarial inert control (SEEDED).** A hand-authored pattern that
   LOOKS structurally suggestive (e.g., a periodic block of identical
   non-WRITE bytes, or a symmetric static arrangement) but contains no
   WRITE opcode anywhere, so it is causally inert by construction (it
   cannot change unless a rare mutation flips its opcode field).
   Purpose: a required true-negative check -- any detector that reports
   "construction" or "heredity" activity on this control has a
   confirmed false-positive bug, full stop.

5. **Resource-rich.** Any of the above, with high initial per-cell
   energy (e.g. near 255) and/or Regime-B-style dense replenishment.
   Purpose: tests whether abundance alone is sufficient/necessary for
   persistent structure, independent of density regimes 1-2.

6. **Resource-poor.** Any of the above, with low initial energy and
   sparse or zero replenishment. Purpose: the opposite extreme; likely
   DEAD or FROZEN quickly, itself informative (a "how little is needed
   to sustain anything" boundary probe).

7. **Heterogeneous environment.** A single world split into spatial
   zones with DIFFERENT parameters or initial densities/energy (e.g.
   one half resource-rich, one half resource-poor, or a density
   gradient across columns). Purpose: tests whether spatial
   heterogeneity itself (not present in any of regimes 1-6) creates
   pressure for structures that exploit a boundary or gradient --
   directly relevant to R8's "maintaining gradients or boundaries" and
   to later transplant-style experiments (AETHER_CONCEPT.md).

Regimes 3-4 are SEEDED instrument controls. Regimes 1-2, 5-7 are
SPONTANEOUS-origin regimes (no hand-authored functional pattern is
placed in them) -- note regime 7's zones may still be entirely
spontaneous-origin if only the *parameters*, not the initial content,
are hand-authored; only regimes 3-4 place a hand-designed FUNCTIONAL
BYTE PATTERN into the world.

## How spontaneous and seeded evidence stay separated

This is a hard requirement (R1, HEREDITY_REQUIREMENTS.md), not a
convention:

1. **Provenance tag is mandatory and physics-invisible.** Every run's
   provenance record (REQUIREMENTS.md) carries an `instrument_class`
   field: `SPONTANEOUS` or `SEEDED_CONTROL`, plus, for seeded runs, the
   exact byte pattern and placement used. This tag lives ONLY in
   run metadata (observatory/provenance layer) -- it is never encoded
   into the lattice bytes themselves and cannot be read by any cell
   (R1, R10).
2. **No pooling across classes.** Any statistic, detector calibration,
   or scientific claim must report SPONTANEOUS and SEEDED_CONTROL
   results separately. A seeded run's detector firing may only be used
   to validate that the detector CAN fire on a known true positive
   (regime 3) or must NOT fire on a known true negative (regime 4) --
   never combined with, or substituted for, a spontaneous-run result.
3. **A seeded positive control produces exactly one type of claim:**
   "the detector correctly identifies this known instrument." It can
   NEVER be cited as "we observed construction" in the scientific
   (spontaneous-origin) sense, regardless of how interesting its
   trajectory looks -- this must be stated in the header of any report
   that includes a regime-3 result (HEREDITY_REQUIREMENTS.md).
4. **Automated cross-contamination check, required before any
   spontaneous-origin claim.** Compute a structural fingerprint
   (e.g. a hash of the byte-pattern-relative-to-itself, translation/
   rotation-normalized) of the candidate spontaneous structure and
   compare it against the fingerprint library of ALL seeded patterns
   ever used (regimes 3-4 and any future ones). A match is a hard stop
   -- either a genuine reinvention worth extra scrutiny, or (far more
   likely at first) a campaign-script bug that leaked a seeded pattern
   into a nominally spontaneous run. This check runs automatically as
   part of any claim pipeline, not manually and not optionally.
5. **Campaign configs are versioned artifacts.** The exact byte pattern
   and RNG seed used to generate every regime-1/2/5/6/7 initial state
   is itself logged (not just "random soup, seed=X" in prose) so a
   contamination investigation can always reconstruct exactly what was
   run.

## What this file deliberately does not do

Does not specify detector thresholds, does not specify what counts as
"interesting" output, does not run anything. Regime parameters (soup
density, energy levels, replenishment rates) are swept by the
habitability campaign (HABITABILITY.md), not fixed here.
