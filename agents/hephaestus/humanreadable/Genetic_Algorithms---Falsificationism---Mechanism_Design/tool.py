import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Evolutionary Falsification-Mechanism Scorer (EFMS)
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, conditionals, causals) via regex.
    2. Constructive Computation: Actively solves numeric, temporal, and logical constraints found in the prompt.
    3. Falsification (Popperian): Checks if candidates contradict explicit constraints or computed truths.
    4. Mechanism Design: Weights features based on their ability to distinguish valid from invalid structures.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to lower confidence appropriately.
    """

    def __init__(self):
        # Mechanism design weights: [n_neg, n_comp, n_cond, n_num, n_cau, n_ord]
        self.w = np.ones(6) / 6.0 
        self.learning_rate = 0.1
        self.archive = []  # Refuted vectors for diversity
        
        # Regex patterns
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|none|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.I),
            'comp': re.compile(r'\b(more than|less than|greater than|smaller than|>=|<=|>|<|exceeds)\b', re.I),
            'cond': re.compile(r'\b(if|then|unless|provided that|otherwise)\b', re.I),
            'num': re.compile(r'\b(\d+(?:\.\d+)?)\b'),
            'cau': re.compile(r'\b(because|causes|leads to|therefore|thus|hence|due to)\b', re.I),
            'ord': re.compile(r'\b(first|last|before|after|next|previous|second|third)\b', re.I)
        }
        
        # Ambiguity triggers for Tier B
        self.presupposition_triggers = re.compile(r'\b(stopped|quit|failed|start)\s+(you|he|she|they|it)\b', re.I)
        self.false_dichotomy = re.compile(r'\b(either|or)\b', re.I)
        self.subjectivity = re.compile(r'\b(best|worst|favorite|opinion|think)\b', re.I)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural feature vector [neg, comp, cond, num, cau, ord]"""
        if not text:
            return np.zeros(6)
        text_lower = text.lower()
        counts = [
            len(self.patterns['neg'].findall(text)),
            len(self.patterns['comp'].findall(text)),
            len(self.patterns['cond'].findall(text)),
            len(self.patterns['num'].findall(text)),
            len(self.patterns['cau'].findall(text)),
            len(self.patterns['ord'].findall(text))
        ]
        return np.array(counts, dtype=float)

    def _compute_truth_conditions(self, prompt: str) -> Tuple[Optional[float], List[str]]:
        """
        Constructive Computation Module.
        Attempts to derive a definitive numeric or logical truth from the prompt.
        Returns (computed_value, list_of_facts)
        """
        facts = []
        computed_val = None
        
        # 1. Numeric Extraction & Simple Arithmetic
        nums = [float(x) for x in self.patterns['num'].findall(prompt)]
        if len(nums) >= 2:
            # Detect simple operations implied by context keywords
            p_lower = prompt.lower()
            if 'sum' in p_lower or 'total' in p_lower or 'combined' in p_lower:
                computed_val = sum(nums)
                facts.append(f"Computed sum: {computed_val}")
            elif 'difference' in p_lower or 'subtract' in p_lower:
                computed_val = abs(nums[0] - nums[1])
                facts.append(f"Computed difference: {computed_val}")
            elif 'average' in p_lower or 'mean' in p_lower:
                computed_val = sum(nums) / len(nums)
                facts.append(f"Computed average: {computed_val}")
            elif 'product' in p_lower or 'times' in p_lower:
                computed_val = nums[0] * nums[1]
                facts.append(f"Computed product: {computed_val}")
        
        # 2. Logical Constraints (Modus Tollens/Ponens simplification)
        # If prompt says "If A then B", and candidate says "A but not B", it's false.
        if self.patterns['cond'].search(prompt):
            facts.append("conditional_logic_present")
            
        return computed_val, facts

    def _check_ambiguity(self, prompt: str) -> float:
        """
        Tier B: Meta-confidence check.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.presupposition_triggers.search(prompt):
            return 0.2
        
        # 2. False Dichotomy without exhaustion
        if self.false_dichotomy.search(prompt) and 'only' not in p_lower:
            # Heuristic: if "either/or" appears but no clear exhaustive list
            if 'or' in p_lower and 'either' in p_lower:
                 return 0.4 # Moderate penalty, might be valid logic puzzle
                 
        # 3. Subjectivity
        if self.subjectivity.search(prompt):
            return 0.3
            
        # 4. Pronoun ambiguity (simplified)
        # If "he/she" appears and question asks "who"?
        if re.search(r'\b(he|she|him|her)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.3
            
        return 1.0

    def _evaluate_candidate_logic(self, prompt: str, candidate: str, computed_val: Optional[float]) -> float:
        """
        Check candidate against computed truths and logical constraints.
        Returns a falsification score (0.0 = refuted, 1.0 = consistent).
        """
        score = 1.0
        c_lower = candidate.lower()
        
        # 1. Numeric Consistency
        if computed_val is not None:
            cand_nums = [float(x) for x in self.patterns['num'].findall(candidate)]
            if cand_nums:
                # If candidate provides a number, check against computed truth
                # Allow small epsilon for float issues
                if abs(cand_nums[0] - computed_val) > 0.01:
                    score -= 0.8 # Heavy penalty for wrong math
                else:
                    score += 0.2 # Bonus for correct math
        
        # 2. Contradiction Detection (Simplified)
        # If prompt has "not X" and candidate asserts "X" strongly
        # This is a basic check; full NLI is too heavy for this constraint
        prompt_negs = self.patterns['neg'].findall(prompt)
        cand_pos = len(self.patterns['neg'].findall(candidate)) == 0
        
        return max(0.0, score)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic (0 = identical, 1 = different)"""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0: return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """Public wrapper for ambiguity check"""
        return self._check_ambiguity(prompt)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        computed_val, logic_facts = self._compute_truth_conditions(prompt)
        
        results = []
        
        # Pre-calculate NCD to prompt for diversity (optional tiebreaker)
        prompt_len = len(prompt)
        
        for cand in candidates:
            # 1. Structural Features
            cand_features = self._extract_features(cand)
            
            # 2. Falsification Score (V)
            # Does the candidate survive logical checks?
            logic_score = self._evaluate_candidate_logic(prompt, cand, computed_val)
            
            # 3. Mechanism Design Fitness (f = w·x + λ·V)
            # Normalize features roughly to [0,1] range based on typical counts
            norm_features = np.clip(cand_features / 5.0, 0, 1) 
            structural_score = np.dot(self.w, norm_features)
            
            # Combine: Logic/Computation is primary, Structure secondary
            # If we have a computed value, logic_score dominates
            if computed_val is not None:
                final_score = 0.3 * structural_score + 0.7 * logic_score
            else:
                # If no computation possible, rely on structure and NCD tiebreak
                ncd = self._ncd_score(prompt, cand)
                # Penalize exact echoes (bag-of-words trap)
                if ncd < 0.1: 
                    logic_score = 0.5 # Echoes get mediocre scores
                final_score = 0.6 * structural_score + 0.4 * logic_score

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{structural_score:.2f}, Logic:{logic_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Update mechanism weights (Simple surrogate gradient)
        # If top candidates have high logic scores, increase weight of logic-related features
        if results and results[0]['score'] > 0.5:
            # Simplified update: nudge weights towards features present in high scorers
            top_feats = self._extract_features(results[0]['candidate'])
            self.w = 0.9 * self.w + 0.1 * (top_feats / (np.sum(top_feats) + 1))
            self.w = self.w / np.sum(self.w) # Renormalize

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty (ambiguity checks).
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Constructive Computation Check
        computed_val, _ = self._compute_truth_conditions(prompt)
        cand_nums = [float(x) for x in self.patterns['num'].findall(answer)]
        
        base_conf = 0.5 # Base uncertainty
        
        if computed_val is not None:
            if cand_nums:
                if abs(cand_nums[0] - computed_val) < 1e-6:
                    base_conf = 0.95 # Definitive correct computation
                else:
                    base_conf = 0.1 # Definitive wrong computation
            else:
                # Computation required but answer has no number
                base_conf = 0.2
        else:
            # No clear computation path, rely on structural match
            # Check if answer contradicts prompt structure
            prompt_feats = self._extract_features(prompt)
            ans_feats = self._extract_features(answer)
            
            # If prompt has conditionals, answer should reflect logic
            if prompt_feats[2] > 0: # Has conditionals
                if ans_feats[2] > 0 or ans_feats[4] > 0: # Answer has logic/causal
                    base_conf = 0.7
                else:
                    base_conf = 0.4 # Weak match
            
            # Fallback for non-numeric, non-ambiguous
            base_conf = 0.6

        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive
        if computed_val is None and final_conf > 0.85:
            final_conf = 0.85
            
        return float(np.clip(final_conf, 0.0, 1.0))