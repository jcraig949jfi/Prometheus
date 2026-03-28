import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Lyapunov-Chunk Scorer (ALCS) with Epistemic Honesty.
    
    Mechanism:
    1. Epistemic Filter (Tier B): Detects presuppositions, ambiguity, and unanswerable queries.
       If detected, confidence is capped low (<0.3) regardless of candidate match.
    2. Structural Parsing: Extracts atomic propositions, negations, and implications (if->then).
    3. Constraint Propagation: Iteratively updates truth states based on logical rules.
    4. Chaos Analysis: Computes a surrogate Lyapunov exponent to measure logical stability.
    5. Cognitive Load: Penalizes solutions requiring >4 active concepts in a single chunk.
    6. Scoring: Combines consistency, stability, load, and NCD (tiebreaker).
    """
    
    def __init__(self):
        self.M = 4  # Working memory limit
        self.alpha = 0.01
        self.beta = 0.2
        self.max_load = 10
        # Regex patterns
        self.pat_if = re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)\.', re.IGNORECASE)
        self.pat_is = re.compile(r'(.+?)\s+is\s+(.+?)\.', re.IGNORECASE)
        self.pat_neg = re.compile(r'(not|no|never|none)', re.IGNORECASE)
        self.pat_num = re.compile(r'-?\d+\.?\d*')
        self.pat_comp = re.compile(r'(greater|less|more|fewer|before|after)', re.IGNORECASE)
        self.pat_presup = re.compile(r'(have you stopped|why did .+ fail|when did .+ stop)', re.IGNORECASE)
        self.pat_ambig = re.compile(r'(every .+ a .+|who was .+|either .+ or .+)', re.IGNORECASE)

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps: presupposition, ambiguity, subjectivity."""
        p_lower = prompt.lower()
        if self.pat_presup.search(p_lower): return 0.1
        if "best" in p_lower or "worst" in p_lower or "favorite" in p_lower:
            if "calculate" not in p_lower and "compute" not in p_lower: return 0.2
        if self.pat_ambig.search(p_lower): return 0.25
        if "who" in p_lower.split("?")[0] and ("he" in p_lower or "she" in p_lower): return 0.2
        return 1.0

    def _parse_text(self, text: str) -> Tuple[List[str], np.ndarray, List[List[int]]]:
        """Extracts propositions and builds implication matrix."""
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        props = []
        implications = [] # (from_idx, to_idx)
        
        # Simple extraction
        for sent in sentences:
            tokens = sent.lower().split()
            if not tokens: continue
            
            # Check for numbers
            nums = self.pat_num.findall(sent)
            if len(nums) >= 2:
                # Numeric comparison heuristic
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    props.append(f"num_check:{v1}<{v2}")
                    props.append(f"num_check:{v1}>{v2}")
                except: pass

            # Check conditionals
            match_if = self.pat_if.search(sent)
            if match_if:
                antecedent = match_if.group(1).strip()
                consequent = match_if.group(2).strip()
                # Normalize
                if antecedent not in props: props.append(antecedent)
                if consequent not in props: props.append(consequent)
                implications.append((props.index(antecedent), props.index(consequent)))
            else:
                # Atomic fact
                if sent not in props: props.append(sent)
        
        n = len(props)
        if n == 0: return [], np.array([]), []
        
        W = np.zeros((n, n))
        for i, j in implications:
            if i < n and j < n: W[i, j] = 1.0
            
        return props, W, implications

    def _propagate(self, W: np.ndarray, initial_state: np.ndarray) -> np.ndarray:
        """Iterative constraint propagation (Modus Ponens)."""
        s = initial_state.copy()
        for _ in range(10):
            new_s = np.dot(W, s)
            # Threshold logic: if antecedent true, consequent becomes true
            # Also maintain existing truths
            next_s = np.where(new_s >= 0.5, 1.0, s) 
            # Keep initial assertions
            next_s = np.maximum(next_s, s) 
            if np.array_equal(next_s, s): break
            s = next_s
        return s

    def _compute_lyapunov(self, W: np.ndarray, s: np.ndarray) -> float:
        """Estimates logical stability via surrogate Jacobian norm."""
        if W.size == 0: return 0.0
        # Surrogate derivative (epsilon)
        diag_s = np.diag(np.where(np.abs(np.dot(W, s) - 0.5) < 0.1, 0.1, 0.01))
        J = np.dot(W, diag_s)
        try:
            norm_val = np.linalg.norm(J, 2)
            return np.log(norm_val + 1e-6)
        except:
            return 0.0

    def _calc_load_penalty(self, s: np.ndarray) -> float:
        """Penalizes high cognitive load."""
        active = np.sum(s > 0.5)
        return max(0, active - self.M)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Parse prompt structure
        props, W, _ = self._parse_text(prompt)
        n = len(props)
        base_state = np.zeros(n) if n > 0 else np.array([])
        
        # Initial truth from explicit "is" or positive assertions in prompt
        # For this simplified version, we assume prompt assertions are true initially
        if n > 0:
            # Heuristic: First few props are likely premises
            base_state[:min(3, n)] = 1.0 

        for cand in candidates:
            score = 0.0
            reason_parts = []
            
            # 1. Epistemic Check
            if meta_cap < 0.3:
                score = 0.1 * meta_cap
                reason_parts.append("Low confidence due to ambiguity/presupposition.")
            else:
                # 2. Candidate Integration & Evaluation
                # Combine prompt + candidate to test consistency
                full_text = f"{prompt} {cand}."
                c_props, c_W, _ = self._parse_text(full_text)
                
                # Numeric Check (Constructive)
                nums_cand = self.pat_num.findall(cand)
                nums_prompt = self.pat_num.findall(prompt)
                numeric_match = False
                if nums_cand and nums_prompt:
                    try:
                        # Simple equality check for numeric answers
                        if float(nums_cand[0]) == float(nums_prompt[0]): numeric_match = True
                        # Or if candidate solves a simple arithmetic implied
                    except: pass

                if c_W.size > 0 and len(c_props) > 0:
                    # Re-initialize state based on combined text
                    s_init = np.ones(len(c_props)) * 0.5 # Uncertain start
                    # Assume prompt premises are true
                    for i, p in enumerate(c_props):
                        if p in prompt: s_init[i] = 1.0
                    
                    s_final = self._propagate(c_W, s_init)
                    
                    # Lyapunov Stability
                    lyap = self._compute_lyapunov(c_W, s_final)
                    lyap_norm = lyap / (1 + abs(lyap))
                    
                    # Load Penalty
                    load_pen = self._calc_load_penalty(s_final)
                    
                    # Adaptive Gain (Simplified)
                    consistency = np.mean(s_final)
                    g = 1.0 + self.alpha * (1.0 - lyap_norm) * (1.0 - load_pen/self.max_load)
                    g = np.clip(g, 0, 1)
                    
                    raw_score = g * (1.0 - lyap_norm) - self.beta * (load_pen / self.max_load)
                    
                    # NCD Tiebreaker (Max 15% weight)
                    ncd = self._ncd_score(prompt, cand)
                    ncd_contrib = (1.0 - ncd) * 0.15
                    
                    score = (raw_score * 0.85) + ncd_contrib
                    if numeric_match: score += 0.2 # Boost for correct numeric extraction
                    
                    reason_parts.append(f"Stability: {1-lyap_norm:.2f}, Load: {load_pen}")
                else:
                    # Fallback for non-structural matches
                    score = 0.5 if numeric_match else 0.3
                    reason_parts.append("Heuristic match only.")

            results.append({
                "candidate": cand,
                "score": float(np.clip(score, 0, 1)),
                "reasoning": "; ".join(reason_parts)
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt)
        if meta < 0.3:
            return meta
        
        # Attempt to verify via evaluation logic
        # We treat the answer as a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.1
            
        base_score = res[0]['score']
        
        # Cap confidence if no structural parsing occurred
        props, _, _ = self._parse_text(prompt)
        if len(props) == 0:
            # If no structure found, rely on meta and simple overlap
            return min(0.4, meta) 
            
        # Scale by meta-confidence
        final_conf = base_score * meta
        return float(np.clip(final_conf, 0, 0.95)) # Never 1.0 unless proven mathematically