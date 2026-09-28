# Literature map: Forgetting, Regime Change, and Abstraction

Scope: when discarding or discounting old information helps, and how systems
handle history that has become obsolete. Covers 2015-2026 work plus classics.
Compiled 2026-09-28.

## Verification legend

- [V] = the bibliographic details and the headline claim were checked against
  the abstract, the publisher page, or a search-result summary of the source
  during this session. This is ABSTRACT-LEVEL verification. It does not mean
  the full text was read.
- [R] = recalled from memory and not re-checked this session. Treat the
  specific numbers as unverified. Treat the direction of the claim as likely
  but not certain.
- Parts marked "(interpretation)" are my own reading for this project. They
  are not claims made by the source.

## The eight questions asked of each source

- Q1: What is stored?
- Q2: What is compressed?
- Q3: Where does the compression happen: at storage, at retrieval, or at
  prediction?
- Q4: Is the forgetting causal (it is the thing that helps) or incidental (a
  side effect)?
- Q5: What is the generalization target?
- Q6: What is the capacity constraint?
- Q7: What changes when nuisance information is kept?
- Q8: Is there a theoretical limit that links retained information to
  prediction quality?

Answers are kept short. "n/a" means the source does not address the question.

---------------------------------------------------------------------------

## PART 1. Source cards

### 1A. Theoretical anchors: how retained information relates to prediction

**Bialek, Nemenman & Tishby (2001). "Predictability, complexity, and learning."**
Neural Computation 13(11):2409-2463.
https://doi.org/10.1162/089976601753195969 [V]
- Q1: In the ideal case, only the predictive information I_pred(T), which is
  the mutual information between the past and the future.
- Q2: Everything in the past beyond I_pred. The total entropy of the past
  grows linearly with T, while I_pred grows sublinearly (it stays finite, grows
  as log T, or grows as a power law). [V]
- Q3: At storage, in the ideal case.
- Q4: Causal in principle: the non-predictive part of the past has no value.
- Q5: The future of the same process.
- Q6: None imposed. The result is a statement about the process itself.
- Q7: Keeping extensive (non-predictive) memory adds cost and adds no
  predictive value.
- Q8: YES. For a model with K parameters, I_pred ~ (K/2) log T. The amount
  of the past worth keeping is set by the complexity of the model class, not
  by the length of the history. [V]

**Still, Sivak, Bell & Crooks (2012). "Thermodynamics of prediction."**
Physical Review Letters 109:120604.
https://link.aps.org/accepted/10.1103/PhysRevLett.109.120604 [V]
- Q1: The system state, which holds memory of past inputs.
- Q2: The non-predictive part of that memory, meaning information about the
  past that does not help predict the future.
- Q3: At storage.
- Q4: Causal: keeping non-predictive memory is wasteful.
- Q5: Future environmental fluctuations.
- Q6: Energy. Non-predictive information corresponds to dissipation. [V]
- Q7: Kept nuisance shows up as measurable inefficiency.
- Q8: YES. Model inefficiency, defined as I(state; past) - I(state; future),
  equals a thermodynamic dissipation bound. [V]
- (interpretation) This gives a formal definition of "obsolete history": it
  is the memory - predictive gap.

**Shalizi & Crutchfield (2001). "Computational mechanics: pattern and prediction, structure and simplicity."**
Journal of Statistical Physics 104:817-879. https://arxiv.org/abs/cond-mat/9907176 [R]
- Q1: Causal states. These are equivalence classes of pasts that have the
  same conditional future distribution.
- Q2: All distinctions between pasts that do not change the forecast.
- Q3: At storage (the state is the compression).
- Q4: Causal. The causal-state partition is the minimal sufficient statistic.
- Q5: The conditional distribution of the future.
- Q6: Statistical complexity C_mu, the entropy of the causal states.
- Q7: A finer partition is still sufficient but no longer minimal. It adds
  no predictive power and costs sample efficiency when the partition has to
  be learned.
- Q8: YES. The causal states are the unique minimal sufficient predictive
  statistic. This is the time-series analogue of bisimulation (see 1E).

**Tishby, Pereira & Bialek (1999). "The information bottleneck method."**
Allerton / arXiv:physics/0004057 [R]
**Achille & Soatto (2018). "Emergence of invariance and disentanglement in deep representations."**
JMLR 19(50):1-34. https://jmlr.org/papers/v19/17-646.html [R]
- Q1: A representation z of x.
- Q2: I(z; x) is minimized subject to I(z; y) being preserved.
- Q3: At storage, in the representation.
- Q4: Causal in the theory. Achille and Soatto argue that a minimal
  sufficient representation is maximally invariant to nuisances, and that
  limiting the information held in the weights limits overfitting. [R]
- Q5: y on the same distribution.
- Q6: Information in the representation or in the weights.
- Q7: Nuisance information kept in z reduces invariance.
- Q8: YES, conditionally. The link is "minimal sufficient implies invariant".
  It assumes the nuisance is independent of y. It says nothing about
  nuisances that are correlated with y in training (spurious correlation).
- CRITIQUE: Saxe et al. (2018), "On the information bottleneck theory of deep
  learning," ICLR, https://openreview.net/forum?id=ry_WPG-A- [R]. The
  "compression phase" depends on the activation function (it appears with
  tanh but not with ReLU), and generalization does not track compression.
  Conclusion: a compression story in the representation is not a
  demonstrated cause of generalization.

**Xu & Raginsky (2017). "Information-theoretic analysis of generalization capability of learning algorithms."**
NeurIPS. https://arxiv.org/abs/1705.07809 [R]
- Q8: The generalization gap is at most sqrt(2 sigma^2 I(S; W) / n). Less
  information about the training sample S kept in the weights W means a
  smaller possible gap. This is an i.i.d. result. It says nothing about the
  test distribution shifting.

**Feldman (2020). "Does learning require memorization? A short tale about a long tail."**
STOC. https://arxiv.org/abs/1906.05271 [R]
**Brown, Bun, Feldman, Smith & Talwar (2021). "When is memorization of irrelevant training data necessary for high-accuracy learning?"**
STOC, pp. 123-132. https://arxiv.org/abs/2012.06421 [V]
- Q1: Much of the training examples, including parts irrelevant to the label.
- Q2: Nothing, and that is the point of the result.
- Q3: n/a.
- Q4: Here forgetting HURTS. Brown et al. construct natural tasks in which
  every sufficiently accurate learner must encode essentially all the
  information about a large subset of its training examples, even
  high-entropy irrelevant information. [V]
- Q5: Long-tailed subpopulations, where test examples resemble singleton
  training examples.
- Q6: The number of samples relative to the number of subpopulations.
- Q7: Keeping "exact episodic identity" is REQUIRED for accuracy on rare
  subpopulations.
- Q8: YES, as a lower bound on memorization. This is the counterweight to
  the information bottleneck: when the distribution is long-tailed, near
  optimal accuracy requires retaining information that looks irrelevant.

**Sutton, Koop & Silver (2007). "On the role of tracking in stationary environments."**
ICML, pp. 871-878. http://www.incompleteideas.net/papers/SKS-07.pdf [V]
- Q1: The current weights, updated with a constant step size (tracking).
- Q2: Old data is discounted exponentially.
- Q3: At storage.
- Q4: CAUSAL. Tracking beats every converging algorithm on a STATIONARY
  problem (the "Black and White" example, and computer Go). [V] Recalled
  mechanism [R]: when the function approximator has limited capacity, the
  environment looks non-stationary from the agent's point of view, so
  following the local region of state space is better than averaging over
  all of it.
- Q5: Near-term prediction and value.
- Q6: The capacity of the function approximator.
- Q7: Keeping old data (converging) forces one global compromise.
- Q8: No bound. The result is a demonstration.
- (interpretation) This is the key point: forgetting can help WITHOUT any
  regime change, when capacity is limited and the input distribution is
  locally structured.

**Anderson & Schooler (1991). "Reflections of the environment in memory."**
Psychological Science 2:396-408.
https://journals.sagepub.com/doi/10.1111/j.1467-9280.1991.tb00174.x [V]
- Q1: Item traces with histories of how often and how recently they were
  used.
