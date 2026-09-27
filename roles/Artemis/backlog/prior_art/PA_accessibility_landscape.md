# PA_accessibility_landscape -- prior art for the construction-landscape cluster

Seat: Artemis (charter Block D, prior-art research). Date: 2026-09-27.
Worktree read: /home/jcraig/Prometheus-worktrees/artemis-base-role (read-only; this file is the only write).
Web: every URL below was returned by a web search or fetch in this pass. Items that could not be
checked against a primary source are marked UNVERIFIED.

---

## 1. The internal question

Cluster question: does the CONSTRUCTION LANDSCAPE (assembly geometry, basin width, foothold
density, flat valleys, neutral networks, task supply), rather than the PAYOFF of a finished
mechanism, decide whether evolution or search discovers it? Five engines report compatible but
differently framed findings (H-D3-64). Crius (H-D3-60, H-D3-61, H-D3-62, H-D3-63, H-D1-45, H-D1-46):
a 47-edit procedural-reuse mechanism worth +16 tasks was never assembled in 36 runs, because the
parts were worth nothing alone (flat valley, one ledge, then a cliff), and selection settled into
"invocation without content". Ares (H-D3-56, H-D3-57): evolution took recurrence, with a wide
viable parameter region, over the designated keep carrier, whose viable region is a 4% sliver.
Aether D-15 (H-D3-12): a conditional form behind a zero-evaluation valley was committed as a
transplant study and never built. Ananke (H-D3-44): XOR/FLIP gave 0 signal in 165 cells; two-stage
compositions were never assembled. Aphrodite (H-D3-50, H-D3-51): the G1->G2 recursion test was
blocked by a task supply in which only additive families qualify. Older lines: H-D1-23 asks
gradient-free vs rare-but-climbable; H-D5-22 finds reuse is threshold-then-plateau, so the first
reuse is where selection acts; H-D5-40 says selection cannot value constructive steps that pay
later. Internal holdings already on disk: the Crius essay (docs/essays/2026-09-24-accessibility-frontier.md)
cites 17 sources, including Lenski 2003, Weinreich 2006, Poelwijk 2007/2011, Franke 2011,
Covert 2013, Kauffman-Levin 1987, Gavrilets 1997, Schuster 1994, Wagner 2008, Greenbury 2022,
Gould-Vrba, Gerhart-Kirschner, Goldberg, Lehman-Stanley 2011, Minsky and Sutton. Also on disk:
ergon/kouvaris2017 (Kouvaris vs Toussaint), elenchus/kashtan-alon-mvg, and a large Herakles
history-conditioned-accessibility (HCA) pass (herakles/HERAKLES_HISTORICAL_COLLIDER_V0/, including
HCL01_NEUTRAL_NETWORK_LITERATURE_PASS_2026-09-03.md and ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl).
This note adds what those do NOT already hold, and connects the older holdings to this cluster.
No thread currently links them.

---

