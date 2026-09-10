# Prompt 97: Chemical Reaction Networks as Computation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYi1mYXVEVkFwYV9fdU1QMmZEcmlRdxIXYmItZmF1RFZBcGFfX3VNUDJmRHJpUXc
**Elapsed:** 910s

---

# FRONTIER PRACTITIONER DOSSIER: Chemical Reaction Networks as Computation

## LEADING PARAGRAPH

The field of Chemical Reaction Networks (CRNs) as computation explores how collections of interacting molecules can process information, act as control circuitry, and run algorithms natively in wet-lab environments. 
*   **The core premise** is that abstract chemical reactions can be viewed as a programming language where species counts represent state and rate constants define execution speed [cite: 1]. 
*   **The computational power** depends heavily on the underlying semantics: deterministic continuous models are computationally restricted, whereas stochastic, low-copy-number models (simulated via Gillespie algorithms) are Turing universal, provided a non-zero probability of error is permitted [cite: 2, 3]. 
*   **The physical implementation** relies on DNA strand displacement (DSD), allowing in-silico CRN theorems to be compiled into actual nucleic acid sequences [cite: 4, 5, 6]. 
*   **The current frontier** is defined by a shift from static test-tube logic toward machine-learning-inspired topologies—such as Recurrent Neural CRNs (RNCRNs)—and the highly contested effort to make these circuits function reliably inside living cells and cell-free extracts [cite: 6, 7, 8]. 
For a computational scientist, this domain offers a rare bridge between pure discrete state-space theory and physical molecular execution, though it is currently hampered by fragmented software toolchains and the physical reality of unintended chemical leakage.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Chemical reaction networks are formally bipartite graphs mapping input species to output species via reaction nodes. As a computational paradigm, this field treats molecular concentrations (or discrete molecule counts) as registers and mass-action kinetics as the transition function. The field sits at the intersection of theoretical computer science, systems biology, and dynamic DNA nanotechnology. When simulated at macroscopic scales, CRNs are systems of ordinary differential equations (ODEs). However, at nanoscopic scales with few molecules, the dynamics are governed by the Chemical Master Equation and simulated as continuous-time Markov chains. The field exploits this dichotomy: algorithms that fail under continuous deterministic logic can succeed under discrete stochastic logic, leveraging random fluctuations to break symmetry and explore state spaces.

What is SETTLED: The theoretical boundaries of CRN computation are rigorously proven. It is settled that error-free Turing universal computation is impossible in finite stochastic CRNs; however, if an arbitrarily small but strictly positive error probability is tolerated, stochastic CRNs are Turing universal [cite: 1, 3, 9]. The physical substrate for abstract CRNs is also settled: toehold-mediated strand displacement (TMSD) is the undisputed standard for compiling arbitrary CRNs into physical DNA [cite: 6, 10, 11]. The logic of using short overhanging DNA domains (toeholds) to initiate branch migration is the undisputed foundation of the wet-lab side of this field.

What is CONTESTED: The ability to predict the physical reaction kinetics of arbitrary DSD networks from sequence alone remains highly contested [cite: 10]. While thermodynamics can be reliably scored, kinetic rates often deviate from theoretical predictions due to transient secondary structures, toehold occlusion, and blunt-end strand invasion [cite: 4, 12]. Practitioners heavily debate the appropriate level of abstraction for simulation: some argue that sequence-level simulators are the only ground truth, while others maintain that domain-level condensation is necessary to prevent combinatorial state-space explosion during verification.

What is OPEN: The translation of these circuits from idealized, buffer-filled test tubes into messy biological environments is the defining open frontier. Researchers are actively attempting to execute DNA and RNA computing circuits inside living cells and reconstituted cell-free systems (like PURE), facing immense challenges from nuclease degradation, molecular crowding, and competing background reactions [cite: 6, 8, 13]. Furthermore, the field has recently expanded into chemical machine learning. The design of Recurrent Neural CRNs (RNCRNs) that can be trained to approximate arbitrary non-linear dynamic behaviours represents a brand-new frontier, moving the field away from traditional Boolean logic gates toward continuous, differentiable chemical learning [cite: 7, 14, 15].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Soloveichik, Cook, Winfree, Bruck
2008
Computation with finite stochastic chemical reaction networks
Natural Computing
DOI 10.1007/s11047-008-9067-y
This paper establishes the foundational theorem of the field: finite stochastic CRNs cannot compute Turing-computable functions without error, but by scaling an "accuracy species," they become Turing universal with an arbitrarily small error probability [cite: 1, 2, 16]. A practitioner must know this to understand why all computational claims in stochastic CRNs must include a probabilistic error bound.

