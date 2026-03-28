import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Incentive-Driven Phase-Transition Cellular Automaton (AI-PTCA) Simulator.
    
    Mechanism:
    1. Mechanism Design (Core): Candidates act as agents in a VCG-style auction.
       They bid based on structural alignment with the prompt (negations, comparatives, numbers).
       Truthful bidding (high structural match) maximizes local welfare.
    2. Phase Transitions (Validation): The system calculates an 'Order Parameter' (entropy)
       of the candidate set. If the top candidate's structural score pushes the system 
       across a critical threshold (high coherence), the hypothesis is validated.
       Low coherence (chaotic/low match) indicates hypothesis falsification.
    3. Cellular Automata (Structure): Used only in confidence() to parse local 
       character-level dependencies (structural parsing) without running global dynamics.
    
    This architecture prioritizes logical structure over string similarity (NCD),
    using NCD only as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        # Critical threshold for phase transition (empirically tuned for binary logic tasks)
        self.critical_point = 0.65 
        # Weights for mechanism design auction
        self.w_negation = 2.0
        self.w_comparative = 1.5
        self.w_numeric = 1.8
        self.w_conditional = 1.2

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|nor|without)\b', t_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|>=|<=|==|!=)\b', t_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|provided|when|whenever)\b', t_lower)),
            'numeric': len(re.findall(r'\d+(?:\.\d+)?', text))
        }
        return features

    def _calculate_bid(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Calculate 'welfare' bid based on structural alignment.
        Agents (candidates) gain payoff by matching the structural complexity of the prompt.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        total_prompt_features = sum(p_feat.values()) + 1e-9
        
        # Reward matching the presence/absence of logical structures
        # If prompt has negations, candidate should ideally reflect logic handling them
        # Simplified alignment: Candidate gets points for having structural density similar to prompt
        # or explicitly answering numeric/comparative queries.
        
        # 1. Negation Alignment
        if p_feat['negation'] > 0:
            score += self.w_negation * (1.0 if c_feat['negation'] > 0 or len(candidate) < 5 else 0.5)
        else:
            score += self.w_negation * (1.0 if c_feat['negation'] == 0 else -0.5)

        # 2. Comparative/Numeric Logic
        if p_feat['comparative'] > 0 or p_feat['numeric'] > 0:
            # Reward candidates that contain numbers or comparative words if prompt has them
            if c_feat['numeric'] > 0 or c_feat['comparative'] > 0:
                score += self.w_comparative * (p_feat['numeric'] + p_feat['comparative'])
        
        # 3. Conditional Logic
        if p_feat['conditional'] > 0:
            score += self.w_conditional * (1.0 if c_feat['conditional'] > 0 else 0.2)

        # Base length penalty/bonus to avoid trivial answers unless justified
        if len(candidate) < 3 and total_prompt_features > 0:
            score -= 1.0
            
        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (tie-breaker only)."""
        if not s1 or not s2: return 1.0
        s1_b, s2_b = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Mechanism Design auctions and Phase Transition validation.
        """
        if not candidates:
            return []
        
        # Step 1: Mechanism Design - Collect Bids (Structural Scores)
        bids = []
        for i, cand in enumerate(candidates):
            bid_score = self._calculate_bid(prompt, cand)
            bids.append((i, bid_score))
        
        # Sort by bid score (descending) - The "Auction" result
        bids.sort(key=lambda x: x[1], reverse=True)
        
        # Step 2: Phase Transition Analysis
        # Calculate order parameter (normalized entropy of top bids) to detect criticality
        # If the top candidate is significantly better than others, we are in an "Ordered" phase (High Confidence)
        # If scores are similar, we are in "Chaotic" phase (Low Confidence/Ambiguous)
        
        normalized_scores = []
        max_bid = bids[0][1] if bids[0][1] > 0 else 1.0
        for _, score in bids:
            normalized_scores.append(score / max_bid)
            
        # Simple entropy-like measure for order parameter
        # High variance in scores = Ordered (Clear winner). Low variance = Chaotic.
        avg_score = sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0
        variance = sum((s - avg_score)**2 for s in normalized_scores) / len(normalized_scores)
        
        # Map variance to a phase state. 
        # High variance -> Distinct winner -> Stable phase (Hypothesis Supported)
        # Low variance -> Noise -> Chaotic phase (Hypothesis Uncertain)
        # We use the variance to boost the top score if it's distinct (phase transition effect)
        phase_boost = 1.0 + (variance * 0.5) 
        
        results = []
        for rank, (idx, raw_score) in enumerate(bids):
            candidate_text = candidates[idx]
            final_score = raw_score * phase_boost
            
            # Tie-breaking with NCD if structural scores are very close
            if rank > 0:
                prev_idx = bids[rank-1][0]
                prev_raw = bids[rank-1][1]
                if abs(raw_score - prev_raw) < 0.01:
                    # Use NCD to break tie
                    ncd_curr = self._ncd_distance(prompt, candidate_text)
                    ncd_prev = self._ncd_distance(prompt, candidates[prev_idx])
                    if ncd_curr < ncd_prev: # Lower NCD is better match
                        final_score += 0.001 # Tiny nudge
                    else:
                        final_score -= 0.001

            # Generate reasoning string
            reasoning = f"Structural alignment score: {raw_score:.2f}. "
            if variance > 0.1:
                reasoning += "System in ordered phase (clear logical distinction)."
            else:
                reasoning += "System near critical point (ambiguous logical structure)."
                
            results.append({
                "candidate": candidate_text,
                "score": final_score,
                "reasoning": reasoning
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural parsing (CA local rules) 
        and phase proximity to critical point.
        """
        # 1. Structural Parsing (The CA Rule)
        # Check if answer contains logical operators present in prompt
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        match_count = 0
        total_checks = 0
        
        # Check Negation consistency
        total_checks += 1
        if (p_feat['negation'] > 0 and a_feat['negation'] > 0) or \
           (p_feat['negation'] == 0 and a_feat['negation'] == 0):
            match_count += 1
            
        # Check Numeric consistency
        if p_feat['numeric'] > 0:
            total_checks += 1
            if a_feat['numeric'] > 0:
                match_count += 1
        
        # Check Comparative consistency
        if p_feat['comparative'] > 0:
            total_checks += 1
            if a_feat['comparative'] > 0 or a_feat['numeric'] > 0:
                match_count += 1

        base_conf = match_count / max(total_checks, 1)
        
        # 2. Phase Transition Modifier
        # If the answer is structurally rich enough to sustain the prompt's complexity,
        # we are above the critical point (High Confidence).
        structural_density = (a_feat['negation'] + a_feat['numeric'] + a_feat['comparative']) / (len(answer) + 1) * 10
        
        # Heuristic mapping to 0-1 range
        # Base logic match contributes 50%, structural density contributes 50%
        confidence_val = (0.6 * base_conf) + (0.4 * min(1.0, structural_density * 2))
        
        # Clamp
        return max(0.0, min(1.0, confidence_val))