## 2. Terminology map (Prometheus term -> literature term(s))

    accessibility frontier            -> evolutionary accessibility (Franke et al. 2011); "arrival problem" /
                                         arrival of the fittest (Wagner 2014; de Vries 1904 phrase)
    construction landscape            -> genotype-phenotype (GP) map structure + fitness landscape of
                                         intermediates; "phenotype bias" / "developmental bias" /
                                         "mutational bias" (Uller et al. 2018; Greenbury, Louis, Ahnert)
    basin width / wide flat region    -> neutral set size / phenotype frequency ("arrival of the frequent",
    (Ares)                               Schaper & Louis 2014; "ascent of the abundant", Cowperthwaite 2008);
                                         mutational robustness / "survival of the flattest" (Wilke 2001);
                                         in ML: basin volume V_B(f), parameter-function map bias,
                                         flat minima (Valle-Perez 2019; Mingard 2021)
    flat valley / zero-credit links   -> fitness plateau; neutral or deleterious intermediates; reciprocal sign
                                         epistasis (Poelwijk 2011); "needle in a haystack" (Hinton & Nowlan 1987);
                                         stochastic tunnelling / plateau crossing (Weissman et al. 2009)
    foothold density                  -> no standard name. Nearest: distribution of fitness effects of
                                         partial constructs; "evolvability-enhancing mutations" (Wagner 2023,
                                         held in Herakles HCL01); fraction of accessible paths (Franke 2011)
    assembly geometry / two-stage     -> building-block interdependency (Watson, Hornby, Pollack 1998: HIFF);
    composition (Ananke XOR)             deception (Goldberg 1987); epistasis; compositional evolution (Watson 2006)
    rho accessibility ratio           -> no standard form; theory of valley-crossing times (Weissman 2009) gives
                                         the "c" term in closed form for asexual populations
    invocation without content        -> introns / bloat / "neutral code is protective" in GP (Nordin, Francone,
    (fossil)                             Banzhaf 1996); constructive neutral evolution (Stoltzfus 1999;
                                         Gray et al. 2010); non-adaptive complexity (Lynch 2007)
    representation objection (H-D3-61)-> neutral networks (Schuster 1994; Wagner 2008); redundancy and
                                         locality of representations (Rothlauf 2006; Knowles & Watson 2002);
                                         direct vs indirect encoding (Clune et al. 2011)
    task supply (Aphrodite)           -> curriculum; modularly varying goals (Kashtan & Alon 2005); facilitated
                                         variation by environmental regularity (Parter et al. 2008); open-ended
                                         environment generation (POET, Wang et al. 2019); library learning
                                         dependence on task corpus (DreamCoder, Ellis et al. 2021)
    dials A-G of the controlled pair  -> A exaptation; B niches / quality-diversity (MAP-Elites); C linkage
                                         learning / symbiotic encapsulation (Watson 2006); D staged goals /
                                         curriculum; E credit assignment / Baldwin effect (Hinton & Nowlan);
                                         F facilitated variation (Gerhart & Kirschner); G substrate transplant
                                         (no standard name)
    hidden axis (useful gradient      -> evolvability (Wagner 2005; Kirschner & Gerhart 1998); "evolution of
    toward incomplete machinery)         evolvability"; evolution-as-learning (Watson & Szathmary 2016)

---

## 3. Key works

Only works not already in the Crius essay's source list lead this section. Held works appear
where this cluster needs a new reading of them.

1. Schaper S., Louis A.A. (2014). The arrival of the frequent: how bias in genotype-phenotype maps
   can steer populations to local optima. PLoS ONE 9(2): e86635. doi:10.1371/journal.pone.0086635.
   URL: https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0086635
   Relevance: This is the literature name for the Ares result and for H-D3-64's claim. Frequent
   phenotypes (large neutral sets) fix even when much fitter phenotypes are accessible, because
   the fittest never "arrive" in time. The paper decouples frequency from fitness, which is what
   the controlled pair wants.
   Verdict: SUPPORTS (strongly). It also REFRAMES Ares: "basin width beats peak" is a known effect
   with a known mechanism, arrival rate. The claim needs no new principle.

2. Cowperthwaite M.C., Economo E.P., Harcombe W.R., Miller E.L., Meyers L.A. (2008). The ascent of
   the abundant: how mutational networks constrain evolution. PLoS Comput Biol 4(7): e1000110.
   URL: https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000110
   Relevance: Exhaustive RNA landscapes at 12-18 nt show that abundant structures are reached first.
   Herakles already holds this paper. Its internal row says the effect is PRESENT for the
   destination but ABSENT for the starting position: where you start matters less than how big
   the target's network is.
   Verdict: SUPPORTS the destination-side reading (basin of the target). It CONTRADICTS any
   reading that starting-position accessibility predicts outcome.

3. Wilke C.O., Wang J.L., Ofria C., Lenski R.E., Adami C. (2001). Evolution of digital organisms at
   high mutation rates leads to survival of the flattest. Nature 412: 331-333. doi:10.1038/35085569.
   URL: https://www.nature.com/articles/35085569
   Relevance: In Avida, slower but mutationally robust genotypes displace faster ones, but only at
   high mutation rate. The flatness advantage is conditional on mutation load.
   Verdict: REFRAMES Ares. "Wide basin" can win by two different mechanisms. Arrival (item 1)
   works even at low mutation rate. Flatness (this item) needs high mutation rate. Ares has not
   separated them. Varying mutation rate would.