Angluin, Aspnes, Eisenstat
2008
A simple population protocol for fast robust approximate majority
Distributed Computing
DOI 10.1007/s00446-008-0059-z
This source defines the 3-state approximate majority protocol, demonstrating how stochastic interactions can rapidly and robustly achieve consensus [cite: 17, 18]. It provides the canonical benchmark experiment used to test stochastic CRN simulators and fault-tolerant network designs.

Qian, Winfree
2011
Scaling up digital circuit computation with DNA strand displacement cascades
Science
DOI 10.1126/science.1200520
This is the milestone experimental paper that proved abstract CRNs could be scaled up in physical DNA to perform complex logic operations (calculating square roots) using seesaw gates [cite: 6, 19]. It is essential reading for understanding how theoretical networks are translated into wet-lab realities.

Badelt, Grun, Sarma, Wolfe, Shin, Winfree
2020
A domain-level DNA strand displacement reaction enumerator allowing arbitrary non-pseudoknotted secondary structures
Journal of the Royal Society Interface
DOI 10.1098/rsif.2019.0866
This paper introduces Peppercorn and formalises the translation of domain-level DNA interactions into abstract CRNs by enumerating all possible pathways [cite: 20, 21]. It is the critical text for understanding the gap between high-level CRN design and low-level physical leakage.

CURRENT SOURCES

Dack, Qureshi, Ouldridge, Plesa
2026
Recurrent neural chemical reaction networks that approximate arbitrary dynamics
Cell Systems
DOI 10.1016/j.cels.2026.101572
This defines the current algorithmic frontier, showing how modular chemical neurons (RNCRNs) can be trained to approximate arbitrary dynamic systems [cite: 7, 14, 15]. It signals the field's shift from discrete Boolean logic to continuous, trainable chemical machine learning.

Jung, Collinson, Hawes, Fellermann
2025
From the Test Tube to the Cell: A Homecoming for DNA Computing Circuits?
Intelligent Computing
DOI 10.34133/icomputing.0112
The single best modern survey of the field, this paper details the push to move DNA computing circuits into living cells and RNA environments [cite: 6, 13]. It outlines the physical boundaries of the current frontier, making it mandatory reading for anyone designing networks intended for biological deployment.

Jurado, Pandey, Murray
2026
Nucleotide-Level Chemical Reaction Network Modeling Enables Quantitative Prediction of Reconstituted Cell-Free Expression Systems
ACS Synthetic Biology
DOI 10.1021/acssynbio.6c00163
This paper demonstrates the frontier of cell-free CRN execution by creating a predictive nucleotide-level model of the PURE system [cite: 8, 22]. A practitioner needs this to understand how in-silico models are currently being calibrated to match complex in-vitro transcription and translation environments.

Ouldridge et al.
2025
Design of DNA strand displacement reactions
Current Opinion in Biotechnology
DOI 10.1016/j.copbio.2025.103396
This review dissects the physical limitations of predicting kinetic rates for single strand displacement reactions [cite: 10, 11]. It is crucial for computational scientists because it highlights exactly where and why physical DNA implementations deviate from idealized in-silico ODE/SSA models.

Doty et al.
2023
Discrete chemical reaction networks for optimal information encoding
arXiv:2307.01939
This paper links CRN computation directly to Kolmogorov complexity, showing the optimal number of reactions to generate a specific molecular count [cite: 23]. It establishes the theoretical limits of physical memory and succinctness in stochastic self-organization.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Bioscrape
https://github.com/biocircuits/bioscrape
Python, Cython
MIT Licence
Approximate year of most recent activity: 2024
Maturity verdict: MAINTAINED
Bioscrape is the community standard for simulating both deterministic (ODE) and stochastic (Gillespie SSA) CRNs, offering single-cell simulation and Bayesian parameter inference [cite: 24, 25, 26]. You can use it today to run the Approximate Majority experiment, benchmarking execution times and probability of consensus. The primary limitation is its installation pipeline: because the core engine is written in Cython for speed, it strictly requires a local C++ compiler, which frequently breaks on modern Windows toolchains or unconfigured macOS environments without Xcode CLI tools. 

Peppercorn Enumerator
https://github.com/DNA-and-Natural-Algorithms-Group/peppercornenumerator
Python
MIT Licence
Approximate year of most recent activity: 2024
Maturity verdict: MAINTAINED
Peppercorn is the authoritative tool for discovering what a designed DNA network will actually do. It accepts domain-level specifications of DNA strands and exhaustively enumerates all possible interactions, outputting the complete condensed CRN [cite: 4, 12, 20]. Today, you would use it to verify that your hand-designed DSD network does not contain unintended crosstalk. Its main limitation is combinatorial explosion: if the timescale separation assumption is violated, the software will attempt to enumerate implausible polymerization states until it exhausts system memory.

