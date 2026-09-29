# PA -- Memory that matters (Selective Irreversibility) and Compression/Abstraction (Sagacity)

seat: Artemis (research backlog curator), charter Block D, prior-art pass.
date: 2026-09-27. Worktree read: /home/jcraig/Prometheus-worktrees/artemis-base-role (READ-ONLY; no repo
code or tests were run; this file is the only write).
internal evidence read: roles/Artemis/backlog/harvest/D5_older_lines.md (H-D5-01,02,05..10,13..24,34,41,49),
D1_program.md (H-D1-32,33,37..44,52,53,68), D3_new_lenses.md (H-D3-26..28,31..33,38,39,41,45,50..53,66),
programs/selective_irreversibility/ (README, HYPOTHESIS, FALSIFIERS, memo/PORTFOLIO_MEMO_2026-09-25.md) and
the directive s1-s4 (roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md).

VERIFICATION CONVENTION. "[web-checked]" = title/authors/claim re-confirmed by web search or fetch on
2026-09-27. "UNVERIFIED" = cited from background knowledge, not re-fetched this session; the bibliographic
facts are very likely right but the specific quantitative claim attributed to it must be re-checked before
anyone quotes it in a verdict. Do not cite an UNVERIFIED number as evidence (lesson of H-D5-41).

---------------------------------------------------------------------------------------------------------
## 1. Internal questions this pass serves (harvest ids)

CLUSTER A -- memory that matters / selective irreversibility
  Q-A1  Is the SI law's "requires" clause empirical at all, and does transient query-time contraction
        count as the required contraction? (H-D1-38; FALSIFIERS 12:40Z; H-D3-39)
  Q-A2  Is a selective advantage really selectivity, or inductive-bias match / reservoir size?
        (H-D1-39, H-D1-40, H-D3-31)
  Q-A3  Is selectivity causally required -- intervene on it inside a competent system?
        (H-D3-32, H-D3-45, H-D1-41; FALSIFIERS "MISSING FALSIFIER by mechanism")
  Q-A4  Why do self-signal (surprise/residual) eviction rules lose to random? (H-D3-33; H-D5-23)
  Q-A5  Is the relevance-blind control really blind (recency, distribution matching)? (H-D1-68)
  Q-A6  One ruler for "memory kept and used": Cosmos P1/P2, Ensorain LM01, Ananke SI01, DSA.
        (H-D3-66, H-D3-26, H-D3-28, H-D3-41, H-D1-42, H-D1-43, H-D1-44)
  Q-A7  Label-free, self-generated evaluation of a memory index. (H-D5-24, H-D1-37, H-D5-25)
  Q-A8  When does retention pay (a pressure law)? capacity vs order? (H-D3-27, H-D5-23, H-D1-52)
  Q-A9  Is richer failure memory signal or exhaust? (H-D5-05, 06, 09, 10)

CLUSTER B -- compression / abstraction / sagacity
  Q-B1  Does a compact handle causally increase downstream reachability, or only describe what worked?
        (H-D5-02 -- THE sagacity anchor; H-D5-13, H-D5-34)
  Q-B2  Reinjection: does handing the handle to a receiver improve it vs a random-name control?
        (H-D5-08, H-D5-07, H-D1-53)
  Q-B3  Are learned libraries on the causal path, or decoration? (H-D5-17, 18, 19, 20, 22; H-D1-32, 33)
  Q-B4  Library-learning family choice and automated vocabulary growth (H-D5-14, 15, 16, 21)
  Q-B5  Search leverage vs recursion; bounded RSI; the misattributed plateau (H-D3-50, 51, 53; H-D5-41)
  Q-B6  Whole-program behavioural identity as the enabler of abstraction (H-D3-52)
  Q-B7  Representation ceiling vs mechanism ceiling: state injection (H-D5-49), structure discovery
        failure (H-D3-38), ecology-minted ceilings (H-D5-13)
  Q-B8  Inheritance unit and whole-stack ablation (H-D5-01, H-D5-05)

