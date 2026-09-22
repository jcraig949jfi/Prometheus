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

1. **Random soup.** Every field of every site drawn i.i.d. uniformly
   from its valid range (opcode uniform over 256 values -- i.e. WRITE
   at ~1/256 density; energy uniform 0-255). No structure at t=0.
   Purpose: the least-informative baseline; almost certainly DEAD or
   HOMOGENIZED, itself a required data point.

2. **Sparse soup.** As random soup, but opcode drawn so WRITE appears
   at a swept low density (e.g. 1-5%), all other sites RESERVED_INERT
   with random non-WRITE opcode byte; arg0/arg1/payload still uniform
   random for WRITE sites. Purpose: isolate the effect of active-site
   density independent of the full 1/256 baseline; a central sweep
   axis for HABITABILITY.md.

3. **Structured positive control (SEEDED).** A hand-authored small
   pattern known, by direct inspection of its own opcode/arg0/arg1
   values, to cause at least one site to repeatedly copy a specific
   payload into a specific neighbor field over multiple ticks (a
   minimal deterministic "template state copier"), placed in an otherwise
   inert or sparse-soup background. Purpose: (a) confirms the
   observatory's detectors can recognize a KNOWN true positive; (b) a
   deliberately simple instrument, not a claim about spontaneous
   capability.

4. **Adversarial inert control (SEEDED).** A hand-authored pattern that
   LOOKS structurally suggestive (e.g., a periodic block of identical
   non-WRITE bytes, or a symmetric static arrangement) but contains no
   WRITE opcode anywhere, so it is causally inert by construction.
   **[REPAIRED per ASTRA_REVIEW_01.md S03: perturbation is copy-coupled, not
   an autonomous per-tick process -- see PHYSICS_SPEC_DRAFT.md "Perturbation
   (Mu)"]** If placed in a wholly `RESERVED_INERT` background, this
   pattern's bytes cannot change AT ALL, ever, at any `MUT_NUMER`,
   because perturbation only fires on a winning WRITE proposal and none
   exists anywhere in this configuration -- there is no "rare perturbation"
   path for a fully inert world. If placed in a sparse-soup background
   instead, it can change ONLY if a background WRITE site's proposal
   wins a contest targeting one of this pattern's sites (an ordinary
   external cause, not a spontaneous internal event). Purpose: a
   required true-negative check -- any detector that reports
   "construction" or "configuration transmission" activity on this control has a
   confirmed false-positive bug, full stop.

5. **Resource-rich.** Any of the above, with high initial per-site
   energy (e.g. near 255) and/or Regime-B-style dense replenishment.
   Purpose: tests whether abundance alone is sufficient/necessary for
   persistent structure, independent of density regimes 1-2.

