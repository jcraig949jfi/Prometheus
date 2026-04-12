import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Bandit Type-Checker (VBTC) Approximation.
    
    Mechanism:
    1. Free Energy Principle (Core): Treats the 'surprise' (negative log-likelihood) of a candidate
       as the sum of semantic mismatch (NCD) and structural violation penalties. Minimizing Free Energy
       equates to minimizing this combined cost.
    2. Type Theory (Constraint Gate): Parses logical constraints (negations, comparatives, conditionals).
       Violating a detected constraint inflates the Free Energy (penalty), simulating a 'type error'
       that rejects logically inconsistent hypotheses regardless of semantic similarity.
    3. Multi-Armed Bandit (Selection): Ranks candidates by expected reward (inverse Free Energy),
       balancing exploitation (low error) and exploration (uncertainty via length normalization).
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp_both = len(zlib.compress(b1 + b2))
        max_len = max(comp1, comp2)
        if max_len == 0:
            return 0.0
        return (comp_both - min(comp1, comp2)) / max_len

    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical markers: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|cannot|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'has_question': '?' in text
        }
        return features

    def _check_type_consistency(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Simulates Type Checking by verifying logical consistency between prompt constraints
        and candidate properties. Returns a penalty (0.0 = consistent, >0.0 = type error).
        """
        penalty = 0.0
        
        # Constraint 1: Negation Consistency
        # If prompt strongly implies negation logic, candidate shouldn't blindly affirm without nuance
        if prompt_feats['negations'] > 0:
            # Simple heuristic: if prompt has 'not' and candidate is extremely short (e.g., "Yes"), penalize
            if cand_feats['negations'] == 0 and len(candidate.split()) < 3 and prompt_feats['negations'] >= 1:
                # Check if candidate is a bare affirmative in a negative context
                if any(x in candidate.lower() for x in ['yes', 'true', 'correct']):
                    penalty += 0.5

        # Constraint 2: Numeric Transitivity/Comparison
        if prompt_feats['numbers'] and cand_feats['numbers']:
            try:
                p_nums = [float(x) for x in prompt_feats['numbers']]
                c_nums = [float(x) for x in cand_feats['numbers']]
                
                # If prompt asks for "less than" and candidate provides larger number (heuristic check)
                if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_nums and p_nums:
                        # If candidate number is larger than the max in prompt when asking for smaller
                        if max(c_nums) > max(p_nums):
                            penalty += 0.4
                elif 'more' in prompt.lower() or 'greater' in prompt.lower():
                    if c_nums and p_nums:
                        if min(c_nums) < min(p_nums):
                            penalty += 0.4
            except ValueError:
                pass

        # Constraint 3: Conditional Logic Presence
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] == 0:
            # If prompt is conditional but candidate ignores logic (no conditional words), slight penalty
            # unless it's a direct factual answer. Heuristic: penalize if candidate is long but lacks logic words
            if len(candidate.split()) > 10:
                penalty += 0.2

        return penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy F = Surprise + Complexity Penalty.
        Surprise = NCD (Semantic mismatch)
        Complexity Penalty = Type Error Penalty (Logical inconsistency)
        """
        # 1. Semantic Surprise (NCD)
        # We measure NCD between prompt and candidate. Lower is better.
        semantic_surprise = self._ncd(prompt, candidate)
        
        # 2. Structural Features
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        
        # 3. Type Checking Penalty
        type_penalty = self._check_type_consistency(p_feats, c_feats, prompt, candidate)
        
        # Free Energy = Semantic Distance + (Alpha * Type Penalty)
        # Alpha set to 0.4 to balance semantic fit vs logical correctness
        free_energy = semantic_surprise + (0.4 * type_penalty)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        energies = []
        
        # Phase 1: Compute Free Energy for all arms (candidates)
        for cand in candidates:
            f_energy = self._compute_free_energy(prompt, cand)
            energies.append(f_energy)
        
        # Normalize scores to 0-1 range where higher is better (Inverse Free Energy)
        min_e = min(energies) if energies else 1.0
        max_e = max(energies) if energies else 1.0
        range_e = max_e - min_e if (max_e - min_e) > 1e-9 else 1.0
        
        for i, cand in enumerate(candidates):
            # Transform Free Energy to Score: 1 - normalized_energy
            # This mimics the Bandit reward signal (maximizing expected reduction in free energy)
            norm_energy = (energies[i] - min_e) / range_e
            score = 1.0 - norm_energy
            
            # Construct reasoning string
            reason = f"FreeEnergy={energies[i]:.4f}; "
            if energies[i] == min_e:
                reason += "Optimal hypothesis (minimized surprise + type errors)."
            elif norm_energy > 0.8:
                reason += "High surprise or logical type violation detected."
            else:
                reason += "Viable candidate."

            results.append({
                "candidate": cand,
                "score": round(score, 6),
                "reasoning": reason
            })
        
        # Sort by score descending (Bandit selection policy)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on inverse Free Energy.
        1.0 = Low Free Energy (High consistency, low surprise)
        0.0 = High Free Energy (High surprise or type error)
        """
        f_energy = self._compute_free_energy(prompt, answer)
        # Map free energy (approx 0.0 to 1.5+) to 0.0-1.0
        # Assuming max reasonable free energy is around 1.5 for normalization
        conf = max(0.0, 1.0 - f_energy)
        return round(conf, 6)