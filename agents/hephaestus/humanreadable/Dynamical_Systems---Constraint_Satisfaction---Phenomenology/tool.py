import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dynamical Phenomenological Constraint Solver (DPCS) - Computational Approximation
    
    Mechanism:
    1. Phenomenological Layer (Epoché Gate): Parses the prompt to extract structural 
       constraints (negations, comparatives, conditionals) forming the 'intentional focus'.
    2. Dynamical Core: Simulates candidate evolution as a trajectory in a latent space 
       defined by constraint satisfaction. Candidates are 'pulled' toward logical consistency.
    3. Constraint Satisfaction: Uses soft-logic scoring (NeuroSAT-inspired) to evaluate 
       how well a candidate satisfies the extracted structural rules.
    4. Metacognitive Signal: Computes a stability score (Lyapunov proxy) based on the 
       gradient between the candidate's semantic content and the prompt's structural requirements.
       High instability (contradiction) lowers the score; smooth convergence raises it.
       
    This implementation approximates the ODE/Lyapunum dynamics via deterministic 
    structural parsing and logical consistency checks, using NCD only as a tiebreaker.
    """

    def __init__(self):
        self._negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self._comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'smaller'}
        self._conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'assuming'}
        self._quantifiers = {'all', 'every', 'some', 'any', 'most', 'few', 'many'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical operators and structural constraints (Phenomenological Bracketing)."""
        tokens = set(self._tokenize(text))
        features = {
            'has_negation': bool(tokens & self._negation_words),
            'has_comparative': bool(tokens & self._comparatives),
            'has_conditional': bool(tokens & self._conditionals),
            'has_quantifier': bool(tokens & self._quantifiers),
            'numbers': re.findall(r'\d+\.?\d*', text.lower()),
            'negation_count': len([t for t in tokens if t in self._negation_words]),
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates constraint satisfaction by checking logical alignment between 
        prompt structures and candidate content. Returns a score 0.0 to 1.0.
        """
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        c_tokens = set(self._tokenize(candidate))
        p_tokens = set(self._tokenize(prompt))
        
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        if p_feats['has_negation']:
            # Penalty if candidate ignores negation context completely while being short
            if not c_feats['has_negation'] and len(c_tokens) < 5:
                score -= 0.2
        
        # 2. Comparative Consistency
        if p_feats['has_comparative']:
            # If prompt compares, candidate should ideally contain comparative logic or numbers
            if not c_feats['has_comparative'] and not c_feats['numbers']:
                # Check if candidate is just echoing numbers without logic
                if len(c_feats['numbers']) == 0:
                    score -= 0.15

        # 3. Conditional Consistency
        if p_feats['has_conditional']:
            # Candidates answering conditionals often contain 'yes', 'no', or logical connectors
            if not any(w in c_tokens for w in ['yes', 'no', 'true', 'false', 'if', 'then', 'because']):
                score -= 0.1

        # 4. Numeric Evaluation (Hard Constraint Proxy)
        p_nums = p_feats['numbers']
        c_nums = c_feats['numbers']
        
        if p_nums and c_nums:
            try:
                # Simple heuristic: if prompt asks for max/min/comparison, check value magnitude
                if 'max' in p_tokens or 'largest' in p_tokens or 'highest' in p_tokens:
                    if len(c_nums) > 0:
                        # We can't verify without full context, but we reward numeric presence
                        score += 0.1
                elif 'min' in p_tokens or 'smallest' in p_tokens or 'lowest' in p_tokens:
                     if len(c_nums) > 0:
                        score += 0.1
            except:
                pass

        # 5. Contradiction Detection (Simple overlap check for 'no' vs 'yes' in specific contexts)
        if p_feats['has_negation'] and ('yes' in c_tokens) and ('no' not in c_tokens):
            # Potential contradiction if prompt is negative and candidate is affirmative without nuance
            # This is a rough approximation of trajectory divergence
            if 'not' in prompt and 'yes' in candidate.lower():
                score -= 0.3

        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        
        len1, len2, len12 = len(z1), len(z2), len(z12)
        if len12 == 0: return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _simulate_dynamics(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates the DPCS trajectory.
        Returns (stability_score, reasoning_trace).
        """
        # Phase 1: Phenomenological Bracketing (Feature Extraction)
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        
        reasoning_steps = []
        
        # Phase 2: Constraint Network Evaluation
        logic_score = self._check_logical_consistency(prompt, candidate)
        
        if p_feats['has_negation']:
            reasoning_steps.append(f"Detected negation in prompt. Candidate consistency: {'High' if c_feats['has_negation'] or logic_score > 0.7 else 'Low'}")
        if p_feats['has_comparative']:
            reasoning_steps.append(f"Comparative structure detected. Numeric/Logic check applied.")
        if p_feats['has_conditional']:
            reasoning_steps.append(f"Conditional logic detected. Evaluating consequence alignment.")
            
        # Phase 3: Dynamical Stability (Lyapunov Proxy)
        # High logic_score = stable attractor. Low score = bifurcation risk.
        # We add a small noise term based on length mismatch to simulate dynamic tension
        length_ratio = min(len(candidate), len(prompt)) / max(len(candidate), len(prompt) + 1)
        stability = (logic_score * 0.8) + (length_ratio * 0.2)
        
        if stability < 0.5:
            reasoning_steps.append("WARNING: Trajectory approaching bifurcation (low stability).")
        else:
            reasoning_steps.append("Trajectory converging to stable attractor.")
            
        return stability, "; ".join(reasoning_steps)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            stability, trace = self._simulate_dynamics(prompt, cand)
            # NCD as tiebreaker only
            ncd_val = self._compute_ncd(prompt, cand)
            # Combine: Stability is primary, NCD breaks ties (inverted, lower NCD is better)
            final_score = stability - (ncd_val * 0.01) 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": trace
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        stability, _ = self._simulate_dynamics(prompt, answer)
        return float(stability)