6. **Resource-poor.** Any of the above, with low initial energy and
   sparse or zero replenishment. Purpose: the opposite extreme; likely
   DEAD or FROZEN quickly, itself informative (a "how little is needed
   to sustain anything" boundary probe).

7. **Heterogeneous environment.** **[REPAIRED per ASTRA_REVIEW_01.md
   S02(b), ACCEPT, see REPAIR_LEDGER_01.md -- narrowed scope: the
   `aeth01.v1` transition law reads exactly five GLOBAL scalar run
   parameters with no spatial index (PHYSICS_SPEC_DRAFT.md); a runner
   that varied `WRITE_COST` etc. BY ZONE would silently be executing a
   different, unspecified physics while claiming the `aeth01.v1` replay
   tuple.]** A single world, under the SAME five global run parameters
   for its entire extent, split into spatial zones with DIFFERENT
   INITIAL BYTE CONTENT ONLY -- e.g. different initial per-site energy
   levels or different initial WRITE density by zone (a density or
   energy GRADIENT across columns is legal; a `WRITE_COST` gradient is
   NOT). Purpose: tests whether spatial heterogeneity of INITIAL
   CONDITIONS creates pressure for structures that exploit a boundary or
   gradient -- directly relevant to R8's "maintaining gradients or
   boundaries" and to later transplant-style experiments
   (AETHER_CONCEPT.md). A genuinely spatially-varying LAW (per-zone run
   parameters) is a DIFFERENT, not-yet-specified physics, requiring its
   own `semantics_id` and its own replay-tuple extension (a parameter
   MAP, not five scalars) if ever pursued -- not silently implemented in
   a runner under the `aeth01.v1` label.

**[REPAIRED per ASTRA_REVIEW_01.md S06, ACCEPT, see REPAIR_LEDGER_01.md
-- the reviewed draft let regimes 5-7 "wrap" a seeded regime-3/4 pattern
while ALSO calling regimes 5-7 spontaneous-origin, a direct
contradiction: a seeded state copier with altered energy satisfied both
descriptions.]** Origin classification (`instrument_class`, below)
COMPOSES through every overlay: regimes 5-7 are OVERLAYS (resource/
energy/initial-content heterogeneity choices) applicable on top of
EITHER a regime-1/2 base (giving `SPONTANEOUS`) OR a regime-3/4 base
(giving `SEEDED_CONTROL`) -- they carry NO origin label of their own.
`instrument_class = SEEDED_CONTROL` if ANY hand-authored functional
byte pattern (regimes 3-4) is present ANYWHERE in the initial lattice
content, regardless of which overlay is additionally applied.
`instrument_class = SPONTANEOUS` only if the ENTIRE initial lattice
content derives exclusively from unstructured generation (regimes 1-2),
under ANY overlay. There is no configuration in which the same
initialization is validly labeled both ways.

## How spontaneous and seeded evidence stay separated

This is a hard requirement (R1, HEREDITY_REQUIREMENTS.md), not a
convention:

1. **Provenance tag is mandatory and physics-invisible.** Every run's
   provenance record (REQUIREMENTS.md) carries an `instrument_class`
   field: `SPONTANEOUS` or `SEEDED_CONTROL`, plus, for seeded runs, the
   exact byte pattern and placement used. This tag lives ONLY in
   run metadata (observatory/provenance layer) -- it is never encoded
   into the lattice bytes themselves and cannot be read by any site
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
   spontaneous-origin claim -- a DIAGNOSTIC trigger, never provenance
   truth.** Compute a structural fingerprint (e.g. a hash of the
   byte-pattern-relative-to-itself, translation/rotation-normalized) of
   the candidate spontaneous structure and compare it against the
   fingerprint library of ALL seeded patterns ever used (regimes 3-4 and
   any future ones). A match is a hard stop -- either a genuine
   reinvention worth extra scrutiny, or (far more likely at first) a
   campaign-script bug that leaked a seeded pattern into a nominally
   spontaneous run. **[REPAIRED per ASTRA_REVIEW_01.md S06]** A
   fingerprint match or non-match NEVER overrides the logged
   initialization recipe (item 5): the recipe log is the sole
   provenance truth; the fingerprint check is an investigation trigger
   that can raise a false alarm (a rare true reinvention) or miss a
   genuine leak (a perturbed copy evading an exact fingerprint) and must
   never be substituted for reading the actual logged recipe. This check
   runs automatically as part of any claim pipeline, not manually and
   not optionally.
5. **Campaign configs are versioned artifacts.** The exact byte pattern
   and RNG seed used to generate every regime-1/2/5/6/7 initial state
   is itself logged (not just "random soup, seed=X" in prose) so a
   contamination investigation can always reconstruct exactly what was
   run. This recipe log is authoritative for `instrument_class`; item 4's
   fingerprint check is secondary to it.

## What this file deliberately does not do

Does not specify detector thresholds, does not specify what counts as
"interesting" output, does not run anything. Regime parameters (soup
density, energy levels, replenishment rates) are swept by the
habitability campaign (HABITABILITY.md), not fixed here.
