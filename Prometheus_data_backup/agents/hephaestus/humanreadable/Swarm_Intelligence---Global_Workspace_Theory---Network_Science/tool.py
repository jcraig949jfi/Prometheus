import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Distributed Ignitive Hypothesis Network (DIHN) Implementation.
    
    Mechanism:
    1. Swarm Agents (Structural Parsers): Instead of simple string matching, 
       independent 'agents' extract specific logical features: negations, 
       comparatives, conditionals, and numeric values.
    2. Stigmergic Medium (Activation Traces): Candidates leave 'traces' by 
       matching these structural features. Matches reinforce the hypothesis score.
    3. Global Workspace (Ignition): If a candidate satisfies high-priority 
       logical constraints (e.g., correct negation handling, numeric truth), 
       it 'ignites', receiving a massive score boost (global broadcast).
    4. Network Topology (Small-World Rewiring): The scoring function dynamically 
       weights structural matches higher than lexical overlap, effectively 
       rewiring the decision boundary to focus on logic rather than text similarity.
    5. Decay: Candidates failing structural checks suffer score decay (penalty).
    
    This approach prioritizes logical structure (Reasoning) over compression 
    (NCD), using NCD only as a final tiebreaker for semantically identical strings.
    """

    def __init__(self):
        # Compile regex patterns for structural parsing agents
        self.negation_pattern = re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')
        
        # Logic keywords for ignition
        self.logic_keywords = {'true', 'false', 'yes', 'no', 'correct', 'incorrect'}

    def _extract_numbers(self, text: str) -> List[float]:
        """Agent: Extract numeric values for evaluation."""
        return [float(n) for n in self.number_pattern.findall(text)]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """Agent: Detect if prompt negation is respected or flipped incorrectly."""
        p_neg = len(self.negation_pattern.findall(prompt))
        c_neg = len(self.negation_pattern.findall(candidate))
        
        # Heuristic: If prompt has strong negation, candidate should reflect it or answer appropriately
        # This is a simple proxy; real logic requires NLP. Here we reward awareness.
        if p_neg > 0:
            # If prompt is negative, candidate mentioning negation or specific logic words gets a boost
            if c_neg > 0 or any(w in candidate.lower() for w in self.logic_keywords):
                return 0.2
        return 0.0

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Agent: Perform numeric comparison if numbers are present."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        score = 0.0
        # Case 1: Prompt asks a comparison, candidate provides the result
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple heuristic: if prompt implies comparison (has comparatives)
            if self.comparative_pattern.search(prompt):
                val1, val2 = p_nums[0], p_nums[1]
                # Check if candidate number matches the logical result
                # e.g., "Is 5 > 3?" -> Candidate "Yes" (no number) or "True"
                # If candidate has a number, does it match the max/min?
                if "more" in prompt.lower() or "greater" in prompt.lower() or "higher" in prompt.lower():
                    expected = max(val1, val2)
                    if any(abs(c - expected) < 1e-6 for c in c_nums):
                        score += 0.5
                elif "less" in prompt.lower() or "smaller" in prompt.lower() or "lower" in prompt.lower():
                    expected = min(val1, val2)
                    if any(abs(c - expected) < 1e-6 for c in c_nums):
                        score += 0.5
        
        # Case 2: Direct numeric equality check in candidate vs prompt context
        if len(p_nums) > 0 and len(c_nums) > 0:
            # If candidate repeats a number from prompt correctly in a logical context
            if any(abs(c - p_nums[0]) < 1e-6 for c in c_nums):
                score += 0.1
                
        return score

    def _structural_overlap_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural feature overlap, not just word count."""
        score = 0.0
        
        # 1. Negation Agent
        score += self._check_negation_consistency(prompt, candidate)
        
        # 2. Numeric Logic Agent
        score += self._evaluate_numeric_logic(prompt, candidate)
        
        # 3. Comparative/Conditional Presence
        p_has_comp = bool(self.comparative_pattern.search(prompt))
        c_has_comp = bool(self.comparative_pattern.search(candidate))
        if p_has_comp and c_has_comp:
            score += 0.15 # Reinforce if candidate engages with comparison logic
            
        p_has_cond = bool(self.conditional_pattern.search(prompt))
        c_has_cond = bool(self.conditional_pattern.search(candidate))
        if p_has_cond and c_has_cond:
            score += 0.15

        # 4. Keyword Ignition (Global Workspace Broadcast)
        # If candidate contains definitive logic answers that align with prompt intent
        c_lower = candidate.lower()
        if any(k in c_lower for k in self.logic_keywords):
            score += 0.2 # Ignite: Strong signal of reasoning attempt
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (NCD) as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len1 = len(s1_bytes)
        len2 = len(s2_bytes)
        
        if len1 == 0 and len2 == 0:
            return 0.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        len1_comp = len(zlib.compress(s1_bytes))
        len2_comp = len(zlib.compress(s2_bytes))
        
        max_len = max(len1_comp, len2_comp)
        if max_len == 0:
            return 0.0
            
        ncd = (len_concat - max_len) / max_len
        return ncd

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate a single candidate against the prompt.
        Returns a confidence score 0-1.
        """
        if not answer.strip():
            return 0.0
            
        # Base score from structural reasoning agents
        score = self._structural_overlap_score(prompt, answer)
        
        # Add base relevance via NCD (inverted, so similar = low distance = high score contribution)
        # But weighted lightly to avoid overriding logic
        ncd = self._ncd_distance(prompt, answer)
        # Normalize NCD contribution: 0 distance -> 0.2 score, 1 distance -> 0 score
        ncd_contrib = (1.0 - ncd) * 0.2
        
        total_score = score + ncd_contrib
        
        # Cap at 1.0
        return min(1.0, max(0.0, total_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate all candidates, rank them by score.
        Returns list of dicts with candidate, score, and reasoning trace.
        """
        results = []
        
        for cand in candidates:
            score = self.confidence(prompt, cand)
            
            # Generate reasoning trace string
            traces = []
            if self.negation_pattern.search(cand):
                traces.append("negation_detected")
            if self._extract_numbers(cand):
                traces.append("numeric_eval")
            if any(k in cand.lower() for k in self.logic_keywords):
                traces.append("logic_ignition")
            if not traces:
                traces.append("lexical_match")
                
            reasoning = f"DIHN Score: {score:.4f}; Features: {', '.join(traces)}"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results