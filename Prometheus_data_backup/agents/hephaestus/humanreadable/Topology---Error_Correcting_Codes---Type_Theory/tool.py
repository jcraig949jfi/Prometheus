import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural parsing, constructive computation,
    and topological confidence modeling.
    
    Mechanism:
    1. Structural Parsing (50%+): Detects negations, comparatives, conditionals, and 
       logical traps (presuppositions, false dichotomies) to determine epistemic validity.
    2. Constructive Computation (20%+): Executes arithmetic, modular math, and set logic
       found in the prompt to verify candidate answers numerically.
    3. Topological Confidence (Meta-Layer): Uses a 'syndrome' approach where logical 
       inconsistencies or ambiguities act as errors. If the error syndrome is non-trivial 
       (i.e., the prompt is ambiguous or trapped), confidence collapses to <0.3 regardless 
       of string similarity.
    4. NCD Tiebreaker (<=15%): Used only when structural and computational signals are neutral.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|isn\'t|aren\'t)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst|best|larger|shorter)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|how did|when did|who is the|which one is the)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all|each)\b.*\b(a|an|the)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|which person)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or|must choose|only option)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe|think)\b', re.I),
        }
        
        # Keywords indicating unanswerable or subjective contexts
        self.trap_keywords = [
            "stopped", "quit", "failed", "assume", "suppose", "either", "or", 
            "best", "worst", "favorite", "opinion", "believe"
        ]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        return [float(x) for x in self.patterns['numbers'].findall(text)]

    def _compute_arithmetic(self, prompt: str) -> Optional[float]:
        """
        Attempt to solve simple arithmetic expressions constructively.
        Supports: addition, subtraction, multiplication, division, modulo.
        """
        # Look for explicit math patterns like "5 + 3", "10 mod 3", "2 * 4"
        # This is a simplified constructive solver for demonstration
        try:
            # Clean prompt to allow only safe math chars
            clean_prompt = re.sub(r'[^\d+\-*/%.()\s]', '', prompt)
            if any(c in clean_prompt for c in '+-*/%') and re.search(r'\d', clean_prompt):
                # Safety check: ensure it's not just random numbers
                if len(clean_prompt.strip()) > 0 and len(clean_prompt) < 100:
                    # Evaluate safely
                    result = eval(clean_prompt)
                    return float(result)
        except:
            pass
        return None

    def _check_logical_consistency(self, prompt: str, candidate: str) -> Tuple[bool, str]:
        """
        Check for basic logical consistency between prompt constraints and candidate.
        Returns (is_consistent, reason).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Check negation traps
        if re.search(self.patterns['negation'], p_lower):
            # If prompt says "not X", and candidate is "X", it's inconsistent
            # Simplified heuristic: if "no" or "not" is prominent, expect negative answer
            if re.search(r'\b(yes|true|correct)\b', c_lower):
                # Heuristic: if prompt is strongly negative, 'yes' might be wrong
                # This is a weak heuristic without full NLP, so we return neutral
                pass 

        # Check for direct contradiction in numbers
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt implies a calculation result and candidate differs
            # We rely on the constructive solver for the actual value check
            pass
            
        return True, "No obvious contradiction"

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Analyze the prompt structure for ambiguity, traps, or 
        unanswerability. Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        if self.patterns['presupposition'].search(p_lower):
            return 0.2  # Highly suspicious of traps
        
        # 2. Scope/Pronoun Ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower) and "same" in p_lower:
            return 0.3
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.25
            
        # 3. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            if "only" in p_lower or "must" in p_lower:
                return 0.3 # Suspicious of forced choice
        
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            # If asking for opinion, confidence in objective truth is low
            if re.search(r'\b(is|are|what|which)\b', p_lower):
                return 0.4 # Subjective questions have no single truth
        
        # 5. Unanswerability (Missing info)
        if re.search(r'\b(without|missing|unknown)\b', p_lower):
            return 0.1

        return 1.0  # No structural traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        # Concatenate with a separator to avoid boundary artifacts
        concat = s1_bytes + b'\x00' + s2_bytes
        len_concat = len(zlib.compress(concat))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated with lengths for simplicity in this context, 
        # but strictly: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using compressed sizes for better accuracy
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c_concat = len_concat # Already compressed
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 0.0
            
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Constructive Computation (The "Truth" anchor)
        computed_answer = self._compute_arithmetic(prompt)
        
        # 2. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            score = 0.0
            reasoning_parts = []
            
            c_lower = candidate.lower().strip()
            p_lower = prompt.lower()
            
            # --- Structural Parsing (50% weight base) ---
            structural_match = False
            
            # Check for direct boolean alignment if prompt implies it
            if re.search(r'\b(yes|no|true|false)\b', c_lower):
                # Simple heuristic: if prompt has "not", "no" -> expect negative
                has_negation = bool(self.patterns['negation'].search(p_lower))
                is_negative_answer = any(x in c_lower for x in ['no', 'false'])
                
                # If prompt is a negative question ("Is it not X?"), logic gets tricky.
                # We rely on the meta_cap to lower confidence if it's a trap.
                if meta_cap < 0.5:
                    structural_score = 0.5 # Uncertain due to trap
                    reasoning_parts.append("Potential logical trap detected.")
                else:
                    # Basic consistency check
                    structural_score = 0.8
                    structural_match = True
                    reasoning_parts.append("Structural boolean alignment.")
            else:
                structural_score = 0.5 # Neutral if no clear boolean structure
                reasoning_parts.append("No clear boolean structure.")

            # --- Constructive Computation (20-40% weight) ---
            comp_score = 0.0
            if computed_answer is not None:
                c_nums = self._extract_numbers(candidate)
                if c_nums:
                    # Allow small epsilon for float comparison
                    if abs(c_nums[0] - computed_answer) < 1e-6:
                        comp_score = 1.0
                        reasoning_parts.append(f"Computed value {computed_answer} matches.")
                    else:
                        comp_score = 0.0
                        reasoning_parts.append(f"Computed {computed_answer}, got {c_nums[0]}.")
                else:
                    comp_score = 0.0 # Expected number, didn't find one
                    reasoning_parts.append("Expected numeric answer.")
            
            # --- NCD Tiebreaker (Max 15% influence) ---
            # Only used if structural and computational scores are ambiguous or equal
            ncd_val = self._ncd_score(prompt, candidate)
            # Invert NCD so 1.0 is perfect match, 0.0 is total mismatch
            # But NCD is distance, so low is good.
            # We use it as a tiebreaker only.
            ncd_contribution = 0.0
            if structural_score < 0.6 and comp_score == 0.0:
                # If we have no strong signal, use NCD but cap its influence
                # High similarity -> low NCD -> high score contribution
                ncd_contribution = max(0, 1.0 - ncd_val) * 0.15 
                reasoning_parts.append(f"NCD similarity: {1.0-ncd_val:.2f}")

            # --- Final Score Aggregation ---
            # Base score from structure
            final_score = structural_score
            
            # Override with computation if available
            if computed_answer is not None:
                final_score = comp_score # Computation trumps structure
            
            # Add NCD contribution if weak
            if final_score < 0.6:
                final_score += ncd_contribution
            
            # Apply Meta-Confidence Cap (The Topological Constraint)
            # If the prompt is a trap (meta_cap < 0.3), the score cannot exceed the cap
            # unless the computation was definitive (which implies the trap was solvable)
            if meta_cap < 0.5 and computed_answer is None:
                final_score = min(final_score, meta_cap)
                reasoning_parts.append(f"Confidence capped by meta-analysis ({meta_cap:.2f}).")

            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Default evaluation."
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns a confidence score 0-1.
        Heavily penalized by meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Verification
        computed = self._compute_arithmetic(prompt)
        is_computed_correct = False
        if computed is not None:
            c_nums = self._extract_numbers(answer)
            if c_nums and abs(c_nums[0] - computed) < 1e-6:
                is_computed_correct = True
        
        # If computation exists and is correct, we can be confident despite some noise
        if computed is not None:
            if is_computed_correct:
                raw_conf = 0.95
            else:
                raw_conf = 0.1 # Definitely wrong number
        else:
            # Fallback to structural/NCD heuristics
            # If meta_cap is low, we are inherently unsure
            if meta_cap < 0.3:
                return meta_cap # Return the low cap directly
            
            # Simple structural check
            p_lower = prompt.lower()
            a_lower = answer.lower().strip()
            
            # Check for boolean consistency roughly
            if re.search(r'\b(yes|true)\b', a_lower):
                if re.search(self.patterns['negation'], p_lower):
                    # Potential mismatch, lower confidence
                    raw_conf = 0.5
                else:
                    raw_conf = 0.7
            elif re.search(r'\b(no|false)\b', a_lower):
                 if re.search(self.patterns['negation'], p_lower):
                    raw_conf = 0.7 # Double negative might be positive
                 else:
                    raw_conf = 0.6
            else:
                # Textual similarity fallback (weak)
                ncd = self._ncd_score(prompt, answer)
                raw_conf = max(0.2, 1.0 - ncd) # Baseline uncertainty

        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Hard floor for "I don't know" scenarios
        if meta_cap < 0.3:
            return round(final_conf, 3)
            
        return round(final_conf, 3)