# Prompt 84: Fitness Landscape Structure: Epistasis, Neutrality and Ruggedness

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd1clNmYXFPcEw0MjFfdU1Qd3FPR3VRSRIXdXJTZmFxT3BMNDIxX3VNUHdxT0d1UUk
**Elapsed:** 304s

---

FRONTIER PRACTITIONER DOSSIER
Field: Fitness Landscape Structure: Epistasis, Neutrality and Ruggedness

Your understanding of the structural approach to problem difficulty is fundamentally correct and accurately traces the lineage of the Kauffman NK model, the role of epistasis, and the qualitative shift introduced by neutrality. You are right that a landscape's difficulty is an intrinsic structural property distinct from any single algorithm's trajectory, and that measuring the actual query count of a hill climber is the necessary grounding mechanism to prove that a structural metric actually matters. 

However, your methodology relies heavily on global statistical metrics such as fitness autocorrelation and raw counts of local optima. While these remain foundational, the current frontier has shifted away from viewing landscapes merely as statistical distributions of points. Over the last decade, the field has transitioned to topological and graph-theoretic abstractions. For discrete spaces, the frontier is defined by Local Optima Networks, which compress the search space into a graph where nodes are local optima and edges represent transition probabilities between their basins. For continuous spaces, the frontier is defined by Exploratory Landscape Analysis, which uses machine learning to map low-level sampled features to high-level structural properties. 

The report below maps exactly where this field sits today in 2026, giving you the software, datasets, and theoretical load-bearing structures you need to start building.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of fitness landscape analysis is currently bifurcated into two dominant paradigms that are only now beginning to merge. In the combinatorial and discrete domain, which includes your anchor of the NK model, the reigning methodology is the Local Optima Network model cite: 11, cite: 12. Instead of merely counting peaks, this approach abstracts the entire fitness landscape into a weighted, directed graph. The vertices are the local optima, and the edges are the transition probabilities between their respective basins of attraction under a specific search operator. In the continuous domain, the field is dominated by Exploratory Landscape Analysis cite: 23, cite: 31, which samples the landscape to compute hundreds of low-level statistical and topological features, using them as inputs for Automated Algorithm Selection. 

What is SETTLED is that simple ruggedness measures, such as the raw count of local optima or fitness distance correlation, are insufficient to predict algorithm performance cite: 39. The structure of the landscape matters more than the raw counts. It is settled that landscapes decompose into "funnels" or communities of local optima cite: 14, cite: 15, and that the difficulty of a landscape is largely determined by the number of suboptimal funnels and the size of the funnel containing the global optimum. It is also settled that neutrality fundamentally alters landscape traversal; neutral networks percolate through the space, and models like the Local Optima Network have been successfully adapted to compress these neutral plateaus into single topological nodes to preserve the predictive power of the network cite: 13, cite: 39.

What is CONTESTED is the robustness and generalisability of the sampled features used to characterize these landscapes. In the Exploratory Landscape Analysis community, there is an ongoing and severe critique regarding the sensitivity of these features to basic transformations. A live disagreement exists regarding how many of the 300+ standard landscape features are actually measuring structural properties versus simply measuring artefacts of the sampling distribution, scaling, or affine shifting cite: 22. Researchers such as Prager and Trautmann argue that many classical features have unacceptably low signal-to-noise ratios and must be discarded or replaced by invariant counterparts, while others continue to use the full feature suites in standard machine learning pipelines because they empirically improve algorithm selection.

What is OPEN is the unification of discrete, continuous, and categorical landscape analysis into a single mixed-variable framework cite: 23. Real-world optimization problems do not respect the boundary between the NK model's bit-strings and the continuous domains of black-box optimization benchmarks. The frontier is currently focused on Mixed-Variable Exploratory Landscape Analysis and Deep-ELA cite: 22, which attempts to use point-cloud transformers and deep learning to embed landscapes directly without relying on handcrafted, brittle statistical features. Furthermore, extracting Local Optima Networks for large-scale combinatorial problems where exhaustive enumeration is physically impossible remains a largely open computational challenge.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Kauffman, S., and Weinberger, E.
1989
The NK model of rugged fitness landscapes and its application to maturation of the immune response
Journal of Theoretical Biology
DOI 10.1016/S0022-5193(89)80019-0
This is the genesis of the NK model that parameterises epistasis. You must know it to understand how tuning K controls the correlation length and peak density of the landscape.

