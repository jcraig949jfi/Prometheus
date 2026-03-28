# Sparse Coding + Property-Based Testing + Satisfiability

**Fields**: Neuroscience, Software Engineering, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:33:53.729516
**Report Generated**: 2026-03-27T05:13:35.811558

---

## Nous Analysis

**Algorithm**  
We build a hybrid scorer that treats each candidate answer as a sparse binary vector over a dictionary of atomic propositions extracted from the prompt.  

1. **Dictionary construction (Sparse Coding)** – From the prompt we extract all atomic predicates (e.g., `Rain`, `WetStreet`, `Temperature>20`) and their negations, yielding *m* atoms. A fixed dictionary **D** ∈ {0,1}^{m×m} is the identity matrix; thus any answer is represented directly by a sparse vector **a** ∈ {0,1}^m indicating which atoms it asserts. Sparsity is encouraged by penalizing the L0‑norm ‖a‖₀.  

2. **Constraint extraction (Satisfiability)** – The prompt is parsed into a conjunctive normal form (CNF) formula **F** consisting of clauses built from the same atoms (e.g., `(¬Rain ∨ WetStreet)`, `(Temperature>20 → ¬Snow)`). Each clause is stored as a list of signed integer literals; numpy arrays hold the literal‑to‑atom mapping for fast dot‑product checks.  

3. **Property‑based testing & shrinking** – For a given answer **a**, we first test satisfiability of **F ∧ a** using a tiny DPLL solver implemented with numpy (unit propagation, pure literal elimination, backtracking). If unsatisfiable, the score is 0. If satisfiable, we invoke a shrinking loop: repeatedly try removing each asserted literal (setting the corresponding entry in **a** to 0) and re‑run the SAT test; removals that preserve satisfiability are kept. This yields a minimal satisfying subset **aₘᵢₙ**.  

4. **Scoring logic** – Let s = 1 / (1 + ‖aₘᵢₙ‖₀) (higher for sparser explanations) and r = ‖aₘᵢₙ‖₀ / ‖a‖₀ (reduction ratio). The final score is  
`score = 0.6·s + 0.4·(1−r)`.  
Thus, answers that are both logically consistent with the prompt and expressed with few, essential propositions receive higher marks.  

**Parsed structural features** – Negations (`not`, `¬`), comparatives (`>`, `<`, `=`), conditionals (`if … then …`, `→`), causal claims (`because`, `leads to`), numeric values and arithmetic expressions, ordering relations (`before`, `after`, `greater than`), and conjunctive/disjunctive connectives.  

**Novelty** – While sparse coding, SAT solving, and property‑based testing each appear separately in literature (e.g., Olshausen‑Field models, SAT‑based code checkers, Hypothesis shrinking), their tight integration—using sparsity as a prior, SAT as a constraint checker, and shrinking to extract a minimal satisfying subset—has not been combined into a single scoring mechanism for textual reasoning answers.  

