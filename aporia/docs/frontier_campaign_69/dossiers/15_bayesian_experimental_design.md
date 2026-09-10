# Prompt 15: Bayesian Experimental Design

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZSNmVlYXFtWUw3enVfdU1QN3RfalNBEhZSNmVlYXFtWUw3enVfdU1QN3RfalNB
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: Bayesian Experimental Design

This report provides a comprehensive, practitioner-focused assessment of Bayesian Experimental Design as it stands at the frontier in 2026. It is written specifically for a computational scientist looking to write code, deploy models, and execute state-of-the-art experiments without getting bogged down in historical surveys of dormant mathematical statistics. 

Your understanding of the core mechanism is fundamentally correct in theory but requires a critical correction regarding modern implementation. You noted that to compute the Expected Information Gain, you measure the Shannon distance between the prior and the expected posterior, and that outside of conjugate normal models, this is estimated by Nested Monte Carlo. Theoretically, this is exactly what the field does. Computationally, this description is outdated and represents a dead end. 

The correction you requested: Pure Nested Monte Carlo is fundamentally crippled by double intractability. Because you must sample parameters from the prior, and for each parameter sample data from the likelihood, and then for each imagined dataset run an inner Monte Carlo loop to estimate the posterior evidence, the computational complexity is quadratic. For any sequential experiment where decisions must be made in real time, Nested Monte Carlo fails completely (cite: 4, 41). The modern frontier does not use raw Nested Monte Carlo to compute the design utility. Instead, the field relies on amortized variational inference. Today, practitioners train deep neural networks—such as Conditional Neural Processes or Transformers—offline across thousands of simulated trajectories. These networks learn a policy that directly maps an experimental history to the next optimal design using a single forward pass, completely bypassing the need to compute live posteriors or run nested loops during the actual experiment (cite: 23, 81, 87).

What follows is the exact map of the field, the literature, the software, and the blueprints you need to build at the 2026 frontier.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Bayesian Experimental Design has undergone a computational revolution. Historically a subfield of theoretical statistics reliant on linear models, Laplace approximations, and exhaustive grid searches, it has been largely absorbed into the machine learning and probabilistic programming communities. The focus has shifted entirely from static, one-off designs to sequential, adaptive designs where the results of step t determine the design of step t+1. This is now achieved through Amortized Experimental Design, where deep policy networks are trained via reinforcement learning or stochastic gradient ascent to maximize variational lower bounds on the Expected Information Gain (cite: 41, 62). 

What is SETTLED: Expected Information Gain remains the undisputed, mathematically optimal metric for purely information-seeking experiments. Furthermore, it is settled that traditional greedy, myopic design—optimizing only for the immediate next step without considering future steps—is strictly suboptimal compared to non-myopic policies that optimize the total information gain over an entire sequence (cite: 15, 63). Finally, it is settled that live, test-time Nested Monte Carlo is unscalable; any serious 2026 deployment uses offline amortized training.

What is CONTESTED: The architecture and rigidity of the amortized policy. On one side, proponents of fully amortized design argue that a sufficiently powerful Transformer trained on enough prior samples can operate perfectly zero-shot at test time (cite: 87). On the opposing side, researchers argue that real-world experiments inevitably suffer from distribution shift—the true physical parameters often sit in the tails of the training prior. This side advocates for semi-amortized design, where the pre-trained policy is rapidly fine-tuned or updated online during the live experiment to prevent collapse (cite: 93, 94). Additionally, there is a live debate over whether Expected Information Gain is actually the right metric when the ultimate goal is a specific real-world action, with a rising faction advocating for Decision Utility Gain instead of pure parameter estimation (cite: 32, 33).

What is OPEN: Likelihood-free or implicit model design. Designing experiments when your simulator is a complex black-box physics engine or agent-based model—meaning you can generate data but cannot evaluate the exact likelihood function—remains a massive computational challenge (cite: 24, 65). Also open is the issue of robust prior specification. Expected Information Gain is highly sensitive to the chosen prior; if the human specifies a misinformative prior, the resulting neural policy will confidently command the collection of useless data (cite: 98, 99). 

