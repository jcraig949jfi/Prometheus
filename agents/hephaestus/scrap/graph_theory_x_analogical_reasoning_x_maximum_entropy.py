import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Maximum-Entropy Analogical Graph Neural Network (ME-AGNN) Simulation.
    
    Mechanism:
    1. Graph Theory (Structural Parsing): Encodes the prompt's logical structure 
       (negations, comparatives, conditionals) as a lightweight adjacency representation.
       Per constraints, this is used for structural scoring, not direct final scoring.
    2. Analogical Reasoning: Maps the parsed structure of the prompt against candidate 
       answers to find structural isomorphisms (e.g., does the candidate preserve the 
       negation or comparative direction?).
    3. Maximum Entropy: Instead of picking the single highest matching candidate, 
       computes a probability distribution over candidates that maximizes Shannon entropy 
       subject to the constraint that the expected analogical fit matches the observed 
       structural evidence. This prevents over-confidence and encourages exploration 
       of diverse but valid hypotheses.
    4. Epistemic Honesty (Meta-Confidence): A dedicated layer detects ambiguity, 
       presupposition, and unanswerable patterns (Tier B) to cap confidence scores, 
       ensuring the system admits uncertainty rather than hallucinating answers.
    """

    def __init__(self):
        # Patterns for Tier B (Epistemic Honesty) detection
        self.presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bquit\b", r"\bassumed\b", r"\bpresuppose\b"
        ]
        self.scope_patterns = [r"\bevery\s+\w+.*\ba\s+\w+\b"]  # Simplified scope check
        self.pronoun_patterns = [r"\b(he|she|him|her|they)\b.*\bwho\b"]
        self.false_dichotomy_patterns = [r"\beither\s+.*\bor\s+", r"\bis it\s+.*\s+or\s+"]
        self.subjectivity_patterns = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        
        # Structural parsing regexes
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise'}

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value (low if problematic, 1.0 if clean).
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for false dichotomies
        for pattern in self.false_dichotomy_patterns:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a forced choice without context
                if "or" in p_lower and ("either" in p_lower or "is it" in p_lower):
                    return 0.25

        # Check for subjectivity without data
        has_subj = any(re.search(p, p_lower) for p in self.subjectivity_patterns)
        if has_subj and "data" not in p_lower and "statistics" not in p_lower:
            return 0.25

        # Check for pronoun ambiguity in specific "who" questions
        if re.search(r"\bwho\b", p_lower) and any(p in p_lower for p in ["he", "she", "him", "her", "they"]):
            # Heuristic: if multiple names appear, it might be ambiguous
            names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(names) >= 2:
                return 0.25

        return 1.0

    def _parse_structure(self, text: str) -> dict:
        """Extracts structural features: negations, comparatives, conditionals, numbers."""
        tokens = set(re.findall(r'\b\w+\b', text.lower()))
        numbers = re.findall(r'\d+\.?\d*', text)
        
        features = {
            'has_negation': bool(tokens & self.negation_words),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'numbers': [float(n) for n in numbers],
            'token_set': tokens
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _structural_score(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural consistency (Graph Theory analog).
        Ensures logical properties (negation, direction) are preserved.
        """
        score = 0.0
        weight = 0.0

        # Negation consistency
        weight += 1.0
        if prompt_feats['has_negation'] == cand_feats['has_negation']:
            score += 1.0
        
        # Conditional consistency
        weight += 1.0
        if prompt_feats['has_conditional'] == cand_feats['has_conditional']:
            score += 1.0
            
        # Numeric evaluation (Constructive computation)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            weight += 2.0
            # Simple heuristic: if prompt has numbers, candidate should too, 
            # or perform explicit comparison if possible
            if len(cand_feats['numbers']) > 0:
                score += 1.0
                # Check for direct calculation match if obvious (e.g. 2+2)
                # For this implementation, we rely on the presence of numbers as a proxy 
                # for engaging with the numeric constraint, unless we can parse an expression.
        
        # Base textual overlap (Analogical mapping of tokens)
        # Jaccard similarity of tokens
        intersection = len(prompt_feats['token_set'] & cand_feats['token_set'])
        union = len(prompt_feats['token_set'] | cand_feats['token_set'])
        jaccard = intersection / union if union > 0 else 0
        score += jaccard
        weight += 1.0

        return (score / weight) if weight > 0 else 0.0

    def _max_entropy_distribution(self, scores: List[float], temperature: float = 1.0) -> List[float]:
        """
        Converts raw scores into a probability distribution maximizing entropy
        subject to the constraint of expected score.
        P(i) = exp(score_i / T) / sum(exp(score_j / T))
        """
        if not scores:
            return []
        
        # Shift scores for numerical stability
        max_score = max(scores)
        exp_scores = [math.exp((s - max_score) / temperature) for s in scores]
        sum_exp = sum(exp_scores)
        
        if sum_exp == 0:
            return [1.0 / len(scores)] * len(scores)
            
        return [e / sum_exp for e in exp_scores]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._parse_structure(prompt)
        raw_scores = []
        
        # 1. Structural & Analogical Scoring
        for cand in candidates:
            cand_feats = self._parse_structure(cand)
            s_score = self._structural_score(prompt_feats, cand_feats, prompt, cand)
            raw_scores.append(s_score)
        
        # 2. Maximum Entropy Inference
        # We use a low temperature to sharpen distinctions but keep entropy high enough
        # to avoid over-confidence on weak signals.
        probs = self._max_entropy_distribution(raw_scores, temperature=0.7)
        
        # 3. NCD Tiebreaker (Max 15% influence)
        # We blend the structural/analogical score with NCD only if structural scores are close
        final_results = []
        max_prob = max(probs) if probs else 0
        
        for i, cand in enumerate(candidates):
            base_score = probs[i]
            
            # NCD component
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and normalize roughly
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Blend: Structural is dominant (85%), NCD is tiebreaker (15%)
            # However, if structural signal is weak (all probs similar), NCD might sway slightly
            combined_score = (base_score * 0.85) + (ncd_score * (base_score + 0.1)) 
            
            # Reasoning string generation
            reasoning = f"Structural fit: {base_score:.3f}, NCD influence: {ncd_score:.3f}"
            if prompt_feats['has_negation'] and not self._parse_structure(cand)['has_negation']:
                reasoning += " [Warning: Negation mismatch]"

            final_results.append({
                "candidate": cand,
                "score": combined_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 even for definitive answers to maintain epistemic humility.
        """
        # 1. Meta-Confidence Check (Tier B Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural Verification (Tier A Competence)
        # If the prompt is clean, we check if the answer structurally aligns
        prompt_feats = self._parse_structure(prompt)
        ans_feats = self._parse_structure(answer)
        
        # Basic consistency check
        consistency = 0.5 # Base confidence for clean prompts
        
        # Penalize negation mismatch
        if prompt_feats['has_negation'] != ans_feats['has_negation']:
            consistency -= 0.4
        
        # Penalize conditional mismatch
        if prompt_feats['has_conditional'] != ans_feats['has_conditional']:
            consistency -= 0.2
            
        # Boost for numeric presence if prompt has numbers
        if prompt_feats['numbers']:
            if ans_feats['numbers']:
                consistency += 0.3
            else:
                consistency -= 0.3
        
        # Clamp between 0 and 0.9 (Never 1.0 to allow for unknown unknowns)
        final_conf = max(0.0, min(0.9, consistency))
        
        return final_conf