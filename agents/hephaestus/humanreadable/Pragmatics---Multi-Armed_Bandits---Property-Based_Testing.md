# Pragmatics + Multi-Armed Bandits + Property-Based Testing

**Fields**: Linguistics, Game Theory, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T04:00:37.688083
**Report Generated**: 2026-03-27T16:08:10.296357

---

## Nous Analysis

**Algorithm: Pragmatic Bandit Property‑Test Scorer (PB‑PTS)**  

1. **Parsing & Proposition Extraction**  
   - Input: prompt `P` and a list of candidate answers `A = [a₁,…,a_k]`.  
   - Use regex‑based structural parsers to pull out:  
     * atomic propositions (e.g., “X is Y”)  
     * comparatives (`>`, `<`, `=`),  
     * conditionals (`if … then …`),  
     * negations (`not`),  
     * causal markers (`because`, `leads to`),  
     * numeric literals.  
   - Each proposition is stored as a tuple `(type, arg1, arg2?, polarity)` in a NumPy structured array `props`.  

2. **Property‑Based Generation of Pragmatic Variants**  
   - For each answer `a_i`, treat its literal proposition set as a seed.  
   - A Hypothesis‑style generator creates *implicature variants* by applying Grice‑style operations:  
     * add scalar implicatures (e.g., “some” → “not all”),  
     * insert conversational maxims (quantity, relevance),  
     * flip polarity under negation scope.  
   - Variants are kept in a list `V_i = [v_{i,0},…,v_{i,m}]` where `v_{i,0}` is the literal form.  

3. **Multi‑Armed Bandit Evaluation**  
   - Each variant `v_{i,j}` is an arm.  
   - Maintain for each arm: empirical mean reward `μ_{i,j}` (NumPy array) and pull count `n_{i,j}`.  
   - Reward of pulling an arm = degree of constraint satisfaction when the variant’s propositions are added to the prompt’s proposition set:  
     * Run a lightweight constraint propagator (transitivity of `>`, modus ponens on conditionals, numeric equality/inequality checks).  
     * Reward = `1 – (num_violated_constraints / total_constraints)`.  
   - At each iteration, select the arm with highest Upper Confidence Bound:  
     `UCB_{i,j} = μ_{i,j} + c * sqrt(log(total_pulls) / n_{i,j})` (c tuned, e.g., 1.0).  
   - Pull the selected arm, update its `μ` and `n`.  
   - After a budget of `B` pulls (e.g., `B = 20 * k`), the final score for answer `a_i` is the mean reward of its best‑performing variant: `score_i = max_j μ_{i,j}`.  

4. **Output**  
   - Return vector `scores` (NumPy array) ranking candidates.  

**Structural Features Parsed**  
- Negation scope (to flip polarity).  
- Comparative operators (`>`, `<`, `>=`, `<=`, `==`) for ordering constraints.  
- Conditional antecedent/consequent for modus ponens.  
- Causal connectors (`because`, `therefore`) treated as directional implications.  
- Numeric literals for arithmetic constraints.  
- Quantifiers (`all`, `some`, `none`) to trigger scalar implicature generation.  

**Novelty**  
The combination is novel: no existing system couples property‑based pragmatic variant generation with a bandit‑driven exploration‑exploitation loop to score answers. Prior work uses either static pragmatic enrichment or bandits for answer selection, but not both together with constraint‑based reward signals.  

**Ratings**  
Reasoning: 8/10 — captures logical constraints and pragmatic enrichment via a principled exploration mechanism.  
Metacognition: 7/10 — the bandit framework implicitly monitors uncertainty and allocates effort, a basic metacognitive control.  
Hypothesis generation: 8/10 — property‑based variant creation systematically explores implicature space.  
Implementability: 9/10 — relies only on regex, NumPy arrays, and standard‑library containers; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.67** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Multi-Armed Bandits + Pragmatics: strong positive synergy (+0.599). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Information Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T07:24:37.311785

---

## Code

**Source**: scrap

