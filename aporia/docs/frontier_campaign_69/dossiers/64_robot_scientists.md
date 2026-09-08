# Prompt 64: Robot Scientists

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdwbVNmYXBqX0I4YmZfdU1QaEpiYWtBYxIXcG1TZmFwal9COGJmX3VNUGhKYmFrQWM
**Elapsed:** 304s

---

# FRONTIER PRACTITIONER DOSSIER: ROBOT SCIENTISTS AND SELF-DRIVING LABORATORIES

### Key Points
The domain of autonomous scientific discovery is currently bifurcated. On one side, materials science and chemistry have aggressively adopted the "self-driving laboratory" model, utilizing large language models to orchestrate high-throughput screening and synthesis. On the other side, systems biology continues the lineage of the "Robot Scientist," focusing on logical, closed-loop hypothesis generation to unravel complex metabolic networks, specifically in model organisms like Saccharomyces cerevisiae. 

Recent years have seen a massive shift in the software stack. The biological domain has largely migrated from proprietary, operating-system-locked software and MATLAB-based mathematical models to open-source, hardware-agnostic Python libraries. However, the field is currently grappling with a crisis of validation. Accelerated throughput has frequently resulted in overstated claims of novelty, most notably in materials science, demonstrating that automated physical execution without rigorous, human-calibrated verification often yields artefacts rather than genuine discoveries.

### Overview for the Practitioner
If you are entering this field with computational expertise but no wet-lab experience, your primary bottleneck will not be machine learning or optimization algorithms. Your bottleneck will be physical error handling, hardware orchestration, and understanding the biological constraints of your model organism. The tacit knowledge of this field revolves around managing the semantic gap between a predicted in-silico metabolic flux and a robotic liquid handler dispensing microliters of viscous, living cultures into a 96-well plate. 

This report provides the exact architecture, reading list, and software stack required to build a functional, closed-loop automated biology platform in 2026. It centers on the yeast functional genomics loop: knocking out genes, predicting nutrient dependencies via genome-scale metabolic models, and executing the physical growth assays via robotic liquid handling. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of automated scientific discovery in 2026 represents the convergence of laboratory automation, artificial intelligence, and systems biology. Historically known as the Robot Scientist paradigm, pioneered by Ross King with the systems Adam and Eve, the field focuses on physically implemented closed-loop scientific discovery [cite: 1, 2]. In this loop, an artificial intelligence originates a hypothesis to explain an observation, devises an experiment to test it, physically runs the experiment using laboratory robotics, interprets the results, and updates its underlying model [cite: 2, 3]. Today, the field is often referred to under the broader umbrella of Self-Driving Laboratories, though this term is frequently diluted to mean any high-throughput automated lab rather than a truly autonomous hypothesis-testing loop [cite: 4].

What is SETTLED: 
The computational modeling of yeast metabolism is highly mature. The use of Genome-Scale Metabolic Models, specifically the consensus S. cerevisiae model Yeast9, combined with Flux Balance Analysis to predict auxotrophies and growth phenotypes, is the undisputed standard [cite: 5, 6]. On the hardware execution side, the software stack has decisively moved away from proprietary, vendor-locked graphical interfaces. Hardware-agnostic Python software development kits, most notably PyLabRobot, have become the settled standard for commanding liquid handlers across different manufacturers [cite: 7, 8].

What is CONTESTED:
The definition and value of "autonomy" is currently the most contested issue. One camp, heavily represented by chemistry and materials science startups, relies on Large Language Models acting as agents to parse literature, generate code, and command robots, treating the LLM as the primary reasoning engine [cite: 4, 9]. The opposing camp, rooted in rigorous systems biology, argues that LLMs are ungrounded and that true scientific discovery requires deterministic, formal logical models or constraint-based mathematical oracles that propose mathematically falsifiable hypotheses [cite: 3, 10]. This tension recently peaked following high-profile retractions and corrections in the materials science domain, where high-throughput automated systems claimed massive numbers of discoveries that were later revealed to be known artefacts misidentified by automated characterization [cite: 11, 12].

What is OPEN:
Scaling from batch microplate experiments to massively parallel, continuous time-course cultivation remains completely open. The frontier is currently defined by the Genesis project, a third-generation Robot Scientist designed to automate eukaryotic systems biology by running 10,000 parallel micro-chemostats [cite: 2, 13]. Managing the physical and computational logistics of continuous fluidic feedback loops, real-time transcriptomic sampling, and dynamic kinetic parameterization of models without human intervention is the bleeding edge of the discipline.

