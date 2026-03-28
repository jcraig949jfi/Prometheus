import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Mechanism-Based Entropic Reasoner (DMBER) Implementation.
    
    Mechanism:
    1. Structural Parsing (Mechanism Design Core): Extracts logical constraints 
       (negations, comparatives, conditionals, numbers) to form a "truth vector".
       This acts as the incentive-compatible scoring rule, rewarding candidates 
       that align with structural logic over string similarity.
       
    2. Dialectical Synthesis (Thesis/Antithesis): For each candidate, we generate 
       a synthetic "antithesis" by logically inverting the extracted structural 
       features (e.g., flipping booleans, inverting number comparisons). 
       The score is the delta between the candidate's fit to the prompt's structure 
       vs. the antithesis's fit. This forces discrimination based on logic, not noise.
       
    3. Maximum Entropy Wrapper: The confidence score uses a logistic scaling 
       derived from the principle of maximum entropy, treating the structural 
       match as a constraint on the probability distribution of correctness. 
       It avoids over-confident priors by capping influence based on feature density.
       
    Note: Per safety guidelines, 'Dialectics' and 'MaxEnt' are restricted to 
    structural support and confidence wrapping, while 'Mechanism Design' drives 
    the core evaluation logic via structural constraint propagation.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|except)\b', re.I),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'length': len(text.split())
        }
        return features

    def _compute_structural_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Mechanism Design Core: Computes a score based on logical consistency.
        Rewards alignment of structural properties (e.g., if prompt has numbers, 
        candidate should likely involve numbers or logical operators).
        """
        score = 0.0
        
        # Constraint 1: Negation Consistency
        # If prompt implies negation logic, candidates lacking it (or having it when not needed) 
        # are penalized if they don't match the prompt's negation density roughly.
        if prompt_feats['has_negation']:
            score += 0.3 if cand_feats['has_negation'] else -0.3
        else:
            # Mild penalty for unnecessary negation in simple prompts
            if cand_feats['has_negation']:
                score -= 0.1

        # Constraint 2: Comparative Logic
        if prompt_feats['has_comparative']:
            score += 0.3 if cand_feats['has_comparative'] else -0.4
        elif cand_feats['has_comparative'] and not prompt_feats['has_comparative']:
            score -= 0.2

        # Constraint 3: Conditional Structure
        if prompt_feats['has_conditional']:
            score += 0.3 if cand_feats['has_conditional'] else -0.3
            
        # Constraint 4: Numeric Evaluation
        # If prompt has numbers, candidate must have numbers to be relevant
        if len(prompt_feats['numbers']) > 0:
            if len(cand_feats['numbers']) > 0:
                # Check magnitude consistency (heuristic: same order of magnitude or logical relation)
                # Simple heuristic: presence is good, exact match is better
                score += 0.2
                # Penalize if numbers are wildly different without context (simplified)
                p_avg = sum(prompt_feats['numbers']) / len(prompt_feats['numbers'])
                c_avg = sum(cand_feats['numbers']) / len(cand_feats['numbers'])
                if p_avg != 0 and abs(c_avg - p_avg) > abs(p_avg) * 10:
                    score -= 0.1
            else:
                score -= 0.5 # Major penalty for missing numbers in numeric prompt
        
        return score

    def _generate_antithesis_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Dialectical Step: Simulate an antithesis by inverting the structural expectations.
        If the candidate matches the "inverted" logic, it is likely wrong.
        """
        # Invert expectations
        inv_score = 0.0
        
        # If prompt has negation, antithesis would lack it (and vice versa)
        if prompt_feats['has_negation']:
            inv_score += 0.3 if not cand_feats['has_negation'] else -0.3
        else:
            inv_score += 0.3 if cand_feats['has_negation'] else -0.3
            
        if prompt_feats['has_comparative']:
            inv_score += 0.3 if not cand_feats['has_comparative'] else -0.3
        else:
            inv_score += 0.3 if cand_feats['has_comparative'] else -0.3
            
        return inv_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        if not candidates:
            return []

        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        for c in candidates:
            ncd_scores.append(self._ncd_distance(prompt, c))
        
        min_ncd = min(ncd_scores) if ncd_scores else 0
        max_ncd = max(ncd_scores) - min_ncd if len(ncd_scores) > 1 else 1
        
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            
            # 1. Mechanism Design: Structural Scoring
            structural_score = self._compute_structural_score(prompt_feats, cand_feats)
            
            # 2. Dialectical Refinement: Subtract Antithesis alignment
            antithesis_score = self._generate_antithesis_score(prompt_feats, cand_feats)
            raw_score = structural_score - antithesis_score
            
            # 3. NCD Tiebreaker (only if structural signal is weak)
            if abs(raw_score) < 0.1:
                ncd_norm = (ncd_scores[i] - min_ncd) / (max_ncd + 1e-9)
                # Lower NCD is better, so we invert it for addition
                raw_score += (1.0 - ncd_norm) * 0.05 
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural match: {structural_score:.2f}, Dialectical delta: {-antithesis_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Maximum Entropy Wrapper:
        Returns a calibrated probability [0, 1] based on structural consistency.
        Uses a logistic function to map the structural score to a probability,
        ensuring we don't over-fit (MaxEnt principle of least bias given constraints).
        """
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer)
        
        # Get raw structural alignment
        struct_score = self._compute_structural_score(prompt_feats, ans_feats)
        anti_score = self._generate_antithesis_score(prompt_feats, ans_feats)
        net_score = struct_score - anti_score
        
        # Add small NCD bonus if text is very similar (exact match case)
        ncd = self._ncd_distance(prompt, answer)
        if ncd < 0.1:
            net_score += 0.5
            
        # MaxEnt Logistic Mapping: P = 1 / (1 + exp(-k * (score - bias)))
        # Calibrated so that 0 score -> 0.5, high score -> 1.0
        # k controls steepness (uncertainty), bias centers the curve
        k = 2.5 
        bias = 0.0
        
        # Clamp input to prevent overflow
        val = max(-10, min(10, k * (net_score - bias)))
        prob = 1.0 / (1.0 + math.exp(-val))
        
        return prob