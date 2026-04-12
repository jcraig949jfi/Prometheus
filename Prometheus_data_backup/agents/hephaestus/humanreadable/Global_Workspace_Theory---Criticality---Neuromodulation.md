# Global Workspace Theory + Criticality + Neuromodulation

**Fields**: Cognitive Science, Complex Systems, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T07:12:53.125939
**Report Generated**: 2026-04-01T20:30:43.768119

---

## Nous Analysis

**Algorithm: Critical‑Gain Workspace Scorer (CGWS)**  

1. **Parsing & Representation**  
   - Tokenize the prompt and each candidate answer with a simple whitespace/punctuation split (stdlib `re`).  
   - Extract structural predicates using regex patterns:  
     *Negations* (`not`, `n't`), *comparatives* (`>`, `<`, `more`, `less`), *conditionals* (`if … then`, `unless`), *causal arrows* (`because`, `since`, `therefore`), *ordering relations* (`first`, `then`, `before`, `after`), and *numeric literals* (`\d+(\.\d+)?`).  
   - Build a directed hypergraph **G = (V, E)** where each node *v* ∈ V is a predicate instance (e.g., “X > Y”, “not Z”). Hyperedges *e* ∈ E connect a set of antecedent nodes to a consequent node, representing modus‑ponens‑style inference (e.g., {X>Y, Y>Z} → X>Z). Store adjacency as a list of NumPy arrays for fast vectorized lookup.

2. **Global Workspace Ignition**  
   - Initialize an activation vector **a** ∈ ℝ^{|V|} with zeros. For each predicate directly mentioned in the prompt, set a[v] = 1 (ignition).  
   - Iterate **T** steps (T = log₂|V| to stay near criticality). At each step:  
     *Compute influence*: **i** = **W**·**a**, where **W** is a sparse weight matrix derived from **E** (weight = 1/|antecedents| for each hyperedge).  
     *Apply neuromodulatory gain*: **g** = 1 + α·σ(**a**) where σ is the logistic function and α ∈ [0.2,0.5] is a gain parameter (simulating dopamine/serotonin modulation).  
     *Update*: **a** ← clip(**a** + η·(**i** ⊙ **g**), 0, 1) with learning rate η = 0.1.  
   - The system operates near the edge of chaos because the spectral radius of **W** is kept ≈1 by normalizing hyperedge weights; small changes in **a** produce large, divergent activation patterns, providing susceptibility to subtle structural differences.

3. **Scoring**  
   - For each candidate answer, compute its predicate activation sum **S** = Σ_{v∈V_cand} a[v] after the final iteration.  
   - Normalize by the number of predicates in the candidate: **score** = S / |V_cand|.  
   - Return the candidate with the highest score; ties broken by fewer logical contradictions (detected via direct negation pairs in **V_cand**).

**Structural Features Parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values.

