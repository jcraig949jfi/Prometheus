# V. EVCA HCA-1 / HCA-2 DESIGN NOTE

**Required by HC-R01 directive section 21, sha256
`6c21f6cd85c197a1d0963bf54ea7f887fca1ed9d07ba4613cb5edc1b76820d60`.
EvCA remains FROZEN. This note does not authorise a run. Do not run EvCA until
this note is reviewed.**

---

## 1. Why the EvCA question has to change

The old EvCA question was: *does failure or accessibility geometry differ between
lineages that did and did not pass through a structural transition?*

HC-T01 shows that question is now too weak in two specific ways.

**K7.** In HC-T01 the cheapest conventional state variable, current best
fitness, predicted subsequent acquisition at least as well as every accessibility
statistic. An EvCA run that only establishes "geometry differs" would land in
exactly the same place: a large, robust, well-resolved difference with no
demonstrated value over a free measurement.

**The machinery-presence confound.** In HC-T01 the two arms differed in whether a
class of representational machinery could exist at all. Any EvCA design must not
repeat that, and the good news is that EvCA structurally cannot.

So the primary EvCA question becomes, verbatim from the directive:

> Does a same-state / same-probe future-accessibility signal predict later
> transition probability beyond current classification performance and cheap
> rule-state metrics?

That is HCA-2, not HCA-1. HCA-1 is the entry ticket, not the result.

---

## 2. Why EvCA is a better substrate than Toussaint for this question

Four structural advantages, and they are the reason to keep EvCA next in the
queue rather than reaching for a fresh specimen.

**A. The machinery class is identical by construction.** Every rule in the
family is a 128-entry binary lookup table over radius-3 neighbourhoods. There is
no operator that one arm can build and another cannot. The confound that
downgraded HC-T01 to `WEAK_SIGNAL_ONLY` cannot arise. This is the single most
important property.

**B. The one-step neighbourhood is finite and exactly enumerable.** A 128-bit
rule table has exactly **128** one-bit-flip neighbours. The accessibility
detector needs no Monte Carlo estimate of *which* variants exist; it enumerates
them. Compare HC-T01, where the detector cost 2000 times the evolution it
observed and the whole estimator-noise protocol existed to handle sampling error
in the mutation step. Here that source of error is **zero**.

The remaining cost is evaluating each neighbour's behaviour, which needs many
random initial conditions. At 10,000 initial conditions per rule that is
1.28 million lattice simulations per detector reading, which is large but exact
in the dimension that mattered before.

**C. Present state is matchable on a published, verified scale.** The recovered
specimen holds six genomes with performance verified by execution against print:

    rule         published   measured
    ---------    ---------   --------
    maj              0.000      0.000
    exp              0.652      0.664
    particle1        0.742      0.733
    particle2        0.755      0.742
    par              0.769      0.765
    GKL              0.816      0.820

`particle1` and `particle2` came from **different genetic-algorithm runs** and
sit 0.009 to 0.013 apart in measured performance. They are a naturally occurring
matched-performance pair with different evolutionary histories, in the same
representation, under the same mutation operator. That is the HC-T01 comparison
without HC-T01's excuse.

**D. Acquisition is a discrete, countable event.** In the density-classification
family the interesting acquisitions are structural transitions in the
computational strategy: the appearance of a new particle type, or of a new
domain boundary interaction. Those are recognisable events, not a continuous
fitness climb. That matters because HC-T01's T2 precedence test was abandoned
precisely for lack of a plateau in a continuously climbing outcome. A discrete
transition gives a genuine before-and-after.

---

## 3. What EvCA can and cannot discriminate

**HCA-1, accessibility difference at matched state: EvCA can establish this
cleanly, and more cleanly than any specimen we hold.** Matched performance,
identical machinery, exact enumeration of the one-step neighbourhood.

**HCA-2, accessibility carrying information beyond current-state variables: EvCA
can attempt this, and the attempt is the point.** The design below is built
around the conditional test, not around the difference.

**What EvCA cannot cleanly discriminate: history from location.** Directive
section 8 is the binding constraint here. Two rules that differ in performance
history also differ in current rule-table content, and rule-table content is
part of the present state. So EvCA on the six recovered genomes can support
STATE-LOCATION ACCESSIBILITY, and it can support HISTORY-CONDITIONED
ACCESSIBILITY only if the histories are generated under control. That forces the
design in section 5.