BioCRNpyler
https://github.com/BuildACell/bioCRNpyler
Python
MIT Licence
Approximate year of most recent activity: 2024
Maturity verdict: MAINTAINED
BioCRNpyler is a modular compiler that translates high-level biological specifications (like a DNA promoter sequence or cell-free extract definition) into exhaustive CRNs in SBML format [cite: 27, 28]. It acts as the frontend to Bioscrape. You can use it today to build a complete model of a genetic circuit inside a PURE cell-free system. Its gotcha is that it requires deep tacit knowledge of biological parameters; if you instantiate a model without carefully tuning the transcription and translation rate dictionaries, the resulting CRN will compile perfectly but yield biologically nonsensical dynamics.

KinDA
https://github.com/DNA-and-Natural-Algorithms-Group/KinDA
Python
MIT Licence
Approximate year of most recent activity: 2023
Maturity verdict: MAINTAINED
KinDA evaluates the sequence-level kinetics and thermodynamics of DSD systems, bridging abstract domains to actual nucleotide sequences by wrapping NUPACK and Multistrand [cite: 29, 30, 31]. It is used to extract precise kinetic data and predict spurious secondary structures before ordering DNA from a vendor. The massive limitation is its dependency tree. The canonical implementation relies on specific legacy versions of Multistrand and NUPACK 4.0.1+. Practitioners bypass local installation entirely and use the provided Apptainer/Singularity container, as compiling the toolchain locally on modern OS variants is highly prone to failure.

Visual DSD / CRN-Engine
https://github.com/microsoft/crn-engine
F#
MIT Licence
Approximate year of most recent activity: 2021
Maturity verdict: DORMANT
Originating from Microsoft Research, this was once the flagship suite for programming DSD circuits [cite: 31, 32]. It can compile its own custom domain-specific language into CRNs and run simulations. However, it is effectively dead for modern development. Automated GitHub workflows have been disabled due to multi-year inactivity [cite: 33]. The canonical implementation is unbuildable on modern .NET 8/9 toolchains; running it requires explicitly installing legacy .NET Core 2.1 and 3.1 SDKs [cite: 32]. Most of the community has migrated to Python-based tools (BioCRNpyler and Peppercorn), leaving this software as a historical artifact with a highly specific syntax that does not easily interface with modern SBML pipelines.

pSSAlib
IDENTIFIER UNKNOWN
C++
IDENTIFIER UNKNOWN
Approximate year of most recent activity: 2017
Maturity verdict: DORMANT
This library provides exact partial-propensity stochastic simulation algorithms, historically used to benchmark SSA execution speeds [cite: 34]. It is noted here as a warning: while it is famous in literature for reducing computational cost in strongly coupled networks, it has not seen active development and practitioners currently prefer Bioscrape for stochastic simulations due to Python interoperability and active maintenance.

PART 4. DATA AND BENCHMARKS

The field of CRN computation does not rely on massive static datasets like ImageNet. Because the networks themselves are generative, benchmarks exist as canonical theoretical tasks or targeted experimental kinetic measurements.

The Approximate Majority Protocol
Access route: Procedurally generated via 4 predefined reactions
Approximate size: 4 abstract chemical reactions, 3 species
Licence: Open
What it measures: This is the authoritative algorithmic benchmark for stochastic CRNs. It measures the ability of a simulator or a physical network to amplify a minority/majority population gap into a unanimous consensus despite stochastic noise [cite: 17, 35, 36, 37, 38]. It tests expected time to absorption and error rates. There is no overfitting problem, but researchers must beware of floating-point contamination if using poorly implemented continuous relaxations instead of strict integer SSAs.

The Seesaw Gate Cascade Benchmark
Access route: Defined in Qian and Winfree (2011)
Approximate size: Varies from 2 to over 100 logic gates
Licence: Open
What it measures: This serves as the physical and in-silico benchmark for scaling DSD computational depth. It measures signal degradation, execution speed, and leakage in deep networks [cite: 6, 19]. It is authoritative for evaluating new DSD compilers. A known limitation is saturation: networks optimized specifically to pass the seesaw benchmark often rely on specific sequence clamping that does not generalise to associative toehold designs.

