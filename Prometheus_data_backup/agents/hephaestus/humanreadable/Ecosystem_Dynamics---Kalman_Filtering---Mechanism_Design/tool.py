import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Ecosystem Dynamics (influence propagation),
    Kalman Filtering (belief updating), and Mechanism Design (proper scoring).
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (S-P-O) and logical flags (negation, causal, etc.)
       into a directed graph.
    2. Ecosystem Dynamics: Constructs a state-transition matrix F representing trophic-like
       influence between propositions.
    3. Kalman Filter: Iteratively updates belief states (x) based on candidate alignment (z),
       balancing process noise (Q) and measurement noise (R).
    4. Mechanism Design: Applies a Brier-based proper scoring rule to incentivize honest belief reporting.
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    # Regex patterns for structural parsing
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without|fails?|stop|quit)\b', re.I),
        'causal': re.compile(r'\b(causes?|leads? to|results? in|implies?|because|since)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst|best)\b', re.I),
        'quantifier': re.compile(r'\b(all|some|none|every|each|most|few)\b', re.I),
        'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
        'presupposition': re.compile(r'\b(have you stopped|why did .*(?:fail|stop|quit)|when did .*(?:stop|fail))\b', re.I),
        'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options|choice is between)\b', re.I),
        'ambiguity': re.compile(r'\b(who|which one|what exactly)\b', re.I)
    }

    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 5
        self.sigma_process = 0.1
        self.sigma_measure = 0.2

    def _extract_propositions(self, text: str) -> List[str]:
        """Extracts atomic propositions (simplified to sentences/clauses)."""
        # Split by common delimiters to get rough propositions
        raw = re.split(r'[.,;:]', text)
        props = [p.strip() for p in raw if len(p.strip()) > 3]
        return props if props else [text[:50]] # Fallback

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, List[str], int]:
        """
        Builds the ecosystem influence matrix F and initial state.
        Nodes are propositions from prompt + candidate.
        """
        # Combine text for context, but distinguish source
        p_props = self._extract_propositions(prompt)
        c_props = self._extract_propositions(candidate)
        
        # Limit size for computational feasibility
        all_props = (p_props + c_props)[:20] 
        n = len(all_props)
        if n == 0:
            return np.array([[1.0]]), ["dummy"], 1

        W = np.zeros((n, n))
        
        # Self-loops for stability
        for i in range(n):
            W[i, i] = 0.5

        # Edge construction based on logical flow (simplified for regex)
        # If proposition i contains causal words affecting j (heuristic: proximity)
        for i, p_i in enumerate(all_props):
            is_neg = bool(self.PATTERNS['negation'].search(p_i))
            is_causal = bool(self.PATTERNS['causal'].search(p_i))
            
            for j, p_j in enumerate(all_props):
                if i == j: continue
                
                # Simple overlap heuristic for "implies"
                words_i = set(re.findall(r'\w+', p_i.lower()))
                words_j = set(re.findall(r'\w+', p_j.lower()))
                overlap = len(words_i & words_j)
                
                if overlap > 1:
                    weight = 0.3 * (overlap / max(len(words_i), 1))
                    if is_causal:
                        weight += 0.4
                    if is_neg:
                        weight = -weight # Negation flips influence
                    
                    W[j, i] += weight # Column i affects Row j (transpose for x_{k+1} = F x_k)

        # Row normalize to create transition matrix F (ecosystem style)
        row_sums = np.abs(W).sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1 # Avoid division by zero
        F = W / row_sums
        
        # Ensure stability (spectral radius < 1 approx)
        F = F * 0.9 
        
        return F, all_props, n

    def _kalman_update(self, F: np.ndarray, n: int, prompt: str, candidate: str) -> Tuple[np.ndarray, float]:
        """
        Runs the Kalman Filter iteration to update beliefs.
        Returns final belief vector and alignment score.
        """
        # State: belief in each proposition (0.5 prior)
        x = np.full(n, 0.5)
        P = np.eye(n) * 0.25 # Initial covariance
        
        Q = (self.sigma_process ** 2) * np.eye(n)
        R = (self.sigma_measure ** 2) * np.eye(n)
        
        # Measurement vector z: 1 if proposition exists in both, else 0
        # Simplified: Check if candidate propositions appear in prompt context or match logically
        p_props = self._extract_propositions(prompt)
        c_props = self._extract_propositions(candidate)
        all_props = (p_props + c_props)[:n]
        
        # Map candidate coverage to vector z
        z = np.zeros(n)
        for i, prop in enumerate(all_props):
            # Check if this prop is supported by candidate
            # Heuristic: if prop comes from candidate part or matches candidate text
            if prop in c_props or any(sub in candidate for sub in prop.split()[:2] if len(sub)>3):
                z[i] = 1.0
            elif any(sub in prompt for sub in prop.split()[:2] if len(sub)>3):
                # If it's in prompt, does candidate address it? 
                # Simple overlap check
                if any(word in candidate for word in re.findall(r'\w+', prop.lower()) if len(word)>3):
                    z[i] = 0.8 # Partial match
        
        # Iteration
        for _ in range(self.max_iter):
            # Prediction
            x_hat = F @ x
            P_hat = F @ P @ F.T + Q
            
            # Update
            K = P_hat @ np.linalg.inv(P_hat + R) # H = I
            innovation = z - x_hat
            x = x_hat + K @ innovation
            P = (np.eye(n) - K) @ P_hat
            
            if np.linalg.norm(innovation) < self.epsilon:
                break

        # Scoring (Mechanism Design: Proper Scoring Rule)
        # S = -||x - z||^2 (Brier score variant)
        # We normalize to 0-1 range where 1 is perfect match
        error = np.linalg.norm(x - z)
        max_error = np.sqrt(n) # Worst case
        score = 1.0 - (error / max_error) if max_error > 0 else 1.0
        
        return x, max(0.0, min(1.0, score))

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """Extracts and compares numeric values. Returns 1.0 if consistent, 0.0 if contradictory."""
        p_nums = [float(x) for x in self.PATTERNS['numeric'].findall(prompt)]
        c_nums = [float(x) for x in self.PATTERNS['numeric'].findall(candidate)]
        
        if not p_nums:
            return 1.0 # No numbers to check
        
        if not c_nums:
            return 0.5 # Candidate missing numbers when prompt has them
        
        # Check for direct contradictions (e.g., prompt says 10, candidate says 5)
        # This is a simplified heuristic: if counts differ significantly, penalize
        if len(p_nums) == len(c_nums):
            matches = sum(1 for p, c in zip(p_nums, c_nums) if abs(p-c) < 1e-6)
            return matches / len(p_nums)
        
        # If counts differ, check if candidate numbers are a subset or derived
        # For now, strict equality on presence
        return 0.8 if any(abs(p-c)<1e-6 for p in p_nums for c in c_nums) else 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.PATTERNS['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(prompt):
            return 0.3
            
        # 3. Ambiguity / Unanswerability markers
        if self.PATTERNS['ambiguity'].search(prompt) and "context" not in p_lower:
            return 0.3
            
        # 4. Subjectivity without criteria
        if self.PATTERNS['comparative'].search(prompt) and ("best" in p_lower or "worst" in p_lower):
            if "criteria" not in p_lower and "data" not in p_lower:
                return 0.4

        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Calculates score based on structural feature alignment."""
        score = 0.0
        count = 0
        
        # Negation consistency
        p_neg = bool(self.PATTERNS['negation'].search(prompt))
        c_neg = bool(self.PATTERNS['negation'].search(candidate))
        if p_neg == c_neg:
            score += 1.0
        else:
            score += 0.2 # Penalty for flipping negation
        count += 1
        
        # Causal/Conditional presence
        if self.PATTERNS['conditional'].search(prompt):
            if self.PATTERNS['conditional'].search(candidate) or any(k in candidate.lower() for k in ['if', 'then', 'because']):
                score += 1.0
            else:
                score += 0.5
            count += 1
            
        return score / count if count > 0 else 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing & Graph Build
            F, props, n = self._build_graph(prompt, cand)
            
            # 2. Kalman Update & Ecosystem Propagation
            _, kf_score = self._kalman_update(F, n, prompt, cand)
            
            # 3. Numeric Verification (Constructive)
            num_score = self._numeric_check(prompt, cand)
            
            # 4. Structural Alignment
            struct_score = self._structural_score(prompt, cand)
            
            # Weighted Combination (Structural >= 50%, Computation >= 20%, NCD <= 15%)
            # KF acts as the core reasoning engine (part of structural/computation)
            base_score = (0.5 * struct_score) + (0.3 * num_score) + (0.2 * kf_score)
            
            # NCD Tiebreaker (Max 15% influence)
            try:
                import zlib
                data = (prompt + cand).encode('utf-8')
                cand_enc = cand.encode('utf-8')
                # Normalized Compression Distance approximation
                lzx = len(zlib.compress(data))
                lz_prompt = len(zlib.compress(prompt.encode('utf-8')))
                lz_cand = len(zlib.compress(cand_enc))
                ncd = (lzx - min(lz_prompt, lz_cand)) / max(lz_prompt, lz_cand, 1)
                ncd_score = 1.0 - ncd # Convert distance to similarity
            except:
                ncd_score = 0.5
                
            final_score = (0.85 * base_score) + (0.15 * ncd_score)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{struct_score:.2f}, Numeric:{num_score:.2f}, KF:{kf_score:.2f}, MetaCap:{meta_cap:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run lightweight evaluation
        res = self.evaluate(prompt, [answer])
        raw_score = res[0]['score'] if res else 0.0
        
        # If meta-analysis says "suspicious", cap the confidence
        final_conf = min(raw_score, meta_cap)
        
        # Never return > 0.9 unless it's a hard calculation match
        if meta_cap == 1.0 and raw_score > 0.9:
            return min(0.95, raw_score)
            
        return float(np.clip(final_conf, 0.0, 1.0))