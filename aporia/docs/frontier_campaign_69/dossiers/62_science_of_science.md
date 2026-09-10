# Prompt 62: Science of Science

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyR0tmYXBidU43bTJfUFVQay1hbHFRSRIXMkdLZmFwYnVON20yX1BVUGstYWxxUUk
**Elapsed:** 456s

---

# FRONTIER PRACTITIONER DOSSIER

Field: Science of Science

Key Points:
- The fundamental hypothesis that heavy-tailed citation distributions arise purely from structural growth rules (preferential attachment) is settled; a system with zero notion of intrinsic quality will mathematically generate massive inequality simply through cumulative advantage cite: 17, 34.
- However, the purist "scale-free" network paradigm is highly contested. Rigorous statistical tests suggest that purely scale-free networks are empirically rare, and log-normal distributions often fit citation data better than strict power laws cite: 1, 3.
- The frontier of the field has shifted from purely topological network models to semantic and generative models. The urgent open question in 2026 is how Large Language Models (LLMs) and generative search engines alter these structural rules, with early evidence showing they dramatically amplify the "rich-get-richer" effect by over-citing already dominant papers cite: 19, 27, 62.
- The tooling landscape is fractured. The canonical datasets are massive (terabyte-scale), but the standard Python analysis packages often assume the user can fit the dataset into working RAM. You will need to build out-of-core pipelines.

The Science of Science (SciSci) is an interdisciplinary field that uses large-scale bibliometric data to understand the mechanisms of scientific discovery, career trajectories, and the diffusion of knowledge. Historically rooted in the sociology of science and bibliometrics, it underwent a massive quantitative shift over the last two decades, driven by complex systems physicists who modeled science as an evolving network of papers, authors, and institutions. As a computational scientist entering this field, your most powerful leverage will be combining the rigorous network generation models of statistical physics with the modern, massive data lakes that have recently replaced proprietary academic search engines.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The Science of Science today is a mature empirical discipline that operates at the intersection of network science, computational social science, and machine learning. Its primary object of study is the global scientific ecosystem, quantified through massive bibliographic graphs comprising hundreds of millions of nodes (papers, authors, concepts) and billions of edges (citations, co-authorships). The field has transitioned from an era of data scarcity, where researchers relied on small, proprietary Web of Science extracts, to an era of data abundance, driven by open data lakes like OpenAlex and SciSciNet cite: 48, 49.

What is SETTLED: The basic generative mechanisms of inequality in scientific attention are mathematically solved. It is settled that you do not need to invoke "quality" or "merit" to explain why a tiny fraction of papers receive tens of thousands of citations while the vast majority receive almost none. A purely structural stochastic process—where new papers arrive and cite existing papers with a probability proportional to the citations those existing papers already have (preferential attachment or cumulative advantage)—is sufficient to produce heavy-tailed degree distributions cite: 20, 36. It is also settled that to accurately model the lifecycle of a specific paper, one must add two parameters to this base rule: an aging function (because papers eventually become obsolete and stop attracting citations) and a fitness parameter (to account for intrinsic variations in novelty or utility that allow some papers to overcome late entry) cite: 11, 13.

What is CONTESTED: The exact shape of the resulting graphs and the universality of the "scale-free" label. For two decades, the field assumed these networks were strictly scale-free, defined by a pure power-law degree distribution. This is now the site of a major live disagreement. On one side are network science traditionalists (often associated with Albert-László Barabási and the original preferential attachment models) who argue that scale-free dynamics are the universal baseline of science. On the other side are rigorous statisticians and empirical network scientists (most notably Aaron Clauset and Anna Broido) who have demonstrated through severe statistical testing that strict power laws are exceedingly rare in real-world networks, and that citation networks are often better described by log-normal or stretched exponential distributions cite: 1, 3. Furthermore, the exact functional form of preferential attachment—whether it is strictly linear or sublinear—remains contested, with evidence suggesting that when you properly account for node fitness, the structural attachment rule is often sublinear cite: 21, 38.

