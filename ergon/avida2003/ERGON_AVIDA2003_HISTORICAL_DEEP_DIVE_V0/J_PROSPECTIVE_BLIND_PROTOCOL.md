# J - PROSPECTIVE BLIND PROTOCOL

The history already happened, so the analysis cannot be prospective. The
DETECTOR can still be tested against hidden outcomes, and that is the point:
otherwise we tune a microscope to a particle whose coordinates we already know.

## Procedure

1. **Assemble.** Build the genotype pool: focal `g_succ` at the three frozen
   checkpoints plus all matched controls. Assign each an opaque identifier
   (`GT-0001` ...) from a keyed shuffle. Write the identifier-to-label map to a
   sealed file that the analysis stage does not read.
2. **Freeze the metric code.** P-MED, R1, H1, R2*, H2* implementations hashed
   and committed before any historical genome is classified. Property tests over
   the full 512 x 512 mask space green.
3. **Compute.** Produce the metric table keyed only by opaque identifier.
   Commit it.
4. **Convergence check** on N2 against opaque identifiers only.
5. **Unseal.** Join labels. Compute the frozen `delta_X(t)` contrasts.
6. **Report** the metric table and the contrast table as separate artifacts, in
   that order, with the commit of step 3 preceding the commit of step 5 in the
   git history. The ordering is the evidence that step 3 was not tuned.

## Honest limits of this blinding

- The analyst knows the *design*: that some genotypes are precursors and some
  are not, and roughly how many of each. Only the assignment is hidden.
- The genomes themselves carry information. A sufficiently determined analyst
  could recognise the ancestor by inspection, and pd-111 sits one step from EQU.
  Blinding raises the cost of unconscious tuning; it does not make it impossible.
- With one historical population the blind is small: three focal genotypes.
  This is a **CASE STUDY**, and section 14 of the directive requires that label
  unless multiple independent runs are recovered.

Stating these limits is not a formality. A blind protocol described without its
failure modes is theatre.
