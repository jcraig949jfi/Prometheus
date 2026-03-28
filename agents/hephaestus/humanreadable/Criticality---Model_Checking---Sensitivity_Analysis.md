# Criticality + Model Checking + Sensitivity Analysis

**Fields**: Complex Systems, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:49:41.763941
**Report Generated**: 2026-03-27T17:21:24.781552

---

## Nous Analysis

**Algorithm – Critical‑Sensitive Model Checker (CSMC)**  

1. **Parsing & Proposition Extraction**  
   - Use regex to capture atomic propositions:  
     *Negations* (`not`, `no`), *comparatives* (`>`, `<`, `>=`, `<=`, `more than`, `less than`), *conditionals* (`if … then …`, `unless`), *causal claims* (`because`, `leads to`, `results in`), *ordering* (`before`, `after`, `first`, `last`), *numeric values* (integers/floats).  
   - Each proposition `p_i` gets a Boolean variable `x_i`. Store propositions in a list `props` and map each to an index.

2. **Constraint Graph (Model‑Checking Structure)**  
   - Build a directed implication graph `G = (V, E)` where `V = {x_i}` and an edge `x_i → x_j` encodes a rule extracted from the prompt (e.g., “if A then B” → edge A→B).  
   - Represent adjacency as a NumPy boolean matrix `A` of shape `(n, n)`.  
   - Add unit clauses for facts directly asserted in the prompt (set corresponding `x_i = True`).

3. **Model‑Checking (Exhaustive State Exploration)**  
   - Perform forward chaining: initialize truth vector `t = zeros(n)`, set unit facts to 1, then iteratively compute `t_new = t | (A.T @ t)` until convergence (using NumPy dot product).  
   - The final `t` is the least model satisfying all Horn‑like constraints.  
   - Evaluate the candidate answer: extract its propositions `cand_props`, build a truth vector `t_cand` similarly, and compute satisfaction score  
     `sat = mean(t_cand & t)` (proportion of answer propositions that are true in the model).

4. **Sensitivity Analysis**  
   - For each proposition `x_i`, flip its truth value in the prompt (toggle unit fact), re‑run forward chaining, and record change in `sat`.  
   - Store finite‑difference gradient `g_i = |sat - sat_i|`.  
   - Compute sensitivity norm `‖g‖₂` (NumPy L2 norm).

5. **Criticality Scoring**  
   - Criticality is high when the answer lies near the satisfaction/unsatisfaction boundary (`sat ≈ 0.5`) and small input perturbations cause large changes (`‖g‖₂` large).  
   - Final score:  
     `score = (1 - |sat - 0.5| * 2) * (1 + tanh(‖g‖₂))`.  
   - The term `(1 - |sat - 0.5| * 2)` ranges from 0 (far from boundary) to 1 (exactly at 0.5); the tanh‑scaled sensitivity amplifies scores for fragile, critical answers.

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal verbs, ordering/temporal relations, numeric constants, and quantifiers (via regex patterns like `\b(all|some|none)\b`). These become the atomic propositions and edges of the implication graph.

**Novelty**  
Pure model‑checking tools (e.g., SPIN) verify specifications but do not measure sensitivity; sensitivity analysis in NLP usually estimates prediction variance without logical guarantees; criticality concepts come from physics. Combining exhaustive logical verification, gradient‑based sensitivity, and a boundary‑proximity criticality metric is not present in existing scoring pipelines, making the CSMC combination novel.

**Rating**  
Reasoning: 8/10 — captures logical entailment and quantifies how close an answer is to violating constraints.  
Metacognition: 6/10 — provides a self‑assessment via sensitivity but lacks explicit reasoning‑about‑reasoning loops.  
Hypothesis generation: 5/10 — focuses on verification; generating new hypotheses would require additional abduction.  
Implementability: 9/10 — relies only on regex, NumPy matrix ops, and fixed‑point iteration; straightforward to code in <150 lines.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Criticality + Model Checking: strong positive synergy (+0.917). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Phase Transitions + Criticality + Model Checking (accuracy: 0%, calibration: 0%)
- Prime Number Theory + Criticality + Model Checking (accuracy: 0%, calibration: 0%)
- Renormalization + Criticality + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=46% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:08:16.353675

---

## Code

**Source**: scrap

