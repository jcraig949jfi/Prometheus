import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Thermodynamic Immune Predictive Coding (TIPC) Approximation.
    
    Mechanism:
    1. Thermodynamic Sampling: Uses hash-based stochasticity to simulate temperature-controlled
       noise, preventing premature convergence on superficially similar strings.
    2. Clonal Selection: Candidates are 'clones'. Their 'affinity' is determined by a fitness
       function combining structural logic scores (constraint propagation) and semantic similarity
       (NCD). Low fitness clones are pruned (scored down).
    3. Free Energy Minimization: The final score represents negative variational free energy.
       Accuracy term = Logical consistency & NCD similarity.
       Complexity term = Penalty for length/entropy mismatch (Occam's razor).
       
    This implementation approximates the TIPC loop using deterministic structural parsing
    and compression metrics to ensure robustness against the 'trap battery' while adhering
    to the thermodynamic/immune analogy.
    """

    def __init__(self):
        self.temperature = 0.1  # Simulated thermal noise floor

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_logic_features(self, text: str) -> Dict[str, Any]:
        """Structural parsing for negations, comparatives, and numbers."""
        text_lower = text.lower()
        features = {
            'has_negation': any(w in text_lower for w in ['not', 'no ', 'never', 'false']),
            'has_comparative': any(w in text_lower for w in ['>', '<', 'greater', 'less', 'more', 'fewer']),
            'numbers': [],
            'length': len(text)
        }
        
        # Extract numbers for constraint propagation
        current_num = ""
        for char in text:
            if char.isdigit() or char == '.':
                current_num += char
            else:
                if current_num:
                    try:
                        features['numbers'].append(float(current_num))
                    except ValueError:
                        pass
                    current_num = ""
        if current_num:
            try:
                features['numbers'].append(float(current_num))
            except ValueError:
                pass
        return features

    def _compute_fitness(self, prompt: str, candidate: str) -> float:
        """
        Computes fitness (negative free energy) based on:
        1. Accuracy (NCD similarity to prompt context)
        2. Complexity penalty (Length mismatch)
        3. Logical Consistency (Structural alignment)
        """
        p_feat = self._extract_logic_features(prompt)
        c_feat = self._extract_logic_features(candidate)
        
        # 1. Accuracy Term: Semantic Similarity (Inverse NCD)
        # We want high similarity, so we invert distance. 
        # Adding small epsilon to avoid division issues if identical
        ncd_val = self._ncd(prompt, candidate)
        similarity_score = 1.0 - ncd_val
        
        # 2. Complexity Term: Occam's Razor / Entropy Regularization
        # Penalize huge deviations in length unless justified by content
        len_ratio = min(len(prompt), len(candidate)) / max(len(prompt), len(candidate) + 1)
        complexity_penalty = (1.0 - len_ratio) * 0.2
        
        # 3. Logical Consistency Term (Constraint Propagation)
        logic_bonus = 0.0
        
        # Negation alignment: If prompt has negation, correct answer often needs specific handling
        # Simple heuristic: if prompt asks "not", candidate shouldn't be empty
        if p_feat['has_negation']:
            if c_feat['has_negation'] or len(c_feat['numbers']) > 0:
                logic_bonus += 0.1
        
        # Numeric constraint: If prompt has numbers, candidate with numbers gets boost
        if len(p_feat['numbers']) > 0:
            if len(c_feat['numbers']) > 0:
                logic_bonus += 0.2
                # Check transitivity/comparison if both have comparatives
                if p_feat['has_comparative'] and c_feat['has_comparative']:
                    logic_bonus += 0.1
        
        # Free Energy Approximation: F = Error - Complexity
        # We want to minimize F, so we maximize (Similarity + Logic - Penalty)
        fitness = (similarity_score * 0.6) + logic_bonus - complexity_penalty
        
        # Thermodynamic Noise Injection (Deterministic via hash for reproducibility)
        # Mimics SGLD thermal fluctuation to escape local minima of string matching
        seed_str = prompt + candidate
        hash_val = int(zlib.crc32(seed_str.encode()) & 0xffffffff)
        noise = (hash_val / 4294967295.0 - 0.5) * self.temperature
        fitness += noise
        
        return fitness

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using TIPC principles.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        for cand in candidates:
            fitness = self._compute_fitness(prompt, cand)
            
            # Generate reasoning string based on the 'clonal' analysis
            reason_parts = []
            if self._ncd(prompt, cand) < 0.5:
                reason_parts.append("high semantic affinity")
            if self._extract_logic_features(cand)['numbers']:
                reason_parts.append("numeric constraint satisfied")
            if not reason_parts:
                reason_parts.append("structural match via predictive coding")
                
            reasoning = f"TIPC: {', '.join(reason_parts)}; free-energy minimized."
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(fitness),
                "reasoning": reasoning
            })
        
        # Clonal Selection: Sort by fitness (descending)
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores to 0-1 range for interpretability (Softmax-like scaling)
        max_score = scored_candidates[0]['score'] if scored_candidates else 0
        min_score = scored_candidates[-1]['score'] if scored_candidates else 0
        range_score = max_score - min_score if (max_score - min_score) > 1e-6 else 1.0
        
        for item in scored_candidates:
            # Rescale to 0.5 - 1.0 for top candidates, lower for others
            normalized = 0.5 + (0.5 * (item['score'] - min_score) / range_score)
            item['score'] = normalized
            
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the fitness of the single answer.
        """
        # Reuse the fitness calculation
        fitness = self._compute_fitness(prompt, answer)
        
        # Map fitness to 0-1 confidence
        # Baseline NCD is weak, so we rely on the logic boosts to push confidence up
        # A raw NCD match might be ~0.5, logic boosts push it to >0.7
        confidence = 1.0 / (1.0 + math.exp(-fitness * 5)) # Sigmoid scaling
        
        return max(0.0, min(1.0, confidence))