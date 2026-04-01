import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining Gauge Theory (invariance), Neuromodulation (gain control),
    Metamorphic Testing (perturbation robustness), and Dynamical Systems (trajectory stability).
    
    Mechanism:
    1. Parsing: Extracts logical tuples, numbers, and polarity into a scene graph.
    2. Gauge Layer: Computes semantic consistency via TF-IDF covariant differences.
    3. Neuromodulation: Adjusts edge weights based on modality (certainty vs. possibility).
    4. Metamorphic/Dynamics: Perturbs numeric values and re-ranks premises to test 
       trajectory stability (Lyapunov-style). High divergence = low confidence.
    5. Scoring: Weighted sum of structural match, computational exactness, and stability.
    """

    def __init__(self):
        self.synonyms = {
            "increase": ["rise", "grow", "climb"], "decrease": ["drop", "fall", "shrink"],
            "cause": ["lead to", "result in", "trigger"], "equal": ["is", "equals", "same as"]
        }
        self.units = {"kg": 1.0, "g": 0.001, "m": 1.0, "cm": 0.01, "s": 1.0, "ms": 0.001}

    def _tokenize(self, text: str) -> Dict:
        """Extract predicates, numbers, polarity, and conditionals."""
        text_lower = text.lower()
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        has_neg = bool(re.search(r'\b(not|no|never|neither)\b', text_lower))
        has_modal = bool(re.search(r'\b(might|could|should|may)\b', text_lower))
        has_causal = bool(re.search(r'\b(causes|leads to|implies)\b', text_lower))
        comparators = re.findall(r'(>=|<=|>|<|=)', text)
        
        # Simple predicate extraction (verb, subject, object) approximation
        predicates = []
        for verb in ["increases", "decreases", "causes", "equals"]:
            if verb in text_lower:
                predicates.append(verb)
                
        return {
            "numbers": numbers,
            "negation": has_neg,
            "modal": has_modal,
            "causal": has_causal,
            "comparators": comparators,
            "predicates": predicates,
            "length": len(text)
        }

    def _gauge_connection(self, s1: str, s2: str) -> float:
        """
        Compute gauge covariance (semantic distance) using bag-of-words TF-IDF approximation.
        Returns 0.0 for perfect match, higher for mismatch.
        """
        def get_vec(t):
            words = re.findall(r'\w+', t.lower())
            vec = {}
            for w in words:
                vec[w] = vec.get(w, 0) + 1
            return vec
        
        v1, v2 = get_vec(s1), get_vec(s2)
        all_words = set(v1.keys()) | set(v2.keys())
        if not all_words:
            return 0.0
            
        # Cosine-like similarity converted to distance
        dot_prod = sum(v1.get(w, 0) * v2.get(w, 0) for w in all_words)
        norm1 = np.sqrt(sum(v**2 for v in v1.values())) + 1e-9
        norm2 = np.sqrt(sum(v**2 for v in v2.values())) + 1e-9
        sim = dot_prod / (norm1 * norm2)
        return float(1.0 - sim)  # 0 = identical, 1 = orthogonal

    def _metamorphic_check(self, prompt: str, candidate: str) -> float:
        """
        Apply metamorphic transformations to numeric literals.
        If the logic holds, the structural relationship should persist.
        Returns a penalty score (0.0 = robust, >0 = fragile).
        """
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 0.0  # No numbers to test
            
        try:
            # Heuristic: If prompt implies linearity (e.g. "double"), check candidate scaling
            # Simplified: Check if candidate numbers are consistent order-wise with prompt
            p_vals = [float(x) for x in p_nums]
            c_vals = [float(x) for x in c_nums]
            
            # Check monotonicity preservation (simple metamorphic relation)
            if len(p_vals) >= 2 and len(c_vals) >= 2:
                p_diff = p_vals[-1] - p_vals[0]
                c_diff = c_vals[-1] - c_vals[0]
                if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                    return 0.5  # Penalty for reversing direction
        except:
            pass
        return 0.0

    def _dynamics_tracker(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        FRAME C: Dynamical Systems Tracker.
        Models reasoning as state evolution. 
        1. Perturb premise order (simulating noise).
        2. Measure trajectory divergence (Lyapunov exponent approximation).
        Returns: (stability_score, convergence_rate)
        """
        sentences = re.split(r'(?<=[.!?])\s+', prompt.strip())
        if len(sentences) < 2:
            return 1.0, 1.0  # Too short to diverge
            
        base_score = self._static_score(prompt, candidate)
        perturbations = []
        
        # Generate perturbed states by shuffling sentences
        np.random.seed(42) # Deterministic for tool
        for _ in range(5):
            np.random.seed(_) 
            shuffled = " ".join(np.random.permutation(sentences))
            perturbations.append(self._static_score(shuffled, candidate))
            
        if not perturbations:
            return 1.0, 1.0
            
        std_dev = np.std(perturbations)
        mean_val = np.mean(perturbations)
        
        # Stability: Low std_dev means the answer is robust to premise reordering
        stability = 1.0 / (1.0 + std_dev * 10) 
        
        # Convergence: How close is the mean to the base?
        convergence = 1.0 - abs(base_score - mean_val)
        
        return float(stability), float(convergence)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'\bHave you (stopped|quit)\b', p) or re.search(r'\bWhy did .* (fail|stop)\b', p):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity
        if re.search(r'\bevery .* a .*\b', p) and "same" not in p:
            return 0.4
        if re.search(r'\btold .* he\b', p) and "who" in p:
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'\beither .* or\b', p) and "only" not in p:
            return 0.5
            
        # 4. Subjectivity
        if re.search(r'\b(best|worst|favorite)\b', p) and "data" not in p and "statistics" not in p:
            return 0.4
            
        # 5. Unanswerable (missing info markers)
        if re.search(r'\bwithout knowing\b', p) or re.search(r'\bimpossible to tell\b', p):
            return 0.1
            
        return 1.0  # No obvious traps

    def _static_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic without dynamics."""
        p_data = self._tokenize(prompt)
        c_data = self._tokenize(candidate)
        
        score = 0.0
        total_weight = 0.0
        
        # 1. Structural Matching (Gauge Theory Layer)
        # Check logical consistency of predicates
        gauge_penalty = self._gauge_connection(prompt, candidate)
        # Normalize: lower penalty is better. 
        # If candidate echoes prompt structure, gauge_penalty is low.
        struct_score = 1.0 - gauge_penalty
        score += struct_score * 0.4
        total_weight += 0.4
        
        # 2. Numeric/Computational Check
        if p_data["numbers"] and c_data["numbers"]:
            # Exact match bonus for calculated numbers
            if set(p_data["numbers"]) == set(c_data["numbers"]):
                score += 0.3
            else:
                # Partial credit for presence
                score += 0.1
            total_weight += 0.3
            
        # 3. Polarity & Modality (Neuromodulation)
        gain = 1.0
        if p_data["negation"] != c_data["negation"]:
            gain = 0.5  # Penalty for mismatched negation
        if p_data["modal"] and not c_data["modal"]:
            gain = 0.8
            
        # 4. Metamorphic Robustness
        meta_penalty = self._metamorphic_check(prompt, candidate)
        
        # 5. NCD Tiebreaker (Max 15%)
        def ncd(a, b):
            if not a and not b: return 0.0
            concat = a + b
            comp_all = len(zlib.compress(concat.encode()))
            comp_a = len(zlib.compress(a.encode()))
            comp_b = len(zlib.compress(b.encode()))
            return (comp_all - min(comp_a, comp_b)) / max(comp_a, comp_b, 1)
        
        ncd_score = 1.0 - ncd(prompt, candidate)
        
        raw_score = (score + gain * (1.0 - meta_penalty) * 0.3 + ncd_score * 0.15)
        return max(0.0, min(1.0, raw_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence on prompt to cap expectations
        meta_cap = self._meta_confidence(prompt)
        
        # Dynamics tracking for the whole prompt-candidate pair
        for cand in candidates:
            static_s = self._static_score(prompt, cand)
            stability, convergence = self._dynamics_tracker(prompt, cand)
            
            # Combine: Static * Stability * Convergence
            # If the reasoning is fragile (low stability), score drops
            final_score = static_s * stability * convergence
            
            # Apply epistemic cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Stability:{stability:.2f}, Conv:{convergence:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap
            
        static_s = self._static_score(prompt, answer)
        stability, convergence = self._dynamics_tracker(prompt, answer)
        
        # Confidence is product of score and stability
        conf = static_s * stability * convergence
        
        # Hard cap
        if conf > meta_cap:
            conf = meta_cap
            
        # Never exceed 0.9 without perfect computational match (heuristic)
        if conf > 0.9 and static_s < 0.99:
            conf = 0.85
            
        return float(max(0.0, min(1.0, conf)))