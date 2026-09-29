# Block B -- are B1, B6 and a candidate B8 one problem? (Archaeon, 2026-09-27)

## Claim
Every documented attribution error in the Prometheus Z80/PTE record can be placed on THREE axes. Each error is a conflation within one
axis, or a missing entry on one axis:

| axis | the question it answers | its values (each maps differently per substrate) |
|---|---|---|
| **CARRIER** (what the claim is about) | whose / which thing is being credited | executing body/context (WHO), code location (WHERE), material identity (WHAT) |
| **RELATION** (what kind of causal link) | how the credited thing relates to the outcome | PRODUCTION / FLOW: the actual copy path (identity by descent); RESEMBLANCE: state match, in full or only at informative units (the latter is E-002's DIFFERENCE); DEPENDENCE: counterfactual necessity or sufficiency under a NAMED intervention |
| **CONTRAST** (relative to what) | the baseline a difference or dependence claim is measured against | the alternative parent; the operator's null; a randomized victim; a sham host; the ceiling of a behavioural ruler |

A fourth thing is not an axis but an OPERATION: **aggregation**. Organism-level "lineage", "authorship" and "establishment" are
aggregates of per-unit facts. B1 is the discovery that the aggregate needs a declared referent and convention.

## Documented cases where conflation changed a conclusion

| case | engine | conflation | axis | consequence |
|---|---|---|---|---|
| FF-1 parent chain | Archaeon ENVGATE | executor identity (WHO) read as material lineage (WHAT) | CARRIER | establishment counts 8-42x inflated; ENVGATE-01 C4 downgraded |
| AN1 "decoupling" / D2 | BEE | code location (WHERE) read as code material (WHAT) | CARRIER | 27,083/28,163 location-foreign births in r038751 were own-material governed |
| FF-31 / D3 | NPE | executing context (WHO) read as governing code (WHAT) and as material share | CARRIER + RELATION | v0.1 "20/34 donor continuity" fell to 9/34; 26.4% of directed writes had WHO != WHAT |
| FF-27 material = target | BEE | positional RESEMBLANCE read as FLOW | RELATION | 847,000 births misattributed by resemblance |
| v0.1 AN3 (C4 used for rebuild) | NPE | one DEPENDENCE test (authorship under intervention) read as another (rebuild) | RELATION + CONTRAST (which intervention) | host-conditioned count 8 -> 16 |
| AN6 11/16 vs 1/16 | PTE | v0.1 counted DIFFERENCE (resemblance at informative units); v0.2 counted FLOW | RELATION | a "correction" (FF-33) that was really a switch of referent |
| 1/16 "tie" | PTE | a self-cross aggregated as two parents | CONTRAST (alternative parent = same parent) | a spurious ILL_POSED |
| 3/48 behaviour | PTE | a saturated behavioural contrast (ceiling) read as identity evidence | CONTRAST | "not supported" should be "untestable" |
| C-OP' clause (b) | PTE / E-002 | a per-child FLOW-share compared with a population-level operator null | CONTRAST + aggregation | a child byte-identical to a parent called ILL_POSED (E1b, E4) |
| ENVGATE-02 window rescue | Archaeon | none: DEPENDENCE claims carried named interventions and shams | -- | the clean case: a negative that stuck |

## Is B8 (FLOW vs DIFFERENCE) new?
**No as a distinction; yes as a lesson.**
- DIFFERENCE is RESEMBLANCE restricted to informative units (identity-by-state where the parents differ).
- FLOW is identity-by-descent (production).
- The distinction is the RELATION axis that FF-4/FF-27 already exposed in BEE. E-002 found it again in PTE, where FLOW is actually
  logged (the mask), so the two can be compared exactly.
- The new part is where each belongs: continuity/identity questions about CONTENT use DIFFERENCE; genealogy questions use FLOW.
  E-002's M1 test presupposes the content reading.
- Recommendation: do not open "B8" as a new break. Record it as the RELATION axis, with FF-4, FF-27 and FF-33 as its instances.

## Is B6 a special case?
- B6 (WHO / WHERE / WHAT) is the CARRIER axis applied to the GOVERNING CODE.
- B4 (whose vs where) is the same axis applied to MATERIAL ORIGIN.
- B2 (body vs identity) is the same axis applied to the ENTITY.
- Three breaks, one axis.

## Is B5 a special case?
Yes. B5 (factual contribution vs counterfactual sufficiency) is RELATION (production vs dependence) with a CONTRAST that must be named
(J11 already enforces it).

## Reduction
The seven named breaks B1-B7 plus the candidate B8 reduce to three axes (CARRIER, RELATION, CONTRAST) plus aggregation:

| break | reduces to |
|---|---|
| B1 | aggregation |
| B2, B4, B6 | CARRIER |
| B5, B8 | RELATION |
| B7 | CONTRAST |
| B3 | CARRIER (location vs material of executed code) |

The substrates differ in WHICH values of each axis they record natively:
- Archaeon: WHAT via taint, FLOW via copy labels.
- BEE: WHERE, resemblance.
- NPE: WHO, value-DIFFERENCE, DEPENDENCE via P-11.
- PTE: FLOW via the mask, only in replay.
Nothing forces them into identical mechanics. Each native field just needs a coordinate on these axes before it is combined with
another engine's field.

## What this does NOT establish
- That three axes suffice for new substrates. Every axis here was found by an engine, so the next engine may add one.
- The reduction is a classification of observed errors. It is not tested predictively.
- Predictive test (cheapest): take a native field from an engine not yet examined (e.g. Aether or Ensorain). Assign its coordinates
  BEFORE use, and see whether the misreadings it would cause are predicted.
