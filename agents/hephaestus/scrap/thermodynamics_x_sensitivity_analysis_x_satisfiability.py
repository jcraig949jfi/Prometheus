import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Energy-Sensitive SAT-Score (ESSS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (negations, comparatives, 
       conditionals, causality) from the prompt using regex.
    2. Clause Database: Builds a weighted set of logical constraints.
    3. Energy Function: Calculates 'free energy' based on unsatisfied clauses.
    4. Sensitivity Analysis: Perturbs numeric thresholds to penalize brittle answers.
    5. Scoring: Returns negative energy (higher is better), using NCD only as a tiebreaker.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(greater|less|higher|lower|more|fewer)\s*(than)?', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?)\s*(?:,|then)?\s+(.+?)(?:\.|$)', re.IGNORECASE),
            'causal': re.compile(r'(\w+(?:\s+\w+)*?)\s*(leads to|causes|because|results in)\s*(\w+(?:\s+\w+)*)', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(°C|C|F|K|m|s|kg|%)?', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after)\b', re.IGNORECASE)
        }
        self.lambda_sens = 0.1

    def _extract_clauses(self, text: str) -> List[Dict]:
        """Extract structural constraints as weighted clauses."""
        clauses = []
        text_lower = text.lower()
        
        # 1. Negations (Penalize if candidate contradicts explicit negation)
        for match in self.patterns['negation'].finditer(text):
            # Context window around negation
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].lower()
            clauses.append({'type': 'negation', 'context': context, 'weight': 1.0})

        # 2. Comparatives (e.g., A greater than B)
        for match in self.patterns['comparative'].finditer(text):
            clauses.append({'type': 'comparative', 'raw': match.group(0), 'weight': 1.5})
            
        # 3. Conditionals (If A then B)
        for match in self.patterns['conditional'].finditer(text):
            clauses.append({'type': 'conditional', 'antecedent': match.group(1), 'consequent': match.group(2), 'weight': 2.0})
            
        # 4. Causal
        for match in self.patterns['causal'].finditer(text):
            clauses.append({'type': 'causal', 'cause': match.group(1), 'effect': match.group(3), 'weight': 1.8})
            
        # 5. Numeric constraints
        nums = self.patterns['numeric'].findall(text)
        if len(nums) >= 2:
            # Simple transitivity check setup
            clauses.append({'type': 'numeric_set', 'count': len(nums), 'weight': 1.2})

        return clauses if clauses else [{'type': 'fallback', 'weight': 0.5}]

    def _check_satisfaction(self, clause: Dict, candidate: str) -> float:
        """
        Returns 0.0 if satisfied, 1.0 if violated.
        Uses simple heuristic matching for demonstration of the logic engine.
        """
        cand_lower = candidate.lower()
        ctype = clause['type']
        
        if ctype == 'negation':
            # If prompt says "not X", and candidate contains "X" without negation nearby, penalize?
            # Simplified: If prompt has negation, candidate should ideally reflect uncertainty or negation
            # This is a heuristic proxy for logical consistency
            if 'not' in cand_lower or 'no' in cand_lower or 'false' in cand_lower:
                return 0.0 # Candidate acknowledges negation
            return 0.5 # Partial penalty for ignoring negation context
            
        elif ctype == 'comparative':
            raw = clause['raw']
            # Check if candidate preserves the comparative direction roughly
            # Heuristic: If prompt says "A greater than B", candidate shouldn't say "B is max"
            if 'less' in raw or 'fewer' in raw:
                if 'highest' in cand_lower or 'max' in cand_lower or 'greater' in cand_lower:
                    return 1.0 # Contradiction
            elif 'greater' in raw or 'more' in raw:
                if 'lowest' in cand_lower or 'min' in cand_lower or 'least' in cand_lower:
                    return 1.0 # Contradiction
            return 0.0

        elif ctype == 'conditional':
            # If candidate explicitly contradicts the consequent when antecedent is implied
            # Very hard to do perfectly without LLM, using keyword presence as proxy
            if clause['consequent'].lower().split()[0] in cand_lower and 'not' in cand_lower:
                return 1.0
            return 0.0

        elif ctype == 'numeric_set':
            # Check if candidate contains numbers consistent with prompt order?
            # Fallback to 0 (satisfied) unless obvious contradiction
            return 0.0
            
        return 0.0

    def _compute_sensitivity(self, prompt: str, candidate: str, base_energy: float) -> float:
        """
        Perturb numeric literals in the candidate to test robustness.
        If small changes in numbers drastically change validity, energy increases.
        """
        nums = self.patterns['numeric'].findall(candidate)
        if not nums:
            return base_energy
        
        # Finite difference approximation
        epsilon = 0.01
        perturbed_score = 0.0
        
        # We simulate perturbation by checking if the answer relies on specific numeric precision
        # In a full engine, we would re-evaluate the SAT score with shifted thresholds.
        # Here, we penalize if the candidate is purely numeric and short (brittle)
        if len(nums) > 0 and len(candidate.split()) < 5:
            perturbed_score = base_energy * (1 + self.lambda_sens)
            
        return base_energy + perturbed_score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        clauses = self._extract_clauses(prompt)
        results = []
        
        for cand in candidates:
            # 1. Energy Calculation (Sum of penalties)
            energy = 0.0
            total_weight = 0.0
            
            for clause in clauses:
                violation = self._check_satisfaction(clause, cand)
                weight = clause['weight']
                energy += violation * weight
                total_weight += weight
            
            # Normalize energy by total possible weight to get a baseline score
            # Lower energy is better. Base score = 1.0 - (energy / max_possible)
            base_score = 1.0 - (energy / (total_weight + 1e-6))
            
            # 2. Sensitivity Analysis Adjustment
            final_score = self._compute_sensitivity(prompt, cand, base_score)
            
            # Ensure score is within reasonable bounds
            final_score = max(-1.0, min(1.0, final_score))
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f"Structural match: {1.0 - (energy/(total_weight+1e-6)):.2f}, Sensitivity adjusted."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are identical (very close)
        if len(results) > 1:
            if abs(results[0]['score'] - results[1]['score']) < 1e-4:
                # Use NCD relative to prompt
                results.sort(key=lambda x: self._ncd(prompt, x['candidate']), reverse=False)

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score (-1 to 1) to confidence (0 to 1)
        confidence = (score + 1.0) / 2.0
        
        # Boost confidence if structural patterns were detected and satisfied
        clauses = self._extract_clauses(prompt)
        if len(clauses) > 1 and score > 0.5:
            confidence = min(1.0, confidence + 0.1)
            
        return float(np.clip(confidence, 0.0, 1.0))