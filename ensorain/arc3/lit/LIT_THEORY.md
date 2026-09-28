# LIT_THEORY -- How much retained information does a learner need, and when does discarding help?

Compiled 2026-09-28. Pure ASCII. Scope: theory of retained information vs prediction/generalization.

Verification legend (per source):
- [V] = metadata and the specific claim used here were checked against the abstract/landing page
  during this session (arXiv, PMLR, ACM, AIP, APS, Project Euclid, JMLR, OUP pages).
- [V-meta] = bibliographic metadata checked; the substantive claim used is from memory of the paper body.
- [R] = recalled, not checked this session. Treat as probably right but unverified.

Per-source questions (abbreviated in entries):
Q1 stored / Q2 compressed / Q3 where compression happens (storage, retrieval, prediction) /
Q4 forgetting causal or incidental / Q5 generalization target / Q6 capacity constraint /
Q7 effect of preserving nuisance info / Q8 theoretical limit linking retained info to prediction.

---------------------------------------------------------------------------------------------

## 0. The two anchor facts everything else is measured against

A. More information cannot hurt the Bayes-optimal decision maker (value of information >= 0).
   - Good, I. J. (1967). "On the principle of total evidence." British Journal for the Philosophy
     of Science 17(4):319-321. doi:10.1093/bjps/17.4.319. [V-meta: abstract-level description
     confirms: a coherent Savage agent always prefers to collect rather than ignore FREE evidence.]
   - Blackwell, D. (1953). "Equivalent comparisons of experiments." Annals of Mathematical
     Statistics 24(2):265-272. [R] (a garbling of an experiment is never more valuable for any
     decision problem).
   Conditions (load-bearing): evidence is free, the agent's prior/model is correct, and the agent
   can compute the posterior. Drop any of these and the theorem does not apply.

B. Minimal sufficient statistic = the maximal lossless compression for a known model family.
   - Fisher (1922); Lehmann-Scheffe (1950). [R] A statistic T(X) is sufficient for theta iff
     p(x|T,theta) does not depend on theta; the minimal sufficient statistic is a function of every
     other sufficient statistic. Discarding the NON-sufficient part costs zero Bayes risk for every
     loss; discarding any part of the minimal sufficient statistic costs something for some loss.
   - In sequence prediction the analog is the causal state (Section 5): the minimal sufficient
     statistic of the past for the future.

Consequence: for an unbounded, correctly specified learner, discarding information is never
NECESSARY and at best free. Every theorem that makes discarding "helpful" adds one of:
(i) a rate/memory budget, (ii) finite samples + estimation of the compressor/predictor,
(iii) a restricted (computationally bounded or inductive-biased) predictor family,
(iv) model misspecification, or (v) a shift between train and test distributions (invariance).

---------------------------------------------------------------------------------------------

## 1. Information bottleneck (IB) and its critiques

### 1.1 Tishby, Pereira, Bialek (1999/2000). "The information bottleneck method." Proc. 37th
Allerton Conf.; arXiv:physics/0004057. [R]
- Q1: an encoder p(t|x); representation T. Q2: X is compressed into T, trading I(X;T) against I(T;Y).
- Q3: storage/representation (T replaces X). Q4: forgetting is the objective (causal by design).
- Q5: relevance to a fixed Y under the KNOWN joint p(x,y) -- not generalization from samples.
- Q6: rate I(X;T) via Lagrange multiplier beta. Q7: nuisance info raises I(X;T) without raising I(T;Y);
  with known p(x,y) it is merely wasteful, not harmful. Q8: the IB curve is the rate-distortion
  function with log-loss distortion; at beta->inf T becomes a minimal sufficient statistic for Y.
- Note: IB as originally posed is a distribution-known problem; it says nothing about finite samples.