Changes in the last three years:
Between 2023 and 2026, the field experienced a shockwave from the integration of Large Language Models. Systems like Coscientist demonstrated that GPT-4 could write functional scripts to control liquid handlers via Application Programming Interfaces and navigate hardware documentation natively [cite: 14, 15]. Simultaneously, the release of PyLabRobot democratized automation, meaning a practitioner no longer needed a 100,000 dollar vendor contract to write custom robotic methods [cite: 16]. Finally, Yeast9 integrated thermodynamic feasibility constraints into the yeast consensus model, shifting predictions from purely stoichiometric possibilities to physically realistic metabolic fluxes [cite: 17, 18].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

King, R.D., et al.
2009
The Automation of Science
Science
DOI 10.1126/science.1165620
This is the genesis of the field, detailing Adam, the first machine to autonomously discover novel scientific knowledge by formalizing yeast functional genomics into a logical language and executing robotic experiments [cite: 19, 20]. A practitioner must read this to understand the fundamental architecture of a closed-loop hypothesis generator.

Williams, K., et al.
2015
Cheaper faster drug development validated by the repositioning of drugs against neglected tropical diseases
Journal of the Royal Society Interface
DOI 10.1098/rsif.2014.1289
This details Eve, the second-generation Robot Scientist, which transitioned the loop from functional genomics to drug screening using active learning and quantitative structure-activity relationship models [cite: 21, 22]. It is critical for understanding how to integrate econometric modeling and batch active learning into physical workflows.

Lu, H., et al.
2019
A consensus S. cerevisiae metabolic model Yeast8 and its ecosystem for comprehensively probing cellular metabolism
Nature Communications
DOI 10.1038/s41467-019-11581-3
This paper defined the modern standard for yeast metabolic modeling, introducing strict version control and a collaborative GitHub ecosystem for a biological model [cite: 23, 24]. It provides the baseline understanding of how genome-scale metabolic models are structured and curated.

CURRENT SOURCES

Zhang, C., et al.
2024
Yeast9: a consensus genome-scale metabolic model for S. cerevisiae curated by the community
Molecular Systems Biology
DOI 10.1038/s44320-024-00060-7
This is the current frontier of the anchor method, updating Yeast8 with thermodynamic constraints and single-cell transcriptomic integration [cite: 6, 25]. A practitioner must know this because it defines the exact computational substrate (4131 reactions, 1161 genes) used to generate in-silico yeast hypotheses today.

Wierenga, R.P., et al.
2023
PyLabRobot: An open-source, hardware-agnostic interface for liquid-handling robots and accessories
Device
DOI 10.1016/j.device.2023.100111
This paper introduces the software that allows Python to natively command proprietary liquid handlers [cite: 7, 8]. It is mandatory reading for anyone intending to write execution code, as it maps out the Cartesian coordinate abstraction layer that makes automated biological execution portable.

Boiko, D.A., et al.
2023
Autonomous chemical research with large language models
Nature
DOI 10.1038/s41586-023-06792-0
This paper introduces Coscientist, demonstrating how GPT-4 can act as a planner to orchestrate hardware documentation search, chemical reasoning, and code execution [cite: 15, 26]. It is essential for understanding how the LLM-agent workflow has been successfully applied to physical laboratory tasks.

Szymanski, N.J., et al.
2023
An autonomous laboratory for the accelerated synthesis of novel materials
Nature
DOI 10.1038/s41586-023-06734-w
This introduces the A-Lab, a high-throughput autonomous system that utilized active learning and robotics for solid-state synthesis [cite: 27, 28]. It is vital reading not just for the method, but as the setup for the most important critique in the modern field.

Leeman, J., et al.
2024
Challenges in High-Throughput Inorganic Materials Prediction and Autonomous Synthesis
PRX Energy
DOI 10.1103/PRXEnergy.3.011002
This paper systematically dismantled the novelty claims of the A-Lab paper, proving that the automated characterization systems hallucinated discoveries by failing to account for compositional disorder [cite: 11, 29]. It is the single most important warning on the dangers of removing human verification from the endpoint of a high-throughput automated loop.

Szymanski, N.J., et al.
2026
Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials
Nature
DOI 10.1038/s41586-025-09992-y
The formal correction to the A-Lab paper, walking back the claim of discovering new materials to merely realizing target compounds [cite: 12, 29]. This correction establishes the epistemological baseline for what an automated laboratory is actually legally and scientifically permitted to claim in 2026.

PART 3. SOFTWARE I CAN ACTUALLY RUN

