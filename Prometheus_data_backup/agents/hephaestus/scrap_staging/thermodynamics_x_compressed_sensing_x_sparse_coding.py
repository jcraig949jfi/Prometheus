import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Regularized Sparse Inference Engine.
    
    Mechanism:
    1. Structural Parsing (Data Fidelity): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored by how 
       well they satisfy these hard logical constraints.
    2. Compressed Sensing Analogy (Sparsity): Treats the candidate answer as a 
       'recovery' of the prompt's intent. We penalize candidates that introduce 
       unnecessary complexity or fail to align with the 'measurements' (key tokens).
    3. Thermodynamic Regularization (Energy Cost): Implements an energy penalty 
       proportional to the 'work' required to maintain the hypothesis. 
       Energy = (Complexity * Entropy). 
       - Complexity: Length of deviation from prompt vocabulary.
       - Entropy: Disorder in token distribution (approximated by char frequency).
       Low-energy, high-fidelity candidates are favored (Occam's Razor).
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparators = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """Scores based on structural parsing of negations, comparatives, and numbers."""
        score = 1.0
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        p_lower = prompt.lower()
        c_lower = candidate.lower()

        # 1. Negation Check
        # If prompt has negation, candidate should ideally reflect it or not contradict it
        has_p_neg = any(n in p_tokens for n in self.negation_words)
        has_c_neg = any(n in c_tokens for n in self.negation_words)
        
        if has_p_neg and not has_c_neg:
            # Potential contradiction if candidate ignores negation context
            # Soft penalty unless it's a direct yes/no trap
            if any(w in c_lower for w in ['yes', 'true', 'correct']):
                score -= 0.4

        # 2. Numeric Consistency
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check basic ordering if comparators exist
            has_comp = any(c in p_tokens for c in self.comparators)
            if has_comp:
                # Simple heuristic: if prompt says "greater", candidate number should be greater
                # This is a simplified proxy for full logical deduction
                if 'greater' in p_tokens or 'larger' in p_tokens or '>' in prompt:
                    if c_nums[-1] < p_nums[-1]: # Rough heuristic
                        score -= 0.3
                elif 'less' in p_tokens or 'smaller' in p_tokens or '<' in prompt:
                    if c_nums[-1] > p_nums[-1]:
                        score -= 0.3
        
        # 3. Conditional Presence
        if any(cond in p_tokens for cond in self.conditionals):
            # Candidate should ideally contain conditional markers or logical consequence words
            if not any(cond in c_tokens for cond in self.conditionals) and \
               not any(w in c_tokens for w in ['therefore', 'thus', 'so', 'result']):
                score -= 0.1 # Soft penalty for ignoring conditional structure

        return max(0.0, score)

    def _compute_thermodynamic_cost(self, prompt: str, candidate: str) -> float:
        """
        Computes an energy cost based on Landauer's principle analogy.
        Cost = k * (Sparsity Penalty + Entropy Penalty)
        Lower cost is better.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        p_set = set(p_tokens)
        
        # 1. Sparsity/Compression Cost (Compressed Sensing analogy)
        # How many tokens in candidate are NOT in the prompt's 'dictionary'?
        # A true sparse recovery should use the basis vectors (prompt words) efficiently.
        new_tokens = [t for t in c_tokens if t not in p_set]
        sparsity_penalty = len(new_tokens) / (len(c_tokens) + 1e-6)
        
        # 2. Entropy Cost (Thermodynamics)
        # Calculate Shannon entropy of character distribution in candidate
        if not candidate:
            entropy = 0.0
        else:
            freq = {}
            for char in candidate.lower():
                if char.isalpha():
                    freq[char] = freq.get(char, 0) + 1
            total_chars = sum(freq.values())
            entropy = 0.0
            if total_chars > 0:
                for count in freq.values():
                    p = count / total_chars
                    if p > 0:
                        entropy -= p * math.log2(p)
            # Normalize entropy by max possible (log2 of unique chars)
            max_entropy = math.log2(len(freq) + 1) if len(freq) > 0 else 1
            entropy = entropy / (max_entropy + 1e-6)

        # Total Energy (Work required to sustain this hypothesis)
        # Beta weights the entropy term
        beta = 0.5
        energy = sparsity_penalty + beta * entropy
        return energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if min(z1, z2) == 0:
            return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Logical Consistency (Data Fidelity Term)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Thermodynamic Cost (Regularization Term)
            energy_cost = self._compute_thermodynamic_cost(prompt, cand)
            
            # 3. NCD Tiebreaker (Secondary)
            # We want low NCD (high similarity) but logic is primary
            ncd = self._ncd_distance(prompt, cand)
            
            # Combined Score:
            # High Logic, Low Energy, Low NCD (similar context)
            # Score = (Logic * 0.6) + ((1 - Energy) * 0.3) + ((1 - ncd) * 0.1)
            # Note: Energy can be > 1, so we clamp or scale. 
            # Let's normalize energy impact: exp(-energy)
            
            thermodynamic_fit = math.exp(-energy_cost)
            ncd_fit = 1.0 - min(1.0, ncd)
            
            final_score = (logic_score * 0.60) + (thermodynamic_fit * 0.30) + (ncd_fit * 0.10)
            
            reasoning = f"Logic:{logic_score:.2f} Energy:{energy_cost:.2f} NCD:{ncd:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score of the single answer."""
        # Evaluate against a dummy set containing just the answer to get relative scoring
        # But since we need absolute confidence, we rely on the internal metrics directly
        
        logic_score = self._check_logical_consistency(prompt, answer)
        energy_cost = self._compute_thermodynamic_cost(prompt, answer)
        thermodynamic_fit = math.exp(-energy_cost)
        
        # Weighted combination similar to evaluate
        raw_conf = (logic_score * 0.7) + (thermodynamic_fit * 0.3)
        
        # Clamp to 0-1
        return max(0.0, min(1.0, raw_conf))