### 1.2 Shamir, Sabato, Tishby (2010). "Learning and generalization with the information
bottleneck." Theoretical Computer Science 411(29-30):2696-2711. doi:10.1016/j.tcs.2010.04.006.
[V-meta; bound content R]
- Q1: an empirical-plug-in IB encoder with finite cardinality |T|. Q2: X -> T.
- Q3: storage. Q4: causal (the bound's gap term grows with |T| and the mutual informations).
- Q5: the TRUE I(T;Y) and I(X;T) estimated from a finite sample. Q6: cardinality |T| of the bottleneck.
- Q7: large |T| / high I(X;T) makes the empirical I(T;Y) overfit (finite-sample estimation error).
- Q8: yes -- generalization bounds for the IB objective scale with |T| and not with |X|;
  the first formal "less retained info -> better estimation of the relevant info" result.

### 1.3 Shwartz-Ziv, Tishby (2017). "Opening the black box of deep neural networks via
information." arXiv:1703.00810. [R]
- Claimed: SGD training shows a fitting phase then a compression phase (I(X;T) falls), and
  compression drives generalization. Q3: representation (hidden activations). Q4: claimed causal.
- Status: largely refuted as a general claim (1.4, 1.5).

### 1.4 Saxe, Bansal, Dapello, Advani, Kolchinsky, Tracey, Cox (2018). "On the information
bottleneck theory of deep learning." ICLR 2018; extended J. Stat. Mech. (2019) 124020.
https://openreview.net (ICLR 2018); https://iopscience.iop.org/article/10.1088/1742-5468/ab3985 [V]
- Finding (verified in abstract): the compression phase depends on the nonlinearity (double-sided
  saturating tanh compresses; ReLU generally does not); "no evident causal connection between
  compression and generalization: networks that do not compress are still capable of generalization,
  and vice versa"; compression when present also appears under full-batch GD, so it is not SGD
  diffusion.
- Q4: forgetting is INCIDENTAL (a nonlinearity/binning artifact). Q7: networks that preserve input
  info in hidden layers generalize fine. Q8: none -- this is the key counterexample.
- Related [R]: Goldfeld et al. (2019) "Estimating information flow in deep neural networks," ICML --
  for deterministic nets I(X;T) is infinite/constant; measured "compression" is clustering of
  representations, not information loss.

### 1.5 Kolchinsky, Tracey, Van Kuyk (2019). "Caveats for information bottleneck in deterministic
scenarios." ICLR 2019. arXiv:1808.07593. [V]
- When Y is a deterministic function of X: (1) the IB Lagrangian cannot trace the IB curve,
  (2) trivial solutions exist at all points of the curve, (3) layers of a low-error classifier
  cannot exhibit a strict compression/prediction trade-off.
- Relevance: in deterministic synthetic worlds IB-style "compression" diagnostics are degenerate.
  Use predictive rate-distortion on stochastic futures or on causal states instead (Section 5).

### 1.6 Achille, Soatto (2018). "Emergence of invariance and disentanglement in deep
representations." JMLR 19:1947-1980. https://jmlr.org/papers/volume19/17-646/17-646.pdf [V]
- Q1: representation z of x (and separately, information in the WEIGHTS about the dataset).
- Q2: nuisance information. Q3: representation/prediction.
- Q4: causal FOR INVARIANCE: they show invariance to nuisances is equivalent to minimality
  (low I(x;z)) of a sufficient representation. Q5: invariance to nuisance factors (a
  distribution-shift-flavored target), not iid test error per se.
- Q6: I(x;z) plus I(weights; dataset) (an IB on the weights = PAC-Bayes-like term).
- Q7: preserved nuisance = lack of invariance; hurts when the test distribution changes the nuisance.
- Q8: relates minimality to invariance; the generalization link runs through the weight-information
  term, not through activation compression (this distinction is the useful part).

### 1.7 Kawaguchi, Deng, Ji, Huang (2023). "How does information bottleneck help deep learning?"
ICML 2023, PMLR 202:16049-16096. arXiv:2305.18887. [V]
- Q8 (verified): generalization bounds that scale with the degree of information bottleneck
  (roughly I(X;Z|Y), "unnecessary information" in hidden layers), not with parameter counts.
- Q4 (verified quote-level): controlling IB is "one way to control generalization errors ... although
  it is not the only or necessary way." This is the cleanest formal statement that discarding is
  SUFFICIENT-FOR-A-BOUND, NOT NECESSARY.
- Q7: preserved nuisance loosens the bound; it does not force bad test error.

### 1.8 Xu, Zhao, Song, Stewart, Ermon (2020). "A theory of usable information under
computational constraints." ICLR 2020. arXiv:2002.10689. [V]
- Defines predictive V-information I_V(X->Y) relative to a predictor family V.
- Q8 (verified): V-information violates the data processing inequality: computation can CREATE
  usable information (e.g., decrypting), so a deterministic transform of X can be more useful to a
  bounded predictor than X itself. PAC-style estimation guarantees depend on the complexity of V.
- Relevance: the formal bridge between "Shannon-available" and "accessible to a bounded learner."
  Discarding + recoding can raise V-information even though it cannot raise Shannon information.
- Follow-up [V-meta, content R]: Dubois, Kiela, Schwab, Vedantam (2020), "Learning optimal
  representations with the decodable information bottleneck," NeurIPS 2020, arXiv:2009.12789 --
  V-sufficiency and V-minimality; minimal-for-family V representations give guarantees for that
  family specifically.

### 1.9 Westphal, Hailes, Musolesi (2025/2026). "A generalized information bottleneck theory of
deep learning." arXiv:2509.26327 (preprint). [V]
- Reformulates IB via synergy; claims compression phases appear across architectures including ReLU
  and that synergistic functions generalize better; GIB upper-bounds the IB objective.
- Status: recent, unreviewed preprint; treat as Conjecture-tier for the program.

---------------------------------------------------------------------------------------------

## 2. Rate-distortion for learning and bounded agents

### 2.1 Arumugam, Van Roy (2021). "Deciding what to learn: a rate-distortion approach." ICML 2021,
PMLR 139:373-382. arXiv:2101.06197. [V]
- Q1: a learning TARGET (a compressed surrogate of the optimal policy/environment), chosen by
  rate-distortion. Q2: the environment/optimal-policy description.
- Q3: in what the agent tries to learn (upstream of storage). Q4: causal -- a deliberate trade
  "between the information an agent must acquire to learn and the sub-optimality of the resulting
  policy." Q6: rate (bits about the environment). Q8: regret bounds in terms of the rate-distortion
  function of the target. Takeaway: under a sample/info budget, aiming at a lossy target is optimal.
- Related [R]: Arumugam et al. (2022) "On rate-distortion theory in capacity-limited cognition &
  reinforcement learning," arXiv:2210.16877; Sims, C. A. (2003) "Implications of rational
  inattention," J. Monetary Economics 50(3):665-690 (channel-capacity-limited agents);
  Ortega, Braun (2013) "Thermodynamics as a theory of decision-making with information-processing
  costs," Proc. R. Soc. A 469:20120683. These define bounded optimality with an explicit
  information cost; discarding is optimal GIVEN the cost, never absent it.

### 2.2 Rate-distortion-theoretic generalization bounds. [R]
- Sefidgaran, Gohari, Richard, Simsekli (2022), "Rate-distortion theoretic generalization bounds for
  stochastic learning algorithms," COLT 2022; Sefidgaran, Zaidi, Piantanida (2023) "Minimum
  description length and generalization guarantees for representation learning," NeurIPS 2023,
  arXiv:2402.03254 [V-meta via search listing].
- Idea: the generalization gap is bounded by the rate needed to describe a lossy (distorted) version
  of the learned hypothesis/representation, so a learner that is "compressible up to distortion"
  generalizes. Q4: compressibility is a certificate, not a mechanism requirement.

---------------------------------------------------------------------------------------------

## 3. MDL, compression and information-theoretic generalization bounds (and counterexamples)

### 3.1 Classic MDL / Occam. [R]
- Rissanen (1978) "Modeling by shortest data description," Automatica 14:465-471; Grunwald (2007)
  "The Minimum Description Length Principle," MIT Press; Blumer, Ehrenfeucht, Haussler, Warmuth
  (1987) "Occam's razor," IPL 24:377-380; Littlestone, Warmuth (1986) "Relating data compression
  and learnability" (tech report).
- Q1: a code for the hypothesis plus data-given-hypothesis. Q2: the training sample.
- Q3: storage of the hypothesis. Q4: causal in the bound (short description -> small gap).
- Q8: gap <= O((description length + log 1/delta)/n). Compressing the HYPOTHESIS, not the data
  stream, is what generalizes.

### 3.2 Sample compression schemes. Moran, Yehudayoff (2016) "Sample compression schemes for VC
classes," J. ACM 63(3). [R]
- Every VC class of dim d has a sample compression scheme of size exp(d). Learning = keeping a
  small subset of the data and reconstructing. Q1: k retained EXAMPLES (literal storage of a few
  raw records). Q3: storage. Q8: compression size k implies generalization; for VC classes
  learnability <-> finite compression. This is "exact retention of a few items" as a sufficient
  mechanism -- a useful contrast to "statistic retention".

### 3.3 Hypothesis compression bounds for deep nets. [R, except Lotfi V]
- Arora, Ge, Neyshabur, Zhang (2018) "Stronger generalization bounds for deep nets via a
  compression approach," ICML 2018.
- Dziugaite, Roy (2017) "Computing nonvacuous generalization bounds for deep (stochastic) neural
  networks with many more parameters than training data," UAI 2017.
- Zhou, Veitch, Austern, Adams, Orbanz (2019) "Non-vacuous generalization bounds at the ImageNet
  scale: a PAC-Bayesian compression approach," ICLR 2019.
- Lotfi, Finzi, Kapoor, Potapczynski, Goldblum, Wilson (2022) "PAC-Bayes compression bounds so tight
  that they can explain generalization," NeurIPS 2022. [V] Quantization in a linear subspace;
  large models compress more than previously known.
- Q3 for all: compression is applied POST HOC to the stored hypothesis to certify it; the trained
  model itself may store a lot. Q4: incidental to learning, causal only for the certificate.

### 3.4 Information-theoretic (mutual-information) generalization bounds. [R, except where V]
- Russo, Zou (2016) AISTATS; Xu, Raginsky (2017) "Information-theoretic analysis of generalization
  capability of learning algorithms," NeurIPS 2017: gap <= sqrt(2 sigma^2 I(S;W)/n).
- Steinke, Zakynthinou (2020) "Reasoning about generalization via conditional mutual information,"
  COLT 2020, PMLR 125:3437-3452. arXiv:2001.09122 [V]: CMI = how well the training set can be
  recognized from the output given a supersample; unifies VC/uniform convergence and DP.
- Q1: the learned hypothesis W. Q2: information about the SAMPLE S in W. Q3: storage of W.
- Q8: gap bounded by I(S;W) or CMI -- "retained info about the specific sample" -> gap.

### 3.5 Counterexamples to "little retained information is necessary/explanatory"
- Bassily, Moran, Nachum, Shafer, Yehudayoff (2018). "Learners that use little information."
  ALT 2018, PMLR 83:25-55. arXiv:1710.05233. [V] d-bit information learners generalize (upper
  bound); BUT there are concept classes for which any empirical risk minimizer must reveal a lot of
  information (lower bound); in the distribution-dependent setting every VC class has low-info ERMs.
  [R: the lower-bound example is thresholds, needing ~log log |X| bits for proper consistent learners.]
- Livni (2023). "Information theoretic lower bounds for information theoretic upper bounds."
  NeurIPS 2023. arXiv:2302.04925. [V] In stochastic convex optimization, any algorithm achieving
  true-risk minimization must carry dimension-dependent mutual information with the sample, even
  though SGD/regularized ERM have dimension-free sample complexity -> MI bounds cannot explain
  those algorithms' generalization.
- Nagarajan, Kolter (2019). "Uniform convergence may be unable to explain generalization in deep
  learning." NeurIPS 2019. arXiv:1902.04742. [V] Bounds can grow with n; there exist GD-trained
  overparameterized linear/NN classifiers where even algorithm-dependent uniform convergence is
  nearly vacuous.
- Feldman (2020). "Does learning require memorization? A short tale about a long tail."
  STOC 2020. arXiv:1906.05271. [V] With long-tailed subpopulation frequencies, memorizing labels of
  rare (even singleton) examples is NECESSARY for near-optimal generalization.
- Brown, Bun, Feldman, Smith, Talwar (2021). "When is memorization of irrelevant training data
  necessary for high-accuracy learning?" STOC 2021. arXiv:2012.06421. [V] Natural problems where
  EVERY sufficiently accurate algorithm must encode essentially all information about a large
  subset of its training examples, including information irrelevant to the task.
- Feldman, Kornowski, Lyu (2025). "Trade-offs in data memorization via strong data processing
  inequalities." COLT 2025, PMLR 291:1935-1973. arXiv:2506.01855. [V] Omega(d) bits about the
  training data must be memorized when only O(1) d-dimensional examples are available; the required
  memorization decays with n at a problem-specific rate; simple algorithms match the lower bounds.
- Per-question summary for this cluster: Q4 forgetting would be HARMFUL; Q7 preserving nuisance is
  forced in low-sample/long-tail regimes because the learner cannot tell nuisance from signal from
  few examples; Q8 there are LOWER bounds on retained information that decrease with sample size.
  This is the strongest theory against "discarding is necessary."

---------------------------------------------------------------------------------------------

## 4. Algorithmic statistics (the individual-sequence version of sufficiency)

### Vereshchagin, Vitanyi (2004). "Kolmogorov's structure functions and model selection."
IEEE Trans. Inf. Theory 50(12):3265-3290. [V]
- Q1: a model (finite set) containing the data; data-to-model code. Q2: the individual string.
- Q8: the structure function determines the best-fitting model at each complexity level; an
  algorithmic sufficient statistic captures all "meaningful" regularity, the rest is typical noise.
- Related [R]: Gacs, Tromp, Vitanyi (2001) "Algorithmic statistics," IEEE TIT 47(6); Vitanyi (2002)
  "Meaningful information," arXiv:cs/0111053. Caveat: uncomputable; no resource bound (see 7.2
  epiplexity for the bounded version).

---------------------------------------------------------------------------------------------

## 5. Sequence prediction: causal states, predictive states, predictive information

### 5.1 Crutchfield, Young (1989) "Inferring statistical complexity," PRL 63:105; Shalizi, Crutchfield
(2001) "Computational mechanics: pattern and prediction, structure and simplicity," J. Stat. Phys.
104:817-879. [R]
- Q1: the causal state = equivalence class of pasts with identical conditional future distributions.
- Q2: the past. Q3: storage (the state IS the memory). Q4: forgetting everything except the causal
  state is lossless for prediction (causal-state sufficiency); forgetting more is lossy.
- Q5: optimal prediction of the whole future (not a single target Y).
- Q6: statistical complexity C_mu = H(causal state) = memory of the minimal unifilar optimal predictor.
- Q7: storing more than the causal state (e.g., the raw window) costs memory, never prediction.
- Q8 (theorems, R): causal states are minimal among prescient (maximally predictive) rivals and
  unique; E (excess entropy = I(past;future)) <= C_mu; the gap C_mu - E is crypticity (information
  stored that is not transmitted to the future). So the MINIMUM memory for exact prediction is
  generally STRICTLY MORE than the predictive information.

### 5.2 Crutchfield, Feldman (2003). "Regularities unseen, randomness observed: levels of entropy
convergence." Chaos 13(1):25-54. arXiv:cond-mat/0102181. [V]
- Q8 (verified): entropy convergence curves H(L) give the apparent memory and the information that
  must be extracted to synchronize to and optimally predict a source; ignoring structure (short
  windows) converts missed regularities into apparent randomness.
- Direct discriminator: an observer with window L sees entropy rate h(L) > h_mu; the excess
  sum_L (h(L) - h_mu) = E. Prediction loss from truncation is measurable and has an exact oracle.

### 5.3 Crutchfield, Ellison, Mahoney (2009) "Time's barbed arrow: irreversibility, crypticity, and
stored information," PRL 103:094101. [R] -- crypticity chi = C_mu - E; nonzero crypticity means
some stored information is never "visible" in the future yet is required to generate it.

### 5.4 Still, Crutchfield, Ellison (2010). "Optimal causal inference: estimating stored information
and approximating causal architecture." Chaos 20(3):037111. arXiv:0708.1580. [V]
- Predictive rate-distortion (IB between past and future). Q4: controlled lossy clustering of pasts.
- Q8 (verified): as the model-complexity constraint relaxes, optimal causal filtering recovers the
  causal-state partition exactly; at finite sample sizes, "optimal causal estimation" picks a
  coarser model to avoid overfitting -- i.e., DISCARDING is justified by FINITE DATA, and the
  lossless limit is the epsilon-machine.

### 5.5 Creutzig, Globerson, Tishby (2009). "Past-future information bottleneck in dynamical
systems." Phys. Rev. E 79:041925. doi:10.1103/PhysRevE.79.041925. [V]
- For linear-Gaussian systems the past-future IB reduces to a generalized eigenvalue problem (CCA),
  with structural phase transitions as the rate increases. Gives an exactly solvable
  rate-vs-predictive-information curve for Gaussian worlds.

### 5.6 Marzen, Crutchfield (2016). "Predictive rate-distortion for infinite-order Markov
processes." J. Stat. Phys. 163:1312-1338 (correction 2021). arXiv:1412.2859. [V]
- Q8 (verified): clustering long pasts to predict long futures has resources exponential in length;
  casting predictive rate-distortion in terms of forward/reverse causal states circumvents the
  curse of dimensionality. Gives exact predictive RD curves for processes with known epsilon-machines.

### 5.7 Jurgens, Crutchfield (2021). "Divergent predictive states: the statistical complexity
dimension of stationary, ergodic hidden Markov processes." Chaos 31(8):083114. arXiv:2102.10487. [V]
- Q8 (verified): even finite-state HMM generators generically produce processes whose optimal
  predictors require infinitely many (uncountable, claimed) predictive features; C_mu diverges and
  its growth is characterized by a statistical complexity dimension.
- CRITIQUE: Grassberger (2024/2025) "On three papers by Jurgens & Crutchfield, and on the basic
  structure of 'computational mechanics'," arXiv:2401.03279. [V] Argues computational errors (open
  sets vs closures), that the mixed-state formalism is the standard HMM forward algorithm, that
  causal states correspond generally to FINITE histories and epsilon-machines are always countable.
  => The "uncountable causal states" claim is CONTESTED; do not build on it without checking.
