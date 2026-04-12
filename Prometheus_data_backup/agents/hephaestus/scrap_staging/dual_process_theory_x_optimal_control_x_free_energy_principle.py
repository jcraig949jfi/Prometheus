import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A Hierarchical Active-Inference Reasoning Tool.
    
    Mechanism:
    1. System 2 (Deliberative/Meta-Cognitive): Analyzes the prompt for logical traps,
       presuppositions, and ambiguities (Tier B). If detected, it suppresses confidence
       to enforce Epistemic Honesty.
    2. System 1 (Fast/Structural): Performs deterministic structural parsing (negations,
       comparatives) and numeric evaluation (Tier A).
    3. Free Energy Principle (Scoring): Candidates are scored by minimizing "surprise"
       (distance from structural/numeric truth). High surprise = low score.
    4. Dual-Process Fusion: Final score is a weighted sum where Structural/Computation
       dominates (>70%), NCD is a minor tiebreaker (<15%), and Meta-Cognition caps
       confidence if the question itself is flawed.
    """

    def __init__(self):
        self.numeric_ops = ['+', '-', '*', '/', '//', '%', '**']
        
    # --- SYSTEM 2: META-COGNITIVE MONITOR (Epistemic Honesty) ---
    
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value: 1.0 (safe) or < 0.3 (unsafe/trap detected).
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"\bhave you (stopped|quit|ceased)\b",
            r"\bwhy did (.*?) (fail|stop|end)\b",
            r"\bwhen did (.*?) stop\b",
            r"\bis it true that (.*?) failed\b",
            r"\bcontinue to\b", # Implies ongoing action
            r"\bassumes that\b"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.2  # Strong cap for presupposition

        # 2. Scope & Pronoun Ambiguity
        # "Every X did a Y" (Same Y?) - Hard to detect perfectly, look for "same" vs "different"
        if re.search(r"\bevery.*\b(same|different)\b", p):
            # Context dependent, but often a trap if not specified
            if "same" in p and "which" in p: 
                return 0.4 # Soft cap, needs context
        
        # Pronoun ambiguity: "X told Y he..." + "who"
        if re.search(r"\btold\b", p) and re.search(r"\b(he|she|him|her)\b", p):
            if re.search(r"\bwho\b", p):
                return 0.25

        # 3. False Dichotomy
        if re.search(r"\beither\b", p) and re.search(r"\bor\b", p):
            if not re.search(r"\belse\b", p) and not re.search(r"\bother\b", p):
                # Potential false dichotomy if no "other" option mentioned
                if re.search(r"\b(true|false|yes|no)\b", p):
                     return 0.3

        # 4. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p for w in subjective_words):
            if "measure" not in p and "criteria" not in p and "define" not in p:
                return 0.3

        # 5. Unanswerability (Missing info)
        if re.search(r"\b(calculate|solve|find)\b", p):
            if re.search(r"\b(no|without|missing)\b.*\b(data|info|number|value)\b", p):
                return 0.2

        return 1.0  # No traps detected

    # --- SYSTEM 1: STRUCTURAL & NUMERIC PARSER ---

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'[-]?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _solve_numeric(self, prompt: str) -> Optional[float]:
        """Attempts to solve simple arithmetic expressions found in the prompt."""
        # Look for explicit math patterns like "5 + 3", "9.11 < 9.9"
        # Simple evaluator for single line expressions
        try:
            # Extract potential expression (very basic heuristic)
            # If prompt contains "what is", "compute", etc., look for numbers and ops
            if any(op in prompt for op in ['+', '-', '*', '/', '=']):
                # Try to find a math expression
                # Remove non-math chars except digits, operators, dots, spaces
                cleaned = re.sub(r'[^\d\.\+\-\*\/\(\)\s]', '', prompt)
                if cleaned.strip() and any(c in cleaned for c in '+-*/'):
                    # Safety check: only allow math chars
                    if re.match(r'^[\d\.\+\-\*\/\(\)\s]+$', cleaned):
                        return eval(cleaned)
        except:
            pass
        return None

    def _check_comparatives(self, prompt: str, candidate: str) -> float:
        """
        Checks if the candidate correctly answers a comparative in the prompt.
        Returns 1.0 if correct, 0.0 if incorrect, -1.0 if N/A.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Pattern: "Which is larger/greater? A or B?"
        ops = [
            (r'larger|greater|max', max),
            (r'smaller|less|min', min),
            (r'shorter', min), # Context dependent, assume min for numbers
            (r'longer', max)
        ]
        
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            for pattern, func in ops:
                if re.search(pattern, p_lower):
                    target = func(nums)
                    # Check if candidate contains the target number string
                    target_str = str(target)
                    # Handle float formatting differences
                    if target_str in candidate or f"{target:.2f}" in candidate or f"{int(target)}" in candidate:
                        return 1.0
                    # If candidate is a number but not the target
                    cand_nums = self._extract_numbers(candidate)
                    if cand_nums and cand_nums[0] != target:
                        return 0.0
        return -1.0

    def _check_negation_logic(self, prompt: str, candidate: str) -> float:
        """
        Checks basic negation traps. 
        E.g., "Which is NOT red?" 
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        if "not " in p_lower or " except " in p_lower:
            # This is a negative constraint. 
            # Heuristic: If the prompt asks what is NOT X, and candidate is X, score 0.
            # Extract the object of negation roughly
            match = re.search(r'not\s+(\w+)', p_lower)
            if match:
                target = match.group(1)
                if target in c_lower:
                    # Candidate contains the forbidden word
                    # Verify it's not saying "It is not [target]"
                    if not re.search(rf'not\s+{target}', c_lower):
                        return 0.0 # Likely wrong
        return 1.0 # Neutral/Pass

    # --- FREE ENERGY SCORING (Expected Free Energy Minimization) ---
    
    def _compute_free_energy_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on minimizing 'surprise' (deviation from structural truth).
        High score = Low Free Energy (Good fit).
        Decomposition: Structural (50%) + Computation (35%) + NCD (15%)
        """
        score = 0.0
        weights = {'struct': 0.50, 'comp': 0.35, 'ncd': 0.15}
        
        # 1. Structural Parsing (Negation, Comparatives)
        struct_score = 1.0
        comp_val = self._check_comparatives(prompt, candidate)
        if comp_val != -1:
            struct_score = comp_val
        else:
            # Fallback to negation check if no comparative found
            struct_score = self._check_negation_logic(prompt, candidate)
            
        # 2. Computation (Numeric)
        comp_score = 1.0
        # If prompt has numbers and looks like a math problem
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2 and ('=' in prompt or 'sum' in prompt.lower() or 'total' in prompt.lower()):
            # Try to verify if candidate matches a computed result
            # Very basic: if candidate is a number, does it match a simple op?
            cand_nums = self._extract_numbers(candidate)
            if cand_nums:
                # Heuristic: Check simple addition of first two numbers if "sum" mentioned
                if 'sum' in prompt.lower() or 'total' in prompt.lower():
                    expected = sum(nums[:2]) # Simplified for demo
                    if abs(cand_nums[0] - expected) < 0.01:
                        comp_score = 1.0
                    else:
                        comp_score = 0.0
                else:
                    # Generic numeric match confidence boost if numbers align
                    comp_score = 0.8 
            else:
                comp_score = 0.2 # Missing number in math context
        elif len(nums) == 0:
            comp_score = 1.0 # No math required

        # 3. NCD Tiebreaker (Normalized Compression Distance)
        # NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # We want similarity, so we use 1 - NCD
        try:
            p_bytes = prompt.encode('utf-8')
            c_bytes = candidate.encode('utf-8')
            c_p = len(zlib.compress(p_bytes))
            c_c = len(zlib.compress(c_bytes))
            c_pc = len(zlib.compress(p_bytes + c_bytes))
            
            min_c = min(c_p, c_c)
            max_c = max(c_p, c_c)
            
            if max_c == 0:
                ncd = 1.0
            else:
                ncd = (c_pc - min_c) / max_c
            
            ncd_score = 1.0 - min(ncd, 1.0) # Convert distance to similarity
        except:
            ncd_score = 0.5

        # Weighted Sum
        final_score = (struct_score * weights['struct']) + \
                      (comp_score * weights['comp']) + \
                      (ncd_score * weights['ncd'])
        
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates against the prompt using the dual-process architecture.
        """
        results = []
        
        # Meta-cognitive check on the prompt itself
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # Calculate raw free energy score (lower energy = higher score)
            raw_score = self._compute_free_energy_score(prompt, cand)
            
            # Apply Meta-Cognitive Cap (Epistemic Honesty)
            # If the prompt is a trap, even the "best" candidate gets low confidence
            if meta_cap < 0.3:
                # If the question is flawed, we penalize all candidates heavily
                # unless the candidate explicitly points out the flaw (advanced, not implemented here)
                # For now, we cap the score to reflect uncertainty.
                final_score = raw_score * meta_cap 
                reasoning = f"Meta-cognitive warning: Prompt contains ambiguity/trap. Score capped."
            else:
                final_score = raw_score
                reasoning = f"Structural/Computational analysis complete. Score: {final_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects traps.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta-Cognitive Check (The "Honesty" Filter)
        meta_val = self._meta_confidence(prompt)
        
        if meta_val < 0.3:
            return meta_val
        
        # 2. Structural/Computational Verification
        # If we can structurally verify the answer, confidence goes up
        struct_match = False
        
        # Check comparatives
        comp_res = self._check_comparatives(prompt, answer)
        if comp_res == 1.0:
            struct_match = True
        elif comp_res == 0.0:
            return 0.1 # Definitely wrong based on logic
            
        # Check negation
        neg_res = self._check_negation_logic(prompt, answer)
        if neg_res == 0.0:
            return 0.1
            
        # Base confidence on structural match
        base_conf = 0.6 if struct_match else 0.5
        
        # Boost if numeric match found in a math context
        nums = self._extract_numbers(prompt)
        if len(nums) > 0:
            cand_nums = self._extract_numbers(answer)
            if cand_nums:
                # Simple heuristic: if numbers match, higher confidence
                if any(abs(n - cand_nums[0]) < 0.01 for n in nums):
                    base_conf = 0.85 # High but not 1.0 (avoids overconfidence trap)
        
        # Cap at 0.9 as per instructions unless it's a pure calculation we solved
        # Since we don't have a full symbolic solver, we cap at 0.9
        final_conf = min(base_conf, 0.9)
        
        # Apply meta cap if it was borderline (e.g. 0.4)
        if meta_val < 1.0:
            final_conf = min(final_conf, meta_val)
            
        return final_conf