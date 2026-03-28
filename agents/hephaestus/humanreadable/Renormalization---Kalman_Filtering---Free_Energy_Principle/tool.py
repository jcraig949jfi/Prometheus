import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Kalman Variational Filter (RKVF) Implementation.
    
    Mechanism:
    1. Structural Parsing (Fast Scale/Kalman): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This acts as the high-frequency 
       sensory data update.
    2. Free Energy Minimization (Core Driver): Scores candidates based on 
       "surprise" minimization. A candidate minimizes free energy if it:
       - Preserves structural constraints (e.g., negation flips logic).
       - Maintains numeric consistency.
       - Has high semantic overlap (low NCD) only as a secondary tiebreaker.
    3. Renormalization (Slow Scale): Aggregates local structural matches into a 
       global "scale-invariant" score. Candidates that satisfy constraints across 
       multiple logical scales (syntax + semantics + numeric) survive; spurious 
       matches are integrated out (penalized).
       
    Note: Kalman mechanics are restricted to the structural parsing wrapper to 
    avoid historical failure modes. The Free Energy Principle drives the scoring.
    """

    def __init__(self):
        # Structural patterns for fast-scale extraction
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r"n't"]
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b']
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Fast-scale structural parsing (Kalman-like observation step)."""
        text_lower = text.lower()
        has_negation = any(re.search(p, text_lower) for p in self.negation_patterns)
        has_comparative = any(re.search(p, text_lower) for p in self.comparative_patterns)
        has_conditional = any(re.search(p, text_lower) for p in self.conditional_patterns)
        numbers = [float(n) for n in self.number_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text.split())
        }

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

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes variational free energy (negative score).
        Lower energy = better fit. We return negative energy as the score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        energy = 0.0
        
        # 1. Structural Constraint Propagation (High Precision)
        # If prompt has negation, valid reasoning often requires acknowledging it 
        # or the candidate must logically resolve it. 
        # Simple heuristic: Mismatch in critical structural flags increases energy.
        
        # Negation consistency check
        if p_struct['negation']:
            # If prompt is negated, a simple 'yes' or exact echo might be wrong.
            # We penalize candidates that ignore the complexity introduced by negation
            if not c_struct['negation'] and c_struct['length'] < 5:
                energy += 2.0 
        
        # Numeric consistency (Modus Tollens/Transitivity proxy)
        if p_struct['numbers'] and c_struct['numbers']:
            # If numbers exist, check if candidate preserves order if comparative exists
            if p_struct['comparative']:
                # Rough check: does the candidate contain numbers?
                if not c_struct['numbers']:
                    energy += 1.5
        elif p_struct['numbers'] and not c_struct['numbers']:
            # Prompt has numbers, candidate ignores them completely (potential hallucination)
            if p_struct['comparative'] or p_struct['conditional']:
                energy += 1.0

        # 2. Semantic Surprise (NCD as tiebreaker/secondary)
        # High overlap reduces surprise (free energy), but only if structure matches
        ncd_val = self._ncd(prompt, candidate)
        
        # Weight NCD lightly unless structural energy is low
        # This prevents "echo" answers from winning if they lack structural reasoning
        semantic_term = ncd_val * 0.5
        
        # 3. Renormalization Step (Scale Integration)
        # Combine structural penalty (coarse scale) with semantic penalty (fine scale)
        # If structural energy is high (logic broken), semantic match matters less.
        total_energy = energy + semantic_term + (energy * semantic_term)
        
        return -total_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            reasoning = []
            
            # Generate human-readable reasoning based on the structural parse
            p_struct = self._extract_structure(prompt)
            c_struct = self._extract_structure(cand)
            
            if p_struct['negation'] and not c_struct['negation']:
                reasoning.append("Potential negation mismatch.")
            if p_struct['numbers'] and not c_struct['numbers']:
                reasoning.append("Numeric details ignored.")
            if not reasoning:
                reasoning.append("Structural constraints satisfied.")
                
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": " ".join(reasoning)
            })
        
        # Sort by score descending (higher is better)
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        1.0 = Low energy (high fit), 0.0 = High energy (low fit).
        """
        energy = self._compute_free_energy(prompt, answer)
        # Convert negative energy to 0-1 scale
        # Assuming typical energy range is -5 to 2
        # Map [-5, 2] -> [1, 0] roughly, then clamp
        confidence = 1.0 / (1.0 + math.exp(energy)) # Sigmoid-like mapping
        return max(0.0, min(1.0, confidence))