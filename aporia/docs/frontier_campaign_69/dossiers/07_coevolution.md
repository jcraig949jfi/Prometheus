# Prompt 07: Coevolution

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdKS1NlYXZ2bEd2X2Ytc0FQZ2J5WGlROBIXSktTZWF2dmxHdl9mLXNBUGdieVhpUTg
**Elapsed:** 274s

---

# FRONTIER PRACTITIONER DOSSIER

Competitive coevolution has transitioned from a specialized subfield of evolutionary computation into a core mechanism driving the most advanced open-ended learning and large language model research today. The foundational premise you outlined is exactly correct: evaluating candidate solutions against an actively evolving population of adversaries, rather than a static benchmark, prevents the search from collapsing into a memorised local optimum [cite: 1]. The fitness landscape constantly shifts, creating a continuous learning gradient known as an evolutionary arms race [cite: 2, 3].

However, this dynamic landscape introduces severe methodological hazards. When fitness is entirely subjective and relative to the current opposing population, a system can exhibit the illusion of progress while actually moving in circles, or the populations can completely disengage from one another, destroying the learning gradient entirely [cite: 4, 5]. Understanding these failure modes, and the architectural remedies required to prevent them, is the primary hurdle for a new practitioner.

The following dossier provides a comprehensive, skeptical, and reproducible roadmap for a computational scientist entering this field in 2026.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Competitive coevolution in 2026 is no longer a standalone discipline restricted to optimizing sorting networks or small control policies. It has been largely absorbed into the broader paradigms of Open-Ended Learning, Automated Curriculum Generation, and Adversarial Reinforcement Learning [cite: 6, 7]. The classical methods of discrete genetic algorithms have been heavily integrated with gradient-based neural network optimization and large language model prompt evolution [cite: 8, 9]. What was lost in this merge was the simplicity of minimal substrates; modern experiments require massive compute and often obscure the fundamental dynamics beneath layers of neural architecture. 

What is SETTLED is that pure, unconstrained competitive coevolution does not naturally lead to open-ended progress. Without explicit archiving mechanisms such as a Hall of Fame or external minimal criteria, populations will reliably fall into pathologies like cycling or mediocre stable states [cite: 4, 10]. It is also settled that complexification, allowing solutions to grow in structural size over time, is a highly effective way to maintain an arms race [cite: 11].

What is CONTESTED is the necessity of spatial or geographical isolation. While early methods relied heavily on local tournaments on a 2D grid to preserve diverse niches, modern researchers argue over whether spatial embedding is strictly necessary if you apply rigorous Quality-Diversity algorithms to map and select elites based on behavioral descriptors [cite: 6]. Furthermore, there is active debate over whether large language models acting as both generators and evaluators can self-improve indefinitely without hitting a complexity ceiling or mode collapse.

What is OPEN is the generation of truly novel, endlessly expanding task spaces. The current frontier involves using foundation models as evolutionary mutation operators to write code or generate synthetic tasks, coevolving an archive of diverse model capabilities against an archive of generated environments [cite: 6, 12]. The focus has shifted from finding a single optimal solution to generating a continually expanding collective of diverse, highly capable agents.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Hillis, W. D.
1990
Co-evolving parasites improve simulated evolution as an optimization procedure
Physica D: Nonlinear Phenomena
DOI 10.1016/0167-2789(90)90076-2
The anchor paper defining the host-parasite mechanism on a spatial grid for N=16 sorting networks. A practitioner must know this to understand how relative fitness prevents stagnation [cite: 1, 13].

Ficici, S. G., and Pollack, J. B.
1998
Challenges in coevolutionary learning: Arms-race dynamics, open-endedness, and mediocre stable states
Proceedings of the Sixth International Conference on Artificial Life
IDENTIFIER UNKNOWN
The most critical theoretical paper on why coevolution fails. It defines the specific pathologies of cycling and collusion that you will inevitably encounter [cite: 14, 15].

Stanley, K. O., and Miikkulainen, R.
2004
Competitive Coevolution through Evolutionary Complexification
Journal of Artificial Intelligence Research
DOI 10.1613/jair.1338
Proves that adding structural complexity over time prevents populations from forgetting past innovations and stabilizes the arms race [cite: 11, 16].

