# Cellular Automata + Analogical Reasoning + Free Energy Principle

**Fields**: Computer Science, Cognitive Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T17:01:24.008008
**Report Generated**: 2026-03-27T06:37:38.340791

---

## Nous Analysis

The algorithm treats a set of propositional atoms extracted from the prompt and each candidate answer as a one‑dimensional cellular automaton (CA) whose cells hold a belief value bᵢ∈[0,1] representing the degree to which the atom is true under the Free Energy Principle (FEP).  

**Data structures**  
- `atoms`: NumPy array of shape (N,) storing unique propositions (subject‑predicate‑object triples) obtained via regex patterns for negations, comparatives, conditionals, causal clauses, numeric comparisons, and ordering relations.  
- `W`: NumPy matrix (N,N) of analogy weights; Wᵢⱼ = exp(−‖φᵢ−φⱼ‖²/σ²) where φᵢ, φⱼ are feature vectors (dependency‑parse depths, semantic role labels, numeric magnitude) derived from the source domain (prompt) and target domain (candidate).  
- `bias`: NumPy vector (N,) encoding prior belief (0.5 for all atoms).  
- `lambda`: scalar controlling prediction‑error influence.  

**Operations (per CA step)**  
1. **Prediction**: `p = W @ b` (matrix multiplication) gives the expected belief of each atom from its analogs.  
2. **Prediction error**: `e = np.abs(b - p)`.  
3. **Free‑energy gradient**: `g = bias + W @ b - lambda * e`.  
4. **Update (CA rule)**: `b = sigmoid(g)` where `sigmoid(x)=1/(1+np.exp(-x))`.  
Iterate until ‖bₜ₊₁−bₜ‖₂ < ε (e.g., 1e‑4) or a max of 50 steps.  

**Scoring logic**  
After convergence, compute variational free energy:  
`F = 0.5 * np.sum(e**2) - np.sum(b * np.log(b) + (1-b) * np.log(1-b))`.  
Lower F indicates better prediction error minimization; the candidate score is `S = -F` (higher is better).  

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then”), causal claims (“because”, “leads to”), numeric values and inequalities, ordering relations (“first”, “before”, “greater than”). Each yields a proposition triple with attached type tags that feed into φᵢ.  

**Novelty**  
While belief propagation and Markov random fields have been used for textual reasoning, coupling a CA dynamics with analogical similarity kernels and an explicit free‑energy minimization objective is not present in existing NLP scoring tools; the closest analogs are probabilistic soft logic or neural‑augmented belief networks, which differ in update rule and lack the CA‑style local‑only interaction.  

Reasoning: 7/10 — captures relational structure and error minimization but limited to pairwise analogical weights.  
Metacognition: 5/10 — monitors belief change via free energy but does not explicitly reason about its own uncertainty.  
Hypothesis generation: 6/10 — belief updates can propose new true/false states for atoms, acting as hypothesis candidates.  
Implementability: 8/10 — relies only on NumPy and regex; straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cellular Automata**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Cellular Automata + Free Energy Principle: strong positive synergy (+0.606). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Analogical Reasoning + Free Energy Principle: strong positive synergy (+0.320). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Cellular Automata + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T02:14:22.884479

---

## Code

**Source**: scrap