---

## 4. The cheap-state baseline, fixed before any run

Per directive section 10 this is mandatory and it is specified first, not last.
Every accessibility claim is tested **after conditioning on all of these**, each
of which costs far less than the detector:

    current classification performance      the free variable that beat us before
    Langton lambda                          fraction of 1s in the rule table
    rule-table Hamming weight               same, unnormalised
    symmetry residual                       distance to the nearest
                                            density-symmetric rule
    black/white exchange residual           distance to nearest exchange-symmetric
    performance at a second lattice size    cheap generalisation proxy
    number of particle types                if extractable cheaply
    number of domains                       if extractable cheaply
    one-bit robustness                      mean performance over the 128
                                            neighbours; note this IS a
                                            neighbourhood statistic but it is a
                                            SCALAR and it is cheap, so it counts
                                            as a baseline, not as the detector

That last row is deliberate and it is the hardest baseline to beat. HC-T01's
`avgfit`, the mean fitness of sampled offspring, matched or beat the structured
accessibility statistics. The EvCA equivalent is mean neighbour performance, and
the detector must beat it or the result is another K7.

**The detector only counts if it adds information over this whole set.**

---

## 5. Design, in the order it must run

### Stage 0, archaeology only, no new compute beyond the detector

Enumerate the 128 one-bit neighbours of each of the six recovered genomes.
Measure, for each neighbour, performance at the historical lattice size and at
one other. Report per genome:

- the full 128-point performance distribution, not a summary;
- the count of neighbours that are viable, near-neutral, and improved;
- the strategy-level descriptor distribution, see section 6.

This is a **complete** accessibility reading, not an estimate, on six recovered
1993-1995 artifacts. It is cheap, it is publishable-internally on its own, and it
establishes whether HCA-1 holds at matched performance for the
`particle1`/`particle2` pair.

**This stage alone answers HC-R01 question 1 for a second substrate.** It cannot
answer HCA-2, because six genomes with coarse provenance give no acquisition
outcome.

### Stage 1, generate the histories under control

The recovered genomes cannot separate history from location. So run the
historical genetic algorithm under two or more conditions that are **matched in
machinery and in mutation operator** and differ only in history. Candidate
history axes, in preference order:

1. **Lattice-size schedule.** Evolve at one lattice size versus a varying
   schedule. Both arms are 128-bit tables with the same bit-flip operator. This
   is the closest EvCA analogue of modularly varying goals and it introduces no
   machinery asymmetry.
2. **Initial-density distribution schedule.** Evolve against initial conditions
   drawn uniformly in density versus drawn near 0.5, then probe both against a
   common distribution.
3. **Population size or selection pressure.** Weaker, because it changes the
   sampling of history rather than its content.

Then **harvest matched pairs**: pairs of rules, one from each arm, whose
performance on a common held-out evaluation agrees within a preregistered
tolerance, and whose cheap-state vector from section 4 is also matched as closely
as the harvest allows. Report how many candidate pairs the harvest produced and
how many survived matching, because that ratio is itself the answer to HC-R01
question 3, whether matched-state accessibility difference is common or rare.

### Stage 2, the frozen-population cross-operator probe

Carried over unchanged from HC-T01, where it was the part of the design that
actually worked. Freeze the rule, apply the identical mutation operator,
enumerate all 128 neighbours, feed nothing back. Non-interference is trivially
guaranteed here because enumeration is deterministic and read-only.

The HC-T01 difference-in-differences generalises: for each history arm measure
the neighbourhood under the shared probe, and difference the arms. Because the
operator is identical in both arms by construction there is no mechanical
component to subtract, which is a simplification, and it also means the
generation-zero mechanical null is not merely vacuous as in HC-T01 but genuinely
unnecessary. Say that plainly rather than performing a ritual null.

### Stage 3, the acquisition fork, which is the actual test

