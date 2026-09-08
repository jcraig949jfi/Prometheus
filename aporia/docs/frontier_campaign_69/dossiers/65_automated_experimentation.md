# Prompt 65: Automated Experimentation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdwbVNmYXRfckJyVFFfdU1QdW9tVXdBcxIXcG1TZmF0X3JCclRRX3VNUHVvbVV3QXM
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER: AUTOMATED EXPERIMENTATION

Research suggests that automated experimentation is undergoing a profound transition in 2026. The field is moving away from bespoke, isolated robotic setups and toward standardized, modular "self-driving laboratories" driven by advanced Bayesian optimization and increasingly augmented by large language models. While the orchestration of liquid-handling robots, spin coaters, and inline characterization is largely solved for simple proxy measurements, the field struggles with multi-step solid-state synthesis and the brittle nature of hardware abstraction layers. The evidence leans toward multi-fidelity optimization as the next major breakthrough, where cheap automated proxy measurements are systematically anchored to sparse, expensive full-device fabrications.

Regarding your anchor method: your description is largely accurate, but requires two precise corrections. First, you noted that pseudomobility is computed from conductivity and film thickness. In the canonical Ada platform architecture (cite: 14), pseudomobility is derived by combining four-point probe sheet resistance measurements with UV-Vis-NIR absorptance spectra, not merely thickness. The absorptance data is critical for estimating the charge carrier density. Second, you listed the "count of physical experiments consumed" as a measured quantity. The experiment count is not a measured physical variable but rather the algorithmic budget managed by the optimization software (cite: 14); the robot measures only the physical properties of the film, and the Bayesian optimizer tracks the evaluation count to update its acquisition function.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Automated experimentation, frequently referred to as Self-Driving Laboratories or Materials Acceleration Platforms, operates at the intersection of robotics, analytical chemistry, materials science, and machine learning. Its defining characteristic is the closed-loop cycle: algorithms design an experiment, robotic hardware executes it, analytical instruments measure the result, and the data feeds directly back into the algorithm to design the next iteration without human intervention. The field has evolved beyond basic high-throughput screening, which merely executes pre-planned grids, into active learning paradigms where the machine formulates hypotheses on the fly to maximize information gain or property performance while minimizing resource expenditure.

What is SETTLED is the algorithmic supremacy of Bayesian Optimization over grid search and random search for low-dimensional, expensive physical experiments. It is universally accepted that Gaussian Processes provide the best surrogate models for these tasks because they natively quantify uncertainty, which is required for calculating acquisition functions like Expected Improvement. It is also settled that software architectures must be strictly modular; monolithic codebases that entangle the optimization math with the hardware drivers fail as soon as a single pump or spectrometer is upgraded.

What is CONTESTED is the "Proxy Problem" and the role of autonomous agents. The specific disagreement lies between hardware pragmatists and materials science purists. Pragmatists argue that we must optimize easy-to-measure proxies (like the pseudomobility of a single thin film) because full device fabrication (like building a complete multi-layer solar cell) is too mechanically complex for reliable robotics. Purists argue that proxy optimization frequently finds "false peaks" where the film looks great in isolation but fails in a device due to interface defects or rapid degradation. A second live disagreement involves Large Language Models. One side (led by groups building systems like Coscientist) argues that LLMs should act as autonomous agents that write code to control hardware and plan syntheses based on literature. The opposing side contends that LLMs lack physical grounding, frequently hallucinate impossible robotic movements, and are too unsafe to be given direct control over physical hardware. 

What is OPEN is multi-fidelity closed-loop optimization, where algorithms mathematically fuse large amounts of cheap proxy data with a small amount of expensive full-device data. Also completely open is the standardization of hardware ontologies; the field currently lacks a universally adopted driver framework, forcing every lab to write bespoke Python wrappers for their hardware. In the last three years, the field has seen a massive shift toward incorporating categorical descriptors (e.g., choosing which molecule to use based on its computed physical properties) directly into the optimization loop, moving beyond merely tuning continuous parameters like time and concentration.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

MacLeod, B. P., Parlane, F. G. L., et al.
2020
Self-driving laboratory for accelerated discovery of thin-film materials
Science Advances
DOI 10.1126/sciadv.aaz8867
This is the foundational paper for your anchor method, introducing the Ada platform which optimized the pseudomobility of spiro-OMeTAD hole-transport films. A practitioner must read this to understand how robotic modularity, inline characterization, and Bayesian optimization are physically integrated into a working loop (cite: 14).

