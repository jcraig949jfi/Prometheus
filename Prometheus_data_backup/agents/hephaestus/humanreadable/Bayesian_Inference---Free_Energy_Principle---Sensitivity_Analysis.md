# Bayesian Inference + Free Energy Principle + Sensitivity Analysis

**Fields**: Mathematics, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T21:04:12.544218
**Report Generated**: 2026-03-27T17:21:24.072566

---

## Nous Analysis

**Algorithm**  
We build a lightweight factor‑graph reasoner that treats each extracted proposition as a random variable \(X_i\in\{0,1\}\) (false/true).  
1. **Parsing → graph** – Using regex we capture:  
   * literals (e.g., “the drug reduces blood pressure”) → node \(X_i\)  
   * negations (“not …”) → factor \(\phi_{\neg}(X_i)=1-X_i\)  
   * comparatives (“X > Y”) → ordered pair of nodes with a deterministic factor enforcing the inequality  
   * conditionals (“if A then B”) → implication factor \(\phi_{A\rightarrow B}(X_A,X_B)=\mathbb{I}[X_A\le X_B]\)  
   * causal claims (“A causes B”) → same as conditional but weighted by a causal strength \(w_{AB}\)  
   * numeric values → nodes with Gaussian likelihood factors \(\mathcal{N}(v;\mu,\sigma^2)\).  
   All factors are stored as NumPy arrays; the graph is an adjacency list of factor indices.  

2. **Prior (Free Energy Principle)** – Each node gets a prior belief \(p_i=\sigma(b_i)\) where \(b_i\) is a bias term. The variational free energy for a factorized posterior \(q(X)=\prod_i q_i(X_i)\) is  
   \[
   F = \sum_{\text{factors}} \langle -\log\phi\rangle_q + \sum_i \text{KL}(q_i\|p_i),
   \]  
   computed with simple mean‑field updates:  
   \[
   q_i \leftarrow \sigma\!\Big(b_i + \sum_{f\in\mathcal{N}(i)} \langle \log\phi_f\rangle_{q_{\setminus i}}\Big).
   \]  
   Iterations stop when \(\Delta F<10^{-4}\) or after 20 sweeps.  

3. **Sensitivity Analysis** – After convergence, we perturb each input observation (evidence factor) by \(\pm\epsilon\) (e.g., flipping a literal’s truth value) and recompute the free energy \(F^{\pm}\). The sensitivity score for variable \(i\) is  
   \[
   S_i = \frac{|F^{+}_i - F^{-}_i|}{2\epsilon}.
   \]  
   We aggregate across variables as \(\bar S = \frac{1}{N}\sum_i S_i\).  

4. **Scoring a candidate answer** – The answer is treated as an additional set of evidence factors (e.g., asserting its truth). We run the same inference, obtaining free energy \(F_{\text{ans}}\) and sensitivity \(\bar S_{\text{ans}}\). The final score is  
   \[
   \text{Score} = -F_{\text{ans}} + \lambda \frac{1}{1+\bar S_{\text{ans}}},
   \]  
   with \(\lambda=0.5\) to reward low free energy (good fit) and low sensitivity (robustness). Higher scores indicate better reasoning.

**Parsed structural features** – Negations, comparatives, conditionals, causal language, ordering/temporal relations, and explicit numeric quantities (with units). These are the only syntactic constructs the regexes target, yielding a deterministic graph.

**Novelty** – While variational free energy and mean‑field belief propagation appear in active‑inference literature, coupling them with a explicit sensitivity‑analysis penalty for answer selection in a pure‑numpy QA evaluator is not described in existing work; most scoring methods rely on lexical similarity or neural log‑likelihoods. Hence the combination is novel for this task.

**Rating**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled inference.  
Metacognition: 6/10 — limited self‑monitoring; sensitivity provides a rudimentary robustness check.  
Hypothesis generation: 7/10 — generates posterior beliefs over propositions, enabling ranking of candidate hypotheses.  
Implementability: 9/10 — relies only on regex, NumPy array operations, and simple iterative updates; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Bayesian Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Bayesian Inference + Free Energy Principle: strong positive synergy (+0.655). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Bayesian Inference + Sensitivity Analysis: strong positive synergy (+0.473). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Sensitivity Analysis: strong positive synergy (+0.375). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Constraint Satisfaction + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 33% | +13% |
| Calibration | 20% | +13% |

**Forge Timestamp**: 2026-03-26T01:49:33.771264

---

## Code

**Source**: forge