[View code](./Criticality---Model_Checking---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Critical-Sensitive Model Checker (CSMC)
    
    Mechanism:
    1. Parsing: Extracts atomic propositions based on negations, comparatives, conditionals,
       causal claims, ordering, and numeric values using regex.
    2. Model Construction: Builds a directed implication graph (adjacency matrix) where edges
       represent logical rules (e.g., "if A then B" -> A->B).
    3. Model Checking: Performs forward chaining (fixed-point iteration) to find the least
       model satisfying the constraints.
    4. Sensitivity Analysis: Perturbs input facts to measure the gradient of change in the
       satisfaction score of a candidate answer.
    5. Criticality Scoring: Combines proximity to the satisfaction boundary (0.5) with the
       sensitivity norm to produce a final score. High scores indicate answers that are 
       logically entailed but fragile (critical).
       
    Epistemic Honesty: Includes a meta-checker for Tier B traps (presuppositions, ambiguity)
    to cap confidence when the prompt structure is flawed or unanswerable.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': r'\b(not|no|never|none|neither)\b',
            'comparative': r'\b(more than|less than|greater than|smaller than|>=|<=|>|<)\b',
            'conditional': r'\b(if|then|unless|only if)\b',
            'causal': r'\b(because|leads to|results in|causes|implies)\b',
            'ordering': r'\b(before|after|first|last|preceding|following)\b',
            'numeric': r'\b\d+(\.\d+)?\b',
            'quantifier': r'\b(all|some|every|each|any)\b',
            # Tier B Traps
            'presupposition': r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)\b',
            'false_dichotomy': r'\b(either .+ or .+)\b',
            'subjectivity': r'\b(best|worst|favorite|most beautiful)\b'
        }
        self.compiled_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in self.patterns.items()}

    def _extract_props(self, text: str) -> List[str]:
        """Extract atomic propositions based on structural keywords and numeric values."""
        props = []
        # Simple sentence splitting for proposition granularity
        sentences = re.split(r'[.\n]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            found = False
            # Check for specific structural markers
            for key, regex in self.compiled_patterns.items():
                if key in ['presupposition', 'false_dichotomy', 'subjectivity']:
                    continue # Skip trap markers for proposition extraction
                match = regex.search(sent)
                if match:
                    # Normalize proposition: lowercase, strip punctuation
                    prop = re.sub(r'[^\w\s]', '', sent).lower().strip()
                    if prop and len(prop) > 2:
                        props.append(prop)
                        found = True
                        break
            
            # Fallback: if no structural keyword, treat meaningful chunks as props
            if not found and len(sent) > 5:
                prop = re.sub(r'[^\w\s]', '', sent).lower().strip()
                if prop:
                    props.append(prop)
        
        # Deduplicate while preserving order
        seen = set()
        unique_props = []
        for p in props:
            if p not in seen:
                seen.add(p)
                unique_props.append(p)
        return unique_props

    def _build_graph(self, prompt: str, props: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix A and initial truth vector t."""
        n = len(props)
        if n == 0:
            return np.zeros((0, 0)), np.zeros(0)
        
        A = np.zeros((n, n), dtype=bool)
        t = np.zeros(n, dtype=bool)
        prompt_lower = prompt.lower()
        
        # Map propositions to indices
        prop_to_idx = {p: i for i, p in enumerate(props)}
        
        # Extract rules and facts
        # Heuristic: If a sentence contains "if", link clauses. 
        # If a sentence is a simple assertion (no conditionals), set as fact.
        
        sentences = re.split(r'[.\n]', prompt)
        
        for sent in sentences:
            sent_lower = sent.lower()
            if not sent_lower.strip():
                continue
                
            # Identify which props are in this sentence
            present_indices = [i for i, p in enumerate(props) if p in sent_lower]
            
            if not present_indices:
                continue
                
            # Check for conditional structure
            if re.search(r'\bif\b', sent_lower) or re.search(r'\bleads to\b', sent_lower):
                # Simple heuristic: First prop implies last prop in the sentence context
                if len(present_indices) >= 2:
                    # Assume order in sentence implies direction (simplified)
                    # In a real parser, we'd parse syntax tree. Here we approximate.
                    src = present_indices[0]
                    tgt = present_indices[-1]
                    if src != tgt:
                        A[tgt, src] = True # Column src -> Row tgt (for dot product logic)
            else:
                # Assert facts: If the sentence asserts a proposition directly
                # We assume sentences mentioning the prop assert it unless negated
                is_negated = bool(re.search(self.patterns['negation'], sent_lower))
                for idx in present_indices:
                    if not is_negated:
                        t[idx] = True
                    else:
                        # If negated, we might set it to False, but default is False anyway.
                        # For Horn clauses, we mostly care about what IS true.
                        pass

        return A, t

    def _forward_chain(self, A: np.ndarray, t: np.ndarray) -> np.ndarray:
        """Perform forward chaining until convergence."""
        if A.size == 0:
            return t
        
        n = A.shape[0]
        t_curr = t.copy().astype(float)
        
        for _ in range(n + 2): # Max iterations for convergence
            t_new = t_curr.copy()
            # Matrix multiplication: (A.T @ t) gives implications
            # If A[j, i] is True, then i -> j. If t[i] is true, t[j] becomes true.
            implied = (A.T @ t_curr) > 0
            t_new = np.logical_or(t_curr, implied)
            
            if np.array_equal(t_curr, t_new):
                break
            t_curr = t_new.astype(float)
            
        return t_curr

    def _calculate_satisfaction(self, model: np.ndarray, candidate_props: List[str], all_props: List[str]) -> float:
        """Calculate proportion of candidate propositions true in the model."""
        if not candidate_props:
            return 0.0
        
        true_count = 0
        total_relevant = 0
        
        # Map all known props to indices
        prop_map = {p: i for i, p in enumerate(all_props)}
        
        for cp in candidate_props:
            cp_norm = cp.lower()
            # Check if this candidate prop exists in our model
            if cp_norm in prop_map:
                idx = prop_map[cp_norm]
                if model[idx]:
                    true_count += 1
                total_relevant += 1
            else:
                # Fuzzy match for substrings if exact match fails
                found = False
                for ap, idx in prop_map.items():
                    if cp_norm in ap or ap in cp_norm:
                        if model[idx]:
                            true_count += 1
                        total_relevant += 1
                        found = True
                        break
                if not found:
                    # If candidate mentions something not in prompt, it's not supported (False)
                    total_relevant += 1
                    
        return true_count / total_relevant if total_relevant > 0 else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps and ambiguity. Returns cap on confidence."""
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.compiled_patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.compiled_patterns['false_dichotomy'].search(p_lower):
            # Only flag if it looks like a forced choice without data
            if "or" in p_lower and "either" in p_lower:
                return 0.4
        
        # 3. Subjectivity without criteria
        if self.compiled_patterns['subjectivity'].search(p_lower):
            # If asking for "best" but no numbers/criteria provided
            if not self.compiled_patterns['numeric'].search(p_lower):
                return 0.3

        # 4. Ambiguity check (very heuristic: multiple question marks or "who/which" without clear antecedents)
        if p_lower.count("?") > 1:
            return 0.5
            
        return 1.0

    def _get_structural_score(self, prompt: str, candidate: str) -> float:
        """Core CSMC logic."""
        # 1. Parse Prompt
        prompt_props = self._extract_props(prompt)
        if not prompt_props:
            return 0.0
            
        # 2. Build Model
        A, t_init = self._build_graph(prompt, prompt_props)
        if A.size == 0:
            return 0.0
            
        # 3. Model Check (Forward Chaining)
        model = self._forward_chain(A, t_init)
        
        # 4. Parse Candidate
        cand_props = self._extract_props(candidate)
        if not cand_props:
            return 0.0
            
        # 5. Base Satisfaction
        sat = self._calculate_satisfaction(model, cand_props, prompt_props)
        
        # 6. Sensitivity Analysis
        # Perturb each initial fact and measure change in satisfaction
        n = len(prompt_props)
        gradients = []
        
        for i in range(n):
            t_perturbed = t_init.copy()
            # Toggle the fact
            t_perturbed[i] = not t_perturbed[i]
            
            # Re-run model check
            model_perturbed = self._forward_chain(A, t_perturbed)
            sat_perturbed = self._calculate_satisfaction(model_perturbed, cand_props, prompt_props)
            
            gradients.append(abs(sat - sat_perturbed))
        
        g_norm = np.linalg.norm(gradients) if gradients else 0.0
        
        # 7. Criticality Score
        # Proximity to boundary (0.5)
        boundary_term = 1.0 - abs(sat - 0.5) * 2.0
        boundary_term = max(0.0, boundary_term)
        
        # Sensitivity amplification
        sens_term = 1.0 + np.tanh(g_norm)
        
        # Final Score
        score = boundary_term * sens_term
        
        # Normalize roughly to 0-1 range (tanh caps at 2, boundary at 1)
        # Max theoretical ~2.0, so we might scale, but relative ranking matters most.
        return score

    def _get_ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z = lambda x: len(x.encode('utf-8')) # Placeholder for compression length
            # Using string length as proxy for compression size for speed/simplicity in this constraint
            # Real NCD uses zlib. Let's use zlib for correctness.
            import zlib
            l1 = len(zlib.compress(s1.encode()))
            l2 = len(zlib.compress(s2.encode()))
            l12 = len(zlib.compress((s1 + s2).encode()))
            
            if min(l1, l2) == 0:
                return 1.0
            ncd = (l12 - min(l1, l2)) / max(l1, l2)
            return max(0.0, min(1.0, ncd))
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate structural signals to ensure we beat NCD baseline
        structural_scores = []
        for cand in candidates:
            score = self._get_structural_score(prompt, cand)
            structural_scores.append(score)
        
        max_struct = max(structural_scores) if structural_scores else 0
        
        for i, cand in enumerate(candidates):
            struct_score = structural_scores[i]
            
            # NCD Tiebreaker (only if structural scores are low or identical)
            ncd_score = 0.0
            if max_struct < 0.1 or (len(set(structural_scores)) == 1):
                # Use NCD as secondary signal
                # Invert NCD: lower distance = higher similarity = higher score
                ncd_val = self._get_ncd_score(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.15 # Cap NCD contribution at 15%
            
            final_score = struct_score + ncd_score
            
            # Apply epistemic cap if the prompt itself is flawed
            if meta_cap < 0.5:
                final_score *= meta_cap
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural: {struct_score:.3f}, NCD: {ncd_score:.3f}, Meta-Cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is bad, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # Evaluate the specific answer
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]['score']
        
        # Map score to confidence
        # If structural score is high, confidence is high (but capped by meta)
        # If structural score is low, confidence is low
        base_conf = min(1.0, score * 1.5) # Scale up slightly to utilize range
        
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (score near 1.0)
        if score < 0.9:
            final_conf = min(final_conf, 0.9)
            
        return float(final_conf)
```

</details>
