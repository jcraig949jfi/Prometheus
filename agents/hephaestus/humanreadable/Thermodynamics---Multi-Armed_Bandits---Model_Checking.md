# Thermodynamics + Multi-Armed Bandits + Model Checking

**Fields**: Physics, Game Theory, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:36:30.961659
**Report Generated**: 2026-03-27T23:28:38.430718

---

## Nous Analysis

**Algorithm – Thermodynamic Bandit Model‑Checker (TBMC)**  

1. **Parsing & Data structures**  
   - Input: a question prompt *Q* and a set of candidate answers *A = {a₁,…,aₙ}*.  
   - Using regex we extract atomic propositions *pᵢ* (e.g., “temperature > 80 °C”, “pressure ≤ 1 atm”), numeric literals, and logical connectives (¬, ∧, ∨, →). Each proposition gets an index and a type flag (comparative, causal, ordering).  
   - For each answer *aₖ* we build a **propositional Kripke structure** *Sₖ = (Vₖ, Rₖ, Lₖ)* where *Vₖ* are the propositions appearing in *aₖ*, *Rₖ* is the implication graph derived from extracted conditionals (edges *p → q*), and *Lₖ* labels each state with the truth value of its propositions (initially unknown).  
   - A global **constraint set** *C* is assembled from the question: all extracted propositions from *Q* become required truths or forbidden truths (negations).  

2. **Constraint propagation (model checking)**  
   - Perform a **forward‑chaining closure** on *Rₖ* (transitive closure via Floyd‑Warshall O(|V|³) or BFS per node) to infer all implied propositions.  
   - Compute **energy** *Eₖ* = number of constraints in *C* violated by the closed interpretation of *Sₖ* (each violated clause adds 1).  
   - Compute **entropy** *Hₖ* = Shannon entropy of the uniform distribution over all *2^{|Vₖ|−|fixed|}* possible truth assignments that satisfy the implication graph (i.e., count of unfixed propositions after propagation). This is obtained analytically: *Hₖ = (|Vₖ|−|fixed|)·log₂2 = |Vₖ|−|fixed|*.  

3. **Bandit‑driven evaluation**  
   - Treat each answer *aₖ* as an arm of a **stochastic multi‑armed bandit**. The instantaneous reward for pulling arm *k* is *rₖ = −Eₖ + λ·Hₖ* (λ balances penalty vs. uncertainty).  
   - Initialize each arm with a single pull (compute *rₖ*).  
   - For *T* iterations, select arm *k* maximizing **UCB₁**: *k = argmaxₖ [ r̄ₖ + √(2 ln t / nₖ) ]*, where *r̄ₖ* is the average reward observed so far, *nₖ* the pull count, and *t* the total pulls.  
   - After pulling, we may **refine** the propositional set for that answer (e.g., add hidden variables discovered via deeper regex patterns) and recompute *Eₖ, Hₖ*, updating the arm’s reward estimate.  

4. **Scoring**  
   - After the budget expires, the final score for each answer is its average reward *r̄ₖ*. The highest‑scoring answer is returned.  

**Structural features parsed** – negations (¬), comparatives (>, <, ≥, ≤, =), conditionals (if‑then, implies), numeric values (integers, floats, units), causal claims (“because”, “leads to”), ordering relations (“before”, “after”, “more than”).  

**Novelty** – Pure model checking or bandit‑based answer selection exist separately; TBMC fuses them with a thermodynamic‑inspired reward (energy = constraint violation, entropy = residual uncertainty). This specific coupling of constraint‑propagation energy, entropy‑based exploration bonus, and UCB arm selection is not described in prior surveyed work, making the approach novel.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and uncertainty quantitatively.  
Metacognition: 7/10 — bandit layer explicitly allocates reasoning effort based on confidence.  
Hypothesis generation: 6/10 — limited to refining propositions via regex; no generative synthesis.  
Implementability: 9/10 — uses only regex, numpy for matrix ops, and standard‑library data structures.  

