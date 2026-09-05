# SFE Precursor-Phenomena Program -- Literature Audit

Harmonia C, 2026-09-05. Produced by the `deep-research` workflow (run
`wf_2ecd5962-bcb`: 5 search angles, 26 primary sources fetched, 126
claims extracted, 25 adversarially verified by 3-vote, 17 confirmed,
8 killed, 108 agent calls). Subject: the proposed 100-probe backlog +
Precursor Falsification Stack + "pressure atlas" framing.

Evidence tiers used below:

- **VERIFIED** -- survived 3-vote adversarial verification against the
  primary text (vote shown).
- **EXTRACTED / UNVERIFIED** -- pulled from a primary source by a fetch
  agent but never put through verification (budget exhausted). Treat as
  leads with a citation to check, not as findings.
- **REFUTED** -- a claim that was proposed during search and killed in
  verification. Listed so nobody re-imports it.

Coverage warning: every VERIFIED item is on Q1, Q2, Q9 (Cully only) or
the diversity-collapse strand of Q10. Q3-Q8 are UNVERIFIED-only. That is
a harness budget artifact, not evidence of absence.

---

## Q1. OEE metrics (MODES etc.)

**VERIFIED 3-0.** MODES (Dolson, Vostinar, Wiser, Ofria 2019) measures
four hallmarks -- change, novelty, complexity, ecology -- only on
components passing a lineage-persistence filter (counts at time A only
if descendants exist at A+t). Novelty = persistent components never
before in the persistent pool (equivalent to Bedau's A_new). Ecology =
Shannon entropy of persistent genotypes. Complexity = population MAX of
informative (knockout-sensitive) sites -- misses epistasis by the
authors' own caveat. It does NOT deliver a transition-in-individuality
metric; the 2024 follow-up (Bohm, Zhang, Dolson) still lists four.
Do not cite "the fifth metric, transition potential, has proven more
difficult" -- that sentence exists only in commented-out LaTeX source.

**VERIFIED 2-1 (medium).** No ALife system sustains novel adaptive
activity at biological degree. In MODES's own tests NK baseline
populations stopped producing meaningful novelty (all but one
replicate); high mutation rate keeps novelty going only via drift
preserving lineages past the filter window, and still declines. Avida
novelty declines gradually (declining supply of beneficial mutations).
The only system described as satisfying all hallmarks is the biological
LTEE. OEE-II editors (Packard, Bedau, Channon, Ikegami, Rasmussen,
Stanley, Taylor 2019): "the degree of open-endedness displayed by
biological evolution remains out of reach of today's ALife models, and
we don't understand the mechanisms behind OEE well enough to engineer
systems that display that degree"; reaffirmed in the 2024 editorial.

**VERIFIED 3-0.** Open-endedness is a variegated concept with no single
test. Hintze 2019's trivial system (100 organisms, L/R/F strings, 1%
indel/substitution, unbounded genome length) passes the Wiser-Ribeck-
Lenski hyperbolic-vs-power-law trajectory test for both zlib-complexity
and Levenshtein diversity, yet the editors judge its diversity "trivial
... neither geometric, nor dynamic, nor functional". Statistics "can be
gathered only for the kinds of entities that are specified in advance",
so prespecified spaces show open-ended dynamics "for a while, until the
limits of the space are exhausted". => novelty counts alone cannot
certify OEE; a single "central barrier" claim is contested by
construction. (Taylor 2020 rebuts Hintze's stronger conclusion.)

**VERIFIED 3-0 (medium -- full text unobtainable, 403).** MODES is not a
calibrated instrument: its creators (2024) say it "has only been applied
to a few systems so far, with limited opportunity for controlled
experiments or cross-system comparisons". The first controlled sweep
(Evo-Sandbox: fit-when-rare strength 0-16000 x parasite strength 0-10 x
filter depth 100-2500) found "the regions of parameter space in which
different hallmarks of open-endedness are maximized are non-intuitive"
-- the four hallmarks peak in different regions. Zero citations, no
replication. Direct counterexample to "one diversity knob (add
coevolution/parasites) monotonically raises open-endedness".

**EXTRACTED / UNVERIFIED.** Avida complexity is environment-dependent:
rises-then-plateaus in the empty environment, keeps rising in Logic-9;
authors state unbounded complexity growth requires the environment to
continually supply new information. Channon's Geb: max individual
complexity scales only logarithmically with world size.

---

## Q2. Quality-diversity and stepping stones

