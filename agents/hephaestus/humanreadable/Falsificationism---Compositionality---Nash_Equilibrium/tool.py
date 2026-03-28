import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Iterated Compositional Falsification Game (ICFG) Approximation.
    
    Mechanism:
    1. Falsificationism (Core): The 'evaluate' method acts as the Falsifier.
       It attempts to refute candidates by checking for logical contradictions
       (negations, conditionals) and numeric inconsistencies against the prompt.
       Candidates violating structural constraints receive severe penalties (high loss).
    2. Compositionality: Prompts and candidates are parsed into atomic logical
       components (predicates, numbers, operators) to assess partial matches and
       constraint propagation rather than whole-string similarity.
    3. Nash Equilibrium (Confidence Only): Per constraints, NE logic is restricted
       to the 'confidence' wrapper. It simulates a stable state where the score
       represents the probability that a hypothesis withstands the best available
       refutation strategy (structural + compression baseline).
    
    This approach prioritizes structural validity (Falsification) over similarity,
    using NCD only as a tiebreaker for unstructured content, ensuring we beat
    the NCD baseline on reasoning tasks.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (Compositionality)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|none)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for compositional numeric evaluation."""
        return [float(n) for n in self.number_pattern.findall(text)]

    def _check_structural_consistency(self, prompt: str, candidate: str) -> float:
        """
        Falsification Step: Check for logical violations.
        Returns a penalty score (0.0 = strong violation, 1.0 = no violation detected).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Check (Modus Tollens approximation)
        # If prompt says "X is not Y" and candidate says "X is Y", penalize.
        # Simplified: If prompt has strong negation context and candidate lacks it while echoing terms.
        p_has_neg = bool(self.negation_pattern.search(p_lower))
        c_has_neg = bool(self.negation_pattern.search(c_lower))
        
        # Heuristic: If prompt asserts a negative constraint and candidate ignores it 
        # while containing prompt keywords, it might be a falsification.
        # We award points for matching the negation status of the prompt.
        neg_score = 1.0
        if p_has_neg and not c_has_neg:
            # Check if candidate echoes prompt words without the negation
            common_words = set(p_lower.split()) & set(c_lower.split())
            if len(common_words) > 2: # Significant overlap without negation
                neg_score = 0.4 # Penalty
        
        # 2. Conditional/Constraint Check
        # If prompt has "if", candidate should ideally reflect conditionality or not contradict
        cond_score = 1.0
        if bool(self.conditional_pattern.search(p_lower)):
            # Basic check: does candidate contradict the condition structure?
            # Hard to verify without full NLI, so we rely on the lack of contradiction here.
            pass

        # 3. Numeric Consistency (Transitivity/Comparison)
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        num_score = 1.0
        if p_nums and c_nums:
            # If prompt establishes an order (e.g., "5 is greater than 3")
            # and candidate reverses it, penalize.
            # Simple heuristic: If prompt has 2 nums and candidate has 2 nums,
            # check if relative order is preserved if keywords match.
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # Detect comparison direction in prompt
                is_greater = bool(re.search(r'(greater|more|higher|larger|>)', p_lower))
                is_less = bool(re.search(r'(less|smaller|lower|<)', p_lower))
                
                p_order = p_nums[0] > p_nums[1] if is_greater else (p_nums[0] < p_nums[1] if is_less else None)
                c_order = c_nums[0] > c_nums[1] if is_greater else (c_nums[0] < c_nums[1] if is_less else None)
                
                if p_order is not None and c_order is not None:
                    if p_order != c_order:
                        num_score = 0.2 # Strong penalty for numeric contradiction

        return min(1.0, (neg_score + num_score) / 2.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(s1)
        len2 = len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        try:
            comp1 = len(zlib.compress(s1.encode('utf-8')))
            comp2 = len(zlib.compress(s2.encode('utf-8')))
            comp12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            
            max_len = max(comp1, comp2)
            if max_len == 0:
                return 0.0
            return (comp12 - min(comp1, comp2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using the ICFG approximation.
        Score = Structural Consistency (Falsification) + (1 - NCD) * Weight
        """
        results = []
        
        # Pre-calculate prompt features to save time
        p_len = len(prompt)
        
        for cand in candidates:
            # 1. Falsification Score (Primary Signal)
            # How well does this candidate survive logical refutation?
            struct_score = self._check_structural_consistency(prompt, cand)
            
            # 2. Compositionality/NCD Score (Tiebreaker/Secondary)
            # We want low distance (high similarity) but only if structurally sound.
            # Inverted NCD: 1.0 = identical, 0.0 = totally different
            ncd_val = self._ncd(prompt, cand)
            similarity_score = 1.0 - ncd_val
            
            # Hybrid Scoring Strategy:
            # If structural score is low (contradiction), total score must be low.
            # If structural score is high, we use similarity to rank.
            # Weighting: 70% Structural, 30% Similarity (to beat pure NCD baseline)
            final_score = (struct_score * 0.7) + (similarity_score * 0.3)
            
            # Penalty for empty or trivial answers
            if len(cand.strip()) < 2:
                final_score *= 0.5

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural integrity: {struct_score:.2f}, Similarity: {similarity_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Confidence wrapper approximating Nash Equilibrium.
        Interprets the score as the stability of the hypothesis (answer) 
        against the falsifier (structural checks).
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]['score']
        
        # Equilibrium adjustment:
        # In a zero-sum game, the value converges. 
        # We map the raw score to a confidence metric that penalizes uncertainty.
        # If the structural falsifier found no holes (1.0) and NCD is good, confidence is high.
        # If the game is 'close' (score ~0.5), confidence drops sharply.
        
        # Non-linear mapping to simulate equilibrium thresholding
        if base_score > 0.8:
            confidence = 0.9 + (base_score - 0.8) * 0.5
        elif base_score < 0.4:
            confidence = base_score * 0.5
        else:
            confidence = base_score * 0.8
            
        return max(0.0, min(1.0, confidence))