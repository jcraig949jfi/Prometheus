# Prompt 203: H2 evidence audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdOSU9nYXBxbUctbmhfdU1QbEtyYXVBcxIXTklPZ2FwcW1HLW5oX3VNUGxLcmF1QXM
**Elapsed:** 365s

---

UNTESTED

PART 2. WHO HAS RUN THE DECISIVE TEST

The decisive test, defined strictly as a formal comparison of a discrete cellular automaton driven as a streaming component with per-step input injection against both a lesioned/frozen substrate and a matched-random substrate using a fixed readout budget across sealed executions, has not been published in the literature. While the claim that a dynamical system can serve as a reusable computational component is the foundational assumption of Reservoir Computing with Cellular Automata, rigorous attribution of performance specifically to the intrinsic dynamics of the cellular automaton rather than to the random projection of the encoding scheme or the power of the trained readout remains unverified in a generalized setting.

Several groups have claimed the effect, but ran significantly weaker comparisons. They typically compared their proposed cellular automata systems only against traditional Recurrent Neural Networks, conventional Echo State Networks, or Feed-Forward Networks, omitting the frozen and matched-random controls entirely. 

Ozgur Yilmaz, 2014, arXiv:1410.0162
This is the foundational paper that introduced Reservoir Computing with Cellular Automata. Yilmaz claimed that a cellular automaton driven with random input projections could act as a reservoir capable of long short-term memory, and that the nonlinear dynamics of the automaton provide the necessary projection of the input data onto an expressive and discriminative space. 
What they compared: The system was evaluated on the 5-bit and 20-bit memory benchmarks. The control arm was a standard Echo State Network. 
Sample size and unit of analysis: An unstated number of trials evaluating the minimum reservoir size required to achieve zero error, mapped across different distractor periods.
Effect reported: The paper reported that the cellular automaton reservoir achieved zero error with exponentially smaller reservoir sizes compared to classical Echo State Networks. Yilmaz specifically noted that additive cellular automaton rules enabled efficient processing.
Weaker comparison explicitly noted: Yilmaz did not compare the system against a frozen substrate, such as an identity rule or zero iterations, nor against a matched-random substrate. The performance was assumed to be a product of the cellular automaton dynamics, but the decisive test attributing the computation to the dynamics rather than the encoding was not run.

Stefano Nichele and Andreas Molund, 2017, arXiv:1703.02806, DOI 10.25088/ComplexSystems.26.4.319
This paper extended the paradigm by proposing a deep, layered cellular automaton reservoir architecture. 
What they compared: A single-layer cellular automaton reservoir against a two-layer cellular automaton reservoir on the 5-bit memory task.
Control arm: The baseline single-layer system and previous state-of-the-art results from Yilmaz.
Sample size and unit of analysis: Evaluated across a selection of the 256 elementary cellular automata rules with varying iterations and grid sizes.
Effect reported: A layered system improved memory retention over a single reservoir, with specific rules, such as Rule 165, showing significant improvement in recall accuracy.
Weaker comparison explicitly noted: The authors did not run a frozen or matched-random control. They tested which cellular automaton rules performed best relative to one another, but never tested if the automaton itself was outperforming a static random projection decoded by the same linear readout.

PART 3. NEAR MISSES AND WHAT THEY LACK

The literature contains several near misses where authors accidentally approximated one of the required controls while investigating other phenomena. These papers often discovered that the cellular automaton dynamics were not responsible for the computation. However, none of these constitute the decisive dual-control test of the general claim.

Tom Eivind Glover, Pedro Lind, Anis Yazidi, Evgeny Osipov, Stefano Nichele, 2023, DOI 10.25088/ComplexSystems.32.3.309
This paper is the closest the field has come to applying the matched-random control. The authors explicitly set out to expose weaknesses in the 5-bit memory benchmark as it is typically applied in cellular automata reservoirs. 
What is missing: While they successfully applied a matched-random control by solving the benchmark using independent and identically distributed random vectors, they did not frame this as a test of the hypothesis across a valid suite of tasks. Instead, they used the control solely to invalidate the 5-bit memory benchmark itself. Because they did not pair this matched-random control with a frozen substrate control on a benchmark that actually requires temporal integration, the core claim about cellular automata as reusable computational components remains untested in a valid paradigm.

Mrwan Margem and Osman S. Gedik, 2020, Artificial Intelligence Review
These authors investigated cellular automata reservoirs on the UCR Time Series Classification Archive datasets. They reported a critical failure of the paradigm: the reservoir appeared to solve the classification tasks, but upon ablation, they found the performance was entirely due to the encoding scheme itself, not in any part due to the cellular automaton.
What is missing: Testing the encoding scheme alone acts as a frozen substrate control because it evaluates the system without the dynamical evolution. However, the study lacks the matched-random substrate control. It also lacks a held-out set of tasks where the cellular automaton dynamics theoretically provide a computational advantage, making this a refutation of specific time series applications rather than a controlled test of the underlying theoretical claim.

