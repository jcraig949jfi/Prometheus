import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Adaptive Resonance System with Epigenetic Metaplasticity.
    
    Mechanism:
    1. RG Coarse-Graining: Parses text into structural tokens (negations, comparatives, 
       numerics) representing macroscopic features, ignoring micro-variations (whitespace, case).
    2. Epigenetic Metaplasticity: Maintains a slow-changing 'stability trace' for structural 
       patterns. High stability reduces the learning rate (plasticity), making established 
       beliefs resistant to noise but allowing rapid updates when contradictions occur.
    3. Oscillatory Gating: Simulates Theta-Gamma coupling.
       - Theta Phase (Meta-update): Evaluates global consistency between prompt and candidate.
       - Gamma Phase (Binding): Rapidly binds local structural matches (e.g., number comparisons).
    
    Scoring:
    Primary signal comes from structural parsing (logic, numbers, constraints).
    NCD (Compression) is used strictly as a tie-breaker for low-confidence scenarios.
    """

    def __init__(self):
        # Epigenetic traces: Dict mapping structural pattern hashes to stability (0-1)
        self.epigenetic_traces: Dict[int, float] = {}
        self.trace_decay = 0.95  # Slow forgetting of stability
        self.learning_rate_base = 0.5
        
        # Structural keywords for coarse-graining
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        
    def _coarse_grain(self, text: str) -> Tuple[set, dict]:
        """
        RG Step: Extract high-level structural features (macroscopic state).
        Returns a set of flags and a dict of numeric values found.
        """
        clean = text.lower()
        words = set(re.findall(r'\b\w+\b', clean))
        
        flags = set()
        if words.intersection(self.negations): flags.add('has_negation')
        if words.intersection(self.comparatives): flags.add('has_comparative')
        if words.intersection(self.conditionals): flags.add('has_conditional')
        
        # Extract numbers for numeric evaluation
        nums = {}
        for match in re.finditer(r'(\d+\.?\d*)', text):
            val = float(match.group())
            # Simple hash of position context as key
            key = f"num_{match.start()}"
            nums[key] = val
            
        return flags, nums

    def _oscillatory_gate(self, p_flags: set, c_flags: set, p_nums: dict, c_nums: dict) -> float:
        """
        Oscillatory Gating: Theta-Gamma coupling simulation.
        Theta: Global structural alignment.
        Gamma: Local numeric binding.
        """
        score = 0.0
        
        # Theta Phase: Structural Resonance
        # Reward matching structural categories (e.g., both have negation)
        common_flags = p_flags.intersection(c_flags)
        if common_flags:
            score += 0.3 * len(common_flags)
        
        # Penalty for structural mismatch (e.g., prompt has conditional, candidate doesn't)
        if 'has_conditional' in p_flags and 'has_conditional' not in c_flags:
            score -= 0.4
            
        # Gamma Phase: Numeric Binding
        if p_nums and c_nums:
            # Check if relative order is preserved (simple transitivity check)
            p_vals = sorted(p_nums.values())
            c_vals = sorted(c_nums.values())
            if len(p_vals) == len(c_vals):
                # Do they agree on magnitude direction?
                p_dir = 1 if p_vals[-1] > p_vals[0] else -1 if p_vals else 0
                c_dir = 1 if c_vals[-1] > c_vals[0] else -1 if c_vals else 0
                if p_dir == c_dir and p_dir != 0:
                    score += 0.4
        
        return score

    def _update_epigenetics(self, pattern_hash: int, resonance: float):
        """
        Epigenetic Update: Adjust stability trace based on resonance.
        High resonance -> increased stability (methylation).
        Low resonance -> decreased stability (demethylation).
        """
        current_stability = self.epigenetic_traces.get(pattern_hash, 0.5)
        
        # Metaplasticity: Learning rate depends on current stability
        # Stable patterns change slowly; unstable patterns change quickly
        plasticity = self.learning_rate_base * (1.0 - current_stability)
        
        # Update rule
        target = 1.0 if resonance > 0 else 0.0
        new_stability = current_stability + plasticity * (target - current_stability)
        
        # Clamp and decay
        new_stability = max(0.0, min(1.0, new_stability))
        self.epigenetic_traces[pattern_hash] = new_stability * self.trace_decay + (1-self.trace_decay)*0.5

    def _get_stability_weight(self, text: str) -> float:
        """Retrieve aggregated stability weight for the structural patterns in text."""
        flags, _ = self._coarse_grain(text)
        if not flags:
            return 0.5
        
        total_weight = 0.0
        for flag in flags:
            h = hash(flag)
            total_weight += self.epigenetic_traces.get(h, 0.5)
            
        return total_weight / len(flags)

    def _ncd_tiebreaker(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            ncd = (c12 - min(c1, c2)) / denom
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_flags, p_nums = self._coarse_grain(prompt)
        p_hash = hash(str(sorted(p_flags)) + str(sorted(p_nums.keys())))
        
        for cand in candidates:
            c_flags, c_nums = self._coarse_grain(cand)
            
            # 1. Oscillatory Gating Score (Primary Signal)
            resonance = self._oscillatory_gate(p_flags, c_flags, p_nums, c_nums)
            
            # 2. Epigenetic Weighting (Metaplasticity)
            # Weight the resonance by the stability of the patterns involved
            stability = self._get_stability_weight(prompt + " " + cand)
            base_score = resonance * (0.5 + 0.5 * stability)
            
            # Update traces based on this interaction
            self._update_epigenetics(p_hash, resonance)
            
            # 3. NCD Tiebreaker (Only if structural signal is weak/ambiguous)
            final_score = base_score
            if abs(base_score) < 0.1: 
                ncd_sim = self._ncd_tiebreaker(prompt, cand)
                # NCD is weak, so it only nudges the score slightly
                final_score = base_score + (ncd_sim - 0.5) * 0.05 
            
            # Normalize to 0-1 range roughly
            norm_score = 0.5 + (final_score * 0.5)
            norm_score = max(0.0, min(1.0, norm_score))
            
            results.append({
                "candidate": cand,
                "score": norm_score,
                "reasoning": f"Structural resonance: {resistance:.2f}, Stability: {stability:.2f}" if (resistance := resonance) else f"Structural resonance: {resonance:.2f}, Stability: {stability:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        p_flags, p_nums = self._coarse_grain(prompt)
        c_flags, c_nums = self._coarse_grain(answer)
        
        resonance = self._oscillatory_gate(p_flags, c_flags, p_nums, c_nums)
        stability = self._get_stability_weight(prompt + " " + answer)
        
        # Combine resonance and stability
        raw_conf = resonance * (0.5 + 0.5 * stability)
        
        # Map to 0-1
        conf = 0.5 + (raw_conf * 0.5)
        return max(0.0, min(1.0, conf))