---------------------------------------------------------------------------------------------------------
## 2. Terminology map (external term  <->  Prometheus term / harvest id)  -- terms Prometheus lacks marked *

  * causal states / epsilon-machine (computational mechanics): the coarsening of histories into classes
    with identical conditional futures; the MINIMAL SUFFICIENT STATISTIC of the past for the future.
    <-> "eliminate distinctions that stop mattering" (SI s1). Gives a GENERATOR-derived, non-circular
    relevance partition (memo 11b). Also: statistical complexity C_mu, excess entropy E, crypticity.
  * predictive information I_pred(T) (Bialek-Nemenman-Tishby): mutual info between past and future
    windows; its growth with T classifies world complexity. <-> "changing environments" / memo 11a
    "measured positive entropy rate" (use entropy rate h_mu AND E, not h_mu alone).
  * nonpredictive information I_mem - I_pred (Still et al.): memory that does not help predict; equals
    (in their setting) dissipated work. <-> "irrelevant accessible state" in s4D; a label-free memory
    inefficiency score for H-D5-24.
  * information bottleneck (IB), IB curve, beta; deterministic IB; squared-IB. <-> "relevance-selective
    contraction". Directive s1 says the law is "broader than IB" -- IB is the special case where the
    relevance variable is given.
  * rate-distortion, distortion measure, policy compression (Lai & Gershman) <-> bounded memory budget
    B in WTP; "coarse-grained representation".
  * state abstraction hierarchy (Li-Walsh-Littman: model-irrelevance, Q*-irrelevance, pi*-irrelevance);
    bisimulation metrics; MDP homomorphism. <-> "distinctions relevant to control" (SI s1 "prediction
    AND control" are two different sufficiency notions -- the law does not say which).
  * predictive state representation (PSR) <-> memory defined by future tests, not stored past.
  * Landauer bound; logical vs thermodynamic irreversibility; Bennett compute-copy-uncompute;
    reversible pebble game; Lange-McKenzie-Tapp space-preserving reversible simulation <-> countermodel A.
  * fading memory property; memory capacity MC; information processing capacity IPC (Dambre)
    <-> "memory capacity, not retention order" (H-D5-23); reservoir size curve (H-D1-40).
  * catastrophic forgetting / stability-plasticity; loss of plasticity; primacy bias; resets
    <-> "forgetting as a feature"; SI elimination half.
  * complementary learning systems (CLS), consolidation, replay <-> persistent vs transient contraction.
  * reservoir sampling = distribution matching (a strong baseline, NOT a null) <-> "random eviction".
  * noisy-TV problem; aleatoric vs epistemic uncertainty; collective outliers; learning progress /
    compression progress <-> "surprise-driven eviction keeps noise" (H-D3-33).
  * causal abstraction; interchange intervention (II); interchange intervention accuracy (IIA);
    distributed alignment search (DAS); alignment map; amnesic probing / INLP; activation patching
    <-> Cosmos "state interchange" certificate (H-D3-66), DSA, SI01-REQ anti-merge.
  * MDL, two-part code, PREQUENTIAL code (online codelength) <-> "label-free evaluation" (H-D5-24),
    compression of FUTURE data rather than of what worked (H-D5-02).
  * Kolmogorov structure function; algorithmic sufficient statistic; sophistication; effective
    complexity; LOGICAL DEPTH (Bennett) <-> sagacity "compact handle -> much richer lesson" (a short
    handle whose unfolding is computationally deep is exactly a high-depth object).
  * Levin search / OOPS (Optimal Ordered Problem Solver) <-> reachability: a primitive that shortens a
    solution by k bits speeds Levin search by ~2^k -- a quantitative bridge from compression to reach.
  * library learning, refactoring, anti-unification, lambda abstraction, e-graph rewrite discovery
    (babble), compression objective, "single-use library" <-> Crius reuse, H-D5-15..22.
  * AutoDoc / naming of abstractions <-> handle FORMAT (H-D5-07); random-name control (H-D5-08).
  * knowledge distillation; FIDELITY vs generalization; machine teaching; teaching dimension;
    iterated learning / transmission bottleneck <-> reinjection (H-D5-08), inheritance of experience.
  * compositionality vs transmissibility (emergent communication) <-> "a handle a receiver reconstructs".
  * oracle / privileged-state ablation; perception-reasoning decomposition <-> state injection (H-D5-49).
  * compute-matched baseline; test-time-compute confound <-> H-D5-17, H-D5-41, H-D3-53.

---------------------------------------------------------------------------------------------------------
## 3. Key works (20)

Format: citation | URL | relevance | VERDICT on harvest ids.

W01. Tishby, Pereira, Bialek (1999/2000) "The information bottleneck method." arXiv physics/0004057.
     https://arxiv.org/abs/physics/0004057  (UNVERIFIED -- not re-fetched; canonical)
     Relevance: formal "keep only what predicts Y". The SI directive defines itself against it.
     REFRAMES H-D1-38: IB requires a GIVEN relevance variable Y; the SI law's content is that the
     system finds Y itself under a bounded, changing world -- that is the only part IB does not already
     prove. SUPPORTS memo 11a ("elimination half is a theorem"): for fixed Y, lossy contraction is
     optimal by construction, so it cannot be evidence.

W02. Bialek, Nemenman, Tishby (2001) "Predictability, complexity, and learning." Neural Computation
     13:2409. https://arxiv.org/abs/physics/0007070  (UNVERIFIED)
     Relevance: predictive information I_pred(T) is sub-extensive; everything else in the past is
     useless for the future. Its growth rate (bounded / log T / power law) classifies worlds.
     REFRAMES memo 11a: "changing environment" should be operationalised as I_pred(T) growth class, not
     just positive entropy rate -- a high-entropy i.i.d. world has h>0 but zero I_pred, and there the law
     is trivially true (keep nothing). SUPPORTS H-D3-27 (P3 "when retention pays" = when I_pred is large).

W03. Still, Sivak, Bell, Crooks (2012) "Thermodynamics of prediction." PRL 109:120604.
     https://arxiv.org/abs/1203.3271  [web-checked]
     Relevance: a driven system's state retains info about past input; the NONPREDICTIVE part equals
     (bounds) dissipated work; any maximally efficient memory must be predictive.
     SUPPORTS the SI law's direction in physical substrates, but REFRAMES it: the cost is paid for
     retaining irrelevant info, not for erasing it -- so "selectivity" and "efficiency" are one quantity.
     Gives H-D5-24 a label-free score (I_mem - I_pred from trajectories alone).

W04. Shalizi & Crutchfield (2001) "Computational mechanics: pattern and prediction, structure and
     simplicity." J. Stat. Phys. 104:817. https://arxiv.org/abs/cond-mat/9907176  (UNVERIFIED)
     Relevance: causal states are the unique minimal sufficient statistic of past for future.
     REFRAMES H-D3-45/H-D1-42 (DSA): the R/E/N distinction classes can be DERIVED from the generator's
     causal-state partition instead of hand-labelled; SUPPORTS memo 11b's demand that relevance come from
     the generator. CONTRADICTS reading H-D1-44 C-CORE conservation as relevance (conserved != in the
     causal-state partition).

W05. Lange, McKenzie, Tapp (2000) "Reversible space equals deterministic space." JCSS 60(2):354.
     https://www.sciencedirect.com/science/article/pii/S0022000099916720  [web-checked]
     with Bennett (1973) "Logical reversibility of computation" and Bennett (1989) "Time/space trade-offs
     for reversible computation" (UNVERIFIED, not re-fetched).
     Relevance: ANY S-space deterministic computation can be simulated reversibly in O(S) space, at
     exponential time; Bennett's method needs more space but polynomial time.
     CONTRADICTS a pure-space reading of the SI "requires" clause (H-D1-38, countermodel A): with time
     unpriced, a bounded reversible agent CAN avoid elimination in principle. The law is only non-trivial
     as a TIME-SPACE (throughput/latency) frontier claim. This is the single most important theoretical
     constraint found in this pass; it should go into the Harmonia s12 freeze.

W06. Saxe et al. (2018/2019) "On the information bottleneck theory of deep learning." ICLR 2018;
     J. Stat. Mech. 124020. https://artemyk.github.io/assets/pdf/papers/Saxe%20et%20al_2018_ICLR.pdf
     [web-checked]
     Relevance: the "compression phase" appears only with double-saturating nonlinearities and binning
     MI estimators; networks generalise without compressing and vice versa.
     CONTRADICTS any claim that observed contraction is what CAUSES generalisation (H-D3-32, H-D1-39);
     SUPPORTS H-D1-40 (the effect may be estimator/architecture, not selectivity).

W07. Kolchinsky, Tracey, Van Kuyk (2019) "Caveats for information bottleneck in deterministic
     scenarios." ICLR 2019. https://arxiv.org/abs/1808.07593  [web-checked]
     Relevance: when Y is a deterministic function of X, the IB Lagrangian cannot trace the IB curve and
     trivial solutions exist at every point.
     REFRAMES all SI experiments in DETERMINISTIC worlds (Z80, TINYPROG, many PTE tasks): IB-style
     "relevant vs irrelevant" readings are degenerate unless the world injects noise or the relevance
     variable is stochastic. Pitfall for H-D3-45 and WTP.

W08. Isele & Cosgun (2018) "Selective experience replay for lifelong learning." AAAI.
     https://ojs.aaai.org/index.php/AAAI/article/view/11595  [web-checked]
     Relevance: compared surprise-, reward-, distribution-matching- and coverage-based retention for a
     long-term buffer: surprise and reward selection show catastrophic forgetting; distribution matching
     (reservoir) is consistently best; coverage helps when rare tasks matter.
     SUPPORTS H-D3-33 as a KNOWN result (not an anomaly); REFRAMES H-D1-68: "random" eviction is
     distribution matching, i.e. a strong structured policy, not a relevance-blind null.

W09. Karamcheti, Krishna, Fei-Fei, Manning (2021) "Mind your outliers! ..." ACL 2021.
     https://arxiv.org/abs/2107.02331  [web-checked]
     Relevance: 8 uncertainty-driven acquisition methods fail to beat random across 5 models x 4 datasets;
     cause = COLLECTIVE OUTLIERS the model prefers but cannot learn. Removing them restores the gain.
     SUPPORTS H-D3-33 mechanism ("surprise retains unlearnable/noisy records"); gives a diagnostic
     (per-record learnability map) for LM01's eviction arms.

W10. Chaudhry et al. (2019) "On tiny episodic memories in continual learning."
     https://arxiv.org/abs/1902.10486  [web-checked]
     with Prabhu, Torr, Dokania (2020) GDumb (UNVERIFIED, not re-fetched).
     Relevance: a tiny reservoir-sampled replay buffer beats purpose-built CL methods.
     SUPPORTS H-D5-23 (capacity, not clever order) and H-D1-40 (competence tracks retained exact
     records); CONTRADICTS expecting a large selectivity effect at moderate caps.

W11. Geiger, Wu, Icard, Potts, Goodman et al. (2025) "Causal abstraction: a theoretical foundation for
     mechanistic interpretability." JMLR 26. https://arxiv.org/abs/2301.04709  [web-checked]
     plus Geiger et al. (2022) "Inducing causal structure..." (interchange intervention training)
     https://arxiv.org/abs/2112.00826 (UNVERIFIED).
     Relevance: interchange intervention = swap a component's value from a source run into a base run,
     check the high-level model predicts the outcome; IIA grades faithfulness. Unifies patching,
     causal scrubbing, concept erasure, DAS.
     SUPPORTS H-D3-66: this is the common language for Cosmos state interchange, SI01-REQ anti-merge and
     DSA -- a memory certificate = "an abstract variable M exists with high IIA across the history
     boundary".

W12. Sutter, Minder, Hofmann, Pimentel (2025) "The non-linear representation dilemma: is causal
     abstraction enough for mechanistic interpretability?" NeurIPS 2025.
     https://arxiv.org/abs/2507.08802  [web-checked]
     Relevance: with unrestricted (non-linear) alignment maps, ANY network can be mapped to ANY
     algorithm -- causal abstraction becomes vacuous without a restriction on the map class.
     CONTRADICTS using interchange/state-swap certificates without a frozen, priced alignment-map class
     (H-D3-26 P1 "own readout probe", H-D3-66). Also Makelov et al. (2023) "Is this the subspace you are
     looking for? An interpretability illusion for subspace activation patching"
     https://arxiv.org/abs/2311.17030 (UNVERIFIED).

W13. Elazar, Ravfogel, Jacovi, Goldberg (2021) "Amnesic probing." TACL 9.
     https://arxiv.org/abs/2006.00995  [web-checked]
     Relevance: decodable != used; remove the property (INLP nullspace projection) and measure behaviour.
     SUPPORTS H-D5-49 (represented vs computed dissociation) and H-D5-25 (agreement of geometries is not
     use); a ready-made "memory used" test pattern.

W14. Ellis et al. (2021) "DreamCoder." PLDI. https://arxiv.org/abs/2006.08381 (UNVERIFIED);
     Bowers et al. (2023) "Top-down synthesis for library learning" (Stitch), POPL.
     https://mlb2251.github.io/stitch.pdf  [web-checked]; Cao et al. (2023) "babble: learning better
     abstractions with e-graphs and anti-unification," POPL, https://arxiv.org/abs/2212.04596 (UNVERIFIED).
     Relevance: the compression-selected library canon. DreamCoder's objective is a Bayesian prior over
     programs (MDL of the solved corpus); Stitch is orders of magnitude faster at the same compression
     objective. All three SELECT abstractions by compression of PAST solutions.
     REFRAMES H-D5-02: this canon never tests whether a selected abstraction directs FUTURE acquisition;
     it is exactly the "describes what worked" arm. H-D1-32: Stitch can emit arity>0 abstractions only
     if >=2 programs share a pattern with differing sub-terms -- on 17 programs of 2-4 nodes the
     attainable set is plausibly near-empty (compute it before calling the null).

W15. Grand et al. (2024) "LILO: learning interpretable libraries by compressing and documenting code."
     ICLR. https://arxiv.org/abs/2310.19791  [web-checked]
     Relevance: naively giving an LLM the Stitch abstractions (anonymous fn_42) MEASURABLY DEGRADED task
     solving; AutoDoc (names + docstrings) made the same abstractions usable.
     SUPPORTS H-D5-07 (handle format matters) and H-D5-08 (reinjection needs a random-name AND a
     no-doc control): a compact handle without a decoder can be negative value. Direct evidence that
     "sagacity" is a property of the handle-receiver pair, not the handle.

W16. Berlot-Attwell, Rudzicz, Si (2024) "Library learning doesn't: the curious case of the single-use
     'library'." NeurIPS MATH-AI workshop. https://arxiv.org/abs/2410.20274  [web-checked]
     + Berlot-Attwell et al. (2025) "LLM library learning fails: a LEGO-Prover case study."
     https://arxiv.org/abs/2504.03048  [web-checked]
     + Sesterhenn, Berlot-Attwell, Zenkner, Bartelt (2025) "A compute-matched re-evaluation of TroVE on
     MATH." https://arxiv.org/abs/2507.22069  [web-checked]
     Relevance: reuse in LEGO-Prover and TroVE is extremely infrequent; gains come from self-correction /
     self-consistency; compute-matched, TroVE's benefit shrinks to ~1% and LEGO-Prover's disappears.
     SUPPORTS H-D5-17, H-D5-18 (decoration), H-D3-53 (leverage without recursion); CONTRADICTS reading
     Archaeon "direct reuse 0.06-0.60" or Aphrodite S3 as reuse-driven without leave-one-out + compute
     matching. Note the internal H-D5-17 quote came via an external DR report; these three are the
     primary sources to cite instead.

W17. Stanton, Izmailov, Kirichenko, Alemi, Wilson (2021) "Does knowledge distillation really work?"
     NeurIPS. https://arxiv.org/abs/2106.05945  [web-checked]
     Relevance: students often fail to match teachers even with enough capacity (optimisation, not
     capacity); in self-distillation generalisation improves BECAUSE fidelity is low.
     REFRAMES H-D5-08/H-D1-53: a reinjection null can be a RECEIVER-optimisation failure, and a
     reinjection "win" can come from regularisation rather than transmitted content -- measure fidelity
     (does the receiver reproduce the donor's behaviour on the lesson's domain) separately from gain.

W18. Chaabouni, Kharitonov, Bouchacourt, Dupoux, Baroni (2020) "Compositionality and generalization in
     emergent languages." ACL. https://aclanthology.org/2020.acl-main.407/  [web-checked]
     + Kirby, Cornish, Smith (2008) "Cumulative cultural evolution in the laboratory." PNAS 105:10681.
     https://www.pnas.org/doi/10.1073/pnas.0707835105  [web-checked]
     Relevance: compositionality is NOT correlated with the sender's generalisation but DOES make a
     language easier for NEW learners (even of different architecture); iterated transmission through a
     learning bottleneck makes languages more learnable and structured without a designer.
     REFRAMES the North Star definition: sagacity (handle -> receiver reconstructs the lesson) is a
     TRANSMISSION property measurable only with a fresh receiver, and can be selected for by a
     transmission bottleneck. SUPPORTS H-D5-08 as the right test; CONTRADICTS using the donor's own
     performance (Aphrodite S3/S4) as the sagacity measure.

W19. Blier & Ollivier (2018) "The description length of deep learning models." NeurIPS.
     https://arxiv.org/abs/1802.07044  [web-checked]
     + Schmidhuber (2009) "Driven by compression progress." https://arxiv.org/abs/0812.4360 [web-checked]
     Relevance: prequential (online) codelength charges a learner for predicting each next datum before
     training on it -- compression of the FUTURE, which correlates with test performance better than
     variational codelengths. Compression PROGRESS (first derivative) as the intrinsic signal for what
     to learn next; avoids the noisy-TV trap because noise yields no progress.
     SUPPORTS H-D5-24 (label-free, self-generated criterion) and gives H-D5-02 its operational form:
     a handle "tells what to acquire next" iff it raises predicted compression progress on unsolved
     tasks. Also the principled fix for H-D3-33 (evict by lack of learning progress, not by surprise).

W20. Recursive self-improvement evidence:
     Zelikman et al. (2024) "Self-Taught Optimizer (STOP)." COLM. https://arxiv.org/abs/2310.02304
     [web-checked]; Yin et al. (2025) "Godel Agent." ACL. https://arxiv.org/abs/2410.04444 [web-checked];
     Zhang, Hu, Lu, Lange, Clune (2025) "Darwin Godel Machine." https://arxiv.org/abs/2505.22954
     [web-checked]; Novikov et al. (2025) "AlphaEvolve" (UNVERIFIED id; do NOT reuse the plateau figure
     -- H-D5-41 found it misattributed to DeepMind).
     Relevance: STOP improves the improver for a few rounds on a fixed LM (with weaker LMs the recursion
     reportedly degrades -- UNVERIFIED detail); DGM uses an open-ended ARCHIVE of self-modified agents and
     reports gains on SWE-bench / Polyglot (exact numbers UNVERIFIED); none of these is a
     compute-matched, >3-round compounding demonstration.
     SUPPORTS H-D5-41 and H-D3-53 (leverage != recursion); REFRAMES H-D3-50: DGM's key design element is
     the archive of stepping stones (open-endedness), i.e. task/agent SUPPLY -- consistent with
     Aphrodite's "binding constraint is family SUPPLY" (H-D3-51).

Additional supporting works (cited in pitfalls/tests; all UNVERIFIED unless marked):
  - Dambre, Verstraeten, Schrauwen, Massar (2012) "Information processing capacity of dynamical
    systems." Sci Rep 2:514. https://www.nature.com/articles/srep00514 [web-checked]. Total capacity is
    bounded by the number of linearly independent state variables (equality under fading memory): a
    memory-nonlinearity trade-off. SUPPORTS H-D5-23 (capacity is the first-order variable) and gives
    Ensorain/Cosmos a substrate-agnostic capacity ruler. Jaeger (2002) short-term memory in ESNs; Ganguli,
    Huh, Sompolinsky (2008) "Memory traces in dynamical systems" PNAS.
  - Huang, Zhang, Shan, He (2024) "Compression represents intelligence linearly." COLM.
    https://arxiv.org/abs/2404.09937 [web-checked]; Deletang et al. (2024) "Language modeling is
    compression." ICLR, https://arxiv.org/abs/2309.10668. Support "compression ~ capability" ACROSS
    models trained on similar data; confounded by scale. Chollet (2019) "On the measure of intelligence"
    https://arxiv.org/abs/1911.01547 is the standard critique (skill != intelligence; priors+experience
    must be controlled).
  - Burda et al. (2019) "Large-scale study of curiosity-driven learning" (noisy-TV)
    https://arxiv.org/abs/1808.04355; Oudeyer, Kaplan, Hafner (2007) "Intrinsic motivation systems for
    autonomous mental development" (learning progress). Toneva et al. (2019) "An empirical study of
    example forgetting" https://arxiv.org/abs/1812.05159 (never-forgotten examples can be dropped).
  - Kirkpatrick et al. (2017) EWC https://arxiv.org/abs/1612.00796; Dohare et al. (2024) "Loss of
    plasticity in deep continual learning" Nature; Nikishin et al. (2022) "The primacy bias in deep RL"
    https://arxiv.org/abs/2205.07802; Zhou et al. (2022) "Fortuitous forgetting" https://arxiv.org/abs/2202.00155;
    Richards & Frankland (2017) "The persistence and transience of memory" Neuron 94:1071; Anderson &
    Schooler (1991) "Reflections of the environment in memory" Psych. Sci. -- forgetting as a feature:
    resets/forgetting restore plasticity and generalisation; forgetting curves mirror environmental
    need-probability (i.e. recency IS relevance in natural environments -> H-D1-68).
  - McClelland, McNaughton, O'Reilly (1995) complementary learning systems; Kumaran, Hassabis,
    McClelland (2016) update. Fast exact episodic store + slow consolidated abstraction = the biological
    answer to "lossless vs coarse" is BOTH, with replay moving content between them (countermodel B is
    half of the standard model, not a rival).
  - Sims (2018) "Efficient coding explains the universal law of generalization in human perception."
    Science 360:652; Lai & Gershman (2021) "Policy compression." Rate-distortion accounts of cognition.
  - Li, Walsh, Littman (2006) "Towards a unified theory of state abstraction for MDPs." ISAIM; Givan,
    Dean, Greig (2003) bisimulation. The prediction-sufficient vs control-sufficient distinction.
  - Vereshchagin & Vitanyi (2004) "Kolmogorov's structure functions and model selection." IEEE TIT;
    Bennett (1988) "Logical depth and physical complexity." Schmidhuber (2004) "Optimal ordered problem
    solver." Machine Learning 54:211.
  - Wong et al. (2021) LAPS https://arxiv.org/abs/2106.11053; Wang et al. (2023) Voyager
    https://arxiv.org/abs/2305.16291 (reports a skill-library ablation in favour of the library --
    one of few positive reuse ablations; compute matching not checked).
  - Hu, Lu, Clune (2024) ADAS https://arxiv.org/abs/2408.08435.

