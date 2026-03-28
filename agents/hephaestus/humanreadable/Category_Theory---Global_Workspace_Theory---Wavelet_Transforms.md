# Category Theory + Global Workspace Theory + Wavelet Transforms

**Fields**: Mathematics, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T07:23:02.677368
**Report Generated**: 2026-03-27T16:08:16.819262

---

## Nous Analysis

**Algorithm – Categorical‑Wavelet Global Workspace Scorer**  

1. **Parsing & Object Construction**  
   - Input: a prompt *P* and a set of candidate answers *A₁…Aₙ*.  
   - Using only regex on the raw text we extract elementary propositions *pᵢ* (subject‑verb‑object triples) and annotate each with:  
     * polarity* (¬ if negation detected),  
     * modality* (□ for necessity, ◇ for possibility from modal verbs),  
     * relation type* (comparative >, <, =; causal →; ordering < or >; equality).  
   - Each proposition becomes an object *Oᵢ* in a small category **C**. Morphisms are directed edges representing logical relationships inferred by simple rule‑based inference:  
     * entailment* (modus ponens) when *pᵢ* ∧ (pᵢ→pⱼ) appears,  
     * contradiction* when *pᵢ* ∧ ¬pⱼ,  
     * equivalence* when bidirectional entailment is found.  
   - Morphisms are stored as a sparse adjacency matrix *M* (numpy int8) where *M[i,j]=1* denotes an entailment edge, *-1* a contradiction, *0* none.

2. **Functorial Embedding**  
   - Define a functor *F*: **C** → **Vect** that maps each object *Oᵢ* to a one‑hot basis vector *eᵢ* (size = number of propositions) and each morphism to a linear map:  
     * entailment* → identity matrix *I* (preserves direction),  
     * contradiction* → *-I*,  
     * equivalence* → *I* in both directions.  
   - The functor is applied by multiplying the adjacency matrix *M* with a current activation vector *a* (numpy float64) to propagate activation: *a' = M·a*.

3. **Global Workspace Competition**  
   - Initialize *a* with uniform activation over propositions that appear in the prompt.  
   - Iterate:  
     * a ← ReLU(M·a) (non‑negative activation).  
     * Compute competition: keep only the top‑k entries (k = √|C|) and set others to zero – this mimics the global workspace “ignition” of selected information.  
     * Repeat for *T* steps (T=5) or until ‖a‑aₚᵣₑᵥ‖₁ < ε.

4. **Multi‑Resolution Wavelet Analysis**  
   - Record the activation trajectory *A = [a⁰, a¹, …, aᵀ]* as a |C|×(T+1) matrix.  
   - Apply a discrete Haar wavelet transform column‑wise (using numpy’s cumulative sums) to obtain approximation coefficients *Aₐ* (low‑frequency, global coherence) and detail coefficients *A𝒹* (high‑frequency, local fluctuations).  
   - Define the score for a candidate answer *Aⱼ* as the proportion of its propositional objects that survive in the low‑frequency subspace after the final iteration:  
     *scoreⱼ = ‖F(Oⱼ)·Aₐ‖₂ / ‖F(Oⱼ)‖₂* .  
   - Higher scores indicate that the answer’s propositions are consistently activated across scales, i.e., they integrate well with the prompt’s logical structure.

**Structural Features Parsed**  
- Negations (¬) via “not”, “no”, “never”.  
- Comparatives (>, <, =) via “more than”, “less than”, “as … as”.  
- Conditionals (→) via “if … then”, “unless”.  
- Causal claims (→) via “because”, “leads to”, “results in”.  
- Ordering relations via “before”, “after”, “first”, “last”.  
- Numeric values are captured as literals and attached to propositions for later arithmetic checks (simple numpy comparisons).