- Newer: Jurgens, Crutchfield (2025) "Taxonomy of prediction," arXiv:2504.11371 [V]: bidirectional
  machine, fourteen new calculable multivariate information measures, closed-form for finitely
  modeled processes. Useful as a checklist of quantities to compute in a synthetic world.

### 5.8 Shai, Marzen, Teixeira, Gietelink Oldenziel, Riechers (2024). "Transformers represent belief
state geometry in their residual stream." NeurIPS 2024. arXiv:2405.15943. [V]
- Q1: transformer residual stream linearly encodes Bayesian belief states (mixed states) over the
  generator's hidden states, including fractal geometries, and contains info about the entire
  future beyond next-token. Relevance: empirical check that a trained learner converges to the
  sufficient statistic (belief state), not raw history, when the generator is a known HMM.

### 5.9 Predictive state representations (PSRs). [R]
- Littman, Sutton, Singh (2002) "Predictive representations of state," NeurIPS 14; Singh, James,
  Rudary (2004) "Predictive state representations: a new theory for modeling dynamical systems,"
  UAI 2004. Q1: predictions of a finite set of core tests. Q8: the linear dimension of the
  system-dynamics matrix bounds the number of core tests; PSR dimension <= number of POMDP states.
  Memory = predictions of the future, not beliefs over latent states.

