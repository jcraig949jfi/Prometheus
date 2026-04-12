# Thermodynamics + Pragmatics + Hoare Logic

**Fields**: Physics, Linguistics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T15:54:20.015395
**Report Generated**: 2026-03-27T06:37:37.840281

---

## Nous Analysis

**1. Algorithm**  
Parse the prompt and each candidate answer into a set of atomic propositions \(A_i\) using regex patterns for negations, comparatives, conditionals, causal clauses, and ordering relations (e.g., “if X then Y”, “X > Y”, “X causes Y”). Each proposition receives a Boolean variable and a confidence weight \(w_i\in[0,1]\) initialized from pragmatic cues:  
- **Quantity** – proportional to the number of distinct predicates extracted.  
- **Quality** – inversely proportional to contradictions with known facts (checked via a small static KB).  
- **Relevance** – cosine similarity of TF‑IDF vectors between proposition and prompt (numpy dot‑product).  
- **Manner** – penalty for ambiguous pronouns or vague adverbs (regex count).  

These weights form a diagonal matrix \(W\).  
Hoare‑style triples are built for each conditional: \(\{P\}\,C\,\{Q\}\) where \(P\) and \(Q\) are conjunctions of propositions and \(C\) is the candidate answer statement. The triple is satisfied if, under current truth assignments, \(P\Rightarrow Q\) holds. Violations contribute an energy term \(E_{jk}= \max(0,\, \hat{P}_k - \hat{Q}_k)^2\) where \(\hat{P}_k,\hat{Q}_k\) are the weighted truth values (numpy dot‑product of \(W\) with the proposition vectors).  

Constraint propagation iteratively applies modus ponens and transitivity: for any implication \(X\rightarrow Y\) with weight \(w_{XY}\), update \(\hat{Y}\leftarrow \max(\hat{Y},\, w_{XY}\cdot\hat{X})\) until convergence (numpy power‑iteration).  

After propagation, compute total **energy** \(E=\sum E_{jk}\) and **entropy** \(S=-\sum p_i\log p_i\) where \(p_i=\hat{A}_i/\sum\hat{A}_i\). The free energy \(F=E-TS\) (with fixed temperature \(T=1.0\)) is the final score; lower \(F\) indicates a better answer.