4. Mingard C., Valle-Perez G., Skalse J., Louis A.A. (2021). Is SGD a Bayesian sampler? Well, almost.
   JMLR 22(79). arXiv:2006.15191. URL: https://arxiv.org/abs/2006.15191
   With: Valle-Perez G., Camargo C.Q., Louis A.A. (2019). Deep learning generalizes because the
   parameter-function map is biased towards simple functions. ICLR 2019 (venue UNVERIFIED in this
   pass; the title was confirmed in search results).
   Relevance: In ML, the optimizer lands on functions roughly in proportion to their prior basin
   volume V_B(f), estimated by random parameter sampling, not by their loss value. This is the
   same claim as H-D3-57, made in another field, with a cheap estimator.
   Verdict: SUPPORTS H-D3-57. It supplies a METHOD: estimate P(mechanism) by sampling random
   genomes and compare it with the frequency at which evolution selects the mechanism.

5. Dingle K., Camargo C.Q., Louis A.A. (2018). Input-output maps are strongly biased towards simple
   outputs. Nat Commun 9: 761. doi:10.1038/s41467-018-03101-6.
   URL: https://www.nature.com/articles/s41467-018-03101-6
   With: Johnston I.G., Dingle K., Greenbury S.F., Camargo C.Q., Doye J.P.K., Ahnert S.E., Louis A.A.
   (2022). Symmetry and simplicity spontaneously emerge from the algorithmic nature of evolution.
   PNAS 119(11): e2113883119. URL: https://www.pnas.org/doi/10.1073/pnas.2113883119
   Relevance: "Simplicity bias": P(output) decays exponentially with the output's approximate
   Kolmogorov complexity. This gives an a priori predictor of which mechanisms have big basins,
   without running evolution.
   Verdict: REFRAMES. Crius's reuse, Ananke's XOR and Aphrodite's mul/mod/powr may simply be
   high-complexity outputs of their substrates' maps. If so, the frontier is predictable from a
   complexity estimate, and "assembly geometry" collapses partly into "descriptional complexity
   under this substrate's encoding".

6. Weissman D.B., Desai M.M., Fisher D.S., Feldman M.W. (2009). The rate at which asexual
   populations cross fitness valleys. Theor Popul Biol 75: 286-300.
   URL: https://www.sciencedirect.com/science/article/abs/pii/S0040580909000264
   Relevance: A full theory of crossing valleys and plateaus (neutral or deleterious
   intermediates), covering sequential fixation vs stochastic tunnelling as a function of N, mu
   and the intermediate's cost. This is a theoretical constraint the essay's rho ignores: the
   "c" term (cost of crossing a flat link by drift) has a closed form in these regimes.
   Verdict: REFRAMES. It turns rho from a guess into a derivable quantity, and it warns that
   crossing time scales steeply with plateau length for small N. Crius used an elite of 8.

7. Hinton G.E., Nowlan S.J. (1987). How learning can guide evolution. Complex Systems 1: 495-502.
   URL: https://www.cs.toronto.edu/~hinton/absps/evolution.htm
   Relevance: This is the canonical needle-in-a-haystack: all partial genotypes are worth zero.
   Lifetime learning turns the needle into a basin (the Baldwin effect). Crius organisms DO learn
   within a lifetime, and Ares has a plasticity carrier.
   Verdict: REFRAMES. It is a missing dial for the controlled pair. Plasticity or learning
   smooths the construction landscape without changing the payoff. The essay's dial E (local
   credit) is close to it but not the same. Caveat: the model has been criticised as misleading
   in its specifics (https://egtheory.wordpress.com/2014/02/07/learning-guide-evolution/; this
   critique was not read in full).

8. Lenski R.E., Ofria C., Pennock R.T., Adami C. (2003). The evolutionary origin of complex features.
   Nature 423: 139-144. doi:10.1038/nature01568. URL: https://www.nature.com/articles/nature01568
   (HELD in the essay; re-read for this cluster.)
   Relevance: EQU evolved in 23/50 populations only when simpler functions were rewarded. But the
   paper also finds that "no particular intermediate stage was essential" and that some
   deleterious mutations were stepping stones.
   Verdict: SUPPORTS the path claim, with an important REFRAME. Lenski's lever was the PAYOFF of
   intermediates. The literature therefore does not treat "construction landscape" and "payoff"
   as separable: intermediate payoff IS the landscape. Prometheus must define "payoff" as
   endpoint payoff only, or H-D3-64's question is ill-posed.