### 5.10 Subramanian, Sinha, Seraj, Mahajan (2022). "Approximate information state for approximate
planning and reinforcement learning in partially observed systems." JMLR 23(12):1-83. [V]
- Q1: a recursively updatable function of history sufficient to predict reward and next
  observation. Q8 [R for bound form]: approximation error in the information state (in an IPM)
  yields bounded suboptimality of the resulting policy. This is the control-theoretic formal
  statement of "a finite statistic is enough, and how much error you buy by approximating it."

### 5.11 Bialek, Nemenman, Tishby (2001). "Predictability, complexity, and learning."
Neural Computation 13(11):2409-2463. doi:10.1162/089976601753195969. [V]
- Q1: predictive information I_pred(T) = I(past of length T; future). Q8 (verified): I_pred(T)
  either stays finite, grows logarithmically, or grows as a fractional power law. [R] Log growth
  with coefficient K/2 corresponds to learning a K-parameter model from the past (the sufficient
  statistic is a parameter estimate); power-law growth = nonparametric/infinite-dimensional learning.
  Q7: everything in the past beyond I_pred is nuisance for prediction (non-predictive information),
  which Bialek et al. argue is the "vast majority" of bits.
- This is the cleanest classification of worlds by how retained-information needs scale with time.

### 5.12 Sharan, Kakade, Liang, Valiant (2018). "Prediction with a short memory." STOC 2018.
arXiv:1612.02526. [V]
- Q8 (verified): if I(past;future) <= I, a Markov model on the last I/eps observations achieves
  expected KL error eps relative to the optimal predictor that sees the entire past and knows the
  generator -- ON AVERAGE over time. Lower bounds: window log(n)/eps is information-theoretically
  necessary for HMMs with n hidden states (l1 error sqrt(eps)); and d^Theta(log n / eps) samples
  are necessary for any computationally tractable learner (under hardness assumptions) with
  alphabet size d.