FPEI / Learndnakinetics Dataset
https://github.com/DNA-and-Natural-Algorithms-Group/FPEI
Approximate size: ~20 detailed reaction trajectories
Licence: MIT
What it measures: A specific dataset of experimental parameter estimation for interacting nucleic acid strands modeled as continuous-time Markov chains [cite: 39]. It is used strictly to evaluate parameter inference algorithms on DSD systems. It is popular but niche, primarily useful if you are building Bayesian inference engines for CRNs.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to understand this field is simulating the Approximate Majority (AM) CRN under stochastic semantics to observe noise-driven consensus and compare it against the theoretical limits defined by Angluin et al. 2008 [cite: 17, 18, 38].

Software and version:
Python 3.10+, Bioscrape v1.2.2.

Dataset or generator:
Procedurally generated network inside Bioscrape. Define three species (X, Y, B). Define four mass-action reactions:
1. X + Y -> Y + B
2. Y + B -> Y + Y
3. X + Y -> X + B
4. X + B -> X + X

Parameters to set:
Rate constants: Set all four reaction rates strictly to k = 1.0.
Initial conditions: Total population N = 100. Set X = 55, Y = 45, B = 0.
Simulation time: t = 100 units.
Algorithm: Gillespie SSA (stochastic = True in Bioscrape).

Replicates and seeding:
10,000 independent replicates. Seed the Numpy random state iteratively from 1 to 10000.

Approximate compute cost:
Less than 1 CPU hour on a standard consumer processor. No GPU required.

Expected result:
The system will inevitably reach an absorbing state (either X=100 or Y=100). Because X started with an initial margin of +10, the probability of consensus on X should be overwhelmingly high, but strictly less than 1.0. The expected time to reach consensus must scale proportionally to O(N log N) total interactions. Compare the empirical probability of correct consensus (X winning) against the exact theoretical distribution provided in Angluin et al. 2008 [cite: 17].

The three most common ways people get this experiment wrong:
1. Using Deterministic Solvers: If simulated using ODEs, the system instantly deadlocks at a continuous equilibrium of X=Y. The protocol fundamentally requires discrete integer randomness to break symmetry.
2. Floating-Point Concentration Errors: Tracking species as continuous floats (e.g., X = 99.999) rather than strict integers destroys the absorbing boundary conditions. The system will artificially oscillate indefinitely at the margins instead of halting.
3. Premature Halting/Measurement: Failing to log the exact stochastic step where absorption occurs, and instead just measuring the state at arbitrary continuous time intervals. This corrupts the O(N log N) temporal convergence measurement.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Differentiable Stochastic Simulators for Network Discovery
What goes in: A target dynamical trajectory or a target steady-state probability distribution.
What comes out: An optimized set of abstract chemical reactions and their precise rate constants that natively generate that behaviour.
The hard part: Discovering CRN topologies is currently a manual, intuition-driven process. While gradient descent is easily applied to deterministic ODE formulations of CRNs, the Gillespie SSA operates over discrete integer jumps and continuous random variables for time, making it inherently non-differentiable.
The work: You would need to build a JAX- or PyTorch-based hardware-accelerated simulator using continuous relaxations of Poisson step processes (e.g., Gumbel-Softmax relaxations of the master equation). Several groups have privately rebuilt differentiable ODE CRN simulators to learn topologies, which strongly signals a gap for a robust stochastic equivalent [cite: 35]. This is roughly 6 to 12 months of high-level numerical engineering.

End-to-End Algorithmic DSD Compiler
What goes in: A high-level algorithm written in a standard imperative or functional syntax (e.g., a Python function).
What comes out: A list of DNA sequences mapped to physical domains ready for commercial synthesis.
The hard part: Currently, the toolchain is severely fragmented. A user must manually write the CRN, use Peppercorn to verify domain-level dynamics, and then use NUPACK to assign sequences. There is no unified abstract syntax tree that maps programming logic directly down to physical strand topologies while optimizing for minimal leakage and toehold occlusion.
The work: Creating a unified compiler that bridges the gap between BioCRNpyler, Peppercorn, and sequence generation. This requires deep knowledge of compiler architecture and DNA biophysics, representing a multi-year engineering effort.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Negative Result: Error-Free Turing Universality in Mass-Action CRNs
A foundational attempt in the field was to design chemical networks that compute exactly, similar to silicon processors. This was proven mathematically impossible. Soloveichik et al. demonstrated that under standard mass-action kinetics, finite stochastic CRNs cannot achieve zero-error Turing universality. Systems attempting zero-error computation inevitably face probabilities of incorrect reaction pathways. The standing answer to this result is that one must accept an arbitrarily small, but non-zero, error probability by introducing "accuracy species" to scale the volume and slow down the reactions, effectively trading time/energy for accuracy [cite: 1, 2, 3, 9].