9. Knowles J.D., Watson R.A. (2002). On the utility of redundant encodings in mutation-based
   evolutionary search. PPSN VII, LNCS 2439: 88-98. URL: https://link.springer.com/chapter/10.1007/3-540-45712-7_9
   With: Rothlauf F. (2006). Representations for Genetic and Evolutionary Algorithms, 2nd ed.,
   Springer (locality and redundancy).
   URL: https://www.researchgate.net/publication/235709973_Representations_for_Genetic_and_Evolutionary_Algorithms
   Relevance: Adding random redundancy or neutrality does not help optimisation in general. It
   helps only when the redundancy is biased toward good phenotypes (Rothlauf: synonymous
   redundancy, high locality).
   Verdict: CONTRADICTS the naive fix proposed in H-D3-61 ("add percolating neutral networks and
   the mechanism becomes reachable"). Neutrality is not free accessibility. Its bias is what
   matters.

10. Stanley K.O., Miikkulainen R. (2002). Evolving neural networks through augmenting topologies.
    Evolutionary Computation 10(2): 99-127. URL: https://dl.acm.org/doi/10.1162/106365602320169811
    Relevance: NEAT routinely evolves XOR, which needs a hidden node. Two things make this work:
    complexification from minimal structure, and speciation, which protects new structure while it
    is still worth nothing.
    Verdict: CONTRADICTS any universal reading of Ananke H-D3-44 ("XOR is inaccessible").
    Two-stage composition is reachable when (a) the substrate does not sum inputs before the
    nonlinearity and (b) search protects young innovations. Ananke's failure looks substrate
    specific: "superposition sums packets". It SUPPORTS the construction-landscape thesis only in
    that form.

11. Watson R.A. (2006). Compositional Evolution: The Impact of Sex, Symbiosis, and Modularity on the
    Gradualist Framework of Evolution. MIT Press. URL: https://mitpress.mit.edu/9780262538091/compositional-evolution/
    With: Watson R.A., Hornby G.S., Pollack J.B. (1998). Modeling building-block interdependency
    (HIFF). PPSN V, LNCS 1498. URL: https://link.springer.com/chapter/10.1007/BFb0056853
    Relevance: HIFF is a formal landscape that is unsolvable by point mutation and hill-climbing
    but solvable by recombination or encapsulation of preadapted modules. This is exactly the
    Crius dial C (coupled recombination). Watson shows the difference is algorithmic, not a
    matter of degree.
    Verdict: SUPPORTS dial C. It also gives a ready benchmark (HIFF) on which to calibrate the
    rulers before using them on Crius-like substrates.

12. Kashtan N., Alon U. (2005). Spontaneous evolution of modularity and network motifs. PNAS 102(39):
    13773-13778. URL: https://www.pnas.org/doi/abs/10.1073/pnas.0503610102
    With: Parter M., Kashtan N., Alon U. (2008). Facilitated variation: how evolution learns from
    past environments to generalize to new environments. PLoS Comput Biol 4(11): e1000206.
    URL: https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000206
    And: Clune J., Mouret J.-B., Lipson H. (2013). The evolutionary origins of modularity. Proc R Soc B
    280: 20122863. URL: https://arxiv.org/abs/1207.2743
    Relevance: The TASK-SUPPLY lever. Modularly varying goals (and, in Clune et al., a connection
    cost) change what is evolvable without changing the per-goal payoff. This bears on Aphrodite's
    finding that task supply binds.
    Verdict: REFRAMES H-D3-50/51. The supply of environments is itself a construction-landscape
    dial. Internal caveat, which must travel with any citation: Herakles records a failed open
    replication of Kashtan-Alon MVG (AI Safety Camp 2022) and an "authored curriculum" confinement
    (ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl).

13. Kouvaris K., Clune J., Kounios L., Brede M., Watson R.A. (2017). How evolution learns to generalise.
    PLoS Comput Biol 13(4): e1005358. URL: https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1005358
    With: Watson R.A., Szathmary E. (2016). How can evolution learn? Trends Ecol Evol 31: 147-157.
    URL: https://www.sciencedirect.com/science/article/abs/pii/S0169534715002931
    (Kouvaris is HELD in ergon/kouvaris2017.)
    Relevance: Developmental organisation (the GP map) evolves to bias variation toward past-useful
    phenotypes. The "hidden axis" is itself evolvable.
    Verdict: REFRAMES. The construction landscape is not a fixed property of the substrate; selection
    over varying tasks reshapes it. The strongest internal CONTRADICTION sits here too. Herakles
    ran HC-T01 (Toussaint arm): the accessibility effect was large, but current best fitness
    predicted subsequent acquisition as well as or better than every accessibility statistic (K7).
    A measured accessibility ruler can be real and still add nothing predictive.

14. Greenbury S.F., Louis A.A., Ahnert S.E. (2022). The structure of genotype-phenotype maps makes
    fitness landscapes navigable. Nat Ecol Evol 6: 1742-1752. doi:10.1038/s41559-022-01867-z.
    URL: https://www.nature.com/articles/s41559-022-01867-z   (HELD in the essay.)
    With: Draghi J.A., Parsons T.L., Wagner G.P., Plotkin J.B. (2010). Mutational robustness can
    facilitate adaptation. Nature 463: 353-355. URL: https://pubmed.ncbi.nlm.nih.gov/20090752/
    Relevance: In biological GP maps, peaks are reachable without crossing valleys. Draghi et al.
    add that robustness helps or hinders depending on N, mu and landscape structure.
    Verdict: CONTRADICTS the strong form ("cognitive primitives are generally behind valleys").
    It SUPPORTS the weak form (representation decides). It is the Crius essay's own best attacker.

15. Gray M.W., Lukes J., Archibald J.M., Keeling P.J., Doolittle W.F. (2010). Irremediable complexity?
    Science 330: 920-921. doi:10.1126/science.1198594. URL: https://www.science.org/doi/10.1126/science.1198594
    With: Nordin P., Francone F., Banzhaf W. (1996). Explicitly defined introns and destructive
    crossover in genetic programming. Advances in Genetic Programming 2, MIT Press (bibliographic
    detail from search snippets only; paper not opened; UNVERIFIED).
    And: Lynch M. (2007). The frailty of adaptive hypotheses for the origins of organismal complexity.
    PNAS 104 suppl 1: 8597-8604. URL: https://www.pnas.org/doi/10.1073/pnas.0702207104
    Relevance: Constructive neutral evolution: neutral components accrete and become entrenched
    ("ratchet") with no function. In GP, neutral code (introns) is retained because it protects
    against destructive variation.
    Verdict: REFRAMES H-D3-63. "Invocation without content" is a known class of phenomenon
    (neutral accretion, bloat), so the fossil is not new in kind. What is new is the 4-way
    content-varying assay (intact / wiped / reset / scrambled) as a detector.

Also consulted, secondary (URLs fetched in search):
- LaBar T., Adami C. (2016). Different evolutionary paths to complexity for small and large
  populations of digital organisms. PLoS Comput Biol 12: e1005066. https://arxiv.org/abs/1604.06299
  Small and large populations, but not intermediate ones, grow genomes; drift drives the small
  ones. This matters for Crius's elite of 8.
- Lehman J., Stanley K.O. (2013). Evolvability is inevitable. PLoS ONE 8(4): e62186.
  https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0062186
- Wang R., Lehman J., Clune J., Stanley K.O. (2019). POET. arXiv:1901.01753. https://arxiv.org/abs/1901.01753
  Environment generation as the stepping-stone supplier, relevant to Aphrodite supply.
- Ellis K. et al. (2021). DreamCoder. PLDI 2021. https://dl.acm.org/doi/10.1145/3453483.3454080
  Library learning whose abstractions depend on the task corpus, the closest system to Aphrodite G1->G2.
- Clune J., Stanley K.O., Pennock R.T., Ofria C. (2011). On the performance of indirect encoding
  across the continuum of regularity. IEEE TEC 15(3): 346-367. https://icer.msu.edu/publications/On-the-Performance-of-Indirect-Encoding-Across-the-Continuum-of-Regularity
  Same task, different encoding: the nearest published "controlled pair" on representation.
- Uller T., Moczek A.P., Watson R.A., Brakefield P.M., Laland K.N. (2018). Developmental bias and
  evolution: a regulatory network perspective. Genetics 209: 949-966. https://academic.oup.com/genetics/article/209/4/949/5930979
- Hu T., Payne J.L., Banzhaf W., Moore J.H. (2012). Evolutionary dynamics on multiple scales ...
  linear genetic programming. GPEM 13: 305-337 (from search snippet; paper not opened).
  https://link.springer.com/chapter/10.1007/978-3-642-20407-4_2 (companion "Robustness,
  evolvability, and accessibility in linear GP", EuroGP 2011)
- Yu T., Miller J.F. (2001). Neutrality and the evolvability of Boolean function landscape. EuroGP,
  LNCS 2038. https://link.springer.com/chapter/10.1007/3-540-45355-5_16
- Mouret J.-B., Clune J. (2015). Illuminating search spaces by mapping elites. arXiv:1504.04909.
  https://arxiv.org/abs/1504.04909
- Wagner A. (2014). Arrival of the Fittest. Current/Penguin. https://www.penguinrandomhouse.com/books/314334/arrival-of-the-fittest-by-andreas-wagner/
- Local optima networks (Ochoa and colleagues): https://dl.acm.org/doi/10.1145/3319619.3326852

Not checked in this pass (UNVERIFIED): Toussaint's 2003 thesis claims beyond what ergon/kouvaris2017
records; Kirschner & Gerhart 1998 "Evolvability" PNAS (named from memory, not searched); Stoltzfus
1999 CNE original (named from memory); Wagner 2005 "Robustness and Evolvability in Living Systems"
(named from memory).

---

## 4. Prior failures and known pitfalls

P1. Accessibility statistics that do not beat current fitness. This is Herakles's own HC-T01 result
    (spec-toussaint-exploration, kill condition K7): the accessibility effect was large, yet
    current best fitness predicted acquisition equally well or better. Before foothold density or
    rho is used as a predictor (H-D3-62, H-D1-46), it must be shown to carry information beyond
    current fitness, robustness and genome length. Herakles HCL01 found that the full three-part
    test (position, reachable distribution, later innovation, with the conditioning step) has
    never been assembled on a neutral network. Wagner 2023 is the closest.
P2. Compositional artefacts. Manrubia & Cuesta 2015 (held in Herakles): an apparent history
    effect vanished analytically under conditioning, because populations drift toward hub
    genotypes. Foothold rates pooled across lineages can show the same artefact.
P3. Detector blind to a real effect. Correlation length did not change while added neutrality
    sped up search (Newman & Engelhardt 1998, via Smith, Husbands & O'Shea 2002, held in Herakles).
    Global landscape statistics can miss accessibility entirely. Crius's paired re-evaluation
    against a neutral-edit base rate is the right corrective. Keep it.
P4. Neutrality is not a free fix (Knowles & Watson 2002; Rothlauf). Unbiased redundancy can slow
    search. H-D3-61 must specify the BIAS of the neutral network, not just its presence.
P5. Kashtan-Alon MVG did not replicate in one open attempt. MVG's advantage is confined to an
    authored region (Herakles). Task-supply dials inherit this risk.
P6. Payoff and landscape are confounded in Ares. From ares/ARES_CYCLE2_REPORT.md lines 21-22 and
    137-139: in the swept basin data RECUR's best is 40.00 (the cap) and KEEP's best is 33.75.
    Recurrence therefore has BOTH the wider basin AND the higher swept peak. "Evolution took the
    wide basin, not the higher peak" rests on the hand-built point comparison (keep 33.75 vs
    recur 24.56 at one parameter value). As written, the Ares data do not separate basin from
    payoff. This is the seat's own reading of the numbers, not a re-analysis, but the two
    figures are on the page. H-D3-56's reparameterisation is exactly the test that would
    separate them.
P7. Optimizer dependence. Ares parked ARES-19 (a novelty arm). Lehman & Stanley show that
    objective-based and novelty-based search reach different stepping stones. Any "evolution
    prefers X" claim needs a second optimizer.
P8. Population-size regime. Crius used an elite of 8 with 24 children per generation. Valley
    and plateau crossing theory (Weissman 2009) and LaBar & Adami 2016 predict sharply different
    behaviour at tiny N (drift-driven, sequential fixation). A null at N=8 does not bound
    behaviour at N=1000 in either direction.
P9. Substrate-specific impossibility masquerading as a general frontier. XOR is routinely evolved
    in NEAT. Ananke's null is plausibly caused by the summing superposition, not by composition
    as such.
P10. Hinton-Nowlan specifics are contested (egtheory blog critique; UNVERIFIED depth). Do not
    over-read the Baldwin model's quantitative claims.
P11. Degenerate task samplers (Aphrodite H-D3-51) are a known curriculum failure. POET and
    DreamCoder both needed explicit machinery (minimal-criterion filters, and corpus design
    respectively) to avoid trivial or degenerate tasks.

---

## 5. Existing code and systems usable

- Avida (digital organisms; the Lenski 2003 and Wilke 2001 substrate): https://github.com/devosoft/avida
  (repo URL from knowledge, UNVERIFIED in this pass). Lets the EQU stepping-stone experiment be
  re-run as a payoff-vs-landscape control.
- ViennaRNA (RNAfold) for exact RNA GP maps and neutral-network enumeration at small L. It is the
  standard calibration substrate for arrival-of-the-frequent measurements (UNVERIFIED URL; widely used).
- Polyomino / Boolean-threshold GP map models from the Ahnert and Louis groups (Greenbury 2022 code
  availability UNVERIFIED).
- Linear GP / CGP enumerable systems (Hu et al. 2012; Yu & Miller 2001). Small enough to enumerate
  genotype and phenotype spaces exhaustively, so basin volumes are exact rather than sampled.
- HIFF (Watson et al. 1998): https://www.cs.brandeis.edu/~richardw/hiff.html. A known-answer
  benchmark on which to calibrate foothold density and rho. Point mutation should score near
  zero and recombination high.
- NEAT implementations (e.g. neat-python; UNVERIFIED URL) as an XOR positive control for Ananke-style claims.
- MAP-Elites / QD libraries (pyribs, QDax; UNVERIFIED URLs) for dial B (niches).
- Mingard-style basin-volume estimation needs no library: sample random genomes, develop them,
  and histogram the phenotypes. Every Prometheus GA engine can already do this.
- Internal: Crius's substrate, gates and PARTS diagnostic are public in crius/ (lane closed, not
  reopened here). Ares's GA and basin.json are in ares/runs/sweep_c2/. Herakles HCA registries are
  in herakles/HERAKLES_HISTORICAL_COLLIDER_V0/.