- Q4: forgetting beyond the window is causal-for-tractability: short memory is sufficient on
  average; the computational lower bound says a tractable learner cannot efficiently exploit long
  memory in the worst case. KEY paper for (b).

---------------------------------------------------------------------------------------------

## 6. More information/data can hurt: bounded learners, sample-wise non-monotonicity

### 6.1 Memory-sample lower bounds (retention is NECESSARY for fast learning)
- Raz (2016/2019). "Fast learning requires good memory: a time-space lower bound for parity
  learning." FOCS 2016 pp.266-275; J. ACM 66(1) (2019). arXiv:1602.05161. [V] Any streaming
  learner for parity over {0,1}^n with fewer than n^2/25 bits of memory needs exponentially many
  samples.
- Sharan, Sidford, Valiant (2019). "Memory-sample tradeoffs for linear regression with small error."
  STOC 2019. [V] Subquadratic memory forces a slower convergence rate for streaming linear
  regression.
- [R] Garg, Raz, Tal (2018) "Extractor-based time-space lower bounds for learning," STOC 2018 --
  extends to broad classes. Q4: forgetting is HARMFUL -- lower bounds on retained bits.
  Q6: bits of working memory in a streaming model. Q8: explicit memory x samples trade-off.

### 6.2 Sample-wise non-monotonicity
- Nakkiran (2019). "More data can hurt for linear regression: sample-wise double descent."
  arXiv:1912.07242. [V] Min-norm (GD) linear regression with isotropic Gaussian covariates in the
  overparameterized regime: test risk can INCREASE with more samples (bias falls, variance rises).
- Belkin, Hsu, Ma, Mandal (2019) "Reconciling modern machine-learning practice and the classical
  bias-variance trade-off," PNAS 116(32):15849-15854. [R]
- Bartlett, Long, Lugosi, Tsigler (2020) "Benign overfitting in linear regression," PNAS
  117(48):30063-30070. [R] Interpolating (fully retaining) noisy training data is harmless iff the
  covariance has many low-variance directions to absorb the noise (effective-rank conditions).
  => Retention of noise is benign when there is a "junk subspace" to store it in without
  affecting prediction. A direct theory of "nuisance can be preserved harmlessly."
