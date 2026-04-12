# Evolution + Neural Plasticity + Criticality

**Fields**: Biology, Biology, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:26:43.864645
**Report Generated**: 2026-04-02T04:20:10.672148

---

## Nous Analysis

The algorithm maintains a population of candidate interpreters, each represented as a tuple (P, W) where **P** is a set of extracted logical triples (subject, relation, object) obtained via deterministic regex patterns for negations, comparatives, conditionals, causal cues, ordering markers, and numeric literals; **W** is a NumPy weight vector aligning each relation type with a contribution score.  

**Initialization**: Randomly generate N individuals by assigning each relation type a weight drawn from 𝒩(0,1).  

**Evaluation**: For a given prompt q and candidate answer a, compute a feature vector f(q,a) by counting occurrences of each relation type in P that match patterns in q and a. The raw score is s = W·f.  

**Fitness**: Define fitness F = −‖s − t‖² + λ·Var(W), where t is a target score derived from a rubric (e.g., 1 for correct, 0 for incorrect) and Var(W) measures dispersion of weights across the population. The variance term drives the system toward a critical point: high susceptibility (large weight variance) correlates with maximal correlation length in the fitness landscape.  

**Mutation (Neural Plasticity)**: For each individual, apply a Hebbian‑style update: ΔW = η·(a_correct − a_current)·f, increasing weights for relations present in the correct answer and decreasing for those in incorrect answers. Add small Gaussian noise to simulate drift.  

**Crossover (Evolution)**: Pair individuals proportionally to fitness; combine their P sets via union and average their W vectors.  

**Selection**: Keep the top K individuals (elitism) and repeat mutation/crossover for G generations.  

**Scoring**: After the final generation, return the normalized fitness of the best individual as the answer score.  

**Structural features parsed**: negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then”), causal cues (“because”, “leads to”), ordering relations (“first”, “before”, “after”), numeric values, and quantifiers (“all”, “some”).  

**Novelty**: While neuro‑evolution and Hebbian learning exist separately, coupling them with a criticality‑driven fitness term (variance‑based susceptibility) is not standard in existing reasoning‑scoring tools, making the combination novel.  

Reasoning: 7/10 — The algorithm captures logical structure and optimizes via evolutionary search, but relies on hand‑crafted regex and simple linear scoring.  
Metacognition: 6/10 — Weight variance provides a global signal of search stability, yet no explicit self‑monitoring of prediction confidence is implemented.  
Hypothesis generation: 5/10 — New hypotheses arise from mutation/crossover of relation sets, but the space is limited to predefined pattern types.  
Implementability: 8/10 — Uses only NumPy and the standard library; all operations are straightforward vectorized arithmetic and set manipulation.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T03:41:24.794831

---

## Code

**Source**: scrap

