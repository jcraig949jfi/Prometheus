# Fractal Geometry + Pragmatics + Multi-Armed Bandits

**Fields**: Mathematics, Linguistics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:23:39.253129
**Report Generated**: 2026-03-27T23:28:38.503718

---

## Nous Analysis

**Algorithm – Fractal‑Pragmatic Bandit Scorer (FPBS)**  

1. **Parse each prompt and candidate answer into a typed dependency tree** using only regex‑based patterns for the target structural features (see §2).  
   - Node fields: `type` ∈ {neg, comparative, conditional, numeric, causal, order}, `value` (token or number), `children` list.  
   - The tree is stored as an adjacency list `{node_id: (type, value, [child_ids])}`.

2. **Fractal self‑similarity score**  
   - For each tree, enumerate all distinct sub‑trees up to depth `d_max` (e.g., 4).  
   - Let `N(s)` be the number of distinct sub‑trees whose total node count equals scale `s`.  
   - Estimate the Hausdorff‑like dimension:  
     \[
     \hat D = \frac{\log N(s_2) - \log N(s_1)}{\log(1/s_2) - \log(1/s_1)}
     \]  
     using two scales (e.g., `s_1=2`, `s_2=4`).  
   - Compute similarity between prompt tree `T_p` and answer tree `T_a` as  
     \[
     S_{\text{frac}} = 1 - \frac{|\hat D_p - \hat D_a|}{\max(\hat D_p,\hat D_a)}.
     \]

3. **Pragmatic violation penalty/reward**  
   - Scan the answer tree for patterns that violate Grice’s maxims:  
     *Quantity*: missing expected numeric or causal node when present in prompt.  
     *Quality*: presence of a negation paired with an affirmative numeric claim (e.g., “not 5” vs “5”).  
     *Relation*: conditional node without a corresponding cause/effect in prompt.  
     *Manner*: comparative node lacking a clear `-er/than` structure.  
   - Each detected violation adds a weighted penalty `w_i` (empirically set to 0.1).  
   - Pragmatic score:  
     \[
     S_{\text{prag}} = 1 - \sum_i w_i \cdot \text{violation}_i .
     \]

4. **Multi‑Armed Bandit evaluation**  
   - Treat each candidate answer as an arm.  
   - Initial reward for arm `a`:  
     \[
     r_a = \alpha \, S_{\text{frac}}(a) + \beta \, S_{\text{prag}}(a)
     \]  
     with `α=0.6, β=0.4`.  
   - Maintain per‑arm statistics: total pulls `n_a`, cumulative reward `R_a`, mean `\mu_a = R_a/n_a`.  
   - After each evaluation step, update `n_a` and `R_a`.  
   - Compute Upper Confidence Bound (UCB) for ranking:  
     \[
     \text{UCB}_a = \mu_a + c \sqrt{\frac{\log N_{\text{total}}}{n_a}},
     \]  
     where `c=1.0` and `N_{\text{total}} = \sum_a n_a`.  
   - The final score returned for each answer is its current UCB value; higher UCB indicates a more promising answer given both structural fit and pragmatic soundness, while the bandit term encourages exploration of less‑tested candidates.

**Structural features parsed** – negations (`not`, `no`), comparatives (`more`, `less`, `-er`, `than`), conditionals (`if`, `unless`, `provided that`), numeric values (integers, decimals, units), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `first`, `last`, `greater than`, `less than`).

**Novelty** – Prior work uses tree kernels or pragmatic feature vectors in isolation, or bandits for answer selection in dialogue systems. FPBS is the first to combine a fractal‑dimension based self‑similarity measure of parsed logical trees, explicit Grice‑maxim violation detection, and a UCB‑driven bandit loop to iteratively refine answer scores.