**VERIFIED 3-0.** Direct primary evidence that a MAP-Elites archive
improves DOWNSTREAM adaptability: Nordmoen, Veenstra, Ellefsen, Glette
2021 (Frontiers Robotics & AI). SOFO / MOFD / QDSA co-evolved modular
robots on flat terrain, then moved final populations to two harder
terrains and continued 50k evals x 30 reps: QDSA regained significantly
higher max fitness (Mann-Whitney U). Cross-seeding control: SOFO and
MOFD initialised FROM the QDSA archive -> "no significant differences",
isolating the transferred diverse population as the cause. Open
question: how much is head-start at eval 0 vs faster re-adaptation, and
does it hold with archive size matched to baseline population size.

**VERIFIED 3-0.** The most-cited "stepping stones" paper (Gaier,
Asteroth, Mouret GECCO'19, 2-page poster) only HYPOTHESISES the
mechanism; its sole result is final performance matching Picbreeder
targets. Do not cite it as downstream-adaptability evidence. Nadizar et
al. 2025 (EuroGP, search-trajectory networks) still treat the role of
stepping stones in MAP-Elites as an open gap.

**VERIFIED 3-0 (single run).** PINSKY (Dharna, Hoover, Togelius, Soros
2022, POET derivative on GVGAI dZelda): transfer is mostly
intra-species (66-83%). Removing the minimal criterion while keeping
reward alignment collapses level diversity into a "mega-species" (GAN
mode-collapse analogy) and returns solve rates to pre-alignment levels
(singleDoor 83-90% -> 61%; multiDoor 29% -> 10%). Closest published
diversity-collapse -> stepping-stone-loss -> reduced-progress pathway,
but ONE run per noMC condition and noMC denominators confounded by
possibly-unsolvable levels.

**REFUTED (do not reuse).** "QD archives preclude open-ended search by
construction" and "QD archives do not generalise to task variants" (both
from arXiv 2407.17515) -- killed 1-2 and 0-3. "Cully 2015 benchmarked
against policy-gradient/vanilla-BO as evidence of downstream
adaptability" -- killed 1-2.

---

## Q3. Baldwin effect sign-flip -- EXTRACTED / UNVERIFIED only

- Pre-2007 literature contained models for both acceleration and
  deceleration with no general prediction of which occurs when.
- Paenke/Sendhoff/Kawecki-style "fitness gain gradient": the sign under
  directional selection is set by the effect of marginal plasticity on
  the slope of genotypic trait vs log fitness; same sign as selection ->
  accelerates, opposite -> retards. Claims to reproduce Hinton-Nowlan
  acceleration and Ancel retardation as special cases. Scoped to
  directional selection on one quantitative trait; says nothing about
  stabilising selection, rugged landscapes, or explicit learning cost.
- The "Baldwin expediting effect" is demonstrated only under
  needle-in-a-haystack landscapes (Hinton-Nowlan style); under graded
  fitness functions sign and magnitude depend on function shape and
  starting conditions; faster approach is not necessarily higher
  fitness, so expediting alone cannot explain maintenance of plasticity.
  Must specify WHICH Baldwin variant (expediting vs assimilation /
  canalisation) a probe tests.
- Mayley 1996: assimilation needs high relative learning cost AND
  genotype-phenotype neighbourhood correlation. Rapid environmental
  change favours learning; stable favours assimilated traits.
- Individual-based sim (diploid, K=256, mu=5e-4, 10 plastic + 10
  non-plastic loci): non-costly plasticity ALWAYS increased rescue
  probability after a step change and reduced extinction under linear
  change; sign flipped only by explicit plasticity cost (or linkage to
  developmental noise). Costly plasticity hindered rescue specifically
  when the step was small and benefit weak. Waddington-style assimilation
  after a single shift takes hundreds of generations -- unlikely unless
  developmental noise >= 40% of phenotypic variance.

Implication for probes 11-20 and 53/54/60: the sign of the Baldwin
effect is a function of (landscape shape, learning cost, change rate,
starting conditions). The proposal's "empirical Baldwin laboratory"
framing is supported -- but any probe must pre-register which of those
four axes it varies, or its result is uninterpretable.

## Q4. Niche construction -- EXTRACTED / UNVERIFIED only

- Skeptic position (four of five co-authors of the debate paper): niche
  construction is a CAUSE of the four canonical processes, not a fifth
  process; NC phenomena were studied productively within standard
  theory before and independently of NCT. The lactose/dairying case is
  agreed by both sides to be NC-generated selection yet does not
  discriminate NCT from standard theory.
- NCT population-genetic models (Laland, Odling-Smee, Feldman) predict
  dynamics claimed distinct from conventional coevolution: time lags,
  momentum/inertia, and autocatalytic fixation of even selectively
  disadvantageous niche-constructing traits. These are concrete,
  operationalisable predictions for probes 41-50 -- and the
  "disadvantageous trait fixes via its own construction" prediction is
  the one that would discriminate NCT from reframed standard theory.
