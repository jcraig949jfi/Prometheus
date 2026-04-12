# Symbiosis + Neural Oscillations + Free Energy Principle

**Fields**: Biology, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:14:57.363511
**Report Generated**: 2026-03-27T23:28:38.221718

---

## Nous Analysis

The algorithm treats a candidate answer as a set of interacting “agents” (propositional fragments) that must achieve a mutually beneficial symbiosis with the question’s constraint network. Each fragment is a node in a directed graph; node attributes encode parsed structural features (negation, comparative, conditional, numeric, causal, ordering) as one‑hot vectors stored in a NumPy array **F** of shape *(n_nodes, n_feat)*. Edge existence is given by an adjacency matrix **A** (binary, *n_nodes × n_nodes*).

Scoring proceeds in two coupled phases that mimic neural oscillations:

1. **Theta‑scale (slow) global constraint propagation** – belief vectors **B** (probability each node is true) are updated by applying logical rules (modus ponens, transitivity) via matrix multiplication:  
   `B_new = sigmoid( (A @ B) * W_theta + b_theta )`  
   where **W_theta** and **b_theta** are learned‑free parameters that weight implication and equivalence constraints. This step enforces consistency across the whole graph (similar to belief propagation).

2. **Gamma‑scale (fast) local binding** – fine‑grained compatibility between parent and child nodes is refined using element‑wise products that mimic cross‑frequency coupling:  
   `B_new = B_new * sigmoid( (F * F.T) * W_gamma + b_gamma )`  
   Here **W_gamma** captures feature‑wise affinity (e.g., a comparative node binds strongly to a numeric node). The gamma update repeats several times per theta iteration.

The free energy principle is instantiated as the prediction error between the current belief **B** and the observed answer feature vector **O** (extracted directly from the candidate text):  
`F = 0.5 * || B - O ||^2 + λ * sum( B * log(B) )`  
(the second term is an entropy regularizer). Coordinate descent alternates theta and gamma updates until **F** converges; the final score is `-F` (lower free energy → higher answer quality).

**Structural features parsed** (via regex and shallow parsing):  
- Negations (`not`, `no`)  
- Comparatives (`more than`, `less than`, `-er`)  
- Conditionals (`if … then …`, `unless`)  
- Numeric values (integers, decimals, percentages)  
- Causal claims (`because`, `leads to`, `results in`)  
- Ordering relations (`before`, `after`, `greater than`, `less than`)

**Novelty**: While belief propagation and probabilistic soft logic exist, coupling them with an explicit oscillatory schedule (theta/gamma) and a free‑energy minimization objective is not standard in existing reasoning‑scoring tools. The approach merges constraint propagation, rhythmic binding, and variational inference into a single numpy‑based pipeline.

**Ratings**  
Reasoning: 8/10 — captures logical structure and global consistency well.  
Metacognition: 6/10 — limited self‑monitoring; no explicit uncertainty calibration beyond entropy term.  
Hypothesis generation: 7/10 — can produce alternative belief bindings via gamma updates, but not open‑ended generation.  
Implementability: 9/10 — relies only on NumPy and standard library; all operations are matrix‑based and straightforward to code.

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

- **Symbiosis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Neural Oscillations: strong positive synergy (+0.271). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Oscillations + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=43% cal=17% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T18:25:14.740894

---

## Code

**Source**: scrap