---

## 6. What looks genuinely unexplored

"Unexplored" means not found in this pass or in Herakles HCL01. That is evidence of absence, not proof.

U1. A 2x2 that separates GP-map frequency from intermediate credit, with endpoint payoff fixed,
    on a MULTI-LINK computational mechanism. Schaper & Louis vary frequency with fitness fixed
    (RNA, single phenotype). Lenski 2003 varies intermediate reward (Avida logic). No paper
    found crosses {target neutral-set size high/low} x {intermediate credit present/absent} for
    one mechanism with an identical endpoint payoff. That design answers H-D3-64 directly: which
    factor dominates, and do they interact? This is Prometheus's controlled pair, made sharp.

U2. Foothold density measured against a neutral-edit base rate, by paired re-evaluation of real
    ancestral steps. The literature measures distributions of fitness effects, fractions of
    accessible orderings (Franke, Weinreich) and evolvability-enhancing mutations (Wagner 2023).
    None found uses "partial-machinery steps vs neutral steps under the same paired held-out test"
    as the statistic. Crius's instrument appears novel. Per P1 it must be shown to beat current
    fitness before it counts as a ruler.

U3. Syntax-without-semantics as a cross-substrate detector. CNE and GP bloat describe neutral
    accretion. No work found proposes the content-varying control (intact / wiped / reset /
    scrambled, plus transplant and ablation) as a general assay for "operations of a capability
    without its content", applied across memory, communication and tool-use substrates. The
    essay's list of analogues (communication without information, reasoning traces without causal
    contribution) is a testable unification that the literature has not attempted.