Mersmann, O., Bischl, B., Trautmann, H., Preuss, M., Weihs, C., and Rudolph, G.
2011
Exploratory landscape analysis
Proceedings of the 13th Annual Genetic and Evolutionary Computation Conference
DOI 10.1145/2001576.2001690
This paper defined Exploratory Landscape Analysis for continuous spaces, establishing the standard six high-level properties and their low-level statistical proxies that are still computed by modern software today.

Ochoa, G., Tomassini, M., Verel, S., and Darabos, C.
2008
A Study of NK Landscapes' Basins and Local Optima Networks
Proceedings of the 10th Annual Genetic and Evolutionary Computation Conference
DOI 10.1145/1389095.1389204
The foundational paper that introduced Local Optima Networks for combinatorial spaces, proving that NK landscapes exhibit small-world network properties and changing the field's focus from point statistics to basin topology.

Verel, S., Ochoa, G., and Tomassini, M.
2011
Local Optima Networks of NK Landscapes with Neutrality
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2010.2046175
This paper extends Local Optima Networks to the NKp and NKq models, defining how neutral plateaus are compressed into nodes and demonstrating mathematically how neutrality enhances heuristic search by creating percolating networks.

CURRENT SOURCES

Doerr, C., Wang, H., Ye, F., van Rijn, S., and Bäck, T.
2018 (Updated continuously, foundational for 2026 praxis)
IOHprofiler: A Benchmarking and Profiling Tool for Iterative Optimization Heuristics
arXiv:1810.05281
This defines the modern standard for benchmarking heuristic query counts against structured landscapes. It is the authoritative methodology for proving that a landscape metric actually correlates with algorithm exhaustion.

Prager, R. P., and Trautmann, H.
2024
Pflacco: Feature-Based Landscape Analysis of Continuous and Constrained Optimization Problems in Python
Evolutionary Computation
DOI 10.1162/evco_a_00346
This paper documents the shift of Exploratory Landscape Analysis from R to Python, detailing the exact mathematical implementations of modern landscape features and defining the current software frontier.

Prager, R. P., and Trautmann, H.
2024
Exploratory Landscape Analysis for Mixed-Variable Problems
arXiv:2402.16467
This paper represents the absolute frontier of structural analysis, bridging the gap between discrete loci and continuous variables by using machine learning encoding techniques to calculate landscape features for mixed-variable spaces.

Mitchell, P., and Chassagne, R.
2023
Fitness landscape analysis for assisted seismic history matching problems
Journal of Geophysics and Engineering
DOI 10.1093/jge/gxad062
A crucial read for a practitioner because it proves how these abstract structural methods apply to real-world, ill-posed, computationally expensive inverse problems, demonstrating how data errors manifest topologically as low-lying plateaus.

Santoni, C., et al. (Prager, Trautmann)
2025
Deep-ELA: Deep Exploratory Landscape Analysis with Point-Cloud Transformers
arXiv identifier pending or accessible via recent conference proceedings (cite: 22)
This maps the immediate future of the field, demonstrating how handcrafted landscape features are being replaced by transformer-based embeddings to avoid the correlation and scaling weaknesses of traditional metrics.

PART 3. SOFTWARE I CAN ACTUALLY RUN

IOHprofiler
https://iohprofiler.github.io
Implementation: C++ and Python
Licence: BSD-3-Clause
Most recent activity: 2026
Maturity: MAINTAINED
This is the absolute community standard for running the experiments you described. It consists of IOHexperimenter for generating data and IOHanalyzer for statistical evaluation. You can use it today to run a one-flip hill climber over a parameterized suite of discrete problems and perfectly track the fixed-target running time (the query count) against the problem difficulty. Its primary limitation is that integrating entirely novel landscape topologies requires writing custom C++ wrappers, though the Python bindings have improved significantly.

