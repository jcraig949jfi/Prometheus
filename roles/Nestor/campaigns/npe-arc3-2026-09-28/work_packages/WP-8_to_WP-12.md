# ARC3 work packages WP-8 .. WP-12

Common setup: see `../../npe-p2-endogenous-heredity-2026-09-27/work_packages/README.md`.
- The canonical M1 lease is `roles/Nestor/tools/nestor_lease.py` (host lease file + comms record).
- The register-reset world axis is `roles/Nestor/lib/reset_axis.py` (CARRIED is the default).

## WP-8 Descendant execution inheritance
Threads T-EST-5, T-DC-2, T-SCAF-4. Resource: LEASED-M1, ~2 h.

**Q.** In NPE a child is the overwritten organism: it keeps its slot, niche and, in the CARRIED world, the overwritten
organism's registers. Which of these a child "inherits" decides whether it can reproduce.

**Design.** A world axis for what a child's registers are at birth:
- (a) the slot's old registers (the default);
- (b) zeros;
- (c) the parent's post-run registers;
- (d) random.

The parent is unchanged in every arm. The X-A3-AUTOPSY instrument measures C4 (usable start) through C6 (child
copies).

**Also.** Search the autopsy records for parent-written prologues (T-SCAF-4).

## WP-9 Full neutral-baseline comparison (PORTABLE; can run off M1)
Thread T-BASE-1. Resource: ~9 CPU-h, 2 processes, any node with the repo.

**Q.** Does soup variation-selection reach fresh-start-competent copiers faster than a neutral mutation walk with
matched mutation opportunities, starting material and ruler screens?

**Design.** `../delegates/accessibility/BASELINE_DESIGN.md`. Preregister the thresholds proposed there BEFORE running,
as a CONFIRM-style frozen doc. The scripts are `neutral.py` and `compare.py`.

**Known asymmetry to state as part of the treatment.** Copy errors and overwrites exist only in the soup.

## WP-10 Candidate-transition assay (after the forensic delegate)
Thread T-END-1. Resource: LIGHT + LEASED-M1.

**Q.** Take the localized change from `../delegates/forensic_16000006/FORENSIC_16000006.md`:
- Does it recur independently in fresh evolutionary runs?
- Does it transfer to other genomes?

**Design.** Screen existing and new DENSE runs for the same motif or change class. If found in more than one lineage,
freeze a CONFIRM.

## WP-11 Reproductive architecture comparison
Threads T-LOC-2, T-STATE-1. Resource: LIGHT.

**Q.** The transplant classes are tape-anchored, state-anchored and true locator; state-free vs zero-start is a
separate axis. Do these differ in:
- accessibility (neutral-network size);
- robustness;
- evolvability (the fraction of 1-2 step mutants that are competent and differ in class)?

**Stop rule.** If class predicts nothing beyond state-freedom, stop.

## WP-12 External scaffolding synthesis (REPO; off M1)
Threads T-SCAF-1..5.

**Q.** Build the comparison table (systems x supplied functions: reset, placement, geometry, primitive, division,
allocation, partner) and classify each NPE function:
- ENVIRONMENTAL SUPPORT;
- SCAFFOLDING (internalizable);
- IRREDUCIBLE PHYSICS.

Include evidence where internalization occurred or failed (Tierra Baugh 2015; Stringmol Clark 2017; Bourrat 2022).
Starting point: `../delegates/external/EXTERNAL_SCAFFOLDING.md`.