U4. Basin-volume-predicts-selection across PRIMITIVES within one program substrate (H-D3-57). The
    idea exists in ML (Mingard) and RNA (Schaper, Cowperthwaite). No evolutionary-computation or
    ALife paper was found that estimates the random-genome prior P(carrier) for each of several
    functionally sufficient carriers and tests it against the carrier evolution recruits,
    controlling peak payoff. Ares is one reparameterisation away from doing this.

U5. Cross-substrate transplant of one fixed mechanism with fixed gates (dial G). Clune et al. 2011
    compare encodings on one task. No work found holds a cognitive mechanism, its payoff and its
    causal gates fixed and moves the whole challenge across several unrelated substrates to map
    where the frontier falls. BEE's lowering machinery is unusual in making this cheap.

U6. The task-supply side of arrival-of-the-frequent. The idea is that environment and task
    distributions have their own "frequency bias": families that are qualifiable often get
    learned. MVG and POET manipulate environments, but none found measures qualification rate
    per task family and treats it as the environment-side analogue of phenotype frequency.
    Aphrodite's 0/32 acceptance for mul/mod/powr is exactly this measurement, and it is unusual.

U7. A tested rho. Weissman 2009 gives crossing-time theory for asexual populations. No one has
    checked it against program substrates with multi-link, zero-credit plateaus and small elites
    with takeover checks. Deriving rho's c from Weissman's regimes and testing the predicted
    scaling of discovery time with plateau length k is open and cheap on HIFF-like or Crius-like
    toy substrates.

