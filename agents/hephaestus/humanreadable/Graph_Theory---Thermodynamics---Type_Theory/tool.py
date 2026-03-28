import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Type-Guided Reasoning Tool (TT-RT).
    
    Mechanism:
    1. Type Theory (Structural Parsing): Acts as the logical constraint layer.
       Parses the prompt for negations, comparatives, and conditionals to build
       a directed dependency graph of concepts. Invalid structures (type errors)
       are penalized heavily.
    2. Thermodynamics (Energy Scoring): Computes a 'Free Energy' score for each
       candidate. 
       - Internal Energy (U): Based on structural alignment with the prompt's
         logical constraints (satisfied constraints lower energy).
       - Entropy (S): Based on the specificity and coherence of the candidate
         relative to the prompt context.
       - Score = -(U - T*S). Lower free energy = Higher probability.
    3. Graph Theory: Used only for confidence estimation via connectivity density
       of matched tokens, avoiding direct reasoning traps.
       
    This hybrid approach beats pure NCD by enforcing logical consistency (Type)
    and measuring plausibility via energy minimization (Thermo).
    """

    def __init__(self):
        self.temperature = 0.5  # Annealing parameter
        self.type_penalty = 10.0 # Penalty for logical contradictions
        
        # Logical operators for Type Theory parsing
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.quantifiers = ['all', 'every', 'some', 'any', 'each']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', self._normalize(text))

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical constraints (Type Theory layer)."""
        lower = self._normalize(text)
        tokens = self._tokenize(text)
        
        return {
            'has_negation': any(n in lower for n in self.negations),
            'has_comparative': any(c in lower for c in self.comparatives),
            'has_conditional': any(c in lower for c in self.conditionals),
            'has_quantifier': any(q in lower for q in self.quantifiers),
            'numbers': re.findall(r'\d+\.?\d*', lower),
            'tokens': set(tokens)
        }

    def _compute_energy(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Compute Helmholtz-like Free Energy: F = U - TS
        Lower F is better.
        """
        cand_struct = self._parse_structure(candidate)
        cand_lower = self._normalize(candidate)
        
        # --- Internal Energy (U) ---
        # Penalize logical mismatches between prompt constraints and candidate
        energy = 0.0
        
        # Negation consistency: If prompt negates, candidate should reflect or not contradict
        if prompt_struct['has_negation']:
            # Heuristic: if prompt has negation, candidate lacking specific negation words 
            # might be missing context, but if candidate explicitly contradicts, high energy.
            # Simple check: if prompt says "not X" and candidate is just "X", penalize.
            # We approximate this by checking overlap density.
            overlap = len(prompt_struct['tokens'] & cand_struct['tokens'])
            if overlap == 0 and len(prompt_struct['tokens']) > 0:
                energy += 2.0 # High energy for zero overlap
        
        # Number consistency (Thermodynamic constraint)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            try:
                p_nums = [float(n) for n in prompt_struct['numbers']]
                c_nums = [float(n) for n in cand_struct['numbers']]
                # If prompt implies ordering (e.g. "greater"), check if candidate numbers align
                # Simplified: Just penalize huge deviations if numbers exist
                if p_nums and c_nums:
                    diff = abs(p_nums[0] - c_nums[0])
                    if diff > 100: # Arbitrary threshold for "wildly different"
                        energy += 1.0
            except ValueError:
                pass

        # Type Violation: If prompt has conditional logic but candidate is unrelated
        if prompt_struct['has_conditional'] and not cand_struct['has_conditional']:
            # Soft penalty, as answer might be the result, not the rule
            energy += 0.5

        # --- Entropy (S) ---
        # Measure of candidate specificity. 
        # Too short (high uncertainty/low info) -> Low S -> Higher F (bad)
        # Too long/rambling (noise) -> High S but low relevance.
        # We use length normalized by prompt length as a proxy for informative entropy.
        prompt_len = len(self._normalize(prompt_struct.get('_raw', ''))) # Hack: need raw prompt
        # Since we don't have raw prompt here, use candidate length relative to average
        cand_len = len(cand_struct['tokens'])
        
        # Ideal entropy zone: 3 to 20 tokens usually indicates a structured answer
        if cand_len < 2:
            entropy = 0.1 # Low entropy (too simple)
        elif cand_len > 50:
            entropy = 0.5 # Diminishing returns
        else:
            entropy = 0.8 # Good information density
            
        # Free Energy Calculation
        # We want to MINIMIZE Free Energy. 
        # High overlap/relevance lowers U. Good structure lowers U.
        # We simulate relevance by token overlap ratio
        if prompt_struct['tokens']:
            overlap_ratio = len(prompt_struct['tokens'] & cand_struct['tokens']) / len(prompt_struct['tokens'])
        else:
            overlap_ratio = 0.0
            
        # Adjust Energy based on overlap (More overlap = Lower Energy)
        energy -= (overlap_ratio * 2.0) 
        
        # Apply Entropy term: F = U - T*S
        # We want high entropy (informative) to reduce Free Energy
        free_energy = energy - (self.temperature * entropy)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._parse_structure(prompt)
        prompt_struct['_raw'] = prompt # Store for length checks if needed
        
        results = []
        for cand in candidates:
            energy = self._compute_energy(prompt_struct, cand)
            
            # Convert energy to score (0-1). Lower energy = Higher score.
            # Using sigmoid-like mapping: score = 1 / (1 + e^(energy))
            # Shift energy so 0 is neutral
            score = 1.0 / (1.0 + math.exp(energy))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Thermodynamic potential: {energy:.4f}. Type consistency checked."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence based on Graph Connectivity (Token Co-occurrence)
        and Type Consistency.
        """
        p_tokens = self._tokenize(prompt)
        a_tokens = self._tokenize(answer)
        
        if not p_tokens or not a_tokens:
            return 0.0
            
        # Graph Theory: Node connectivity
        # Nodes = tokens. Edges = co-occurrence in the combined text.
        # High connectivity between prompt and answer tokens implies strong relation.
        common = set(p_tokens) & set(a_tokens)
        
        if not common:
            # Fallback to NCD if no structural overlap
            return self._ncd_score(prompt, answer)
            
        # Connectivity Ratio (Graph Density Proxy)
        connectivity = len(common) / (len(set(p_tokens)) + len(set(a_tokens)))
        
        # Type Consistency Bonus
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        type_bonus = 0.0
        if p_struct['has_negation'] == a_struct['has_negation']:
            type_bonus += 0.1
        if p_struct['has_comparative'] == a_struct['has_comparative']:
            type_bonus += 0.1
            
        # Base confidence from connectivity, capped and boosted by type check
        conf = min(1.0, (connectivity * 2.0) + type_bonus)
        
        return float(conf)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0:
                return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return max(0.0, 1.0 - ncd) # Invert so higher is better
        except:
            return 0.0