In the merge with machine learning, the field lost some of the rigorous, finite-sample theoretical guarantees provided by traditional optimal design (such as A-optimal and D-optimal criteria). These have been traded away for the ability to scale to high-dimensional, non-linear models.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Chaloner, K. and Verdinelli, I.
1995
Bayesian experimental design: A review.
Statistical Science
DOI 10.1214/ss/1177009939
The bedrock mathematical text establishing the information-theoretic framework for experimental design. A practitioner must know this to understand the mathematical axioms the modern deep learning models are attempting to approximate (cite: 38).

Ryan, K. J.
2003
Estimating Expected Information Gains for Experimental Designs With Application to the Random Fatigue-Limit Model.
Journal of Computational and Graphical Statistics
DOI 10.1198/1061860032012
The paper that established Nested Monte Carlo as the standard computational workhorse for Bayesian Experimental Design before the deep learning era. You must read it to understand the baseline you are trying to beat (cite: 45).

Foster, A., Jankowiak, M., Bingham, E., Horsfall, P., Teh, Y. W., Rainforth, T., and Goodman, N.
2019
Variational Bayesian Optimal Experimental Design.
NeurIPS
arXiv:1903.05480
The turning point paper that broke the double intractability of Nested Monte Carlo. It introduced tractable variational lower bounds (like Prior Contrastive Estimation) that allow Expected Information Gain to be optimized using stochastic gradient descent (cite: 4).

Foster, A., Ivanova, D. R., Malik, I., and Rainforth, T.
2021
Deep Adaptive Design: Amortizing Sequential Bayesian Experimental Design.
ICML
arXiv:2103.02438
The paper that defined the current paradigm. It introduced DAD, proving that you can train a neural network policy offline to map experimental histories to optimal designs in milliseconds during live deployment (cite: 84).

Ivanova, D. R., Foster, A., Kleinegesse, S., Gutmann, M. U., and Rainforth, T.
2021
Implicit Deep Adaptive Design: Policy-Based Experimental Design without Likelihoods.
NeurIPS
arXiv:2111.02329
Crucial for computational scientists working with black-box simulators. It extends the Deep Adaptive Design framework to models where the likelihood cannot be evaluated, relying only on forward simulations (cite: 24, 65).

CURRENT

Rainforth, T., Foster, A., Ivanova, D. R., and Bickford Smith, F.
2024
Modern Bayesian Experimental Design.
Statistical Science
arXiv:2302.14545
If a good survey exists, it is this one. It bridges the historical statistics perspective with the modern computational revolution, perfectly summarizing the transition from Nested Monte Carlo to amortized neural policies (cite: 41, 76).

Hedman, M., Ivanova, D. R., Guan, C., and Rainforth, T.
2025
Step-DAD: Semi-Amortized Policy-Based Bayesian Experimental Design.
ICML
arXiv:2507.14057
The current state-of-the-art in robust design. It demonstrates that fully amortized policies can fail in practice and introduces test-time adaptation to periodically update the design policy as real data is gathered (cite: 93, 94).

Huang, D., Wen, X., Bharti, A., Kaski, S., and Acerbi, L.
2025
ALINE: Joint Amortization for Bayesian Inference and Active Data Acquisition.
NeurIPS
arXiv:2506.07259
The absolute technical frontier. Uses Transformer Neural Processes to jointly amortize both the experimental design policy and the posterior inference into a single forward pass, allowing for dynamic targeting of specific parameters (cite: 56, 86).

Huang, D., Guo, Y., Acerbi, L., and Kaski, S.
2024
Amortized Bayesian Experimental Design for Decision-Making.
NeurIPS
arXiv:2411.02064
Essential reading for practitioners who want to run experiments to make decisions rather than just estimate parameters. It introduces Decision Utility Gain and the Transformer Neural Decision Process (cite: 33, 35).

Go, J. and Isaac, T.
2022
Robust Expected Information Gain for Optimal Bayesian Experimental Design Using Ambiguity Sets.
UAI
arXiv:2205.09914
The primary critique of standard Expected Information Gain. It proves that slight misspecifications in your prior can ruin your experimental design, and introduces a robust log-sum-exp stabilization technique to defend against it (cite: 99).

PART 3. SOFTWARE I CAN ACTUALLY RUN

Pyro OED
https://docs.pyro.ai/en/stable/contrib.oed.html
Python
MIT License
2023
MAINTAINED
This is the community standard for basic, static Bayesian Experimental Design. Built into the Pyro probabilistic programming language, it handles the fundamental variational estimators introduced by Foster in 2019. It can run Laplace approximations, Nested Monte Carlo, and Prior Contrastive Estimation on any standard probabilistic model. Limitation: It is designed for static, one-step designs. It completely lacks the infrastructure to train sequential, amortized neural policies. If you want to do modern sequential design, Pyro OED is too low-level and slow.