What is OPEN: The frontier of the field in 2026 is the impact of Artificial Intelligence on the structural dynamics of science. Generative search engines and LLMs are actively changing how scientists discover literature. The open question is whether these tools flatten the citation curve by surfacing obscure but highly relevant papers, or steepen the curve by relying on parametric memory that is biased toward already-famous papers. Early empirical work heavily leans toward the latter, showing that LLMs possess a heightened citation bias that amplifies the Matthew effect cite: 62, 63, 64. Additionally, there is a major push to identify universal dynamics across different human knowledge systems, testing whether the mathematical rules of scientific citations apply identically to patent citations and common law jurisprudence cite: 18, 72. In the last three years, the field has largely absorbed the death of the Microsoft Academic Graph (MAG), migrating entirely to OpenAlex, which has democratized access but shifted the burden of data cleaning onto individual practitioners.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Derek J. de Solla Price
Year: 1976
Title: A general theory of bibliometric and other cumulative advantage processes
Venue: Journal of the American Society for Information Science
Identifier: DOI 10.1002/asi.4630270505
This is the absolute bedrock of the field. Price adapted Polya's urn models to create the Cumulative Advantage Distribution, proving analytically that a simple "success breeds success" stochastic rule generates the heavy-tailed distributions observed in citations, without any need to invoke the intrinsic quality of the papers cite: 32, 34, 36. A practitioner must read this to understand the mathematical origin of the field before it was rebranded as network science.

Authors: Ginestra Bianconi, Albert-László Barabási
Year: 2001
Title: Competition and multiscaling in evolving networks
Venue: Europhysics Letters
Identifier: DOI 10.1209/epl/i2001-00260-6
This paper introduces the Bose-Einstein fitness model, modifying pure preferential attachment by giving each node an intrinsic "fitness" score that multiplies its ability to attract links. It demonstrates the "fitter-gets-richer" phenomenon where latecomers with high fitness can overtake older, highly connected nodes cite: 21, 22. This is the exact mechanism you must implement to separate structural luck from intrinsic quality in a generative experiment.

Authors: James A. Evans
Year: 2008
Title: Electronic Publication and the Narrowing of Science and Scholarship
Venue: Science
Identifier: DOI 10.1126/science.1150473
Evans analyzed 34 million articles to show that as journals moved online, scientists cited fewer distinct articles and heavily favored more recent ones. The efficiency of search engines replaced the serendipity of physical browsing, accelerating consensus and narrowing the range of ideas built upon cite: 52, 56. This is essential reading because it proves that technological shifts in discovery mechanisms directly and measurably alter the topological shape of the citation graph.

Authors: Dashun Wang, Chaoming Song, Albert-László Barabási
Year: 2013
Title: Quantifying Long-Term Scientific Impact
Venue: Science
Identifier: DOI 10.1126/science.1237825
This paper builds the canonical unified mechanistic model of citation dynamics. It combines three parameters: preferential attachment, node fitness, and a log-normal aging function (to ensure papers eventually stop being cited). It proves that this minimal model can collapse the citation histories of papers from different journals and disciplines into a single universal temporal pattern, allowing the prediction of long-term impact from early citation data cite: 11, 13, 20.

CURRENT SOURCES (THE 2026 FRONTIER)

Authors: Anna D. Broido, Aaron Clauset
Year: 2019
Title: Scale-free networks are rare
Venue: Nature Communications
Identifier: DOI 10.1038/s41467-019-08746-5
Using extreme statistical rigor, Broido and Clauset tested nearly 1000 networks and found that only 4 percent exhibit strong scale-free structure, with log-normal distributions often providing a better fit cite: 1, 3. While slightly older than 2023, this is the most critical modern methodological critique in the field and dictates the current frontier of how practitioner evaluates the summary statistics of a generated graph. You must read this so you do not blindly fit power laws to your experimental outputs.

