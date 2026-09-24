# LOCAL ENGINE AMENDMENT 15 -- **DRAFT, NOT FROZEN** -- G1 -> G2: DOES THE
# INHERITED ABSTRACTION HELP PRODUCE A NEW ONE?

Dated 2026-09-24. Drafted after the operator accepted S4
(ENDOGENOUS_ABSTRACTION = YES, ABSTRACTION_TRANSPLANT = YES,
BOUNDED_RSI = NOT YET ESTABLISHED). This file is a PROPOSAL. It becomes
binding only when the operator authorises execution and it is re-committed
as AMENDMENT_15_<date>.md with the open choices of s9 resolved. Campaign 1
remains FROZEN and UNRUN.

--------------------------------------------------------------------------
1. THE ONE QUESTION
--------------------------------------------------------------------------

Does the inherited G1 abstraction help produce a NEW, semantically distinct
abstraction that then improves a fresh G2 relative to G1?
BOUNDED_RSI = YES only if R1-R5 (s7) all hold.

--------------------------------------------------------------------------
2. OBJECTS
--------------------------------------------------------------------------

  L1        the frozen S3 selection (sha 4fed9489d956...): (acc + {H}) + PRISTINE.
  DONOR_G1  the S3 donor procedure (D1-D6 + certificates), inheriting L1: its
            observation search walks L1, and its member space is L1's own
            declared coverage (L1 instantiations x H1 x FINAL, plus M).
  DONOR_P   the same procedure from PRISTINE (control: no inheritance).
  Replicates: R_D = 8 independent observation seeds per donor, PAIRED (S2 keyed
            order; donor replicate r uses the same cells in both donors).
  L2        L1 + the schema DONOR_G1 selects (per replicate; the transfer test
            uses the replicate chosen by a frozen rule: the lowest replicate
            index that selected a distinct schema).

--------------------------------------------------------------------------
3. TREATMENT-BLIND CATALOG (Tier 3E) -- generated, not chosen
--------------------------------------------------------------------------

  Pool: every G4 program (init in H1, body in BODY_SPACE containing both acc
  and v, final in FINAL_SPACE) that passes MECHANICAL filters:
    - order invariance over the non-first elements (the metamorphic tribunal
      requires it), tested on 50 frozen valid inputs;
    - never FAILS on a frozen tribunal-shaped probe set (lengths up to 200),
      so golds are never "None";
    - output depends on the sequence (not constant over B1);
    - one family per certified behavior class.
  Stratified by the body's top-level operator (add, sub, mul, fdiv, mod, gcd,
  powr). K families drawn per stratum under seed "APHRODITE/T3E/CATALOG/v1",
  then assigned OBSERVE / VALIDATE / TRANSFER by seeded shuffle within the
  stratum. Additive bodies are therefore 1 stratum of 7. No family is named or
  chosen by the seat. G2 generator qualification applies unchanged.

--------------------------------------------------------------------------
4. TREATMENT-BLIND ADMISSION (replaces the positive-control S7 rule)
--------------------------------------------------------------------------

A transfer family is admitted iff (a) its witness lies in G4 (true by
construction), (b) its generator qualifies (G2), (c) its witness artifact
passes the tribunal, and (d) it has HEADROOM: PRISTINE qualifies in <= 8/16
pilot recipients. No library other than PRISTINE is consulted, and no
positive control exists in this campaign.

--------------------------------------------------------------------------
5. DISTINCTNESS
--------------------------------------------------------------------------

A schema S is DISTINCT from G1 iff the set of certified body behavior classes
of its in-space instantiations is NOT a subset of G1's. A specialisation of
(acc + {H}) -- e.g. (acc + (v % {H})) -- is therefore NOT distinct
(recommended; see s9-ii).

--------------------------------------------------------------------------
6. ARMS AT TRANSFER
--------------------------------------------------------------------------

  L2 (treatment) vs L1 (the G1 baseline -- the primary comparator) vs
  PRISTINE; L1 + SHAM_k (k = 0..7: a random DISTINCT one-hole schema, drawn
  treatment-blind from the G4 schema space and hashed before the donors run);
  and L1 + DONOR_P's schema, if DONOR_P produced one (sensitivity).
  N = 16; escrow 250,000; the hostile MetaTribunal; emitter v2; S2 pairing;
  class certificates C1-C4.

--------------------------------------------------------------------------
7. CRITERION (all five)
--------------------------------------------------------------------------

  R1 G1-DEPENDENCE. DONOR_G1 derives AND selects a distinct schema in more
     replicates than DONOR_P, paired over the 8 replicates (exact one-sided
     sign test, p < 0.05), OR both derive one but DONOR_P's paired meta-cost
     is higher with its one-sided 95% bound excluding 0.
  R2 G2 > G1. L2 beats L1 on admitted transfer families: pooled paired
     lower95 > 0 AND >= as many qualified recipients on every family.
  R3 ATTRIBUTION -- CONDITION 7 REWRITTEN (no grandfathering). At least TWO
     admitted families where (a) the qualifying solution was reached through
     the NEW schema's entry (coordinate attribution), AND (b) the witness
     BODY's certified class is absent from every body class the donor
     observed. Whole-program classes are no longer the test.
  R4 HOSTILE CONTROLS. L2 beats every L1 + SHAM_k on at least half the
     admitted families and the sham median wherever it claims an effect;
     false positives <= 25% of hits; equal expressivity; only
     tribunal-qualified solutions count.
  R5 no donor state or evaluator information crosses.

--------------------------------------------------------------------------
8. PREREGISTERED RISK (stated before anything runs)
--------------------------------------------------------------------------

In G4, G1's lever is to make additive-shaped bodies outside H2 cheap to
observe. LGG over such observations tends to re-derive (acc + {H}) or a
specialisation of it, which s5 does NOT count as distinct. The plausible
G1-dependent routes to a DISTINCT schema run through conjugation (S4 showed
the additive schema solving `acc - (v % last)` via `first - acc`), and they
depend on the member space (s9-i). R1 FAILING is a real possibility. It would
be reported as an informative negative: in this grammar an inherited
abstraction widens observation but does not seed a new abstraction.

--------------------------------------------------------------------------
9. OPEN CHOICES FOR THE OPERATOR
--------------------------------------------------------------------------

  (i)   MEMBER SPACE for DONOR_G1. Recommended: its own declared search
        coverage (L1 instantiations x H1 x FINAL, plus M). The alternative,
        the full G4 fold space (2.3e8 programs), is infeasible without the
        accelerator.
  (ii)  Whether a SPECIALISATION of G1 counts as distinct. Recommended: NO.
  (iii) The GRAMMAR. Stay in G4, which is the honest test of this engine and
        has the s8 risk; or extend ALL arms equally to depth-3 bodies (G5),
        where G1 can act as a macro and hierarchical abstraction becomes
        expressible. G5 is a new substrate and needs its own conformance and
        qualification pass. Recommended: G4 first.
  (iv)  COMPUTE. 16 donor runs plus an S4-sized transfer: about 3-5 h on M4
        with 7 workers, or much less on the accelerator after its cloud canary.
