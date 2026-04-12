# Category Theory + Compositionality + Free Energy Principle

**Fields**: Mathematics, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T07:28:18.763953
**Report Generated**: 2026-03-27T16:08:07.438883

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use a handful of regex patterns to extract atomic propositions (noun‑phrase + verb‑phrase) and binary relations:  
   *Negation* (`not`), *comparatives* (`>`, `<`, `≥`, `≤`, `more than`, `less than`), *conditionals* (`if … then …`), *causal* (`because`, `leads to`, `results in`), *ordering* (`before`, `after`, `first`, `last`), *numeric* (`\d+`).  
   Each proposition becomes a node; each relation becomes a directed edge labeled with a type from the set R.  
2. **Node feature functor** – Map each node’s lexical content to a fixed‑dimensional vector v∈ℝᵈ using a deterministic hash‑based one‑hot (e.g., `hash(word) % D`) followed by a random orthogonal projection (numpy). This is the “functor” from the syntactic category (word) to a semantic vector space, satisfying compositionality: the meaning of a complex node (e.g., a coordinated phrase) is the sum of its parts’ vectors.  
3. **Adjacency tensors** – For each relation type r∈R build an n×n binary matrix Aʳ (numpy) where Aʳ[i,j]=1 iff edge i→r→j exists. Stack them to a tensor A∈ℝ^{|R|×n×n}.  
4. **Reference distribution** – From a gold‑standard answer (or a set of training answers) compute the expected adjacency tensor Ā and expected node‑feature covariance Σᵥ (numpy mean and cov).  
5. **Free‑energy scoring** – For a candidate answer compute:  
   *Prediction error* = ‖A − Ā‖_F² (Frobenius norm, numpy).  
   *Complexity* = ½·log|Σᵥ| + ½·tr[(V − μ)ᵀ Σᵥ⁻¹ (V − μ)] where V is the matrix of candidate node vectors, μ the mean node vector (Gaussian approximation of variational free energy).  
   *Score* = −(prediction error + λ·complexity), λ∈[0.1,1] tuned on a validation set. Higher (less negative) scores indicate better alignment with the compositional, predictive structure implied by the gold answer.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, temporal/ordering relations, numeric quantifiers, conjunctions/disjunctions, and plural/collective markings.  

**Novelty** – The approach fuses a category‑theoretic functorial semantics (nodes → vectors, relations → tensors) with a Free‑Energy‑Principle‑style variational objective. While probabilistic soft logic and graph‑matching methods exist, the explicit use of free‑energy decomposition (prediction error + Gaussian complexity) on functor‑derived node embeddings is not present in prior work.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and prediction error well, but approximations may miss deep inference.  
Metacognition: 6/10 — provides a scalar uncertainty term (complexity) yet lacks explicit self‑monitoring loops.  
Hypothesis generation: 7/10 — generates alternative parses via edge‑flipping; quality depends on heuristic search depth.  
Implementability: 9/10 — relies only on regex, NumPy linear algebra, and stdlib containers; no external libraries or APIs needed.

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

- **Category Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Category Theory + Free Energy Principle: negative interaction (-0.084). Keep these concepts in separate code paths to avoid interference.
- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Kolmogorov Complexity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T15:27:01.911506

---

## Code

**Source**: scrap

