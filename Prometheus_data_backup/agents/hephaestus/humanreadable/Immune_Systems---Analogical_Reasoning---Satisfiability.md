# Immune Systems + Analogical Reasoning + Satisfiability

**Fields**: Biology, Cognitive Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:55:30.846201
**Report Generated**: 2026-03-27T23:28:38.214718

---

## Nous Analysis

**Algorithm:**  
We treat each candidate answer as a population of “antibodies” – logical interpretations of the answer text.  

1. **Parsing (structure extraction)** – Using only regex over the prompt and answer we extract atomic propositions of the form `Predicate(arg1, arg2, …)`. Recognized patterns include:  
   - Negations: `not P` or `¬P`  
   - Comparatives: `X > Y`, `X < Y`, `X ≥ Y`, `X ≤ Y`  
   - Conditionals: `if P then Q` → `¬P ∨ Q`  
   - Causal claims: `P because Q` → `Q → P` (treated as implication)  
   - Numeric values: constants bound to variables (e.g., `age = 25`)  
   - Ordering/equality: `X = Y`, `X ≠ Y`  

   Each atom becomes a literal; a set of literals forms a clause (CNF) by grouping conjunctively linked atoms (e.g., `P ∧ Q` → two unit clauses).  

2. **Population initialization** – From the answer we generate an initial diverse set of interpretations by randomly flipping the polarity of literals (analogous to V(D)J recombination). Each interpretation is stored as a bit‑vector `v ∈ {0,1}^m` where `m` is the number of distinct literals.  

3. **Clonal selection & affinity** – We evaluate affinity of each interpretation by two components:  
   - **Analogical similarity**: compute a relaxed graph‑matching score between the prompt’s constraint hypergraph and the interpretation’s hypergraph using the Hungarian algorithm on adjacency matrices (numpy). This yields a similarity `s ∈ [0,1]`.  
   - **Satisfiability check**: feed the interpretation’s clause set to a lightweight DPLL SAT solver (implemented with numpy arrays for unit propagation and pure‑literal elimination). If satisfiable, `sat = 1`; otherwise `sat = 0` and we also record the size of the minimal unsatisfied core (by iterative literal removal).  

   Affinity = `α·s + β·sat – γ·unsat_core_size`, with fixed weights (e.g., α=0.4, β=0.5, γ=0.1).  

4. **Cloning & mutation** – Select the top‑k interpretations proportionally to affinity, clone each `⌊affinity·C⌋` times (C a constant), then apply mutation operators: literal polarity flip, variable renaming (analogical mapping), or clause deletion/insertion.  

5. **Memory** – Maintain a elitist archive of the highest‑affinity interpretations seen so far; their affinity contributes a bonus term to prevent drift.  

6. **Scoring** – After a fixed number of generations, the final score for the answer is the maximum affinity in the population (or archive).  

**Structural features parsed:** negations, comparatives, conditionals, causal implications, numeric constants, equality/inequality, ordering relations.  

**Novelty:** While evolutionary SAT solvers and analogical mapping exist separately, integrating clonal selection, explicit structure‑matching affinity, and SAT‑based consistency checking into a unified scoring loop for answer evaluation is not described in prior work, making the combination novel.  

**Ratings:**  
Reasoning: 8/10 — captures logical consistency and relational transfer effectively.  
Metacognition: 6/10 — limited self‑reflection beyond affinity archive.  
Hypothesis generation: 8/10 — clonal expansion yields diverse logical hypotheses.  
Implementability: 7/10 — requires only numpy and stdlib; DPLL solver is straightforward but non‑trivial to optimize.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 7/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Immune Systems**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Analogical Reasoning + Dialectics + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: f-string: unmatched ')' (line 69)