[View code](./Pragmatics---Multi-Armed_Bandits---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Pragmatic Bandit Property-Test Scorer (PB-PTS)
    
    Mechanism:
    1. Parses prompt/candidates into structured propositions (comparatives, negations, numerics).
    2. Generates pragmatic variants (implicatures) via property-based rules.
    3. Uses a Multi-Armed Bandit (UCB) to explore which variant best satisfies logical constraints.
    4. Scores based on constraint satisfaction density; uses NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.c_explore = 1.0
        self.budget_factor = 20
        
    def _parse_props(self, text: str) -> List[Tuple]:
        """Extract atomic propositions: comparatives, numerics, negations, conditionals."""
        props = []
        text_lower = text.lower()
        
        # Numeric literals and comparisons
        nums = re.findall(r'[-]?\d+(?:\.\d+)?', text)
        for i, n in enumerate(nums):
            props.append(('num', float(n), i, 1.0))
            
        # Comparatives (greater, less, equal)
        if re.search(r'\b(greater|more|larger|higher)\b', text_lower):
            props.append(('comp', 'gt', None, 1.0))
        if re.search(r'\b(less|smaller|lower|fewer)\b', text_lower):
            props.append(('comp', 'lt', None, 1.0))
        if re.search(r'\b(equal|same|identical)\b', text_lower):
            props.append(('comp', 'eq', None, 1.0))
            
        # Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            props.append(('neg', 'scope', None, -1.0))
            
        # Conditionals
        if re.search(r'\b(if|then|unless)\b', text_lower):
            props.append(('cond', 'implies', None, 1.0))
            
        # Quantifiers
        if re.search(r'\b(all|every)\b', text_lower):
            props.append(('quant', 'all', None, 1.0))
        if re.search(r'\b(some|few)\b', text_lower):
            props.append(('quant', 'some', None, 1.0))
            
        return props if props else [('null', 'empty', None, 0.0)]

    def _generate_variants(self, base_props: List[Tuple]) -> List[List[Tuple]]:
        """Generate pragmatic implicature variants (Property-Based Testing step)."""
        variants = [base_props] # v_0 is literal
        
        # Scalar implicature: "some" -> "not all" simulation
        has_some = any(p[0] == 'quant' and p[1] == 'some' for p in base_props)
        if has_some:
            new_vars = []
            for p in base_props:
                if p[0] == 'quant' and p[1] == 'some':
                    new_vars.append(('quant', 'not_all', None, 1.0))
                else:
                    new_vars.append(p)
            variants.append(new_vars)
            
        # Negation flip simulation
        has_neg = any(p[0] == 'neg' for p in base_props)
        if has_neg:
            new_vars = []
            for p in base_props:
                if p[0] == 'neg':
                    new_vars.append(('neg', 'flipped', None, 1.0)) # Simplified flip
                else:
                    new_vars.append(p)
            variants.append(new_vars)
            
        return variants

    def _check_constraints(self, prompt_props: List[Tuple], answer_props: List[Tuple]) -> float:
        """Lightweight constraint propagator. Returns satisfaction score 0-1."""
        if not prompt_props or not answer_props:
            return 0.0
            
        violations = 0
        total_checks = 0
        
        # Check numeric consistency
        p_nums = [p[1] for p in prompt_props if p[0] == 'num']
        a_nums = [p[1] for p in answer_props if p[0] == 'num']
        
        # Simple transitivity/ordering check
        if p_nums and a_nums:
            total_checks += 1
            # If prompt implies ordering and answer violates it
            if any(p[1] == 'gt' for p in prompt_props) and len(a_nums) >= 2:
                if a_nums[0] <= a_nums[-1]: # Simplified check
                    violations += 1
                    
        # Check comparative alignment
        p_comp = [p for p in prompt_props if p[0] == 'comp']
        a_comp = [p for p in answer_props if p[0] == 'comp']
        
        if p_comp and a_comp:
            total_checks += 1
            # Rough polarity match
            p_dir = 1 if 'gt' in str(p_comp[0]) else (-1 if 'lt' in str(p_comp[0]) else 0)
            a_dir = 1 if 'gt' in str(a_comp[0]) else (-1 if 'lt' in str(a_comp[0]) else 0)
            if p_dir != 0 and a_dir != 0 and p_dir != a_dir:
                violations += 1

        # Negation scope check
        p_neg = any(p[0] == 'neg' for p in prompt_props)
        a_neg = any(p[0] == 'neg' for p in answer_props)
        if p_neg != a_neg:
            total_checks += 1
            # Contextual penalty if negation presence mismatches significantly
            # (Simplified: strict match required for high score)
            # violations += 0.5 

        if total_checks == 0:
            return 0.5 # Neutral if no specific constraints found
            
        return max(0.0, 1.0 - (violations / max(1, total_checks)))

    def _ucb_score(self, pulls: int, mean_reward: float, total_pulls: int) -> float:
        if pulls == 0:
            return float('inf')
        return mean_reward + self.c_explore * np.sqrt(np.log(total_pulls + 1) / pulls)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_props = self._parse_props(prompt)
        prompt_vars = self._generate_variants(prompt_props)
        
        for cand in candidates:
            cand_props = self._parse_props(cand)
            cand_vars = self._generate_variants(cand_props)
            
            # Multi-Armed Bandit Setup
            # Arms are combinations of (prompt_variant, cand_variant)
            arms = []
            arm_stats = [] # (pulls, mean_reward)
            
            for pv in prompt_vars:
                for cv in cand_vars:
                    arms.append((pv, cv))
                    arm_stats.append([0, 0.0])
            
            total_pulls = 0
            budget = self.budget_factor * len(arms) if len(arms) > 0 else 10
            
            # Bandit Loop
            for _ in range(budget):
                if total_pulls == 0:
                    # Initial pull
                    idx = 0
                else:
                    # Select max UCB
                    ucb_vals = [self._ucb_score(s[0], s[1], total_pulls) for s in arm_stats]
                    idx = int(np.argmax(ucb_vals))
                
                # Pull arm
                pv, cv = arms[idx]
                reward = self._check_constraints(pv, cv)
                
                # Update stats
                pulls, mean = arm_stats[idx]
                new_mean = (mean * pulls + reward) / (pulls + 1)
                arm_stats[idx] = [pulls + 1, new_mean]
                total_pulls += 1
            
            # Final score is max mean reward of any variant
            final_score = max(s[1] for s in arm_stats) if arm_stats else 0.0
            
            # NCD Tiebreaker logic (simplified)
            # If score is neutral (0.5), use string similarity as weak tiebreaker
            if 0.49 < final_score < 0.51:
                import zlib
                s1, s2 = prompt.encode(), cand.encode()
                comp = zlib.compress(s1 + s2)
                ncd = len(comp) / max(len(zlib.compress(s1)), len(zlib.compress(s2)), 1)
                final_score += (1.0 - ncd) * 0.01 # Tiny boost for similarity

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Bandit converged on variant with {final_score:.2f} constraint satisfaction."
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_props = self._parse_props(prompt)
        a_props = self._parse_props(answer)
        
        # Direct constraint check
        base_score = self._check_constraints(p_props, a_props)
        
        # If structural signals are weak, rely on variant exploration
        if base_score == 0.5:
            # Re-run mini-evaluation internally
            res = self.evaluate(prompt, [answer])
            return res[0]['score'] if res else 0.5
            
        return float(base_score)
```

</details>
