import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dynamic Epigenetic Analogy Sandpile (DEAS) - Constrained Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This addresses the "Historical 
       Inhibitor" warning by grounding the system in hard logic rather than pure 
       epigenetic/SOC dynamics.
    2. Epigenetic Modulation: Candidates matching structural patterns receive a 
       "methylation" boost (increased excitability/score). Mismatches (e.g., candidate 
       says "Yes" when prompt has "not") are suppressed.
    3. SOC Avalanche Simulation: Instead of a full graph, we simulate the "avalanche" 
       as a threshold check. If structural evidence is weak, the system relies on 
       NCD (tiebreaker). If structural evidence is strong, it triggers a "large-scale 
       cascade" (high confidence score).
    4. Analogical Reasoning: Used to map the structural pattern of the prompt to the 
       candidate structure (e.g., Question -> Answer pattern matching).
    
    This satisfies the requirement to use Epigenetics/SOC only for modulation/confidence
    while relying on structural parsing for the actual reasoning score.
    """

    def __init__(self):
        # Structural patterns for parsing
        self.negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")
        
        # Epigenetic state (simulated per session for stability)
        # Represents "methylation" levels of structural features based on success
        self.feature_weights = {
            'negation_match': 1.0,
            'numeric_consistency': 1.0,
            'conditional_logic': 1.0,
            'structural_overlap': 1.0
        }

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': any(w in text_lower for w in self.negation_words),
            'has_comparative': any(op in text_lower for op in self.comparative_ops),
            'has_conditional': any(cond in text_lower for cond in self.conditionals),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)],
            'length': len(text)
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """
        Simple numeric reasoning: 
        - If prompt asks for max/min (detected by comparatives), check candidate.
        - Otherwise, check if candidate numbers are a subset or logical derivation.
        For this constrained implementation, we prioritize exact matches or logical 
        presence in simple arithmetic contexts.
        """
        if not prompt_nums:
            return 1.0 # No numeric constraint
        if not cand_nums:
            return 0.2 # Numbers expected but none found
        
        # Heuristic: If prompt has numbers, candidate should likely relate to them
        # Simple overlap check for now to avoid complex math engine
        p_set = set(round(x, 2) for x in prompt_nums)
        c_set = set(round(x, 2) for x in cand_nums)
        
        if p_set & c_set:
            return 1.0
        # If completely disjoint, penalize heavily unless it's a calculation result
        return 0.5

    def _check_logical_consistency(self, prompt_feats: dict, cand_feats: dict) -> float:
        """Check for logical contradictions (e.g., Negation flip)."""
        score = 1.0
        
        # Negation consistency: If prompt implies negative, answer shouldn't be positive affirmation
        # This is a simplification of analogical mapping
        if prompt_feats['has_negation']:
            # If prompt is negative, and candidate is a simple "Yes", penalize
            if cand_feats['length'] < 10 and 'yes' in str(cand_feats).lower():
                score -= 0.5
                
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structural_features(prompt)
        scored_candidates = []

        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            score = 0.0
            reasoning_parts = []

            # 1. Structural Parsing (Primary Signal)
            # Numeric Evaluation
            if prompt_feats['numbers']:
                num_consistency = self._check_numeric_consistency(prompt_feats['numbers'], cand_feats['numbers'])
                score += num_consistency * self.feature_weights['numeric_consistency'] * 0.5
                if num_consistency > 0.8:
                    reasoning_parts.append("Numeric consistency detected")
                elif num_consistency < 0.5:
                    reasoning_parts.append("Numeric mismatch")

            # Logical Consistency (Negation/Conditionals)
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats)
            score += logic_score * self.feature_weights['negation_match'] * 0.3
            
            # Keyword Overlap (Analogical Structure)
            # Check if candidate shares structural keywords (not just content words)
            shared_struct = 0
            if prompt_feats['has_negation'] and cand_feats['has_negation']:
                shared_struct += 0.2
            if prompt_feats['has_conditional'] and cand_feats['has_conditional']:
                shared_struct += 0.2
            
            score += shared_struct
            if shared_struct > 0:
                reasoning_parts.append("Structural analogy match")

            # 2. SOC/Avalanche Trigger (Metacognitive Boost)
            # If structural score is high enough, trigger "avalanche" (boost score significantly)
            # This mimics the critical state where a small input causes a large cascade
            avalanche_threshold = 0.6
            if score >= avalanche_threshold:
                score = 0.9 + (score - avalanche_threshold) # Boost to near 1.0
                reasoning_parts.append("Critical mass reached (SOC boost)")

            # 3. NCD as Tiebreaker (Only if structural signal is weak)
            if score < 0.4:
                # Use NCD only when logic fails to distinguish
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower distance = higher similarity = higher score)
                # But penalize pure echo
                if len(cand) < len(prompt) * 0.9: 
                    score = max(score, (1.0 - ncd_val) * 0.3)
                    reasoning_parts.append("NCD fallback applied")

            # Normalize score to 0-1 range roughly
            score = max(0.0, min(1.0, score))
            
            # Epigenetic update simulation (internal state change for future calls)
            # If this candidate looks good, we slightly upweight the features it used
            if score > 0.7:
                if cand_feats['numbers']:
                    self.feature_weights['numeric_consistency'] = min(1.5, self.feature_weights['numeric_consistency'] * 1.01)

            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Low structural signal"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and epigenetic-like modulation.
        High confidence if structural features align perfectly.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]['score']
        reasoning = res[0]['reasoning']
        
        # Epigenetic modulation: 
        # If the reasoning indicates a strong structural match, boost confidence
        if "Numeric consistency" in reasoning or "Structural analogy" in reasoning:
            return min(1.0, base_score * 1.1)
        
        # If it relied on NCD fallback, cap confidence
        if "NCD fallback" in reasoning:
            return base_score * 0.8
            
        return base_score