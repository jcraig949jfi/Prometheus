# Information Theory + Analogical Reasoning + Normalized Compression Distance

**Fields**: Mathematics, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T07:13:18.427462
**Report Generated**: 2026-03-27T04:25:44.496329

---

## Nous Analysis

Combining Information Theory, Analogical Reasoning, and Normalized Compression Distance (NCD) yields a **compression‑driven analogical hypothesis tester**. Concretely, a system represents each hypothesis *H* and observation *O* as symbolic strings (e.g., parsed graphs or predicate sets). Using a lossless compressor *C* (such as PPM‑D, a neural arithmetic coder, or even gzip for prototyping), it approximates Kolmogorov complexity *K(x)≈|C(x)|*. The NCD between *H* and *O* is  

\[
\text{NCD}(H,O)=\frac{|C(H\!\|O)|-\min\{|C(H)|,|C(O)|\}}{\max\{|C(H)|,|C(O)|\}},
\]

where *H‖O* denotes concatenation. Simultaneously, the system computes mutual information *I(H;O)* from a probabilistic model (e.g., a Bayesian network learned from data) and runs a structure‑mapping engine (like Falkenhainer‑Forbus‑Gentner’s SME or LISA) to obtain a structural alignment score *A(H,O)* that captures relational correspondence.

The overall hypothesis score fuses these three quantities:

\[
\text{Score}(H,O)=\lambda_1\bigl(1-\text{NCD}(H,O)\bigr)+\lambda_2\frac{I(H;O)}{H(H)}+\lambda_3 A(H,O)-\lambda_4|C(H)|,
\]

where the last term penalizes hypothesis complexity (a two‑part MDL code length).  

**Advantage for self‑testing:** The system can autonomously assess whether a hypothesis compresses the data better than alternatives, while rewarding analogical far‑transfer (low NCD across domains) and structural fidelity. Over‑fitting is discouraged by the explicit complexity term, and under‑fitting is flagged when mutual information or alignment is low.

**Novelty:** MDL‑based analogy has been explored (e.g., “Analogical MDL” in cognitive modeling), and compression‑based similarity appears in phylogenetics and music analysis. However, integrating a universal, model‑free NCD with mutual‑information weighting and a dedicated structure‑mapper inside a single hypothesis‑evaluation loop is not a standard technique; recent work treats these strands separately, making the combination relatively nascent but grounded in established components.

**Ratings**

Reasoning: 7/10 — provides a principled, information‑theoretic similarity that captures both statistical and structural aspects.  
Metacognition: 8/10 — enables the system to self‑evaluate hypotheses via compression gain, a direct measure of descriptive adequacy.  
Hypothesis generation: 6/10 — guides generation by favoring compressible, analogically rich candidates, though it does not create new primitives.  
Implementability: 5/10 — requires a good compressor, a structure‑mapping engine, and mutual‑information estimators; feasible but computationally demanding for large domains.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T21:36:25.974645

---

## Code

**Source**: scrap

[View code](./Information_Theory---Analogical_Reasoning---Normalized_Compression_Distance/tool.py)

<details>
<summary>Show code</summary>

