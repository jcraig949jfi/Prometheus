# LIT: Memory systems -- exact storage + query-time readout vs compressed bounded state

Compiled 2026-09-28. Pure ASCII. Scope: 1967-2026, weighted to 2015-2026.

## 0. Legend and epistemic status

- [V] = claim checked this session against the paper's abstract, proceedings page, or a
  search snippet quoting it. It is still only as good as an abstract: numbers in the body
  of a paper were NOT re-read unless stated.
- [R] = recalled from prior knowledge, not re-checked this session. Treat [R] numbers as
  "probably right, cite only after checking".
- [R?] = recalled with low confidence. Check before use.
- "Readout" = the operator applied at query time to stored items (kNN vote, kernel
  smoother, softmax attention, Hopfield update, fine-tuning on neighbours, etc.).
- The eight per-source questions are shortened to:
  Q1 STORED-EXACT / Q2 COMPRESSED / Q3 WHERE (storage | retrieval | prediction) /
  Q4 FORGETTING (causal = it is part of the mechanism that makes prediction work;
  incidental = a side effect of a budget) / Q5 TARGET / Q6 CAPACITY /
  Q7 NUISANCE-PRESERVED / Q8 THEORY LINK.

### A framing that cuts across everything below

Every system here can be written as a triple (write rule, state, read rule):

- Nonparametric / episodic / retrieval: the write rule is append (maybe with eviction).
  The state is the raw set. All compression happens in the READ rule (kernel, k, the
  embedding used as metric, top-k truncation, softmax temperature).
- Recurrent / SSM / linear attention / fast weights: the write rule is a lossy update
  (Hebbian outer product, delta rule, gated decay). The state is bounded. Compression
  happens at WRITE time, before the query is known.
- Wang, Shi and Fox (2025) [V] make this explicit: "memorization" = a regression problem
  solved at test time over (key, value) pairs; layers differ only in (i) regression
  weights, (ii) regressor function class, (iii) the test-time optimizer. Softmax
  attention is the nonparametric (Nadaraya-Watson-like) end; linear attention / SSMs /
  fast-weight programmers are parametric (bounded) ends.

The decisive property: a write-time compressor must decide what to keep WITHOUT seeing
the query. A read-time compressor decides AFTER seeing the query. Everything in the
synthesis follows from that asymmetry plus the cost of doing it.

---------------------------------------------------------------------------------------

## 1. Nearest-neighbour, kernel and local-learning methods (the classical baseline)

### 1.1 Cover and Hart (1967), "Nearest neighbor pattern classification" [R]
- Q1 every training pair. Q2 nothing. Q3 prediction (1-NN vote).
- Q4 no forgetting. Q5 Bayes-optimal classifier.
- Q6 unbounded memory; O(n) query without index.
- Q7 nuisance dimensions enter the metric and inflate distances; asymptotically harmless
  for 1-NN risk bound but slow convergence.
- Q8 asymptotic 1-NN risk <= 2 x Bayes risk (the classic bound). Infinite-sample only.

### 1.2 Stone (1977), "Consistent nonparametric regression", Ann. Statist. [R]
- k-NN with k -> infinity, k/n -> 0 is universally consistent. Q8: consistency needs
  the readout's effective neighbourhood to shrink AND the vote count to grow -- i.e.
  the readout must average (compress) at query time; pure 1-NN is not consistent.
- Decision-relevance: exact storage is necessary-but-not-sufficient; the readout must
  do the averaging that a compressed model would have done at training time.

### 1.3 Chaudhuri and Dasgupta (2014), "Rates of convergence for nearest neighbor
classification", NeurIPS [V]
- Finite-sample, distribution-dependent rates in general metric spaces; new smoothness
  class tailored to NN; under a Tsybakov margin condition the NN rate matches minimax
  lower bounds for nonparametric classification [V].
- Q7/Q8: rates depend on the measure of balls in the chosen metric, so nuisance
  coordinates that spread mass slow learning -- the metric is where compression lives.

### 1.4 Kpotufe (2011), "k-NN regression adapts to local intrinsic dimension", NeurIPS [R]
- Q8: k-NN rates depend on INTRINSIC (local) dimension, not ambient dimension. The curse
  of dimensionality bites only if nuisance variation is genuinely high-dimensional in the
  metric. If nuisance lives on a low-dim manifold, raw storage is cheap to exploit.

### 1.5 Bottou and Vapnik (1992), "Local learning algorithms", Neural Computation [R];
Atkeson, Moore and Schaal (1997), "Locally weighted learning", AI Review [R]
- Q1 all data. Q3 prediction: fit a small model around each query.
- This is the classical ancestor of "test-time training on neighbours" and "ICL as
  query-time regression". Q8: local capacity control trades bias vs variance per query.

### 1.6 Belkin, Hsu and Mitra (2018), "Overfitting or perfect fitting? Risk bounds for
classification and regression rules that interpolate", NeurIPS [R];
Belkin, Rakhlin and Tsybakov (2019), "Does data interpolation contradict statistical
optimality?", AISTATS [R]
- Q1 all data, fit exactly (interpolation). Q8: weighted-NN / singular-kernel
  interpolating schemes can be minimax-optimal. Memorizing every training point, noise
  included, need NOT hurt generalization when the readout is local and weighted.
- Q7: label noise is preserved in storage but diluted by the singular-kernel readout
  away from the training points ("spiky-smooth").

### 1.7 Rahimi and Recht (2007), random features, NeurIPS [R]; kernel ridge regression
- Kernel methods = store all n examples (dual) or compress into D random features
  (primal). This is the cleanest classical "exact vs compressed" dial: D << n compresses
  at storage; error vs D has known bounds. Useful as a template for controlled studies.

### 1.8 Memorization-necessity theory (key for Q7)
- Feldman (2020), "Does learning require memorization? A short tale about a long tail",
  STOC [R]: when the data distribution has a long tail of rare subpopulations,
  near-optimal generalization REQUIRES memorizing singleton examples, labels included.
- Brown, Bun, Feldman, Smith and Talwar (2021), "When is memorization of irrelevant
  training data necessary for high-accuracy learning?", STOC [V]: there are natural
  prediction problems where EVERY sufficiently accurate algorithm must encode essentially
  all information about a large subset of its training examples -- even when most of
  that information is irrelevant to the task, and regardless of model class [V].
- Decision-relevance: a result that preserving nuisance information can be
  information-theoretically forced, not a design flaw. A study that finds a learner
  keeping nuisance bits cannot infer "bad compression" without ruling out this regime.

### 1.9 Information-theoretic generalization bounds
- Xu and Raginsky (2017), "Information-theoretic analysis of generalization capability
  of learning algorithms", NeurIPS [R]: gen gap <= sqrt(2 sigma^2 I(S;W)/n). Low mutual
  information between the training set S and the learned state W => small gap.
- Bassily, Moran, Nachum, Shafer, Yehudayoff (2018), "Learners that use little
  information", ALT [R].
- Tension with 1.6/1.8: exact-storage learners have maximal I(S;W) yet can generalize;
  the bounds are sufficient, not necessary. The generalization is carried by the READOUT
  (which has small I with any single stored point in the local-averaging regime).
- Information bottleneck: Tishby, Pereira, Bialek (1999) [R]; Shwartz-Ziv and Tishby
  (2017) compression-phase claim [R]; Saxe et al. (2018, ICLR) showed the compression
  phase depends on nonlinearity and is not causally required for generalization [R].
