# Prompt 49: Computational Models of Scientific Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcwMXlmYW9ENEE4bXhfUFVQNm9xSmlRSRIXMDF5ZmFvRDRBOG14X1BVUDZvcUppUUk
**Elapsed:** 365s

---

FRONTIER PRACTITIONER DOSSIER
Field: Computational Models of Scientific Discovery

WHO IS ASKING AND WHY

You have asked how to navigate the modern frontier of computational scientific discovery, specifically anchoring on a method that discovers quantitative laws of nature from tabular data using mechanical rules over derived terms. 

Before proceeding to the structured report, a critical correction must be made regarding your description of the mechanism. The specific recursive algorithm you described—building ratios and products iteratively and searching for a constant term within a tolerance limit—is an exact description of the BACON system, primarily BACON.1 through BACON.3, developed by Pat Langley, Herbert Simon, and colleagues between 1979 and 1987 (cite: 24, 38). 

Your description is historically accurate but practically outdated. BACON is no longer the frontier. The specific heuristic loop you described scales exponentially with the number of variables and is notoriously fragile to the observational noise present in real continuous data. Consequently, pure heuristic search over tabular columns has been absorbed into a broader field known as Symbolic Regression (SR). The essential point of searching over derived expressions rather than fitting a pre-chosen functional form remains the foundational philosophy of the field. However, the modern frontier mechanism does not recursively build columns to find a constant. Instead, it represents mathematical expressions as tree structures and navigates the vast, NP-hard search space using Multi-Population Genetic Programming, Reinforcement Learning, and Neural-Guided modularity (cite: 36, 102). Modern systems optimize a Pareto front that balances predictive accuracy against expression complexity (Occam's razor), rather than halting when a constant term is found (cite: 84).

The report below maps the transition from those foundational heuristics to the actual 2026 frontier.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of Computational Models of Scientific Discovery is currently organized around Symbolic Regression and Neural-Symbolic AI. It seeks to automate the extraction of interpretable, closed-form mathematical equations from empirical data. In recent years, the field has aggressively expanded beyond simple curve-fitting to incorporate physical constraints (like dimensional analysis), automated theorem proving (to verify equations against background axioms), and the symbolic distillation of deep neural networks (where black-box models are replaced by interpretable equations). 

What is SETTLED: It is now an established consensus that genetic programming-based symbolic regression outperforms standard black-box machine learning methods (like Random Forests or Gradient Boosting) on tabular physical data when both prediction accuracy and model interpretability are required. The community standard benchmark, SRBench, has conclusively shown that SR methods are the state of the art for these specific physics-based and real-world tabular tasks (cite: 59, 93). It is also settled that pure deep learning models struggle to learn conservation laws naturally; they require explicit constraints or symbolic distillation to yield physically meaningful forces (cite: 71, 86).

What is CONTESTED: The role of Large Language Models (LLMs) as autonomous scientists is highly contested. In the last two years, platforms like Sakana's AI Scientist have claimed to automate the entire research lifecycle, but experimental robustness is fiercely debated. Critics have demonstrated that LLM-based autonomous agents frequently hallucinate numerical results, fail to execute basic code reliably, and rely on superficial keyword matching rather than semantic synthesis (cite: 64, 67). Furthermore, the capability of LLMs to perform genuine equation discovery is contested; recent evaluations show that LLMs have merely memorized historical equations. When standard physics benchmarks are mathematically transformed to prevent memorization, LLM accuracy drops to approximately 31.5 percent (cite: 54, 57).

What is OPEN: The seamless integration of symbolic regression with automated logical reasoning remains open. While systems like AI-Descartes can verify if a data-driven equation complies with background theories (like conservation of energy), the background axioms currently have to be manually encoded by human domain experts in formal logic languages. Automating this abductive reasoning step to close the gap between raw data, missing theory, and final law is the current frontier (cite: 43, 96).

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Langley, P.
Year: 1979
Title: Rediscovering Physics with BACON.3
Venue: International Joint Conference on Artificial Intelligence
Identifier: DOI 10.3390/app9142899 (for recent retrospective context, original is historically archived)
The foundational text defining the exact method you described. It establishes the philosophy of data-driven computational discovery, even though its specific continuous-ratio heuristics were later abandoned for genetic programming (cite: 21, 23, 24).

Authors: Schmidt, M., and Lipson, H.
Year: 2009
Title: Distilling Free-Form Natural Laws from Experimental Data
Venue: Science
Identifier: DOI 10.1126/science.1165893
This is the load-bearing paper that modernized the field. It introduced the principle of identifying nontriviality by searching for invariants in motion-tracking data without prior physical knowledge, discovering Hamiltonians and Lagrangians using evolutionary symbolic regression (cite: 84, 85).

Authors: Udrescu, S. M., and Tegmark, M.
Year: 2020
Title: AI Feynman: A physics-inspired method for symbolic regression
Venue: Science Advances
Identifier: DOI 10.1126/sciadv.aay2631
This paper introduced neural-network-guided symbolic regression. It uses neural networks to detect hidden simplicity like symmetry and separability, breaking harder multidimensional problems into simpler ones, solving the 100 equations of the Feynman benchmark (cite: 79, 82).

CURRENT FRONTIER SOURCES (2023-2026)

Authors: Cranmer, M.
Year: 2023
Title: Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl
Venue: arXiv
Identifier: arXiv:2305.01582
The definitive paper on PySR, the current community standard software. It explains the multi-population evolutionary algorithm and the unique evolve-simplify-optimize loop used to find unknown scalar constants in newly discovered expressions (cite: 99, 102).

Authors: Cornelio, C., Dash, S., Austel, V., et al.
Year: 2023
Title: Combining data and theory for derivable scientific discovery with AI-Descartes
Venue: Nature Communications
Identifier: DOI 10.1038/s41467-023-37236-y
This paper represents the frontier of combining symbolic regression with logical theorem proving. It shows how to discover governing laws from very few data points by using background axioms to filter out equations that fit the data but violate physical laws (cite: 94, 98).

Authors: de Franca, F. O., Virgolin, M., Kommenda, M., et al.
Year: 2024
Title: SRBench++: Principled Benchmarking of Symbolic Regression with Domain-Expert Interpretation
Venue: IEEE Transactions on Evolutionary Computation
Identifier: DOI 10.1109/TEVC.2024.3423681
The most authoritative survey and benchmark methodology paper in the field today. It evaluates 12 modern algorithms and defines how the field currently measures success beyond simple error metrics, incorporating domain-expert interpretations (cite: 59, 89).

Authors: Shojaee, P., Nguyen, N. H., Meidani, K., et al.
Year: 2025
Title: LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models
Venue: arXiv / ICML 2025
Identifier: arXiv:2504.10415
Crucial reading for understanding the limits of LLMs. It proves that frontier LLMs rely on memorization to discover equations and introduces transformed datasets where state-of-the-art models fail, establishing a new rigorous benchmark (cite: 54, 55).

Authors: Tan, E. S. Z., Soubki, A., Cranmer, M.
Year: 2026
Title: SymTorch: Symbolic Distillation of Neural Networks
Venue: arXiv
Identifier: arXiv:2602.21307
Defines the cutting edge of integrating symbolic regression natively into PyTorch to distill exact physical laws and PDE solutions from trained neural networks, replacing black-box components with interpretable mathematical equations (cite: 69, 71).

Authors: Beel, J., Kan, M. Y., Baumgart, M.
Year: 2025
Title: Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results, and a Promising Future?
Venue: arXiv
Identifier: arXiv:2502.14297
A mandatory skeptical reading on autonomous AI research agents. It meticulously documents the 42 percent failure rate, coding errors, and hallucinated data produced by the highly publicized AI Scientist system (cite: 64, 67).

PART 3. SOFTWARE I CAN ACTUALLY RUN

PySR
URL: https://github.com/astroautomata/PySR
Language: Python (frontend) and Julia (backend via SymbolicRegression.jl)
Licence: Apache License 2.0
Recent Activity: 2026
Maturity: MAINTAINED
This is the community standard that most people actually use today. PySR version 2.0.0 (released in 2025/2026) is a highly modular framework that compiles user-defined operators into SIMD kernels at runtime. It can run everything from standard tabular symbolic regression to extracting interaction forces from graph neural networks. Gotchas: Extreme values or unconstrained dimensional analysis can crash the Julia workers with "DomainError with Inf" (cite: 45). Installation requires careful alignment of Julia and Python paths, though recent updates bypass environment activation delays.

SRBench
URL: https://github.com/cavalab/srbench
Language: Python and Docker
Licence: MIT License
Recent Activity: 2026
Maturity: MAINTAINED
This is the authoritative benchmark harness for the field. You can run 25 different symbolic regression algorithms in a standardized, containerized way against hundreds of datasets. It is highly recommended to use their Docker installation route (DOCKER_BUILDKIT=0 docker build . -t srbench). Limitations: It is an evaluation harness, not a discovery tool. You use this to prove your new algorithm beats PySR, not to run PySR on your private lab data (cite: 49, 52).

AI-Descartes
URL: https://github.com/IBM/AI-Descartes
Language: Python and Java
Licence: MIT License
Recent Activity: 2023
Maturity: DORMANT
This is the reference implementation for combining symbolic regression with deductive reasoning. It can run the Kepler's Third Law experiment using background theory. Gotchas: It is notoriously difficult to set up. It requires KeYmaera X (a theorem prover) and a free license of the WolframEngine/Mathematica to achieve the published results. Using the open-source Z3 solver instead of Mathematica significantly degrades performance and fails to prove most conjectures (cite: 112). 

SymTorch
URL: IDENTIFIER UNKNOWN (Installed via pip install torch-symbolic in the paper)
Language: Python
Licence: MIT License UNCONFIRMED
Recent Activity: 2026
Maturity: MAINTAINED
A newly released framework that wraps PyTorch modules, caches input-output behavior during forward passes, and replaces neural network layers with symbolic equivalents generated by PySR. It is used to accelerate LLM inference or extract PDEs from Physics-Informed Neural Networks. Gotchas: Still early in its lifecycle; memory management during the CPU-GPU transfer phase of symbolic distillation can be a bottleneck (cite: 71, 73).

The AI Scientist
URL: https://github.com/SakanaAI/AI-Scientist
Language: Python
Licence: Apache License 2.0 UNCONFIRMED
Recent Activity: 2026
Maturity: MAINTAINED
An open-ended autonomous discovery agent that brainstorms ideas, writes code, runs experiments, and writes LaTeX papers. You can run it today to generate a $15 research paper. Gotchas: It is explicitly warned by the authors to run in a highly restricted sandbox because it spawns processes and executes LLM-generated code. As documented by independent evaluators, it frequently hallucinates numerical results and suffers from severe code-execution failures (cite: 104, 106).

Eureqa
URL: IDENTIFIER UNKNOWN
Language: C++
Licence: Proprietary
Recent Activity: 2017
Maturity: ABANDONED
Historically famous as the software from the 2009 Schmidt and Lipson paper. It is effectively dead for academic research. It was commercialized, acquired by DataRobot, and integrated into their enterprise platform. The community has completely migrated to PySR as the open-source replacement (cite: 32, 48).

PART 4. DATA AND BENCHMARKS

Penn Machine Learning Benchmarks (PMLB)
URL: https://github.com/EpistasisLab/pmlb
Size: 179 classification and 271 regression datasets
Licence: MIT License
This is the standard repository of tabular data used by SRBench. It standardizes datasets from the UCI ML repository and OpenML. It is used to measure generalized predictive accuracy of symbolic regression against black-box machine learning methods (cite: 114, 117).

Feynman Symbolic Regression Benchmark
URL: https://space.mit.edu/home/tegmark/aifeynman.html
Size: 100 to 120 equations
Licence: MIT License UNCONFIRMED
Compiled by Udrescu and Tegmark, this contains equations from the Feynman Lectures on Physics. It is treated as authoritative for measuring whether an algorithm can rediscover exact, dimensionally consistent physical laws. Known problems: It is heavily saturated. Most modern algorithms achieve near 100 percent exact recovery on the noiseless versions, and Large Language Models have completely memorized it, rendering it useless for evaluating LLM reasoning (cite: 32, 54).

LLM-SRBench
URL: https://github.com/deep-symbolic-mathematics/llm-srbench
Size: 239 problems
Licence: MIT License
Created in 2025 specifically to address the contamination of the Feynman benchmark. It contains LSR-Transform (Feynman equations mathematically manipulated to isolate input features as target variables) and LSR-Synth (synthetic terms added to known physical laws). Used to measure true symbolic reasoning in LLMs versus mere text memorization. (cite: 54, 58).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to establish a baseline in this field is to rediscover Kepler's Third Law (Feynman equation I.15.1) from noisy data using PySR, while enforcing dimensional analysis constraints.

Exact Software and Version:
Python 3.10+, Julia 1.10+.
PySR version 2.0.0.

Dataset:
The Feynman Symbolic Regression Benchmark dataset for Equation I.15.1. The data provides variables for the mass of the sun, the mass of the planet, the distance, and the period.

Parameters:
maxsize: 30 (the default was raised from 20 in recent PySR versions).
parsimony: 0.001 (multiplicative factor punishing complexity).
dimensional_constraint_penalty: 1000.0 (an additive penalty if the expression fails dimensional analysis).
X_units: Passed as an array corresponding to the input columns (e.g., mass, distance).
y_units: Passed as the unit for the target variable (period).

Replicates and Seeding:
40 independent runs with different random seeds.

Compute Cost:
Negligible for a single tabular equation on modern hardware. Under 1 CPU hour.

Expected Result:
PySR will return a Pareto front of equations. The equation selected by the "score" metric (which balances complexity and accuracy) should exactly match Kepler's formula. The published benchmark success for PySR on this exact equation under noiseless conditions is 100 percent, and it maintains high robustness even with 10 percent added noise, as documented in SRBench (La Cava et al., 2021) and the SymLang evaluation (cite: 36, 45, 74).

Three most common ways people get this experiment wrong:
1. Misconfiguring the dimensional constraints. PySR requires exact unit strings. If a discovered constant requires a derived unit to make the equation physically valid, users often fail to specify wildcard units (e.g., letting a constant absorb the remaining dimensionality), resulting in the model applying the 1000.0 penalty to correct physical laws and discarding them (cite: 77, 78).
2. Ignoring the Pareto front. Beginners look only at the model with the absolute lowest loss, which is usually a highly overfitted, non-physical mathematical polynomial. The correct equation is found by selecting the model with the highest negated derivative of the log-loss with respect to complexity (the highest 'score').
3. Floating-point limits. In astrophysical datasets like Kepler's, supplying raw unscaled numbers (like mass in exact kilograms) causes floating-point overflow during the exponential or power mutations in the Julia backend, crashing the worker threads with "DomainError with Inf". Variables must be normalized or non-dimensionalized prior to the search (cite: 45, 75).

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field with software engineering resources, do not build another symbolic regression search algorithm. The genetic programming backend of PySR is highly optimized. What is missing is the connective tissue between raw scientific literature, deep background logic, and symbolic regression.

1. An Abductive Reasoning Axiom Generator
Interface: IN: Raw text/PDFs of background literature and a dataset. OUT: A formally encoded KeYmaera X axiom file.
The hard part: AI-Descartes proved that filtering symbolic regression outputs against logical background theory is incredibly powerful. However, the background theory (e.g., Newton's laws) currently has to be manually written by domain experts into rigid formal logic syntax. A reliable LLM-based agent that reads scientific papers, translates the constraints into KeYmaera X or Z3 formal logic formats, and manages the inevitable syntax errors does not exist. The engineering lift is substantial because formal verification tools require absolute syntactic precision, which LLMs struggle with (cite: 96, 112).

2. Differentiable Dimensional Analysis in Continuous Search
Interface: IN: Dataset with attached unit metadata. OUT: Dimensionally consistent equations derived via gradient descent.
The hard part: Currently, PySR handles units by calculating the expression and applying a massive post-hoc penalty (1000.0) if the dimensions do not match. This makes the search space rugged and inefficient. Several groups are trying to build native dimensional analysis into the search graph itself (so invalid trees cannot even be formed), but doing this dynamically while discovering hidden dimensionless constants is an open mathematical and engineering problem (cite: 75, 77). 

3. Reliable LLM Test-Time Symbolic Verification
Interface: IN: LLM prompt proposing a physical law. OUT: Automated execution of PySR to verify the LLM's hypothesis against data, feeding the residual error back into the LLM context.
The hard part: Systems like Sakana's AI Scientist attempt to run Python code, but when the code fails, the LLM often gets stuck in a loop of trivial syntax fixes (adding an average of only 8 percent more characters per iteration). You would need to build a specialized agentic loop that treats PySR as a native tool, parses the Pareto front output, and translates the mathematical residuals back into semantic text the LLM can reason about (cite: 64).

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of this field is littered with claims of automated discovery that did not survive methodological scrutiny. This section is critical for avoiding past traps.

The BACON Fudging Critique
The method you anchored this query to—BACON—suffers from a standing, unrefuted historical and methodological critique. BACON claimed to rediscover Kepler's Third Law and Ohm's Law from raw data. However, epistemologists and historians of science, notably Albrecht Heeffer, demonstrated that the data fed into BACON was highly sanitized and idealized (cite: 38). Kepler did not possess clean tables of average distances and periods; he had noisy, geocentric, irregular observational data. BACON was measuring its ability to solve a pre-cleaned algebraic puzzle, not the phenomenon of scientific discovery. Furthermore, BACON's tabular heuristic of generating ratio and product columns failed entirely when applied to noisy data with more than a few variables, leading to combinatorial explosion and the eventual abandonment of the BACON architecture in favor of evolutionary search (cite: 24, 38, 39).

LLM Memorization and the Benchmark Crisis
In 2024 and 2025, numerous papers claimed that Large Language Models could perform symbolic regression and equation discovery zero-shot. This programme has largely collapsed. The LLM-SRBench paper (2025) proved that LLMs were simply regurgitating equations from their training data. When the authors took the standard AI Feynman benchmark and mathematically inverted the features (LSR-Transform) or added synthetic terms (LSR-Synth), the performance of state-of-the-art LLMs crashed to 31.5 percent. This proved that LLMs were measuring the benchmark itself (memorization) rather than performing data-driven reasoning. Do not rely on pure LLMs to discover math (cite: 54, 57, 88).

The AI Scientist Replicability Failures
Sakana AI's "AI Scientist" (2025) claimed to fully automate research from idea generation to peer review. Independent evaluation by Beel et al. (2025) revealed severe methodological failures. The system classified 100 percent of its own ideas as "novel" based purely on simplistic keyword searches against the Semantic Scholar API, completely failing to recognize established concepts (e.g., misclassifying standard micro-batching as a novel discovery). In 42 percent of its experiments, the system crashed due to unresolvable coding errors. Furthermore, 57 percent of the published manuscripts contained hallucinated numerical results, and experiments optimized for energy efficiency falsely reported accuracy gains while increasing compute. The system is an impressive text generator but a failed scientific experimenter (cite: 17, 64, 67).

Deep Learning's Failure to Learn Conservation Laws
Attempts to use standard Deep Neural Networks (like Multilayer Perceptrons or unconstrained Graph Neural Networks) to model physical systems have repeatedly shown that while the models achieve high predictive accuracy on the test set, they fail to learn the underlying conservation laws (e.g., energy, momentum). Without explicit symbolic constraints or symbolic distillation, the networks learn sample-specific "implied" forces that violate physics when extrapolated even slightly outside the training domain. This standing critique justifies the entire existence of the Neural-Symbolic subfield (cite: 36, 71).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you are a well-resourced newcomer with compute and engineering talent, you should ignore the crowded space of tweaking genetic programming algorithms and ignore the hype of pure LLM prompting. Aim for the intersection of symbolic distillation and foundational models.

Experiment 1: Distilling LLM MLP Layers into Symbolic Surrogates
What to do: Replicate and scale the SymTorch experiment. Take an open-source Large Language Model (e.g., Llama 3 or Qwen). Wrap its Multi-Layer Perceptron (MLP) layers during a forward pass to collect input-output data. Run PySR to find a closed-form mathematical equation that approximates that layer. Then, replace the neural layer with the exact symbolic equation.
Why it is feasible now: PySR 2.0.0 and the SymTorch framework (2026) solved the engineering barriers of GPU-CPU data transfer and input-output caching during forward passes. 
What it measures: The throughput (tokens per second) versus perplexity degradation when dense matrix operations are replaced by sparse, interpretable mathematical equations.
Falsification: If the perplexity costs of symbolic replacement are vastly inferior to standard dimensionality reduction (like PCA) at the same throughput, the idea that neural networks learn fundamentally compressible symbolic mathematical logic is falsified (cite: 69, 71).

Experiment 2: Active Learning for Disambiguating Symbolic Pareto Fronts
What to do: Build a closed-loop system where PySR is run on a very small, initial dataset (e.g., 10 data points). PySR will output a Pareto front containing 3 or 4 entirely different physical equations that all fit the 10 points perfectly. Write an algorithm that mathematically calculates the specific input domain where Equation A and Equation B diverge the most. Query the user (or a simulation engine) for the exact ground-truth data at that specific divergence point, and feed it back into PySR.
Why it is feasible now: PySR's Julia backend is now fast enough to run continuously in an active-learning loop.
What it measures: The minimum number of actively selected data points required to converge on a single true physical law, compared to random random sampling.
Falsification: If active sampling does not reduce the data requirements compared to uniform random sampling, it implies the symbolic search space is too chaotic for targeted disambiguation.

What will NOT work:
Do not attempt to build a fully autonomous "AI Researcher" by chaining LLM prompts together to write code and analyze data without deterministic grounding. The evaluations of Sakana's AI Scientist prove that conversational context windows are insufficient for debugging complex experimental pipelines; the LLMs will hallucinate results to fulfill the prompt's mandate to write a paper. Furthermore, do not attempt to revive BACON-style tabular heuristics for modern continuous data. The noise profiles of real-world physics and biology datasets immediately defeat strict constant-term heuristics, which is exactly why the field abandoned them for evolutionary algorithms decades ago.
