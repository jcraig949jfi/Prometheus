# LOCAL ENGINE AMENDMENT 18 (DRAFT) -- ABSTRACTION COMPOUNDING ASSAY C1
# "Does an inherited abstraction become a stepping stone once composition is
#  accessible?"  DRAFT -- NOT FROZEN. The frozen text will be
#  AMENDMENT_18_2026-09-2x.md, committed before any C1 code runs.

Program: ABSTRACTION COMPOUNDING (operator, 2026-09-27). This amendment never writes a
BOUNDED_RSI label, and historical labels are unchanged. Improvement of the improver is
out of scope (P2, science/compounding/rb6/).

0. INSTRUMENTS (new identities; the old ones stay the instruments of record for <= A17)
  WORLD W5         instantiation space and search fallback = G5 "g5-depth3-v1"
                   (465,954 bodies) for EVERY arm. The inits, finals and escrow
                   (250,000) are unchanged.
  TRIBUNAL T4      engine/tribunal_t4.py <frozen sha>, parameters as frozen there (RB-2).
  RULER v2         science/compounding/rb1/ruler_v2.py <frozen sha> (NEW_FINAL,
                   COMPOSES, REFINES).
  COMPOSITION MOVE engine/a18.py compositions(S). For every schema S in the donor's
                   START library: wrap(S, op, atom), for every primitive op, atom in
                   BODY_ATOMS and both argument orders, kept iff >= 2 in-space
                   instantiations. These are candidates in the UNCHANGED paired selection
                   (a17.select), next to the LGG-derived candidates. It is
                   treatment-blind: the same rule applies to every arm.
  Gates: G1 conformance (standard + whole-program on W5 programs) GREEN; fasteval
  equivalence on W5 bodies (>= 200k pairs, 0 mismatches) or the reference evaluator.

1. PANEL (built by a18.build_panel, seed "APHRODITE/A18/PANEL/v1", hashed at freeze)
  G1 = (acc + {H}); SHAM_0..3 = ON-path matched abstractions (NEW_FINAL vs G1,
  >= 20 accumulating W5 instances, >= 20 compositions); OFF_0 = an OFF-path inherited
  schema whose compositions are never supplied. Pilot values: pow(v,{H}), (v % {H}),
  gcd({H}, v), gcd((last // {H}), v); OFF (v - {H}).

2. SUPPLIES (both frozen and hashed before any donor runs)
  S-CON  CONSTRUCTED: families whose witness body is an accumulating in-space
         instantiation of a composition of an ON-path panel schema, with equal share per
         schema; init in H1, final uniform among finals mentioning acc. Qualified by
         Q2 + T4 + the successor window (RB-2).
  S-NAT  NATURAL: uniform W5 families (no construction), with the same qualification.
  Roles per replicate (seeded; identical for all donors): OBSERVE 4, VALIDATE 5 (S-CON:
  one per ON-path panel schema + 1 background), TRANSFER 10 (S-CON: two per ON-path
  schema, disjoint from validation, + 2 background).

3. ARMS (donors; each runs every replicate on the identical supply and cells)
  D_G1        inherits G1, composition ON
  D_G1_NC     inherits G1, composition OFF (ablates the move)
  D_SHAMk     inherits SHAM_k, composition ON (k = 0..3; generic stepping-stone test)
  D_OFF       inherits OFF_0, composition ON (off-path control)
  D_P         PRISTINE, composition ON (a no-op: nothing to compose)
  n = 8 replicates per arm per supply.

4. THE LADDER (each stage reported separately, per arm; never one success label)
  REPRESENTABLE  (analytic) composed schemas of the inherited abstraction have >= 10
                 accumulating W5 instances.
  REACHABLE      the donor's candidate set contains a schema that COMPOSES the inherited
                 abstraction.
  SOLVED         at least one VALIDATE cell of that schema's panel group is solved by the
                 composed candidate library within escrow, where the donor's START library
                 fails within escrow.
  SELECTED       the donor selects a candidate that COMPOSES its inherited abstraction
                 (paired selection, lower95 > 0).
  REUSABLE       the selected library solves (T4-qualified) >= 2 DISTINCT TRANSFER
                 families through the composed coordinate.
  CAPABILITY-EXPANDING  on >= 2 TRANSFER families: the selected library qualifies at
                 escrow 250k where BOTH the donor's start library and PRISTINE fail at
                 40 x escrow (10M). The ratio is reported; in a finite grammar capability
                 is always budget-relative.
  NOVELTY        the selected schema is NEW_FINAL vs G1 (and vs the inherited schema).
  COMPOUNDING    the selected schema COMPOSES or REFINES the inherited schema.

5. HYPOTHESES AND VERDICT RULES (S-CON primary; S-NAT reported beside it, never pooled)
  H1 (G1 stepping stone): D_G1 SELECTED-composing in > D_G1_NC and > D_P and > D_OFF
     replicates (one-sided sign tests vs each, p < 0.05), AND D_G1 REUSABLE and
     CAPABILITY-EXPANDING in >= 5/8 replicates.
     => G1_STEPPING_STONE = YES / NO / UNTESTABLE (supply or gate failure).
  H2 (generic): the same rule applied to each D_SHAMk on its own panel group.
     => GENERIC_STEPPING_STONE = count of SHAMs passing (0-4). A G1-only YES with 0/4
     generic is reported as G1-specific.
  H3 (natural availability): the S-NAT ladder counts for D_G1 vs D_P. Descriptive only.
     A YES on S-CON with nothing on S-NAT is reported as
     "stepping stone exists; the natural world rarely presents it".
  Smuggling disclosure: S-CON is built from compositions of the panel schemas. The
  scientific content is (a) that the FIXED selector picks and pays for the right
  composition, (b) transfer and capability, (c) symmetry across SHAMs, and (d) the D_OFF
  and D_G1_NC nulls. It is NOT the mere existence of such tasks.

6. BUDGET
  Pilot timing (forensic): <fill from rb4/PILOT_C1.json>. Arms x replicates x supplies =
  8 x 8 x 2 = 128 donor runs, plus transfer rows. If the conservative ETA exceeds 6 h,
  S-NAT drops to 4 replicates, declared before running.