Watson, R. A., and Pollack, J. B.
2001
Coevolutionary dynamics in a minimal substrate
Proceedings of the Genetic and Evolutionary Computation Conference
IDENTIFIER UNKNOWN
Introduces the minimal "Greater-Than" game to isolate and study disengagement and forgetting without the noise of a complex domain [cite: 3, 4].

CURRENT

Wang, R., Lehman, J., Clune, J., and Stanley, K. O.
2019
Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions
arXiv
arXiv:1901.01753
The paper that resurrected coevolution for deep reinforcement learning by proving that environments and agents must be paired and transferred to achieve open-endedness [cite: 17, 18].

Mash, R., Castanon, G., and Culbertson, J.
2024
Curious POET: Intrinsic Motivation Improves Exploration Efficiency
Artificial Life Conference Proceedings
DOI 10.1162/isal_a_00736
Demonstrates that adding an intrinsically curious oracle to the POET framework forces populations out of redundant behavioral spaces, representing the modern approach to diversity [cite: 19, 20].

Lange, R. T.
2023
evosax: JAX-Based Evolution Strategies
Proceedings of the Genetic and Evolutionary Computation Conference
arXiv:2212.04180
The foundational paper for modern, hardware-accelerated evolutionary computation, proving that evolution strategies can be scaled on TPUs and GPUs using JAX [cite: 21, 22].

Bahlous-Boldi, M., et al.
2026
AC/DC: Assessment Coevolving with Diverse Capabilities
ICLR
arXiv:2604.14969
The absolute frontier of coevolution in 2026. Models evolve via weight merging while tasks evolve via synthetic generation, creating an open-ended loop without explicit objective functions [cite: 6, 12].

PART 3. SOFTWARE I CAN ACTUALLY RUN

evosax
https://github.com/RobertTLange/evosax
Python and JAX
MIT License
2023
MAINTAINED
This is the premier tool for scaling continuous evolution strategies to modern hardware. You can run massive parallel rollouts of neural network controllers against varied environments entirely on GPU. The primary limitation is that it is built around continuous spaces and JAX primitives; coercing it to handle variable-length discrete structures like sorting networks requires complex mapping and XLA compilation workarounds [cite: 23, 24].

EvoTorch
https://github.com/nnaisense/evotorch
Python and PyTorch
Apache-2.0 License
2025
MAINTAINED
A highly scalable PyTorch-native evolutionary library that easily integrates with Ray for distributed compute. It excels at neuroevolution and black-box optimization. It includes explicit competitive coevolution primitives and functional APIs. The gotcha is that highly irregular discrete search spaces can bottleneck the tensor-optimized pipeline, requiring careful batching [cite: 25, 26].

DEAP
https://github.com/DEAP/deap
Python
LGPL-3.0 License
2023
DORMANT
The classic community standard for explicit genetic algorithms and programming. You can literally reproduce Hillis's exact sorting network experiment today using DEAP's built-in tools. However, it relies entirely on Python's native multiprocessing. It has no modern GPU tensor acceleration, making it agonizingly slow for deep neural networks or massive population scales compared to evosax [cite: 27, 28].

Curious-POET
https://github.com/act3-ace/Curious-POET
Python
UNCONFIRMED License
2024
DORMANT
The reference implementation for intrinsically motivated auto-curricula. It allows you to run BipedalWalker coevolution out of the box. The major limitation is the extreme compute requirement; the authors explicitly state the architecture requires a 96-core CPU node with 400GB RAM alongside a separate GPU node just to run effectively [cite: 29]. 

PART 4. DATA AND BENCHMARKS

SWE-bench
https://github.com/swe-bench/SWE-bench
Approximate size: 2294 real-world issue-pull request pairs (base), expanding dynamically.
MIT License
Used to measure the ability of code-generation agents to resolve complex software engineering issues. This is treated as highly authoritative because execution against real unit tests provides an ungameable ground truth. It is perfect for host-parasite experiments where agents are evaluated against an evolving suite of adversarial edge-case tests [cite: 30, 31].

