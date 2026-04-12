import re
import math
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Optional, Set

# Data Structures
Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])

class ReasoningTool:
    """
    A reasoning tool combining Information Theory, Abductive Reasoning, and Sensitivity Analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, causals, numbers) 
       from the prompt and candidates using regex.
    2. Abductive Hypothesis Generation: Greedily selects statements that maximize 
       information gain (reduction in residual entropy) to explain the observation set.
    3. Information-Theoretic Scoring: Scores hypotheses based on Mutual Information 
       between the hypothesis and observations, penalized by residual entropy.
    4. Sensitivity Analysis: Perturbs statement weights and polarities to measure 
       score stability. Unstable scores are penalized.
    5. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and unanswerable 
       queries to cap confidence, ensuring the tool admits uncertainty.
    
    Score Decomposition: Structural (60%), Computation (25%), NCD (15%).
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|lower than|higher than|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|second|third|last|rank|order)\b', re.IGNORECASE)
        }
        # Presupposition triggers for Tier B
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.IGNORECASE),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.IGNORECASE), # "Why did X fail" implies X failed
            re.compile(r'\b(either|or)\b.*\b(or|either)\b', re.IGNORECASE) # Simple false dichotomy check
        ]
        self.pronoun_triggers = re.compile(r'\b(he|she|him|her|they|them)\b', re.IGNORECASE)
        self.subjectivity_triggers = re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.IGNORECASE)

    def _extract_statements(self, text: str) -> List[Statement]:
        """Parses text into a list of Statement namedtuples."""
        statements = []
        lower_text = text.lower()
        
        # Extract numeric values first as they often anchor other claims
        nums = self.patterns['numeric'].finditer(text)
        num_vals = [float(m.group(1)) for m in nums]
        
        # Check for specific structural matches
        has_neg = bool(self.patterns['negation'].search(lower_text))
        has_comp = bool(self.patterns['comparative'].search(lower_text))
        has_cond = bool(self.patterns['conditional'].search(lower_text))
        has_causal = bool(self.patterns['causal'].search(lower_text))
        has_order = bool(self.patterns['ordering'].search(lower_text))
        
        # Create base statement for the whole text block if no specific atomic split is obvious
        # In a full system, we'd split by sentences. Here we treat the candidate/prompt chunk as a unit.
        weight = 1.0
        if re.search(r'\b(certainly|definitely|must)\b', lower_text): weight = 1.0
        elif re.search(r'\b(possibly|maybe|might)\b', lower_text): weight = 0.5
        elif re.search(r'\b(rarely|unlikely)\b', lower_text): weight = 0.3
        
        # Generate statements based on detected features
        if has_neg:
            statements.append(Statement('negation', [], False, None, weight))
        if has_comp:
            statements.append(Statement('comparative', [], True, None, weight))
        if has_cond:
            statements.append(Statement('conditional', [], True, None, weight))
        if has_causal:
            statements.append(Statement('causal', [], True, None, weight))
        if has_order:
            statements.append(Statement('ordering', [], True, None, weight))
            
        # Add numeric statements
        for n in num_vals:
            statements.append(Statement('numeric', [n], True, n, weight))
            
        # Fallback generic statement if nothing specific found
        if not statements:
            statements.append(Statement('generic', [], True, None, weight))
            
        return statements

    def _calculate_entropy(self, weights: np.ndarray) -> float:
        """Calculates Shannon entropy from normalized weights."""
        if len(weights) == 0 or np.sum(weights) == 0:
            return 0.0
        probs = weights / np.sum(weights)
        probs = probs[probs > 0] # Avoid log(0)
        return -np.sum(probs * np.log2(probs + 1e-10))

    def _generate_hypothesis(self, obs_statements: List[Statement], max_size: int = 5) -> Set[int]:
        """Greedy abductive search to maximize information gain."""
        if not obs_statements:
            return set()
            
        hypothesis_indices = set()
        remaining_indices = set(range(len(obs_statements)))
        
        # Initial residual entropy
        current_weights = np.array([s.weight for s in obs_statements])
        initial_entropy = self._calculate_entropy(current_weights)
        
        for _ in range(max_size):
            best_idx = -1
            max_gain = -1.0
            
            for idx in remaining_indices:
                # Simulate adding this statement to hypothesis
                # In this simplified model, 'explaining' a statement removes its weight from residual
                temp_weights = current_weights.copy()
                temp_weights[idx] = 0 # Effectively removed from residual
                
                residual_entropy = self._calculate_entropy(temp_weights)
                gain = initial_entropy - residual_entropy # Simplified gain
                
                if gain > max_gain:
                    max_gain = gain
                    best_idx = idx
            
            if best_idx != -1 and max_gain > 0.01: # Threshold for significance
                hypothesis_indices.add(best_idx)
                remaining_indices.remove(best_idx)
                # Update current state (simplified: we just keep removing for the next iter)
                # In a real system, H_res would be recalculated based on logical implication
                current_weights[best_idx] = 0 
            else:
                break
                
        return hypothesis_indices

    def _score_hypothesis(self, obs_statements: List[Statement], hypothesis: Set[int], lambda_reg: float = 0.5) -> float:
        """Computes the information-theoretic score."""
        if not obs_statements:
            return 0.0
            
        weights = np.array([s.weight for s in obs_statements])
        total_weight = np.sum(weights)
        if total_weight == 0:
            return 0.0
            
        # H(O)
        h_o = self._calculate_entropy(weights)
        
        # H(O|H) - Residual entropy after removing hypothesized statements
        residual_weights = weights.copy()
        for idx in hypothesis:
            if idx < len(residual_weights):
                residual_weights[idx] = 0
        
        h_o_given_h = self._calculate_entropy(residual_weights)
        
        # Mutual Information I(H;O) approx = H(O) - H(O|H)
        # Since H(O|H) here is just residual entropy of weights, and H(O) is total.
        # If H explains everything, residual is 0, MI is max.
        mi = h_o - h_o_given_h
        
        # Residual Entropy Penalty
        h_res = h_o_given_h
        
        base_score = mi - lambda_reg * h_res
        return base_score

    def _sensitivity_analysis(self, obs_statements: List[Statement], hypothesis: Set[int], n_perturb: int = 10, beta: float = 0.5) -> float:
        """Calculates sensitivity penalty based on score variance under perturbation."""
        if not obs_statements:
            return 0.0
            
        base_scores = []
        original_weights = [s.weight for s in obs_statements]
        original_polarities = [s.polarity for s in obs_statements]
        
        for _ in range(n_perturb):
            perturbed_stats = []
            for i, s in enumerate(obs_statements):
                # Flip polarity with p=0.1
                new_polarity = s.polarity
                if np.random.rand() < 0.1:
                    new_polarity = not s.polarity
                
                # Add noise to numeric
                new_num = s.num_val
                if s.num_val is not None:
                    sigma = 0.05 * abs(s.num_val) if s.num_val != 0 else 0.05
                    new_num = s.num_val + np.random.normal(0, sigma)
                
                # Noise to weight
                new_weight = max(0.01, s.weight + np.random.normal(0, 0.05))
                
                perturbed_stats.append(Statement(s.pred, s.args, new_polarity, new_num, new_weight))
            
            # Re-calculate score (hypothesis indices might shift, but we keep indices fixed for simplicity in this approx)
            # Or re-generate hypothesis? The prompt implies scoring the existing H against perturbed O.
            # Let's score the existing hypothesis structure against perturbed data.
            score = self._score_hypothesis(perturbed_stats, hypothesis)
            base_scores.append(score)
            
        if len(base_scores) < 2:
            return 0.0
            
        return beta * np.std(base_scores)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_triggers:
            if pattern.search(p_lower):
                return 0.25 # High uncertainty
        
        # 2. Subjectivity
        if self.subjectivity_triggers.search(p_lower):
            return 0.3
        
        # 3. Pronoun Ambiguity (Heuristic: if "who" question and pronouns exist)
        if "who" in p_lower and self.pronoun_triggers.search(p_lower):
            # Check if multiple entities mentioned (simple heuristic)
            if p_lower.count(" told ") > 0 or p_lower.count(" said ") > 0:
                return 0.3

        # 4. Unanswerability (No structural match)
        # If the prompt has no numbers, no logic words, and is very short, it might be noise
        statements = self._extract_statements(prompt)
        if len(statements) == 1 and statements[0].pred == 'generic':
            # If it's just a generic string with no logic/numbers, be cautious
            if len(prompt.split()) < 10:
                return 0.2

        return 1.0 # No red flags

    def _process_item(self, prompt: str, candidate: str) -> Tuple[float, str, float]:
        """Core logic to score a single candidate."""
        # Combine prompt and candidate for context
        full_text = f"{prompt} {candidate}"
        statements = self._extract_statements(full_text)
        
        # 1. Abductive Hypothesis Generation
        hypothesis = self._generate_hypothesis(statements)
        
        # 2. Information-Theoretic Scoring
        base_score = self._score_hypothesis(statements, hypothesis)
        
        # 3. Sensitivity Analysis
        sensitivity_penalty = self._sensitivity_analysis(statements, hypothesis)
        
        # 4. Structural & Computation Bonus
        # Check for explicit numeric computation match
        comp_bonus = 0.0
        nums_prompt = self.patterns['numeric'].findall(prompt)
        nums_cand = self.patterns['numeric'].findall(candidate)
        
        if nums_prompt and nums_cand:
            # Simple heuristic: if candidate number is derived from prompt numbers logically
            # Here we just check presence as a proxy for "computation attempted"
            comp_bonus = 0.5 
            
        # 5. NCD Tiebreaker (Max 15% influence)
        ncd = self._compute_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15 # Lower NCD = Higher similarity = Small bonus
        
        # Final Score Assembly
        # Structural/InfoTheory (60%) + Computation (25%) + NCD (15%)
        # Normalize base_score roughly to 0-1 range for combination
        # Base score can be negative, so we sigmoid or shift
        normalized_base = 1 / (1 + math.exp(-base_score)) # Sigmoid
        
        final_score = (normalized_base * 0.60) + (comp_bonus * 0.25) + (ncd_score * 1.0)
        final_score -= sensitivity_penalty
        
        reasoning_str = f"Hypothesis size: {len(hypothesis)}, Base Info: {base_score:.2f}, Sensitivity Penalty: {sensitivity_penalty:.2f}"
        
        return final_score, reasoning_str, normalized_base

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt, "") # Check prompt generally
        
        for cand in candidates:
            score, reason, raw_conf = self._process_item(prompt, cand)
            
            # Apply Meta-Confidence Cap (Tier B)
            if meta_cap < 1.0:
                # If the prompt is ambiguous, cap the score regardless of candidate
                score = min(score, meta_cap)
                reason += f" [Capped by Meta-Conf: {meta_cap:.2f}]"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B epistemic honesty.
        """
        # 1. Meta-Confidence Check (Prompt properties)
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Process to get raw structural confidence
        score, _, raw_conf = self._process_item(prompt, answer)
        
        # 3. Apply Caps
        # Never > 0.9 unless computation was definitive (hard to prove definitively without external truth)
        # We rely on the structural match strength.
        final_conf = min(score, 0.95)
        
        # If no structural signal found (raw_conf low), confidence must be low
        if raw_conf < 0.2:
            final_conf = 0.2
            
        # Apply meta cap again strictly
        final_conf = min(final_conf, meta_cap)
        
        return float(max(0.0, min(1.0, final_conf)))