---------------------------------------------------------------------------------------------------------
## 4. Pitfalls (each tied to where Prometheus is exposed)

P1. REVERSIBLE-IN-PRINCIPLE (W05). With time free, countermodel A wins by theorem (LMT 2000). If the
    freeze prices only bytes, the law is either false or saved only by a hidden time assumption. Price
    ops/tick and latency explicitly (memo 11e covers exports but not time). -> H-D1-38, H-D1-41.
P2. QUERY-TIME CONTRACTION = BENNETT UNCOMPUTE. L-R (exact store + transient refit per query) is the
    agent-level analogue of compute-copy-uncompute. Deciding by definition whether it "counts" is the
    post-hoc-retreat trap; deciding by per-query compute scaling is not (see T2). -> H-D1-38, H-D3-39.
P3. IB ESTIMATOR / DETERMINISM ARTEFACTS (W06, W07). Binned MI shows compression that is not there;
    deterministic Y makes IB degenerate. Any MI-based selectivity readout needs a known-answer fixture
    (the stewards already learned this: FALSIFIERS 00:45Z) and noise in the relevance variable.
P4. "RANDOM" IS NOT BLIND (W08, W10, Anderson-Schooler). Reservoir random eviction = distribution
    matching; FIFO = recency, which correlates with need-probability in natural streams. The blind
    control must be relevance-blind BY CONSTRUCTION w.r.t. the generator's causal-state partition, and
    its selectivity measured, not assumed. -> H-D1-68, H-D3-33.
