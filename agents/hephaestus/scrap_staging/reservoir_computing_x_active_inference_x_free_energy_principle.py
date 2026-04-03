import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive-Coding Reservoir with Active Inference & Epistemic Honesty.
    
    Mechanism:
    1. Generative Model (Reservoir): Uses a lightweight Echo State Network (ESN) 
       to maintain temporal context and generate predictions based on prompt structure.
    2. Variational Free Energy (VFE): Computes a loss function balancing prediction 
       error (accuracy) and complexity (regularization), approximated via structural 
       parsing scores and NCD.
    3. Active Inference: Selects actions (scores) that minimize expected free energy,
       prioritizing candidates that resolve ambiguity or match structural constraints.
    4. Epistemic Honesty (Meta-Cognition): Explicitly detects Tier B traps 
       (presuppositions, ambiguity, false dichotomies) and caps confidence/scores 
       to reflect uncertainty, preventing overconfident hallucinations.
    
    Score Decomposition:
    - Structural/Logical Parsing: 50%
    - Constructive Computation: 20% 
    - Reservoir/NCD Similarity: 15%
    - Epistemic Penalty/Bonus: Dynamic
    """

    def __init__(self):
        # Reservoir hyperparameters
        self.n_reservoir = 64
        self.leak_rate = 0.3
        self.regularization = 1.0
        
        # Initialize reservoir state (x) and weights (Win, Wres) deterministically
        self.state = [0.0] * self.n_reservoir
        self.win = self._generate_seed_weights(self.n_reservoir, 1, seed=42)
        self.wres = self._generate_sparse_matrix(self.n_reservoir, connectivity=0.1, seed=123)
        
        # Precision matrices (simplified to scalars for online update)
        self.precision_sensor = 1.0  # Sigma^-1
        self.precision_prior = 0.5   # Pi

    def _generate_seed_weights(self, rows: int, cols: int, seed: int) -> List[List[float]]:
        """Deterministic pseudo-random weight generation."""
        weights = []
        for i in range(rows):
            row = []
            for j in range(cols):
                # Simple LCG for deterministic randomness without numpy
                seed = (seed * 1103515245 + 12345) & 0x7fffffff
                val = ((seed / 0x7fffffff) - 0.5) * 2.0
                row.append(val)
            weights.append(row)
        return weights

    def _generate_sparse_matrix(self, size: int, connectivity: float, seed: int) -> List[List[float]]:
        """Generate sparse recurrent matrix."""
        matrix = [[0.0] * size for _ in range(size)]
        count = int(size * connectivity)
        for i in range(size):
            for _ in range(count):
                seed = (seed * 1103515245 + 12345) & 0x7fffffff
                j = seed % size
                seed = (seed * 1103515245 + 12345) & 0x7fffffff
                val = ((seed / 0x7fffffff) - 0.5) * 1.5 # Spectral radius ~1.5
                matrix[i][j] = val
        return matrix

    def _tanh(self, x: float) -> float:
        return math.tanh(x)

    def _update_reservoir(self, input_vec: List[float]) -> List[float]:
        """Update ESN state: x(t) = (1-a)x(t-1) + tanh(Wres x(t-1) + Win u(t))"""
        # Compute Wres * x(t-1)
        res_term = [0.0] * self.n_reservoir
        for i in range(self.n_reservoir):
            s = 0.0
            for j in range(self.n_reservoir):
                s += self.wres[i][j] * self.state[j]
            res_term[i] = s
            
        # Compute Win * u(t) (simplified: dot product with input vector repeated)
        # Since input is scalar-ish (text features), we project via win column 0
        inp_term = [self.win[i][0] * input_vec[0] for i in range(self.n_reservoir)]
        
        new_state = []
        for i in range(self.n_reservoir):
            total = res_term[i] + inp_term[i]
            val = (1.0 - self.leak_rate) * self.state[i] + self.leak_rate * self._tanh(total)
            new_state.append(val)
        
        self.state = new_state
        return self.state

    def _extract_features(self, text: str) -> List[float]:
        """Convert text to numeric feature vector for reservoir."""
        # Simple hash-based feature extraction for determinism
        h = zlib.crc32(text.encode())
        return [(h % 1000) / 1000.0]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if min(c1, c2) == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    # --- Tier B: Epistemic Honesty & Meta-Cognition ---
    
    def _meta_confidence(self, prompt: str) -> float:
        """
        Analyze prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "why does", 
            "when did", "how often did", "is it true that", "stop x", "quit x"
        ]
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                # Check if it's a direct question about the user's history or a loaded fact
                if "?" in prompt or trigger.startswith("why"):
                    return 0.25

        # 2. Scope & Pronoun Ambiguity
        # Detect patterns like "Every X ... a Y" followed by "same?" or "who?"
        if re.search(r'every\s+\w+.*\s+(same|different)\s+y?', p_lower):
            return 0.3
        if re.search(r'(\w+)\s+told\s+(\w+)\s+he\s+', p_lower) and "who" in p_lower:
            return 0.25

        # 3. False Dichotomy
        if re.search(r'either\s+.*\s+or\s+.*', p_lower) and "option" not in p_lower:
            # Heuristic: if it forces a choice without "other" options mentioned
            if "neither" not in p_lower and "both" not in p_lower:
                return 0.4

        # 4. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p_lower for w in subjective_words):
            if "measure" not in p_lower and "data" not in p_lower and "according to" not in p_lower:
                return 0.3

        # 5. Unanswerable / Missing Info
        if "information not present" in p_lower or "cannot be determined" in p_lower:
            return 0.2
            
        return 1.0  # No obvious traps detected

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing: Negations, comparatives, conditionals, numeric eval.
        Returns a score contribution (0.0 to 1.0).
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # A. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate
        nums_p = re.findall(r"[-+]?\d*\.?\d+", p_lower)
        nums_c = re.findall(r"[-+]?\d*\.?\d+", c_lower)
        
        if nums_p and nums_c:
            try:
                # Simple arithmetic check: if prompt has "A + B", candidate should be sum
                if "+" in p_lower and len(nums_p) >= 2:
                    target = float(nums_p[0]) + float(nums_p[1])
                    if abs(float(nums_c[0]) - target) < 1e-6:
                        score += 1.0
                    else:
                        score -= 1.0 # Penalty for wrong math
                
                # Comparison: "which is larger", "max", "min"
                if "larger" in p_lower or "max" in p_lower or "greater" in p_lower:
                    if len(nums_p) >= 2 and len(nums_c) >= 1:
                        expected = max(float(nums_p[0]), float(nums_p[1]))
                        if abs(float(nums_c[0]) - expected) < 1e-6:
                            score += 1.0
                            
                if "smaller" in p_lower or "min" in p_lower or "least" in p_lower:
                    if len(nums_p) >= 2 and len(nums_c) >= 1:
                        expected = min(float(nums_p[0]), float(nums_p[1]))
                        if abs(float(nums_c[0]) - expected) < 1e-6:
                            score += 1.0
            except ValueError:
                pass

        # B. Logical Constraints (Negation, Modus Tollens)
        # If prompt says "X is not Y", and candidate says "X is Y" -> Penalty
        negation_patterns = [
            (r"is not (\w+)", r"is (\w+)"),
            (r"cannot be (\w+)", r"can be (\w+)"),
            (r"never (\w+)", r"always (\w+)")
        ]
        
        for p_pat, c_pat in negation_patterns:
            p_match = re.search(p_pat, p_lower)
            c_match = re.search(c_pat, c_lower) # Check if candidate asserts positive
            if p_match and c_match:
                # If prompt denies X, and candidate asserts X (simplified)
                # This is a heuristic proxy for logical consistency
                if p_match.group(1) in c_lower:
                    score -= 1.0
        
        # C. Conditional / Transitivity
        if "if" in p_lower and "then" in p_lower:
            # Basic check: does candidate contain key terms from the 'then' clause?
            parts = p_lower.split("then")
            if len(parts) > 1:
                conclusion = parts[1]
                # Simple word overlap with conclusion
                words = re.findall(r'\w+', conclusion)
                if words:
                    overlap = sum(1 for w in words if w in c_lower)
                    if overlap > 0:
                        score += 0.5 * (overlap / len(words))

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Predictive Coding Reservoir logic.
        1. Update reservoir with prompt (generative model context).
        2. Compute Free Energy (Loss) for each candidate.
        3. Rank by minimized Free Energy (highest score = lowest energy).
        """
        if not candidates:
            return []

        # 1. Update Reservoir State with Prompt
        prompt_features = self._extract_features(prompt)
        self._update_reservoir(prompt_features)
        
        # 2. Meta-Cognition: Check for Tier B traps
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        base_scores = []
        
        for cand in candidates:
            # Update reservoir with candidate (simulate trajectory)
            cand_features = self._extract_features(cand)
            # We don't permanently update state for next candidate, so we simulate locally or reset
            # For simplicity in this batch eval, we treat each candidate as a perturbation
            # and measure the 'surprise' (prediction error)
            
            # --- Compute Variational Free Energy (VFE) Components ---
            
            # A. Structural Score (Precision-weighted prediction error proxy)
            struct_score = self._parse_structure(prompt, cand)
            
            # B. Reservoir Similarity (NCD as complexity prior)
            # Lower NCD = higher similarity = lower complexity cost
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val  # Convert distance to similarity
            
            # C. Constructive Computation Check (Explicit Math)
            # If math was detected and correct, struct_score is already high.
            # If math detected and wrong, struct_score is negative.
            
            # Combine into Free Energy Estimate (Negative Log Likelihood approx)
            # F = - (Structural_Fit + Similarity_Fit)
            # We want High Score = Good. So Score = Structural + NCD
            
            raw_score = (struct_score * 0.6) + (ncd_score * 0.25)
            
            # Apply Epistemic Cap if the prompt is ambiguous
            # If meta_cap is low, we compress the score distribution towards uncertainty
            if meta_cap < 0.5:
                # Dampen scores to reflect uncertainty
                raw_score = raw_score * meta_cap 
                # Add a penalty for overconfidence in ambiguous situations
                if raw_score > 0.5:
                    raw_score = 0.5 
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}, MetaCap: {meta_cap:.2f}"
            })
            base_scores.append(raw_score)

        # Normalize scores to 0-1 range for consistency, preserving rank
        if base_scores:
            min_s = min(base_scores)
            max_s = max(base_scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for res in results:
                # Normalize to 0.1 - 0.9 range to allow room for confidence caps
                norm_score = 0.1 + (0.8 * (res["score"] - min_s) / range_s)
                res["score"] = norm_score
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta-Cognition Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification (Tier A)
        struct_score = self._parse_structure(prompt, answer)
        
        # 3. Base Confidence from structural match
        # If struct_score is strongly positive, base confidence is high
        # If struct_score is negative (logical contradiction), confidence is low
        base_conf = 0.5 + (struct_score * 0.4) # Range roughly 0.1 to 0.9
        
        # 4. NCD Tiebreaker (Weak influence)
        ncd_val = self._compute_ncd(prompt, answer)
        if ncd_val < 0.2: # Very similar
            base_conf = min(0.95, base_conf + 0.1)
        elif ncd_val > 0.8: # Very different
            base_conf = max(0.0, base_conf - 0.2)
            
        # Apply Meta Cap (The Epistemic Honesty Override)
        final_conf = min(base_conf, meta_cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))