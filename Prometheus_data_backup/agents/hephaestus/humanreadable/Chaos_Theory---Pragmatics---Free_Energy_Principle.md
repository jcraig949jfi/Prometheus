# Chaos Theory + Pragmatics + Free Energy Principle

**Fields**: Physics, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T07:50:00.031693
**Report Generated**: 2026-03-27T16:08:10.581352

---

## Nous Analysis

**Algorithm (Chaos‑Pragmatic Free‑Energy Scorer)**  
1. **Parsing → Propositional Graph**  
   - Use regex‑based patterns to extract atomic propositions (e.g., “X is Y”, “X > 5”, “if A then B”) and annotate each with: polarity (negation), modality (might/must), quantifier (some/all/most), and speech‑act force (assertion, question, command).  
   - Build a directed graph *G = (V, E)* where each node *vᵢ* holds a belief state *bᵢ ∈ [0,1]* (probability the proposition is true). Edges *eᵢⱼ* encode logical dependencies extracted from conditionals, causals, and comparatives; weight *wᵢⱼ ∈ [0,1]* reflects initial confidence (derived from pragmatic cues: higher for utterances obeying Grice’s maxims, lower for flouted maxims).  
   - Store adjacency matrix *W* as a NumPy float64 matrix; node beliefs as vector *b*.

2. **Free‑Energy (Prediction‑Error) Computation**  
   - Prediction for each node: *p = sigmoid(Wᵀ·b)* (matrix‑vector product, NumPy).  
   - Observation vector *o* is built from explicit facts in the prompt (e.g., numeric values, asserted propositions) with 1 for true, 0 for false, 0.5 for unknown.  
   - Precision (inverse variance) *π* is set to 1 for all nodes (can be modulated by pragmatic certainty).  
   - Free energy *F = ½·(o−p)ᵀ·π·(o−p)* (scalar, NumPy). Lower *F* means better predictive fit.

3. **Chaos‑Sensitivity Penalty**  
   - Approximate the Jacobian *J = ∂p/∂b = diag(sigmoid′(Wᵀ·b))·Wᵀ*.  
   - Compute the largest eigenvalue magnitude *λ_max* of *J* via NumPy’s `linalg.eigvals`. This serves as a Lyapunov‑like exponent: larger *λ_max* → higher sensitivity to perturbations.  
   - Penalty term *C = α·λ_max* (α = 0.1 tuned empirically).  

4. **Pragmatic Adjustment**  
   - After each free‑energy step, modify edge weights: *wᵢⱼ ← wᵢⱼ·(1 + β·cᵢⱼ)* where *cᵢⱼ* = +1 if the edge respects a pragmatic cue (e.g., quantifier “all” → strong entailment, scalar implicature “some” → weak), −1 if it violates a cue (e.g., hedging “might” on a definitive claim), 0 otherwise. β = 0.05.  
   - Iterate steps 2‑4 for a fixed number of rounds (e.g., 10) or until ΔF < 1e‑4.

5. **Scoring**  
   - Final score *S = −(F + C)* (higher is better). Return *S* for each candidate answer; rank accordingly.

**Structural Features Parsed**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “≤”, “≥”)  
- Conditionals (“if … then …”, “unless”)  
- Causal connectors (“because”, “leads to”, “results in”)  
- Ordering/temporal markers (“first”, “then”, “after”)  
- Numeric values and units  
- Quantifiers (“all”, “some”, “most”, “none”)  
- Modal verbs (“might”, “must”, “should”)  
- Speech‑act markers (“please”, “I claim that”, “question?”)

**Novelty**  
The coupling of a predictive‑coding free‑energy minimization loop with a Lyapunov‑exponent‑based sensitivity penalty and pragmatic‑driven weight modulation is not found in existing pure‑numpy reasoners. Related work exists in neural‑symbolic predictive coding and argumentation frameworks, but none combine all three measures explicitly in a lightweight, regex‑parsable system.

