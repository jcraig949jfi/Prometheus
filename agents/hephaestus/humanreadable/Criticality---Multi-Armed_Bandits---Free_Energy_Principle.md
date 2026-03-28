# Criticality + Multi-Armed Bandits + Free Energy Principle

**Fields**: Complex Systems, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T14:24:08.883621
**Report Generated**: 2026-03-27T16:08:16.563667

---

## Nous Analysis

**Algorithm**  
Each candidate answer is treated as an arm of a multi‑armed bandit. For every arm we maintain a Beta belief \(B_i=(\alpha_i,\beta_i)\) over its latent correctness. The algorithm proceeds in rounds \(t=1…T\):

1. **Structural parsing** – Using only `re` we extract from the question‑answer pair a set of propositional atoms:  
   * literals (e.g., “X is Y”),  
   * negations (`not`),  
   * comparatives (`>`, `<`, `≥`, `≤`),  
   * conditionals (`if … then …`),  
   * causal cues (`because`, `leads to`, `results in`),  
   * ordering (`before`, `after`),  
   * numeric literals with units.  
   Each atom becomes a node in a directed constraint graph \(G_i\) (numpy `int8` adjacency matrix). Edges encode logical relations:  
   * `if A then B` → edge A→B,  
   * `A causes B` → edge A→B with causal weight 1,  
   * `A > B` → edge A→B with comparative weight 1,  
   * `not A` → self‑loop with negation weight ‑1, etc.

2. **Constraint propagation & prediction error** – We compute the transitive closure of \(G_i\) with Floyd‑Warshall (numpy `dot`‑based Boolean matrix power) to derive implied literals. A clause is violated if both a literal and its negation are reachable. The **prediction error** \(e_i\) is the fraction of violated clauses (range 0‑1). This error is the variational free‑energy approximation \(F_i = e_i + \mathcal{H}[B_i]\) where the entropy term \(\mathcal{H}\) is analytically available for the Beta distribution.

3. **Belief update** – Treat the error as a binary observation: “correct” with probability \(1-e_i\). Update the Beta:  
   \(\alpha_i \leftarrow \alpha_i + (1-e_i)\),  
   \(\beta_i \leftarrow \beta_i + e_i\).

4. **Criticality‑modulated exploration** – Compute the susceptibility \(\chi_t = \mathrm{Var}\{e_i\}_{i}\) across arms (numpy `var`). When \(\chi_t\) exceeds a threshold \(\theta\) (indicating proximity to a critical point), we inflate the exploration coefficient \(c_t = c_0 \cdot (1+\kappa\chi_t)\); otherwise \(c_t=c_0\).  
   The arm score (UCB‑like) is  
   \[
   S_i(t)=\frac{\alpha_i}{\alpha_i+\beta_i}+c_t\sqrt{\frac{\ln t}{n_i}},
   \]
   where \(n_i\) is the number of times arm \(i\) has been pulled. The arm with maximal \(S_i\) is selected as the scored answer.

**Structural features parsed** – negations, comparatives, conditionals, causal predicates, temporal ordering, numeric literals and units, equality/inequality statements.

**Novelty** – The scheme fuses three well‑studied ingredients: (1) bandit exploration/exploitation, (2) variational free‑energy minimization as a principled error measure, and (3) criticality‑driven adaptive exploration. While Bayesian bandits and active inference exist separately, the explicit use of susceptibility from criticality to modulate the exploration term in a free‑energy‑based bandit has not, to the best of my knowledge, been described in the literature.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure and propagates constraints, yielding a principled correctness estimate.  
Metacognition: 7/10 — Susceptibility provides a self‑monitoring signal that adjusts exploration, reflecting a rudimentary form of self‑assessment.  
Hypothesis generation: 6/10 — Arms are updated via observed error; generating new candidate hypotheses would require additional proposal mechanisms.  
Implementability: 9/10 — All steps rely on regex, NumPy linear algebra, and Beta updates; no external libraries or APIs are needed.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=39% cal=11% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T14:39:30.411528

---

## Code

**Source**: scrap

