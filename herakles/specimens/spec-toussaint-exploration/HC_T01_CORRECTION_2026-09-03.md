# HC-T01 CORRECTION NOTICE

**Issued 2026-09-03, after the HC-R01 directive and after reading the Ergon lane's
Kouvaris forensics. Two corrections. Both are downgrades. Both are binding, and
they take precedence over the wording in `HC_T01_REVIEW_PACKET.txt` and
`HC_T01_EXECUTION_REVIEW_PACKET.txt`, which are left unedited as the record of
what the seat said at the time.**

---

## CORRECTION 1: the verdict is HC_T01_WEAK_SIGNAL_ONLY

`HC_T01_EXECUTION_REVIEW_PACKET.txt` section 18 returned
`HC_T01_PARTICLE_SURVIVES` and flagged a tension for the reviewer: kill
condition K7 had fired, and section 21 of the execution directive says HC-T01 is
scientifically negative if any kill condition holds.

**James adjudicated against the seat.** The correct verdict is
`HC_T01_WEAK_SIGNAL_ONLY`, on two grounds:

1. K7 fired. Current fitness predicts subsequent acquisition at least as well as
   every accessibility statistic measured.
2. The structural limitation the seat disclosed but then reasoned past: `beta = 0`
   populations cannot evolve the second-type operators available to `beta > 0`
   populations. So the experiment cannot separate

   > history reorganised comparable machinery into different future accessibility

   from the narrower

   > only one treatment was allowed to construct an additional class of
   > representational machinery.

The seat's own reviewer's-bottom-line question asked exactly this and the answer
is that the confound is not cleared. `CP-REPRESENTATION-REWRITE` is **retained**
as a serious candidate mechanism part. Both halves are binding: do not weaken
the caveat, do not discard the part.

**What still stands unchanged.** The reconstruction is valid. The same-probe
history effect is real and 24 to 108 times the estimator noise. The historical
detector worked. The contemporaneous mechanical effect of the operator is tiny
against the historical effect. At identical phenotype and identical fitness the
two arms have different one-step reachable distributions. None of that is
withdrawn. What is withdrawn is the claim that this is a clean demonstration of
the particle.

---

## CORRECTION 2: the wider-literature claim does not survive

`HC_T01_REVIEW_PACKET.txt` reported `MISSING_CELL_SUPPORTED` for the wider
literature, on 24 screened descendants with five documented access gaps.

**That claim is withdrawn.** The Ergon lane's forensics on Kouvaris 2017
(`ergon/kouvaris2017/`, deliverables A-P) identified three works this seat's
descendants search never saw:

- **Tiso 2024**, University of Groningen PhD thesis chapter 3, "The evolution of
  mutational transformers", defended 23 January 2024. Carries all four elements
  in qualified form: a local detector of 1000 mutations per locus from the
  current best individual, applied within-run at four time points, under a
  representational manipulation with environment and selection held fixed, with
  a descriptive within-run link to recovery speed. Its defects are that the
  detector is absent from the negative-control arm, the within-run link is
  `n = 1` and unquantified, and it was never published.
- **Petak et al. 2025**, PNAS, "The variability of evolvability". A local
  detector using the **same mutation operator used in the evolutionary runs**,
  longitudinal, 15 replicates with 95 percent confidence intervals, published.
  Selection-side intervention.
- **Kounios et al. 2016**, arXiv 1612.05955. A genuine representational on/off
  ablation, a one-to-one genotype-phenotype map against an evolving gene
  regulatory network, with the mutation operator identical in both arms, 30
  replicates, Mann-Whitney U. It **predates this specimen's directive by four
  months** and shares HC-T01's confound rather than curing it.

### Why this seat missed them, which is the transferable lesson

The descendants search was seeded on the **citation graph of Toussaint's own six
works**. Tiso, Petak and Kounios sit in the Watson and Kouvaris lineage and do
not cite Toussaint. A one-author citation graph cannot see a parallel lineage
that never cited that author.

The screening criterion was sound and was applied honestly to 24 works. The
**population** it was applied to was drawn too narrowly, and no amount of rigour
inside a mis-drawn population fixes that. This is the same defect class the
programme has recorded before under a different name: a scope claim is itself a
measurement, and it was not measured here.

### The corrected claim

`MISSING_CELL_CONFIRMED` about **Toussaint's own corpus** stands. It is
machine-checked by `derived/verify_t0_claims.py` and nothing in the Ergon lane
touches it.

The wider claim is replaced by a narrower and honest one:

> The surviving novelty of HC-T01 is a **RIGOUR CELL**, not a missing cell. The
> composition exists in the literature in qualified forms. What did not exist,
> and what HC-T01 supplies, is the composition run **quantified, in every arm
> including the control, with run-level uncertainty, under an operator on/off,
> against a preregistered mechanical-effect null**. Tiso 2024 fails the
> all-arms requirement, Petak 2025 has no operator-side intervention, and
> Kounios 2016 measures its accessibility quantity in a single unablated
> condition.

That is a smaller result and it must be sold as one.

---

## Consequences carried into HC-R01

1. Before any "nobody measured X" claim, the descendants population must be
   drawn from **more than one seed lineage**, and the seed choice must be
   justified in writing as part of the claim.
2. Author code repositories are searched before absence is asserted. Two for two
   in this programme, recovering author code found a working detector that
   appears in no publication.
3. Cheap-state baselines are mandatory from the start on every accessibility
   candidate, per HC-R01 section 10. K7 is promoted from a kill condition to a
   standing design rule.
4. Kounios 2016 is recorded in the recurrence registry as **sharing** HC-T01's
   machinery-presence confound, not curing it. It is not evidence for recurrence
   under stronger controls.
