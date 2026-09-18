+=====================================================================+
|  C4-08 -- CAN ROBUSTNESS BE CONSTRUCTED RATHER THAN GIVEN?           |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  When free semantic insulation is removed, can selection assemble
  structures that move their own effective damage boundary?

RE-PREMISE (D4-007)
  "Free semantic insulation" cannot be removed on this substrate (C4-03):
  the removal arm does not exist. The remainder of the directive's method
  is runnable as written: expose lineages to repeated ordinary pressure
  PLUS a preregistered perturbation regime; identify repeated structural
  changes with Proteus's descriptors AFTER behaviour is measured; compare
  the ancestral population and the descendants under the SAME fresh
  mutation assay (C4-01's); ablate suspected structures prospectively.
  The question becomes: under selection with elevated perturbation, do
  descendants change their own D-transition probabilities, and is an
  evolved structural difference responsible?

LINEAGES
  Ancestral: the depth-16 C4-05 walkers of the non-degenerate parents
  (the C4-06 starting population; digest-verified).
  Descendants: the final populations of evolutionary runs on W2_K2
  (E=16, N=200, G=100, 6 seeds), two regimes:
    ordinary     the C4-06 mutation_only arm's final populations, reused
                 (no new compute; same lineages, same budget)
    perturbed    descend applies TWO frozen-weight edits per birth
                 (radius 2, C4-02's r2: loss .66 vs .52 at r1) -- a
                 mutation-load regime, no reward term names anything
  Elites and the top-32 of each final population are the descendant
  sample (6 seeds x 32 = 192 per regime).

THE FRESH ASSAY (C4-01, unchanged)
  Every sampled program (ancestral 188; ordinary 192; perturbed 192) x
  the 12 grammar operators x 4 draws, classified by D4-003 on W2_K2 (the
  environment they were selected in; the ancestral walkers scored on it
  too). Measured per population: P(D2 or D3 | operator) pooled, P(D5),
  displacement histogram, coherent share; Wilson bands.

PREDICTIONS (written to be lost)
  P1  the perturbed descendants' single-edit loss is LOWER than the
      ancestral walkers' by >= 0.10 (selection under mutation load
      assembles robustness)
  P2  the ordinary descendants' loss is NOT lower than the ancestral by
      >= 0.10 (robustness needs the load, not just selection)
  A held P1 with a held P2 is the directive's "strong evidence" first
  half; the second half needs the ablation.

STRUCTURE AND ABLATION (only after the assay is measured)
  Proteus's structural descriptor (opcode category counts, length,
  manifest limits) on every sampled program; the categories whose share
  differs between perturbed descendants and ancestors by >= 0.10 are
  the "suspected structures". Ablation: for the perturbed elites, knock
  out (replace with NOP) every instruction of the suspected category and
  re-run the fresh assay on the ablated program; the structure
  contributes iff the ablated program's loss rises by >= 0.10 toward the
  ancestral value while its own W2_K2 reward stays >= floor. If no
  category differs by >= 0.10, the ablation arm is NOT_EXAMINED and
  recorded so. "Mere duplication or larger genomes" is checked first:
  if the descendants' mean length exceeds the ancestors' by >= 25% the
  length confound is reported beside every rate.

CONTROLS
  positive   the ancestral sample's loss under the fresh assay equals
             C4-01's shelf/w0 rates within 0.10 (the assay is the same
             instrument)
  negative   the ordinary arm's descendants are the C4-06 mutation_only
             final populations byte-for-byte (digests)
  cheat      a hand-set descendant row with loss 0 reads as "robust"
  determinism  one perturbed seed reproduces its trace

DISPOSITIONS
  SUPPORTED if P1 holds AND an ablation shows a contributing structure;
  ROBUST_WITHOUT_MECHANISM if P1 holds and no ablation isolates it;
  NEGATIVE if P1 is lost; INSTRUMENT_INVALID on a control failure;
  the "insulation removed" arm: REPRESENTATION_BLOCKED, recorded.

BUDGET
  6 perturbed runs (G=100, N=200); fresh assay 572 programs x 48 edits
  = 27,456 evaluations on W2_K2 plus ablations; minutes.
