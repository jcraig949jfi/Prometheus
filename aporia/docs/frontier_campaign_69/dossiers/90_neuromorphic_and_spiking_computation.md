# Prompt 90: Neuromorphic and Spiking Computation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdvN3VmYXVIR0JNTFhfdU1Qd2RfczhRbxIXbzd1ZmF1SEdCTUxYX3VNUHdkX3M4UW8
**Elapsed:** 395s

---

FRONTIER PRACTITIONER DOSSIER
Field: Neuromorphic and Spiking Computation

The following dossier provides a comprehensive, skeptical, and reproducible baseline for entering the field of neuromorphic and spiking computation in 2026. This report explicitly addresses the methodological confound of evaluating event-driven algorithms on von Neumann hardware and details the theoretical, software, and practical state of the frontier. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Spiking Neural Networks are event-driven computational models wherein neurons communicate via discrete binary spikes in continuous time, rather than via continuous floating-point activations. The field's central hypothesis is that this discrete, asynchronous paradigm can drastically reduce energy consumption and natively process temporal data, mirroring biological efficiency. Computation occurs only when a spike triggers an update, meaning the network is otherwise silent and consumes minimal dynamic power. Because the spiking mechanism (often modeled as a Leaky Integrate-and-Fire neuron) relies on a non-differentiable hard threshold, standard backpropagation fails. The dominant workaround over the last several years has been the surrogate gradient method, which uses a smooth, differentiable approximation of the step function during the backward pass while maintaining the binary threshold in the forward pass cite: 1, 2, 47, 57.

What is SETTLED: It is now settled that deep spiking neural networks can be trained directly using backpropagation through time via surrogate gradients, achieving task accuracies that rival conventional artificial neural networks on small-to-medium datasets. The field has moved past biological plausibility as its sole justification and has successfully adopted modern deep learning architectures, culminating in spiking transformers that exceed 80 percent accuracy on ImageNet cite: 56, 73. Furthermore, it is settled that Artificial-to-Spiking Neural Network conversion, while historically popular for rate-coded networks, incurs severe latency penalties because it requires simulating many time steps to approximate an analog activation value, largely defeating the purpose of low-latency event-driven computation cite: 1, 98. 

What is CONTESTED: The fundamental validity of energy-efficiency claims remains fiercely contested. A persistent methodological confound plagues the literature: comparing a spiking network running on a GPU against a conventional network running on a GPU measures the inefficiency of simulating sequential time steps on parallel hardware, not the efficiency of the algorithm cite: 16, 69. The community is split between researchers who report theoretical synaptic operations as a proxy for energy, and systems researchers who argue that only physical deployment on neuromorphic hardware validates the claim. The NeuroBench initiative represents a major faction attempting to enforce a strict decoupling of hardware-independent algorithmic metrics from hardware-dependent system metrics to resolve this cite: 18, 26.

What is OPEN: The theoretical foundation of surrogate gradients in deterministic networks has recently been torn open. While treated as a settled engineering heuristic for years, rigorous theoretical work in 2024 and 2025 demonstrated that surrogate gradients in deterministic networks do not correspond to a conservative vector field and cannot be interpreted as the true gradients of any surrogate loss function cite: 61, 78. They can even point in the wrong direction, failing to guarantee convergence to local minima. The frontier has now shifted toward stochastic spiking networks, where surrogate gradients can be mathematically justified as exact derivatives of a neuronal escape noise function via stochastic automatic differentiation cite: 60, 80. Additionally, the software ecosystem suffered a massive consolidation in the last three years following the abandonment of Intel's Lava framework, leaving a major open gap in open-source hardware compilation cite: 97, 100.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Neftci, E. O., Mostafa, H., & Zenke, F.
2019
Surrogate Gradient Learning in Spiking Neural Networks
IEEE Signal Processing Magazine
arXiv:1901.09948
This is the canonical tutorial paper that standardized the surrogate gradient method for the machine learning community. A practitioner must read this to understand exactly how the chain rule is patched during the backward pass to bypass the non-differentiable spike threshold.

Zenke, F., & Ganguli, S.
2018
SuperSpike: Supervised Learning in Multilayer Spiking Neural Networks
Neural Computation
DOI 10.1162/neco_a_01086
This paper introduced a nonlinear voltage-based three-factor learning rule using a surrogate gradient approach, opening the door for training multilayer spiking networks. It is essential reading for understanding the credit assignment problem across time and depth in event-driven systems.