- Predictive information: Bialek, Nemenman, Tishby (2001), Neural Computation [R] --
  the part of the past that predicts the future is sub-extensive; the rest is nuisance.
  Computational mechanics (Crutchfield and Young 1989; Shalizi and Crutchfield 2001) [R]:
  causal states are the minimal sufficient statistic of the past for the future. This is
  the formal "ideal bounded state": anything a bounded memory keeps beyond causal-state
  information is nuisance, anything less loses prediction.

---------------------------------------------------------------------------------------

## 2. Two meanings of "reservoir"

### 2.1 Reservoir SAMPLING -- Vitter (1985), "Random sampling with a reservoir",
ACM TOMS 11(1) [R]
- Q1 a uniform random subset of size k of a stream (exact items). Q2 nothing within an
  item; the stream is compressed by SUBSAMPLING. Q3 storage (which items survive).
- Q4 forgetting is incidental (budget), and uniform/unbiased by design.
- Used as the buffer policy in continual learning: Chaudhry et al. (2019), "On tiny
  episodic memories in continual learning" [R]; Rolnick et al. (2019), "Experience
  replay for continual learning", NeurIPS [R]; Buzzega et al. (2020) DER [R].
  Finding [R]: even tiny exact replay buffers (1 example per class) outperform many
  regularization-based (compressed-into-weights) continual-learning methods.

### 2.2 Reservoir COMPUTING -- Jaeger (2001) echo state networks (GMD report 148) [R];
Maass, Natschlaeger, Markram (2002) liquid state machines, Neural Computation [R];
Lukosevicius and Jaeger (2009) survey, Computer Science Review [R]
- Q1 nothing exact. Q2 the whole input history, compressed into a fixed random
  recurrent state with fading memory (echo-state property). Q3 storage (the dynamics).
  Only the linear READOUT is trained.
- Q4 forgetting is CAUSAL: the echo-state property (fading memory) is required for the
  state to be a well-defined function of the input history.
- Q6 Jaeger (2002) short-term memory capacity: total linear memory capacity <= N
  (number of units) [R]. Hard bounded-state limit.
- Q7 nuisance past inputs occupy capacity; the readout can ignore them only if they are
  linearly separable from target features in state space.
- Gauthier, Bollt, Griffith, Barbosa (2021), "Next generation reservoir computing",
  Nature Communications [R]: replaces the random reservoir with explicit time-delay
  taps + polynomial features -- i.e. store a short exact window and compress at readout.
  Reported equal or better forecasting with far less data/warm-up [R]. This is a direct
  instance of "exact short window + nonlinear readout beats random compressed state".
- Note the naming collision: reservoir sampling = exact storage with subsampling;
  reservoir computing = bounded compressed state. They are opposite ends of the axis.

---------------------------------------------------------------------------------------

## 3. Associative memory

### 3.1 Hopfield (1982), PNAS [R]; Amit, Gutfreund, Sompolinsky (1985) [R]
- Q1 nothing exact: patterns are superimposed into a Hebbian weight matrix (storage
  compression). Q3 storage. Readout = attractor dynamics.
- Q6 ~0.138 N random patterns (N neurons) before catastrophic retrieval failure.
- Q4 forgetting incidental and CATASTROPHIC (blackout past capacity), not graceful.
- Q7 crosstalk: every stored pattern adds noise to every retrieval; spurious mixture
  states appear. This is the canonical "interference at storage".

### 3.2 Krotov and Hopfield (2016), "Dense associative memory for pattern recognition",
NeurIPS [R]; Demircigil et al. (2017), J. Stat. Phys. [R];
Lucibello and Mezard (2024), "Exponential capacity of dense associative memories",
PRL 132, 077301 [V]
- Q1 in the "dense" formulation the patterns themselves are stored (the energy is a sum
  over stored patterns of a sharp separation function) -- storage is effectively exact;
  the NONLINEARITY of the readout suppresses crosstalk.
- Q3 compression moves from storage to RETRIEVAL (the separation function).
- Q6 polynomial (N^(n-1)) for degree-n interactions; exponential P = exp(alpha N) for
  exponential separation; Lucibello-Mezard give exact asymptotic thresholds and basin
  sizes [V].
- Decision-relevance: the jump from 0.14N to exp(N) comes entirely from changing the
  READOUT, with the same raw information stored. Strong existence proof that
  "interference" in classical Hopfield was a readout property.

### 3.3 Ramsauer et al. (2021), "Hopfield networks is all you need", ICLR [R]
- Continuous modern Hopfield update = softmax attention; one-step retrieval; exponential
  capacity; three regimes (global averaging, metastable subset averaging, single-pattern
  retrieval) controlled by inverse temperature beta [R].
- Q7/Q8: beta is a direct knob between "memorize/retrieve one item" and "average many
  items" -- i.e. between lookup and generalization. Excellent experimental dial.

### 3.4 Kanerva (1988) Sparse Distributed Memory [R]; Bricken and Pehlevan (2021),
"Attention approximates sparse distributed memory", NeurIPS [R]
- SDM stores superimposed patterns in hard locations; read = sum over locations within
  Hamming radius. Bricken-Pehlevan show softmax attention approximates SDM read [R].

### 3.5 Memorization -> generalization transitions in DenseAMs
- Pham, Raya, Negri, Zaki, Ambrogioni, Krotov (2025), "Memorization to generalization:
  emergence of diffusion models from associative memory", arXiv 2505.21777 (ICLR 2025
  workshop; NeurIPS-listed at IBM) [V]: below critical capacity each training sample is
  its own attractor (memorization); when data exceed the critical storage capacity,
  NEW minima distinct from training data emerge -- generalization. Diffusion models
  show the same transition with data size [V].
- Kalaj, Lauditi, Perugini, Lucibello, Malatesta, Negri (2025), "Random features
  Hopfield networks generalize retrieval to previously unseen examples", Physica A 678;
  arXiv 2407.05658 [V]: when stored examples are superpositions of latent random
  features, a feature-learning transition appears: attractors for the FEATURES and for
  UNSEEN mixtures emerge; explained as spurious states of the learned features [V].
- Q3 here compression happens at STORAGE, and it is causal: generalization is
  literally produced by the overload/interference that destroys exact recall.
- Q4 forgetting (of individual examples) is CAUSAL for generalization in this family.
- This is the single most important counterweight to the "exact storage + readout"
  story: in superposition memories, loss of exact recall and the onset of
  generalization are the SAME transition. It gives a sharp, measurable signature
  (see synthesis 3.c, D5).

---------------------------------------------------------------------------------------

## 4. Episodic memory in RL and in the brain

### 4.1 Lengyel and Dayan (2007), "Hippocampal contributions to control: the third
way", NeurIPS [R]
- Argues episodic control (replay the best remembered action sequence) beats model-free
  and model-based control in the low-data regime. Q5 fast early performance.

### 4.2 Blundell et al. (2016), "Model-free episodic control", arXiv 1606.04460 [V]
- Q1 a table of the MAXIMUM return seen per (embedded state, action) [V].
- Q2 observations via random projection or VAE embedding [V/R: random projection V].
- Q3 storage (projection + max-return aggregation) and retrieval (k-NN averaging for
  unseen states) [V].
- Q4 incidental: least-recently-updated entry removed when full [V].
- Q5 fast policy improvement; more data-efficient than DQN-class learners early [V].
- Q7 max-return aggregation preserves lucky outcomes in stochastic environments
  (optimism bias) [R] -- a nuisance (noise) that exact storage keeps and a compressed
  value function would average away.

### 4.3 Pritzel et al. (2017), "Neural episodic control", ICML, PMLR 70 [V]
- Q1 growing per-action arrays of (key = learned embedding, value = N-step Q estimate)
  in a Differentiable Neural Dictionary [V]. Q2 slowly-changing learned embedding.