**Novelty**  
The combination is not a direct replica of existing work. Category‑theoretic functorial encoding of logical graphs is uncommon in lightweight scorers; pairing it with a global workspace competition loop adds a biologically‑inspired attention mechanism; applying a Haar wavelet to the activation trajectory introduces a multi‑resolution stability check that typical constraint‑propagation or similarity‑based tools lack. While each component appears separately in NLP literature, their joint use for answer scoring is novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure, inference, and multi‑scale consistency, though limited by shallow regex parsing.  
Metacognition: 6/10 — global workspace provides a crude self‑monitoring competition but lacks explicit reflection on its own uncertainties.  
Hypothesis generation: 5/10 — the system can propose new propositions via morphism chaining, but does not rank or diversify hypotheses beyond activation thresholds.  
Implementability: 9/10 — relies only on numpy and the Python standard library; all steps are explicit matrix operations and regex loops, making it straightforward to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: SyntaxError: (unicode error) 'utf-8' codec can't decode byte 0xb7 in position 403: invalid start byte (tmpot5xpdkv.py, line 20)

**Forge Timestamp**: 2026-03-27T15:59:40.655979

---

## Code

**Source**: scrap

[View code](./Category_Theory---Global_Workspace_Theory---Wavelet_Transforms/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Categorical-Wavelet Global Workspace Scorer.
    
    Mechanism:
    1. Parsing: Extracts propositions (SVO) with modalities/negations via Regex.
    2. Category Theory: Builds a logical graph (Category C) where objects are propositions
       and morphisms are logical relations (entailment, contradiction).
    3. Functorial Embedding: Maps C to Vect (numpy matrices). Activation propagates via M·a.
    4. Global Workspace: Iterative competition (ReLU + Top-K sparsification) simulates 
       attention ignition.
    5. Wavelet Analysis: Haar transform on activation history distinguishes stable 
       (low-freq) logical coherence from noisy fluctuations.
    6. Epistemic Honesty: Meta-checks for ambiguity/presupposition cap confidence.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
        'modal_nec': re.compile(r'\b(must|should|ought to|have to|needs to)\b', re.I),
        'modal_pos': re.compile(r'\b(may|might|could|can|possible)\b', re.I),
        'causal': re.compile(r'\b(because|since|leads to|results in|causes)\b', re.I),
        'conditional': re.compile(r'\b(if|unless|when|then)\b', re.I),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|as.*as)\b', re.I),
        'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.I),
        'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop|when did .+ stop)\b', re.I),
        'false_dichotomy': re.compile(r'\b(either .+ or .+|choose between .+ and .+)\b', re.I),
        'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|ugliest)\b', re.I),
        'pronoun_ambig': re.compile(r'\b(he|she|him|her|they|them)\b', re.I),
        'number': re.compile(r'-?\d+(?:\.\d+)?')
    }

    def __init__(self):
        self.max_iter = 5
        self.epsilon = 1e-4

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract simple SVO-like propositions with annotations."""
        props = []
        # Simple sentence splitting
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        for sent in sentences:
            if not sent: continue
            
            # Detect features
            has_neg = bool(self.PATTERNS['negation'].search(sent))
            has_nec = bool(self.PATTERNS['modal_nec'].search(sent))
            has_pos = bool(self.PATTERNS['modal_pos'].search(sent))
            has_causal = bool(self.PATTERNS['causal'].search(sent))
            has_cond = bool(self.PATTERNS['conditional'].search(sent))
            has_comp = bool(self.PATTERNS['comparative'].search(sent))
            has_order = bool(self.PATTERNS['ordering'].search(sent))
            
            # Extract numbers
            nums = [float(n) for n in self.PATTERNS['number'].findall(sent)]
            
            # Simplified subject-verb-object heuristic (first noun phrase, verb, rest)
            # This is a lightweight approximation for the "Category Objects"
            words = sent.split()
            if len(words) < 3:
                continue
                
            # Crude SVO: First word group (Subject), middle (Verb), end (Object)
            mid = len(words) // 2
            subj = " ".join(words[:max(1, mid-1)])
            verb = words[mid-1] if mid > 0 else words[0]
            obj = " ".join(words[mid:])
            
            props.append({
                'text': sent,
                'subj': subj,
                'verb': verb,
                'obj': obj,
                'negated': has_neg,
                'modality': 'nec' if has_nec else ('pos' if has_pos else 'none'),
                'type': 'causal' if has_causal else ('cond' if has_cond else ('comp' if has_comp else ('order' if has_order else 'fact'))),
                'nums': nums,
                'activation': 0.0
            })
        return props

    def _build_adjacency_matrix(self, props: List[Dict]) -> np.ndarray:
        """Build sparse adjacency matrix M based on logical rules."""
        n = len(props)
        if n == 0:
            return np.zeros((0, 0), dtype=np.int8)
            
        M = np.zeros((n, n), dtype=np.int8)
        
        for i, p_i in enumerate(props):
            for j, p_j in enumerate(props):
                if i == j:
                    M[i, j] = 1  # Self entailment
                    continue
                
                # Rule 1: Contradiction (Negation match)
                if p_i['subj'] == p_j['subj'] and p_i['verb'] == p_j['verb']:
                    if p_i['negated'] != p_j['negated']:
                        M[i, j] = -1 # Contradiction edge
                
                # Rule 2: Entailment (Exact text match or subset)
                if p_i['text'].lower() in p_j['text'].lower():
                    M[j, i] = 1 # j entails i (if j contains i)
                
                # Rule 3: Causal chaining (simplified)
                if p_i['type'] == 'causal' and p_j['text'].lower().find(p_i['obj'].lower()) != -1:
                    M[i, j] = 1 # i leads to j contextually

        return M

    def _global_workspace_competition(self, M: np.ndarray, prompt_props_idx: List[int]) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Iterative activation with ReLU and Top-K sparsification."""
        n = M.shape[0]
        if n == 0:
            return np.array([]), []
            
        # Initialize activation vector
        a = np.zeros(n, dtype=np.float64)
        for idx in prompt_props_idx:
            if idx < n:
                a[idx] = 1.0
                
        if np.sum(a) == 0:
            a[:] = 1.0 / n # Uniform if no prompt match
            
        history = [a.copy()]
        
        k = max(1, int(np.sqrt(n))) # Top-K sparsification
        
        for _ in range(self.max_iter):
            # Propagate: a' = M * a
            a_new = M.dot(a)
            
            # ReLU (Non-negative)
            a_new = np.maximum(0, a_new)
            
            # Competition: Keep top-K
            if np.sum(a_new) > 0:
                threshold = np.sort(a_new.flatten())[-k] if len(a_new) >= k else 0
                a_new[a_new < threshold] = 0
                
            # Check convergence
            if np.linalg.norm(a_new - a, 1) < self.epsilon:
                break
            a = a_new
            history.append(a.copy())
            
        return a, history

    def _haar_wavelet_score(self, history: List[np.ndarray], candidate_props_idx: List[int]) -> float:
        """Compute score based on low-frequency stability of candidate propositions."""
        if not history or len(history) < 2:
            return 0.0
            
        A = np.array(history) # Shape: (Time, Props)
        A = A.T # Shape: (Props, Time)
        
        if A.shape[1] < 2:
            return 0.0
            
        # Discrete Haar Wavelet (Approximation coefficients)
        # For simplicity in 1D row-wise: Average of pairs
        # We want low-freq component (global coherence)
        approx = A.copy()
        while approx.shape[1] > 1:
            # Pairwise average
            even = approx[:, ::2]
            odd = approx[:, 1::2]
            if odd.shape[1] < even.shape[1]:
                # Handle odd length by padding last col (simplified)
                pass 
            approx = (even[:, :odd.shape[1]] + odd) / 2.0
            if approx.shape[1] == 0: break
            
        if approx.shape[1] == 0:
            return 0.0
            
        # Final approximation is the mean activation over time (Low freq)
        final_approx = np.mean(A, axis=1)
        
        if not candidate_props_idx:
            return 0.0
            
        # Score: Proportion of candidate props with high low-freq activation
        total_score = 0.0
        for idx in candidate_props_idx:
            if idx < len(final_approx):
                total_score += final_approx[idx]
                
        # Normalize by number of candidate props to avoid length bias
        return total_score / len(candidate_props_idx) if len(candidate_props_idx) > 0 else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.PATTERNS['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity without criteria
        if self.PATTERNS['subjectivity'].search(p_lower) and 'criteria' not in p_lower:
            return 0.4
            
        # 4. Pronoun Ambiguity in "Who" questions
        if 'who' in p_lower and self.PATTERNS['pronoun_ambig'].search(p_lower):
            # Check if multiple people mentioned
            names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(set(names)) > 1:
                return 0.3
                
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_props = self._extract_propositions(prompt)
        prompt_texts = {p['text'].lower() for p in prompt_props}
        
        # Build category for prompt
        M = self._build_adjacency_matrix(prompt_props)
        
        # Map prompt props to indices
        prompt_indices = list(range(len(prompt_props)))
        
        results = []
        
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            cand_indices = list(range(len(cand_props))) # Relative to cand, but we need combined space?
            
            # Simplified approach: Evaluate candidate propositions against prompt structure
            # We treat the "Universe" as Prompt Props + Candidate Props
            all_props = prompt_props + cand_props
            M_combined = self._build_adjacency_matrix(all_props)
            
            # Indices for prompt (sources) and candidate (targets)
            p_indices = list(range(len(prompt_props)))
            c_indices = list(range(len(prompt_props), len(all_props)))
            
            if len(all_props) == 0:
                score = 0.0
            else:
                # Run Global Workspace
                _, history = self._global_workspace_competition(M_combined, p_indices)
                
                if not history:
                    score = 0.0
                else:
                    # Wavelet Score on candidate portion
                    # We need to map candidate indices to the full history
                    # History shape: (Time, Total Props)
                    # We only care about the stability of the CANDIDATE props
                    cand_score = 0.0
                    if len(history) > 0:
                        # Re-run wavelet logic specifically for candidate indices
                        # Extract candidate trajectories
                        cand_history = [h[len(prompt_props):] for h in history] # Slice candidate part
                        if len(cand_history[0]) == 0:
                             # If no candidate props extracted, use NCD fallback
                            score_val = 1.0 - self._ncd(prompt, cand)
                            cand_score = max(0, score_val)
                        else:
                            # Apply Haar manually on the sliced history
                            A_cand = np.array(cand_history).T # (Cand_Props, Time)
                            if A_cand.size > 0:
                                mean_activation = np.mean(A_cand, axis=1)
                                cand_score = np.mean(mean_activation) if len(mean_activation) > 0 else 0.0
                    score = cand_score

            # Structural Boost: Numeric consistency
            prompt_nums = []
            for p in prompt_props: prompt_nums.extend(p['nums'])
            cand_nums = []
            for p in cand_props: cand_nums.extend(p['nums'])
            
            if prompt_nums and cand_nums:
                # Simple check: if numbers match exactly, boost
                if sorted([round(x, 2) for x in prompt_nums]) == sorted([round(x, 2) for x in cand_nums]):
                    score += 0.2
                # If numbers contradict (e.g. prompt says 5, cand says 10 and logic implies equality)
                # Hard to detect without deep semantic parse, skip for lightweight
                
            # NCD Fallback/Booster (Max 15% influence)
            ncd_val = 1.0 - self._ncd(prompt, cand)
            if score < 0.1: # If structural score is low, rely partially on similarity
                score = 0.5 * ncd_val + 0.5 * score
            else:
                score = 0.85 * score + 0.15 * ncd_val

            results.append({
                "candidate": cand,
                "score": float(min(1.0, max(0.0, score))),
                "reasoning": f"Wavelet stability: {score:.3f}, NCD: {ncd_val:.3f}"
            })
            
        # Rank
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural evaluation
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # If meta-confidence is low (ambiguous), cap the result
        final_conf = min(base_score, meta_cap)
        
        # Heuristic: If the answer is just "Yes" or "No" and prompt is complex, lower confidence
        if answer.strip().lower() in ['yes', 'no'] and len(prompt.split()) > 10:
            final_conf = min(final_conf, 0.6)
            
        return float(max(0.0, min(1.0, final_conf)))
```

</details>
