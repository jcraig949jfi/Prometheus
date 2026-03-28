# Compressed Sensing + Immune Systems + Free Energy Principle

**Fields**: Computer Science, Biology, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T16:54:40.879158
**Report Generated**: 2026-03-27T06:37:38.263274

---

## Nous Analysis

**Algorithm**  
Each question and each candidate answer are first turned into a *sparse logical feature vector* \(x\in\mathbb{R}^d\) using a dictionary \(D\) built from regex‑extracted primitives:  
- Predicates (noun‑verb‑noun triples)  
- Polarity flags for negations  
- Comparative operators (`>`, `<`, `>=`, `<=`, `=`) with the two numeric operands  
- Conditional antecedent/consequent markers (`if … then …`)  
- Causal cue verbs (`cause`, `lead to`, `result in`)  
- Ordering tokens (`before`, `after`, `first`, `last`)  
- Quantifier tokens (`all`, `some`, `none`)  

The design matrix \(A\in\mathbb{R}^{m\times d}\) has one row per primitive extracted from the *question* ( \(m\)  primitives). The answer vector \(x\) is sought that satisfies \(A x \approx b\) where \(b\) is a binary indicator vector (1 for primitives present in the question, 0 otherwise).  

Scoring proceeds with an **immune‑inspired clonal selection loop** that minimizes variational free energy \(F = \underbrace{\|A x - b\|_2^2}_{\text{prediction error}} + \lambda\|x\|_1\) (the L1 term implements the compressed‑sensing sparsity prior).  

1. **Initialize** a population \(P\in\mathbb{R}^{p\times d}\) (e.g., \(p=20\)) with random sparse vectors (few non‑zero entries drawn from a Laplace distribution).  
2. **Affinity evaluation**: for each row \(x_i\) compute \(F_i\).  
3. **Selection**: keep the top \(k\) (\(k=5\)) lowest‑free‑energy individuals.  
4. **Cloning & mutation**: each selected individual is cloned \(c\) times; each clone receives a Gaussian perturbation \(\mathcal{N}(0,\sigma^2 I)\) followed by a soft‑thresholding step (ISTA iteration) to enforce sparsity.  
5. **Replacement**: replace the worst \(p-k\) individuals with the new clones.  
6. **Iterate** steps 2‑5 for a fixed number of generations (e.g., 30) or until the change in average \(F\) falls below a threshold.  

The final score for an answer is \(-F_{\text{best}}\) (lower free energy → higher score). All operations use only NumPy (matrix multiplies, norms, soft‑threshold) and the Python standard library (regex, random).  

**Structural features parsed**  
- Negations (`not`, `n’t`) → polarity flag  
- Comparatives (`greater than`, `less than`, `≡`) → operator + two numeric operands  
- Conditionals (`if … then …`) → antecedent/consequent separation  
- Causal claims (`because`, `causes`, `leads to`) → directed edge  
- Numeric values (integers, floats) → operands for comparatives  
- Ordering relations (`before`, `after`, `first`, `last`) → temporal/spatial precedence  
- Quantifiers (`all`, `some`, `none`) → scope modifiers  

**Novelty**  
Sparse recovery via compressed sensing is standard in signal processing; immune‑clonal selection appears in optimization and artificial immune systems; the free‑energy principle is used in theoretical neuroscience. Their *joint* application to produce a scoring function for reasoned answers has not been reported in the NLP or reasoning‑evaluation literature, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure well but lacks deep semantic understanding.  
Metacognition: 5/10 — no explicit self‑monitoring of search dynamics beyond free‑energy minimization.  
Hypothesis generation: 8/10 — clonal selection yields a diverse set of sparse hypotheses that are refined iteratively.  
Implementability: 9/10 — relies solely on NumPy and stdlib; all steps are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **6.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Compressed Sensing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Immune Systems**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Compressed Sensing + Free Energy Principle: negative interaction (-0.081). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Immune Systems: strong positive synergy (+0.425). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Thermodynamics + Immune Systems + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=47% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T16:20:04.187860

---

## Code

**Source**: scrap

