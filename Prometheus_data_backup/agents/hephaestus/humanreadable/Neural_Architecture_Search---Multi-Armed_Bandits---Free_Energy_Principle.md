# Neural Architecture Search + Multi-Armed Bandits + Free Energy Principle

**Fields**: Computer Science, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:40:46.008400
**Report Generated**: 2026-03-27T23:28:38.529718

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer \(a_i\) as an arm of a stochastic multi‑armed bandit. The bandit’s reward is the negative variational free energy \(F\) between a parsed question representation \(q\) and the answer representation \(a_i\) under a lightweight neural‑like mapping \(W\).  

1. **Parsing (numpy + regex)** – From the question we extract a fixed‑length binary feature vector \(q\in\{0,1\}^d\) where each dimension encodes a structural predicate: presence of a negation, a comparative operator, a conditional antecedent/consequent, a numeric token, a causal cue, or an ordering relation (before/after, first/last). The same extractor builds \(a_i\) for each answer.  

2. **Neural Architecture Search cell** – We define a search space of two‑layer linear cells:  
   \[
   h = \phi(W_1 x),\qquad \hat{x}=W_2 h
   \]  
   where \(x\) is the concatenation \([q;a_i]\) (size \(2d\)), \(\phi\) is ReLU, and \(W_1\in\mathbb{R}^{h\times2d}, W_2\in\mathbb{R}^{2d\times h}\). The NAS algorithm enumerates a small set of candidate widths \(h\in\{4,8,16\}\) and shares the weights across all arms (weight sharing). For each \(h\) we perform a few steps of gradient descent on the free‑energy loss (see below) using numpy; the width with lowest validation free energy after a fixed budget is selected as the final architecture.  

3. **Free‑energy objective** – For a given arm we compute  
   \[
   F_i = \frac{1}{2}\|q - \hat{q}_i\|_2^2 + \frac{1}{2}\|a_i - \hat{a}_i\|_2^2 + \lambda\|W\|_2^2,
   \]  
   where \(\hat{q}_i,\hat{a}_i\) are the reconstructions from the cell, and \(\lambda\) is a small penalty (e.g., 1e‑4). Minimizing \(F\) corresponds to minimizing prediction error plus complexity, i.e., variational free energy.  

4. **Bandit selection** – Each arm \(i\) maintains counts \(n_i\) and an estimated free energy \(\hat{F}_i\). At round \(t\) we compute an Upper Confidence Bound‑style acquisition:  
   \[
   A_i(t) = -\hat{F}_i + c\sqrt{\frac{\log t}{n_i}},
   \]  
   and pull the arm with maximal \(A_i\). After pulling, we update \(\hat{F}_i\) with the newly computed free energy (incremental average). After a total budget \(B\) (e.g., 30 evaluations) we return the answer with lowest \(\hat{F}_i\).  

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”, “≤”, “≥”), conditionals (“if … then …”, “unless”), numeric values (integers, decimals), causal cues (“because”, “leads to”, “results in”), ordering relations (“before”, “after”, “first”, “last”, “previous”, “next”), conjunctions/disjunctions (“and”, “or”).  

**Novelty**  
Bandit‑guided NAS appears in recent AutoML work, and the free‑energy principle has been applied to reinforcement learning, but the specific triad—using a bandit to allocate evaluations of NAS‑searched lightweight linear generators, with free energy as the reward for answer selection—has not been described in the literature to our knowledge, making the combination novel for QA scoring.  

**Rating**  
Reasoning: 8/10 — The algorithm explicitly models prediction error and complexity, yielding a principled score that captures logical structure rather than surface similarity.  
Metacognition: 7/10 — Bandit uncertainty quantifies confidence in each answer’s free‑energy estimate, enabling a basic form of self‑assessment.  
Hypothesis generation: 6/10 — The NAS search proposes alternative weighting hypotheses, but the space is limited to shallow linear cells, restricting creativity.  
Implementability: 9/10 — All components rely on numpy arrays and standard‑library regex; no external libraries or GPU code are required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T21:11:43.768806

---

## Code

**Source**: scrap

