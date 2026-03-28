# Titan Council Prompt 07 — Forge Review: 7 Surviving Reasoning Tools

*For: Claude/Coeus, ChatGPT/Atlas, Gemini/Hyperion, DeepSeek/Oceanus, Grok/Prometheus*
*From: Project Prometheus — automated reasoning tool forge*
*Date: 2026-03-25*

---

## CONTEXT

We built an automated pipeline that:
1. **Nous** generates cross-domain concept triples (e.g., "Ergodic Theory × Falsificationism × Maximum Entropy") and sends them to a 397B model for theoretical evaluation
2. **Hephaestus** takes the top-scoring triples, asks a model to implement them as Python reasoning tools, validates the code compiles and runs, then tests them against a 10-trap reasoning battery
3. Out of **88 attempts**, **7 tools survived** the full pipeline (8% forge rate)

Each surviving tool is a Python class with two methods:
- `evaluate(prompt, candidates) → ranked list with scores`
- `confidence(prompt, answer) → float 0-1`

They use **only numpy and standard library** — no ML frameworks, no models, no training. They are pure algorithmic reasoning strategies that operate on text via hashing, tokenization, and mathematical scoring.

**The purpose:** These tools will become terms in an evolutionary fitness function (RLVF — Reinforcement Learning from Verification Feedback) that replaces RLHF. Instead of "what would a human rate highly," the late layers of a model learn to optimize for "what survives these computable reasoning criteria."

---

## THE 7 SURVIVING TOOLS

### Tool 1: EFME Engine
**Concepts:** Ergodic Theory × Falsificationism × Maximum Entropy

**Mechanism:**
- MaxEnt prior based on candidate complexity (length) — favors neither specific nor overly complex answers
- Ergodic sampling via deterministic hash-seeded pseudo-random walk over hypothesis space
- Falsification scoring: candidates are penalized if they contain logical contradictions with prompt keywords (e.g., answering "Yes" when the prompt contains negation markers)
- Posterior combines prior × falsification survival

**What it does well:** Penalizes candidates that contradict the prompt's logical structure. Favors concise answers that survive keyword-based consistency checks.

**Limitation:** The falsification is keyword-matching, not logical reasoning. It catches surface contradictions but not deep ones.

---

### Tool 2: EGSAE-MC
**Concepts:** Ergodic Theory × Sparse Autoencoders × Model Checking

**Mechanism:**
- Extracts bag-of-words feature vectors from prompt and candidates
- Projects to sparse latent space via L1-like thresholding (only high-magnitude features survive)
- Model checking: compares candidate's latent signature against prompt's expected signature
- Ergodic convergence: hash-seeded trajectory ensures consistent state-space exploration

**What it does well:** Measures structural similarity between prompt and candidate in a compressed feature space. Candidates that activate the same sparse features as the prompt score higher.

**Limitation:** Bag-of-words loses word order and semantic meaning. "Is 9.11 larger than 9.9" and "Is 9.9 larger than 9.11" produce the same features.

---

### Tool 3: EATM-S
**Concepts:** Ergodic Theory × Theory of Mind × Abductive Reasoning

**Mechanism:**
- Simulates nested beliefs by hashing prompt with candidate-specific "agent perspectives"
- Abductive scoring via token intersection (explanation power) weighted by simplicity prior (shorter = better)
- Ergodic pseudo-MCMC chain over candidate space, tracking running average convergence
- If the chain stabilizes (low variance), the belief state is deemed reliable

**What it does well:** Introduces a convergence criterion — candidates that consistently score high across multiple hash-seeded "perspectives" are more robust than those with high variance.

**Limitation:** The "theory of mind" is hash-based, not cognitive. The multi-perspective sampling is creative but doesn't model actual reasoning perspectives.

---

### Tool 4: IBAI
**Concepts:** Information Theory × Active Inference × Free Energy Principle

