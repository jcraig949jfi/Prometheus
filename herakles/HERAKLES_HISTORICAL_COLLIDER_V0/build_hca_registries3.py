"""Append the HC-R01 detector-stack lane findings to registry S.

All rows below come from the HC-R01 detector lane. Read depth is stated per row
and must not be upgraded. Two sources were read in full; the rest are abstract
or search-mediated, and several were blocked by 403 or expired TLS.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

S_ADD = [
 {"detector_id": "DP-VANNIMWEGEN-SPECTRAL-1999",
  "historical_name": "population-average neutrality via network spectral radius",
  "first_source": "van Nimwegen, Crutchfield and Huynen 1999, 'Neutral evolution of mutational robustness', PNAS 96(17):9716-9720",
  "access": "ABSTRACT_ONLY",
  "mathematical_object": "mean number of neutral one-mutant neighbours per individual, shown analytically to equal the principal eigenvalue of the neutral network's adjacency matrix in the population's stationary distribution",
  "estimator": "ANALYTIC. Once the theory is granted, the population's own steady-state distribution over the network converges to the principal eigenvector, so average neutrality is inferable from ordinary population data.",
  "sampling_cost": "EFFECTIVELY ZERO MARGINAL COST. Requires only the population data already being collected to run the experiment.",
  "locality": "LOCAL (neutral degree) but population-averaged",
  "longitudinal_capability": "YES, and it is the point of the paper: measurable continuously from an ongoing run's composition",
  "substrate_generality": "framed as general theory of populations on neutral networks",
  "causal_interpretability": "not tested with an intervention",
  "predictive_power_beyond_current_fitness": "NOT TESTED. The claim is about robustness and mutation load, not about predicting subsequent gain.",
  "what_it_misses": "it is a robustness statistic, not a count of distinct reachable phenotypes; it says nothing about WHICH novel phenotypes are one step away",
  "known_confounds": "requires quasi-equilibrium on a neutral network; the result is stated to be independent of mutation rate, population size and selective advantage, which is a strength for portability and a weakness for discrimination",
  "verdict_for_us": "THE CHEAPEST DETECTOR FOUND ANYWHERE. Zero marginal cost against our 2000x. Worth stealing on cost grounds alone, if the quasi-equilibrium precondition can be met.",
  "evidence_tier": "HCR01_LANE_ABSTRACT_ONLY"},

 {"detector_id": "DP-SMITH-EVOLVABILITY-PORTRAIT-2002",
  "historical_name": "evolvability metrics Ea/Eb/Ec/Ed and the fitness-evolvability portrait",
  "first_source": "Smith, Husbands, Layzell and O'Shea 2002, 'Fitness Landscapes and Evolvability', Evolutionary Computation 10(1):1-34; the identical-content Sussex tech report CSRP 534 was read in full",
  "access": "FULL_TEXT_READ",
  "mathematical_object": "the offspring transmission function T(f | h,k), the probability density of offspring fitness given parent genotype and parent fitness, in the Cavalli-Sforza and Feldman / Altenberg formalism. Ea = P(offspring fitness >= parent fitness); Eb = expected offspring fitness; Ec and Ed = expected fitness of the top and bottom percentile of offspring.",
  "estimator": "BOTH analytic (closed form for NK) and Monte Carlo; the discrete version FULLY ENUMERATES the one-mutant neighbourhood of each sampled parent",
  "sampling_cost": "stated: 1000 individuals from each of 100 landscapes, 100,000 sampled solutions, each with its 25-neighbour set enumerated, about 2.5M neighbour evaluations; the online variant collects 100,000 evaluations as a BYPRODUCT of the search itself rather than as extra probing",
  "locality": "LOCAL, one variation step, real operator",
  "longitudinal_capability": "YES AND EXPLICITLY VALIDATED. Section 7 computes the metrics from genotypes collected DURING an actual hill-climbing run and shows the biased online sample gives the same qualitative predictions as unbiased random sampling.",
  "substrate_generality": "the transmission-function formalism is substrate-general and the authors explicitly motivate it by problems where no distance metric can even be defined, which is why they avoid correlation-length measures",
  "causal_interpretability": "not combined with an intervention",
  "predictive_power_beyond_current_fitness": "NOT TESTED, and the reason is instructive. The portrait is BUILT BY conditioning on fitness, plotting evolvability as a function of current fitness. So the paper does the conditioning and then never asks the marginal question. Its predictive claims are landscape-level difficulty at different fitness thresholds.",
  "what_it_sees": "how the SHAPE of the offspring-fitness distribution changes with parent fitness, capturing both ruggedness and neutrality, which the authors show correlation-length methods cannot",
  "known_confounds": "the authors flag that random sampling badly under-represents high-fitness regions in skewed landscapes, which is why they built the online variant",
  "verdict_for_us": "STRUCTURALLY THE CLOSEST HISTORICAL RELATIVE OF OUR OWN INSTRUMENT, and it is 2002, one year before Toussaint's thesis. It independently invented the offspring-distribution detector, validated it online during real runs, and stopped one question short of the marginal test.",
  "evidence_tier": "HCR01_LANE_FULL_TEXT"},

 {"detector_id": "DP-HANSEN-CONDITIONAL-EVOLVABILITY",
  "historical_name": "conditional evolvability, respondability, autonomy (G-matrix suite)",
  "first_source": "Hansen and Houle 2008, J Evol Biol 21:1201-1219; tested in Hansen, Solvin and Pavlicev 2019, 'Predicting evolutionary potential: A numerical test of evolvability measures', Evolution 73(4):689-703",
  "access": "ABSTRACT_ONLY for both; the 2019 abstract was retrieved directly",
  "mathematical_object": "functions of the additive-genetic variance-covariance matrix: unconditional evolvability, respondability, CONDITIONAL evolvability (potential when other traits are held under stabilising selection), autonomy, integration. NOTE this is continuous multivariate trait space, NOT mutation-neighbourhood reachability on a discrete map.",
  "estimator": "analytic closed forms from the G matrix; the 2019 test used individual-based simulations to generate ground-truth selection responses",
  "sampling_cost": "cheap once G is estimated; the cost is upstream in estimating G",
  "locality": "n/a, trait-space",
  "longitudinal_capability": "the 2019 test compares static measures against simulated short-term selection RESPONSES, which is the clearest static-predicts-dynamic design found",
  "substrate_generality": "general quantitative-genetics theory",
  "causal_interpretability": "the 2019 design imposes stabilising selection on other traits and checks whether conditional evolvability predicts the resulting response, which is intervention-paired validation",
  "predictive_power_beyond_current_fitness": "CLOSEST ADJACENT HIT, BUT NOT OUR QUESTION. Reported positive: conditional evolvability successfully predicts rates of evolution in an equilibrium situation, and evolvabilities bracket responses to selection. But the CONDITIONING VARIABLE is competing-trait selective load, not current fitness. Effect sizes not obtainable from the abstract.",
  "known_confounds": "approximation formulas carry known bias for low-dimensional G matrices, and corrections to the 2008 appendices have been published",
  "verdict_for_us": "shows the field CAN do a conditional test, in a different formalism, on a different conditioning variable",
  "evidence_tier": "HCR01_LANE_ABSTRACT_ONLY"},

 {"detector_id": "DP-LON-THOMSON-2020",
  "historical_name": "sampled local-optima-network features predicting search success",
  "first_source": "Ochoa, Verel and Tomassini local optima networks, circa 2008; Thomson, Ochoa, Verel and Veerapen 2020, 'Inferring Future Landscapes: Sampling the Local Optima Level', Evolutionary Computation 28(4):621-641",
  "access": "ABSTRACT_ONLY",
  "mathematical_object": "a compressed graph whose vertices are local optima or neutral plateaus and whose edges are basin-transition probabilities",
  "estimator": "originally full enumeration, which scales badly; the 2020 paper's contribution is sampling-based construction",
  "sampling_cost": "reduced by design; sampled LONs reportedly explain search-performance variance as well as or better than fully enumerated ones",
  "locality": "GLOBAL, coarse-grained to the local-optimum level",
  "longitudinal_capability": "offline feature extraction, not a per-generation in-run statistic",
  "substrate_generality": "demonstrated on the Quadratic Assignment Problem and NK landscapes",
  "causal_interpretability": "not established",
  "predictive_power_beyond_current_fitness": "STRONGEST NAMED PREDICTIVE RESULT IN THE STACK, BUT THE WRONG UNIT. A model predicting tabu-search success from combined LON features reportedly explains 99 percent of variance. That predicts ALGORITHM performance across problem INSTANCES, not an individual genotype's future gain net of its own current fitness. Exact figure or table number not confirmed.",
  "known_confounds": "basin definitions depend on the local-search operator, and two edge definitions give materially different structure",
  "verdict_for_us": "a warning about unit of analysis as much as a candidate. Very high explained variance at the instance level says nothing about the individual-trajectory question.",
  "evidence_tier": "HCR01_LANE_ABSTRACT_ONLY"},

 {"detector_id": "DP-WEINBERGER-CORRELATION-LENGTH-1990",
  "historical_name": "fitness-landscape autocorrelation and correlation length",
  "first_source": "Weinberger 1990, 'Correlated and uncorrelated fitness landscapes and how to tell the difference', Biological Cybernetics 63:325-336; method reproduced in Smith et al 2002 which was read in full",
  "access": "ABSTRACT_ONLY, corroborated by full-text secondary description",
  "mathematical_object": "autocorrelation of fitness along a random walk; correlation length tau = -1/ln(rho(1))",
  "estimator": "Monte Carlo random walk",
  "sampling_cost": "CHEAP. Scales with walk length, one new fitness evaluation per step, not with neighbourhood size.",
  "locality": "global summary",
  "longitudinal_capability": "walk-based by construction, but summarises global structure rather than tracking a live population",
  "substrate_generality": "fully general for any solution set, neighbourhood and fitness triple",
  "causal_interpretability": "not combined with an intervention",
  "predictive_power_beyond_current_fitness": "NOT TESTED, and worse: DOCUMENTED BLIND TO A REAL EFFECT. Newman and Engelhardt showed added neutrality speeds up search without changing correlation length at all, and Barnett showed the statistic is insensitive to neutrality even when neutrality demonstrably changes search speed.",
  "known_confounds": "conflates ruggedness with neutrality-driven dynamics",
  "verdict_for_us": "OUR BACKGROUND, MIRRORED. Our detector saw a difference that did not matter; this detector misses a difference that does. Both failure directions are on record.",
  "evidence_tier": "HCR01_LANE_ABSTRACT_ONLY + full-text secondary"},

 {"detector_id": "DP-GREENBURY-CROSS-SUBSTRATE",
  "historical_name": "constrained and unconstrained sequence partition of genotype-phenotype maps",
  "first_source": "Greenbury, Johnston, Louis and Ahnert 2015/2016, J R Soc Interface",
  "access": "ABSTRACT_ONLY",
  "mathematical_object": "decomposition of sequence positions into constrained and unconstrained parts, yielding genotypic and phenotypic robustness and evolvability and their scaling",
  "estimator": "exhaustive enumeration, feasible for the small model systems used",
  "sampling_cost": "not confirmed",
  "locality": "LOCAL neighbourhood counts, aggregated",
  "longitudinal_capability": "static, not applied per generation",
  "substrate_generality": "STRONGEST IN THE STACK. The same statistics are computed and compared across RNA secondary structure, HP lattice protein folding and Polyomino self-assembly, three genuinely different physical maps.",
  "causal_interpretability": "not established",
  "predictive_power_beyond_current_fitness": "NOT TESTED. The work is about the robustness-evolvability trade-off structure.",
  "known_confounds": "robustness and evolvability correlate negatively at genotype level and positively at phenotype level, a level-of-description confound the field itself flags",
  "verdict_for_us": "the cross-substrate comparison method is worth stealing even though the statistic is not longitudinal",
  "evidence_tier": "HCR01_LANE_ABSTRACT_ONLY"},

 {"detector_id": "DP-OTHERS-SCREENED",
  "historical_name": "screened and not carried forward",
  "first_source": "Schuster, Fontana, Stadler and Hofacker 1994 neutral networks; Wagner genotype-network evolvability; Ancel and Fontana 2000 plasticity and modularity in RNA; Kauffman and Levin 1987 adaptive walks; Jones and Forrest 1995 fitness-distance correlation; Vanneschi et al negative slope coefficient; Verel, Collard and Clergue 2006 autocorrelation of evolvability (FULL_TEXT_READ); Eyre-Walker and Keightley 2007 distribution of fitness effects; Holstad et al 2024 Science evolvability predicts macroevolution; Payne and Wagner 2019 review",
  "access": "mixed; mostly ABSTRACT_ONLY. Ancel and Fontana 2000 could NOT be read: the author-hosted PDF has an expired TLS certificate and every mirror returned 403. It is flagged as the weakest-evidenced item and is the closest published analogue to our own instrument, so it remains an open access gap.",
  "predictive_power_beyond_current_fitness": "NOT TESTED in any of them",
  "verdict_for_us": "each is either a static landscape characterisation or an aggregate difficulty predictor. Kauffman-Levin adaptive-walk statistics are CHEAP (order N neighbour evaluations per step) and Verel's autocorrelation-of-evolvability is walk-based and therefore also cheap. Holstad 2024 is real macroevolutionary evidence that evolvability predicts divergence in living taxa, but whether current performance was controlled could not be confirmed.",
  "evidence_tier": "HCR01_LANE_MIXED"},
]

if __name__ == "__main__":
    p = os.path.join(HERE, "HCA_DETECTOR_COMPARISON.jsonl")
    with open(p, "a", encoding="utf-8") as f:
        for r in S_ADD:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("HCA_DETECTOR_COMPARISON.jsonl +%d -> %d rows"
          % (len(S_ADD), sum(1 for _ in open(p, encoding="utf-8"))))
