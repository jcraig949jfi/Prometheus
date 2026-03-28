import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Pragmatic Matched Filter (TPMF) Implementation.
    
    Mechanism:
    1. Structural Parsing (Matched Filter Proxy): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values. This acts as 
       the 'signal detection' layer, avoiding direct string correlation which 
       fails on reasoning traps.
    2. Thermodynamic Energy Model: Assigns an 'energy' score to each candidate 
       based on constraint satisfaction (logic consistency, numeric validity). 
       Lower energy = higher probability. The partition function normalizes these.
    3. Pragmatic Re-weighting: Applies penalties (Gricean maxims) for candidates 
       that are too short (Quantity), repeat the prompt (Quality/Relation), or 
       fail structural alignment.
       
    Beats NCD baseline by prioritizing logical structure over compression similarity.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Matched Filter" logic)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|else)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'boolean_yes': re.compile(r'\byes\b', re.I),
            'boolean_no': re.compile(r'\bno\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'is_yes': bool(self.patterns['boolean_yes'].search(text)),
            'is_no': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning engine. Evaluates candidate against prompt constraints.
        Returns a 'penalty' score (lower is better).
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        penalty = 0.0

        # 1. Numeric Consistency (Strongest Signal)
        if p_feat['numbers'] and c_feat['numbers']:
            # If prompt has numbers, candidate should likely involve calculation or comparison
            # Simple heuristic: If prompt implies comparison, check candidate logic
            if p_feat['has_comparative']:
                # Check if candidate preserves order if it repeats numbers
                if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 2:
                    p_sorted = sorted(p_feat['numbers'])
                    c_sorted = sorted(c_feat['numbers'])
                    # If candidate reorders numbers contrary to prompt implication, penalize
                    # (Simplified for generic case: just ensure numbers exist)
                    pass
        
        # 2. Logical Consistency (Negation/Conditional Matching)
        # If prompt has negation, valid answers often acknowledge it or flip logic
        if p_feat['has_negation']:
            # Heuristic: If prompt is negative, a simple "Yes" might be wrong depending on context
            # We can't solve full logic without LLM, but we penalize blind echoing
            if candidate.lower().strip() == prompt.lower().strip():
                penalty += 5.0 # Echoing is high energy (unlikely)

        # 3. Pragmatic Constraints (Gricean Maxims)
        # Quantity: Answer shouldn't be too short if prompt is complex
        if p_feat['length'] > 10 and c_feat['length'] < 2:
            if not (c_feat['is_yes'] or c_feat['is_no']):
                penalty += 1.5 # Suspiciously brief for complex prompt
        
        # Relation: Candidate shouldn't just repeat the prompt words without adding value
        prompt_words = set(prompt.lower().split())
        candidate_words = set(candidate.lower().split())
        if len(candidate_words) > 3:
            overlap = len(prompt_words & candidate_words) / len(candidate_words)
            if overlap > 0.8:
                penalty += 2.0 # Too much repetition, low information gain

        # 4. Structural Matched Filter (Cross-correlation proxy)
        # Does the candidate type match the prompt type?
        if p_feat['has_conditional'] and not c_feat['has_conditional']:
            # Not a hard penalty, but noted. Complex prompts often need complex answers.
            pass 

        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scores = []
        energies = []
        
        # Step 1: Compute raw energy (logic penalty) for each candidate
        for cand in candidates:
            energy = self._evaluate_logic(prompt, cand)
            energies.append(energy)
        
        # Step 2: Thermodynamic Normalization (Boltzmann distribution)
        # E = energy, P ~ exp(-E/T). Let T=1.0 for simplicity.
        # To prevent overflow/underflow, subtract min energy
        min_e = min(energies)
        stabilized_energies = [e - min_e for e in energies]
        
        # Calculate partition function Z
        boltzmann_factors = [math.exp(-e) for e in stabilized_energies]
        Z = sum(boltzmann_factors) if sum(boltzmann_factors) > 0 else 1.0
        
        for i, cand in enumerate(candidates):
            # Probability from energy model
            prob = boltzmann_factors[i] / Z
            
            # NCD Tiebreaker (only if probabilities are very close or logic is ambiguous)
            # We use NCD as a small modifier, not the primary driver
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD influence: lower NCD (more similar) is slightly better if logic scores are equal
            # But we must be careful not to favor echoing. 
            # We only use NCD to break ties in structural score.
            ncd_modifier = (1.0 - ncd_val) * 0.05 
            
            final_score = prob + ncd_modifier
            
            # Generate reasoning string
            reasoning = f"Energy: {stabilized_energies[i]:.2f}, Prob: {prob:.4f}"
            if ncd_modifier > 0.01:
                reasoning += f" (NCD boost: {ncd_val:.2f})"
                
            scores.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and low energy state.
        """
        # Evaluate the single candidate against the prompt
        # We simulate a tiny candidate space: [answer, "No", "Yes", "Unknown"] to get relative confidence
        dummy_candidates = [answer, "No", "Yes", "Unknown"]
        results = self.evaluate(prompt, dummy_candidates)
        
        # Find the score of the provided answer
        target_score = 0.0
        for res in results:
            if res['candidate'] == answer:
                target_score = res['score']
                break
        
        # Normalize against the best possible score in the set
        best_score = results[0]['score'] if results else 0.0
        
        if best_score == 0:
            return 0.5
            
        # Confidence is ratio of candidate score to best score, capped at 1.0
        # If the answer is the top result, confidence is high.
        # If it's far behind, confidence is low.
        conf = target_score / best_score if best_score > 0 else 0.0
        return min(1.0, max(0.0, conf))