Denis Kleyko, Evgeny Osipov, et al., 2022, PMC9215349
The authors tested whether Cellular Automaton Rule 90 could replace a stored dictionary of random vectors in Vector Symbolic Architectures. They compared the memory buffer made from Rule 90 expanded representations against a memory buffer made from independent and identically distributed random vectors of matching dimensionality.
What is missing: This evaluates the cellular automaton as a static pseudo-random number generator expanding a seed representation into a larger spatial dimension, rather than as a driven dynamical system with per-step input injection. It completely lacks the streaming component, the explicit reset, and the trained readout on sequential data required to answer your specific query.

Caleb Munigety, 2026, arXiv:2606.09929
This paper explicitly tested a learned substrate versus a frozen substrate to determine when training a physical substrate beats freezing it. They found a predicted signature of band closure where trained models settle near the stability floor, seeking the edge of chaos unprompted.
What is missing: The substrate tested was a continuous network of nonlinear oscillators in the context of physical reservoir computing, not a discrete cellular automaton. Furthermore, the component was trained end-to-end using a symplectic integrator rather than tested as a fixed, reusable component with a sealed execution and a subsequently trained readout. 

PART 4. EFFECT SIZES AND BASE RATES

The trajectory of reported effect sizes in the literature perfectly mirrors the implementation of stricter methodological controls. 

When the base rate is evaluated without proper controls, as seen in the work from 2014 to 2017, the effect size of adding a cellular automaton reservoir appears massive. On the 5-bit memory benchmark, early papers reported 100 percent recall accuracy using extremely small parameter budgets, such as grid sizes of 4 to 20 cells evolving for a small number of iterations. The variance across different rules was reported to be high, leading to the conclusion that specific rules operating at the edge of chaos were uniquely responsible for the computational effect.

However, as controls get stricter, the reported effects shrink dramatically, often to zero. The sequence of shrinking effects is itself the defining finding of the recent critical literature:

First, in the uncontrolled era, cellular automata achieved 100 percent accuracy on sequence memory tasks, and the effect was entirely attributed to the temporal mixing of the cellular automaton dynamics.

Second, when the frozen substrate control was approximated on the UCR Time Series Classification datasets, the performance was found to remain identical when the cellular automaton iterations were removed entirely. The effect size of the dynamics on accuracy was exactly zero. The base rate established by the linear readout mapping the static encoding scheme accounted for 100 percent of the performance.

Third, when the matched-random control was applied to the 5-bit memory benchmark by Glover and colleagues, a memory buffer of random vectors achieved the exact same 100 percent accuracy. The effect size of carefully selected rules, such as Rule 90, over random noise was zero. 

If several groups measured the effect, do the numbers agree? Yes, the empirical measurements agree perfectly that the 5-bit memory benchmark is solved with 100 percent accuracy. However, the recent critical literature agrees that the base rate for solving it without any cellular automaton dynamics is also 100 percent. The variance in performance between different rules, which was heavily analyzed and charted in early papers, is now understood to be an artifact of how different discrete rules destroy the initial random projection, rather than how they process temporal information. Rules that map to a homogeneous state simply destroy the encoding, yielding low accuracy. Rules that preserve information, such as additive rules, simply pass the initial random projection to the readout, yielding high accuracy that is entirely attributable to the decoder.

PART 5. WHAT THE FIELD ARGUES ABOUT

The live methodological disputes bearing on this claim revolve around the nature of computation in complex systems, the validity of standard benchmarks, the mathematics of discrete topology, and the random projection problem.

The Edge of Chaos versus Disordered Topology
A foundational argument in complex systems is that true computation occurs at the edge of chaos, corresponding to Wolfram Class IV behavior, where systems exhibit both order for memory retention and chaos for information mixing. Early reservoir computing researchers argued that reservoir performance was directly tied to this criticality, suggesting that parameter tuning must seek this boundary. 

However, recent papers explicitly contest this requirement. Testing Partially-Local Cellular Automata and Homogeneous Random Boolean Networks reveals that disordered topology does not necessarily mean disordered computation. The opposing side argues that topology imperfections lead to higher collapse rates but simultaneously increase sensitivity to initial conditions. This shrinks the theoretical critical range without destroying the computing capacity of the system. This critique has not been fully answered by the edge-of-chaos proponents, as empirical results increasingly demonstrate that completely random networks perform equivalently to fine-tuned critical cellular automata in reservoir setups, challenging the necessity of structured dynamics.

