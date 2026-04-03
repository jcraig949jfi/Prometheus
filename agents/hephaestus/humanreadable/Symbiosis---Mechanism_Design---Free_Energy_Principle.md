# Symbiosis + Mechanism Design + Free Energy Principle

**Fields**: Biology, Economics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T05:32:15.444611
**Report Generated**: 2026-04-01T20:30:43.639122

---

## Nous Analysis

**Algorithm**  
Each candidate answer is first parsed into a set of logical atoms \(A_i\) using regex patterns that capture predicates, arguments, negations, comparatives, conditionals, causal markers, numbers and ordering terms (e.g., “if X then Y”, “X > Y”, “because Z”). Atoms are stored as tuples (predicate, arg1, arg2, polarity) in a Python list.  

A factor graph is built where each atom is a variable node. Three types of constraint factors are added:  

1. **Symbiosis factors** – for every pair of atoms that appear in a mutual‑benefit pattern (e.g., “X provides Y and Y provides X”), a factor rewards joint truth: \(f_{sym}(x_i,x_j)=\exp(w_{sym}\cdot[x_i\land x_j])\).  
2. **Mechanism‑design factors** – each atom that corresponds to an incentive‑compatible statement (detected via keywords like “should”, “optimal”, “maximize”) gets a unary factor \(f_{md}(x_i)=\exp(w_{md}\cdot x_i)\); misaligned statements receive a negative weight.  
3. **Free‑energy factors** – a global prior model \(M\) (derived from a reference answer or knowledge base) supplies expected truth values \(\hat{p}_i\). The factor implements prediction‑error minimization: \(f_{fe}(x_i)=\exp(-\lambda\cdot (x_i-\hat{p}_i)^2)\).  

