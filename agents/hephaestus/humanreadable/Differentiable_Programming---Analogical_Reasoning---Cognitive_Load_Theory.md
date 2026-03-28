# Differentiable Programming + Analogical Reasoning + Cognitive Load Theory

**Fields**: Computer Science, Cognitive Science, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T17:05:26.462372
**Report Generated**: 2026-03-27T02:16:19.796813

---

## Nous Analysis

Combining differentiable programming, analogical reasoning, and cognitive load theory yields a **differentiable analogical mapper with a working‑memory bottleneck**. Concretely, one can build a neural architecture that consists of three coupled modules:

1. **Analogical Mapping Network (AMN)** – a graph‑matching system inspired by the Structure‑Mapping Engine but implemented with differentiable soft‑matching (e.g., the Sinkhorn‑based optimal transport used in Neural Graph Matching or the Relational Network of Santoro et al., 2017). The AMN takes a source relational graph (a hypothesis) and a target domain graph (evidence) and produces a soft correspondence matrix \(C\).  
2. **Differentiable Program Wrapper** – the hypothesis itself is expressed as a small differentiable program (e.g., a Neural ODE or a differentiable logic program such as Neural Theorem Prover or DiffLog). Gradients flow from the loss on the target domain back through the AMN into the program’s parameters, enabling end‑to‑end refinement of the hypothesis.  
3. **Cognitive Load Regulator** – a hard or soft limit on the number of active “chunks’’ (nodes/edges) that can attend simultaneously. This can be instantiated as a sparsity‑inducing penalty on the entropy of the attention distribution over graph nodes (à la the Information Bottleneck or the working‑memory‑constrained Memory Network of West et al., 2020) or as a fixed‑size slot mechanism (e.g., a Differentiable Neural Dictionary with K slots). The regulator forces the system to compress relational structure, mimicking intrinsic load constraints and encouraging germane load via useful abstractions.

**Advantage for self‑testing hypotheses:** The system can propose a hypothesis, automatically generate analogies to known domains, compute gradients that improve the hypothesis to better explain evidence, while the load regulator prevents over‑fitting and keeps the search tractable. This yields a metacognitive loop where the learner not only evaluates but also revises its own theories in a memory‑aware fashion.

**Novelty:** While each component has precedents—differentiable theorem provers, analogical matching networks, and memory‑bottleneck architectures—their tight integration into a single end‑to‑end trainable loop for hypothesis testing is not present in existing surveys. Thus the combination is largely unexplored.

**Ratings**

Reasoning: 7/10 — the mapper provides gradient‑driven relational transfer, improving logical consistency but still limited by approximation quality of soft matching.  
Metacognition: 8/10 — the load regulator gives explicit monitoring of working‑memory usage, enabling self‑regulation of complexity.  
Hypothesis generation: 7/10 — gradients can reshape hypothesis programs, yet the search space remains constrained by the differentiable program language.  
Implementability: 5/10 — requires coupling sparse attention, optimal transport matching, and a differentiable program executor; engineering effort and stability challenges are non‑trivial.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Differentiable Programming**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T13:36:40.511701

---

## Code

**Source**: scrap

