+=====================================================================+
|  C4-02 -- MUTATION-RADIUS RESPONSE CURVE: READOUT                     |
|  Archaeon[m2-49ee5a4d]   2026-09-18 06:20Z   attempt of record a01   |
|  Disposition: SUPPORTED (slot rule), THIN: one traversable cell       |
+=====================================================================+

Numbers from attempts/a01/CURVES.json. Same 57 parents, environments and
CRN episodes as C4-01; children = delta successive frozen-weight edits.
342 engine records on one world; 31 s.

-----------------------------------------------------------------------
0. CONTROLS
-----------------------------------------------------------------------
  radius 0 (identity)     57/57 displacement 0, parent's rewards (label
                          D5 45, D2 12 = the 12 degenerate parents)
  consistency             TVD(radius-1 D-distribution, C4-01 frozen-weight
                          mixture) = 0.029  (bound 0.10)  PASS
                          r1: D2 .425 D3 .097 D5 .467 | mixture: .447 .088 .449

-----------------------------------------------------------------------
1. THE CURVE (pooled, applied 456 per radius; D0 = 0, D1 eligible 0)
-----------------------------------------------------------------------
  radius   D2     D3     D4     D5     D6     D7   loss(D2+D3)  disp  var
  r1      .425   .097   .002   .467   .009    0      .522      .319  .211
  r2      .546   .118   .018   .305   .013    0      .664      .499  .238
  r4      .713   .121   .015   .147   .004    0      .834      .663  .210
  r8      .809   .121   .018   .046   .007    0      .930      .769  .165
  r16     .903   .086   .000   .004   .007    0      .989      .831  .130
  displacement histogram (0 | (0,.25] | (.25,.5] | (.5,.75] | (.75,1]):
  r1  306 | 1 | 1 | 0 | 148      r8   99 | 0 | 1 | 0 | 356
  r2  221 | 0 | 6 | 1 | 228      r16  71 | 1 | 0 | 0 | 384
  r4  146 | 0 | 4 | 0 | 306

  by stratum (loss / neutral / displacement):
                   r1            r2            r4            r8            r16
  w0_solver     .42/.58/.40   .64/.34/.63   .82/.18/.78   .95/.04/.92   .99/.00/.96
  shelf         .29/.68/.30   .45/.47/.51   .71/.24/.75   .85/.09/.89   .98/.01/.98
  delay_general .55/.45/.54   .69/.31/.69   .90/.10/.89   .98/.02/.97  1.00/.00/.99
  gen0_random  1.00/.00/.04  1.00/.00/.15   .99/.01/.17   .99/.01/.20   .99/.01/.27
  (gen0_random parents are degenerate themselves; their D2 is inherited.)

-----------------------------------------------------------------------
2. THE SHAPES (preregistered predicates, as measured)
-----------------------------------------------------------------------
  flat-neutral            NO   (P(D5) .467 at r1, .004 at r16)
  cliff                   NO   (largest adjacent loss step .170, r1->r2)
  exploding variance      NO   (displacement variance FALLS with radius)
  complete catastrophe    NO   (loss .522 at r1)
  parent-specific islands YES  (gen0_random: TVD vs pooled .79/.57/.45 at
                                r0/r1/r2 -- the inherited-degenerate stratum;
                                every viable stratum sits within .3 of pooled)
  operator-specific       YES  (at r1 by first operator: unreachable_removal
  islands                       TVD .456 vs pooled r1 -- it mostly cannot
                                apply and is neutral when it does; all other
                                operators within .24)
  traversable region      shelf ONLY, at r2 ONLY: P(D5) .467, loss .454,
  (P(D5) <= .5 AND           displacement .506. No other (stratum, radius)
   loss <= .5 AND             cell satisfies all three; w0_solver at r2 is
   0 < disp < 1)              loss .64, delay_general at r1 is loss .55.

-----------------------------------------------------------------------
3. READING (no more than the table says)
-----------------------------------------------------------------------
R1  Genotypic distance predicts the PROBABILITY of destruction, not the
    DEGREE of behavioural change. Loss rises smoothly and monotonically
    with radius (.52 -> .99); but displacement, conditional on any change
    at all, is > .75 at every radius. There is no radius at which edits
    produce moderate, graded behavioural difference. The C4-01 cliff is
    not a radius-1 artefact: it is the substrate's response at every
    scale tried.

R2  The "region between nothing changes and everything dies" is one
    narrow cell (shelf parents, two edits), and it is narrow because the
    two halves it lies between are themselves bimodal: half the edits are
    silent, half are destructive, and the cell is where those halves
    happen to balance, not where graded change appears.

R3  D7 = 0 at every radius (2,280 children): multi-step random edits find
    no improvement from any of these 57 starting points. D6 (exaptive)
    is present at every radius (.4-1.3%), almost entirely shelf parents.

R4  The falsifying outcome (flat-neutral or complete catastrophe in every
    stratum) is NOT met; the slot rule (a traversable region in >= 1
    stratum) IS met, by one cell. SUPPORTED, and thin: the honest
    summary is R1, not the cell.

-----------------------------------------------------------------------
4. WHAT IT FEEDS / DOES NOT ESTABLISH
-----------------------------------------------------------------------
Feeds C4-05 (neutral walks: the D5 mass at r1 is .47 and decays fast;
walks must step one edit at a time and test the band at each step) and
C4-06 (recombination between independently drifted lineages must be
compared against this monotone loss curve). Does not establish any
mechanism, anything about selection, or the fate of the D5 mass under
a walk (C4-05). Harness contrast label: WEAK_POSITIVE (r8 loss .930 vs
r1 .522, effect .41, no battery declared), recorded beside the slot rule.
+=====================================================================+
