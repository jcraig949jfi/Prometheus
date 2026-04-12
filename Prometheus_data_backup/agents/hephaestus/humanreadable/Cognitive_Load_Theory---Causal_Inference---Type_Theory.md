# Cognitive Load Theory + Causal Inference + Type Theory

**Fields**: Cognitive Science, Information Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:59:01.475523
**Report Generated**: 2026-03-27T03:25:59.226311

---

## Nous Analysis

Combining Cognitive Load Theory, Causal Inference, and Type Theory yields a **load‑aware causal type‑checking engine** that operates inside a proof‑assistant‑style environment (e.g., an extension of Lean or Agda). The engine represents each causal hypothesis as a dependent type whose parameters encode structural assumptions (DAG edges, functional forms, and intervention signatures). Type‑checking a hypothesis corresponds to verifying that the proposed DAG satisfies the do‑calculus rules and that any derived counterfactuals are well‑typed. Cognitive load is modeled as a quantitative budget attached to each type‑checking step: intrinsic load reflects the size of the term (number of variables and arrows), extraneous load is penalized for unnecessary syntactic sugar or redundant lemmas, and germane load is rewarded when the term re‑uses previously proven lemmas (chunking). An optimizer continuously rewrites the proof term to stay under a user‑specified load threshold, discarding or simplifying hypotheses that would exceed it.

**Advantage for self‑testing:** When the system proposes a new causal hypothesis, it first attempts to type‑check the corresponding do‑calculus derivation. If the check fails, the type error pinpoints exactly which assumption is violated (e.g., a missing back‑door path). Because the checker tracks load, the system can automatically generate alternative, lower‑load variants (by chunking sub‑derivations or applying known lemmas) and re‑test them, yielding a metacognitive loop that balances explanatory power against cognitive feasibility. This lets the agent prune implausible causal models early, focus its limited working memory on promising candidates, and iteratively refine interventions based on type‑sound feedback.

**Novelty:** While each component has been explored separately — probabilistic programming languages with dependent types (e.g., **Featherweight Haskell** for Bayesian models), causal inference embedded in type theory (research on “Causal Calculus in Dependent Type Theory”), and cognitive‑load‑aware tutoring systems — no existing framework unifies all three to drive a self‑checking, load‑budgeted causal reasoner. Thus the combination is largely novel, though it builds on adjacent work.

**Ratings**

Reasoning: 8/10 — The engine provides sound, type‑checked causal deductions and can automatically explore alternatives, markedly improving logical rigor over pure statistical methods.  
Metacognition: 7/10 — Load tracking gives the system explicit self‑monitoring of working‑memory usage, though translating human‑like chunking into term rewriting remains heuristic.  
Hypothesis generation: 7/10 — By generating load‑constrained variants of failed type checks, the system proposes useful refinements, but the space of possible chunks is still large.  
Implementability: 6/10 — Requires extending a proof assistant with causal DSLs and load metrics; feasible with current tooling but non‑trivial engineering effort.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 6/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Causal Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T02:30:17.717171

---

## Code

**Source**: scrap