Failed Programme: Direct In-Vivo Porting of DNA Logic Gates
For years, a major goal was to design complex DNA strand displacement circuits in buffer solutions (test tubes) and directly inject them into living cells to serve as smart therapeutics. This largely failed. The biological environment is hostile to bare DNA circuits. High concentrations of intracellular nucleases rapidly degrade the synthetic strands. Furthermore, molecular crowding alters diffusion rates by factors of 5 to 100, and varying magnesium ion concentrations destroy the tightly calibrated hybridization energies required for toehold exchange [cite: 6, 13]. The field has corrected this by shifting away from direct injection toward transcribable RNA circuits (where the cell continuously produces the circuit to outpace degradation) or using protective lipid nanoparticles [cite: 6].

Standing Critique: The Physical Leakage Problem
The most persistent, unresolved critique of the DSD field is that theoretical models assume zero cross-talk, whereas physical DNA molecules always exhibit "leak." Due to spontaneous thermal breathing, blunt-end DNA complexes can initiate branch migration even without a toehold (zero-toehold displacement). Furthermore, toehold occlusion (where toeholds bind to partially complementary random domains) alters the assumed kinetics [cite: 4, 12]. Critics argue that without active, energy-consuming error correction, DSD networks will never scale beyond a few dozen gates because leakage amplifies exponentially with network depth. While enumerators like Peppercorn attempt to model this leak by condensing slow reactions, the critique that purely passive DNA computing cannot scale to microprocessor complexity remains essentially unanswered by physical demonstration.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Execute Recurrent Neural CRNs inside Reconstituted Cell-Free Systems
What it is: Implement the newly theorized RNCRN architectures (networks of chemical perceptrons designed to approximate ODEs) [cite: 14, 15] inside a controlled cell-free environment like the PURE system [cite: 8].
Why now: It is feasible today because the theoretical mapping of neural networks to mass-action kinetics has just been formalized, and nucleotide-level models of PURE have recently matured [cite: 7, 8].
What it measures: The ability of a chemical neural network to dynamically shift between programmed states (e.g., from bistability to oscillation) upon receiving a molecular input.
Falsification: If background cross-talk, nuclease activity, or resource depletion in the PURE system prevents the necessary separation of timescales between the "executive" and "neural" species, the RNCRN architecture is physically uninstantiable.

2. Differentiable Discovery of Fault-Tolerant Protocols
What it is: Build a gradient-based optimization pipeline to discover entirely new stochastic protocols that outperform Approximate Majority in either speed or species count [cite: 35].
Why now: The advent of highly optimized, GPU-accelerated tensor frameworks (like JAX) allows for continuous relaxations of discrete state spaces to be computed at scales impossible a decade ago.
What it measures: The minimal number of abstract reactions and expected time to consensus required to solve distributed computation tasks.
Falsification: If the discovered networks rely on exact, highly tuned floating-point reaction rates to function, they will fail catastrophically when mapped back to integer-based Gillespie simulations or physical DNA, proving that the continuous relaxation found an unphysical local minimum.

What will NOT work:
Attempting to build massive, feed-forward Boolean logic structures (like 16-bit ALUs or complex cryptographic hashers) using raw DNA strand displacement cascades will fail. The physical leakage, synthesis impurities, and slow diffusion rates will drown the signal in noise long before the final logic gate triggers. Raw scaling of deterministic DSD logic, without fundamentally new energy-driven error correction chemistries, is a proven dead end.

