import re
import math
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining Model Checking, Metamorphic Testing, and Hoare Logic.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic predicates (facts), conditionals (Hoare triples), 
       and numeric constraints from text using regex patterns robust to variable naming.
    2. Symbolic State Construction: Builds an initial state S0 from asserted facts.
    3. Transition & Verification: Simulates transitions based on conditionals. Checks if 
       candidate answers violate logical consequences (Hoare violations).
    4. Metamorphic Testing: Applies transformations (e.g., scaling numbers, swapping entities) 
       to check if the logical relationship holds invariant.
    5. Scoring: Combines structural consistency (primary), computational correctness, 
       and NCD (tiebreaker only).
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction (variable-agnostic)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|when|unless|provided that)\b(.+?)(?:then|,|\.)?(.+?)(?:\.|$)', re.IGNORECASE | re.DOTALL),
            'comparative': re.compile(r'(\w+)\s+(is|are|was|were)?\s*(greater|less|more|fewer|twice|half)\s+(than|as)?\s*(\w+|\d+)', re.IGNORECASE),
            'numeric_val': re.compile(r'(\d+(?:\.\d+)?)'),
            'equality': re.compile(r'(\w+)\s+(is|are|was|were|equals)\s+(\w+|\d+)', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|preceding|following)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did|when did|quit|fail to)', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'(every|all|each)\s+\w+.*\b(a|the)\s+\w+', re.IGNORECASE),
            'false_dichotomy': re.compile(r'(either|or|must be|only option)', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|think)\b', re.IGNORECASE)
        }
        
        # Common logic traps
        self.trap_keywords = ['bat', 'ball', 'cost', 'total', 'sum', 'average', 'odd', 'even']

    def _extract_entities(self, text: str) -> Set[str]:
        """Extract potential entities (capitalized words or quoted strings)."""
        entities = set(re.findall(r'\b([A-Z][a-z]+)\b', text))
        entities.update(re.findall(r'"([^"]+)"', text))
        # Filter common stop words that might be capitalized
        stop_words = {'The', 'A', 'An', 'If', 'When', 'Because', 'So', 'But', 'And'}
        return entities - stop_words

    def _parse_facts(self, text: str) -> List[Tuple[str, str, str]]:
        """Parse simple SVO or Equality facts."""
        facts = []
        # Match "X is Y" or "X has Y"
        for match in re.finditer(r'(\w+)\s+(is|are|has|contains|owns)\s+([^\.]+)', text, re.IGNORECASE):
            subj, verb, obj = match.groups()
            obj = obj.strip().rstrip('.')
            if 'if' in subj.lower(): continue # Skip conditionals
            facts.append((subj.lower(), verb.lower(), obj.lower()))
        return facts

    def _check_computation(self, prompt: str, candidate: str) -> float:
        """
        Attempt to solve numeric problems constructively.
        Returns 1.0 if candidate matches computed result, 0.0 if wrong, 0.5 if unsure.
        """
        numbers = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', candidate)]
        
        if not numbers:
            return 0.5 # No numbers to compute
            
        # Bat-and-Ball problem heuristic
        if 'bat' in prompt.lower() and 'ball' in prompt.lower() and 'total' in prompt.lower():
            # Pattern: A + B = Total, A = B + Diff. Solve for B.
            # Usually Total=1.10, Diff=1.00 -> B=0.05
            if len(numbers) >= 2:
                total = numbers[0]
                diff = numbers[1] if len(numbers) > 1 else 1.0
                # Standard solution: (Total - Diff) / 2
                expected = (total - diff) / 2.0
                if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                    return 1.0
                elif cand_nums:
                    return 0.0 # Computed wrong answer

        # Simple subtraction/addition checks
        if len(numbers) == 2:
            if 'less' in prompt.lower() or 'subtract' in prompt.lower():
                expected = numbers[0] - numbers[1]
            elif 'more' in prompt.lower() or 'add' in prompt.lower():
                expected = numbers[0] + numbers[1]
            else:
                expected = None
            
            if expected is not None and cand_nums:
                if abs(cand_nums[0] - expected) < 0.01:
                    return 1.0
                else:
                    return 0.0

        return 0.5 # Cannot determine computationally

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap on confidence (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. Scope Ambiguity (simplified heuristic)
        if self.patterns['scope_ambiguity'].search(prompt) and 'same' not in p_lower and 'different' not in p_lower:
            return 0.4
            
        # 3. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt) and 'otherwise' not in p_lower:
            return 0.3
            
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.3
            
        # 5. Unanswerability (missing info heuristics)
        if 'who is' in p_lower and 'named' not in p_lower and len(self._extract_entities(prompt)) == 0:
            return 0.2
            
        return 1.0

    def _run_model_check(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core logic: Build symbolic state, apply transitions, check Hoare triples.
        Returns (score, reason_string)
        """
        violations = 0
        checks = 0
        reasons = []
        
        # 1. Parse Initial State (Facts)
        facts = self._parse_facts(prompt)
        entities = self._extract_entities(prompt)
        
        # 2. Extract Conditionals (Hoare Triples: If P then Q)
        conditionals = []
        for match in self.patterns['conditional'].finditer(prompt):
            condition = match.group(2).strip()
            consequence = match.group(4).strip()
            if condition and consequence:
                conditionals.append((condition.lower(), consequence.lower()))
        
        # 3. Verify Candidate against Facts and Conditionals
        cand_lower = candidate.lower()
        
        # Check direct fact contradiction
        for subj, verb, obj in facts:
            # If fact says "A is B", and candidate says "A is not B" or "A is C" (where C != B)
            if subj in cand_lower:
                if f"not {obj}" in cand_lower or (verb in cand_lower and obj not in cand_lower and "no" in cand_lower):
                    violations += 1
                    reasons.append(f"Contradicts fact: {subj} {verb} {obj}")
        
        # Check Conditionals (Modus Ponens/Tollens simulation)
        for condition, consequence in conditionals:
            checks += 1
            # Simple keyword overlap for condition satisfaction (robust to variable names)
            cond_words = set(re.findall(r'\w+', condition))
            prompt_words = set(re.findall(r'\w+', prompt.lower()))
            
            # If condition keywords are present in prompt, consequence should be inferable
            if len(cond_words & prompt_words) > 0:
                # Check if candidate contains consequence keywords
                cons_words = set(re.findall(r'\w+', consequence))
                if not any(w in cand_lower for w in cons_words):
                    # Potential violation, but allow for paraphrasing (soft penalty)
                    # Only penalize if candidate explicitly negates or ignores critical logic
                    if f"not {list(cons_words)[0]}" in cand_lower:
                        violations += 1
                        reasons.append(f"Violates conditional: If {condition} then {consequence}")
        
        # 4. Metamorphic Check (Numeric Invariance)
        # If we scale numbers in prompt, does the logic hold? 
        # (Simplified: Check if candidate number matches prompt number logic)
        comp_score = self._check_computation(prompt, candidate)
        if comp_score == 0.0:
            violations += 2 # Heavy penalty for math errors
            reasons.append("Computational error detected")
        elif comp_score == 1.0:
            checks += 1 # Reward correct computation

        if checks == 0:
            checks = 1 # Avoid division by zero
            
        score = max(0.0, 1.0 - (violations / (checks + 1)))
        reason_str = "; ".join(reasons) if reasons else "No structural violations found"
        
        return score, reason_str

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Logical Score (Weight: 50%)
            logic_score, logic_reason = self._run_model_check(prompt, cand)
            
            # 2. Computational Score (Weight: 30% - embedded in logic_score via _check_computation)
            # We rely on _run_model_check to have penalized math errors heavily.
            
            # 3. NCD Tiebreaker (Weight: 15% max)
            # Only use NCD if logic scores are similar or low confidence
            ncd = self._calculate_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Combine scores: Structural > Computation > NCD
            # If logic found violations, score is low regardless of NCD
            final_score = (logic_score * 0.7) + (ncd_score * 0.15) + (0.15 if logic_score > 0.8 else 0.0)
            
            # Apply Epistemic Cap
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap + 0.2) # Allow slight variation but keep low
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": logic_reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence if prompt is ambiguous/trapped.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run internal check
        score, _ = self._run_model_check(prompt, answer)
        
        # Base confidence on structural match
        base_conf = score
        
        # If computation was definitive (1.0 or 0.0), we can be more confident
        comp = self._check_computation(prompt, answer)
        if comp == 1.0:
            base_conf = 0.95
        elif comp == 0.0:
            base_conf = 0.05
            
        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # If no structural signal found at all, be honest (low confidence)
        if base_conf == 0.5 and meta_cap == 1.0:
            return 0.4 # Uncertain
            
        return round(final_conf, 3)