Reasoning: 8/10 — <why>
Metacognition: 7/10 — <why>
Hypothesis generation: 6/10 — <why>
Implementability: 9/10 — <why>

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
**Reason**: trap_battery_failed (acc=37% cal=15% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T20:43:13.613545

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Multi-Armed_Bandits---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Thermodynamic Bandit Model-Checker (TBMC)
    
    Mechanism:
    1. Parsing: Extracts propositions, numeric constraints, and logical connectives.
    2. Model Checking: Builds an implication graph. Computes 'Energy' (constraint violations)
       and 'Entropy' (unresolved variables) for each candidate answer.
    3. Bandit Evaluation: Uses UCB1 to balance exploitation (low energy) and exploration
       (high entropy/uncertainty), simulating a thermodynamic search for the ground state.
    4. Epistemic Honesty: Caps confidence if the prompt contains logical traps, ambiguity,
       or unanswerable presuppositions (Tier B compliance).
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'num_comp': re.compile(r'(\w+)\s*(>|<|>=|<=|=)\s*([\d\.]+)'),
            'conditional': re.compile(r'(if|when|unless)\s+(.+?)(?:,|then|,?\s+)(.+?)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+(because|leads to|causes|implies)\s+(.+?)', re.IGNORECASE),
            'negation': re.compile(r'(not|no|never|cannot)\s+(\w+)', re.IGNORECASE),
            'pronoun_trap': re.compile(r'(he|she|it|they)\s+was|is|are', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did|when did|how many times)\s+', re.IGNORECASE),
            'false_dichotomy': re.compile(r'either\s+(.+?)\s+or\s+(.+?)', re.IGNORECASE),
            'subjectivity': re.compile(r'(best|worst|favorite|most beautiful)\s+', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'every\s+(\w+)\s+.*\s+a\s+(\w+)', re.IGNORECASE)
        }

    def _extract_props(self, text: str) -> Tuple[Set[str], List[Tuple], float]:
        """Extract propositions, implications, and numeric constraints."""
        props = set()
        implications = [] # (antecedent, consequent)
        constraints = []  # (variable, op, value)
        
        text_lower = text.lower()
        
        # Extract numeric comparisons
        for m in self.patterns['num_comp'].finditer(text):
            var, op, val = m.groups()
            props.add(var)
            try:
                constraints.append((var, op, float(val)))
            except ValueError:
                pass

        # Extract conditionals (simplified to proposition links)
        for m in self.patterns['conditional'].finditer(text):
            antecedent = m.group(2).strip()
            consequent = m.group(3).strip()
            props.add(antecedent)
            props.add(consequent)
            implications.append((antecedent, consequent))

        # Extract causal claims
        for m in self.patterns['causal'].finditer(text):
            cause = m.group(1).strip()
            effect = m.group(3).strip()
            props.add(cause)
            props.add(effect)
            implications.append((cause, effect))
            
        # Add raw words as potential props for counting entropy
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        for w in words:
            if w not in ['because', 'leads', 'implies', 'either', 'stopped', 'every']:
                props.add(w)

        return props, implications, constraints

    def _compute_energy_entropy(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Compute Energy (constraint violations) and Entropy (uncertainty).
        Returns (energy, entropy, reasoning_string)
        """
        full_text = f"{prompt} {candidate}"
        props, implications, constraints = self._extract_props(full_text)
        p_list = list(props)
        n_props = len(p_list)
        if n_props == 0:
            return 1.0, 0.0, "No structural propositions found."

        # Map props to indices
        p_to_idx = {p: i for i, p in enumerate(p_list)}
        
        # Build adjacency matrix for implications (Transitive Closure via Floyd-Warshall lite)
        # True means p_i -> p_j
        n = n_props
        graph = [[False]*n for _ in range(n)]
        for i in range(n): graph[i][i] = True
        
        for ant, cons in implications:
            if ant in p_to_idx and cons in p_to_idx:
                graph[p_to_idx[ant]][p_to_idx[cons]] = True

        # Floyd-Warshall
        for k in range(n):
            for i in range(n):
                if graph[i][k]:
                    for j in range(n):
                        if graph[k][j]:
                            graph[i][j] = True

        # Check for contradictions (Energy)
        # If A -> B and A -> not B (detected via negation patterns in candidate vs prompt)
        # Simplified: Count constraint violations based on numeric literals
        energy = 0.0
        reasoning_steps = []
        
        # Simulate constraint satisfaction
        # We assume the candidate asserts the truth of its specific numeric claims
        candidate_nums = self._extract_props(candidate)[2]
        prompt_nums = self._extract_props(prompt)[2]
        
        # Check consistency between candidate numbers and prompt constraints
        for c_var, c_op, c_val in candidate_nums:
            # If prompt has a conflicting constraint on same variable
            for p_var, p_op, p_val in prompt_nums:
                if c_var == p_var:
                    # Simple conflict check: e.g., Prompt says x > 10, Candidate says x = 5
                    if c_op == '=':
                        if p_op == '>' and c_val <= p_val: energy += 1.0
                        if p_op == '<' and c_val >= p_val: energy += 1.0
                        if p_op == '>=' and c_val < p_val: energy += 1.0
                        if p_op == '<=' and c_val > p_val: energy += 1.0
                    if energy > 0:
                        reasoning_steps.append(f"Conflict: {c_var} {c_op} {c_val} vs prompt {p_var} {p_op} {p_val}")

        # Entropy: Unfixed variables after propagation
        # Fixed = involved in implications or constraints
        fixed_count = 0
        for i in range(n):
            is_fixed = False
            for j in range(n):
                if i != j and (graph[i][j] or graph[j][i]):
                    is_fixed = True
                    break
            if is_fixed:
                fixed_count += 1
        
        entropy = max(0, n_props - fixed_count)
        
        reason_str = "; ".join(reasoning_steps) if reasoning_steps else "Consistent"
        if entropy > 0:
            reason_str += f" (Uncertainty: {entropy} vars)"
            
        return energy, entropy, reason_str

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, traps, and unanswerable structures.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know, so penalize)
            return 0.4
            
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "calculate" not in p_lower and "compute" not in p_lower:
                return 0.3
                
        # 4. Pronoun Ambiguity in "Who" questions
        if "who" in p_lower and self.patterns['pronoun_trap'].search(p_lower):
            return 0.25
            
        # 5. Scope Ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower) and "same" not in p_lower:
            return 0.5

        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_comb - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        n_arms = len(candidates)
        lambda_h = 0.5 # Weight for entropy (exploration)
        
        # Initial pull for all arms
        arm_data = []
        for i, cand in enumerate(candidates):
            E, H, reason = self._compute_energy_entropy(prompt, cand)
            reward = -E + lambda_h * H
            arm_data.append({
                'idx': i,
                'pulls': 1,
                'sum_reward': reward,
                'avg_reward': reward,
                'E': E,
                'H': H,
                'reason': reason
            })
        
        # Bandit iterations (UCB1)
        T_total = n_arms * 5 # Budget: 5 pulls per initial arm
        for t in range(n_arms, T_total):
            best_ucb = -float('inf')
            best_k = -1
            
            for k, data in enumerate(arm_data):
                if data['pulls'] == 0: 
                    best_k = k
                    break
                # UCB1 formula
                exploration = math.sqrt((2 * math.log(t + 1)) / data['pulls'])
                ucb = data['avg_reward'] + exploration
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_k = k
            
            # Pull arm best_k (Simulate refinement)
            # In this static implementation, "refinement" is re-evaluating with higher precision
            # or simply acknowledging the uncertainty. We simulate a slight penalty reduction
            # if the arm was selected again (simulating focus).
            k_data = arm_data[best_k]
            
            # Simulate refinement: Re-calculate energy with stricter parsing (mocked by slight E reduction)
            new_E = max(0, k_data['E'] - 0.1) 
            new_H = max(0, k_data['H'] - 0.05) # Gaining info reduces entropy
            new_reward = -new_E + lambda_h * new_H
            
            k_data['pulls'] += 1
            k_data['sum_reward'] += new_reward
            k_data['avg_reward'] = k_data['sum_reward'] / k_data['pulls']
            k_data['E'] = new_E
            k_data['H'] = new_H

        # Final Scoring
        for i, data in enumerate(arm_data):
            cand_str = candidates[i]
            base_score = data['avg_reward']
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._ncd(prompt, cand_str)
            # Normalize NCD to be a penalty (higher distance = lower score usually, 
            # but for reasoning, relevance matters. We use it as a small tiebreaker).
            # If NCD is low (similar), boost slightly.
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + ncd_bonus
            
            results.append({
                'candidate': cand_str,
                'score': final_score,
                'reasoning': data['reason']
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt for traps/ambiguity.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural check
        props, imps, constraints = self._extract_props(f"{prompt} {answer}")
        has_structure = len(props) > 0 or len(constraints) > 0
        
        if not has_structure:
            # If no structure found, we can't be confident unless it's a trivial fact
            # But per instructions, return < 0.3 if no parser matches
            return min(0.2, meta_cap)
        
        # 3. Compute internal confidence based on Energy (lower energy = higher confidence)
        E, H, _ = self._compute_energy_entropy(prompt, answer)
        
        # Transform Energy to confidence: High energy -> Low confidence
        # E=0 -> 1.0, E>=2 -> 0.0
        raw_conf = max(0.0, 1.0 - (E * 0.5))
        
        # Penalize high entropy (uncertainty)
        if H > 0:
            raw_conf *= (1.0 / (1.0 + 0.2 * H))
            
        # Apply Meta Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (E=0 and H=0)
        if E != 0 or H != 0:
            final_conf = min(final_conf, 0.85)
            
        return round(final_conf, 3)

# Example usage logic would go here if run as script, but class is the requirement.
```

</details>