Where Prometheus's framing adds something (and should not defer to prior art):
- It separates existence, reward and path with separate controls (transplant, ablation, lookup-table
  control). Most "did not evolve" reports cannot say which of the three failed.
- It puts the subject matter in cognitive primitives rather than proteins or RNA folds.
- It has five engines with independent substrates, so the same question can be asked in five
  maps. The literature typically has one map per paper.
- It explicitly names payoff-invariance as the control, which the literature (Lenski) does not.

Where prior art should correct Prometheus:
- "Basin width beats peak" is arrival of the frequent / ascent of the abundant. Cite it and test
  arrival versus flatness (Wilke). Do not present it as new.
- Neutral networks help only when biased (Knowles & Watson). H-D3-61 needs that clause.
- XOR is not generally inaccessible (NEAT). H-D3-44 should be read as substrate specific.
- Accessibility rulers must beat current fitness (Herakles K7) before they are called predictors.

---

## 7. Cheapest discriminating test the literature suggests

Ares H-D3-56, extended into a 2x2 arrival-vs-flatness test with a prior-volume predictor.

Why it is cheapest: the GA, worlds, seeds and basin sweep already exist (ares/runs/sweep_c2/). The
change is one parameterisation (store and mutate log(1/(1-keep)), as the Ares report proposes). It
needs 10 seeds per cell, and no new substrate is required.

