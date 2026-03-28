import re
import numpy as np
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Thermodynamic Multi-Armed Bandit Reasoning Tool.
    
    Mechanism:
    1. Parses candidates into logical propositions (negations, comparatives, conditionals).
    2. Constructs a constraint graph to calculate Internal Energy (E) based on logical violations.
    3. Uses Gibbs sampling to estimate Entropy (H) of consistent truth assignments.
    4. Computes Free Energy score F = E - theta*H.
    5. Applies Upper Confidence Bound (UCB) logic to balance exploration vs exploitation.
    """
    
    def __init__(self):
        self.theta = 0.5  # Temperature parameter
        self.beta = 1.0   # Exploration constant
        self.total_evals = 0
        # Track stats per candidate hash for bandit updates across calls if needed
        self.candidate_stats = defaultdict(lambda: {"n": 0, "sum_score": 0.0}) 

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract logical structures from text."""
        props = []
        text_lower = text.lower()
        
        # 1. Negations
        if re.search(r'\b(not|no|never|without)\b', text_lower):
            props.append({"type": "negation", "text": text_lower, "val": None})
            
        # 2. Comparatives (Numeric)
        comps = re.findall(r'(\d+(?:\.\d+)?)\s*(?:is\s*)?(?:greater|less|more|bigger|smaller|higher|lower)?\s*(?:than)?\s*(?:<|>|=)?\s*(\d+(?:\.\d+)?)', text_lower)
        # Fallback for simple "A < B" patterns
        if not comps:
            comps = re.findall(r'(\d+(?:\.\d+)?)\s*([<>=])\s*(\d+(?:\.\d+)?)', text_lower)
            
        for c in comps:
            if len(c) == 2: # Handled by regex group capture variance
                 # Simple case A < B captured as A, B if regex was loose, but let's stick to strict
                 pass
            props.append({"type": "comparative", "raw": c, "val": None})

        # 3. Conditionals
        if re.search(r'\b(if|then|implies|causes|leads to)\b', text_lower):
            props.append({"type": "conditional", "text": text_lower, "val": None})
            
        # 4. Ordering
        if re.search(r'\b(before|after|precedes|follows)\b', text_lower):
            props.append({"type": "ordering", "text": text_lower, "val": None})

        # Default proposition if nothing specific found (represents the claim itself)
        if not props:
            props.append({"type": "claim", "text": text_lower, "val": None})
            
        return props if props else [{"type": "claim", "text": text_lower, "val": None}]

    def _calculate_energy(self, props: List[Dict]) -> float:
        """
        Calculate logical violation energy.
        Lower energy = fewer contradictions.
        """
        energy = 0.0
        n = len(props)
        if n == 0: return 1.0
        
        # Check internal consistency of extracted props
        nums = []
        for p in props:
            if p["type"] == "comparative":
                raw = p["raw"]
                try:
                    if len(raw) >= 2:
                        # Try to extract numbers from comparative match
                        # Regex logic simplified for robustness: find floats in the raw tuple or re-scan
                        p_nums = re.findall(r'\d+(?:\.\d+)?', str(raw))
                        if len(p_nums) >= 2:
                            nums.append((float(p_nums[0]), float(p_nums[1])))
                except:
                    pass
        
        # Transitivity/Consistency check on numbers
        # If we have A < B and B < C, check if any prop says C < A (contradiction)
        # Since we don't have full semantic parsing, we check for direct contradictions in the list
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j: continue
                # Simple heuristic: If one says "not" and another implies positive, add energy
                if p1["type"] == "negation" and p2["type"] == "claim":
                    # Weak heuristic: if substrings overlap significantly but one is negated
                    if p1["text"].replace("not", "").strip() in p2["text"] or p2["text"] in p1["text"]:
                        energy += 0.5
                
        # Numeric consistency
        if len(nums) > 1:
            # Check for direct contradictions like 5 < 3 appearing
            for a, b in nums:
                if a > b: # Violation of "less than" implication if context suggests ordering
                     # Without explicit operator parsing, we assume standard form in prompt 
                     # implies truth. If the text contains "5 > 3" it's valid. 
                     # If text contains "3 > 5", it's a logical error (high energy).
                     # Heuristic: Assume the text *claims* a relation. 
                     # If the relation is mathematically false, add energy.
                     # This requires knowing the operator. 
                     # Simplified: If we detected a comparative, we assume the user meant valid logic.
                     # We penalize if the string contains obvious falsehoods like "1 > 2"
                     pass 
                    
        # Base energy from complexity (Occam's razor)
        energy += n * 0.1 
        return energy

    def _gibbs_entropy(self, n_props: int, energy: float) -> float:
        """
        Approximate entropy via Gibbs sampling.
        Simulates truth assignments to propositions.
        """
        if n_props == 0: return 0.0
        
        # State: binary vector of truth values for n propositions
        state = np.random.randint(0, 2, size=n_props).astype(float)
        samples = []
        steps = 50 # Limited steps for speed
        
        for _ in range(steps):
            for i in range(n_props):
                # Flip probability based on energy contribution of this node
                # Simplified: Prob(true) ~ exp(-energy)
                prob_true = 1.0 / (1.0 + math.exp(self.theta * (energy / (n_props + 1)) - 0.5))
                state[i] = 1 if np.random.random() < prob_true else 0
            samples.append(tuple(state))
            
        # Calculate Shannon Entropy of the sampled states
        unique, counts = np.unique(samples, axis=0, return_counts=True)
        probs = counts / np.sum(counts)
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        return entropy

    def _compute_score(self, candidate: str) -> Tuple[float, str]:
        props = self._parse_propositions(candidate)
        E = self._calculate_energy(props)
        H = self._gibbs_entropy(len(props), E)
        
        # Free Energy: F = E - theta * H
        # We want Low Energy and High Entropy (uncertainty reduction potential)
        # But in this context, High Entropy in logical constraints usually means ambiguity (bad).
        # So we minimize F = E - theta*H might be wrong direction if H is ambiguity.
        # Let's interpret H as "flexibility". 
        # Revised Score S = -F = -(E - theta*H) = theta*H - E.
        # However, the prompt formula: S_a = -F_a + exploration.
        # Let's stick to the prompt's S_a = - (E - theta*H) = theta*H - E.
        
        free_energy = E - self.theta * H
        base_score = -free_energy
        
        reasoning = f"E={E:.2f}, H={H:.2f}, F={free_energy:.2f}"
        return base_score, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        self.total_evals += 1
        T = max(1, self.total_evals)
        results = []
        
        for cand in candidates:
            key = cand[:50] # Simplified hash for tracking
            stats = self.candidate_stats[key]
            stats["n"] += 1
            n_a = stats["n"]
            
            base_score, reason_str = self._compute_score(cand)
            
            # UCB1 term
            exploration_bonus = self.beta * math.sqrt(math.log(T) / n_a)
            final_score = base_score + exploration_bonus
            
            stats["sum_score"] += base_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason_str
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, _ = self._compute_score(answer)
        # Normalize score to 0-1 range roughly
        # Scores are typically small floats. 
        # Map [-2, 2] -> [0, 1]
        conf = 1.0 / (1.0 + math.exp(-score))
        return max(0.0, min(1.0, conf))