For each matched pair, fork **many** independent continuations under identical
conditions, and record for each fork whether and when a preregistered structural
transition occurs.

    unit of analysis          the fork, nested in the matched pair
    outcome                   time to the next structural transition,
                              right-censored at the horizon
    primary test              does the Stage-2 accessibility statistic predict
                              the outcome AFTER conditioning on the full
                              section-4 cheap-state vector
    method                    Cox proportional hazards or a censored regression
                              with the pair as a random effect; the accessibility
                              term is entered LAST and the question is the
                              partial contribution
    preregistered failure     the accessibility term adds nothing once the cheap
                              vector is in the model. That is K7 firing again,
                              and it is reported as the result, not as a setback.

Right-censoring is required, not optional. HC-T01's acquisition analysis was
distorted by a ceiling: once most runs reached the optimum, gain became an
arithmetic function of current fitness, and that is what produced the degenerate
Spearman correlation of exactly -1.000. A censored time-to-event outcome does not
have that pathology.

---

## 6. The detector, and the thing we do not yet have

HC-T01's primary statistic, the modular degree, was hand-tailored to a period-5
target and does not transfer. EvCA needs its own, and there are three candidates
of increasing ambition:

1. **Performance distribution over the 128 neighbours.** Cheap, exact,
   substrate-general. Its scalar summaries are cheap-state baselines, so the
   detector must be the *shape*: the full distribution, its multimodality, the
   size of the near-neutral plateau, and the count of neighbours reaching a
   distinct performance mode.
2. **Strategy-descriptor distribution.** The count and type of particles and
   domain boundaries reachable in one flip, using the computational-mechanics
   filtering that the historical EvCA programme itself built. This is the honest
   analogue of "distribution over reachable strategies" and it is the one that
   would make EvCA a genuinely independent substrate rather than a second
   performance measurement.
3. **Behavioural-distance cloud.** Pairwise distance between the space-time
   behaviour of the parent and each of the 128 neighbours on a common set of
   initial conditions, with no reference to performance at all. This is the only
   candidate that is fully decoupled from the outcome variable, which matters
   because HC-T01's TRAP 2 coupling concern was real and, per the Ergon lane, is
   a property of this whole experimental family rather than a Toussaint defect.

**Recommendation: candidate 3 as primary, candidate 2 as the interpretable
secondary, candidate 1 as the cheap-state baseline it really is.** Choosing a
performance-based detector and then testing it against a performance baseline is
how K7 fires.

Candidate 2 requires recovering the historical particle-filtering method as a
detector part. That work is not done and it is the main prerequisite this note
identifies.

---

## 7. What EvCA would establish, and what it would not

If Stage 0 shows a matched-performance accessibility difference, EvCA delivers
**HCA-1 in a second substrate with no machinery asymmetry**, which is exactly
what HC-T01 could not. That is worth having on its own and it is cheap.

If Stage 3's accessibility term survives conditioning on the cheap vector, EvCA
delivers **the first HCA-2 evidence in the programme**, and only then does
`CP-REPRESENTATION-REWRITE` have a second substrate behind it.

If Stage 3's accessibility term does not survive, the programme has two
independent substrates in which accessibility differs at matched state and does
not predict acquisition beyond free measurements. That is stop condition S2, and
it would say something real and negative: that present behaviour underdetermines
future accessibility, but the underdetermination does not carry usable
information. Which would make the accessibility programme a description of hidden
state rather than a component of compounding capability.

Neither outcome should be preferred, and the design must be frozen before either
is visible.

---

## 8. Prerequisites before EvCA can run

1. Recover the historical particle/domain filtering method as a detector part,
   with a specification precise enough to implement. Without it the strategy
   descriptor is not available and the detector collapses to a performance
   measurement.
2. Freeze the matched-pair tolerance and the structural-transition definition in
   writing, before Stage 1 harvest.
3. Freeze the cheap-state vector of section 4 and the conditional test of
   Stage 3, before any accessibility number is looked at.
4. Compute budget: measure it, do not estimate it. HC-T01's estimate was wrong by
   a factor of three in our favour and the ratio prediction was the only part
   that held.
5. Resolve whether Stage 1 is authorised at all, since it generates new
   evolutionary histories rather than reconstructing a historical experiment,
   and is therefore a different kind of object from HC-T01.

**Point 5 is a question for James, not a decision for the seat.** Stage 0 is
pure archaeology on recovered artifacts and consumes nothing. Stage 1 onward is a
new experiment wearing EvCA's clothes.