The Validity of the 5-Bit Memory Benchmark
There is a fierce dispute over the specific benchmark that built the field of cellular automata reservoir computing. The 5-bit memory task requires the system to remember a short binary string across a distractor period of zeros. Proponents used this to prove the architecture has long short-term memory. 

Glover and colleagues are on the opposing side, arguing the benchmark is pathologically flawed. Because the distractor period consists only of zeros, an additive rule like Rule 90, which operates essentially as an exclusive-or gate, will simply diffuse the original input across the grid without any nonlinear interference. Because Rule 90 acts as a linear map over the Galois field of two elements, its evolution can be written as a sequence of linear matrix multiplications. A linear classifier can then trivially reverse the transformation. Glover answered the early claims by explicitly showing the benchmark selects for additive mathematical properties rather than complex computation, completely bypassing the need for nonlinear temporal mixing. The original authors have not published a rebuttal defending the validity of the benchmark.

Encoding versus Dynamics, also known as the Random Projection Problem
A persistent argument across all of reservoir computing, but heavily pronounced in discrete substrate research, is whether the dynamical system is actually doing temporal processing or merely acting as a static random projection matrix. Because discrete cellular automata typically use a random mapping to project the low-dimensional input onto the high-dimensional grid, the readout layer receives a massive expansion of the input space. 

Critics argue that a sufficiently powerful linear decoder can manufacture the correct result purely from this spatial expansion, bypassing the temporal evolution entirely. This critique was definitively answered for the UCR datasets when it was shown that the encoding scheme alone was responsible for the classification success. The proponents of the paradigm have never answered this critique with a task that rigorously isolates temporal integration from spatial expansion while controlling for the random projection.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT

Because the question is theoretically sharp enough to test, but currently sits in the UNTESTED category due to poor benchmark selection and omitted controls, a competent group could settle this in a matter of weeks.

The goal is to test whether the cellular automaton dynamics provide temporal mixing and memory that a frozen or random substrate cannot. The experiment must strictly avoid sequence tasks where the distractor period is empty, preventing static random projections from surviving without true temporal integration.

Task: The Non-linear Auto-Regressive Moving Average 10-step time series prediction task. This benchmark requires complex nonlinear mixing of inputs across a temporal window and cannot be solved mathematically by static random projection or linear diffusion.

Substrate: A one-dimensional Elementary Cellular Automaton. The group should test Rule 110, which is Class IV and capable of universal computation, and Rule 90, which is additive. The state dimension should be fixed at a budget of 256 cells.

Encoding Scheme: A fixed random sparse projection. The per-step input is injected into the substrate by flipping the state of fixed, predefined cells at every time step.

Execution: Sealed executions. The cellular automaton is explicitly reset to a state of all zeros at the start of each individual sequence.

Replicate Count: 100 independent trials. The encoding projection matrix and the initial random seeds must be resampled each time to ensure the unit of analysis treats the random mapping generation as the random variable, preventing seed-sharing errors.

The Three Arms to Compare:
1. The Full System: Input is injected, the cellular automaton evolves for exactly four steps, and the final state is concatenated to the readout buffer.
2. Control 1, the Frozen Substrate: Input is injected into the 256-cell grid via the exact same encoding, but the automaton evolves for zero steps. The readout sees only the static random projection of the current input.
3. Control 2, the Matched-Random Substrate: The automaton is replaced by a discrete Random Boolean Network. Every cell still receives exactly three inputs to match the parameter budget of the elementary cellular automaton neighborhood, but the wiring is randomized and the update rules are assigned randomly from the 256 possible three-input Boolean functions.

Readout: Ridge regression, utilizing an L2 regularized linear classifier. Crucially, the regularization parameter must be fixed in advance across all three arms to strictly control the parameter budget, preventing the decoder from manufacturing a result through hyperparameter tuning.

Compute Cost: Minimal. This experiment operates entirely on discrete binary vectors and linear algebra. It can be implemented using standard scientific computing software and executed on a single consumer machine in less than twenty-four hours.

If the Full System statistically outperforms both Control 1 and Control 2 across the independent replicates, the hypothesis is ESTABLISHED. If Control 1 matches the Full System, the performance is entirely due to the readout and the spatial expansion of the encoding, meaning the hypothesis is REFUTED. If Control 2 matches the Full System, the performance is attributable to high-dimensional random mixing rather than the specific structured dynamics of the fixed cellular automaton, meaning the precise claim of a fixed, specific dynamical system being necessary is REFUTED.