- Q3 retrieval: kernel-weighted average over k nearest keys.
- Q4 incidental (LRU when capacity reached) [R].
- Q5 sample efficiency; learns "significantly faster" than prior deep RL [V]; known to
  be overtaken asymptotically by parametric agents [R].
- Decision-relevance: canonical evidence that exact store + kernel readout wins
  EARLY (low data) and loses LATE (when a compressed function has had enough data).

### 4.4 Complementary learning systems
- McClelland, McNaughton, O'Reilly (1995), Psych. Review [R]; Kumaran, Hassabis,
  McClelland (2016), TICS [R]: fast hippocampal exact store + slow neocortical
  compressed learner; interleaved replay avoids catastrophic interference.
- Sun, Advani, Spruston, Saxe, Fitzgerald (2023), "Organizing memories for
  generalization in complementary learning systems", Nature Neuroscience 26:1438-1448
  [V]: unregulated consolidation (transfer all memories into the compressed learner)
  causes OVERFITTING and harms generalization in an unpredictable world; optimal policy
  consolidates only the PREDICTABLE components [V].
- Q7 direct answer: preserving nuisance (unpredictable) components inside the COMPRESSED
  store hurts generalization; keeping them in the EXACT store (hippocampus) is harmless
  and useful for recall. Nuisance is toxic in bounded parametric state, benign in an
  indexed exact store with a selective readout.
- Q8 linear teacher-student theory with explicit noise; generalization-optimal
  consolidation amount depends on the teacher's signal-to-noise [R for details].
- Nature Machine Intelligence (2024), "Sequential memory improves sample and memory
  efficiency in episodic control" [V title only] -- storing sequences rather than
  independent entries in episodic control.

---------------------------------------------------------------------------------------

## 5. Retrieval-augmented models

### 5.1 Khandelwal et al. (2020), "Generalization through memorization: nearest
neighbor language models", ICLR [R]
- Q1 a datastore of (context-embedding, next-token) for every training token (hundreds of
  millions of entries). Q2 contexts compressed into the LM's hidden vector (the key).
- Q3 retrieval: kNN distribution interpolated with the parametric LM.
- Q5 perplexity; reported ~2.9-point perplexity gain on Wikitext-103 with NO extra
  training, and larger gains when the datastore is larger than the training set or for
  domain adaptation [R].
- Q6 datastore size linear in tokens; query cost = ANN search per token (was reported as
  a large slowdown [R]).

### 5.2 Xu, Alon, Neubig (2023), "Why do nearest neighbor language models work?", ICML,
PMLR 202 [V]
- kNN-LM beats the parametric LM EVEN WHEN the datastore is the LM's own training set
  [V]. Three identified causes [V abstract]: (1) a different input representation used
  as the key, (2) approximate kNN search, (3) softmax temperature of the kNN
  distribution. Insights were folded back into a parametric LM, improving it WITHOUT
  retrieval [V].
- Decision-relevance: the gain from "exact storage" here was substantially a READOUT
  effect (different representation + temperature + ANN noise acting as regularizer),
  not access to unseen facts. Distinguishes "memory adds information" from "memory adds
  a better readout". The softmax-bottleneck hypothesis was examined in the body [V
  snippet] but is not one of the three abstract-level causes.

### 5.3 Borgeaud et al. (2022), RETRO, "Improving language models by retrieving from
trillions of tokens", ICML [R]
- Q1 2T-token database of raw text chunks; Q2 frozen BERT embeddings for keys;
  Q3 retrieval (chunked cross-attention on retrieved neighbours).
- Q5 LM loss; reported a 7.5B RETRO comparable to ~25x larger models on the Pile [R],
  with the caveat [R] that much of the gain came from test-train leakage/overlap; gains
  shrink on low-overlap data. Important confound for any "exact storage wins" claim.

### 5.4 Lewis et al. (2020), RAG, NeurIPS [R]; Guu et al. (2020), REALM, ICML [R];
Izacard and Grave (2021), FiD, EACL [R]; Izacard et al. (2023), Atlas, JMLR [R]
- Q1 document corpus (exact); Q2 dense passage embeddings; Q3 retrieval and reader.
- Q4 no forgetting; knowledge updatable by swapping the index (a property compressed
  weights lack).
- Atlas: 11B retrieval model competitive with 540B PaLM on few-shot knowledge tasks [R].

### 5.5 Min et al. (2023), "Nonparametric masked language modeling" (NPM), Findings ACL
[R] -- output distribution entirely nonparametric over a phrase corpus; strong on rare
entities. Supports the long-tail (Feldman) story.

### 5.6 Hardt and Sun (2024), "Test-time training on nearest neighbors for large
language models", ICLR [V]
- Q1 the Pile, indexed by text embeddings [V]. Q3 PREDICTION: retrieve ~20 neighbours,
  one gradient step each on the model's own loss, then predict [V].
- Q5 LM performance on >20 Pile tasks; narrows gap between GPT-2 and a >10x larger
  GPT-Neo [V].
- Decision-relevance: an explicit third option -- exact store + query-time PARAMETRIC
  fit (local learning a la Bottou-Vapnik). Query compute = k forward+backward passes.

### 5.7 Xu, Ping et al. (2024), "Retrieval meets long context large language models",
ICLR [V]
- A 4K-context LLM with simple retrieval matches a 16K-context finetuned LLM on long-
  context tasks at much lower compute; retrieval helps even the extended-context models
  [V]. Direct evidence that selective readout (top-k) beats full attention over all
  stored tokens on cost, and matches on accuracy.

---------------------------------------------------------------------------------------

## 6. Memory-augmented networks

- Weston, Chopra, Bordes (2015), Memory Networks, ICLR [R]; Sukhbaatar et al. (2015),
  End-to-end memory networks, NeurIPS [R]: slot memory of (embedded) facts; soft
  attention readout; multi-hop. Q1 each fact stored as a slot. Q3 retrieval.
- Graves, Wayne, Danihelka (2014), Neural Turing Machine [R]; Graves et al. (2016),
  Differentiable Neural Computer, Nature 538 [R]: learned write/erase to a bounded slot
  matrix -- a hybrid: slots are exact-ish but the WRITE is learned and lossy. Q4 learned
  erase = causal forgetting. Q6 number of slots. Known to be hard to train [R].
- Santoro et al. (2016), "One-shot learning with memory-augmented neural networks",
  ICML [R]: external memory enables one-shot class binding.
- Wu, Rabe, Hutchins, Szegedy (2022), "Memorizing transformers", ICLR [R]: kNN lookup
  into an EXACT cache of past (key, value) pairs (up to ~262K tokens), no gradient
  through memory; perplexity keeps improving with memory size [R]. Q3 retrieval.
- Zhang, Bottou et al. (2024), "Memory mosaics" [R?]: networks of associative memories
  (kernel smoothers over stored key-value pairs) as transparent alternative to attention.

---------------------------------------------------------------------------------------

## 7. Long-context and sequence-memory architectures (2019-2026)

### 7.1 Exact-cache end: softmax attention
- Q1 every past (k, v) exactly (KV cache). Q3 retrieval/prediction (softmax readout).
- Q6 memory O(T), per-token compute O(T).
- Jelassi, Brandfonbrener, Kakade, Malach (2024), "Repeat after me: transformers are
  better than state space models at copying", ICML, PMLR 235 [V]: a 2-layer transformer
  can copy strings of EXPONENTIAL length; generalized SSMs are fundamentally limited by
  their fixed-size latent state -- they cannot copy strings carrying more information
  than the state holds [V]. Empirically transformers are better in efficiency AND
  generalization on copy-type synthetic tasks [V].