- Loog, Viering, Mey (2019) "Minimizers of the empirical risk and risk monotonicity," NeurIPS 2019;
  Viering, Loog (2022) "The shape of learning curves: a review," IEEE TPAMI. [R] ERM can be
  non-monotone in n even in simple well-specified settings.
- Bousquet, Daniely, Kaplan, Mansour, Moran, Stemmer (2022). "Monotone learning." COLT 2022,
  PMLR 178:842-866. arXiv:2202.05246. [V] Every (multiclass) learning algorithm can be transformed
  into a monotone one with similar performance. => Non-monotonicity is a property of the LEARNER,
  not of the information; it is fixable by wrapping (e.g., holdout-validated acceptance of updates).
- Grunwald, van Ommen (2017). "Inconsistency of Bayesian inference for misspecified linear models,
  and a proposal for repairing it." Bayesian Analysis 12(4):1069-1103. doi:10.1214/17-BA1085. [V]
  Under misspecification (heteroskedastic truth, homoskedastic model), the posterior concentrates on
  worse, higher-dimensional models as n grows ("hypercompression"); SafeBayes (tempered likelihood)
  repairs it. => Even the Bayesian loses Good's guarantee once the model is wrong.

### 6.3 Irrelevant features / nuisance dimensions cost bounded learners
- Ng (2004). "Feature selection, L1 vs. L2 regularization, and rotational invariance." ICML 2004.
  [V] L1-logistic regression: sample complexity logarithmic in #irrelevant features; ANY rotationally
  invariant algorithm (L2 logistic regression, SVMs, standard-init NNs trained by GD) has worst-case
  sample complexity LINEAR in #irrelevant features.
- Littlestone (1988) "Learning quickly when irrelevant attributes abound: a new linear-threshold
  algorithm," Machine Learning 2:285-318. [R] Winnow: mistakes O(k log n) with n-k irrelevant attrs.
- Q7 (cleanest answer in the literature): preserving nuisance dims costs samples linearly or
  logarithmically depending on the learner's symmetry/inductive bias; the Bayes-optimal predictor
  (with the right prior) is unaffected.

### 6.4 Computational-statistical gaps and computation-data trade-offs
- Chandrasekaran, Jordan (2013). "Computational and statistical tradeoffs via convex relaxation."
  PNAS 110(13):E1181-E1190. arXiv:1211.1073. [V] "Algorithmic weakening": as data grows, back off
  to cheaper relaxations; more data buys computation (the reverse direction: more info helps a
  bounded learner).
- [R] Shalev-Shwartz, Shamir, Tromer (2012) "Using more data to speed-up training time," AISTATS.
- [R] Berthet, Rigollet (2013) "Complexity theoretic lower bounds for sparse principal component
  detection," COLT 2013 -- a regime where the information is present but (under planted clique)
  no poly-time test uses it.
- [R] Kearns (1998) "Efficient noise-tolerant learning from statistical queries," J. ACM -- parity
  not SQ-learnable; Barak, Edelman, Goel, Kakade, Malach, Zhang (2022) "Hidden progress in deep
  learning: SGD learns parities near the computational limit," NeurIPS 2022.
- Q8: gaps show "information-theoretically available" and "efficiently usable" come apart by
  polynomial-vs-exponential margins in explicit problems.

---------------------------------------------------------------------------------------------

## 7. Formalizations of "available vs accessible" information

### 7.1 V-information (Xu et al. 2020, entry 1.8). [V] Information relative to a predictor family;
DPI fails; computation creates usable information.

### 7.2 Finzi, Qiu, Jiang, Izmailov, Kolter, Wilson (2026). "From entropy to epiplexity: rethinking
information for computationally bounded intelligence." arXiv:2601.03220 (v1 Jan 2026, rev. Mar
2026). [V abstract]
- Defines epiplexity: the structural information a time-bounded observer can learn, separated from
  "time-bounded entropy" (unpredictable-to-the-observer content such as PRG output or chaos).
- Claims (verified at abstract level): information CAN increase under deterministic computation;
  information DEPENDS ON DATA ORDERING; likelihood modeling can yield programs more complex than the
  generator. Gives estimators that correlate with downstream/OOD performance.
- Status: preprint; the ordering-dependence claim is directly testable in synthetic worlds.

### 7.3 Resource-bounded Kolmogorov / pseudorandomness [R]: Yao (1982), Blum-Micali (1984) --
a PRG output has near-zero Shannon/Kolmogorov information beyond the seed yet is maximally
unpredictable to poly-time observers. This is the canonical world where "exact history is
sufficient information-theoretically but useless computationally."

### 7.4 Bounded rationality with information cost [R]: Sims (2003), Ortega-Braun (2013),
Tishby-Polani (2011) "Information theory of decisions and actions" (in Perception-Action Cycle,
Springer). Discarding is optimal given a price on bits processed.

---------------------------------------------------------------------------------------------

## 8. SYNTHESIS

### (a) When is DISCARDING information NECESSARY for generalization, vs one way to implement a
bounded learner?

1. Never necessary for a correctly specified, computationally unbounded Bayesian (Good 1967;
   Blackwell 1953). Discarding the non-sufficient part is free; discarding more is costly.
   The minimal sufficient statistic / causal state marks the exact boundary.

