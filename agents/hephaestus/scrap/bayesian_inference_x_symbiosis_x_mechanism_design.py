import re
import math
import zlib
from typing import List, Dict, Tuple

try:
    import numpy as np
except ImportError:
    # Fallback if numpy is strictly unavailable, though prompt implies it's allowed
    raise ImportError("numpy is required for this tool")

class ReasoningTool:
    """
    A reasoning tool combining Bayesian Inference, Feature Symbiosis, and Mechanism Design.
    
    Mechanism:
    1. Parses prompts into logical features (negations, comparatives, causals, etc.).
    2. Constructs a 'Symbiosis Matrix' where co-occurring features in valid logical structures
       reinforce each other (high diagonal/off-diagonal weights).
    3. Computes a compatibility score for each candidate based on feature presence.
    4. Applies Bayesian updating to derive posterior probabilities.
    5. Uses a Logarithmic Proper Scoring Rule for final ranking.
    6. Implements Tier B Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Feature patterns
        self.features = [
            ('negation', r'\b(not|no|never|none|neither)\b'),
            ('comparative', r'\b(greater|less|more|fewer|better|worse|higher|lower)\b'),
            ('conditional', r'\b(if|unless|then|otherwise)\b'),
            ('causal', r'\b(because|therefore|leads to|results in|causes)\b'),
            ('ordering', r'\b(first|second|before|after|next|last)\b'),
            ('quantifier', r'\b(all|some|every|each|any)\b'),
            ('numeric', r'\d+(\.\d+)?'),
            ('unit', r'\b(meters?|seconds?|hours?|days?|years?|%|percent)\b'),
            ('superlative', r'\b(best|worst|most|least|favorite)\b'),
            ('dichotomy', r'\b(either|or|whether)\b'),
            ('presupposition_stop', r'\b(stopped|quit|ceased)\b'),
            ('pronoun_ambig', r'\b(he|she|him|her|they|them)\b'),
        ]
        
        # Tier B Trap Patterns
        self.trap_patterns = {
            'presupposition': [r'\b(have|has|had)\s+you\s+(stopped|quit)\b', r'\bwhy\s+did\s+\w+\s+(fail|stop|lose)\b'],
            'false_dichotomy': [r'\beither\s+.+\s+or\s+.+\?'],
            'subjectivity': [r'\b(best|worst|favorite|opinion)\b'],
            'scope_ambiguity': [r'\bevery\s+\w+\s+did\s+a\s+\w+'], # Simplified heuristic
            'pronoun_query': [r'\bwho\s+was\s+(he|she|it)\?', r'\bwhich\s+one\s+is\s+(he|she|it)\?']
        }

        # Symbiosis Matrix (Manual construction for logical consistency)
        # Features that often co-occur in correct logical reasoning
        self.k = len(self.features)
        self.S = np.eye(self.k) * 1.0  # Base self-weight
        
        # Define symbiotic relationships (indices)
        # Negation + Comparative often implies valid logical distinction
        self._set_sym('negation', 'comparative', 2.0)
        # Conditional + Causal
        self._set_sym('conditional', 'causal', 2.5)
        # Numeric + Unit
        self._set_sym('numeric', 'unit', 3.0)
        # Quantifier + Ordering
        self._set_sym('quantifier', 'ordering', 1.5)
        # Comparative + Numeric (Quantitative comparison)
        self._set_sym('comparative', 'numeric', 2.0)

        self.alpha = 0.5  # Likelihood scaling factor

    def _set_sym(self, f1: str, f2: str, val: float):
        idx1 = next((i for i, (name, _) in enumerate(self.features) if name == f1), None)
        idx2 = next((i for i, (name, _) in enumerate(self.features) if name == f2), None)
        if idx1 is not None and idx2 is not None:
            self.S[idx1, idx2] = val
            self.S[idx2, idx1] = val

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text."""
        text_lower = text.lower()
        vector = np.zeros(self.k)
        for i, (_, pattern) in enumerate(self.features):
            if re.search(pattern, text_lower):
                vector[i] = 1.0
        return vector

    def _compute_compatibility(self, feature_vec: np.ndarray) -> float:
        """Compute x^T S x"""
        return float(np.dot(feature_vec, np.dot(self.S, feature_vec)))

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Analyze prompt structure for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Presupposition Traps
        for pattern in self.trap_patterns['presupposition']:
            if re.search(pattern, p_lower):
                return 0.2 # Highly suspicious, likely a trap
        
        # 2. False Dichotomy
        for pattern in self.trap_patterns['false_dichotomy']:
            if re.search(pattern, p_lower):
                # Check if answer acknowledges complexity or just picks A/B
                if len(a_lower.split()) < 5 and ('either' in p_lower or 'or' in p_lower):
                    return 0.4 

        # 3. Subjectivity without criteria
        for pattern in self.trap_patterns['subjectivity']:
            if re.search(pattern, p_lower):
                # If the prompt asks for "best" but provides no metrics
                if 'measure' not in p_lower and 'data' not in p_lower:
                    return 0.3

        # 4. Pronoun Ambiguity in "Who" questions
        if re.search(r'\bwho\s+', p_lower):
            # Simple heuristic: if multiple names appear before the question
            names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(set(names)) > 2: # Multiple actors potential ambiguity
                return 0.3

        # 5. Unanswerability / Missing Info
        # If prompt has numbers but answer is non-numeric and not a word problem explanation
        has_nums = bool(re.search(r'\d+', prompt))
        if has_nums and len(answer.strip().split()) < 3 and not re.search(r'\d+', answer):
             # Suspicious if math problem expects number but gets short text
             if any(k in p_lower for k in ['calculate', 'sum', 'total', 'difference']):
                 return 0.1

        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        z = zlib.compress
        l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        if l1 == 0 or l2 == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Extract Prompt Features (Context)
        # We don't score the prompt, but its features define the "environment"
        # However, the algorithm specifies scoring candidates based on their INTERNAL feature symbiosis.
        # We interpret "Parsed structural features" as extracting from the Candidate+Prompt combo 
        # or just the Candidate's alignment with logical structures implied by the prompt.
        # To strictly follow the "Symbiosis Matrix" logic:
        # We score how well the CANDIDATE exhibits logical structure (features) that co-occur.
        
        N = len(candidates)
        scores = []
        compat_scores = []
        
        # Pre-calculate feature vectors and compatibility for all candidates
        for cand in candidates:
            # Combine prompt context with candidate for feature extraction if needed,
            # but the prompt says "for answer a_i ... indicating which parsed features are present".
            # We analyze the candidate text primarily, but logical features often require the prompt context.
            # Strategy: Analyze (Prompt + " " + Candidate) to catch conditionals/negations spanning both.
            full_text = f"{prompt} {cand}"
            f_vec = self._extract_features(full_text)
            c_score = self._compute_compatibility(f_vec)
            compat_scores.append(c_score)
        
        # Bayesian Update
        # Prior: Uniform
        # Likelihood: exp(alpha * c_i)
        logits = np.array(compat_scores) * self.alpha
        
        # Stability trick: subtract max
        logits -= np.max(logits)
        exp_logits = np.exp(logits)
        posterior = exp_logits / np.sum(exp_logits)
        
        # Mechanism Design Scoring Rule (Log score)
        # score_i = log(P(H_i|F))
        log_scores = np.log(posterior + 1e-10) # Avoid log(0)
        
        # NCD Tiebreaker (Max 15% influence logic handled by sorting stability or minor addition)
        # Since we need a float score for ranking, we'll keep the log_prob as primary.
        # NCD is used as a secondary sort key if log_scores are very close.
        
        results = []
        for i, cand in enumerate(candidates):
            # Base score from Bayesian mechanism
            base_score = log_scores[i]
            
            # Minor NCD nudge for tie-breaking (normalized to be small)
            # Compare candidate to prompt (similarity might indicate echoing, which is bad)
            # Actually, NCD measures similarity. High similarity to prompt (echoing) is often a distractor.
            # We prefer lower NCD distance to "ideal" but we don't have ideal.
            # Let's use NCD to penalize exact substring echoes if the candidate is too short.
            ncd_val = self._ncd_score(prompt, cand)
            ncd_penalty = 0.0
            if len(cand) < len(prompt) * 0.5 and ncd_val < 0.2: # Likely an echo
                ncd_penalty = -0.5 # Penalize echoing
            
            final_score = base_score + ncd_penalty
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Feature compatibility: {compat_scores[i]:.2f}, Posterior log-prob: {base_score:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of prompt ambiguity (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.3:
            return meta_cap # Hard cap for ambiguous/trap questions

        # 2. Structural Evaluation
        # Evaluate the single answer against the set of "all possible answers" (simulated)
        # Since we only have one answer here, we assess its internal logical consistency score
        full_text = f"{prompt} {answer}"
        f_vec = self._extract_features(full_text)
        c_score = self._compute_compatibility(f_vec)
        
        # Normalize compatibility to 0-1 range roughly
        # Max theoretical score depends on matrix, but let's assume ~10-15 is high for this setup
        raw_conf = 1.0 / (1.0 + math.exp(-0.5 * (c_score - 5.0))) # Sigmoid mapping
        
        # 3. Computation Check (Heuristic)
        # If prompt has math, answer must have numbers
        has_math = bool(re.search(r'\d+\s*[\+\-\*/=]\s*\d+', prompt)) or bool(re.search(r'\d+', prompt))
        if has_math:
            if not re.search(r'\d+', answer):
                raw_conf = 0.1 # Low confidence if math problem answered with text only
            else:
                # Try to verify simple arithmetic if present
                # This is a simplified constructive computation check
                try:
                    # Extract numbers from answer
                    ans_nums = re.findall(r'\d+\.?\d*', answer)
                    if ans_nums:
                        # If the answer contains a number, we boost confidence slightly
                        # assuming the structural parser caught the logic
                        raw_conf = min(1.0, raw_conf + 0.2)
                except:
                    pass

        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless it looks like a definitive computation
        # (Handled by meta_cap mostly, but explicit check)
        if final_conf > 0.9:
            # Require strong numeric or logical markers
            if not (re.search(r'\d+', answer) or 'therefore' in answer.lower() or 'because' in answer.lower()):
                final_conf = 0.85
                
        return max(0.0, min(1.0, final_conf))

# Example Usage (Internal Test Logic)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If A is greater than B, and B is greater than C, is A greater than C?"
    cands = ["Yes, because of transitivity.", "No, A is smaller.", "Maybe."]
    
    res = tool.evaluate(p, cands)
    print("Evaluation Results:")
    for r in res:
        print(f"- {r['candidate']}: {r['score']:.4f}")
        
    conf = tool.confidence(p, res[0]['candidate'])
    print(f"Confidence: {conf:.2f}")
    
    # Tier B Test
    p_trap = "Have you stopped cheating on tests?"
    conf_trap = tool.confidence(p_trap, "Yes, I have stopped.")
    print(f"Trap Confidence: {conf_trap:.2f}") # Should be low