Authors: Zihang Lin, Yian Yin, Lu Liu, Dashun Wang
Year: 2023
Title: SciSciNet: A large-scale open data lake for the science of science research
Venue: Scientific Data
Identifier: DOI 10.1038/s41597-023-02198-9
This paper documents the creation of SciSciNet, the current authoritative data lake that maps 134 million publications to external linkages like funding and patents cite: 48, 50. It details the preprocessing, disambiguation, and filtering steps required to handle modern bibliometric data, serving as the blueprint for any data pipeline you will build.

Authors: Andres Algaba, Carmen Mazijn, Vincent Holst, Floriano Tori, Sylvia Wenmackers, Vincent Ginis
Year: 2025
Title: Large Language Models Reflect Human Citation Patterns with a Heightened Citation Bias
Venue: Findings of the Association for Computational Linguistics
Identifier: arXiv:2405.15739
The authors show that LLMs prompted to suggest citations for scientific abstracts exhibit a massively amplified Matthew effect, disproportionately favoring already highly-cited papers compared to ground-truth human reference lists cite: 62, 65. This defines the absolute bleeding edge of the field: studying how generative AI is structurally mutating the citation graph.

Authors: Sadamori Kojaku, Robert Mahari, Sandro Claudio Lera, Esteban Moro, Alex Pentland, Yong-Yeol Ahn
Year: 2025
Title: Uncovering the universal dynamics of citation systems: From science of science to law of law and patterns of patents
Venue: arXiv
Identifier: arXiv:2501.15552
This paper tests whether the laws of citation (preferential attachment, exponential growth, aging) generalize outside of academic papers by applying the same mechanistic models to U.S. case law and patent networks cite: 18, 72. It represents the frontier methodology for cross-domain validation, proving that citation network dynamics are universal features of formalized knowledge systems, not just quirks of academic sociology.

Authors: Vincent Traag
Year: 2025
Title: Science of science - Citation models and research evaluation
Venue: arXiv
Identifier: arXiv:2207.11116
This is the single best modern survey of the field. Traag rigorously connects generative mathematical citation models to the sociological realities of research evaluation and peer review, while exposing the statistical difficulties in proving that preferential attachment is truly causal rather than an artifact of exponential system growth cite: 17, 20.

PART 3. SOFTWARE I CAN ACTUALLY RUN

pySciSci
URL: https://github.com/SciSciCollective/pyscisci
Language: Python
Licence: MIT
Activity: 2023
Maturity: MAINTAINED
This is the standard community library for the Science of Science, developed by Alexander Gates and the SciSciCollective. It provides a unified API for loading and analyzing major bibliometric databases, calculating standardized metrics like the H-index, disruption index, and Rao-Stirling interdisciplinarity, and preprocessing citation networks cite: 6, 9. 
Experiment it can run: You can use it to ingest raw OpenAlex data, disambiguate authors, and compute the static structural measurements (Gini coefficients, degree distributions) of the true empirical citation graph to serve as the baseline for your generative experiments.
Gotchas: It is entirely built on top of Pandas and keeps entire dataframes in working memory. If you attempt to load the full OpenAlex citation graph (billions of edges) on a standard machine, it will instantly result in an out-of-memory crash cite: 6, 57. You must aggressively filter by field or time window before loading, or port its logic to an out-of-core framework like Dask or Polars.

PAFit
URL: https://cran.r-project.org/package=PAFit
Language: R (with C++ OpenMP backend)
Licence: GPL-3
Activity: 2025
Maturity: MAINTAINED
Written by Thong Pham, this is a spectacular and rigorous package dedicated entirely to the non-parametric estimation of preferential attachment and node fitness in growing complex networks cite: 37, 38. It does not force you to assume a specific mathematical form (like linear preferential attachment); instead, it learns the actual attachment kernel from temporal network snapshots.
Experiment it can run: It contains built-in generative functions like `generate_BB` to simulate the Bianconi-Barabasi fitness model, and `generate_BA` for pure Barabasi-Albert networks cite: 77, 78. You can simulate a graph, and then run its `joint_estimate` function to blindly recover the preferential attachment function and fitness distribution from the simulated time-series data.
Gotchas: Because it tracks the network state at every discrete time step of its growth, the memory complexity scales severely with the number of nodes. It relies on OpenMP for parallelization, which can be notoriously difficult to compile cleanly on modern macOS toolchains without manual compiler flag interventions.

