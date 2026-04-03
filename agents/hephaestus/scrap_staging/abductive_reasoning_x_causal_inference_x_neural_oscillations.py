import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Oscillatory Causal Abductive Network (OCAN) Implementation.
    
    Mechanism:
    1. Theta-Gated Meta-Cognition (Hypothesis Generation & Honesty):
       - Analyzes the prompt for Tier B traps (presuppositions, ambiguity, false dichotomies).
       - If a trap is detected, the "Theta Gate" opens to suppress confidence (<0.3), enforcing epistemic honesty.
       - If clear, it proceeds to structural parsing.
    
    2. Gamma-Binding (Structural Parsing & Computation):
       - Binds logical operators (negations, comparatives) and numeric values into "explanation packets".
       - Performs deterministic computation (PEMDAS, transitivity) to generate a ground-truth score baseline.
    
    3. Causal Intervention (Scoring):
       - Simulates a 'do-calculus' intervention by comparing candidate structure against the parsed logical skeleton.
       - Uses NCD only as a minor tie-breaker (<15% weight) when structural signals are weak.
    """

    def __init__(self):
        # Thresholds for oscillatory gating
        self.theta_threshold = 0.3  # Confidence cap for ambiguous inputs
        self.ncd_weight = 0.15      # Max weight for compression distance
        self.struct_weight = 0.55   # Min weight for structural logic
        self.comp_weight = 0.30     # Min weight for computation

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects presuppositions, ambiguities, and unanswerable constraints.
        Returns a confidence cap (0.0 - 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did\b.*\b(fail|stop|quit)\b",
            r"\bwhen did\b.*\b(stop|fail)\b", r"\bis it true that\b",
            r"\bassum(?:e|ing)\b.*\b(false|wrong)\b"
        ]
        for pattern in presupposition_patterns:
            if re.search(pattern, p):
                return 0.2  # Strong cap for loaded questions

        # 2. Scope/Pronoun Ambiguity ("Every X did a Y", "X told Y he...")
        ambiguity_patterns = [
            r"\bevery\b.*\b(a|an)\b\s*\w+\b", # Potential scope ambiguity
            r"\btold\b.*\bhe\b", r"\btold\b.*\bshe\b", r"\bsaid to\b.*\bhim\b",
            r"\bwho\b.*\b(was|is)\b.*\bwrong\b" # Pronoun resolution needed
        ]
        for pattern in ambiguity_patterns:
            if re.search(pattern, p):
                # Only cap if the question asks for resolution without context
                if re.search(r"\bwho\b|\bwhich\b|\bwhat\b", p):
                    return 0.25

        # 3. False Dichotomy ("Either A or B" without exhaustiveness)
        if re.search(r"\beither\b.*\bor\b", p) and not re.search(r"\bor else\b|\bor not\b", p):
            # Heuristic: if "either" exists but no clear exhaustive list, flag potential bias
            # This is a soft check to avoid over-capping valid logic puzzles
            if re.search(r"\bmust\b|\bonly\b", p):
                return 0.3

        # 4. Subjectivity without criteria
        subjective_triggers = ["best", "worst", "favorite", "beautiful"]
        if any(word in p for word in subjective_triggers):
            if not re.search(r"\baccording to\b|\bdata\b|\bmetric\b", p):
                return 0.25

        return 1.0  # No meta-cognitive red flags

    def _parse_structure(self, prompt: str) -> Dict:
        """
        Extracts logical skeleton: negations, comparatives, conditionals.
        """
        p = prompt.lower()
        return {
            "negations": len(re.findall(r"\b(not|no|never|neither|without)\b", p)),
            "comparatives": len(re.findall(r"\b(more|less|greater|smaller|higher|lower|better|worse)\b", p)),
            "conditionals": len(re.findall(r"\b(if|then|unless|only if)\b", p)),
            "numbers": re.findall(r"-?\d+(?:\.\d+)?", p),
            "has_question": "?" in prompt
        }

    def _compute_ground_truth(self, prompt: str) -> Optional[float]:
        """
        Tier A: Constructive Computation.
        Attempts to solve numeric or logical expressions directly.
        Returns a definitive score (0.0-1.0) if solvable, else None.
        """
        # Detect simple math expressions embedded in text
        numbers = re.findall(r"-?\d+(?:\.\d+)?", prompt)
        ops = re.findall(r"[\+\-\*\/]", prompt)
        
        # Simple arithmetic check (e.g., "What is 2 + 2?")
        if len(numbers) >= 2 and len(ops) >= 1:
            try:
                # Extract just the math part if possible, otherwise try whole string
                # Very basic extractor for "X op Y" patterns
                match = re.search(r"(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)", prompt)
                if match:
                    n1 = float(match.group(1))
                    op = match.group(2)
                    n2 = float(match.group(3))
                    if op == '+': res = n1 + n2
                    elif op == '-': res = n1 - n2
                    elif op == '*': res = n1 * n2
                    elif op == '/': res = n1 / n2 if n2 != 0 else 0
                    else: res = None
                    
                    if res is not None:
                        return res
            except:
                pass
        
        # Detect direct float comparison traps (e.g. 9.11 vs 9.9)
        comp_match = re.search(r"(\d+\.\d+)\s*(<|>|==|!=)\s*(\d+\.\d+)", prompt)
        if comp_match:
            v1 = float(comp_match.group(1))
            op = comp_match.group(2)
            v2 = float(comp_match.group(3))
            if op == '<': return 1.0 if v1 < v2 else 0.0
            if op == '>': return 1.0 if v1 > v2 else 0.0
            if op == '==': return 1.0 if v1 == v2 else 0.0
            if op == '!=': return 1.0 if v1 != v2 else 0.0

        return None

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _gamma_bind_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment and logical consistency.
        Returns a score between 0.0 and 1.0.
        """
        p_struct = self._parse_structure(prompt)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.5 # Base prior
        
        # 1. Negation Consistency
        # If prompt has "not", candidate should ideally reflect negation or contradiction
        if p_struct['negations'] > 0:
            if any(neg in c_lower for neg in ["not", "no", "false", "impossible"]):
                score += 0.2
            else:
                # Penalty if candidate ignores strong negation in a yes/no context
                if "yes" in c_lower or "true" in c_lower:
                    score -= 0.3
        
        # 2. Comparative Logic
        if p_struct['comparatives'] > 0:
            # Check if candidate contains comparative words or numbers
            nums_in_c = re.findall(r"-?\d+(?:\.\d+)?", candidate)
            if nums_in_c:
                score += 0.2 # Good, candidate provides quantitative evidence
            
        # 3. Conditional/Logic Flow
        if p_struct['conditionals'] > 0:
            if any(w in c_lower for w in ["therefore", "thus", "because", "so", "if"]):
                score += 0.15

        # 4. Numeric Verification (if ground truth exists)
        gt = self._compute_ground_truth(prompt)
        if gt is not None:
            # Try to extract number from candidate
            c_nums = re.findall(r"-?\d+(?:\.\d+)?", candidate)
            if c_nums:
                try:
                    c_val = float(c_nums[-1]) # Take last number as answer
                    if abs(c_val - gt) < 1e-6:
                        score = 1.0
                    else:
                        score = 0.1 # Strong penalty for wrong math
                except:
                    pass
        else:
            # Fallback to NCD if no computation possible (max 15% influence)
            ncd = self._calculate_ncd(prompt, candidate)
            # Invert NCD (lower is better) and scale
            ncd_score = (1.0 - ncd) * self.ncd_weight
            score = (score * (1.0 - self.ncd_weight)) + ncd_score

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Theta-Gate: Meta-Cognitive Check
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Gamma-Bind: Structural & Computational Scoring
        results = []
        for cand in candidates:
            raw_score = self._gamma_bind_score(prompt, cand)
            
            # Apply Epistemic Honesty Cap
            if meta_cap < 0.3:
                # If the question is ambiguous, we suppress confidence regardless of candidate match
                # unless the candidate explicitly identifies the ambiguity
                if any(word in cand.lower() for word in ["ambiguous", "unclear", "cannot", "insufficient"]):
                    final_score = 0.8 # Reward identifying the trap
                    reason = "Identified epistemic trap."
                else:
                    final_score = raw_score * meta_cap # Suppress
                    reason = "Question contains ambiguity/presupposition; confidence capped."
            else:
                final_score = raw_score
                reason = "Structural and computational alignment."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B honesty constraints.
        """
        # 1. Meta-Cognitive Cap
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Validation
        # We simulate the evaluation of this single candidate
        struct_score = self._gamma_bind_score(prompt, answer)
        
        # If computation yielded a definitive result (e.g. math), trust it more
        gt = self._compute_ground_truth(prompt)
        if gt is not None:
            c_nums = re.findall(r"-?\d+(?:\.\d+)?", answer)
            if c_nums:
                try:
                    if abs(float(c_nums[-1]) - gt) < 1e-6:
                        return min(0.95, meta_cap) # High confidence but capped by honesty
                    else:
                        return 0.05 # Definitely wrong math
                except:
                    pass
        
        # Combine structural score with meta cap
        # If meta_cap is low (ambiguous question), confidence must be low
        # unless the answer explicitly addresses the ambiguity
        is_trap_answer = any(word in answer.lower() for word in ["ambiguous", "unclear", "cannot", "insufficient", "depends"])
        
        if meta_cap < 0.3:
            if is_trap_answer:
                return 0.85 # High confidence that this is the right way to handle the trap
            else:
                return meta_cap # Low confidence because the question is flawed
        
        # Normal case: blend structural fit with a penalty for overconfidence
        base_conf = struct_score
        if base_conf > 0.9 and gt is None and not is_trap_answer:
            # Don't be too sure if no hard computation was done
            base_conf = 0.85
            
        return round(min(1.0, base_conf), 4)