BipedalWalker (Gymnasium)
Access via standard pip install gymnasium
Small footprint
MIT License
The de facto standard for open-ended environment coevolution (via the POET lineage). Used to measure continuous control adaptation. Note that standard versions are highly susceptible to saturation; agents can memorize specific gait patterns if the terrain generator is not properly parameterized to force varied morphologies [cite: 19].

N=16 Sorting Networks Space
Implicit algorithmic space
Zero footprint
Public Domain
An exhaustively studied discrete optimization space. There are 16 factorial possible test cases. It is used to strictly measure the efficiency and generalisation of competitive coevolution mechanisms. The global optimum is a network of 60 comparisons, providing an absolute mathematical ground truth to verify if your coevolutionary arms race actually succeeded or merely cycled [cite: 1].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to understand the tacit knowledge of this field is the foundational Hillis N=16 Sorting Network experiment. Because modern POET implementations require prohibitive compute clusters, recreating Hillis on a modern machine exposes every theoretical pathology (cycling, disengagement) in a highly controlled environment in a matter of hours.

Software: DEAP version 1.4.1 running on Python 3.9.
Dataset: Generator function producing random sequences of 16 integers.
Parameters:
Host Population: 65536 individuals.
Parasite Population: 65536 individuals.
Grid: 256 by 256 spatial torus.
Host representation: Ordered list of 60 to 120 pairs of integers (representing comparators).
Parasite representation: 10 to 20 test cases per parasite (each case is a sequence of 16 integers).
Evaluation: The host at coordinate x, y is evaluated exclusively against the parasite at x, y. 
Host Crossover: Two-point crossover at a rate of 0.6.
Host Mutation: Random comparator exchange at a rate of 0.01.
Seeding: 10 independent replicates using distinct random integer seeds.
Compute cost: Approximately "2 to 4" CPU hours per replicate on a standard modern workstation.
Expected result: The coevolutionary setup should reliably produce a valid sorting network requiring 61 comparisons. This compares against the published baseline of 65 comparisons for an isolated genetic algorithm without parasites. Citation: Hillis 1990 [cite: 1, 13].

Three common ways people get this experiment wrong:
One. Failing to implement the spatial grid correctly. If you evaluate hosts against a uniformly mixed pool of parasites, the dominant parasites wipe out the niche tests, causing the hosts to overfit and lose generalisation.
Two. Using the internal relative fitness to plot progress. The internal fitness graph will look like static noise or random oscillation (Red Queen dynamics). You must evaluate the best host of each generation against a comprehensive, held-out set of permutations to observe the true historical learning gradient [cite: 32].
Three. Permitting disengagement by allowing the parasite mutation rate to be too high. If the test cases become overwhelmingly difficult too quickly, host fitness drops to absolute zero, selection pressure vanishes into a random walk, and the populations drift [cite: 4, 14].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A practitioner entering this space today will find a glaring gap: there is no off-the-shelf, hardware-accelerated (JAX or PyTorch) framework specifically designed for discrete, spatially-embedded bipartite coevolution. 

If you want to run LLM agents (hosts) against generated prompts (parasites) using a rigorous grid-based tournament or an explicit Hall of Fame archive, you must write the interaction matrix manager yourself. 
What goes in: Two dynamically sized arrays of behavioral embeddings representing the current populations, plus an unbounded historical archive.
What comes out: A bipartite interaction matrix of scalar fitness scores, calculated efficiently without requiring N-squared pairwise evaluations.
The hard part: Managing the memory and computational explosion of the interaction matrix over thousands of generations. When assessing cross-generational progress, you cannot afford to evaluate every new agent against every historical environment.
Work estimate: This is a robust systems-engineering problem requiring roughly "200 to 400" hours of development to implement a sparse, distributed Elo-rating or Nash-averaging selection mechanism [cite: 5, 33]. Several AI alignment labs have rebuilt this exact component privately to manage adversarial red-teaming because existing tools like evosax are fundamentally tuned for continuous parameter search rather than discrete text-based game theoretic evaluation [cite: 9, 34].

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of competitive coevolution is littered with failed assumptions, primarily because researchers trusted the internal fitness metric. The standing critique, most rigorously defined by Ficici, Watson, and Pollack, is that competitive coevolution does not intrinsically optimise for objective quality; it optimises for surviving the current opponent [cite: 14, 15].