Davies, M., et al.
2018
Loihi: A Neuromorphic Manycore Processor with On-Chip Learning
IEEE Micro
DOI 10.1109/MM.2018.112130359
The foundational architectural paper for Intel's Loihi chip. Even if you do not have access to the hardware, you must read this to understand the physical constraints (hierarchical connectivity, dendritic compartments, programmable learning rules) that neuromorphic algorithms are ultimately attempting to exploit.

Cramer, B., et al.
2020
The Heidelberg Spiking Data Sets for the Systematic Evaluation of Spiking Neural Networks
IEEE Transactions on Neural Networks and Learning Systems
DOI 10.1109/TNNLS.2020.3044364
This paper introduces the Spiking Heidelberg Digits dataset, generated via an artificial cochlea model. It is critical because it explains why evaluating spiking networks on static images converted to spikes is a methodological error, and establishes the standard for natively temporal event-based benchmarks.

CURRENT SOURCES

Gygax, J., & Zenke, F.
2025
Elucidating the Theoretical Underpinnings of Surrogate Gradient Learning in Spiking Neural Networks
Neural Computation
arXiv:2404.14964
This paper is the current theoretical frontier. It proves that surrogate gradients are mathematically unprincipled in standard deterministic networks, but perfectly align with stochastic automatic differentiation in networks with escape noise, dictating that future highly-optimized networks should likely be stochastic.

Yik, J., et al.
2025
The neurobench framework for benchmarking neuromorphic computing algorithms and systems
Nature Communications
DOI 10.1038/s41467-025-56739-4
The defining paper of the current benchmarking era, supported by over 60 institutions. It explicitly addresses the field's hardware confound by separating evaluation into an algorithm track and a systems track. A practitioner must align their experimental reporting with the metrics defined here.

Zhou, Z., et al.
2024
Spikformer V2: Join the High Accuracy Club on ImageNet with an SNN Ticket
arXiv:2401.02020
This paper proves that spiking networks can scale to massive datasets. By integrating a Spiking Self-Attention module that avoids softmax and floating-point multiplication, the authors achieved over 80 percent Top-1 accuracy on ImageNet. It represents the state-of-the-art in direct-trained large-scale spiking architectures.

Bittar, A., & Garner, P. N.
2022
A surrogate gradient spiking baseline for speech command recognition
Frontiers in Neuroscience
DOI 10.3389/fnins.2022.865897
An exceptional, highly reproducible paper that provides a clean baseline comparing recurrent and adaptive spiking architectures on temporal audio data. It is the perfect starting point for a practitioner wanting to reproduce a rigorous surrogate gradient experiment without massive compute overhead.

Luu, N. T., et al.
2026
A Survey on Spiking Neural Network Foundation and Recent Progress
IEEE Access
DOI 10.1109/ACCESS.2026.3685666
The best and most recent comprehensive survey of the field. It covers biological neuron theories, synaptic modeling, surrogate-gradient learning, conversion pipelines, and modern hardware integration. Use this to fill gaps in terminology and historical context.

PART 3. SOFTWARE I CAN ACTUALLY RUN

snnTorch
https://github.com/jeshraghian/snntorch
Python
MIT Licence
2026
MAINTAINED
snnTorch is arguably the most accessible and pedagogically sound framework for gradient-based training of spiking networks. It extends PyTorch by treating spiking neurons as recurrent activation units deeply integrated with autograd. You can run simple feedforward, convolutional, and recurrent spiking network experiments today, entirely on GPU. Its primary limitation is that it focuses on algorithmic simulation; it does not natively compile to physical neuromorphic hardware. The community relies heavily on its exceptional interactive tutorials for onboarding cite: 11, 12, 15, 82.

SpikingJelly
https://github.com/fangwei123456/spikingjelly
Python
UNCONFIRMED
2026
MAINTAINED
SpikingJelly is the current heavy-lifter for large-scale spiking deep learning. It provides critical acceleration backends including CuPy and Triton, which drastically speed up the simulation of multiple time steps on GPUs. It is the framework of choice for modern, large-scale architectures like Spikformer and includes advanced features like memory-efficient training, experimental distributed execution, and precision control. If you are training on ImageNet or building massive spiking transformers, you must use SpikingJelly. A known gotcha is its API instability; the module names were heavily refactored starting in version 0.0.0.0.14, breaking older codebases cite: 6, 7, 9, 91.

