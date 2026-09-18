+=====================================================================+
|  C4-04 -- ADDRESSING DAMAGE: READOUT                                  |
|  Archaeon[m2-49ee5a4d]   2026-09-18 07:05Z   attempt of record a01   |
|  Disposition: NEGATIVE on the pooled prediction (CAPABLE_NEGATIVE);   |
|  executed mode comparison REPRESENTATION_BLOCKED; structure inside    |
+=====================================================================+

Static analysis on the committed C4-01 children (4,866 regenerated,
4,866 digests equal to the committed ones); controls: constructed-jump
positive (break detected inside the span, intact outside), identity
negative 57/57, cheat ok. 40 of 57 parents carry at least one statically
reachable jump. 13 engine records, 0 errors, 1.3 s.

-----------------------------------------------------------------------
1. HOW OFTEN LENGTH-CHANGING EDITS BREAK A REFERENCE
-----------------------------------------------------------------------
  P(a reachable jump is broken or removed | the parent has one)
  deletion .525   splice .489   movement .428   region_swap .388
  insertion .315  duplication .302   |  randomization .122
  config .070  operand .062  reference_redirection .059  replacement .047
  pooled over the five length-changing operators: .423 [.397, .449]

-----------------------------------------------------------------------
2. LOSS (D2 or D3) GIVEN THE REFERENCE STATE
-----------------------------------------------------------------------
                       broken/removed     intact        no reachable jump
  pooled (five ops)    .640 (n 588)      .552 (n 802)   .745 (n 624)
  insertion            .712              .497           .779
  movement             .679              .486           .635
  duplication          .571              .549           .728
  splice               .686              .651           .765
  deletion             .566              .599           .792
  by stratum (five ops pooled):
  w0_solver            .648              .444           .563
  delay_general        .749              .624           .675
  shelf                .507              .412           .350
  gen0_random         1.000             1.000           .996
  coherent share (D3/D4/D6/D7 or D5 with displacement > 0) among broken:
  .172 pooled; delay .252, shelf .171, w0 .114, gen0 .000.

-----------------------------------------------------------------------
3. THE PREDICTIONS, AS WRITTEN
-----------------------------------------------------------------------
  P1  P(loss | broken) - P(loss | intact) >= 0.10, pooled:  .087  LOST
  P2  parents with no reachable jump lose LESS by >= 0.10:  they lose
      MORE (.745 vs .589)                                   LOST
  Harness: CAPABLE_NEGATIVE (effect .087 < .10).

-----------------------------------------------------------------------
4. READING (decompose, do not reject)
-----------------------------------------------------------------------
R1  The pooled negative is an interaction, not an absence. Where the
    edit SHIFTS content without removing it (insertion +.215, movement
    +.193) a broken reference raises loss by a fifth; where the edit
    REMOVES content (deletion -.033, splice +.035, duplication +.022)
    the reference state adds nothing, because the removal itself is the
    damage. Within every viable stratum the broken-minus-intact gap is
    positive (w0 +.204, delay +.125, shelf +.095); the pooled .087 is
    pulled down by gen0_random (loss 1.0 on both sides, inherited
    degeneracy) and by the shelf.
R2  P2 inverts because "no reachable jump" is mostly the gen0_random
    stratum (272 of 624 no-jump rows, loss .996) and short programs;
    within w0_solver the no-jump rows (.563) sit between the intact
    (.444) and broken (.648) rows, and within the shelf they are the
    least brittle (.350). Jump-free is not robust; it is short.
R3  Breaking a reference does not merely kill: the coherent share among
    broken-reference children (.172) is not below the population's
    (.109 in C4-01), and D5-with-displacement rows exist there. A
    re-targeted jump is a different program, sometimes a viable one.
R4  Position-sensitive addressing is the only addressing this ISA has
    (relative offsets, no fix-up). A relational or template mode cannot
    be expressed without a new primitive: REPRESENTATION_BLOCKED, and
    the size of the prize is now bounded from the data: at most the
    .19-.22 gap on insertion/movement, nothing on deletion/splice.

-----------------------------------------------------------------------
5. CLAIM CEILING / FEEDS
-----------------------------------------------------------------------
Static co-occurrence on one substrate at edit radius 1; not causal.
Feeds C4-05 (neutral walks should track whether a step broke a jump;
steps that do are twice as likely to leave the band under insertion
and movement) and the damage geometry map's "reference" column.
+=====================================================================+
