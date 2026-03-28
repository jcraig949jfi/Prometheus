# Cognitive Load Theory + Pragmatics + Hoare Logic

**Fields**: Cognitive Science, Linguistics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T03:34:54.750884
**Report Generated**: 2026-03-27T16:08:15.717682

---

## Nous Analysis

The algorithm treats a prompt as a Hoare‑style specification and scores each candidate answer by how well it satisfies the specification while respecting pragmatic enrichment and cognitive‑load limits.

**Data structures**  
- `Clause`: a tuple `(pred, args, polarity)` where `pred` is a predicate name (e.g., `greater`, `cause`), `args` are constants or variables, and `polarity` ∈ {+1,‑1} for affirmation/negation.  
- `VarEnv`: dict mapping variables to grounded values (numbers, strings, or `None` if ungrounded).  
- `WorkStack`: list representing the current working‑memory chunk limit (default 4). Each push adds a clause; popping removes the oldest when the limit is exceeded.  
- `Score`: float initialized to 0.

**Operations**  
1. **Structural parsing** – regex extracts clauses for: negations (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`, `equal`), conditionals (`if … then …`, `unless`), causal markers (`because`, `leads to`, `results in`), temporal ordering (`before`, `after`, `while`), numeric literals with units, and quantifiers (`all`, `some`, `none`). Each clause is stored with its polarity.  
2. **Pragmatic enrichment** – apply Grice maxims:  
   - *Quantity*: if a conditional’s antecedent is missing but the consequent is present, generate a plausible antecedent clause (e.g., from domain knowledge).  
   - *Relation*: add implicature clauses that link cause/effect or temporal order when a causal marker appears.  
   - *Quality*: discard clauses contradicting known facts (e.g., `greater(5,3)` is true).  
   Enriched clauses are pushed onto `WorkStack`.  
3. **Hoare‑style verification** – treat the set of clauses on `WorkStack` as the precondition `P`. For each imperative‑like statement in the candidate answer (extracted similarly), form a tentative postcondition `Q`. Using forward chaining (modus ponens) on the clause set, derive all logical consequences. If `Q` is entailed, add `+2` to `Score`; if `¬Q` is entailed, add `‑3` (contradiction).  
4. **Cognitive‑load scoring** –  
   - *Intrinsic load*: if the number of distinct variables in `WorkStack` exceeds the chunk limit, subtract `1` per excess variable.  
   - *Extraneous load*: for each clause in the answer that is not derivable from `P` (i.e., no proof path), subtract `1`.  
   - *Germane load*: for each derived clause that connects a premise to an answer clause (i.e., a useful inference), add `1`.  

The final `Score` is normalized to `[0,1]` for comparison across candidates.

**Structural features parsed**  
Negations, comparatives, conditionals, causal markers, temporal ordering, numeric values/units, quantifiers, and speech‑act indicators (e.g., “I claim that…”).

**Novelty**  
Pure Hoare‑logic verifiers exist in program analysis, and pragmatics‑based enrichment appears in some QA systems, but coupling both with an explicit working‑memory chunk constraint from Cognitive Load Theory is not found in current open‑source evaluation tools. The combination yields a load‑aware logical scorer that goes beyond simple bag‑of‑words or similarity metrics.

**Rating**  
Reasoning: 8/10 — captures logical entailment and contradiction via Hoare triples and forward chaining.  
Metacognition: 7/10 — models load limits and distinguishes intrinsic/extraneous/germane load, offering self‑regulation insight.  
Hypothesis generation: 6/10 — generates plausible antecedents and implicatures, but relies on hand‑crafted heuristics rather than learned hypothesis space.  
Implementability: 9/10 — uses only regex, basic data structures, and numpy for numeric checks; no external APIs or neural components required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Hoare Logic**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Cognitive Load Theory + Pragmatics: strong positive synergy (+0.267). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Hoare Logic + Pragmatics: strong positive synergy (+0.619). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Network Science + Pragmatics + Hoare Logic (accuracy: 0%, calibration: 0%)
- Pragmatics + Hoare Logic + Satisfiability (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=19% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T08:04:42.920364

---

## Code

**Source**: scrap

[View code](./Cognitive_Load_Theory---Pragmatics---Hoare_Logic/tool.py)

<details>
<summary>Show code</summary>

```python
import re
from typing import List, Dict, Any, Optional, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining Hoare Logic verification, Pragmatic enrichment,
    and Cognitive Load constraints.
    
    Mechanism:
    1. Parses prompts into logical clauses (pred, args, polarity) using regex.
    2. Enriches clauses via pragmatic heuristics (Gricean maxims).
    3. Verifies candidate answers against prompt constraints (Hoare-style P -> Q).
    4. Scores based on logical entailment, contradiction penalties, and cognitive load limits.
    5. Uses NCD (zlib) only as a tiebreaker for structurally identical scores.
    """

    def __init__(self):
        self.chunk_limit = 4  # Working memory limit
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|equal to|greater than|less than)\s*(\w+|\d+\.?\d*)', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|when)\b.*?\b(then|,|\.)', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'\b(\d+\.?\d*)\b'),
            'quantifier': re.compile(r'\b(all|some|every|none)\b', re.IGNORECASE)
        }

    def _parse_clauses(self, text: str) -> List[Tuple[str, tuple, int]]:
        """Extract logical clauses (pred, args, polarity) from text."""
        clauses = []
        text_lower = text.lower()
        
        # Negations
        if self.patterns['negation'].search(text_lower):
            clauses.append(('negated_context', (), -1))
            
        # Comparatives (simplified extraction)
        for match in re.finditer(r'(\w+)\s*(is\s+)?(greater|less|equal|bigger|smaller)\s+(than)?\s*(\w+|\d+\.?\d*)', text_lower):
            pred = match.group(3)
            arg2 = match.group(5)
            polarity = 1 if 'greater' in pred or 'bigger' in pred else -1 if 'less' in pred or 'smaller' in pred else 0
            if 'equal' in pred: polarity = 0
            clauses.append((f'{pred}_comp', (arg2,), polarity))

        # Numeric extraction for direct comparison
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        if len(nums) >= 2:
            if nums[0] > nums[1]:
                clauses.append(('numeric_greater', (nums[0], nums[1]), 1))
            elif nums[0] < nums[1]:
                clauses.append(('numeric_less', (nums[0], nums[1]), 1))
                
        return clauses

    def _pragmatic_enrichment(self, clauses: List[Tuple]) -> List[Tuple]:
        """Apply Gricean maxims to enrich clauses (Quantity, Relation)."""
        enriched = list(clauses)
        # Quantity: If conditional logic detected but antecedent missing, assume standard causality
        has_causal = any('causal' in str(c) or 'lead' in str(c) for c in clauses)
        if has_causal:
            enriched.append(('implicature_cause_effect', (), 1))
        
        # Relation: Link temp/causal if present
        if any('numeric' in str(c) for c in clauses):
            enriched.append(('implicature_numeric_relevance', (), 1))
            
        return enriched

    def _verify_hoare(self, prompt_clauses: List[Tuple], answer_clauses: List[Tuple]) -> Tuple[float, str]:
        """Verify if answer clauses (Q) are entailed by prompt clauses (P)."""
        score = 0.0
        reasoning = []
        
        # Simple forward chaining simulation
        # If prompt establishes X > Y, and answer claims X > Y, +2
        # If prompt establishes X > Y, and answer claims Y > X, -3
        
        p_preds = {c[0]: c for c in prompt_clauses}
        
        for ans_pred, ans_args, ans_pol in answer_clauses:
            found_match = False
            for p_pred, p_data in p_preds.items():
                if p_pred == ans_pred or (ans_pred in p_pred and p_pred in ans_pred): # Fuzzy match
                    # Check polarity consistency
                    if ans_pol == p_data[2]:
                        score += 2.0
                        reasoning.append(f"Entailed: {ans_pred}")
                        found_match = True
                        break
                    elif ans_pol != p_data[2] and ans_pol != 0: # Contradiction
                        score -= 3.0
                        reasoning.append(f"Contradiction: {ans_pred}")
                        found_match = True
                        break
            
            if not found_match:
                # Extraneous load penalty
                score -= 1.0
                reasoning.append(f"Unsubstantiated: {ans_pred}")

        return score, "; ".join(reasoning) if reasoning else "No logical link found"

    def _cognitive_load_score(self, clauses: List[Tuple]) -> float:
        """Calculate load based on variable count vs chunk limit."""
        variables = set()
        for _, args, _ in clauses:
            for arg in args:
                if isinstance(arg, str) and arg.replace('.','').isdigit() == False:
                    variables.add(arg)
        
        intrinsic_load = 0
        if len(variables) > self.chunk_limit:
            intrinsic_load = -1.0 * (len(variables) - self.chunk_limit)
            
        # Germane load bonus for connectedness (simplified)
        germane_bonus = 0.5 if len(clauses) > 0 else 0
        return intrinsic_load + germane_bonus

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_bytes = s1.encode()
        s2_bytes = s2.encode()
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_clauses = self._parse_clauses(prompt)
        enriched_prompt = self._pragmatic_enrichment(prompt_clauses)
        base_load_score = self._cognitive_load_score(enriched_prompt)
        
        results = []
        for cand in candidates:
            cand_clauses = self._parse_clauses(cand)
            # Hoare Verification
            logic_score, logic_reason = self._verify_hoare(enriched_prompt, cand_clauses)
            
            # Total Score = Logic + Load Adjustment
            # Normalize roughly to 0-1 range assuming max logic score ~10
            raw_score = logic_score + base_load_score
            normalized_score = max(0.0, min(1.0, (raw_score + 5.0) / 10.0))
            
            results.append({
                "candidate": cand,
                "score": normalized_score,
                "reasoning": logic_reason,
                "_logic_raw": logic_score # For tie-breaking
            })
        
        # Sort by score desc, then by NCD similarity to prompt (lower NCD = better tiebreaker)
        results.sort(key=lambda x: (x['score'], -self._calculate_ncd(prompt, x['candidate'])), reverse=True)
        
        # Clean up internal keys
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": round(r["score"], 4),
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        return res[0]["score"] if res else 0.0
```

</details>