NeuroBench
https://github.com/neurobench/neurobench
Python
UNCONFIRMED
2025
MAINTAINED
This is not a neural network framework, but the definitive community evaluation harness. You use it to wrap your PyTorch, snnTorch, or SpikingJelly models to output standardized, hardware-independent complexity metrics, ensuring your results are directly comparable to the literature without falling prey to the hardware confound cite: 17, 20. 

sparch
https://github.com/idiap/sparch
Python
UNCONFIRMED
2022
DORMANT
This is the reference implementation for the Bittar and Garner 2022 speech command baseline. It is small, clean, and runs effectively today. It implements Leaky Integrate-and-Fire and adaptive LIF neurons with and without recurrent connections. While dormant, it remains highly valuable because it provides a verified, unbloated architecture specifically tuned for temporal spike data rather than static image classification cite: 34, 87.

Lava
https://github.com/lava-nc/lava
Python
BSD 3-Clause
2026
ABANDONED
Intel originally built Lava as a massive, open-source, hardware-agnostic framework designed to unify the field, featuring an asynchronous message-passing architecture. It is completely dead. Intel has archived all Lava repositories and stated they will no longer provide support, patches, or updates, choosing instead to move the next-generation Loihi SDK to a closed or different standard. Do not build new projects on Lava, despite its heavy presence in papers published between 2021 and 2023 cite: 97, 98, 100.

BindsNET
https://github.com/BindsNET/bindsnet
Python
UNCONFIRMED
2022
DORMANT
Historically famous for integrating biological plasticity rules like Spike-Timing-Dependent Plasticity with machine learning and reinforcement learning. It is effectively dormant and has been superseded by snnTorch and SpikingJelly for surrogate gradient backpropagation workloads. Its published results often require pinning to very old PyTorch versions to reproduce cite: 36, 37, 102.

PART 4. DATA AND BENCHMARKS

Spiking Heidelberg Digits
https://zenkelab.org/datasets/
Approx 1 GB
Creative Commons Attribution 4.0
This dataset contains spoken digits from zero to nine in English and German, converted into spikes via an artificial cochlea model (LAUSCHER). It is authoritative for evaluating native temporal processing capabilities in spiking networks. Because the data is already natively event-based, it bypasses the artificial step of converting static images into spike trains, which often masks the actual utility of the spiking paradigm cite: 31, 35.

Prophesee 1 Megapixel Automotive Detection Dataset
IDENTIFIER UNKNOWN
UNCONFIRMED
UNCONFIRMED
Recorded with a high-resolution event camera mounted on a car windshield over several months, capturing data under various lighting and weather conditions. It is used to measure large-scale object detection on native event data and is treated as an authoritative benchmark for scaling capabilities by the NeuroBench algorithm track cite: 16, 26.

DVS128 Gesture
IDENTIFIER UNKNOWN
Approx 2 GB
UNCONFIRMED
A dataset of 11 hand gesture categories recorded using a Dynamic Vision Sensor event camera. It is heavily used in the literature to benchmark spatial-temporal feature extraction. However, it is known to be easily saturated by modern deep spiking networks and is prone to overfitting, making it less useful for frontier capability testing in 2026 cite: 26.

NeuroBench Algorithm Track
https://neurobench.ai/
Variable
UNCONFIRMED
Not a single dataset, but a community-curated task collection and evaluation methodology. It uses datasets like the Prophesee 1MP and DVS Gesture, but enforces a measurement regime that outputs static metrics (synaptic operations, spike sparsity, task accuracy). It is authoritative because it successfully isolates algorithmic performance from the underlying system hardware, providing a fair baseline against conventional non-spiking networks cite: 17, 18.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to understand surrogate gradients on temporal data is the recurrent spiking baseline for speech command recognition by Bittar and Garner (2022). It elegantly isolates the exact variables you are asking about, executes quickly, and does not require a supercomputer.

Software and Version:
Clone the sparch repository from https://github.com/idiap/sparch. Pin your environment to PyTorch 1.10 or 1.11 to match the 2022 release, though the code generally runs on modern PyTorch with minor deprecation warnings.