pflacco
https://github.com/Reiyan/pflacco
Implementation: Python
Licence: BSD-2-Clause
Most recent activity: 2025
Maturity: MAINTAINED
This is the modern reimplementation of the original R-based flacco package. It calculates nearly 300 Exploratory Landscape Analysis features. You can pass it a sample of genotypes and their fitness values, and it will output structural metrics including ruggedness, local optima estimates, and neutrality gradients. The gotcha here is that because it relies on sampling, the features are highly stochastic. A known limitation is that the Sobol sequence generator used internally was flagged for producing deterministic samples across sessions unless explicitly reseeded, which can silently ruin independent replicate claims.

flacco
https://github.com/kerschke/flacco
Implementation: R
Licence: BSD-2-Clause
Most recent activity: 2019
Maturity: DORMANT
This is the canonical reference implementation of Exploratory Landscape Analysis from the originating authors. While famous and load-bearing in the literature, it is effectively dead for new experimental pipelines because the field has migrated to Python. The R implementation is drastically slower than pflacco and is maintained only for legacy reproducibility. Do not build new infrastructure on this.

COCO (Comparing Continuous Optimizers)
https://github.com/numbbo/coco
Implementation: C, with Python/Java/MATLAB wrappers
Licence: BSD-3-Clause
Most recent activity: 2024
Maturity: MAINTAINED
COCO hosts the Black-Box Optimization Benchmark suite. It is the evaluation harness that everyone uses to prove an algorithm works. While primarily continuous, it is the benchmark against which landscape features are most frequently measured. A known gotcha is that calculating expected running times across different transformed instances of the same function can obscure landscape differences, as the affine transformations can alter the topological difficulty.

Nevergrad
https://github.com/facebookresearch/nevergrad
Implementation: Python
Licence: MIT
Most recent activity: 2024
Maturity: MAINTAINED
Developed by Facebook Research, this is a vast collection of algorithms and benchmark suites. It is useful for extracting baseline algorithms to test your landscapes against. It integrates well with pflacco for extracting features of the spaces it explores. 

PART 4. DATA AND BENCHMARKS

Black-Box Optimization Benchmark (BBOB)
URL: Hosted within the COCO and IOHprofiler repositories.
Size: 24 base continuous functions, scalable to any dimension, with endless instantiated variants.
Licence: BSD-3-Clause
What it measures: Continuous landscape difficulty. It is the authoritative benchmark in the field. Every new landscape metric must be tested on BBOB to prove it can separate multimodal, rugged, and ill-conditioned funnels. Known contamination issue: Because BBOB is so dominant, many meta-heuristic algorithms are implicitly overfitted to its specific suite of 24 functions. Features extracted from BBOB do not always generalise to real-world landscapes like neural architecture search or history matching.

Pseudo-Boolean Optimization (PBO) Suite
URL: Embedded within IOHexperimenter.
Size: 25 discrete test problems of the kind mapping bit-strings to real numbers.
Licence: BSD-3-Clause
What it measures: Combinatorial algorithmic performance. This is the authoritative suite for discrete search. It includes tunable ruggedness and epistatic interactions. If you are running an NK model experiment, you will run it against the PBO suite framework to ensure your metrics are comparable to the literature.

CEC Benchmark Suites
URL: Distributed annually via IEEE Congress on Evolutionary Computation.
Size: Varies annually, typically 10 to 30 functions.
Licence: Open access via competition rules.
What it measures: Algorithm performance on heavily rotated, shifted, and hybridized continuous functions. These are merely popular, not authoritative like BBOB. They suffer from severe saturation; top algorithms overfit the competition rules, and the landscapes are often artificial composite structures that do not resemble physical or computational phenomena.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in this field is the extraction of a Local Optima Network from an NK landscape and the correlation of its structural metrics with the query count of an Iterated Local Search algorithm. This proves the direct link between epistasis (K), network topology (basins), and actual search difficulty.

The Recipe:
1. Software and Versions:
Write a custom Python script utilising numpy (version 1.26 or later) for the landscape generation and networkx (version 3.2 or later) for the graph representation. Use IOHprofiler (version 3.3 or later) strictly to host the Iterated Local Search baseline.

2. Dataset / Generator:
Generate standard Kauffman NK landscapes. Set N=18. This is the critical threshold. N=18 creates a state space of 262,144 genotypes. This is small enough that you can exhaustively evaluate the entire space in RAM to find the absolute truth of the landscape, but large enough that a hill climber will exhibit variable query counts.