- Q2: Items become less available as a power function of time since use.
- Q3: At retrieval. Availability is a prior on how likely an item is to be
  needed.
- Q4: Causal, in the rational-analysis sense. The probability that an item
  will be needed follows power laws of frequency, recency and spacing in the
  environment (newspaper headlines, speech to children, email), and memory
  matches those laws. [V]
- Q5: Predicting what will be needed next.
- Q6: The cost of retrieval and search.
- Q7: Items that are never forgotten slow retrieval and reduce its precision.
- Q8: No formal bound. The claim is optimality relative to the statistics of
  the environment.

### 1B. Forgetting as a feature in neuroscience

**Richards & Frankland (2017). "The persistence and transience of memory."**
Neuron 94(6):1071-1084. https://doi.org/10.1016/j.neuron.2017.04.037 [V]
- Q1: Engram-level episodic and semantic traces.
- Q2: Details that are outdated or noisy.
- Q3: At storage. Traces are actively weakened or overwritten, for example
  through neurogenesis-driven remapping and synaptic decay.
- Q4: Claimed to be CAUSAL. Transience improves decisions in environments
  that change and are noisy. [V] It works in two ways: (i) it removes
  outdated information, and (ii) it acts as a regularizer against
  overfitting to particular episodes, which helps generalization. [V]/[R]
- Q5: New experiences that are similar but not identical, and a world that
  has changed.
- Q6: Implicit. The argument is framed as regularization, not storage limits.
- Q7: Perfect retention leads to overfitting to specific episodes, and to
  conflict when the world changes.
- Q8: No bound. This is a normative argument that borrows ML analogies.
- CAVEAT: This is a Perspective. The causal evidence it relies on comes from
  rodent manipulations such as Akers 2014.

**Akers et al. (2014). "Hippocampal neurogenesis regulates forgetting during adulthood and infancy."**
Science 344(6184):598-602. https://doi.org/10.1126/science.1248903 [V]
- Q1: Hippocampal contextual fear memories.
- Q2: Established memories are degraded by the integration of new neurons.
- Q3: At storage (circuit remodeling).
- Q4: CAUSAL manipulation in both directions. Increasing neurogenesis AFTER
  learning induced forgetting in adults. Decreasing it in infants reduced
  infantile amnesia. [V]
- Q5: n/a. This paper measures forgetting and does not test whether
  forgetting improves anything.
- Q6: The capacity of the dentate gyrus to encode new memories.
- Q7: Not tested directly. A follow-up (Epp et al. 2016, Nat Commun) [R]
  reported that neurogenesis-mediated forgetting helped later
  reversal/interference learning in a water maze.
- Q8: n/a.
- (interpretation) This is the cleanest example of an "ablate the forgetting
  mechanism" design, but the outcome it measures is retention, not
  generalization.

**Shuai et al. (2010). "Forgetting is regulated through Rac activity in Drosophila."**
Cell 140:579-589 [R]
**Davis & Zhong (2017). "The biology of forgetting -- a perspective."**
Neuron 95:490-503 [R]
**Ryan & Frankland (2022). "Forgetting as a form of adaptive engram cell plasticity."**
Nature Reviews Neuroscience 23:173-186 [R]
- Q1: Molecular and engram traces.
- Q3: At storage (Rac1 and dopamine-driven "intrinsic forgetting") OR at
  retrieval (Ryan & Frankland argue that many forgotten engrams are still
  present but cannot be accessed, and can be reactivated optogenetically).
- Q4: CAUSAL in flies. Blocking Rac1 slows forgetting and activating it
  speeds forgetting. [R]
- (interpretation) The distinction between forgetting at storage and
  forgetting at retrieval is central to this project. Ryan & Frankland's
  "forgetting is retrieval failure, and the trace can be restored" is the
  biological version of a restore-the-discarded-information test.

**Hardt, Nader & Nadel (2013). "Decay happens: the role of active forgetting in memory."**
Trends in Cognitive Sciences 17(3):111-120 [R]
- Q3: At storage. Active decay happens during quiet waking and sleep.
- Q4: Proposed to be causal, clearing out memories not worth keeping.

**Tononi & Cirelli (2014). "Sleep and the price of plasticity" (the synaptic homeostasis hypothesis, SHY).**
Neuron 81(1):12-34. https://doi.org/10.1016/j.neuron.2013.12.025 [V]
- Q1: Synaptic weights.
- Q2: Synapses are scaled down across the board during sleep, with
  "down-selection" that spares the connections that are strongly or
  consistently activated.
- Q3: At storage, offline.
- Q4: Claimed causal. Learning while awake saturates plasticity and lowers
  the signal-to-noise ratio. Downscaling restores both and favors the gist
  (the consistently co-activated traces) over the idiosyncratic ones. [V]/[R]
- Q5: Future learning capacity, and integrating memories into gist.
- Q6: Energy, space, and the saturation of synapses.
- Q7: Without downscaling: saturation (lost plasticity) and noise.
- Q8: No bound.
- (interpretation) This is the biological counterpart of shrink-and-perturb,
  L2 regularization, and continual backpropagation (Part 1D), which all fix
  plasticity loss in networks.

### 1C. Complementary learning systems (CLS) and consolidation

**McClelland, McNaughton & O'Reilly (1995). "Why there are complementary learning systems in the hippocampus and neocortex."**
Psychological Review 102(3):419-457 [R]
**Kumaran, Hassabis & McClelland (2016). "What learning systems do intelligent agents need? CLS theory updated."**
Trends in Cognitive Sciences 20(7):512-534.
https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30043-2 [V]
- Q1: TWO stores. The hippocampus holds sparse, pattern-separated episodes
  (exact identity). The neocortex holds distributed, slowly learned
  structure.
- Q2: Neocortex compresses across episodes, and interleaved replay trains it.
- Q3: At storage, in the cortex. The hippocampus keeps detail, which is then
  available at retrieval.
- Q4: Forgetting in the hippocampus is incidental and gradual, while the
  cortex slowly absorbs the content. The central claim is that fast learning
  of new material into a single shared structured network causes
  CATASTROPHIC INTERFERENCE, and that interleaving solves it. [V]
- Q5: Structured generalization (cortex) together with one-shot recall
  (hippocampus).
- Q6: Shared weights in the cortex, which make interference the problem.
- Q7: Episodic detail is KEPT in a separate store and so does not corrupt the
  structured store. The 2016 update adds that new information CONSISTENT
  with an existing schema can be absorbed into cortex quickly (citing Tse et
  al. 2007). [V]/[R]
- Q8: No bound.
- DESIGN LESSON: CLS does not choose between keeping and forgetting. It
  handles nuisance by SPLITTING the representation: detail goes to one store
  and structure to another.

### 1D. Continual learning in machine learning: interference, plasticity, resets

**Kirkpatrick et al. (2017). "Overcoming catastrophic forgetting in neural networks" (EWC).**
PNAS 114(13):3521-3526. https://doi.org/10.1073/pnas.1611835114 [R]
**Zenke, Poole & Ganguli (2017). "Continual learning through synaptic intelligence."**
ICML [R]
- Q1: The weights, plus a per-weight importance estimate (the Fisher
  information in EWC, the path integral in SI).
- Q2: Nothing is forgotten on purpose. Important weights are anchored.
- Q3: At storage (a penalty during learning).
- Q4: This line of work treats forgetting as the ENEMY.
- Q5: All previous tasks, weighted equally.
- Q6: A fixed set of parameters.
- Q7: n/a. The approach assumes old tasks remain valid. If a task has
  become obsolete, EWC's anchoring keeps it anyway (interpretation).

**Parameter isolation. Rusu et al. (2016), "Progressive neural networks," arXiv:1606.04671; Mallya & Lazebnik (2018), "PackNet," CVPR. [R]**
- Q1: One separate column or subnetwork per task.
- Q4: No forgetting.
- Q6: Capacity grows with the number of tasks.
- Q7: Old structure never interferes. The price is that every task needs a
  task ID at test time, which means the regime has to be known or inferred.

