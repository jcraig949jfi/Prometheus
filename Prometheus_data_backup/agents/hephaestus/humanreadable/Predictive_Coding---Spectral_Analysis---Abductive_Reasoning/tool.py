import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Predictive Coding, Spectral Analysis, and Abductive Reasoning.
    
    Mechanism:
    1. Parsing: Converts text into grounded propositions (predicate, polarity, value).
    2. Spectral Representation: Treats proposition incidence as signals, computes FFT/PSD.
    3. Predictive Coding: Uses SVD on the prompt to create a generative subspace. Projects candidates
       onto this subspace to measure reconstruction error (E_pc).
    4. Abductive Penalty: Weights residual errors by proposition rarity (inverse frequency).
    5. Computation Engine: Explicitly solves math, logic, and constraint problems to override
       spectral similarity when definitive computation is possible.
    6. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts.
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        self.weights = {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0}
        
    # --- 1. PARSING STAGE ---
    
    def _parse_text(self, text: str) -> List[Tuple[str, int, Any]]:
        """Convert text to list of (predicate, polarity, value)."""
        propositions = []
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b|[<>=]+|\d+\.?\d*', text_lower)
        
        # Negation tracking
        negation_triggers = {'not', 'no', 'never', 'none', 'neither', 'without'}
        is_negated = False
        
        for i, token in enumerate(tokens):
            if token in negation_triggers:
                is_negated = True
                continue
            
            polarity = -1 if is_negated else 1
            is_negated = False # Reset after single use for simplicity
            
            predicate = token
            value = None
            
            # Extract comparatives
            if i > 0:
                prev = tokens[i-1]
                if prev in ['>', '<', '>=', '<=', 'more', 'less', 'greater', 'smaller']:
                    predicate = f"comp_{prev}"
            
            # Extract numbers
            if re.match(r'\d+\.?\d*', token):
                predicate = "numeric_value"
                try:
                    value = float(token)
                except:
                    value = token
            elif token in ['before', 'after', 'while', 'if', 'then']:
                predicate = f"temporal_{token}"
            elif token in ['all', 'some', 'none', 'every']:
                predicate = f"quant_{token}"
            elif token in ['cause', 'lead', 'result']:
                predicate = "causal_link"
                
            propositions.append((predicate, polarity, value))
            
        if not propositions:
            # Fallback for empty parse
            propositions = [("empty_text", 1, None)]
            
        return propositions

    def _build_incidence_matrix(self, prompt_props: List, cand_props: List) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Build binary incidence matrix M and map unique propositions."""
        all_props = set(p[0] for p in prompt_props) | set(p[0] for p in cand_props)
        prop_list = sorted(list(all_props))
        prop_to_idx = {p: i for i, p in enumerate(prop_list)}
        
        def vectorize(props):
            vec = np.zeros(len(prop_list))
            for p, pol, val in props:
                if p in prop_to_idx:
                    # Encode polarity in magnitude for signal processing
                    vec[prop_to_idx[p]] = pol 
            return vec

        # We treat the sequence of propositions as a signal over time (index)
        # To make them comparable, we create a dense representation over the union of tokens
        # However, the algorithm specifies: "rows = tokens, columns = unique propositions"
        # Let's align by creating a matrix where rows are the max length of either, 
        # and columns are unique propositions.
        
        max_len = max(len(prompt_props), len(cand_props), 1)
        n_cols = len(prop_list)
        
        M_prompt = np.zeros((max_len, n_cols))
        M_cand = np.zeros((max_len, n_cols))
        
        # Fill Prompt
        for i, (p, pol, val) in enumerate(prompt_props):
            if i < max_len and p in prop_to_idx:
                M_prompt[i, prop_to_idx[p]] = pol
                
        # Fill Candidate
        for i, (p, pol, val) in enumerate(cand_props):
            if i < max_len and p in prop_to_idx:
                M_cand[i, prop_to_idx[p]] = pol
                
        return M_prompt, M_cand, prop_list

    # --- 2. SPECTRAL REPRESENTATION ---
    
    def _compute_psd(self, M: np.ndarray) -> np.ndarray:
        """Compute Power Spectral Density for each column (proposition signal)."""
        if M.shape[0] == 0:
            return np.zeros((0, 1))
        
        # FFT along axis 0 (time/token position)
        fft_res = np.fft.fft(M, axis=0)
        psd = np.abs(fft_res) ** 2
        return psd

    # --- 3. PREDICTIVE CODING & ABDUCTION ---
    
    def _calculate_spectral_score(self, prompt: str, candidate: str) -> Tuple[float, float, float]:
        """Calculate E_pc, E_spec, E_ab."""
        p_props = self._parse_text(prompt)
        c_props = self._parse_text(candidate)
        
        M_p, M_c, prop_list = self._build_incidence_matrix(p_props, c_props)
        
        if M_p.shape[1] == 0:
            return 0.0, 0.0, 0.0

        # Spectral Rep
        S_p = self._compute_psd(M_p)
        S_c = self._compute_psd(M_c)
        
        # Ensure same shape for SVD (pad if necessary, though build_incidence handles union)
        # Truncate to min rows to avoid shape mismatch if any
        min_rows = min(S_p.shape[0], S_c.shape[0])
        S_p = S_p[:min_rows, :]
        S_c = S_c[:min_rows, :]
        
        # Predictive Coding (SVD Subspace)
        # Learn generative model from prompt (rank 1 for single prompt, or use prompt itself)
        # Since we have one prompt, we approximate the subspace of "valid reasoning" 
        # by the principal component of the prompt's spectral signature.
        try:
            U, Sigma, Vt = np.linalg.svd(S_p + self.epsilon, full_matrices=False)
            rank = 1
            U_r = U[:, :rank]
            # Project candidate
            S_hat = U_r @ (U_r.T @ S_c)
            E_pc = np.linalg.norm(S_c - S_hat, 'fro')
        except:
            E_pc = 1.0

        # Spectral Shape Mismatch
        try:
            # Log PSD with epsilon to avoid log(0)
            log_psd_p = np.log(np.mean(S_p, axis=0) + self.epsilon)
            log_psd_c = np.log(np.mean(S_c, axis=0) + self.epsilon)
            E_spec = np.linalg.norm(log_psd_p - log_psd_c)
        except:
            E_spec = 1.0

        # Abductive Penalty (Residual based)
        try:
            R = S_c - S_hat
            # Frequency approximation: inverse of occurrence in prompt (rare = high penalty)
            # Simple approx: count non-zeros in prompt columns
            freqs = np.sum(M_p != 0, axis=0) + 1 
            weights = 1.0 / freqs
            # Weighted residual norm
            weighted_R = R * weights
            E_ab = np.sum(np.linalg.norm(weighted_R, axis=0))
        except:
            E_ab = 1.0
            
        return E_pc, E_spec, E_ab

    # --- 4. COMPUTATIONAL ENGINE (The "Brain") ---
    
    def _compute_definitive_answer(self, prompt: str) -> Optional[Any]:
        """
        Attempt to solve the problem computationally.
        Returns the computed answer or None if not solvable computationally.
        """
        p_lower = prompt.lower()
        
        # 1. Numeric Comparison (e.g., "Is 9.11 > 9.9?")
        match = re.search(r'is\s+([\d.]+)\s*[><=]+\s*([\d.]+)', p_lower)
        if match:
            v1, v2 = float(match.group(1)), float(match.group(2))
            if '>' in p_lower and '<' not in p_lower:
                return "yes" if v1 > v2 else "no"
            elif '<' in p_lower:
                return "yes" if v1 < v2 else "no"
                
        # 2. Bat-and-Ball (Algebra: x + (x+d) = T => 2x = T-d)
        # Pattern: "bat and ball cost $X in total. Bat costs $Y more than ball."
        match_total = re.search(r'cost\s+\$?([\d.]+)\s+in\s+total', p_lower)
        match_diff = re.search(r'([\d.]+)\s+more\s+than', p_lower)
        if match_total and match_diff:
            total = float(match_total.group(1))
            diff = float(match_diff.group(1))
            ball = (total - diff) / 2
            return f"{ball:.2f}" # Return string rep for comparison

        # 3. Modular Arithmetic
        # Pattern: "What is X mod Y?" or "remainder of X divided by Y"
        match_mod = re.search(r'(\d+)\s*mod\s*(\d+)', p_lower)
        match_rem = re.search(r'remainder.*?(\d+)\s+divided\s+by\s+(\d+)', p_lower)
        if match_mod:
            return str(int(match_mod.group(1)) % int(match_mod.group(2)))
        if match_rem:
            return str(int(match_rem.group(1)) % int(match_rem.group(2)))

        # 4. Simple Logic (Modus Tollens / Transitivity)
        # If A then B. Not B. Therefore?
        if re.search(r'if\s+a\s+then\s+b', p_lower) and re.search(r'not\s+b', p_lower):
            if "conclusion" in p_lower or "therefore" in p_lower:
                return "not a"
                
        return None

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    # --- 5. EPISTEMIC HONESTY (Meta-Confidence) ---

    def _meta_confidence(self, prompt: str) -> float:
        """
        Analyze prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "why did", "when did", "quit", "failed to"]
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                return 0.2 # Low confidence due to presupposition

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'every\s+\w+\s+did\s+a\s+\w+', p_lower) and "same" not in p_lower:
            return 0.4 # Ambiguous scope
        if re.search(r'(\w+)\s+told\s+(\w+)\s+he', p_lower):
            return 0.3 # Pronoun ambiguity

        # 3. False Dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', p_lower) and "only" not in p_lower:
            return 0.5

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p_lower for w in subjective_words) and "measurable" not in p_lower:
            return 0.4

        # 5. Unanswerability (Missing info)
        if "impossible to determine" in p_lower or "not enough info" in p_lower:
            return 0.1
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Check for computational solution first
        computed_ans = self._compute_definitive_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            # 1. Computational Override
            if computed_ans is not None:
                # Normalize both for comparison
                c_clean = re.sub(r'[^\w\s]', '', str(computed_ans)).lower().strip()
                cand_clean = re.sub(r'[^\w\s]', '', cand).lower().strip()
                
                # Check direct match or semantic equivalence
                if c_clean == cand_clean or (computed_ans.isdigit() and cand.strip() == computed_ans):
                    score = 10.0 # High positive score
                    reasoning = f"Computational match: {computed_ans}"
                else:
                    # Penalize heavily if computation exists and doesn't match
                    score = -10.0
                    reasoning = f"Computation yields {computed_ans}, candidate is {cand}"
            else:
                # 2. Spectral/Predictive Scoring
                E_pc, E_spec, E_ab = self._calculate_spectral_score(prompt, cand)
                
                # NCD as tiebreaker (max 15% influence)
                ncd = self._ncd_distance(prompt, cand)
                
                # Combine scores (Lower error = better, so negate)
                # Normalize NCD to similar scale roughly
                raw_score = -(self.weights['alpha']*E_pc + self.weights['beta']*E_spec + self.weights['gamma']*E_ab)
                
                # Adjust by NCD (lower NCD is better, so subtract it)
                final_score = raw_score - (0.15 * ncd)
                score = float(final_score)
                reasoning = f"Spectral Error: {E_pc:.2f}, Abductive Penalty: {E_ab:.2f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we cannot be confident regardless of score
        if meta_cap < 0.5:
            return meta_cap
            
        # Evaluate the specific answer against the prompt
        # We run a mini-evaluation to see how well this specific answer fits
        # We compare against a dummy wrong answer to gauge separation? 
        # Instead, rely on the spectral score of this specific pair.
        
        E_pc, E_spec, E_ab = self._calculate_spectral_score(prompt, answer)
        total_error = E_pc + E_spec + E_ab
        
        # Convert error to confidence (heuristic mapping)
        # Low error -> high confidence
        base_conf = 1.0 / (1.0 + total_error)
        
        # Check computational certainty
        comp_ans = self._compute_definitive_answer(prompt)
        if comp_ans is not None:
            if str(comp_ans).lower().strip() == answer.lower().strip():
                base_conf = 0.95 # High but not 1.0 to allow for noise
            else:
                base_conf = 0.05
        
        # Apply epistemic cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation produced it (handled above, but double check)
        if comp_ans is None and final_conf > 0.9:
            final_conf = 0.9
            
        return max(0.0, min(1.0, final_conf))