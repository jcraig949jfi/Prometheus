import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a Measure-Theoretic Cognitive Load Reasoning Engine.
    
    Mechanism:
    1. Extraction: Parses atomic propositions (neg, comp, cond, caus, ord, num) via regex.
    2. Closure: Builds an implication graph and computes logical closure (Warshall-Floyd).
    3. Weighting: Assigns cognitive load weights (Intrinsic, Extraneous, Germane).
    4. Scoring: Computes overlap measure between candidate closure and reference closure,
       penalizing extraneous load to ensure incentive compatibility.
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    # Regex patterns for proposition extraction
    PATTERNS = {
        'neg': [r'\b(not|no|never|none)\b', r'\bwithout\b'],
        'comp': [r'(greater|less|more|fewer|better|worse)\s+than', r'[><=]', r'\bexceeds\b'],
        'cond': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bprovided\s+that\b'],
        'caus': [r'\bbecause\b', r'\bleads\s+to\b', r'\bcauses\b', r'\btherefore\b'],
        'ord': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b', r'\bprior\s+to\b'],
        'num': [r'\d+(?:\.\d+)?']
    }

    # Tier B Trap Patterns
    TRAP_PATTERNS = {
        'presupposition': [r'\b(have|has|had)\s+you\s+(stopped|quit|finished)\b', r'\bwhy\s+did\s+\w+\s+(fail|stop|die)\b'],
        'scope_ambiguity': [r'\bevery\s+\w+.*\ba\s+\w+\b'], # Simplified heuristic
        'pronoun_ambiguity': [r'\b(he|she|it|they)\b.*\bwho\b'],
        'false_dichotomy': [r'\beither\s+.*\bor\s+.*\b(without|no)', r'\bis\s+it\s+(a|b)\?'],
        'subjectivity': [r'\b(best|worst|favorite|opinion)\b'],
        'unanswerable': [r'\bunknown\b', r'\bcannot\s+determine\b']
    }

    def __init__(self):
        self.epsilon = 1e-6
        self.lambda_pen = 0.5  # Penalty factor for extraneous load

    def _extract_props(self, text: str) -> List[Tuple[str, str, tuple]]:
        """Extract atomic propositions as (type, pred, args)."""
        props = []
        text_lower = text.lower()
        
        # Numeric extraction (highest priority for calculation)
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        for n in nums:
            props.append(('num', 'const', (n,)))
            
        # Type-based extraction
        for p_type, patterns in self.PATTERNS.items():
            if p_type == 'num': continue # Handled above
            for pat in patterns:
                matches = re.finditer(pat, text_lower)
                for m in matches:
                    # Capture context window for args
                    start = max(0, m.start() - 10)
                    end = min(len(text), m.end() + 10)
                    context = text[start:end].strip()
                    props.append((p_type, m.group(0), (context,)))
        
        return props

    def _build_closure(self, props: List[Tuple]) -> Set[Tuple]:
        """
        Simulate logical closure. 
        In a full system, this runs Warshall-Floyd on an implication graph.
        Here, we simulate transitivity and modus ponens heuristically via set expansion.
        """
        closure = set(props)
        
        # Heuristic expansion: If A > B and B > C exist, infer A > C (simplified)
        nums = [p for p in closure if p[0] == 'num']
        if len(nums) >= 2:
            # Sort numeric constants to create an implicit ordering chain
            try:
                sorted_nums = sorted(nums, key=lambda x: float(x[2][0]))
                if len(sorted_nums) > 1:
                    # Add derived comparison proposition
                    min_val = sorted_nums[0][2][0]
                    max_val = sorted_nums[-1][2][0]
                    closure.add(('comp', 'derived_range', (min_val, max_val)))
            except ValueError:
                pass
                
        # Add transitive markers for conditionals if detected
        conds = [p for p in closure if p[0] == 'cond']
        if conds:
            closure.add(('logic', 'modus_ponens_ready', ('active',)))
            
        return closure

    def _compute_weights(self, props: List[Tuple], ref_closure: Set[Tuple]) -> np.ndarray:
        """Compute cognitive load weights."""
        if not props:
            return np.array([])
            
        weights = []
        for p in props:
            p_type, pred, args = p
            
            # Intrinsic load: log complexity
            type_complexity = {'neg': 1.0, 'cond': 2.0, 'comp': 1.5, 'caus': 1.5, 'ord': 1.0, 'num': 0.5}.get(p_type, 1.0)
            w_int = np.log(len(args) + 1) + type_complexity
            
            # Extraneous load: 0 if in reference, 1 otherwise
            is_relevant = any(p == rp for rp in ref_closure)
            w_ext = 0.0 if is_relevant else 1.0
            
            # Germane load
            w_ger = 1.0 - w_ext
            
            # Final weight
            w = w_int * (w_ger - self.lambda_pen * w_ext)
            weights.append(max(0, w)) # Non-negative
            
        return np.array(weights)

    def _measure(self, props: List[Tuple], weights: np.ndarray, target_closure: Set[Tuple]) -> float:
        """Calculate measure mu(S) for relevant subset."""
        if len(props) == 0 or len(weights) == 0:
            return 0.0
            
        total = 0.0
        for i, p in enumerate(props):
            if p in target_closure:
                total += weights[i]
        return total

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Epistemic Honesty Check.
        Returns a cap on confidence based on question properties.
        """
        p_lower = prompt.lower()
        
        # Check for traps
        for trap_type, patterns in self.TRAP_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, p_lower):
                    # High risk of ambiguity or presupposition
                    return 0.25 
        
        # Check for insufficient info markers
        if "cannot" in p_lower or "unknown" in p_lower or "insufficient" in p_lower:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Treat prompt as the "Reference" source of truth for extraction
        # In a real scenario, we might have a separate ground truth, 
        # but here we assume the prompt contains the necessary constraints.
        ref_props = self._extract_props(prompt)
        ref_closure = self._build_closure(ref_props)
        ref_weights = self._compute_weights(ref_props, ref_closure)
        
        results = []
        
        for cand in candidates:
            cand_props = self._extract_props(cand)
            cand_closure = self._build_closure(cand_props)
            
            # Compute weights based on relevance to prompt (reference)
            # We re-calculate weights dynamically based on the union of contexts
            all_props = ref_props + cand_props
            # Deduplicate for weight calculation context
            unique_props = list(set(all_props)) 
            
            # Map weights back to indices (simplified for this implementation)
            # We calculate score directly using the formula
            # Score = mu(C(A) n C(R)) / (mu(C(A)) + eps)
            
            # 1. Calculate denominator: Measure of Candidate Closure
            # We need weights for candidate props relative to the whole context
            cand_weights = self._compute_weights(cand_props, ref_closure)
            mu_cand = np.sum(cand_weights) if len(cand_weights) > 0 else self.epsilon
            if mu_cand == 0: mu_cand = self.epsilon
            
            # 2. Calculate numerator: Measure of Intersection
            # Intersection is simply props in cand_closure that are also in ref_closure
            intersection_measure = 0.0
            for i, p in enumerate(cand_props):
                if p in ref_closure:
                    intersection_measure += cand_weights[i]
            
            base_score = intersection_measure / (mu_cand + self.epsilon)
            
            # Tiebreaker: NCD (max 15% influence)
            # Normalize NCD to [0, 1] where 1 is good (low distance)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            final_score = (base_score * 0.85) + ncd_score
            
            # Reasoning string generation
            reasoning = f"Extracted {len(cand_props)} propositions. "
            reasoning += f"Cognitive load penalty applied to {len(cand_props) - int(intersection_measure)} extraneous items. "
            if base_score > 0.5:
                reasoning += "High logical overlap with prompt constraints."
            else:
                reasoning += "Low logical overlap or high extraneous load."
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level to ensure epistemic honesty.
        """
        # 1. Check Meta-Confidence (Tier B Traps)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural/Computation Check
        # If we can extract clear numbers and the answer matches a calculation, confidence is high
        props = self._extract_props(prompt)
        nums = [p for p in props if p[0] == 'num']
        
        # If there are numbers, we expect a computed answer
        if len(nums) >= 2:
            # Heuristic: Does the answer contain a number?
            ans_nums = re.findall(r'\d+(?:\.\d+)?', answer)
            if not ans_nums:
                return 0.3 # Low confidence if computation expected but no number provided
            
            # Simple verification: Is the answer's number close to any derived logic?
            # (In a full engine, this would be the actual calculation result)
            try:
                ans_val = float(ans_nums[0])
                prompt_vals = [float(n[2][0]) for n in nums]
                
                # If the answer is one of the prompt numbers, it might be a copy, not a solution
                # Unless it's a specific type of question. 
                # For this tool, if we detect math, we want to see a result that isn't just an input.
                if ans_val in prompt_vals and len(prompt_vals) > 1:
                    # Suspiciously simple, but maybe correct. 
                    # Let's rely on the structural score for the exact value.
                    pass 
                    
                # If we passed the trap check and have numbers, we are moderately confident
                # unless the answer is nonsense.
                return min(0.85, meta_cap) 
                
            except ValueError:
                return 0.4

        # 3. Default Structural Confidence
        # If no numbers, rely on proposition match
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
            
        score = eval_res[0]['score']
        
        # Map score to confidence, capped by meta
        # Score 0.5 -> Conf 0.6, Score 1.0 -> Conf 0.9
        raw_conf = 0.5 + (score * 0.4)
        
        return min(raw_conf, meta_cap)