Roch, L. M., Hase, F., et al.
2018
ChemOS: An orchestration software to democratize autonomous discovery
PLOS One
DOI 10.1371/journal.pone.0229862
This paper defines the software abstraction layers required to separate the machine learning "brain" from the robotic "body". You must know this architecture to avoid the trap of writing a monolithic, unmaintainable control script for your instruments (cite: 38).

Hase, F., et al.
2021
Olympus: a benchmarking framework for noisy optimization and experiment planning
Machine Learning: Science and Technology
DOI 10.1088/2632-2153/abedc8
Olympus provides standard datasets derived from real robotic experiments, including the Ada thin-film runs. It is essential reading because it demonstrates how to test your algorithms in silico against real-world heteroscedastic noise before deploying them on expensive physical hardware (cite: 45).

Shields, B. J., et al.
2021
Bayesian reaction optimization as a tool for chemical synthesis
Nature
DOI 10.1038/s41586-021-03213-y
Though focused on chemical reactions rather than thin films, this is the load-bearing paper for implementing experimental design via Bayesian optimization in chemistry. It established the community standard for encoding categorical variables (like solvent or ligand choice) alongside continuous variables.

CURRENT SOURCES

Hickman, R. J., et al.
2025
Atlas: A brain for self-driving laboratories
Digital Discovery
DOI 10.1039/D4DD00134F
Atlas is the modern software successor to older optimizers like Phoenics and Gryffin. This paper maps the current frontier of Bayesian optimization in self-driving labs, explicitly solving problems like unknown experimental constraints, mixed continuous-categorical spaces, and multi-fidelity optimization (cite: 34).

Boiko, D. A., MacKnight, R., et al.
2023
Autonomous chemical research with large language models
Nature
DOI 10.1038/s41586-023-06792-0
This paper introduces Coscientist, representing the current frontier of integrating LLMs into robotic experimentation. It is vital for understanding how text-based AI can read literature, generate robotic execution code, and interface with liquid handlers, highlighting the shift from pure math-based optimization to reasoning-based agents (cite: 48).

Zhang, J., Wu, J., et al.
2024
Self-driving AMADAP laboratory: Accelerating the discovery and optimization of emerging perovskite photovoltaics
MRS Bulletin
DOI 10.1557/s43577-024-00676-4
This source applies the self-driving lab concept specifically to the complexities of perovskite photovoltaics, pushing beyond the Ada platform by handling higher-dimensional parameter spaces and addressing the stability-performance trade-offs inherent in next-generation solar materials (cite: 56).

Liang, Q., et al.
2021
Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains
npj Computational Materials
DOI 10.1038/s41524-021-00656-9
This paper critically evaluates how different Bayesian optimization strategies actually perform across diverse experimental setups. It is crucial reading because it shatters the illusion that one specific surrogate model or acquisition function works best for all materials science problems (cite: 31).

PART 3. SOFTWARE I CAN ACTUALLY RUN

Atlas
https://github.com/aspuru-guzik-group/atlas
Python
MIT Licence
2025
MAINTAINED
Atlas is the current state-of-the-art "brain" for self-driving laboratories, built on top of BoTorch (cite: 33). It can run constrained, multi-objective, and multi-fidelity optimizations out of the box, and is the tool you should use today to run the pseudomobility optimization experiment. Its main gotcha is its heavy dependency on specific PyTorch versions; attempting to run it on bleeding-edge Python 3.12 or unaligned CUDA toolchains will result in deep tensor compilation errors.

Olympus
https://github.com/the-matter-lab/olympus
Python
MIT Licence
2021
MAINTAINED
Olympus is the community standard benchmarking harness that allows you to run in-silico emulations of real physical experiments (cite: 29). You can instantiate the Ada thin-film dataset within Olympus and test your optimization loop in seconds rather than days. Its limitation is that its emulators are purely interpolative deep learning models; if your optimizer queries a region of the parameter space sparsely sampled by the original authors, Olympus will return a smoothly guessed value rather than actual physical failure, hiding cliff-edge physics.