PyLabRobot
https://github.com/pylabrobot/pylabrobot
Implementation: Python
Licence: MIT
Activity: 2024 to 2026
Verdict: MAINTAINED
This is the operating system of the modern automated laboratory. It replaces proprietary Windows-only graphical software like Hamilton VENUS or Tecan EVOware with a modern, async Python 3.9 framework [cite: 7, 30]. Today, you can use it to program an Opentrons OT-2, a Hamilton STAR, or a Tecan EVO to dispense selective media and yeast cultures into a 96-well plate using a single, unified script [cite: 8, 16]. Its primary limitation is that it does not officially support every proprietary firmware version, and using it to bypass vendor software voids manufacturer warranties [cite: 30]. The community relies heavily on its browser-based visualizer to simulate deck state before physical execution. Note that the older, Hamilton-specific library PyHamilton is now effectively DORMANT and superseded by this project [cite: 7].

COBRApy
https://github.com/opencobra/cobrapy
Implementation: Python
Licence: GPL and LGPL version 2 or later
Activity: 2024 to 2026
Verdict: MAINTAINED
This is the constraint-based modeling package required to load the Yeast9 model and run Flux Balance Analysis [cite: 31, 32]. You use this to run the in-silico knockout experiment: deleting a gene, optimizing for the biomass objective function, and checking if the predicted growth is zero [cite: 6, 33]. Its primary limitation is that it models steady-state fluxes perfectly but fundamentally cannot capture dynamic temporal responses, stochastic gene expression, or lag phases, which are critical parameters in the real physical growth curves your robot will measure [cite: 17, 31].

RAVEN Toolbox
https://github.com/SysBioChalmers/RAVEN
Implementation: MATLAB
Licence: GPL
Activity: 2024 to 2026
Verdict: MAINTAINED
While the execution world has moved to Python, maintaining and compiling the raw upstream yeast-GEM repository still frequently requires MATLAB and the RAVEN toolbox [cite: 34]. If you want to contribute patches to the core Yeast9 consensus model or run the heavy-duty gap-filling algorithms, you must have RAVEN version 2.8.3 or later installed. The gotcha here is the language barrier: you will often have to serialize models out of MATLAB via SBML or JSON to ingest them into your Python orchestration stack [cite: 34].

PART 4. DATA AND BENCHMARKS

yeast-GEM (Yeast9)
https://github.com/SysBioChalmers/yeast-GEM
Size: 4131 reactions, 2806 metabolites, 1161 genes
Licence: CC-BY 4.0
This is the authoritative metabolic model for Saccharomyces cerevisiae [cite: 6, 34]. It tracks community development via version control. You will download the specific release (e.g., version 9.0.2) as an SBML file. It is used as the foundational ground truth to predict which gene knockouts will result in which nutrient dependencies [cite: 6]. The benchmark metric is how well its simulated steady-state biomass flux matches physical wet-lab growth rates.

BiGG Models Database
http://bigg.ucsd.edu
Size: Over 100 curated genome-scale metabolic models
Licence: Varies by model, generally open access
While yeast-GEM is specific to S. cerevisiae, BiGG is the authoritative community repository for all constraint-based models [cite: 31]. If you expand your autonomous loop to E. coli (using the iML1515 model), you will pull the baseline data from here [cite: 31]. A known limitation is that while central carbon metabolism is universally highly curated across these models, secondary metabolism and stress responses often overfit to specific legacy experimental conditions.

Genesis-DB
IDENTIFIER UNKNOWN (Hosted internally by the Genesis project teams)
Size: Data from thousands of micro-chemostat cultivations
Licence: Unknown (Described in 2023 preprints, access likely restricted or bespoke)
An ontology and database designed specifically for modeling data and metadata from autonomously performed yeast micro-chemostat cultivations in the Genesis robot scientist framework [cite: 35]. This represents the future standard for how time-series robotic biology data will be structured to support AI-driven automated reasoning, contrasting with simple CSV exports of plate-reader data.

PART 5. THE REPRODUCTION RECIPE

The most informative experiment to anchor your program is the automated detection of a URA3 gene knockout auxotrophy, comparing the in-silico prediction directly to an automated physical layout.

Software and Dataset:
Python 3.10
COBRApy version 0.26 or later
PyLabRobot version 0.1 or later
yeast-GEM (Yeast9) SBML file version 9.0.2

