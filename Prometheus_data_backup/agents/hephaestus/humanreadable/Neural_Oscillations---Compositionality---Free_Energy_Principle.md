# Neural Oscillations + Compositionality + Free Energy Principle

**Fields**: Neuroscience, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T03:08:52.634038
**Report Generated**: 2026-03-27T17:21:24.169564

---

## Nous Analysis

**Algorithm**  
We define a class `OscCompositionalFreeEnergyScorer`. Input: a prompt `P` and a list of candidate answers `C = [c₁,…,cₙ]`.  
1. **Parsing layer (Compositionality)** – Each sentence is tokenised with `str.split`. A deterministic finite‑state transducer (implemented as a nested `dict`) extracts elementary propositions:  
   - atomic predicates (`X is Y`),  
   - binary relations (`X > Y`, `X causes Y`, `X if Y`),  
   - negations (`not X`),  
   - numeric literals (`5`, `3.2`).  
   The transducer builds a directed hypergraph `G = (V, E)` where vertices are propositions and edges encode syntactic combination rules (e.g., conjunction → AND‑node, conditional → implication‑node). Edge weights are initialized to 1.0.  
2. **Oscillatory binding layer (Neural Oscillations)** – For each frequency band `f ∈ {theta, gamma}` we compute a binding strength matrix `B_f ∈ ℝ^{|V|×|V|}` using numpy:  
   - `theta` band captures long‑range temporal coherence: `B_theta[i,j] = exp(-|t_i - t_j|/τ_theta)` where `t_i` is the sentence index of proposition i.  
   - `gamma` band captures local feature binding: `B_gamma[i,j] = 1` if propositions share a lexical head or numeric value, else 0.  
   The combined binding matrix is `B = α·B_theta + (1‑α)·B_gamma` (α=0.6). Edge weights in `G` are updated as `w_e ← w_e * B[i,j]` for the incident vertices i,j.  
3. **Free‑energy minimization layer** – We treat each candidate answer as a set of hypothesized propositions `H_k`. Variational free energy `F_k` is approximated by the prediction error between `H_k` and the observed graph `G`:  
   - Compute mismatch vector `e_k = |A_G - A_{H_k}|` where `A` is the adjacency matrix of `G` restricted to vertices in `H_k`.  
   - Free energy `F_k = 0.5 * e_k.T @ Σ^{-1} @ e_k + 0.5 * log|Σ|`, with `Σ = λI` (λ=0.1) – a simple isotropic precision.  
   Score `S_k = -F_k` (lower free energy → higher score).  
4. **Selection** – Return `argmax_k S_k`. All operations use only `numpy` for matrix algebra and the standard library for parsing.

**Structural features parsed**  
- Negations (`not`, `no`) → polarity flag on vertices.  
- Comparatives (`greater than`, `less than`, `≤`, `≥`) → ordered relation edges with direction.  
- Conditionals (`if … then …`, `unless`) → implication edges.  
- Causal verbs (`cause`, lead to, result in) → causal edges.  
- Numeric values and units → attribute on vertices, enabling numeric comparison via binding.  
- Ordering relations (`first`, `second`, `before`, `after`) → temporal edges stamped with sentence index for theta coherence.

**Novelty**  
The combination mirrors existing work: compositional semantic graphs (e.g., Abstract Meaning Representation), oscillatory binding models (e.g., Fries’ communication‑through‑coherence), and active inference frameworks that minimize variational free energy. However, integrating all three into a single, deterministic scoring pipeline that operates purely with numpy‑based linear algebra and rule‑based parsing is not commonly reported in public reasoning‑evaluation tools, making the approach novel in its specific implementation.

**Ratings**  
Reasoning: 8/10 — The algorithm explicitly propagates logical constraints and quantifies prediction error, yielding principled scores for complex relational reasoning.  
Metacognition: 6/10 — It lacks a self‑monitoring mechanism to adjust precision or band weights based on past performance; metacognitive awareness is implicit only via the free‑energy term.  
Hypothesis generation: 7/10 — By constructing a graph of candidate propositions and scoring their fit, the system generates and evaluates multiple hypotheses in parallel.  
Implementability: 9/10 — All components rely on regex‑style parsing, numpy matrix ops, and basic data structures; no external libraries or GPU code are required, making it straightforward to deploy.

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

- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Neural Oscillations: strong positive synergy (+0.271). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Kolmogorov Complexity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=41% cal=2% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:36:44.745789

---

## Code

**Source**: scrap