[View code](./Category_Theory---Compositionality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    A reasoning tool combining Category Theory (functorial mapping), Compositionality,
    and the Free Energy Principle (FEP) for answer scoring.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic propositions and logical relations
       (negation, comparison, conditionals) using regex patterns.
    2. Functorial Mapping: Maps syntactic tokens to a semantic graph (vertices=propositions,
       edges=logical morphisms).
    3. Free Energy Minimization: Treats truth values as variational parameters.
       Minimizes a Free Energy function balancing prediction error (match with prompt)
       and logical consistency (implication constraints).
    4. Scoring: Final score is negative Free Energy (lower energy = higher score).
       NCD is used only as a tiebreaker.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+than\b', r'\bfewer\s+than\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
            'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bcauses\b', r'\btherefore\b'],
            'ordering': [r'\bfirst\b', r'\blast\b', r'\bafter\b', r'\bbefore\b'],
            'connective': [r'\band\b', r'\bor\b', r'\but\b']
        }
        self.eta = 0.01  # Learning rate
        self.steps = 10  # Optimization steps

    def _extract_predicates(self, text):
        """Extract atomic predicates and relations using regex (Compositionality)."""
        text_lower = text.lower()
        predicates = []
        relations = []
        
        # Simple noun-verb-noun extraction approximation
        # Look for patterns like "A is B", "A > B", "if A then B"
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
                
            # Check for specific relation types
            found_rel = False
            
            # Comparatives
            for pat in self.patterns['comparative']:
                if re.search(pat, sent, re.IGNORECASE):
                    # Extract rough subject/object around the pattern
                    parts = re.split(pat, sent, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        subj = parts[0].strip().split()[-1] if parts[0].strip() else "unknown"
                        obj = parts[1].strip().split()[0] if parts[1].strip() else "unknown"
                        predicates.append(f"{subj}_GT_{obj}") # Greater Than relation
                        relations.append(('comp', subj, obj))
                        found_rel = True
                    break
            
            if not found_rel:
                # Negations
                for pat in self.patterns['negation']:
                    if re.search(pat, sent, re.IGNORECASE):
                        # Mark surrounding context as negated
                        predicates.append(f"NEG:{sent[:50]}")
                        found_rel = True
                        break
            
            if not found_rel:
                # Conditionals
                if any(re.search(p, sent, re.IGNORECASE) for p in self.patterns['conditional']):
                    predicates.append(f"COND:{sent[:50]}")
                    found_rel = True

            # Fallback: generic proposition
            if not found_rel and len(sent) > 5:
                words = sent.split()
                if len(words) >= 3:
                    predicates.append(f"{words[0]}_{words[-1]}")

        return list(set(predicates)), relations

    def _build_graph(self, prompt, candidate):
        """
        Build the semantic graph G=(V, E).
        Vertices: Propositions from prompt and candidate.
        Edges: Logical morphisms.
        """
        # Combine text for context, but distinguish sources
        full_text = f"{prompt} {candidate}"
        preds, rels = self._extract_predicates(full_text)
        
        # Create unique vertex list
        vertices = list(set(preds))
        n = len(vertices)
        if n == 0:
            return [], [], np.array([]), np.array([])
            
        v_map = {v: i for i, v in enumerate(vertices)}
        
        # Initialize p (observed truth) and q (variational truth)
        # p_i = 1 if in prompt, 0.5 if unknown, 0 if explicitly negated in prompt
        p = np.full(n, 0.5)
        prompt_lower = prompt.lower()
        
        for i, v in enumerate(vertices):
            # Simple heuristic: if vertex substring exists in prompt, assume true (1)
            # If it contains NEG, assume false (0)
            if "NEG:" in v:
                # Check if the core content is in prompt
                core = v.replace("NEG:", "")
                if core.lower() in prompt_lower:
                    p[i] = 0.0 # Explicitly negated in prompt context
            else:
                # Check presence in prompt
                # Very loose matching for demonstration
                if any(part.lower() in prompt_lower for part in v.split('_')):
                    p[i] = 1.0
                else:
                    p[i] = 0.5 # Unknown (candidate only)

        # Build adjacency matrix for implications (A -> B)
        # For this implementation, we assume transitivity among extracted relations
        # and direct implication from prompt assertions to candidate assertions.
        W = np.zeros((n, n))
        
        # Add edges based on extracted relations
        for r_type, subj, obj in rels:
            if r_type == 'comp':
                # Find vertices containing these terms
                idx_subj = [i for i, v in enumerate(vertices) if subj in v]
                idx_obj = [i for i, v in enumerate(vertices) if obj in v]
                for i in idx_subj:
                    for j in idx_obj:
                        if i != j:
                            W[i, j] = 0.8 # Strong implication weight

        # Diagonal self-consistency
        np.fill_diagonal(W, 1.0)
        
        return vertices, p, W

    def _compute_free_energy(self, p, W):
        """
        Compute Free Energy F and minimize it via gradient descent.
        F = Sum((q - p)^2) + Sum(w_ij * max(0, q_i - q_j)^2)
        """
        n = len(p)
        if n == 0:
            return 0.0
            
        q = p.copy() # Initialize q = p
        pi = 1.0 # Uniform precision
        
        for _ in range(self.steps):
            # Prediction Error Term Gradient: 2 * (q - p) * pi
            grad_pred = 2 * (q - p) * pi
            
            # Consistency Term Gradient
            # Term: w_ij * max(0, q_i - q_j)^2
            # Derivative w.r.t q_i: if q_i > q_j: 2 * w_ij * (q_i - q_j)
            # Derivative w.r.t q_j: if q_i > q_j: -2 * w_ij * (q_i - q_j)
            
            grad_cons = np.zeros(n)
            for i in range(n):
                for j in range(n):
                    if W[i, j] > 0:
                        diff = q[i] - q[j]
                        if diff > 0:
                            d_val = 2 * W[i, j] * diff
                            grad_cons[i] += d_val
                            grad_cons[j] -= d_val
            
            total_grad = grad_pred + grad_cons
            q -= self.eta * total_grad
            
            # Clamp q to [0, 1]
            q = np.clip(q, 0, 1)
            
        # Calculate final Free Energy
        pred_err = np.sum((q - p)**2 * pi)
        cons_err = 0.0
        for i in range(n):
            for j in range(n):
                if W[i, j] > 0:
                    diff = q[i] - q[j]
                    if diff > 0:
                        cons_err += W[i, j] * (diff ** 2)
        
        F = pred_err + cons_err
        return -F # Return negative F so higher is better

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_base = prompt.lower()
        
        # Pre-calculate prompt graph components if needed, but here we do per-candidate
        # to handle candidate-specific propositions.
        
        scores = []
        for cand in candidates:
            vertices, p, W = self._build_graph(prompt, cand)
            
            if len(vertices) == 0:
                # Fallback for empty parse
                fe_score = -1.0
            else:
                fe_score = self._compute_free_energy(p, W)
            
            scores.append((cand, fe_score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Handle ties with NCD
        final_results = []
        for i, (cand, score) in enumerate(scores):
            # Check for ties within a small epsilon
            is_tie = False
            if i > 0:
                if abs(score - scores[i-1][1]) < 1e-6:
                    is_tie = True
            
            if is_tie:
                # Use NCD to break tie (lower NCD to prompt is better)
                # Note: In a real tie-breaker scenario we might compare to a hypothetical ideal
                # Here we just use NCD to prompt as a secondary heuristic
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly by NCD (inverted, so lower NCD adds to score)
                score += (1.0 - ncd_val) * 1e-9

            reasoning = f"Free Energy minimized over {len(self._build_graph(prompt, cand)[0])} propositions."
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the free energy score."""
        # Evaluate single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1 range
        # Score is negative free energy. 
        # Theoretically unbounded below, but in practice bounded by our setup.
        # A perfect match (p=q, no conflicts) yields F=0 -> score=0.
        # Errors yield negative scores.
        # We need to normalize. Let's assume worst case F is roughly N (number of props).
        # Normalize: 1 / (1 + |score|) gives a rough probability-like value.
        
        if score >= 0:
            return 1.0
        else:
            # Transform negative score to 0-1
            # e.g., score -10 -> 0.09, score -0.1 -> 0.9
            conf = 1.0 / (1.0 + abs(score))
            return min(1.0, max(0.0, conf))
```

</details>