2. Discarding is NECESSARY only relative to an explicit constraint, and the constraint determines
   WHAT to discard:
   - Memory/rate budget (IB, predictive rate-distortion, rational inattention, Arumugam-Van Roy):
     keep the highest-value bits per unit rate. Necessary by definition of the budget.
   - Finite-sample estimation of the compressor/predictor (Shamir-Sabato-Tishby 2010; Still et al.
     2010): the coarser model is chosen because its parameters can be estimated; the optimal
     coarseness shrinks toward the causal-state partition as n grows. Discarding is a
     variance-control device whose optimal amount -> the lossless limit as data grows.
   - Distribution shift / invariance (Achille-Soatto 2018): minimality = invariance to nuisance;
     necessary only if the test distribution moves the nuisance.
   - Learner symmetry / inductive bias (Ng 2004): rotationally invariant learners pay linearly for
     retained nuisance dimensions; L1/Winnow-type learners pay log. So "discarding helps" is
     learner-relative, not world-relative.

3. There are strong results that discarding is HARMFUL or impossible:
   - Memorization lower bounds (Feldman 2020; Brown et al. 2021; Feldman-Kornowski-Lyu 2025):
     accurate learners MUST retain large amounts of sample-specific, even task-irrelevant,
     information when data is scarce or long-tailed; the required amount decays with n.
   - Memory-sample lower bounds (Raz 2016; Sharan-Sidford-Valiant 2019): below a memory threshold,
     sample complexity blows up (exponentially for parity).
   - MI-bound limitations (Bassily et al. 2018; Livni 2023; Nagarajan-Kolter 2019): low retained
     information is not what explains generalization of standard algorithms.
   - Empirical-theory refutation of "compression phase causes generalization" (Saxe et al. 2018;
     Goldfeld et al. 2019); Kawaguchi et al. 2023 prove IB control is sufficient-for-a-bound but
     "not the only or necessary way."

   Net: across the theory, compression of the HYPOTHESIS (description length / information about the
   sample in the weights) is the quantity with the clean link to generalization. Compression of the
   STREAM / representation is neither necessary nor sufficient in general. Forgetting is causal only
   under an explicit budget, finite-sample estimation pressure, or a shift target. Otherwise it is
   an implementation choice of a bounded learner.

4. Where compression "occurs" matters, and the literature separates it cleanly:
   - storage (IB, causal states, sufficient statistics, sample compression),
   - hypothesis/weights (MDL, PAC-Bayes, MI/CMI bounds -- the one tied to generalization),
   - prediction/readout (V-information, decodable IB: what a restricted readout can use).
   A study that measures only storage compression and attributes generalization to it is repeating
   the Shwartz-Ziv/Tishby error that Saxe et al. refuted.

### (b) Information-theoretic availability vs computationally accessible generalization -- who has
formalized it and how

- Availability side: Good (1967) / Blackwell (1953) value-of-information >= 0; data processing
  inequality; sufficiency; causal-state optimality (Shalizi-Crutchfield 2001).
- Accessibility side, formal objects:
  1. Predictor-family-relative information: V-information (Xu et al. ICLR 2020), with DPI failure
     proven; decodable IB (Dubois et al. 2020).
  2. Time-bounded structural information: epiplexity (Finzi et al. 2026, preprint) -- ordering
     dependence and computation-created information; resource-bounded Kolmogorov / PRG theory.
  3. Memory-bounded learning complexity: Raz (2016), Garg-Raz-Tal (2018), Sharan-Sidford-Valiant
     (2019) -- explicit memory x sample trade-offs.
  4. Computationally-bounded sequence prediction: Sharan-Kakade-Liang-Valiant (2018) -- short windows
     suffice on average; tractable learners need d^Theta(log n/eps) samples.
  5. Computational-statistical gaps: Berthet-Rigollet (2013), SQ lower bounds (Kearns 1998);
     trade in the reverse direction (more data buys cheaper computation): Chandrasekaran-Jordan (2013).
  6. Learner-relative sample complexity under nuisance: Ng (2004) rotational-invariance lower bound.
  7. Non-monotonicity as a learner property: Nakkiran (2019), Loog et al. (2019), with the
     monotonization theorem (Bousquet et al. 2022) showing it is not forced by the data.
  8. Misspecified Bayes: Grunwald-van Ommen (2017) -- more data hurts a Bayesian with the wrong model.
- Honest gap: no single framework unifies (i) rate/memory, (ii) compute time, (iii) sample size into
  one "accessible information" quantity with matching upper and lower bounds. V-information handles
  predictor class but not memory; Raz-type bounds handle memory but not a general predictor class;
  epiplexity handles time but is new and unvalidated. A synthetic-world study can be positioned
  exactly in this gap.

### (c) Cheap experimental discriminators for a synthetic-world memory study

Design principle: in a synthetic world the Bayes-optimal predictor, the causal states, C_mu, E and
I_pred(T) are computable exactly, so every learner can be scored as (loss - Bayes loss) and
(retained bits - minimal sufficient bits). Report both against a constant/marginal twin.

D1. Sufficiency-class ladder (world family indexed by what is provably sufficient):
    - W0 iid: nothing needs to be retained (sufficient stat = empty).
    - W1 exchangeable with unknown parameter (e.g., Bernoulli with unknown p, Dirichlet-categorical):
      counts are sufficient; I_pred grows as (K/2) log T (Bialek et al. 2001). Exact history is
      never needed; any retained ordering information is nuisance.
    - W2 order-k Markov: last k symbols sufficient (finite window).
    - W3 finite unifilar HMM with long memory (e.g., Even process, golden mean): finite causal state
      sufficient, but NO finite window is (Even process is infinite-order Markov). Separates
      "statistic" learners from "window" learners.
    - W4 nonunifilar HMM (e.g., simple nonunifilar source): belief-state (mixed state) sufficient,
      C_mu large or divergent (Jurgens-Crutchfield 2021; contested by Grassberger) -- a finite
      approximate information state is needed (Subramanian et al. 2022).
    - W5 key-value / long-tail recall world: future queries ask for arbitrary earlier items; the
      sufficient statistic grows linearly with time, i.e., exact history (or its content-addressable
      subset) is provably necessary (Feldman 2020 style).
    Prediction to test: a learner that discards to a fixed-size statistic wins on W1-W3 and must lose
    on W5; a verbatim-store learner is flat across all and loses only if retrieval/readout is bounded.