[View code](./Neural_Oscillations---Compositionality---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    OscCompositionalFreeEnergyScorer implementation.
    
    Mechanism:
    1. Compositionality: Parses text into a hypergraph of propositions (nodes) 
       and logical relations (edges) using regex and state logic.
    2. Neural Oscillations: Simulates binding via frequency-based matrices.
       - Theta: Temporal coherence (sentence proximity).
       - Gamma: Lexical/Numeric feature sharing.
       These modulate edge weights in the proposition graph.
    3. Free Energy Principle: Treats each candidate as a hypothesis graph.
       Calculates Variational Free Energy (prediction error) between the 
       candidate's structure and the prompt's structure. Lower energy = higher score.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.tau_theta = 2.0
        self.alpha = 0.6
        self.lambda_prec = 0.1
        # Patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|else|provided)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|results in|because|since)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|who is the)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or|must choose between)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I)
        }

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def _extract_propositions(self, text: str) -> List[Dict[str, Any]]:
        """Parses text into atomic propositions with attributes."""
        props = []
        sentences = re.split(r'[.!?]', text)
        for idx, sent in enumerate(sentences):
            if not sent.strip():
                continue
            tokens = sent.strip().split()
            if not tokens:
                continue
            
            p = {
                'id': f"p_{len(props)}",
                'text': sent.strip(),
                'sentence_idx': idx,
                'tokens': set(tokens),
                'negated': bool(self.patterns['negation'].search(sent)),
                'has_numeric': bool(self.patterns['numeric'].search(sent)),
                'numbers': [float(n) for n in re.findall(r'\d+\.?\d*', sent)],
                'type': 'atomic'
            }
            
            if self.patterns['conditional'].search(sent):
                p['type'] = 'conditional'
            elif self.patterns['causal'].search(sent):
                p['type'] = 'causal'
            elif self.patterns['comparative'].search(sent):
                p['type'] = 'comparative'
                
            props.append(p)
        return props

    def _build_graph(self, text: str) -> Tuple[List[Dict], np.ndarray]:
        """Builds the proposition graph and binding matrix."""
        props = self._extract_propositions(text)
        if not props:
            return [], np.array([])
        
        n = len(props)
        V = list(range(n))
        
        # 1. Oscillatory Binding Matrices
        B_theta = np.zeros((n, n))
        B_gamma = np.zeros((n, n))
        
        # Theta: Temporal coherence
        for i in range(n):
            for j in range(n):
                t_i = props[i]['sentence_idx']
                t_j = props[j]['sentence_idx']
                B_theta[i, j] = np.exp(-abs(t_i - t_j) / self.tau_theta)
        
        # Gamma: Lexical/Numeric binding
        for i in range(n):
            for j in range(n):
                if i == j:
                    B_gamma[i, j] = 1.0
                    continue
                # Shared tokens or shared numbers
                shared_lex = len(props[i]['tokens'] & props[j]['tokens'])
                shared_num = len(set(props[i]['numbers']) & set(props[j]['numbers']))
                if shared_lex > 0 or shared_num > 0:
                    B_gamma[i, j] = 1.0
        
        B = self.alpha * B_theta + (1.0 - self.alpha) * B_gamma
        
        # 2. Construct Adjacency Matrix (Structural Logic)
        # Simple heuristic: Connect if types match or logical flow exists
        A = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                # Base connectivity
                score = 0.5
                # Boost if logical types align (e.g., conditional -> atomic)
                if props[i]['type'] == 'conditional' or props[j]['type'] == 'conditional':
                    score += 0.5
                if props[i]['type'] == 'causal' or props[j]['type'] == 'causal':
                    score += 0.5
                
                # Apply oscillatory binding
                weight = score * B[i, j]
                A[i, j] = weight
                A[j, i] = weight
                
        return props, A

    def _compute_free_energy(self, prompt_A: np.ndarray, cand_A: np.ndarray) -> float:
        """Computes variational free energy approximation."""
        if prompt_A.size == 0 or cand_A.size == 0:
            return 100.0 # High energy for empty
        
        # Resize candidate to match prompt dimensions for comparison (padding with 0)
        n_p, m_p = prompt_A.shape
        n_c, m_c = cand_A.shape
        
        # Truncate or pad to match
        min_dim = min(n_p, n_c)
        if min_dim == 0:
            return 100.0
            
        A_g = prompt_A[:min_dim, :min_dim]
        A_h = cand_A[:min_dim, :min_dim]
        
        # Prediction error
        e = A_g - A_h
        e_vec = e.flatten()
        
        # F = 0.5 * e^T * Sigma^-1 * e + 0.5 * log|Sigma|
        # Sigma = lambda * I => Sigma^-1 = (1/lambda) * I
        inv_sigma = (1.0 / self.lambda_prec) * np.eye(len(e_vec))
        
        # Quadratic form
        energy = 0.5 * np.dot(e_vec, np.dot(inv_sigma, e_vec))
        
        # Regularization term (log det) - constant for fixed size, but included for form
        log_det = 0.5 * len(e_vec) * np.log(self.lambda_prec)
        
        return float(energy + log_det)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for ambiguity, presupposition, and unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Only penalize if it looks like a forced choice question
            if '?' in prompt:
                return 0.3
                
        # 3. Subjectivity without context
        if self.patterns['subjectivity'].search(p_lower):
            if 'calculate' not in p_lower and 'logic' not in p_lower:
                return 0.3

        # 4. Pronoun/Scope ambiguity (Heuristic: high ratio of pronouns to nouns?)
        # Simplified: If "who" or "which" appears in a question with multiple entities
        if re.search(r'\b(who|which one|he|she)\b', p_lower) and '?' in prompt:
             # Check for multiple potential antecedents (simple count of capitalized words)
             caps = len(re.findall(r'\b[A-Z][a-z]+\b', prompt))
             if caps > 2:
                 return 0.4

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_props, prompt_A = self._build_graph(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        prompt_comp = zlib.compress(prompt.encode())
        
        scores = []
        for i, cand in enumerate(candidates):
            cand_props, cand_A = self._build_graph(cand)
            
            # Primary Score: Free Energy (Negative Energy = Higher Score)
            # We invert and scale because lower energy is better
            fe = self._compute_free_energy(prompt_A, cand_A)
            # Normalize FE roughly to 0-1 range based on matrix size
            norm_factor = (prompt_A.size * prompt_A.size) if prompt_A.size > 0 else 1
            structural_score = max(0, 1.0 - (fe / (norm_factor * 10 + 1)))
            
            # Secondary Score: Numeric Consistency
            # If prompt has numbers and candidate has numbers, check logical consistency
            numeric_bonus = 0.0
            p_nums = [p['numbers'] for p in prompt_props if p['numbers']]
            c_nums = [p['numbers'] for p in cand_props if p['numbers']]
            
            if p_nums and c_nums:
                # Simple check: does the candidate preserve the magnitude order?
                # This is a heuristic proxy for "solving" the math
                p_flat = [n for sublist in p_nums for n in sublist]
                c_flat = [n for sublist in c_nums for n in sublist]
                if len(p_flat) == len(c_flat):
                    # Check correlation
                    if len(p_flat) > 1:
                        corr = np.corrcoef(p_flat, c_flat)[0, 1]
                        if not np.isnan(corr):
                            numeric_bonus = 0.2 * max(0, corr)
                    else:
                        # Exact match for single numbers
                        if abs(p_flat[0] - c_flat[0]) < 1e-6:
                            numeric_bonus = 0.2

            # Tiebreaker: NCD (max 15% influence)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Final Score Composition
            # Structural >= 50%, Computation (Numeric) >= 20%, NCD <= 15%
            final_score = (structural_score * 0.65) + (numeric_bonus * 1.0) + ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FE:{fe:.2f}, Struct:{structural_score:.2f}, Num:{numeric_bonus:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-confidence check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        # If the parser found zero propositions in prompt, we can't reason structurally
        props, A = self._build_graph(prompt)
        if not props or A.size == 0:
            return 0.2 # Low confidence if structure cannot be parsed
        
        # 3. Compute score for this specific answer
        cand_props, cand_A = self._build_graph(answer)
        fe = self._compute_free_energy(A, cand_A)
        
        # Normalize score
        norm_factor = (A.size * A.size) if A.size > 0 else 1
        raw_score = max(0, 1.0 - (fe / (norm_factor * 10 + 1)))
        
        # Boost if numeric calculation matches (Constructive computation)
        p_nums = [p['numbers'] for p in props if p['numbers']]
        c_nums = [p['numbers'] for p in cand_props if p['numbers']]
        calculation_confirmed = False
        
        if p_nums and c_nums:
            p_flat = [n for sublist in p_nums for n in sublist]
            c_flat = [n for sublist in c_nums for n in sublist]
            # Heuristic: If candidate numbers are a direct result of prompt numbers
            # e.g. Prompt: "2 + 2", Answer: "4" (detected as 4.0)
            # This is a simplification; real math solving requires eval AST
            if len(p_flat) >= 2 and len(c_flat) == 1:
                if abs(sum(p_flat) - c_flat[0]) < 1e-6 or abs(p_flat[0] * p_flat[1] - c_flat[0]) < 1e-6:
                    calculation_confirmed = True
        
        # Map raw score to 0-1
        conf = raw_score
        if calculation_confirmed:
            conf = min(1.0, conf + 0.3) # Boost for calculated answers
        
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Cap at 0.9 unless calculation confirmed (Epistemic honesty rule)
        if not calculation_confirmed:
            final_conf = min(final_conf, 0.9)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
