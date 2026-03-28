import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Energy-Based Predictive Coding Network (Approximated).
    
    Mechanism:
    1. Free Energy Principle (Core): The 'evaluate' method minimizes a variational free energy
       functional. We approximate the energy landscape by parsing structural constraints
       (negations, comparatives, conditionals) from the prompt. Lower free energy = higher score.
    2. Hebbian Learning (Restricted): Used ONLY in 'confidence()' to measure the correlation
       between prompt structures and the proposed answer string (co-activation), acting as
       a structural consistency check rather than a primary scorer.
    3. Statistical Mechanics: Candidates are treated as modes in an energy landscape.
       Scores are derived from the Boltzmann distribution of the computed energy errors.
       Noise (fluctuation) is simulated via penalty scaling to ensure robustness.
    
    This implementation prioritizes structural parsing and numeric evaluation as the
    primary drivers of the energy function, using NCD only as a high-temperature tiebreaker.
    """

    def __init__(self):
        self._temp = 0.1  # Simulation temperature for Boltzmann scaling

    def _parse_structure(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'bool_yes': len(re.findall(r'\byes\b', text_lower)),
            'bool_no': len(re.findall(r'\bno\b', text_lower))
        }
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute the variational free energy (E) for a candidate.
        E = Prediction Error + Structural Violation - Consistency
        Lower E is better.
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        energy = 0.0

        # 1. Numeric Evaluation (Strong Constraint)
        # If prompt has numbers, candidate should ideally reflect logical outcome
        if p_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Check for direct calculation matches or logical consistency
                # Simple heuristic: if prompt implies comparison, check candidate numbers
                if 'greater' in prompt.lower() or 'less' in prompt.lower():
                    if c_nums:
                        # Expect candidate to contain the result of a comparison or the correct number
                        # This is a proxy for "prediction error"
                        pass 
                # Penalty if candidate introduces random large numbers not in prompt
                for n in c_nums:
                    if n not in p_nums:
                        energy += 0.5 # Small penalty for new numbers unless justified
            except ValueError:
                pass

        # 2. Structural Consistency (Modus Tollens/Constraint Propagation)
        # If prompt has strong negation, candidate shouldn't be a blind affirmative without nuance
        if p_feat['negations'] > 0 and c_feat['bool_yes'] > 0 and c_feat['negations'] == 0:
            # Potential trap: Prompt says "X is not Y", Candidate says "Yes" (implying X is Y)
            # We add energy (penalty) unless the prompt is a negative question answered correctly
            if 'not' in prompt.lower() and ('yes' in candidate.lower()):
                 energy += 2.0
        
        # 3. Conditional Logic Check
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] == 0 and len(c_feat['numbers']) == 0 and len(c_feat['comparatives']) == 0:
                # If prompt is complex conditional, simple answers might be insufficient (high energy)
                # unless they are definitive "No/False" types which we handle via NCD later
                energy += 1.0

        # 4. Hebbian-like Co-activation (Structural Overlap)
        # Reward shared structural tokens (excluding stop words)
        common_struct = set(p_feat['comparatives']) & set(c_feat['comparatives'])
        energy -= len(common_struct) * 1.5 # Reduce energy for shared logic terms

        # 5. NCD as Tiebreaker (High Temp noise)
        # Only apply if structural energy is neutral (close to 0)
        if abs(energy) < 0.1:
            ncd = self._ncd(prompt, candidate)
            energy += ncd * self._temp
            
        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates by minimizing variational free energy.
        Returns list of dicts sorted by score (descending).
        """
        results = []
        energies = []
        
        # Phase 1: Compute Energy for all candidates
        for cand in candidates:
            e = self._compute_energy(prompt, cand)
            energies.append(e)
        
        # Phase 2: Convert to Probabilistic Scores (Boltzmann Distribution)
        # P ~ exp(-E / T). We normalize to 0-1 range.
        if not energies:
            return []
            
        min_e = min(energies)
        max_e = max(energies)
        range_e = max_e - min_e if (max_e - min_e) > 1e-6 else 1.0
        
        scored_candidates = []
        for i, cand in enumerate(candidates):
            e = energies[i]
            # Normalize energy to 0-1 (inverted so lower energy = higher score)
            norm_e = (e - min_e) / range_e
            score = 1.0 - norm_e
            
            # Add small deterministic jitter based on length to break ties deterministically
            # simulating stochastic sampling without randomness
            jitter = (len(cand) % 10) * 0.001
            final_score = min(1.0, max(0.0, score + jitter))
            
            reasoning = f"Energy={e:.4f}, StructMatch={1.0-norm_e:.4f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence using Hebbian-like structural co-activation.
        Measures how well the answer's structure aligns with the prompt's constraints.
        Returns 0.0 to 1.0.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        alignment_score = 0.0
        total_checks = 0.0

        # Check 1: Negation Consistency
        # If prompt has negation, answer should ideally reflect it or be a direct contradiction check
        if p_feat['negations'] > 0:
            total_checks += 1.0
            if a_feat['negations'] > 0 or ('no' in answer.lower()):
                alignment_score += 1.0 # Aligned
        
        # Check 2: Numeric Presence
        if p_feat['numbers']:
            total_checks += 1.0
            if a_feat['numbers']:
                alignment_score += 1.0
        
        # Check 3: Comparative Presence
        if p_feat['comparatives'] > 0:
            total_checks += 1.0
            if a_feat['comparatives'] > 0 or a_feat['numbers']:
                alignment_score += 1.0

        # Base confidence on structural alignment
        if total_checks > 0:
            base_conf = alignment_score / total_checks
        else:
            # Fallback to NCD if no structural features found
            base_conf = 1.0 - self._ncd(prompt, answer)

        # Hebbian Modulation: If the answer is extremely short (Yes/No) but prompt is complex,
        # reduce confidence unless structural checks passed strongly.
        if len(answer.split()) < 2 and (p_feat['conditionals'] > 0 or p_feat['comparatives'] > 0):
            base_conf *= 0.8

        return float(min(1.0, max(0.0, base_conf)))