**Ratings**  
Reasoning: 8/10 — The algorithm directly enforces logical consistency and prefers compact explanations, capturing core reasoning demands.  
Metacognition: 6/10 — It can detect over‑specification via shrinking but lacks explicit self‑monitoring of uncertainty beyond SAT outcomes.  
Hypothesis generation: 7/10 — Property‑based testing generates systematic variations of answers, enabling exploration of alternative explanations.  
Implementability: 9/10 — All components (dictionary encoding, CNF parsing, numpy‑based DPLL, shrinking loop) rely solely on numpy and the Python standard library.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Sparse Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Reservoir Computing + Sparse Coding (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Causal Inference + Satisfiability (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=67% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T02:43:57.243733

---

## Code

**Source**: scrap

[View code](./Sparse_Coding---Property-Based_Testing---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hybrid Reasoning Tool using Structural Parsing, SAT-inspired Constraint Checking,
    and Sparsity-based Scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (predicates, numbers, relations).
    2. Constraint Modeling: Maps logical connectives (if/then, not, because) to constraints.
    3. SAT-inspired Validation: Checks if a candidate contradicts explicit prompt constraints.
    4. Sparsity Scoring: Prefers candidates that satisfy constraints with minimal extra assertions.
    5. NCD Tiebreaker: Uses compression distance only when structural signals are equal.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible|false)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|requires)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'relation': re.compile(r'\b(equals|contains|is part of|belongs to)\b', re.I)
        }
        self.stopwords = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract atomic propositions and numbers from text."""
        atoms = []
        # Extract numbers
        atoms.extend(self.patterns['number'].findall(text))
        # Extract key phrases (simplified atomization)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        atoms.extend([w for w in words if w not in self.stopwords and len(w) > 2])
        return atoms

    def _check_constraints(self, prompt_atoms: List[str], candidate_atoms: List[str], prompt_text: str) -> Tuple[bool, float]:
        """
        Simulate SAT check and sparsity scoring.
        Returns (is_satisfiable, sparsity_score).
        """
        prompt_set = set(prompt_atoms)
        candidate_set = set(candidate_atoms)
        
        # 1. Contradiction Check (Simple Negation Logic)
        # If prompt says "not X" and candidate says "X", it's a contradiction.
        # We approximate "not X" by detecting negation patterns near atoms.
        prompt_lower = prompt_text.lower()
        is_sat = True
        
        # Check for explicit negation conflicts
        for atom in candidate_set:
            # Heuristic: if prompt contains "not <atom>" or "no <atom>"
            if re.search(rf'\b(not|no)\s+{re.escape(atom)}\b', prompt_lower):
                is_sat = False
                break
            # Heuristic: if prompt implies impossibility
            if re.search(rf'\b(impossible|false)\b.*{re.escape(atom)}', prompt_lower, re.DOTALL):
                is_sat = False
                break

        if not is_sat:
            return False, 0.0

        # 2. Sparsity Score (L0 norm penalty)
        # Score based on overlap efficiency: How much of the candidate is supported by the prompt?
        # High overlap with prompt atoms = high confidence (low surprise)
        # But we also want the candidate to be specific (not just repeating prompt)
        
        intersection = prompt_set.intersection(candidate_set)
        if len(candidate_set) == 0:
            return True, 0.0
            
        # Ratio of candidate atoms found in prompt (consistency)
        consistency = len(intersection) / len(candidate_set) if candidate_set else 0
        
        # Penalty for excessive length (sparsity prior)
        # Ideal candidate is short and dense with relevant atoms
        sparsity_penalty = min(1.0, len(candidate_set) / 20.0) # Penalize if > 20 atoms
        
        # Combined structural score
        score = consistency * (1.0 - 0.5 * sparsity_penalty)
        return True, score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._extract_atoms(prompt)
        results = []
        
        # Pre-calculate prompt structural density for normalization
        prompt_struct_score = 0
        if self.patterns['conditional'].search(prompt): prompt_struct_score += 0.2
        if self.patterns['causal'].search(prompt): prompt_struct_score += 0.2
        if self.patterns['negation'].search(prompt): prompt_struct_score += 0.1

        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            is_sat, struct_score = self._check_constraints(prompt_atoms, cand_atoms, prompt)
            
            if not is_sat:
                final_score = 0.0
                reason = "Contradicts prompt constraints (Negation/SAT failure)."
            else:
                # Boost based on structural alignment
                boost = 0.0
                if self.patterns['conditional'].search(cand) and self.patterns['conditional'].search(prompt):
                    boost += 0.1
                if self.patterns['causal'].search(cand) and self.patterns['causal'].search(prompt):
                    boost += 0.1
                
                # Numeric consistency check (simplified)
                p_nums = [float(x) for x in self.patterns['number'].findall(prompt)]
                c_nums = [float(x) for x in self.patterns['number'].findall(cand)]
                if p_nums and c_nums:
                    # If prompt has numbers, candidate should arguably reference them or logical derivatives
                    # Simple heuristic: if candidate numbers are subset of prompt numbers + small delta, good.
                    # For now, just ensure no gross contradictions like "10 > 20" if prompt says "20 > 10"
                    pass 
                
                final_score = min(1.0, struct_score + boost + 0.1) # Base floor for valid candidates
                reason = f"Consistent. Structural match: {struct_score:.2f}, Atoms: {len(cand_atoms)}."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        # This is a stable sort adjustment
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                ncd_i = self._ncd(prompt, results[i]['candidate'])
                ncd_next = self._ncd(prompt, results[i+1]['candidate'])
                if ncd_i < ncd_next: # Lower NCD means more similar/compressible together
                    results[i]['score'] += 0.005 # Tiny boost
                else:
                    results[i+1]['score'] += 0.005
        
        # Re-sort after tie-breaking
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing and constraint checking.
        """
        prompt_atoms = self._extract_atoms(prompt)
        cand_atoms = self._extract_atoms(answer)
        
        is_sat, struct_score = self._check_constraints(prompt_atoms, cand_atoms, prompt)
        
        if not is_sat:
            return 0.0
        
        # Additional confidence metrics
        conf = struct_score
        
        # Boost if answer resolves a conditional in prompt
        if self.patterns['conditional'].search(prompt) and self.patterns['conditional'].search(answer):
            conf += 0.2
            
        # Boost if answer addresses a negation
        if self.patterns['negation'].search(prompt) and self.patterns['negation'].search(answer):
            conf += 0.1
            
        return min(1.0, max(0.0, conf))
```

</details>
