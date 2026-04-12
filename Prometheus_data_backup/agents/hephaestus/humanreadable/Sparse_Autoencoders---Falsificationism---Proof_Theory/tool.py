import re
import numpy as np
from itertools import product

class ReasoningTool:
    """
    Sparse Proof-Falsifier: A hybrid reasoning tool combining sparse logical feature extraction,
    resolution-based entailment checks, and Popperian falsification scoring.
    
    Mechanism:
    1. Sparse Extraction: Uses regex to identify logical atoms (negations, conditionals, comparatives).
    2. Proof Check: Attempts to derive a contradiction from Premises + Not(Candidate).
    3. Falsification: Searches for a truth assignment satisfying Premises but falsifying Candidate.
    4. Scoring: High score = Entailment holds AND no counter-model found.
    """
    
    # Logical patterns dictionary (simplified for brevity and speed)
    PATTERNS = {
        'not': [r'\bnot\b', r'\bnever\b', r'\bfalse\b', r'^no\b'],
        'and': [r'\band\b', r'\bboth\b', r'\balso\b'],
        'or': [r'\bor\b', r'\beither\b'],
        'if': [r'\bif\b', r'\bimplies\b', r'\bthen\b'],
        'all': [r'\ball\b', r'\bevery\b', r'\bnone\b'],
        'gt': [r'>', r'greater than', r'more than'],
        'lt': [r'<', r'less than', r'fewer than'],
        'eq': [r'=', r'equal to', r'is\s+the\s+same\s+as']
    }

    def __init__(self):
        self.lambda_penalty = 0.5
        self.depth_limit = 5

    def _extract_atoms(self, text: str) -> dict:
        """Extract binary activation of logical features."""
        text_lower = text.lower()
        atoms = {}
        for key, patterns in self.PATTERNS.items():
            match = False
            for p in patterns:
                if re.search(p, text_lower):
                    match = True
                    break
            atoms[key] = 1 if match else 0
        return atoms

    def _parse_comparatives(self, text: str) -> list:
        """Extract numeric comparisons if present."""
        nums = re.findall(r'(\d+\.?\d*)', text)
        facts = []
        if len(nums) >= 2:
            try:
                vals = [float(n) for n in nums]
                if 'greater' in text or '>' in text:
                    facts.append(vals[0] > vals[1])
                elif 'less' in text or '<' in text:
                    facts.append(vals[0] < vals[1])
                elif 'equal' in text or '=' in text:
                    facts.append(abs(vals[0] - vals[1]) < 1e-6)
            except: pass
        return facts

    def _resolve(self, premises: list, candidate: str) -> tuple:
        """
        Simplified resolution check.
        Returns (steps_to_contradiction, falsifiable).
        """
        # Heuristic: If candidate contains 'not' and premise contains same key terms without 'not',
        # or vice versa, we flag potential conflict.
        # Real resolution is complex; we simulate via keyword overlap and negation checks.
        
        cand_atoms = self._extract_atoms(candidate)
        cand_lower = candidate.lower()
        
        steps = 0
        contradiction_found = False
        falsifiable = False
        
        # Check for direct negation conflicts
        for p in premises:
            p_atoms = self._extract_atoms(p)
            p_lower = p.lower()
            
            # Shared vocabulary check
            shared_words = set(re.findall(r'\b\w+\b', p_lower)) & set(re.findall(r'\b\w+\b', cand_lower))
            shared_words = {w for w in shared_words if len(w) > 3} # Ignore short words
            
            if not shared_words:
                continue
                
            steps += 1
            
            # Negation conflict: One has 'not', other doesn't, but share words
            if cand_atoms['not'] != p_atoms['not'] and len(shared_words) > 0:
                contradiction_found = True
                steps += 1 # Penalty for extra step
            
            # Falsification check: Can we imagine a world where P is true and C is false?
            # If P says "A and B" and C says "A", it's not falsifiable easily.
            # If P says "A or B" and C says "A", it IS falsifiable (B could be true, A false).
            if p_atoms['or'] and not cand_atoms['or']:
                falsifiable = True

        if contradiction_found:
            return 1, falsifiable
        return self.depth_limit + 1, falsifiable

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        # Treat prompt as premises
        premises = [prompt] 
        
        for cand in candidates:
            # 1. Sparse Feature Extraction
            cand_atoms = self._extract_atoms(cand)
            prompt_atoms = self._extract_atoms(prompt)
            
            # 2. Numeric Evaluation (Structural Parsing)
            p_nums = self._parse_comparatives(prompt)
            c_nums = self._parse_comparatives(cand)
            numeric_consistent = True
            if p_nums and c_nums:
                # If both have numbers, they must agree logically (simplified)
                numeric_consistent = (p_nums[0] == c_nums[0]) if len(p_nums)==len(c_nums) else False
            
            # 3. Proof-Theoretic Check
            steps, is_falsifiable = self._resolve(premises, cand)
            entailment_conf = 1.0 / (1.0 + steps)
            
            # 4. Falsification Scoring
            # Penalize if a counter-model exists (is_falsifiable)
            falsification_penalty = self.lambda_penalty if is_falsifiable else 0.0
            
            base_score = entailment_conf * (1.0 - falsification_penalty)
            
            # Boost for numeric consistency if detected
            if p_nums and c_nums:
                base_score = min(1.0, base_score + 0.2) if numeric_consistent else base_score * 0.5

            # Tie-breaker: NCD-like length similarity (very weak weight)
            len_ratio = min(len(prompt), len(cand)) / max(len(prompt), len(cand) + 1)
            final_score = base_score * 0.9 + (len_ratio * 0.1 * 0.05)

            reasoning = f"Steps:{steps}, Falsifiable:{is_falsifiable}, NumOK:{numeric_consistent}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a single candidate."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]