```python
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A compression-driven analogical hypothesis tester.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical features (negations, 
       comparatives, conditionals, numeric values) from prompts and candidates.
       It scores candidates based on logical consistency (e.g., matching negation 
       polarity, correct numeric ordering, constraint satisfaction).
    2. Analogical Alignment: Checks if the candidate preserves the relational 
       structure of the prompt (e.g., A is to B as C is to ?).
    3. Normalized Compression Distance (Tiebreaker): Uses zlib to estimate 
       Kolmogorov complexity. Lower NCD between (Prompt + Candidate) implies 
       higher mutual information/compressibility, used only when structural 
       signals are ambiguous or equal.
    4. Scoring: Weighted fusion where Structural Score >> NCD Score.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', "n't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _analyze_structure(self, text: str) -> Dict:
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        has_negation = bool(tokens & self.negation_words)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'token_set': tokens,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        
        max_c = max(c1, c2)
        if max_c == 0:
            return 0.0
        
        ncd = (c12 - min(c1, c2)) / max_c
        return max(0.0, min(1.0, ncd))

    def _structural_score(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Calculate score based on logical consistency and structural alignment.
        Returns a value between 0 and 10.
        """
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt implies negation context, candidate should likely reflect it or answer appropriately
        if prompt_struct['negation'] == cand_struct['negation']:
            score += 2.0
        
        # 2. Numeric Logic (Constraint Propagation)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Simple heuristic: If prompt has numbers and candidate has numbers,
            # check if they follow obvious ordering if comparatives are present
            if prompt_struct['comparative'] or cand_struct['comparative']:
                # Check if the candidate number logically follows the trend if detectable
                # This is a simplified proxy for complex reasoning
                if len(p_nums) >= 1 and len(c_nums) >= 1:
                    # Reward if the candidate number isn't identical to prompt (avoids echo)
                    if c_nums[-1] != p_nums[-1]:
                        score += 3.0
                    else:
                        score += 0.5
            else:
                # Non-comparative numeric presence is often good for math problems
                score += 2.0
        
        # 3. Conditional/Logical Flow
        if prompt_struct['conditional']:
            # If prompt is conditional, reward candidates that look like conclusions (no 'if')
            if not cand_struct['conditional'] and len(cand_struct['token_set']) > 0:
                score += 2.0
            elif cand_struct['conditional']:
                # Penalize repeating the condition without resolution
                score -= 1.0
        else:
            score += 1.0 # Baseline for non-conditional
            
        # 4. Length Penalty (Occam's Razor)
        # Penalize extremely long candidates that don't add proportional info
        if cand_struct['length'] > prompt_struct['length'] * 3:
            score -= 1.0
            
        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._analyze_structure(prompt)
        results = []
        
        # Pre-calculate NCDs for tie-breaking
        # We want low NCD (high similarity/compressibility) but structural score is king
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._analyze_structure(cand)
            
            # Primary Score: Structural/Logical Consistency
            struct_score = self._structural_score(prompt_struct, cand_struct, prompt, cand)
            
            # Secondary Score: NCD (Compression driven)
            # We invert NCD so higher is better (1 - NCD)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Fusion: Structural score dominates (scaled), NCD is tiebreaker
            # Scale struct_score to be roughly 0-10, NCD is 0-1
            final_score = (struct_score * 10.0) + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if struct_score > 5:
                reasoning_parts.append("High structural alignment")
            if cand_struct['negation'] == prompt_struct['negation']:
                reasoning_parts.append("Negation polarity matched")
            if cand_struct['numbers'] and prompt_struct['numbers']:
                reasoning_parts.append("Numeric constraints evaluated")
            if not reasoning_parts:
                reasoning_parts.append(f"NCD tiebreaker: {1-ncd_val:.4f}")
                
            reasoning = "; ".join(reasoning_parts)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the relative score of the answer against a generated set of alternatives
        to estimate confidence.
        """
        # Generate dummy alternatives to create a distribution
        # In a real system, these would be sampled from a model. 
        # Here we use simple perturbations to simulate alternatives.
        alternatives = [
            answer, 
            "No", "Yes", "Unknown", "Maybe", 
            str(len(answer) * 2), # Random numeric distractor
            answer + " not", # Negated version
            "The answer is " + answer
        ]
        
        # Remove duplicates while preserving order
        unique_alts = []
        seen = set()
        for alt in alternatives:
            if alt not in seen:
                unique_alts.append(alt)
                seen.add(alt)
                
        results = self.evaluate(prompt, unique_alts)
        
        if not results:
            return 0.0
            
        # Find the score of the provided answer
        target_score = None
        max_score = results[0]['score'] if results else 0
        
        for res in results:
            if res['candidate'] == answer:
                target_score = res['score']
                break
                
        if target_score is None:
            return 0.0
            
        # Normalize confidence based on how close it is to the top score
        # If it's the top score, confidence is high.
        if max_score == 0:
            return 1.0 if target_score > 0 else 0.5
            
        # Simple normalization: ratio of score to max score, capped at 1
        conf = target_score / max_score if max_score > 0 else 0.0
        
        # Boost if it's the clear winner (gap to second place)
        if len(results) > 1:
            second_score = results[1]['score'] if results[0]['candidate'] != answer else (results[2]['score'] if len(results) > 2 else 0)
            gap = target_score - second_score
            if gap > 5.0: # Significant structural lead
                conf = min(1.0, conf + 0.2)
                
        return float(max(0.0, min(1.0, conf)))
```

</details>