D2. Truncation curve with an exact oracle: for W2/W3 vary memory window L or state budget; measure
    h(L) - h_mu and cumulative excess (Crutchfield-Feldman 2003). The shape identifies which world
    class a learner has effectively assumed. Check Sharan et al.'s I/eps window bound on W3.

D3. Nuisance-dimension dial: append k iid irrelevant bits to observations (or rotate them into the
    signal with a random orthogonal map). Bayes loss is invariant in k. Predictions: rotationally
    invariant learners' sample complexity grows ~linearly in k; sparse/L1/Winnow-type grows ~log k
    (Ng 2004; Littlestone 1988). Axis-aligned vs rotated nuisance with equal Shannon content is a
    direct "available vs accessible" test (V-information differs, I does not).

D4. Pseudorandom world: next symbol = PRG(seed, history). Shannon: history is sufficient and the
    world is nearly deterministic; bounded learner: indistinguishable from noise. Pair with an
    identical-statistics world using true randomness. If a learner's retained-information metric
    differs between them, the metric is measuring accessible structure (epiplexity/V-info), not
    Shannon information. Also permute data ORDER with fixed content to test Finzi et al.'s
    ordering-dependence claim.

D5. Memory-capped streaming parity (Raz 2016): n-bit hidden parity, stream (a, <a,x> mod 2); cap
    learner memory above/below ~n^2/25 bits. Predicted cliff in samples-to-solve at the threshold.
    Cheap at n = 10-20. Demonstrates retention NECESSARY for efficiency.

D6. Sample-wise sweep at fixed capacity: plot test loss vs n for each learner with the Bayes curve
    and the constant twin; look for non-monotone regions (Nakkiran 2019). Include a monotonized
    wrapper (holdout-accept updates; Bousquet et al. 2022) as a control: if the wrapper removes the
    bump, the bump was a learner property, not an information property.

D7. Long-tail memorization test (Feldman 2020; Brown et al. 2021; Feldman-Kornowski-Lyu 2025):
    Zipfian subpopulations with singleton labels. Measure accuracy on rare classes vs bits retained
    about specific training items. Theory predicts required memorization decays with n; a learner
    that compresses aggressively should lose exactly on the tail.

D8. Locus-of-compression arms (same world, same budget): (i) compress at storage (keep a
    statistic), (ii) store verbatim and compress at retrieval (query-time summarization),
    (iii) store verbatim, restrict the predictor (readout family). Theory predicts (i) = (ii) = Bayes
    on W1-W3 at the sufficient rate; (i) < (ii) on W5; (iii) reveals V-information limits (D3/D4).

D9. Misspecification probe (Grunwald-van Ommen 2017): give a Bayesian learner a model class missing
    the true generator (e.g., fit order-k Markov to W3 Even process, or homoskedastic model to
    heteroskedastic data). Check whether loss increases with n and whether a tempered posterior fixes
    it. Separates "more info hurt" due to misspecification from "more info hurt" due to capacity.

D10. Crypticity control: choose two worlds with equal E but different C_mu (nonzero crypticity).
    A learner whose retained bits track E rather than C_mu cannot be an exact predictor on the
    cryptic world; a learner whose retained bits exceed C_mu is storing nuisance.

Cheap-to-compute exact quantities for all of the above: epsilon-machine by construction for
W2-W3; C_mu = H(stationary state dist); E by block-entropy convergence or closed form; Bayes
predictive via forward algorithm; belief-state entropy for W4; for W1, the Dirichlet-multinomial
posterior predictive. These give each discriminator a published answer key.

---------------------------------------------------------------------------------------------

## 9. Most decision-relevant findings (short)

1. Discarding is never necessary for the Bayes-optimal predictor. It is necessary only under an
   explicit budget (rate, memory, samples, compute) or a distribution-shift target. The minimal
   sufficient statistic / causal state is the exact lossless limit. [anchor facts: R/V-meta]
2. The generalization-relevant compression is of the HYPOTHESIS (information about the sample in
   the weights), not of the representation/stream. "Compression phase causes generalization" is
   refuted (Saxe et al. 2018 [V]); IB control is sufficient-for-a-bound but explicitly not necessary
   (Kawaguchi et al. 2023 [V]).
3. There are LOWER bounds on retained information: accurate learners must memorize task-irrelevant
   data when samples are few or long-tailed (Brown et al. 2021; Feldman-Kornowski-Lyu 2025 [V]),
   and memory-capped learners need exponentially more samples (Raz 2016 [V]).
4. "Available vs accessible" has formal objects: V-information (DPI fails) [V]; epiplexity
   (ordering-dependent; preprint) [V abstract]; the Sharan et al. 2018 short-memory theorem plus
   its computational lower bound [V]; Ng 2004 rotational-invariance nuisance cost [V]. No unified
   memory x time x sample theory exists.
5. Sample-wise non-monotonicity is a learner property (Nakkiran 2019 [V]) that can always be
   removed by wrapping (Bousquet et al. 2022 [V]); for Bayes it appears only under
   misspecification (Grunwald-van Ommen 2017 [V]).
6. Causal-state theory gives exact oracles (C_mu >= E; crypticity) for synthetic worlds, but the
   "uncountable causal states" line (Jurgens-Crutchfield) is contested by Grassberger [V].
