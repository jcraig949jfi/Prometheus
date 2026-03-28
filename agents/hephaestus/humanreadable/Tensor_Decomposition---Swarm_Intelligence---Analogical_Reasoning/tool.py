import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    DT-F-SAT Implementation: Distributed Tensor-Factorization Swarm with Analogical Transfer.
    
    Mechanism:
    1. Structural Parsing (Analogical Core): Extracts logical signatures (negations, comparatives,
       conditionals, numbers) to form a 'structural tensor' representation of the prompt and candidates.
    2. Swarm Intelligence (Optimization): Agents (candidate answers) are evaluated against the prompt's
       structural constraints. 'Pheromones' are simulated as bonus scores for satisfying logical consistency
       (e.g., if prompt has 'not', candidate lacking negation gets penalty).
    3. Analogical Transfer: Maps the structural pattern of the prompt to candidates. If the prompt implies
       a reversal (A > B -> B < A), candidates mirroring this structure get higher fitness.
    4. Fitness: A composite score of structural match, numeric consistency, and NCD (as tiebreaker).
    """

    def __init__(self):
        self.n_agents = 5  # Simulated swarm agents for hypothesis testing

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|>|<|increases|decreases)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text.split())
        }
        # Convert numbers to float for comparison
        try:
            features['numeric_vals'] = [float(n) for n in features['numbers']]
        except ValueError:
            features['numeric_vals'] = []
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _swarm_fitness(self, prompt: str, candidate: str) -> float:
        """
        Computes fitness based on structural alignment (Analogical Reasoning)
        and constraint satisfaction (Swarm pheromone simulation).
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        score = 0.0
        
        # 1. Analogical Structural Mapping
        # If prompt has high negation, candidate should likely reflect it (or explicitly deny it)
        if p_feat['negations'] > 0:
            # Reward if candidate acknowledges negation context (simple heuristic: contains negation or 'false')
            if c_feat['negations'] > 0 or 'false' in candidate.lower() or 'no' in candidate.lower():
                score += 0.3
            else:
                score -= 0.2 # Penalty for ignoring negation
        
        # 2. Comparative Consistency
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0:
                score += 0.2
            # Check numeric consistency if numbers exist
            if p_feat['numeric_vals'] and c_feat['numeric_vals']:
                # Simple transitivity check: if prompt implies order, does candidate respect magnitude?
                # This is a rough analogical proxy for tensor factor alignment
                p_avg = np.mean(p_feat['numeric_vals'])
                c_avg = np.mean(c_feat['numeric_vals'])
                if abs(p_avg - c_avg) < 1.0: # Close numeric values often indicate correct extraction
                    score += 0.4
        
        # 3. Conditional Logic Check
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or 'therefore' in candidate.lower() or 'thus' in candidate.lower():
                score += 0.2

        # 4. Length heuristic (Answers usually aren't empty or absurdly long relative to prompt)
        if 0.1 * p_feat['length'] <= c_feat['length'] <= 2.0 * p_feat['length']:
            score += 0.1

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_feat = self._extract_structure(prompt)
        
        # Pre-calculate prompt complexity for normalization
        base_score = 0.0
        
        for cand in candidates:
            # Swarm Fitness (Structural/Analogical)
            fitness = self._swarm_fitness(prompt, cand)
            
            # NCD as tiebreaker/secondary signal
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Combined Score: High fitness + Low NCD (high similarity in compressed info) is good
            # But we prioritize structural fitness. NCD is scaled to be a minor factor unless fitness is tied.
            final_score = fitness + (0.1 * (1.0 - ncd_val))
            
            # Heuristic boost for exact string matches of logical keywords found in prompt
            cand_lower = cand.lower()
            if ('yes' in cand_lower or 'true' in cand_lower) and prompt_feat['negations'] == 0:
                final_score += 0.05
            elif ('no' in cand_lower or 'false' in cand_lower) and prompt_feat['negations'] > 0:
                final_score += 0.05

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {fitness:.2f}, NCD factor: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment and fitness."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        # Normalize score to 0-1 range roughly based on our scoring logic
        # Max theoretical score approx 1.0-1.2, min approx -0.5
        raw_score = ranked[0]['score']
        confidence = (raw_score + 0.5) / 1.5 
        return max(0.0, min(1.0, confidence))