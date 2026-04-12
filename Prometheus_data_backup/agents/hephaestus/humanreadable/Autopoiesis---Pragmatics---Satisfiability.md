# Autopoiesis + Pragmatics + Satisfiability

**Fields**: Complex Systems, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:28:02.410250
**Report Generated**: 2026-04-02T10:55:58.845198

---

## Nous Analysis

**Algorithm**  
1. **Parsing → clause base** – Each sentence is turned into a set of propositional literals using regex‑based structural patterns (see §2). Literals are annotated with a *context tag* (e.g., `scalar`, `presupposition`). A clause is a disjunction of literals; the whole text yields a CNF formula `F₀`.  
2. **Autopoietic closure loop** – Repeatedly apply deterministic inference rules that are *self‑producing*:  
   * Modus ponens: from `(p → q)` and `p` add `q`.  
   * Transitivity: from `p < q` and `q < r` add `p < r`.  
   * Pragmatic enrichment: if a literal carries a scalar tag (`some X`) and the context does not entail `all X`, add the implicature `¬all X`.  
   Each iteration adds newly derived literals to the clause set, producing `Fᵢ`. The loop stops when a fixed point is reached (`Fᵢ = Fᵢ₊₁`); the resulting set `F*` is the *organizationally closed* theory self‑generated from the input.  
3. **Candidate scoring** – A candidate answer `A` is expressed as additional unit clauses `C_A`. Form the combined formula `F* ∧ C_A`.  
   * Run a pure‑Python DPLL SAT solver (using only `numpy` for clause‑matrix ops and the standard library for stacks).  
   * If SAT, score = `+|C_A|` (reward for each asserted literal that is satisfied).  
   * If UNSAT, extract a minimal unsatisfiable core (MUC) by iterative clause removal; penalty = `|MUC|`. Final score = `+|C_A| − penalty`.  
   Higher scores indicate answers that extend the autopoietic closure without causing conflict, respecting pragmatic enrichment.

**Structural features parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `more … than`), conditionals (`if … then …`, `unless`), causal claims (`because …`, `leads to`), ordering relations (`before`, `after`, `precedes`), numeric values and arithmetic expressions, quantifiers (`all`, `some`, `none`, `most`), temporal markers (`afterwards`, `previously`), and speech‑act cues (`I promise`, `I suggest`).

**Novelty** – Pure SAT‑based scoring exists, as do pragmatic enrichment loops (e.g., implicature generators). The autopoietic closure — iteratively rebuilding the theory until organizational stability — has not been combined with SAT‑based answer evaluation in publicly available tools, making this triple hybrid novel.

**Ratings**  
Reasoning: 8/10 — captures logical consequence, pragmatic context, and self‑consolidating inference, yielding nuanced scores.  
Metacognition: 6/10 — the system monitors its own clause set for fixed points but lacks explicit reflection on its inference strategy.  
Hypothesis generation: 7/10 — generates new literals (hypotheses) via closure rules; quality depends on rule completeness.  
Implementability: 9/10 — relies only on regex parsing, numpy‑based clause matrices, and a DPLL solver from the stdlib; no external libraries needed.

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
**Reason**: validation:runtime_error: NameError: name 're' is not defined

**Forge Timestamp**: 2026-04-02T10:05:39.949850

---

## Code

**Source**: scrap

