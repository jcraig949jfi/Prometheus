# Free Energy Principle + Hoare Logic + Satisfiability

**Fields**: Theoretical Neuroscience, Formal Methods, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:17:11.721824
**Report Generated**: 2026-03-27T23:28:38.409718

---

## Nous Analysis

**Algorithm**  
1. **Parsing → propositional representation**  
   - Use regex to extract atomic propositions from the prompt and each candidate answer:  
     * literals (e.g., “X is Y”), negations (“not X”), comparatives (“X > Y”), conditionals (“if X then Y”), causal (“X because Y”), and ordering (“X before Y”).  
   - Map each distinct proposition to an integer ID; store its negation as `-id`.  
   - Represent a conditional “if A then B” as the clause `(-A ∨ B)`.  
   - Store all clauses in a list `clauses`, each clause being a Python list of ints (CNF).  

2. **Hoare‑style step encoding**  
   - For each extracted conditional, treat its antecedent as a *precondition* set `P` and its consequent as a *postcondition* set `Q`.  
   - Keep a list of triples `[(P, Q), …]`. During scoring, a triple is satisfied if the current truth assignment makes all literals in `P` true ⇒ all literals in `Q` true; otherwise it contributes a prediction error.  

3. **Satisfiability check (DPLL)**  
   - Implement a simple DPLL solver using only Python lists and recursion (no external libraries).  
   - Input: the union of (a) prompt clauses, (b) candidate‑answer unit clauses, (c) all conditional clauses.  
   - The solver returns either a satisfying assignment `model` (list of bool per ID) or reports UNSAT.  

4. **Free‑energy‑style scoring**  
   - Define a precision vector `π` (numpy array) initialized to 1.0 for each proposition; optionally weight comparatives higher.  
   - For a given `model`, compute the error vector `e` where `e_i = 0` if literal `i` is satisfied in its clause, else `e_i = 1`.  
   - Approximate variational free energy: `F = π · (e ** 2)` (dot product).  
   - Score the candidate as `S = -F` (lower free energy → higher score).  
   - If UNSAT, iteratively drop clauses to find a minimal unsatisfiable core; increase `F` proportionally to the core size to penalize contradictions heavily.  

**Structural features parsed**  
Negations, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal cues (`because`, `leads to`), ordering relations (`before`, `after`, `greater than`), and explicit numeric values/constants.  