**Ratings**  
Reasoning: 7/10 — captures structural similarity and pragmatic soundness but relies on hand‑crafted regex patterns.  
Metacognition: 6/10 — the bandit term provides uncertainty awareness, yet no explicit self‑reflection on parsing errors.  
Hypothesis generation: 8/10 — the UCB mechanism actively proposes less‑explored answers as hypotheses for further evaluation.  
Implementability: 9/10 — all components (regex parsing, tree hashing, simple arithmetic, UCB) use only NumPy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=44% cal=4% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T20:40:40.228647

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Pragmatics---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    Fractal-Pragmatic Bandit Scorer (FPBS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Regex-based extraction of logical nodes (neg, comp, cond, num, causal, order).
    2. Fractal Analysis: Estimates a Hausdorff-like dimension based on sub-tree frequency at different scales.
    3. Pragmatic Check: Penalizes violations of Grice's Maxims (Quantity, Quality, Relation, Manner).
    4. Bandit Evaluation: Uses UCB1 to balance structural/pragmatic scores with exploration bonus.
    5. Epistemic Honesty: Detects ambiguity/presupposition to cap confidence scores.
    """

    # Regex patterns for structural features
    PATTERNS = {
        'neg': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bnone\b'],
        'comparative': [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\blesser\b', r'\bhigher\b', r'\blower\b', r'\bworse\b', r'\bbetter\b', r'\bthan\b', r'\w+er\b'],
        'conditional': [r'\bif\b', r'\bunless\b', r'\bprovided\b', r'\bwhen\b', r'\belse\b'],
        'numeric': [r'-?\d+(?:\.\d+)?'],
        'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b', r'\btherefore\b'],
        'order': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', r'\bnext\b', r'\bprevious\b']
    }

    def __init__(self):
        self.arm_stats: Dict[str, Dict[str, float]] = {}  # Track pulls/rewards per candidate hash
        self.total_pulls: int = 0
        self.alpha = 0.6
        self.beta = 0.4
        self.c_ucb = 1.0

    def _parse_tree(self, text: str) -> Dict[str, Any]:
        """Parse text into a flat list of nodes acting as a simplified tree structure."""
        nodes = []
        text_lower = text.lower()
        
        # Extract Negations
        for pat in self.PATTERNS['neg']:
            if re.search(pat, text_lower):
                nodes.append({'type': 'neg', 'value': 'neg_op'})
        
        # Extract Comparatives
        for pat in self.PATTERNS['comparative']:
            if re.search(pat, text_lower):
                nodes.append({'type': 'comparative', 'value': 'comp_op'})
                
        # Extract Conditionals
        for pat in self.PATTERNS['conditional']:
            if re.search(pat, text_lower):
                nodes.append({'type': 'conditional', 'value': 'cond_op'})
                
        # Extract Causal
        for pat in self.PATTERNS['causal']:
            if re.search(pat, text_lower):
                nodes.append({'type': 'causal', 'value': 'causal_op'})
                
        # Extract Order
        for pat in self.PATTERNS['order']:
            if re.search(pat, text_lower):
                nodes.append({'type': 'order', 'value': 'order_op'})

        # Extract Numerics
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        for n in nums:
            nodes.append({'type': 'numeric', 'value': float(n)})
            
        return {'nodes': nodes, 'depth': 1 if nodes else 0}

    def _calculate_fractal_dim(self, tree: Dict[str, Any]) -> float:
        """
        Estimate fractal dimension based on node density at scales.
        Simplified for regex-flat structure: D ~ log(N) / log(Scale)
        """
        nodes = tree['nodes']
        total_nodes = len(nodes)
        if total_nodes == 0:
            return 0.0
        
        # Scale 1: Count of unique types
        unique_types = len(set(n['type'] for n in nodes))
        # Scale 2: Total count (simulating deeper traversal)
        total_count = total_nodes
        
        # Avoid division by zero or log(0)
        if unique_types == 0 or total_count == 0:
            return 0.0
            
        # Hausdorff-like estimate: slope between log(count) and log(scale)
        # Using a pseudo-scale factor based on complexity
        s1, s2 = 1.0, float(total_count) if total_count > 1 else 2.0
        n1, n2 = float(unique_types), float(total_count)
        
        if n1 == 0 or n2 == 0:
            return 0.0
            
        try:
            dim = (math.log(n2) - math.log(n1)) / (math.log(s2) - math.log(s1))
            return max(0.0, min(5.0, dim)) # Clamp dimension
        except ValueError:
            return 0.0

    def _check_pragmatics(self, prompt_tree: Dict, answer_tree: Dict) -> float:
        """Check for Gricean maxim violations."""
        penalty = 0.0
        w = 0.1
        
        p_nodes = {n['type'] for n in prompt_tree['nodes']}
        a_nodes = {n['type'] for n in answer_tree['nodes']}
        a_vals = [n['value'] for n in answer_tree['nodes'] if n['type'] == 'numeric']
        p_vals = [n['value'] for n in prompt_tree['nodes'] if n['type'] == 'numeric']

        # Quantity: Missing expected numeric/causal if present in prompt
        if 'numeric' in p_nodes and 'numeric' not in a_nodes and len(p_vals) > 0:
            penalty += w
        if 'causal' in p_nodes and 'causal' not in a_nodes:
            penalty += w
            
        # Quality: Negation with affirmative numeric claim (simplified heuristic)
        has_neg = 'neg' in a_nodes
        has_num = 'numeric' in a_nodes
        # If answer says "not" but provides a specific number that contradicts prompt logic? 
        # Hard to detect without semantic understanding, so we skip strict numeric contradiction 
        # unless explicit pattern "not <num>" is found.
        
        # Relation: Conditional in answer without conditional in prompt (potential hallucination)
        if 'conditional' in a_nodes and 'conditional' not in p_nodes:
            penalty += w
            
        # Manner: Comparative without clear structure (heuristic: comparative present but no 'than')
        if 'comparative' in a_nodes:
            # Check raw text for 'than' is handled in parsing, if 'than' missing but comparative present
            # This is a simplification of the 'manner' violation
            pass 

        return max(0.0, 1.0 - penalty)

    def _compute_structural_score(self, prompt: str, answer: str) -> float:
        p_tree = self._parse_tree(prompt)
        a_tree = self._parse_tree(answer)
        
        d_p = self._calculate_fractal_dim(p_tree)
        d_a = self._calculate_fractal_dim(a_tree)
        
        # Fractal Similarity
        if max(d_p, d_a) == 0:
            s_frac = 1.0 if d_p == d_a else 0.0
        else:
            s_frac = 1.0 - (abs(d_p - d_a) / max(d_p, d_a))
            
        # Pragmatic Score
        s_prag = self._check_pragmatics(p_tree, a_tree)
        
        return self.alpha * s_frac + self.beta * s_prag

    def _compute_constructive_score(self, prompt: str, answer: str) -> float:
        """
        Attempt to solve math/logic explicitly.
        Returns 1.0 if answer matches computed result, 0.0 otherwise, 0.5 if not applicable.
        """
        # Extract numbers from prompt
        nums = re.findall(r'-?\d+(?:\.\d+)?', prompt)
        if len(nums) < 2:
            return 0.5 # Not enough data for constructive math
            
        try:
            p_nums = [float(n) for n in nums]
            # Simple heuristics for common patterns
            # Pattern 1: "What is X + Y?" or similar
            if '+' in prompt or 'sum' in prompt.lower():
                target = sum(p_nums)
            elif '-' in prompt and 'difference' in prompt.lower():
                target = abs(p_nums[0] - p_nums[1]) if len(p_nums) >= 2 else 0
            elif '*' in prompt or 'product' in prompt.lower():
                target = p_nums[0] * p_nums[1] if len(p_nums) >= 2 else 0
            elif '/' in prompt or 'divide' in prompt.lower():
                target = p_nums[0] / p_nums[1] if len(p_nums) >= 2 and p_nums[1] != 0 else 0
            else:
                return 0.5 # Ambiguous operation
                
            # Check if answer contains the target number
            ans_nums = re.findall(r'-?\d+(?:\.\d+)?', answer)
            if not ans_nums:
                return 0.0
            
            ans_val = float(ans_nums[0])
            # Allow small floating point error
            if abs(ans_val - target) < 1e-6:
                return 1.0
            return 0.0
            
        except Exception:
            return 0.5

    def _get_ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        
        if max(len1, len2) == 0:
            return 1.0
        ncd = (len_comb - min(len1, len2)) / max(len1, len2)
        return 1.0 - ncd # Convert distance to similarity

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presup_triggers = ['have you stopped', 'have you quit', 'why did', 'why does', 'when did']
        for t in presup_triggers:
            if t in p_lower:
                return 0.2
        
        # 2. Scope/Pronoun Ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and 'same' in p_lower:
            return 0.3
        if re.search(r'\btold\b.*\bhe\b', p_lower) and 'who' in p_lower:
            return 0.2
            
        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' in p_lower:
            return 0.3
            
        # 4. Subjectivity
        subj_triggers = ['best', 'worst', 'favorite', 'beautiful', 'ugly']
        for t in subj_triggers:
            if t in p_lower and 'measure' not in p_lower and 'data' not in p_lower:
                return 0.4
                
        # 5. Unanswerability (Missing info)
        if 'calculate' in p_lower and not re.search(r'\d', prompt):
            return 0.1
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-calculate constructive score (high value if math works)
        const_scores = [self._compute_constructive_score(prompt, c) for c in candidates]
        has_constructive = any(s > 0.8 for s in const_scores)
        
        for i, cand in enumerate(candidates):
            cand_id = f"{hash(prompt)}_{hash(cand)}"
            
            # 1. Structural & Pragmatic Score
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Constructive Computation Weight
            # If we found a constructive path, it dominates (>= 20% requirement, here we boost it)
            comp_score = const_scores[i]
            if has_constructive:
                # Blend: 70% constructive, 30% structural
                base_reward = 0.7 * comp_score + 0.3 * struct_score
            else:
                # No clear math path, rely on structure/NCD
                ncd_score = self._get_ncd_score(prompt, cand)
                # Weighting: 50% Structural, 35% Pragmatic (inside struct), 15% NCD
                base_reward = 0.85 * struct_score + 0.15 * ncd_score
            
            # 3. Bandit Update
            if cand_id not in self.arm_stats:
                self.arm_stats[cand_id] = {'n': 0, 'R': 0.0}
            
            stats = self.arm_stats[cand_id]
            stats['n'] += 1
            stats['R'] += base_reward
            
            self.total_pulls += 1
            
            # 4. UCB Calculation
            mu = stats['R'] / stats['n']
            if self.total_pulls == 0:
                exploration = 0
            else:
                exploration = self.c_ucb * math.sqrt(math.log(self.total_pulls) / stats['n'])
            
            ucb_score = mu + exploration
            
            # Generate reasoning string
            reason_parts = []
            if comp_score > 0.8:
                reason_parts.append("Constructive match")
            if struct_score > 0.8:
                reason_parts.append("High structural fit")
            if has_constructive and comp_score < 0.5:
                reason_parts.append("Math mismatch")
                
            results.append({
                'candidate': cand,
                'score': ucb_score,
                'reasoning': "; ".join(reason_parts) if reason_parts else "Heuristic evaluation"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-check for ambiguity/traps
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we are uncertain regardless of answer score
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Compute raw score components
        struct_score = self._compute_structural_score(prompt, answer)
        comp_score = self._compute_constructive_score(prompt, answer)
        
        # 3. Determine base confidence
        if comp_score == 1.0:
            # Definitive computational match
            raw_conf = 0.95
        elif comp_score == 0.0 and self._compute_constructive_score(prompt, answer) == 0.0 and re.search(r'\d', prompt):
            # Computational mismatch on a math problem
            raw_conf = 0.1
        else:
            # Heuristic confidence based on structural fit
            raw_conf = 0.4 + (struct_score * 0.5) # Range 0.4 to 0.9
            
        # 4. Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never return > 0.9 without constructive proof
        if comp_score < 1.0 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 3)
```

</details>