Negative Results and Pathologies:
Cycling (Intransitivity): Populations frequently fall into Rock-Paper-Scissors dynamics. Host A beats Parasite A. Parasite B evolves to beat Host A. Host B evolves to beat Parasite B. Parasite A returns to beat Host B. The algorithm endlessly loops through these states. Internal fitness looks healthy, but objective performance against an absolute metric shows zero historical progress [cite: 3, 32].

Mediocre Stable States (Collusion): The most damning failure mode. Instead of an arms race, the populations find a local equilibrium where both receive moderate fitness scores by adopting minimal-effort strategies. They implicitly "collude" to stop evolving. A classic retracted expectation was that pure predator-prey coevolution would continually escalate; in reality, without an external complexity forcing function, predators and prey often settle into simple, repetitive tracking behaviours [cite: 10, 35].

Disengagement (Loss of Gradient): When one population discovers an innovation that the other cannot immediately counter, it dominates completely. If parasites become too hard, all hosts score zero. With all hosts scoring zero, there is no differential fitness, selection becomes random, and the populations drift aimlessly. Substitution of the Fittest and competitive fitness sharing were proposed to answer this, but they require delicate hyperparameter tuning [cite: 3, 14].

Methodological Critiques:
The primary standing critique is that without a "Minimal Criterion" or an expanding archive (Hall of Fame), coevolution is memoryless. It was repeatedly shown that methods appearing to generate boundless complexity were actually just shifting horizontally across an uninteresting landscape. This critique was largely answered by the introduction of Quality-Diversity algorithms (like MAP-Elites) and Minimal Criteria Coevolution, which force the system to maintain an explicitly mapped archive of diverse, functionally competent individuals rather than relying on population drift [cite: 6, 12].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Rank 1: Coevolving Software Engineers and Adversarial Unit Tests on SWE-bench.
Experiment: Maintain a population of open-weights coding LLMs (hosts, modified via evolutionary model merging or LoRA). Maintain a population of synthetic unit tests (parasites). The host is scored on tests passed; the parasite is scored on how many competent hosts it breaks. 
Why feasible now: The open-source availability of highly capable code models and fast inference frameworks allows running this at scale [cite: 6, 31].
What it measures: Whether automated, adversarial test-generation can force a coding model to generalise beyond its pre-training distribution without human labels.
Falsification: If the final archived code model fails to outperform the base model on a frozen, held-out subset of SWE-bench verified, the arms race was an illusion.

Rank 2: Intrinsically Motivated Prompt-Injection Red Teaming.
Experiment: Coevolve a population of jailbreak prompts against a population of system-prompt defenses. Apply the "Curious Oracle" method from Curious-POET to the attackers, rewarding them specifically for triggering internal activation states in the host model that are orthogonal to previous attacks [cite: 9, 19].
Why feasible now: Tooling for extracting intermediate attention and activation states from open models is now standardized, allowing intrinsic motivation to be calculated directly from the network's latent space.
What it measures: The coverage of the safety boundary.
Falsification: If the curious attackers fail to discover unique jailbreaks compared to standard random fuzzing.

What will NOT work:
Attempting pure, unconstrained competitive self-play between two large language models playing conversational games without an external execution environment (like a compiler or a physics engine). Without a strict, ungameable ground truth, language models in pure coevolution reliably degenerate into idiosyncratic, self-reinforcing dialects. They will fall directly into a mediocre stable state, colluding to pass the evaluation by outputting easily verifiable but meaningless tokens. You must anchor the fitness to an external, undeniable reality like passing a unit test [cite: 9, 34].