**Replay. Rolnick et al. (2019), "Experience replay for continual learning," NeurIPS; Shin et al. (2017), "Continual learning with deep generative replay," NeurIPS; van de Ven, Siegelmann & Tolias (2020), "Brain-inspired replay," Nature Communications 11:4069. [R]**
- Q1: A buffer of raw episodes, or a generative model of past data.
- Q3: At storage (the data are replayed into training).
- Q4: Replay prevents forgetting. The buffer policy (reservoir, FIFO, and so
  on) decides WHICH history is forgotten.
- Q7: A generative replay model regenerates what it has abstracted, not the
  exact episodes, so exact identity is lost.

**Prabhu, Torr & Dokania (2020). "GDumb: A simple approach that questions our progress in continual learning."**
ECCV. https://doi.org/10.1007/978-3-030-58536-5_31 [V]
- Q1: A greedy class-balanced buffer.
- Q3: At prediction time. The model is retrained FROM SCRATCH on the buffer
  whenever a prediction is needed. [V]
- Q4: No sequential learning happens at all. The weights are thrown away
  every time.
- Result [V]/[R]: this "dumb" baseline was competitive with or better than
  many published continual-learning methods. That suggests the benchmarks
  measured buffer policy and task assumptions more than sequential learning.
- (interpretation) This is the cheapest control for any study of forgetting:
  "keep a bounded sample of history and refit from scratch" versus "learn
  online".

**Ramasesh, Dyer & Raghu (2021). "Anatomy of catastrophic forgetting: hidden representations and task semantics."**
ICLR [R]
- Finding [R]: Forgetting is concentrated in the DEEPER (later) layers.
  Interference is worst for tasks of INTERMEDIATE similarity: tasks that are
  very similar or very different interfere less.
- (interpretation) Measure forgetting per layer and by task similarity, not
  as one number.

**Nikishin, Schwarzer, D'Oro, Bacon & Courville (2022). "The primacy bias in deep reinforcement learning."**
ICML (PMLR 162). https://proceedings.mlr.press/v162/nikishin22a/nikishin22a.pdf [V]
- Q1: The replay buffer (kept in full) and the network weights.
- Q2: The weights are periodically reset, completely or partly (often the
  last layers), while the buffer is KEPT. [V]
- Q3: At storage. The parameterized summary is discarded, and the raw
  history remains.
- Q4: CAUSAL. The resets are the intervention, and they consistently improve
  Atari-100k and DeepMind Control results. [V]
- Q5: The return of the same task. The problem being fixed is overfitting to
  EARLY data (primacy), not a regime change.
- Q6: The capacity of the network plus how well it can still be optimized.
- Q7: Keeping the early-fit weights locks in bad early features.
- Q8: No bound.
- DESIGN LESSON: "Forget the compression, keep the data" is a distinct
  mechanism from "forget the data". It points to the fitted summary being
  where history does harm, not the history itself.

**Ash & Adams (2020). "On warm-starting neural network training."**
NeurIPS. https://arxiv.org/abs/1910.08475 [V]
- Q4: CAUSAL. A model warm-started on part of the data and then trained on
  all of it generalizes WORSE than one trained from scratch, even when the
  training loss ends up similar. The fix is "shrink and perturb": scale the
  weights down and add noise. [V]
- Q5: The same i.i.d. distribution. No regime shift is involved.
- (interpretation) Old history held in the weights harms generalization even
  when the old data remain valid. So the damage passes through the
  optimization state, not through stale content.

**Dohare et al. (2024). "Loss of plasticity in deep continual learning."**
Nature 632:768-774. https://doi.org/10.1038/s41586-024-07711-7 [V]
- Q1: Weights. "Continual backpropagation" also tracks how useful each unit
  is.
- Q2: Units with low utility are re-initialized, a little at a time.
- Q3: At storage.
- Q4: CAUSAL. Without the re-initialization, networks lose plasticity until
  they learn no better than a shallow or linear network. One example: on a
  continual ImageNet binary task, accuracy fell from 89% on early tasks to
  77% by the 2000th task. [V] L2 plus weight perturbation also helps. [V]
- Q5: Learning future tasks, which is plasticity rather than retention.
- Q6: A fixed network size.
- Q7: Keeping every unit's history leads to dead units, growing weight
  magnitudes, and falling effective rank. [R]
- Q8: No bound.

**Lyle et al. (2023). "Understanding plasticity in neural networks."**
ICML [R]
- Plasticity loss is tied to the curvature and conditioning of the loss
  landscape, and no single metric such as dead units or weight norm predicts
  it on its own. [R]

**Zhou, Vani, Larochelle & Courville (2022). "Fortuitous forgetting in connectionist networks."**
ICLR. https://arxiv.org/abs/2202.00155 [V]
- Q1: Weights.
- Q2: A "forget" step removes information selectively: reset the later
  layers, or perturb or prune weights. A "relearn" step follows.
- Q3: At storage.
- Q4: CAUSAL, and argued to be SELECTIVE. Forgetting removes
  "undesirable" information (for example memorized examples or
  idiosyncratic features) more than information that is "consistently useful
  under different conditions", and relearning reinforces the latter. [V]
  This framework unifies iterative magnitude pruning, later-layer
  resetting, and iterated learning in emergent language. [V]
- Q5: Held-out generalization, and compositional structure in emergent
  languages.
- Q6: n/a.
- Q7: Kept undesirable information delays or prevents generalization.
- Q8: No bound.
- DESIGN LESSON: The mechanism works because the forgetting is
  DISPROPORTIONATE: easy-to-relearn, consistently useful features come back
  after a reset, and idiosyncratic ones do not. A test for this is to measure
  what returns after the forget step.

**Chen et al. (2023). "Improving language plasticity via pretraining with active forgetting."**
NeurIPS. https://arxiv.org/abs/2307.01163 [V]
- Q2: The token embedding layer is reset every K updates during
  pretraining. [V]
- Q4: CAUSAL. The resulting model adapts faster to new languages and does
  better in low-data settings, especially for languages far from English.
  [V] It works as meta-learning: the body is forced not to depend on any one
  particular set of embeddings.
- (interpretation) Periodically forgetting the INTERFACE (the lexical lookup)
  pushes the body toward abstraction that does not depend on the interface.
  This is a direct handle on the "syntactic-router" type of problem.

**Nanda, Chan, Lieberum, Smith & Steinhardt (2023). "Progress measures for grokking via mechanistic interpretability."**
ICLR. https://arxiv.org/abs/2301.05217 [V for venue and the Fourier algorithm; R for the phases]
- Q4: [R] The paper describes three phases: memorization, formation of a
  generalizing circuit, and CLEANUP, in which weight decay removes the
  memorization components. The drop in test loss happens at cleanup. So here
  forgetting the memorized solution is causally tied to the moment
  generalization appears, but weight decay also drives the circuit to form
  in the first place.
- (interpretation) This case shows why "causal versus incidental" is hard to
  separate. The same regularizer both builds the abstraction and removes the
  memorized solution.

**In-context vs in-weights learning. Chan et al. (2022), "Data distributional properties drive emergent in-context learning in transformers," NeurIPS; Singh et al. (2023), "The transient nature of emergent in-context learning in transformers," NeurIPS; Anand et al. (2024), arXiv:2406.00053, "Dual process learning ... with weight forgetting." [R; the arXiv ID was seen in a search result]**
- [R] Bursty, long-tailed data favors in-context learning (ICL), and ICL can
  fade with longer training as in-weights memorization takes over. Weight
  forgetting can keep structural ICL alive.
- (interpretation) Here exact-identity memorization in the weights CROWDS OUT
  a general in-context mechanism. This is a nuisance that hurts by competing
  with the mechanism, not by adding noise.

### 1E. Regime and latent-cause inference: split or update?