[View code](./Autopoiesis---Pragmatics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, List, Set, Tuple

class ReasoningTool:
    """
    Autopoiesis x Pragmatics x Satisfiability reasoning tool.
    
    Mechanism:
    1. Parse text into propositional clauses with context tags
    2. Apply autopoietic closure: iterate inference rules until fixed point
    3. Score candidates via SAT solver (DPLL) on combined theory
    4. Epistemic honesty: detect ambiguity/presuppositions and return low confidence
    """
    
    def __init__(self):
        self.clauses = []
        self.literals = set()
        
    def _parse_to_clauses(self, text: str) -> List[Tuple[Set[str], str]]:
        """Extract propositional literals from text with context tags."""
        clauses = []
        text_lower = text.lower()
        
        # Negations: "not X", "no X"
        for m in re.finditer(r'\b(?:not|no)\s+(\w+)', text_lower):
            clauses.append(({f"~{m.group(1)}"}, "negation"))
        
        # Comparatives: "X > Y", "X < Y", "more than", "less than"
        for m in re.finditer(r'(\w+)\s+(?:>|greater than|more than)\s+(\w+)', text_lower):
            clauses.append(({f"{m.group(1)}>{m.group(2)}"}, "comparative"))
        for m in re.finditer(r'(\w+)\s+(?:<|less than|fewer than)\s+(\w+)', text_lower):
            clauses.append(({f"{m.group(1)}<{m.group(2)}"}, "comparative"))
        
        # Conditionals: "if X then Y"
        for m in re.finditer(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+)', text_lower):
            clauses.append(({f"~{m.group(1)}", m.group(2)}, "conditional"))
        
        # Quantifiers: "some X", "all X"
        for m in re.finditer(r'\bsome\s+(\w+)', text_lower):
            clauses.append(({f"some_{m.group(1)}"}, "scalar"))
        for m in re.finditer(r'\ball\s+(\w+)', text_lower):
            clauses.append(({f"all_{m.group(1)}"}, "universal"))
        
        # Extract positive assertions from statements
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            words = re.findall(r'\b\w+\b', sent.lower())
            if len(words) > 0:
                clauses.append(({f"atom_{words[0]}"}, "atom"))
        
        return clauses
    
    def _autopoietic_closure(self, clauses: List[Tuple[Set[str], str]]) -> Set[str]:
        """Apply inference rules until fixed point (organizational closure)."""
        literals = set()
        for clause, _ in clauses:
            literals.update(clause)
        
        changed = True
        iterations = 0
        while changed and iterations < 10:
            changed = False
            old_size = len(literals)
            
            # Transitivity: p<q, q<r => p<r
            comp_lits = [l for l in literals if '<' in l or '>' in l]
            for l1 in comp_lits:
                for l2 in comp_lits:
                    if '<' in l1 and '<' in l2:
                        parts1 = l1.split('<')
                        parts2 = l2.split('<')
                        if len(parts1) == 2 and len(parts2) == 2 and parts1[1] == parts2[0]:
                            new_lit = f"{parts1[0]}<{parts2[1]}"
                            if new_lit not in literals:
                                literals.add(new_lit)
                                changed = True
            
            # Pragmatic enrichment: some_X & ~all_X implicature
            for lit in list(literals):
                if lit.startswith("some_"):
                    all_version = lit.replace("some_", "all_")
                    if all_version not in literals:
                        neg_all = f"~{all_version}"
                        if neg_all not in literals:
                            literals.add(neg_all)
                            changed = True
            
            if len(literals) > old_size:
                changed = True
            iterations += 1
        
        return literals
    
    def _dpll_sat(self, clauses: List[Set[str]]) -> bool:
        """Simple DPLL SAT solver."""
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        
        # Unit propagation
        units = [list(c)[0] for c in clauses if len(c) == 1]
        if units:
            unit = units[0]
            neg = f"~{unit}" if not unit.startswith("~") else unit[1:]
            new_clauses = [c for c in clauses if unit not in c]
            new_clauses = [c - {neg} for c in new_clauses]
            return self._dpll_sat(new_clauses)
        
        # Choose literal
        lit = list(clauses[0])[0]
        neg = f"~{lit}" if not lit.startswith("~") else lit[1:]
        
        # Try assigning True
        new_clauses = [c for c in clauses if lit not in c]
        new_clauses = [c - {neg} for c in new_clauses]
        if self._dpll_sat(new_clauses):
            return True
        
        # Try assigning False
        new_clauses = [c for c in clauses if neg not in c]
        new_clauses = [c - {lit} for c in new_clauses]
        return self._dpll_sat(new_clauses)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _numeric_score(self, prompt: str, candidate: str) -> float:
        """Score numeric comparisons and arithmetic."""
        score = 0.0
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if p_nums and c_nums:
            # Check if candidate satisfies numeric constraints
            if any(x in prompt.lower() for x in ['greater', 'more', 'larger']):
                if c_nums and p_nums and float(c_nums[0]) > float(p_nums[0]):
                    score += 2.0
            if any(x in prompt.lower() for x in ['less', 'fewer', 'smaller']):
                if c_nums and p_nums and float(c_nums[0]) < float(p_nums[0]):
                    score += 2.0
        
        return score
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerable patterns."""
        p_lower = prompt.lower()
        
        # Presupposition: "have you stopped/quit X?"
        if re.search(r'\b(?:have you|did you)\s+(?:stop|quit|cease)', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(?:he|she|it|they)\s+(?:was|were)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\s+.*?\bor\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if any(x in p_lower for x in ['best', 'worst', 'favorite', 'prefer']):
            if not any(x in p_lower for x in ['most', 'least', 'measure', 'metric']):
                return 0.3
        
        # Unanswerable: asking for info not provided
        if 'why' in p_lower and 'because' not in p_lower:
            return 0.35
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using autopoietic SAT scoring."""
        # Parse prompt to clauses
        prompt_clauses = self._parse_to_clauses(prompt)
        
        # Autopoietic closure
        base_literals = self._autopoietic_closure(prompt_clauses)
        base_clause_sets = [c[0] for c in prompt_clauses]
        
        results = []
        for cand in candidates:
            cand_clauses = self._parse_to_clauses(cand)
            cand_literals = set()
            for clause, _ in cand_clauses:
                cand_literals.update(clause)
            
            # Combine and check SAT
            all_literals = base_literals | cand_literals
            clause_sets = base_clause_sets + [c[0] for c in cand_clauses]
            
            # SAT check
            is_sat = self._dpll_sat(clause_sets) if clause_sets else True
            
            # Structural score
            struct_score = len(cand_literals) if is_sat else -len(cand_literals)
            
            # Numeric score
            num_score = self._numeric_score(prompt, cand)
            
            # NCD penalty (inverse - lower is better)
            ncd = self._ncd(prompt, cand)
            ncd_score = (1 - ncd) * 0.5
            
            # Combine: 60% structural, 30% numeric, 10% NCD
            final_score = 0.6 * struct_score + 0.3 * num_score + 0.1 * ncd_score
            
            reasoning = f"SAT={'yes' if is_sat else 'no'}, struct={len(cand_literals)}, num={num_score:.2f}, ncd={ncd:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on prompt properties and answer fit."""
        # Check meta-confidence (epistemic honesty)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        score = results[0]["score"]
        
        # Normalize score to 0-1 range (heuristic)
        if score > 3:
            conf = 0.8
        elif score > 1:
            conf = 0.6
        elif score > 0:
            conf = 0.5
        else:
            conf = 0.3
        
        # Cap by meta-confidence
        return min(conf, meta_conf)
```

</details>