NetworkX
URL: https://networkx.org
Language: Python
Licence: BSD 3-Clause
Activity: 2026
Maturity: MAINTAINED
The absolute standard for general graph manipulation in Python. It is heavily utilized in SciSci for network analysis and rapid prototyping of custom generative models cite: 42, 45.
Experiment it can run: Implementing a custom, bare-bones preferential attachment loop where nodes arrive, calculate degree probabilities, and attach edges. It is useful for verifying small-scale variations of the Wang-Song-Barabasi model.
Gotchas: NetworkX is written in pure Python and is famously slow for large graphs. Running a node-by-node growth simulation for a graph approaching 1 million nodes will bottleneck entirely on single-core Python overhead. It is an evaluation harness, not a production simulation engine. 

igraph
URL: https://igraph.org
Language: C core with Python and R bindings
Licence: GPL
Activity: 2026
Maturity: MAINTAINED
The high-performance alternative to NetworkX. Its C backend allows for massive scale analysis and it includes specific generative games tailored to the science of science.
Experiment it can run: It contains highly specific, optimized functions like `igraph_cited_type_game` and `igraph_barabasi_aging_game` which directly implement preferential attachment combined with vertex aging cite: 46. You can use it to generate massive citation graphs in seconds rather than hours.
Gotchas: The API is highly idiosyncratic and heavily focused on integer indexing. The Python documentation often lags behind the C documentation, requiring you to read C headers to understand exactly how the aging parameters are distributed.

PART 4. DATA AND BENCHMARKS

SciSciNet-V2
URL: https://github.com/EZlzh/SciSciNet
Size: ~100 GB (compressed relational tables)
Licence: MIT
Measurement: The authoritative, pre-cleaned data lake for empirical Science of Science experiments. Originally built on the Microsoft Academic Graph, version 2 is built on OpenAlex. It contains 134 million papers linked to authors, affiliations, grants (NIH/NSF), and patents cite: 48, 49. It provides the exact ground truth for citation networks, author publication sequences, and field classifications. It is explicitly treated as authoritative by the field.
Gotchas: The data is provided as massive static dumps. Normalizing citation counts across different eras and handling the truncation of recent citation counts (the right-censoring problem) is left to the user.

OpenAlex
URL: https://openalex.org
Size: >300 GB (updated continuously)
Licence: CC0
Measurement: The live, raw bibliographic graph of the world. It replaced MAG as the global standard. It measures everything: works, authors, sources, institutions, concepts, and funders. 
Gotchas: OpenAlex is incredibly noisy. Author name disambiguation is an ongoing challenge (two researchers with the same name are frequently merged). Benchmarks built directly on raw OpenAlex data without the cleaning steps described by SciSciNet will suffer from massive entity contamination.

ResearchQA / SciArena
URL: Available via the respective LLM evaluation repositories from recent ACL proceedings.
Size: Tens of thousands of paper abstracts and reference lists.
Licence: Varies (often derived from Semantic Scholar open APIs).
Measurement: Used to measure the citation generation bias of LLMs. They contain the abstract of a focal paper and the ground-truth list of references that the human authors actually cited cite: 30.
Gotchas: Data leakage is a severe problem. Because these datasets are drawn from papers published on arXiv, they are frequently ingested into the training corpora of models like GPT-4o and Claude 3.5. You cannot safely know if an LLM is predicting a citation via its "internal world model" or simply reciting memorized text. Algaba et al. specifically had to filter for papers published after the strict knowledge cut-offs of the models to safely measure systemic bias cite: 64.