Parameters and Execution:
1. Load the yeast-GEM.xml into COBRApy.
2. Set the model objective to the biomass reaction: r_2111.
3. Configure the boundary conditions to simulate a defined minimal medium (glucose-limited, aerobic). Set the lower bound of glucose exchange to negative 10 mmol/gDW/hr, and oxygen to negative 20. Ensure all other carbon and amino acid exchange fluxes are set to 0.
4. Run standard Flux Balance Analysis model.optimize. The expected result is a positive biomass flux of approximately 0.085 gDW/hr. This is your wild-type control [cite: 6].
5. Simulate the knockout by setting the bounds of the reactions associated with the URA3 gene to 0. Run FBA. The expected result is a biomass flux of 0.0. The model predicts cell death.
6. Simulate the nutrient add-back by opening the exchange reaction for uracil. Run FBA. The expected result is the restoration of positive biomass flux.
7. Translate this to PyLabRobot. Write a script that defines a 96-well plate and a media reservoir. Command the liquid handler to dispense 190 microliters of minimal media into column 1, and 190 microliters of minimal media plus uracil into column 2. Command the robot to aspirate 10 microliters of the URA3 knockout yeast liquid culture and dispense it into both columns.

Compute Cost:
The COBRApy FBA simulation utilizes linear programming and will execute in less than one second on a standard CPU [cite: 31]. The physical PyLabRobot execution will take roughly two minutes of robot time.

Common Failures:
1. Confusing reaction IDs with metabolic function annotations. In Yeast9, specific reaction IDs must be targeted (e.g., users frequently attempt to knockout a gene name string rather than using the model.genes.get_by_id syntax, or rely on outdated Yeast8 reaction IDs) [cite: 6].
2. Failing to properly define the in-silico media. If a practitioner forgets to constrain the uptake of trace amino acids or vitamins that are open by default in the SBML file, the FBA will find a mathematically valid but biologically impossible pathway to bypass the URA3 knockout, resulting in a false-positive growth prediction.
3. Physical evaporation and edge effects. In the physical robotic assay, placing the small-volume cultures on the outer edge of a 96-well plate during a 24-hour incubation will result in evaporation, concentrating the media and skewing the optical density readings, leading the orchestrator to falsely categorize a growing strain as dead.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

The Orchestration State Machine
No off-the-shelf software provides the closed-loop orchestrator. You have COBRApy for inference and PyLabRobot for physical execution, but you must build the middleware agent that sits between them. 
Interface: The input is a CSV or JSON file containing continuous optical density readings over time from a robotic plate reader. The output is a compiled PyLabRobot Python script detailing the exact pipetting steps for the next batch of 96 wells.
The hard part: Building a robust exception-handling state machine. If the plate reader reports an optical density of 0.0 for a positive control, your orchestrator must recognize this as a physical hardware failure (e.g., a clogged pipette tip or a dropped plate) rather than a biological reality. It must pause the loop and page a human, rather than updating the COBRApy model with mathematically disastrous false-negative data. Several groups, including the Acceleration Consortium and the Genesis team, have rebuilt custom laboratory information management systems to handle this state routing privately, signaling a massive gap in open-source infrastructure [cite: 35, 36].

Dynamic Lag-Phase Extractors
Current automated systems easily read maximum optical density, but you must build a custom signal-processing pipeline to extract lag time and maximum doubling rate from noisy, non-linear time-series plate reader data. You will need to write a module that fits the raw optical density time-series to a Gompertz or Baranyi growth model, filtering out the initial noise caused by condensation on the plate lid.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The A-Lab Correction and the Peril of Automated Oracles
The most significant negative result in the field of autonomous discovery occurred in early 2024 and culminated in a 2026 correction [cite: 12, 29]. The A-Lab, a heavily funded autonomous solid-state synthesis platform, published a claim in Nature of discovering 41 novel materials out of 58 targets using automated robotics and active learning [cite: 27]. However, a methodological critique by Leeman et al. demonstrated that the automated X-ray diffraction analysis used to confirm these discoveries was deeply flawed. Because human verification was removed from the loop, the machine misidentified known, compositionally disordered solid solutions as entirely novel materials [cite: 11]. The authors were forced to issue a formal correction, shifting their claim from the discovery of new materials to merely the realization of target compounds [cite: 12]. This stands as the definitive warning for the entire field: if your automated loop relies on an unverified algorithmic oracle to classify a physical result, the loop will inevitably optimize for the oracle's blind spots rather than scientific truth.

The Failure of Large Language Models as Autonomous Reasoners
While Coscientist demonstrated that GPT-4 could orchestrate simple API calls [cite: 15], attempts to use raw Large Language Models to generate novel biological hypotheses from scratch have broadly failed. Critiques point out that LLMs suffer from a profound semantic gap: they predict text based on literature distributions, not physical realities. When tasked with designing metabolic pathways without a constraint-based oracle like COBRApy, LLMs frequently hallucinate chemically impossible intermediates or violate mass and charge balance. LLMs are highly effective as translation layers between human intent and Python code, but they are catastrophic failures when deployed as the foundational physics or biology engine.