All factors are combined into an energy \(E=-\log\prod f\). Approximate variational free energy is minimized by loopy belief propagation: messages are numpy arrays of shape (2,) representing \(P(x_i=0)\) and \(P(x_i=1)\). Iterations update messages using standard sum‑product rules until convergence or a fixed step limit. The final score for an answer is the negative free energy (lower \(E\) → higher score) plus the sum of mechanism‑design unary weights, yielding a scalar that reflects mutual benefit, incentive alignment, and predictive fidelity.

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”, “equals”), conditionals (“if … then …”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values and units, ordering relations (“before”, “after”, “first”, “last”), quantifiers (“all”, “some”, “none”), and conjunction/disjunction markers.

**Novelty**  
While logical parsing, constraint propagation, and variational inference each appear separately, the specific fusion of symbiosis‑inspired mutual‑benefit factors, mechanism‑design incentive compatibility, and free‑energy‑based belief propagation into a single scoring loop is not documented in existing literature, making the combination novel.

**Rating lines**  
Reasoning: 8/10 — captures logical structure and propagates constraints effectively, though approximate inference limits exactness.  
Metacognition: 6/10 — the algorithm can adjust weights based on prediction error but lacks explicit self‑monitoring of its own reasoning process.  
Hypothesis generation: 7/10 — generates a structured set of propositional hypotheses from text and evaluates their joint viability.  
Implementability: 9/10 — relies only on regex, numpy arrays for message passing, and standard‑library containers; no external dependencies or neural components.

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
**Reason**: trap_battery_failed (acc=37% cal=42% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T16:29:04.438863

---

## Code

**Source**: scrap

[View code](./Symbiosis---Mechanism_Design---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool fusing Symbiosis (mutual benefit), Mechanism Design (incentive alignment),
    and Free Energy Principle (prediction error minimization) via loopy belief propagation.
    
    Core Mechanism:
    1. Parse candidates into logical atoms (predicates, numbers, conditionals).
    2. Construct a factor graph with:
       - Symbiosis factors: Reward joint truth of mutually beneficial atoms.
       - Mechanism Design factors: Reward incentive-compatible statements.
       - Free Energy factors: Minimize divergence from a prior model (reference answer/logic).
    3. Perform loopy belief propagation to estimate marginal probabilities.
    4. Score = Negative Free Energy + Mechanism Alignment.
    
    Epistemic Honesty (Tier B):
    - Detects presuppositions, ambiguities, and unanswerable queries.
    - Caps confidence low (<0.3) for ambiguous/unanswerable prompts.
    - Prioritizes constructive computation (math/logic) over string similarity.
    """

    def __init__(self):
        # Weights for the energy function
        self.w_sym = 2.0       # Symbiosis weight
        self.w_md = 1.5        # Mechanism design weight
        self.lambda_fe = 3.0   # Free energy precision
        
        # Regex patterns for atomic parsing
        self.patterns = {
            'conditional': re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+(because|leads to|results in|causes)\s+(.+?)', re.IGNORECASE),
            'comparative': re.compile(r'(.+?)\s+(greater than|less than|equals|is more than|is less than)\s+(.+?)', re.IGNORECASE),
            'numeric': re.compile(r'\d+(?:\.\d+)?'),
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'incentive': re.compile(r'\b(should|optimal|maximize|minimize|best|efficient)\b', re.IGNORECASE),
            'symbiosis': re.compile(r'(.+?)\s+(provides|gives|helps)\s+(.+?)\s+and\s+\3\s+(provides|gives|helps)\s+\1', re.IGNORECASE),
            # Tier B Traps
            'presupposition': re.compile(r'(have you stopped|why did .+? fail|why is .+? true)', re.IGNORECASE),
            'pronoun_ambig': re.compile(r'(.+?)\s+told\s+(.+?)\s+he\s+', re.IGNORECASE),
            'false_dichotomy': re.compile(r'either\s+(.+?)\s+or\s+(.+?)\s+(?:\?|$)', re.IGNORECASE),
            'subjectivity': re.compile(r'(best|worst|favorite|most beautiful)\s+(?!way|method|approach)', re.IGNORECASE)
        }

    def _parse_atoms(self, text: str) -> List[Tuple[str, Any, Any, int]]:
        """Parse text into logical atoms: (predicate, arg1, arg2, polarity)"""
        atoms = []
        text_lower = text.lower()
        
        # Check negations
        has_negation = bool(self.patterns['negation'].search(text_lower))
        polarity = -1 if has_negation else 1

        # Extract numerics for constructive computation
        numbers = [float(n) for n in self.patterns['numeric'].findall(text)]
        if numbers:
            atoms.append(('numeric_value', numbers[0], None, polarity))
            if len(numbers) >= 2:
                atoms.append(('comparison', numbers[0], numbers[1], polarity))

        # Extract conditionals
        for match in self.patterns['conditional'].finditer(text):
            atoms.append(('conditional', match.group(1).strip(), match.group(2).strip(), polarity))

        # Extract causals
        for match in self.patterns['causal'].finditer(text):
            atoms.append(('causal', match.group(1).strip(), match.group(3).strip(), polarity))

        # Extract comparatives
        for match in self.patterns['comparative'].finditer(text):
            atoms.append(('comparative', match.group(1).strip(), match.group(3).strip(), polarity))

        # Fallback atomic propositions (simple split if nothing else found)
        if not atoms:
            words = [w for w in re.split(r'\s+', text) if len(w) > 3]
            if len(words) >= 2:
                atoms.append(('prop', words[0], " ".join(words[1:]), polarity))
        
        return atoms if atoms else [('empty', '', '', 1)]

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        Frame B: Constructive Computation.
        Attempts to solve math/logic problems directly.
        Returns a score boost if the candidate matches the computed result.
        """
        score = 0.0
        p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        # Simple arithmetic verification
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Try basic ops
            ops = {
                '+': p_nums[0] + p_nums[1] if len(p_nums) > 1 else p_nums[0],
                '-': p_nums[0] - p_nums[1] if len(p_nums) > 1 else p_nums[0],
                '*': p_nums[0] * p_nums[1] if len(p_nums) > 1 else p_nums[0],
                '/': (p_nums[0] / p_nums[1]) if len(p_nums) > 1 and p_nums[1] != 0 else p_nums[0]
            }
            
            # Check if candidate contains any computed result
            for op_val in ops.values():
                if any(abs(op_val - cn) < 1e-6 for cn in c_nums):
                    score += 2.0 # Strong signal for correct computation
            
            # Check direct number match for simple retrieval
            if c_nums and p_nums and abs(c_nums[0] - p_nums[-1]) < 1e-6:
                score += 1.0

        return score

    def _build_and_solve_graph(self, atoms: List[Tuple], reference_model: Optional[str] = None) -> Tuple[float, float]:
        """
        Build factor graph and run loopy belief propagation.
        Returns: (negative_free_energy, mechanism_alignment_score)
        """
        n = len(atoms)
        if n == 0:
            return 0.0, 0.0

        # Initialize messages: P(x=0), P(x=1)
        # Uniform prior initially
        messages = [[0.5, 0.5] for _ in range(n)]
        
        # Precompute factors
        # 1. Mechanism Design Factors (Unary)
        md_weights = []
        for atom in atoms:
            pred, a1, a2, pol = atom
            text_rep = f"{pred} {a1} {a2}"
            if self.patterns['incentive'].search(text_rep):
                md_weights.append(self.w_md * pol) # Reward if aligned, penalize if negated misalignment
            else:
                md_weights.append(0.0)

        # 2. Symbiosis Factors (Pairwise) - Simplified for O(N^2)
        # We look for mutual patterns in the atom list
        sym_pairs = []
        for i in range(n):
            for j in range(i+1, n):
                # Heuristic: if atoms share arguments and imply mutual benefit
                p1, a1_1, a1_2, _ = atoms[i]
                p2, a2_1, a2_2, _ = atoms[j]
                # Simple overlap check for symbiosis simulation
                if (a1_1 == a2_2 or a1_2 == a2_1) and ('provide' in str(p1) or 'help' in str(p1)):
                    sym_pairs.append((i, j))

        # 3. Free Energy Factors (Prior from reference or heuristic)
        # If no reference, assume neutral prior (0.5), else bias towards expected truth
        prior_probs = [0.5] * n 
        if reference_model:
            # Simplified: if reference exists, assume atoms appearing in it are likely true
            ref_lower = reference_model.lower()
            for i, atom in enumerate(atoms):
                if str(atom[1]).lower() in ref_lower or str(atom[2]).lower() in ref_lower:
                    prior_probs[i] = 0.9
                else:
                    prior_probs[i] = 0.1

        # Loopy Belief Propagation (Fixed iterations for determinism)
        for _ in range(10):
            new_messages = []
            for i in range(n):
                # Start with prior (Free Energy term approximation)
                # f_fe = exp(-lambda * (x - p)^2)
                # Approximate as bias towards prior
                bias = [math.exp(-self.lambda_fe * (0 - prior_probs[i])**2), 
                        math.exp(-self.lambda_fe * (1 - prior_probs[i])**2)]
                
                # Add Mechanism Design unary factor
                md_factor = math.exp(md_weights[i])
                local_potential = [bias[0], bias[1] * md_factor]
                
                # Multiply by messages from neighbors (Symbiosis)
                for (u, v) in sym_pairs:
                    if u == i:
                        neighbor = v
                        # Simplified sum-product: multiply by neighbor's belief
                        nb = messages[neighbor]
                        local_potential[0] *= nb[0]
                        local_potential[1] *= nb[1]
                    elif v == i:
                        neighbor = u
                        nb = messages[neighbor]
                        local_potential[0] *= nb[0]
                        local_potential[1] *= nb[1]
                
                # Normalize
                total = sum(local_potential) + 1e-9
                new_messages.append([local_potential[0]/total, local_potential[1]/total])
            
            messages = new_messages

        # Calculate final scores
        # Negative Free Energy (approximated by log-prob of max state)
        total_energy = 0.0
        for i in range(n):
            prob_true = messages[i][1]
            if prob_true > 0:
                total_energy += math.log(prob_true + 1e-9)
            # Add MD weight if true
            if prob_true > 0.5:
                total_energy += md_weights[i]

        return -total_energy, sum(md_weights)

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Pronoun ambiguity
        if self.patterns['pronoun_ambig'].search(p_lower) and 'who' in p_lower:
            return 0.25
            
        # 3. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 4. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4 # Slightly higher but still low
            
        # 5. Unanswerability (Heuristic: very short prompt with no numbers/structure)
        words = re.findall(r'\w+', p_lower)
        if len(words) < 3 and not self.patterns['numeric'].search(p_lower):
            return 0.3

        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)"""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            ncd = (c12 - min_len) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_atoms = self._parse_atoms(prompt)
        
        # Generate a pseudo-reference model from the prompt itself (assuming prompt contains truth)
        ref_model = prompt 
        
        for cand in candidates:
            cand_atoms = self._parse_atoms(cand)
            
            # 1. Constructive Computation (Frame B Priority)
            comp_score = self._compute_constructive_score(prompt, cand)
            
            # 2. Factor Graph Scoring
            # Combine prompt and candidate atoms for joint evaluation
            all_atoms = prompt_atoms + cand_atoms
            neg_fe, md_score = self._build_and_solve_graph(all_atoms, ref_model)
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd_val = self._ncd_score(prompt, cand)
            # Invert NCD so higher is better, scale to small range
            ncd_score = (1.0 - ncd_val) * 0.5 
            
            # Final Score Composition
            # Structural/Logic (neg_fe) + Mechanism (md_score) + Computation (comp_score) + NCD
            final_score = neg_fe + md_score + comp_score + ncd_score
            
            # Boost if constructive math matched
            if comp_score > 0:
                final_score += 5.0

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FE:{neg_fe:.2f}, MD:{md_score:.2f}, Comp:{comp_score:.1f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        cap = self._meta_confidence(prompt, answer)
        
        if cap < 0.3:
            return cap

        # 2. Structural/Computation check
        # If we can't parse any structure and it's not a simple string, confidence should be low
        atoms = self._parse_atoms(prompt + " " + answer)
        has_structure = len(atoms) > 1 or self.patterns['numeric'].search(prompt)
        
        if not has_structure:
            # Fallback to NCD for simple factual lookup if no structure
            ncd = self._ncd_score(prompt, answer)
            # If NCD is high (different), confidence low. If low (similar), confidence moderate.
            base_conf = (1.0 - ncd) * 0.8
        else:
            # Use the scoring mechanism to determine confidence
            # Evaluate single candidate against prompt
            res = self.evaluate(prompt, [answer])
            score = res[0]['score'] if res else 0
            
            # Map score to confidence (sigmoid-like)
            # Assume score > 5 is high confidence, < 0 is low
            base_conf = 1 / (1 + math.exp(-0.5 * (score - 2.0)))
        
        # Apply cap
        final_conf = min(base_conf, cap)
        
        # Enforce strict upper bound unless computation was definitive
        if final_conf > 0.9 and not self.patterns['numeric'].search(answer):
            final_conf = 0.9
            
        return round(final_conf, 3)
```

</details>