Design:
- Factor A (GP map): keep in the original parameterisation vs the widened one. Keep's phenotype
  and payoff are unchanged, so its peak stays at 33.75, below recurrence's 40 cap in the sweep.
  Only its genotype-space volume changes.
- Factor B (mutation rate): baseline vs about 4x (the Wilke 2001 ratio).
- Predictor, recorded BEFORE any run: for each carrier and each parameterisation, estimate the
  random-genome prior P(carrier viable) by sampling about 10^4 random genomes (Mingard-style) and
  apply the existing viability threshold (>= 50% of best).
- Outcome: the share of lineages in which keep is load-bearing, plus time-to-threshold.

Discriminating predictions:
- Arrival of the frequent (Schaper & Louis): keep's share rises in the widened map at BOTH mutation
  rates, roughly tracking the change in P(keep viable), despite keep's lower peak. That would
  confirm "construction landscape over payoff" cleanly, because payoff is fixed and still lower.
- Survival of the flattest (Wilke): the widening effect appears mainly at the high mutation rate.
- Payoff dominance (the null): keep's share does not move. Recurrence's higher swept peak (40
  vs 33.75) explains the original result, and H-D3-57 is refuted as a design rule.
- If all three are ambiguous, add a novelty arm (ARES-19) to rule out optimizer dependence (P7).

The next cheapest test is the calibration of the rulers (foothold density, rho) on HIFF with point
mutation vs recombination. The answer is known there, so a ruler that fails on HIFF is disqualified
before it is spent on Crius, Aether D-15 or Ananke.
