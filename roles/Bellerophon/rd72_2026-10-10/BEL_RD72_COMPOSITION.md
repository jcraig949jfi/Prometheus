# BEL-RD-72 COMPOSITION (Workstream B: composition ladder, triviality attack, transplantation)

Question (operator review): can independently useful mechanisms combine without destroying one another?
Everything below is from frozen analyses unless marked; receipts in receipts/.

## 1. The ladder and its triviality floor (B1 / B2; TRIVIALITY_AUDIT s1-s2)
CONST -> ECHO -> INC -> COND_ONE -> COND_MULTI (and SUM2).
- Random competence: ECHO 1 in ~230 uniform tapes; INC 4 / 20,000; composites 0 / 300,000.
- One-step routes: dense DOWN the ladder (composite -> half: hundreds) and 0 UP into any composite, from every rung and
  from the copier.
- Ruler on evolved material (RU-E1b): every evolved "half-composite" solver is a whole ECHO or INC machine with 1-7
  critical bytes. The ladder's lower rungs are cheap, independent programs, not partial composites.

## 2. Composition of two engineered half-blocks across a verified desert (K2; prereg s3 / 3-A1)
X (copier + transform) and Y (copier + branch) are each a working replicator and each correct on one half. The composite
is >= 4 / >= 5 substitutions away, with one two-source prefix-transfer route.
- Result: 0 competent replicators in 1,320 worlds (three copy operators, paid / random reward / unpaid, 60 seeds per
  cell). One non-heritable competent product (PARTIAL_BYTE).
- Frozen: K-P2 and K-P4 FAIL; K-P1 and K-P3 NOT_TESTABLE (K-P1 for extinction, K-P3 for no event).
- Strict two-source attribution (the reviewer's fix for the tag leak) was never exercised: there was no composite to
  attribute.

## 3. Composition of evolved half-solvers (E1b + DP)
- ECHO and INC replicators COEXISTED in 13 paid COND_ONE worlds for up to 2,800 ticks; a composite never formed (0/150).
- Geometry: 0 one-step routes (~3.9M neighbours, including donor splices from the partner) and 0/52,000 three-step
  paths, from either partner.

## 4. Maintenance -- the planted composite (F1) and its cause (F2)
- F1: a planted composite (copier + COND_ONE witness, 32 copies) is NOT maintained.
  - Paid: kept to tick 2,000 in 1 of 14 surviving worlds; it decays into the ECHO / INC solvers of section 3.
  - Unpaid: gone by tick 100.
  - 0 crossings from founders 1, 2 or 4 knockouts away. 1-knockout founders have 1-103 SUB routes each.
  - Frozen rule: the composition null is DESTRUCTIVE SELECTION / INSTABILITY, not inaccessibility.
- F2: paired-halves payment (half-solvers earn nothing) does NOT rescue maintenance (2/20 vs 1/20; F2-P0 fails). The
  decay does not need paid half-solvers: it is variation, not selection for halves.
- F3: mutation rate controls maintenance, with a monotone dose-response. Kept to tick 2,000 in 1/20 worlds at MED
  (0.008), 13/20 at LOW (0.002) and 17/20 at VLOW (0.0005); p 2.0e-7. CAUSALLY_CONFIRMED: an error threshold.
  At VLOW, payment still matters (17/20 vs 8/20 unpaid).

## 5. Transplantation
- C3F (descriptive): a foreign ECHO solver implanted into ECHO-free worlds -> ECHO present at the end 6/10 vs 4/10 for
  the sham.
- F1 is itself a transplant of the composite witness into a fresh evolving population: it does NOT survive
  transplantation into this setting.
- BEL-48H's complementation mechanism survived transplantation to new operands and world models; nothing composite
  here did.

## 6. The one crossing (F2 world f2_00022; RESULTS_LOG XR)
- A KO1 founder (compare operand knocked out, INC-like) regained the composite by a single point change at a birth at
  tick 652. The deterministic replay is valid at all 11 censuses.
- 7 of the 8 critical bytes are founder material; 47 carriers were alive at tick 2,000.
- This is the geometrically predicted distance-1 repair, not an innovation; it occurred in 1 of 40 KO1 worlds.
- F4: at LOW mutation, where maintenance works and replicated on fresh seeds (12/20 vs 1/20), one-step precursors
  crossed in 1/20 worlds (vs 0/20 at MED). Most KO1 worlds lost their replicators. Across 60 KO1 worlds: 2 crossings,
  both kept; 0 from the ECHO-like and 2-knockout founders.

## 7. Disposition
- No composite computational mechanism was BUILT by evolution in this campaign (K2: 0/1,320; E1b: 0/150; F1: 0 from any
  distance).
- The obstacle is not only distance. At the mutation rate at which evolution finds minimal capabilities (MED), a
  10-critical-byte composite is above the error threshold. It is not MAINTAINED even when planted, and it decays to
  cheap 2-6-byte half-solvers. The cause is the mutation rate (F3), not payment structure (F2).
- "Independently useful mechanisms combine without destroying one another": NOT observed. In F1 the composite was
  destroyed into its independently useful parts.