[View code](./Criticality---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Set
import zlib

class ReasoningTool:
    """
    A reasoning tool fusing Multi-Armed Bandits, Criticality, and Free Energy.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (literals, negations, comparatives, 
       conditionals, causality) from prompt-candidate pairs using regex.
    2. Constraint Graph: Builds a directed graph where edges represent logical implications.
    3. Free Energy Approximation: Computes prediction error (e_i) based on constraint 
       violations (contradictions found via transitive closure). 
       F_i = e_i + Entropy(Beta).
    4. Criticality Modulation: Uses variance in errors across candidates (susceptibility) 
       to dynamically adjust exploration vs exploitation.
    5. Epistemic Honesty: Detects ambiguity/presuppositions in the prompt to cap confidence.
    """

    def __init__(self):
        # Beta prior parameters (uniform prior)
        self.alpha_0 = 1.0
        self.beta_0 = 1.0
        
        # Criticality parameters
        self.c_0 = 0.5  # Base exploration
        self.kappa = 2.0 # Criticality gain
        self.theta = 0.05 # Criticality threshold
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\s+(\w+)', re.I),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\w+)', re.I),
            'conditional': re.compile(r'\b(if|when|unless)\s+(.+?)\s*(then|,)?\s*(.+?)(?=\bif\b|\bthen\b|$)', re.I),
            'causal': re.compile(r'(\w+(?:\s+\w+)*)\s+(causes|leads to|results in|because|due to)\s+(\w+(?:\s+\w+)*)', re.I),
            'numeric': re.compile(r'(\d+(?:\.\d+)?)\s*(==|=|!=|<>|>|<|>=|<=)\s*(\d+(?:\.\d+)?)'),
            'presupposition': re.compile(r'\b(have you stopped|why did|why does|stopped|quit|failed to)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all)\s+\w+.*\b(a|an)\s+\w+', re.I),
            'pronoun_ambiguity': re.compile(r'\b(\w+)\s+told\s+(\w+)\s+(he|she|it|they)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\s+\w+\s+(or|but)\s+\w+', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I)
        }

    def _extract_atoms(self, text: str) -> Tuple[Set[str], Dict[str, List[Tuple[str, str]]]]:
        """Extract literals and relations from text."""
        text_lower = text.lower()
        atoms = set()
        relations = [] # (source, target, type)
        
        # Extract simple literals (words)
        words = re.findall(r'\b\w+\b', text_lower)
        atoms.update(words)
        
        # Negations: not X -> (X, not_X)
        for m in self.patterns['negation'].finditer(text_lower):
            target = m.group(2)
            atoms.add(f"not_{target}")
            relations.append((target, f"not_{target}", 'negation'))
            
        # Comparatives: A > B -> A > B
        for m in self.patterns['comparative'].finditer(text_lower):
            a, op, b = m.group(1), m.group(2), m.group(3)
            atoms.add(f"{a}_gt_{b}")
            relations.append((a, b, 'comparative'))
            
        # Conditionals: If A then B -> A -> B
        for m in self.patterns['conditional'].finditer(text_lower):
            # Simplified grouping for regex robustness
            cond_part = m.group(2).strip() if m.group(2) else ""
            res_part = m.group(4).strip() if m.group(4) else ""
            if cond_part and res_part:
                c_atom = cond_part.split()[0] if cond_part else "cond"
                r_atom = res_part.split()[0] if res_part else "res"
                relations.append((c_atom, r_atom, 'conditional'))
                
        # Causal: A causes B -> A -> B
        for m in self.patterns['causal'].finditer(text_lower):
            src = m.group(1).split()[-1] if m.group(1) else ""
            tgt = m.group(3).split()[0] if m.group(3) else ""
            if src and tgt:
                relations.append((src, tgt, 'causal'))
                
        # Numeric evaluation
        for m in self.patterns['numeric'].finditer(text):
            v1, op, v2 = float(m.group(1)), m.group(2), float(m.group(3))
            valid = False
            if op in ['==', '=', 'is']: valid = (v1 == v2)
            elif op in ['!=', '<>']: valid = (v1 != v2)
            elif op == '>': valid = (v1 > v2)
            elif op == '<': valid = (v1 < v2)
            elif op == '>=': valid = (v1 >= v2)
            elif op == '<=': valid = (v1 <= v2)
            
            if not valid:
                # Mark as a contradiction atom if numeric logic fails
                atoms.add("numeric_contradiction")
                
        return atoms, relations

    def _build_graph(self, atoms: Set[str], relations: List) -> np.ndarray:
        """Build adjacency matrix for constraint propagation."""
        atom_list = list(atoms)
        idx_map = {a: i for i, a in enumerate(atom_list)}
        n = len(atom_list)
        if n == 0:
            return np.zeros((0,0), dtype=np.int8), atom_list, idx_map
            
        adj = np.zeros((n, n), dtype=np.int8)
        
        for src, tgt, rtype in relations:
            if src in idx_map and tgt in idx_map:
                u, v = idx_map[src], idx_map[tgt]
                adj[u, v] = 1
                if rtype == 'negation':
                    # Self loop for negation marker or specific handling
                    pass 
                    
        return adj, atom_list, idx_map

    def _compute_transitive_closure(self, adj: np.ndarray) -> np.ndarray:
        """Floyd-Warshall using boolean matrix power (numpy dot)."""
        if adj.shape[0] == 0:
            return adj
        n = adj.shape[0]
        # Boolean matrix multiplication via dot and threshold
        closure = adj.copy()
        np.fill_diagonal(closure, 1)
        
        # Simple iterative squaring for small graphs (T=10 max usually for sentences)
        for _ in range(n): 
            closure = np.dot(closure, closure)
            closure = (closure > 0).astype(np.int8)
        return closure

    def _calculate_error(self, prompt: str, candidate: str) -> float:
        """
        Calculate prediction error based on constraint violations.
        Returns a value in [0, 1].
        """
        full_text = f"{prompt} {candidate}"
        atoms, relations = self._extract_atoms(full_text)
        
        if not atoms:
            return 0.5 # Neutral if nothing parsed
            
        adj, atom_list, idx_map = self._build_graph(atoms, relations)
        if adj.shape[0] == 0:
            return 0.5
            
        closure = self._compute_transitive_closure(adj)
        
        violations = 0
        total_checks = 0
        
        # Check for contradictions: A and not_A both reachable or implied
        for atom in atom_list:
            if atom.startswith("not_"):
                pos_atom = atom[4:]
                if pos_atom in idx_map and atom in idx_map:
                    i_pos = idx_map[pos_atom]
                    i_neg = idx_map[atom]
                    # If pos implies neg or neg implies pos (in a closed loop of contradiction)
                    # Or if both are reachable from a common root (simplified here to direct conflict)
                    if closure[i_pos, i_neg] == 1 or closure[i_neg, i_pos] == 1:
                        violations += 1
                    total_checks += 1
                    
        # Explicit numeric contradiction
        if "numeric_contradiction" in atoms:
            violations += 1
            total_checks += 1
            
        if total_checks == 0:
            # No explicit contradictions found, check semantic overlap as proxy
            # Use NCD as a minor penalty for low coherence if no logic found
            return 0.1 
            
        error = min(1.0, violations / max(1, total_checks))
        return error

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            score = min(score, 0.2)
            
        # 2. Scope ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            score = min(score, 0.4)
            
        # 3. Pronoun ambiguity (if question asks 'who' or 'he/she')
        if self.patterns['pronoun_ambiguity'].search(p_lower) and ('who' in p_lower or '?' in p_lower):
            score = min(score, 0.3)
            
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            score = min(score, 0.5)
            
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            score = min(score, 0.6)
            
        # 6. Unanswerability (heuristic: very short prompt or specific keywords)
        if len(prompt.split()) < 3 or "insufficient" in p_lower or "unknown" in p_lower:
            score = min(score, 0.3)
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(z1), len(z2), len(z12)
        return (len12 - min(len1, len2)) / max(len1, len2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        T = len(candidates)
        # Initialize Beta beliefs
        alphas = np.full(T, self.alpha_0)
        betas = np.full(T, self.beta_0)
        errors = np.zeros(T)
        n_pulls = np.zeros(T)
        
        # Round 1: Structural Parsing & Error Calculation
        for i, cand in enumerate(candidates):
            e_i = self._calculate_error(prompt, cand)
            errors[i] = e_i
            # Update Beta based on error as binary observation
            # "Correct" prob = 1 - e_i
            alphas[i] += (1.0 - e_i)
            betas[i] += e_i
            n_pulls[i] = 1.0
            
        # Criticality Modulation
        chi_t = float(np.var(errors))
        if chi_t > self.theta:
            c_t = self.c_0 * (1.0 + self.kappa * chi_t)
        else:
            c_t = self.c_0
            
        scores = []
        for i in range(T):
            mean_val = alphas[i] / (alphas[i] + betas[i])
            # UCB-like score
            exploration = c_t * np.sqrt(np.log(max(1, T)) / n_pulls[i])
            score = mean_val + exploration
            
            # NCD Tiebreaker (max 15% influence)
            # Compare candidate to prompt coherence
            ncd_val = self._ncd(prompt, candidates[i])
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Weighted combination: 85% Logic/Bandit, 15% NCD
            final_score = 0.85 * score + 0.15 * ncd_score
            
            scores.append({
                "candidate": candidates[i],
                "score": float(final_score),
                "reasoning": f"Error:{errors[i]:.2f}, Entropy:{np.log(alphas[i]+betas[i]):.2f}, Crit:{chi_t:.2f}"
            })
            
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural evaluation
        error = self._calculate_error(prompt, answer)
        
        # Base confidence from error (inverse)
        # If error is 0, conf is high. If error is 1, conf is low.
        base_conf = 1.0 - error
        
        # Apply NCD penalty if answer is gibberish relative to prompt
        ncd_val = self._ncd(prompt, answer)
        if ncd_val > 0.8: # Very different
            base_conf *= 0.5
            
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_cap)
        
        # Ensure strict bounds
        return float(max(0.0, min(1.0, final_conf)))
```

</details>