Microsoft Academic Graph (MAG)
URL: N/A
Maturity: ABANDONED
Historically the most famous dataset in this field, used to generate almost all breakthrough papers between 2015 and 2021. Microsoft sunset the project at the end of 2021. You will read dozens of foundational papers referencing MAG. You cannot use it today. Any pipeline demanding MAG must be aggressively refactored to consume OpenAlex or SciSciNet.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible, informative, and structurally pure experiment you can run to build tacit knowledge in this field is the non-parametric recovery of the "fitter-gets-richer" mechanism using PAFit on a simulated network. This experiment proves that you can mathematically separate the structural advantage of being early (preferential attachment) from intrinsic quality (fitness).

Software and Version: 
R version 4.3+, using the PAFit package version 1.2.10 (or latest stable) cite: 39.

Dataset/Generator:
The internal `generate_BB` function from PAFit, which simulates the Bianconi-Barabasi model (linear preferential attachment competing with a drawn node fitness) cite: 77, 78.

Parameters to Set:
- N (Total nodes): 100000 (a realistic size for a sub-field citation network).
- m (Edges per new node): 10 (average references per paper).
- num_seed (Initial nodes): 10.
- mode_f (Fitness distribution): "log_normal".
- s (Distribution variance parameter): 10.
These parameters mirror the structural realities of academic publication rates and reference list lengths.

Replicates and Seeding:
Execute 50 independent replicates. Seed the R pseudo-random number generator sequentially from 1 to 50 to ensure exact reproducibility across runs.

Compute Cost:
Generating the graphs is fast. Running the non-parametric `joint_estimate` function on 50 graphs of 100,000 nodes will require approximately 10 to 15 CPU hours on a modern multi-core workstation. It does not use GPUs. It relies heavily on OpenMP threading.

Expected Result:
You will output the estimated attachment function \( A_k \) and the estimated fitness values \( \eta_i \). 
1. The attachment function should fit a nearly perfect linear line \( A_k \approx k \), recovering the pure structural rule.
2. The extracted fitness values \( \eta_i \) should highly correlate with the true fitness values injected by the generator (Pearson correlation > 0.85). 
3. The degree distribution of the final graph should exhibit multiscaling, where the dynamic exponent is strictly dependent on the fitness parameter, perfectly matching the analytical prediction in Bianconi and Barabasi (2001) cite: 21.

Three Most Common Ways People Get This Wrong:
1. Snapshot Bias: Users frequently attempt to estimate the attachment kernel from a single static snapshot of a citation network rather than temporal time-steps. Without longitudinal data showing exactly when edges were formed, the estimation of fitness versus structural advantage is mathematically ill-posed, leading to wildly incorrect sublinear attachment parameters.
2. Time-Window Truncation: In real data, users fail to account for the right-censoring of citations (papers published near the end of the dataset have no time to accumulate citations). In simulations, failing to discard the most recently added nodes before running the estimation artificially depresses the fitness estimates of the newest nodes.
3. Ignoring the Regularization Parameter: The expectation-maximization algorithm in PAFit relies on a regularization parameter to smooth the fitness distribution. Users often skip the cross-validation step (`cv for joint_estimate`) to save compute time, resulting in severe overfitting to structural noise and producing a jagged, nonsensical attachment kernel.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

The field entirely lacks a scalable, out-of-core generative simulation harness that integrates topological growth rules with semantic embeddings (LLM agent behaviors). 

Currently, simulations (like those in NetworkX or PAFit) treat nodes as blank integer IDs. Empirical analyses (like pySciSci) treat nodes as static dataframe rows. If you want to run the frontier experiment—simulating how a scientific field evolves when human scientists are replaced or augmented by LLMs suggesting citations—you must build the engine yourself.

