# Neural Plasticity + Free Energy Principle + Normalized Compression Distance

**Fields**: Biology, Theoretical Neuroscience, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T17:20:37.890199
**Report Generated**: 2026-03-27T05:13:35.130555

---

## Nous Analysis

**Algorithm**  
1. **Parse** the prompt and each candidate answer with a fixed set of regex patterns that extract atomic propositions \(p_i\) and label them with structural features (negation, comparative, conditional, causal, numeric, ordering). Each proposition becomes a node in a directed graph \(G=(V,E)\).  
2. **Initialize** edge weights \(w_{ij}\) as the pointwise mutual information of co‑occurrence of \(p_i\) and \(p_j\) within a sliding window of the prompt (computed with numpy counts).  
3. **Hebbian update**: for a candidate answer, compute activation vector \(a\) where \(a_i=1\) if \(p_i\) appears in the answer, else 0. Then \(w_{ij}\leftarrow w_{ij}+η·a_i·a_j\) (η = 0.01).  
4. **Synaptic pruning**: after each update, set \(w_{ij}=0\) if \(w_{ij}<τ\) (τ = 0.001) to keep the graph sparse.  
5. **Free‑energy‑like prediction error**: compute the expected description length \(L_{exp}=−∑_{i,j} w_{ij}·log p(w_{ij})\) (using numpy log). Compute the actual compressed length \(L_{act}=len(zlib.compress(text))\) where text is the concatenation of prompt + answer. Prediction error \(ε=|L_{act}−L_{exp}|\).  
6. **Score** the answer as \(S = NCD(prompt,answer) + λ·ε\) with λ = 0.5. Lower S indicates a better‑fitting answer. NCD is approximated by \((C_{xy}−min(C_x,C_y))/max(C_x,C_y)\) where \(C_*\) are zlib lengths. All operations use only numpy arrays and the std‑lib zlib** module.

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then …”), causal claims (“because”, “leads to”), numeric values (integers, decimals), ordering relations (“first”, “before”, “after”). These are turned into proposition labels that influence edge creation (e.g., a conditional creates a directed edge from antecedent to consequent).

**Novelty** – While NCD, Hebbian learning, and free‑energy minimization each appear separately in literature, their joint use as a text‑scoring pipeline that alternates synaptic‑style weight updates with compression‑based prediction error has not been described in existing work, making the combination novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and prediction error but relies on shallow regex parsing.  
Metacognition: 6/10 — error term provides a self‑monitoring signal, yet no explicit reflection on confidence.  
Hypothesis generation: 5/10 — generates candidate‑specific weight changes, but does not propose alternative hypotheses beyond scoring.  
Implementability: 8/10 — all steps use numpy and std‑lib; no external libraries or training data needed.

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

- **Neural Plasticity**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 29% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Neural Plasticity: strong positive synergy (+0.575). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Chaos Theory + Neural Plasticity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: AttributeError: 'ReasoningTool' object has no attribute '_extract_propctions'

**Forge Timestamp**: 2026-03-26T09:35:33.635064

---

## Code

**Source**: scrap