- Q8: the cleanest theoretical link: required state bits >= information that must be
  retrieved exactly. Bounded state is a hard ceiling for exact-recall targets.

### 7.2 Bounded-state end: RNN / SSM / linear attention
- Katharopoulos et al. (2020), "Transformers are RNNs", ICML [R]: linear attention =
  a d x d outer-product state (Hebbian write).
- Schlag, Irie, Schmidhuber (2021), "Linear transformers are secretly fast weight
  programmers", ICML [R]: linear attention can store at most ~d orthogonal key-value
  associations in a d-dim key space; beyond that, retrieval collides; they propose the
  delta rule to overwrite rather than add [R].
- Yang et al. (2024), DeltaNet parallelization, NeurIPS [R]; Yang, Kautz, Hatamizadeh
  (2025), "Gated delta networks: improving Mamba2 with delta rule", ICLR [V]: gating =
  rapid erasure, delta rule = targeted overwrite; complementary [V]. When sequence
  length exceeds the model/key dimension, "memory collisions" are inevitable in a fixed
  state; gating/clearance mitigates [V (secondary summary)].
  Q4: forgetting is CAUSAL here -- the gate is the mechanism that keeps the state usable.
- Gu and Dao (2023), Mamba [R]; Dao and Gu (2024), Mamba-2 / SSD, ICML [R]:
  input-selective decay; compression at write time, but the write is input-dependent.
- Arora et al. (2023), "Zoology: measuring and improving recall in efficient language
  models", arXiv 2312.04927 (ICLR 2024) [V]: introduces MQAR (multi-query associative
  recall); gated-convolution models need model dimension scaling at least LINEARLY in
  sequence length to solve associative recall, while attention solves it with
  near-constant dimension [V]. Most of the perplexity gap between attention and
  gated-conv models at scale is attributable to recall [R].
- Arora et al. (2024), "Simple linear attention language models balance the
  recall-throughput tradeoff" (Based), ICLR 2024 / arXiv 2402.18668 [V]: a fundamental
  tradeoff between recall ability and memory consumed during generation; dialing window
  size and feature dimension traverses the Pareto frontier from full-attention quality
  to small-state efficiency [V]. +6.22 points over Mamba on recall-intensive tasks at
  1.3B [V].
- Wen, Dang, Lyu (2025), "RNNs are not transformers (yet): the key bottleneck on
  in-context retrieval", ICLR 2025 [V]: CoT improves RNNs but does not close the gap;
  the bottleneck is inability to perfectly retrieve from context (associative recall,
  is-a-tree); adding RAG or ONE transformer layer closes it [V].
- Waleffe et al. (2024), "An empirical study of Mamba-based language models", arXiv
  2406.07887 [V]: 8B Mamba-2 vs Transformer vs hybrid at 3.5T tokens; pure SSMs lag on
  copying, in-context learning, long-context reasoning; 5-shot MMLU 17 points lower at
  1.1T tokens; an 8B hybrid (a few attention layers) exceeds the Transformer on all 12
  standard tasks (+2.65 avg), ~8x faster generation predicted [V].
- Pantazopoulos et al. (2026), "Retrievit: in-context retrieval capabilities of
  transformers, SSMs and hybrids", arXiv 2603.02874 [V]: hybrids beat SSMs and
  match/exceed transformers on n-gram retrieval data efficiency/extrapolation, but
  TRANSFORMERS remain superior on POSITION retrieval; SSMs learn locality-aware
  embeddings [V].
- Boesch and Wee (2026), "Anatomy of associative recall in fixed-state recurrences: a
  matched-state decomposition, an interference wall, and a curriculum that breaks it",
  arXiv 2609.16183 (submitted 2026-09-14; very recent, unreviewed) [V abstract only]:
  models that solve 32-pair recall fall to chance retrieving 4 pairs from a DISTRACTOR
  haystack -- an interference problem, NOT a capacity limit, arising under sparse
  supervision; a distance curriculum raises "lock-in" from 1/10 to 7/10 seeds; the short
  convolution carries most of the recall gain [V]. Directly relevant to synthesis (b):
  interference distinct from capacity, and seed-lottery sensitive.

### 7.3 Compress-the-past hybrids
- Dai et al. (2019), Transformer-XL, ACL [R]: segment recurrence; cache is exact but
  gradients stop.
- Rae et al. (2020), "Compressive transformers for long-range sequence modelling",
  ICLR [R]: FIFO exact memory + a second compressed memory (conv/pool compression of
  evicted activations), trained with attention-reconstruction loss. Q3 storage (at
  eviction). Q4 incidental (FIFO) then compressive. Introduced PG-19.
- Bulatov, Kuratov, Burtsev (2022), "Recurrent memory transformer", NeurIPS [R];
  Bulatov et al. (2023/2024) scaling RMT to 1M+ tokens; BABILong benchmark (Kuratov et
  al. 2024, NeurIPS D&B) [R]: memory tokens passed between segments -> bounded state.
- Munkhdalai, Faruqui, Gopal (2024), "Leave no context behind: Infini-attention" [R]:
  local softmax attention + linear-attention compressive memory per head.
- Lee, McLeish, Goldstein, Fanti (2026), "Do language models need sleep? Offline
  recurrence for improved online inference", arXiv 2605.26099 [V abstract]: periodically
  convert recent context into fast weights ("sleep") then clear the cache; gains on
  cellular automata, graph retrieval and math reasoning; improves with sleep duration
  [V]. A CLS-style consolidation step: compression moved OFF the query path.

### 7.4 Test-time training / memory as test-time regression (2024-2026)
- Sun et al. (2024/2025), "Learning to (learn at test time): RNNs with expressive
  hidden states", arXiv 2407.04620, ICML 2025 [V]: hidden state = a model (linear or
  MLP) updated by a self-supervised gradient step per token; like Transformers, TTT
  layers keep reducing perplexity with more context while Mamba stops after ~16K [V].
- Behrouz, Zhong, Mirrokni (2025), "Titans: learning to memorize at test time",
  arXiv 2501.00663, NeurIPS 2025 [V]: deep neural long-term memory updated at test time
  (surprise-driven gradient + momentum + weight-decay forgetting) combined with attention
  as short-term memory; >2M context; strong on BABILong [V].
- Behrouz et al. (2025/2026), "It's all connected: a journey through test-time
  memorization, attentional bias, retention, and online optimization" (Miras),
  arXiv 2504.13173, ICLR 2026 [V]: four design choices -- memory architecture,
  attentional-bias objective, RETENTION gate, memory learning algorithm; forgetting
  re-read as retention REGULARIZATION [V]. Q4: forgetting is an explicit regularizer,
  i.e. causal, a design variable.
- Behrouz et al. (2025), "ATLAS: learning to optimally memorize the context at test
  time", arXiv 2505.23735 [R title V]: optimize memory over a window of past tokens
  (not just the current one) -- a step back toward exact-window storage.
- Wang, Shi, Fox (2025), "Test-time regression: a unifying framework for designing
  sequence models with associative memory", arXiv 2501.12352 [V]: see framing above.
  Softmax attention = nonparametric regression over all stored pairs; linear
  attention/SSMs/fast weights = parametric regression with specific weights/optimizer.
- Liu et al. (2024), "Longhorn: state space models are amortized online learners"
  [R title V].
- Zhang et al. (2025), "Test-time training done right", arXiv 2505.23884 [R? title V]:
  large-chunk TTT to raise hardware utilization.
- Behrouz et al. (2025), "Nested learning: the illusion of deep learning
  architectures", arXiv 2512.24695 [V title only].

---------------------------------------------------------------------------------------

## 8. In-context learning as query-time fitting

