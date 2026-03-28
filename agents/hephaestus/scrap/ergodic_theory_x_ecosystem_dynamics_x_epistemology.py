import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Replicator-Ergodic Belief Network (REBN) Approximation.
    
    Mechanism:
    1. Ergodic Sampling Layer: Uses structural parsing (negations, comparatives, 
       conditionals, numeric eval) to generate an initial unbiased 'likelihood' score.
       This acts as the time-averaged sample converging to truth.
    2. Ecosystem Dynamics: Implements replicator dynamics where candidate scores 
       evolve based on 'epistemic fitness'. Fitness = Structural Score + Coherence Bonus.
       Candidates compete for 'cognitive resources' (probability mass).
    3. Epistemic Justification: 
       - Coherentist Checker: Penalizes logical contradictions within the answer relative 
         to prompt constraints.
       - Reliabilist Monitor: Boosts candidates with high structural clarity (low entropy).
       
    Note: Per causal analysis, 'Ecosystem' math is restricted to the confidence wrapper 
    and internal weight normalization to avoid historical failure modes. 'Ergodic' and 
    'Epistemology' logic paths are kept distinct.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extracts structural features acting as the Ergodic Sampling Layer."""
        text_lower = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(no|not|never|none|neither|nobody)\b', text_lower)),
            'conditional_count': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'comparative_count': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'numeric_count': len(re.findall(r'\d+(?:\.\d+)?', text)),
            'logic_keywords': len(re.findall(r'\b(therefore|because|thus|hence|since)\b', text_lower)),
            'length': len(text.split())
        }
        return features

    def _evaluate_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Checks numeric validity if numbers are present."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+(?:\.\d+)?', prompt)
        c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric constraint to violate
        
        try:
            # Simple heuristic: if candidate introduces numbers wildly outside prompt range, penalize
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            if not p_vals: return 1.0
            
            p_min, p_max = min(p_vals), max(p_vals)
            range_span = (p_max - p_min) if p_max != p_min else 1.0
            
            penalty = 0.0
            for val in c_vals:
                if val < p_min - range_span or val > p_max + range_span:
                    penalty += 0.2
            return max(0.0, 1.0 - penalty)
        except ValueError:
            return 1.0

    def _calculate_coherence(self, prompt: str, candidate: str) -> float:
        """Epistemic justification: Checks for logical consistency markers."""
        score = 1.0
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # If prompt has conditionals, candidate should ideally have logic keywords or specific structure
        if p_feat['conditional_count'] > 0:
            if c_feat['logic_keywords'] == 0 and c_feat['conditional_count'] == 0:
                score -= 0.15 # Weak coherence
        
        # Negation handling: If prompt asks "Which is NOT...", candidate should ideally not be empty
        if p_feat['negation_count'] > 0:
            if len(candidate.strip()) < 3:
                score -= 0.3
                
        return max(0.0, score)

    def _replicator_step(self, scores: List[float], fitness: List[float]) -> List[float]:
        """
        Applies replicator dynamics: x_i' = x_i * (f_i - avg_f) / avg_f
        Simplified to: x_i_new = x_i * f_i / sum(fitness) to maintain probability distribution.
        This simulates the ecosystem weight dynamics.
        """
        total_fit = sum(fitness) + self.epsilon
        new_scores = []
        for s, f in zip(scores, fitness):
            # Growth proportional to fitness relative to population
            growth = f / total_fit
            new_scores.append(s * growth)
        
        # Normalize to ensure sum to 1 (Ecosystem carrying capacity)
        total_new = sum(new_scores) + self.epsilon
        return [s / total_new for s in new_scores]

    def _get_base_score(self, prompt: str, candidate: str) -> float:
        """Primary scoring via structural parsing (Ergodic Layer)."""
        score = 0.5
        
        # 1. Numeric Consistency
        score *= self._evaluate_numeric_consistency(prompt, candidate)
        
        # 2. Structural Alignment
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # Bonus for matching complexity (if prompt is complex, simple answers might be wrong)
        if p_feat['conditional_count'] > 0 and c_feat['logic_keywords'] > 0:
            score += 0.15
        if p_feat['negation_count'] > 0 and 'no' in candidate.lower() or 'not' in candidate.lower():
            score += 0.1
            
        # Length heuristic (penalize extremely short answers for complex prompts)
        if p_feat['length'] > 10 and c_feat['length'] < 3:
            score -= 0.2
            
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Ergodic Sampling Layer: Initial unbiased structural scoring
        base_scores = [self._get_base_score(prompt, c) for c in candidates]
        
        # 2. Epistemic Justification Layer: Coherence and Reliability
        fitness = []
        for i, c in enumerate(candidates):
            coherence = self._calculate_coherence(prompt, c)
            reliability = 1.0 if len(c.split()) > 1 else 0.8 # Reliabilist monitor bonus for substance
            # Fitness = Base * Coherence * Reliability
            fit = (base_scores[i] + self.epsilon) * coherence * reliability
            fitness.append(fit)
        
        # 3. Ecosystem Dynamics: Replicator update
        # Initialize uniform distribution as starting population state
        pop_state = [1.0 / len(candidates)] * len(candidates)
        
        # Run a few steps of replicator dynamics to converge
        for _ in range(3):
            pop_state = self._replicator_step(pop_state, fitness)
            
        # Final scoring combines structural base with ecosystem convergence
        # We blend base score (40%) and ecosystem result (60%)
        final_scores = []
        for i in range(len(candidates)):
            # NCD Tiebreaker (only if scores are very close)
            ncd_score = 0.0
            if len(candidates) > 1:
                # Simple NCD approximation for tie-breaking
                s_joint = len(zlib.compress((prompt + candidates[i]).encode()))
                s_sep = len(zlib.compress(prompt.encode())) + len(zlib.compress(candidates[i].encode()))
                ncd_val = (s_joint - min(s_sep, s_joint)) / max(s_joint, 1)
                ncd_score = 1.0 - ncd_val # Higher is better
            
            # Weighted combination
            raw_score = 0.4 * base_scores[i] + 0.6 * pop_state[i]
            if ncd_score > 0: 
                # Only apply NCD as a tiny nudge for tie-breaking logic
                raw_score += (ncd_score * 0.01) 
                
            final_scores.append(max(0.0, min(1.0, raw_score)))

        # Rank and format
        results = []
        for i, c in enumerate(candidates):
            results.append({
                "candidate": c,
                "score": final_scores[i],
                "reasoning": f"Structural:{base_scores[i]:.2f}, Eco:{pop_state[i]:.2f}, Fit:{fitness[i]:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as primary signal, modulated by ecosystem-style 
        normalization to prevent overconfidence in noisy inputs.
        """
        base = self._get_base_score(prompt, answer)
        coherence = self._calculate_coherence(prompt, answer)
        
        # Ecosystem-inspired damping: if the 'environment' (prompt) is chaotic/long,
        # reduce confidence unless coherence is perfect.
        p_feat = self._structural_parse(prompt)
        complexity_penalty = 0.0
        if p_feat['length'] > 50:
            complexity_penalty = 0.1 * (1.0 - coherence)
            
        conf = (base * coherence) - complexity_penalty
        
        # Reliabilist check: explicit numbers increase confidence if consistent
        if self._evaluate_numeric_consistency(prompt, answer) == 1.0 and p_feat['numeric_count'] > 0:
            conf = min(1.0, conf + 0.1)
            
        return max(0.0, min(1.0, conf))