P5. SURPRISE RETAINS NOISE (W08, W09, noisy TV). Residual-driven retention ranks aleatoric noise and
    unlearnable collective outliers highest. H-D3-33 is the expected result, not an anomaly; the repair
    is learning-progress or epistemic-only (ensemble-disagreement) scoring.
P6. CAPACITY DOMINATES ORDER (W10, Dambre). Selectivity effects are second-order at moderate caps; a
    reservoir-size curve can masquerade as a selective/lossless contrast (H-D1-40). Always sweep capacity
    first (H-D5-23).
P7. VACUOUS CAUSAL ABSTRACTION (W12). An interchange certificate with a flexible or system-chosen
    alignment map (Cosmos P1 "own readout probe") can certify anything; with a too-narrow map it misses
    in-flight memory (Ananke M2, H-D3-41). Freeze and price the map class; report IIA vs map complexity.
P8. DECODABLE != USED (W13). Geometry agreement (Mantel r=0.94, H-D5-25) and probe accuracy say nothing
    about use; require an amnesic/ablation counterfactual.
P9. SINGLE-USE LIBRARY / COMPUTE CONFOUND (W16). Gains attributed to libraries often come from extra
    sampling, self-consistency or retries. Requires usage census + leave-one-out mask + compute-matched
    no-library arm. -> H-D5-17, 18, H-D3-53, Archaeon campaign2.
