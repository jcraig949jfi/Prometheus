import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Hierarchical Prediction-Error Swarm Optimizer (HPESO) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical propositions, negations, comparatives, 
       and causal links from the prompt to form a 'sensory input' vector.
    2. Swarm Optimization: Agents represent candidate answer parses. They evolve 
       to minimize 'Free Energy' (prediction error) between the candidate's 
       structural features and the prompt's extracted constraints.
    3. Epistemic Honesty: A meta-cognitive layer detects ambiguity, presupposition, 
       and scope issues. If detected, confidence is capped low regardless of score.
    4. Scoring: Weighted sum of Structural Match (50%), Computational Consistency (35%), 
       and NCD similarity (15%).
    """

    def __init__(self):
        self.swarm_size = 15
        self.iterations = 20
        # Priors for logical operators and structural markers
        self.logic_keywords = ['if', 'then', 'else', 'because', 'therefore', 'not', 'no', 'never']
        self.comp_ops = ['>', '<', '>=', '<=', '=', '==', 'more', 'less', 'greater', 'smaller']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'without']
        self.presupposition_triggers = ['stopped', 'quit', 'ceased', 'failed', 'regret', 'realize']
        self.ambiguity_triggers = ['either', 'or', 'best', 'worst', 'favorite', 'he', 'she', 'they', 'who']

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers, logic."""
        text_lower = text.lower()
        features = {
            'neg_count': sum(1 for w in self.negations if re.search(r'\b' + w + r'\b', text_lower)),
            'comp_count': sum(1 for w in self.comp_ops if w in text_lower),
            'logic_count': sum(1 for w in self.logic_keywords if re.search(r'\b' + w + r'\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text),
            'has_question': '?' in text,
            'length': len(text),
            'word_count': len(text.split())
        }
        # Numeric consistency check
        features['numeric_sum'] = 0.0
        if features['numbers']:
            try:
                features['numeric_sum'] = sum(float(n) for n in features['numbers'])
            except ValueError:
                pass
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _detect_ambiguity(self, prompt: str) -> Tuple[bool, str]:
        """
        Tier B Reasoning: Detect presuppositions, scope ambiguity, and unanswerability.
        Returns (is_ambiguous, reason_string)
        """
        p_lower = prompt.lower()
        reasons = []

        # 1. Presupposition checks ("Have you stopped...", "Why did X fail...")
        for trigger in self.presupposition_triggers:
            if re.search(rf'\b(have|has|did|why|when)\s+\w*\s*{trigger}', p_lower):
                reasons.append("presupposition")
                break
        
        # 2. False Dichotomy / Either-Or without exhaustiveness
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\b(both|all|options)\b', p_lower):
            # Heuristic: if "either/or" exists but no explicit "only" or exhaustive list
            if len(re.findall(r'\b(or|either)\b', p_lower)) == 2: 
                reasons.append("false_dichotomy")

        # 3. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p_lower):
            if not re.search(r'\b(data|metric|criteria|according to)\b', p_lower):
                reasons.append("subjectivity")

        # 4. Pronoun Ambiguity in questions
        if re.search(r'\b(he|she|they|him|her)\s+(was|is|did)\b', p_lower) and '?' in prompt:
             if re.search(r'\bwho\b', p_lower):
                 reasons.append("pronoun_ambiguity")

        # 5. Unanswerable / Missing Info indicators
        if re.search(r'\b(calculate|solve|find)\b', p_lower) and not re.search(r'\d+', p_lower):
             # Asking for math without numbers
             if not any(k in p_lower for k in ['count', 'list', 'name']):
                 reasons.append("missing_data")

        is_ambig = len(reasons) > 0
        return is_ambig, "; ".join(reasons) if is_ambig else "none"

    def _swarm_optimize(self, prompt_features: Dict, candidate_features: Dict, candidate_text: str) -> float:
        """
        Simulate HPESO: Minimize free energy between prompt priors and candidate state.
        Returns negative free energy (higher is better).
        """
        # Initialize swarm: state = [neg_weight, comp_weight, logic_weight, num_match, length_match]
        # Dimensions correspond to feature importance
        dim = 5
        population = np.random.rand(self.swarm_size, dim) # Positions (0-1)
        velocity = np.zeros((self.swarm_size, dim))
        
        # Target vector (normalized prompt features)
        # We normalize features to ~0-1 range for comparison
        target = np.array([
            min(1.0, prompt_features['neg_count'] / 5.0),
            min(1.0, prompt_features['comp_count'] / 5.0),
            min(1.0, prompt_features['logic_count'] / 10.0),
            1.0 if prompt_features['numbers'] else 0.0, # Binary presence
            0.5 # Length is handled separately
        ])
        
        # Candidate vector
        cand_vec = np.array([
            min(1.0, candidate_features['neg_count'] / 5.0),
            min(1.0, candidate_features['comp_count'] / 5.0),
            min(1.0, candidate_features['logic_count'] / 10.0),
            1.0 if candidate_features['numbers'] else 0.0,
            0.5
        ])

        best_fitness = -np.inf
        global_best = np.random.rand(dim)

        # Precision matrix (diagonal) - higher precision on logic and numbers
        Pi = np.diag([1.0, 1.0, 1.5, 2.0, 0.5]) 

        for t in range(self.iterations):
            for i in range(self.swarm_size):
                # 1. Prediction Error
                error = target - population[i]
                
                # 2. Precision Weighting
                weighted_error = Pi @ error
                
                # 3. Free Energy Approximation (Negative of squared error weighted)
                # F = 0.5 * e^T * Pi * e
                free_energy = 0.5 * np.dot(error, weighted_error)
                fitness = -free_energy # Maximize negative free energy

                # Update personal best logic (simplified for vectorization)
                if fitness > best_fitness:
                    best_fitness = fitness
                    global_best = population[i].copy()

                # 4. Swarm Update (PSO equations)
                w = 0.7 # Inertia
                c1, c2 = 1.4, 1.4
                r1, r2 = np.random.rand(2)
                
                # Velocity update
                velocity[i] = (w * velocity[i] + 
                               c1 * r1 * (cand_vec - population[i]) + # Attract to candidate structure
                               c2 * r2 * (global_best - population[i])) # Attract to global best
                
                # Position update
                population[i] += velocity[i]
                
                # Clip/Sigmoid thresholding for binary-like behavior on presence
                population[i] = 1.0 / (1.0 + np.exp(-population[i])) 

        # Final Score Calculation based on best agent's alignment
        # We add a computational consistency bonus if numbers match
        comp_bonus = 0.0
        if prompt_features['numbers'] and candidate_features['numbers']:
            # Simple heuristic: if candidate contains same numbers, boost score
            p_nums = set(prompt_features['numbers'])
            c_nums = set(candidate_features['numbers'])
            if p_nums.intersection(c_nums):
                comp_bonus = 0.5 # Significant boost for numeric consistency

        return float(best_fitness) + comp_bonus

    def _meta_confidence(self, prompt: str) -> float:
        """
        Epistemic Honesty Check.
        Caps confidence if the prompt exhibits Tier B failure modes.
        """
        is_ambig, reason = self._detect_ambiguity(prompt)
        if is_ambig:
            return 0.25 # Low confidence for ambiguous/trap prompts
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Baseline NCD for the prompt (to normalize candidate NCDs)
        # We compare candidate to prompt, but NCD is symmetric enough for ranking relative to prompt
        base_ncd = 0.0 
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural & Swarm Score (50%)
            swarm_score = self._swarm_optimize(prompt_feats, cand_feats, cand)
            # Normalize swarm score roughly to 0-1 range (assuming range -2 to 2)
            norm_swarm = (swarm_score + 2.0) / 4.0 
            norm_swarm = max(0.0, min(1.0, norm_swarm))
            
            # 2. Computational Consistency (35%)
            # Check numeric logic if numbers exist
            comp_score = 0.5 # Default neutral
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # If prompt has math verbs, check if candidate looks like a number
                if re.search(r'\b(calculate|sum|add|subtract|multiply|divide|equal)\b', prompt.lower()):
                    # If candidate is purely numeric or starts with a number, high score
                    if re.match(r'^-?\d+(\.\d+)?', cand.strip()):
                        comp_score = 1.0
                    else:
                        comp_score = 0.2 # Likely wrong format
                else:
                    comp_score = 0.8 # Numbers present, likely relevant
            elif not prompt_feats['numbers']:
                comp_score = 0.8 # No numbers to check, assume pass
            
            # 3. NCD Similarity (15%)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Weighted Sum
            final_score = (0.50 * norm_swarm) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap
            if meta_cap < 1.0:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight variance but keep low
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {norm_swarm:.2f}, Comp: {comp_score:.2f}, NCD: {ncd_score:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        # 1. Meta-Cognitive Check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        
        # If meta says ambiguous, return low confidence immediately
        if meta_conf < 0.5:
            return meta_conf

        # 2. Structural/Computational Verification
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer)
        
        # Run a mini-evaluation to get structural alignment
        # We treat the single answer as a candidate list of 1
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
            
        base_score = eval_res[0]['score']
        
        # Calibration: 
        # - High structural match + No ambiguity = High confidence (max 0.95)
        # - Low structural match = Low confidence
        # - Ambiguity detected earlier = Capped low
        
        # Adjust base_score to 0-1 confidence scale
        # Base score is already weighted, but we need to be conservative
        confidence_val = base_score * 0.95 
        
        # Penalty for length mismatch in logical prompts
        if prompt_feats['logic_count'] > 2 and len(answer.split()) < 3:
            confidence_val *= 0.5
            
        return float(np.clip(confidence_val, 0.0, 0.95))

# Example usage logic (not part of class, for demonstration)
# tool = ReasoningTool()
# print(tool.evaluate("If A > B and B > C, is A > C?", ["Yes", "No", "Maybe"]))
# print(tool.confidence("Have you stopped cheating?", "Yes")) # Should be low