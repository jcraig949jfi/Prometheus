# Open-endedness, Artificial Life, Quality-Diversity, Environment Generation and Self-Modifying Systems: the frontier from 2025 to Oct 2026

Compiled 2026-10-09. Scope excludes LLM-guided program evolution (AlphaEvolve/FunSearch/ShinkaEvolve-as-method), world models/cognitive architectures, and local-LLM lists; borderline items are flagged `[ADJACENT]`.

Verification legend used on every item:
- `[V-arXiv]`: title, authors, v1 date, latest-version date and author comments were confirmed with the arXiv export API (export.arxiv.org/api/query?id_list=...) on 2026-10-09. The "v1" date is the arXiv `published` field. An ID whose YYMM prefix is later than its v1 date usually means the paper was held in moderation.
- `[V-GH]`: stars, last push, creation date and latest release were confirmed with the GitHub REST API on 2026-10-09.
- `[V-prog]`: listed in the ALIFE 2026 program PDF ("Ver 2026-06-30", marked TENTATIVE), whose text was extracted locally.
- `[snippet]`: seen only in search-engine summaries or secondary pages, not in the primary record.
- `UNVERIFIED`: the claim could not be confirmed.
- `BACKGROUND`: dated before 2025.

---

## Q1. Most important works from 2025 through Oct 2026, by sub-field

### Takeaway
Most of the 2025–26 frontier sits in five clusters:
1. **Self-referential self-improvers in an open-ended archive.** This is the DGM to Hyperagents line, plus the Huxley-Gödel Machine. The HGM showed that a parent's benchmark score is a poor proxy for the productivity of its lineage.
2. **Foundation models used as the "interestingness/novelty" oracle for ALife search.** This covers ASAL, its VLM-guided descendants, and the Picbreeder replication.
3. **Computational-life / primordial-soup replicator emergence.** A sharp 2026 correction arrived here: two independent groups report that pairwise population coupling is *not* needed and may even slow replicator discovery.
4. **NCA/Lenia substrates becoming continuously-learning ecologies.** Examples are Petri-Dish NCA, PBT-NCA and Digital Ecosystems.
5. **Steady, incremental QD/UED algorithm work.** Examples are Dominated Novelty Search, regret- and co-learnability-based UED, and QD reframed as multi-objective optimisation.

Two kinds of work are thin in 2025–26: genuine major-transitions models and standardized open-endedness measurement.

### Cited Findings