The Interface:
- Input: An OpenAlex Parquet dump of a specific subfield (e.g., all papers in computational biology from 1990 to 2010), containing temporal metadata, abstracts, and true citation edges.
- Input: A set of parameterized agent rules (e.g., Agent A cites based on pure preferential attachment; Agent B cites based on cosine similarity of text embeddings; Agent C queries an open-weights LLM for citation suggestions based on the abstract).
- Output: An evolving synthetic edge list generated step-by-step from 2010 to 2026, alongside the structural summary statistics of the resulting graph (Gini coefficient, maximum degree, clustering coefficient) at each timestep.

The Hard Part:
Graph simulation is inherently sequential. Node 100,000 bases its attachment probabilities on the exact degree state of the graph after Node 99,999 has attached. You cannot trivially vectorize or MapReduce this across a GPU. Furthermore, generating vector embeddings or calling an LLM inference API inside a tightly coupled sequential graph-growth loop is computationally catastrophic. 

Roughly How Much Work It Is:
This is a robust software engineering project requiring 3 to 6 months for a competent computational scientist. You must write a custom Rust or C++ core to handle the topological state tracking in memory, exposing bindings to Python so that asynchronous batched calls can be made to an embedding model or LLM inference server (like vLLM) to determine the semantic targets of the citations.

Signal of a Real Gap:
Multiple groups have recently published papers evaluating LLM citation biases by manually generating thousands of prompts via Python scripts hacking against the OpenAI API and checking semantic similarity via crude fuzzy matching against Semantic Scholar cite: 31, 64. They are all rebuilding slow, brittle, one-off scripts to bridge the gap between semantic AI text generation and rigorous topological graph metrics.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of the Science of Science is littered with methodological corrections, mostly where physicists imported assumptions from statistical mechanics that failed against the sociological realities of academic behavior.

The Scale-Free Myth
The most pervasive standing critique in the field is that the obsession with "scale-free" networks (pure power-law degree distributions) was a theoretical aesthetic rather than an empirical reality. For nearly twenty years, it was standard practice to plot a degree distribution on a log-log scale, fit a straight line via ordinary least squares, and declare the network scale-free. This methodology is now considered completely discredited.
Broido and Clauset (2019) delivered the fatal blow by applying likelihood-ratio tests to compare power-law fits against log-normal and stretched exponential alternatives cite: 1, 3. They found that for the vast majority of social and biological networks, a log-normal distribution fits the data statistically significantly better. This means that while citations are vastly unequal (heavy-tailed), they are not strictly scale-free. The critique was initially met with fierce resistance from the Barabasi camp, but the methodological standard has permanently shifted. Today, if you claim your generative model produces a power law, you are expected to prove it using maximum likelihood estimation and Kolmogorov-Smirnov goodness-of-fit tests, not just a line on a log-log plot.

