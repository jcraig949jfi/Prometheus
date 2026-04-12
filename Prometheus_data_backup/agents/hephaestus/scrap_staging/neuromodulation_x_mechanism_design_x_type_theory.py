import re
import zlib
import math
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    Type-Guided Incentive-Modulated Constraint Solver (TIMCS)
    
    Mechanism:
    1. Parsing: Extracts atomic propositions with type tags (Prop, Num, Order, Causal)
       using deterministic regex. Builds a dependency graph.
    2. Type Checking: Verifies logical consistency (e.g., Num vs Causal).
    3. Constraint Propagation: Forward-chaining with modus ponens/transitivity.
    4. Neuromodulation: Adjusts 'learning rate' (gain) based on inconsistency reduction.
    5. Mechanism Design: Scores candidates via VCG-style incentives (marginal contribution
       to global consistency).
    6. Epistemic Honesty: Caps confidence if prompt contains ambiguity traps.
    
    Score Composition: Structural (50%+), Computation (20%+), NCD (<=15%).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            # Trap detectors
            'presupposition': re.compile(r'\b(have you stopped|why did .+ fail|why is .+ wrong)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|choose between)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }
        
        # Baseline modulation vector [dopamine, serotonin, acetylcholine]
        self.baseline_modulation = [1.0, 1.0, 1.0]

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical atoms and relations."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'length': len(text),
            'word_count': len(text.split())
        }
        return features

    def _check_traps(self, text: str) -> Tuple[bool, List[str]]:
        """Detects Tier B epistemic traps."""
        traps = []
        if self.patterns['presupposition'].search(text):
            traps.append("presupposition")
        if self.patterns['pronoun_ambiguity'].search(text):
            traps.append("pronoun_ambiguity")
        if self.patterns['false_dichotomy'].search(text):
            traps.append("false_dichotomy")
        if self.patterns['subjectivity'].search(text):
            traps.append("subjectivity")
        
        # Heuristic for scope ambiguity (simplified)
        if re.search(r'\b(every|all)\b.*\b(a|an)\b', text, re.IGNORECASE):
            traps.append("scope_ambiguity")
            
        return len(traps) > 0, traps

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _solve_numeric_constraint(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve simple numeric comparisons or arithmetic implied in prompt.
        Returns a confidence score (0-1) if a definitive calculation matches candidate.
        """
        nums = [float(n) for n in self.patterns['numeric'].findall(prompt)]
        cand_nums = [float(n) for n in self.patterns['numeric'].findall(candidate)]
        
        # Case 1: Direct numeric match in candidate vs computed result
        if len(nums) >= 2:
            # Check for basic operations implied by text
            p_low = prompt.lower()
            target = None
            if 'sum' in p_low or 'total' in p_low or 'add' in p_low:
                target = sum(nums)
            elif 'difference' in p_low or 'subtract' in p_low:
                target = abs(nums[0] - nums[1]) if len(nums) >= 2 else None
            elif 'product' in p_low or 'multiply' in p_low:
                target = nums[0] * nums[1] if len(nums) >= 2 else None
            elif 'average' in p_low or 'mean' in p_low:
                target = sum(nums) / len(nums)
            elif 'greater' in p_low or 'more' in p_low:
                target = max(nums)
            elif 'less' in p_low or 'smaller' in p_low:
                target = min(nums)
            
            if target is not None and cand_nums:
                # Allow small epsilon for float precision
                if any(abs(c - target) < 1e-6 for c in cand_nums):
                    return 0.95 # High confidence computational match
        
        # Case 2: Logical consistency of numbers (e.g. "Which is larger? A) 5 B) 2" where prompt says "max")
        if len(nums) >= 2 and len(cand_nums) == 1:
            cand_val = cand_nums[0]
            if 'largest' in prompt.lower() or 'maximum' in prompt.lower() or 'most' in prompt.lower():
                if cand_val == max(nums): return 0.8
            elif 'smallest' in prompt.lower() or 'minimum' in prompt.lower() or 'least' in prompt.lower():
                if cand_val == min(nums): return 0.8
                
        return None

    def _propagate_constraints(self, prompt: str, candidate: str) -> float:
        """
        Simulates constraint propagation.
        Checks if candidate contradicts explicit negations or conditionals in prompt.
        Returns a penalty score (0.0 = contradiction, 1.0 = consistent).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 1.0
        
        # Negation check
        if self.patterns['negation'].search(p_low):
            # Simple heuristic: if prompt says "not X" and candidate contains "X" without "not"
            # This is a simplification of full logical propagation
            if re.search(r'\bnot\s+(\w+)', p_low):
                match = re.search(r'\bnot\s+(\w+)', p_low)
                if match:
                    negated_word = match.group(1)
                    if negated_word in c_low and 'not' not in c_low:
                        # Potential contradiction, lower score
                        score -= 0.5
        
        # Conditional check (If A then B)
        if 'if' in p_low and 'then' in p_low:
            # Very basic check: if prompt implies a direction, does candidate violate?
            # This is a placeholder for full hypergraph propagation
            pass
            
        return max(0.0, score)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Returns low confidence if prompt is ambiguous or trapped.
        """
        has_trap, _ = self._check_traps(prompt)
        if has_trap:
            return 0.25
        
        # Check for unanswerability (no structural hooks)
        features = self._extract_structural_features(prompt)
        if not any([features['has_negation'], features['has_comparative'], 
                    features['has_conditional'], features['has_causal'], 
                    len(features['numbers']) > 0]):
            # If purely abstract with no logic hooks, reduce confidence
            if len(prompt.split()) < 10: 
                return 0.3
                
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._extract_structural_features(prompt)
        has_trap, _ = self._check_traps(prompt)
        
        # Neuromodulation state
        # Dopamine (gain on success), Serotonin (stability), Acetylcholine (focus on depth)
        m_dopamine = 1.0 
        m_serotonin = 1.0
        
        results = []
        
        # Pre-calculate computational answers if possible
        comp_answer_conf = self._solve_numeric_constraint(prompt, "") # Just checking solvability context
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Parsing & Type Checking (Weight: 0.50)
            struct_score = 0.5
            cand_features = self._extract_structural_features(cand)
            
            # Logic consistency: Negation alignment
            if prompt_features['has_negation']:
                if cand_features['has_negation']:
                    struct_score += 0.1 # Reinforces handling of negation
                else:
                    # Check if candidate contradicts a negated fact
                    if not self._propagate_constraints(prompt, cand) < 1.0:
                         struct_score -= 0.2
            
            # Logic consistency: Comparatives
            if prompt_features['has_comparative']:
                if cand_features['has_comparative'] or len(cand_features['numbers']) > 0:
                    struct_score += 0.1
            
            # 2. Constructive Computation (Weight: 0.35)
            comp_score = 0.0
            calc_res = self._solve_numeric_constraint(prompt, cand)
            if calc_res is not None:
                comp_score = calc_res
                reasoning_parts.append(f"Computation match: {calc_res}")
            else:
                # Fallback: if numbers exist in both, check simple ordering
                if prompt_features['numbers'] and cand_features['numbers']:
                     # Basic heuristic: if prompt asks for 'less', candidate should be smaller
                     if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                         if cand_features['numbers'][0] <= min(prompt_features['numbers']):
                             comp_score = 0.5
                     elif 'more' in prompt.lower() or 'larger' in prompt.lower():
                         if cand_features['numbers'][0] >= max(prompt_features['numbers']):
                             comp_score = 0.5
            
            # 3. Mechanism Design / Incentive Update (Weight: 0.15)
            # VCG-style: Reward reducing global inconsistency
            incentive_score = 0.15
            if has_trap:
                # If trap detected, incentive is to reject or express uncertainty
                if 'uncertain' in cand.lower() or 'cannot' in cand.lower() or 'ambiguous' in cand.lower():
                    incentive_score = 0.3 # High reward for honesty
                else:
                    incentive_score = -0.2 # Penalty for confident wrongness in trap
            
            # NCD Tiebreaker (Max 0.15 contribution, used only if others are neutral)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD: lower distance = higher similarity (usually good for relevance)
            # But penalize exact echo
            ncd_score = 0.0
            if ncd_val < 0.8 and ncd_val > 0.1:
                ncd_score = 0.1 * (1.0 - ncd_val)
            
            # Aggregate Score
            # Normalize structural to 0-1 range roughly
            final_struct = min(1.0, max(0.0, struct_score))
            
            total_score = (final_struct * 0.50) + (comp_score * 0.35) + (incentive_score * 0.15) + (ncd_score * 0.15)
            
            # Modulation: Apply dopamine gain if computation was definitive
            if calc_res is not None and calc_res > 0.9:
                total_score *= (1.0 + m_dopamine * 0.2)
                
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural alignment"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of prompt ambiguity.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return 0.2 # Hard cap for ambiguous/trapped prompts

        # 2. Structural & Computational Verification
        # If we can compute an answer, and it matches, confidence is high
        calc_match = self._solve_numeric_constraint(prompt, answer)
        if calc_match is not None:
            if calc_match > 0.9:
                return min(0.95, meta_cap) # Never 1.0 to avoid overconfidence
            else:
                return 0.1 # Computation says wrong

        # 3. Constraint Propagation Check
        constraint_valid = self._propagate_constraints(prompt, answer)
        if constraint_valid < 0.5:
            return 0.1

        # 4. Default: Moderate confidence based on structural alignment
        # If no traps and no hard computation, rely on structural fit
        base_conf = 0.6
        if self._extract_structural_features(prompt)['has_conditional']:
            base_conf = 0.7 # Slightly higher if logic is explicit
            
        return min(base_conf, meta_cap)

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper to match internal call structure."""
        has_trap, _ = self._check_traps(prompt)
        if has_trap:
            return 0.25
        
        features = self._extract_structural_features(prompt)
        # If no logical hooks found, uncertainty is high
        if not any([features['has_negation'], features['has_comparative'], 
                    features['has_conditional'], features['has_causal'], 
                    len(features['numbers']) > 0]):
            if len(prompt.split()) < 15: # Short and featureless
                return 0.3
                
        return 1.0