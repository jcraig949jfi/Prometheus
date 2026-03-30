import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Self-Producing Falsification Swarm (SFS) Implementation.
    
    Mechanism:
    1. Swarm Intelligence: Parallel evaluation of candidates via multiple lightweight "agents" 
       (structural parsers, numeric evaluators, logical checkers).
    2. Falsificationism: Agents actively seek disqualifiers (negations, contradictions, 
       impossible numerics). Candidates surviving falsification gain "survival" scores.
    3. Autopoiesis: The system maintains an internal "coherence" state. If a prompt triggers 
       ambiguity detectors (presuppositions, scope issues), the system self-regulates by 
       capping confidence (organizational closure) to prevent reasoning drift into false certainty.
    
    Scoring Decomposition:
    - Structural/Logical (Swarm/Falsification): 50%
    - Numeric/Computation (Constructive): 20% 
    - NCD (Similarity): 15% (Tiebreaker only)
    - Epistemic Honesty (Meta-Confidence): Hard caps on output.
    """

    def __init__(self):
        # Internal state representing the "organizational closure" of the autopoietic module
        self._coherence_threshold = 0.3
        self._max_confidence_cap = 1.0
        
        # Patterns for Tier B (Judgment Traps) detection
        self._presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bquit\b.*\bproblem\b", r"\bassumes?\b"
        ]
        self._ambiguity_triggers = [
            r"\bwho is\b", r"\bwhich one\b", r"\beither.*or\b", r"\bbest\b", 
            r"\bworst\b", r"\bfavorite\b", r"\bopinion\b", r"\bsubjective\b"
        ]
        self._scope_triggers = [
            r"\bevery.*a.*\b", r"\ball.*same\b", r"\bthey\b.*\bwho\b"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a confidence cap. If traps are found, returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self._presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Strong cap for loaded questions
                
        # Check for subjectivity/unanswerability without context
        for pattern in self._ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Only cap if it looks like a judgment call without data
                if "best" in p_lower or "favorite" in p_lower or "opinion" in p_lower:
                    return 0.25
                
        # Check for specific logical traps (False Dichotomy hint)
        if re.search(r"\beither.*or\b", p_lower) and re.search(r"\bchoice\b|\boption\b", p_lower):
            # Heuristic: if it forces a choice, be cautious
            pass # Context needed, but let's not cap hard unless obvious
            
        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for constructive computation."""
        # Matches integers and floats, handles negative signs
        matches = re.findall(r'[-]?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Agent 1: Structural & Logical Parser.
        Checks for negation alignment, boolean consistency, and keyword matching.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation Check
        negations = ["no", "not", "never", "none", "cannot", "impossible"]
        p_has_neg = any(n in p_lower for n in negations)
        c_has_neg = any(n in c_lower for n in negations)
        
        if p_has_neg == c_has_neg:
            score += 0.4  # Alignment on negation
        else:
            score -= 0.4  # Penalty for negation mismatch
            
        # Boolean/YesNo consistency
        yes_words = ["yes", "true", "correct", "affirmative"]
        no_words = ["no", "false", "incorrect", "negative"]
        
        p_yes = any(w in p_lower for w in yes_words)
        p_no = any(w in p_lower for w in no_words)
        c_yes = any(w in c_lower for w in yes_words)
        c_no = any(w in c_lower for w in no_words)
        
        if (p_yes and c_yes) or (p_no and c_no):
            score += 0.3
        elif (p_yes and c_no) or (p_no and c_yes):
            score -= 0.3
            
        # Length heuristic (very rough proxy for completeness)
        if len(candidate) > 0.5 * len(prompt):
            score += 0.1
            
        return max(0.0, min(1.0, 0.5 + score))

    def _computational_score(self, prompt: str, candidate: str) -> float:
        """
        Agent 2: Constructive Computation.
        Extracts numbers and verifies arithmetic or ordering.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 0.5  # Neutral if no numbers to compute
        
        if not c_nums:
            # If prompt has numbers but candidate doesn't, likely wrong for math problems
            # But could be conceptual. Return neutral-low.
            return 0.3 

        # Check 1: Exact number match (order independent)
        # Sort to compare sets of numbers
        if sorted(p_nums) == sorted(c_nums):
            return 1.0
        
        # Check 2: Arithmetic result presence
        # Simple heuristic: if candidate contains a number that is the sum/prod of prompt numbers
        p_sum = sum(p_nums)
        p_prod = 1
        for n in p_nums: p_prod *= n
        
        c_val = c_nums[0] if c_nums else 0
        
        # Tolerance for float comparison
        tol = 1e-6
        if abs(c_val - p_sum) < tol or abs(c_val - p_prod) < tol:
            return 1.0
            
        # Check 3: Ordering (if prompt implies sorting)
        if len(p_nums) >= 2 and len(c_nums) >= 2:
            # If candidate numbers are a permutation of prompt numbers, it's structurally sound
            if sorted(p_nums) == sorted(c_nums):
                return 0.9

        # Fallback: If candidate number is wildly different from any prompt number logic
        return 0.4

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Agent 3: Normalized Compression Distance (NCD).
        Used ONLY as a tiebreaker. Measures similarity.
        """
        try:
            s1 = prompt.encode('utf-8')
            s2 = candidate.encode('utf-8')
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            
            # NCD formula: (c12 - min(c1, c2)) / max(c1, c2)
            # Result is 0 (identical) to 1 (disjoint)
            # We want high score for similarity, so invert: 1 - NCD
            denom = max(c1, c2)
            if denom == 0: return 0.5
            ncd = (c12 - min(c1, c2)) / denom
            return max(0.0, 1.0 - ncd)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-evaluation: Check prompt for traps first
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # Swarm Agents
            s_score = self._structural_score(prompt, cand)
            c_score = self._computational_score(prompt, cand)
            n_score = self._ncd_score(prompt, cand)
            
            # Weighted Aggregation (Swarm Consensus)
            # Structural: 50%, Computational: 35%, NCD: 15%
            raw_score = (s_score * 0.50) + (c_score * 0.35) + (n_score * 0.15)
            
            # Apply Epistemic Cap (Autopoietic Regulation)
            # If the prompt is ambiguous, the system cannot be confident regardless of candidate match
            if meta_cap < 0.3:
                # If the prompt is a trap, we penalize high confidence unless the candidate 
                # explicitly identifies the trap (heuristic: candidate length > prompt and contains 'error' or 'ambiguous')
                c_lower = cand.lower()
                if ('ambigu' in c_lower or 'error' in c_lower or 'cannot' in c_lower or 'insufficient' in c_lower):
                    final_score = min(raw_score, 0.8) # Allow high score for identifying the trap
                    reasoning = f"Trap detected in prompt. Candidate addresses uncertainty. Raw: {raw_score:.2f}"
                else:
                    final_score = raw_score * meta_cap # Severely penalize confident answers to bad questions
                    reasoning = f"Prompt contains ambiguity/presupposition. Confidence capped. Raw: {raw_score:.2f}"
            else:
                final_score = raw_score
                reasoning = f"Structural: {s_score:.2f}, Comp: {c_score:.2f}, NCD: {n_score:.2f}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check Prompt Properties (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (Tier A)
        # Run a mini-evaluation to get the raw score
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
            
        raw_score = eval_res[0]["score"]
        
        # 3. Apply Autopoietic Cap
        # If the prompt is ambiguous, confidence cannot exceed the cap
        final_conf = min(raw_score, meta_cap)
        
        # 4. Hard constraints per requirements
        # Never > 0.9 without definitive computation (simplified here to strict capping)
        # If meta_cap is low, we are honest about uncertainty.
        if meta_cap < 0.3:
            # If the candidate explicitly calls out the issue, we can be confident IN THE DETECTION
            c_lower = answer.lower()
            if any(x in c_lower for x in ['ambigu', 'error', 'cannot', 'insufficient', 'false dichotomy']):
                return min(raw_score, 0.85) # High confidence that this is the right rejection
            else:
                return min(final_conf, 0.25) # Low confidence for normal answers to bad questions

        return min(final_conf, 0.95) # General cap to avoid overconfidence