- No ALife demonstration of inherited-structure effects was reached
  before budget exhaustion. The proposal's "ALife experiments have
  already demonstrated strong effects" sentence currently has NO
  citation behind it in this audit.

## Q5. Evolutionary rescue -- EXTRACTED / UNVERIFIED only

- Bell 2017 (Annu. Rev.): rescue probability depends jointly on
  abundance, genetic variation, and rate/severity of deterioration;
  microbial experimental evolution has broadly supported the theory.
  Rescue = relative fitness (evolutionary) synthesised with absolute
  fitness (demographic): the U-shaped absolute-population trajectory is
  the observable. Any ALife rescue probe must track absolute population
  size, not relative rank.
- Bell's abstract does NOT list plasticity among the supported
  determinants. A reviewer can challenge "plasticity preserves lineages
  long enough for genetic adaptation" as resting on Chevin/Lande/Mace
  theory rather than the experimental rescue literature.
- Avida mass-extinction episodes: EQU evolved, lost during the
  low-resource episode, and in some cases re-evolved -- loss-and-
  reacquisition of a complex trait is reproducibly observable in a
  digital system (near-replica for probe 06).

## Q6. Major transitions -- EXTRACTED / UNVERIFIED only

- Avida clonal colonies (<=25 organisms, 400 colonies, 50 reps/
  treatment): raising an imposed task-switching cost (0/25/50 CPU
  cycles) monotonically increased evolved division of labour measured as
  mutual information between organism identity and task (0.400 ->
  0.813 -> 1.066). Near-replica for probes 73/78 with a ready-made
  metric. Nothing reached on communication emergence, conflict
  reduction, or interdependence ramps.

## Q7. Evolvability -- EXTRACTED / UNVERIFIED only

- Clune, Mouret, Lipson 2013: connection cost ALONE yields modularity
  comparable to Kashtan-Alon modularly-varying goals at MVG's strongest,
  exceeds MVG when change is too slow for MVG to work, and combining
  them raises modularity further (p = 3e-5). Directly undercuts any
  premise that alternating pressure is THE driver of modularity: a
  static cost pressure suffices. Probe 67 is a replication; probe 62/68
  should be run WITH and WITHOUT connection cost or they cannot
  attribute the effect.
- Nothing reached on mutation-rate evolution, survival-of-the-flattest,
  or developmental indirection.

## Q8. Measurement primitives -- EXTRACTED / UNVERIFIED only

(a) History-ablation / Markovian twin: NO published method was reached.
    This primitive currently has no literature anchor in the audit.
