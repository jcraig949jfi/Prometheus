# Prompt 58: Computational Philosophy of Science

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoV0dmYXJYZEZjaWRfdU1QNXE2WHNBcxIXaFdHZmFyWGRGY2lkX3VNUDVxNlhzQXM
**Elapsed:** 334s

---

FRONTIER PRACTITIONER DOSSIER
Field: Computational Philosophy of Science

Your description of the target method is historically precise but mathematically outdated. You have accurately described Explanatory Coherence (TEC) and its canonical connectionist implementation, ECHO, exactly as Paul Thagard introduced them in 1989 (cite: 11). The parallel constraint satisfaction network, the symmetric excitatory links for explanation, the inhibitory links for contradiction, and the always-on data unit are all correct. 

However, a critical correction is required for a practitioner in 2026. The field no longer treats this as a connectionist settling problem. It is now formally recognised that ECHO's algorithm is a heuristic solver for a specific combinatorial optimisation problem: MAX-CUT on a signed graph (cite: 17), or equivalently, finding the ground state of an Ising model in statistical mechanics (cite: 20). The connectionist update rule you described is notoriously sensitive to node update order and cycle budgets, and it frequently gets trapped in local minima. Today, the frontier does not use the connectionist settling rule. Instead, the exact same epistemic problem is solved either by mapping the propositions to an Ising model and calculating the partition function (cite: 35), or by passing the signed graph to exact MAX-SAT/MAX-CUT solvers (cite: 17). 

Here is the concrete operational intelligence you need to begin building in this space.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Computational Philosophy of Science currently sits at the intersection of cognitive science, formal epistemology, and neurosymbolic artificial intelligence. Historically, the field was dedicated to building formal, computational models of how scientists choose between competing theories. For nearly two decades, the field was largely dormant, having been intellectually outcompeted by Bayesian causal networks, which absorbed the probability-minded researchers. However, the last three years (2023 to 2026) have seen a massive revival driven by two factors: the mathematical mapping of coherence networks to Ising models, which allows for rigorous statistical evaluation without connectionist artefacts (cite: 20), and the rise of Large Language Models (LLMs), which solve the field's oldest bottleneck by automatically extracting propositional graphs from raw scientific text (cite: 17).

What is SETTLED is that classical connectionist settling (the original ECHO algorithm) is dead as a computational tool. It is mathematically inferior to modern exact solvers for the same graph topologies (cite: 17). What is CONTESTED is the optimal mathematical substrate for coherence. One camp, led by researchers in psychological methods (e.g., Maier, Borsboom), models coherence as an Ising model where theories are evaluated based on their thermodynamic energy landscapes (cite: 20). The other camp, led by applied mathematicians and AI researchers (e.g., Huntsman), treats it as Coherence-Driven Inference (CDI) via signed graphs and weighted simplicial complexes (cite: 25). What is OPEN is the automated synthesis of these graphs at scale. The frontier right now is neurosymbolic: using LLMs as "System 1" to read thousands of papers and output a signed graph of propositions, and using CDI/Ising solvers as "System 2" to mechanically deduce the most coherent global theory (cite: 24). 

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Thagard, P.
1989
Explanatory coherence
Behavioral and Brain Sciences
DOI 10.1017/S0140525X00057046
This is the foundational text of the entire field. It introduces the seven principles of explanatory coherence and the original ECHO connectionist model that your query is anchored to (cite: 11). 

Thagard, P., and Verbeurgt, K.
1998
Coherence as constraint satisfaction
Cognitive Science
DOI 10.1207/s15516709cog2201_1
This paper is mathematically load-bearing. It bridges the gap between philosophy and computer science by formally proving that the explanatory coherence problem is an instance of MAX-CUT, establishing its NP-hard complexity (cite: 32).

Pearl, J.
1988
Probabilistic reasoning in intelligent systems: networks of plausible inference
Morgan Kaufmann
ISBN 9781558604791
While not an ECHO paper, this is the foundational text for the Bayesian network approach that successfully absorbed much of this field (cite: 9). A practitioner must read it to understand the probabilistic alternative to coherence-driven constraint satisfaction.

CURRENT FRONTIER SOURCES

Maier, M., van Dongen, N., and Borsboom, D.
2023
Comparing theories with the Ising model of explanatory coherence
Psychological Methods
DOI 10.1037/met0000543
This paper defines the modern methodological frontier for the Ising-model camp. It replaces the outdated connectionist network with statistical mechanics, providing a rigorous, reproducible way to compare real scientific theories rather than toy historical examples (cite: 20).

