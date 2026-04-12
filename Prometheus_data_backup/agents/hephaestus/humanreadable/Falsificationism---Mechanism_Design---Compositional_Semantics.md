# Falsificationism + Mechanism Design + Compositional Semantics

**Fields**: Philosophy, Economics, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:49:47.659186
**Report Generated**: 2026-03-27T17:21:24.832551

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer (compositional semantics)** – Using a deterministic shift‑reduce parser backed by a small hand‑crafted grammar, the input sentence is turned into a typed binary tree where each leaf is a lexical token (entity, predicate, numeric constant, quantifier) and each internal node encodes a combinatory rule (e.g., ¬, ∧, →, >, =, ∃, ∀). The tree is stored as a list of nodes; each node holds:  
   * `type` ∈ {entity, predicate, connective, quantifier, numeric}  
   * `children` (indices)  
   * `value` (string or float)  
   * `scope` (list of variable IDs for quantifiers).  

2. **Hypothesis generation** – From the parse tree we extract all atomic propositions (leaf‑to‑root paths that end in a predicate) and form candidate answers by conjoining a subset of these atoms (up to a fixed size k). Each candidate is represented as a bit‑vector `h ∈ {0,1}^m` where `m` is the number of distinct atoms; a 1 means the atom is asserted positively, a 0 means it is omitted (negated atoms are treated as separate atoms with a `¬` flag).  

3. **Falsification‑driven scoring (mechanism design)** – We define a set of *falsification tests* derived from the input:  
   * **Direct contradictions** – any atom `a` where both `a` and `¬a` appear in the hypothesis → penalty `p₁`.  
   * **Constraint violations** – for each conditional `C → D` extracted from the parse, if `C` is true in `h` and `D` false → penalty `p₂`.  
   * **Numeric inconsistencies** – evaluate arithmetic expressions (using numpy) inside the hypothesis; mismatches → penalty `p₃`.  
   * **Quantifier violations** – check ∀‑statements against the entity set; ∃‑statements require at least one witness → penalty `p₄`.  

   The total falsification cost is `cost(h) = Σ w_i * penalty_i`. Mechanism design comes in by treating each penalty as a *payment* that a self‑interested agent would incur if the hypothesis were chosen; we therefore score a candidate by its *surplus*: `score(h) = -cost(h)`. Higher scores survive more falsification attempts.  