P10. ANONYMOUS HANDLES HURT (W15). A reinjection arm that passes bare fn_N handles can be negative;
    a named/doc'd arm can win on the name's LANGUAGE prior, not the abstraction. Need both a
    random-name control and a scrambled-body-same-name control. -> H-D5-07, H-D5-08.
P11. FIDELITY vs GAIN (W17). Receiver improvement after reinjection may be regularisation; receiver
    failure may be optimisation. Report fidelity to the donor on the lesson domain separately.
P12. SPEED vs CEILING. Almost every positive in library learning and RSI is speed (search leverage). A
    ceiling claim needs tasks unsolved at k x budget without the handle (H-D5-13, H-D5-34, H-D3-53).
P13. COMPRESSION-INTELLIGENCE CORRELATIONS ARE CROSS-MODEL (Huang; Deletang). They do not show that
    compressing MORE within one system causes capability; Chollet's priors-and-experience objection
    applies to any "compact = smart" metric.
P14. RETRIEVAL COUNTERFEIT (H-D5-19) has an external twin: "rediscovery" of a library already in the
    LLM prior (LILO/LEGO-Prover). Any endogenous-abstraction claim needs a no-prior or scrambled-prior arm.
P15. MISATTRIBUTED CITATIONS (H-D5-41). Do not cite the AlphaEvolve plateau; RSI numbers from blogs and
    DR reports must be checked against the primary paper.