**Gershman, Blei & Niv (2010). "Context, learning, and extinction."**
Psychological Review 117(1):197-209 [R]
**Gershman, Monfils, Norman & Niv (2017). "The computational nature of memory modification."**
eLife 6:e23763. https://elifesciences.org/articles/23763 [V]
- Q1: A set of latent causes. Each has its own associative weights.
  Observations are assigned to causes by posterior inference with a
  Chinese-restaurant-process prior.
- Q2: Many trials are compressed into a few causes. Within a cause, the
  weights are a running summary.
- Q3: At storage (whether a new cause is created) AND at retrieval (the
  cause posterior controls which memory is expressed).
- Q4: Old memory is NOT forgotten when a new cause is inferred. It is SPLIT
  off. An old memory is MODIFIED only when new data are attributed to the
  same cause. [V]
- Q5: Predicting the US (unconditioned stimulus) in new contexts, and
  explaining relapse phenomena: spontaneous recovery, renewal, and
  reinstatement.
- Q6: The CRP concentration alpha, which sets the prior on how many causes
  there are.
- Q7: Kept old causes produce "return of fear": the old regime's prediction
  comes back when context cues shift the cause posterior.
- Q8: No bound. The model is Bayes-optimal given its generative model.
- KEY CAUSAL TEST: **Gershman, Jones, Norman, Monfils & Niv (2013), "Gradual
  extinction prevents the return of fear: implications for the discovery of
  state," Frontiers in Behavioral Neuroscience 7:164,
  https://doi.org/10.3389/fnbeh.2013.00164 [V]** (a 2021 corrigendum removed
  one animal from the analysis [V]). If the change is made gradually, the
  prediction error stays small, no new cause is inferred, and the OLD memory
  is overwritten, so fear returns less. An abrupt change creates a new cause
  and preserves the old memory, so fear returns more. [V for the claim of
  less return; R for the exact details of the schedule]
- DESIGN LESSON: The same total evidence produces OVERWRITE or SPLIT
  depending on HOW FAST the regime changes. This is a cheap, sharp
  discriminator (see Part 2d).

**Lu, Nguyen, Zhang, Hasson, Griffiths, Zacks, Gershman & Norman (2024). "Reconciling shared versus context-specific information in a neural network model of latent causes" (LCNet).**
Scientific Reports 14:16782. https://arxiv.org/abs/2312.08519 [V]
- Q1: Structure SHARED across contexts is held in the network weights.
  Structure SPECIFIC to a context is held in a context module, and a
  Bayesian nonparametric latent-cause algorithm chooses which context is
  active. [V]
- Q3: At retrieval (choosing the context).
- Q4: Interference is avoided by gating, not by forgetting.
- Q7: [R] The paper reports blocked-versus-interleaved curriculum effects and
  effects of how "sticky" contexts are.
- (interpretation) This is the clearest current neural-network design for
  "keep shared structure, gate regime-specific structure".

**Heald, Lengyel & Wolpert (2021). "Contextual inference underlies the learning of sensorimotor repertoires" (the COIN model).**
Nature 600:489-493. https://doi.org/10.1038/s41586-021-04129-3 [V]
- Q1: A repertoire of context-specific motor memories plus a probabilistic
  belief about which context is active.
- Q3: At retrieval, and in how strongly each memory is EXPRESSED.
- Q4: Much of what looks like forgetting is really a change in which memory
  is expressed ("apparent learning"), not a change in what is stored
  ("proper learning"). [V]
- Q5: Motor adaptation under contexts that switch.
- Q7: Kept old memories show up as spontaneous recovery and EVOKED recovery.
  Evoked recovery is a NEW prediction that was confirmed: a few trials of the
  old context's cue bring the old memory back. [V]
- Q8: No bound.
- DESIGN LESSON: Evoked recovery is a RESTORE TEST. If a brief cue restores
  performance on the old regime, the memory was gated rather than erased.

**Adams & MacKay (2007). "Bayesian online changepoint detection" (BOCPD).**
arXiv:0710.3742. https://arxiv.org/abs/0710.3742 [V]
- Q1: A posterior over the RUN LENGTH (time since the last change), and a
  sufficient statistic for each possible run length.
- Q2: Data from before the inferred changepoint receive weight in proportion
  to the posterior probability that no change happened since.
- Q3: At prediction. The predictive distribution averages over run lengths.
- Q4: CAUSAL, and ADAPTIVE. The effective memory length is inferred, not
  fixed.
- Q5: The next observation.
- Q6: Pruning of the run-length posterior.
- Q7: Assumes the regimes are INDEPENDENT (parameters before and after a
  change are unrelated), so old regimes are never reused. That is the
  opposite of latent-cause models, which can return to an old cause.
- Q8: Exact Bayesian inference under the assumed hazard rate.

**Nassar, Wilson, Heasly & Gold (2010). J Neurosci 30:12366; Wilson, Nassar & Gold (2013), "A mixture of delta-rules approximation to Bayesian inference in change-point problems," PLoS Computational Biology 9:e1003150 [R]**
**Behrens, Woolrich, Walton & Rushworth (2007). "Learning the value of information in an uncertain world." Nature Neuroscience 10:1214 [R]**
- Q2: Humans adjust their learning rate. It rises after surprising outcomes
  that suggest a changepoint and when the environment is volatile.
- Q3: At storage (the learning rate).
- Q4: Causal and adaptive.
- (interpretation) The behavioral signature is a learning rate that depends
  on surprise, and it can be measured cheaply.

**Non-stationary bandits. Garivier & Moulines (2011), "On upper-confidence bound policies for switching bandit problems," ALT; Besbes, Gur & Zeevi (2014), "Stochastic multi-armed-bandit problem with non-stationary rewards," NeurIPS [R]**
- Q2: Discounting or a sliding window over past rewards.
- Q8: YES. Regret bounds link the window or discount size to how many
  switches occur, or to a variation budget V_T. Regret is on the order of
  T^{2/3} V_T^{1/3} in Besbes et al. [R] There is an optimal forgetting rate
  that depends on how fast the world changes. Forgetting too little or too
  much both cost regret.

**Mixtures of experts and multiple models. Jacobs, Jordan, Nowlan & Hinton (1991), "Adaptive mixtures of local experts," Neural Computation 3:79-87; Wolpert & Kawato (1998), "Multiple paired forward and inverse models for motor control," Neural Networks 11:1317 (MOSAIC); Collins & Koechlin (2012), "Reasoning, learning, and creativity: frontal lobe function and human decision-making," PLoS Biology 10:e1001293; Collins & Frank (2013), "Cognitive control over learning: creating, clustering, and generalizing task-set structure," Psychological Review 120:190 [R]**
- Q1: Several models kept at the same time, plus a responsibility or
  reliability signal for each.
- Q3: At retrieval (gating).
- Q4: Old models are kept and switched back in when they become reliable
  again. Collins & Koechlin's PROBE model keeps a small number of
  strategies, around 3, and creates a new one when none of them is reliable.
  [R]
- Q6: The number of experts or task sets held in memory.
- Q7: Collins & Frank (2013) show that people build and REUSE task-set
  clusters even when doing so has no immediate benefit. That is a bias
  toward structure that pays off when regimes come back.

**Continual model-based RL with regime inference. Nagabandi, Finn & Levine (2019), "Deep online learning via meta-learning: continual adaptation for model-based RL," ICLR (MOLe, a CRP mixture of models); Xie, Harrison & Finn (2021), "Deep RL amidst continual structured non-stationarity," ICML (LILAC) [R]**
- (interpretation) These are the ML versions of latent-cause inference. MOLe
  creates a new model when surprise is high and recalls an old one when a
  task recurs.

### 1F. State abstraction and successor representations in RL

**Li, Walsh & Littman (2006). "Towards a unified theory of state abstraction for MDPs."**
ISAIM. http://anytime.cs.umass.edu/aimath06/proceedings/P21.pdf [V for citation; R for content]
- Q1: An abstract state phi(s).
- Q2: Ground states that are equivalent under a chosen criterion. From
  finest to coarsest: model-irrelevance (bisimulation), Q^pi-irrelevance,
  Q*-irrelevance, a*-irrelevance, and pi*-irrelevance. [R]