The Illusion of Linear Preferential Attachment
A massive, ongoing critique detailed by Traag (2025) targets the foundational mechanism itself. Preferential attachment assumes that a new paper directly measures the degree of older papers and cites them proportionally cite: 17, 20. However, Traag and others point out that you can generate the exact same macroscopic linear growth curve simply through exponential system growth combined with random recursive referencing (e.g., citing a paper, and then randomly citing one of that paper's references). In this regime, highly cited papers get cited more simply because they appear on more reference lists, acting as a redirection mechanism. Therefore, measuring linear preferential attachment at the macro level does not prove that individual scientists are actually making decisions based on accumulated citations. This critique remains partially unanswered, which is why mechanistic models now rely heavily on adding "fitness" parameters to account for unobservable quality.

The Narrowing of Science
In 2008, James Evans hypothesized that the digitization of science would democratize knowledge and broaden the citation graph. The actual result was a spectacular failure of the democratization hypothesis. Evans proved that the transition to online databases actually narrowed science: researchers cited fewer unique articles and heavily favored recent, already-popular papers cite: 52, 53, 56. The efficiency of search algorithms bypassed the serendipity of physical browsing. Critics like Lariviere initially argued this was a transient phenomenon, suggesting that as online archives deepened, older literature would see a resurgence cite: 67. However, the core finding stands: algorithmic mediation of search steepens the inequality of the citation distribution. 

Citation Normalization Failures
Early attempts to measure scientific impact globally failed because citation practices vary wildly by field (biology papers cite 50 references; mathematics papers cite 10). Attempts to solve this by dividing by the field average (e.g., the Mean Normalized Citation Score) often fail because defining the boundaries of a "field" is subjective and fluid. Methods that looked strong were shown to be measuring the artifacts of the classification system (like Web of Science subject categories) rather than true phenomena. The current standard is to use network-based normalization, where impact is scaled relative to the immediate topological neighborhood of the paper, bypassing arbitrary human-defined categories entirely.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the state of the field, the unique capabilities of 2026, and the available open data lakes, a well-resourced newcomer should bypass purely topological model-fitting and aim directly at the intersection of AI, semantic search, and network dynamics.

1. The Generative Citation Intervention Experiment (Rank 1)
Experiment: Build a closed-loop simulation where a citation network is grown from 1990 to 2010 using empirical data from SciSciNet. Then, from 2010 onward, generate the arrival of new nodes where the attachment targets are selected not by a mathematical preferential attachment formula, but by querying an open-weights LLM (e.g., Llama 3) with the abstract of the new paper. 
Feasibility: Feasible now due to cheap, localized LLM inference (vLLM) and massive open datasets (OpenAlex/SciSciNet).
Measurement: Measure the Gini coefficient and the power-law alpha parameter of the resulting LLM-driven graph versus a standard Barabasi-Albert growth graph and the true empirical graph. 
Falsification: If the LLM-driven graph exhibits a lower Gini coefficient (more equality) than the empirical graph, the idea that LLMs inherently amplify the Matthew effect via parametric memory is falsified.

2. Disentangling Content Fitness from Topological Advantage (Rank 2)
Experiment: Replicate the Bianconi-Barabasi fitness model, but instead of drawing random hidden fitness parameters from a log-normal distribution, calculate the true empirical semantic novelty of every paper (using vector embeddings of their full text) upon publication. Inject these empirical novelty scores into the PAFit estimation harness as the known fitness parameter, and see if the residual structural preferential attachment drops to zero.
Feasibility: Full-text embeddings for millions of open-access papers are now cheaply available or pre-computed in databases like OpenAIRE.
Measurement: The statistical variance in citation counts explained by semantic novelty versus topological luck. 
Falsification: If the estimated preferential attachment parameter remains strongly linear even when full semantic text novelty is accounted for, it proves that structural advantage (the rich-get-richer effect) dominates intrinsic paper content.

3. Cross-Domain Universal Disruption (Rank 3)
Experiment: The "disruption index" (a measure of whether a paper eclipses its predecessors or bridges them) is highly popular in SciSci. Apply the exact calculation of the disruption index to the entire U.S. Case Law citation network and the USPTO patent network to see if the decline of disruptive science over the last century is a universal feature of all human knowledge systems or specific to academic publishing.
Feasibility: Massive, structured legal and patent citation graphs have recently been formatted into compatible standards cite: 18, 72.
Measurement: The temporal slope of the average disruption index from 1950 to 2020 across three separate domains.
Falsification: If patent disruption is rising while scientific disruption is falling, the hypothesis of universal knowledge stagnation is falsified.

What Will NOT Work
Attempting to predict the exact citation count of an individual paper using deep learning graph neural networks (GNNs). This has been tried endlessly by machine learning entrants to the field. It fails reliably. Because the underlying generative process of citations is a heavy-tailed stochastic process dominated by initial conditions and random early attachments (luck), the variance of individual node outcomes is mathematically unbounded. You can predict the macroscopic summary statistics of the graph perfectly; you cannot reliably predict the micro-level success of a single node. Focusing on structural statistics, rather than individual prediction, is the only way to run rigorous experiments in the Science of Science.