[View code](./Cognitive_Load_Theory---Causal_Inference---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Load-Aware Causal Type-Checker (LACTC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Causal/Type Logic): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a 'structural signature'.
       This mimics the 'type-checking' of causal hypotheses against the prompt's constraints.
    2. Cognitive Load Modeling: Calculates a 'load score' based on the complexity of the 
       candidate relative to the prompt. Short, direct answers that satisfy structural 
       constraints (e.g., matching negation logic) receive lower 'extraneous load' (higher score).
    3. Germane Load (Chunking): Rewards candidates that reuse specific terminology from the 
       prompt (simulating lemma reuse), penalizing generic or unrelated text.
    4. Scoring: Candidates are ranked by how well their structural signature matches the 
       prompt's implied logic (e.g., if prompt has 'not', correct answer often lacks the 
       affirmed term or explicitly negates it), adjusted by load. 
    5. NCD Tiebreaker: Uses Normalized Compression Distance only when structural signals are equal.
    """

    def __init__(self):
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible', 'false']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for causal magnitude comparison."""
        pattern = r"-?\d+\.\d+|-?\d+"
        try:
            return [float(x) for x in re.findall(pattern, text)]
        except:
            return []

    def _has_token(self, text: str, tokens: List[str]) -> bool:
        text_lower = text.lower()
        return any(t in text_lower for t in tokens)

    def _structural_signature(self, text: str) -> Tuple[bool, bool, bool, int]:
        """
        Extracts a tuple representing the logical structure:
        (has_negation, has_comparative, has_conditional, number_count)
        This acts as the 'Type' of the causal hypothesis.
        """
        has_neg = self._has_token(text, self.negations)
        has_comp = self._has_token(text, self.comparatives)
        has_cond = self._has_token(text, self.conditionals)
        nums = self._extract_numbers(text)
        return (has_neg, has_comp, has_cond, len(nums))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Verifies causal numeric consistency.
        If prompt implies an order (e.g., "9.11 < 9.9"), checks if candidate aligns.
        Returns 1.0 for consistent, 0.0 for inconsistent, 0.5 for neutral.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # If no numbers, neutral
        if not p_nums or not c_nums:
            return 0.5
        
        # Simple heuristic: If prompt has two numbers and candidate has one,
        # check if the candidate picks the 'correct' one based on comparatives.
        if len(p_nums) >= 2 and len(c_nums) == 1:
            has_less = self._has_token(prompt, ['less', 'smaller', 'lower', '<'])
            has_more = self._has_token(prompt, ['more', 'greater', 'larger', 'higher', '>'])
            
            target = min(p_nums[:2]) if has_less else (max(p_nums[:2]) if has_more else None)
            
            if target is not None:
                # Allow small float tolerance
                if abs(c_nums[0] - target) < 1e-6:
                    return 1.0
                else:
                    # If it picked the other number explicitly present in prompt, likely wrong
                    if any(abs(c_nums[0] - x) < 1e-6 for x in p_nums):
                        return 0.0
        
        return 0.5

    def _evaluate_load_and_type(self, prompt: str, candidate: str) -> float:
        """
        Core engine: Computes a score based on Type Matching and Cognitive Load.
        """
        p_sig = self._structural_signature(prompt)
        c_sig = self._structural_signature(candidate)
        
        score = 0.0
        
        # 1. Type Checking (Logical Consistency)
        # If prompt has negation, valid answers often need to handle negation logic
        # (This is a heuristic proxy for do-calculus verification)
        if p_sig[0]: # Prompt has negation
            if c_sig[0]: # Candidate acknowledges negation
                score += 0.4
            else:
                # Potential trap: Prompt says "X is not Y", candidate says "Y" -> Wrong
                # We penalize if candidate ignores the negation context entirely
                score -= 0.2
        
        # 2. Numeric Causal Consistency
        num_score = self._check_numeric_consistency(prompt, candidate)
        score += num_score * 0.5
        
        # 3. Cognitive Load Optimization (Germane vs Extraneous)
        # Reward 'chunking': reusing specific prompt tokens (excluding common stopwords)
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        common = p_words.intersection(c_words)
        # Remove stopwords from common count to avoid noise
        stopwords = {'the', 'is', 'are', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        meaningful_common = common - stopwords
        
        # Germane load reward: Reusing meaningful concepts
        if len(meaningful_common) > 0:
            score += 0.3 * min(1.0, len(meaningful_common) / 3.0)
            
        # Extraneous load penalty: Candidate much longer than necessary without adding info
        if len(candidate) > len(prompt) * 1.5:
            score -= 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_sig = self._structural_signature(prompt)
        
        for cand in candidates:
            # Primary Score: Structural and Logical consistency
            base_score = self._evaluate_load_and_type(prompt, cand)
            
            # Secondary Score (Tiebreaker): NCD
            # We invert NCD because lower distance = higher similarity = better tiebreaker
            ncd_val = self._compute_ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "ncd": ncd_val,
                "reasoning": f"Type match: {base_score:.2f}, NCD tiebreaker: {ncd_val:.2f}"
            })
        
        # Sort: Primary by score (desc), Secondary by NCD (asc, so lower distance is better)
        # Since we want higher score first, and for ties, lower NCD first.
        results.sort(key=lambda x: (-x['score'], x['ncd']))
        
        # Clean up output to match interface
        return [
            {"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]}
            for r in results
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate against a dummy list to reuse logic, then extract specific score
        # Or directly compute metrics
        base = self._evaluate_load_and_type(prompt, answer)
        num_cons = self._check_numeric_consistency(prompt, answer)
        
        # Combine heuristics
        # Base score can be negative, so we need to normalize roughly
        # Range is approx -0.3 to 1.3 based on weights above
        raw_conf = base + (num_cons * 0.2)
        
        # Clamp and normalize roughly to 0-1
        conf = max(0.0, min(1.0, (raw_conf + 0.5) / 1.5))
        return conf
```

</details>