Steady-State Limitations of Flux Balance Analysis
A standing critique of the anchor method involves the limitations of Flux Balance Analysis. FBA predicts steady-state metabolic flux based entirely on stoichiometry and thermodynamics [cite: 17]. It has routinely failed to predict toxicity. An in-silico knockout might suggest that feeding a yeast strain a specific intermediate will rescue growth, but physically, that intermediate might accumulate in the cytosol and kill the cell due to a lack of dynamic regulation [cite: 17, 18]. The critique is that relying solely on FBA for the hypothesis generator will result in a high physical failure rate in the robot. This critique is partially answered by the integration of single-cell transcriptomics and proteomic constraints in Yeast9, which moderate fluxes based on empirical enzyme abundance, but predicting precise time-course dynamics remains an unsolved problem [cite: 5, 37].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Automated Kinetic Parameterization via Perturbation
What to do: Do not use the robot to search for new pathways; use the robot to fix the dynamic blind spots of the model. Program the system to systematically perturb every non-lethal single-gene knockout strain with sub-lethal concentrations of metabolic inhibitors, reading high-resolution optical density growth curves.
Feasibility: PyLabRobot allows micro-titration of continuous gradients that would be soul-crushing for a human to pipette.
Measurement: You would measure precise changes in the length of the lag phase, not just final biomass.
Falsification: If the extracted kinetic parameters do not improve the dynamic predictions of a hybrid kinetic-stoichiometric Yeast9 model on a hold-out set of double-knockout strains, the hypothesis that lag-phase variance maps directly to specific enzyme kinetics is falsified.

2. Adversarial Multi-Model Orchestration
What to do: Build an orchestrator that runs two different metabolic models (e.g., Yeast8 versus Yeast9, or a purely stoichiometric model versus a thermodynamic-constrained model) in parallel. Have the orchestrator search the in-silico space for the single knockout-nutrient pairing where the two models confidently predict opposite physical outcomes (one predicts death, one predicts growth). The orchestrator then commands the robot to physically run exactly that assay to declare a winner.
Feasibility: Compute is cheap enough to run massive parallel FBAs to find divergence points, and PyLabRobot makes the execution trivial.
Measurement: Final optical density compared against a negative control to provide a binary growth/no-growth verdict.
Falsification: If the physical yeast behaves in a third, unpredicted way (e.g., hyper-growth or morphological shift), both models are falsified and the anomaly is flagged for human review.

What will NOT work:
Attempting to build a generalized "AI Scientist" that uses an LLM to read papers, design arbitrary biological experiments, and command a liquid handler without a constrained mathematical model in the middle will fail. The combinatorial explosion of biological noise, combined with the LLM's tendency to hallucinate non-physical plate layouts, will result in the robot dispensing expensive reagents into the wrong wells, generating garbage data that the LLM will then confidently analyze as a breakthrough. Bounded, constraint-based optimization anchored to strict stoichiometric physics is the only proven path forward in automated wet-lab execution.

