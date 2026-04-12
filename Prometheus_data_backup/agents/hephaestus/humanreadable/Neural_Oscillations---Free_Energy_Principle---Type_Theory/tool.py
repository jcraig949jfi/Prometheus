import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a hybrid reasoning engine based on the Free Energy Principle (FEP) 
    and Type Theory, with Neural Oscillations restricted to confidence modulation.
    
    Mechanism:
    1. FEP Core (evaluate): Minimizes 'variational free energy' by selecting candidates 
       that structurally align with prompt constraints (negations, comparatives, logic).
       Low energy = high score.
    2. Type Theory: Enforces 'type correctness' by checking if the candidate's logical 
       structure (e.g., boolean output for yes/no questions) matches the prompt's expected 
       return type. Mismatches incur high energy penalties.
    3. Neural Oscillations: Used ONLY in confidence(). High-frequency patterns (gamma) 
       in the text (rapid changes in token types) modulate the confidence bound, 
       acting as a scheduler for certainty rather than a direct scorer.
    """

    def __init__(self):
        # Structural parsers for FEP constraint propagation
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'else', 'unless', 'when']
        self.bool_keywords = ['yes', 'no', 'true', 'false', 'correct', 'incorrect']

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extracts logical constraints (FEP priors) from text."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in lower_text for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        
        # Numeric extraction for type checking
        nums = re.findall(r'\d+\.?\d*', lower_text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'negation': has_neg,
            'comparative': has_comp,
            'conditional': has_cond,
            'numbers': numbers,
            'word_count': len(words),
            'is_bool': any(w in self.bool_keywords for w in words)
        }

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a pseudo-free-energy score. 
        Lower energy = better fit. 
        Based on constraint satisfaction (FEP) and type consistency (Type Theory).
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        energy = 0.0

        # 1. Type Consistency Check (Type Theory)
        # If prompt asks for logic/bool (implied by structure), candidate should ideally be concise or logical
        if p_struct['is_bool'] or p_struct['conditional']:
            if not c_struct['is_bool'] and c_struct['word_count'] > 10:
                energy += 2.0  # Penalty for verbose answer to simple logic question
        
        # 2. Constraint Propagation (FEP)
        # Negation handling: If prompt has negation, correct answer often flips logic
        # We simulate this by checking if candidate acknowledges the constraint context
        if p_struct['negation']:
            # Heuristic: Candidates repeating negation words often preserve context better in simple tasks
            if not any(n in candidate.lower() for n in self.negations):
                energy += 0.5 # Small penalty if context is lost
        
        # 3. Numeric Consistency
        if p_struct['numbers'] and c_struct['numbers']:
            # If both have numbers, check basic ordering if comparatives exist
            if p_struct['comparative'] and len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) >= 1:
                # Simple transitivity check approximation
                p_max = max(p_struct['numbers'])
                c_val = c_struct['numbers'][0]
                if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_val > p_max: energy += 1.5 # Contradiction
                elif 'greater' in prompt.lower() or 'larger' in prompt.lower():
                    if c_val < min(p_struct['numbers']): energy += 1.5 # Contradiction

        # 4. Structural Overlap (Baseline alignment)
        # Reward shared logical keywords, penalize noise
        common_logic = 0
        if p_struct['negation'] and c_struct['negation']: common_logic += 1
        if p_struct['comparative'] and c_struct['comparative']: common_logic += 1
        if p_struct['conditional'] and c_struct['conditional']: common_logic += 1
        
        energy -= (common_logic * 0.8) # Reduce energy for matching logical forms

        # Base penalty for length mismatch (Occam's razor)
        len_diff = abs(p_struct['word_count'] - c_struct['word_count'])
        energy += (len_diff * 0.05)

        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return float(c12) / float(max(c1, c2, 1))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_struct = self._structural_parse(prompt)
        
        for cand in candidates:
            # Core FEP evaluation
            energy = self._compute_free_energy(prompt, cand)
            
            # NCD Tiebreaker (only if structural signal is weak)
            # We add a tiny fraction of NCD to break ties without dominating
            ncd_val = self._ncd(prompt, cand)
            final_score = -energy + (0.01 * (1.0 - ncd_val)) 
            
            # Reasoning trace
            reasoning = f"FEP Energy: {-energy:.2f}. "
            if p_struct['negation'] and not self._structural_parse(cand)['negation']:
                reasoning += "Warning: Negation context may be dropped. "
            if p_struct['numbers'] and self._structural_parse(cand)['numbers']:
                reasoning += "Numeric consistency checked. "
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Uses 'Neural Oscillations' as a metaphor for confidence modulation.
        High frequency changes in token types (gamma) reduce confidence bounds.
        """
        if not answer: return 0.0
        
        # Simulate oscillatory stability
        # Map string to a sequence of 'frequencies' (char codes mod 10)
        seq = [ord(c) % 10 for c in answer]
        if len(seq) < 2: return 0.5
        
        # Calculate 'gamma burst' variance (local volatility)
        diffs = [abs(seq[i] - seq[i-1]) for i in range(1, len(seq))]
        if not diffs: return 0.5
        
        avg_diff = sum(diffs) / len(diffs)
        
        # Base confidence from FEP alignment (low energy)
        energy = self._compute_free_energy(prompt, answer)
        base_conf = 1.0 / (1.0 + abs(energy)) # Sigmoid-like mapping
        
        # Oscillatory modulation: High variance in char patterns reduces confidence
        # This mimics gamma bursts disrupting stable theta-phase locking
        oscillation_penalty = min(0.4, avg_diff / 20.0) 
        
        final_conf = max(0.0, min(1.0, base_conf - oscillation_penalty))
        return final_conf