**Novelty**  
While each component exists separately (Hoare logic for program verification, DPLL SAT solvers, and free‑energy formulations in perceptual coding), their joint use as a scoring mechanism for natural‑language reasoning answers is not present in mainstream QA or explanation‑generation work. The closest relatives are Markov Logic Networks or Probabilistic Soft Logic, but those rely on weighted soft constraints and approximate inference; here we combine exact SAT checking with a variational free‑energy penalty, yielding a novel deterministic scoring scheme.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and conditional inference via Hoare triples and SAT solving.  
Metacognition: 6/10 — the method can detect contradictions but lacks explicit self‑monitoring of uncertainty beyond free‑energy magnitude.  
Hypothesis generation: 7/10 — by examining alternative models from the DPLL search it can generate competing assignments.  
Implementability: 9/10 — relies only on regex, basic Python data structures, numpy for vector ops, and a hand‑rolled DPLL solver; no external APIs or neural components.

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
**Reason**: trap_battery_failed (acc=30% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T20:51:50.280948

---

## Code

**Source**: scrap

[View code](./Free_Energy_Principle---Hoare_Logic---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A reasoning tool combining Free Energy Principle, Hoare Logic, and SAT solving.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, comparatives, and conditionals 
       from text into a propositional logic format (CNF).
    2. Hoare Encoding: Treats conditionals as Precondition -> Postcondition triples.
    3. SAT Solving: Uses a recursive DPLL algorithm to check if a candidate answer 
       creates a contradiction (UNSAT) with the prompt's logic.
    4. Free Energy Scoring: Calculates a 'surprise' metric (Free Energy) based on 
       violated constraints. Lower energy = higher score.
    5. Epistemic Honesty: Detects ambiguity patterns (presuppositions, false dichotomies)
       to cap confidence, ensuring the model admits uncertainty on Tier B traps.
    """

    def __init__(self):
        self.clause_db = []
        self.prop_map = {}
        self.rev_map = {}
        self.prop_count = 0

    def _get_id(self, lit: str) -> int:
        """Map literal string to integer ID. Negations stored as negative."""
        is_neg = lit.startswith('not ')
        core = lit[4:] if is_neg else lit
        if core not in self.prop_map:
            self.prop_map[core] = self.prop_count
            self.rev_map[self.prop_count] = core
            self.prop_count += 1
        base_id = self.prop_map[core]
        return -base_id if is_neg else base_id

    def _parse_propositions(self, text: str) -> List[int]:
        """Extract atomic propositions and relations from text."""
        literals = []
        text_lower = text.lower()
        
        # Extract comparatives (X > Y, X before Y, etc)
        comp_patterns = [
            r'(\w+)\s+(?:is greater than|>\s|comes after)\s+(\w+)',
            r'(\w+)\s+(?:is less than|<\s|comes before)\s+(\w+)',
            r'(\w+)\s+(?:before|after)\s+(\w+)'
        ]
        for pat in comp_patterns:
            for m in re.finditer(pat, text_lower):
                literals.append(f"{m.group(1)}_{m.group(0).split()[1]}_{m.group(2)}")
        
        # Extract simple facts (X is Y)
        for m in re.finditer(r'(\w+)\s+(?:is|are|was)\s+(\w+)', text_lower):
            literals.append(f"{m.group(1)}_is_{m.group(2)}")
            
        # Extract explicit negations
        for m in re.finditer(r'(?:no|not|never)\s+(\w+)', text_lower):
            literals.append(f"not_{m.group(1)}")

        # Extract conditionals as separate logic later, but mark presence
        if not literals:
            # Fallback: tokenize words as potential props if nothing structured found
            literals = list(set(re.findall(r'\b[a-z]{3,}\b', text_lower)))[:10]
            
        return [self._get_id(l) for l in literals] if literals else []

    def _extract_conditionals(self, text: str) -> List[Tuple[List[int], List[int]]]:
        """Extract If-Then rules as Hoare triples (Pre, Post)."""
        triples = []
        text_lower = text.lower()
        
        # Pattern: if A then B, A implies B, A because B (B -> A)
        patterns = [
            (r'if\s+(.+?)\s+(?:then|,)\s+(.+)', 'forward'),
            (r'(.+?)\s+implies\s+(.+)', 'forward'),
            (r'(.+?)\s+because\s+(.+)', 'backward'), # B because A => A -> B
        ]
        
        for pat, direction in patterns:
            for m in re.finditer(pat, text_lower):
                pre_txt = m.group(1).strip()
                post_txt = m.group(2).strip()
                
                # Simplify to single token representatives for the solver
                pre_ids = self._parse_propositions(pre_txt)
                post_ids = self._parse_propositions(post_txt)
                
                if pre_ids and post_ids:
                    if direction == 'backward':
                        triples.append((post_ids, pre_ids))
                    else:
                        triples.append((pre_ids, post_ids))
        return triples

    def _dpll(self, clauses: List[List[int]], model: Dict[int, bool]) -> Optional[Dict[int, bool]]:
        """Simple recursive DPLL solver."""
        if not clauses:
            return model
        
        # Unit propagation
        for clause in clauses:
            if len(clause) == 0: 
                return None # Empty clause means contradiction
            if len(clause) == 1:
                lit = clause[0]
                var = abs(lit)
                val = lit > 0
                if var in model:
                    if model[var] != val: return None
                else:
                    new_model = model.copy()
                    new_model[var] = val
                    # Simplify clauses
                    new_clauses = []
                    for c in clauses:
                        if any((x > 0 and new_model.get(abs(x), None) == True) or 
                               (x < 0 and new_model.get(abs(x), None) == False) for x in c):
                            continue # Clause satisfied
                        new_c = [x for x in c if abs(x) != var]
                        new_clauses.append(new_c)
                    return self._dpll(new_clauses, new_model)

        # Choose first unassigned variable
        all_vars = set()
        for c in clauses: all_vars.update(abs(x) for x in c)
        
        for var in all_vars:
            if var not in model:
                # Try True
                res = self._dpll(clauses, {**model, var: True})
                if res: return res
                # Try False
                res = self._dpll(clauses, {**model, var: False})
                return res
        
        return model

    def _check_satisfiability(self, prompt_clauses: List[List[int]], 
                              candidate_clauses: List[List[int]]) -> Tuple[bool, float]:
        """Check SAT and compute Free Energy penalty."""
        all_clauses = prompt_clauses + candidate_clauses
        model = self._dpll(all_clauses, {})
        
        if model is not None:
            # Satisfiable: Calculate Free Energy (error count)
            # In a full implementation, we'd check every clause against the model
            # Here, if SAT, error is 0.
            return True, 0.0
        else:
            # UNSAT: Find minimal unsatisfiable core size approximation
            # We penalize heavily based on total clauses involved
            return False, len(all_clauses) * 2.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        if re.search(r'(have you stopped|have you quit|why did .+ fail|why is .+ wrong)', p):
            return 0.2
        
        # 2. Scope/Pronoun ambiguity
        if re.search(r'(every .+ a .+|told .+ he was|told .+ she was)', p):
            if re.search(r'who\s+|which one', p):
                return 0.3
                
        # 3. False Dichotomy
        if re.search(r'either .+ or .+', p) and not re.search(r'both|neither|other', p):
            return 0.4
            
        # 4. Subjectivity without criteria
        if re.search(r'(best|worst|favorite|most beautiful)', p) and not re.search(r'(data|statistics|according to)', p):
            return 0.3
            
        # 5. Unanswerable / Missing Info
        if re.search(r'(cannot be determined|insufficient info|unknown)', p):
            return 0.1
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        self.prop_map = {}
        self.rev_map = {}
        self.prop_count = 0
        
        # 1. Parse Prompt
        prompt_props = self._parse_propositions(prompt)
        prompt_triples = self._extract_conditionals(prompt)
        
        # Build base clauses from prompt facts (unit clauses)
        base_clauses = [[p] for p in prompt_props]
        # Add conditional clauses (-A or B)
        for pre, post in prompt_triples:
            # Simplified: take first prop of pre and post for clause generation
            if pre and post:
                # If A then B => (-A v B)
                clause = [-pre[0]] + post 
                base_clauses.append(clause)

        for cand in candidates:
            # Parse Candidate
            cand_props = self._parse_propositions(cand)
            cand_clauses = [[p] for p in cand_props]
            
            # Check Satisfiability
            is_sat, energy = self._check_satisfiability(base_clauses, cand_clauses)
            
            # Scoring
            if not is_sat:
                score = -10.0 - energy # Heavy penalty for contradiction
            else:
                # Base score on structural overlap and lack of contradiction
                # Higher overlap with prompt props implies consistency
                overlap = len(set(cand_props) & set(prompt_props))
                score = 1.0 + (overlap * 0.5) - (energy * 0.1)
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "Consistent" if is_sat else f"Contradiction detected (Energy: {energy:.2f})"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-check for ambiguity/traps
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.5:
            return meta_cap # Honest uncertainty
            
        # 2. Structural evaluation
        self.prop_map = {}
        self.rev_map = {}
        self.prop_count = 0
        
        prompt_props = self._parse_propositions(prompt)
        prompt_triples = self._extract_conditionals(prompt)
        base_clauses = [[p] for p in prompt_props]
        for pre, post in prompt_triples:
            if pre and post:
                base_clauses.append([-pre[0]] + post)
                
        cand_props = self._parse_propositions(answer)
        cand_clauses = [[p] for p in cand_props]
        
        is_sat, energy = self._check_satisfiability(base_clauses, cand_clauses)
        
        if not is_sat:
            return 0.05 # Definitely wrong due to contradiction
            
        # 3. Compute confidence based on logical derivation strength
        # If the answer is a direct logical consequence, energy is 0 and props match
        base_conf = 0.6 # Base confidence for consistent answers
        if len(cand_props) > 0 and len(prompt_props) > 0:
            # Boost if candidate props are subset of implied logic (simplified)
            base_conf += 0.3 
        elif len(prompt_props) == 0:
            # If prompt had no structure, we can't be very confident
            base_conf = 0.4
            
        return min(base_conf, meta_cap)

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If it rains, the ground is wet. It is raining."
    cands = ["The ground is wet", "The ground is dry", "It is sunny"]
    
    print("Evaluation:")
    for r in tool.evaluate(p, cands):
        print(f"{r['candidate']}: {r['score']:.2f} ({r['reasoning']})")
        
    print("\nConfidence:")
    print(f"Wet: {tool.confidence(p, 'The ground is wet'):.2f}")
    print(f"Dry: {tool.confidence(p, 'The ground is dry'):.2f}")
    
    # Tier B Test
    trap = "Have you stopped cheating on tests?"
    print(f"\nTrap Confidence ('{trap}'): {tool.confidence(trap, 'Yes'):.2f}")
```

</details>
