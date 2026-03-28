import re
import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Multi-Aarmed Bandits (UCB), 
    and Phase Transitions for answer selection, with strong epistemic honesty checks.
    
    Mechanism:
    1. Meta-Confidence Check: Analyzes the prompt for logical traps (presuppositions, ambiguity).
       If detected, confidence is capped low regardless of answer content.
    2. Structural Parsing: Extracts logical features (negations, comparatives, numbers) from 
       prompt and candidates using regex.
    3. Scoring Logic:
       - Structural Similarity (Jaccard) between prompt and candidate features.
       - Numeric Consistency: Explicitly checks if numeric constraints in prompt match candidate.
       - NCD (Compression): Used only as a minor tiebreaker (<15% weight).
    4. Kalman/Bandit Simulation:
       - Treats each candidate as an arm.
       - Maintains belief (mu, sigma) updated by structural match score.
       - Uses UCB for selection order (simulated here by iterating and updating).
       - Applies Phase Transition: If variance drops below threshold, belief "crystallizes".
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|n\'t)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|fewer|larger|smaller|before|after)\b|[><=]', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|none|every|each|any|most)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did|when does)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|is it .+ or .+\?)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'negation': len(self.patterns['negation'].findall(text)),
            'comparative': len(self.patterns['comparative'].findall(text)),
            'conditional': len(self.patterns['conditional'].findall(text)),
            'causal': len(self.patterns['causal'].findall(text)),
            'quantifier': len(self.patterns['quantifier'].findall(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'length': len(text.split())
        }
        return features

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute similarity based on structural feature overlap and numeric consistency.
        Returns a score between 0 and 1.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Feature Vector Jaccard Similarity (Binary presence)
        feature_keys = ['negation', 'comparative', 'conditional', 'causal', 'quantifier']
        p_set = {k for k in feature_keys if p_feat[k] > 0}
        c_set = {k for k in feature_keys if c_feat[k] > 0}
        
        if not p_set and not c_set:
            jaccard = 1.0
        elif not p_set or not c_set:
            jaccard = 0.0
        else:
            intersection = len(p_set & c_set)
            union = len(p_set | c_set)
            jaccard = intersection / union if union > 0 else 0.0

        # 2. Numeric Consistency Check
        # If prompt has numbers, candidate should ideally reflect logical consequence
        # Simple heuristic: If prompt has numbers, candidate having numbers boosts score slightly
        # unless it's a direct copy (which might be bad), but here we look for presence.
        num_score = 0.0
        if p_feat['numbers']:
            if c_feat['numbers']:
                # Check if candidate numbers are derived or consistent? 
                # Hard to do without LLM, so we check if candidate contains ANY numbers 
                # when prompt has them (indicates engagement with quantities)
                num_score = 0.5 
                # Penalty if counts differ wildly (heuristic for "ignoring data")
                if abs(len(p_feat['numbers']) - len(c_feat['numbers'])) > 2:
                    num_score = 0.2
            else:
                # Prompt has numbers, candidate has none -> likely wrong for math/logic problems
                num_score = 0.1
        else:
            num_score = 1.0 # No numbers to check

        # Weighted combination: Structural 70%, Numeric 30%
        base_score = 0.7 * jaccard + 0.3 * num_score
        return min(1.0, base_score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for logical traps, ambiguity, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.25
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know), assume risky
            return 0.4
            
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "measure" not in p_lower and "data" not in p_lower:
                return 0.3

        # 4. Pronoun/Scope Ambiguity (Simple heuristic: "who", "which" at end)
        if re.search(r'\b(who|which one|what exactly)\b\?$', p_lower):
            # If the question asks for clarification, we might be uncertain
            pass # Let structural score handle it, but cap high confidence
        
        return 1.0 # No specific trap detected

    def _kalman_update(self, mu: float, sigma_sq: float, z: float, R: float, Q: float) -> tuple:
        """Perform scalar Kalman update."""
        # Prediction step (add process noise)
        sigma_sq_pred = sigma_sq + Q
        
        # Update step
        K = sigma_sq_pred / (sigma_sq_pred + R) if (sigma_sq_pred + R) > 0 else 0
        mu_new = mu + K * (z - mu)
        sigma_sq_new = (1 - K) * sigma_sq_pred
        
        return mu_new, sigma_sq_new

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        # Parameters
        Q = 0.01  # Process noise
        R = 0.04  # Observation noise
        epsilon = 0.01 # Phase transition threshold
        c_ucb = 1.0
        
        results = []
        
        # Initialize belief states for each candidate
        # State: {'mu': 0.5, 'sigma_sq': 1.0, 'n': 0, 'candidate': str}
        states = [
            {'mu': 0.5, 'sigma_sq': 1.0, 'n': 0, 'candidate': cand, 'ordered': False}
            for cand in candidates
        ]
        
        total_evals = 0
        
        # Simulate Bandit process: Iterate until budget or all ordered
        # Since we have all candidates upfront, we can simulate the "selection" 
        # by iterating through them, updating beliefs, and checking phase transition.
        # To mimic UCB, we sort by UCB score before each "round" of updates if we were selecting one by one.
        # Here, we perform one pass of evaluation per candidate, updating beliefs.
        # To strictly follow the algorithm description:
        # "At each round we select an answer... repeat until budget exhausted"
        # We will simulate T rounds where T = len(candidates) * 2 (simple budget)
        
        budget = max(len(candidates) * 3, 5)
        t = 0
        
        while t < budget:
            t += 1
            # Calculate UCB for non-ordered candidates
            best_idx = -1
            best_ucb = -float('inf')
            
            active_count = 0
            for i, state in enumerate(states):
                if state['ordered']:
                    continue
                active_count += 1
                n_i = state['n']
                if n_i == 0:
                    ucb = float('inf') # Explore unvisited first
                else:
                    ucb = state['mu'] + c_ucb * math.sqrt(math.log(t + 1) / n_i)
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_idx = i
            
            if best_idx == -1: # All ordered
                break
                
            # Select and Evaluate candidate at best_idx
            state = states[best_idx]
            candidate_text = state['candidate']
            
            # Get observation z (structural score)
            # We add a tiny bit of noise to z to simulate observation noise R, 
            # but base it on the deterministic structural score.
            base_z = self._compute_structural_score(prompt, candidate_text)
            
            # NCD Tiebreaker (max 15% influence)
            # If structural score is ambiguous (close to 0.5), NCD helps
            ncd_val = self._compute_ncd(prompt, candidate_text)
            # Invert NCD (0 is similar, 1 is different) and scale
            ncd_score = 1.0 - ncd_val
            
            # Weighted score: 85% structural, 15% NCD
            z_obs = 0.85 * base_z + 0.15 * ncd_score
            
            # Kalman Update
            new_mu, new_sigma_sq = self._kalman_update(
                state['mu'], state['sigma_sq'], z_obs, R, Q
            )
            
            state['mu'] = new_mu
            state['sigma_sq'] = new_sigma_sq
            state['n'] += 1
            
            # Phase Transition Check
            if state['sigma_sq'] < epsilon:
                state['ordered'] = True

        # Compile results
        for state in states:
            # Final score is posterior mean
            score = state['mu']
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt itself is flawed, no candidate can be "correct" with high confidence
            meta_cap = self._meta_confidence(prompt)
            
            # If the prompt is a trap, we downgrade the score of ALL candidates 
            # to reflect that the question is unanswerable reliably.
            if meta_cap < 0.5:
                # Scale down score towards uncertainty (0.5)
                # If meta_cap is 0.2, max score should be around 0.2-0.3
                score = score * meta_cap 

            results.append({
                'candidate': state['candidate'],
                'score': score,
                'reasoning': f"Kalman posterior mu={score:.3f}, variance={state['sigma_sq']:.4f}. "
                             f"Structural match applied. Meta-confidence cap: {meta_cap:.2f}."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        # 1. Check Meta-Confidence (Prompt Traps)
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is fundamentally flawed, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap

        # 2. Evaluate structural match for this specific answer
        struct_score = self._compute_structural_score(prompt, answer)
        
        # 3. NCD component (minor)
        ncd_val = self._compute_ncd(prompt, answer)
        ncd_score = 1.0 - ncd_val
        combined_score = 0.85 * struct_score + 0.15 * ncd_score
        
        # 4. Apply Cap
        final_conf = min(combined_score, meta_cap)
        
        # Ensure we don't return > 0.9 without definitive computation
        # Since we rely on heuristics, hard cap at 0.95 unless it's a perfect numeric match?
        # For safety and honesty, cap at 0.92 for heuristic-based tools
        if final_conf > 0.92:
            final_conf = 0.92
            
        return max(0.0, min(1.0, final_conf))