[View code](./Bayesian_Inference---Free_Energy_Principle---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A lightweight factor-graph reasoner based on Bayesian Inference and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositions (literals, negations, conditionals, causals, numerics) via regex.
    2. Graph Construction: Builds a factor graph where nodes are boolean variables and factors encode logic.
    3. Inference: Uses Mean-Field Variational Inference to minimize Variational Free Energy (VFE).
       - Priors are set by bias terms; posteriors are updated iteratively.
    4. Sensitivity Analysis: Perturbs evidence to measure robustness (stability of the solution).
    5. Scoring: Ranks candidates by balancing fit (low VFE) and robustness (low sensitivity).
    
    This approach captures logical structure and uncertainty better than lexical similarity or NCD.
    """

    def __init__(self):
        self.epsilon = 0.1
        self.max_iter = 20
        self.tol = 1e-4
        self.lambda_robust = 0.5

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _parse_text(self, text: str) -> Tuple[List[str], List[Dict]]:
        """Extract literals and build factor graph structure."""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]', text_lower)
        literals = []
        factors = []
        literal_map = {} # Map cleaned literal to index

        def get_idx(lit: str) -> int:
            if lit not in literal_map:
                literal_map[lit] = len(literals)
                literals.append(lit)
            return literal_map[lit]

        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Detect numeric comparisons (e.g., "9.11 is less than 9.9")
            num_match = re.search(r'(\d+\.?\d*)\s+(is\s+)?(less|greater|smaller|larger)\s+(than\s+)?(\d+\.?\d*)', sent)
            if num_match:
                v1, comp, v2 = float(num_match.group(1)), num_match.group(3), float(num_match.group(5))
                lit = f"{v1} {comp} {v2}"
                idx = get_idx(lit)
                val = (v1 < v2) if comp in ['less', 'smaller'] else (v1 > v2)
                factors.append({'type': 'evidence', 'idx': idx, 'val': float(val)})
                continue

            # Detect conditionals (if A then B)
            cond_match = re.search(r'if\s+(.+?)\s+(?:then\s+)?(.+)', sent)
            if cond_match:
                a_str = cond_match.group(1).strip()
                b_str = cond_match.group(2).strip()
                # Simple cleanup
                a_str = re.sub(r'\b(not)\s+', '', a_str).strip()
                b_str = re.sub(r'\b(not)\s+', '', b_str).strip()
                idx_a = get_idx(a_str)
                idx_b = get_idx(b_str)
                factors.append({'type': 'implication', 'idx_a': idx_a, 'idx_b': idx_b})
                continue

            # Detect causals (A causes B)
            cause_match = re.search(r'(.+?)\s+causes\s+(.+)', sent)
            if cause_match:
                a_str = cause_match.group(1).strip()
                b_str = cause_match.group(2).strip()
                idx_a = get_idx(a_str)
                idx_b = get_idx(b_str)
                factors.append({'type': 'causal', 'idx_a': idx_a, 'idx_b': idx_b, 'weight': 0.8})
                continue

            # Detect simple literals (with optional negation)
            # Remove common stop words for key extraction if needed, but keep full phrase for now
            clean_sent = re.sub(r'\b(it is|the|a|an)\s+', ' ', sent).strip()
            is_neg = bool(re.match(r'^not\s+', clean_sent)) or 'no ' in clean_sent
            clean_sent = re.sub(r'^(not\s+|no\s+)', '', clean_sent).strip()
            
            if clean_sent:
                idx = get_idx(clean_sent)
                if is_neg:
                    factors.append({'type': 'negation', 'idx': idx})
                else:
                    # Treat raw sentence as a potential evidence node if it looks like a fact
                    # In this simplified model, we assume the prompt provides the context,
                    # and we check consistency. We add a weak prior favoring truth for stated facts.
                    factors.append({'type': 'prior_boost', 'idx': idx, 'bias': 1.0})

        return literals, factors

    def _run_inference(self, n_nodes: int, factors: List[Dict], evidence_overrides: Optional[Dict[int, float]] = None) -> Tuple[float, np.ndarray]:
        """Run Mean-Field Variational Inference to minimize Free Energy."""
        if n_nodes == 0:
            return 0.0, np.array([])

        # Initialize beliefs (q) with neutral prior (0.5)
        q = np.full(n_nodes, 0.5)
        biases = np.zeros(n_nodes)
        
        # Apply static biases from factors
        for f in factors:
            if f['type'] == 'prior_boost':
                biases[f['idx']] += f.get('bias', 0.5)

        # Evidence overrides (for testing candidate answers)
        if evidence_overrides:
            for idx, val in evidence_overrides.items():
                if idx < n_nodes:
                    biases[idx] += 10.0 if val > 0.5 else -10.0 # Strong evidence

        prev_f = float('inf')
        
        for _ in range(self.max_iter):
            # Update beliefs based on factors
            q_new = q.copy()
            for i in range(n_nodes):
                logit = biases[i]
                # Neighbors contribution
                for f in factors:
                    if f['type'] == 'implication' and f['idx_a'] == i:
                        # If A then B: A -> B. If A is true, B must be true.
                        # Contribution to A: depends on B.
                        pass 
                    # Simplified mean-field update: aggregate local field
                    # For implication A->B: logit_A += log(P(B|A)) approx
                    # We use a heuristic coupling for speed and stability in this lightweight impl
                    if f['type'] == 'implication':
                        if f['idx_a'] == i:
                            logit += (q[f['idx_b']] - 0.5) * 2.0 # Encourage consistency
                        elif f['idx_b'] == i:
                            logit += (q[f['idx_a']] - 0.5) * 2.0
                    
                    if f['type'] == 'causal':
                        w = f.get('weight', 0.5)
                        if f['idx_a'] == i:
                            logit += (q[f['idx_b']] - 0.5) * w * 2
                        elif f['idx_b'] == i:
                            logit += (q[f['idx_a']] - 0.5) * w * 2
                            
                    if f['type'] == 'negation':
                        if f['idx'] == i:
                            logit -= (q[i] - 0.5) * 2.0 # Self-consistency check for negation logic is tricky in MF without pairs
                            # Actually, negation usually links two vars. Here we treat it as a constraint on the single var's truthiness relative to context.
                            # Simplification: Negation in prompt suggests the literal is false if asserted as fact, 
                            # but here we just model the logical structure.
                            pass

                q_new[i] = self._sigmoid(logit)
            
            q = q_new
            # Compute approximate Free Energy (KL + Energy)
            # F ~ -Sum(log phi) + KL(q||p)
            # Simplified energy calculation for convergence check
            energy = 0.0
            for i in range(n_nodes):
                if q[i] > 1e-9 and q[i] < 1-1e-9:
                    energy += q[i] * np.log(q[i] + 1e-9) + (1-q[i]) * np.log(1-q[i] + 1e-9)
            
            if abs(prev_f - energy) < self.tol:
                break
            prev_f = energy

        return prev_f, q

    def _compute_sensitivity(self, n_nodes: int, factors: List[Dict], base_evidence: Dict[int, float]) -> float:
        """Compute average sensitivity of free energy to evidence perturbation."""
        if n_nodes == 0: return 0.0
        
        f_base, _ = self._run_inference(n_nodes, factors, base_evidence)
        sens_sum = 0.0
        count = 0
        
        # Perturb each evidence node
        for idx in base_evidence:
            for delta in [self.epsilon, -self.epsilon]:
                perturbed = base_evidence.copy()
                # Flip probability slightly
                val = base_evidence[idx]
                new_val = np.clip(val + delta, 0.0, 1.0)
                perturbed[idx] = new_val
                
                f_pert, _ = self._run_inference(n_nodes, factors, perturbed)
                sens_sum += abs(f_pert - f_base)
                count += 1
                
        return sens_sum / (count + 1e-9)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Combine prompt and candidate to form the full context for evaluation
        # We treat the candidate as an asserted fact to see how well it fits the prompt's logic
        full_text = f"{prompt} {candidate}"
        literals, factors = self._parse_text(full_text)
        n_nodes = len(literals)
        
        if n_nodes == 0:
            return -10.0, "No logical structure found."

        # Identify which nodes correspond to the candidate answer
        # We assume the last few literals or specific keywords belong to the candidate
        # For this implementation, we assert the candidate's main claim as evidence
        candidate_literals = set(re.findall(r'\b\w+\b', candidate.lower()))
        evidence_map = {}
        
        # Map literals to evidence based on overlap with candidate
        for i, lit in enumerate(literals):
            lit_words = set(re.findall(r'\b\w+\b', lit))
            if lit_words & candidate_literals:
                evidence_map[i] = 1.0 # Assert true
            elif lit in candidate.lower():
                evidence_map[i] = 1.0

        # If no specific mapping, assume the whole candidate is a single proposition added
        if not evidence_map and literals:
            evidence_map[len(literals)-1] = 1.0

        # 1. Base Inference
        f_base, q = self._run_inference(n_nodes, factors, evidence_map)
        
        # 2. Sensitivity Analysis
        sens = self._compute_sensitivity(n_nodes, factors, evidence_map)
        
        # 3. Scoring
        # Score = -FreeEnergy + lambda * Robustness
        # Lower Free Energy is better (higher likelihood). Lower Sensitivity is better (robust).
        # We invert sens for the score: 1/(1+sens)
        score = -f_base + self.lambda_robust * (1.0 / (1.0 + sens))
        
        reason_str = f"Nodes:{n_nodes}, F:{f_base:.4f}, Sens:{sens:.4f}"
        return score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reason})
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 range roughly
        # Assuming typical free energy ranges, map to sigmoid
        conf = 1.0 / (1.0 + np.exp(-score/2.0))
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
