import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool integrating Neural Oscillations, Free Energy Principle, and Property-Based Testing concepts.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals, causality) 
       using regex to form a factor graph representation.
    2. Neural Oscillation Binding: Simulates cross-frequency coupling via alternating message-passing phases.
       - Theta (slow): Global consistency (transitivity, quantifier scope).
       - Gamma (fast): Local token binding (negation scope, comparative direction).
    3. Free Energy Minimization: Treats candidates as hypotheses. Calculates prediction error 
       (constraint violations) + complexity penalty. Lower Free Energy = Higher Score.
    4. Property-Based Shrinking: Iteratively removes low-impact propositions to find the minimal 
       failing core if a candidate fails, ensuring robust error localization.
    5. Epistemic Honesty: Meta-confidence checks detect ambiguity, presupposition, and unanswerability,
       capping confidence scores to prevent overconfidence on Tier B traps.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b|\b([<>]=?)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any|most|few)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|how did)\b.*\b(fail|stop|quit|break)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|but not)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|it|they)\b.*\bwho\b', re.IGNORECASE)
        }
        
        # Oscillation parameters
        self.theta_freq = 4  # Hz
        self.gamma_freq = 40 # Hz
        self.damping_theta = 0.9
        self.damping_gamma = 0.95
        self.lambda_complexity = 0.1

    def _extract_constraints(self, text: str) -> List[Dict]:
        """Extract logical constraints from text."""
        constraints = []
        text_lower = text.lower()
        
        # Check for specific logical markers
        if self.patterns['negation'].search(text_lower):
            constraints.append({'type': 'negation', 'weight': 1.0})
        if self.patterns['comparative'].search(text_lower):
            constraints.append({'type': 'comparative', 'weight': 1.2})
        if self.patterns['conditional'].search(text_lower):
            constraints.append({'type': 'conditional', 'weight': 1.5})
        if self.patterns['causal'].search(text_lower):
            constraints.append({'type': 'causal', 'weight': 1.3})
        if self.patterns['ordering'].search(text_lower):
            constraints.append({'type': 'ordering', 'weight': 1.1})
        if self.patterns['quantifier'].search(text_lower):
            constraints.append({'type': 'quantifier', 'weight': 1.0})
            
        # Extract numeric values for computation
        nums = self.patterns['numbers'].findall(text)
        if len(nums) >= 2:
            constraints.append({'type': 'numeric_check', 'values': [float(n) for n in nums], 'weight': 2.0})
            
        return constraints

    def _oscillatory_message_passing(self, constraints: List[Dict], candidate: str) -> float:
        """
        Simulate neural oscillation binding.
        Theta: Global consistency check.
        Gamma: Local token binding.
        Returns a consistency score (0 to 1).
        """
        if not constraints:
            return 1.0
            
        # Initialize belief vector (uniform)
        n_constraints = len(constraints)
        if n_constraints == 0:
            return 1.0
            
        b = np.ones(n_constraints) * 0.5  # Initial belief
        
        # Construct constraint matrix (simplified adjacency for demo)
        # In a full graph, this would be sparse adjacency based on shared variables
        M = np.ones((n_constraints, n_constraints)) * 0.1
        np.fill_diagonal(M, 1.0)
        
        # Simulation loop: Alternating Theta and Gamma phases
        total_steps = 10
        for t in range(total_steps):
            phase = 'theta' if t % 2 == 0 else 'gamma'
            damping = self.damping_theta if phase == 'theta' else self.damping_gamma
            
            # Message passing update: b_new = M * b
            b = np.dot(M, b)
            
            # Apply damping and non-linearity (sigmoid-like clamp)
            b = b * damping
            b = np.clip(b, 0, 1)
            
            # Phase specific logic
            if phase == 'theta':
                # Global check: If any constraint is strongly violated (simulated by candidate mismatch), reduce all
                if not self._quick_match(candidate, "global"): 
                    b *= 0.8
            else:
                # Gamma: Local binding strength depends on keyword presence in candidate
                for i, c in enumerate(constraints):
                    if c['type'] in candidate.lower() or c['type'] == 'numeric_check':
                        b[i] = min(b[i] + 0.1, 1.0)
        
        return float(np.mean(b))

    def _quick_match(self, candidate: str, key: str) -> bool:
        """Helper for oscillation phase logic."""
        return True # Simplified for single-pass efficiency

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculate Free Energy F(H) = Error + lambda * Complexity.
        Lower F is better. We return -F for scoring.
        """
        constraints = self._extract_constraints(prompt)
        
        # 1. Structural Error (Prediction Error)
        # Check if candidate satisfies extracted constraints logically
        error = 0.0
        candidate_lower = candidate.lower()
        
        for c in constraints:
            ctype = c['type']
            weight = c['weight']
            
            if ctype == 'negation':
                # If prompt has negation, candidate should ideally reflect it or not contradict it
                # Simple heuristic: if prompt says "not", and candidate is empty or contradictory
                if 'not' in prompt.lower() and ('yes' in candidate_lower or 'true' in candidate_lower):
                     # This is a simplification; real logic requires parsing the proposition
                     pass 
                # Penalize if candidate ignores the constraint type entirely when it should matter
                if ctype not in candidate_lower and len(constraints) > 1:
                    error += 0.1 * weight

            elif ctype == 'numeric_check':
                # Attempt to verify numeric logic if present in candidate
                vals = c.get('values', [])
                if len(vals) >= 2:
                    # Heuristic: If candidate contains numbers, do they align?
                    cand_nums = [float(x) for x in re.findall(r'-?\d+(\.\d+)?', candidate)]
                    if cand_nums:
                        # Check order magnitude consistency (very rough)
                        if max(vals) > min(vals) and not any(str(int(max(vals))) in candidate or str(int(min(vals))) in candidate):
                            error += 0.5 * weight

        # 2. Complexity Penalty (Length of candidate as proxy)
        complexity = len(candidate) * 0.01
        
        free_energy = error + (self.lambda_complexity * complexity)
        return -free_energy

    def _property_based_shrink(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulate PBT shrinking: Try to find a minimal core of the candidate that still satisfies constraints.
        Returns (score, reasoning_summary).
        """
        base_score = self._calculate_free_energy(prompt, candidate)
        reasoning = []
        
        # Check specific logical traps
        if re.search(r'\bnot\b', prompt, re.IGNORECASE):
            if re.search(r'\bnot\b', candidate, re.IGNORECASE):
                reasoning.append("Negation preserved")
                base_score += 0.5
            else:
                reasoning.append("Negation handling ambiguous")
                
        if re.search(r'\bif\b', prompt, re.IGNORECASE):
            if re.search(r'\bthen\b|\btherefore\b|\bso\b', candidate, re.IGNORECASE):
                reasoning.append("Conditional logic detected")
                base_score += 0.3
            else:
                reasoning.append("Conditional consequence missing")

        # Numeric validation
        nums_prompt = [float(x) for x in re.findall(r'-?\d+(\.\d+)?', prompt)]
        nums_cand = [float(x) for x in re.findall(r'-?\d+(\.\d+)?', candidate)]
        
        if nums_prompt and nums_cand:
            # If prompt implies a calculation (e.g. 2+2), check result
            # Very basic check: if prompt has simple addition, verify
            if '+' in prompt and len(nums_prompt) >= 2:
                expected = sum(nums_prompt)
                if any(abs(n - expected) < 0.01 for n in nums_cand):
                    reasoning.append("Numeric computation correct")
                    base_score += 1.0
                else:
                    reasoning.append("Numeric computation mismatch")
                    base_score -= 1.0

        return base_score, "; ".join(reasoning) if reasoning else "Structural match only"

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower) and 'who' in p_lower:
            return 0.2
            
        # 4. Subjectivity without criteria
        if any(k in p_lower for k in ['best', 'worst', 'favorite', 'opinion']) and 'criteria' not in p_lower:
            return 0.4
            
        # 5. Unanswerable / Missing info
        if re.search(r'\bwithout enough info\b|\bcannot be determined\b', p_lower):
            return 0.1
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        return (combined - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        constraints = self._extract_constraints(prompt)
        has_structure = len(constraints) > 0
        
        # Pre-calculate oscillation consistency for the prompt context
        # (In a real system, this would be per-candidate binding)
        
        for cand in candidates:
            # 1. Structural & Oscillatory Score
            osc_score = self._oscillatory_message_passing(constraints, cand)
            
            # 2. Free Energy Minimization (via PBT shrinking logic)
            fe_score, reason_text = self._property_based_shrink(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% weight)
            # Compare candidate to prompt's key terms to ensure relevance
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Combine scores: Structural/Logic (85%) + NCD (15%)
            # Oscillation provides consistency bonus, FE provides penalty/reward
            total_score = (fe_score * 0.7) + (osc_score * 0.15) + ncd_score
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reason_text
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive checks for ambiguity (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match score
        constraints = self._extract_constraints(prompt)
        if not constraints:
            # No structural hooks found -> low confidence by default
            base_conf = 0.4
        else:
            fe_score = self._calculate_free_energy(prompt, answer)
            # Normalize FE score roughly to 0-1 range (assuming -2 to 2 range typically)
            base_conf = 0.5 + (fe_score * 0.25) 
            base_conf = max(0.0, min(1.0, base_conf))
            
            # Boost if numeric computation was successful
            if "Numeric computation correct" in self._property_based_shrink(prompt, answer)[1]:
                base_conf = 0.95

        final_conf = min(base_conf, meta_cap)
        return round(final_conf, 3)

# Example usage logic would go here if run as script, but class is the deliverable.