3. Parameters:
Set N=18. Generate 30 independent landscape instances for each value of K in the set: 2, 4, 6, 8, 10, 12, 14, 16, 17. 
Neighbourhood operator: 1-bit flip.

4. Execution Steps:
Step A: Exhaustively evaluate all 262,144 points for a given instance.
Step B: From every point, run a best-improvement hill climber until it hits a local optimum. Record the optimum. The set of all starting points that terminate at a specific optimum is its Basin of Attraction.
Step C: Construct the Local Optima Network. Nodes are the unique local optima. Node weights are the size of their basins. Edges are the transition probabilities: the chance that a 1-bit mutation from a solution in basin A lands in basin B.
Step D: Calculate the network metrics: number of nodes, average path length between nodes, and out-degree.
Step E: Run an Iterated Local Search algorithm on the exact same instance. Record the number of objective function queries required to hit the global optimum (or the best found within a fixed budget of 10000 queries).
Step F: Calculate the multiple linear regression between the LON features and the ILS query count.

5. Compute Cost:
Extracting the complete LON for a single N=18 landscape takes roughly 2 to 5 CPU minutes on a modern architecture. Generating the full suite of 270 instances (30 instances across 9 K-values) and computing their networks will consume approximately 15 to 25 CPU hours. No GPU is required.

6. Expected Result:
As K increases from 2 to 17, the number of local optima will scale exponentially, and the basins of attraction will shrink. The network will exhibit small-world properties. The multiple linear regression will show that LON features (specifically the number of local optima and the basin size of the global optimum) strongly predict the ILS query count. You are aiming to replicate the exact structural progression shown in Ochoa et al., 2012 (arXiv:1210.3946).

7. The Three Most Common Ways People Get This Wrong:
First, using a first-improvement hill climber instead of a best-improvement hill climber to define the basins. First-improvement makes basin definition stochastic, meaning the Local Optima Network is no longer a deterministic property of the landscape structure, ruining reproducibility.
Second, failing to correctly normalize the edge weights. The transition probability must be calculated across the entire basin, not just from the local optimum itself.
Third, attempting to increase N to 24 or higher. At N=24, the state space is 16.7 million. Exhaustive extraction becomes computationally prohibitive in Python without a heavily optimized C backend, leading practitioners to switch to sampling without realizing that sampled LONs have entirely different statistical properties than exhaustively extracted ones.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field as a competent computational scientist, the most glaring gap you will notice is the lack of a scalable, off-the-shelf software library for extracting Local Optima Networks via statistical sampling for large N. 

Currently, if you want to analyse an NK landscape where N=100 or N=1000, exhaustive extraction is impossible. Several research groups have privately rebuilt Markov Chain Monte Carlo random-walk samplers to estimate LON topologies (e.g., Snowball sampling or Metropolis-Hastings walks over the optima). None of these are standardised.

What you must build:
A Python library named, for instance, `LONsampler`.
Interface In: A fitness function `f(x)`, a discrete genotype length `N`, a neighbourhood definition (e.g., Hamming distance 1), and a sampling budget (e.g., 100000 evaluations).
Interface Out: A `networkx` directed graph object representing the sampled Local Optima Network, with nodes annotated with estimated basin sizes, and edges annotated with estimated transition probabilities.
The Hard Part: Unbiased sampling of basins. A random walk will inevitably get trapped in the largest basins (the "funnel" effect), severely under-sampling the structural periphery of the landscape. Correcting for this sampling bias to accurately estimate the true number of local optima requires implementing advanced Wang-Landau or Multicanonical Monte Carlo algorithms. 
Effort: This is a three to six-month engineering project for a single competent computational scientist, but it would immediately become a load-bearing tool for the entire discrete optimization community.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field has a history of adopting attractive structural metrics that later turn out to be deeply flawed. You must internalise these critiques before running experiments.

1. The Correlation and Sensitivity of ELA Features
The most significant standing critique of the continuous field is that the 300+ Exploratory Landscape Analysis features are highly correlated and sensitive to basic affine transformations. Renau, Prager, and Trautmann have demonstrated that simply scaling the objective values or shifting the domain boundaries will drastically alter the calculated feature values for Classical ELA, Information Content, and Principal Component Analysis sets. A machine learning model trained to select algorithms based on these features is often just learning the scale of the domain rather than the topological difficulty of the landscape. This critique was answered partially by identifying subset groups of "robust" features, but it remains a persistent vulnerability in the methodology.

