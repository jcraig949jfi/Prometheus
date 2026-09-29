# E5 -- Collective, morphogenetic, embodied and unconventional computation

Delegate report for Odysseus / Prometheus "physics of intelligence" frontier program.
Date: 2026-09-27. Web search and fetch: WORKING (WebSearch + WebFetch used).

Citation tags:
- VERIFIED = bibliographic facts (title/authors/venue/year) and the headline claim were confirmed by a web search or fetch this session.
- PARTIAL = paper existence confirmed; the specific numbers or details quoted come from memory and were not re-checked.
- UNVERIFIED = from memory only; not checked this session.

Per-entry fields: (1) demonstrated, (2) assumptions built in, (3) failed / contested / overclaimed,
(4) measurement that made it visible, (5) reusable code/data, (6) Prometheus echo,
(7) genuinely open, (8) ANTI-GRAVITY version.

---------------------------------------------------------------------------

## PART 1 -- IDEA ENTRIES (23)

### E5-01. Bioelectric pattern memory in planaria (two-head "rewritable" target morphology)
Cites: Durant, Morokuma, Fields, Williams, Adams, Levin, "Long-term, stochastic editing of regenerative anatomy via targeting endogenous bioelectric gradients", Biophys J 2017 (PARTIAL; lab news release confirmed the result 2017-05). Durant et al., "Bistability of somatic pattern memories: stochastic outcomes in bioelectric circuits underlying regeneration", Phil Trans R Soc B 2019 (VERIFIED via search). Oviedo et al. 2010 (octanol / gap-junction block) (UNVERIFIED).
1. Brief gap-junction blockade (octanol) of trunk fragments -> some regenerate as two-headed; re-cut in plain water they stay two-headed over later rounds. Genome unchanged; altered state persists as a "target morphology" held in some physiological state. Some worms look normal but carry the altered pattern ("cryptic" phenotype) that shows only when re-cut.
2. Assumes the persistent variable is bioelectric (membrane voltage pattern). Voltage-dye imaging is the readout, and treatments are pharmacological with pleiotropic effects.
3. Penetrance is stochastic and not near 100%. The claim that the memory "is" the voltage map rests on correlation plus manipulation, not a sufficiency proof. Voltage-reporter dyes are hard to calibrate. There is little independent replication outside the Levin network (no published failed replications were found either). The word "memory" smuggles in cognitive framing (see Part 5).
4. Anatomical outcome after amputation (a delayed, conditional readout), plus voltage-sensitive dye imaging. The key design is the re-cut test: the latent state is visible only when you perturb and read it out later.
5. Levin lab protocols page ("resources for planarian memory experiments", thoughtforms.life). BETSE (bioelectric tissue simulator, Pietak & Levin) is open source (UNVERIFIED current status).
6. Memory with no designated memory medium: the "store" is a distributed attractor of coupled cell physiology, readable only by a regeneration event. Echo for lattice executable matter: probe latent state with destroy-and-regrow tests, not by reading the current pattern.
7. Is the persistent variable really voltage, or a downstream chromatin/transcriptional state that voltage only triggers? How many distinct stable morphologies can be written, and how much is that capacity in bits?
8. Anti-gravity: a pattern memory that no observer can see in steady state and that exists only as a *conditional response to damage*. Define memory operationally as "perturbation-conditional divergence of regrowth".

