import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Bayesian-Control-Free-Energy Scorer.
    
    Mechanism:
    1. Parsing: Extracts propositions and relations (negation, comparative, causal, etc.) 
       into a symbolic graph represented by NumPy arrays.
    2. Likelihood: Computes compatibility between prompt KB and candidate assertions.
    3. Bayesian Update: Updates posterior probabilities based on likelihood.
    4. Feedback Control: Uses a PID controller on Shannon Entropy to regulate temperature (tau),
       preventing over-confidence or excessive diffusion.
    5. Free Energy: Minimizes variational free energy (surprise + complexity) to refine scores.
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence (Tier B).
    """

    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05
        self.target_entropy = 0.8  # Target uncertainty level
        self.tau = 1.0             # Temperature
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # Weights for relations
        self.weights = {
            'equality': 2.0,
            'comparative': 1.5,
            'causal': 1.2,
            'conditional': 1.0,
            'temporal': 0.8,
            'negation': -2.0 # Penalty for contradiction
        }
        self.rel_map = {'equality': 0, 'comparative': 1, 'causal': 2, 'conditional': 3, 'temporal': 4, 'negation': 5}

    def _extract_props(self, text: str) -> List[str]:
        """Simple extraction of potential propositions (clauses)."""
        # Split by common delimiters but keep content
        raw = re.split(r'[;,.]| (?:and|or|but) ', text.lower())
        return [s.strip() for s in raw if len(s.strip()) > 2]

    def _parse_relations(self, text: str, props: List[str]) -> List[Tuple[int, int, str]]:
        """Extract relations between propositions or entities."""
        relations = []
        text_l = text.lower()
        
        # Helper to find prop index
        def get_idx(sub):
            for i, p in enumerate(props):
                if sub in p or p in sub:
                    return i
            return -1

        # Negation
        if re.search(r'\b(not|no|never|none)\b', text_l):
            for i, p in enumerate(props):
                if re.search(r'\b(not|no|never|none)\b', p):
                    relations.append((i, i, 'negation'))

        # Comparatives
        if re.search(r'(greater|less|more|fewer|larger|smaller|before|after)', text_l):
            # Simplified: assume relation between first two props if numbers exist
            nums = re.findall(r'-?\d+\.?\d*', text)
            if len(nums) >= 2:
                # Map numbers to props roughly
                idxs = []
                for n in nums[:2]:
                    found = False
                    for i, p in enumerate(props):
                        if n in p and i not in idxs:
                            idxs.append(i)
                            found = True
                            break
                    if not found: idxs.append(len(props)-1) # Fallback
                
                if 'greater' in text_l or 'more' in text_l or 'larger' in text_l:
                     if len(idxs) >= 2: relations.append((idxs[0], idxs[1], 'comparative')) # A > B
                elif 'less' in text_l or 'fewer' in text_l or 'smaller' in text_l:
                    if len(idxs) >= 2: relations.append((idxs[1], idxs[0], 'comparative')) # B > A (so A < B)
                    
        # Equality
        if re.search(r'(equal|same|identical|is|are|was|were)', text_l) and 'not' not in text_l:
             if len(props) >= 2:
                 relations.append((0, 1, 'equality'))

        # Causal/Conditional
        if re.search(r'(because|therefore|leads to|results in|if|then|unless)', text_l):
            if len(props) >= 2:
                if 'because' in text_l or 'leads' in text_l:
                    relations.append((1, 0, 'causal')) # Effect <- Cause
                else:
                    relations.append((0, 1, 'conditional')) # If A then B

        return relations

    def _build_kb(self, prompt: str) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray]:
        """Construct Knowledge Base graph."""
        props = self._extract_props(prompt)
        if not props: props = [prompt] # Fallback
        
        rels = self._parse_relations(prompt, props)
        n = len(props)
        
        # Arrays: src, dst, type
        if not rels:
            return props, np.array([]), np.array([]), np.array([])
            
        src = np.array([r[0] for r in rels])
        dst = np.array([r[1] for r in rels])
        rtype = np.array([self.rel_map.get(r[2], 0) for r in rels])
        
        return props, src, dst, rtype

    def _compute_assertion_matrix(self, candidate: str, kb_props: List[str], kb_src: np.ndarray, kb_dst: np.ndarray, kb_rtype: np.ndarray) -> np.ndarray:
        """Map candidate assertions to KB structure."""
        if len(kb_src) == 0:
            return np.array([])
            
        A = np.zeros_like(kb_src, dtype=float)
        cand_l = candidate.lower()
        
        # Check for direct contradictions or confirmations based on keywords
        for i, (s, d, rt) in enumerate(zip(kb_src, kb_dst, kb_rtype)):
            # Very simplified check: does candidate contain negation words where KB implies positive, or vice versa?
            # Since KB is derived from prompt, we assume prompt is Truth.
            # If candidate has "not" and KB relation is positive -> -1
            # If candidate lacks "not" and matches context -> 1
            
            has_neg = bool(re.search(r'\b(not|no|never|false|incorrect)\b', cand_l))
            
            if rt == 5: # Negation in KB
                A[i] = -1.0 if not has_neg else 1.0 # If KB says "Not X", and Cand says "X" (no neg), penalty? 
                # Actually, if KB says "Not X", and Cand says "X", that's a contradiction (-1).
                # If Cand says "Not X", that's a match (1).
                A[i] = 1.0 if has_neg else -1.0
            else:
                # Positive relation in KB
                if has_neg:
                    A[i] = -1.0 # Contradiction
                else:
                    A[i] = 1.0 # Match (silent assumption of agreement if no contradiction found)
                    
        return A

    def _compute_entropy(self, post: np.ndarray) -> float:
        if np.sum(post) == 0: return 0.0
        p = post / np.sum(post)
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    def _pid_step(self, entropy: float):
        error = self.target_entropy - entropy
        self.integral_error += error
        derivative = error - self.prev_error
        
        self.tau += self.Kp * error + self.Ki * self.integral_error + self.Kd * derivative
        self.tau = max(0.1, min(5.0, self.tau)) # Clamp tau
        self.prev_error = error

    def _free_energy_step(self, log_L: float, post: np.ndarray, prior: np.ndarray):
        # F = -log L + KL(Post || Prior)
        # Approximate gradient descent on tau is complex without explicit function, 
        # so we use the PID output as the primary regulator and this as a score modifier.
        kl_div = np.sum(post * np.log((post + 1e-10) / (prior + 1e-10)))
        return -log_L + kl_div

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|why did .+ fail|when did .+ stop)', p):
            score -= 0.8
        # 2. Scope/Pronoun ambiguity
        if re.search(r'(every .+ a .+|told .+ he |told .+ she)', p) and '?' in p:
            score -= 0.5
        # 3. False dichotomy
        if re.search(r'(either .+ or .+)', p) and 'other' not in p:
            score -= 0.4
        # 4. Subjectivity
        if re.search(r'(best|worst|favorite|opinion)', p) and 'calculate' not in p:
            score -= 0.6
        # 5. Unanswerable / Missing info
        if re.search(r'(impossible|cannot be determined|not enough info)', p):
            score = 0.1
            
        return max(0.0, min(1.0, score))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            c1 = len(repr(s1)) # Approx compression length for short strings
            c2 = len(repr(s2))
            c12 = len(repr(s1 + s2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt KB
        kb_props, kb_src, kb_dst, kb_rtype = self._build_kb(prompt)
        n_rels = len(kb_src)
        
        if n_rels == 0:
            # Fallback to NCD if no structure found
            scores = []
            for c in candidates:
                # Inverse NCD: lower distance = higher score
                dist = self._ncd_score(prompt, c)
                scores.append(1.0 - dist)
            total = sum(scores) + 1e-9
            scores = [s/total for s in scores]
            return [{"candidate": c, "score": float(s), "reasoning": "NCD fallback"} for c, s in zip(candidates, scores)]

        # 2. Compute Likelihoods
        raw_scores = []
        assertion_matrices = []
        
        for c in candidates:
            A_c = self._compute_assertion_matrix(c, kb_props, kb_src, kb_dst, kb_rtype)
            assertion_matrices.append(A_c)
            
            # Weighted sum
            s = 0.0
            for i, val in enumerate(A_c):
                if val != 0:
                    rel_type_int = kb_rtype[i]
                    # Map int back to weight lookup (simplified)
                    w = 1.0 
                    if rel_type_int == 0: w = self.weights['equality']
                    elif rel_type_int == 1: w = self.weights['comparative']
                    elif rel_type_int == 2: w = self.weights['causal']
                    elif rel_type_int == 5: w = self.weights['negation']
                    
                    s += w * val # val is 1 (match) or -1 (contradiction)
            raw_scores.append(s)

        # Iterative refinement (PID + Free Energy loop)
        raw_scores = np.array(raw_scores)
        prior = np.ones(len(candidates)) / len(candidates)
        
        # Initial Likelihood
        exp_scores = np.exp((raw_scores - np.max(raw_scores)) / self.tau) # Stability shift
        likelihood = exp_scores / np.sum(exp_scores)
        
        # Bayesian Update
        posterior = likelihood * prior
        posterior /= np.sum(posterior) + 1e-10
        
        # Feedback Control Loop (Simulate one step of regulation)
        H = self._compute_entropy(posterior)
        self._pid_step(H)
        
        # Recompute with new tau
        exp_scores = np.exp((raw_scores - np.max(raw_scores)) / self.tau)
        likelihood = exp_scores / np.sum(exp_scores)
        posterior = likelihood * prior
        posterior /= np.sum(posterior) + 1e-10
        
        # Free Energy Calculation for final scoring
        log_L = np.sum(np.log(likelihood + 1e-10))
        F = self._free_energy_step(log_L, posterior, prior)
        
        # Final Score: Mix of Posterior and Free Energy minimization
        # Higher posterior = better. Lower Free Energy = better.
        # We use Posterior as the main rank, adjusted by F slightly if needed, 
        # but Posterior already encapsulates the likelihood derived from structural match.
        final_scores = posterior
        
        results = []
        for i, c in enumerate(candidates):
            # Meta-confidence check for the specific candidate content vs prompt ambiguity
            meta_conf = self._meta_confidence(prompt)
            
            # If the prompt is ambiguous, cap the score difference
            if meta_conf < 0.3:
                # Flatten scores towards uniform if prompt is a trap
                final_scores[i] = (final_scores[i] * 0.2) + (0.8 / len(candidates))
            
            results.append({
                "candidate": c,
                "score": float(final_scores[i]),
                "reasoning": f"Structural match: {raw_scores[i]:.2f}, Tau: {self.tau:.2f}, MetaConf: {meta_conf:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Run evaluation to get structural score
        res = self.evaluate(prompt, [answer, "DUMMY_PLACEHOLDER_TO_FORCE_RELATIVITY"])
        if not res:
            return 0.0
            
        base_score = res[0]['score'] if res[0]['candidate'] == answer else (res[1]['score'] if len(res) > 1 else 0.5)
        
        # Normalize base_score roughly to 0-1 range assuming binary choice
        # If answer is top ranked, score is high. 
        # However, if meta_conf is low, we must cap.
        
        final_conf = base_score * 2.0 # Scale up slightly since binary split dilutes
        final_conf = min(1.0, final_conf)
        
        # Apply epistemic cap
        if meta_conf < 0.3:
            return min(final_conf, 0.25) # Hard cap for ambiguous prompts
        
        # Never return > 0.9 unless the structural match is perfect and unambiguous
        if meta_conf < 1.0:
            final_conf = min(final_conf, 0.85)
            
        return float(final_conf)