Huntsman, S., Robinson, M., and Huntsman, L.
2024
Prospects for inconsistency detection using large language models and sheaves
arXiv:2401.16713
This establishes the topological and sheaf-theoretic approach to coherence. It is crucial for understanding how modern researchers are upgrading simple signed graphs to weighted simplicial complexes to capture multi-proposition trilemmas (cite: 24).

Huntsman, S., and Thomas, M.
2025
Benchmarking Coherence-Driven Inference
arXiv:2502.13953
This is the absolute bleeding edge of the neurosymbolic integration. The authors generate synthetic signed coherence graphs and benchmark the ability of frontier LLMs (like GPT-4o and o1) to extract the propositions and reconstruct the graph for downstream MAX-CUT solving (cite: 17). 

Wadden, D., et al. (or associated authors of sciwrite-lint)
2026
sciwrite-lint: Verification Infrastructure for the Age of Science Vibe-Writing
arXiv:2604.08501
This paper represents the applied engineering frontier. It details a computational pipeline that uses coherence-like principles and LLM adjudication to verify claim support and citation integrity across scientific manuscripts at writing time (cite: 45).

Spanhol, F., et al.
2026
An integrated explainability-augmented deep learning framework for binary histopathological classification
Frontiers in Medicine (Imaging)
DOI 10.3389/fimag.2026.1846414
This shows the migration of explanatory coherence into machine learning evaluation. The authors create an Explanatory Coherence Score (ExpiScore) by mathematically aggregating outputs from SHAP, Grad-CAM, and LIME into a single coherence metric (cite: 18).

PART 3. SOFTWARE I CAN ACTUALLY RUN

IMEC (Ising Model of Explanatory Coherence)
https://cran.r-project.org/web/packages/IMEC/index.html
R
GPL-3 (UNCONFIRMED specific version, open source on CRAN)
2024
MAINTAINED
This is the community standard for modern, serious experiments in this field (cite: 35). It implements the Ising model translation of explanatory coherence. Today, you can run exact comparisons of competing psychological or biological theories by defining their nodes and edges in a matrix. Gotchas: It is written in R, which limits easy integration if your surrounding infrastructure is built in Python.

JavaECHO_command_line
https://github.com/russellcameronthomas/JavaECHO_command_line
Java
MIT
2020
DORMANT
This is an updated, stripped-down command-line version of Thagard's canonical 1992 JavaECHO applet (cite: 49). It executes the original connectionist parallel constraint satisfaction algorithm. Gotchas: The repository owner explicitly notes that the command-line arguments are broken in the latest commit (cite: 40). You will have to fork it and fix the argument parser to pass your own data files.

echo (by tjd)
https://github.com/tjd/echo
Java
AGPL-3.0
2018
ABANDONED
A direct source-code commit of the old Waterloo Java applet. Unbuildable on modern toolchains without significant dependency wrangling. Listed here strictly so you know to avoid it, despite it appearing in search results (cite: 41).

ConnectionistSudoku
https://github.com/MaxRae/ConnectionistSudoku
Python
License UNKNOWN
2018
ABANDONED
An attempt to use ECHO in Python to solve Sudoku via parallel constraint satisfaction. Famous in niche circles but effectively dead (cite: 48). Published results rely on obsolete Python 2/3 transition environments.

Huntsman CDI Benchmarking Code
URL UNCONFIRMED
Python
License UNCONFIRMED
2025
DORMANT / PENDING
The codebase for the 2025 arXiv:2502.13953 paper. The authors state they "plan to release code and data in the coming weeks" (as of February 2025). When released, this will be the canonical reference implementation for evaluating LLM-driven coherence extraction on signed graphs (cite: 17). 

PART 4. DATA AND BENCHMARKS

Mutualism vs. Common Cause Intelligence Dataset
https://osf.io/shaef
Size: 16 nodes (8 phenomena, 8 hypotheses), ~30 edges.
License: CC-BY 4.0 (via OSF)
Used to measure the explanatory coherence of the two dominant theories of human intelligence. This is the authoritative modern dataset for testing Ising-model coherence (IMEC). It is highly curated and serves as the standard sanity check for new solvers (cite: 35). 