### E5-02. TAME / basal cognition / "competency of cells"
Cites: Levin, "Technological Approach to Mind Everywhere (TAME)", Front Syst Neurosci 2022 (VERIFIED arXiv 2201.10346). Lyon et al., "Reframing cognition: getting down to biological basics", Phil Trans R Soc B 2021 (UNVERIFIED). Critiques: Schulte 2024 on plant cognition (PARTIAL via search summary); "A Mark of the Noncognitive", Biological Theory 2026 (VERIFIED existence); Segundo-Ortin 2025 plant cognition methodological primer (VERIFIED existence).
1. A framework rather than a result. It proposes placing systems on a continuum of goal-directedness via "cognitive light cone" (the spatiotemporal scale of the goals a system can pursue), and ranking them by how far they can be "persuaded" to reach set points by different means.
2. Assumes goal-directedness is observer-relative and graded, and that the right level of description is whatever gives the best prediction and control.
3. Critics argue it has no discriminating criterion: every homeostat qualifies, so "cognition" loses contrast. Deflationary critics say that once a physico-chemical mechanism is known, calling it cognition adds nothing. It is contested whether TAME makes risky predictions.
4. Intervention success ("can I reprogram outcome X by addressing set point Y?") rather than any intrinsic measurement.
5. None as code; conceptual.
6. Direct relevance: Prometheus needs a *non-anthropocentric* capability ladder. TAME's "persuadability" axis (hardware rewiring -> set-point editing -> training by reward -> argument) is a usable operational scale for how an intervention reaches a world.
7. Can a cognitive light cone be measured from trajectories alone, without an experimenter's goal attribution?
8. Anti-gravity: measure goal-directedness as *counterfactual convergence*, meaning the same end state is reached from perturbed starts by different paths (James's "same end, varying means"), with no goal named in advance. Infer the goal from the convergence basin.

### E5-03. Self-sorting arrays with "unexpected competencies" (Levin-lab minimal model)
Cites: Zhang, Goldstein, Levin, "Classical sorting algorithms as a model of morphogenesis: self-sorting arrays reveal unexpected competencies in a minimal model of basal intelligence", Adaptive Behavior 2024/2025 (VERIFIED; arXiv 2401.05375).
1. Bubble/insertion/selection sort is recast as cell-level agents, each running its own policy. The distributed arrays tolerate "frozen" (broken) elements better than top-down versions. They show "delayed gratification" (temporary increases in disorder to get past a defect). Mixed-algorithm arrays form clusters ("algotypes") that no rule specifies.
2. The sorting objective is fixed and designer-given. "Competency" is defined relative to that objective.
3. Heavily contested as overinterpretation: "delayed gratification" is a label for non-monotone progress around an obstacle, which any local-rule system does. Algotype clustering can be explained as an artifact of the swap dynamics. The work is a good illustration of *reading* hidden behaviours out of deterministic code, but the cognitive vocabulary is not earned.
4. Sortedness trajectory (monotonicity error) versus time under injected faults, and clustering statistics of algotypes.
5. Authors released code (PARTIAL).
6. Exactly Prometheus's problem: capabilities *not explicitly installed* show up as side effects of local rules under damage. The methodological lesson is to perturb (freeze elements) and see what the dynamics does that the specification never mentioned.
7. A null model is needed. What fraction of "unexpected competencies" appear in random local-rule systems with the same fixed points?
8. Anti-gravity: skip the designed objective entirely. Run random local-rule arrays, inject faults, and look for *any* conserved quantity that is restored after damage. That restored quantity is the "goal".

### E5-04. Xenobots (computer-designed organisms) and sim-to-real morphology design
Cites: Kriegman, Blackiston, Levin, Bongard, "A scalable pipeline for designing reconfigurable organisms", PNAS 2020 (VERIFIED). Coghlan & Leins, "Living robots: ethical questions about xenobots", AJOB 2020 (VERIFIED).
1. Evolutionary search in a voxel simulator produces body plans (passive skin cells plus contractile cardiomyocytes). These are hand-sculpted from Xenopus cells, and some reproduce the simulated locomotion behaviour.
2. The simulator is a crude soft-body model, and cells are assumed to hold their role. Cilia-driven motility was not in the first design pipeline.
3. Only a fraction of designs transfer. "Programmable organism" and "living robot" are overclaims: the cells run their own developmental program, and design selects shapes that the default program then animates. The robot framing is contested.
4. Trajectory tracking of motile clusters versus the simulated prediction (behavioural transfer rate).
5. Voxcraft-sim (GPU voxel soft-body simulator) is open source (PARTIAL).
6. The *environment/body* does the computation. Behaviour is a property of shape plus unmodified cells, which fits Prometheus's "no organism boundary" matter.
7. How much of the phenotype is designed and how much is default cell competency? No ablation-style accounting of credit was found.
8. Anti-gravity: behaviours from bodies no one designed, i.e. random aggregates of self-motile units, scored for emergent reliable function.

### E5-05. Kinematic self-replication (xenobots gathering loose cells into copies)
Cites: Kriegman, Blackiston, Levin, Bongard, "Kinematic self-replication in reconfigurable organisms", PNAS 2021 (VERIFIED). Spheroid parents averaged 1.2 +/- 0.4 rounds (max 2); AI-designed semitoroid ("Pac-Man") parents averaged 3 +/- 0.8 rounds (max 4) (VERIFIED via search summary).
1. Ciliated spheroids moving in a field of dissociated stem cells sweep them into piles. Piles above a size threshold mature into new motile spheroids, so replication happens by *kinematics and environment*, not by growth or division. A designed shape extends the number of generations.
2. Needs a feedstock of free cells provided by the experimenter, a confined dish, and a size threshold for piles to become viable.
3. Replication dies out after a few rounds: it is not open-ended, carries no heredity of variation, and has no evolution. "Novel form of reproduction" is fair. "Self-replicating living robots" (the press framing) suggests open-ended replication, which was not shown.
4. Counting offspring per generation and generations until extinction.
5. Simulation code released with the paper (PARTIAL).
6. VERY strong echo: reproduction as *environment-mediated aggregation*, with no template copying. It relates directly to Prometheus's byte-tape soup (replicators via interaction) and to lattice matter (copies assembled from ambient material).
7. What conditions (feedstock density, motility, pile threshold) make kinematic replication sustained, with R0 > 1? Can it carry heritable variation (shape as the "gene")?
8. Anti-gravity: replication with no genome. The "hereditary information" is the geometry of the collector, which biases the geometry of what it collects. Test whether shape is transmitted.

### E5-06. Anthrobots (self-assembling motile human airway-cell spheroids)
Cites: Gumuskaya, Srivastava, Cammarata, Kaplan, Levin, "Motile living biobots self-construct from adult human somatic progenitor seed cells", Advanced Science 2023/2024 (VERIFIED via search). Gumuskaya et al., "The morphological, behavioral, and transcriptomic life cycle of anthrobots", Adv Sci 2025 (VERIFIED existence). Age-reversal claims (Tufts 2025 news) (PARTIAL).
1. Adult human bronchial epithelial cells grown inside-out form cilia-driven motile spheroids with distinct morphotypes and movement types. Aggregates of them promoted closure of neuron-monolayer scratches in vitro.
2. Uses standard organoid culture plus a protocol inversion. There is no genetic engineering.
3. The wound-healing effect is modest and in vitro. The "biological age reversal" claim rests on epigenetic clocks, whose meaning in reprogrammed or cultured cells is contested. The "robot" label is again contested. No independent replication was found.
4. Morphotype clustering, trajectory classification, and scratch-closure assays.
5. UNVERIFIED availability of data.
6. Moderate echo: new collective behaviours from *old parts in a new context* with no new instructions. This is "capability not installed" by recontextualisation.
7. How large is the space of behaviours reachable by context change alone? Is it measurable as a context-to-behaviour map?
8. Anti-gravity: capability discovery by *changing boundary conditions only* (geometry, medium, confinement) on a fixed rule set. This is directly testable in Prometheus worlds.

### E5-07. Growing neural cellular automata (morphogenesis, regeneration)
Cites: Mordvintsev, Randazzo, Niklasson, Levin, "Growing Neural Cellular Automata", Distill 2020 (VERIFIED from long familiarity; PARTIAL this session). Randazzo et al., "Adversarial Reprogramming of NCA", Distill 2021 (VERIFIED).
1. A small per-cell network with a 3x3 perception (Sobel filters) and stochastic asynchronous updates is trained by backprop-through-time to grow a target image from one seed. With pool-based training plus damage augmentation, the pattern persists and regenerates.
2. There is a global differentiable loss over the full grid, and the designed channels include an "alive" mask. The target is fixed.
3. Regeneration exists only for damage types seen in training, and it breaks under unseen perturbations. Long-horizon instability (patterns explode or decay) required tricks. Adversarial cells can take over the collective (Adversarial Reprogramming 2021).
4. Pixel loss after damage at long horizons, and the stability of the attractor.
5. Code and colab notebooks are public (google-research self-organising-systems); a 2026 review with a reference implementation exists ("A New Kind of Network? Review and Reference Implementation of NCA", arXiv 2604.24990, VERIFIED existence).
6. Lattice executable matter with no organism boundary: NCA *are* that. The key difference from Prometheus is that NCA learning is external (backprop), so they show what a local rule *can* represent, not how such a rule would arise.
7. How much capacity exists in local rules, i.e. how many attractor patterns can one rule hold? What are the stability and attractor geometry (see "Stability and Geometry of Attractors in NCA", arXiv 2604.12720, VERIFIED existence)?
8. Anti-gravity: evolve or drift NCA rules with no loss. Select only for *persistence under damage* and see whether morphogenesis-like attractors arise.

### E5-08. Self-classifying MNIST and consensus NCA
Cites: Randazzo, Mordvintsev, Niklasson, Levin, Greydanus, "Self-classifying MNIST Digits", Distill 2020 (PARTIAL).
1. Each pixel-cell of a digit must, by local communication only, agree on a global label. Consensus is reached and propagates, and relabels after the digit is edited.
2. The cell mask is given, the global loss is per-cell cross-entropy, and training uses BPTT.
3. Label oscillation and instability at long horizons needed fixes. Accuracy is below that of a CNN. Consensus is slow, with time scaling with shape diameter.
4. Per-cell label agreement over time, and time-to-consensus after edits.
5. Distill notebooks (public).
6. Direct echo of *communication-dependent computation*: the answer exists only after information traverses the shape, so topology and latency dominate. This is a clean Prometheus analogue for packet-substrate worlds: vary loss and latency and measure how consensus time and accuracy degrade.
7. What is the scaling law of consensus time and accuracy against communication loss and topology? This is a natural Prometheus experiment.
8. Anti-gravity: consensus with no designed consensus rule, i.e. selection only on "collective does something coherent".

### E5-09. NCA for ARC-AGI and discrete/logic NCA (2025-2026)
Cites: Xu & Miikkulainen, "Neural Cellular Automata for ARC-AGI", ALIFE 2025 (VERIFIED; arXiv 2506.15746). Guichard, Reimers, Kvalsund, Lepperod, Nichele, "ARC-NCA: Towards Developmental Solutions to the ARC", arXiv 2505.08778 (VERIFIED). Miotti, Niklasson, Randazzo, Mordvintsev, "Differentiable Logic Cellular Automata", ALIFE 2025 (VERIFIED; arXiv 2506.04912). "Self-Organising Digital Circuits", arXiv 2608.02606 (VERIFIED existence only).
1. Per-task gradient-trained NCA solved 23 of 172 "feasible" ARC-1 public training tasks (13.4%). 138 tasks were excluded for grid resizing and 90 for colour generalisation (VERIFIED from the paper). DiffLogic CA learns exact Game-of-Life rules and damage-robust patterns using discrete logic-gate circuits at inference.
2. The loss is per task and fixed-size. ARC-NCA assumes hidden memory channels help.
3. ARC-NCA's "comparable to or surpassing ChatGPT 4.5" is a weak baseline comparison and an overclaim risk. The Xu result excludes more than half of the tasks. The stated failures are overfitting to examples, high-variance solutions, and inability to handle global coordination or long-range propagation.
4. Exact-match on test grids, and the fraction of pixels correct.
5. Code (PARTIAL; Xu/UT Austin, Google self-organising-systems for DiffLogic).
6. The failure mode is the finding: *local-rule computers fail where information must travel far*. This is the same communication-limited computation axis Prometheus varies in packet substrates.
7. Does adding long-range channels (graph NCA, sparse teleports) fix ARC generalisation, or only memorisation?
8. Anti-gravity: discrete rules found by search/drift (not gradient) that transform grids robustly, with generalisation measured on held-out inputs.

### E5-10. Coupled learning and equilibrium propagation in physical networks
Cites: Scellier & Bengio, "Equilibrium Propagation", Front Comput Neurosci 2017 (UNVERIFIED this session, well known). Stern, Hexner, Rocks, Liu, "Supervised learning in physical networks: from machine learning to learning machines", PRX 2021 (UNVERIFIED). Stern & Murugan, "Learning Without Neurons in Physical Systems", Annu Rev CMP 14:417-441, 2023 (VERIFIED).
1. Networks that relax to energy minima (resistors, springs, flow) can do supervised learning with a *local* rule. Compare a "free" state with a "clamped/nudged" state (output nudged toward the target), and update each edge by the difference in its local energy. This approximates gradient descent on a cost.
2. Requires: (a) an energy-minimising (or at least steady-state) physics; (b) two phases, free and clamped, and either a way to hold both, or a memory of one while in the other; (c) a trainer that imposes the clamp; (d) edges with adjustable parameters that respond to local signal differences.
3. Scaling is unproven past small networks. The two-phase requirement is the Achilles heel: in hardware it needs duplicated networks or memory. Learning is supervised, so a teacher is external. Noise and device variation limit accuracy.
4. Test error on regression/classification tasks versus training steps, in simulation and hardware.
5. Code from the Liu/Stern groups (PARTIAL; several GitHub repos).
6. Learning with *no processor*: the substrate's own relaxation computes the gradient. The echo for Prometheus lattice matter is whether an energy field that relaxes plus a local plasticity field that tracks a free/clamped difference could spontaneously learn.
7. What natural process supplies the "clamped" phase without a teacher? Candidates: environmental forcing, periodic driving, neighbouring subsystems acting as teacher.
8. Anti-gravity: the environment is the clamp. Periodic external forcing alternates free and nudged states, and plasticity integrates the difference. Nobody designed a learning rule; it falls out of alternation plus slow adaptation (see E5-12).

### E5-11. Learning metamaterials in hardware (electronic, elastic, shape-morphing)
Cites: Dillavou, Stern, Liu, Durian, "Demonstration of decentralized physics-driven learning", Phys Rev Applied 2022 (UNVERIFIED). Dillavou, Beyer, Stern, Liu, Miskin, Durian, "Machine learning without a processor: emergent learning in a nonlinear analog network", PNAS 121(28) 2024 (VERIFIED; arXiv 2311.00537). Altman et al., "Experimental demonstration of coupled learning in elastic networks", arXiv 2311.00170 (VERIFIED existence). Du, van Mastrigt, Veenstra, Coulais, "Metamaterials that learn to change shape", Nature Physics 22 (2026) 784-790 (VERIFIED). LCE metamaterials "Training and retraining liquid crystal elastomer metamaterials for pluripotent functionality", PNAS 2025 (VERIFIED existence).
1. Transistor-based self-adjusting resistor networks learn nonlinear tasks (XOR-class and nonlinear regression in the 2024 paper; about 32 edges, PARTIAL) with purely local update and no processor. Mechanical metamaterials learn target shape changes by locally updating stiffness, can learn sequentially (forget and relearn), and learn non-reciprocal and multistable responses (gripping, locomotion).
2. Each element carries its own twin/duplicate or memory to implement the two-phase rule. An experimenter sets the boundary conditions.
3. Small size. The learning rule is engineered into each element (the "local rule" is designed). Claims of "emergent learning" apply at the network level, but the element-level rule is installed.
4. Measured output error during training in real hardware, and retention after retraining.
5. Some data and code with the papers (PARTIAL).
6. Echo: learning as physics plus installed local plasticity. Prometheus should notice that *every hardware success still installs the local rule*. The open frontier is where the local rule itself comes from.
7. Minimal element-level plasticity that yields network-level learning without two-phase hardware.
8. Anti-gravity: materials whose *ordinary* ageing/wear (plastic creep, erosion) acts as the plasticity (see E5-13 and E5-14).

### E5-12. Temporal contrastive learning via implicit non-equilibrium memory
Cites: Falk, Strupp, Scellier, Murugan, "Temporal Contrastive Learning through implicit non-equilibrium memory", arXiv 2312.17723 (rev 2025) (VERIFIED).
1. Replaces the stored "free vs clamped" comparison with alternating temporal protocols plus integral feedback in each learning degree of freedom. The system's own lagged dynamics holds the memory of the previous phase. Non-equilibrium dissipation improves learning, and the paper derives a Landauer-like energy cost of contrastive learning.
2. Periodic alternation of forcing, a time-scale separation (learning DOFs slow, state DOFs fast), and integral feedback.
3. Theory/simulation. No hardware demonstration was found. The energy-cost bound is model-dependent.
4. Training loss versus protocol period and dissipation, and the energy dissipated per bit learned.
5. UNVERIFIED code.
6. STRONG echo: *propagation by timing rather than content*. The "teacher signal" is encoded in when forcing alternates, not in a separate channel, and memory is implicit in lag. This is precisely a Prometheus-native mechanism for energy-field lattices.
7. Can a natural periodic environment (day/night, tidal, feeding cycles) serve as the alternation protocol? What is the minimal dissipation for a given learning rate?
8. Anti-gravity: learning with no stored copy of anything. Memory = hysteresis/lag, rule = integral feedback, teacher = environmental periodicity.

### E5-13. Adaptive flow networks: Physarum memory in tube hierarchy
Cites: Kramar & Alim, "Encoding memory in tube diameter hierarchy of living flow network", PNAS 118(10) 2021 (VERIFIED). Bhattacharyya, Zwicker, Alim, "Memory capacity of adaptive flow networks", Phys Rev E 107, 034407 (2023) (VERIFIED). Tero et al., "Rules for biologically inspired adaptive network design", Science 2010 (UNVERIFIED this session). Nakagaki et al., "Maze-solving by an amoeboid organism", Nature 2000 (UNVERIFIED).
1. A nutrient stimulus's location is imprinted in which tubes grow and which shrink, and the imprint persists and guides later migration. The general adaptation rule (tubes thicken with flow, shrink without) gives shortest-path and Tokyo-rail-like network optimisation.
2. Positive feedback of flux on conductance plus decay (a use-it-or-lose-it rule), and conserved volume.
3. "Solves mazes" is shortest-path by flux reinforcement. It is physical optimisation, which is fair, but "intelligence" framing overreads it. Memory capacity is finite and is overwritten. Imprinting versus ageing is a tradeoff (Bhattacharyya 2023).
4. Time-lapse imaging of tube diameters (network morphology as the readout).
5. Tero model is trivially implementable. Datasets from the Alim lab (PARTIAL).
6. VERY strong echo: memory with no designated memory medium, since the *transport structure itself* is the memory. Relevant to packet substrates, where link conductance could adapt to traffic.
7. Capacity scaling with network size. Can such a network store associations (A predicts B), not just locations?
8. Anti-gravity: any Prometheus world where channel capacity grows with use and decays without it already implements a Physarum-style memory. Measure whether past traffic predicts future routing.

### E5-14. Physarum habituation and transfer of learned behaviour by fusion
Cites: Boisseau, Vogel, Dussutour, "Habituation in non-neural organisms: evidence from slime moulds", Proc R Soc B 2016 (VERIFIED). Vogel & Dussutour, "Direct transfer of learned behaviour via cell fusion in non-neural organisms", Proc R Soc B 2016 (VERIFIED). Saigusa et al., "Amoebae anticipate periodic events", PRL 2008 (UNVERIFIED). Bruna & Gyllingberg, "Cognition without neurons: modelling anticipation in a basal reservoir computer", arXiv 2505.02114 (VERIFIED).
1. Plasmodia habituate to quinine/caffeine bridges over days, with stimulus specificity and recovery. Fused naive+habituated plasmodia behave habituated, and later work proposed salt uptake as the carrier (memory = absorbed substance). Anticipation of periodic cold pulses. A 2025 model shows local allostatic nodes in a hex network re-enact learned periodic input.
2. Behavioural assays with speed as the readout. Habituation criteria are borrowed from animal work (Thompson and Spencer).
3. Habituation vs sensory adaptation/fatigue is hard to separate. The salt-uptake mechanism makes "memory" a stored chemical, deflationary but informative. The anticipation result has had limited replication (UNVERIFIED).
4. Crossing speed across days, recovery tests, and the fusion transfer test.
5. Little code; the model paper may have code (UNVERIFIED).
6. Memory stored as *absorbed environmental material*, and memory transferable by merging bodies. This echoes Prometheus lattice worlds where agents can fuse: is state transferable by merger?
7. Is fusion-transfer a general property of substance-based memory (it should be), and does it fail for structure-based memory (tube hierarchy)?
8. Anti-gravity: learning where "the lesson" is literally a quantity of environment carried inside. The store is uptake, with no rule beyond a concentration-dependent response.

### E5-15. Single-cell habituation (Stentor) and dynamical principles of habituation
Cites: Rajan, Makushok, Marshall et al., "Single-cell analysis of habituation in Stentor coeruleus", Current Biology 2023 (VERIFIED). Eckert, ... Gunawardena, "Biochemically plausible models of habituation for single-cell learning", Current Biology 2024 (VERIFIED). "A receptor-inactivation model for single-celled habituation in Stentor", Current Biology 2025 (VERIFIED existence). Smart, Shvartsman, Monnigmann, "Dynamical principles of habituation across substrates and scales", arXiv 2608.00249 (Jul 2026) (VERIFIED).
1. A single cell shows habituation hallmarks, including stimulus specificity and dishabituation-like effects, with heterogeneity across cells. Molecular networks with *two memory variables on separated timescales* (one fast-decaying, one slow) reproduce the hallmarks. 2026: linear time-invariant systems *cannot* habituate. Linear fading memory plus a static nonlinearity suffices, and the same motif appears in circuits and neuromorphic materials.
2. Stimulus trains at controlled rates. Habituation hallmarks are defined by the classic list.
3. Which hallmarks count is somewhat definitional. Receptor inactivation is deflationary (habituation = molecular fatigue with specific kinetics).
4. Response probability versus stimulus number, rate-sensitivity, and recovery.
5. Model code probably released (UNVERIFIED).
6. Gives Prometheus a *minimal certificate*: fading memory (two timescales) plus nonlinearity is the floor for the simplest non-associative learning. It can be tested in any substrate.
7. What is the equivalent minimal motif for *associative* learning (see E5-16)?
8. Anti-gravity: every substrate with multi-timescale relaxation plus a threshold habituates for free. Prometheus can scan its worlds for spontaneous habituation as the first rung.

### E5-16. Associative learning in gene regulatory networks
Cites: Watson, Buckley, Mills et al., "Associative memory in gene regulation networks", ALIFE 2010 (UNVERIFIED). Biswas, Manicka, Hoel, Levin, "Gene regulatory networks exhibit several kinds of memory", iScience 24(3):102131 (2021) (VERIFIED). Biswas, Clawson, Levin, "Learning in transcriptional network models", IJMS 24(1):285 (2023) (VERIFIED). Pigozzi, Goldstein, Levin, "Associative conditioning in gene regulatory network models increases integrative causal emergence", Commun Biol 8:1027 (2025) (VERIFIED).
1. Existing ODE models of real GRNs (BioModels) and random networks, *without changing parameters*, show habituation, sensitisation and Pavlovian-like associative memory under stimulus protocols. Memory lives in dynamical state (attractor switching), not in weight change. 2025: conditioning raises integrated-information-style causal emergence measures.
2. Uses the ODE models as given, experimenter-chosen stimulus/response node triples, and exhaustive search over node assignments.
3. Searching over all node triples can find "memory" by multiple comparisons. The proportion found in random networks shows it is generic, which is deflationary. No wet-lab confirmation of GRN Pavlovian conditioning in the referenced work (UNVERIFIED for 2024-2026). Causal-emergence measures are contested as metrics.
4. Response of R to CS before versus after CS+UCS pairing, compared with controls.
5. Models come from BioModels (public). The group's code (PARTIAL).
6. STRONG echo: *learning with no plasticity*, since state-based memory in fixed dynamics suffices. Prometheus byte-tape or lattice worlds likely contain such state-memory everywhere; the question is how to detect it without cherry-picking.
7. What are the base rates in random dynamical systems, and what is the correct null for "found memory"? Can state-based associative memory be *used* by the system itself for fitness?
8. Anti-gravity: memory with no memory medium and learning with no learning rule. It is only an attractor landscape visited in a history-dependent order.

### E5-17. Natural induction (Watson et al.)
Cites: Buckley, Lewens, Levin, Millidge, Tschantz, Watson, "Natural Induction: Spontaneous Adaptive Organisation without Natural Selection", Entropy 26 (2024) (VERIFIED). Watson, Levin, Lewens, "Evolution by natural induction", Interface Focus 15(6) 2025 (VERIFIED). Earlier: Watson et al., "Optimization in self-modelling complex adaptive systems", Complexity 2011 (UNVERIFIED).
1. In a network of interacting elements whose connections "give way slightly under stress" (plastic yielding), under repeated perturbation-and-relaxation, the connections change in a Hebbian direction. The system comes to find lower-energy (better-satisfying) configurations than it could originally, i.e. associative-learning-like optimisation *without selection and without a designed learning rule*.
2. Requires energy minimisation (relaxation), connections that yield to stress (slow plasticity proportional to stress), repeated perturbation (resets) so that many attractor visits occur, and timescale separation.
3. The claim that this is a *general* alternative to natural selection is contested. Evidence is mostly theoretical and simulation (Hopfield-style), and demonstrations in real physical systems are sparse (UNVERIFIED 2025-26). Critics note it requires fine-tuned timescales.
4. Energy of attractors found after induction versus before, and the distribution of attractor quality.
5. Hopfield-with-Hebbian code is trivial.
6. THE central anti-gravity mechanism for Prometheus: any lattice/energy world where couplings relax under stress and the world is repeatedly perturbed will self-organise toward generalising solutions. No rule design is needed.
7. Which physical systems actually have stress-yielding couplings on the right timescale? Is it seen in glasses, granular media, tissue? What goes wrong when perturbations are too frequent or too rare?
8. Anti-gravity: this *is* the anti-gravity version of Hebbian learning.

### E5-18. Self-assembly and nucleation as classifiers (molecular pattern recognition)
Cites: Evans, O'Brien, Winfree, Murugan, "Pattern recognition in the nucleation kinetics of non-equilibrium self-assembly", Nature 625:500-507 (2024) (VERIFIED). Murugan, Zeravcic, Brenner, Leibler, "Multifarious assembly mixtures", PNAS 2015 (UNVERIFIED).
1. 917 DNA tiles can assemble into three alternative structures. Concentration patterns (30x30 grayscale images) bias which structure nucleates first. Trained in silico to classify 18 images into 3 classes, and all trained images were correctly classified experimentally after a 150-hour anneal.
2. The "weights" (tile-to-structure assignment) are designed in silico, not learned by the molecules. Inputs are encoded as concentrations.
3. Extremely slow (days). Test-set robustness is limited, and learning is external to the substrate.
4. Fluorescence and AFM readout of which structure nucleated.
5. Designs and data at the Caltech DNA lab (PARTIAL).
6. Computation by *which phase wins a race* (nucleation kinetics), i.e. a timing-based readout. Echo: "propagation by timing rather than content".
7. Can the multicomponent mixture *learn* (e.g. via repeated assembly-disassembly cycles that bias concentrations, a natural-induction analogue)? Murugan's group has theorised this (UNVERIFIED).
8. Anti-gravity: classification by generic multistable physics, with the "answer" given by which basin was reached first.

### E5-19. Physical reservoir computing in materio (and its limits)
Cites: Fernando & Sojakka, "Pattern recognition in a bucket", ECAL 2003 (UNVERIFIED). Nakajima et al., "Information processing via physical soft body", Sci Rep 5:10487 (2015) (VERIFIED existence). Nakajima, "Physical reservoir computing -- an introductory perspective", Jpn J Appl Phys 2020 (VERIFIED existence, arXiv 2005.00992). Tanaka et al., "Recent advances in physical reservoir computing: a review", Neural Netw 2019 (VERIFIED existence, arXiv 1808.04962). Gan et al., "Task-adaptive physical reservoir computing", Nature Materials 2023/24 (VERIFIED existence). "Reservoir Computing Benchmarks: a tutorial review and critique", arXiv 2405.06561 (VERIFIED existence). "Restrictions on physical stochastic reservoir computers", arXiv 2307.14474 (VERIFIED existence).
1. Many physical media (water surface waves, soft silicone arms, spintronic oscillators, photonic delay loops, memristors, origami) provide fading memory plus nonlinearity, so a *trained linear readout* performs time-series tasks (NARMA, spoken digits).
2. All learning is in the external linear readout, and inputs are carefully encoded. Performance depends on operating-point tuning (edge of stability).
3. Benchmarks are weak and inconsistent (critiqued 2024). Much of the performance comes from the readout and input preprocessing. Stochasticity/noise sharply limits capacity (2023 theory). There is a memory-nonlinearity tradeoff (information processing capacity is bounded by degrees of freedom). "The bucket computes" overstates it.
4. Information processing capacity (Dambre et al. 2012) and memory capacity. NARMA error.
5. Many RC libraries (reservoirpy, etc.).
6. The environment/body *as part of the computation* (morphological computation). Prometheus worlds are reservoirs by default. The question is what, inside the world, plays the readout.
7. Can a reservoir's *own* slow variables learn the readout (self-organising reservoirs)? This is where RC meets E5-10/12.
8. Anti-gravity: the readout is also physical and adapts by local plasticity, giving a closed loop with no external regression step.

### E5-20. Physical neural networks trained through hardware (physics-aware training)
Cites: Wright et al., "Deep physical neural networks trained with backpropagation", Nature 601:549-555 (2022) (VERIFIED). Momeni et al., "Training of physical neural networks", Nature (2025) (VERIFIED; review). Momeni et al., "Backpropagation-free training of deep PNNs", arXiv 2304.11042 (VERIFIED existence).
1. Arbitrary physical systems (optics, electronics, a vibrating plate) are used as trainable layers. Physics-aware training uses the real system forward and a digital twin backward.
2. A digital computer and model remain in the loop. "Physical learning" here is not autonomous.
3. The 2025 review names noise accumulation, device drift, architecture mismatch, and energy efficiency not yet competitive at scale.
4. Accuracy on MNIST-class tasks versus a digital baseline.
5. Wright et al. code public (PARTIAL).
6. Cautionary echo: much of "physical intelligence" work is physics-as-accelerator with digital learning. Prometheus should distinguish substrate-computes-and-learns from substrate-computes-and-computer-learns.
7. When is a digital twin avoidable?
8. Anti-gravity: drop the twin; the system perturbs itself (node perturbation, E5-12 style) and learns from its own fluctuation-response.

### E5-21. Stigmergic construction (TERMES) and swarm construction
Cites: Werfel, Petersen, Nagpal, "Designing collective behavior in a termite-inspired robot construction team", Science 343:754 (2014) (VERIFIED). "Reaching new heights in multi-agent collective construction", arXiv 2408.13615 (VERIFIED existence).
1. Identical robots with no communication except the partially built structure build designer-specified 3D structures from bricks. A compiler turns the target structure into local traffic rules ("structpaths") guaranteeing completion.
2. The target is compiled offline: global design, local execution. Robots read local structure accurately.
3. Scale and robustness in the physical demo were limited. Stigmergy here is designed, not emergent; nothing is learned.
4. Completed-structure fidelity and completion time.
5. Simulators exist (PARTIAL).
6. Stigmergy = the environment as shared memory and communication channel. For Prometheus packet substrates: when the direct channel is lossy, do agents shift coordination into the environment?
7. Emergent (not compiled) stigmergic construction whose products increase builders' fitness. That is niche construction as capability accumulation.
8. Anti-gravity: construction with no blueprint. Structures that accumulate because they make further building easier (autocatalytic architecture).

### E5-22. Ant trail stigmergy as collective memory; swarm robots with morphological computation
Cites: Classic: Deneubourg, Goss et al. double-bridge experiments (UNVERIFIED). "Morphological computation and decentralized learning in a swarm of sterically interacting robots" (Ben Zion et al., Science Robotics 2023) (PARTIAL). "Kinetic theory of decentralized learning for smart active matter", arXiv 2501.03948 (VERIFIED existence). "Theory of collective learning in populations of adaptive agents", arXiv 2607.02171 (VERIFIED existence). "Emergent interactions lead to collective frustration in robotic matter", arXiv 2507.22148 (VERIFIED existence).
1. Pheromone fields store the colony's recent history that no individual holds, giving shortest-path selection via reinforcement plus evaporation. Swarms of bumping robots with simple local policies learn collective behaviour (e.g. phototaxis) through morphological coupling. Kinetic theories now describe learning agents as active matter.
2. Evaporation (forgetting) is essential. Deposition proportional to success needs some success signal.
3. The ant analogy is often over-sold as "ACO explains ants". Real ants use private memory and visual cues too. Robot swarm learning often retains global reward (counterfactual rewards), which is not decentralised.
4. Trail choice statistics and swarm-level displacement.
5. ACO and swarm simulators abundant.
6. Memory in the medium between agents, whose capacity is limited by evaporation and topology. Direct analogue for packet-substrate worlds: routing tables that are reinforced by use.
7. When does collective memory in the medium outperform individual memory, as a function of communication loss? (A Prometheus experiment.)
8. Anti-gravity: memory that belongs to no one; reinforcement-with-decay in a shared field.

### E5-23. Emergent self-replicators in program soups (BFF) and the deflationary follow-up
Cites: Aguera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo, Versari, "Computational Life: How well-formed, self-replicating programs emerge from simple interaction", arXiv 2406.19108 (2024) (VERIFIED). Knierim, Versari, Obryk, Aguera y Arcas, Saurous, "BFF: Simple explanations for complex phenomena", arXiv 2607.01483 (Jul 2026) (VERIFIED).
1. In soups of random byte programs (BFF, a Brainfuck variant; also Forth, Z80, 8080) with pairwise concatenate-execute-split interactions and no fitness function, self-replicators arise (about 40% of BFF runs within 16k epochs) and take over. This is tracked by high-order entropy and token-ancestry tracing.
2. Self-modifying code with a shared tape for the interacting pair. Mutation optional.
3. The 2026 follow-up by overlapping authors is deflationary: *replicators can be found at least as easily by simple mutation random walks in program space*. Ancestry-depth/width caps do not prevent replicator emergence; they only stop takeover. So "emergence through interaction" is weaker than claimed. Interaction matters for takeover, not for discovery.
4. High-order entropy (compressibility-based) and ancestry tracing.
5. Code public (PARTIAL; github cubff).
6. Directly Prometheus's byte-tape world. The key lesson is to separate *discovery* (how rare replicators are in random program space) from *propagation/takeover* (the interaction topology). The 2026 paper says these are distinct.
7. What happens after takeover? Do replicator ecologies accumulate capabilities, or does the soup freeze into one replicator family?
8. Anti-gravity: capabilities accumulating after the replicator transition with no fitness function, measured by compressibility trajectories.

### E5-24. Minimal cognition and evolved embodied agents (Beer); morphological computation (Pfeifer)
Cites: Beer, "The dynamics of active categorical perception in an evolved model agent", Adaptive Behavior 2003 (UNVERIFIED). Beer, "Toward a formal theory of minimal cognition / autopoiesis" (various) (UNVERIFIED). Pfeifer & Bongard, "How the Body Shapes the Way We Think", MIT Press 2006 (UNVERIFIED). Nakajima, "Backpropagation through soft body", arXiv 2503.05601 (VERIFIED existence).
1. Tiny evolved CTRNN agents (about 5 neurons) do categorical perception, discriminating circles from diamonds by *active scanning*. Dynamical analysis shows the categorisation lives in the brain-body-environment loop, not the controller. Morphological computation: passive dynamics (passive walkers, soft arms) offload control.
2. Evolution is a designed optimiser with a fitness function. The body/environment is simulated.
3. "Minimal cognition" can inflate trivial feedback control. Morphological computation lacks a quantitative definition (critiques by Muller & Hoffmann 2017, UNVERIFIED), so the offloaded computation is rarely measured.
4. Dynamical-systems analysis (state-space trajectories, bifurcations), plus performance versus lesions.
5. Simple to reimplement.
6. Computation split across agent and world. Prometheus needs a *measure* of how much of a task is done by the environment, which remains underdeveloped here.
7. A quantitative decomposition of "who computed what" between controller, body and environment. Information-theoretic (synergy, transfer entropy) attempts exist, but none is standard.
8. Anti-gravity: agents with no controller at all; bodies whose passive dynamics alone are selected for doing a task.

### E5-25. Tissue and packing mechanics that learn (2026)
Cites: Ameen, Zhang, Schwarz, "Training cell stress patterns in 3D cellular packings", arXiv 2604.25439 (Apr 2026) (VERIFIED). Dangol, "Untrainable elements determine what physical learning remembers", arXiv 2608.00097 (Jul-Aug 2026) (VERIFIED).
1. Vertex/Voronoi tissue models learn target stress patterns by contrastive adjustment of cell-shape parameters. Rigidity sets an exploration/exploitation tradeoff: soft tissue rearranges and learns, rigid tissue stays put. Sequential training is more robust than parallel training. Separately, in physical learning circuits, a *single fixed (untrainable) element* makes the learned function depend on initialisation scale (about 8-12% drift). The *structure*, not the learning rule, is the main inductive bias.
2. The contrastive rule is installed, and simulation only.
3. Preprints, not yet replicated.
4. Learning phase diagram (constraint load x rigidity x protocol) and drift of the learned function versus initialisation scale.
5. UNVERIFIED.
6. The second paper is highly relevant: in Prometheus worlds most of the substrate is *not* plastic. Frozen parts determine what is remembered and what inductive bias applies.
7. Measure the fraction of plastic versus frozen DOFs as a control parameter for what a substrate can learn.
8. Anti-gravity: the frozen skeleton *is* the prior. Change the substrate's fixed geometry and watch the learned function shift with no rule change.

---------------------------------------------------------------------------

## PART 2 -- WHAT PROMETHEUS SHOULD KNOW (9 bullets)

1. Almost every "learning without a computer" demonstration still INSTALLS the element-level rule (coupled learning, metamaterials, tissue models) or keeps a digital computer in the loop (physical neural networks, reservoir readouts, NCA backprop, DNA tile design). The truly unsolved problem, and Prometheus's niche, is where the local rule itself comes from. The best candidate answers are natural induction (stress-yielding couplings plus repeated perturbation) and implicit non-equilibrium memory (lag plus periodic forcing).
2. Memory without plasticity is cheap and generic. Fixed GRN dynamics, attractor switching, tube hierarchies and absorbed substances all store history. So "found memory" in a Prometheus world is NOT evidence of learning without a null model from random dynamics of the same class. Base rates are a must.
3. Habituation has a proven floor: linear time-invariant systems cannot habituate, while fading memory on two timescales plus a static nonlinearity suffices (2024 Gunawardena et al.; 2026 Smart/Shvartsman/Monnigmann). Use habituation as the first rung of a capability ladder that is cheap to test in any world.
4. Discovery and propagation are separable. The 2026 BFF follow-up shows replicators are about as easy to find by mutation random walks as by interaction, and that interaction topology governs takeover. Prometheus's byte-tape experiments should report both quantities separately.
5. Local-rule computers fail on long-range coordination (NCA-ARC failure modes; consensus time scales with diameter). Communication physics (latency, loss, topology) is therefore a *first-order* determinant of what collective substrates can compute. This is exactly the axis Prometheus varies in packet worlds, and it is under-studied.
6. Frozen/untrainable structure sets the inductive bias (2026). In mostly non-plastic worlds, the geometry of the frozen part determines what gets learned. Report the plastic fraction as a control parameter.
7. Timing-based computation is real and underexploited: nucleation races (DNA tiles), temporal alternation as the teacher signal (temporal contrastive learning), and Physarum anticipation of periodic events. Channels that carry no content but carry *when* can support learning.
8. Environment-as-memory (stigmergy, pheromone, Physarum tubes, salt uptake) has a capacity set by decay/evaporation and overwriting (Bhattacharyya/Zwicker/Alim 2023). There is an optimal forgetting rate, so a "no forgetting" world is not maximally capable.
9. Treat the Levin-program vocabulary (competency, delayed gratification, memory, cognitive light cone) as hypotheses to test, not as findings. The experimental kernels (re-cut tests, frozen-element perturbations) are reusable. The interpretive layer is contested and rarely has nulls.

---------------------------------------------------------------------------

## PART 3 -- MECHANISMS BY WHICH NON-NEURAL SUBSTRATES LEARN (with minimum conditions)

Legend: [M] = memory only (no generalisation), [H] = habituation/sensitisation (non-associative), [A] = associative, [S] = supervised/function-fitting, [O] = optimisation/generalisation.

L1. Fading-memory habituation [H]
 Minimum conditions: (a) at least two internal state variables with separated relaxation timescales; (b) a static nonlinearity (threshold/saturation) between state and response; (c) input repeated faster than the slow variable's relaxation. LTI systems provably insufficient.
 Examples: Stentor, Physarum, Gunawardena 2024 molecular networks, analog circuits (2026).

L2. State-based (attractor) memory in fixed dynamics [M, sometimes A]
 Minimum conditions: (a) multistability (at least 2 attractors) or slow manifolds; (b) inputs that can move the state between basins; (c) basins that persist longer than the inter-stimulus interval. For associative: a coupling so that the joint CS+UCS drives a basin transition that CS alone cannot, and then CS alone can trigger the new basin's response. NO parameter change needed.
 Examples: GRN Pavlovian memory (Biswas 2021; Pigozzi 2025), planarian bioelectric bistability.

L3. Use-dependent conductance (reinforcement plus decay) [M -> O]
 Minimum conditions: (a) a transport network; (b) edge capacity that grows with flux and (c) decays without it (forgetting); (d) conservation or competition (fixed total volume/budget) so that growth somewhere means shrinkage elsewhere. Capacity is set by the imprint/age balance.
 Examples: Physarum tube hierarchy, ant pheromone trails, Tero model; packet-routing analogues.

L4. Substance uptake / carried environment [M, H]
 Minimum conditions: (a) the stimulus is (or deposits) a material that can be internalised; (b) the response depends on the internal concentration; (c) slow clearance. Transferable by fusion/mixing.
 Examples: Physarum salt habituation and fusion transfer.

L5. Contrastive local learning: coupled learning / equilibrium propagation [S]
 Minimum conditions: (a) physics that relaxes to a steady state that extremises some functional; (b) two conditions (free vs nudged/clamped) applied to the same elements; (c) per-element memory of one condition while in the other (a twin network, a stored value, or implicit lag, see L6); (d) element parameters that change in proportion to the local difference; (e) an external source of the clamp (a teacher or environment).
 Examples: Dillavou et al. 2022/2024, elastic networks, shape-learning metamaterials (Coulais 2026), tissue stress learning (2026).

L6. Implicit non-equilibrium memory via temporal alternation [S]
 Minimum conditions: (a) as L5 (a) and (d); (b) periodic alternation of forcing (timing carries the teacher signal); (c) integral feedback / lag in the learning DOF so it effectively compares successive phases; (d) timescale separation (learning DOF much slower than state DOF); (e) dissipation (it has an energy cost, Landauer-like).
 Examples: Falk, Strupp, Scellier, Murugan (2023/2025).

L7. Natural induction: stress-yielding couplings under repeated perturbation [A, O]
 Minimum conditions: (a) a system that relaxes toward local energy minima; (b) couplings that yield plastically in the direction that reduces their own stress, slowly; (c) repeated perturbation/reset so many different minima are visited; (d) timescale separation (relaxation much faster than yielding, which is much slower than perturbation cadence); (e) frustration (not all constraints satisfiable at once). Produces Hebbian-equivalent change and improved attractors with no designed rule and no selection.
 Examples: Watson et al. 2011; Buckley et al. 2024; Watson, Levin, Lewens 2025. Physical realisations are mostly UNVERIFIED.

L8. Selection among variants (evolutionary / replicator dynamics) [O]
 Minimum conditions: (a) units that persist or replicate; (b) heritable variation, even crude, such as the shape of kinematic replicators; (c) differential persistence under resource limits. Discovery may need only mutation random walks. Takeover needs interaction topology (BFF 2026).
 Examples: BFF soups, kinematic replicators (heredity not shown), digital evolution.

L9. Reservoir plus adaptive readout [S]
 Minimum conditions: (a) fading memory; (b) nonlinearity; (c) enough independent degrees of freedom (capacity bound); (d) noise below the bound where stochasticity kills capacity; (e) a readout that adapts. In practice (e) is always external; a physical adaptive readout reduces to L5/L6.
 Examples: bucket of water, soft arms, spintronics, photonics.

L10. Structure-as-prior: frozen elements plus plastic elements [shapes all of the above]
 Minimum conditions: learning is defined only relative to a plastic subset; the frozen subset sets the inductive bias and history-dependence (2026). Rigidity/softness sets exploration versus exploitation (2026 tissue).

L11. Stigmergic accumulation (niche construction) [M, O]
 Minimum conditions: (a) agents modify a persistent shared medium; (b) the modifications change agents' future actions; (c) decay slower than the deposition rate at useful sites. Becomes capability accumulation only if (d) modifications feed back to agents' persistence (unshown in robotics; true in termites and ants).

RECURRENT MINIMUM CONDITIONS (the cross-mechanism core):
 C1. Separated timescales. Fast state dynamics plus slow modifiable variables (L1, L5, L6, L7). Nothing learns without a slow variable that integrates a fast one.
 C2. Nonlinearity or multistability. Needed to make history matter (L1 is provably impossible with LTI; L2 needs multiple attractors).
 C3. Use-dependent plasticity with decay. Change proportional to local activity or stress, plus forgetting (L3, L7, L11). Forgetting is not optional: capacity peaks at intermediate decay.
 C4. A contrast signal. Comparison between two conditions (free/clamped, before/after, stressed/relaxed). The contrast can be supplied by timing (alternation) instead of a stored copy (L5, L6, L7).
 C5. Repeated perturbation / reset. Many visits to many states so that slow variables average over experience (L7, L8, L1).
 C6. Constraint/competition/frustration. A conserved budget or unsatisfiable constraints, so improvement somewhere costs elsewhere (L3, L7).
 C7. Dissipation. Learning costs energy (L6 explicit bound). Equilibrium systems do not learn.
 The claim for Prometheus: C1 + C3 + C5 + C7 appear to be the jointly minimal set for learning with no designed rule (natural induction and temporal-contrastive routes). C4 can arise for free from environmental periodicity.

---------------------------------------------------------------------------

## PART 4 -- OPEN QUESTIONS (18)

1. Where does a local learning rule come from if nobody installs it? Can natural induction (L7) be demonstrated in a real physical material, not a Hopfield simulation?
2. What is the base rate of "memory" and "associative memory" in random dynamical systems of a given class? This null is needed before claiming any substrate learns.
3. Can environmental periodicity alone play the "clamp" for contrastive learning, with no teacher (L6 in the wild)?
4. What is the energy cost per bit of physical learning, and do biological substrates operate near it?
5. How do communication loss, latency and topology set the capability ceiling of a local-rule collective (consensus time, NCA long-range failure)? Is there a phase transition?
6. What fraction of plastic versus frozen DOFs maximises learnability, and does the optimum depend on task class (2026 frozen-element result)?
7. Can kinematic self-replication carry heritable variation (shape as genome) and become open-ended?
8. After replicator takeover in program soups, do capabilities accumulate or does the soup freeze? How can "capabilities not installed" be measured there?
9. What is the capacity (bits) of bioelectric pattern memory, and is voltage the store or the trigger?
10. Can state-based memory (L2) be *used* by the system to improve its own persistence, closing the loop from memory to adaptive advantage?
11. Is there a quantitative decomposition of how much computation the environment does versus the agent (morphological computation measure)?
12. When does memory in a shared medium (stigmergy) beat individual memory, as a function of channel noise and agent density?
13. Does substance-based memory transfer by fusion while structure-based memory does not, and is that a general classification?
14. Can NCA or discrete local rules generalise ARC-type transformations when given sparse long-range channels, or do they only memorise?
15. Do self-organising reservoirs, with physically adapting readouts, exceed fixed-reservoir capacity bounds?
16. Is there an operational, observer-independent measure of goal-directedness (counterfactual convergence) that separates homeostats from problem-solvers?
17. Can multicomponent self-assembly mixtures learn from repeated assembly cycles (not just classify with designed weights)?
18. What is the minimal motif for *associative* learning (analogous to L1's result for habituation), and is it provably out of reach for some dynamical classes?

---------------------------------------------------------------------------

## PART 5 -- OVERCLAIMS THE FIELD IS KNOWN FOR

1. "Robots" and "programmable organisms" (xenobots, anthrobots). The cells run their own developmental program; design mostly picks shapes. Critics and ethicists contest the robot framing.
2. "Self-replicating living robots": kinematic replication lasted at most about 4 rounds with experimenter-supplied feedstock, and showed no heredity or evolution.
3. Cognitive vocabulary for generic dynamics: "delayed gratification", "competency", "memory", "decision", "cognitive light cone" applied to sorting algorithms, GRNs and tissues without null models from random systems of the same class. The deflationary critique (Schulte 2024; "Mark of the Noncognitive" 2026) is that once the mechanism is known, the label adds nothing.
4. "Learning without a computer" when the element-level rule is engineered and a human supplies the clamp. The emergence is at network level only.
5. "Physical neural networks" and "reservoir computing in a bucket": the digital readout or digital twin does the learning, benchmarks are weak and inconsistent (2024 critique), and noise limits capacity.
6. "Emergence of life from interaction alone" (BFF 2024): walked back in part by a 2026 follow-up from overlapping authors. Mutation random walks find replicators just as easily.
7. NCA "solves ARC / rivals frontier LLMs": 13% of a pre-filtered subset of ARC-1 training tasks, or comparisons with weak LLM baselines.
8. "Slime mould solves mazes / designs Tokyo rail": real but it is flux-reinforcement optimisation. Intelligence framing exceeds the mechanism.
9. "Age reversal" in anthrobots, which rests on epigenetic clocks of contested meaning in cultured/reprogrammed cells.
10. Morphological computation is widely invoked but rarely quantified, and claims of offloaded computation usually lack a measured decomposition.
11. Causal-emergence / integrated-information increases as evidence of learning "making a self" (GRN 2025). The metrics themselves are contested.

---------------------------------------------------------------------------

## SOURCES CONSULTED THIS SESSION (URLs)
- https://arxiv.org/abs/2506.15746 (NCA for ARC-AGI, Xu & Miikkulainen)
- https://arxiv.org/abs/2505.08778 (ARC-NCA)
- https://arxiv.org/abs/2506.04912 ; https://google-research.github.io/self-organising-systems/difflogic-ca/
- https://www.annualreviews.org/doi/10.1146/annurev-conmatphys-040821-113439 (Stern & Murugan 2023)
- https://www.pnas.org/doi/10.1073/pnas.2319718121 ; https://arxiv.org/abs/2311.00537 (Dillavou 2024)
- https://arxiv.org/abs/2501.11958 (Coulais group, Nature Physics 2026)
- https://arxiv.org/abs/2312.17723 (Temporal contrastive learning)
- https://arxiv.org/abs/2608.00097 (Untrainable elements, 2026)
- https://arxiv.org/abs/2604.25439 (Tissue stress learning, 2026)
- https://www.pnas.org/doi/10.1073/pnas.2007815118 (Kramar & Alim 2021)
- https://arxiv.org/abs/2208.11192 (Memory capacity of adaptive flow networks)
- https://royalsocietypublishing.org/doi/abs/10.1098/rspb.2016.0446 (Physarum habituation)
- https://pubmed.ncbi.nlm.nih.gov/28003457/ (fusion transfer)
- https://arxiv.org/abs/2505.02114 (basal reservoir anticipation)
- https://www.cell.com/current-biology/fulltext/S0960-9822(24)01430-1 (Gunawardena 2024)
- https://arxiv.org/abs/2608.00249 (Dynamical principles of habituation, 2026)
- https://www.nature.com/articles/s42003-025-08411-2 (GRN conditioning causal emergence)
- https://pubmed.ncbi.nlm.nih.gov/39330098/ (Natural Induction, Entropy 2024)
- https://royalsocietypublishing.org/rsfs/article/15/6/20250025/366156/Evolution-by-natural-induction
- https://www.nature.com/articles/s41586-023-06890-z (Evans et al. 2024)
- https://www.pnas.org/doi/10.1073/pnas.2112672118 (kinematic self-replication)
- https://www.tandfonline.com/doi/abs/10.1080/15265161.2020.1746102 (xenobot ethics)
- https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.202409330 (anthrobot life cycle)
- https://journals.sagepub.com/doi/10.1177/10597123241269740 (self-sorting arrays)
- https://arxiv.org/abs/2201.10346 (TAME)
- https://royalsocietypublishing.org/doi/10.1098/rstb.2019.0765 (bistable somatic pattern memory)
- https://arxiv.org/abs/2406.19108 ; https://arxiv.org/abs/2607.01483 (BFF and deflationary follow-up)
- https://www.nature.com/articles/s41586-025-09384-2 (Training of PNNs review, 2025)
- https://arxiv.org/html/2405.06561v2 (RC benchmarks critique) ; https://arxiv.org/pdf/2307.14474 (stochastic RC restrictions)
- https://www.science.org/doi/10.1126/science.1245842 (TERMES)
- https://distill.pub/selforg/2021/adversarial/ (NCA adversarial reprogramming)
- https://link.springer.com/article/10.1007/s13752-026-00548-5 (A Mark of the Noncognitive)
- https://compass.onlinelibrary.wiley.com/doi/full/10.1111/phc3.70068 (plant cognition primer)