2. The Big Valley Hypothesis is Flawed
For decades, combinatorial landscapes like the Travelling Salesperson Problem were assumed to follow the "Big Valley" hypothesis: that local optima are clustered around a single central global optimum, forming one massive funnel. Recent extraction of Local Optima Networks has completely falsified this. Landscapes frequently decompose into multiple, distinct funnels separated by high fitness barriers. Methods built on the assumption that a landscape has a single macro-gradient have failed to generalise.

3. Inferred Landscapes Underestimate Ruggedness
When practitioners attempt to infer a fitness landscape from a time series of a reproducing population (such as inferring epistasis from biological mutation data), the statistical models consistently exhibit a specific failure mode. Because models like penalized linear regressions omit variables (such as higher-order interactions between loci) due to lack of data, the inferred fitness landscape systematically exhibits less local ruggedness than the true underlying landscape. This bias makes evolutionary trajectories look more predictable than they actually are.

4. The Curse of Dimensionality in Cell Mapping
Several early landscape metrics attempted to divide the search space into a grid of cells (Cell Mapping features) to calculate dispersion and topological boundaries. This programme completely failed for high dimensions. For any N greater than 20, cell-based metrics become computationally intractable and statistically meaningless because almost all cells are empty. The field quietly dropped these features, but they still exist as dead code in packages like flacco.

5. Misidentifying the Benchmark for the Phenomenon
Many structural algorithms look strong in publications because they classify the 24 BBOB functions with 99 percent accuracy. It was later shown that these models were not learning the universal principles of "multimodality" or "ill-conditioning"; they were memorizing the specific parametric generators of the BBOB suite. When applied to real-world tasks like assisted seismic history matching, where the landscape consists of low-lying plateaus with massive data errors, the highly tuned ELA pipelines failed to predict algorithm performance better than random guessing.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given your compute access and ability to build, you should bypass the saturated continuous benchmarking competitions and aim at the exact intersection of landscape analysis and modern machine learning. Here are the specific experiments to run, ranked by value.

1. Deep-ELA for Mixed-Variable Spaces
Aim: Compute embeddings for mixed-variable landscapes (combinations of categorical, integer, and continuous variables, typical of Neural Architecture Search or Hyperparameter Optimization) without using handcrafted statistical features.
Feasibility: Feasible now because of the recent adaptation of point-cloud transformers to landscape analysis. 
Measurement: Generate a massive dataset of random mixed-variable instances. Sample points and pass them through a point-cloud transformer to create a latent vector. Measure whether the cosine similarity of these vectors correlates with the transferability of optimization hyperparameters between the instances.
Falsification: If a simple Random Forest trained on traditional pflacco features outperforms the transformer embedding in predicting the best algorithm, the Deep-ELA hypothesis is falsified.

2. The Sampling-Based M-LON (Monotonic Local Optima Network) for Massive N
Aim: Measure the topological funnel structure of a highly epistatic NKq landscape (which includes neutrality) for N=1000.
Feasibility: Feasible now because you can build the biased-random-walk sampling software described in Part 6.
Measurement: Instead of counting local optima, measure the number of unique "Plateaus" (compressed neutral networks) and the transition probabilities between them. Measure the correlation between the size of the largest plateau and the exhaustion rate of a hill climber. 
Falsification: If the network properties derived from the sampling algorithm fluctuate wildly under different random seeds and fail to converge on a stable graph topology after 1,000,000 evaluations, the hypothesis that massive landscapes can be approximated via sampling is falsified.

3. What Will NOT Work
Do not attempt to design "new and improved" statistical low-level features for Exploratory Landscape Analysis. The space of handcrafted statistical proxies (skewness of fitness distributions, correlation lengths, convexity measurements) is entirely saturated. Adding a new mathematical metric to the existing 300+ will not yield any predictive edge because the remaining unexplained variance in algorithm performance is structurally non-linear. The field does not need more features; it needs robust, scale-invariant representations of the topology. Writing a paper proposing "A novel feature for ruggedness" is a guaranteed dead end in 2026. Stick to network topologies and learned embeddings.
