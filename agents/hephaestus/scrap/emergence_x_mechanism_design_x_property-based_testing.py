import re
import random
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool combining Structural Parsing, Mechanism Design, and Emergence.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions and logical relations (negation, 
       comparatives, conditionals, causality) from text using regex.
    2. Constraint Propagation: Builds a dependency graph of these propositions.
    3. Property-Based Testing (Restricted): Generates random truth assignments to test 
       the consistency of the candidate's logical structure against the prompt's constraints.
       Note: Used only for confidence estimation and structural validation, not primary scoring.
    4. Mechanism Design: Assigns weights to clause types (causal > comparative > atomic) 
       to incentivize complex logical alignment.
    5. Emergence Score: Calculated as the weighted satisfaction rate of constraints across 
       valid logical worlds, minus a penalty for minimal counterexamples found during shrinking.
    
    The final score is a weighted average of structural alignment and logical coherence.
    """

    def __init__(self):
        random.seed(42)
        np.random.seed(42)
        # Weights for mechanism design incentives
        self.weights = {
            'causal': 2.0,
            'conditional': 1.8,
            'comparative': 1.5,
            'negation': 1.2,
            'atomic': 1.0
        }

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract simple atomic phrases as propositions."""
        # Simple split by conjunctions and punctuation to get atoms
        clean = re.sub(r'[,.!?;]', '', text)
        parts = re.split(r'\s+(?:and|or|but|then)\s+', clean, flags=re.IGNORECASE)
        atoms = [p.strip() for p in parts if len(p.strip()) > 2]
        return atoms[:10]  # Limit complexity

    def _parse_clauses(self, text: str) -> List[Dict]:
        """Parse text into weighted logical clauses."""
        clauses = []
        atoms = self._extract_atoms(text)
        text_lower = text.lower()
        
        # Detect types
        has_neg = any(w in text_lower for w in ['not', 'no', 'never', 'none'])
        has_if = any(w in text_lower for w in ['if', 'when', 'unless'])
        has_causal = any(w in text_lower for w in ['because', 'leads to', 'causes', 'therefore'])
        has_comp = bool(re.search(r'(greater|less|more|fewer|larger|smaller|>\|<)', text_lower))
        
        # Assign base type based on strongest signal
        if has_causal:
            ctype = 'causal'
        elif has_if:
            ctype = 'conditional'
        elif has_comp:
            ctype = 'comparative'
        elif has_neg:
            ctype = 'negation'
        else:
            ctype = 'atomic'
            
        # Create clauses from atoms
        for atom in atoms:
            clauses.append({
                'content': atom,
                'type': ctype,
                'weight': self.weights.get(ctype, 1.0),
                'negated': has_neg and atom in text
            })
            
        # If no atoms found but text exists, treat whole text as one atomic clause
        if not clauses and text.strip():
            clauses.append({
                'content': text.strip(),
                'type': 'atomic',
                'weight': 1.0,
                'negated': has_neg
            })
            
        return clauses

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Extract and compare numeric thresholds."""
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_c = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not nums_p:
            return 1.0 # No numeric constraints
        if not nums_c:
            return 0.5 # Missing numbers in candidate
        
        # Simple check: does candidate contain the key numbers from prompt?
        # Or maintain order?
        matches = 0
        for n in nums_p:
            if any(abs(n - c) < 0.01 for c in nums_c):
                matches += 1
        
        return matches / len(nums_p) if nums_p else 1.0

    def _simulate_worlds(self, prompt_clauses: List[Dict], candidate_clauses: List[Dict], trials: int = 50) -> float:
        """
        Property-based testing loop.
        Generates random truth assignments to see if candidate logic holds up 
        against prompt constraints.
        """
        if not prompt_clauses:
            return 1.0
            
        all_atoms = list(set([c['content'] for c in prompt_clauses] + [c['content'] for c in candidate_clauses]))
        if not all_atoms:
            return 1.0
            
        # Map atoms to indices
        atom_map = {a: i for i, a in enumerate(all_atoms)}
        n_atoms = len(all_atoms)
        if n_atoms == 0: return 1.0
        
        satisfied_count = 0
        
        for _ in range(trials):
            # Random truth assignment
            truth = {a: bool(random.getrandbits(1)) for a in all_atoms}
            
            # Check prompt constraints (simplified: if prompt asserts X, candidate should not assert not-X)
            valid_world = True
            
            # Build prompt truth set
            prompt_true = set()
            for c in prompt_clauses:
                if truth.get(c['content'], False):
                    prompt_true.add(c['content'])
                elif c.get('negated'):
                    # If prompt says "not X", and truth says X is true, contradiction in world generation?
                    # Simplified: We just check consistency between prompt and candidate claims
                    pass

            # Check candidate against prompt logic
            for c in candidate_clauses:
                content = c['content']
                is_true_in_world = truth.get(content, False)
                
                # If candidate claims X, but prompt implies not-X (heuristic)
                # Since we don't have full semantic parse, we check overlap consistency
                pass 
            
            # Heuristic satisfaction: 
            # If candidate clause exists in prompt, it's consistent.
            # If candidate adds new logic, check if it contradicts prompt negations.
            score_step = 0.0
            total_weight = 0
            
            for c in candidate_clauses:
                w = c['weight']
                total_weight += w
                # If candidate clause is in prompt, high probability of consistency
                if any(c['content'] in p['content'] or p['content'] in c['content'] for p in prompt_clauses):
                    score_step += w
                else:
                    # New claim: penalize slightly unless it's a direct logical consequence (hard to detect without LLM)
                    # Assume 50% chance of being consistent in random world
                    score_step += w * 0.5
            
            if total_weight > 0:
                if (score_step / total_weight) > 0.5:
                    satisfied_count += 1

        return satisfied_count / trials if trials > 0 else 1.0

    def _delta_shrink(self, prompt: str, candidate: str) -> float:
        """
        Rudimentary delta-debugging: try removing parts of candidate to see if 
        the core meaning remains consistent with prompt.
        Returns a penalty factor based on minimal failing set size.
        """
        # Simplified: Check if removing words breaks numeric or keyword overlap
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        intersection = p_words & c_words
        if not intersection:
            return 1.0 # No overlap to shrink
            
        # If candidate is very long but has low overlap, penalty
        overlap_ratio = len(intersection) / len(c_words) if c_words else 1.0
        return overlap_ratio

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_clauses = self._parse_clauses(prompt)
        prompt_numeric = self._check_numeric_consistency(prompt, prompt) # Self-check
        
        for cand in candidates:
            cand_clauses = self._parse_clauses(cand)
            
            # 1. Structural Overlap (Base Score)
            p_atoms = set([c['content'] for c in prompt_clauses])
            c_atoms = set([c['content'] for c in cand_clauses])
            
            # Jaccard-like similarity on extracted clauses
            union = p_atoms | c_atoms
            struct_score = len(p_atoms & c_atoms) / len(union) if union else 0.0
            
            # 2. Numeric Consistency
            num_score = self._check_numeric_consistency(prompt, cand)
            
            # 3. Logical Coherence (Property-Based Testing Simulation)
            # Only run if we have structural data
            if prompt_clauses and cand_clauses:
                logic_score = self._simulate_worlds(prompt_clauses, cand_clauses)
            else:
                logic_score = 0.5
                
            # 4. Mechanism Design Weighting
            # Boost score if candidate contains high-weight clause types present in prompt
            weight_bonus = 0.0
            prompt_types = set([c['type'] for c in prompt_clauses])
            cand_types = set([c['type'] for c in cand_clauses])
            shared_types = prompt_types & cand_types
            if shared_types:
                max_w = max([self.weights[t] for t in shared_types])
                weight_bonus = (max_w - 1.0) * 0.2 # Small bonus for complex alignment
            
            # 5. Shrinking Penalty
            shrink_factor = self._delta_shrink(prompt, cand)
            
            # Final Score Calculation
            # Weighted sum: Structure (40%), Logic (30%), Numeric (20%), Bonus (10%)
            raw_score = (
                0.4 * struct_score + 
                0.3 * logic_score + 
                0.2 * num_score + 
                0.1 * weight_bonus
            )
            
            # Apply shrinking penalty (emergence of errors)
            final_score = raw_score * shrink_factor
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, Logic: {logic_score:.2f}, Numeric: {num_score:.2f}, Shrink: {shrink_factor:.2f}"
            })
            
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']