**Sources:**
1. [ai4science.si](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFalWQJ19hcpi-01iHIYzwZKAlpkQ7MKQON32e1Ah3_MEgslIHZ3sGoclCvE7dXlMokUl0ZxA8xua0XJrc5YFGDC5plGZRoNnq67mxC4Fddb_b0dqfJpHZtSCc5zVmyg==)
2. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPXQSVv2rCx2N0pIl1ezrZx9AOa6sBYydKbKnZCQMS1I-HV4wg9WSiBl-fK1c5XUkUorDiJedcByLXwk0u7YLMUfu474PqthNuVgrwj5yiVV97EvsPb-WsVGz46cxbNiiUx91nQTjZl78=)
3. [uvm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5FJ_DzLjqQw4dOnwEifWQTuSytnIG-vF9K7gANCXwZnfnTsXwbw8lic9AB6UfoduZ8xX4DI90M1dqPTEmxsRkNo9GkPgqis9gNAytiM6Sf-opslIGyMITTZk1C0gwaICyDaRejMLAPOA-9ETC7c-CKAPmpzB8C8TK)
4. [lifesciencesaihandbook.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnS2UpRNAnc2erpI01K06IploflxR__fgrpmYf7ymcd1qDemBVX_rLi31WbPrnG1N68mv6H39nM2IkJ2RNL0TdU_GeqVKM9RkxkGcieQatwu6hYPGqzyoSMiJivZbI7qrk0wxd7ZDYBbCBjuWKFQ_sTxEp09xzLqAGeA==)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF27sQIsBwDoa9Q7CjvtNa9bauJ4KDSQK9mVPpih0PiwEp2V6fkOY4r956s_5Vw6laUgH__s4NLpIqDsCsQv85KrBwbsTV5HiZXoWEGbsTEatYun9tkTfTDpyyt0vSlVg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfoCTDHTzl15mfr4UjUv5Xw2nJtJYj_s17xYlKkZtJG8GOhEVPzYIc4crD5KRITX4ZmxrWoa7FxgaA4hKZ7YBHAe5uCFUDbIAHXZMxTcHw8QqF6GP-drRPYQ==)
7. [pylabrobot.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtbyOsEPYuqSpYSuBjswsFO5q-IIEagQyEt_dzD7ezJjOEa5Gh7Z0w4HfML5vElFNQgALY8LK3xOagWDvppCokWwmkHcRDCVK3JCiPoZVnEmhq32zNfKRy18kUUnDQqiI=)
8. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC9Hk1qvNxLLj0PILo0vjvvv1suHEuum_xz5TvSLrDTok3UMkzFLs6lb_7HoXAMA0XVz5ap1k6-3WjcdYPKRElvhRVlBWaVCO7REs76iGCId_zIv76u_ywbIUPHFc2zbiMuABh1dzW5_1pkm2jjLCCjdclY8UuolDKJcPii_fG9tCg2jOvEhpYE6iwF_j8y3I2tE78xRBlrADP-07rT4by9g6DnDfCPogCPHIoc8aVABmOly_kF8DhFszeUFZVDw==)
9. [hunterheidenreich.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfY4r4LYEUsVa9dsvH9j6JchQreIapni4wiiHaIeiYZnTHVkDkSmj1h27M5cnuRqbRwd9ZH3apJE6nYJVNVbtaEp-_oSy-gA0LXB-NY5CqDRmoBCL4VyjULkWHQEsxIXcZV_qnmAgMKISGfi_1XHznlzkwzqRQ4uw8ytvIleYQ5HYI9mgPyji20OSUWnNwsmkc_EtjA9HvO7yFc7k-6A==)
10. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQwnw5M7Mmq6FTs3Q0LskD69mgFjwubBNAUPv36eJu-5xYzOJuJTR58vQy8hVO6ikTxMc96EhDgSxQeqEhl3NCV0H_3By4MP8B1NR8tfgBOlX-rV3YR8wHggV4aHl3w_kQ)
11. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFtZz33gJaSb67MQsd2ctpMXK0viizGmjLhLq4QxJI3PGz6kf7nKHsYUUfDYIRmntgu9ZZm37nZqeehjdjiZ4tvv9DK_6ce7lzgg5fylMT5-UoC3IVww_AxUSuVpi_AgrAdm1IGFU10YI04-wOaoSgYqeWLwhfF7hufvkKnwULoxwmIWJmTopEMLki9pTxMm1-Cci2TP7-hMR2KMjUFy3tkay74pXlSW2XMQ==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKQQWEXx52XHUkEca5uryzK7EfdgJi_Qb7BO-XAjjqQ2p8XHK6S_te325F82Hn_pMnhTNyhqAvEH3wGDzxtWnbDtCPXr1n0NkHIKNsX1QMzhhkHJZJNC_B2NZfXcIAFiCXQRAYxY3onxn9EiWVtxKOWVLvTjQoZjJ3gNcXEcBCRkM5KQtd1EXjOV-Yj-hO69eHcrnrojlemcod-oqFSpTu5PkwcGsrNYyNhdc1YdroBr0K-OlgqjCtCnuCxgVxwKqEgInphihxOnQ=)
13. [mondodigitale.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFry3cXZQuMM9R1GUljEjNUKEvhvxkWeSavbgd9INEn7eWNkW5hhcnCaz8uDUR2xwHjBiN9rxvwXp5ALOZbnYMm0gaJ4a8HjhHzxK04ZMa4o4hGCE0JqaJWd0S1VsOOQFTef2ObD3MN-LgsE_yg9W6yYMbyQsGAfkwN)
14. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMjyBLvDIQCWW9k1MmzmmrfQrC2oEAx7anyOPMnSbHz1MCWqWHqQL0eSBbKvhwe6_1JqcwwjBfol97Zq1bRlZXjpuatYL2qzhAXpiHd_OYegJvVT8bfVPxhBIHiwQHf_MGbZtV2DpR0hWdn3VjDHX-A8qSOH0a23aMe-d4D-geuUeuAxldQMFRTyYsoMdEhSMgAZ_g2Brm5Ef671x_fc0tOvWhPKPnj4TFCix-id9zbS1FLJt9z4zG2DnRVfMoYw==)
15. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG69YG7x0HZ6S9I2dOB1vcRdwRpNZAyPngV5HA6QsIQ_7r-lwauqESkWouEZuZNrC5ejVVhLNVPwjmgrx02bKs0X6Uj1CckBsWKv4YXwIqMwsY331BpCfQeK5rfkYHgFg==)
16. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc46isGNHUZwuTMVQlbgjdhk5fH4W1yKtW0GBvY77mtbxfS1vj9DTnS5LWfTBdzQteSXbuBM8KWel9n1fWXJyRrlHe_2SVb04N_h_VOjwYb55gI0oFN-ZMU4K1CHBgUYkViOQWSrPh4A==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqmOzwx7tsT-sr_ayrHhKiuUODznNsjTOqeSwDNtwnDvPLUHQyByFBZ6DJ-KSYUr_162Pp6aJQmWoy0Aft3zcTuSvbcgrxtTkd9pJIHOsQutzKh85OhvPpgQ==)
18. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED5RHkKNbSktL6fmo8GaTXrxcZzuqnWT3XwL8ihi5JWfazKV9IQAALAdJKCAVi6Sn2yxMT1lqrg8uL47Pfk9zxcgozBcKFczGyJqO_bV76WjVv0R6LIHMy5rpKpjBlysRW_FHJkkv41QkH2kT4tiw9fxHf2bjaXbLossCzfKNoGg==)
19. [oecd.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFElBeyN1LAT0-XZZzZyf3K5Ei95dcCXd3YQrgssg5mLgfE9-eO7k1U5Ym5EKJi5eRJTEoPrDhrhqv9PcWGpDJ_4-js4bJ-EN9TQ5YQmlzmH1BqFxzcJZWHSGm8dczz1fu4368ntz9QouE8jllDykWjzBr9PFzroLGv2UAJ0I_r37EOCy9E3AYT91dqDiTwBaAOBzYpy-tLnQEn1c1gkAaa4cmT7M223HSGwmPtx8whdNuW8tXKiahfOMX1SKNfaNBOiY2FP3jEmvsewgO7LV5XQ==)
20. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRJ7fTBCAk7AdT87uqndC_bt36KTLdL96H3IfV89w1ewd1kv3Cu5bNqHOdb8ImtsHHV6ARu83YdRAj1D9iSmMIIxlpFXjZr5gaUNVlbneorFJwj7iNBR3c5XQWyWhNDA==)
21. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg7sFFm2mLuFr9X9RE6gxT8RFmk6LXSK4vZDVlnNTy5IE20V98dKkYOL8Nex5_dEM_OnZP1cymKKSM6j14RPMzbc5erg6xVvQD5r-n2HGnS-UbRJbPa3QyhEbzeEB_4Gp_HpMl8KZmaiAtRXJTMMcHeSAS7vb02CqVg2-gKd_rsaTVv1fuvcqnhqN9UXpDMFJQ2wg4Sn1MjVjORkk7DDFulMKJJgEYe3jS268x)
22. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGI5TIeWJg_kdpsMLBvK8MaH9MAS-Vgj5zFvJLE2ZgJPx7vp7inzy8blWbbHnB-jEgSVPxcKBb5bv2HaANF2yMAMZHmdQFKimW67EVKAgucucHmq4zTAbaDdrn32I0kDg==)
23. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJpSLM20uJCo1M1_MBnjHMOp1WJPCdpmiA2hXy3Ic-FHEWJjQ3F6JSUjmIfbvnCadFHVE5-InsY93rAynFuNzGYhT64tpwnZ_eMIjLJBSChCcmXtgWHG8m5LSh7HSSQVIh0_cNI9jV)
24. [benjasanchez.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1Tpty3IFKrOFyGnY-r0PElMZghpHnNj_TcG7eFrU3FP40gjjLNeFq9PsojwTvmKajTYoLgWv1agMzAv1xXQzg8LbvLqhuKh4IcyljmJtTLQNSIGWG-WoCrL8hSdBEvBdFdi60bUNy8byCBb8Nqg==)
25. [ntu.edu.sg](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ7iFcJblYOpYhAsGnuHLidlxXhDuzwtZ_Q6Yl2l5J2ITcvPpOArJPjSppeKFpsPIFaFmPcraESaZJE8eN5Dd1saFGaRFugPTdHcfV-MOZAHCy_PlH_84KxuXjDRCRP-tkqRzVjLZBSqMAH3RO_TMPU9Y_tn9ZRgl3ub_OmJE2C4zdjxu2)
26. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF70YRP7LCX_6BSlebNSmE3d32BlF2gOKDL955YK0pXrhF3u5Q_Grf6eKf-I4Qv66Yqppuppk4spi-0N6MNjTjoThKzPjQjOki0NiLbi61_PjksRofRBMgAusITvwI5-ozJMacR0D09RThPqFRopBZNxVq4UlVo524DHgj9yvO4RzLRzxxm70slSe-FY9x9Se3Y8BFvmHWViivm4J1qS1V-ANnzXYuHcXIVsHKZmI7nwvr7L7XXOAF98SXYujlpIW2dxBrNGVQ=)
27. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs5iLXUMql0mhyIsgAFhzUp1qAOHesA841DRT8gjvN8xaYrKmq8oQKEkbnuR8oH-pmwqhLCYz7P2ZwdD9NsewzxgMT1oXRamCGMLeM3NLnlfkOFsqL15cR_L1K0zkKNg==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiozmOIoidZWc0hVV5QKFmkcD7mQYx8Vw-KUKoDUYarZgHp-ga_Bgem48AqO46gQm-CIIl13HyetWreeGAtNGG5jrqbErCfusU3jxDlGirjoDFx3rPpRWz-yNsrtEgMJp-m-Ug1EaQO5meLUJlKXPeIrlf-jTLAEBbhDifhlK4TBf0Cc--HyLwNo6lB1R2iWS_8OJsVi7VrSu66VkGSlYaMr1NfaX4Cn2RmtlJk_3qpdKtH8JyOFE=)
29. [gautamparab.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRR-59eKeVhh6lV425BTkTmMQFJrdcQP_m7gyDS4Djva-IPoTiMGefsYUfSk7QePAAIGvlPQwEFhKw7dFTzad-Ns1WB6Mk2TLfYIWNeIw4ZLWcXjlcD1HGUAjdMjG3nvDa4IrC6HuTu466ZeYKE_DfyPUq-RlhKA==)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFp1drTQcjJXthDmOK5acMXjvEAjGnC5igMN9YDl43Iq3-xDVO_kdnjUKXwTIavkiqe55kE5MDqOT0PM7owTmwrDkZHu7PVgLvhIBIwA5ayRF2gEi1n2AEvCMv0mrWs)
31. [bioprocesstools.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBTakOz7DGBp1x94kpzW7Az1bAV4oAxEDpMs7SIDl7AJNtBSvMLnE1mZ1X9Zk2bCEljJJL35myF3zFYSWkoFq1Ny7AimkHC26xpogctmXe9il0pCSkmG0VsHBdLAwKItySVZdaiF1G7FvdM3gxXG1hxMJdc_XLZaHT)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoo6W17toNVFeY7nyoFXnIDcrUPJcXvb_4420zCQxgpH_emMSFJ6dMqvWYnEBJAyeH5z2scCaYe9i5-PeaNd-Gc1E7_G3fc2ZAwLSyZAtxtxfrkKt_diYuUsg=)
33. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3FJmtusrsAXSF5Z8X9GyS05XIXKDLrHV-cu_dvl7RdAdwyvPIzwcmXwzKzUXJD-10SVaNoT5Mia6NBEYTiQ7CT5VMSzBRo19w9f3dVlxH6J-lDqw7nopyaaw=)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS6E_SNtWi1vFnQum1Fdkrqj2OYOpY3iE9jrNa0d-Gh-9u-UxNpS1xmEpvFCEjVFyJazOuF-UrotcmYvij7Iji6aV49Fm1AdqqzcA67PI_56tFqaswmDmTW28MjQq_-TL-)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJgSjDXBLzsV2w1Mp1L3kM2iPlGMIMbJSsOteLaVfR51pvMY71LAZ06FMrrVxzU15EoDp21cCDYE_XOLme-bsWl_ecWsww0bqL7HseeNxx4zjoQ1squNLZ75zoZjq_99d52BdzuMv6U_XiOvR0hBNIDkkFhPGRMcUgMnYqrnMnzeWkFrsOQ5dU-R4VEGkAwTlT4ltX4yw-BWXh8DP6TU1n)
36. [drugtargetreview.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2w8LQ2B_OSHxgXxoQjYL5v6su_cbQZVhhrZkaEf3s_ZFc51M1kg6UMTqxHgXAwggQ8ljGNrNeIE_WRD8BY1MM73xa1AeRByOW7oAEKeErVF1dkLd6mXkFEEdfpFkI8vKxAXa2-DbwoXW5LsmdmLTvMp3ONws2JHd7u24B8y1C_toLHpldx0yBbitNCPgwgcKmbK6oqiBeebsA)
37. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIYQD7ip-Q-ioVyqUFoFLIUULKuRl9kKAb8HGQN_s4pa4iwLL4bEWLZIHsaxsdmGxyQZdF6LuWygbtYYTdGPtFSzAHQUUl6w1n1y1N5CmRbRjOIv8X4vT2c9FaPyjmFR43eLuirm0M71HJN5Yzm8gq4dw=)