[View code](./Evolution---Neural_Plasticity---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Evolutionary Neuro-Plastic Reasoning Tool with Criticality Dynamics.
    
    Mechanism:
    1. Structural Parsing: Extracts logical triples (negations, comparatives, conditionals, causality).
    2. Dynamical Systems (Frame C): Models reasoning as a state vector evolving through premises.
       - Uses Lyapunov-style stability analysis: Re-orders premises to check if the conclusion converges.
       - High divergence = Low confidence (ambiguity/fragility).
    3. Evolutionary Optimization: Maintains a population of weight vectors (W) for relation types.
       - Fitness includes a variance term to drive the population toward "criticality" (high susceptibility).
       - Hebbian mutation adjusts weights based on pattern matching strength.
    4. Epistemic Honesty (Tier B): Detects presuppositions, false dichotomies, and scope ambiguities.
       - Caps confidence if meta-features indicate unanswerability or trickery.
    5. Scoring: Weighted sum of Structural Match (50%), Computation/Dynamics (35%), NCD (15%).
    """

    def __init__(self):
        self.n_population = 20
        self.n_generations = 15
        self.relation_types = ['negation', 'comparative', 'conditional', 'causal', 'ordering', 'numeric', 'quantifier']
        self.rng = np.random.default_rng(seed=42)  # Deterministic
        
        # Initialize Population: (P_set, W_vector)
        # P is static per individual logic, but here we share the parser and evolve W
        self.population_W = self.rng.normal(0, 1, (self.n_population, len(self.relation_types)))
        
        # Patterns for extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\bmore than\b', r'\bless than\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bprovided\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bleads to\b', r'\bcauses\b'],
            'ordering': [r'\bfirst\b', r'\blast\b', r'\bbefore\b', r'\bafter\b', r'\bnext\b'],
            'numeric': [r'\d+\.?\d*'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bevery\b', r'\bnone\b', r'\bmost\b']
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract logical triples and counts based on regex patterns."""
        text_lower = text.lower()
        features = {}
        counts = np.zeros(len(self.relation_types))
        
        for i, r_type in enumerate(self.relation_types):
            matches = []
            for pattern in self.patterns[r_type]:
                matches.extend(re.findall(pattern, text_lower))
            counts[i] = len(matches)
            features[r_type] = matches
            
        features['counts'] = counts
        features['raw'] = text
        return features

    def _compute_dynamics(self, prompt: str, answer: str) -> Tuple[float, float]:
        """
        Frame C: Dynamics Tracker.
        Simulates reasoning as a state evolution.
        Returns: (convergence_score, stability_metric)
        """
        # Split prompt into sentences/premises
        sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
        if len(sentences) < 2:
            return 1.0, 1.0  # Too short to analyze dynamics
            
        base_state = self._extract_features(prompt)
        initial_score = np.dot(base_state['counts'], self.population_W[0])
        
        # Perturbation: Re-order sentences (simulating premise re-ordering)
        # If the logic is robust, the "gist" (feature density) shouldn't change drastically
        # unless the order matters (temporal/causal chain).
        perturbations = []
        for _ in range(5):
            shuffled = sentences[:]
            self.rng.shuffle(shuffled)
            shuffled_text = " ".join(shuffled)
            feat = self._extract_features(shuffled_text)
            score = np.dot(feat['counts'], self.population_W[0])
            perturbations.append(score)
            
        perturbations = np.array(perturbations)
        divergence = np.std(perturbations)
        stability = 1.0 / (1.0 + divergence) # High stability if low divergence
        
        # Convergence: Does the answer align with the prompt's feature density?
        ans_feat = self._extract_features(answer)
        # Simple heuristic: If prompt has high numeric/comparative, answer should too
        prompt_logic_density = np.sum(base_state['counts'][1:]) # Exclude raw numeric count, focus on logic
        ans_logic_density = np.sum(ans_feat['counts'][1:])
        
        # Ideal ratio check (heuristic)
        if prompt_logic_density > 0:
            ratio = ans_logic_density / prompt_logic_density
            convergence = 1.0 if 0.5 <= ratio <= 2.0 else 0.5
        else:
            convergence = 1.0 if ans_logic_density == 0 else 0.5
            
        return convergence, stability

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap factor (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        cap = 1.0
        
        # 1. Presupposition traps
        if re.search(r'\b(have you|did you|why did|when did)\b.*\b(stopped|quit|failed|broke)\b', p_lower):
            cap = min(cap, 0.2)
            
        # 2. Scope/Pronoun Ambiguity (Simplified heuristic)
        if re.search(r'\b(every|all)\b.*\b(a|an)\b', p_lower) and re.search(r'\b(same|different|who|he|she)\b', p_lower):
            cap = min(cap, 0.3)
            
        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bor else\b', p_lower):
            # Check if options are exhaustive (hard to detect, assume risky)
            if re.search(r'\b(true|false|yes|no)\b', p_lower):
                pass # Binary is okay
            else:
                cap = min(cap, 0.4)

        # 4. Subjectivity
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and not re.search(r'\b(objective|fact|data)\b', p_lower):
            cap = min(cap, 0.3)

        # 5. Unanswerability (Missing info indicators)
        if re.search(r'\bwithout knowing\b|\bcannot be determined\b|\binsufficient\b', p_lower):
            cap = min(cap, 0.1)

        return cap

    def _evolve_and_score(self, prompt: str, candidate: str) -> float:
        """Run the evolutionary loop for this specific prompt/candidate pair."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Target vector: Ideally, candidate mirrors prompt's logical structure
        # If prompt has negation, candidate should acknowledge it.
        # Simplified target: High correlation between prompt and candidate features
        target_corr = 1.0 
        if np.sum(p_feat['counts']) == 0:
            target_corr = 0.0 # Empty prompt
            
        best_fitness = -np.inf
        best_W = None
        
        # Evolution Loop
        current_W = self.population_W.copy()
        
        for gen in range(self.n_generations):
            fitnesses = []
            scores = []
            
            for i in range(self.n_population):
                # Compute Score s = W . f_diff (Difference in feature presence)
                # We want the candidate to satisfy the constraints in the prompt
                f_vec = np.abs(p_feat['counts'] - c_feat['counts']) # Penalty for mismatch
                # Invert: lower difference is better
                s = -np.dot(current_W[i], f_vec) 
                
                # Fitness: Accuracy + Criticality (Variance drive)
                # We want weights to be diverse (critical) but accurate
                acc = -np.linalg.norm(f_vec)**2 
                var_term = 0.1 * np.var(current_W[i]) # Encourage non-zero weights
                
                F = acc + var_term
                fitnesses.append(F)
                scores.append(s)
            
            fitnesses = np.array(fitnesses)
            
            # Selection: Keep top K
            top_k_idx = np.argsort(fitnesses)[-self.n_population//2:]
            parents = current_W[top_k_idx]
            
            # Crossover & Mutation (Hebbian-style)
            next_gen = []
            for i in range(self.n_population):
                p1, p2 = parents[i % len(parents)], parents[(i+1) % len(parents)]
                child = (p1 + p2) / 2.0
                
                # Hebbian Update: Strengthen weights where features match
                # If prompt and candidate both have 'negation', increase weight for 'negation'
                match_mask = (p_feat['counts'] > 0) & (c_feat['counts'] > 0)
                if np.any(match_mask):
                    child[match_mask] += 0.1 * (1.0 - child[match_mask]) # Potentiation
                
                # Noise
                child += self.rng.normal(0, 0.05, size=len(child))
                next_gen.append(child)
            
            current_W = np.array(next_gen)
            
            # Track best
            if np.max(fitnesses) > best_fitness:
                best_fitness = np.max(fitnesses)
                best_W = current_W[np.argmax(fitnesses)]

        # Final Score Calculation
        if best_W is None: best_W = current_W[0]
        
        # Normalized structural score
        f_diff = np.abs(p_feat['counts'] - c_feat['counts'])
        raw_score = -np.dot(best_W, f_diff)
        struct_score = 1.0 / (1.0 + np.exp(-raw_score)) # Sigmoid
        
        return struct_score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if min(z1, z2) == 0: return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def _constructive_check(self, prompt: str, candidate: str) -> float:
        """
        Attempt constructive computation for numeric/logic problems.
        Returns 1.0 if candidate matches computed result, 0.0 if contradicts, 0.5 if N/A.
        """
        p_lower = prompt.lower()
        
        # Numeric comparison check
        nums = re.findall(r'\d+\.?\d*', p_lower)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                cand_lower = candidate.lower()
                
                # Check for explicit comparison words in candidate
                if 'greater' in cand_lower or 'more' in cand_lower or 'larger' in cand_lower:
                    return 1.0 if n1 > n2 else 0.0
                if 'less' in cand_lower or 'smaller' in cand_lower:
                    return 1.0 if n1 < n2 else 0.0
                if 'equal' in cand_lower or 'same' in cand_lower:
                    return 1.0 if abs(n1 - n2) < 1e-6 else 0.0
                    
                # If candidate is just a number, check if it's the result of a simple op mentioned
                # (Very basic PEMDAS check for "X + Y" or "X * Y")
                if '+' in prompt:
                    target = str(n1 + n2)
                    if target in candidate: return 1.0
                if '*' in prompt or 'times' in p_lower:
                    target = str(n1 * n2)
                    if target in candidate: return 1.0
            except:
                pass
        return 0.5 # Neutral if no constructive check applies

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-check meta-confidence on the prompt itself
        meta_cap = self._check_meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Evolutionary Score (50%)
            evol_score = self._evolve_and_score(prompt, cand)
            
            # 2. Constructive/Dynamic Score (35%)
            conv, stab = self._compute_dynamics(prompt, cand)
            const_score = self._constructive_check(prompt, cand)
            
            # Combine dynamics and constructive
            dynamic_component = (conv * stab * 0.5) + (const_score * 0.5)
            if const_score == 0.5: # If no constructive check, rely more on dynamics
                dynamic_component = (conv * stab)
            
            # 3. NCD Tiebreaker (15%)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd # Invert so higher is better
            
            # Weighted Sum
            final_score = (0.50 * evol_score) + (0.35 * dynamic_component) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap (Tier B)
            if meta_cap < 0.3:
                final_score *= 0.5 # Penalize heavily if prompt is tricky
            
            # Reasoning String
            reasoning = f"Structural match: {evol_score:.2f}, Dynamics stability: {stab:.2f}, Constructive: {const_score:.2f}"
            if meta_cap < 0.5:
                reasoning += " [WARNING: Potential ambiguity or presupposition detected]"
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Cap (The "Honesty" Filter)
        meta_cap = self._check_meta_confidence(prompt)
        
        # If the prompt is inherently ambiguous/tricky, cap confidence immediately
        if meta_cap < 0.3:
            return meta_cap * 0.9 # Return low confidence
            
        # 2. Compute raw score components
        evol_score = self._evolve_and_score(prompt, answer)
        conv, stab = self._compute_dynamics(prompt, answer)
        const_score = self._constructive_check(prompt, answer)
        
        # 3. Determine base confidence
        # High confidence only if:
        # - High structural match
        # - High stability (robust to reordering)
        # - Constructive check passed (if applicable)
        
        base_conf = 0.0
        if const_score == 1.0:
            base_conf = 0.95 # Definitive computation
        elif const_score == 0.0:
            base_conf = 0.1 # Contradicts computation
        else:
            # Rely on stability and structural fit
            base_conf = (evol_score * 0.4) + (stab * 0.6)
            
        # 4. Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 without constructive proof
        if const_score != 1.0 and final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