Huntsman Signed Coherence Graphs Benchmark
Access route: UNCONFIRMED (Pending release alongside the 2025 paper)
Size: N=30 coherence graphs per consensus median, spanning various sparsity levels.
License: UNCONFIRMED
This is the new authoritative benchmark for the neurosymbolic frontier. It measures the fidelity with which an LLM can read natural language propositions and correctly output the adjacency matrix of the underlying signed coherence graph (cite: 17). Known limitation: currently relies on synthetic generated propositions where logical consistency is strictly unambiguous, which does not generalise perfectly to messy, contradictory human scientific literature (cite: 25).

Thagard's Historical Cases Archive
Access route: Embedded within the JavaECHO_command_line repository data files.
Size: Tiny (typically 10 to 30 nodes).
License: MIT
Used to measure historical theory replacement (e.g., Lavoisier's Oxygen vs. Phlogiston; Darwin vs. Creationism). Note: The field completely treats these as saturated, heavily overfitted toy datasets. They are known to be solved in a way that does not generalise, because the manual encoding was specifically designed by the author to guarantee that Darwin and Lavoisier win (cite: 11).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in the modern field is Maier, van Dongen, and Borsboom's adjudication between the "Mutualism" and "Common Cause" theories of intelligence using IMEC (cite: 35).

Software and Version: R version 4.1.2 (or higher), IMEC package version 0.2.0.
Dataset: The intelligence theory matrix provided in Table 1 of the IMEC documentation/preprint (cite: 53).
Parameters: 
- Node thresholds (representing empirical evidence) for E1 through E8 are set to +1.0. 
- Explanatory links (blue edges) are assigned a positive weight (e.g., +1.0). 
- Contradictory links (red edges) are assigned a negative weight (e.g., -1.0). 
Replicates and Seeding: Because the Ising model partition function for a graph of 16 nodes can be calculated exactly, no seeding regime or independent stochastic replicates are required. The energy landscape is deterministic.
Compute Cost: Less than 1 minute of CPU time on a standard laptop.
Expected Result: The Mutualism theory yields an explanatory coherence score of 0.788 (bounded between 0 and 1). The Common Cause theory yields a significantly lower score, falsifying the hypothesis that a latent general factor (g) provides a more coherent explanation of the positive manifold phenomenon (cite: 35).

Three most common ways people get this experiment wrong:
1. Treating phenomena as hypotheses. Users often fail to fix the external thresholds of evidence nodes (E1-E8) to +1.0, allowing the network to reject reality if it contradicts a strongly connected theoretical cluster.
2. Failing to normalise for theory complexity. If the partition function is not properly penalised for the number of auxiliary assumptions, a theory that hallucinates a new hypothesis for every data point will artificially inflate its score.
3. Ignoring the default parameters of the connectionist legacy. If someone attempts to reproduce this using old JavaECHO instead of IMEC, the decay rate and excitation multipliers will cause the network to oscillate and fail to settle, producing irreproducible acceptance thresholds.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

What is missing, and what a serious entrant must build, is an end-to-end Python pipeline that natively bridges natural language scientific literature and exact combinatorial solvers. Currently, researchers use LLMs in isolated scripts, manually clean the output, and pass it to R (IMEC) or standalone SAT solvers.

You will need to build the "Neurosymbolic Coherence Compiler".
Interface In: A directory of raw PDF scientific papers or text files representing a specific domain debate (e.g., dark matter vs. MOND).
Interface Out: A fully resolved weighted simplicial complex (or signed adjacency matrix) and a boolean array of accepted/rejected hypotheses.
The Hard Part: Entity resolution and cross-paper grounding. If Paper A proposes Hypothesis X, and Paper B proposes Hypothesis Y, the LLM must correctly determine if X and Y are identical, synergistic, or contradictory, and assign the appropriate edge weight. Furthermore, you must write a custom PyTorch-accelerated MAX-CUT / Ising solver to evaluate the graph, because no maintained, pip-installable Python library exists solely for Explanatory Coherence.
Work Estimate: 4 to 6 months of intense engineering for a solo computational scientist.
Gap Signal: Huntsman's group (2024/2025) and Wadden's group (2026) have both privately built partial versions of this pipeline (LLM extraction to graph algorithms) for their respective benchmarks (cite: 17, cite: 45), proving this is the exact tooling gap everyone is currently trying to cross.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The field is scarred by several standing critiques and failed paradigms that you must navigate.

The Bayesian Critique (Never fully answered):
Led by Judea Pearl and other probabilistic pioneers, the standard critique is that coherence networks rely on arbitrary, ad-hoc link weights (e.g., +1 for explanation, -1 for contradiction) that lack any normative probabilistic interpretation (cite: 9). Bayesians argue that theory choice should strictly follow Bayes' rule using prior probabilities and likelihoods. Thagard answered this by arguing that for truly novel scientific theories, prior probabilities simply do not exist and cannot be meaningfully estimated (cite: 45). The critique was never formally resolved; the fields simply bifurcated, with Bayesians dominating machine learning and coherence surviving in cognitive modelling.

The Echo Chamber / Hypercoherence Artefact (Confirmed):
Recent work has shown that coherence networks inherently produce confirmation bias (cite: 47). If a network possesses a tightly clustered, highly coherent set of prior beliefs, introducing a contradictory piece of evidence will result in the network driving the activation of the evidence node to negative. In other words, the algorithm "rejects" empirical data to preserve theoretical harmony. While this is an excellent model of human psychological flaws (e.g., radicalisation, conspiracy theories), it fundamentally compromises the method as an objective automated tool for scientific truth-seeking unless evidence nodes are hard-locked with massive external data-priority weights (cite: 43).

The Manual Encoding Artefact (Standing Critique):
The most devastating methodological critique of the pre-2023 field was that the method measured the programmer's historical bias, not the theory's objective truth. Thagard's famous simulations of the Darwinian and Chemical revolutions were meticulously hand-coded. Critics pointed out that whoever decides what counts as a "proposition" and whether a link is "explanatory" or "contradictory" predetermines the winner. This critique went unanswered for 30 years until the recent Huntsman benchmark (2025), which attempts to remove the human by using LLMs for objective proposition extraction (cite: 24).

The Intractability Problem (Answered via modern solvers):
Thagard and Verbeurgt (1998) mathematically proved that calculating maximum coherence is NP-hard. For years, critics like van Rooij (2012) argued that the model could not scale to real scientific domains because connectionist settling would fail in the massive energy landscapes of real science (cite: 32). This critique has been answered: while exact solutions remain NP-hard, the mapping of the problem to statistical mechanics (IMEC) and the use of modern semidefinite programming or simulated annealing allows for near-optimal approximation even on large graphs (cite: 17).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you want to run frontier experiments starting today, here is what you should build and measure, ranked by impact.

1. Automated Adjudication of a Live Scientific Dispute
What to do: Do not re-run historical cases. Take a live, messy, unresolved scientific dispute (e.g., the Amyloid vs. Tau hypothesis in Alzheimer's, or String Theory vs. Loop Quantum Gravity). Feed the abstracts of the last 1,000 papers into an LLM (using the CoT extraction prompts from Huntsman 2025) to generate a massive signed coherence graph. Run a MAX-CUT / Ising solver over it to see which theory the global topology actually favours.
Why it is feasible now: LLM context windows (200k+ tokens) and reasoning capabilities (o1-tier) can now accurately map natural language to formal propositional logic, removing the manual encoding bottleneck (cite: 17).
What it measures: The objective structural coherence of competing research programmes at scale.
Falsification: If the winning theory flips wildly when you change the random seed of the LLM prompt, or if changing the LLM from Claude to GPT inverts the graph topology, the entire neurosymbolic extraction pipeline is falsified as an artefact of prompt sensitivity.

2. Real-Time Coherence Linting at the Manuscript Level
What to do: Reimplement and scale the concepts behind sciwrite-lint (cite: 45). Build a pipeline that takes a single draft manuscript, extracts its internal claims and its citation graph, and computes an "Internal Explanatory Coherence Score" based on whether the cited evidence logically excites or inhibits the claims.
Why it is feasible now: Fast local LLMs and open-source citation databases (OpenAlex, Semantic Scholar) allow for graph traversal in seconds.
What it measures: The structural integrity and non-contradiction of a single paper before submission.
Falsification: If the tool assigns high coherence scores to known retracted or fraudulent papers, the network weights are capturing rhetorical flow rather than logical explanation.

What will NOT work:
Do not attempt to write a faster connectionist parallel constraint satisfaction solver in C++ or CUDA to run classical ECHO on millions of nodes. It will not work. The connectionist update rule is fundamentally flawed for large-scale optimisation; it will shatter into local minima and fail to settle within the cycle budget. The field has moved to formal Ising models and SAT solvers for a reason. Do not resurrect the 1989 algorithm; steal the 1989 epistemology and execute it with 2026 mathematics.