ChemOS
https://github.com/aspuru-guzik-group/ChemOS
Python
MIT Licence
2020
DORMANT
ChemOS was the orchestrator used in the original Ada thin-film paper to pass data between the robotic hardware and the optimizer (cite: 38). While famous and highly cited, the public open-source repository is effectively dormant and unsuited for a new 2026 build. Modern practitioners either build their own lightweight message-passing infrastructure using MQTT or Redis, or they utilize emerging standards like SiLA2. Do not attempt to build a new lab tightly coupled to this specific repository.

Phoenics
https://github.com/aspuru-guzik-group/phoenics
Python
MIT Licence
2018
ABANDONED
Phoenics was the Bayesian optimizer originally used to optimize the dopant concentration and annealing time in the Ada platform (cite: 14). It relies on Bayesian kernel density estimation rather than standard Gaussian Processes. It is effectively dead, having been superseded first by Gryffin and now entirely by Atlas. Published results using Phoenics reproduce well theoretically, but installing the canonical implementation on modern environments is an exercise in dependency hell. Use Atlas instead.

BoTorch
https://github.com/pytorch/botorch
Python
MIT Licence
2026
MAINTAINED
BoTorch is the underlying computational engine maintained by Meta that powers almost all modern Bayesian optimization, including Atlas (cite: 28). If Atlas lacks a specific exotic acquisition function you want to build, you will write it here. The gotcha is its exceptionally steep learning curve; it assumes deep familiarity with PyTorch tensor operations and Monte Carlo integration. 

Ax
https://github.com/facebook/Ax
Python
MIT Licence
2026
MAINTAINED
Ax is the higher-level API for BoTorch, also maintained by Meta. While it is incredibly robust for A/B testing and software hyperparameter tuning, it is often considered too "heavy" and opinionated for custom chemical robotic platforms. It struggles natively with the asynchronous, crash-prone nature of physical laboratory equipment where a batch of three experiments might return two successes and one shattered glass slide.

PART 4. DATA AND BENCHMARKS

The Olympus Benchmark Suite
URL: https://github.com/the-matter-lab/olympus
Size: Roughly 50 MB (contains 33 tabular datasets)
Licence: MIT
This is the authoritative benchmark collection for the field. It contains the "Thin Film" (Ada) dataset, which maps the 2D space of dopant concentration and annealing time to pseudomobility (cite: 30). It is used to measure how quickly an optimization algorithm can find the global maximum of a real, noisy physical system. Note that because these are empirical datasets, they suffer from saturation; many algorithms now score identically well on them, making it hard to distinguish between a "good" algorithm and a "great" one.

The Summit Benchmark Suite
URL: https://github.com/sustainable-processes/summit
Size: Roughly 20 MB
Licence: MIT
Summit is authoritative for continuous flow chemistry rather than thin-film deposition, but it is deeply respected in the automated experimentation community. It measures the ability of an optimizer to maximize reaction yield and minimize E-factor (waste). It includes kinetic models rather than just static datasets, meaning it does not suffer from the interpolation limitations of Olympus.

The Schwefel Function Emulators
Access route: Generated via Olympus or SciPy
Size: N/A (Analytical function)
Licence: Open
While purely mathematical, this highly multimodal function is universally used to test if a Bayesian optimizer gets trapped in local optima. However, there is a known, severe overfitting problem in the literature here. Many researchers tune their acquisition function exploration hyperparameters specifically to solve the Schwefel function, resulting in algorithms that fail to generalize to the broad, sweeping gradients actually found in chemical systems like thin-film annealing. 

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment you can run today to gain tacit knowledge of this field is the in-silico execution of the Ada thin-film optimization campaign. You will use historical robotic data to see exactly how a machine learning agent navigates a physical parameter space.

Software and Versions:
Python version 3.9 or 3.10.
Olympus version 1.0.0.
Atlas version 1.0.0 (or the most recent stable release).

Dataset:
The "thin_film" dataset accessed directly through the Olympus surface generator module. This acts as a digital twin of the spin-coater and analytical instruments.

Parameters to Set:
The domain consists of two continuous variables.
Variable 1: Dopant concentration, strictly bounded between 0.0 and 1.0 (representing 0 to 100 percent doping ratio).
Variable 2: Annealing time, strictly bounded between 0.0 and 240.0 (seconds).
Objective: Maximize pseudomobility.

Experimental Protocol:
1. Initialize the Atlas GPPlanner with the parameter space defined above.
2. Set the initial design strategy to Latin Hypercube Sampling with exactly 5 initial points.
3. Run the ask-tell loop sequentially. In each iteration, "ask" Atlas for the next parameters, feed them to the Olympus thin_film emulator to "tell" you the pseudomobility, and pass that measurement back to Atlas.
4. Set the budget to 35 total evaluations (5 initialization, 30 active learning).