---------------------------------------------------------------------------------------------------------
## 5. Usable code (not run here; check licences before vendoring -- H-D5-21 records Stitch licence as unresolved)

  stitch (Rust) + stitch_core (PyPI)   https://github.com/mlb2251/stitch ; https://pypi.org/project/stitch-core/
        compression-based library learning; fastest option; licence UNVERIFIED in this pass.
  DreamCoder (ec)                     https://github.com/ellisk42/ec  (UNVERIFIED URL/licence) heavy, OCaml+Python.
  LILO                                https://github.com/gabegrand/lilo  (UNVERIFIED URL) Stitch + AutoDoc.
  babble                              https://github.com/dcao/babble  (UNVERIFIED URL) e-graph library learning;
                                      the Family-B option of H-D5-21.
  pyvene                              https://github.com/stanfordnlp/pyvene  (UNVERIFIED URL) interchange
                                      interventions / DAS for torch models; for non-torch engines, reimplement
                                      the II loop (it is small) on the H-D1-43 replay-and-perturb hook.
  INLP / amnesic probing              https://github.com/shauli-ravfogel/nullspace_projection (UNVERIFIED URL).
  dit                                 https://github.com/dit/dit ; docs https://dit.readthedocs.io/ [web-checked]
                                      discrete info theory incl. rate-distortion module (IB support
                                      UNVERIFIED); excess entropy, PID. Use for known-answer fixtures.
  Avalanche                           https://github.com/ContinualAI/avalanche (UNVERIFIED URL) reservoir,
                                      class-balanced, GSS replay buffers -- ready eviction baselines for LM01.
  reservoirpy                         https://github.com/reservoirpy/reservoirpy (UNVERIFIED URL) ESN memory
                                      capacity measurement.
  STOP                                https://github.com/microsoft/stop [web-checked]
  Darwin Godel Machine                https://github.com/jennyzzt/dgm [web-checked]
  Godel Agent                         https://github.com/Arvid-pku/Godel_Agent [web-checked]
  llm-compression-intelligence        https://github.com/hkust-nlp/llm-compression-intelligence [web-checked]
  Causal-state reconstruction (CSSR / transCSSR) -- implementations exist (UNVERIFIED which is maintained);
        for planted finite-state generators the epsilon-machine can be computed exactly by minimising the
        generator (Moore-style minimisation on predictive equivalence) -- no library needed.

---------------------------------------------------------------------------------------------------------
## 6. Genuinely unexplored (specific; most valuable). Novelty claims are UNVERIFIED beyond this pass's searches.