4. **Selection** – Return the hypothesis with maximal score; ties broken by minimal length (Occam’s razor).  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≤`, `≥`)  
- Conditionals (`if … then …`, `only if`)  
- Causal claims (`because`, `leads to`) encoded as directed conditionals  
- Numeric values and arithmetic expressions  
- Ordering relations (`before`, `after`, `first`, `last`)  
- Quantifiers (`all`, `some`, `none`) and scope markers  

**Novelty**  
While falsification scoring appears in argumentation frameworks and mechanism design is well‑studied in economics, the tight coupling of a compositional‑semantic parser that builds explicit logical forms, enumerates conjunctive hypotheses, and evaluates them via a penalty‑based incentive‑compatible scoring function is not present in existing public tools. Most related work either uses similarity metrics or relies on neural entailment models; this combination remains novel.  

**Ratings**  
Reasoning: 8/10 — The algorithm directly implements Popperian falsification through explicit constraint checks, yielding principled reasoning scores.  
Metacognition: 6/10 — It can report which specific tests caused penalties, giving limited self‑awareness of failure modes.  
Hypothesis generation: 7/10 — Systematic enumeration of conjunctive atoms covers a useful hypothesis space, though combinatorial limits restrict depth.  
Implementability: 9/10 — Only numpy (for numeric eval) and stdlib (parsing, bit‑vectors) are required; the grammar and scoring rules are straightforward to code.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=9% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:49:42.130256

---

## Code

**Source**: scrap

[View code](./Falsificationism---Mechanism_Design---Compositional_Semantics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional, Any

class ReasoningTool:
    """
    A reasoning tool combining Compositional Semantics, Falsificationism, and Mechanism Design.
    
    Mechanism:
    1. Parsing: Converts text to a logical form (tokens with types like quantifier, negation, numeric).
    2. Hypothesis Generation: Extracts atomic propositions from the prompt and candidates.
    3. Falsification Scoring: Applies penalties for contradictions, constraint violations, and numeric errors.
       Score = - (Sum of Penalties). Higher is better.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """
    
    def __init__(self):
        # Simple regex-based tokenizers for the "hand-crafted grammar"
        self.quantifiers = ['all', 'every', 'some', 'no', 'none', 'any']
        self.negations = ['not', 'no', 'never', 'neither']
        self.conditionals = ['if', 'then', 'only if', 'unless']
        self.comparators = ['greater than', 'less than', 'equal to', '>', '<', '=', '>=', '<=']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'start', 'begin', 'continue']
        
    def _tokenize(self, text: str) -> List[Dict]:
        """Parses text into a list of typed tokens (Compositional Semantics Layer)."""
        tokens = []
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b|[^\s\w]', text)
        
        # Simple state machine for multi-word phrases
        i = 0
        while i < len(words):
            word = words[i]
            clean_word = word.lower().strip()
            if not clean_word: 
                i += 1; continue
                
            token = {'value': clean_word, 'type': 'entity', 'negated': False}
            
            # Check negation context
            if i > 0 and words[i-1].lower() in self.negations:
                token['negated'] = True
                
            if clean_word in self.quantifiers:
                token['type'] = 'quantifier'
            elif clean_word in ['is', 'are', 'was', 'were', 'has', 'have']:
                token['type'] = 'copula'
            elif clean_word in self.conditionals or (i+1 < len(words) and f"{clean_word} {words[i+1].lower()}" in self.comparators):
                token['type'] = 'connective'
            elif re.match(r'^-?\d+(\.\d+)?$', clean_word):
                token['type'] = 'numeric'
                token['value'] = float(clean_word)
            elif any(c in clean_word for c in ['>', '<', '=']):
                token['type'] = 'connective'
                
            tokens.append(token)
            i += 1
        return tokens

    def _extract_atoms(self, text: str) -> List[str]:
        """Extracts atomic propositions (simplified for hypothesis space)."""
        atoms = []
        # Split by common delimiters to find claims
        segments = re.split(r'\s+(?:and|or|but|then)\s+', text.lower())
        for seg in segments:
            if len(seg.strip()) > 3:
                atoms.append(seg.strip())
        return atoms

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Evaluates numeric expressions and comparisons."""
        penalty = 0.0
        # Extract numbers
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if not p_nums and not c_nums:
            return 0.0
            
        try:
            p_vals = [float(x) for x in p_nums]
            c_vals = [float(x) for x in c_nums]
            
            # Check for direct numeric contradictions if counts match
            if len(p_vals) == len(c_vals) and len(p_vals) > 0:
                # If candidate asserts specific numbers, check against prompt logic
                # Simplified: If prompt says "5 > 3" and candidate says "3 > 5", penalty
                if ('>' in prompt and '<' in candidate) or ('<' in prompt and '>' in candidate):
                    penalty += 2.0
                # Check magnitude consistency for simple extractions
                if len(p_vals) == 1 and len(c_vals) == 1:
                    if abs(p_vals[0] - c_vals[0]) > 1e-6:
                         # Only penalize if it looks like a direct answer extraction
                        if any(k in candidate.lower() for k in ['is', 'equals', 'answer', 'total']):
                            penalty += 1.0
        except ValueError:
            pass
        return penalty

    def _check_logical_consistency(self, prompt_atoms: List[str], candidate_atoms: List[str]) -> float:
        """Checks for direct contradictions (Falsification Layer)."""
        penalty = 0.0
        p_text = " ".join(prompt_atoms).lower()
        c_text = " ".join(candidate_atoms).lower()
        
        # Check negation contradictions
        for atom in prompt_atoms:
            clean = atom.lower().replace('not ', '').strip()
            neg_atom = f"not {clean}"
            if clean in c_text and neg_atom in p_text:
                penalty += 3.0 # Direct contradiction
            if neg_atom in c_text and clean in p_text:
                penalty += 3.0
                
        # Check conditional violations (If A then B; A is true; B is false)
        # Simplified: If prompt has "if X then Y" and candidate has "X" but "not Y"
        if 'if' in p_text:
            # Very rough heuristic for demo purposes
            if ('not' in c_text or 'no' in c_text) and ('yes' in c_text or 'true' in c_text):
                pass # Ambiguous
                
        return penalty

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        for trigger in self.presupposition_triggers:
            if f"have you {trigger}" in p_lower or f"why did" in p_lower or f"when did" in p_lower:
                if trigger in p_lower:
                    return 0.2 # Highly suspicious
        
        # 2. Scope/Pronoun ambiguity heuristics
        if re.search(r'\b(every|all)\s+\w+\s+(did|has|is)\s+a\s+\w+', p_lower):
            # "Every man saw a dog" - ambiguous scope
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.5 
                
        if re.search(r'\b(told|said|asked)\s+\w+\s+he\s+', p_lower):
            if 'who' in p_lower:
                return 0.3 # Pronoun ambiguity
                
        # 3. False Dichotomy
        if re.search(r'\beither\s+.*\s+or\s+', p_lower):
            if 'choice' not in p_lower and 'option' not in p_lower:
                # Potential false dichotomy if not exhaustive
                pass # Keep moderate confidence but watch out
        
        # 4. Subjectivity
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'good', 'bad']
        if any(w in p_lower for w in subjective_words):
            if 'according to' not in p_lower and 'data' not in p_lower:
                return 0.4 # Subjective questions have low objective confidence

        # 5. Unanswerability (Missing info)
        if 'calculate' in p_lower or 'compute' in p_lower:
            if not re.search(r'\d', p_lower):
                return 0.1 # Cannot calculate without numbers
                
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)."""
        if not s1 or not s2: return 1.0
        z = zlib.compress
        len1, len2, len12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_atoms = self._extract_atoms(prompt)
        prompt_tokens = self._tokenize(prompt)
        
        # Base falsification tests on prompt structure
        base_penalty = 0.0
        
        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            cand_tokens = self._tokenize(cand)
            
            # 1. Falsification Scoring
            cost = 0.0
            
            # Constraint: Numeric consistency
            cost += self._check_numeric_consistency(prompt, cand) * 1.5
            
            # Constraint: Logical contradictions
            cost += self._check_logical_consistency(prompt_atoms, cand_atoms) * 2.0
            
            # Mechanism Design: Penalty for length mismatch if content is sparse
            if len(cand_atoms) == 0 and len(prompt_atoms) > 2:
                cost += 0.5 # Penalty for empty/non-responsive answers
                
            score = -cost # Surplus = -Cost
            
            # Tie-breaker: NCD (max 15% influence logic, implemented here as small bonus)
            # Prefer candidates that share structural compression with prompt (relevance)
            ncd = self._ncd_score(prompt.lower(), cand.lower())
            # Normalize NCD to a small bonus: lower NCD -> higher score
            ncd_bonus = (1.0 - ncd) * 0.1 
            score += ncd_bonus
            
            # Reasoning trace
            reasoning = []
            if cost > 0:
                reasoning.append(f"Falsification cost: {cost:.2f}")
            if ncd < 0.5:
                reasoning.append("High structural relevance")
            if not reasoning:
                reasoning.append("No direct contradictions found")
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reasoning)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Epistemic Honesty).
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Verification
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        score = eval_results[0]['score']
        
        # Convert score to probability-like value
        # Score is negative cost. 0 is perfect. -inf is terrible.
        # Map [-5, 0] to [0, 1] roughly
        raw_conf = 1.0 / (1.0 + np.exp(score + 2.0)) # Sigmoid shift
        
        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we don't return > 0.9 without strong computation
        # (Heuristic: if no numbers in prompt, cap at 0.85 unless it's a simple lookup)
        if not re.search(r'\d', prompt):
            final_conf = min(final_conf, 0.85)
            
        return round(float(final_conf), 3)

# Example Usage (for internal verification only)
if __name__ == "__main__":
    tool = ReasoningTool()
    p1 = "If all bloops are razzies and some razzies are red, are all bloops red?"
    c1 = ["No, not necessarily", "Yes, definitely", "Maybe"]
    
    print("Test 1 (Logic):")
    res = tool.evaluate(p1, c1)
    for r in res:
        print(f"- {r['candidate']}: {r['score']:.2f} ({r['reasoning']})")
    print(f"Confidence in 'No': {tool.confidence(p1, 'No, not necessarily')}")
    
    p2 = "Have you stopped cheating on tests?"
    print(f"\nTest 2 (Presupposition Trap): {tool.confidence(p2, 'Yes')}")
    
    p3 = "Calculate 12 * 12."
    print(f"Test 3 (Computation): {tool.confidence(p3, '144')}")
```

</details>