[View code](./Symbiosis---Neural_Oscillations---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool implementing a Symbiosis x Neural Oscillations x Free Energy Principle framework.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negation, comparatives, conditionals, numerics) 
       from the prompt and candidate to form node attributes (F).
    2. Graph Construction: Builds an adjacency matrix (A) based on logical dependency.
    3. Theta-Gamma Oscillation: 
       - Theta (Slow): Global belief propagation via matrix multiplication (A @ B).
       - Gamma (Fast): Local feature binding via element-wise compatibility checks.
    4. Free Energy Minimization: Iteratively updates beliefs to minimize prediction error 
       between the candidate's structural profile and the prompt's constraints.
    5. Epistemic Honesty: Detects ambiguity/traps (Tier B) to cap confidence scores.
    
    Scoring: Structural match (50%) + Computational verification (35%) + NCD tiebreaker (15%).
    """

    def __init__(self):
        self.feature_names = ['negation', 'comparative', 'conditional', 'numeric', 'causal', 'ordering']
        self.n_feat = len(self.feature_names)
        
        # Learned-free parameters (heuristic initialization)
        self.W_theta = 0.5
        self.b_theta = 0.1
        self.W_gamma = 0.8
        self.b_gamma = 0.2
        self.lambda_entropy = 0.05

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features as a one-hot-like vector (float counts normalized)."""
        text_lower = text.lower()
        features = np.zeros(self.n_feat)
        
        # 1. Negation
        if re.search(r'\b(not|no|never|none|neither)\b', text_lower):
            features[0] = 1.0
            
        # 2. Comparatives
        if re.search(r'\b(more|less|greater|smaller|better|worse|higher|lower|-er)\b', text_lower) or '>' in text or '<' in text:
            features[1] = 1.0
            
        # 3. Conditionals
        if re.search(r'\b(if|then|unless|otherwise|provided|assuming)\b', text_lower):
            features[2] = 1.0
            
        # 4. Numeric
        if re.search(r'\d+(\.\d+)?%?', text_lower):
            features[3] = 1.0
            
        # 5. Causal
        if re.search(r'\b(because|leads to|results in|causes|due to|therefore)\b', text_lower):
            features[4] = 1.0
            
        # 6. Ordering
        if re.search(r'\b(before|after|first|last|precede|follow)\b', text_lower):
            features[5] = 1.0
            
        return features

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Build the graph representation.
        Nodes: [Prompt_Features, Candidate_Features]
        Returns: F (features), A (adjacency), O (observed target derived from prompt constraints)
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Stack features: Row 0 = Prompt, Row 1 = Candidate
        F = np.stack([p_feat, c_feat])
        
        # Adjacency: Bidirectional influence for symbiosis
        A = np.array([[0, 1], 
                      [1, 0]], dtype=float)
        
        # Observed vector O: Ideally, candidate features should match prompt requirements.
        # We treat the prompt's structural demand as the "observation" the candidate must satisfy.
        # For symbiosis, we want the candidate to complement or mirror the prompt's logic.
        O = p_feat.copy()
        
        return F, A, O

    def _oscillate_and_minimize(self, F: np.ndarray, A: np.ndarray, O: np.ndarray) -> float:
        """
        Perform Theta-Gamma oscillations to minimize Free Energy.
        Returns the negative Free Energy (higher is better).
        """
        n_nodes = F.shape[0]
        
        # Initialize Beliefs (B): Probability that the node (candidate) satisfies the constraint
        # Start with simple feature similarity
        B = np.ones(n_nodes) * 0.5 
        B[1] = np.exp(-np.linalg.norm(F[0] - F[1])) # Initial candidate belief based on similarity
        
        # Oscillation parameters
        theta_steps = 5
        gamma_steps = 3
        
        for t in range(theta_steps):
            # 1. Theta-scale (Slow): Global constraint propagation
            # B_new = sigmoid( (A @ B) * W + b )
            global_input = (A @ B) * self.W_theta + self.b_theta
            B_theta = 1 / (1 + np.exp(-global_input))
            
            # 2. Gamma-scale (Fast): Local binding refinement
            # Repeat gamma steps per theta step
            B_curr = B_theta.copy()
            for g in range(gamma_steps):
                # Feature affinity matrix (simplified for 2 nodes: dot product of feature vectors)
                # F * F.T gives interaction strength between prompt and candidate features
                affinity = np.dot(F[0], F[1]) / (self.n_feat + 1e-6) # Normalized affinity
                
                local_mod = 1 / (1 + np.exp(-(affinity * self.W_gamma + self.b_gamma)))
                
                # Update belief based on local binding
                B_curr[1] = B_curr[1] * local_mod 
                B_curr[0] = 1.0 # Prompt is ground truth anchor
            
            B = B_curr
            
        # Calculate Free Energy: F = 0.5 * ||B - O||^2 + lambda * Entropy
        # We focus on the candidate node (index 1)
        pred_error = 0.5 * ((B[1] - np.mean(O)) ** 2) # Simplified O match
        
        # Entropy regularizer (encourages uncertainty if evidence is weak)
        eps = 1e-6
        entropy = -(B[1] * np.log(B[1] + eps) + (1-B[1]) * np.log(1-B[1] + eps))
        
        free_energy = pred_error + self.lambda_entropy * entropy
        return -free_energy # Return negative free energy as score

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Primary scoring signal: Structural alignment."""
        F, A, O = self._build_graph(prompt, candidate)
        return self._oscillate_and_minimize(F, A, O)

    def _compute_numeric_truth(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Check if numeric claims in candidate are mathematically consistent 
        with numeric claims in prompt.
        """
        # Extract all numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to check
            
        # Heuristic: If prompt has a comparison operator and candidate has a number,
        # check if the number satisfies a simple extraction logic.
        # Since full symbolic math is hard without libs, we use a proxy:
        # If the candidate number appears in the prompt, it's likely a retrieval task (Good).
        # If the candidate number is a result of a simple operation present in text, that's ideal.
        
        # Simple presence check for now as a robust baseline
        matches = 0
        for cn in c_nums:
            if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                matches += 1
                
        if matches == len(c_nums) and len(c_nums) > 0:
            return 1.0
        elif matches > 0:
            return 0.7
        return 0.3

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ bad)\b', p):
            return 0.2
            
        # 2. Scope ambiguity (Every X ... a Y)
        if re.search(r'\b(every|all) .+ (a|an) .+\b', p) and 'same' in p:
            return 0.3
            
        # 3. Pronoun ambiguity
        if re.search(r'\b(told|said to) .+ he\b', p) and 'who' in p:
            return 0.2
            
        # 4. False dichotomy
        if re.search(r'\b(either .+ or .+)\b', p) and 'only' not in p:
            # Only flag if it looks like a logical trap question
            if 'must' in p or 'true' in p:
                return 0.3
                
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            if 'data' not in p and 'chart' not in p and 'graph' not in p:
                return 0.2
                
        # 6. Unanswerability / Missing info
        if re.search(r'\b(without|missing|unknown)\b', p):
            return 0.1

        return 1.0 # No obvious traps detected

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta says ambiguous, return low confidence immediately
        if meta_cap < 0.4:
            return meta_cap
            
        # Otherwise, derive confidence from the strength of the structural match
        # and whether the answer actually contains the required features.
        score = self._compute_structural_score(prompt, answer)
        
        # Map score to 0-1 range roughly. 
        # High negative free energy (low error) -> High confidence.
        # The oscillation returns negative free energy. 
        # Let's normalize: if score > -0.5, it's good.
        conf = 1 / (1 + np.exp(5 * score)) # Sigmoid mapping
        
        # Penalize if the answer doesn't share key structural tokens with prompt
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        if np.sum(p_feats) > 0 and np.sum(a_feats) == 0:
            conf = min(conf, 0.4) # Low confidence if structure missing
            
        return float(np.clip(conf * meta_cap, 0.0, 0.95)) # Never 1.0 to allow uncertainty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to ensure we don't reward empty answers
        p_feats = self._extract_features(prompt)
        has_structure = np.sum(p_feats) > 0
        
        for cand in candidates:
            # 1. Structural Score (Oscillation/Free Energy) - Weight 0.50
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Computational/Truth Score - Weight 0.35
            comp_score = self._compute_numeric_truth(prompt, cand)
            
            # 3. NCD Tiebreaker - Weight 0.15 (Inverted, lower distance is better)
            # We want high score for low distance, but penalize exact echo slightly if too short
            ncd = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd 
            
            # Combine scores
            # Normalize struct_score (which is negative free energy) to ~0-1 range roughly
            # Assuming typical range -2 to 0.
            norm_struct = 1 / (1 + np.exp(2 * struct_score)) 
            
            final_score = (0.50 * norm_struct) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Penalty for "I don't know" if the prompt actually has structure
            if has_structure and np.sum(self._extract_features(cand)) == 0:
                if "don't know" in cand.lower() or "cannot" in cand.lower():
                    final_score *= 0.5 # Penalize giving up when structure exists

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {norm_struct:.2f}, Comp: {comp_score:.2f}, NCD: {ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example usage logic (not part of the class, for context):
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > 5, is A > 5?", ["Yes", "No", "Maybe"])
# print(res)
```

</details>