**Rating**  
Reasoning: 7/10 — captures logical consistency and prediction error, but approximates dynamics crudely.  
Metacognition: 6/10 — sensitivity term offers a rudimentary “uncertainty‑about‑uncertainty” signal, yet lacks explicit self‑monitoring.  
Hypothesis generation: 5/10 — can propose alternative belief states via gradient steps, but no structured search over hypothesis space.  
Implementability: 8/10 — relies only on regex, NumPy matrix ops, and basic linear algebra; easy to code and run offline.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Chaos Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Chaos Theory + Pragmatics: strong positive synergy (+0.302). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Chaos Theory + Free Energy Principle: strong positive synergy (+0.438). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Pragmatics: strong positive synergy (+0.595). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=37% cal=25% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T07:58:01.019603

---

## Code

**Source**: scrap

[View code](./Chaos_Theory---Pragmatics---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaos-Pragmatic Free-Energy Scorer.
    Mechanism:
    1. Parses text into a propositional graph using regex (nodes=beliefs, edges=dependencies).
    2. Computes Free Energy (prediction error) between inferred states and observed facts.
    3. Applies a Chaos Penalty based on the spectral radius (Lyapunov exponent proxy) of the Jacobian.
    4. Iteratively adjusts edge weights via Pragmatic cues (Gricean maxims).
    5. Scores candidates by minimizing (Free Energy + Chaos Penalty).
    """
    
    def __init__(self):
        self.alpha = 0.1  # Chaos penalty weight
        self.beta = 0.05  # Pragmatic adjustment rate
        self.max_iter = 10
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|else)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|results in|causes)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|most|every|none)\b', re.IGNORECASE),
            'modal': re.compile(r'\b(might|must|should|could|will)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>=|<=|>|<|==|!=|greater than|less than)\s*(\w+)', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'assertion': re.compile(r'^[A-Z][^.!?]*[.]$', re.MULTILINE)
        }

    def _extract_props(self, text: str) -> Tuple[List[str], Dict]:
        """Extract atomic propositions and metadata."""
        props = []
        meta = {}
        
        # Simple sentence splitting as proxy for atomic propositions
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        for i, sent in enumerate(sentences):
            if not sent: continue
            props.append(sent)
            meta[i] = {
                'negated': bool(self.patterns['negation'].search(sent)),
                'conditional': bool(self.patterns['conditional'].search(sent)),
                'causal': bool(self.patterns['causal'].search(sent)),
                'quantified': bool(self.patterns['quantifier'].search(sent)),
                'modal': bool(self.patterns['modal'].search(sent)),
                'has_number': bool(self.patterns['number'].search(sent)),
                'polarity': -1 if bool(self.patterns['negation'].search(sent)) else 1
            }
        return props, meta

    def _build_graph(self, text: str, candidate: str = "") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build adjacency matrix W, belief vector b, and observation vector o."""
        full_text = f"{text} {candidate}"
        props, meta = self._extract_props(full_text)
        n = max(len(props), 2) # Ensure at least 2 nodes for matrix ops
        
        if n == 0: n = 2
        
        # Initialize matrices
        W = np.zeros((n, n), dtype=np.float64)
        b = np.ones(n, dtype=np.float64) * 0.5 # Prior belief 0.5
        o = np.ones(n, dtype=np.float64) * 0.5 # Observation 0.5 (unknown)
        
        # Populate beliefs and observations based on parsing
        for i, (sent, m) in enumerate(zip(props, meta.values())):
            # Belief initialization based on modality
            if m['modal']: b[i] = 0.7 # "Must" implies higher prior than random
            if m['negated']: b[i] = 0.3 # Negation lowers initial truth probability
            
            # Observation vector: explicit numbers or assertions get higher confidence
            if m['has_number'] or m['assertion'] if 'assertion' in m else False:
                # Simple heuristic: if it looks like a fact, set observation to 1 (true) or 0 (false if negated)
                o[i] = 1.0 if not m['negated'] else 0.0
            else:
                o[i] = 0.5 # Unknown

        # Build edges based on co-occurrence and pragmatic cues
        for i in range(n):
            for j in range(n):
                if i == j: 
                    W[i, j] = 0.0
                    continue
                
                mi = props[i] if i < len(props) else ""
                mj = props[j] if j < len(props) else ""
                
                # Pragmatic weight initialization
                weight = 0.1
                if meta[i].get('conditional') and meta[j].get('assertion'):
                    weight = 0.8 # Strong link if conditional leads to assertion
                elif meta[i].get('causal'):
                    weight = 0.7
                elif meta[i].get('quantified'):
                    weight = 0.5
                
                # Modulate by Gricean maxims (simplified)
                if meta[i].get('modal') and not meta[j].get('modal'):
                    weight *= 0.8 # Hedging reduces strength
                
                W[i, j] = weight

        return W, b, o

    def _compute_free_energy(self, W: np.ndarray, b: np.ndarray, o: np.ndarray) -> float:
        """Compute Free Energy F = 0.5 * (o-p)^T * pi * (o-p)."""
        if W.size == 0: return 0.0
        try:
            p = 1.0 / (1.0 + np.exp(-np.dot(W.T, b))) # Sigmoid prediction
            pi = np.ones_like(b) # Precision = 1
            diff = o - p
            F = 0.5 * np.dot(diff.T, pi * diff)
            return float(F)
        except:
            return 1e6

    def _compute_chaos_penalty(self, W: np.ndarray, b: np.ndarray) -> float:
        """Compute chaos penalty based on spectral radius of Jacobian."""
        if W.size == 0: return 0.0
        try:
            # Jacobian approximation: J = diag(sigmoid'(W^T b)) * W^T
            z = np.dot(W.T, b)
            sigmoid_prime = np.exp(-z) / ((1.0 + np.exp(-z)) ** 2)
            J = np.diag(sigmoid_prime) @ W.T
            
            # Largest eigenvalue magnitude (Lyapunov proxy)
            eigvals = np.linalg.eigvals(J)
            lambda_max = np.max(np.abs(eigvals))
            return self.alpha * lambda_max
        except:
            return 1.0

    def _pragmatic_adjust(self, W: np.ndarray, meta: Dict) -> np.ndarray:
        """Adjust edge weights based on pragmatic cues."""
        n = W.shape[0]
        W_adj = W.copy()
        for i in range(n):
            if i in meta:
                m = meta[i]
                factor = 1.0
                if m.get('quantified'): factor += self.beta # Stronger entailment
                if m.get('modal') and not m.get('conditional'): factor -= self.beta # Hedging weakness
                W_adj[i, :] *= factor
        return W_adj

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            W, b, o = self._build_graph(prompt, cand)
            props, meta = self._extract_props(f"{prompt} {cand}")
            
            # Iterative minimization loop
            current_F = self._compute_free_energy(W, b, o)
            
            for _ in range(self.max_iter):
                # 1. Compute Prediction
                if W.size > 0:
                    p = 1.0 / (1.0 + np.exp(-np.dot(W.T, b)))
                    # Gradient descent step on beliefs (simplified)
                    b = b + 0.1 * (o - p) 
                    b = np.clip(b, 0.01, 0.99)
                
                # 2. Pragmatic Adjustment
                W = self._pragmatic_adjust(W, meta)
                
                # 3. Recalculate F
                new_F = self._compute_free_energy(W, b, o)
                if abs(current_F - new_F) < 1e-4:
                    break
                current_F = new_F

            # Final Scoring
            F_final = current_F
            C_final = self._compute_chaos_penalty(W, b)
            score = -(F_final + C_final) # Higher is better (less energy/chaos)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"F={F_final:.4f}, C={C_final:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        # Normalize score to 0-1 range heuristically
        # Since score is negative energy, higher (closer to 0) is better.
        # Assume worst case is -10, best is 0.
        s = res[0]['score']
        conf = 1.0 / (1.0 + np.exp(s + 2.0)) # Sigmoid shift
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