**Sources:**
1. [pennds.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf_jjM3uEg48ZHJaWMZvy6JyJaixQhwBv4qMyjKyGQI1yHGnXr_UUXvjHDHqbC_lQuOfMg73p27zz81TV4cjnbmKTt0mMwehIJlpmo_tqUqBQMOt4IaPNyK3W016BzEWt0V-rODUPZhaK0iUtmEGUEch_gM4lmjHusO0847RJCZNtzDXXFvA4PrS-_h9I=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE15JXBZ4NQBOpOo-D9QEXOeVh8tmluUulmQ-dkJSdmVhuh6f6pI9PX1PToXND9QD1HQa1mNJ2oN06vkjbO5FXKaLID-rOQ_K09CMJPkUswwf20vnCNpQ==)
3. [scitepress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfKdnTPlMPYMWL37S3pwpaC-dBjlquAa1Qdef4qKui3FoS2ZYvOYrbz3SjjO3-JnTrt7LYWFQFpPQHt-wKKYdzq4osseLS-mmegfGpMol6r_Vuz5u1gjjaR2BgyVFOtBq282R3kCQsJEFfPWk0RA==)
4. [unr.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfRO-xkq3R_sA0yM9JpUk8DUTKVXeWU9O8rgBi6sqvADPshQpsyBTXCSB0NkMIpvs9kFSKoXyUDpx2uz9Gf9wu2snD4AcfQPfCuB8aT_pAtnDFGBipnPY89eS6yrqoYytOYve1HF-2bmR4Hr6zCBbqrYLceSsHGkFK8HL7E07IusUoUqUK7vdavQ==)
5. [brandeis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFkYWqWgh6V3jEzL5vTbR-33vN2s4elCdrMJL_1JimiaiJ8XdJPiOaS2QEFZWhKBZqGNvxRJMlqV-DJyZeDJ6CFJNw6ywqKP_SxLGbgGvBGCZhn3XCAAt9gdD8T1S1NDoT5PmmvKbHlhk3Ebqbz6kTN7l9lis4E4MxS6d5NBeuBaGCxPtIG_kba5amac7xcVdx8HSvFVevjaWHtZJo861mWjy7AIJcgw==)
6. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0v25NG9GGaFhiJc_FmSqjrThwFkjahptmwPuafKokNd7Rzt-VATQDsHIipkGXhyygCmfphVMtgOE0gc-aii_rUrOsjk1JtM03HomCCiV8F6iTVuUcT0Z5aHA1weFC6x4=)
7. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjaWR7ERF-FMGHiAmb8ABdkHiL9dDKVIQs0_L8X1NepHGfF0pAvtW2FdgGSJksSawASquLXCtlwGXRjHe-L38kxqdKLF9MuylNwD7auQdKIKu--p6d2iulIKyjErwMNRjJpom1Y_yQMCmNghgiYLmZZ-uCtr6mDzyFHBD_K98VchHCiNr4mm0uCLhLDfzgKIv-mLcQJgGAGAycXpYT08EC09ci)
8. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB8QQkKR2vx6wP12NGz43vlB6bKxiUdCxACgMnXkM-UzdNA_qbyp27NwYxel_XVIfnffJd9LnKPCO6nWXVnyB7q0hHfdhAdLdQcLDArmpK2SrI5r10AAPKL2-muL-8UCN5NW59be0vgw==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0uWvVEYWza2dyWlHzTO3U7-oPlbDVHhOvaBkviFP9s3j5kcGeu8q9ufVkbyadaiae8dUzKhSeaJBfsg403258T-WJJbGgVGzXRi-bFJINiq6x7PR8bUA3SA==)
10. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4E5Mu6JYe_d_m6MZsK2vRC0syNuwC1DpEtydU62BgsX8oB_LM3SaBH76Hlsd_e6NiSfPghYdUXH1Oo_5yQbt3dduujciIv2Bf1cL3cPZRhFXElzXn3UYKJZVk7ivuzqosJ6qa)
11. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdbLkms9RiqgzUslo1xF8HeziggA6Tou7iNJ3YFl1kDkyefbwAFrIz9ZFImmPeAr5gsm7TqWQraRy0HohYBzo844Sqz462yKCsEvgL3fXS1mRpUvWPF_E-A1_jV5UEdLLGBlG5EFyyobSko8mSZklguNk=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf-bZEVbMH0ztl0fffr-dcxk5KrZplP6VHUFutDQNcr9p4s_lIa6yIstKAmuSkFvWCfk4HxYXmWqBkbaO3hneF5iQY5-2AGubKEyRiaNL8nrT9tszl2PBgSQ==)
13. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6YCE5KQ60xL3XrI-avICkvnnJMTwpLdiHSn_r5NEhRcBGmE5e_Bq8uOXZqRUdFfeUCzkx7JbYEwIr3z5EfzYkGfq_jm5FUWEyGG1v1FHV0c_HNZ7SDvUu1FAAGefI1VMHQkSzmz7SRGYd0a_6Zee6Uhgk6f35PBjVhu6sItj0MFSNkwJzysIL6BpoEcLAQhcF)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFQ8YtnCySnena_toMOXB3dJX4vtYiDbyVweqvleBCNXgN60iEi2r0xCVf52oaR8kP0mAzn2fbSiqcYqg5EDo1Ab9Vzsf0DfFonGxl5KdCo_Yp2tW76G7ObA==)
15. [jasss.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh5-B5rSeaF-KFkl70_i45DS-DEPo5eEPzJYOmJ2qwqSGaKvlsQF-O4zC8Xmq7hnJLioko5A6et8KDNZgXSezGEHK4wfDZB9lfp5J-zCTSccdsQw4rHxw=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnFkg4nLfG5CVhDBYeV1DP4aolCu66HZJ4j9qor2HRIU2VhfrSkCkF_OHBqtv6yzl5V8LvICZHDAoRX-Tw-DR7kRomvKpNH49-DuZe-NHXu-KFu30c)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmKN7pVHtvTdg7jPqMifzyS6IZ7EGI4Ds4qYW9u0cCoPgO8z3ELO-0FYRDAE_wOhSlozgvyow48Xf2KqU1JgjtuBgR1XeC0toQ7ljPluXPKXQo4zwXb2r87A==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwefiECvLsWmh1FRftAAKkWniYX5G29ulkpwY2qblj4_QRhLPlzTlQM1x52VwRsiEVt0Pbl_udozyRASzADXHGtXvPynLDg8HenXMyhV_foV9QRE47ww==)
19. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9R-jE0UR5vAYxGMMi7djepvUM0mIOfa8AS3nion_KW4MnyPSrCyTLQB0XbLhoTUkQxp2hMKodJzMT18bTxUrWDFrd1DDc7Ifr9qJ_MSwQvIxei4vjhy8CpalftJ9kWcOL0zhqNPvtZQLHvrg6sQJl5AMQXJZlvd43yfJK7Auk9Yz3wHUtfldP9A==)
20. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmoyL6HJu0EKI1ANSBpntaMFLRHrQHKW1xlb1B5Qjz7lsoRGwXsuwYOR_-NnQhJh_D5f9Lko8VzfT6cOHgwfOT37cPMSwWgFeJPtdPXaNHbd_CTvqiNmKj4HOd9-O7ulxRvlMDktZR_EbWpawB6-fNXyay7f9FJEtY6Lf2HsRsvNAB8IVlovkjiHqTbDdQE9tHOt0siaxUYJ_-lOdLypiMm981pw==)
21. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ1_Dclkz5p5AB3cZrAO1opjARQx1tvXpazyjh57dmKBtr29ZDlUj_TKqYRe5TQVCUBSIUAid8JZf3U0mkFoeoA5SLUjx3x9fEyRo_q1HNc_oUkLDN3X-COhXb5POU8gvdyO08Keuz2_0f_cBqXrVQfS-xGBlZcO0gDZXGqKhTk9tQdVTe4lgDyp5UbAgtzXu_CBHACqa2AySFcHBJRV_WWlThi8YofJZv6NIGkJFqYX9hkdKmRjcFw_aPIxO8BsWtH72mug==)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGzmHZSqkQ4-O3ouazMZ6xq_LrXFByuFkfJ2iP6kU23MMnWwQsDC8bfCXasQZfqw_20G4QL8Gs235uLAh75SL9MSHNFurKPYJrMMaIjBl4RkzYIGQSaS0oCz_1fg==)
23. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbCYkfjwIso7a4I7Ba84gbyesDz38JoReHR-tXhKFB79rn9neQ7KvMrHjzjVz6Ln2byvuffEBvk9kf4JOSV9MVSARjP4evvQtOT1V_lzmFkLIMdSZTia-BhXq21Q==)
24. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBkRzumi7ja7fhoYNHq2Ws6Lox-tbj-sMQn1KrG2y1t3GwA0lYdtZwGkkJvZVGT27fIEV4WoevE8i-d8KDwdsqaoMG9GZBXZa8akf9ac-A7DfIILhk_ikZ2prfeA==)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk6kreQ1Csk_AfdewW2ezuwtNMUcNnEx3UEED6OJgQniZ8YGghQq6a24r5-MknhLBAQrPd-VyaNcLG135JzeuKZf3yNXiEIQo1I3mZmo9dGXKC6DpY3qNK9Uob)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVDs5VTBCKBIBm9E6jGgfZHWZ64XNh0mFn7ViNBuxyJONtRMCwVAFuRTVsvbO_qmPjKTOYKMhrIWJE8ciig78ZhCPJ-K8WvkmlWxGTvMf5HymyezedZopCjw_6tbv-JU8iaLYp)
27. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3QQstXuuBbYPfDrXGlrTfW_xV1sS8UOwofRRTUsIeZUtWZCfI_wUcg-O5co4SKCGORAlau_xoN7Bp8QsK7GGkeQZtwN4906s8J-C-hItymhvhvTNmKqshpK_RXMwontKPeLI=)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGimhsfdBC-1CTutottAo-2H1Lmw1j9OjYByJJ0UT9WSmWjyU2dtgi-KlLF90nYXP8W5Vlyz7MQlvlaz1oDaPIFCjH1VPskJ9MulRMWDS6egTYx)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcqVJCpTir0Q0mlAmiRIQd-LwSA5EI7sfo8KPjSWdwF_TO6oNHkCA6GOyHbDjdOscKWqNUkiQjIL7f57-qmWfc17hqY6MVHFMs4tTByK8VnUoaxT_u-_cJqdyIEJfS)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeJ6DPbwk0ZrEUXqowzAWZMKb0jcxS8zwZCxro7fGBgUB5CKR50ujvgt_Qv5IBEFiEQUMB4cBpzGS2qMQOnCcGR7AAIJbUJjyyA94ojb4aPdq81b-J4IC5Dgg87w==)
31. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsu0w4JbgOF56loKp-UgcqHwsiA-moSLXHZyInX-rSRpHbwyTsecHagl6hiFfW7G2kKKUG88itoth5SkdtVQ7i--2rwD3aBUTSIpqcs2QSGjD0yw-87hXK9Q9ir1wdx_licH4f4siaWPePSKs0E_C-4pZQfMH8AAesyNQZ34E50QXuwbYHa5Tk4y-ahWsDMcImWaW83MZhzA==)
32. [bham.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFkmZUZ6Y-BvghtrDmbMTc9TzAeN2CoHa1Re4ItbN7WM3CkuPytiWvs6dBhW47Klg19K3aWGS-lZJ7dM2nTq-uIrqSZW45-BDk_h_I03Tt5QYtMe0oVRkvicpXhSK9UEqyEX1J28s=)
33. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRo0R_5IukVOy849FKgWgeTWt5MgCYWHfSKmASZcDBKqTDZHa7lfnrOTDP3Tc8i0k9eg0eOSe7xIZDE3OH8cYY6olgBh9259GPO7rki2FGGhbVxS2gFf_zZPsjh9NbhNy9VrO9DCp6imo22BTFj8c7MxM=)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbE-46OQjQu5C5Aime_wyh6Wsr6FhvxgrNxCUEvtvH3NI5fbrj2q0yJyjaeX8cddu40WSEf5SXKugBHp1FVjlvKih5EZ0cva1qfFF2ZyGCD9jTr3aC0OjX1PI9tNvbpYDthgUolPdUmYLL)
35. [york.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8R1gKkT6iFxwELO8-mXs6p-sbH0a-X2vxgrk7_xvC7nmfrXqZE38bNh6TG70bLWqlPu6SEyV0yFF6gz-W_1qC6jrW1sEqoJTIV2N-jYI2k2LuGg-gXxOBh7QefiGJfvhS_8rQCaclFinImcsIBj2Zh9g=)