Dataset:
Spiking Heidelberg Digits. Download the HDF5 files from zenkelab.org. The dataset consists of 8332 training samples and 2088 test samples. Place them in the data directory expected by the sparch data loader.

Parameters to Set:
Neuron Model: Recurrent Adaptive Leaky Integrate-and-Fire (RadLIF)
Simulation time steps: Determined dynamically by the dataset sequence length (max 100 timesteps after binning).
Batch size: 128
Optimizer: Adam
Learning rate: 1e-3
Surrogate gradient function: Fast Sigmoid (also known as SuperSpike heuristic)
Surrogate steepness parameter (beta): 10.0
Hidden layers: 3 layers of 128 neurons each.
Readout layer: Non-spiking Leaky Integrate-and-Fire units acting as integrators, where the maximum membrane potential over time dictates the class prediction.

Replicates and Seeding:
The original study ran 5 independent replicates with random seeds initializing the PyTorch and NumPy random number generators.

Approximate Compute Cost:
Very low. Training takes approximately 2 to 4 GPU hours on a single NVIDIA A100 or V100.

Expected Result:
You should observe a test accuracy of 94.6 percent. This is the published state-of-the-art baseline for RadLIF on SHD from the original 2022 paper cite: 31, 87.

The Three Most Common Ways People Get This Wrong:
1. Dead Neurons from Initialization: If the initial membrane resting potential is set too low relative to the threshold, or if the initial weights are too small, the neurons will never fire. Because they never fire, no gradients flow even with a surrogate, and the network fails to learn.
2. Tensor Dimension Mismatches during BPTT: In standard PyTorch, tensors are usually shaped as (Batch, Channel, Height, Width). In spiking networks, time is a strict dimension. Practitioners frequently confuse the time step dimension with the batch dimension, feeding the network incorrect temporal sequences or causing catastrophic memory blowouts when PyTorch attempts to unroll the computation graph backward through time.
3. Surrogate Gradient Mismatch: The steepness of the surrogate derivative is a critical hyperparameter. If it is too steep, gradients explode or vanish exactly as they would with a hard step function. If it is too wide, the network suffers from gradient mismatch, where the backward pass updates weights assuming a smooth activation, but the forward pass evaluates a binary threshold, leading to severe performance degradation.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Stochastic Surrogate Gradient Kernels
Currently, mainstream frameworks like SpikingJelly and snnTorch implement deterministic Leaky Integrate-and-Fire neurons. However, recent theoretical work proves that surrogate gradients are mathematically unprincipled in deterministic networks and only form a valid conservative field when used in stochastic networks via stochastic automatic differentiation cite: 60, 61, 78. If you want to run theoretically grounded experiments, you will have to write your own custom PyTorch autograd functions. 
Interface: The input is a tensor of membrane potentials and a random noise tensor. The forward pass evaluates a probabilistic spike generation function based on an escape noise formulation. The backward pass must implement stochastic automatic differentiation where the derivative explicitly matches the chosen noise distribution. 
Difficulty: High. Writing the custom CUDA kernels for fast stochastic generation and backward passes without destroying the memory footprint is substantial engineering work.

Hardware-Agnostic Compilation Layers
Because Intel abandoned the Lava framework, there is no longer a community-standard intermediate representation and compiler stack to move a trained PyTorch model directly onto disparate neuromorphic chips (like Loihi 2 or BrainChip Akida) cite: 97, 100.
Interface: An export function that takes a PyTorch computational graph of a spiking network and outputs the exact routing matrices, weight quantizations, and compartmental parameters required by the target hardware's proprietary SDK.
Difficulty: Extreme. Several private labs and startups have rebuilt these bridges internally, which is why the literature frequently features deployment papers without published compilation code. Building this requires deep knowledge of both PyTorch graph parsing and proprietary hardware specifications.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Hardware-Algorithm Confound
The most persistent standing critique of this field is the conflation of algorithms with hardware. The defining claim of spiking computation is energy efficiency. However, simulating sequential, temporal, event-driven processing on highly parallel, synchronous von Neumann architectures like GPUs is vastly less efficient than running dense matrix multiplications. Claims that a spiking network is "more efficient" based on low spike-counts are purely theoretical until physically deployed on event-driven neuromorphic silicon. For years, papers successfully passed peer review by comparing theoretical SNN operations against measured ANN energy on GPUs, a deeply flawed methodology. This critique is largely being answered now by the NeuroBench framework, which forces a strict separation of algorithmic complexity from physical hardware execution cite: 16, 18, 69.

