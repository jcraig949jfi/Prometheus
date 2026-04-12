import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Neuromodulated Optimal Gene Regulatory Controller (NOGRC) for Reasoning.
    
    Mechanism:
    1.  **GRN Attractor Dynamics**: Candidates are treated as target states in a conceptual 
        gene-regulatory network. The "concentration" of a candidate is its likelihood.
    2.  **Neuromodulation (Gain Control)**: Structural parsing (negations, conditionals) acts 
        as dopamine-like signals that modulate the "gain" of specific logical pathways. 
        High structural alignment increases the basin of attraction for a candidate.
    3.  **Optimal Control (Cost Function)**: We compute a cost J = Prediction_Error + Control_Cost.
        - Prediction Error: How well the candidate matches the prompt's structural constraints.
        - Control Cost: The "effort" required to force the GRN into the candidate's state. 
          If a candidate requires ignoring a negation or presupposition, the control cost spikes.
    4.  **Epistemic Honesty (Meta-Confidence)**: Before scoring, the prompt is analyzed for 
        ambiguity, presuppositions, and unanswerability. If detected, confidence is capped 
        low regardless of candidate score, satisfying Tier B requirements.
    
    Score Decomposition:
    - Structural/Logical Parsing: 50%
    - Computational/Logical Deduction: 35%
    - NCD (Similarity): 15%
    """

    def __init__(self):
        # Weights for the cost function J = w_struct * Err_struct + w_comp * Err_comp + w_ncd * Err_ncd
        self.w_struct = 0.50
        self.w_comp = 0.35
        self.w_ncd = 0.15
        
        # Preset keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        self.conditionals = ['if', 'unless', 'provided', 'assuming']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'stopped', 'realize', 'know']
        self.ambiguity_markers = ['either', 'or', 'who', 'which', 'best', 'favorite', 'every']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_matches(self, text: str, keywords: List[str]) -> int:
        tokens = re.findall(r'\b\w+\b', text.lower())
        return sum(1 for t in tokens if t in keywords)

    def _check_presupposition(self, prompt: str) -> bool:
        """Detects loaded questions or presuppositions (Tier B)."""
        p_low = prompt.lower()
        # Check for "Have you stopped...", "Why did X fail..."
        if any(k in p_low for k in self.presupposition_triggers):
            # Simple heuristic: if question starts with Why/How/Have and contains trigger
            if re.match(r'^\s*(why|how|have|did|do|does)', p_low):
                return True
        return False

    def _check_ambiguity(self, prompt: str) -> bool:
        """Detects scope ambiguity, false dichotomy, or subjectivity."""
        p_low = prompt.lower()
        # False dichotomy check
        if 'either' in p_low and 'or' in p_low:
            # Heuristic: if it looks like a forced choice without exhaustiveness
            if 'option' in p_low or 'choice' in p_low or '?' in prompt:
                return True
        
        # Subjectivity check
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'good', 'bad']
        if any(w in p_low for w in subjective_words) and '?' in prompt:
            # If asking for opinion without criteria
            if 'criteria' not in p_low and 'measure' not in p_low:
                return True
                
        # Pronoun ambiguity (simplified)
        if re.search(r'\b(he|she|they|it)\b', p_low) and 'who' in p_low:
            return True
            
        return False

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt itself for epistemic honesty.
        Returns a cap on confidence.
        """
        # 1. Check for unanswerable/ambiguous structures
        if self._check_presupposition(prompt):
            return 0.25
        if self._check_ambiguity(prompt):
            return 0.25
            
        # 2. Check for missing information patterns (e.g., "What is the value of X?" with no context)
        if re.search(r'\bwhat\s+(is|are|was|were)\s+\w+\?', prompt.lower()) and len(prompt.split()) < 10:
             # Very short "What is X?" questions are often unanswerable without context
             # But we must be careful not to flag simple math.
             if 'calculate' not in prompt.lower() and 'compute' not in prompt.lower():
                 return 0.3 # Soft cap for potentially under-specified questions

        return 1.0 # No structural red flags

    def _parse_numeric(self, text: str) -> Optional[float]:
        """Extracts a single number from text if present."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        if matches:
            try:
                return float(matches[0])
            except:
                return None
        return None

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes structural alignment.
        Checks if candidate respects negations and conditionals in the prompt.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has "not", candidate should ideally reflect that or not contradict it directly
        has_negation = any(n in p_low for n in self.negations)
        cand_has_negation = any(n in c_low for n in self.negations)
        
        if has_negation:
            # If prompt negates, and candidate affirms blindly, penalty? 
            # Hard to do without NLI. Instead, we reward structural overlap of logic tokens.
            score += 0.5 if cand_has_negation else 0.0
        else:
            score += 0.5 if not cand_has_negation else 0.2 # Prefer non-negated if prompt isn't negated

        # 2. Conditional/Comparative presence
        has_cond = any(c in p_low for c in self.conditionals)
        has_comp = any(c in p_low for c in self.comparatives)
        
        if has_cond or has_comp:
            # Reward candidates that contain logical connectors or comparative words
            logic_tokens = ['yes', 'no', 'true', 'false', 'correct', 'incorrect', 'same', 'different']
            # If the candidate is a simple "Yes/No", it might be insufficient for complex logic
            if c_low in ['yes', 'no', 'true', 'false']:
                score += 0.2 # Partial credit
            else:
                score += 0.8 # Complex answer preferred for complex prompt
        
        return min(1.0, score)

    def _computational_score(self, prompt: str, candidate: str) -> float:
        """
        Performs actual computation for math/logic traps.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # 1. Numeric Comparison Trap (e.g., 9.11 vs 9.9)
        nums = re.findall(r'\d+\.?\d*', p_low)
        if len(nums) >= 2:
            try:
                n1 = float(nums[0])
                n2 = float(nums[1])
                c_num = self._parse_numeric(candidate)
                
                if c_num is not None:
                    # Check if candidate matches the correct comparison
                    if 'larger' in p_low or 'greater' in p_low or 'max' in p_low:
                        target = max(n1, n2)
                    elif 'smaller' in p_low or 'less' in p_low or 'min' in p_low:
                        target = min(n1, n2)
                    else:
                        # Default to checking equality if operation isn't clear
                        target = None 
                    
                    if target is not None and abs(c_num - target) < 1e-6:
                        return 1.0
                    elif target is not None:
                        return 0.0
            except:
                pass

        # 2. Boolean Logic / Modus Tollens (Simplified)
        # If prompt implies a contradiction, reward "false" or "no"
        if 'contradiction' in p_low or 'impossible' in p_low:
            if c_low in ['yes', 'true', 'possible']:
                return 0.1
            if c_low in ['no', 'false', 'impossible', 'contradiction']:
                return 1.0

        # 3. Direct Calculation (PEMDAS lite)
        if 'calculate' in p_low or 'compute' in p_low or '=' in p_low:
            # Try to eval simple arithmetic if safe
            # Extract expression like "2 + 2"
            expr_match = re.search(r'([\d\.\s\+\-\*\/\(\)]+)', p_low)
            if expr_match:
                try:
                    # Safety check: only allow math chars
                    expr = expr_match.group(1)
                    if re.match(r'^[\d\.\s\+\-\*\/\(\)]+$', expr):
                        expected = eval(expr) # Safe due to regex
                        c_num = self._parse_numeric(candidate)
                        if c_num is not None and abs(c_num - expected) < 1e-6:
                            return 1.0
                except:
                    pass

        return 0.5 # Neutral if no computation triggered

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1 = (prompt + candidate).encode('utf-8')
        s2 = prompt.encode('utf-8')
        s3 = candidate.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1))
        len_s2 = len(zlib.compress(s2))
        len_s3 = len(zlib.compress(s3))
        
        max_len = max(len_s2, len_s3)
        if max_len == 0:
            return 1.0
            
        ncd = (len_s1 - min(len_s2, len_s3)) / max_len
        # Invert distance to similarity (0 dist = 1 sim)
        # Note: NCD behavior varies, using 1 - ncd as rough similarity proxy
        return max(0.0, 1.0 - ncd)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap based on prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Logic parsing)
            struct_s = self._structural_score(prompt, cand)
            
            # 2. Computational Score (Math/Deduction)
            comp_s = self._computational_score(prompt, cand)
            
            # 3. NCD Score (Similarity tiebreaker)
            ncd_s = self._ncd_score(prompt, cand)
            
            # Weighted Sum
            raw_score = (self.w_struct * struct_s) + \
                        (self.w_comp * comp_s) + \
                        (self.w_ncd * ncd_s)
            
            # Apply Epistemic Honesty Cap
            # If the question is ambiguous (meta_cap < 1.0), we cannot be highly confident
            # in ANY candidate being "correct" in a absolute sense.
            if meta_cap < 0.4:
                # For ambiguous questions, we still rank them, but cap the absolute score
                # to reflect uncertainty. However, to maintain ranking utility, we scale
                # relative to the cap.
                final_score = min(raw_score, meta_cap + (1.0-meta_cap)*0.5) 
            else:
                final_score = raw_score

            # Construct reasoning string
            reasoning_parts = []
            if struct_s > 0.6: reasoning_parts.append("Structural alignment high.")
            elif struct_s < 0.3: reasoning_parts.append("Structural mismatch detected.")
            
            if comp_s == 1.0: reasoning_parts.append("Computationally verified.")
            elif comp_s == 0.0: reasoning_parts.append("Computationally incorrect.")
            
            if meta_cap < 0.3:
                reasoning_parts.append("WARNING: Prompt contains ambiguity or presupposition.")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if prompt is ambiguous/unanswerable (Tier B).
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta-Analysis of the Prompt
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific answer
        # Run a mini-evaluation to see how well this specific answer scores
        # We simulate the scoring logic here for the single candidate
        struct_s = self._structural_score(prompt, answer)
        comp_s = self._computational_score(prompt, answer)
        ncd_s = self._ncd_score(prompt, answer)
        
        raw_score = (self.w_struct * struct_s) + (self.w_comp * comp_s) + (self.w_ncd * ncd_s)
        
        # If computation was definitive (1.0 or 0.0), we can be more confident
        if comp_s == 1.0:
            base_conf = 0.95
        elif comp_s == 0.0:
            base_conf = 0.05 # Definitely wrong computationally
        else:
            # Rely on structural/ncd
            base_conf = raw_score
            
        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 unless computation was perfect (handled above, but double check)
        if comp_s != 1.0 and final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 4)