- Q3: At storage (the representation).
- Q4: Causal. Coarser abstractions are more sample-efficient.
- Q5: Optimal behavior in the same MDP.
- Q7/Q8: YES, in qualitative form [R]. The finer abstractions keep
  optimality when used with Q-learning. The coarsest (pi*-irrelevance) can
  make Q-learning FAIL to converge to optimal behavior, and some
  abstractions stop being safe for planning. A coarser abstraction discards
  more, and what it discards can include information that the LEARNING
  ALGORITHM needs even when the optimal policy does not.
- (interpretation) What can safely be thrown away depends on the downstream
  learner, not only on the task.

**Givan, Dean & Greig (2003). "Equivalence notions and model minimization in Markov decision processes."**
Artificial Intelligence 147:163-223 [R]
**Ravindran & Barto (2002/2003). MDP homomorphisms (SARA 2002; IJCAI 2003) [R]**
**Ferns, Panangaden & Precup (2004). "Metrics for finite Markov decision processes."**
UAI [R]
- Q1: A quotient MDP. Bisimulation groups states that have the same reward
  and the same transitions into equivalence classes. A homomorphism also
  maps actions, which captures symmetries.
- Q2: Every distinction that does not affect reward or dynamics.
- Q8: YES. Bisimulation is the coarsest partition that keeps ALL values for
  all policies. The bisimulation METRIC bounds how much the optimal value can
  differ between states.
- Q7: Bisimulation keeps reward-irrelevant but dynamics-relevant structure.
  It removes only what is irrelevant to both reward and dynamics. That makes
  it the conservative choice.

**Abel, Hershkowitz & Littman (2016). "Near optimal behavior via approximate state abstraction."**
ICML [R]
- Q8: YES. Approximate abstractions (states merged when their Q* values are
  within epsilon) give a bounded value loss of about 2 epsilon R_max /
  (1 - gamma)^2. [R] This is a direct price for discarding information.

**Zhang, McAllister, Calandra, Gal & Levine (2021). "Learning invariant representations for reinforcement learning without reconstruction" (DBC).**
ICLR. https://arxiv.org/abs/2006.10742 [V]
- Q1: An encoder in which latent L1 distance matches the bisimulation
  distance. [V]
- Q2: Task-irrelevant visual detail, such as moving video backgrounds used
  as distractors.
- Q3: At storage (the representation).
- Q4: Causal. Reconstruction objectives are forced to KEEP distractors, and
  DBC drops them.
- Q5: The same task with new distractors.
- Q7: Pixel-reconstruction models spend capacity on distractors, and their
  RL performance drops when distractors are present. [R for the size of the
  effect]
- Q8: The paper includes a value bound inherited from the bisimulation
  metric. [R]
- (interpretation) "Reconstruct everything" is how kept high-frequency detail
  hurts: it competes for capacity with task-relevant structure.