The Theoretical Failure of Deterministic Surrogate Gradients
For half a decade, surrogate gradients were used as a highly effective, yet purely heuristic, engineering trick. In 2024 and 2025, the Zenke lab published standing critiques proving that applying surrogate gradients to deterministic spiking networks is mathematically flawed. They demonstrated that the surrogate gradient does not integrate to zero over a closed loop, meaning it does not represent a conservative vector field. Consequently, it is impossible for the surrogate gradient to be the true gradient of any underlying surrogate loss function. In practical terms, this means surrogate gradient descent in deterministic networks can point in the wrong direction and is completely unguaranteed to find a local minimum. This critique has only been answered for stochastic networks, where the surrogate matches the escape noise derivative cite: 61, 78, 81.

The Abandonment of Intel Lava
Intel attempted to centralize neuromorphic software development by launching Lava, an open-source, hardware-agnostic software framework relying on asynchronous message passing between processes. Despite extensive marketing and early adoption by the community, the framework was highly complex, difficult to interface with standard deep learning pipelines, and suffered from fragmented documentation. Intel recently archived all Lava repositories, officially abandoning the open-source project to focus on a closed or differently standardized SDK for their next-generation hardware. Any research program that invested heavily in the Lava ecosystem lost their toolchain entirely cite: 97, 98.

The Latency of ANN-to-SNN Conversion
In the early days of deep spiking networks, the most successful training method was to train an analog network normally, then convert the ReLU activations into spiking thresholds. This relied on rate coding, where the firing rate of a spiking neuron approximated the continuous activation value of the analog neuron. This approach failed in deployment. To accurately approximate a floating-point value with binary spikes, the network had to be simulated over hundreds or thousands of time steps. This massively inflated inference latency, destroying the low-power and fast-reaction-time promises of the event-driven paradigm. The field has largely pivoted away from conversion in favor of direct training with surrogate gradients, which allows for functional networks using as few as 1 to 4 time steps cite: 1, 98.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: Stochastic Spiking Transformers via Stochastic Auto-Differentiation
Feasibility: High. Spiking transformers (Spikformer V2) exist and can handle ImageNet, and the theoretical foundation for stochastic gradients (Gygax 2025) has just been published. 
What it measures: This experiment would implement stochastic Leaky Integrate-and-Fire neurons inside a Spikformer architecture, training it with true stochastic automatic differentiation rather than heuristic surrogate gradients. It measures whether mathematically rigorous gradients yield superior generalization, robustness to noise, or faster convergence than the deterministic heuristic.
Falsification: If the theoretically sound stochastic network fails to exceed the accuracy-per-operation metric of the heuristically trained deterministic Spikformer, it falsifies the hypothesis that the mathematical invalidity of deterministic surrogate gradients actually harms empirical deep learning performance.

Experiment 2: Token-Pruned Spiking Self-Attention on Native Event Data
Feasibility: High. Tools like SpikingJelly and NeuroBench easily support processing event-camera data, and token pruning methods for spiking transformers have been proposed but rarely rigorously benchmarked on native high-resolution event data.
What it measures: Transformers scale poorly due to quadratic attention costs. Spiking Self-Attention avoids softmax and multiplication, but still routes too many tokens. By applying block-level early stopping to uninformative tokens in the time domain, you measure the strict energy-delay product limit of attention mechanisms applied to autonomous driving data (Prophesee 1MP dataset).
Falsification: If the pruned Spikformer's hardware-independent complexity metrics do not significantly undercut the equivalent metrics of a highly optimized, non-spiking MobileNet or state-space model, the hypothesis that spiking attention buys an inherent efficiency advantage is falsified.

What Will NOT Work:
Building a new unifying software compiler to replace Lava. The neuromorphic hardware landscape is heavily fragmented, and vendors are protecting their proprietary SDKs. An academic entrant attempting to write a universal bridge from PyTorch to physical neuromorphic hardware will spend years on reverse-engineering without producing novel experimental science. Rely on simulation proxies validated by NeuroBench, and leave physical hardware compilation to the hardware vendors.