[View code](./Neural_Plasticity---Free_Energy_Principle---Normalized_Compression_Distance/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Neural Plasticity, Free Energy Principle, and Structural Parsing.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions with features (negation, causal, numeric).
    2. Neural Plasticity (Hebbian): Builds a co-occurrence graph from the prompt. Weights update 
       based on candidate activation (synaptic strengthening).
    3. Free Energy Principle: Computes prediction error as the delta between expected description 
       length (graph entropy) and actual compressed length.
    4. Scoring: Prioritizes structural constraint satisfaction (logic/numeric checks). Uses 
       Free Energy error as a secondary signal. NCD is restricted to tie-breaking only.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|higher|lower)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|therefore|leads to|causes|due to)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(?:\.\d+)?'),
        'ordering': re.compile(r'\b(first|last|before|after|next|previous)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.tau = 0.001  # Pruning threshold
        self.eta = 0.01   # Learning rate
        self.lambda_fep = 0.5 # FEP weight

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Parse text into atomic propositions with structural labels."""
        props = []
        text_lower = text.lower()
        
        # Check for presence of structural features
        features = {}
        for key, pattern in self.PATTERNS.items():
            if key != 'numeric':
                features[key] = bool(pattern.search(text_lower))
        
        # Extract numeric values for direct comparison logic
        numbers = [float(n) for n in self.PATTERNS['numeric'].findall(text)]
        
        # Create a node for the whole text context and specific features
        # Node 0: Global context
        props.append({'id': 0, 'text': 'global', 'features': features, 'numbers': numbers})
        
        # Create nodes for specific structural hits to allow graph connectivity
        node_id = 1
        for key, exists in features.items():
            if exists:
                props.append({'id': node_id, 'text': key, 'features': {key: True}, 'numbers': []})
                node_id += 1
                
        return props

    def _build_graph(self, prompt: str) -> Tuple[np.ndarray, List[str]]:
        """Initialize adjacency matrix based on co-occurrence (PMI approximation)."""
        props = self._extract_propctions(prompt)
        n = len(props)
        if n == 0:
            return np.array([]), []
            
        # Initialize weights with structural priors (stronger edges for logic markers)
        W = np.zeros((n, n))
        labels = [p['text'] for p in props]
        
        # Hebbian-like initialization: co-occurrence in the same sentence/window
        # Since we parsed the whole prompt, we assume high connectivity for structural elements
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Base connectivity
                    W[i, j] = 0.1 
                    # Boost if both are logical operators
                    if 'causal' in props[i]['features'] or 'conditional' in props[i]['features']:
                        if 'causal' in props[j]['features'] or 'conditional' in props[j]['features']:
                            W[i, j] = 0.5
        
        return W, labels

    def _hebbian_update(self, W: np.ndarray, prompt_props: List[Dict], answer_props: List[Dict]) -> np.ndarray:
        """Update edge weights based on candidate answer activation."""
        if W.size == 0:
            return W
            
        n = W.shape[0]
        # Activation vector: 1 if proposition type exists in answer, else 0
        # We map answer features back to the prompt's proposition indices by feature type
        a = np.zeros(n)
        
        # Map answer features to indices
        answer_features = set()
        for p in answer_props:
            for k, v in p['features'].items():
                if v: answer_features.add(k)
                
        for i, prop in enumerate(prompt_props):
            # Check if global or if specific feature matches
            if prop['text'] == 'global':
                a[i] = 1.0
            else:
                if prop['text'] in answer_features:
                    a[i] = 1.0
        
        # Hebbian update: W_ij += eta * a_i * a_j
        outer_product = np.outer(a, a)
        W_new = W + self.eta * outer_product
        
        # Synaptic pruning
        W_new[W_new < self.tau] = 0
        return W_new

    def _compute_fep_error(self, W: np.ndarray, prompt: str, answer: str) -> float:
        """Compute Free Energy-like prediction error."""
        if W.size == 0:
            return 1.0
            
        # Expected Description Length (Entropy of the graph)
        # Normalize weights to probability distribution
        w_sum = np.sum(W)
        if w_sum == 0:
            L_exp = 0.0
        else:
            P = W / w_sum
            # Avoid log(0)
            P_safe = P[P > 0]
            L_exp = -np.sum(P_safe * np.log(P_safe + 1e-9))
        
        # Actual Description Length (Compression)
        text = (prompt + " " + answer).encode('utf-8')
        L_act = len(zlib.compress(text))
        
        # Prediction Error
        # Scale L_act to be comparable to L_exp (rough heuristic)
        epsilon = abs(L_act * 0.01 - L_exp)
        return epsilon

    def _check_structural_logic(self, prompt: str, answer: str) -> float:
        """
        Primary scoring signal: Check if answer respects structural constraints.
        Returns a score boost (0.0 to 1.0).
        """
        score = 0.0
        p_low = prompt.lower()
        a_low = answer.lower()
        
        # 1. Negation Check
        if self.PATTERNS['negation'].search(p_low):
            # If prompt has negation, answer should ideally reflect it or be short (denial)
            # Heuristic: If prompt says "not X", and answer says "X", penalize.
            # This is hard without NLP, so we check for contradiction patterns.
            if re.search(r'\byes\b', a_low) and re.search(r'\bnot\b', p_low):
                # Ambiguous, but let's assume explicit confirmation of negative is good
                pass 
            score += 0.2 # Reward detecting negation context

        # 2. Numeric Consistency
        p_nums = [float(n) for n in self.PATTERNS['numeric'].findall(p_low)]
        a_nums = [float(n) for n in self.PATTERNS['numeric'].findall(a_low)]
        
        if len(p_nums) >= 2 and len(a_nums) >= 1:
            # Simple comparative check
            if "more than" in p_low or "greater than" in p_low:
                if a_nums[0] > p_nums[0]: # Rough heuristic
                    score += 0.3
            elif "less than" in p_low:
                if a_nums[0] < p_nums[0]:
                    score += 0.3
        
        # 3. Conditional/Logical Flow
        if self.PATTERNS['conditional'].search(p_low):
            # Reward answers that contain logical connectors or are concise
            if len(a_low.split()) < 10 or any(k in a_low for k in ['if', 'then', 'because', 'yes', 'no']):
                score += 0.2

        return min(score, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_props = self._extract_propositions(prompt)
        base_graph, _ = self._build_graph(prompt)
        
        results = []
        
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            
            # 1. Structural Logic Score (Primary Signal)
            logic_score = self._check_structural_logic(prompt, cand)
            
            # 2. Neural Plasticity Update
            if base_graph.size > 0:
                W_updated = self._hebbian_update(base_graph.copy(), prompt_props, cand_props)
            else:
                W_updated = base_graph
            
            # 3. Free Energy Prediction Error
            fep_error = self._compute_fep_error(W_updated, prompt, cand)
            
            # 4. NCD (Tiebreaker)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Final Score Construction
            # Higher is better. 
            # Logic provides the base. FEP error is subtracted (lower error = better).
            # NCD is used minimally as a tiebreaker for similar logic scores.
            base_score = logic_score * 10.0  # Scale up logic importance
            fep_penalty = fep_error * self.lambda_fep
            
            # Invert FEP error: lower error -> higher score
            # Normalize fep roughly: assume error < 5.0 is typical range
            fep_component = max(0, 2.0 - (fep_error * 0.2)) 
            
            total_score = base_score + fep_component - (ncd_val * 0.1)
            
            reasoning = f"Logic:{logic_score:.2f} FEP:{fep_component:.2f} NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and FEP."""
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        # Normalize score to 0-1 range heuristically
        # Logic score maxes around 1.0 * 10 = 10. FEP adds ~2.
        # So max theoretical ~12. 
        conf = min(1.0, max(0.0, score / 12.0))
        return conf
```

</details>