- Garg, Tsipras, Liang, Valiant (2022), "What can transformers learn in-context? A case
  study of simple function classes", NeurIPS [R]: transformers trained on (x, f(x))
  prompts match least squares for linear f, and do well for sparse linear, trees, 2-layer
  nets.
- Akyurek et al. (2023), "What learning algorithm is in-context learning?", ICLR [R]:
  ICL implements ridge / GD / exact least squares depending on depth and noise.
- von Oswald et al. (2023), "Transformers learn in-context by gradient descent", ICML
  [R]: a linear self-attention layer can implement one step of GD on an in-context
  regression loss; trained models converge to it.
- Xie, Raghunathan, Liang, Ma (2022), "An explanation of in-context learning as
  implicit Bayesian inference", ICLR [R].
- Raventos, Paul, Chen, Ganguli (2023), "Pretraining task diversity and the emergence of
  non-Bayesian in-context learning for regression", NeurIPS [V]: below a task-diversity
  threshold the transformer behaves as the Bayes estimator with the FINITE pretraining
  task set as prior (it memorizes tasks -> retrieval); above it, it behaves like ridge
  regression (Gaussian prior) and solves unseen tasks [V].
  Q3: the memorize-tasks vs fit-at-query transition is a switch between compression in
  WEIGHTS (task lookup) and compression in the READOUT (in-context regression).
- Chan et al. (2022), "Data distributional properties drive emergent in-context learning
  in transformers", NeurIPS [R]: bursty, Zipfian data -> ICL; in-weights vs in-context
  learning trade off. Singh et al. (2023), "The transient nature of emergent in-context
  learning", NeurIPS [R]: ICL can fade as in-weights memorization takes over with long
  training.
- Olsson et al. (2022), "In-context learning and induction heads", Anthropic [R]:
  induction heads = copy/lookup readout over exact context.
- Reddy (2024), "The mechanistic basis of data dependence and abrupt learning in an
  in-context classification task", ICLR [R].
- Decision-relevance: ICL is literally "exact storage (the prompt) + a learned
  query-time regressor". The Raventos threshold is a sharp, cheap-to-reproduce
  discriminator between compressed-lookup and query-time-fitting regimes.

---------------------------------------------------------------------------------------

## 9. Retrieval interference evidence (for synthesis b)

- Shi et al. (2023), "Large language models can be easily distracted by irrelevant
  context", ICML, PMLR 202 [V]: GSM-IC; accuracy drops substantially when irrelevant
  sentences are added; mitigated by self-consistency and an instruction to ignore
  irrelevant info [V].
- Liu et al. (2024), "Lost in the middle: how language models use long contexts", TACL
  [R]: U-shaped accuracy vs position of the relevant document; more retrieved documents
  can reduce accuracy.
- Yoran et al. (2024), "Making retrieval-augmented language models robust to irrelevant
  context", ICLR [R]: irrelevant retrieved passages hurt; NLI-filtering or fine-tuning on
  mixed relevant/irrelevant contexts fixes most of it.
- Cuconasu et al. (2024), "The power of noise: redefining retrieval for RAG systems",
  SIGIR [V existence] claimed RANDOM documents could IMPROVE accuracy; but
  Mazuryk et al. (2026), "The powerless noise: how experimental settings shape the
  reported power of noise", SIGIR 2026 reproducibility track, arXiv 2607.03615 [V]:
  the effect "appears, weakens, or disappears" under small prompt/decoding changes;
  much of it traced to output truncation and malformed generations [V]. Treat
  "noise helps" as NOT established.
- Hong et al. / Chroma (2025), "Context rot: how increasing input tokens impacts LLM
  performance", Chroma technical report [V summary]: 18 frontier models degrade as input
  length grows even on simple tasks; degradation accelerates when needle-question
  semantic similarity is low and in the presence of semantically similar distractors;
  distractor impact is non-uniform [V]. (Industry report, not peer reviewed.)
- Boesch and Wee (2026) [V abstract], above: distractor "interference wall" separate from
  capacity in fixed-state recurrences.
- Classical Hopfield crosstalk (3.1) vs DenseAM (3.2): same stored content, interference
  removed by sharpening the readout.
- Xu, Alon, Neubig (2023) [V]: approximate (noisier) kNN search HELPED -- retrieval noise
  can act as regularization, so interference is not monotone.

---------------------------------------------------------------------------------------

## 10. SYNTHESIS

### (a) When exact storage + a query-time readout matches or beats compressed state,
and what it costs

Regimes where exact + readout wins (evidence strength in brackets):

1. The target requires EXACT recall of information larger than the bounded state
   (copying, associative recall, phonebook lookup, position retrieval). Theory: Jelassi
   et al. 2024 [V], Zoology 2023 [V], Wen-Dang-Lyu 2025 [V]. Here it is not a matter of
   degree: bounded state is provably insufficient once required bits > state bits.
2. Low-data / early-learning regime: episodic control beats parametric RL early
   (MFEC, NEC) [V]; NG-RC beats random reservoirs with little data [R]; tiny replay
   buffers beat weight-regularization in continual learning [R].
3. Long-tailed distributions where singletons matter: Feldman 2020 [R], Brown et al.
   2021 [V], NPM [R]. Memorization is necessary, so compressed state that drops
   singletons loses accuracy.
4. Non-stationary or updatable knowledge: RAG index swap vs retraining [R].
5. When the benefit is actually a better READOUT, not more information: kNN-LM on its
   own training set [V]. Warning: this regime is replicable INSIDE a parametric model
   once the readout insight is known (Xu et al. folded it back in [V]).

Regimes where compressed state matches or beats:

1. Targets that are smooth functions of a low-dimensional sufficient statistic
   (causal states / predictive information small): the bounded state can hold it, and
   write-time compression is free of retrieval noise [R, theory].
2. Large-data asymptotics: parametric agents overtake NEC [R]; a model given enough data
   internalizes what kNN would retrieve.
3. Unpredictable/noisy environments IF the compressed learner only absorbs the
   predictable part (Sun et al. 2023 [V]); a fully-consolidating learner overfits.
4. Superposition memories past critical capacity: generalization EMERGES from
   compression (Pham et al. 2025 [V], Kalaj et al. 2025 [V]) -- exact recall is lost
   and novel-but-valid outputs appear.

Best-of-both is the empirical frontier, not either pole: hybrids with a few exact-
attention layers (Waleffe et al. [V], Wen et al. one-layer fix [V]), retrieval + short
context (Xu, Ping et al. [V]), Titans-style short exact + long compressed [V].

Query-compute cost of exact + readout:
- Full softmax: O(T) per query token, O(T) memory; linear/SSM: O(1) per token.
- kNN/ANN retrieval: O(log n)-ish per query with an index plus index build; kNN-LM was
  reported as substantially slower at inference [R].
- Test-time fitting (Hardt-Sun): k forward+backward passes per query [V k~20, 1 step].
- Based paper [V]: the recall-vs-state-size tradeoff is a Pareto frontier -- you pay for
  recall with inference memory; there is no free lunch point.
- Xu, Ping et al. [V]: selective top-k readout is cheaper than full long-context
  attention at matched accuracy. So "exact storage" is cheap; "exact storage + DENSE
  readout" is what costs.

### (b) Retrieval interference: do irrelevant stored items hurt, and is it retrieval
rather than storage?

Evidence points to interference being primarily a READOUT phenomenon when storage is
exact, and a STORAGE phenomenon only when storage is superposed:

- Exact storage (KV cache, datastore, prompt): stored items do not degrade each other;
  degradation comes from the readout assigning weight to distractors. Signatures: depends
  on distractor-query SIMILARITY, not merely count (Context rot [V]; Shi et al. [V]);
  depends on POSITION (lost in the middle [R]); fixable by changing the readout only --
  filtering, instructions, self-consistency, fine-tuning on mixed contexts (Shi [V],
  Yoran [R]). None of these fixes touch the store, which is the diagnostic.
