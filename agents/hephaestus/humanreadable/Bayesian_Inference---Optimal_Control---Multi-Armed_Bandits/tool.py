import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Bayesian Inference, Optimal Control, and Multi-Armed Bandits.
    
    Mechanism:
    1. Structural Parsing: Extracts binary features (negations, comparatives, numerics, etc.)
       from the prompt and candidates to form evidence.
    2. Bayesian Update: Uses a Beta-Bernoulli conjugate model. Each feature acts as a 
       Bernoulli trial updating the prior Beta(alpha, beta) to a posterior.
       - Feature present -> increment alpha (evidence for correctness)
       - Feature absent/negative -> increment beta (evidence against)
    3. Optimal Control Cost: Calculates a stage-cost c_i = Expected Error + lambda * Uncertainty.
       This balances exploitation (picking the most likely correct answer) with exploration
       (penalizing high uncertainty when evidence is sparse).
    4. Epistemic Honesty (Tier B): Analyzes the prompt for ambiguity, presupposition, or 
       unanswerability. If detected, confidence is capped strictly to ensure the tool 
       admits ignorance rather than hallucinating certainty.
    5. Scoring: Final score is a weighted combination of structural match, computational 
       verification (numeric/logic), and a small NCD tiebreaker.
    """

    def __init__(self):
        # Prior parameters (uninformative start)
        self.alpha_0 = 1.0
        self.beta_0 = 1.0
        # Control parameter: trade-off between error minimization and uncertainty penalty
        self.lambda_uncertainty = 0.5 
        # Feature keywords
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.causal = ['cause', 'lead', 'result', 'make', 'force']
        self.ordering = ['first', 'second', 'third', 'before', 'after', 'next', 'last']
        # Presupposition triggers
        self.presupposition_triggers = ['stopped', 'quit', 'ceased', 'failed', 'why did', 'why does']

    def _extract_features(self, text: str) -> Dict[str, int]:
        """Extract binary structural features from text."""
        text_lower = text.lower()
        features = {}
        
        # 1. Negations
        features['has_negation'] = 1 if any(w in text_lower for w in self.negations) else 0
        
        # 2. Comparatives
        features['has_comparative'] = 1 if any(w in text_lower for w in self.comparatives) else 0
        
        # 3. Conditionals
        features['has_conditional'] = 1 if any(w in text_lower for w in self.conditionals) else 0
        
        # 4. Causal verbs
        features['has_causal'] = 1 if any(w in text_lower for w in self.causal) else 0
        
        # 5. Ordering
        features['has_ordering'] = 1 if any(w in text_lower for w in self.ordering) else 0
        
        # 6. Numeric values (presence of digits)
        features['has_numeric'] = 1 if re.search(r'\d+', text) else 0
        
        # 7. Logical connectors
        features['has_logic'] = 1 if any(w in text_lower for w in ['therefore', 'thus', 'hence', 'because']) else 0

        return features

    def _compute_numeric_truth(self, prompt: str, candidate: str) -> float:
        """
        Attempt to solve numeric comparisons or simple arithmetic implied in the text.
        Returns 1.0 if candidate is computationally verified, 0.0 if disproven, 0.5 if N/A.
        """
        # Extract numbers from prompt
        prompt_nums = re.findall(r'-?\d+\.?\d*', prompt)
        if len(prompt_nums) < 2:
            return 0.5 # Not enough data for numeric reasoning
            
        try:
            p_nums = [float(x) for x in prompt_nums]
            
            # Check for explicit comparison in candidate against extracted logic
            c_lower = candidate.lower()
            
            # Case 1: Candidate is a number found in prompt logic
            cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if cand_nums:
                c_val = float(cand_nums[0])
                # Simple heuristic: if prompt has "A > B" structure and candidate is max/min
                if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'max' in prompt.lower():
                    if c_val == max(p_nums): return 1.0
                    if c_val != max(p_nums): return 0.0
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'min' in prompt.lower():
                    if c_val == min(p_nums): return 1.0
                    if c_val != min(p_nums): return 0.0
                    
            # Case 2: Direct arithmetic check (e.g. prompt "2 + 2", candidate "4")
            # Very basic eval safety check not needed for simple regex floats, but good practice
            # Here we just check if candidate number matches a simple operation result if obvious
            if len(p_nums) == 2:
                a, b = p_nums
                if abs(c_val - (a + b)) < 1e-6: return 1.0
                if abs(c_val - (a * b)) < 1e-6: return 1.0
                
        except ValueError:
            pass
            
        return 0.5 # No clear numeric contradiction or confirmation

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value (low if problematic, 1.0 if clean).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if any(trigger in p_lower for trigger in self.presupposition_triggers):
            # Check if it's a "Why" question which implies a fact might not be established
            if 'why' in p_lower and ('fail' in p_lower or 'stop' in p_lower or 'wrong' in p_lower):
                return 0.25
        
        # 2. False Dichotomy indicators without exhaustive context
        if re.search(r'\b(either|or)\b', p_lower) and 'only' not in p_lower:
            # Heuristic: if "either A or B" appears but no context guarantees exclusivity
            if 'either' in p_lower:
                return 0.30

        # 3. Subjectivity without criteria
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly']
        if any(w in p_lower for w in subjective_words):
            if 'measure' not in p_lower and 'data' not in p_lower:
                return 0.35

        # 4. Pronoun/Scope Ambiguity (Simple heuristic)
        # "X told Y he..." followed by "who"?
        if re.search(r'\b(he|she|they|it)\b', p_lower) and 'who' in p_lower:
            return 0.40
            
        return 1.0 # No obvious traps detected

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if max(len1, len2) == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._extract_features(prompt)
        prompt_len = len(prompt.split())
        
        # Meta-confidence cap based on prompt analysis
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            cand_features = self._extract_features(candidate)
            
            # --- Step 1: Structural Evidence (Bayesian Update) ---
            alpha = self.alpha_0
            beta = self.beta_0
            
            # Compare features: Match increases alpha, mismatch increases beta
            # We treat feature presence in candidate that matches prompt context as evidence
            for key in prompt_features:
                if key in cand_features:
                    if cand_features[key] == prompt_features[key] and prompt_features[key] == 1:
                        alpha += 1.0 # Match on positive feature
                    elif cand_features[key] != prompt_features[key]:
                        beta += 0.5 # Mismatch penalty
                    else:
                        # If prompt has no feature (0) and candidate has no feature (0), 
                        # it's neutral, but if candidate has feature (1) when prompt doesn't, 
                        # it might be hallucination -> beta++
                        if cand_features[key] == 1 and prompt_features[key] == 0:
                            beta += 0.2
            
            # --- Step 2: Computational Verification ---
            comp_score = self._compute_numeric_truth(prompt, candidate)
            if comp_score == 1.0:
                alpha += 5.0 # Strong boost for verified computation
            elif comp_score == 0.0:
                beta += 5.0  # Strong penalty for computational error

            # --- Step 3: Optimal Control Cost ---
            # Expected value of theta (probability of correctness)
            expected_theta = alpha / (alpha + beta)
            
            # Uncertainty (Standard Deviation approximation for Beta)
            # Var = (alpha*beta) / ((alpha+beta)^2 * (alpha+beta+1))
            variance = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
            uncertainty = math.sqrt(variance)
            
            # Cost function: Minimize Error + Lambda * Uncertainty
            # We want low error (high expected_theta) and low uncertainty
            cost = (1.0 - expected_theta) + self.lambda_uncertainty * uncertainty
            
            # Convert cost to a raw score (inverse relationship)
            # Raw score roughly correlates with expected_theta but penalized by uncertainty
            raw_score = 1.0 / (1.0 + cost) 
            
            # --- Step 4: NCD Tiebreaker (Max 15% weight) ---
            ncd = self._calculate_ncd(prompt, candidate)
            # NCD is distance (0=similar, 1=different). We want similarity for context, 
            # but distinctness for answer. 
            # Heuristic: Moderate similarity is good. 
            ncd_score = 1.0 - abs(ncd - 0.4) # Peak around 0.4 difference
            
            # --- Final Score Composition ---
            # Structural/Computational (85%) + NCD (15%)
            final_score = (0.85 * raw_score) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap
            if meta_cap < 1.0:
                # If the prompt is ambiguous, cap the confidence regardless of candidate quality
                # But allow relative ranking within the capped range
                final_score = min(final_score, meta_cap * 0.9) 
                
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Bayesian update (alpha={alpha:.1f}, beta={beta:.1f}), Control Cost={cost:.2f}, Meta-Cap={meta_cap:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get the raw score for this specific answer
        # We simulate a list with just this answer to get its specific metrics
        # However, to save compute, we can approximate or call evaluate with [answer]
        # Calling evaluate ensures consistency with ranking logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_conf = res[0]['score']
        
        # The final confidence is the minimum of the calculated score and the meta-cap
        # This ensures that if the question is flawed (meta_cap < 0.3), 
        # we never return high confidence even if the string matches well.
        final_conf = min(raw_conf, meta_cap)
        
        # Additional safety: If no structural features matched at all (very short/empty),
        # and meta_cap wasn't triggered by specific keywords, still be skeptical
        prompt_feats = self._extract_features(prompt)
        if sum(prompt_feats.values()) == 0 and len(prompt.split()) < 5:
            final_conf = min(final_conf, 0.3)

        return float(f"{final_conf:.4f}") # Round to 4 decimals