**Mechanism:**
- Maps text to deterministic latent state vector via hash
- Computes "surprise" as distance between prompt's latent state and candidate's latent state
- Estimates epistemic value: candidates that resolve ambiguity (high divergence from null prior, low divergence from prompt posterior) gain intrinsic value
- Ranks by Expected Free Energy = extrinsic cost + intrinsic uncertainty

**What it does well:** Explicitly models uncertainty reduction. Candidates that are "surprising but relevant" score higher than candidates that are either obvious or random.

**Limitation:** The latent space is hash-derived, so the "distance" is a proxy for string similarity rather than semantic similarity.

---

### Tool 5: ME-CGA
**Concepts:** Information Theory × Genetic Algorithms × Criticality

**Mechanism:**
- Encodes candidates as binary genotypes via hash
- Fitness approximated via text similarity to prompt (mutual information proxy)
- Entropy penalty encourages diversity (penalizes when all candidates score similarly)
- Criticality term: estimates susceptibility based on score variance — drives toward "edge of chaos" where small changes yield significant fitness shifts

**What it does well:** The criticality term is novel — it explicitly models whether the scoring landscape has useful gradient. Flat landscapes (all candidates score the same) get penalized.

**Limitation:** The "genetic algorithm" doesn't actually evolve — it's a single-pass scoring function that borrows GA terminology.

---

### Tool 6: Information-Guided Sparsity-Constrained Feature-Selection Bandit
**Concepts:** Information Theory × Sparse Autoencoders × Multi-Armed Bandits

**Mechanism:**
- Hashes text into sparse binary codes (simulating SAE latent features)
- Each feature is an "arm" in a multi-armed bandit
- UCB (Upper Confidence Bound) selects features that maximize estimated mutual information + exploration bonus
- Candidates scored by sum of MI contributions from their most informative active features

**What it does well:** The bandit framework means the tool LEARNS which features are informative as it processes more candidates. It adapts its scoring within a single `evaluate()` call.

**Limitation:** The "learning" resets per call since there's no persistent state. And 256 hash-derived features don't capture real semantic structure.

---

### Tool 7: CPCTTN
**Concepts:** Tensor Decomposition × Criticality × Free Energy Principle

**Mechanism:**
- Maps candidates to latent vectors via hash-based projection (simulating tensor-train compression)
- Free energy proxy: divergence between candidate embedding and prompt context vector
- Criticality regularization: adjusts Jacobian spectral norm toward 1.0 ("edge of chaos"), maximizing sensitivity to small prediction errors
- Candidates with the lowest free energy at critical sensitivity score highest

**What it does well:** The criticality tuning is the most mathematically sophisticated mechanism — it explicitly models the scoring function's sensitivity and optimizes for the sweet spot where the function is most discriminative.

**Limitation:** All the mathematical sophistication operates on hash-derived vectors that don't capture real meaning.

---

## WHAT WE WANT FROM YOU

For each of the 7 tools:

**1. Is the underlying theoretical combination sound?**
Does the synthesis of these concepts produce something genuinely useful for reasoning evaluation, or is it mathematical theater — impressive-sounding but fundamentally just string matching in disguise?

**2. If you could rebuild this tool from scratch, what would you change?**
Keep the same three concepts but architect the implementation differently. What's the right way to combine these ideas into a reasoning evaluator? Provide concrete pseudocode or Python sketch (under 100 lines).

**3. Rank all 7 tools from most to least promising as a fitness function term for training a language model to reason.**
Consider: Which tool measures something that actually correlates with correct reasoning? Which would produce useful gradient signal during evolutionary search? Which would be gameable (a model could satisfy the criterion without actually reasoning)?

**4. What's missing from all 7?**
Is there a concept combination or architectural pattern that none of these tools capture but that would be critical for a reasoning fitness function?

**5. The hash problem.**
All 7 tools convert text to vectors via cryptographic hashing. This makes them deterministic and dependency-free, but it means they measure string similarity rather than semantic similarity. Is there a way to build a deterministic, numpy-only reasoning evaluator that captures semantic structure without hashing? Or is the hash limitation fundamental when you can't use a neural model?