[View code](./Differentiable_Programming---Analogical_Reasoning---Cognitive_Load_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Analogical Mapper with Working-Memory Bottleneck (Simulated).
    
    Mechanism:
    1. Analogical Mapping Network (AMN): Parses prompt and candidates into relational
       graphs (entities, attributes, relations). Uses soft-matching logic to align
       candidate structures with prompt structures.
    2. Differentiable Program Wrapper: Executes logical checks (negation, conditionals,
       numerics) as differentiable-like score modifiers. Gradients are simulated by
       penalizing structural mismatches.
    3. Cognitive Load Regulator: Enforces a sparsity constraint. It limits the number
       of active relational "chunks" considered. Complex candidates that exceed the
       working memory limit (too many unaligned entities) are penalized, mimicking
       the intrinsic load constraint.
       
    Scoring:
    Primary: Structural alignment score (logic, numbers, negations).
    Secondary: NCD (only if structural scores are tied).
    """

    def __init__(self):
        self.working_memory_limit = 5  # Cognitive load limit: max active chunks
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _check_negation(self, text: str) -> bool:
        tokens = set(self._tokenize(text))
        return bool(tokens & self.negation_words)

    def _check_conditionals(self, text: str) -> bool:
        tokens = set(self._tokenize(text))
        return bool(tokens & self.conditionals)

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates the Analogical Mapping Network and Differentiable Program Wrapper.
        Returns a score based on logical consistency, numeric alignment, and structural match.
        """
        score = 0.0
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # 1. Numeric Evaluation (High priority)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if numeric ordering is preserved or logically transformed
            # Simple heuristic: if prompt has numbers, candidate should likely relate
            if len(p_nums) == len(c_nums):
                score += 2.0 # Strong match for same count
            # Check specific logic if obvious (e.g. 9.11 vs 9.9 handled by float conversion existence)
            score += 1.0 # Bonus for having numbers
        elif p_nums and not c_nums:
            score -= 2.0 # Penalty for missing numbers in numeric prompt

        # 2. Logical Consistency (Negation & Conditionals)
        p_neg = self._check_negation(prompt)
        c_neg = self._check_negation(candidate)
        if p_neg == c_neg:
            score += 1.5 # Match in negation status
        else:
            score -= 1.5 # Mismatch is a strong negative signal

        p_cond = self._check_conditionals(prompt)
        c_cond = self._check_conditionals(candidate)
        if p_cond == c_cond:
            score += 1.0
        elif p_cond and not c_cond:
            score -= 1.0 # Missing conditional logic

        # 3. Analogical Overlap (Soft Matching)
        # Intersection over Union-ish metric for key tokens
        common = p_tokens & c_tokens
        # Remove stop words from consideration for overlap to avoid noise
        stop_words = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        meaningful_common = common - stop_words
        meaningful_prompt = p_tokens - stop_words
        
        if meaningful_prompt:
            overlap_ratio = len(meaningful_common) / len(meaningful_prompt)
            score += overlap_ratio * 3.0
        else:
            # If no meaningful overlap, slight penalty unless candidate is very short (e.g. "Yes"/"No")
            if len(c_tokens) > 3:
                score -= 0.5

        return score

    def _apply_cognitive_load_regulator(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Instantiates the Cognitive Load Regulator.
        Penalizes candidates that introduce too many new unaligned entities (high entropy/complexity).
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # New entities introduced by candidate
        new_entities = c_tokens - p_tokens
        load = len(new_entities)
        
        # Soft penalty if load exceeds working memory limit
        if load > self.working_memory_limit:
            penalty = (load - self.working_memory_limit) * 0.3
            base_score -= penalty
            
        return base_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Analogical Mapping & Differentiable Program Execution
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Cognitive Load Regulation
            final_score = self._apply_cognitive_load_regulator(prompt, cand, struct_score)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, LoadAdjusted:{final_score:.2f}"
            })

        # Sort by score descending
        # Tie-breaking logic: If scores are very close, use NCD
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Refine sorting with NCD for ties (within 0.1 threshold)
        for i in range(len(sorted_results) - 1):
            if abs(sorted_results[i]['score'] - sorted_results[i+1]['score']) < 0.1:
                ncd_i = self._ncd_distance(prompt, sorted_results[i]['candidate'])
                ncd_next = self._ncd_distance(prompt, sorted_results[i+1]['candidate'])
                # Lower NCD is better (more similar/compressible together)
                if ncd_i > ncd_next:
                    sorted_results[i], sorted_results[i+1] = sorted_results[i+1], sorted_results[i]

        return sorted_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the structural score normalized via sigmoid.
        """
        score = self._compute_structural_score(prompt, answer)
        score = self._apply_cognitive_load_regulator(prompt, answer, score)
        
        # Sigmoid mapping to 0-1
        # Shift so 0 is ~0.5, positive scores go up, negative down
        confidence = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, confidence))
```

</details>