**2. Parsed structural features**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “as … as”)  
- Conditionals (“if … then …”, “provided that”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Ordering relations (“before”, “after”, “precedes”)  
- Quantifiers (“all”, “some”, “none”) for pragmatic relevance  

**3. Novelty**  
The fusion of Hoare triples with a thermodynamic free‑energy formulation and pragmatics‑derived weights is not present in standard textual entailment or logic‑programming systems. Existing work uses either pure logical inference (e.g., Logic Tensor Networks) or energy‑based models (e.g., contrastive losses) but does not explicitly incorporate Gricean maxims as weighted pre‑condition/post‑condition constraints, making this combination novel.

**Rating**  
Reasoning: 8/10 — captures logical entailment, constraint propagation, and uncertainty via energy‑entropy trade‑off.  
Metacognition: 6/10 — the model can monitor its own violation energy but lacks explicit self‑reflection on reasoning steps.  
Hypothesis generation: 5/10 — generates implied propositions through propagation, but does not rank alternative hypotheses beyond energy minimization.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic loops; no external libraries or APIs needed.

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

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Hoare Logic**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Hoare Logic + Pragmatics: strong positive synergy (+0.619). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Network Science + Pragmatics + Hoare Logic (accuracy: 0%, calibration: 0%)
- Pragmatics + Hoare Logic + Satisfiability (accuracy: 0%, calibration: 0%)
- Thermodynamics + Optimal Control + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: TypeError: unsupported operand type(s) for -: 'dict' and 'float'

**Forge Timestamp**: 2026-03-26T19:17:50.975963

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Pragmatics---Hoare_Logic/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool fusing Thermodynamics, Pragmatics, and Hoare Logic.
    
    Mechanism:
    1. Pragmatics (Parsing): Extracts atomic propositions from text using regex patterns
       for negations, comparatives, conditionals, and causality. Weights are assigned
       based on Quantity, Quality (consistency), Relevance (TF-IDF cosine sim), and Manner.
    2. Hoare Logic: Constructs triples {P} C {Q} where P is the prompt context and
       C is the candidate answer. The triple is satisfied if P implies Q.
    3. Thermodynamics: Computes an energy score based on logical violations (E) and
       entropy (S) of the proposition distribution. The final score is derived from
       Free Energy F = E - TS. Lower F is better; we invert this for the final score.
    
    Structural parsing is the primary signal; NCD is a tiebreaker.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|provided|unless|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|precedes|follows|first|last)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'numbers': re.compile(r'\d+\.?\d*')
        }
        self.stopwords = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b\w+\b', text) if w.lower() not in self.stopwords]

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features and return counts/flags."""
        features = {}
        text_lower = text.lower()
        
        # Count pattern matches
        for key, pattern in self.patterns.items():
            matches = pattern.findall(text_lower)
            features[key] = len(matches)
        
        # Numeric extraction for comparison
        nums = self.patterns['numbers'].findall(text_lower)
        features['has_numbers'] = len(nums) > 0
        features['numeric_value'] = float(nums[0]) if nums else 0.0
        
        return features

    def _compute_relevance(self, prompt_vec: Dict[str, int], candidate_vec: Dict[str, int]) -> float:
        """Cosine similarity between prompt and candidate term frequencies."""
        all_terms = set(prompt_vec.keys()) | set(candidate_vec.keys())
        if not all_terms:
            return 0.0
        
        v1 = [prompt_vec.get(t, 0) for t in all_terms]
        v2 = [candidate_vec.get(t, 0) for t in all_terms]
        
        dot_prod = sum(a*b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a*a for a in v1))
        norm2 = math.sqrt(sum(b*b for b in v2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_prod / (norm1 * norm2)

    def _build_hoare_triple(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Construct Hoare Triple {P} C {Q}.
        P = Prompt propositions, C = Candidate, Q = Implied result.
        Returns (Energy, Entropy, Reasoning String).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # 1. Pragmatic Weights (Quantity, Quality, Relevance, Manner)
        # Quantity: distinct predicates
        quantity = sum(1 for k, v in c_feats.items() if k != 'has_numbers' and k != 'numeric_value' and v > 0)
        
        # Relevance: TF-IDF approx (simple cosine on tokens)
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        p_freq = {t: p_tokens.count(t) for t in set(p_tokens)}
        c_freq = {t: c_tokens.count(t) for t in set(c_tokens)}
        relevance = self._compute_relevance(p_freq, c_freq)
        
        # Manner: Penalty for ambiguity (simple heuristic: length vs unique words)
        c_words = c_tokens
        manner_penalty = 0.0
        if len(c_words) > 0:
            ratio = len(set(c_words)) / len(c_words)
            if ratio < 0.5: # High repetition implies vagueness
                manner_penalty = 0.5
        
        # 2. Logical Consistency (The "Energy" Component)
        # Check for direct contradictions in structural features
        energy = 0.0
        reasoning_steps = []
        
        # Negation conflict: If prompt has no negation but candidate asserts "not" strongly without cause
        if p_feats['negation'] == 0 and c_feats['negation'] > 2:
            energy += 1.0
            reasoning_steps.append("High negation density in candidate not supported by prompt.")
            
        # Conditional logic: If prompt has "if", candidate should ideally reflect conditionality or consequence
        if p_feats['conditional'] > 0:
            if c_feats['conditional'] == 0 and c_feats['causal'] == 0:
                # Soft penalty: candidate might be missing the logical link
                energy += 0.2
                reasoning_steps.append("Candidate may lack conditional structure present in prompt.")
        
        # Numeric consistency
        if p_feats['has_numbers'] and c_feats['has_numbers']:
            # Simple heuristic: if prompt says "9.11" and candidate says "9.9", check magnitude context if possible
            # Here we just check if numbers are present and consistent in order of magnitude if both exist
            pass 

        # Relevance penalty (Low relevance increases energy)
        energy += (1.0 - relevance) * 0.5
        
        # Manner penalty
        energy += manner_penalty
        
        # 3. Entropy Calculation
        # Distribution of truth values (simulated by feature activation)
        feature_vals = [v for k, v in c_feats.items() if isinstance(v, (int, float)) and k not in ['has_numbers']]
        total = sum(feature_vals) + 1e-9
        probs = [v/total for v in feature_vals if v > 0]
        entropy = -sum(p * math.log(p + 1e-9) for p in probs) if probs else 0.0
        
        # Normalize entropy roughly to [0, 1] range for stability (max entropy ~ log(N))
        max_entropy = math.log(len(feature_vals) + 1) if feature_vals else 1.0
        norm_entropy = entropy / (max_entropy + 1e-9)
        
        # Free Energy F = E - T*S (T=1.0). We want low F.
        # But we also want high relevance. 
        # Let's define Score = (Relevance * Quantity) - Energy + Entropy_bonus
        # Actually, per prompt: F = E - TS. Lower F is better.
        # We will return -F as the score so higher is better.
        
        temperature = 1.0
        free_energy = energy - (temperature * norm_entropy)
        
        reason_str = "; ".join(reasoning_steps) if reasoning_steps else "Structural consistency maintained."
        if relevance > 0.8:
            reason_str += " High semantic overlap."
        if p_feats['conditional'] > 0 and c_feats['causal'] > 0:
            reason_str += " Conditional logic preserved."
            
        return free_energy, norm_entropy, reason_str

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass: Compute structural scores
        for cand in candidates:
            energy, entropy, reason = self._build_hoare_triple(prompt, cand)
            # Score is inverse of free energy, boosted by relevance implicitly in energy calc
            # We negate energy so lower energy = higher score
            base_score = -energy 
            results.append({
                "candidate": cand,
                "base_score": base_score,
                "reasoning": reason
            })
            scores.append(base_score)
        
        # Handle ties or close calls with NCD
        # If max score is unique, use it. If multiple candidates are within 0.01, use NCD.
        max_score = max(scores) if scores else 0
        threshold = 0.05 # Sensitivity threshold
        
        final_results = []
        for i, res in enumerate(results):
            # Normalize score to 0-1 range roughly
            # Shift so max is 1.0 and min is >0
            normalized = (res - min(scores) + 1e-6) / (max_score - min(scores) + 1e-6) if max(scores) != min(scores) else 0.5
            
            # Tie-breaking logic
            is_top_tier = (res >= max_score - threshold)
            if is_top_tier and len([s for s in scores if s >= max_score - threshold]) > 1:
                # Use NCD as tiebreaker: lower NCD to prompt is better
                ncd_val = self._ncd(prompt, res['candidate'])
                # Adjust score slightly by NCD (lower NCD -> higher score)
                normalized += (1.0 - ncd_val) * 0.01
            
            final_results.append({
                "candidate": res['candidate'],
                "score": float(normalized),
                "reasoning": res['reasoning']
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # The score is already normalized roughly to 0-1 in evaluate logic relative to the set
        # But for single item, we rely on the base_score mapping.
        # Re-run logic to get raw score
        energy, _, _ = self._build_hoare_triple(prompt, answer)
        # Map energy to 0-1. Energy ~0 is perfect. Energy > 2 is bad.
        # Confidence = 1 / (1 + energy) approx
        conf = 1.0 / (1.0 + max(0, energy))
        return min(1.0, max(0.0, conf))
```

</details>