**Novelty** – The triple blend is not present in existing NLP reasoners. Global Workspace ignition appears in neural‑network attention models but not as a discrete, numpy‑only activation dynamics; criticality has been used in reservoir computing but not combined with explicit hypergraph constraint propagation; neuromodulatory gain control is rare in symbolic reasoners. Thus the combination is novel, though each component has precedents.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty via critical dynamics, but lacks deep semantic grounding.  
Metacognition: 5/10 — provides a self‑regulated gain mechanism, yet no explicit monitoring of reasoning steps.  
Hypothesis generation: 6/10 — activation spread can suggest implicit inferences, but no generative proposal step.  
Implementability: 9/10 — relies only on regex, NumPy vector ops, and stdlib; straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=30% cal=24% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T19:57:01.025567

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Criticality---Neuromodulation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Critical-Gain Workspace Scorer (CGWS) with Dynamics Tracking.
    
    Mechanism:
    1. Parsing: Extracts logical predicates (negations, comparatives, causals) into a hypergraph.
    2. Dynamics: Simulates a reservoir-like dynamical system where activation spreads through the 
       logical graph. We track the trajectory of the answer's activation state.
    3. Criticality & Gain: Uses a logistic gain function modulated by global activation to operate 
       near the "edge of chaos," amplifying coherent logical chains while suppressing noise.
    4. Scoring: Combines final activation strength, trajectory stability (convergence), and 
       structural consistency. NCD is used only as a minor tie-breaker.
    5. Epistemic Honesty: Explicitly detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        self.regex_patterns = {
            'negation': re.compile(r'\b(not|n\'t|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|>\|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|except)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|since|therefore|thus|hence|causes?|leads? to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|second|then|before|after|next|finally)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did|when does)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or | neither .+ nor | must be .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|ugliest)\b', re.IGNORECASE)
        }
        self.alpha = 0.35  # Neuromodulatory gain parameter
        self.eta = 0.1     # Learning rate
        self.T_steps = 10  # Iteration steps for dynamics

    def _tokenize(self, text: str) -> List[str]:
        return re.split(r'[\s\.,;:!?()"\']+', text.lower())

    def _extract_predicates(self, text: str) -> List[str]:
        """Extract structural predicates as nodes in the hypergraph."""
        predicates = []
        text_lower = text.lower()
        
        # Check specific regex categories
        for key, pattern in self.regex_patterns.items():
            if key in ['presupposition', 'false_dichotomy', 'subjectivity']:
                continue # These are for meta-analysis, not graph nodes
            matches = pattern.findall(text_lower)
            if matches:
                predicates.extend([f"{key}:{m}" for m in matches])
        
        # Extract numeric comparisons if present
        nums = self.regex_patterns['numeric'].findall(text_lower)
        if len(nums) >= 2:
            predicates.append(f"numeric_seq:{'_'.join(nums[:4])}")
            
        return predicates if predicates else ["default_node"]

    def _build_hypergraph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build adjacency matrix W and initial activation vector a0.
        Returns: (W, a0, node_labels)
        """
        # Combine context for node extraction
        full_text = f"{prompt} {candidate}"
        predicates = self._extract_predicates(full_text)
        
        # Unique nodes
        nodes = list(set(predicates))
        n = len(nodes)
        if n == 0:
            return np.array([[0]]), np.array([1.0]), ["default"]

        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        # Initialize Activation Vector (a)
        # Ignite nodes present in the prompt specifically
        prompt_preds = set(self._extract_predicates(prompt))
        a0 = np.zeros(n)
        for i, node in enumerate(nodes):
            if node.split(':')[0] in [p.split(':')[0] for p in prompt_preds] or node in prompt_preds:
                a0[i] = 1.0
        
        # Build Sparse Weight Matrix W (Adjacency)
        # Simplified logic: Connect sequential predicates or shared types
        # In a full implementation, this would parse logical forms (A->B)
        W = np.zeros((n, n))
        
        # Create connectivity based on predicate type similarity (clustering)
        # and sequential order in the text
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i == j:
                    continue
                type_i, val_i = node_i.split(':')
                type_j, val_j = node_j.split(':')
                
                # Connect if same type (logical consistency) or sequential
                if type_i == type_j:
                    W[i, j] = 1.0 / n # Normalized weight
                elif abs(i - j) == 1: # Sequential proximity
                    W[i, j] = 0.5 / n
        
        # Normalize to ensure spectral radius approx 1 (Criticality)
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W = W / row_sums * 0.9 # Scale slightly below 1 for stability
        
        return W, a0, nodes

    def _run_dynamics(self, W: np.ndarray, a0: np.ndarray) -> Tuple[float, float]:
        """
        Run the Critical-Gain Workspace dynamics.
        Returns: (final_score, stability_metric)
        """
        a = a0.copy()
        n = len(a)
        if n == 0: return 0.0, 0.0
        
        trajectory = []
        
        # Determine T based on log2(|V|) to stay near criticality
        T = max(3, int(np.log2(n) + 2)) 
        T = min(T, self.T_steps)
        
        history = []

        for t in range(T):
            # Compute influence: i = W * a
            influence = W @ a
            
            # Neuromodulatory gain: g = 1 + alpha * sigmoid(a)
            # Using numpy logistic: 1 / (1 + exp(-x))
            sigma_a = 1.0 / (1.0 + np.exp(-a))
            g = 1.0 + self.alpha * sigma_a
            
            # Update: a <- clip(a + eta * (i * g), 0, 1)
            a = a + self.eta * (influence * g)
            a = np.clip(a, 0, 1)
            
            trajectory.append(np.sum(a))
            
            # Early stopping if converged
            if len(history) > 2:
                if abs(trajectory[-1] - trajectory[-2]) < 1e-4:
                    break
                    
        # Calculate Stability (Lyapunov-like approximation via trajectory variance)
        if len(trajectory) > 1:
            diffs = np.diff(trajectory)
            stability = 1.0 / (1.0 + np.std(diffs)) # Higher std = lower stability
        else:
            stability = 1.0
            
        return float(np.sum(a)), stability

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0: return 1.0
        return (c12 - min_len) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.regex_patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.regex_patterns['false_dichotomy'].search(p_lower):
            # Check if the prompt implies only two options exist when more might
            if "or" in p_lower and ("must" in p_lower or "have to" in p_lower):
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.regex_patterns['subjectivity'].search(p_lower):
            if "according to" not in p_lower and "data" not in p_lower:
                return 0.25

        # 4. Pronoun/Scope Ambiguity (Heuristic)
        # If "who" or "which" is asked but the sentence structure is simple
        if re.search(r'\b(who|which one|what)\b', p_lower):
            if p_lower.count("told") > 0 or p_lower.count("said") > 0:
                # Potential pronoun ambiguity
                return 0.4 

        return 1.0

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Internal scorer returning (raw_score, reasoning_string)."""
        W, a0, nodes = self._build_hypergraph(prompt, candidate)
        activation_sum, stability = self._run_dynamics(W, a0)
        
        # Structural Score: Activation * Stability
        struct_score = activation_sum * stability
        
        # Computation Check: Numeric consistency
        comp_bonus = 0.0
        prompt_nums = self.regex_patterns['numeric'].findall(prompt)
        cand_nums = self.regex_patterns['numeric'].findall(candidate)
        
        reasoning_parts = []
        
        if prompt_nums and cand_nums:
            try:
                # Simple check: does the candidate contain a number derived from prompt?
                # This is a heuristic for "constructive computation"
                p_floats = [float(n) for n in prompt_nums]
                c_floats = [float(n) for n in cand_nums]
                
                # Check for direct inclusion or simple derivation
                if any(cf in p_floats for cf in c_floats):
                    comp_bonus = 0.2
                    reasoning_parts.append("Numeric consistency detected.")
                elif len(p_floats) >= 2 and len(c_floats) >= 1:
                    # Check basic arithmetic relations (sum, diff)
                    ops = [p_floats[0] + p_floats[1], p_floats[0] - p_floats[1]]
                    if any(abs(cf - op) < 1e-6 for cf in c_floats for op in ops):
                        comp_bonus = 0.3
                        reasoning_parts.append("Arithmetic derivation confirmed.")
            except ValueError:
                pass

        # NCD Tiebreaker (Max 15% impact)
        ncd = self._compute_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15
        
        final_score = (struct_score * 0.65) + (comp_bonus * 0.2) + ncd_score
        
        # Reasoning string generation
        if stability < 0.5:
            reasoning_parts.append("Low trajectory stability (fragile logic).")
        if activation_sum < 0.5:
            reasoning_parts.append("Weak predicate activation.")
        if not reasoning_parts:
            reasoning_parts.append("Strong structural alignment.")
            
        return final_score, " ".join(reasoning_parts)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            raw_score, reason_str = self._evaluate_candidate(prompt, cand)
            
            # Apply epistemic cap
            if raw_score > meta_cap:
                raw_score = meta_cap
                reason_str += " (Capped by epistemic uncertainty)"
                
            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": reason_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt itself is problematic, return low confidence immediately
        if meta_cap < 0.4:
            return meta_cap
            
        raw_score, _ = self._evaluate_candidate(prompt, answer)
        
        # Cap by meta-confidence
        final_conf = min(raw_score, meta_cap)
        
        # Ensure we never return > 0.9 unless computation was very strong
        # (The dynamics score usually caps around 1.0 naturally, but we enforce strictness)
        if final_conf > 0.9:
            # Only allow >0.9 if numeric derivation was explicit
            if "Arithmetic derivation" not in _: 
                final_conf = 0.85 # Penalize lack of explicit computation for very high confidence
                
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
