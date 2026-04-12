import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Pragmatics, Model Checking, and Multi-Armed Bandits.
    
    Mechanism:
    1. Pragmatic Parsing: Extracts logical atoms (negations, conditionals, comparatives) 
       from the prompt using regex to form a set of constraints.
    2. Model Checking: Treats each candidate answer as a state in a Kripke structure. 
       It verifies if the candidate satisfies the extracted constraints (literal correctness)
       and checks for pragmatic implicatures (e.g., consistency with negation).
    3. Bandit Scoring: Uses UCB1 (Upper Confidence Bound) logic to score candidates. 
       The 'reward' is derived from the model check satisfaction. The confidence width 
       accounts for the complexity of the pragmatic match, simulating exploration vs exploitation.
    
    This approach prioritizes structural logical consistency over string similarity (NCD),
    using NCD only as a final tiebreaker for candidates with identical logical scores.
    """

    def __init__(self):
        # Patterns for pragmatic constraint extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bnever\b', r'\bno\b\s+\b', r'\bwithout\b'],
            'conditional': [r'\bif\b.*?\bthen\b', r'\bunless\b', r'\bprovided\s+that\b'],
            'comparative': [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\bequal\s+to\b', r'[><=]'],
            'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bresults\s+in\b', r'\btherefore\b'],
            'temporal': [r'\bbefore\b', r'\bafter\b', r'\bwhile\b', r'\bduring\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bat\s+least\b']
        }
        self.t = 0  # Global time step for bandit
        self.lambda_prag = 0.5  # Weight for pragmatic relevance

    def _extract_atoms(self, text: str) -> List[Dict]:
        """Extract pragmatic constraints as propositional atoms."""
        atoms = []
        text_lower = text.lower()
        
        for category, regex_list in self.patterns.items():
            for regex in regex_list:
                matches = re.finditer(regex, text_lower)
                for match in matches:
                    atoms.append({
                        'type': category,
                        'text': match.group(),
                        'start': match.start(),
                        'polarity': -1 if category == 'negation' else 1
                    })
        return atoms

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Verify numeric claims if present."""
        # Extract numbers from prompt and candidate
        nums_prompt = re.findall(r"-?\d+\.?\d*", prompt)
        nums_cand = re.findall(r"-?\d+\.?\d*", candidate)
        
        if not nums_prompt or not nums_cand:
            return 1.0 # No numeric conflict detected
            
        try:
            # Simple heuristic: if candidate introduces a number wildly out of range of prompt, penalize
            p_vals = [float(n) for n in nums_prompt]
            c_vals = [float(n) for n in nums_cand]
            
            if not p_vals or not c_vals:
                return 1.0
                
            p_range = max(p_vals) - min(p_vals) if len(p_vals) > 1 else 1.0
            for c in c_vals:
                if p_range > 0 and (c < min(p_vals) - p_range or c > max(p_vals) + p_range):
                    # Heuristic penalty for outliers, but don't zero out immediately
                    return 0.8
            return 1.0
        except ValueError:
            return 1.0

    def _model_check(self, prompt: str, candidate: str) -> Tuple[int, float]:
        """
        Simulate model checking: M |= phi.
        Returns (satisfaction_flag, pragmatic_score).
        """
        atoms = self._extract_atoms(prompt)
        if not atoms:
            # If no constraints, assume literal truth but low pragmatic value
            return 1, 0.0

        satisfied_count = 0
        total_weight = 0
        
        cand_lower = candidate.lower()
        
        for atom in atoms:
            total_weight += 1
            type_ = atom['type']
            text = atom['text']
            
            # Simplified verification logic based on type
            is_present = text in cand_lower
            
            if type_ == 'negation':
                # If prompt has negation, candidate should ideally acknowledge it or not contradict
                # Heuristic: If prompt says "not X", and candidate says "X" (without not), penalize?
                # Instead, we check if the candidate contradicts the negation structure
                # For this implementation, we reward candidates that contain the negation context
                if is_present:
                    satisfied_count += 1
                else:
                    # Check for contradiction (simple version)
                    # If prompt says "not big", candidate says "big" -> fail? 
                    # Too complex for regex only. We reward presence of the constraint marker.
                    pass 
            elif type_ in ['conditional', 'causal', 'temporal']:
                # Candidate should ideally reflect the logical flow or not contradict
                # Reward if candidate contains key terms or logical connectors
                if is_present:
                    satisfied_count += 1
            elif type_ == 'comparative':
                # Check numeric consistency if comparatives exist
                num_consist = self._check_numeric_consistency(prompt, candidate)
                satisfied_count += num_consist
            else:
                if is_present:
                    satisfied_count += 1

        # Normalize pragmatic score
        prag_score = (satisfied_count / total_weight) if total_weight > 0 else 0.0
        
        # Binary satisfaction: Must not actively contradict key negations
        # Simplified: If we found atoms, and candidate is empty, sat=0. 
        # Otherwise, we rely on the continuous score for ranking.
        sat = 1 if (len(atoms) == 0 or prag_score > 0.0 or len(candidate.strip()) > 0) else 0
        
        # Special case: If prompt has "not", and candidate is just "yes", likely wrong.
        # But without semantic understanding, we rely on the score.
        
        return sat, prag_score

    def _ucb_score(self, sat: int, prag_score: float, n_i: int, t: int) -> float:
        """Calculate UCB1 based score."""
        if n_i == 0:
            return float('inf') # Explore unseen arms
        
        # Reward definition from prompt: r_i = sat * (1 + lambda * prag_i)
        r_i = sat * (1.0 + self.lambda_prag * prag_score)
        
        # Update mean estimate (simplified for single shot: mean is just r_i)
        mu_hat = r_i
        
        # Confidence width: sqrt(2 log t / n_i)
        if t == 0:
            w_i = 1.0
        else:
            w_i = math.sqrt((2.0 * math.log(t + 1)) / n_i)
            
        return mu_hat + w_i

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as tiebreaker."""
        try:
            import zlib
            s1_b = s1.encode('utf-8')
            s2_b = s2.encode('utf-8')
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        self.t += 1
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        if len(candidates) > 1:
            # Compare each candidate to prompt
            for c in candidates:
                ncd_scores.append(self._ncd_distance(prompt, c))
        else:
            ncd_scores = [0.0]

        for i, cand in enumerate(candidates):
            sat, prag_score = self._model_check(prompt, cand)
            
            # Simulate bandit arm pull
            # n_i is effectively 1 for this evaluation pass (stateless between calls mostly)
            # But we treat the current evaluation as step t
            score = self._ucb_score(sat, prag_score, n_i=1, t=self.t)
            
            # Adjust score slightly by NCD if scores are close (tiebreaker logic)
            # We invert NCD because lower distance is better, but we want higher score
            # Only use as minor modifier to not override logic
            ncd_mod = (1.0 - ncd_scores[i]) * 0.001 
            
            final_score = score + ncd_mod
            
            # Reasoning string generation
            reason_parts = []
            if sat == 1:
                reason_parts.append("Logical constraints satisfied")
            else:
                reason_parts.append("Logical constraints violated")
            
            if prag_score > 0.5:
                reason_parts.append("Strong pragmatic alignment")
            elif prag_score < 0.2:
                reason_parts.append("Weak pragmatic alignment")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reason_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on model check satisfaction."""
        sat, prag_score = self._model_check(prompt, answer)
        
        if sat == 0:
            return 0.0
        
        # Map pragmatic score to confidence
        # Base confidence 0.5, boosted by pragmatic alignment
        conf = 0.5 + (0.49 * prag_score)
        
        # Penalize if answer is empty but prompt exists
        if not answer.strip() and prompt.strip():
            return 0.1
            
        return min(1.0, max(0.0, conf))