BoTorch
https://botorch.org/
Python
MIT License
2026
MAINTAINED
The authoritative reference for Bayesian Optimization. While Bayesian Optimization is technically a subset of experimental design focused on finding the maximum of a function rather than full parameter estimation, BoTorch provides the most highly optimized, GPU-accelerated Monte Carlo acquisition functions in existence. Limitation: It assumes Gaussian Process surrogates and is not natively built to maximize Shannon mutual information for arbitrary mechanistic simulators, though its backend architecture is the gold standard for how you should structure your own code (cite: 52, 54).

Deep Adaptive Design (DAD)
https://github.com/ae-foster/dad
Python
MIT License
2021
DORMANT
The reference implementation from the originating authors of the amortized design revolution. It allows you to train a fully amortized policy network offline and deploy it. It runs the canonical Source Location Finding benchmark perfectly. Limitation: The repository is no longer actively updated for modern PyTorch versions, and fully amortized policies trained here will struggle with out-of-distribution real-world data without heavy manual intervention (cite: 67, 68).

ALINE
https://github.com/huangdaolang/aline
Python
MIT License
2025
MAINTAINED
The absolute current frontier software. It implements the Amortized Active Learning and Inference Engine using Transformer Neural Processes. You can use it today to jointly train an inference head and an acquisition head. It successfully runs the Location Finding and Constant Elasticity of Substitution benchmarks. Gotcha: Because it relies on heavily parameterized Transformers trained via reinforcement learning, hyperparameter tuning the reward signal (self-estimated information gain) is notoriously difficult on custom simulators. It requires extensive GPU compute to converge (cite: 57).

Step-DAD
https://github.com/marcelhedman/stepdad
Python
MIT License
2025
MAINTAINED
The modern reimplementation and extension of the original DAD concept. It adds the critical test-time refinement loops required to make amortized design survive contact with real-world data. If you are building a physical experiment today, this is the architecture you should use as your base. Limitation: Requires you to keep compute attached to the live experiment to run the periodic policy updates, which limits its use in edge-compute scenarios where inference must be truly instantaneous (cite: 29).

PART 4. DATA AND BENCHMARKS

Because Bayesian Experimental Design evaluates expected future states, it does not rely on static datasets like ImageNet. Instead, the field relies on standard forward simulators and task formulations. 

Source Location Finding
https://github.com/huangdaolang/aline/tree/main/tasks
Approximate size: Infinite (Generative Simulator)
MIT License
The authoritative, most widely used benchmark in the field. It simulates an acoustic energy attenuation model where the goal is to locate hidden signal sources in a 2D plane by choosing where to place sensors. It measures a policy's ability to navigate a 2D design space sequentially. Known limitation: Saturation. Modern amortized policies (like ALINE and Step-DAD) now routinely hit the theoretical upper bound of Expected Information Gain on this task. Solving it no longer proves a new method is broadly superior (cite: 62, 64).

Constant Elasticity of Substitution (CES)
https://github.com/huangdaolang/aline/tree/main/tasks
Approximate size: Infinite (Generative Simulator)
MIT License
An economics model benchmark that is treated as the standard for testing higher-dimensional design spaces. The design space is 6-dimensional, which is enough to cause basic grid-search and naive deep learning policies to fail. It measures the scalability of the acquisition function (cite: 68).

Pharmacokinetic Compartmental Models
Literature standard, natively implemented across PyMC and Pyro
Approximate size: Infinite (Generative Simulator)
Open Access
The traditional mathematical biology benchmark. You design the exact hours and minutes to draw blood from a patient to estimate absorption and elimination rates. It is used to measure continuous-time design capabilities. Known contamination: Many papers solve this by heavily restricting the prior to a tiny, highly conjugate region, resulting in policies that completely fail to generalize to realistic, wide-variance human populations (cite: 71, 74).

Hyperbolic Temporal Discounting
https://github.com/marcelhedman/stepdad
Approximate size: Infinite (Generative Simulator)
MIT License
A psychology benchmark where the design space is discrete (choosing between monetary reward A now or reward B later). It is used to measure a method's ability to handle non-differentiable, categorical design choices, which breaks pure gradient-ascent policy methods (cite: 92).

PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative experiment to anchor yourself in the 2026 frontier is the ALINE Transformer on the Source Location Finding task. This will teach you how joint amortized inference and acquisition actually functions.

Software and Version:
Clone the ALINE repository (https://github.com/huangdaolang/aline). Use the main branch as of late 2025. You will require Python 3.11, PyTorch 2.3 or higher, and the Hydra configuration library.

Dataset/Generator:
The synthetic Source Location Finding simulator, natively included in the repository under tasks=location_finding.

Parameters to Set:
Execute the training loop via the CLI with these exact parameters used by the original authors (cite: 57):
python train_aline.py task=location_finding task.theta_dist=uniform task.n_target_theta=2 task.K=1 lr=1e-3 T=30 task.n_query_init=200 max_epoch=100000 burning_epoch=20000 eval=bed eval.batch_size=1000 eval.L_final=1000000 eval.batch_size_final=200 eval.n_query_final=2000 eval.T_final=35

Replicates and Seeding:
Run across 3 independent random seeds. The final evaluation must be tested over 2000 independent query trajectories (eval.n_query_final=2000) drawing 1000000 outer prior samples (eval.L_final=1000000) to ensure the nested contrastive bounds do not exhibit high variance.

Compute Cost:
Training the Transformer Neural Process policy will take approximately 12 to 18 hours on a single NVIDIA A100 or H100 GPU. Evaluation will take an additional 2 hours.

Expected Result:
You are measuring the lower bound of the Total Expected Information Gain at step T=30. You should expect the model to converge to a Total EIG of 4.6 to 4.8 nats. Compare this against the Step-DAD baseline results in Hedman et al., 2025 (cite: 94).

Three Most Common Ways People Get This Wrong:
1. Inner-loop starvation. When evaluating the final policy using Nested Monte Carlo to find the ground-truth EIG, practitioners frequently use too few inner samples to estimate the marginal likelihood. This artificially inflates the EIG estimate due to Jensen's inequality, making the policy look vastly better than it actually is.
2. Train-test prior leakage. The policy is trained on data generated from the prior. If the evaluation step does not draw a strictly newly seeded, independent batch of ground-truth parameters from the prior, the Transformer simply memorizes the training trajectories.
3. Ignoring the burning epoch. Reinforcement learning on self-estimated information gain is highly unstable early on. Failing to enforce a strict warmup (the burning_epoch parameter) causes the policy network to collapse into a sub-optimal local minimum where it repeatedly queries the exact same useless design space.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments on complex systems, you will find a massive tooling gap: there is no off-the-shelf software for Likelihood-Free, Semi-Amortized Design. 

Currently, if you have a simulator with a closed-form likelihood, you can use Step-DAD. If you have an implicit simulator (no likelihood), you can use iDAD. But if you have an implicit simulator and you want a robust, test-time-adaptive policy (Semi-Amortized Implicit Design), you must build it yourself.

The Interface:
You need to build a Python library that accepts a black-box simulator function, a prior distribution object, and a design space definition. 
Input: `def simulate(parameters, design) -> observations`
Output: A trained, deployable policy object `policy.get_next_design(history)` that includes a `.fine_tune(actual_observation)` method.

The Hard Part:
Because the likelihood is implicit, you cannot compute the standard contrastive bounds for Expected Information Gain. You have to train a neural density estimator or a classifier (via ratio estimation) just to approximate the likelihood ratio. You must then pipe the gradients from this density estimator into a Transformer policy network. Finally, at test time, you must write a highly optimized routine that updates both the density estimator and the policy network simultaneously using the live data, without catastrophic forgetting. 

Work Estimate:
This requires marrying the codebases of iDAD and Step-DAD, swapping out the basic Multi-Layer Perceptrons for Transformer Neural Processes. For a single competent computational scientist, this is a 3 to 5 month build. 

Signal of Gap:
Multiple groups working on simulation-based inference (SBI) in fluid dynamics and epidemiology have privately rebuilt bespoke active-learning loops using surrogate neural networks because they cannot plug their non-differentiable simulators into Pyro OED or ALINE.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Nested Monte Carlo for Sequential Design:
Attempting to use raw Nested Monte Carlo to calculate optimal designs at runtime has completely failed. The O(N*M) computational complexity means that to get a low-variance EIG estimate, you need thousands of outer samples and thousands of inner samples per candidate design. Doing this at every step of a 30-step experiment is impossible in real time. The entire field has abandoned this in favor of amortized neural bounds (cite: 4, 15).

Greedy / Myopic Optimization:
Historically, the field optimized designs one step at a time (myopic design). This approach repeatedly failed to replicate theoretical optimums because it ignored delayed information paths. A myopic policy might avoid a measurement that yields no immediate information but sets up a highly informative measurement in the next step. Myopic design is now widely considered an obsolete baseline (cite: 63, 64).

Out-of-Distribution Fragility of Fully Amortized Policies:
Deep Adaptive Design (DAD) looked incredibly strong in 2021. However, when practitioners took these fully amortized policies out of purely synthetic environments and applied them to physical experiments, they failed to replicate the simulated efficiency. The critique was proven correct: amortized policies overfit to the exact prior they are trained on. If a physical parameter deviates slightly from the training distribution, the policy breaks down and acts randomly. This standing critique necessitated the invention of Step-DAD to allow online course correction (cite: 26, 91).

Prior Misspecification and Expected Information Gain:
A standing methodological critique by Go and Isaac (2022) points out that Expected Information Gain is hyper-sensitive to the prior distribution. If a practitioner uses an uninformative or slightly misspecified prior (which happens constantly in the real world), maximizing EIG will force the experiment to spend all its budget exploring regions of the parameter space that are highly uncertain but physically impossible. The proposed answer was Robust Expected Information Gain (REIG), which optimizes over an ambiguity set of priors using a log-sum-exp relaxation (cite: 96, 99). However, REIG is notoriously difficult to scale to sequential amortized design, and this critique remains largely unanswered in the sequential space.

Task Mismatch (Parameter vs Predictive):
For years, the field assumed that maximizing information about model parameters was universally good. It was later shown that if the user's actual goal is downstream decision making or predicting future states, optimizing parameter EIG wastes massive amounts of compute learning "nuisance parameters" that have no impact on the final decision. This critique was answered just recently by the introduction of Decision Utility Gain and Expected Predictive Information Gain, shifting the objective function away from the parameters and onto the downstream task (cite: 32, 87).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current state of the art, a well-resourced newcomer with compute and engineering skills should ignore standard parameter estimation on conjugate models and aim directly at the intersection of robust design and implicit simulators.

Aim 1: Robust Semi-Amortized Design for Implicit Models
Rank: 1
What makes it feasible now: The release of ALINE's Transformer Neural Processes and Step-DAD's online updating algorithms provide the architectural blueprints. You have the compute to train the offline phase and fine-tune online.
What it would measure: You would deploy this on a highly non-linear, non-differentiable physics simulator (e.g., fluid dynamics sensor placement) where the prior is deliberately misspecified by 20 percent. You would measure the Total Expected Information Gain against a standard amortized policy.
What falsifies it: If the online refinement step takes longer to compute than simply running a brute-force surrogate optimization, or if the robust policy performs worse than standard ALINE on an out-of-distribution task, the ambiguity set math is too conservative for sequential deployments.

Aim 2: Task-Aware Design for Agent-Based Models
Rank: 2
What makes it feasible now: The recent mathematical formalization of Decision Utility Gain (DUG) allows the objective function to bypass pure parameter entropy.
What it would measure: You would apply this to an epidemiology or economics agent-based simulator to design an optimal intervention strategy (not just parameter recovery). You would measure the downstream decision accuracy (e.g., successful containment of a simulated outbreak) per experiment cost.
What falsifies it: If maximizing Decision Utility Gain results in the exact same sequence of designs as maximizing parameter Expected Information Gain, the concept is a theoretical novelty that offers no practical real-world efficiency gains.

What Will NOT Work:
Do not attempt to solve Bayesian Experimental Design by throwing massive reinforcement learning compute at a standard reward loop without contrastive bounds. The bare Expected Information Gain reward signal is far too sparse and noisy; naive Deep RL agents will fail to converge. Furthermore, do not attempt to revive Nested Monte Carlo by writing custom CUDA kernels to brute-force the inner loops. The variance inherent in the double intractability will destroy the signal in high dimensions regardless of your floating-point throughput. Stick strictly to variational lower bounds and amortized neural architectures.