Replicates and Seeding:
You must run 50 independent replicates. Seed both the Latin Hypercube initializer and the PyTorch random number generator explicitly from 1 to 50 for each respective run.

Compute Cost:
Extremely low. Less than 1 CPU hour on a standard consumer laptop for all 50 replicates.

Expected Result:
By experiment 30, the median optimization regret trace across your 50 replicates should converge to the global maximum. The published expected optimal region is roughly 50 to 60 percent dopant concentration and 10 to 30 seconds of annealing time. You are comparing your convergence speed against the baseline established in MacLeod et al., Science Advances 2020. 

The Three Most Common Ways People Get This Wrong:
1. Ignoring heteroscedastic noise. The real physical experiment has varying levels of measurement noise depending on the dopant concentration (highly doped films degrade faster during measurement). If you treat the emulator as a noiseless analytical function, your optimizer will become overconfident and fail to explore adequately.
2. Failing to standardize the objective values. Bayesian optimizers using Gaussian Processes generally assume a prior with a mean of zero and a variance of one. If you feed raw pseudomobility values directly into the optimizer without standardizing them, the GP prior will be vastly mismatched to the data, breaking the acquisition function.
3. Misunderstanding the bounds. Some practitioners normalize the input space (0 to 1 for both variables) for the optimizer, but forget to map the variables back to their physical bounds before querying the emulator, resulting in out-of-bounds crashes or querying flat, uninformative regions of the space.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you build a physical self-driving lab, the primary component you will have to write yourself is the Hardware Abstraction Layer (HAL) for your specific instruments. There is no off-the-shelf universal plug-and-play driver for chemistry automation.

What goes in: High-level Python commands (e.g., "spin_coat(rpm=2000, time=30)", "get_spectrum()").
What comes out: Low-level serial (RS-232), USB, or TCP/IP packet sequences sent to the hardware, followed by polling loops to parse the raw byte-stream responses into structured data arrays.

The hard part: State management and error handling. Commercial laboratory equipment is designed for human GUI operation, not asynchronous robotic control. The firmware on a spin-coater often blocks the communication port while it is spinning, or throws cryptic hexadecimal error codes if a pneumatic line drops pressure. You have to write robust asynchronous polling loops that can detect if a physical action has actually completed, failed, or timed out. Furthermore, you must write exception handling that safely aborts a robotic movement if a collision is imminent.

Roughly how much work it is: 
Writing the driver for a simple hotplate or syringe pump takes a competent programmer two days. Writing the driver for an industrial robotic arm or a proprietary UV-Vis spectrometer can take three to six weeks of reverse-engineering undocumented serial protocols. 

Signal of a real gap: Almost every major group in this field (Aspuru-Guzik, Hein, Berlinguette, Cronin, Cooper) has privately rebuilt their own custom Python orchestration layers and hardware drivers for similar standard robotic arms and liquid handlers because a universally robust, hardware-agnostic standard does not yet exist, despite ongoing efforts from consortiums like SiLA.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most persistent methodological critique in automated experimentation is the "Proxy Invalidation Problem." In the quest to automate, researchers often measure what is easy for a robot rather than what actually matters for the technology. Pseudomobility optimization in thin films is a prime example. While the robotic loop successfully found a highly doped formulation with excellent short-term mobility, researchers later found that high concentrations of cobalt dopants rapidly degrade the film under operational conditions due to moisture absorption and ion migration. The method optimized the benchmark flawlessly but produced a material that was practically useless for long-term solar cell deployment. The critique is that the algorithm blindly exploits the proxy, and unless stability or device-level metrics are included as multi-objective constraints, the results are often technological artefacts rather than scientific breakthroughs.

A second standing critique is the "Babysitter Paradox." Many papers claim "fully autonomous" closed-loop operation for hundreds of hours. However, tacit knowledge dictates that almost all of these platforms require a graduate student sitting in the room to replace clogged pipette tips, wipe up spilled solvents, restart frozen Windows 98 legacy software on analytical instruments, and un-jam substrate handlers. The methods look autonomous in silico, but the physical reality is highly brittle. This critique is rarely answered in the literature; it is simply accepted as the cost of doing business.