#### A. Open-endedness: theory, positions, measurement, OEE claims
- **Hughes, Dennis, Parker-Holder, Behbahani, Mavalankar, Shi et al.**, "Open-Endedness is Essential for Artificial Superhuman Intelligence"; arXiv 2406.04268; v1 2024-06-06 (BACKGROUND; Google DeepMind open-endedness position paper) [V-arXiv] — [arXiv](https://arxiv.org/abs/2406.04268)
- **Sheth, Wehner, Abdelnabi, Binkyte, Fritz**, "Safety Must Precede the Deployment of Open-Ended AI"; arXiv 2502.04512; v1 2025-02-06, v4 2026-06-01. Comment: "Accepted to ICML'26". Position paper on safety risks of open-ended systems [V-arXiv] — [arXiv](https://arxiv.org/abs/2502.04512)
- **Kumar, Clune, Lehman, Stanley**, "Questioning Representational Optimism in Deep Learning: The Fractured Entangled Representation Hypothesis"; arXiv 2505.11581; v1 2025-05-16 [V-arXiv]. It compares networks found by open-ended (Picbreeder-style) search with SGD-trained networks of the same output, and argues that SGD yields "fractured entangled" internal representations while open-ended search yields unified, factored ones [snippet]. This is directly relevant to "retaining useful structure" — [arXiv](https://arxiv.org/abs/2505.11581); [alphaXiv listing](https://www.alphaxiv.org/researchers/jeff-clune)
- **Earle, Arulkumaran, Dai, Kumar, Togelius, Risi**, "In Search of the Ingredients of Open-Endedness: Replicating Picbreeder with Large Vision-Language Models"; arXiv 2605.23908; v1 2026-04-01, v2 2026-05-27; GECCO '26, July 13–17 2026, San José, Costa Rica [V-arXiv]. It was the only best-paper nominee in GECCO 2026's Complex Systems track — [arXiv](https://arxiv.org/abs/2605.23908); [GECCO 2026 nominations](https://gecco-2026.sigevo.org/Best-Paper-Nominations)
- **Xu, Zhu, Van Roy** (Stanford), "An Information-Theoretic Definition for Open-Ended Learning"; arXiv 2606.08369; v1 2026-06-06 [V-arXiv]. A formal definition, usable as a measurement target — [arXiv](https://arxiv.org/abs/2606.08369)
- **Cao, Yang**, "Beyond Fixed Representations: The Vocabulary and Verifier Gaps in Open-Ended AI"; arXiv 2607.09560; v1 2026-07-10 [V-arXiv] — [arXiv](https://arxiv.org/abs/2607.09560)
- **de Pinho, Sinapayen**, "A speciation simulation that partly passes open-endedness tests"; arXiv 2603.01701; q-bio.PE; v1 2026-03-02 [V-arXiv]. ToLSim shows unbounded *total* cumulative evolutionary activity. However, normalized activity appears bounded and *new* evolutionary activity is persistently null, so the authors conclude it is not open-ended [snippet]. This is a worked example of applying Bedau-style activity statistics as a falsification test — [arXiv](https://arxiv.org/abs/2603.01701)
- **Akhtyrchenko, Katsnelson, Ustyuzhanin**, "Directing Open-Ended Evolution in Artificial Life via Multi-Scale Path Divergence"; arXiv 2606.17091; cs.NE; v1 2026-06-12, v2 2026-08-03 [V-arXiv]. MSPD is a renormalization-group-inspired, interpretable complexity metric. It serves both as a gradient-free fitness for OEE and as a diagnostic. Static particles, Brownian motion and a single coherent blob all score near zero [snippet] — [arXiv](https://arxiv.org/abs/2606.17091); [arXiv HTML](https://arxiv.org/html/2606.17091v1)
- **Paolo, Warner, Shahrzad, Hodjat, Miikkulainen, Meyerson** (Cognizant AI Lab), "TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"; arXiv 2603.16910; cs.MA; v1 2026-03-06 [V-arXiv] [ADJACENT] — [arXiv](https://arxiv.org/abs/2603.16910)
- **Yuksel, Sawaf**, "EvoForest: A Novel Machine-Learning Paradigm via Open-Ended Evolution of Computational Graphs"; arXiv 2604.19761; v1 2026-03-26 [V-arXiv] — [arXiv](https://arxiv.org/abs/2604.19761)
- **Kumar, Bahlous-Boldi, Sharma, Isola, Risi, Tang et al.** (Sakana/MIT), "Digital Red Queen: Adversarial Program Evolution in Core War with LLMs"; arXiv 2601.03335; v1 2026-01-06 [V-arXiv]. It runs Red-Queen co-evolution of Core War warriors, a classic ALife substrate, with LLM mutation [ADJACENT: LLM-driven program evolution]. Code: [SakanaAI/drq](https://github.com/SakanaAI/drq) (pushed 2026-01-13, 226 stars [V-GH]) — [arXiv](https://arxiv.org/abs/2601.03335)
- **Qu, Zheng, Zhou et al.**, "CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery"; arXiv 2604.01658; v1 2026-04-02, v3 2026-09-02 [V-arXiv] [ADJACENT: LLM multi-agent] — [arXiv](https://arxiv.org/abs/2604.01658)
- "Hybrid Open-Ended Tri-Evolution Makes Better Deep Researcher" (HOTE); arXiv 2606.13710; June 2026 [snippet; not API-checked] [ADJACENT] — [arXiv](https://arxiv.org/abs/2606.13710)
- ALIFE 2026 talks on theory and definitions (all at Waterloo, 17–21 Aug 2026) [V-prog] — [ALIFE 2026 program PDF](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf):
  - Gershenson & Lopez Diaz, "Closing the Loop: How Semantic Closure Enables Open-Ended Evolution?" (summary)
  - Stepney, "An Engineering Definition of (Artificial) Life" (summary) and "From ALife Worlds to ALife World Views"
  - Bohm, "Where Does Life Begin? Persistence, Synergy, and the Continuity of Evolution"
  - Gupta & Adami, "Can AI Detect Life? Lessons from Artificial Life"
  - Andersen, Lin, Vorselen, Adams, Witkowski, "Weaving Cellular Automata: Open-Endedness and Creativity through Hybridising Computation" (poster)
  - Ziwei Ma, "Proxy Exploitation in a Minimal Signaling Ecology: How Confounded Evaluation Creates and Redistributes Exploitation Regimes" (poster). This is relevant as a falsification-instrument study.

#### B. Self-modifying / self-improving systems (DGM lineage) and autopoiesis
- **Zhang, Hu, Lu, Lange, Clune**, "Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents"; arXiv 2505.22954; v1 2025-05-29, v3 2026-03-12 [V-arXiv]. Published at ICLR 2026 (poster) — [ICLR 2026](https://iclr.cc/virtual/2026/poster/10007327).
  - Method: the agent edits its own code. Each change is validated empirically, and an archive of agents serves as stepping stones. Parent selection is roughly proportional to score and inversely proportional to the number of children with codebase-editing functionality.
  - Results: SWE-bench rose from 20.0% to 50.0% and Polyglot from 14.2% to 30.7% [snippet].
  - Code: [jennyzzt/dgm](https://github.com/jennyzzt/dgm), created 2025-05-23, last push 2025-08-13, 2,398 stars, no releases [V-GH] — [arXiv](https://arxiv.org/abs/2505.22954)
- **Zhang, Zhao, Yang, Foerster, Clune, Jiang, Devlin, Shavrina** (UBC/Vector/Edinburgh/NYU/Meta FAIR/MSL), "Hyperagents"; arXiv 2603.19461; v1 2026-03-19 [V-arXiv].
  - DGM-H merges the task agent and the meta (self-improvement) agent into one fully editable self-referential program, inside an open-ended archive search.
  - It was evaluated on coding, paper review, robotics reward design and Olympiad-math grading. The paper reports that meta-level improvements transfer across domains and accumulate across runs [snippet].
  - Code: [facebookresearch/HyperAgents](https://github.com/facebookresearch/HyperAgents), created 2026-03-19, last push 2026-07-31, 2,789 stars [V-GH]. A third-party doc page says the license is CC BY-NC-SA 4.0 [snippet] — [arXiv](https://arxiv.org/abs/2603.19461); [mintlify docs](https://www.mintlify.com/facebookresearch/HyperAgents/introduction)
- **Wang, Piękos, Nanbo, Laakom, Chen, Ostaszewski et al., with Schmidhuber** (KAUST), "Huxley-Gödel Machine: Human-Level Coding Agent Development by an Approximation of the Optimal Self-Improving Machine"; arXiv 2510.21614; v1 2025-10-24 [V-arXiv]. ICLR 2026 oral — [ICLR oral](https://www.iclr.cc/virtual/2026/oral/10009360); [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/821d20219c2f14850af1b5220f0ed13f-Abstract-Conference.html).
  - It defines a "Metaproductivity–Performance Mismatch": an agent's own benchmark score poorly predicts how useful its descendants will be.
  - It introduces **Clade-Metaproductivity (CMP)**, which aggregates the scores of all descendants. With the true CMP, the scheme reproduces the Gödel Machine's acceptance mechanism. Expansion uses Thompson sampling [snippet].
  - Code: [metauto-ai/HGM](https://github.com/metauto-ai/HGM), last push 2026-02-07, 437 stars [V-GH] — [arXiv](https://arxiv.org/abs/2510.21614)
- **Hu, Lu, Clune**, "Automated Design of Agentic Systems" (ADAS); arXiv 2408.08435; v1 2024-08-15, v2 2025-03-02 (BACKGROUND; ICLR 2025) [V-arXiv] — [arXiv](https://arxiv.org/abs/2408.08435)
- **Xiong, Hu, Clune**, "Learning to Continually Learn via Meta-learning Agentic Memory Designs"; arXiv 2602.07755; v1 2026-02-08 [V-arXiv] — [arXiv](https://arxiv.org/abs/2602.07755)
- "Group-Evolving Agents: Open-Ended Self-Improvement via Experience Sharing" is listed as an ICLR 2026 Lifelong Agents (LLA) workshop poster. Authors and arXiv id are UNVERIFIED [snippet] — [OpenReview LLA submissions](https://openreview.net/submissions?page=2&venue=ICLR.cc%2F2026%2FWorkshop%2FLLA)
- **Connor, Defant**, "The Minary Primitive of Computational Autopoiesis"; arXiv 2601.04501; math.DS; v1 2026-01-08 [V-arXiv]. It proposes a candidate formally provable autopoietic *self-maintenance* primitive (probabilistic event vectors with interference). Self-replication is left open [snippet] — [arXiv](https://arxiv.org/abs/2601.04501)
- **Cabaret**, "Emergence of autopoietic vesicles able to grow, repair and reproduce in a minimalist particle system"; arXiv 2311.10761 (BACKGROUND, 2023-11-14) [V-arXiv] — [arXiv](https://arxiv.org/abs/2311.10761)
- ALIFE 2026 work on self-modification and autopoiesis [V-prog] — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf):
  - C. A. O'Hara, "What Simulation Discloses: Emergence, Organizational Closure, and Autopoiesis in Self-Modifying Systems"
  - Banzhaf & Perrico, "Self-Modifying Linear Genetic Programming" (poster)
  - Hintze, Proschinger Åström, Millward-Sadler, "Giving Agentic AI a Self"
  - Letelier & Segura-Lepe, "A New Grounding For (M,R) Systems" (poster)
  - Letelier & Soto-Andrade's tutorial "Autopoiesis and Structural coupling: An overview"
  - Workshop "Autopoiesis, Self & Other: Modeling Autonomy, Boundaries, and Life(-like) & Mind(-like) Interactions in ALife" (Damiano, Stano, Nehaniv, Sirmai)

#### C. Computational life / primordial soups / artificial chemistry (self-replicator emergence)
- **Agüera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson et al.**, "Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction"; arXiv 2406.19108; v1 2024-06-27 (BACKGROUND) [V-arXiv]. This is the BFF soup paper. Code: [paradigms-of-intelligence/cubff](https://github.com/paradigms-of-intelligence/cubff), last push 2025-12-04, 207 stars [V-GH] — [arXiv](https://arxiv.org/abs/2406.19108)
- **Knierim, Versari, Obryk, Agüera y Arcas, Saurous** (Google Paradigms of Intelligence), "BFF: Simple explanations for complex phenomena"; arXiv 2607.01483; cs.NE; v1 2026-07-01 [V-arXiv]. It tests the claim that pairwise interaction is what makes replicators findable, against the rival that distribution-tuned random mutation walks work at least as well. Findings [snippet]:
  - Tuned mutation matches pairwise interaction.
  - Limiting the depth or width of the ancestry tree restricts takeover, not emergence.
  - The paper adds direct self-replicator detectors. The original work inferred replicators from a drop in compressed soup size.
  — [arXiv](https://arxiv.org/abs/2607.01483); [emergentmind](https://www.emergentmind.com/papers/2607.01483)
- **Papadopoulos, Hudcová, Dušek**, "Replicator Discovery Is Faster Without Population Coupling in a Self-Modifying Program Soup". ALIFE 2026 talk, 17 Aug 2026, "What is Life?" session [V-prog]. It independently converges with the Google paper above — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
- **Cicala, Niklasson, Randazzo, Boukortt, Basti, Etcheverry et al.**, "Coevolution of self-replication and function in a digital primordial soup"; arXiv 2607.09211; cs.NE; v1 2026-07-10, v2 2026-09-02 [V-arXiv]. Details [snippet]:
  - Setup: random 32-byte Z80 programs, where correct polynomial evaluation raises a program's interaction probability.
  - Self-replication and computation co-evolve from randomness.
  - Penalizing runtime ("metabolic cost") produces conditional execution.
  - Spatial task niches create an emergent curriculum built from stepping stones.
  - v1 and v2 differ, so check the current version.
  — [arXiv](https://arxiv.org/abs/2607.09211)
- ALIFE 2026 chemistry and replicator items [V-prog]:
  - Sayama & Horiguchi, "Space-Size-Driven Transition of Evolutionary Dynamics in Structural Cellular Hash Chemistry"
  - Biehl & Virgo, "Towards chemistries in dynamical systems"
  - Maslov & Tkachenko, "Onset of natural selection and catalytic function in prebiotic information-coding polymers" (summary)
  - Mognetti, Maslov, Tkachenko, "Evolutionary learning in dimerization networks" (summary)
  - Nagata, Lin, Yang, "Constructive Evolution in Chemical Space: Emergent Macro-Operations and Punctuated Dynamics…"
  - Workshop "Chemistry and Artificial Life Forms VI" (Čejková, Löffler, Rasmussen)
  - Workshop "LifeDef 2026: On a definition of life and observations of onset of life" (Rasmussen, Stepney, Sayama, Čejková, Löffler)
  — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)

#### D. ALife substrates: Lenia, NCA, particle/agent worlds, FM-guided search
- **Kumar, Lu, Kirsch, Tang, Stanley, Isola et al.** (Sakana/MIT/OpenAI/IDSIA), "Automating the Search for Artificial Life with Foundation Models" (ASAL); arXiv 2412.17799; v1 2024-12-23, v2 2025-05-16 [V-arXiv] (BACKGROUND/2025 revision).
  - A VLM scores simulation videos in three modes: target, open-endedness and illumination.
  - Substrates covered: Boids, Particle Life, Game of Life, Lenia and NCA.
  - Code: [SakanaAI/asal](https://github.com/SakanaAI/asal), JAX, last push 2025-10-23, 485 stars [V-GH]
  — [arXiv](https://arxiv.org/abs/2412.17799); [Sakana page](https://sakana.ai/asal/)
- **Baid, Erlebach, Hellegouarch, Wieser**, "Guiding Evolution of Artificial Life Using Vision-Language Models"; arXiv 2509.22447; v1 2025-09-26; ALIFE 2025 proceedings (MIT Press) [V-arXiv]. Its OE score is 1 minus the maximum CLIP similarity to earlier frames [snippet] — [arXiv](https://arxiv.org/abs/2509.22447)
- **Zhang, Risi, Darlow** (Sakana), "Petri Dish Neural Cellular Automata" (PD-NCA), 2025. A competitive population of NCA keeps learning by gradient descent inside the simulation. Reported behaviours include cyclic dynamics, territorial defense and cooperation, and the work was presented at ALIFE 2025 [snippet]. The arXiv id is UNVERIFIED. Code: [SakanaAI/petri-dish-nca](https://github.com/SakanaAI/petri-dish-nca), last push 2025-11-06 [V-GH] — [Sakana PD-NCA](https://sakana.ai/pd-nca/); [paper PDF](https://pub.sakana.ai/pdnca/assets/pdf/pdnca.pdf)
- **Berdica, Foerster, Hutter, Zela**, "Evolving Many Worlds: Towards Open-Ended Discovery in Petri Dish NCA via Population-Based Training"; arXiv 2604.11248; v1 2026-04-13, v2 2026-06-22 [V-arXiv]. PD-NCA is hyperparameter-fragile and collapses to frozen equilibria, noise or monocultures, so the authors add a PBT exploit/explore layer [snippet]. It is also an ALIFE 2026 talk [V-prog]. Code: [arberzela/pbt-nca](https://github.com/arberzela/pbt-nca), last push 2026-04-14 — [arXiv](https://arxiv.org/abs/2604.11248)
- **Darlow** (Sakana), "Digital Ecosystems: Interactive Multi-Agent Neural Cellular Automata". It is a browser platform, and a learned growth-gate steepness acts like a Langton-λ (frozen, critical or turbulent regimes) [snippet]. It is an ALIFE 2026 talk [V-prog] — [Sakana page](https://pub.sakana.ai/digital-ecosystem); [paper PDF](https://pub.sakana.ai/digital-ecosystem/paper/paper.pdf)
- **Béna, Faldor, Goodman, Cully**, "A Path to Universal Neural Cellular Automata"; arXiv 2505.13058; v1 2025-05-19; GECCO '25 Companion (Málaga) [V-arXiv]. It trains an NCA towards universal computation, culminating in an MNIST-classifying network emulated inside the CA state [snippet] — [arXiv](https://arxiv.org/abs/2505.13058)
- **Etcheverry, Miotti, Sirbu, Schürholt, Drozdova, Ghosh et al.**, "Reasoning with Neural Cellular Automata"; arXiv 2609.36126; v1 2026-09-28 [V-arXiv]. NCAs act as decentralized, damage-recovering visual reasoners that adapt their compute and scale to raw pixels [snippet] — [arXiv](https://arxiv.org/abs/2609.36126)
- **Hamon, Etcheverry, Chan, Moulin-Frier, Oudeyer**, "Discovering Sensorimotor Agency in Cellular Automata using Diversity Search"; arXiv 2402.10236 (2024-02-14). Journal version: Science Advances 11(44) eadp0834, 2025-10-31 [V-arXiv jref]. Diversity search plus curriculum plus gradient descent finds CA rules with self-organized moving, robust "individuals" — [arXiv](https://arxiv.org/abs/2402.10236); [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12577699/)
- **Guillet, Jülicher**, "Continuous Game of Life: cell emergence and self-organization at the edge of growth"; arXiv 2607.27402; v1 2026-07-29, v2 2026-09-05; "To be published in Artificial Life" [V-arXiv]. Code: codeberg.org/A-Guillet/cGoL — [arXiv](https://arxiv.org/abs/2607.27402)
- **Gupta**, "Collision-based logic in Lenia and its composition boundary"; arXiv 2609.01348; v1 2026-09-01. Code: github.com/ChakshuGupta13/lab [V-arXiv] — [arXiv](https://arxiv.org/abs/2609.01348)
- **Cool, Hartl, Levin, Petti**, "Agnosiophobia in a virtual agent: behavioral and dynamical architecture in Lenia"; arXiv 2605.30708; v1 2026-05-29 [V-arXiv]. ALIFE 2026 talk [V-prog] — [arXiv](https://arxiv.org/abs/2605.30708)
- **Pio-Lopez, Hartl, Levin**, "BraiNCA: brain-inspired neural cellular automata and applications to morphogenesis and motor control"; arXiv 2604.01932; v1 2026-04-02 [V-arXiv] — [arXiv](https://arxiv.org/abs/2604.01932)
- **Faldor, Cully**, "Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity" (Leniabreeder); arXiv 2406.04235 (BACKGROUND, ALIFE 2024) [V-arXiv]. Code: [maxencefaldor/Leniabreeder](https://github.com/maxencefaldor/Leniabreeder), last push 2025-04-02 — [arXiv](https://arxiv.org/abs/2406.04235)
- **Plantec, Hamon, Etcheverry, Oudeyer, Moulin-Frier, Chan**, "Flow-Lenia"; arXiv 2212.07906 (BACKGROUND) [V-arXiv]. Code: [erwanplantec/FlowLenia](https://github.com/erwanplantec/FlowLenia), last push 2026-10-09 [V-GH] — [arXiv](https://arxiv.org/abs/2212.07906)
- ALIFE 2026 substrate talks [V-prog]:
  - Oka, Tensen, Regan, Szep, Stanley, Chan, "Microcosmos: Reimagining Artificial Life for the GPU Era"
  - Risi, Mordvintsev, Barylli, Nisioti, Bena, "Self-Organising Digital Circuits"
  - Schauser, Risi, Najarro, Llera Montero, "Learning Developmental Scaffoldings to Guide Self-Organisation"
  - Hartl, Cvjetko, Moulin-Frier, Oudeyer, Levin, "The Artificial Experimentalist: Discovery and Control of Self-Organizing Phenomena with Autotelic RL"
  - Ludwig, Mordvintsev, Stovold et al., "Visualising the Attractor Landscape of NCA"
  - Khajehabdollahi et al., "Architecture Generalization with MetaNCA"
  - Plantec & Bessone, "Emergent Macro-Criticality from Micro-Critical Agents"
  - Hong & Song, "Expanding the Mathematical Foundations of ALife: A Systematic Search … in Lenia"
  - Bergeron & Papadopoulos, "Using Human Feedback and Reward Modeling to Search for Artificial Life"
  - Masumori, Maruyama, Doi, "OpenLife: Toward Open-World ALife with Autonomous LLM Agents"
  - Tang, Tian, Misaki, Ikegami, Akiba, Kuroki, "Shachi: … LLM-Based Agent-Based Modeling of Emergent Collective Behavior"
  — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)

#### E. Evolvability, digital evolution, major transitions
- PNAS, "Evolution takes multiple paths to evolvability when facing environmental change"; DOI 10.1073/pnas.2413930121.
  - Setup: Avida, six environment-change regimes, about 30,000 generations.
  - Findings: evolved mutational neighborhoods give rapid re-adaptation to previously seen environments, while higher mutation rates help in novel ones [snippet].
  - Publication date is UNVERIFIED; it appears to be late 2024 or early 2025.
  — [PNAS](https://www.pnas.org/doi/10.1073/pnas.2413930121)
- ALIFE 2026 evolvability items [V-prog]:
  - Hintze & Bohm, "The Surprising Evolvability of Unappreciated Cellular Automata"
  - Fontana & Wróbel, "Evolvability in Artificial Development of Large, Complex Structures and the Principle of Terminal Addition" (journal talk)
  - Ferguson & Escondo, "Summarizing Populations: Characterizing the Effects of Sampling in Computational Evolutionary Replay Experiments"
  - de Bruin, Glette, Ellefsen, "Lamarckian Inheritance in Dynamic Environments"
  - Erden, "Sexual Selection as a Mechanism of Evolutionary Information Preservation"
  — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
- ALIFE 2026 items on transitions and symbiosis [V-prog]:
  - van Gerven, Chaturvedi, El-Gazzar, "Role Differentiation in a Coupled Resource Ecology under Multi-Level Selection"
  - Johnson, Kelley, …, Vostinar, Lalejini, Dolson, Khalili, "Endosymbiotic mutualism can constrain host diversity and evolved complexity"
  - Mendoza, …, Vostinar, Dolson, Lalejini, "Saved by the Symbiont…"
  - Workshop "OTEL: Origins and Transitions in the Evolution of Learning" (Yoder, Gaskin, Pontes, Ferguson)
  — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
- **Samanta, Hazan, Levin**, "Training Ecosystems: A Computational Approach to Uncovering Learning Behavior in Unconventional Contexts"; arXiv 2605.30109; q-bio.PE; v1 2026-05-28 [V-arXiv] — [arXiv](https://arxiv.org/abs/2605.30109)
- **Pigozzi, Levin**, "The Causally Emergent Alignment Hypothesis: Causal Emergence Aligns with and Predicts Final Reward in RL Agents"; arXiv 2605.06746; v1 2026-05-07 [V-arXiv]. ALIFE 2026 poster [V-prog]. It proposes a candidate *early predictor* of final performance, the same shape of problem as HGM's CMP — [arXiv](https://arxiv.org/abs/2605.06746)
- **Zhang, Goldstein, Levin**, "Classical Sorting Algorithms as a Model of Morphogenesis"; arXiv 2401.05375 (BACKGROUND). Journal version: Adaptive Behavior 33(1):25–54, 2025 [snippet] — [arXiv](https://arxiv.org/abs/2401.05375)

#### F. Quality-Diversity / MAP-Elites descendants
- **Bahlous-Boldi, Faldor, Grillotti, Janmohamed, Coiffard, Spector et al.**, "Dominated Novelty Search: Rethinking Local Competition in Quality-Diversity"; arXiv 2502.00593; cs.NE; v1 2025-02-01 [V-arXiv]. GECCO 2025 [snippet].
  - QD is recast as a GA in which local competition happens through a fitness transformation: no grid, no bounds, and variable-dimensional descriptors are supported.
  - It is a drop-in replacement for the MAP-Elites grid.
  - Code: [adaptive-intelligent-robotics/Dominated-Novelty-Search](https://github.com/adaptive-intelligent-robotics/Dominated-Novelty-Search) [V-GH]
  — [arXiv](https://arxiv.org/abs/2502.00593)
- **Tsakonas, Chatzilygeroudis**, "Vector Quantized-Elites: Unsupervised and Problem-Agnostic QD Optimization"; arXiv 2504.08057; v1 2025-04-10, v3 2025-11-19; IEEE Transactions on Evolutionary Computation [V-arXiv] — [arXiv](https://arxiv.org/abs/2504.08057)
- **Janmohamed, Cully**, "Multi-Objective Quality-Diversity in Unstructured and Unbounded Spaces"; arXiv 2504.03715; v1 2025-03-28; GECCO 2025 [V-arXiv] — [arXiv](https://arxiv.org/abs/2504.03715)
- **Lin, Guo, Liu, Zhang, Sun**, "Quality-Diversity Optimization as Multi-Objective Optimization"; arXiv 2602.00478; v1 2026-01-31 [V-arXiv] — [arXiv](https://arxiv.org/abs/2602.00478)
- **Dai, Meinardus, Regan, Tian, Tang** (Sakana), "Discovering Novel LLM Experts via Task-Capability Coevolution"; arXiv 2604.14969; v1 2026-04-16; ICLR 2026 [V-arXiv]. It uses DNS for model selection because DNS handles variable-dimensional descriptors [snippet] — [arXiv](https://arxiv.org/abs/2604.14969)
- **Kuroki, Nakamura, Akiba, Tang** (Sakana), "Agent Skill Acquisition for LLMs via CycleQD"; arXiv 2410.14735; ICLR 2025 [V-arXiv] — [arXiv](https://arxiv.org/abs/2410.14735)
- **Donaghy, Rastogi**, "DEI: Diversity in Evolutionary Inference for QD Search"; arXiv 2605.27130; v1 2026-05-26; ICML 2026 Workshop SCALE [V-arXiv]. Heterogeneous LLMs serve as mutation operators across distributed nodes [snippet] — [arXiv](https://arxiv.org/abs/2605.27130)
- GECCO 2026 QD items:
  - Koohy & Bayne, "Distributional Value Estimation Without Target Networks for Robust Quality-Diversity", a best-paper nominee in the EML track — [nominations](https://gecco-2026.sigevo.org/Best-Paper-Nominations)
  - Companion-volume QD papers reported via dblp include a QD benchmark with variable constraints (Shyne & Cooper, "QDA-VC") and "discrete gene crossover speeds up QD" (Hutchinson, Herrmann, Smith) [snippet; UNVERIFIED titles] — [dblp GECCO Companion 2026](https://dblp.org/db/conf/gecco/gecco2026c.html)
- "IDEAgent: Agentic QD Search for Research Idea Generation"; arXiv 2607.22375 [snippet; not API-checked] [ADJACENT] — [arXiv](https://arxiv.org/html/2607.22375)

#### G. POET-style environment co-evolution and Unsupervised Environment Design (UED)
- **Faldor, Zhang, Cully, Clune**, "OMNI-EPIC: Open-endedness via Models of human Notions of Interestingness with Environments Programmed in Code"; arXiv 2405.15568; v1 2024-05-24, v3 2025-02-14; ICLR 2025 [V-arXiv]. Code: [maxencefaldor/omni-epic](https://github.com/maxencefaldor/omni-epic), last push 2024-12-26 [V-GH] — [arXiv](https://arxiv.org/abs/2405.15568)
- **Matthews, Beukman, Lu, Foerster**, "Kinetix: Investigating the Training of General Agents through Open-Ended Physics-Based Control Tasks"; arXiv 2410.23208; ICLR 2025 Oral [V-arXiv] — [arXiv](https://arxiv.org/abs/2410.23208)
- **Monette, Letcher, Beukman, Jackson, Rutherford, Goldie et al.** (Oxford), "An Optimisation Framework for UED"; arXiv 2505.20659; v1 2025-05-27; RLC 2025 [V-arXiv]. NCC: entropy-regularized game with two-timescale GDA, evaluated on Minigrid, XLand-MiniGrid and Craftax [snippet] — [arXiv](https://arxiv.org/abs/2505.20659)
- **Cho, Im, Lee, Yi, Kim, Kim**, "TRACED: Transition-aware Regret Approximation with Co-learnability for Environment Design"; arXiv 2506.19997; v1 2025-06-24, v5 2026-03-15; ICLR 2026 [V-arXiv] — [arXiv](https://arxiv.org/abs/2506.19997)
- **Furelos-Blanco, Pert, Kelbel, Spies, Russo, Dennis**, "Beyond Fixed Tasks: UED for Task-Level Pairs"; arXiv 2511.12706; v1 2025-11-16; AAAI 2026 [V-arXiv] — [arXiv](https://arxiv.org/abs/2511.12706)
- **Li, Tio, Varakantham**, "Efficient UED through Hierarchical Policy Representation Learning"; arXiv 2602.09813; v1 2026-02-10 [V-arXiv] — [arXiv](https://arxiv.org/abs/2602.09813)
- **Yuan, Yin, Shen, Xie, Yang, Qin et al.**, "PACE: Parameter Change for UED"; arXiv 2605.01358; v1 2026-05-02 [V-arXiv] — [arXiv](https://arxiv.org/abs/2605.01358)
- **Dharna, Lu, Clune**, "Foundation Model Self-Play: Open-Ended Strategy Innovation via Foundation Models"; arXiv 2507.06466; v1 2025-07-09; RLC 2025 [V-arXiv] — [arXiv](https://arxiv.org/abs/2507.06466)
- **Lu, Hu, Clune**, "Automated Capability Discovery via Foundation Model Self-Exploration"; arXiv 2502.07577; v1 2025-02-11 [V-arXiv] — [arXiv](https://arxiv.org/abs/2502.07577)
- **Guo, Yang et al.**, "GenEnv: Difficulty-Aligned Co-Evolution Between LLM Agents and Environment Simulators"; arXiv 2512.19682; v1 2025-12-22. Code: github.com/Gen-Verse/GenEnv [V-arXiv] [ADJACENT] — [arXiv](https://arxiv.org/abs/2512.19682)
- **Kang, Ye, Liu et al.**, "SimWorld Studio: Automatic Environment Generation with Evolving Coding Agent for Embodied Agent Learning"; arXiv 2605.09423; v1 2026-05-10 [V-arXiv] [ADJACENT] — [arXiv](https://arxiv.org/abs/2605.09423)
- **Fan, Yu, Cai et al.**, "Environment Evolution for Terminal Agents"; arXiv 2609.04128; v1 2026-09-03 [V-arXiv] [ADJACENT] — [arXiv](https://arxiv.org/abs/2609.04128)
- **Zong, Liu, Shen et al.**, "Co-Evolution in Agentic Systems: Toward Self-Directed Evolution Beyond Human Design" (survey); arXiv 2608.10299; v1 2026-08-10 [V-arXiv] — [arXiv](https://arxiv.org/abs/2608.10299)
- Nasir, Li, James, Togelius, "Mortar: Evolving Mechanics for Automatic Game Design", a GECCO 2026 EML best-paper nominee — [nominations](https://gecco-2026.sigevo.org/Best-Paper-Nominations)
- **Aki, Ikeda, Saito, Regan, Oka**, "LLM-POET"; arXiv 2406.04663 (BACKGROUND, 2024-06-07) [V-arXiv]. An LLM replaces the CPPN environment generator of Enhanced-POET [snippet] — [arXiv](https://arxiv.org/abs/2406.04663)
- DE-Gen (Mead et al., 2025) and COvolve (Sygkounas et al., 2026) are described in a 2026 survey as POET-lineage follow-ups. Both are UNVERIFIED: no primary record was found [snippet].

### Inferences
- **A direct falsification result Prometheus can reuse.** The 2026 BFF re-analysis and the ALIFE 2026 Papadopoulos et al. talk independently point the same way: population coupling (pairwise interaction) is not the causal ingredient for replicator emergence. It may even slow discovery, while coupling and ancestry structure govern *takeover*. This makes "emergence vs takeover" a separable pair of measurements. It also makes a "mutation-only twin" a necessary control for any soup-style claim.
- **HGM's mismatch is the same failure as a selector that cannot see novelty.** HGM's Metaproductivity–Performance Mismatch is the formal version: selecting on an agent's own score is a poor proxy for the value of its lineage. Clade-level scoring (CMP) and Levin's "causal emergence predicts final reward" are two candidate lineage-level predictors worth testing as selection signals.
- **Hyperagents makes the meta-mechanism itself the evolvable object.** Its claim that meta-level improvements transfer across domains and accumulate across runs is the closest published analogue to an ecology that retains improvement *mechanisms* rather than improved artifacts. It is a single-lab result: preprint, not yet in a peer-reviewed venue.
- **Two ready-made tools for an open-ended ecology.** DNS removes the need for predefined descriptor bounds. ToLSim-style evolutionary-activity tests (normalized and new activity, not only total) are a ready falsification battery for any "open-ended" claim.
- **FM-as-oracle is now the default ALife search method.** ASAL, the VLM-guided evolution paper, the Picbreeder replication and the human-feedback reward-model talk all use it. Results that depend on CLIP/VLM novelty therefore inherit the oracle's blind spots. MSPD is the first explicit attempt at an oracle-free, physics-grounded alternative.

### Gaps
- No Google DeepMind open-endedness team (Rocktäschel/Hughes) paper dated 2025–26 surfaced in searches, beyond talks. Their output may now sit in world-model work, which is out of scope, or the search may simply have missed it.
- Genuine *major-transitions* models from 2025–26 are scarce. Only ALIFE 2026 multi-level-selection and endosymbiosis talks were found, and no arXiv preprint specifically on egalitarian or fraternal transitions.
- No 2025–26 arXiv follow-up to ASAL by Sakana itself was found. The descendants come from other groups or from Sakana's NCA line.
- The PD-NCA arXiv id, the Group-Evolving Agents arXiv id, and the DE-Gen and COvolve primary records were not found.
- The full GECCO 2026 QD/ALife paper list could not be retrieved: dblp rate-limited and reset connections on 2026-10-09.
- ALIFE 2026 talk listings come from a TENTATIVE program dated 2026-06-30. The final proceedings table of contents at direct.mit.edu returned HTTP 403.

---

## Q2. Labs, groups and individuals that produce most of this work

### Takeaway
Output is concentrated in a few clusters:
1. **Clune lab (UBC/Vector).** Mostly self-improvement and FM-driven open-endedness, now partly co-run with Meta FAIR/MSL.
2. **Sakana AI.** ASAL, the NCA ecologies, Digital Red Queen and CycleQD. Risi holds a joint ITU role.
3. **Imperial AIRL (Cully).** QD algorithms, QDax, DNS, CAX and universal NCA.
4. **Oxford FLAIR (Foerster).** JAX open-ended RL environments and UED.
5. **Google Paradigms of Intelligence / self-organising-systems.** BFF soups and NCA.
6. **Levin lab (Tufts) and the INRIA Flowers lineage.** Lenia, NCA agency and autotelic discovery.
7. **Individual ALife groups,** visible mainly through ALIFE/GECCO: Sayama, Hintze/Bohm, Vostinar/Lalejini/Dolson, Stepney, Gershenson.

### Cited Findings
- **UBC / Jeff Clune lab** (also Vector Institute).
  - 2025–26 outputs: DGM (ICLR 2026), Hyperagents (with Meta), Automated Capability Discovery, Foundation Model Self-Play (RLC 2025), meta-learned agentic memory, and the FER hypothesis — [DGM](https://arxiv.org/abs/2505.22954); [Hyperagents](https://arxiv.org/abs/2603.19461); [ACD](https://arxiv.org/abs/2502.07577); [FMSP](https://arxiv.org/abs/2507.06466)
  - "Towards end-to-end automation of AI research" (Lu, Lu, Lange, Yamada, Hu, Foerster, Ha, Clune) is reported as Nature 651(8107):914–919, 2026 [snippet; out of scope: AI-scientist line] — [search source](https://www.alphaxiv.org/researchers/jeff-clune)
  - Code lives under personal GitHub accounts: [jennyzzt/dgm](https://github.com/jennyzzt/dgm), [maxencefaldor/omni-epic](https://github.com/maxencefaldor/omni-epic).
  - Curated list: [jennyzzt/awesome-open-ended](https://github.com/jennyzzt/awesome-open-ended), 475 stars, last push 2026-09-19 [V-GH]. This is a high-value watch-list source.
  - Author index: [dblp: Jeff Clune](https://dblp.org/pid/49/2799.html)
- **Meta FAIR / Meta Superintelligence Labs** (Minqi Jiang, Sam Devlin, Tatiana Shavrina) co-authored Hyperagents. GitHub: [facebookresearch](https://github.com/facebookresearch/HyperAgents). Meta's publication page: [ai.meta.com](https://ai.meta.com/research/publications/hyperagents)
- **Sakana AI** (Tokyo).
  - ALife and QD outputs: ASAL, PD-NCA, Digital Ecosystems, Digital Red Queen, CycleQD, Task-Capability Coevolution, and Shachi (ALIFE 2026). It also produces ShinkaEvolve, which is out of scope.
  - GitHub org [SakanaAI](https://github.com/SakanaAI): Organization, 63 public repos, blog field https://sakana.ai/ [V-GH]
  - Hugging Face org [SakanaAI](https://huggingface.co/SakanaAI) exists; the API returns models such as SakanaAI/EvoVLM-JP-v1-7B [verified via HF models API 2026-10-09]
  - Project pages are hosted at pub.sakana.ai — [ASAL](https://sakana.ai/asal/); [PD-NCA](https://sakana.ai/pd-nca/)
  - The PPSN 2026 booklet describes Sebastian Risi as a Research Scientist at Sakana AI who leads the Creative AI Lab at ITU Copenhagen. His PPSN keynote "Building Collective Intelligence Across Scales" was on 31 Aug 2026 — [PPSN booklet](https://ppsn2026.disi.unitn.it/docs/PPSN_booklet.pdf)
- **ITU Copenhagen Creative AI Lab** (Risi, Najarro, Nisioti).
  - 2026 outputs: the Picbreeder replication (GECCO 2026 nominee), plus the ALIFE 2026 talks "Self-Organising Digital Circuits" and "Learning Developmental Scaffoldings" — [arXiv 2605.23908](https://arxiv.org/abs/2605.23908); [ALIFE 2026 program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
  - No 2026 arXiv paper by Risi specifically on NCA evolution was found by search — [dblp Risi](https://dblp.org/pid/81/7183)
- **MIT (Phillip Isola) / Akarsh Kumar.** Kumar is first author on ASAL, the FER hypothesis and Digital Red Queen, and co-authored the Picbreeder replication — [ASAL](https://arxiv.org/abs/2412.17799); [FER](https://arxiv.org/abs/2505.11581); [DRQ](https://arxiv.org/abs/2601.03335)
- **Imperial College Adaptive & Intelligent Robotics Lab** (Antoine Cully, Maxence Faldor, Luca Grillotti, Hannah Janmohamed).
  - Outputs: DNS, MOQD, Universal NCA, CAX, Leniabreeder and QDax.
  - GitHub org [adaptive-intelligent-robotics](https://github.com/adaptive-intelligent-robotics): 32 public repos [V-GH]
  - Lab site: http://www.imperial.ac.uk/adaptive-intelligent-robotics [V-GH blog field]
  — [DNS](https://arxiv.org/abs/2502.00593); [Universal NCA](https://arxiv.org/abs/2505.13058)
- **Oxford FLAIR** (Jakob Foerster; Beukman, Matthews, Rutherford, Chris Lu).
  - Outputs: Kinetix (ICLR 2025 oral), Craftax, JaxLife, JaxUED, the NCC UED optimisation framework (RLC 2025), and PBT-NCA (with Hutter and Zela, Freiburg/ELLIS).
  - GitHub org [FLAIROx](https://github.com/FLAIROx): 17 public repos [V-GH]. No Hugging Face org found under "FLAIR" [HF API empty].
  — [Kinetix](https://arxiv.org/abs/2410.23208); [NCC](https://arxiv.org/abs/2505.20659); [PBT-NCA](https://arxiv.org/abs/2604.11248)
- **UCL DARK / Google DeepMind Open-Endedness team.**
  - Tim Rocktäschel is Director, Principal Scientist and Open-Endedness Team Lead at Google DeepMind, and Professor at UCL. His 2025 talks framed open-endedness through foundation world models — [Stuttgart lecture listing](https://www.isa.uni-stuttgart.de/en/institute/news/event/Distinguished-Lecture-Series-Tim-Rocktaeschel/)
  - Edward Hughes argued that "2025 is the year of open-endedness" — [Air Street Press](https://press.airstreet.com/p/edward-hughes-raais-2025)
  - GitHub: [ucl-dark](https://github.com/ucl-dark) has 9 public repos; [google-deepmind](https://github.com/google-deepmind) has 409 public repos [V-GH]. No ucl-dark Hugging Face org found [HF API empty].
  - The legacy UED stack (minimax, dcd) is stale or archived; see Q4.
- **Google Paradigms of Intelligence** (Blaise Agüera y Arcas) and **Google Research self-organising-systems** (Mordvintsev, Randazzo, Niklasson).
  - Outputs: Computational Life/BFF, the 2026 "simple explanations" re-analysis, and the Z80 soup coevolution.
  - GitHub orgs: [paradigms-of-intelligence](https://github.com/paradigms-of-intelligence) (12 public repos) and [google-research/self-organising-systems](https://github.com/google-research/self-organising-systems) (last push 2026-01-09; release biomaker-v1.0.0, 2024-02-07) [V-GH]
  — [2607.01483](https://arxiv.org/abs/2607.01483); [2607.09211](https://arxiv.org/abs/2607.09211)
- **Michael Levin lab (Tufts / Allen Discovery Center).**
  - 2026 computational preprints: Training Ecosystems, the Causally Emergent Alignment Hypothesis, Language Game (arXiv 2605.16321, 2026-05-05 [V-arXiv]), BraiNCA, Agnosiophobia in Lenia, and "A Little Rank Goes a Long Way" (arXiv 2604.08749 [snippet]).
  - Non-arXiv 2026 work includes "Topological constraints on self-organization in locally interacting systems" (Phil. Trans. A) [snippet].
  - Publication pages to watch: [Levin Lab preprints](https://www.drmichaellevin.org/publications); [arXiv 2605.16321](https://arxiv.org/abs/2605.16321)
- **INRIA Flowers** (Oudeyer, Moulin-Frier) with Etcheverry, Hamon and Chan. Outputs: sensorimotor agency (Science Advances, 2025-10-31), Flow-Lenia, and "The Artificial Experimentalist" (ALIFE 2026) — [arXiv 2402.10236](https://arxiv.org/abs/2402.10236). The GitHub org "flowersteam" is UNVERIFIED: the GitHub API was rate-limited before the check.
- **Cognizant AI Lab** (Miikkulainen, Meyerson, Paolo, Hodjat). Output: TerraLingua (2026) — [arXiv](https://arxiv.org/abs/2603.16910)
- **KAUST AI Initiative** (Schmidhuber). Output: Huxley-Gödel Machine (ICLR 2026 oral). GitHub: [metauto-ai](https://github.com/metauto-ai/HGM) — [arXiv](https://arxiv.org/abs/2510.21614)
- **Stanford** (Benjamin Van Roy). Output: an information-theoretic definition of open-ended learning — [arXiv](https://arxiv.org/abs/2606.08369)
- **Cross Labs** (Kyoto; Olaf Witkowski).
  - Search found no dated 2026 papers. Witkowski appears as co-author on the ALIFE 2026 poster "Weaving Cellular Automata: Open-Endedness and Creativity…" and co-organised the ALIFE 2026 BCI tutorial — [ALIFE 2026 program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
  - Background on the institute — [HackerNoon interview](https://sia.hackernoon.com/deep-learning-is-already-dead-towards-artificial-life-with-olaf-witkowski-kv163t0d)
- **Other recurring ALife authors in 2026,** from the ALIFE 2026 program — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf):
  - Hiroki Sayama (Binghamton): hash chemistry
  - Arend Hintze and Clifford Bohm: evolvability of cellular automata
  - Anya Vostinar, Alexander Lalejini and Emily Dolson: endosymbiosis in digital evolution
  - Susan Stepney (York): definitions of life
  - Carlos Gershenson: semantic closure
  - Takashi Ikegami (Tokyo): NCA ontogeny
  - Mizuki Oka with Ken Stanley and Bert Chan: Microcosmos, a GPU ALife platform
  - Joel Lehman: co-organiser of the "Agent Ethology" workshop
- **Lana Sinapayen.** Co-author of the ToLSim open-endedness test (2026) — [arXiv](https://arxiv.org/abs/2603.01701)
- **Uber AI legacy (POET).** The repo is dormant: [uber-research/poet](https://github.com/uber-research/poet), last push 2022-03-23 [V-GH]

### Inferences
- Watch-list priority by output density in 2025–26:
  1. jennyzzt/awesome-open-ended plus Clune-lab arXiv authors (Jenny Zhang, Shengran Hu, Cong Lu)
  2. Sakana (pub.sakana.ai, github.com/SakanaAI)
  3. Imperial AIRL
  4. FLAIR
  5. Google PoI / self-organising-systems
  6. Levin lab preprints page
  7. INRIA Flowers authors (Etcheverry, Hartl, Plantec)
- Several key people bridge labs: Risi (Sakana and ITU), Kumar (MIT, Sakana and Clune collaborations), Foerster (FLAIR, Meta and Hyperagents), and Etcheverry (Flowers lineage, now co-authoring the Google soup and NCA-reasoning papers). Author-based polling will catch more than org-based polling.
- Hugging Face is not where this community publishes. Only Sakana has a meaningful HF org; code lives on GitHub, often under personal accounts.

### Gaps
- No Santa Fe Institute output specific to 2025–26 open-endedness or ALife was found in searches.
- The Cross Labs 2026 publication record was not found.
- No DeepMind open-endedness paper was found (see Q1 Gaps).
- The GitHub orgs for INRIA Flowers ("flowersteam") and the Hintze lab ("Hintzelab", MABE) are UNVERIFIED because of the API rate limit.
- Blog URLs other than sakana.ai and the Levin lab page were not verified.

---

## Q3. Venues and workshops (2025 and 2026 dates, proceedings, OpenReview ids)

### Takeaway
The core venues are ALIFE (MIT Press open-access proceedings), GECCO (ACM DL; Complex Systems and EML tracks), the Artificial Life journal and EvoStar.

The big-ML venues no longer host a dedicated open-endedness workshop: ALOE ran last at NeurIPS 2023. The topic has dispersed into these workshops instead:
- ICLR 2026: "Lifelong Agents" (LLA) and "AI with Recursive Self-Improvement" (RSI)
- NeurIPS 2025: "Scaling Environments for Agents" (SEA)
- ICML 2026: SCALE

These are on OpenReview; ALIFE and GECCO are not.

### Cited Findings
- **ALIFE 2025 ("Ciphers of Life")**: Kyoto, Japan plus online, 6–10 October 2025 — [2025.alife.org](https://2025.alife.org/)
  - Proceedings: "ALIFE 2025: Ciphers of Life: Proceedings of the Artificial Life Conference 2025", MIT Press (direct.mit.edu) — [Complex Systems Digest notice](https://comdig.cssociety.org/2025/12/04/alife-2022-the-2022-conference-on-artificial-life-mit-press-2/)
  - Exact volume URL is UNVERIFIED. By the 2026 pattern it is probably direct.mit.edu/isal/isal2025/volume/37, which is an inference.
  - The workshop "Cultural Evolution of Planet X" was held 7 Oct 2025 — [workshop site](https://sites.google.com/view/planetx-alife2025/home)
- **ALIFE 2026 (27th Conference on Artificial Life)**: Waterloo, Ontario, 17–21 August 2026, at Wilfrid Laurier University, held jointly with AMMCS — [ISAL announcement](https://alife.org/2025/08/15/announcement-of-alife-2026-venue-dates-and-organizers/); [2026.alife.org](https://2026.alife.org/)
  - Full papers (3–8 pages) are peer-reviewed and published open access by MIT Press. Summaries are presented but not included in the proceedings. The deadline was extended to 12 April 2026, and camera-ready was due 21 June 2026 — [CfP](https://2026.alife.org/call-for-papers/)
  - Proceedings URL: https://direct.mit.edu/isal/isal2026/volume/38 — [Complex Systems Digest](https://comdig.cssociety.org/2026/09/06/alife-2026-proceedings-of-the-2026-artificial-life-conference/). The page returned HTTP 403 to automated fetch.
  - Workshops and tutorials (ALIFE 2026 program, tentative) [V-prog]:
    - ALife in Organizations
    - Autopoiesis and Structural Coupling (tutorial)
    - Information Theoretic Approaches in the (Artificial) Life Sciences
    - OTEL: Origins and Transitions in the Evolution of Learning
    - LifeDef 2026
    - Emerging Researchers in ALife (ERA)
    - Robot Evolution: From Evolutionary Robotics to Physical AI
    - Robot Ecology
    - Open Research Questions in Sugarscape After 30 Years
    - Virtual Creature Competition (organised by Federico Pigozzi)
    - Autopoiesis, Self & Other
    - ALife for Social and Environmental Good
    - Agent Ethology (Hu, Rong, Lehman)
    - Agentic and Generative AI as Artificial Life (Nichele, Suzuki et al.)
    - Henkaku Village
    - Teaching (with) ALife
    - Chemistry and Artificial Life Forms VI
    - Reservoir Computing
    - "Artificial Life in the Wild", a hybrid workshop on 20 Aug 2026 — [Luma](https://luma.com/5nhlwhi4)
    - Source for the list: [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)
  - No workshop titled "open-ended evolution" (OEE) was found at ALIFE 2026.
- **ALIFE 2027**: a UCT Prague (vscht.cz) news post is titled "The Road to ALIFE 2027 Begins in Waterloo". The host city is inferred as Prague but is UNVERIFIED — [VSCHT news](https://alife.vscht.cz/news/260816waterloo)
- **GECCO 2025**: Málaga, Spain, 14–18 July 2025, as stated in the comment on arXiv 2505.13058 — [arXiv](https://arxiv.org/abs/2505.13058). Table of contents: [sigevo.org GECCO 2025 TOC](https://www.sigevo.org/gecco-2025/toc.html)
- **GECCO 2026**: Costa Rica (venue in San Antonio de Belén near San José), 13–17 July 2026, hybrid. Full papers appear in the ACM DL Main Proceedings and posters in the Companion (ISBN 979-8-4007-2488-6). Full papers were due 26 Jan 2026 — [GECCO 2026 site](https://gecco-2026.sigevo.org/); [CfP](https://sigevo.hosting.acm.org/gecco-2026/Call+for+Papers)
  - Relevant workshops include:
    - Evolving self-organisation
    - Large Language Models for and with Evolutionary Computation
    - BENCH@GECCO26 (good benchmarking practices)
    - Open Source Software for EC
    - ECADA (16th, on automated design of algorithms)
    - Program Synthesis
    - Source: [GECCO 2026 workshops](https://gecco-2026.sigevo.org/Workshops); [ESO workshop notice](https://comdig.cssociety.org/2026/03/10/evolving-self-organisation-workshop-gecco-2026/)
  - Best-paper nominees relevant here: in Complex Systems, the Picbreeder-with-VLMs paper; in EML, "Mortar" and "Distributional Value Estimation … Robust QD" — [nominations](https://gecco-2026.sigevo.org/Best-Paper-Nominations)
  - dblp index: [GECCO Companion 2026](https://dblp.org/db/conf/gecco/gecco2026c.html)
  - GECCO 2027 CfP page exists — [gecco-2027.sigevo.org](https://gecco-2027.sigevo.org/Call-for-Papers)
- **EvoStar 2026**: Toulouse, France, 8–10 April 2026, hybrid (EuroGP, EvoApplications, EvoCOP, EvoMUSART). **EvoStar 2027**: Mainz, 31 March–2 April 2027, submission deadline 1 November 2026 — [evostar.org](https://evostar.org)
- **PPSN 2026**: Trento; Risi keynote on 31 Aug 2026 — [booklet](https://ppsn2026.disi.unitn.it/docs/PPSN_booklet.pdf)
- **Artificial Life journal (MIT Press)**: "Continuous Game of Life" (arXiv 2607.27402) is listed as "To be published in Artificial Life" — [arXiv](https://arxiv.org/abs/2607.27402). An earlier ALife-journal example is "Evolvability Tradeoffs in Emergent Digital Replicators" (BACKGROUND) — [direct.mit.edu/artl](https://direct.mit.edu/artl/article/22/4/483/2846/Evolvability-Tradeoffs-in-Emergent-Digital)
- **Science Advances**: published the sensorimotor-agency-in-CA paper on 2025-10-31 — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12577699/)
- **ICLR 2026** (Rio de Janeiro; workshops 26–27 April 2026) — [ICLR 2026 workshops](https://iclr.cc/virtual/2026/events/workshop); [Agents in the Wild](https://agentwild-workshop.github.io/)
  - Main conference: DGM (poster) and HGM (oral) appeared; TRACED and Task-Capability Coevolution were accepted.
  - Relevant workshops:
    - "Lifelong Agents: Learning, Aligning, Evolving" (26 Apr; OpenReview `ICLR.cc/2026/Workshop/LLA`, confirmed in OpenReview URLs)
    - "AI with Recursive Self-Improvement" (26 Apr; OpenReview group `ICLR.cc/2026/Workshop/RSI`). The RSI id was confirmed via the OpenReview groups API; matching it to this title is an inference from the name.
    - "Multi-Agent Learning … Era of Generative AI" (27 Apr)
    - MemAgents (OpenReview group `ICLR.cc/2026/Workshop/MemAgent`)
    - Agents in the Wild (`AIWILD`)
  - No workshop on open-endedness, ALife or evolutionary computation was found at ICLR 2026.
  - Sources: [OpenReview LLA](https://openreview.net/submissions?page=2&venue=ICLR.cc%2F2026%2FWorkshop%2FLLA); [OpenReview groups API](https://api2.openreview.net/groups?prefix=ICLR.cc/2026/Workshop/)
- **NeurIPS 2025**: the only clearly matching workshop is "Workshop on Scaling Environments for Agents", 7 Dec 2025 (OpenReview group `NeurIPS.cc/2025/Workshop/SEA`; the id–title match is an inference). No open-endedness, ALife or evolution workshop was listed — [NeurIPS 2025 workshops](https://neurips.cc/virtual/2025/events/workshop); [OpenReview groups API](https://api2.openreview.net/groups?prefix=NeurIPS.cc/2025/Workshop/)
- **Earlier ML-venue workshops** (BACKGROUND): "Agent Learning in Open-Endedness" (ALOE) at NeurIPS 2023, and IMOL at NeurIPS 2023 and 2024 — [ALOE 2023](https://neurips.cc/virtual/2023/workshop/66527); [NeurIPS 2024 workshops](https://neurips.cc/virtual/2024/events/workshop). minimax was "Presented at ALOE 2023" — [arXiv 2311.12716](https://arxiv.org/abs/2311.12716)
- **ICML 2026**:
  - Workshop groups on OpenReview include `ICML.cc/2026/Workshop/SCALE`, where DEI was accepted, and `AI4Research`; there is no open-endedness workshop — [OpenReview groups API](https://api2.openreview.net/groups?prefix=ICML.cc/2026/Workshop/); [DEI arXiv](https://arxiv.org/abs/2605.27130)
  - "Safety Must Precede the Deployment of Open-Ended AI" was accepted to the ICML 2026 main track — [arXiv](https://arxiv.org/abs/2502.04512)
- **RLC 2025**: venue for NCC-UED and Foundation Model Self-Play. **AAAI 2026**: venue for UED Task-Level Pairs — [2505.20659](https://arxiv.org/abs/2505.20659); [2507.06466](https://arxiv.org/abs/2507.06466); [2511.12706](https://arxiv.org/abs/2511.12706)

### Inferences
- For a polling pipeline, the OpenReview groups API (`api2.openreview.net/groups?prefix=<Venue>/<Year>/Workshop/`) lists each year's workshop ids. A keyword filter on workshop names is enough to detect a revived open-endedness workshop.
- ALIFE and GECCO need non-OpenReview pollers:
  - direct.mit.edu/isal (volume ids 38 for 2026, presumably 37 for 2025)
  - dblp `conf/gecco` and `conf/alife`. dblp throttles aggressively, so cache responses and back off.
  - the Complex Systems Digest (comdig.cssociety.org), which reposts proceedings and workshop calls
- The upcoming deadlines Prometheus could target for submission or monitoring are EvoStar 2027 (1 Nov 2026) and GECCO 2027 (CfP live). ALIFE 2027 is likely Prague (unverified).

### Gaps
- No exact 2025 ALIFE proceedings URL or DOI prefix was verified.
- The final ALIFE 2026 table of contents was not readable (403).
- GECCO 2026 track-level accepted-paper lists were not retrieved because dblp was throttled.
- ICLR/NeurIPS conference-level OpenReview ids were not separately queried. `ICLR.cc/2026/Conference` and `NeurIPS.cc/2025/Conference` follow the standard pattern but were not checked.
- No information was found on whether the Artificial Life journal ran a 2025–26 special issue on open-endedness.

---

## Q4. Active open-source frameworks and libraries (GitHub URLs, last-release dates)

### Takeaway
Activity is concentrated in JAX and accelerated stacks. The following were active within the last ~4 months as of 2026-10-09: pyribs, evosax, EvoX, EvoTorch, CAX, Kinetix, Craftax and ALIEN.

QDax's last release was May 2025; XLand-MiniGrid's was December 2025.

These are stale or archived and should not be treated as live: OpenELM (2023), minimax (2024), POET (2022), JaxLife (2024), dcd (archived), evojax (archived) and Avida (last release 2021).

### Cited Findings
All figures come from the GitHub REST API on 2026-10-09: stars / last push / latest release tag and date [V-GH].

**Quality-Diversity and evolutionary computation libraries**
- **QDax** (Imperial AIRL + InstaDeep): 360 / pushed 2025-10-30 / v0.5.0 on 2025-05-27. Paper: arXiv 2308.03665 (journal venue not verified here) — [GitHub](https://github.com/adaptive-intelligent-robotics/QDax); [arXiv](https://arxiv.org/abs/2308.03665)
- **pyribs** (USC ICAROS): 265 / pushed 2026-07-22 / v0.12.0 on 2026-07-22. Paper: arXiv 2303.00191 (GECCO '23) — [GitHub](https://github.com/icaros-usc/pyribs); [arXiv](https://arxiv.org/abs/2303.00191)
- **evosax** (R. T. Lange): 798 / pushed 2026-08-17 / tag "v.0.3.1" on 2026-08-17. Paper: arXiv 2212.04180 — [GitHub](https://github.com/RobertTLange/evosax); [arXiv](https://arxiv.org/abs/2212.04180)
- **EvoTorch** (NNAISENSE): 1,149 / pushed 2026-10-05 / v0.6.1 on 2025-05-14. Paper: arXiv 2302.12600 — [GitHub](https://github.com/nnaisense/evotorch); [arXiv](https://arxiv.org/abs/2302.12600)
- **EvoX** (EMI-Group): 2,640 / pushed 2026-10-09 / v1.4.0 on 2026-09-09. Paper: arXiv 2301.12457 (IEEE TEVC) — [GitHub](https://github.com/EMI-Group/evox); [arXiv](https://arxiv.org/abs/2301.12457)
- **TensorNEAT** (EMI-Group): 401 / pushed 2026-05-01 / no releases — [GitHub](https://github.com/EMI-Group/tensorneat)
- **EvoJAX** (Google): 951 / ARCHIVED / v0.2.17 on 2024-06-18 — [GitHub](https://github.com/google/evojax)
- **OpenELM** (CarperAI): 747 / pushed 2023-11-15 / v0.2.1 on 2023-03-08 (stale) — [GitHub](https://github.com/CarperAI/OpenELM)
- **Dominated Novelty Search** reference implementation: 7 / pushed 2025-02-01 — [GitHub](https://github.com/adaptive-intelligent-robotics/Dominated-Novelty-Search)

**ALife substrates**
- **CAX: Cellular Automata Accelerated in JAX** (Faldor & Cully): 271 / pushed 2026-09-24 / v0.4.4 on 2026-09-05. Paper: arXiv 2410.02651 (v2 2025-03-11) — [GitHub](https://github.com/maxencefaldor/cax); [arXiv](https://arxiv.org/abs/2410.02651)
- **ASAL**: 485 / pushed 2025-10-23 / no releases — [GitHub](https://github.com/SakanaAI/asal)
- **Petri-Dish NCA**: pushed 2025-11-06, 58 stars — [GitHub](https://github.com/SakanaAI/petri-dish-nca)
- **PBT-NCA**: pushed 2026-04-14, 18 stars — [GitHub](https://github.com/arberzela/pbt-nca)
- **cubff** (BFF/Forth/Z80 soups, Google PoI): 207 / pushed 2025-12-04 / no releases — [GitHub](https://github.com/paradigms-of-intelligence/cubff)
- **self-organising-systems** (Google Research; NCA, Biomaker CA): 442 / pushed 2026-01-09 / biomaker-v1.0.0 on 2024-02-07 — [GitHub](https://github.com/google-research/self-organising-systems)
- **Lenia** (Chakazul): 3,870 / pushed 2024-07-19 / v3.0 on 2020-10-14 (reference implementation, dormant) — [GitHub](https://github.com/Chakazul/Lenia)
- **Flow-Lenia**: 27 / pushed 2026-10-09 / no releases — [GitHub](https://github.com/erwanplantec/FlowLenia)
- **Leniabreeder**: pushed 2025-04-02 — [GitHub](https://github.com/maxencefaldor/Leniabreeder)
- **ALIEN** (CUDA artificial-life environment): 5,539 / pushed 2026-10-09 / v4.12.3 on 2024-12-29 — [GitHub](https://github.com/chrxh/alien)
- **Avida**: 669 / pushed 2025-01-27 / 2.14.0 on 2021-07-03 — [GitHub](https://github.com/devosoft/avida)

**Environment generation, UED and open-ended RL environments**
- **Craftax**: 460 / pushed 2026-06-20 / v1.6.1 on 2026-06-20. Paper: arXiv 2402.16801 — [GitHub](https://github.com/MichaelTMatthews/Craftax); [arXiv](https://arxiv.org/abs/2402.16801)
- **Kinetix**: 276 / pushed 2026-09-24 / v3.0.2 on 2026-09-24 — [GitHub](https://github.com/FLAIROx/Kinetix)
- **XLand-MiniGrid**: 344 / pushed 2025-12-16 / v0.9.2 on 2025-12-16. Paper: arXiv 2312.12044 (NeurIPS 2024 D&B) — [GitHub](https://github.com/dunnolab/xland-minigrid); [arXiv](https://arxiv.org/abs/2312.12044)
- **JaxUED**: 102 / pushed 2026-01-21 / no releases. Paper: arXiv 2403.13091 — [GitHub](https://github.com/DramaCow/jaxued); [arXiv](https://arxiv.org/abs/2403.13091)
- **minimax** (Meta/UCL): 216 / pushed 2024-08-24 / v0.1.0 on 2023-11-22 (stale) — [GitHub](https://github.com/facebookresearch/minimax)
- **dcd** (Meta, dual curriculum design): ARCHIVED, last push 2024-08-20 — [GitHub](https://github.com/facebookresearch/dcd)
- **JaxLife**: 61 / pushed 2024-08-11 (stale). Paper: arXiv 2409.00853 — [GitHub](https://github.com/luchris429/JaxLife); [arXiv](https://arxiv.org/abs/2409.00853)
- **EvoGym**: 263 / pushed 2025-06-08 / 2.0.0 on 2024-08-10 — [GitHub](https://github.com/EvolutionGym/evogym)
- **OMNI-EPIC**: 82 / pushed 2024-12-26 — [GitHub](https://github.com/maxencefaldor/omni-epic)
- **POET** (Uber): 268 / pushed 2022-03-23 (dormant) — [GitHub](https://github.com/uber-research/poet)

**Self-improving agents**
- **DGM**: 2,398 / pushed 2025-08-13 — [GitHub](https://github.com/jennyzzt/dgm)
- **HyperAgents**: 2,789 / pushed 2026-07-31 — [GitHub](https://github.com/facebookresearch/HyperAgents)
- **HGM**: 437 / pushed 2026-02-07 — [GitHub](https://github.com/metauto-ai/HGM)
- **Digital Red Queen**: 226 / pushed 2026-01-13 — [GitHub](https://github.com/SakanaAI/drq)

**Out of scope, listed for completeness**
- **ShinkaEvolve** (Sakana; LLM program evolution, covered by other researchers): 1,434 / pushed 2026-10-05 / v0.0.7 on 2026-06-02. Paper: arXiv 2509.19349 (2025-09-17) — [GitHub](https://github.com/SakanaAI/ShinkaEvolve); [arXiv](https://arxiv.org/abs/2509.19349)

### Inferences
- **Release-polling recipe.** Use GitHub `releases.atom` per repo for those that tag releases (QDax, pyribs, evosax, EvoTorch, EvoX, CAX, Craftax, Kinetix, XLand-MiniGrid, ALIEN). For research repos that never tag (DGM, HyperAgents, HGM, ASAL, cubff, jaxued, TensorNEAT, PD-NCA), poll `pushed_at`.
- **Candidate base stack for Prometheus.** CAX (CA/NCA substrates) plus evosax or EvoX (ES/GA at scale) plus QDax or pyribs (archives; DNS for unbounded descriptors) plus Kinetix or Craftax (open-ended task distributions) is a coherent, actively maintained JAX stack. QDax's last release was May 2025, so pyribs (July 2026) is the more recently maintained QD library.

### Gaps
- MABE2 (Hintze lab), Empirical (devosoft), Symbulation and Microcosmos (ALIFE 2026) were not checked on GitHub because of the API rate limit.
- The existence of a public Microcosmos repo is UNVERIFIED.
- No Hugging Face model or dataset hubs exist for most of these frameworks; only Sakana's HF org was confirmed.

---

## Q5. Benchmarks and datasets for measuring open-endedness or ALife emergence

### Takeaway
There is still no standard, widely adopted benchmark for open-ended evolution or ALife emergence. What exists falls into three groups:
1. Open-ended RL task distributions: Craftax, Kinetix, XLand-MiniGrid and OMNI-EPIC.
2. Competing metrics: Bedau-style evolutionary activity, VLM/CLIP novelty, MSPD, compression and direct replicator detection, information-theoretic definitions, and functional-information estimators.
3. One new "Open-Endedness Bench" (Oct 2026), aimed at research-agent epistemics rather than ALife.

### Cited Findings
- **Craftax** (Matthews, Beukman, Ellis, Samvelyan, Jackson, Coward et al.): "A Lightning-Fast Benchmark for Open-Ended RL"; arXiv 2402.16801 (BACKGROUND, 2024); repo actively released (v1.6.1, 2026-06-20) [V-arXiv, V-GH] — [arXiv](https://arxiv.org/abs/2402.16801)
- **Kinetix**: an open-ended, procedurally generated 2D physics-control task space, used to train general agents; ICLR 2025 Oral; v3.0.2 released 2026-09-24 [V-arXiv, V-GH] — [arXiv](https://arxiv.org/abs/2410.23208); [project](https://kinetix-env.github.io/)
- **XLand-MiniGrid**: "Scalable Meta-Reinforcement Learning Environments in JAX"; NeurIPS 2024 Datasets & Benchmarks track [V-arXiv] — [arXiv](https://arxiv.org/abs/2312.12044)
- **OMNI-EPIC**: an environment generator programmed in code, filtered by an interestingness model (ICLR 2025) — [arXiv](https://arxiv.org/abs/2405.15568)
- **JaxLife**: an open-ended agentic simulator (BACKGROUND, 2024; repo stale) — [arXiv](https://arxiv.org/abs/2409.00853)
- **Open-Endedness Bench** (Shi, Ji, Huang, Wang, He, Liu), "Measuring Epistemic Process from Agent Records"; arXiv 2610.02588; v1 2026-10-01 [V-arXiv].
  - Code: github.com/ARA-Labs/oeb (created 2026-09-29) [V-GH]
  - Data: HF dataset AgentNativeResearchLab/oeb-scored-runs. The HF org exists per the API.
  - A search summary reports that only 16–29% of the improvements research agents claim hold up against logged results [snippet].
  - [ADJACENT: measures AI research agents, not ALife]
  — [arXiv](https://arxiv.org/abs/2610.02588)
- **Metric: Bedau evolutionary activity statistics** (total, normalized, new activity), applied as an OEE test to ToLSim (2026). The result was a partial pass: unbounded total activity, but bounded normalized activity and null new activity [snippet] — [arXiv 2603.01701](https://arxiv.org/abs/2603.01701)
- **Metric: VLM/CLIP novelty.**
  - ASAL's open-endedness mode (2024) — [arXiv 2412.17799](https://arxiv.org/abs/2412.17799)
  - The ALIFE 2025 paper's OE score (1 minus the maximum CLIP similarity to any earlier frame) — [arXiv 2509.22447](https://arxiv.org/abs/2509.22447)
- **Metric: Multi-Scale Path Divergence (MSPD)**, an interpretable, renormalization-group-inspired measure. It gives near-zero scores to static particles, Brownian motion and a single moving blob, used as negative controls [snippet] — [arXiv 2606.17091](https://arxiv.org/abs/2606.17091)
- **Metric: replicator detection.**
  - The original BFF work inferred takeover from a shrinking compressed size of the soup (BACKGROUND).
  - The 2026 re-analysis adds "(reasonably) reliable direct self-replicator detectors" [snippet] — [arXiv 2607.01483](https://arxiv.org/abs/2607.01483); [arXiv 2406.19108](https://arxiv.org/abs/2406.19108)
- **Metric: information-theoretic definition of open-ended learning** (Xu, Zhu, Van Roy, 2026) — [arXiv 2606.08369](https://arxiv.org/abs/2606.08369)
- **ALIFE 2026 measurement items** [V-prog] — [program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf):
  - Bartko, Song, Myers, "Prediction and Entropy of Evolving Sequences: A Transformer-Based Estimator of Functional Information"
  - Egri-Nagy & Nehaniv, "Measuring the Computational Power of Finite Patches of Cellular Automata"
  - Ferguson & Escondo, "Summarizing Populations…" (sampling effects in evolutionary replay experiments)
  - Virtual Creature Competition, a competitive benchmark format
  - Gupta & Adami, "Can AI Detect Life?"
- **QD benchmarks.**
  - QDax ships standard QD tasks — [QDax arXiv](https://arxiv.org/abs/2308.03665)
  - A GECCO 2026 Companion QD benchmark with variable constraints, "QDA-VC" (Shyne & Cooper) [snippet; UNVERIFIED title] — [dblp](https://dblp.org/db/conf/gecco/gecco2026c.html)
  - The BENCH@GECCO26 workshop on benchmarking practice — [GECCO workshops](https://gecco-2026.sigevo.org/Workshops)
- **Older OEE measurement literature** (BACKGROUND):
  - Stepney, "Modelling and measuring open-endedness" (OEE4 workshop) — [PDF](http://workshops.alife.org/oee4/papers/stepney-oee4-camera-ready.pdf)
  - A review noting persistence filtering and evolutionary activity as the main proposals, with "a significant degree of disagreement" — [arXiv 2105.03216](https://arxiv.org/pdf/2105.03216)

### Inferences
- For Prometheus as a falsification instrument, the most reusable 2025–26 measurement ideas are:
  - ToLSim's multi-statistic OEE test. Total activity alone gives false positives; normalized and new activity are the discriminating statistics.
  - MSPD's explicit negative controls: static, Brownian and coherent-blob systems must score near zero.
  - Direct replicator detectors plus a mutation-only twin, from the BFF re-analysis.
  - HGM's clade-level metric, to tell lineage productivity apart from the current score.
  - Open-Endedness Bench's finding that most claimed improvements fail against logs. This mirrors the "measurement carries its answer" problem.
- VLM/CLIP-based novelty is the most-used OE metric of 2025–26, but it is an oracle with a visual prior. It is unsuitable for non-visual substrates such as program soups or reasoning mechanisms without a re-embedding step.

### Gaps
- No dataset of long-running ALife or OEE runs (logged lineages or activity statistics) was found as a public, versioned benchmark. Open-Endedness Bench's HF dataset is the only "runs" dataset found, and it concerns research agents.
- No consensus open-endedness benchmark suite comparable to the QDax task suite was found for ALife substrates.
- The "QDA-VC" GECCO 2026 benchmark title and contents were not verified from a primary source.