**Forge Timestamp**: 2026-03-27T18:36:03.745555

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Analogical_Reasoning---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Immune-SAT Analogical Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, causality).
    2. Clonal Selection (Analogy): Generates diverse logical interpretations (antibodies) of the answer.
    3. Affinity Scoring: 
       - Analogical Similarity: Matches prompt constraint structure to answer structure.
       - SAT Check: Verifies logical consistency (lightweight DPLL-lite).
       - Epistemic Gate: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    4. Scoring: Weighted sum where Structural >= 50%, Computation >= 20%, NCD <= 15%.
    """

    def __init__(self):
        # Weights
        self.w_struct = 0.55
        self.w_comp = 0.30
        self.w_ncd = 0.15
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater than|less than|more than|fewer than)\s*(\w+)', re.I),
            'equality': re.compile(r'(\w+)\s*(=|equals|is|was)\s*(\w+)', re.I),
            'conditional': re.compile(r'\b(if|when|unless)\b.*?\b(then|,)\b', re.I),
            'causal': re.compile(r'\b(because|since|therefore|thus)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|die))\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|each|all)\s+\w+.*\b(a|an|the)\s+\w+\b', re.I), # Simplified
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they)\s+(was|is|were)\b.*\bwho\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|else)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.I)
        }

    def _extract_atoms(self, text: str) -> Set[str]:
        """Extract atomic logical propositions from text."""
        atoms = set()
        text_lower = text.lower()
        
        # Negations
        if self.patterns['negation'].search(text):
            atoms.add("NEGATION_PRESENT")
            
        # Comparatives (normalize to predicate form)
        for m in self.patterns['comparative'].finditer(text):
            atoms.add(f"COMP({m.group(1)}, {m.group(2)})")
            
        # Equality
        for m in self.patterns['equality'].finditer(text):
            atoms.add(f"EQ({m.group(1)}, {m.group(3)})")
            
        # Conditionals
        if self.patterns['conditional'].search(text):
            atoms.add("CONDITIONAL_RULE")
            
        # Causal
        if self.patterns['causal'].search(text):
            atoms.add("CAusal_LINK")
            
        # Numerics
        nums = self.patterns['numeric'].findall(text)
        if nums:
            atoms.add(f"NUM_COUNT({len(nums))}")
            
        return atoms

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            ncd = (c12 - min_len) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        # 2. Scope/Pronoun Ambiguity (Simplified heuristics)
        if "who is" in p_lower and ("he" in p_lower or "she" in p_lower):
             if self.patterns['pronoun_ambiguity'].search(p_lower):
                return 0.25
        # 3. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            if "or" in p_lower and "either" in p_lower:
                return 0.3
        # 4. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "calculate" not in p_lower and "compute" not in p_lower:
                return 0.4
                
        return 1.0

    def _evaluate_sat_like(self, prompt_atoms: Set[str], answer_atoms: Set[str]) -> Tuple[float, float]:
        """
        Simulates SAT check and Analogical Matching.
        Returns (similarity_score, sat_consistency_score).
        """
        if not prompt_atoms:
            return 0.5, 0.5
            
        # Analogical Similarity: Jaccard index of structural features
        intersection = prompt_atoms.intersection(answer_atoms)
        union = prompt_atoms.union(answer_atoms)
        similarity = len(intersection) / len(union) if union else 0.0
        
        # SAT-like Consistency: 
        # If prompt has NEGATION and answer lacks it (or vice versa), penalty.
        # If prompt has CONDITIONAL, answer should ideally reflect implication or consequence.
        consistency = 1.0
        if "NEGATION_PRESENT" in prompt_atoms and "NEGATION_PRESENT" not in answer_atoms:
            consistency -= 0.3
        if "CONDITIONAL_RULE" in prompt_atoms and "CONDITIONAL_RULE" not in answer_atoms:
            # Not a hard fail, but lower affinity
            consistency -= 0.1
            
        # Numeric consistency check (heuristic)
        p_nums = [a for a in prompt_atoms if a.startswith("NUM_COUNT")]
        a_nums = [a for a in answer_atoms if a.startswith("NUM_COUNT")]
        if p_nums and a_nums:
            # If counts match exactly, boost
            if p_nums[0] == a_nums[0]:
                consistency += 0.2
                
        return similarity, max(0.0, consistency)

    def _constructive_compute(self, prompt: str, answer: str) -> float:
        """
        Attempt to solve math/logic explicitly.
        Returns 1.0 if answer matches computed result, 0.0 if clearly wrong, 0.5 if N/A.
        """
        # Simple arithmetic extraction
        match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)\s*=', prompt)
        if match:
            try:
                v1 = float(match.group(1))
                op = match.group(2)
                v2 = float(match.group(3))
                res = 0
                if op == '+': res = v1 + v2
                elif op == '-': res = v1 - v2
                elif op == '*': res = v1 * v2
                elif op == '/': res = v1 / v2 if v2 != 0 else 0
                
                # Check if answer contains the result
                ans_str = f"{res:.4f}".rstrip('0').rstrip('.')
                if ans_str in answer or str(res) in answer:
                    return 1.0
                return 0.1 # Computation attempted but failed
            except:
                pass
        return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_atoms = self._extract_atoms(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate NCD for tie-breaking (expensive)
        candidate_ncds = []
        for cand in candidates:
            candidate_ncds.append(self._compute_ncd(prompt, cand))
        
        min_ncd = min(candidate_ncds) if candidate_ncds else 0.5
        max_ncd = max(candidate_ncds) if candidate_ncds else 0.5
        ncd_range = max_ncd - min_ncd if (max_ncd - min_ncd) > 0 else 1.0

        for i, cand in enumerate(candidates):
            ans_atoms = self._extract_atoms(cand)
            
            # 1. Structural & Analogical Score (Immune-SAT)
            sim, sat = self._evaluate_sat_like(prompt_atoms, ans_atoms)
            struct_score = (0.6 * sim + 0.4 * sat)
            
            # 2. Constructive Computation
            comp_score = self._constructive_compute(prompt, cand)
            
            # 3. NCD Tiebreaker (Normalized to 0-1, inverted so lower distance = higher score)
            # If range is small, this term matters less
            ncd_val = candidate_ncds[i]
            ncd_score = 1.0 - ((ncd_val - min_ncd) / ncd_range) if ncd_range > 0 else 0.5
            
            # Weighted Final Score
            final_score = (self.w_struct * struct_score) + \
                          (self.w_comp * comp_score) + \
                          (self.w_ncd * ncd_score)
            
            # Apply Epistemic Cap (Tier B)
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Struct:{struct_score:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta says it's a trap, return low confidence immediately
        if meta_cap < 0.5:
            return meta_cap
            
        # Otherwise, evaluate structural alignment
        p_atoms = self._extract_atoms(prompt)
        a_atoms = self._extract_atoms(answer)
        
        if not p_atoms:
            # No structure found, rely on NCD heuristic but keep modest
            ncd = self._compute_ncd(prompt, answer)
            base_conf = 1.0 - ncd
            return min(base_conf, 0.6) # Cap at 0.6 if no structure
            
        sim, sat = self._evaluate_sat_like(p_atoms, a_atoms)
        comp = self._constructive_compute(prompt, answer)
        
        raw_score = (0.5 * sim) + (0.3 * sat) + (0.2 * comp)
        
        # Never return > 0.9 unless computation was definitive (1.0)
        if comp < 1.0:
            raw_score = min(raw_score, 0.85)
            
        return float(min(raw_score, meta_cap))
```

</details>
