import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuro-Evolutionary Compositional Synthesizer (Simplified for CPU/No-Dep)
    
    Mechanism:
    1. Compositionality: Parses prompts into a graph of logical primitives (negation, comparison, conditionals).
    2. Genetic Algorithms: Maintains a population of 'hypothesis weights' (genome) that evolve via selection 
       based on how well they rank known structural patterns in training-like internal checks.
    3. Neuromodulation: A dynamic gain signal ('dopamine') that adjusts the penalty for complexity vs. 
       structural match. High gain (exploration) allows risky logical leaps; low gain (exploitation) 
       enforces strict structural adherence.
    
    Implementation:
    Since we cannot run full neural evolution in <150 lines without deps, we simulate the 'evolved state'
    by using a deterministic, structurally-aware scoring function that mimics the output of a 
    converged neuro-evolutionary search. We use NCD only as a tie-breaker.
    """

    def __init__(self):
        self.generation = 0
        # Simulated evolved genome: weights for structural features
        self.genome = {
            'negation_weight': 0.8,
            'comparative_weight': 0.9,
            'conditional_weight': 0.7,
            'numeric_precision': 0.95
        }
        # Neuromodulatory gain (dynamic exploration/exploitation balance)
        self.modulatory_gain = 0.5 

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract logical primitives (Compositionality layer)."""
        text_lower = text.lower()
        features = {
            'has_negation': 0.0,
            'has_comparative': 0.0,
            'has_conditional': 0.0,
            'numeric_val': None,
            'logic_score': 0.0
        }
        
        # Negation detection
        negations = ['not', 'no ', 'never', 'none', 'cannot', "n't"]
        if any(n in text_lower for n in negations):
            features['has_negation'] = 1.0
            
        # Comparative detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'better', 'worse']
        if any(c in text_lower for c in comparatives):
            features['has_comparative'] = 1.0
            
        # Conditional detection
        conditionals = ['if', 'then', 'unless', 'otherwise', 'when', 'provided']
        if any(c in text_lower for c in conditionals):
            features['has_conditional'] = 1.0

        # Numeric extraction (simple float finding)
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            try:
                features['numeric_val'] = float(nums[0])
            except ValueError:
                pass
                
        return features

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Apply evolved logical constraints to score candidate.
        Mimics the fitness function of the genetic algorithm.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.5 # Base prior
        
        # Constraint Propagation: Negation consistency
        if p_feat['has_negation']:
            # If prompt has negation, candidate should ideally reflect understanding 
            # (simplified: if candidate also has negation or specific 'no' keywords, boost)
            if c_feat['has_negation'] or 'no' in candidate.lower() or 'false' in candidate.lower():
                score += self.genome['negation_weight'] * self.modulatory_gain
            else:
                # Penalty for ignoring negation
                score -= 0.5

        # Constraint Propagation: Comparatives
        if p_feat['has_comparative'] and p_feat['numeric_val'] is not None and c_feat['numeric_val'] is not None:
            # Check if numeric logic holds (simplified heuristic)
            # In a real system, this would parse the specific comparison operator
            if abs(p_feat['numeric_val'] - c_feat['numeric_val']) < 0.01:
                score += self.genome['comparative_weight']
        
        # Conditional logic check (heuristic)
        if p_feat['has_conditional']:
            if c_feat['has_conditional'] or 'then' in candidate.lower() or 'if' in candidate.lower():
                score += self.genome['conditional_weight'] * 0.5

        # Neuromodulatory Gain Adjustment:
        # If the prompt is complex (multiple features), increase gain to encourage 
        # looking for structural matches over simple string overlap.
        complexity = sum([p_feat['has_negation'], p_feat['has_comparative'], p_feat['has_conditional']])
        if complexity > 1:
            self.modulatory_gain = min(1.0, self.modulatory_gain + 0.2)
            score *= (1.0 + self.modulatory_gain * 0.1)
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tie-breaker only)."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Reset modulatory gain per episode (Exploration start)
        self.modulatory_gain = 0.3 
        
        for cand in candidates:
            # Primary Score: Structural/Logical reasoning
            logic_score = self._evaluate_logic(prompt, cand)
            
            # Secondary Score: NCD (only used if logic scores are tied/close)
            # We invert NCD so higher is better (lower distance = higher score)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.05 # Small weight, strictly tie-breaking
            
            final_score = logic_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.2f}, NCD-adjusted: {ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        # Re-use evaluation logic for a single pair
        # We simulate a ranking of [answer, "dummy"] to get the score relative to baseline
        ranked = self.evaluate(prompt, [answer, ""])
        if not ranked:
            return 0.0
            
        target = ranked[0]
        if target['candidate'] == answer:
            # Normalize score to 0-1 range roughly
            conf = min(1.0, max(0.0, target['score']))
            return conf
        else:
            # If dummy won, answer is likely bad
            return 0.1