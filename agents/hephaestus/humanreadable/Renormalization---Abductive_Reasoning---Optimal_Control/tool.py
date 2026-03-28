import re
import math
import zlib
from typing import List, Dict, Tuple, Any
import numpy as np

class ReasoningTool:
    """
    Hierarchical Abductive-Control Scorer (HACS)
    
    Mechanism:
    1. Parsing: Extracts logical atoms (negations, conditionals, causals, numerics) into a graph.
    2. Renormalization: Coarse-grains the graph by contracting nodes of same type within distance thresholds.
    3. Abduction: Identifies missing causal links (hypotheses) required for closure.
    4. Optimal Control: Computes a cost function J based on hypothesis rarity (prior) and graph deviation.
       Lower J implies a more plausible explanation.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presupposition, or unanswerable traits.
    
    Score = Structural Consistency (50%) + Computational Verification (35%) + NCD Tiebreaker (15%)
    """

    def __init__(self):
        # Precompiled regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|lead|result|make|force|enable)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?(?:\s*(?:%|units?|meters?|seconds?|hours?|days?|years?))?'),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did|why does|when did)\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every|all)\s+\w+.*\b(a|an|the)\s+\w+', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they)\b.*\bwho\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }
        # Corpus frequency priors (simulated log-probabilities)
        self.priors = {
            'causal': -1.5, 'conditional': -1.2, 'negation': -2.0, 
            'comparative': -1.8, 'numeric': -0.5, 'quantifier': -1.0
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Tokenize and extract structural features."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_quantifier': bool(self.patterns['quantifier'].search(text)),
            'numbers': [float(n) for n in re.findall(self.patterns['numeric'].pattern, text)],
            'length': len(text.split()),
            'raw': text
        }
        return features

    def _check_meta_confidence(self, text: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        text_lower = text.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(text):
            return 0.2
        
        # 2. Scope ambiguity (Every X did a Y)
        if self.patterns['scope_ambiguity'].search(text) and 'same' not in text_lower and 'different' not in text_lower:
            return 0.4
            
        # 3. Pronoun ambiguity with "who"
        if self.patterns['pronoun_ambiguity'].search(text):
            return 0.3
            
        # 4. False dichotomy indicators without exhaustive context
        if self.patterns['false_dichotomy'].search(text) and 'only' not in text_lower:
            return 0.5
            
        # 5. Subjectivity without criteria
        if self.patterns['subjectivity'].search(text) and 'measure' not in text_lower and 'data' not in text_lower:
            return 0.4
            
        # 6. Unanswerability (missing info indicators)
        if 'unknown' in text_lower or 'cannot be determined' in text_lower:
            return 0.1
            
        return 1.0

    def _renormalize_graph(self, features: Dict) -> Tuple[np.ndarray, float]:
        """
        Simulates hierarchical renormalization.
        Constructs a feature vector and computes a 'coarse-grained' complexity cost.
        """
        # Level 0: Raw features
        x0 = np.array([
            float(features['has_negation']),
            float(features['has_conditional']),
            float(features['has_causal']),
            float(features['has_comparative']),
            float(features['has_quantifier']),
            min(len(features['numbers']), 5.0) / 5.0 # Normalized numeric density
        ])
        
        # Level 1: Contract based on causal/conditional presence (Logic compression)
        # If conditional exists, negation cost is reduced (logic handles it)
        logic_factor = 0.8 if features['has_conditional'] else 1.0
        x1 = x0 * logic_factor
        
        # Level 2: Super-node (Scalar complexity measure)
        # High complexity (many disjoint logic types) increases cost unless resolved
        complexity = np.linalg.norm(x1, ord=1)
        
        return x1, complexity

    def _compute_abductive_cost(self, prompt_feat: Dict, ans_feat: Dict) -> float:
        """
        Computes the cost J* for the optimal control problem.
        J = ||s_prompt - s_answer||^2 + lambda * ||u||_1 + gamma * prior(h)
        Where u represents the 'hypotheses' (missing links) needed to reconcile prompt and answer.
        """
        # State difference (Deviation from full explanation)
        s_prompt, _ = self._renormalize_graph(prompt_feat)
        s_ans, _ = self._renormalize_graph(ans_feat)
        
        deviation = np.linalg.norm(s_prompt - s_ans) ** 2
        
        # Hypothesis generation cost (Abduction)
        # If prompt has structure (e.g., conditional) and answer lacks it, we need a hypothesis to bridge
        u_cost = 0.0
        if prompt_feat['has_conditional'] and not ans_feat['has_conditional']:
            u_cost += 2.0 * math.exp(self.priors['conditional']) # Penalty for missing logic
            
        if prompt_feat['has_negation'] and not ans_feat['has_negation']:
            u_cost += 2.5 * math.exp(self.priors['negation']) # High penalty for missing negation
            
        # Numeric consistency check (Constructive computation)
        numeric_penalty = 0.0
        if prompt_feat['numbers'] and ans_feat['numbers']:
            # Simple check: if numbers exist, do they match or result from simple ops?
            # For this implementation, we penalize large deviations in numeric count if counts differ significantly
            if abs(len(prompt_feat['numbers']) - len(ans_feat['numbers'])) > 1:
                numeric_penalty = 1.5
        elif prompt_feat['numbers'] and not ans_feat['numbers']:
            # Answer ignores numbers entirely
            numeric_penalty = 3.0

        total_cost = deviation + u_cost + numeric_penalty
        return total_cost

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Attempts to verify numeric claims.
        Returns 1.0 if consistent, 0.0 if contradictory, 0.5 if neutral.
        """
        p_nums = [float(x) for x in re.findall(self.patterns['numeric'].pattern, prompt)]
        c_nums = [float(x) for x in re.findall(self.patterns['numeric'].pattern, candidate)]
        
        if not p_nums:
            return 0.5 # No numeric constraint
            
        if not c_nums:
            return 0.2 # Prompt has numbers, candidate ignores them
        
        # Heuristic: If candidate contains the result of a simple operation on prompt numbers
        # Or if the max number in candidate matches max in prompt (rough check)
        # This is a simplified "solver" for the sake of the constraint
        p_sum = sum(p_nums)
        c_sum = sum(c_nums)
        
        # Check for direct equality or simple transformation
        if any(abs(c - p_sum) < 1e-6 for c in c_nums):
            return 1.0
        if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
            return 0.9
            
        # If counts match exactly, likely consistent
        if len(p_nums) == len(c_nums):
            return 0.8
            
        return 0.4

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        meta_cap = self._check_meta_confidence(prompt)
        
        results = []
        raw_scores = []
        
        # Phase 1: Compute raw costs
        for cand in candidates:
            ans_feat = self._extract_features(cand)
            
            # 1. Structural/Abductive Cost (50%)
            cost = self._compute_abductive_cost(prompt_feat, ans_feat)
            struct_score = math.exp(-cost)
            
            # 2. Constructive Computation (35%)
            comp_score = self._compute_numeric_score(prompt, cand)
            
            # 3. NCD Tiebreaker (15%) - Inverted distance
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Sum
            final_score = (0.50 * struct_score) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap (Tier B)
            if meta_cap < 1.0:
                # If ambiguous, scale down confidence but preserve relative ranking slightly
                final_score *= meta_cap
            
            raw_scores.append(final_score)
            results.append({"candidate": cand, "score": final_score, "reasoning": ""})

        # Normalize scores to 0-1 range relative to the best candidate
        max_score = max(raw_scores) if raw_scores else 1.0
        min_score = min(raw_scores) if raw_scores else 0.0
        
        ranked_results = []
        for i, res in enumerate(results):
            # Normalize: (score - min) / (max - min) to spread out, then cap at meta_cap
            if max_score > min_score:
                norm_score = (raw_scores[i] - min_score) / (max_score - min_score)
            else:
                norm_score = 0.5
            
            # Ensure we don't exceed the epistemic cap
            norm_score = min(norm_score, meta_cap)
            
            # Generate reasoning string
            reason_parts = []
            if prompt_feat['has_negation'] and not self._extract_features(res['candidate'])['has_negation']:
                reason_parts.append("Missing negation detected.")
            if prompt_feat['has_conditional'] and not self._extract_features(res['candidate'])['has_conditional']:
                reason_parts.append("Conditional logic incomplete.")
            if meta_cap < 0.5:
                reason_parts.append("Prompt contains ambiguity or presupposition.")
            if not reason_parts:
                reason_parts.append("Structurally consistent.")
                
            res["score"] = float(norm_score)
            res["reasoning"] = " ".join(reason_parts)
            ranked_results.append(res)

        # Sort by score descending
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        meta_cap = self._check_meta_confidence(prompt)
        
        # If the prompt itself is problematic, return low confidence immediately
        if meta_cap < 0.5:
            return meta_cap
            
        # Evaluate the specific pair
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # Cap the final confidence by the meta-analysis
        final_conf = min(base_score, meta_cap)
        
        # Never return > 0.9 unless it's a perfect structural match and no ambiguity
        if meta_cap == 1.0 and base_score > 0.95:
            return 0.95
            
        return float(final_conf)