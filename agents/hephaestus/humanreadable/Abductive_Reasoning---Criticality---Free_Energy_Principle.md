# Abductive Reasoning + Criticality + Free Energy Principle

**Fields**: Philosophy, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:15:14.163736
**Report Generated**: 2026-04-01T20:30:32.892505

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions *pᵢ* and binary relations *r(pᵢ, pⱼ)* from the prompt and each candidate answer. Relations captured: negation (¬), conditional (→), causal (⇒), comparative (> , <, =), ordering (before/after), and numeric equality/inequality. Store propositions in a list `props` and relations in a sparse adjacency matrix `R` (numpy `int8` where 1 = present, 0 = absent).  
2. **Factor graph construction** – For each relation create a factor *fₖ* that predicts the truth value of the dependent proposition from its antecedents. A factor’s prediction error is `eₖ = (v_dep - Σ wₖᵢ·v_ant)²`, where `v` are binary truth values (0/1) and `wₖᵢ` are learned weights (initially 1 for all links).  
3. **Precision (inverse variance) as critical control** – Treat the precision matrix `Π` (diagonal, same size as number of factors) as a free‑energy hyper‑parameter. Initialize `Πᵢᵢ = 1`. After each belief‑propagation sweep compute the susceptibility χ = Var(eₖ) / ⟨eₖ⟩². Adjust `Πᵢᵢ ← Πᵢᵢ * (1 + η·(χ - χ*))` where χ* is the target susceptibility at criticality (set to the median χ of a random baseline) and η a small step (0.01). This drives the system to the point of maximal correlation length without diverging.  
4. **Belief propagation (loopy)** – Iterate: update marginal beliefs `bᵢ = sigmoid( Σⱼ Rⱼᵢ·wⱼᵢ·bⱼ )` until Δb < 1e‑4 or max 20 iterations.  
5. **Free‑energy score** – Compute variational free energy `F = Σₖ Πₖₖ·eₖ - H(b)`, where `H(b) = -Σᵢ [bᵢ log bᵢ + (1-bᵢ) log(1-bᵢ)]` is the entropy of beliefs. Lower `F` indicates a better abductive explanation.  
6. **Answer ranking** – For each candidate, inject its asserted propositions as fixed beliefs (clamp `bᵢ` to 0 or 1) and run steps 4‑5. The score is the resulting `F`; the answer with minimal `F` wins.

**Structural features parsed**  
Negations, conditionals (if‑then), causal arrows, comparatives (> , <, =), ordering relations (before/after), numeric values, and quantifiers (all/some/none) are extracted via regex patterns and turned into propositions and weighted links.

**Novelty**  
Predictive‑coding and free‑energy formulations exist in neuroscience, and criticality has been applied to neural networks, but coupling them with explicit symbolic abductive hypothesis generation in a pure‑numpy, rule‑based scorer is not present in current evaluation tools. The approach is therefore novel for text‑based reasoning assessment.

**Rating**  
Reasoning: 8/10 — captures explanatory depth via free‑energy minimization while respecting logical constraints.  
Metacognition: 7/10 — the susceptibility‑driven precision update offers a rudimentary self‑monitoring of confidence.  
Hypothesis generation: 7/10 — abductive scoring arises naturally from comparing free energies of alternative fixed‑belief sets.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and simple iterative loops; no external libraries or training needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Abductive Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Abductive Reasoning + Criticality: negative interaction (-0.080). Keep these concepts in separate code paths to avoid interference.
- Abductive Reasoning + Free Energy Principle: negative interaction (-0.071). Keep these concepts in separate code paths to avoid interference.
- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Evolution + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Architecture Search + Criticality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=27% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T10:01:28.539955

---

## Code

**Source**: scrap

