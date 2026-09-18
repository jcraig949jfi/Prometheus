+=====================================================================+
|  C4-08 -- CAN ROBUSTNESS BE CONSTRUCTED RATHER THAN GIVEN? READOUT   |
|  Archaeon[m2-49ee5a4d]   2026-09-18 08:45Z   attempt of record a01   |
|  Disposition: ROBUST_WITHOUT_MECHANISM (slot rule), with the length   |
|  confound flagged and the robustness identified as neutrality         |
+=====================================================================+

Ancestral = 188 depth-16 C4-05 walkers (digests 188/188). Ordinary =
the C4-06 mutation_only arm RERUN (6 seeds; traces equal C4-06's 6/6:
the negative control). Perturbed = the same runs with two frozen-weight
edits per birth (n_ops=2). Descendant sample: top-32 of each final
population (192 per regime). Fresh C4-01 assay on W2_K2: 12 operators x
4 draws per program (8,270 / 9,000 / 9,135 applied edits). 4 engine
records, 0 errors, 420 s. The "insulation removed" arm: REPRESENTATION_
BLOCKED (D4-007), recorded.

-----------------------------------------------------------------------
1. THE FRESH ASSAY, THREE POPULATIONS
-----------------------------------------------------------------------
  population   programs  loss (D2+D3)          neutral D5  coherent            D7  mean len  W2_K2 reward
  ancestral       188    .419 [.408, .429]        .538     .149 [.142, .157]   10    19.1       .410
  ordinary        192    .185 [.177, .193]        .789     .077 [.071, .082]    0    40.1       .583
  perturbed       192    .125 [.118, .132]        .863     .044 [.040, .048]    0    62.5       .609
  category shares: no category differs between perturbed and ancestral
  by >= .10 (largest: control +.010, opaque_io -.020).

-----------------------------------------------------------------------
2. PREDICTIONS
-----------------------------------------------------------------------
  P1  perturbed loss < ancestral by >= .10       HELD (.419 -> .125)
  P2  ordinary loss NOT < ancestral by >= .10    LOST (.419 -> .185)
  ablation                                       NOT_EXAMINED (no
                                                 suspected category)
  length confound (>= 25% longer)                YES: 19 -> 40 -> 62
                                                 instructions
  Harness label CAPABLE_NEGATIVE: an artefact of my declaration's sign
  (min_effect -0.10 was read as a floor on treatment - control; the
  measured -0.294 is the predicted direction). The slot's preregistered
  readings above are the record; the label is kept beside them.

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  Selection on W2_K2 for 100 generations makes programs whose single
    edits mostly do nothing: loss falls from .42 to .19 under ordinary
    load and to .13 under doubled load. The robustness is real and
    measurable with the same instrument that measured the ancestors.
R2  It is NOT mutation-load specific: P2 lost. Ordinary selection
    already halves the loss; doubling the load takes it further along
    the same line (and doubles the length again).
R3  What was built is neutrality, not preserved variation: the coherent
    share falls monotonically (.149 -> .077 -> .044) as the neutral
    share rises (.54 -> .79 -> .86), and D7 disappears (10 -> 0 -> 0).
    Descendants are harder to break and harder to change.
R4  The genomes tripled in length with no change in category composition:
    the directive's "mere duplication or larger genomes" caveat applies
    in full, and with no structural category to ablate, no intervention
    can attribute the robustness to a structure. ROBUST_WITHOUT_MECHANISM.
R5  For C4-10's rule (decrease loss AND increase non-trivial variation)
    this condition FAILS the second half by construction of what it
    built: it does not qualify. Read as measured, not as hoped.

-----------------------------------------------------------------------
4. CLAIM CEILING / FEEDS
-----------------------------------------------------------------------
One substrate, one challenge world, 6 seeds per regime; a population-
level fresh-assay comparison with a length confound. Feeds the damage
geometry map (the "selected descendants" rows) and C4-10's selection
(mutation_load: disqualified). Not a mechanism.
+=====================================================================+
