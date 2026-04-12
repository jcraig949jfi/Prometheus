import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Distributed Active-Inference RL Swarm (Simulated via Structural Parsing).
    
    Mechanism:
    1. Active Inference Core (evaluate): The 'agent' maintains a generative model of the prompt's
       logical structure. It minimizes variational free energy by maximizing the alignment between
       the prompt's structural constraints (negations, comparatives, conditionals) and the candidate.
       High alignment = Low Free Energy = High Score.
       
    2. Swarm Intelligence (Stigmergic Confidence): Instead of a complex multi-agent simulation,
       we simulate the 'swarm' as a collection of independent structural parsers (agents) that
       deposit 'pheromones' (confidence weights) on specific logical features. The confidence()
       method aggregates these signals. Per constraints, Swarm logic is restricted to the 
       confidence wrapper and structural support, not the primary scoring engine.
       
    3. RL Component: The scoring function acts as a policy gradient, rewarding candidates that
       satisfy epistemic constraints (logical consistency) and penalizing those that increase
       prediction error (contradictions).
       
    This implementation prioritizes structural parsing and numeric evaluation over NCD,
    using NCD only as a tiebreaker to ensure we beat the baseline.
    """

    def __init__(self):
        # Structural patterns for active inference matching
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical features from text to form the generative model."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': re.findall(self.numeric_pattern, text),
            'length': len(text),
            'words': set(re.findall(r'\b\w+\b', text_lower))
        }
        return features

    def _numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Check numeric logic (e.g., if prompt implies sorting or comparison)."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No numeric data to contradict
        
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            # If prompt has numbers and candidate has numbers, check magnitude alignment
            # Simple heuristic: If prompt asks for 'larger', candidate should reflect that?
            # Since we don't parse the intent verb perfectly, we check for presence/absence mismatch
            # A strong signal is if the candidate introduces random numbers not in prompt context
            # For this tool, we reward candidates that contain numeric values if the prompt has them
            # assuming the answer requires numeric derivation.
            return 0.8 if len(c_vals) > 0 else 0.5
        except ValueError:
            return 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Active Inference principles.
        Score = Structural Alignment (Primary) + NCD Tiebreaker (Secondary).
        """
        p_feat = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            c_feat = self._extract_structure(cand)
            score = 0.0
            reasoning_parts = []

            # 1. Negation Consistency (Active Inference: Minimizing prediction error on logic)
            # If prompt has negations, correct answer often needs to acknowledge them or flip logic.
            # Heuristic: Presence match is safer than absence for complex logic.
            neg_match = 0.0
            if p_feat['negations'] > 0:
                # If prompt has negation, candidate having some logical marker is good
                neg_match = 0.3 if c_feat['negations'] > 0 else 0.0
                reasoning_parts.append(f"negation_check:{'pass' if neg_match > 0 else 'fail'}")
            else:
                neg_match = 0.2 # Default small bonus for simplicity
            
            # 2. Comparative/Conditional Alignment
            comp_score = 0.0
            if p_feat['comparatives'] > 0:
                # Candidate should ideally have comparatives or numbers if prompt compares
                if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                    comp_score = 0.3
                    reasoning_parts.append("comparative_aligned")
                else:
                    reasoning_parts.append("comparative_mismatch")
            
            cond_score = 0.0
            if p_feat['conditionals'] > 0:
                if c_feat['conditionals'] > 0 or len(c_feat['words']) > 5: # Complex answer expected
                    cond_score = 0.2
                    reasoning_parts.append("conditional_handled")

            # 3. Numeric Evaluation
            num_score = self._numeric_consistency(p_feat['numbers'], c_feat['numbers'])
            if p_feat['numbers'] and c_feat['numbers']:
                reasoning_parts.append("numeric_present")

            # Base structural score
            base_score = neg_match + comp_score + cond_score + (0.2 * num_score)
            
            # 4. NCD as Tiebreaker (Only if structural signals are weak or equal)
            # We invert NCD (lower distance = higher similarity = higher score contribution)
            # But we weight it lightly so structure dominates.
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + ncd_score
            
            # Constraint: Must beat random guessing. Add small bias for length appropriateness.
            if len(c_feat['words']) == 0:
                final_score -= 0.5 # Penalty for empty or non-text
                reasoning_parts.append("empty_penalty")

            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural_baseline"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Simulates Swarm Confidence via Stigmergic accumulation.
        Multiple 'agents' (checks) deposit confidence.
        Restricted to wrapper logic as per constraints.
        """
        if not answer or not answer.strip():
            return 0.0
        
        p_feat = self._extract_structure(prompt)
        a_feat = self._extract_structure(answer)
        
        confidence_deposit = 0.0
        agents_active = 0

        # Agent 1: Negation Consistency Check
        agents_active += 1
        if p_feat['negations'] == 0 and a_feat['negations'] == 0:
            confidence_deposit += 0.3 # Consistent absence
        elif p_feat['negations'] > 0 and a_feat['negations'] > 0:
            confidence_deposit += 0.4 # Consistent presence
        elif p_feat['negations'] > 0 and a_feat['negations'] == 0:
            confidence_deposit += 0.1 # Risky but possible if answer is 'Yes'
        else:
            confidence_deposit += 0.2

        # Agent 2: Length/Complexity Plausibility
        agents_active += 1
        len_ratio = len(answer) / (len(prompt) + 1)
        if 0.01 < len_ratio < 2.0:
            confidence_deposit += 0.3
        else:
            confidence_deposit += 0.05

        # Agent 3: Keyword Overlap (Stigmergic trace)
        agents_active += 1
        common_words = p_feat['words'].intersection(a_feat['words'])
        overlap_ratio = len(common_words) / (len(p_feat['words']) + 1)
        confidence_deposit += min(overlap_ratio * 0.5, 0.4)

        # Normalize roughly to 0-1 range based on max possible deposits
        # Max deposit approx 1.1, cap at 1.0
        raw_conf = confidence_deposit / 1.1
        return min(max(raw_conf, 0.0), 1.0)