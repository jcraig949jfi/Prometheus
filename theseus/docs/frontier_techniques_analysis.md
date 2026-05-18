# Theseus — Frontier Techniques Analysis

**Date**: 2026-05-18 (Fire #2 of the loop)
**Status**: Decision document. Each technique gets a verdict (BUILD / BUILD-LATER / DEFER / DROP) with justification, integration plan, and cost estimate.

The point of this doc is to *decide*, not just survey. The substrate's discipline is to commit to a roadmap and measure yield rather than churn through ideas.

---

## Framework for evaluation

Each technique is judged on five axes:

1. **What it is** — technical summary, including the canonical paper / library if applicable
2. **Theseus fit** — which generator family / engine component it integrates with
3. **Cost** — dev hours + dependencies (Low: <4h, Medium: 4–20h, High: 20+h, Very High: weeks)
4. **Value** — what specifically improves: throughput, info_density, diversity, novelty-vs-pretraining
5. **Verdict** — BUILD (next 1–3 fires), BUILD-LATER (Tier 1 once foundations solidify), DEFER (depends on something downstream that doesn't exist yet), DROP (won't ship)

Hard constraints that shape verdicts:

- **No AI-to-AI inflation**. LLM-driven claim generation is forbidden as primary generator (Standing Order 3). LLM techniques get downweighted unless they have a narrow paraphrasing/auxiliary role.
- **Token-free preference**. Anything that costs API tokens gets deferred until the token-free arsenal plateaus.
- **Volume-target alignment**. v0.1 hits ~85K records / 30s; techniques that improve *yield per record* matter more than techniques that improve *throughput*.
- **Ergon-paused awareness**. Techniques whose value depends on a trained Learner are DEFERRED until Ergon resumes (`feedback_substrate_passive_consumer_warning.md`).

---

## 1. Counterfactual Augmentation (Pearl-style causal mutation)

**What it is**: Generate examples by *intervening* on variables to create maximally challenging counterfactuals — not random perturbations, but targeted ones that test the causal structure of a claim. Roots: Pearl's *Causality* (2009), more recently Kaushik et al. *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data* (ICLR 2020), and CounterGAN-style data augmentation.

**Theseus fit**: C-family mutations. The naive C1 swaps objects randomly; counterfactual mutation picks the swap that MAXIMALLY CHALLENGES the claim. For threshold-mutation (C2), this means binary-searching the boundary rather than random-laddering. For C4 generalization, it means dropping the constraint most likely to flip the truth.

**Implementation sketch**:
```python
# In C2, replace random ladder choice with boundary-bisection:
def next_threshold(orig_k, value_a, value_b):
    actual_diff = abs(value_a - value_b)
    if actual_diff < orig_k:
        return actual_diff  # mutate to the exact boundary
    else:
        return actual_diff + 1  # one step past
```

Each such mutation is informationally dense: it pins down the EXACT threshold at which the claim flips.

**Cost**: Low (4–6h). Mostly upgrades to existing C-family code.

**Value**: High info_density gain. Currently C2 produces 98% kills mostly because random ladder choices land far from the boundary; counterfactual C2 would land AT the boundary, producing margin-tight records — exactly the kind D2 already prioritizes.

**Verdict**: **BUILD**. Fire #3 candidate. Already partially in the C2 v0.1 spirit; finish it.

---

## 2. Symbolic Regression (PySR / DEEP_SYMREG)

**What it is**: Algorithms that discover symbolic mathematical expressions matching numerical data. The canonical modern implementation is **PySR** (Cranmer 2023, BSD-licensed, Julia backend with Python bindings). It uses multi-population genetic programming + simulated annealing to evolve expressions; competitive with deep neural networks for finding physics laws from data.

**Theseus fit**: A-family. Direct fit for A4 (ratio invariance: "is `i(a)/j(b)` constant?"). Also A3 (functional identity: "for what `f`, `g` does `f(i(a)) == g(j(b))` hold?"). Instead of testing pre-specified relations, let SR discover symbolic expressions matching cross-catalog data.

**Implementation sketch**:
```python
from pysr import PySRRegressor
model = PySRRegressor(
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["abs", "log", "sqrt"],
    populations=20,
    niterations=40,
)
# For each (catalog_A_invariant, catalog_B_invariant) pair:
model.fit(knot_invariants, ec_invariants)
# Emit each discovered expression as a TheseusRecord
for eq in model.equations_:
    record = TheseusRecord(..., canonical_claim_text=str(eq), ...)
```

**Cost**: Medium-High (10–15h). PySR install on Windows is sometimes finicky due to Julia. Could ship a numpy-only fallback first (least-squares polynomial fit, multi-degree) for v0.1, then add PySR Tier-2.

**Value**: Very high — generates **non-obvious** relations rather than testing pre-specified ones. Could find genuine cross-catalog bridges. Frontier-aligned (Cranmer et al. found symbolic laws in dark-matter halo data; same shape as our cross-catalog problem).

**Verdict**: **BUILD**. Fire #4–5 candidate. Start with numpy polynomial-fit fallback; upgrade to PySR Tier-2 if Julia install behaves.

---

## 3. MCTS Over Claim Trees (Polu/Sutskever, AlphaGeometry)

**What it is**: Monte Carlo Tree Search with UCT (Upper Confidence Bound applied to Trees) exploration. Used in AlphaGo, AlphaZero, AlphaGeometry, and Polu/Sutskever's neural theorem proving. Builds a search tree of (claim → mutation → mutation → ...) chains, biased toward branches with high expected yield.

**Theseus fit**: D-family. Replace D1's random-neighbor walk with UCT-guided neighborhood search. D3 (triangulation seeds) is the natural fit — INCONCLUSIVE claims drive a tree expansion exploring adjacent precision/method paths.

**Implementation sketch**:
```python
class MCTSNode:
    def __init__(self, claim, parent=None):
        self.claim = claim
        self.parent = parent
        self.children: list[MCTSNode] = []
        self.visits = 0
        self.value_sum = 0.0  # accumulated info_density

    def uct_score(self, c=1.414):
        if self.visits == 0: return float("inf")
        exploit = self.value_sum / self.visits
        explore = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploit + explore
```

Selection: descend tree picking max-UCT child. Expansion: emit one mutated child. Simulation: run verification (sigma or local). Backprop: propagate info_density up.

**Cost**: Medium (8–12h) for a clean MCTS implementation. The classic algorithm is small (200 lines); the engineering work is integrating with TheseusRecord lineage.

**Value**: Medium-High. Better directed search than random walks when claim space has structure. Particularly useful for D3 (where the structure is precision × method × convergence-status, exactly the kind of small branching factor MCTS handles well).

**Verdict**: **BUILD**. Fire #5–6 candidate. Implement D3 with MCTS as v0.1.

---

## 4. Process Supervision (OpenAI / Anthropic step-level reward)

**What it is**: Score each STEP of a multi-step reasoning chain, not just the final answer. Lightman et al. *Let's Verify Step by Step* (OpenAI 2023) showed process-supervised reward models outperform outcome-supervised ones for math reasoning. Anthropic uses similar patterns in Constitutional AI.

**Theseus fit**: D3 (triangulation seeds) and the H2 (triangulation-protocol) stub. When sigma returns INCONCLUSIVE on a claim, it has typically run multiple verification paths (e.g. mpmath dps=30, dps=60, dps=100; sympy factorization; catalog lookup). Process supervision means: score each PATH separately, not just the aggregate. The info_density of the chain is its weakest link, not its terminal verdict.

**Implementation sketch**: Extend `info_density_score(record)` to consume a list of `step_records` rather than a single verdict. Each step contributes a partial score; aggregation is min (weakest link) or mean (average rigor).

**Cost**: Medium (6–8h). Requires extending TheseusRecord schema with optional `step_trace: List[StepRecord]` field, plus the aggregator.

**Value**: Medium. Aligns with substrate's already-stratified epistemics (precision/method/convergence). Surfaces "this claim passed the cheap check but failed the expensive one" patterns that get washed out in single-verdict info_density.

**Verdict**: **BUILD** (paired with MCTS for D3). Fire #6 candidate.

---

## 5. GFlowNets (Bengio et al.)

**What it is**: Generative Flow Networks — train a policy to sample objects PROPORTIONAL TO their reward, rather than maximizing reward like RL. Loss function is "flow conservation" (probability mass into a node equals mass out). Result: diverse high-reward samples instead of mode collapse. Bengio et al. *GFlowNet Foundations* (2023). The `torchgfn` library (open source) provides the standard implementation.

**Theseus fit**: Bandit replacement. EpsilonGreedyBandit (v0.1) splits between exploit-best and explore-uniform; GFlowNet samples generators proportional to their expected yield, naturally producing diversity. Once 40 generators are filled, GFlowNet would prevent the bandit from collapsing onto 2–3 high-yield generators.

**Implementation sketch**: Replace `EpsilonGreedyBandit.select()` with a `GFlowNetBandit` that maintains a learned distribution `P(generator | history)` trained to be proportional to `exp(yield_score)`. Use `torchgfn` if available; minimal pure-Python version otherwise.

**Cost**: High (20–30h). PyTorch dependency; learning curve on GFlowNet semantics.

**Value**: Medium-High once 15+ generators are active. With only 8 active, simple bandit suffices.

**Verdict**: **BUILD-LATER**. Tier 1 once 15+ generators are active. Premature now.

---

## 6. Active Learning / Uncertainty Sampling

**What it is**: When verification is expensive, prioritize examples the model is most uncertain about. Settles' *Active Learning Literature Survey* (2009) is canonical; modAL and libact are mature Python libraries.

**Theseus fit**: F3 (importance sampling) — sample from regions where substrate uncertainty is highest. Also H3 (Learner-curiosity) once Ergon resumes.

**Implementation sketch**: Maintain a per-region "uncertainty estimate" based on (a) variance of info_density of past claims in that region, (b) coverage (claims per region). Sample regions with `Pr ∝ uncertainty × (1 / coverage)`.

**Cost**: Low (4–6h). Just a weighted sampler.

**Value**: Medium. Improves yield-per-claim when verification is expensive (high-precision mpmath, full discovery_pipeline routing). v0.1 generators are cheap, so the gain is smaller initially.

**Verdict**: **BUILD**. Fire #4 candidate (paired with F3 fill).

---

## 7. Self-Play / Proposer-vs-Hunter (AlphaZero pattern)

**What it is**: Two policies playing against each other generate training data. In AlphaZero, the same network plays both sides; in math, this generalizes to a "proposer" emitting claims and a "hunter" finding counter-examples. Mukhoty et al. (NeurIPS 2023) showed self-play improves theorem-prover training data without external labels.

**Theseus fit**: New H-family generator (`h1_mutation_from_kill` elevated, or fresh `h5_self_play`). Pair every A1 with a paired "anti-A1" that hunts counter-examples to A1's surviving claims. The Hunter's job: given an A1 claim that survived, find an object pair that would have killed it.

**Implementation sketch**:
```python
class SelfPlayGenerator(Generator):
    def next(self):
        # Pick a SHADOW_CATALOG (survived) record from corpus
        survivor = self._pick_survivor()
        # Hunt: search for an (a', b') in the same catalogs such that
        # the same (i, j, relation) DOES NOT hold
        for _ in range(50):
            a_prime = self._rng.choice(self._knots)
            b_prime = self._rng.choice(self._ecs)
            if not _evaluate_relation(...):
                # Found a counter-example — emit
                return _make_record(... claim_kind="hunter_counterexample")
        return None
```

The hunter's emissions are STRUCTURALLY CONTRASTIVE — for every survivor record, a paired record showing where the relation breaks.

**Cost**: Medium (8–10h). Need a corpus reader (pull past survivors from JSONL) and the hunter search loop.

**Value**: High — self-play data is naturally contrastive, which is exactly what Ergon's Learner needs (positive + negative pairs).

**Verdict**: **BUILD**. Fire #3–4 candidate. Token-free, anti-AI-to-AI-inflation, structurally high-value.

---

## 8. Contrastive Embeddings (SimCLR / CLIP-style)

**What it is**: Learn embeddings by contrasting positive and negative pairs. Reimers & Gurevych's *sentence-transformers* library (2019, MIT-licensed) provides production-quality models. Small models (all-MiniLM-L6-v2, 22MB) embed ~10K sentences/sec on CPU.

**Theseus fit**: Diversity scoring. Replace Jaccard-token-distance (v0.1) with cosine distance over learned embeddings of `canonical_claim_text`. Better semantic diversity signal.

**Implementation sketch**:
```python
from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")

def diversity_score(record, recent):
    if not recent: return 1.0
    my_emb = _model.encode(record.canonical_claim_text)
    recent_embs = _model.encode([r.canonical_claim_text for r in recent[-50:]])
    sims = my_emb @ recent_embs.T / (norm(my_emb) * norm(recent_embs))
    return 1.0 - sims.mean()
```

**Cost**: Low (3–4h). One library install (`pip install sentence-transformers`), single function swap.

**Value**: Medium. Better cross-generator dedup signal. Jaccard misses semantic similarity (e.g., "rank vs torsion" and "rank vs tamagawa" look distant in Jaccard but might be near-duplicates semantically).

**Verdict**: **BUILD**. Fire #3 candidate. Low cost, immediately improves diversity scoring.

---

## 9. Curriculum Learning / Difficulty Estimation

**What it is**: Bengio et al. *Curriculum Learning* (ICML 2009). Rate examples by difficulty; feed easy first to bootstrap, then progressively harder.

**Theseus fit**: Meta-axis in TheseusRecord (`difficulty: float`). Generators that emit too-easy or too-hard claims relative to consumer capacity get downweighted.

**Cost**: Low.

**Value**: Genuinely depends on Ergon being live. Difficulty matters only when there's a consumer whose learning curve is shaped by example ordering.

**Verdict**: **DEFER** until Ergon resumes. The signal exists but the consumer doesn't.

---

## 10. Lean / Formal Verification as Oracle

**What it is**: Lean 4 + Mathlib as a gold-standard formal verification oracle. When sigma returns INCONCLUSIVE, hand the claim to Lean for definitive proof or refutation. AlphaGeometry uses Lean-adjacent formalizations; AlphaProof (2024) achieved Olympiad-level performance via Lean integration.

**Theseus fit**: Backup oracle for INCONCLUSIVE claims. D3 triangulation seeds that exhaust sigma's precision ladder get routed to Lean.

**Cost**: Very High (months). Lean install on Windows is involved; auto-formalization (claim text → Lean syntax) is itself an open research problem; tactic search is its own engine.

**Value**: Transformative when working. Provides ground-truth verdicts that nothing else can match.

**Verdict**: **DEFER** to Tier-3 (months from now). The lift is enormous and Theseus has cheaper wins ahead.

---

## Honorable Mentions (briefer treatment)

### 11. Bayesian Optimization (Ax / Optuna / BoTorch)
**Fit**: Per-region hyperparameter tuning. For each (catalog_A, catalog_B) pair, tune A1's invariant-pair-selection probabilities to maximize yield.
**Cost**: Medium. Optuna is the easier choice (pure Python).
**Value**: Medium. Helps once the bandit reveals which catalog pairs are productive.
**Verdict**: **BUILD-LATER** (Tier 1).

### 12. Discrete Diffusion Models
**Fit**: Tier 2-3. Bengio et al. recent work on discrete diffusion over combinatorial spaces could replace mutation generators with diffusion-guided sampling.
**Cost**: High. PyTorch + custom diffusion training.
**Value**: Unclear vs MCTS for our domain.
**Verdict**: **DEFER**. Track but don't build.

### 13. Information Bottleneck / Invariant Risk Minimization (IRM)
**Fit**: G-family symmetry/transformation generators. IRM-style penalty terms could score how well a claim's truth is invariant across catalog "environments."
**Cost**: Medium.
**Value**: Medium for G-family.
**Verdict**: **BUILD-LATER** when G-family is implemented.

### 14. Neural Theorem Proving (NTPs)
**Fit**: Precursor to MCTS-for-math; the lpolu/Sutskever line of work. Less powerful than AlphaProof but still informative.
**Cost**: High.
**Value**: Subsumed by MCTS+Lean combo.
**Verdict**: **DROP** as standalone; covered by #3 + #10.

### 15. Hypothesis-driven exploration (IRIS — Lu et al. ACL 2025)
**Fit**: Already in our reference set (`reference_iris.md`). MCTS-based hypothesis generation. Same family as #3.
**Cost**: Medium (build the IRIS-style search).
**Value**: Medium.
**Verdict**: **BUILD-LATER**. Roll into D3 / H2 work.

### 16. Quantization-aware design for precision_dps
**Fit**: Substrate-level. The precision_dps field could be optimized via training-aware quantization — log only the precisions that actually matter.
**Cost**: Low.
**Value**: Low (storage optimization, not yield).
**Verdict**: **DROP** — premature optimization.

### 17. Contrastive Decoding (Li et al. EMNLP 2023)
**Fit**: Tier-2 LLM augmentation. When using local LLM (I-family), use contrastive decoding to suppress conventional phrasings.
**Cost**: Medium.
**Value**: Medium *if* I-family generators ship.
**Verdict**: **BUILD-LATER** when I-family is active.

---

## Prioritized implementation roadmap

The full picture, sorted by fire-number priority:

### Fire #3 (next)
- **#1 Counterfactual augmentation** in C2 (boundary bisection) and prototype in C4
- **#8 Contrastive embeddings** for diversity scoring (replace Jaccard)
- **#7 Self-play H1** generator (proposer-vs-hunter)

### Fire #4
- **#6 Active learning** for F3 (importance sampling stub)
- **A3 functional identity** stub fill (deferred from Fire #2 redirect)
- **B1 operator-rotation** stub fill (deferred from Fire #2 redirect)

### Fire #5
- **#2 Symbolic regression** for A4 — numpy polynomial-fit fallback first
- **E2 arXiv mining** stub (populate local corpus + wire)

### Fire #6
- **#3 MCTS** for D3 triangulation seeds
- **#4 Process supervision** schema extension to TheseusRecord step_trace
- **B-family fills**: B2 composition, B3 inverse

### Fire #7–8 (Tier 1 transition)
- **#11 Bayesian optimization** for per-region hyperparameter tuning
- **G-family fills** (G1–G3): symmetry/transformation generators
- **#13 IRM-style** invariance scoring

### Fire #9+ (Tier 2)
- **#5 GFlowNet** bandit replacement (once 20+ generators active)
- **Local LLM (I-family)** Tier-2 deployment
- **#2 PySR** upgrade for symbolic regression

### Tier 3 (months)
- **#10 Lean** formal verification oracle
- **Frontier API J-family** surgical use

### Dropped
- **#14 NTPs** (subsumed by MCTS+Lean)
- **#16 Quantization** (premature optimization)

---

## Summary verdicts

**BUILD** (next 1–3 fires):
1. Counterfactual augmentation (C2/C4 upgrades)
7. Self-play proposer-vs-hunter (new H1 generator)
8. Contrastive embeddings (diversity scoring replacement)
6. Active learning / uncertainty sampling (F3)
2. Symbolic regression numpy fallback (A4)
3. MCTS for D3
4. Process supervision schema extension

**BUILD-LATER** (Tier 1, once foundations solidify):
5. GFlowNets bandit (needs 15+ generators)
11. Bayesian optimization (per-region tuning)
13. IRM (with G-family)
15. IRIS-style (rolled into D3/H2)
17. Contrastive decoding (with I-family)

**DEFER** (depends on something downstream):
9. Curriculum learning (depends on Ergon)
10. Lean verification (Tier 3, months out)
12. Discrete diffusion (track, don't build)

**DROP**:
14. NTPs (subsumed by MCTS+Lean)
16. Quantization-aware precision

---

## Honest caveats

- The verdicts above are based on training-knowledge of these techniques plus the existing Theseus architecture. Implementation details may surface gotchas not anticipated here (Julia install for PySR, GFlowNet convergence finickiness, etc.). Each BUILD verdict should be revisited at implementation time.
- The yield estimates ("info_density gain", "diversity gain") are qualitative. Theseus's empirical yield-curve discipline replaces them with measurement once the technique ships.
- Several techniques have learned-model components (GFlowNet, contrastive embeddings via sentence-transformers, symbolic regression's evolved expressions). These are **subordinate to substrate-native generation**, not replacements for it. The anti-AI-to-AI-inflation rule still applies: learned models help shape yield, not propose primary claims.
- The "no LLM-first" rule means even when local LLM (Family I) ships in Tier 2, it's paraphrasing only. Frontier API (Family J) is surgical-only forever.

---

*Theseus discipline: commit to a roadmap, measure yield, revisit verdicts when measurement contradicts them.*

*— Theseus, Fire #2 analysis doc, 2026-05-18*
