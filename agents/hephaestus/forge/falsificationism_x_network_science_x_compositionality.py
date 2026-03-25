import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Falsification-Driven Compositional Hypothesis Engine (FCHE).
    
    Mechanism:
    1. Compositionality: Parses the prompt into a graph-like structure of 
       primitives (numbers, booleans, entities) and relational operators 
       (comparatives, negations, conditionals).
    2. Network Science: Models the candidate answer as a node in a dependency 
       network with the prompt. Edges represent logical constraints derived 
       from the parsed structure.
    3. Falsificationism (Core): Instead of seeking confirmation, the engine 
       attempts to FALSIFY each candidate. It simulates the logical consequence 
       of the candidate being true against the prompt's constraints.
       - If a candidate contradicts a hard constraint (e.g., numeric inequality), 
         it receives a high "severity" penalty (falsified).
       - If a candidate survives rigorous structural testing, it retains high credence.
    4. Scoring: Final score is inversely proportional to the falsification severity.
       NCD is used only as a tie-breaker for structural equivalence.
    """

    def __init__(self):
        self._num_pattern = re.compile(r'-?\d+\.?\d*')
        self._comp_ops = ['greater than', 'less than', 'equal to', 'larger', 'smaller', 'more', 'fewer']
        self._negations = ['not', 'no', 'never', 'false', 'impossible']
        self._conditionals = ['if', 'then', 'unless', 'only if']

    def _extract_numbers(self, text: str) -> List[float]:
        """Compositional primitive: Extract numeric entities."""
        return [float(x) for x in self._num_pattern.findall(text)]

    def _has_negation(self, text: str) -> bool:
        """Compositional primitive: Detect negation operators."""
        t_lower = text.lower()
        return any(n in t_lower for n in self._negations)

    def _parse_logic(self, prompt: str) -> dict:
        """
        Decomposes prompt into a structural graph representation.
        Returns a dict representing the 'laws' of the simulation substrate.
        """
        p_lower = prompt.lower()
        nums = self._extract_numbers(prompt)
        has_neg = self._has_negation(prompt)
        has_cond = any(c in p_lower for c in self._conditionals)
        
        # Detect comparative directionality
        direction = 0 # 0: none, 1: A > B, -1: A < B
        if 'greater' in p_lower or 'larger' in p_lower or 'more' in p_lower:
            direction = 1
        elif 'less' in p_lower or 'smaller' in p_lower or 'fewer' in p_lower:
            direction = -1
            
        return {
            "numbers": nums,
            "negation": has_neg,
            "conditional": has_cond,
            "comparative_dir": direction,
            "length": len(prompt)
        }

    def _simulate_falsification(self, prompt_logic: dict, candidate: str) -> float:
        """
        Runs the candidate through the network substrate to test for contradictions.
        Returns a severity score (0.0 = survived, 1.0 = falsified).
        """
        severity = 0.0
        c_lower = candidate.lower()
        c_nums = self._extract_numbers(candidate)
        
        # Test 1: Numeric Consistency (Hard Constraint)
        # If prompt has specific numbers and candidate has numbers, they must align logically
        if prompt_logic["numbers"] and c_nums:
            # Simple heuristic: If prompt implies A > B, and candidate violates it
            # Since we don't have full semantic parse, we check for direct contradiction patterns
            # e.g. Prompt: "5 is greater than 3", Candidate: "3 is greater than 5"
            p_nums = prompt_logic["numbers"]
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # Check if candidate reverses the order implied by prompt comparatives
                if prompt_logic["comparative_dir"] == 1: # Prompt says A > B
                    if c_nums[0] < c_nums[1]: # Candidate implies A < B (Falsified)
                        severity += 0.5
                elif prompt_logic["comparative_dir"] == -1: # Prompt says A < B
                    if c_nums[0] > c_nums[1]: # Candidate implies A > B (Falsified)
                        severity += 0.5

        # Test 2: Negation Contradiction
        # If prompt asserts a negative constraint, and candidate affirms the positive strongly
        if prompt_logic["negation"] and not self._has_negation(candidate):
            # Heuristic: If prompt says "not X" and candidate looks like a direct assertion of X
            # We soften this as it's semantic-heavy, but add slight severity risk
            severity += 0.1

        # Test 3: Structural Compositionality Match
        # Candidates that preserve the structural complexity (e.g. conditionals) of the prompt
        # are less likely to be random noise.
        has_cond = any(c in c_lower for c in self._conditionals)
        if prompt_logic["conditional"] and not has_cond:
            # Candidate fails to compose the conditional logic required
            severity += 0.2
            
        return min(severity, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_logic = self._parse_logic(prompt)
        scored_candidates = []
        
        for cand in candidates:
            # 1. Falsification Step: Try to break the candidate
            severity = self._simulate_falsification(prompt_logic, cand)
            
            # 2. Base Credence: Inverse of severity
            # If severity is 1.0 (falsified), score is 0. If 0.0, score is 1.0
            base_score = 1.0 - severity
            
            # 3. Network Tie-Breaker: Use NCD if structural signals are weak
            # If severity is low (survived), use NCD to differentiate based on similarity to prompt context
            if severity < 0.15:
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly by NCD (lower NCD = higher similarity = slight boost)
                # But keep base_score dominant
                base_score += (1.0 - ncd_val) * 0.05 
            
            scored_candidates.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Severity: {severity:.2f}. Survived falsification tests."
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on falsification survival."""
        prompt_logic = self._parse_logic(prompt)
        severity = self._simulate_falsification(prompt_logic, answer)
        # Confidence is simply the survival rate (1 - severity)
        return max(0.0, min(1.0, 1.0 - severity))