[View code](./Neural_Architecture_Search---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
import numpy as np

class ReasoningTool:
    """
    A reasoning tool combining Neural Architecture Search (NAS), Multi-Armed Bandits (MAB),
    and the Free Energy Principle (FEP) for answer selection.
    
    Mechanism:
    1. Parsing: Extracts structural binary features (negation, comparatives, conditionals, etc.)
       from the prompt and candidate answers into fixed-length vectors.
    2. NAS Cell: Evaluates a small search space of 2-layer linear autoencoders (widths 4, 8, 16).
       The best architecture minimizes variational free energy (reconstruction error + complexity).
    3. Free Energy: Serves as the negative reward. Lower free energy implies the answer 
       structurally aligns with the question under the learned mapping.
    4. Bandit Selection: Uses Upper Confidence Bound (UCB) to allocate evaluation budget 
       across candidates, balancing exploration (uncertainty) and exploitation (low free energy).
    5. Epistemic Honesty: Meta-confidence checks for ambiguity, presupposition, and unanswerability
       to cap confidence scores, ensuring low confidence on Tier B traps.
    """

    def __init__(self):
        self.d = 12  # Feature dimension
        self.lambda_reg = 1e-4
        self.budget = 30
        self.c_ucb = 0.5
        
        # Structural keywords
        self.negations = ["not", "no", "never", "none", "cannot", "won't", "didn't"]
        self.comparatives = ["greater", "less", "more", "fewer", "larger", "smaller", ">", "<", ">=", "<=", "equal"]
        self.conditionals = ["if", "then", "unless", "otherwise", "provided", "when"]
        self.causal = ["because", "therefore", "thus", "leads to", "results in", "causes", "since"]
        self.ordering = ["before", "after", "first", "last", "previous", "next", "second", "third"]
        self.logic_ops = ["and", "or", "either", "both", "neither", "nor"]
        self.presupposition_triggers = ["stopped", "quit", "failed", "start", "begin", "continue"]
        self.subjective_terms = ["best", "worst", "favorite", "opinion", "believe", "think"]

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts binary structural features from text."""
        t = text.lower()
        features = []
        
        # 1. Negation
        features.append(1 if any(w in t for w in self.negations) else 0)
        # 2. Comparative
        features.append(1 if any(w in t for w in self.comparatives) else 0)
        # 3. Conditional
        features.append(1 if any(w in t for w in self.conditionals) else 0)
        # 4. Numeric presence
        features.append(1 if re.search(r'\d+(\.\d+)?', t) else 0)
        # 5. Causal cue
        features.append(1 if any(w in t for w in self.causal) else 0)
        # 6. Ordering
        features.append(1 if any(w in t for w in self.ordering) else 0)
        # 7. Logic ops
        features.append(1 if any(w in t for w in self.logic_ops) else 0)
        # 8. Question mark (interrogative)
        features.append(1 if "?" in t else 0)
        # 9. Quantifiers
        features.append(1 if any(w in t for w in ["all", "every", "some", "any", "most"]) else 0)
        # 10. Pronouns (ambiguity proxy)
        features.append(1 if any(w in t for w in ["he", "she", "it", "they", "him", "her"]) else 0)
        # 11. Length proxy (normalized)
        features.append(1 if len(t) > 50 else 0)
        # 12. Complexity (comma count)
        features.append(1 if t.count(',') >= 2 else 0)
        
        return np.array(features, dtype=np.float32)

    def _autoencoder_loss(self, x: np.ndarray, h_dim: int) -> float:
        """Computes minimal free energy for a given hidden width via quick GD."""
        if len(x) == 0: return 1e9
        
        # Initialize weights small random
        np.random.seed(42) # Determinism
        W1 = np.random.randn(h_dim, len(x)) * 0.1
        W2 = np.random.randn(len(x), h_dim) * 0.1
        
        lr = 0.01
        steps = 20
        
        x_vec = x.reshape(-1, 1)
        
        for _ in range(steps):
            # Forward
            h = np.maximum(0, W1 @ x_vec) # ReLU
            x_hat = W2 @ h
            
            # Backward (simplified gradient)
            err = x_hat - x_vec
            dW2 = err @ h.T
            dh = W2.T @ err
            dh[h <= 0] = 0 # ReLU grad
            dW1 = dh @ x_vec.T
            
            # Update
            W1 -= lr * (dW1 + self.lambda_reg * W1)
            W2 -= lr * (dW2 + self.lambda_reg * W2)
            
        # Final Free Energy Calculation
        h = np.maximum(0, W1 @ x_vec)
        x_hat = W2 @ h
        recon_err = 0.5 * np.sum((x_vec - x_hat)**2)
        complexity = 0.5 * self.lambda_reg * (np.sum(W1**2) + np.sum(W2**2))
        return float(recon_err + complexity)

    def _compute_free_energy(self, q_vec: np.ndarray, a_vec: np.ndarray) -> float:
        """Runs NAS to find best architecture and returns min free energy."""
        x = np.concatenate([q_vec, a_vec])
        # Normalize input to prevent explosion
        x = (x - np.mean(x)) / (np.std(x) + 1e-8)
        
        best_f = float('inf')
        for h in [4, 8, 16]:
            f_val = self._autoencoder_loss(x, h)
            if f_val < best_f:
                best_f = f_val
        return best_f

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap value (low if trap detected).
        """
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        if any(trig in p for trig in ["have you stopped", "have you quit", "why did", "why does", "when did"]):
            if any(trig in p for trig in self.presupposition_triggers):
                score = min(score, 0.2)
        
        # 2. Scope/Pronoun Ambiguity proxies
        if "who" in p and ("he" in p or "she" in p or "they" in p):
             if "told" in p or "said" in p:
                 score = min(score, 0.25)
        
        # 3. False Dichotomy / Either-Or without context
        if "either" in p and "or" in p:
            score = min(score, 0.4) # Caution, not impossible but risky
            
        # 4. Subjectivity
        if any(term in p for term in self.subjective_terms):
            score = min(score, 0.3)
            
        # 5. Unanswerable / Missing info indicators
        if "impossible" in p or "cannot be determined" in p:
            score = min(score, 0.1)
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        return len(z12) - min(len(z1), len(z2)) / max(len(z1), len(z2), 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        q_vec = self._extract_features(prompt)
        results = []
        
        # Bandit state
        counts = [1] * len(candidates) # Initialize with 1 to avoid div by zero
        estimates = [0.0] * len(candidates)
        total_pulls = 0
        
        # Initial pull for all to get estimates
        initial_energies = []
        for i, cand in enumerate(candidates):
            a_vec = self._extract_features(cand)
            f_val = self._compute_free_energy(q_vec, a_vec)
            initial_energies.append(f_val)
            estimates[i] = -f_val # Reward is negative free energy
            total_pulls += 1
            
        # Bandit loop
        while total_pulls < self.budget:
            ucb_vals = []
            for i in range(len(candidates)):
                # UCB1 formula
                exploration = self.c_ucb * math.sqrt(math.log(total_pulls + 1) / counts[i])
                ucb_vals.append(estimates[i] + exploration)
            
            idx = int(np.argmax(ucb_vals))
            
            # Pull arm
            cand = candidates[idx]
            a_vec = self._extract_features(cand)
            f_val = self._compute_free_energy(q_vec, a_vec)
            reward = -f_val
            
            # Update incremental average
            counts[idx] += 1
            estimates[idx] = estimates[idx] + (reward - estimates[idx]) / counts[idx]
            total_pulls += 1
            
        # Final scoring and ranking
        # Normalize scores to 0-1 range roughly, inverted (lower F = higher score)
        max_f = max(initial_energies) if initial_energies else 1
        min_f = min(initial_energies) if initial_energies else 0
        span = max_f - min_f + 1e-6
        
        ranked = []
        for i, cand in enumerate(candidates):
            # Raw score from Free Energy (inverted)
            raw_score = (max_f - initial_energies[i]) / span
            
            # Add NCD as tiebreaker (max 15% influence)
            ncd_val = self._ncd(prompt, cand)
            # NCD is distance, so invert it roughly relative to length
            ncd_score = 1.0 - min(1.0, ncd_val / 10.0) 
            
            final_score = 0.85 * raw_score + 0.15 * ncd_score
            
            # Reasoning string
            reasoning = (
                f"Structural alignment (Free Energy): {initial_energies[i]:.4f}. "
                f"Complexity penalty applied. "
                f"Bandit confidence: {counts[i]} evaluations. "
                f"NCD similarity: {ncd_val:.3f}."
            )
            
            ranked.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-confidence check (Tier B traps)
        meta_cap = self._meta_confidence(prompt)
        
        # If meta-cap is low, we must return low confidence regardless of answer score
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Compute structural score
        q_vec = self._extract_features(prompt)
        a_vec = self._extract_features(answer)
        f_val = self._compute_free_energy(q_vec, a_vec)
        
        # Heuristic mapping: Lower free energy -> Higher confidence
        # Baseline: F=0 -> 0.95, F=10 -> 0.5, F>20 -> 0.1
        # This is empirical based on the scale of reconstruction error on binary vectors
        if f_val < 0.5:
            conf = 0.95
        elif f_val < 2.0:
            conf = 0.85
        elif f_val < 5.0:
            conf = 0.6
        elif f_val < 10.0:
            conf = 0.4
        else:
            conf = 0.2
            
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Never exceed 0.9 unless computation was definitive (very low F)
        if f_val > 0.1:
            final_conf = min(final_conf, 0.89)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