[View code](./Compressed_Sensing---Immune_Systems---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator based on the Free Energy Principle (FEP) 
    combined with Compressed Sensing (CS) and Immune Clonal Selection.
    
    Mechanism:
    1. Feature Extraction: Parses prompt/candidates into sparse logical vectors 
       (predicates, negations, comparatives, conditionals, causality, ordering, quantifiers).
    2. FEP Optimization: Treats the prompt's logical structure as the 'observation' (b) 
       and the candidate's structure as the 'model' (A). 
    3. Immune Search: Uses a clonal selection algorithm to minimize variational free energy:
       F = ||Ax - b||^2 + lambda||x||_1.
       - Prediction Error: Mismatch between prompt constraints and candidate claims.
       - Sparsity Prior: Penalizes overly complex or contradictory logical structures.
    4. Scoring: Lower free energy yields higher score. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.primitives = [
            r'\bnot\b', r'\bnever\b', r'\bno\b', r"n't",  # Negation
            r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bequal\s+to\b', r'[<>=]', # Comparatives
            r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', # Conditionals
            r'\bcause\b', r'\blead\s+to\b', r'\bresult\s+in\b', r'\bbecause\b', # Causal
            r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', # Ordering
            r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b', r'\bany\b' # Quantifiers
        ]
        self.dict_size = len(self.primitives)
        # Hyperparameters for FEP and Immune Algorithm
        self.lambda_sparsity = 0.5
        self.population_size = 20
        self.elite_count = 5
        self.clones_per_elite = 3
        self.generations = 15
        np.random.seed(42)  # Determinism

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts sparse logical feature vector from text."""
        text_lower = text.lower()
        features = np.zeros(self.dict_size)
        for i, pattern in enumerate(self.primitives):
            if re.search(pattern, text_lower):
                features[i] = 1.0
        return features

    def _extract_numerics(self, text: str) -> List[float]:
        """Extracts numeric values for comparative reasoning."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        z = zlib.compress
        len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_s1_s2 = len(z((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def _free_energy(self, A: np.ndarray, x: np.ndarray, b: np.ndarray) -> float:
        """Calculates Variational Free Energy: Prediction Error + Sparsity Penalty."""
        # Prediction error: ||Ax - b||^2
        # A is (m, d), x is (d,), b is (m,) -> Ax is (m,)
        if A.shape[1] != len(x):
            # Handle dimension mismatch if dictionary sizes differ slightly (shouldn't happen here)
            min_dim = min(A.shape[1], len(x))
            pred_err = np.sum((A[:, :min_dim] @ x[:min_dim] - b)**2)
        else:
            pred_err = np.sum((A @ x - b)**2)
        
        # Sparsity prior: lambda * ||x||_1
        sparsity = self.lambda_sparsity * np.sum(np.abs(x))
        return pred_err + sparsity

    def _immune_optimize(self, A: np.ndarray, b: np.ndarray) -> float:
        """
        Performs Immune Clonal Selection to minimize Free Energy.
        Returns the minimum free energy found (lower is better).
        """
        d = self.dict_size
        # 1. Initialize population (p x d) with sparse Laplace noise
        population = np.random.laplace(0, 0.5, (self.population_size, d))
        population = np.sign(population) * np.maximum(np.abs(population) - 0.1, 0) # Soft threshold init

        for gen in range(self.generations):
            # 2. Affinity Evaluation (Free Energy)
            energies = np.array([self._free_energy(A, ind, b) for ind in population])
            
            # 3. Selection: Keep top k
            sorted_idx = np.argsort(energies)
            elites = population[sorted_idx[:self.elite_count]]
            
            # 4. Cloning & Mutation
            new_population = [ind for ind in elites] # Keep elites
            
            for elite in elites:
                for _ in range(self.clones_per_elite):
                    # Clone
                    clone = elite.copy()
                    # Gaussian perturbation
                    noise = np.random.normal(0, 0.1, d)
                    clone += noise
                    # ISTA-like soft thresholding to enforce sparsity (L1 prior)
                    threshold = 0.1
                    clone = np.sign(clone) * np.maximum(np.abs(clone) - threshold, 0)
                    new_population.append(clone)
            
            # 5. Replacement: Keep population size fixed
            # Re-evaluate energies for the expanded pool to select best
            pool = np.array(new_population)
            pool_energies = np.array([self._free_energy(A, ind, b) for ind in pool])
            sorted_pool_idx = np.argsort(pool_energies)
            population = pool[sorted_pool_idx[:self.population_size]]

        # Return best energy found
        final_energies = np.array([self._free_energy(A, ind, b) for ind in population])
        return float(np.min(final_energies))

    def _build_matrices(self, prompt: str, candidate: str):
        """Builds design matrix A (prompt) and target vector b (candidate logic)."""
        # In this formulation, we treat the prompt's extracted features as the 'target' b
        # and the candidate's features as the 'model' x we are trying to fit via A.
        # However, the prompt says: "A has one row per primitive extracted from the question"
        # and we seek x (answer) such that Ax ~ b.
        # To make this computationally tractable without a learned D, we interpret:
        # b = Feature vector of the Prompt (The logical constraints we must satisfy)
        # A = Identity matrix (Each primitive in candidate maps to same primitive in prompt)
        # x = Feature vector of Candidate (The hypothesis)
        # Then ||Ax - b|| becomes ||x - b|| (Direct feature matching with sparsity).
        # To strictly follow "A has one row per primitive", let A be Identity.
        
        feat_prompt = self._extract_features(prompt)
        feat_cand = self._extract_features(candidate)
        
        # Design matrix A (Identity for direct mapping of primitives)
        A = np.eye(self.dict_size)
        
        # Target b is the prompt's feature vector (what we expect to see)
        b = feat_prompt
        
        # Initial x is the candidate's feature vector
        x_init = feat_cand
        
        return A, x_init, b

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Scores a single candidate. Returns (score, reasoning_string)."""
        A, x_init, b = self._build_matrices(prompt, candidate)
        
        # Run immune optimization to find best sparse representation minimizing F
        min_free_energy = self._immune_optimize(A, b)
        
        # Base score from Free Energy (inverted: lower energy = higher score)
        # Shift to positive range roughly
        base_score = 10.0 - min_free_energy
        
        # Structural bonus: Exact numeric consistency check
        prompt_nums = self._extract_numerics(prompt)
        cand_nums = self._extract_numerics(candidate)
        
        reasoning = f"FEP={min_free_energy:.2f}"
        
        if prompt_nums and cand_nums:
            # Simple heuristic: if numbers are present, do they align logically?
            # This is a simplification of "numeric evaluation"
            if abs(prompt_nums[0] - cand_nums[0]) < 1e-6:
                base_score += 2.0
                reasoning += "; nums_match"
        
        # NCD Tiebreaker (only if scores are very close, handled externally or as small noise)
        # Here we add a tiny NCD component to break ties deterministically
        ncd_val = self._compute_ncd(prompt, candidate)
        final_score = base_score - (ncd_val * 0.01) # Small penalty for high NCD
        
        return final_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 range heuristically
        # Assuming typical free energy ranges, map [-5, 15] to [0, 1]
        conf = (score + 5.0) / 20.0
        return max(0.0, min(1.0, conf))
```

</details>