U1. CAUSAL-STATE-CALIBRATED DISTINCTION SURVIVAL. Plant finite-state (hidden-Markov) generators whose
    epsilon-machine is known exactly, run evolved/learned memories, and score each specimen's retained
    partition against the causal-state partition: refines it (keeps irrelevant distinctions), coarsens
    it (loses relevant ones), or matches. This turns SI's "relevant" into a generator theorem (memo 11b),
    gives DSA (H-D1-42) and SI01's R/E/N classes (H-D3-45) a ground truth, and makes countermodel C's
    control "merge uniformly across causal-state boundaries" exact. Computational mechanics has not
    (as far as searched) been used as a grading instrument for EVOLVED memory in ALife.

U2. THE TIME-SPACE FRONTIER VERSION OF THE LAW. Restate "requires" as: at fixed bytes AND fixed ops per
    tick, as I_pred horizon grows, every non-selective strategy (lossless+refit, reversible, blind loss)
    falls off the competence frontier. LMT/Bennett give the exact reversible trade-off curve to beat.
    No ALife or continual-learning work frames memory this way; it converts H-D1-38 from a definitional
    dispute into a measurable crossover.

U3. NONPREDICTIVE INFORMATION AS A LABEL-FREE MEMORY SCORE. Estimate I(state; past input) - I(state;
    future input) from logged trajectories (Still et al.) in a stochastic world. Needs no task labels,
    no author relevance, no probe -- answers H-D5-24's "criterion the system itself generates", and can
    be applied to Ananke M2's in-flight bit (H-D3-41) if in-flight packets are included in "state".

U4. HANDLES SELECTED BY TRANSMISSION, NOT COMPRESSION. Every library learner (W14-W16) selects by
    compression of its own corpus; iterated learning (W18) selects by learnability to a fresh learner.
    Nobody has run library learning where an abstraction survives only if a FRESH receiver, given it,
    reaches more held-out tasks (reinjection gain as the selection criterion). This is the literal
    North Star mechanism and it is unbuilt anywhere found.

U5. SAGACITY AS LOGICAL DEPTH PER BIT. Define a handle's sagacity = (receiver compute saved or reach
    gained on held-out tasks) / (handle length), with random-handle subtraction. High-depth, short
    handles are Bennett-deep objects. No empirical program measures depth-per-bit of transmitted
    abstractions; it would unify H-D5-02, H-D5-07 and H-D5-08 in one number.

U6. DIRECTIVE vs DESCRIPTIVE COMPRESSION (H-D5-02 exactly). Test whether the delta-description-length a
    handle induces on NOT-YET-SOLVED tasks (computed before search) predicts the ORDER in which tasks
    later become solved. DreamCoder's recognition model implicitly bets on this, but the prediction has
    never been scored as a forecast against a no-handle and random-handle baseline.

U7. LEARNING-PROGRESS EVICTION UNDER HETEROSCEDASTIC NOISE. The surprise-vs-random literature (W08-W10)
    is in supervised/RL buffers; the specific claim "surprise loses exactly where noise is
    heteroscedastic, learning-progress wins there and ties elsewhere" appears untested as a clean
    dose-response. LM01 dev already has the arms to test it (T3).

U8. PRICED-ALIGNMENT-MAP CERTIFICATE. After Sutter et al., a memory certificate should report IIA as a
    function of alignment-map complexity (identity-on-cells < linear < MLP) with a random-network
    baseline at each complexity. A cross-engine version on shared specimens (Cosmos planted, Ensorain
    reservoir, Ananke M2) would be H-D3-66's single ruler; not done anywhere found.

U9. SPEED-TO-CEILING CONVERSION. H-D3-53 (40% cheaper, nothing new) + OOPS/Levin theory predict that
    search leverage becomes reach only at the budget boundary where the handle-less search's 2^k cost
    exceeds budget. Nobody has measured the budget at which leverage turns into ceiling movement; it
    predicts WHICH tasks should flip, which is a sharp falsifier for H-D5-13.

---------------------------------------------------------------------------------------------------------
## 7. Cheapest discriminating tests