- Superposed storage (Hopfield, linear attention, SSM state): interference is crosstalk
  at write time; stored items literally overwrite each other; fixes change the WRITE
  rule (delta rule [R], gating [V], retention regularizers [V]). But DenseAM results
  [V] show the same capacity limit can be moved by the READ nonlinearity -- so even in
  "storage" systems, part of what looked like storage interference is readout.
- Fixed-state recurrences can show an interference wall below capacity (Boesch-Wee 2026
  [V abstract]): failure with 4 pairs + distractors after success with 32 clean pairs.
  That is not a storage-budget failure; it is a learned-readout/addressing failure under
  sparse supervision, and is seed-sensitive.
- Irrelevant items can help: approximate kNN noise helped kNN-LM [V]. The "random
  documents help RAG" claim did NOT robustly replicate [V]. Default assumption:
  distractors hurt, with magnitude set by similarity and readout sharpness.
- Mechanistic reason (convergent across literatures): a soft readout (softmax, kernel
  average, Hopfield update at finite beta) mixes values in proportion to key similarity.
  Distractors that are near the query in key space steal mass. Sharper readouts (higher
  beta, smaller k, exponential separation) reduce this at the price of lower averaging
  (less generalization). So the interference/generalization tradeoff is ONE dial.

### (c) Cheap discriminators for a synthetic-world study separating storage compression
from readout compression

Design: a synthetic world where each episode has (predictive latent z, nuisance u);
observations x = g(z, u); target y = f(z) (+ optional noise). Control dim(z), dim(u),
number of stored episodes n, and distractor similarity. Compare learners that store raw
x vs learners with bounded state. Then:

D1. Post-hoc probe of stored content (storage test). Train a decoder on the memory
    state to predict u (nuisance) and exact episode identity. Exact store: u and
    identity decodable at ceiling for all n. Storage compressor: u decodability falls
    with n and with state size; identity recall collapses past capacity. If u is
    decodable from storage but prediction ignores it, compression is in the readout.
    Cost: one linear probe per condition.

D2. Readout swap at fixed storage. Keep the stored set fixed; swap the readout (1-NN,
    k-NN with k in {1,4,16,64}, kernel with beta sweep, ridge fit on retrieved set).
    If accuracy changes a lot with readout alone, readout compression dominates. This
    is the kNN-LM / DenseAM lesson: same store, different readout, very different
    capacity and generalization. Beta sweep also maps the Ramsauer regimes.

D3. Late-query / query-set shift test (the asymmetry test). Change WHICH function of
    the past is queried after storage is finished (e.g. at write time the useful latent
    is z1, at query time ask about z2 or about u). A write-time compressor that
    discarded z2/u cannot recover; an exact store + readout can. This is the single most
    diagnostic test: it measures whether compression happened before or after the query
    was known. Cheap: one extra query head.

D4. State-size vs information scaling (Jelassi/Zoology). Plot accuracy vs (bits that
    must be retrieved) / (state bits). Bounded-state learners should show a knee at
    ratio ~1 (or at key-dim d for linear attention); exact-store learners should not.
    Absence of a knee in a supposedly bounded model means it is not really bounded
    (leak) or the task does not require exact recall.

D5. Memorization-to-generalization transition (DenseAM test). Increase n at fixed
    state. A superposition (storage-compressing) learner shows: exact recall of training
    episodes falls AND accuracy on unseen z-combinations rises at the same n (Pham 2025,
    Kalaj 2025). An exact-store learner shows recall flat at ceiling, generalization
    governed by readout width. Co-location of the two curves is the fingerprint of
    storage compression.

D6. Distractor-similarity sweep with fixed count (interference locus). Add m stored
    distractor episodes at controlled key similarity to the query. If harm scales with
    similarity and is fixed by readout changes (sharpening, filtering) without touching
    storage -> readout interference. If harm scales with COUNT regardless of similarity,
    and only write-rule changes fix it -> storage crosstalk. Include the 4-pairs-in-
    haystack control from Boesch-Wee since that failure is distinct from capacity.

D7. Nuisance-noise regime (CLS test). Make part of y unpredictable noise tied to u.
    Measure (i) exact-store recall of noisy labels, (ii) generalization of the
    compressed learner as a function of how much it absorbs. Sun et al. 2023 predict the
    compressed learner overfits if it absorbs noise; the exact store should be harmless
    if the readout averages. Also run the Feldman long-tail variant (singleton
    subpopulations) where memorizing IS required -- a readout that averages away
    singletons should LOSE there. Two worlds, opposite predictions: a clean dissociation.

D8. Constant/trivial twins (house rule, not literature). For each learner report its
    score against (i) the best constant, (ii) a 1-NN on raw x, (iii) the Bayes-optimal
    predictor on z. Without (ii) one cannot tell whether a compressed state earns
    anything beyond raw lookup; without (iii) one cannot tell whether the readout is the
    bottleneck.

D9. Compute-matched comparison. Report query FLOPs and memory alongside accuracy, and
    compare at matched inference budget (Based-style Pareto frontier). An exact store
    that wins only at 100x query compute is a different claim from one that wins at
    matched compute.

Cheapest high-value subset: D3 (late-query shift), D2 (readout swap at fixed store),
D5 (co-location of recall loss and generalization gain). These three alone separate
"where compression happens" in all families surveyed.

---------------------------------------------------------------------------------------

## 11. Caveats on this review

- Several 2026 items (Boesch-Wee, Lee et al. "sleep", Retrievit, Powerless Noise) were
  verified only at abstract level; Boesch-Wee was posted two weeks before this review
  and is unreviewed.
- RETRO gains partly reflect train-test overlap [R]; check before citing as evidence of
  exact-storage superiority.
- Titans/Miras headline benchmark claims come from the authors; independent
  replications were not checked.
- Classical results (Cover-Hart bound, Hopfield 0.138N, Jaeger memory capacity <= N,
  Schlag et al. d-association limit) are [R]; they are textbook but numbers should be
  confirmed before quoting in a paper.

---------------------------------------------------------------------------------------

## 12. Bibliography (URLs; [V] = located this session)

Nonparametric / theory
- Cover, T., Hart, P. (1967). Nearest neighbor pattern classification. IEEE Trans. Inf.
  Theory 13(1):21-27. https://doi.org/10.1109/TIT.1967.1053964 [R]
- Stone, C. J. (1977). Consistent nonparametric regression. Ann. Statist. 5(4):595-620.
  https://doi.org/10.1214/aos/1176343886 [R]
- Chaudhuri, K., Dasgupta, S. (2014). Rates of convergence for nearest neighbor
  classification. NeurIPS. https://papers.nips.cc/paper/5439-rates-of-convergence-for-nearest-neighbor-classification [V]
- Kpotufe, S. (2011). k-NN regression adapts to local intrinsic dimension. NeurIPS.
  https://arxiv.org/abs/1110.4300 [R]
- Bottou, L., Vapnik, V. (1992). Local learning algorithms. Neural Computation 4(6).
  https://doi.org/10.1162/neco.1992.4.6.888 [R]
- Atkeson, C., Moore, A., Schaal, S. (1997). Locally weighted learning. AI Review 11.
  https://doi.org/10.1023/A:1006559212014 [R]
- Belkin, M., Hsu, D., Mitra, P. (2018). Overfitting or perfect fitting? NeurIPS.
  https://arxiv.org/abs/1806.05161 [R]