(b) Exaptation / task-distance operationalisation: nothing reached.
(c) Invasion analysis: adaptive-dynamics invasion fitness = geometric
    growth rate of a rare mutant in the resident background; extinction
    w.p. 1 iff rate <= 1. Valid ONLY under rare-mutation, timescale-
    separation, small-mutational-step assumptions; the standard review
    explicitly EXCLUDES changing/stochastic environments, oscillatory
    dynamics and finite populations -- exactly the program's regimes.
    Also single-frequency by definition: multi-frequency injection
    (the proposal's own primitive) is needed for positive frequency
    dependence / Allee bistability. So: the proposal's multi-frequency
    design is RIGHT, but it cannot cite adaptive dynamics as its
    theoretical basis in these regimes.
(d) Replay / lineage intervention:
    - Blount, Borland, Lenski 2008 (PNAS): a potentiating mutation by
      ~20,000 generations in Ara-3; replays from frozen ancestors show
      only clones sampled AFTER that point re-evolve Cit+. This is the
      direct published near-replica of "resurrect before/after event E,
      replay forward, does P(C) change". Cit+ appeared in 1/12
      populations after >30,000 generations; produced a stable Cit+/
      Cit- polymorphism, not a sweep (relevant to INVASION: innovation
      can create a niche and coexist).
    - Blount, Lenski, Losos 2018 (Science) review: three replay designs
      -- parallel replay, ANALYTIC replay (restart from archived time
      points to locate when the outcome probability shifted), and
      historical-difference. Analytic replay is the proposal's LINEAGE
      primitive, and it is "relatively new, few performed" (5 of 51
      studies). Overall verdict: repeatability is COMMON at the fitness
      level; divergence grows moving fitness -> phenotype -> genotype;
      contingency grows with the "footprint of history". Authors flag
      circularity: landscape structure is inferred from the same replay
      outcomes.
    - Lenski, Ofria, Pennock, Adami 2003 (Nature): EQU in Avida; first
      EQU genotypes were 1-2 mutations from parents but many from the
      ancestor, and earlier (sometimes deleterious) mutations were
      crucial -- historical contingency of innovation in a digital
      system with perfect history reconstruction.
    - Wiser, Ribeck, Lenski 2013: 50,000-generation mean fitness better
      fit by power law than hyperbola (no plateau).

## Q9. Published near-replicas of probes

**VERIFIED 3-0.** Cully, Clune, Tarapore, Mouret (Nature 2015) is a
near-replica of the damage-recovery PROBE, not of the rescue MECHANISM:
~13,000-gait MAP-Elites map built offline on the UNDAMAGED robot, then
map-based Bayesian optimisation lets a physical hexapod compensate for
leg damage in <2 min / <~10 trials across 5 hexapod and 14 arm damage
conditions. No population, heredity or post-damage selection. Because
damage was never seen during archive generation it is also an
archive-transfer result (Q2). Reusable negative-control facts:
performance measured by external motion capture (oracle); prior built
on the undamaged morphology only.

UNVERIFIED near-replicas surfaced: Avida extinction/EQU re-evolution
(probe 06); Avida task-switching-cost division of labour (73/78); Clune
connection cost (67); Blount analytic replay (LINEAGE primitive; probes
55/56/99); Nordmoen terrain transfer (25/30). Not reached: predator-prey
coevolution in Avida/Polyworld/Tierra, signalling emergence, sudden
actuator loss in evolved morphologies.

## Q10. Contested premises

| proposal premise | status | kill citation |
|---|---|---|
| "diversity collapse is the central barrier to OEE" | CONTESTED (verified) | Packard et al. 2019: no consensus on categories; Hintze 2019 shows trivial diversity passes trajectory tests; Bohm 2024 hallmarks do not co-maximise |
| "coevolution is an antidote to saturation" | CONTESTED (medium) | Bohm, Zhang, Dolson 2024: parasite strength x fit-when-rare effects are regime-specific, not uniform |
| "MAP-Elites/novelty preserve stepping stones that help later" | SUPPORTED narrowly (verified) | Nordmoen 2021 yes; Gaier 2019 does NOT show it; PINSKY single-run |
| "alternating pressure drives modularity" | UNDERCUT (unverified) | Clune 2013: connection cost alone suffices and beats MVG when change is slow |
| "plasticity preserves lineages long enough for genetic adaptation" | THEORY-ONLY (unverified) | Bell 2017 lists abundance/variation/dispersal, not plasticity |
| "Baldwin effect: learning accelerates or retards" | SUPPORTED as an open question (unverified) | gain-gradient rule + needle-vs-graded landscape results |
| "niche construction is a distinct inheritance channel" | CONTESTED (unverified) | four-of-five-author skeptic position; discriminating prediction = autocatalytic fixation of disadvantageous constructing traits |
| "invasion at multiple frequencies" | RIGHT design, WRONG citation base | adaptive dynamics excludes the program's regimes |
| "history-dependent reacquisition advantage is rare" | NOT TESTED | -- |
| "moderate intermittent pressure beats monotonic" | NOT TESTED | -- |

Strongest published counter-argument to the pressure-atlas framing
(from Packard et al. 2019, verified): statistics can only be gathered
for entity kinds specified in advance, so an atlas built over a
prespecified tag ontology (pressure x effect x timescale x ...) will
show structure "for a while, until the limits of the space are
exhausted". The atlas must include a mechanism for the ontology itself
to be revised by the data, or it measures its own priors.

---

## Refuted claims -- do not import

1. "Fitness sharing produced the only ecology signal at the cost of
   complexity in MODES" -- 0-3.
2. "Hintze's toy satisfies all 13 compiled OEE requirements" -- 1-2.
3. "MODES measures potentials (remaining space) rather than produced
   entities" -- 0-3.
4. "Inter-species transfer explains 39-75% of PINSKY solved levels" as a
   standalone claim -- 1-2 (number is real; framing failed).
5. "Cully 2015 benchmarked vs policy gradient / vanilla BO" -- 1-2.
6. "QD archives preclude open-ended search by construction" -- 1-2.
7. "QD archives do not generalise to task variants" -- 0-3.
8. "Replace 'is it open-ended' with 'does it answer a scientific
   question'" as Hintze's thesis -- 1-2.

## What a second pass should do

Resume the workflow with verification restricted to the UNVERIFIED
tier above (Q3-Q8, ~60 extracted claims), plus targeted searches for
the three anchors that came back empty: (i) any published history-
ablation / memory-ablation causal test in evolved or RL agents;
(ii) any operational exaptation metric; (iii) ALife inherited-structure
niche-construction demonstrations. Until then, sections Q3-Q8 of the
proposal are "not yet audited", not "supported".