**Dayan (1993). "Improving generalization for temporal difference learning: the successor representation."**
Neural Computation 5:613-624 [R]
**Stachenfeld, Botvinick & Gershman (2017). "The hippocampus as a predictive map."**
Nature Neuroscience 20:1643 [R]
**Momennejad et al. (2017). "The successor representation in human reinforcement learning."**
Nature Human Behaviour 1:680 [R]
**Lehnert & Littman (2020). "Successor features combine elements of model-free and model-based reinforcement learning."**
JMLR 21 [R]
- Q1: The SR, M(s, s'), which is the expected discounted future occupancy of
  s' starting from s. It separates dynamics and policy from reward.
- Q2: The detailed transition structure is compressed into expected
  occupancies. Timing and path details are lost.
- Q3: At storage.
- Q4: Incidental. The SR keeps whatever is predictive under the CURRENT
  policy.
- Q5: Fast re-planning when the REWARD changes (revaluation).
- Q7: The SR adapts to reward changes but not to TRANSITION changes.
  Momennejad et al. 2017 found humans better at reward revaluation than
  transition revaluation, which fits partial SR use. [R] Lehnert & Littman:
  successor-feature abstractions generalize across reward functions but are
  tied to the policy. [R]
- (interpretation) The SR is a clear example of a compression that becomes
  obsolete with the right kind of regime change. It is robust to one kind of
  change (reward) and fragile to another (dynamics). "Which change makes
  which compression stale" can be tested directly.

### 1G. Capacity limits as inductive bias: "less is more" and starting small

**Elman (1993). "Learning and development in neural networks: the importance of starting small."**
Cognition 48(1):71-99 [R]
- Q1: SRN (simple recurrent network) hidden state.
- Q2: Early training uses a small memory window: context is reset every 3-4
  words, with the window growing later. Alternatively, the input starts
  simple.
- Q3: At storage (a limited recurrent window).
- Q4: Claimed CAUSAL. The network failed to learn embedded clauses unless it
  started with limited memory or simple input. [R]
- Q6: The length of the working-memory window.
- Q7: Full memory from the start means long-range dependencies swamp
  learning before local structure is learned.

**Rohde & Plaut (1999). "Language acquisition in the absence of explicit negative evidence: how important is starting small?"**
Cognition 72(1):67-109.
https://doi.org/10.1016/S0010-0277(99)00031-1 [V]
- FAILED REPLICATION IN SPIRIT. With different grammar statistics (semantic
  constraints that make long-distance dependencies informative) and
  different training parameters, starting small was NOT necessary, and
  starting with simplified input or limited memory HINDERED learning. [V]
- LESSON: A "less is more" effect depends on details of the environment and
  the training setup. It is not a law.

**Newport (1990). "Maturational constraints on language learning."**
Cognitive Science 14:11-28 [R]
- Claim: children's limited processing capacity helps them break language
  into morphological parts, while adults take in larger unanalyzed chunks.
- Q3: At encoding (perception and storage).
- Evidence is correlational (age of acquisition). There is no manipulation.

**Kareev (2000). "Seven (indeed, plus or minus two) and the detection of correlations."**
Psychological Review 107:397-402 [R]
**Kareev, Lieberman & Lev (1997). "Through a narrow window: sample size and the perception of correlation."**
Journal of Experimental Psychology: General 126:278-287 [V citation]
**Juslin & Olsson (2005). "Capacity limitations and the detection of correlations: comment on Kareev (2000)."**
Psychological Review 112:256-267 [V citation]
- Claim [R]: Small samples (window size around 7) exaggerate correlations,
  because the sampling distribution of r is skewed, and so they help detect
  them early.
- Critique [R]: Juslin & Olsson argue the advantage mostly disappears once
  hit rates are weighed against false-alarm rates (a signal-detection
  analysis). A small window increases bias, not discriminability.
- LESSON: Any "capacity limit helps" claim has to be scored with a measure
  that is invariant to response criterion (d', AUC). A raw hit rate can make
  a biased limited learner look better.

**Collins & Frank (2012). "How much of reinforcement learning is working memory, not reinforcement learning?"**
European Journal of Neuroscience 35(7):1024-1035.
https://doi.org/10.1111/j.1460-9568.2011.07980.x [V]
- Q1: Two systems. A capacity-limited WM (working-memory) store that learns
  fast and decays, and a slow incremental RL store.
- Q4: WM decay and its capacity limit, around 3-4 items [R], are fitted as
  parameters. Ignoring WM MISATTRIBUTES behavioral variance to the RL system.
  [V]
- Q7: When the set size is below WM capacity, behavior looks like one-shot
  learning. Above it, behavior falls back on slow RL.
- (interpretation) This is a methodological warning for any synthetic study.
  An agent with a small fast store can look like it has "learned" structure
  when it is really holding recent items.

**Cowan (2001). "The magical number 4 in short-term memory."**
Behavioral and Brain Sciences 24:87-185 [R]. Gives the WM capacity limit of
about 4 chunks.

**Capacity as a regularizer in ML, with the complications. Zhang et al. (2017), "Understanding deep learning requires rethinking generalization," ICLR; Nakkiran et al. (2020), "Deep double descent," ICLR; Arpit et al. (2017), "A closer look at memorization in deep networks," ICML [R]**
- Networks with capacity to memorize random labels still generalize on real
  labels. Test error is NOT monotone in capacity (double descent). Networks
  fit simple patterns before they memorize noise.
- LESSON: "Smaller capacity is better" is not reliably true for i.i.d. test
  error. Capacity helps or hurts depending on where the model sits relative
  to the interpolation threshold, and on the kind of nuisance (see Sagawa
  below).

**Bengio, Louradour, Collobert & Weston (2009). "Curriculum learning."**
ICML [R]. This is the ML version of starting small. Its benefits are
real but small and depend on the task.

### 1H. Spurious correlations, shortcut learning, and IRM

**Geirhos et al. (2020). "Shortcut learning in deep neural networks."**
Nature Machine Intelligence 2:665-673. https://arxiv.org/abs/2004.07780 [R]
- Q1: Decision rules that do well on the training distribution.
- Q2: The model uses whichever features separate the training data most
  easily. Those can be texture, background, or watermark.
- Q3: At prediction (the choice of features).
- Q5: OOD (out-of-distribution) data where the shortcut and the label come
  apart.
- Q7: The shortcut is PREDICTIVE in training and fails at test.
- Q8: No bound. This is a taxonomy and review.

**Hermann, Mobahi, Fel & Mozer (2024). "On the foundations of shortcut learning."**
ICLR. https://arxiv.org/abs/2310.16228 [V]
- Q2/Q7: Which feature a model uses depends on PREDICTIVITY (how reliably it
  predicts the training label) AND AVAILABILITY (how easily it can be
  extracted). [V] A feature that is more available but less predictive can
  win. [R for the specific results]
- LESSON: A nuisance hurts when it is MORE AVAILABLE than the core feature,
  even when it is less predictive. In a synthetic study, availability can be
  varied separately from predictivity.

**Hermann & Lampinen (2020). "What shapes feature representations? Exploring datasets, architectures, and training."**
NeurIPS [R]. When two features are both predictive, the easier one
suppresses the harder one. Features that were not needed for the task are
still partly decodable.

**Shah, Tamuly, Raghunathan, Jain & Netrapalli (2020). "The pitfalls of simplicity bias in neural networks."**
NeurIPS. https://arxiv.org/abs/2006.07710 [V]
- Q2: [R] Networks can rely EXCLUSIVELY on the simplest predictive feature
  and ignore complex features that are equally predictive. This extreme
  simplicity bias gives non-robustness, and ensembles or adversarial
  training do not fully fix it.

**Kirichenko, Izmailov & Wilson (2023). "Last layer re-training is sufficient for robustness to spurious correlations" (DFR).**
ICLR. https://arxiv.org/abs/2204.02937 [V]
- Q1: The features in the backbone.
- Q3: Compression and selection happen at PREDICTION, in the last layer.
  They do not happen at storage.
- Q4: The core features are STILL PRESENT in the representation even when
  the classifier relies on the spurious one. [V] Retraining only the last
  layer on a small group-balanced set matches state-of-the-art robustness.
  [V]
- Q7: Keeping the nuisance in the representation is NOT the harm. The harm
  comes from the readout weighting it.
- DESIGN LESSON (the most decision-relevant item in this section): This is a
  restore-and-reweight test. Freeze the representation, retrain the readout
  on data where the nuisance does not predict the label, and see whether
  performance recovers. If it does, the representation already held the
  right information, and the fault is in the readout. If it does not, the
  information was never encoded.

**Sagawa, Raghunathan, Koh & Liang (2020). "An investigation of why overparameterization exacerbates spurious correlations."**
ICML (PMLR 119:8346-8356). https://proceedings.mlr.press/v119/sagawa20a.html [V]
- Q6: Model size, beyond the interpolation threshold.
- Q7: [V] Overparameterization improves average error but HURTS minority
  groups when spurious correlations are present. The cause is an inductive
  bias toward "memorizing" as few examples as possible: the model uses the
  spurious feature for the majority and memorizes the minority. How much
  this happens depends on the majority/minority ratio and on the
  signal-to-noise ratio of the spurious feature. SUBSAMPLING the majority
  helps. Upweighting the minority does not. [V]
- (interpretation) Here, capacity to memorize exact identity is what LETS a
  spurious rule survive. Memorizing the exceptions shields the shortcut from
  gradient pressure. A limit on capacity or memorization could help against
  spurious correlation specifically, while it would hurt on long-tailed data
  (Feldman). This conflict is the core tension.

**Sagawa, Koh, Hashimoto & Liang (2020). "Distributionally robust neural networks for group shifts" (GroupDRO).**
ICLR [R]. Strong regularization is needed for GroupDRO to work.
**Liu et al. (2021). "Just train twice" (JTT).**
ICML [R]. Upweights the examples that an early, heavily regularized model
gets wrong.

**Arjovsky, Bottou, Gulrajani & Lopez-Paz (2019). "Invariant risk minimization."**
arXiv:1907.02893 [R]
**Peters, Buhlmann & Meinshausen (2016). "Causal inference by using invariant prediction."**
JRSS-B 78:947-1012 [R]
- Q1: A representation Phi such that the same optimal classifier on top of
  Phi works in every training environment.
- Q2: Features whose relation to y changes across environments.
- Q3: At storage (Phi) and at prediction.
- Q5: New environments.
- Q7: Environment-specific (regime-specific) correlations are removed ON
  PURPOSE.
- Q8: IRM gives conditions for recovering the invariant predictor that need
  enough environments. Its linear-case result is roughly that the number of
  environments must exceed the dimension of the spurious features. [R]

**Rosenfeld, Ravikumar & Risteski (2021). "The risks of invariant risk minimization."**
ICLR. https://arxiv.org/abs/2010.05761 [V]
- [V] Under a natural and general model, IRM and its alternatives "fundamentally
  do not improve over" ERM. In the linear case, IRM needs more environments
  than there are spurious dimensions. In the NONLINEAR case, IRM can find a
  predictor that is invariant on the training environments but uses the
  spurious features almost everywhere else, so it fails catastrophically
  under a mild shift. [R for the nonlinear detail]

**Kamath, Tangella, Sutherland & Srebro (2021). "Does invariant risk minimization capture invariance?"**
AISTATS [R]. The practical relaxation IRMv1 can pick non-invariant
predictors, even with infinite data and only two environments.

**Gulrajani & Lopez-Paz (2021). "In search of lost domain generalization."**
ICLR [R]. With careful model selection, ERM matches or beats IRM and most
other domain-generalization methods on DomainBed.

**Nagarajan, Andreassen & Neyshabur (2021). "Understanding the failure modes of out-of-distribution generalization."**
ICLR [R]. Even in EASY tasks where the invariant feature fully determines
the label, max-margin classifiers and gradient descent still pick up
spurious features. There are two routes: a "geometric" skew (the ratio of
majority to minority examples) and a "statistical" skew (how fast the
margin converges).

**Puli, Zhang, Oermann & Ranganath (2022). "Out-of-distribution generalization in the presence of nuisance-induced spurious correlations" (NuRD).**
ICLR. https://arxiv.org/abs/2107.00520 [V]
- Q7: They define a NUISANCE-RANDOMIZED distribution in which the nuisance
  is independent of the label. [V] They reweight or generate data to reach
  it, and then learn representations that do not use the nuisance.
- (interpretation) This is exactly the "decorrelate the nuisance" manipulation
  a synthetic world can build in directly.

---------------------------------------------------------------------------

## PART 2. Synthesis

### (a) How systems handle obsolete history, and what evidence tells the mechanisms apart

Eight mechanisms appear in the literature. For each one below: what it does,
examples, and the evidence that distinguishes it from the others.

- **M1. OVERWRITE.** Shared weights are updated in place, so old content is
  destroyed.
  - Examples: plain SGD (catastrophic interference, McCloskey & Cohen 1989
    [R]); gradual extinction (Gershman 2013).
  - Distinguishing evidence: a restore cue does NOT bring the old behavior
    back. Relearning the old regime takes as long as the original learning
    (little savings). Probes of the representation no longer decode old-task
    features.
- **M2. DISCOUNT.** Old data receive exponentially or window-decreasing
  weight.
  - Examples: tracking (Sutton 2007); sliding-window and discounted UCB;
    ACT-R power-law decay (Anderson & Schooler 1991).
  - Distinguishing evidence: the recent past dominates predictions in a
    smooth way that depends on time. The effect depends on ELAPSED time or
    number of samples, NOT on surprise. Performance on a returning old regime
    depends only on how long ago it was seen.
- **M3. ADAPTIVE DISCOUNT (surprise-gated learning rate).**
  - Examples: BOCPD (Adams & MacKay 2007); Nassar et al. 2010; Behrens et al.
    2007.
  - Distinguishing evidence: the learning rate goes up after large errors
    and goes back down afterward. Old data drop out quickly after an
    inferred change, but only AFTER a surprise. As in M2, old regimes are not
    reused.
- **M4. GATE RETRIEVAL.** The old trace is kept but not expressed.
  - Examples: COIN (Heald 2021); extinction as new learning (Bouton 2004
    [R]); engram inaccessibility (Ryan & Frankland 2022).
  - Distinguishing evidence: SPONTANEOUS RECOVERY over time, RENEWAL when the
    context changes, REINSTATEMENT, and EVOKED RECOVERY with a few cue
    trials. Savings are large.
- **M5. INFER REGIME and SPLIT representations.** The system builds new
  causes or contexts and keeps the old ones separate.
  - Examples: latent-cause models (Gershman 2010, 2017); LCNet (2024); MOLe;
    Collins & Frank task-sets.
  - Distinguishing evidence: an abrupt change creates a split and a gradual
    change creates an overwrite, even with the same total evidence. When the
    old regime comes back, it is recognized in a few trials. Structure
    learned for one regime transfers to new situations as a CLUSTER (Collins
    & Frank). How many separate models exist can be read out.
- **M6. KEEP MULTIPLE MODELS / SEPARATE STORES.**
  - Examples: CLS (hippocampus plus cortex); parameter isolation; mixtures
    of experts; PROBE's small set of about 3 strategies.
  - Distinguishing evidence: exact recall of episodes survives even when the
    structured store has generalized. Interference is avoided without loss.
    The cost is capacity that grows with the number of regimes, or a hard
    cap on how many can be held.
- **M7. RESET THE SUMMARY, KEEP THE DATA.**
  - Examples: primacy-bias resets (Nikishin 2022); shrink and perturb (Ash &
    Adams 2020); continual backprop (Dohare 2024); forget-and-relearn (Zhou
    2022); embedding resets (Chen 2023); GDumb.
  - Distinguishing evidence: the harm is present even when the world has NOT
    changed (warm-starting on i.i.d. data, a stationary RL task). This
    identifies the fitted STATE (optimization geometry, early features, dead
    units) as the route of harm, not stale CONTENT. The strongest test is
    that a reset with the data kept beats continued training on the same
    data.
- **M8. ABSTRACTION (discard distinctions at storage).**
  - Examples: bisimulation, homomorphisms, the SR, the information
    bottleneck, IRM.
  - Distinguishing evidence: the representation is INVARIANT to the discarded
    factor (it cannot be decoded). Performance is unchanged when that factor
    is intervened on. Recovery after a regime change that needs the
    discarded factor is slow: there is nothing to restore.

The most informative single contrast is **M1/M8 versus M4/M5/M6**: after the
regime changes back, does old-regime performance recover QUICKLY (savings,
evoked recovery) or SLOWLY? Fast recovery means the information was kept and
gated. Slow recovery means it was destroyed or never encoded.

A second contrast is **M7 versus M2/M3**: does the forgetting help even when
the world is STATIONARY? If yes, the harm came from the optimization state,
not from obsolete content. Sutton 2007, Ash & Adams 2020, and Nikishin 2022
all say yes in their settings.

### (b) Taxonomy of nuisance: which kinds hurt, and by what route

**N1. Independent noise.** The nuisance is independent of both label and
dynamics.
- Does keeping it hurt? MILDLY, and mainly through sample efficiency and
  variance. It costs capacity, and reconstruction objectives are forced to
  model it (DBC). In the i.i.d. setting the information-bottleneck and
  Xu-Raginsky bounds say that less information about the sample means a
  smaller possible generalization gap, but deep networks often generalize
  well while memorizing noise (Zhang 2017).
- Route: capacity competition (the representation) and variance (the
  estimator). The harm is usually small unless capacity is tight.

**N2. Spurious correlation.** The nuisance predicts the label in training and
the relation breaks at test.
- Does keeping it hurt? YES. This is the most thoroughly documented kind of
  harm.
- Route: THE READOUT, NOT STORAGE. Kirichenko 2023 shows the core features
  are still present. The damage is in how features are WEIGHTED.
  Availability matters (Hermann 2024), simplicity bias makes it worse (Shah
  2020), and so does memorization capacity, because memorizing exceptions
  shields the shortcut (Sagawa 2020).
- Fixes: fixes that work on the readout (DFR, subsampling, group
  reweighting) work well. Fixes that constrain the representation (IRM) are
  fragile (Rosenfeld 2021, Gulrajani 2021).

**N3. Obsolete structure.** Structure that was true before and has become
false.
- Does keeping it hurt? YES, if it is kept in SHARED weights: it causes
  interference, primacy bias, and loss of plasticity. It does NOT hurt if it
  is kept in a GATED or split store (CLS, COIN, latent causes). Then it helps
  whenever the old regime returns.
- Route: shared-parameter interference and optimization state (M7).
  Retrieval competition, which shows up as return of fear, happens when a
  split was made without good context inference.

**N4. Regime-specific structure.** Structure that is true only within one
recurring regime.
- Does keeping it hurt? It HELPS if the regime can be inferred at test time.
  It hurts if the regime cannot be identified: the model then has to average
  over regimes, or it applies the wrong regime's structure (return of fear).
  IRM removes it by design, which throws away information that is valid
  within the regime.
- Route: regime-inference error, at retrieval.

**N5. Misleading high-frequency detail.** Examples: texture, fine timing,
exact pixel values.
- Does keeping it hurt? YES when it is MORE AVAILABLE than the core feature.
  The texture bias in Geirhos 2020 and Hermann 2024 is an example.
- Route: the availability bias during feature learning, then the readout.
  The detail is learned first and gets entrenched (a primacy-bias link).

**N6. Exact episodic identity.** Memorization of individual items.
- Does keeping it hurt? It depends on the distribution.
  - It HELPS on long-tailed data (Feldman 2020, Brown 2021: it is provably
    necessary).
  - It HURTS by shielding spurious rules (Sagawa 2020).
  - It HURTS by crowding out general in-context mechanisms (the transient-ICL
    line).
  - It can DELAY generalization until it is cleaned up (grokking).
  - CLS resolves the conflict by keeping identity in a SEPARATE store.
- Route: competition with general mechanisms for the job of reducing loss.

Cross-cutting conclusion. In the documented cases, nuisance rarely hurts just
by being STORED. It hurts in one of three ways:
- (i) it is USED by the readout,
- (ii) it SHARES parameters with what needs to change, or
- (iii) it REDUCES the loss-driven pressure to find the general solution.

Which one is at work determines whether forgetting helps, and which kind of
forgetting.

### (c) "Restore the discarded information" designs and similar causal tests

Nine designs appear in the literature. Each is listed with what its result
means.

- **R1. Readout retraining on a nuisance-decorrelated set** (DFR,
  Kirichenko 2023). Freeze the representation and retrain the last layer on
  data where the nuisance does not predict the label.
  - If performance recovers, the information was kept and the harm was in
    the readout.
  - If it does not recover, the information was discarded at storage.
- **R2. Linear probe of the discarded factor** (Hermann & Lampinen 2020;
  Ramasesh 2021). Decode the supposedly discarded factor from each layer.
  - A probe at chance is needed before claiming "forgotten at storage".
  - Also check the reverse: can the probe still decode factors that the
    readout ignores?
- **R3. Evoked or spontaneous recovery** (COIN, extinction). After the
  regime changes, give a FEW cue trials from the old regime, or wait.
  - Fast recovery means the memory was gated (M4/M5).
  - No recovery means it was overwritten.
- **R4. Gradual versus abrupt change with the same evidence** (Gershman
  2013). Compare a schedule where the new regime ramps in with one where it
  arrives all at once, and then test for return of the old regime.
  - This separates a latent-cause learner from a learner using a fixed
    discount rate.
- **R5. Ablate the forgetting mechanism in both directions** (Akers 2014,
  neurogenesis up and down; Shuai 2010, Rac1). Turn the forgetting operator
  up and down after learning. A dose-response relationship with the outcome
  is the causal signature.
  - Note: Akers measured retention, not downstream generalization. A
    complete design measures both.
- **R6. Reset but keep the data** (Nikishin 2022; Ash & Adams 2020;
  GDumb). Compare three arms:
  - (i) continued training,
  - (ii) reset plus retrain on the same retained data,
  - (iii) train from scratch on the recent window only.
  - Result logic: (ii) > (i) means the harm is in the fitted state.
    (iii) > (ii) means the harm is in the stale data.
- **R7. Restore the discarded factor as an input** (interpretation, based on
  IRM, NuRD, and abstraction bounds). Give the abstracted learner the ground
  truth for the factor it dropped (the regime label, the nuisance value, the
  full state) and measure the change in performance.
  - A large gain on a shifted test means the discarded factor had predictive
    value there.
  - No gain, or a loss, on an in-distribution test means discarding it was
    safe or helpful.
  - This is the direct test of whether forgetting helped. Run it with a
    matched-capacity control, so that extra inputs do not also change the
    amount of capacity.
- **R8. What returns after forgetting** (Zhou 2022). After a partial reset,
  measure WHICH features come back during relearning. Selective forgetting
  predicts that general features return quickly and idiosyncratic ones do
  not.
- **R9. Oracle regime label versus inferred regime** (LCNet, MOLe,
  interpretation). Give the true context identity versus the inferred one.
  The gap measures how much comes from regime-inference error, separate from
  storage.

### (d) Cheap discriminators for a synthetic-world study

These are the designs I would build in first, ordered by information per unit
of compute. All of them are (interpretation) based on the sources above.

1. **Stationary control.** Run every forgetting intervention in a world with
   NO regime change as well as in the world with changes.
   - If forgetting helps in the stationary world, the benefit comes from the
     optimization state or from capacity (the Sutton 2007, Ash & Adams, and
     Nikishin cases), not from obsolete content.
   - This is the one control most likely to reframe the result.
2. **Recurring vs non-recurring regimes (A-B-A vs A-B-C).**
   - When regimes recur, gating/splitting (M4/M5) should beat every discount
     rule, and a reset or overwrite should lose.
   - When they do not recur, splitting only has overhead, and M2/M3 should
     win.
   - This separates "the old history is obsolete" from "the old history is
     dormant".
3. **Abrupt vs gradual change with the same endpoint.** This is Gershman's
   2013 manipulation. A regime-inferring learner keeps A under an abrupt
   change and overwrites A under a gradual one. A fixed-discount learner does
   not care which schedule is used.
4. **Savings / evoked recovery after returning to A.** Use a few cue trials
   and measure trials-to-criterion against a naive learner. This is one
   number, and it classifies the learner as keeping and gating versus
   destroying the old regime.
5. **Nuisance-decorrelated readout retrain (DFR) plus a linear probe.**
   Together these place the harm at storage versus at the readout. The cost
   is one extra linear fit.
6. **Vary predictivity and availability separately** (Hermann 2024). Change
   the nuisance's train correlation rho and its extraction difficulty
   independently. Map the region where shortcut use appears. Without this, a
   "nuisance hurts" result cannot be interpreted.
7. **Forgetting-rate sweep vs switch rate.** Bandit theory predicts an
   interior optimum for the discount rate that moves with the switch
   frequency (Besbes et al. 2014). If the best rate does NOT track the switch
   rate, the benefit is not about obsolescence.
8. **Constant and oracle twins.**
   - Score against the best constant predictor.
   - Score against an oracle-regime learner (R9).
   - Score against GDumb: a bounded buffer plus refitting from scratch.
   - Each bound tells you whether a claimed forgetting benefit is larger than
     what trivial memory policies achieve.
9. **Long-tail vs spurious-correlation arm.** Run the same capacity or
   memorization limit on:
   - (i) a long-tailed task, where Feldman predicts limiting memorization
     HURTS, and
   - (ii) a task with a spurious correlation plus minority exceptions, where
     Sagawa predicts limiting memorization HELPS.

   A mechanism that "helps generalization" in both arms would be surprising
   and worth scrutiny. A single arm cannot distinguish them.
10. **Criterion-invariant scoring.** Use AUC or d' and calibrated
    log-likelihood, not accuracy at one threshold. The Kareev versus
    Juslin-Olsson debate shows that a small-window learner can look better on
    hit rate purely through response bias.
11. **Split-count readout.** For latent-cause or mixture learners, log how
    many clusters or experts exist and how each one's weights have moved.
    Compare with the ground-truth number of regimes. Over-splitting means
    regime-specific structure fragments. Under-splitting means obsolete
    structure interferes.
12. **Per-layer forgetting** (Ramasesh 2021) at an intermediate task
    similarity, where interference is worst. A single global forgetting
    number hides where the forgetting happens.

---------------------------------------------------------------------------

## PART 3. Most decision-relevant claims, with confidence

1. [V] Forgetting helps even in STATIONARY settings (Sutton et al. 2007; Ash
   & Adams 2020; Nikishin et al. 2022). A forgetting benefit is therefore not
   evidence of obsolete history unless a stationary control fails to show it.
2. [V] Spurious-correlation harm sits mostly in the READOUT: the core
   features are still present (Kirichenko et al. 2023). Test at the readout
   before concluding anything about the representation.
3. [V] IRM-style invariance-by-discarding does not reliably beat ERM
   (Rosenfeld et al. 2021). [R] The same holds under fair model selection
   (Gulrajani & Lopez-Paz 2021).
4. [V] Latent-cause and contextual-inference models turn "forgetting" into
   gating and splitting. Their causal signatures (gradual vs abrupt change;
   evoked recovery) are cheap to run (Gershman et al. 2013, 2017; Heald et
   al. 2021).
5. [V] Memorizing exact identity is provably NECESSARY on long-tailed tasks
   (Brown et al. 2021) and HARMFUL under spurious correlation with minority
   exceptions (Sagawa et al. 2020). The same limit on memorization has
   opposite effects in the two cases.
6. [V] Loss of plasticity is a separate harm from interference, and it is
   fixed by partial re-initialization (Dohare et al. 2024). [V] "Forget and
   relearn" works because the forgetting removes idiosyncratic features more
   than consistently useful ones (Zhou et al. 2022).
7. [V] "Starting small" is fragile. Rohde & Plaut (1999) found that limited
   memory or simplified input HINDERED learning under different grammar
   statistics.
8. [V] Formal anchors:
   - Predictive information grows sublinearly (Bialek et al. 2001).
   - Non-predictive memory corresponds to dissipation (Still et al. 2012).
   - [R] Causal states and bisimulation are the minimal sufficient
     partitions.
   - [R] An approximate abstraction costs O(epsilon / (1 - gamma)^2) in value.

## Caveats on this document

- The [V] tags mean the abstract or summary was checked, not the full text.
  Specific numbers marked [R] (window sizes, bounds, set sizes) should be
  confirmed before anyone relies on them.
- Coverage of 2024-2026 is thinner than for earlier years. The main recent
  items are LCNet 2024, Dohare 2024, and Hermann 2024. Recent work on
  plasticity loss in LLMs (2025-2026 arXiv work surfaced in searches) was not
  reviewed in depth.