- Belkin, M., Rakhlin, A., Tsybakov, A. (2019). Does data interpolation contradict
  statistical optimality? AISTATS. https://arxiv.org/abs/1806.09471 [R]
- Rahimi, A., Recht, B. (2007). Random features for large-scale kernel machines.
  NeurIPS. https://papers.nips.cc/paper/3182-random-features-for-large-scale-kernel-machines [R]
- Feldman, V. (2020). Does learning require memorization? STOC.
  https://arxiv.org/abs/1906.05271 [R]
- Brown, G., Bun, M., Feldman, V., Smith, A., Talwar, K. (2021). When is memorization of
  irrelevant training data necessary for high-accuracy learning? STOC.
  https://arxiv.org/abs/2012.06421 [V]
- Xu, A., Raginsky, M. (2017). Information-theoretic analysis of generalization
  capability of learning algorithms. NeurIPS. https://arxiv.org/abs/1705.07809 [R]
- Bassily, R., Moran, S., Nachum, I., Shafer, J., Yehudayoff, A. (2018). Learners that
  use little information. ALT. https://arxiv.org/abs/1710.05233 [R]
- Tishby, N., Pereira, F., Bialek, W. (1999). The information bottleneck method.
  https://arxiv.org/abs/physics/0004057 [R]
- Saxe, A. et al. (2018). On the information bottleneck theory of deep learning. ICLR.
  https://openreview.net/forum?id=ry_WPG-A- [R]
- Bialek, W., Nemenman, I., Tishby, N. (2001). Predictability, complexity, and
  learning. Neural Computation 13(11). https://arxiv.org/abs/physics/0007070 [R]
- Shalizi, C., Crutchfield, J. (2001). Computational mechanics: pattern and prediction,
  structure and simplicity. J. Stat. Phys. 104. https://arxiv.org/abs/cond-mat/9907176 [R]

Reservoirs
- Vitter, J. S. (1985). Random sampling with a reservoir. ACM TOMS 11(1):37-57.
  https://doi.org/10.1145/3147.3165 [R]
- Chaudhry, A. et al. (2019). On tiny episodic memories in continual learning.
  https://arxiv.org/abs/1902.10486 [R]
- Rolnick, D. et al. (2019). Experience replay for continual learning. NeurIPS.
  https://arxiv.org/abs/1811.11682 [R]
- Jaeger, H. (2001). The "echo state" approach to analysing and training recurrent
  neural networks. GMD Report 148. [R]
- Jaeger, H. (2002). Short term memory in echo state networks. GMD Report 152. [R]
- Maass, W., Natschlaeger, T., Markram, H. (2002). Real-time computing without stable
  states. Neural Computation 14(11). https://doi.org/10.1162/089976602760407955 [R]
- Lukosevicius, M., Jaeger, H. (2009). Reservoir computing approaches to recurrent
  neural network training. Computer Science Review 3(3). [R]
- Gauthier, D., Bollt, E., Griffith, A., Barbosa, W. (2021). Next generation reservoir
  computing. Nature Communications 12:5564. https://doi.org/10.1038/s41467-021-25801-2 [R]

Associative memory
- Hopfield, J. (1982). Neural networks and physical systems with emergent collective
  computational abilities. PNAS 79(8). https://doi.org/10.1073/pnas.79.8.2554 [R]
- Amit, D., Gutfreund, H., Sompolinsky, H. (1985). Storing infinite numbers of patterns
  in a spin-glass model of neural networks. PRL 55. [R]
- Krotov, D., Hopfield, J. (2016). Dense associative memory for pattern recognition.
  NeurIPS. https://arxiv.org/abs/1606.01164 [R]
- Demircigil, M. et al. (2017). On a model of associative memory with huge storage
  capacity. J. Stat. Phys. https://arxiv.org/abs/1702.01929 [R]
- Lucibello, C., Mezard, M. (2024). Exponential capacity of dense associative memories.
  PRL 132:077301. https://link.aps.org/doi/10.1103/PhysRevLett.132.077301 ;
  https://arxiv.org/abs/2304.14964 [V]
- Ramsauer, H. et al. (2021). Hopfield networks is all you need. ICLR.
  https://arxiv.org/abs/2008.02217 [R]
- Kanerva, P. (1988). Sparse Distributed Memory. MIT Press. [R]
- Bricken, T., Pehlevan, C. (2021). Attention approximates sparse distributed memory.
  NeurIPS. https://arxiv.org/abs/2111.05498 [R]
- Pham, B., Raya, G., Negri, M., Zaki, M., Ambrogioni, L., Krotov, D. (2025).
  Memorization to generalization: emergence of diffusion models from associative memory.
  https://arxiv.org/abs/2505.21777 [V]
- Kalaj, S., Lauditi, C., Perugini, G., Lucibello, C., Malatesta, E., Negri, M. (2025).
  Random features Hopfield networks generalize retrieval to previously unseen examples.
  Physica A 678. https://arxiv.org/abs/2407.05658 ;
  https://www.sciencedirect.com/science/article/pii/S0378437125005989 [V]

Episodic memory / CLS
- Lengyel, M., Dayan, P. (2007). Hippocampal contributions to control: the third way.
  NeurIPS. [R]
- Blundell, C. et al. (2016). Model-free episodic control.
  https://arxiv.org/abs/1606.04460 [V]
- Pritzel, A. et al. (2017). Neural episodic control. ICML, PMLR 70.
  https://arxiv.org/abs/1703.01988 [V]
- McClelland, J., McNaughton, B., O'Reilly, R. (1995). Why there are complementary
  learning systems in the hippocampus and neocortex. Psych. Review 102(3). [R]
- Kumaran, D., Hassabis, D., McClelland, J. (2016). What learning systems do intelligent
  agents need? TICS 20(7). https://doi.org/10.1016/j.tics.2016.05.004 [R]
- Sun, W., Advani, M., Spruston, N., Saxe, A., Fitzgerald, J. (2023). Organizing memories
  for generalization in complementary learning systems. Nature Neuroscience 26:1438-1448.
  https://www.nature.com/articles/s41593-023-01382-9 [V]
- (2024) Sequential memory improves sample and memory efficiency in episodic control.
  Nature Machine Intelligence. https://www.nature.com/articles/s42256-024-00950-3
  [V title/venue only; authors not checked]

Retrieval-augmented
- Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., Lewis, M. (2020).
  Generalization through memorization: nearest neighbor language models. ICLR.
  https://arxiv.org/abs/1911.00172 [R]
- Xu, F., Alon, U., Neubig, G. (2023). Why do nearest neighbor language models work?
  ICML, PMLR 202. https://arxiv.org/abs/2301.02828 [V]
- Borgeaud, S. et al. (2022). Improving language models by retrieving from trillions of
  tokens. ICML. https://arxiv.org/abs/2112.04426 [R]
- Lewis, P. et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP
  tasks. NeurIPS. https://arxiv.org/abs/2005.11401 [R]
- Guu, K. et al. (2020). REALM. ICML. https://arxiv.org/abs/2002.08909 [R]
- Izacard, G. et al. (2023). Atlas: few-shot learning with retrieval augmented language
  models. JMLR. https://arxiv.org/abs/2208.03299 [R]
- Min, S. et al. (2023). Nonparametric masked language modeling. Findings ACL.
  https://arxiv.org/abs/2212.01349 [R]
- Hardt, M., Sun, Y. (2024). Test-time training on nearest neighbors for large language
  models. ICLR. https://arxiv.org/abs/2305.18466 [V]
- Xu, P., Ping, W. et al. (2024). Retrieval meets long context large language models.
  ICLR. https://arxiv.org/abs/2310.03025 [V]

