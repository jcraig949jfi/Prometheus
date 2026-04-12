class ReasoningTool:
    """
    I-E-GAIE Implementation (Adapted for Robustness):
    Uses 'Ecosystem Dynamics' only for structural parsing (niche identification).
    Uses 'Information Theory' as a secondary validator (NCD tiebreaker).
    Uses 'Abductive Reasoning' via constraint propagation and logical form matching.
    
    Strategy:
    1. Structural Parsing: Extract logic operators (negations, comparatives, conditionals).
    2. Numeric Evaluation: Resolve number comparisons explicitly.
    3. Abductive Scoring: Match candidate logical forms to prompt logical forms.
    4. Ecosystem/Info Filter: Use NCD only to break ties among structurally valid candidates.
    """

    def __init__(self):
        self.num_pattern = re.compile(r"-?\d+\.?\d*")
        self.comp_ops = [">", "<", ">=", "<=", "==", "!=", "greater", "less", "equal"]
        self.neg_words = ["no", "not", "never", "none", "neither", "n't"]
        self.cond_words = ["if", "then", "else", "unless", "when"]

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(n) for n in self.num_pattern.findall(text)]

    def _has_negation(self, text: str) -> bool:
        t_lower = text.lower()
        return any(w in t_lower for w in self.neg_words) or "!" in text

    def _has_condition(self, text: str) -> bool:
        t_lower = text.lower()
        return any(w in t_lower for w in self.cond_words)

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Returns 1.0 if numeric logic holds, 0.5 if ambiguous, 0.0 if contradicts."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # If no numbers, return neutral
        if not p_nums or not c_nums:
            return 0.5
        
        # Simple heuristic: If prompt has comparison words, check if candidate result matches
        p_text = prompt.lower()
        has_comp = any(op in p_text for op in self.comp_ops)
        
        if has_comp:
            # If prompt implies a comparison, does the candidate provide the correct result?
            # This is a simplified abductive check: does the candidate number appear in prompt?
            # If the candidate is just a number, check if it's the max/min based on context
            if len(c_nums) == 1:
                val = c_nums[0]
                # If prompt asks for "greater", and candidate is the max of prompt numbers
                if "greater" in p_text or ">" in p_text:
                    if val == max(p_nums): return 1.0
                if "less" in p_text or "<" in p_text:
                    if val == min(p_nums): return 1.0
                # If it's just a number present in the prompt, it's plausible but not proven
                if val in p_nums: return 0.6
        return 0.5

    def _structural_signature(self, text: str) -> tuple:
        """Creates a hashable signature of logical structures."""
        t = text.lower()
        has_neg = self._has_negation(t)
        has_cond = self._has_condition(t)
        num_count = len(self._extract_numbers(t))
        # Count specific logical keywords
        neg_count = sum(t.count(w) for w in self.neg_words)
        return (has_neg, has_cond, num_count, neg_count)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 1.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_sig = self._structural_signature(prompt)
        p_has_neg = p_sig[0]
        p_has_cond = p_sig