T1. H-D5-02 -- DOES A COMPACT HANDLE CAUSALLY INCREASE DOWNSTREAM REACHABILITY?
    Where: the Aphrodite DSL (G1 donor, PRISTINE arm and transplant machinery already exist; H-D3-52/53)
    or Aporia TINYPROG as fallback. No new substrate needed.
    Held-out set: partition held-out tasks BEFORE running into
      R0 = solved by PRISTINE at budget B;  R1 = unsolved by PRISTINE at 10B (the ceiling set).
      (Needs a task supply with a non-empty R1 -- fix H-D3-51's degenerate sampler first; if R1 is
      empty the test can only speak to speed and must say so.)
    Arms (same searcher, same seeds):
      A0 no handle, budget B          A0' no handle, budget B + cost of minting the handle (compute match)
      A1 learned handle H             A2 random-name control: same arity/type, body = random well-typed
                                         term of equal size (IQ-NULL generalised; H-D5-20)
      A3 scrambled-body H (same name/signature, permuted body)
      A4 retrieval-only memo of H's source witnesses, equal bytes (A3-attempt-two control, H-D1-33)
      A5 handle minted on a DIFFERENT family (bias-mismatch control, H-D1-39)
    Readouts: (i) reach = |R1 solved| at B; (ii) speed on R0; (iii) usage census: fraction of new
      solutions that call H (W16); (iv) leave-one-out: re-solve each H-using solution with H masked;
      (v) forecast score: rank R1 tasks by delta-DL under H computed before search; Spearman with
      actual solve order (U6).
    Decision: H is DIRECTIVE iff reach(A1) > max(A0', A2, A3, A4) on R1 with CI excluding zero, usage
      census > 0 on those wins, masking H removes them, and the forecast beats the A2 forecast. Speed-only
      wins (R0) are labelled LEVERAGE, never sagacity. Cost: one campaign of the existing size.
    Reinjection extension (H-D5-08, cheapest version): give H to a DIFFERENT searcher (another seed
      family or architecture) and rerun A1/A2/A3 there; report fidelity separately (W17). If H helps
      only its minting lineage, it is a local search bias, not a handle.

T2. H-D1-38 -- THE "REQUIRES" CLAUSE (does transient contraction count?).
    Replace the definitional question with a scaling test that needs only WTP-LM01 dev arms plus the
    op-meter the memo already lists as missing (s9):
      fix bytes B and a PER-QUERY op budget Q; sweep horizon / history length N (and I_pred growth class).
      Arms: L-K (exact store, unlearned readout), L-R (exact store + per-query refit), SELECTIVE ladder,
      rate-matched random merge (IM-rate reference, 00:45Z rule).
    Prediction if the law is true in its computation-inclusive form: L-R's ops/query grow with N, so at
      fixed Q it must either truncate (become a lossy, possibly blind, contraction -> countermodel C
      territory) or fall off; SELECTIVE holds competence at O(1) ops/query. A crossover N* exists and
      scales with Q.
    Falsifies the law's computation-inclusive form: L-R (or any lossless arm) stays on the competence
      frontier at fixed Q as N grows, with equivalence test + positive control (FALSIFIERS 21:04Z rule).
    This makes "transient contraction" count ONLY if it is affordable within Q -- a pricing rule, not a
      definition -- and closes the s4B unfalsifiability region on generalisation readouts. Must be put
      in the Harmonia s12 freeze BEFORE LM01 rows exist. Also add, from W05: the reversible arm (H-D1-41)
      is judged on the same (B, Q) frontier, since with Q unbounded it wins by theorem.
    Cheapest REQUIREMENT intervention (H-D3-32) compatible with this: mid-life, at matched bytes, replace
      the SELECTIVE arm's store with a causal-state-uniform random merge of the SAME experience (U1
      control), then continue; the Aporia 11:35Z "decided by construction" objection is avoided only if
      the post-swap readout is on future FRESH-field inputs after further learning, not an immediate
      lookup. UNVERIFIED that LM01 can resume from a swapped state; check the harness first.

T3. H-D3-33 -- WHY SURPRISE EVICTION LOSES.
    In LM01 dev (arms exist): add two eviction scores -- (a) learning progress = drop in a record's
      residual over the last k replays; (b) residual minus a noise-floor estimate from repeated
      observations of the same cell (or ensemble disagreement). Vary noise from homoscedastic to
      heteroscedastic at fixed mean noise. Predicted (W08, W09, noisy TV): residual-eviction loses to
      random only under heteroscedastic noise; (a)/(b) beat random there and tie elsewhere. If residual
      loses under homoscedastic noise too, the cause is not noise retention (new anomaly, file it).
    Also log, per retained record, a learnability flag (W09 dataset map) -- a one-line diagnostic.

T4. H-D5-49 -- STATE INJECTION (cheapest in any engine with a hand-writable representation):
    upper bound U_inj = competence with ground-truth state injected; baseline U_0; learned U_L. The
    split (U_inj - U_L) is the representation gap, (1 - U_inj) the mechanism gap. Pair with an amnesic
    arm (W13: remove the injected variable) to show it is used. Run on Ensorain E2 first: it directly
    answers whether H-D3-38's structure-discovery failure is perception or computation.

T5. H-D3-66 -- ONE MEMORY RULER, cheapest: pick ONE specimen visible to all three (a Cosmos planted
    system is public), run Cosmos P1/P2, an LM01-style exact-vs-coarse swap, and an SI01 R/E/N
    recoverability readout on it, each with the alignment-map class frozen and priced (U8, W12). Any
    disagreement is a finding about the instruments, not the specimen.

T6. H-D5-17/18 (hygiene, near-zero compute): usage census + leave-one-out mask + compute-matched arm on
    EXISTING Archaeon campaign2 and Aphrodite S3/S4 logs (reanalysis only; H-D1-51 style). Also compute
    for H-D1-32 the number of arity>0 anti-unifiers structurally available in the 17-program corpus;
    if ~0, reclassify C-06 as NOT TESTABLE on that corpus.

---------------------------------------------------------------------------------------------------------
## Sources (web-checked this pass)
https://arxiv.org/abs/2410.20274 ; https://arxiv.org/abs/2504.03048 ; https://arxiv.org/abs/2507.22069 ;
https://arxiv.org/abs/2507.08802 ; https://ojs.aaai.org/index.php/AAAI/article/view/11595 ;
https://arxiv.org/abs/2107.02331 ; https://arxiv.org/abs/1203.3271 ; https://arxiv.org/abs/2106.05945 ;
https://aclanthology.org/2020.acl-main.407/ ; https://arxiv.org/abs/2505.22954 ; https://github.com/dit/dit ;
https://artemyk.github.io/assets/pdf/papers/Saxe%20et%20al_2018_ICLR.pdf ; https://arxiv.org/abs/1808.07593 ;
https://arxiv.org/abs/1902.10486 ; https://arxiv.org/abs/2006.00995 ; https://arxiv.org/abs/2310.02304 ;
https://arxiv.org/abs/2410.04444 ; https://arxiv.org/abs/2404.09937 ; https://arxiv.org/abs/1802.07044 ;
https://www.pnas.org/doi/10.1073/pnas.0707835105 ; https://arxiv.org/abs/2310.19791 ;
https://arxiv.org/abs/2301.04709 ; https://www.nature.com/articles/srep00514 ; https://github.com/mlb2251/stitch ;
https://www.sciencedirect.com/science/article/pii/S0022000099916720 ; https://arxiv.org/abs/0812.4360
