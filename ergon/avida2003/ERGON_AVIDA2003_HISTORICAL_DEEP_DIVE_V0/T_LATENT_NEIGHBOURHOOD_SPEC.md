# T - LATENT-NEIGHBOURHOOD MEASUREMENT SPECIFICATION

**FROZEN 2026-09-03, before any evaluator exists and before any neighbourhood
has been enumerated.** No metric in this document has been computed. The
evaluator required to compute them has not been recovered.

---

## 1. The question, restated after the V0.1 narrowing

V0.1 established that on the realized 112-genotype lineage the historical
scalar instrument was *sufficient*: 15 phenotypes, 15 merit levels, and all 14
phenotype-changing transitions merit-visible. A detector that only distinguishes
what the lineage visibly did adds nothing.

The surviving question is counterfactual and temporal:

> **Before a realized transition, does the local mutation cloud contain
> phenotype structure that the scalar channel cannot expose?**

## 2. The two channels, defined operationally

For a historical genotype `g` of length `L`:

    N1_sub(g)   every single point substitution: L * 25 genomes
    N1_ins(g)   every single insertion, reported SEPARATELY
    N1_del(g)   every single deletion, reported SEPARATELY

Substitution, insertion and deletion neighbourhoods are **never aggregated**.
The recovered `genesis` shows they arise from different operators at different
rates (copy error 0.0025/instruction; divide-insert 0.05; divide-delete 0.05),
so merging them would merge distinct physics.

For each viable neighbour `g'`:

    HISTORICAL CHANNEL   the scalar the 2003 instrument could report:
                         fitness, and its cLandscape-style class in
                         {DEAD, NEG, NEUT, POS} under the historical
                         neutrality band
    PHENOTYPE CHANNEL    the exact 9-bit task vector P(g'), and the
                         transition class SILENT / LOSS / GAIN / ALT
                         relative to P(g)

## 3. Primary quantity

    RESIDUAL(g) = H( P(g') | historical fitness class, g )

the phenotype entropy remaining after conditioning on everything the historical
channel reports. Enumeration over `N1_sub` is exhaustive (L*25 <= ~1525), so
this is computed by **exact counting, not estimated**. No information-theoretic
estimator, and therefore no estimator bias, enters the primary quantity.

`RESIDUAL(g) = 0` means the historical channel already determines the phenotype
composition of the neighbourhood, and the detector gap is falsified for that
genotype. That outcome is a success and is the single cheapest way to kill the
particle.

## 4. Secondary quantities -- harder to fool, reported always

Per genotype, per neighbourhood type:

  - number of distinct viable neighbour phenotypes
  - number of distinct fitness classes
  - number of phenotype transitions hidden **inside** each fitness bucket
    (this is the quantity that makes the gap concrete rather than abstract)
  - fraction of viable neighbours whose phenotype differs from `P(g)` but whose
    fitness class does not
  - probability mass of EQU-bearing neighbours
  - probability mass of neighbours introducing each of the nine tasks
    separately
  - effective number of neighbour phenotypes, `exp(H)`
  - substitution accessibility by genome position (which sites are live)
  - lethal fraction, per neighbourhood type

## 5. Denominator, frozen

**VIABLE neighbours**, as frozen in `I_RPD_SPEC.md`. All three denominators are
reported; only this one enters any comparison. Unchanged from V0 so the earlier
freeze still governs.

## 6. The temporal test (section 9 of the directive)

Computed over **every** phylogenetic depth where enumeration is feasible, not a
selected window. Depth is the axis, as frozen in `G_MATCHED_CHECKPOINT_DESIGN`.

Alignment: the 14 realized phenotype-changing transitions plus EQU at pd 111
are marked as events. The question is whether any neighbourhood measure moves
**before** an event while the realized organism is still phenotypically
unchanged and scalar-quiet.

**EQU IS NOT THE ONLY EVENT.** All 14 earlier acquisitions are internal
calibration events (directive section 11). A signal appearing only before EQU
is to be treated as suspicious and endpoint-specific, not as the strongest
case. A signal appearing before several independent acquisitions is what would
make the instrument credible.

## 7. Cheap baselines the detector MUST beat (directive section 10)

Frozen now so they cannot be chosen after seeing the result:

    b1  current task count
    b2  current merit
    b3  current fitness
    b4  genome length
    b5  distance in pd to the next realized phenotype change
    b6  historical cLandscape-style POS / NEUT / NEG / DEAD fractions
    b7  simple mutation viability (1 - lethal fraction)
    b8  distance in pd to EQU

**b5 and b8 are look-ahead baselines and cannot be used by a real detector.**
They are included deliberately as ceilings: if the phenotype channel does not
beat b5, it is not even competitive with knowing the answer, and any weaker
claim is moot. b1-b4, b6, b7 are the honest competitors.

Decision rule, frozen: if any of b1-b4, b6, b7 predicts the realized events as
well as the phenotype-partitioned measures, the purported signal is **killed**
(directive section 10, kill criterion K4).

## 8. What this specification forbids

- Aggregating substitution with indel neighbourhoods.
- Selecting a depth window after seeing where the signal is.
- Reporting the primary quantity without the cheap baselines beside it.
- Using the uniform-prior 47.1% figure as an empirical claim. It is retained
  ONLY as a combinatorial upper-space characterisation (directive section 7),
  and it is not a headline.
- Any causal or precursor language. At this phase the object is named
  `LATENT_NEIGHBOURHOOD_STRUCTURE` and nothing more.

## 9. What this can and cannot establish

It can **qualify an instrument** on one historical lineage.

It **cannot** establish that any pattern is unusual, because the lineage is a
survivor and there are no contemporaries. Survivorship (K6) remains active and
no population-level or precursor claim follows from this measurement, however
it comes out. That constraint is non-negotiable and is restated here so it
travels with the spec.

---

*Frozen by Ergon, 2026-09-03, before the evaluator existed.*