**Sources:**
1. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-0lDcaKUuceVD6T7q841osZPllEUZlKyg_iHZaDF0zCbUWET1DYIelyARoUXCg0C6R4ZPTp7SnBZ05iWp9Uj_Mm8YnGUqoh4wygTr3mFmSXg0MrvEt-vfr84jpxKfnyHmYG2_QdO7n3aEC_WhFDBaRhRt)
2. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEniWFJN8VYYm-lu1bWglFzXHsIHx4X59_dQQ1CW4oQwjkslKYsA-I0ueZkyNCsMp5-6UYD0Q2USLjBh1T97KNg9ZHbwF0jF4v4p0VB-6hBhPskzZoJuABZ6zWFbUc3w-grdOulCVRIXrKDrmI5gsA=)
3. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsXEsii1u7vIP6QpMnoWtG8qcXRUGjxwkt3IfWcdzDLbTCE174eyCgdz1VOkgmVv0rakQ7IywA3AH1gbncJ6Kdlv6cfInbavIe09IHlbT-n96gaRMKC75o5w8-A_BTuhKoXsaQMrHv-u_DIdWlbk34Ze9O0vbpppxLEuLU)
4. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTJJ-EhvITHr0YbX0rkOFygoKawGl_W8vKRppS9o4w6uKLc7PRo8Za3LUvguyMQDqRd5uanm9BT_AjyocMA2NxXdtVj4DZr0e19PWHz2lqODZvv3d4eMVZf0Q_YsYhM20drTA7IhAqKPtIZQHAWW5pvbU8xEbbST0sQCeNUOoP6wOFnRwJJY0ZoeRFdNJjkDtIV6h16Td4HhrQGET9nU4BFp6N6zT-gzZRgA==)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElx8f5cSWWQ_09eMz8uQEPiyLGOnQJrAN7vYQJLfIrgITyamgTMM9_fZLN42JBwkYzjsVyXguF8u1TWuaeyxB1GqmDJVNg-OKMi1qfvsJ8-xYQybFzVigNbyclFjM3j--IJZxPExY=)
6. [eurekalert.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVW8JmfQN_2LVGm_z_ICsw4Y0ZBAki8t2QKbLH80Pwg5AhonoLZFYIxzZagcKxOtYhorLMq787c2q9ikTkn53J94l2yqG-cXQ3gMJBwztTyQtCldJ-XNrNlhv4vJA1fUsVXHDaxQ==)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1RFBJ8uOShQ03g0Im6fIKUEfEzT77lMLgj0Nq46EhraY_7XWCSSoQSeUmDoP9JQKjKvKB2Hi1mltx8EO2v9CveDFRDTqGpozQC4p5mAaIh1yhZ3_Lgsk6zwS9RY-j)
8. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm29XdG4O7tKRSjXEKK-DQM55AUfKfyAAB1hvipp-xs8udQPhAs4J5bjAtY7Q-o-jVJ7jlrixH4jrpCdZBTBip9Ut3dxFHvB-XiyJtU2SgZFVygj_7UpX4D05675-H3uAo8FXTrWIa)
9. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5KSDM41NBRzFUVNyT_nW0qSS5mchm2lBPC78A3FXujb0klJ-jv25FghUxliTB06HSCP7Zm6bG9GDtrgKFiKbjyeycAg9BkqDkOSjCUVAlpHZ9hlWYBE8OhPSjVVDYAs3LmWNk3u-f_WdmTahywhKnfZu2821XkMW8R_fU9x07gcQCZA==)
10. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwdN5Egn1-V-SYS0A4kGjyLdGCmlIIUd4m2BtOFyo2aWYTActqnNYNjkn398XvnW59uE8U7d3C10n_sNb5QyX1gshBJ7sEgZhAPNYE88-NeJpZv5d9Fpue-Mh02vwjFYoyVjf-SxyGOlys7j7fX0TbOuvQdK_ES8TGYFv0KHZrx-6G2etjP22-ybDM48eQs26mwVLHrIjJBe0W)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-J4NsU_12GKA6za39jpKNZ_TpDfpMk2yG59mBfW3HXo5n4mhQfGgpfyHcKZyPR62-eSvb0HIDmQSn_D7b-anJnHREdtXTsTP4mvAUxiXfPRRwOvvdSUiG)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDI52ws7NN7J_E8NTpP5u3jWep9M2ZlaIzBJwxTS_7spsnQLFG5jrjGGSF5iQP88x3P2johVQC6-WOvvCtT3xzYszseIlN-9fMINwvrfhovbFBEa9pTKQAfImy7yENQB7tmA5NFbEUfpzD7Ta0OpYzZE1vIvfYi-koXCHGhAT5AYB-cUkmB-lt9w_QTjF-OhgWxIX4JXzvYEG_QfJpMv5GMDuX9lNjmNXsZ3VeNeBdr-7MQs-ClYs=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOz23zZFOYs7vEowPqJPbLrjZB5fAQiK418lmyyNBmfiPQo5cHVHb5DdR-PIhYsTj1MHquDy1IqtmJ9jGiG5ycrlPYoijr3CFVzRlB80vVyhbs5yaTmk5U3NSfIIoh5kPHOI-zi_P5Ggt0WuG6t63ZQ68hnJ8bddU-jnAo2jwuP-Xay_ZcApr0L-6u7ULvLgVO8hq6HubPqG8=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGav1MY1HMdfe2bCrCZCupHc2TwgnjTbCicA6G8qni2IsrSWwqkaMOOR20-U74t2D8UfchfUcXKXFr__tnQacA9xUB8HZnGeJRdgKcYBK4VZdv-NTZE)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdu7iMf01WW6z2KP2Dnc9EfcQmiFo6gcA8CJC5Qk5TXjZkd9Q6_uqgsiRGxoLwiDkc6UQpEgqnnaJp0jLQ6Hn5WPAZtiejJ6BP4J2yHGzPHqWKkOQS)
16. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbjrrIXY0zc9NcLdZMsUI4bVI7PLOU-OBf8-9poODSarYkk-_h9nyLJ5zixLynSqUXlfcZtBJZH2xeOqqlrUPGRWllbrLgiom9J2xAnWLPvk5jf5UQQFHPXG3TdsLsxmlkUsI70JBl)
17. [yale.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXqmQIAODgDDEr9V94f9iw255A3j32Z54gxYOIdigp_PxE0FSGzAuK9km0fb9bPM-k9aDEAbXA7CL2YXhmBvYxfcf1K1GJJh0lkl_J40Ar3hS7xd-KtsjsMlDAzHbL-HKbBJXTpTk4oJ45ybaG6251trA2jii7Bq5_woErbFpHxd2XshyXlL3ny_kHgY7pJRHFGVo2IQjJBg==)
18. [yale.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVptAdHEBdaTOFRaX5Qtiqc63tXHJbqJt81tpADr3-q6br5HeUmGyJGjofCclXwG5qSQttRA3Z97jnYkN1qM34ax9dWPfDJqOrk-aAngi62kCfwgaPV2AXsC262IS7xDN0WF13NPc6FOi1RjTHC3CaTfnz1HPxvIWGZMSS0Z908GMAcQ==)
19. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpvYFUZ29d6VIDx0QAqa653S5E8hGn6NqJ0Eu63Tjq_SIsLkEf9Gb6GwifIYMVh5Bfxc8fNHfkZ3Dxovo1-9PO1Pa4gveovIU5NK_huHeXBzbVHjrf0JwKmt0NQHdtiKAxRqeYc4RgaFbJpDe2pfECQZXKyZzQay7YUQlgofFzaiViERmrGGUQFvOc)
20. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe3XiC1UUx3APUXGvf70xo9OoHK7VZNUGgWmzdj5FTLajp7-IGtDNOmJ1voZk9hQhrgFVprP7x3z_R6CdrMv2soeqt8vfkHe0sbyy3QsU7Pls0yKztEak_UUdmI6Lp)
21. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGiAqR4V7NGjUUspEWGRJpkkVP7Vs0UA0TXGw5SSsrSkC_PTFFHb97Zwr84ZdLXVLv-nnOLkHTm_5ZGVT9tQeeaOVqIS-qks2-UwJJELRS6tNuj6PF-1Tja4H4hGUpx3adu4Q7kt3pRyAJeX-bhpJTEQv6Zl68Ycw=)
22. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9CHP9SdDw4dAu8wROcrspn6s-S5q3f4-x7WPJIYxOfHuSR_lN87LpDMlKvHRJDGeI4ovnpwowCpsBsdfmEK1ZiBc8XWZJt5I4YUpTjdCg1updtgGzgozeCWhJ83dTO2dCY3PDgJiBLB-c9w==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzckPM16wQWyzuD7K2rfgeus66tjikWRIE24zcvBS8n9hVubuMwP3Y7h_ClVLZFLQcHWXFDnXcUGbwIoxxJWoHtt8pBWrZ3XT2Lr7AVqysbK5hCh0C)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm8QKIoRKXt8jQnQzqMtn_N_2rK4s887YlPTIXzkZCyuS0rN8-OlGPWHP_k6rFjGlgcxdO5mtT0r4tytbSEKd95ORfuYCdEHiR9sX5wKHgaBOnmXX5zhC4P-A6JzfZOUGi5hbjyrHRZeFWaIZY1A==)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx0bT0so4oygxtqAOsXIBhPbou5qI_Q6T-VSgHru82yTuwIMARj30peEIsgTifVpbZUf4c50VWjXXSSV0lnTMkwTuAWcJpsIDtBGkxlSf37mV_C_Kzs9lnvA6U-pc=)
26. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj0X1vPeA0fBUJWlD4adguYJF9limCxcdJPB3mHTugK_xuEYrJ5t8teOkurPk5VMrVxP1ZygJ4LK_hGPdwgwb3fkwP32_aRMghZdvLiVv8kUmM5zDM1NlEd7OnzqPYGT4HtLIlCg==)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1VZSAyLgnzgDs13sKWFtkJeOJRVp3zS72N4oOGPug7dfkjvCSjB_lN09Hwc1rRWZxKzsL-OzcNEQPH-4RQ-XaJJXHUNr58ODhJCpjsUeFYaxpyhd77lpvoHNa4rq_)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5TJ-7ePncf3hRtadrZyABtFx2LgxR1URMnNuDPQjUFOercgCgyrcfzxiPFJEH8TSob_Hzy2CPKgMbFhtPLSnR8Wm0qgaCrwt7oWRP9MIQVJNKVnGSp1pEm7kV2mvg8pc=)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHllX6hltu5vu5FtEK7ARLNHUIOd7eHoWCZhmlncbCS8CRNXk-JgSHbNqi_XvhXISz5uQXpjvgDbKRULdTpFyiN3rh8zKvNAfCuLDSuY1dN5D81HuEMU1UR-oUzRxr9CiQxyjHmJ1pNOWIEd3ZWFwNztSomqQQ=)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzF-Eju25q_c2_tMNN4NfbBBghFsQgN4SGBGbc2StJ1K4gg8NQeFz1LjBKCgA6sjfm8o6228pfhDzszSGksbYT2oxzdaiL0deRxAQA4NwQ2SiW7Ms0TmmpK49TEuuRgTXwi6e2-um_Y54SRegsmQ==)
31. [igem.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUMbeYPJA8wdNikx-VchkGaDWtmGot2AdK6ocZZidjI9XtKMHMHxystwxE4Si4GAEtgOpdIh5udG9oEaNy_IHnN6oApFYuYVeUvEV-s_xg2GXQk4M6Ou_VhJLLL26AI_8=)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyPdGuVB-nwYTQxfQ_rPlgVk6YqG1ykrKtACHvmo5fNQ_JtKghosgufYodfNVlT3xZnya6tw3wjxCdiWDavQF77z3N-M5tqzE6qM9N4l3tpFQz2yizgqjvCwyzaQ==)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKsfHy1nRIs-3n1VQe2HzgVn_f2bfn-fQj67-rIPQpX8pyAbTfQmUzCZUKkKfu9RuwULtAXKdLn3ai8tiO5bUg9641QzgjbQnAAj0QIyjHOBK-43mxKUA-TDAZj6CgvfQb2qxdjyN2lDzPHGNPrQiFN_Fq0TIe-8--7JyozNMPS7ZbxA==)
34. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZGzXfXMJgUSvqsZpuxVtBFSM52QmLCwMmoBwTz4hYT-KG-no9nUsXoo5AmIA7ncqGCkhHzrnTSZYh2akP5seVPPzL8Dd2hW1Ijuu59PfzLkgJgY2cuTSuorpG1hLzTtKOEFSc9vO4_5-AstG0x1MHrfmIcodAtYzIU5inqTyxHG8vAQ==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjXSSHs6_kvjDL7XOpQ-ODhVIhOOIzThpGfEjCTXjBCwA3DDNiKuyKWZK6cIIecz6hMmw_I6mzGCr39cOoDkBtVzu4tOCyHZcYKUcfFqbU4yQp4B3lmBWZ)
36. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNWNx-5zo7wJvXdNaRFCEyqwIoMazb9L-BlFR0r3vYYOq9z0OrTmuEmbUOG6hiY5cjBsKeGb88jgmL-o1XZCsrwjVKu4wuv1ThA4-e3GrYmvpPES8Rr3-y1DUULgdhohR-5EM2iO0=)
37. [prismmodelchecker.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKD629MtKTnhsgXpJQsYyt_R_TIvNWqTrc8Zj2Nhzx72AivWciGghky5CZYDw46vg3eqszyjbWu2jJBdTglxMRxMbkDUHaIqmq5AcVAS-U1Du1hc35RNQy64DnyVsL9mpo_dE1HxmFz-TYkf9L40EVGg==)
38. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOpOUdTtIf6frxfl_tcmeN-ajG8wuVAOI1_o2-y02d4VweNGGGb3KqBaBikwzSNIAjBgM1aqz0LvZ_ibs73G9HYL1qGWU33EtkXCpC11meEwlOwhPPT22h_UVDuzsWX2HMZrBtr5J3NsWH_RWminiAaQ0vvj1NheFjIKswpOuCg80suHYJ6JTjBt4RCGIcDjntMjFyjjra-_tQvgQQMfSx4FRuIQ==)
39. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG44o2GJTmxwsq34Hh5Ss7bupAVeGZi6P1Udoi9HJUbPtg8LMj_7M0DzXZ0WPesEZWiLghyX8SXV64tjNlDSAor_eN1_liJVb-UyTLKwSszaNM8--Q4ARiqThKSjHVXInZlitvK0U_yEBcYDL_6)