Memory-augmented networks
- Weston, J., Chopra, S., Bordes, A. (2015). Memory networks. ICLR.
  https://arxiv.org/abs/1410.3916 [R]
- Sukhbaatar, S. et al. (2015). End-to-end memory networks. NeurIPS.
  https://arxiv.org/abs/1503.08895 [R]
- Graves, A., Wayne, G., Danihelka, I. (2014). Neural Turing machines.
  https://arxiv.org/abs/1410.5401 [R]
- Graves, A. et al. (2016). Hybrid computing using a neural network with dynamic
  external memory. Nature 538. https://doi.org/10.1038/nature20101 [R]
- Santoro, A. et al. (2016). One-shot learning with memory-augmented neural networks.
  ICML. https://arxiv.org/abs/1605.06065 [R]
- Wu, Y., Rabe, M., Hutchins, D., Szegedy, C. (2022). Memorizing transformers. ICLR.
  https://arxiv.org/abs/2203.08913 [R]
- Zhang, J., Bottou, L. et al. (2024). Memory mosaics. https://arxiv.org/abs/2405.06394 [R?]

Sequence memory architectures
- Jelassi, S., Brandfonbrener, D., Kakade, S., Malach, E. (2024). Repeat after me:
  transformers are better than state space models at copying. ICML, PMLR 235.
  https://arxiv.org/abs/2402.01032 [V]
- Katharopoulos, A. et al. (2020). Transformers are RNNs. ICML.
  https://arxiv.org/abs/2006.16236 [R]
- Schlag, I., Irie, K., Schmidhuber, J. (2021). Linear transformers are secretly fast
  weight programmers. ICML. https://arxiv.org/abs/2102.11174 [R]
- Yang, S., Kautz, J., Hatamizadeh, A. (2025). Gated delta networks: improving Mamba2
  with delta rule. ICLR. https://arxiv.org/abs/2412.06464 [V]
- Gu, A., Dao, T. (2023). Mamba. https://arxiv.org/abs/2312.00752 [R]
- Dao, T., Gu, A. (2024). Transformers are SSMs (Mamba-2). ICML.
  https://arxiv.org/abs/2405.21060 [R]
- Arora, S. et al. (2023). Zoology: measuring and improving recall in efficient language
  models. https://arxiv.org/abs/2312.04927 [V]
- Arora, S. et al. (2024). Simple linear attention language models balance the
  recall-throughput tradeoff. https://arxiv.org/abs/2402.18668 [V]
- Wen, K., Dang, X., Lyu, K. (2025). RNNs are not transformers (yet): the key bottleneck
  on in-context retrieval. ICLR. https://arxiv.org/abs/2402.18510 [V]
- Waleffe, R. et al. (2024). An empirical study of Mamba-based language models.
  https://arxiv.org/abs/2406.07887 [V]
- Pantazopoulos, G., Nikandrou, M., Konstas, I., Suglia, A. (2026). Retrievit.
  https://arxiv.org/abs/2603.02874 [V]
- Boesch, J., Wee, A. (2026). Anatomy of associative recall in fixed-state recurrences.
  https://arxiv.org/abs/2609.16183 [V abstract]
- Dai, Z. et al. (2019). Transformer-XL. ACL. https://arxiv.org/abs/1901.02860 [R]
- Rae, J. et al. (2020). Compressive transformers for long-range sequence modelling.
  ICLR. https://arxiv.org/abs/1911.05507 [R]
- Bulatov, A., Kuratov, Y., Burtsev, M. (2022). Recurrent memory transformer. NeurIPS.
  https://arxiv.org/abs/2207.06881 [R]
- Kuratov, Y. et al. (2024). BABILong. NeurIPS D&B. https://arxiv.org/abs/2406.10149 [R]
- Munkhdalai, T., Faruqui, M., Gopal, S. (2024). Leave no context behind:
  Infini-attention. https://arxiv.org/abs/2404.07143 [R]
- Lee, S., McLeish, S., Goldstein, T., Fanti, G. (2026). Do language models need sleep?
  https://arxiv.org/abs/2605.26099 [V abstract]
- Sun, Y. et al. (2025). Learning to (learn at test time): RNNs with expressive hidden
  states. ICML. https://arxiv.org/abs/2407.04620 [V]
- Behrouz, A., Zhong, P., Mirrokni, V. (2025). Titans: learning to memorize at test time.
  NeurIPS. https://arxiv.org/abs/2501.00663 [V]
- Behrouz, A. et al. (2026). It's all connected (Miras). ICLR.
  https://arxiv.org/abs/2504.13173 [V]
- Behrouz, A. et al. (2025). ATLAS. https://arxiv.org/abs/2505.23735 [V title]
- Behrouz, A. et al. (2025). Nested learning. https://arxiv.org/abs/2512.24695 [V title]
- Wang, K. A., Shi, J., Fox, E. (2025). Test-time regression.
  https://arxiv.org/abs/2501.12352 [V]
- Liu, B. et al. (2024). Longhorn. https://arxiv.org/abs/2407.14207 [V title]
- Zhang, T. et al. (2025). Test-time training done right.
  https://arxiv.org/abs/2505.23884 [V title; authors R?]

In-context learning
- Garg, S. et al. (2022). What can transformers learn in-context? NeurIPS.
  https://arxiv.org/abs/2208.01066 [R]
- Akyurek, E. et al. (2023). What learning algorithm is in-context learning? ICLR.
  https://arxiv.org/abs/2211.15661 [R]
- von Oswald, J. et al. (2023). Transformers learn in-context by gradient descent. ICML.
  https://arxiv.org/abs/2212.07677 [R]
- Xie, S. M. et al. (2022). An explanation of in-context learning as implicit Bayesian
  inference. ICLR. https://arxiv.org/abs/2111.02080 [R]
- Raventos, A., Paul, M., Chen, F., Ganguli, S. (2023). Pretraining task diversity and
  the emergence of non-Bayesian in-context learning for regression. NeurIPS.
  https://arxiv.org/abs/2306.15063 [V]
- Chan, S. et al. (2022). Data distributional properties drive emergent in-context
  learning in transformers. NeurIPS. https://arxiv.org/abs/2205.05055 [R]
- Singh, A. et al. (2023). The transient nature of emergent in-context learning in
  transformers. NeurIPS. https://arxiv.org/abs/2311.08360 [R]
- Olsson, C. et al. (2022). In-context learning and induction heads.
  https://arxiv.org/abs/2209.11895 [R]
- Reddy, G. (2024). The mechanistic basis of data dependence and abrupt learning in an
  in-context classification task. ICLR. https://arxiv.org/abs/2312.03002 [R]

Interference / distraction
- Shi, F. et al. (2023). Large language models can be easily distracted by irrelevant
  context. ICML, PMLR 202. https://arxiv.org/abs/2302.00093 [V]
- Liu, N. et al. (2024). Lost in the middle. TACL. https://arxiv.org/abs/2307.03172 [R]
- Yoran, O. et al. (2024). Making retrieval-augmented language models robust to
  irrelevant context. ICLR. https://arxiv.org/abs/2310.01558 [R]
- Cuconasu, F. et al. (2024). The power of noise. SIGIR.
  https://arxiv.org/abs/2401.14887 [V]
- Mazuryk, M., Dolmans, F., Gehringer, L., Klaric, I., Ju, J.-H., Aliannejadi, M.
  (2026). The powerless noise. SIGIR 2026 repro. https://arxiv.org/abs/2607.03615 [V]
- Hong, K., Troynikov, A., Huber, J. (2025). Context rot: how increasing input tokens
  impacts LLM performance. Chroma. https://www.trychroma.com/research/context-rot
  [V existence/summary; author list R?]