A major negative result in the algorithmic space is the failure of naive Bayesian optimization in high-dimensional spaces. In the early days (circa 2018), there was a belief that BO could simultaneously optimize 20 or 30 chemical variables at once. This failed to replicate in practice. Because the volume of the parameter space grows exponentially, a Gaussian Process requires massive amounts of data to accurately model the boundaries in higher dimensions. Methods that looked incredibly strong on synthetic high-dimensional math functions failed on real chemistry because physical experiments cannot be sampled millions of times to train the surrogate. It is now settled that without clever dimensionality reduction or highly structured priors, BO is practically limited to roughly 10 continuous variables in an experimental laboratory setting.

Finally, the attempt to use Large Language Models for direct, unconstrained physical hardware control has largely failed in its initial iterations. Early experiments that allowed LLMs to write Python code to actuate robotic arms resulted in catastrophic collisions and broken glass. LLMs lack spatial reasoning and physical state awareness; they will confidently output code that moves a robotic gripper through a solid object if that object is not explicitly mathematically defined in the prompt. The field has learned that LLMs should be restricted to high-level experimental planning (choosing which chemicals to mix) and must pass their outputs through rigorous, deterministic safety checks before any physical hardware moves.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you want to run frontier experiments starting today, with compute and coding skills but avoiding the trap of reinventing the wheel, here is where you should aim.

Rank 1: Multi-Fidelity Closed-Loop Device Fabrication
What has not been done: Automating the transition from thin-film proxies to full-device testing in a unified loop.
The Experiment: Build an orchestration loop where the algorithm evaluates 50 combinations of thin films using fast optical proxies (pseudomobility). Then, force the algorithm to select the 3 most promising candidates, and interface your system with a human technician (or a secondary robotic line) to build full perovskite solar cell devices. Feed the final Power Conversion Efficiency back into the algorithm as a high-fidelity data point to correct the surrogate model. 
Feasibility: Feasible now because modern BO libraries like Atlas natively support multi-fidelity optimization, which was mathematically prohibitive for experimentalists five years ago.
What it measures: The true correlation coefficient between the fast optical proxy and actual device performance across a dynamically explored chemical space.
Falsification: If the multi-fidelity optimizer fails to converge faster than a single-fidelity optimizer running only full devices, it proves the proxy measurement is fundamentally disconnected from the underlying device physics.

Rank 2: Autonomous Troubleshooting and Error Recovery via Computer Vision
What has not been done: A self-driving lab that dynamically diagnoses and fixes its own physical failures.
The Experiment: Integrate a cheap webcam over the spin-coater. Train a lightweight convolutional neural network to classify "good films", "comet streaks", "pinholes", and "un-wetted substrates". Feed this directly into the optimization loop as an explicit constraint. If the vision system detects a pinhole, the loop automatically aborts the optical characterization step, saves the hardware time, flags the parameter set as physically invalid, and dynamically adjusts the spin-coating acceleration profile for the next run.
Feasibility: Feasible now because edge-inference hardware and vision models are cheap and easily deployed via Python APIs, avoiding complex industrial vision software.
What it measures: The percentage reduction in wasted analytical instrument time and the robustness of the surrogate model when fed explicit failure data rather than noisy, corrupted spectral data.
Falsification: If the inclusion of dynamic computer vision abortion does not decrease the total time to global optimum, it indicates that the BO algorithm was already successfully modeling the physical failures as naturally poor objective scores.

Rank 3 (WILL NOT WORK): End-to-End LLM Hardware Orchestration
The Experiment: Giving an LLM like GPT-4 or Claude an objective prompt ("Find the best dopant ratio for this film") and allowing it to iteratively write and execute the Python hardware API calls to run the instruments, analyze the data, and prompt itself for the next step without a traditional Bayesian optimization loop.
Why it will not work: LLMs are powerful at semantic reasoning but terrible at navigating noisy, continuous mathematical spaces efficiently. Without the rigorous mathematical bounds of a Gaussian Process, the LLM will waste immense amounts of physical resources taking random walks through the parameter space. Furthermore, the inherent hallucination rate of LLMs guarantees that eventually, it will misinterpret a serial port timeout as a successful run, or execute a robotic coordinate command that snaps a pipette tip, requiring immediate human intervention and breaking the autonomous cycle. Bayesian optimization remains fundamentally necessary for the actual mathematical search.