[View code](./Cellular_Automata---Analogical_Reasoning---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements a Cellular Automata (CA) based reasoning engine driven by the 
    Free Energy Principle (FEP) and Analogical Reasoning.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms (subject-predicate-object) and 
       structural features (negations, comparatives, numerics) from prompt and candidates.
    2. Analogy Matrix (W): Constructs a similarity matrix where W_ij represents the 
       analogical weight between atom i and atom j based on semantic/structural features.
    3. CA Dynamics: Treats belief values (b) as CA cells. Iteratively updates beliefs 
       to minimize prediction error (Free Energy) via the rule:
       b_new = sigmoid(bias + W @ b - lambda * |b - W @ b|)
    4. Scoring: Candidates are scored by the negative variational free energy (-F) 
       of the converged system. Lower free energy (higher score) implies better 
       consistency between the candidate and the prompt's logical structure.
    """
    
    def __init__(self):
        self.sigma = 0.5  # Analogy kernel width
        self.lambda_err = 1.2  # Prediction error influence
        self.max_steps = 50
        self.epsilon = 1e-4

    def _extract_atoms(self, text):
        """Extracts structural features and creates a list of atom dictionaries."""
        text_lower = text.lower()
        atoms = []
        
        # Patterns for structural features
        patterns = [
            (r'not\s+(\w+)', 'negation', 1.0),
            (r'no\s+(\w+)', 'negation', 1.0),
            (r'more\s+than\s+([\d.]+)', 'comparative_gt', 1.0),
            (r'less\s+than\s+([\d.]+)', 'comparative_lt', 1.0),
            (r'if\s+(.+?)\s+then\s+(.+?)', 'conditional', 1.0),
            (r'because\s+(.+?)', 'causal', 1.0),
            (r'([\d.]+)\s*<\s*([\d.]+)', 'numeric_lt', 1.0),
            (r'([\d.]+)\s*>\s*([\d.]+)', 'numeric_gt', 1.0),
            (r'first|before|prior', 'ordering', 1.0),
            (r'(\w+)\s+is\s+(\w+)', 'relation', 1.0) # Generic relation
        ]
        
        found_features = []
        numeric_vals = []
        
        for pattern, p_type, weight in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    content = "_".join(str(x) for x in match)
                    found_features.append(f"{p_type}:{content}")
                    # Extract numbers for numeric evaluation
                    nums = re.findall(r'[\d.]+', str(match))
                    numeric_vals.extend([float(n) for n in nums])
                else:
                    found_features.append(f"{p_type}:{match}")
                    nums = re.findall(r'[\d.]+', str(match))
                    numeric_vals.extend([float(n) for n in nums])

        # Add generic atoms for presence of key logical operators
        if 'not' in text_lower or 'no' in text_lower:
            found_features.append("logic:negation_present")
        if 'if' in text_lower and 'then' in text_lower:
            found_features.append("logic:conditional_present")
            
        # Add numeric consistency atom if numbers exist
        if numeric_vals:
            # Simple heuristic: check sorted order consistency if "less/more" mentioned
            if 'less' in text_lower and len(numeric_vals) >= 2:
                is_consistent = numeric_vals[0] < numeric_vals[1]
                found_features.append(f"numeric_check:{is_consistent}")
            elif 'more' in text_lower and len(numeric_vals) >= 2:
                is_consistent = numeric_vals[0] > numeric_vals[1]
                found_features.append(f"numeric_check:{is_consistent}")

        # Deduplicate and return as list of feature strings (acting as atoms)
        unique_atoms = list(set(found_features))
        if not unique_atoms:
            unique_atoms = ["generic:content"]
            
        return unique_atoms

    def _compute_feature_vector(self, atom):
        """Generates a simple feature vector for an atom based on string properties."""
        # Features: length, presence of digits, specific type tags
        f1 = len(atom) / 50.0  # Normalized length
        f2 = 1.0 if any(c.isdigit() for c in atom) else 0.0
        f3 = 1.0 if 'negation' in atom else 0.0
        f4 = 1.0 if 'comparative' in atom else 0.0
        f5 = 1.0 if 'conditional' in atom else 0.0
        f6 = 1.0 if 'causal' in atom else 0.0
        f7 = 1.0 if 'numeric' in atom else 0.0
        return np.array([f1, f2, f3, f4, f5, f6, f7])

    def _build_analogy_matrix(self, atoms):
        """Builds the analogy weight matrix W based on feature similarity."""
        n = len(atoms)
        if n == 0:
            return np.array([])
        
        W = np.zeros((n, n))
        features = [self._compute_feature_vector(a) for a in atoms]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 1.0
                else:
                    dist_sq = np.sum((features[i] - features[j])**2)
                    W[i, j] = math.exp(-dist_sq / (self.sigma**2))
        
        # Normalize rows to prevent explosion
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W = W / row_sums
        return W

    def _run_ca_dynamics(self, atoms):
        """Runs the CA update rule to minimize free energy."""
        n = len(atoms)
        if n == 0:
            return 0.0, []
            
        W = self._build_analogy_matrix(atoms)
        b = np.full(n, 0.5)  # Initial belief
        bias = np.full(n, 0.5)  # Prior belief
        
        for _ in range(self.max_steps):
            # 1. Prediction
            p = W @ b
            # 2. Prediction Error
            e = np.abs(b - p)
            # 3. Free Energy Gradient
            # g = bias + expected_belief - lambda * error
            g = bias + (W @ b) - self.lambda_err * e
            # 4. Update
            b_new = 1.0 / (1.0 + np.exp(-g))
            
            if np.linalg.norm(b_new - b) < self.epsilon:
                b = b_new
                break
            b = b_new
            
        # Compute Variational Free Energy F
        # F = 0.5 * sum(e^2) - sum(b * log(b) + (1-b) * log(1-b))
        # Avoid log(0)
        b_clipped = np.clip(b, 1e-10, 1 - 1e-10)
        entropy_term = np.sum(b_clipped * np.log(b_clipped) + (1 - b_clipped) * np.log(1 - b_clipped))
        F = 0.5 * np.sum(e**2) - entropy_term
        
        return -F, b  # Return negative F so higher is better

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_atoms = self._extract_atoms(prompt)
        
        # If no structural atoms found, rely on NCD as tiebreaker logic implies
        # But per instructions, we must use structural parsing as primary signal.
        # We simulate structural depth by combining prompt + candidate atoms.
        
        base_score = 0.0
        if not prompt_atoms:
            # Fallback if prompt is empty of structure
            base_score = -10.0 

        for cand in candidates:
            # Combine prompt and candidate atoms to form the reasoning field
            cand_atoms = self._extract_atoms(cand)
            full_atoms = prompt_atoms + cand_atoms
            
            # Run CA dynamics
            score, _ = self._run_ca_dynamics(full_atoms)
            
            # Heuristic boost for explicit constraint satisfaction
            # If prompt has "not" and candidate has "not", slight boost (analogy)
            prompt_has_not = any('negation' in a for a in prompt_atoms)
            cand_has_not = any('negation' in a for a in cand_atoms)
            if prompt_has_not and cand_has_not:
                score += 0.5
            elif prompt_has_not and not cand_has_not and len(cand_atoms) > 0:
                # Penalty if prompt negates but candidate doesn't reflect it (simplified)
                score -= 0.2

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"CA-FEP convergence on {len(full_atoms)} atoms. Free Energy minimized."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the score relative to a baseline."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1. 
        # Typical FEP scores in this setup might range from -5 to 5 depending on complexity.
        # We use a sigmoid mapping centered at 0.
        confidence = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, confidence))
```

</details>