[View code](./Abductive_Reasoning---Criticality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements an abductive reasoning evaluator using the Free Energy Principle (FEP) 
    and Criticality. 
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relational cues (negation, conditional, 
       causal, comparative, numeric) into a feature matrix.
    2. Factor Graph: Constructs an adjacency matrix representing logical dependencies.
    3. Variational Free Energy: Computes prediction error (consistency with premises) 
       and complexity (entropy of the hypothesis).
    4. Criticality: Calculates susceptibility to perturbations in the complexity parameter,
       rewarding hypotheses that operate near the 'edge of chaos' (high explanatory power 
       with flexible structure).
    
    Scores candidates by minimizing Free Energy while maximizing Criticality.
    """

    def __init__(self):
        self.cues = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b'],
            'causal': [r'\bbecause\b', r'\bleads?\s+to\b', r'\bcauses\b', r'\btherefore\b'],
            'comparative': [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\blesser\s+than\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b']
        }
        self.num_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text):
        """Parses text into propositions and relational cues."""
        text_lower = text.lower()
        features = []
        
        # Extract numeric values
        nums = [float(n) for n in self.num_pattern.findall(text)]
        
        # Detect cue types
        cue_types = []
        for ctype, patterns in self.cues.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    cue_types.append(ctype)
                    break
        
        # Simple sentence splitting for propositions (naive but effective for logic puzzles)
        sentences = re.split(r'[.,;]', text)
        for sent in sentences:
            if not sent.strip():
                continue
            s_lower = sent.lower()
            polarity = 0 if any(re.search(p, s_lower) for p in self.cues['negation']) else 1
            
            # Determine dominant type
            t_id = 0 # atomic
            if 'conditional' in cue_types: t_id = 1
            elif 'causal' in cue_types: t_id = 2
            elif 'comparative' in cue_types: t_id = 3
            elif 'ordering' in cue_types: t_id = 4
            
            # Numeric value (average if multiple, else 0)
            v = np.mean(nums) if nums else 0.0
            
            features.append([polarity, t_id, v, 1.0]) # bias=1.0
            
        if not features:
            return np.array([[0, 0, 0, 1]]) # Default node if empty
            
        return np.array(features)

    def _build_graph(self, X):
        """Builds adjacency matrix based on cue strength."""
        n = X.shape[0]
        if n == 0: return np.zeros((0,0))
        if n == 1: return np.zeros((1,1))
        
        A = np.zeros((n, n))
        W = np.zeros((n, n))
        
        # Connect sequential nodes with weight based on type
        for i in range(n-1):
            t = X[i, 1]
            weight = 0.5 # Default causal/logical flow
            if t == 1: weight = 0.8 # Conditional strong link
            if t == 2: weight = 0.9 # Causal strong link
            if t == 0: weight = 0.3 # Weak atomic link
            
            A[i, i+1] = 1
            W[i, i+1] = weight
            # Symmetric for undirected approximation in this simple model
            A[i+1, i] = 1
            W[i+1, i] = weight
            
        return W

    def _compute_free_energy(self, X, W, z, lam):
        """Computes F = Prediction Error + Complexity."""
        if X.shape[0] == 0:
            return 0.0
            
        # Prediction Error: ||(I - W)z - b||^2
        # b is the observed premise vector (polarity + normalized value)
        b = X[:, 0] + (X[:, 2] / 10.0) # Normalize numeric impact
        
        I = np.eye(X.shape[0])
        pred_err = np.linalg.norm((I - W) @ z - b)**2
        
        # Complexity: Entropy(z)
        eps = 1e-9
        z_safe = np.clip(z, eps, 1-eps)
        entropy = -np.sum(z_safe * np.log(z_safe) + (1-z_safe) * np.log(1-z_safe))
        complexity = lam * entropy
        
        return pred_err + complexity

    def _get_z_vector(self, prompt, candidate):
        """Generates a binary selection vector z based on overlap and logic."""
        # Combine prompt and candidate to form the hypothesis space
        full_text = f"{prompt} {candidate}"
        X = self._extract_features(full_text)
        
        # Create z: 1 if feature exists in candidate, 0 otherwise
        # Simplified: Map candidate words to feature indices
        cand_lower = candidate.lower()
        z = np.zeros(X.shape[0])
        
        # Heuristic: If candidate contains keywords found in the parsed features, activate
        # Since parsing is sentence based, we check if candidate sentence matches feature logic
        # For this implementation, we assume the candidate validates the derived propositions
        # if the candidate length is proportional to the prompt's logical depth.
        
        # Better approach for z: 
        # z_i = 1 if the i-th proposition is supported by the candidate string
        # We simulate this by checking keyword presence in candidate vs prompt segments
        
        # Fallback: Activate all nodes if candidate seems relevant (length > threshold)
        # and deactivate if candidate is "none" or "impossible"
        if re.search(r'\b(no|none|impossible|false)\b', cand_lower):
            z = np.zeros_like(z)
        else:
            z = np.ones_like(z)
            
        return z, X

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        lam_base = 0.5
        delta = 0.01
        alpha = 0.1
        
        # Pre-calculate prompt features for context
        prompt_X = self._extract_features(prompt)
        prompt_W = self._build_graph(prompt_X)

        for cand in candidates:
            z, X = self._get_z_vector(prompt, cand)
            if X.shape[0] == 0:
                score = -100.0
                reasoning = "No logical structure detected."
                results.append({"candidate": cand, "score": score, "reasoning": reasoning})
                continue

            W = self._build_graph(X)
            
            # Adjust W size if X and W dimensions mismatch due to empty handling
            if W.shape[0] != z.shape[0]:
                min_dim = min(W.shape[0], z.shape[0])
                if min_dim == 0: 
                    score = -50.0
                    results.append({"candidate": cand, "score": score, "reasoning": "Dimension mismatch."})
                    continue
                z = z[:min_dim]
                W = W[:min_dim, :min_dim]

            # 1. Compute Free Energy at lambda
            F = self._compute_free_energy(X, W, z, lam_base)
            
            # 2. Compute Susceptibility (Criticality) via finite difference
            F_shift = self._compute_free_energy(X, W, z, lam_base + delta)
            # Susceptibility chi = d<E>/dlambda approx (F_shift - F) / delta
            # Note: In FEP, we look at change in expected state. Here we approximate 
            # the sensitivity of the energy landscape.
            chi = abs(F_shift - F) / (delta + 1e-9)
            
            # Final Score: Minimize F, Maximize Chi (near criticality)
            # S = -F + alpha * chi
            final_score = -F + alpha * chi
            
            # Structural bonus: If candidate resolves numeric comparisons correctly
            nums = [float(n) for n in self.num_pattern.findall(prompt + " " + cand)]
            if len(nums) >= 2:
                # Simple consistency check: does the text imply the order?
                # This is a heuristic boost for numeric logic
                if "greater" in cand.lower() and nums[0] > nums[1]:
                    final_score += 0.5
                elif "less" in cand.lower() and nums[0] < nums[1]:
                    final_score += 0.5

            reasoning = f"F={F:.2f}, Chi={chi:.2f}, Nodes={X.shape[0]}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the score relative to a baseline."""
        # Evaluate single candidate against a dummy negative to get relative score
        res = self.evaluate(prompt, [answer, "No solution possible."])
        
        if not res:
            return 0.0
            
        top_score = res[0]['score']
        target_score = next((r['score'] for r in res if r['candidate'] == answer), -1000)
        
        # Normalize: Assume a range of -10 to 10 is typical
        # Map to 0-1
        conf = (target_score + 10) / 20.0
        return max(0.0, min(1.0, conf))
```

</details>
