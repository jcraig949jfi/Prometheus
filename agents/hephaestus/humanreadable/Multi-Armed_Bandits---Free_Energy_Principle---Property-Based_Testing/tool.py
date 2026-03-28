import re
import math
import random
import zlib
from typing import List, Dict, Tuple, Any

# --- Helper: Normalized Compression Distance (NCD) ---
def ncd(s1: str, s2: str) -> float:
    """Calculate Normalized Compression Distance using zlib."""
    if not s1 or not s2:
        return 1.0
    s1_bytes = s1.encode('utf-8')
    s2_bytes = s2.encode('utf-8')
    len_s1 = len(zlib.compress(s1_bytes))
    len_s2 = len(zlib.compress(s2_bytes))
    len_combined = len(zlib.compress(s1_bytes + s2_bytes))
    # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
    # Simplified symmetric version for stability
    if max(len_s1, len_s2) == 0:
        return 0.0
    return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

class ReasoningTool:
    """
    Bandit-Guided Predictive Property Testing (BG-PPT) Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, numbers).
    2. Free Energy Minimization: Computes prediction error as L2 distance between prompt and answer feature vectors.
    3. Multi-Armed Bandit (Thompson Sampling): Samples arm quality from Beta posteriors to rank candidates.
    4. Epistemic Honesty: Detects ambiguity/traps to cap confidence scores.
    5. Scoring: Structural (50%) + Computation (35%) + NCD Tiebreaker (15%).
    """

    def __init__(self):
        self.budget = 10  # Simulation rounds per evaluation
        self.tau = 0.5    # Error threshold for "reward"
        # Regex patterns for feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|unless)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|bigger|smaller|higher|lower)\b', re.IGNORECASE),
            'comparative_op': re.compile(r'[<>]=?'),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|lead|result|due|because|since)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|precedes|follows|first|last)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ bad)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|must be .+ or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her)\b.*\bwho\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Parse text into logical atoms and numeric values."""
        text_lower = text.lower()
        features = {
            'has_negation': 1 if self.patterns['negation'].search(text_lower) else 0,
            'has_comparative': 1 if (self.patterns['comparative'].search(text_lower) or self.patterns['comparative_op'].search(text)) else 0,
            'has_conditional': 1 if self.patterns['conditional'].search(text_lower) else 0,
            'has_causal': 1 if self.patterns['causal'].search(text_lower) else 0,
            'has_ordering': 1 if self.patterns['ordering'].search(text_lower) else 0,
            'numbers': [],
            'number_count': 0
        }
        
        # Extract numbers for constructive computation
        nums = self.patterns['numbers'].findall(text)
        if nums:
            features['numbers'] = [float(n) for n in nums]
            features['number_count'] = len(nums)
            
        return features

    def _compute_prediction_error(self, prompt_feats: Dict, answer_feats: Dict) -> float:
        """
        Compute Free Energy (Prediction Error) as squared L2 distance.
        Logic: Answers should inherit structural markers from the prompt (e.g., if prompt has numbers, answer should).
        """
        vec_prompt = [
            prompt_feats['has_negation'],
            prompt_feats['has_comparative'],
            prompt_feats['has_conditional'],
            prompt_feats['has_causal'],
            prompt_feats['has_ordering'],
            prompt_feats['number_count'] / 10.0 # Normalize count slightly
        ]
        
        vec_answer = [
            answer_feats['has_negation'],
            answer_feats['has_comparative'],
            answer_feats['has_conditional'],
            answer_feats['has_causal'],
            answer_feats['has_ordering'],
            answer_feats['number_count'] / 10.0
        ]
        
        # L2 Squared Distance
        error = sum((p - a) ** 2 for p, a in zip(vec_prompt, vec_answer))
        return error

    def _constructive_check(self, prompt: str, answer: str) -> float:
        """
        Perform constructive computation on numeric/constraint problems.
        Returns 1.0 if correct, 0.0 if wrong, 0.5 if not applicable.
        """
        # Extract numbers from prompt
        p_nums = self.patterns['numbers'].findall(prompt)
        a_nums = self.patterns['numbers'].findall(answer)
        
        if not p_nums or not a_nums:
            return 0.5 # Not a numeric problem
            
        try:
            p_vals = [float(x) for x in p_nums]
            a_vals = [float(x) for x in a_nums]
            
            # Simple heuristic: If prompt asks for comparison, check answer logic
            if any(op in prompt for op in ['greater', 'less', '>', '<', 'larger', 'smaller']):
                if len(p_vals) >= 2 and len(a_vals) >= 1:
                    # Check if the answer contains the correct extreme
                    max_p = max(p_vals)
                    min_p = min(p_vals)
                    ans_val = a_vals[-1] # Assume last number is the result
                    
                    if 'greater' in prompt.lower() or '>' in prompt or 'max' in prompt.lower() or 'largest' in prompt.lower():
                        return 1.0 if math.isclose(ans_val, max_p, rel_tol=1e-5) else 0.0
                    elif 'less' in prompt.lower() or '<' in prompt or 'min' in prompt.lower() or 'smallest' in prompt.lower():
                        return 1.0 if math.isclose(ans_val, min_p, rel_tol=1e-5) else 0.0
            
            # Simple arithmetic check (e.g. "What is 2 + 2?")
            if '+' in prompt and len(p_vals) >= 2:
                if math.isclose(a_vals[-1], sum(p_vals), rel_tol=1e-5):
                    return 1.0
            
        except ValueError:
            pass
            
        return 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, traps, and unanswerability.
        Returns a cap value (low if problematic).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 4. Pronoun Ambiguity (simplified)
        if self.patterns['pronoun_ambiguity'].search(p_lower) and 'who' in p_lower:
            return 0.3
            
        # 5. Unanswerability keywords
        unanswerable_keys = ['impossible to know', 'not enough info', 'undefined']
        if any(k in p_lower for k in unanswerable_keys):
            return 0.2
            
        return 1.0 # No obvious traps detected

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is clean, calculate structural alignment
        if meta_cap == 1.0:
            p_feats = self._extract_features(prompt)
            a_feats = self._extract_features(answer)
            error = self._compute_prediction_error(p_feats, a_feats)
            
            # Convert error to confidence (inverse relationship)
            # Low error -> High confidence
            raw_conf = 1.0 / (1.0 + error)
            
            # Boost if constructive check passes
            const_score = self._constructive_check(prompt, answer)
            if const_score == 1.0:
                raw_conf = min(1.0, raw_conf + 0.2)
            elif const_score == 0.0:
                raw_conf *= 0.5 # Penalty for wrong math
                
            return min(raw_conf, meta_cap)
        
        return meta_cap

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """
        Rank candidates using BG-PPT algorithm.
        """
        if not candidates:
            return []
            
        p_feats = self._extract_features(prompt)
        n_arms = len(candidates)
        
        # Initialize Bandit Arms (Beta(1,1) = Uniform)
        alphas = [1.0] * n_arms
        betas = [1.0] * n_arms
        
        # Pre-calculate features for all candidates
        cand_feats = [self._extract_features(c) for c in candidates]
        const_scores = [self._constructive_check(prompt, c) for c in candidates]
        
        # Bandit Simulation
        for _ in range(self.budget):
            # a. Sample from Posterior (Thompson Sampling)
            thetas = [random.betavariate(alphas[i], betas[i]) for i in range(n_arms)]
            
            # b. Select arm with highest sampled value
            best_idx = max(range(n_arms), key=lambda i: thetas[i])
            
            # c. Compute Prediction Error (Free Energy)
            err = self._compute_prediction_error(p_feats, cand_feats[best_idx])
            
            # d. Update Posterior
            # Reward if error is low OR constructive check is perfect
            is_reward = (err < self.tau) or (const_scores[best_idx] == 1.0)
            
            if is_reward:
                alphas[best_idx] += 1
            else:
                betas[best_idx] += 1
                
        # Final Scoring
        results = []
        max_ncd_score = 0.0
        
        for i, cand in enumerate(candidates):
            # Posterior Mean
            q_mean = alphas[i] / (alphas[i] + betas[i])
            
            # Constructive Bonus (20-35% weight)
            const_bonus = 0.0
            if const_scores[i] == 1.0:
                const_bonus = 0.35
            elif const_scores[i] == 0.0:
                const_bonus = -0.2 # Penalty
                
            # NCD Tiebreaker (Max 15%)
            # Invert NCD so 1.0 is perfect match, 0.0 is no match
            ncd_val = 1.0 - ncd(prompt, cand)
            ncd_contribution = ncd_val * 0.15
            
            # Final Score Composition
            # Structural/Bandit (50%) + Constructive (35%) + NCD (15%)
            final_score = (q_mean * 0.50) + const_bonus + ncd_contribution
            
            # Clamp score
            final_score = max(0.0, min(1.0, final_score))
            
            # Generate Reasoning String
            reasoning_parts = []
            if p_feats['has_negation'] and cand_feats[i]['has_negation']:
                reasoning_parts.append("matched negation structure")
            if p_feats['has_comparative'] and cand_feats[i]['has_comparative']:
                reasoning_parts.append("matched comparative logic")
            if const_scores[i] == 1.0:
                reasoning_parts.append("verified numeric constraint")
            elif const_scores[i] == 0.0:
                reasoning_parts.append("failed numeric verification")
            if not reasoning_parts:
                reasoning_parts.append("structural alignment via bandit optimization")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results