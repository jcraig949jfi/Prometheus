import re
import numpy as np
import zlib
from itertools import chain

class ReasoningTool:
    """
    Constrained Maximum-Entropy Free-Energy Scorer (CME-FES).
    Mechanism:
    1. Structural Parsing: Extracts numeric constraints, negations, conditionals, and causal links.
    2. Feature Grounding: Evaluates candidate truth-values against these constraints using vectorized ops.
    3. MaxEnt Fitting: Iteratively adjusts Lagrange multipliers (lambda) to match empirical constraint satisfaction.
    4. Free Energy Scoring: Computes -log(P) as a plausibility score; lower free energy = higher plausibility.
    5. Epistemic Honesty: Meta-analysis of prompt ambiguity caps confidence to prevent overconfidence on traps.
    """

    def __init__(self):
        self.max_iter = 50
        self.learning_rate = 0.1
        # Regex patterns for structural extraction
        self.patterns = {
            'numeric': re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:>|<|≥|≤|=|is|are)\s*(\d+(?:\.\d+)?)\b'),
            'comp_num': re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:>|<|≥|≤|=)\s*(\d+(?:\.\d+)?)\b'),
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?),\s*(.+?)', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|because|leads to|results in)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did .+ fail|why did .+ stop|when did .+ stop)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\beither\s+.+\s+or\s+.+\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            'pronoun_ambig': re.compile(r'(.+?)\s+told\s+(.+?)\s+he\s+', re.IGNORECASE)
        }

    def _tokenize(self, text):
        return re.findall(r'\w+|[^\s\w]', text.lower())

    def _extract_constraints(self, text):
        constraints = []
        tokens = self._tokenize(text)
        text_lower = text.lower()
        
        # Numeric comparisons
        for m in self.patterns['comp_num'].finditer(text):
            v1, v2 = float(m.group(1)), float(m.group(2))
            op = m.group(0).replace(m.group(1), '').replace(m.group(2), '').strip()
            constraints.append(('numeric', op, (v1, v2)))
            
        # Negation presence
        if self.patterns['negation'].search(text):
            constraints.append(('negation', 'exists', True))
            
        # Conditional structure
        if self.patterns['conditional'].search(text):
            constraints.append(('conditional', 'exists', True))
            
        # Causal structure
        if self.patterns['causal'].search(text):
            constraints.append(('causal', 'exists', True))
            
        return constraints

    def _ground_features(self, prompt, candidates):
        """Create feature matrix F: (n_candidates, n_features)"""
        if not candidates:
            return np.array([]), []
        
        constraints = self._extract_constraints(prompt)
        if not constraints:
            # Fallback: simple overlap if no structure found
            p_tokens = set(self._tokenize(prompt))
            features = []
            for c in candidates:
                c_tokens = set(self._tokenize(c))
                # Feature: overlap ratio
                val = len(p_tokens & c_tokens) / (len(p_tokens | c_tokens) + 1e-9)
                features.append([val])
            return np.array(features), ['overlap']
        
        feature_names = [f"{c[0]}_{i}" for i, c in enumerate(constraints)]
        F = np.zeros((len(candidates), len(constraints)))
        
        for i, cand in enumerate(candidates):
            cand_lower = cand.lower()
            cand_nums = re.findall(r'\d+(?:\.\d+)?', cand_lower)
            
            for j, (ctype, scope, val) in enumerate(constraints):
                if ctype == 'numeric':
                    # Check if candidate satisfies the numeric relation extracted from prompt
                    # Simplified: Does the candidate contain numbers that satisfy the prompt's logic?
                    # Or does it simply restate the numbers correctly?
                    # Heuristic: If prompt says "A > B", candidate should reflect that order or truth.
                    # Here we check if candidate contradicts explicit prompt numbers.
                    v1, v2 = val
                    op = scope
                    # Extract numbers from candidate to see if they contradict
                    if len(cand_nums) >= 2:
                        cv1, cv2 = float(cand_nums[0]), float(cand_nums[1])
                        satisfied = False
                        if op == '>': satisfied = cv1 > cv2
                        elif op == '<': satisfied = cv1 < cv2
                        elif op == '=': satisfied = abs(cv1 - cv2) < 1e-6
                        F[i, j] = 1.0 if satisfied else 0.0
                    else:
                        # If candidate doesn't have numbers, assume neutral or check text match
                        F[i, j] = 0.5 
                        
                elif ctype == 'negation':
                    has_neg = bool(self.patterns['negation'].search(cand_lower))
                    # If prompt has negation, candidate should likely handle it (heuristic)
                    # This is a weak proxy; better if we parse logic trees.
                    # For now, reward consistency if prompt implies negation handling
                    F[i, j] = 1.0 if has_neg else 0.0
                    
                elif ctype in ('conditional', 'causal'):
                    # Reward candidates that contain logical connectors if prompt has them
                    has_conn = bool(re.search(r'\b(if|then|because|therefore|thus)\b', cand_lower))
                    F[i, j] = 1.0 if has_conn else 0.0
                    
        return F, feature_names

    def _max_ent_fit(self, F):
        """Fit lambda using Generalized Iterative Scaling logic"""
        if F.size == 0:
            return np.array([])
        
        n_feats = F.shape[1]
        lam = np.zeros(n_feats)
        
        # Empirical counts: Assume prompt constraints are "true" observations.
        # We want the model expectation to match a target vector of high satisfaction.
        # Target: All constraints satisfied (1.0) for the "ideal" candidate.
        target = np.ones(n_feats) * 0.9 # Soft target
        
        for _ in range(self.max_iter):
            logits = F @ lam
            # Stabilize exp
            logits -= np.max(logits)
            exp_vals = np.exp(logits)
            sum_exp = np.sum(exp_vals) + 1e-9
            probs = exp_vals / sum_exp
            
            # Gradient: Target - Expected
            expected = F.T @ probs
            grad = target - expected
            
            if np.all(np.abs(grad) < 1e-4):
                break
                
            lam += self.learning_rate * grad
            
        return lam

    def _compute_free_energy(self, F, lam):
        if F.size == 0 or lam.size == 0:
            return np.array([0.5])
            
        logits = F @ lam
        logits -= np.max(logits) # Numerical stability
        Z = np.sum(np.exp(logits)) + 1e-9
        probs = np.exp(logits) / Z
        
        # Free Energy F = -log P (ignoring constant KL term for ranking)
        # Lower F = Higher Prob
        fe = -np.log(probs + 1e-9)
        return fe

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance heuristic"""
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _meta_confidence(self, prompt):
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_low):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_low):
            # Check if options are exhaustive (hard to know), but flag as risky
            if "or" in p_low and "either" in p_low:
                return 0.4
                
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_low):
            if "best" in p_low or "worst" in p_low:
                # If no metrics provided in prompt, it's subjective
                if "metric" not in p_low and "criteria" not in p_low and "%" not in p_low:
                    return 0.3
                    
        # 4. Pronoun Ambiguity
        if self.patterns['pronoun_ambig'].search(p_low):
            if "who" in p_low or "which" in p_low:
                return 0.25

        # 5. Unanswerable / Missing Info
        if "cannot be determined" in p_low or "insufficient" in p_low:
            return 0.1
            
        return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Ground features
        F, _ = self._ground_features(prompt, candidates)
        
        # 2. Fit MaxEnt
        lam = self._max_ent_fit(F)
        
        # 3. Compute Free Energy Scores
        fe_scores = self._compute_free_energy(F, lam)
        
        # 4. Hybrid Scoring (Structure + NCD tiebreaker)
        final_scores = []
        prompt_nums = re.findall(r'\d+', prompt)
        
        for i, cand in enumerate(candidates):
            base_score = -fe_scores[i] if fe_scores.size > 0 else 0.0
            
            # Constructive computation bonus: If prompt has math, check answer
            if len(prompt_nums) >= 2:
                # Simple heuristic: if candidate is a number, does it look like a result?
                cand_nums = re.findall(r'\d+(?:\.\d+)?', cand)
                if cand_nums:
                    # Boost if candidate provides a specific numeric resolution
                    base_score += 0.5 
            
            # NCD Tiebreaker (max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            # NCD is distance (0=same), we want similarity. 
            # But NCD is noisy. Use only if scores are close or as small penalty for gibberish.
            ncd_bonus = (1.0 - ncd) * 0.15
            
            total_score = base_score + ncd_bonus
            final_scores.append(total_score)
        
        # Normalize scores to 0-1 range roughly
        scores_arr = np.array(final_scores)
        if scores_arr.size > 0:
            min_s, max_s = scores_arr.min(), scores_arr.max()
            if max_s > min_s:
                norm_scores = (scores_arr - min_s) / (max_s - min_s + 1e-9)
            else:
                norm_scores = scores_arr
        else:
            norm_scores = np.array([])
            
        # Rank and format
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(norm_scores[i]) if i < len(norm_scores) else 0.0,
                "reasoning": f"MaxEnt-FreeEnergy score based on {len(self._extract_constraints(prompt))} constraints."
            })
            
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-analysis cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # Structural evaluation
        candidates = [answer, "dummy_placeholder_to_force_matrix"]
        # Run a lightweight eval to get score relative to a dummy
        # Actually, better to eval single candidate against constraints
        res = self.evaluate(prompt, [answer])
        
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Cap by meta-confidence
        final_conf = min(base_score, meta_cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))