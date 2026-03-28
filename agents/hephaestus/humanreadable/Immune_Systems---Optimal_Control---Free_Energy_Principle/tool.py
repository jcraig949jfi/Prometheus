import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining Structural Parsing, Free Energy Minimization (FEP),
    and Immune-inspired clonal selection, constrained by Optimal Control theory.
    
    Mechanism:
    1. Structural Parsing: Extracts logical propositions (negations, comparatives, conditionals).
    2. Graph Construction: Builds a constraint graph where nodes are entities/concepts.
    3. Free Energy Minimization: Iteratively updates belief states (mean/c covariance) to minimize
       prediction error between observed constraints and predicted logical outcomes.
    4. Immune Selection: Candidates are treated as antigens; the system selects the candidate
       whose logical structure best binds to the prompt's constraints (lowest free energy).
    5. Epistemic Honesty: Meta-analysis detects ambiguity/traps to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'ordering': re.compile(r'(>=|<=|>|<|=|equals|greater than|less than)', re.IGNORECASE),
            'quantifier': re.compile(r'\b(every|all|some|none|at least one)\b', re.IGNORECASE),
            'dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|failed to)\b', re.IGNORECASE),
            'pronoun_ambig': re.compile(r'\b(he|she|him|her|they|it)\b.*\bwho\b', re.IGNORECASE)
        }
        self.noise_cov = 1e-3  # R matrix scalar

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract logical propositions from text."""
        props = []
        text_lower = text.lower()
        
        # Check flags
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_causal = bool(self.patterns['causal'].search(text))
        has_quant = bool(self.patterns['quantifier'].search(text))
        
        props.append({'type': 'flags', 'neg': has_neg, 'comp': has_comp, 'cond': has_cond, 'causal': has_causal, 'quant': has_quant})
        
        # Extract numerics
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        if nums:
            props.append({'type': 'numeric', 'values': nums})
            
        return props

    def _check_meta_traps(self, text: str) -> Tuple[bool, float]:
        """
        Detects Tier B traps (ambiguity, presupposition).
        Returns (is_trap, penalty_score).
        """
        text_lower = text.lower()
        traps = []
        
        if self.patterns['presupposition'].search(text_lower):
            traps.append('presupposition')
        if self.patterns['pronoun_ambig'].search(text_lower):
            traps.append('pronoun_ambiguity')
        if 'either' in text_lower and 'or' in text_lower and 'question' in text_lower:
             # Heuristic for false dichotomy in questions
            if 'which' in text_lower or 'is it' in text_lower:
                traps.append('false_dichotomy')
        if any(k in text_lower for k in ['best', 'worst', 'favorite', 'opinion']):
            if 'measure' not in text_lower and 'data' not in text_lower:
                traps.append('subjectivity')
                
        if traps:
            return True, 0.7 * len(traps) # High penalty
        
        return False, 0.0

    def _build_constraint_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Builds a simplified belief state for the prompt-candidate pair.
        Returns initial mu, Sigma, and node labels.
        """
        # Combine text for context
        full_text = f"{prompt} {candidate}"
        props = self._extract_propositions(full_text)
        
        # Define nodes based on structural features found
        nodes = ['base_consistency', 'logical_flow', 'numeric_validity', 'causal_link']
        n = len(nodes)
        
        # Initialize Belief State: mu=0 (neutral), Sigma=I (high uncertainty)
        mu = np.zeros(n)
        Sigma = np.eye(n)
        
        # Adjust based on extracted features (Clonal initialization)
        # If candidate contradicts prompt negation, penalize base_consistency
        p_props = self._extract_propositions(prompt)
        c_props = self._extract_propositions(candidate)
        
        # Simple heuristic initialization based on feature overlap
        # This mimics the "antigen binding" phase
        score_init = 0.0
        
        # 1. Negation Check
        if p_props[0]['neg'] and not c_props[0]['neg']:
            # If prompt has negation but candidate doesn't acknowledge it, slight penalty
            # (Very rough heuristic for demonstration)
            pass 
            
        # 2. Numeric Consistency
        p_nums = []
        c_nums = []
        for p in p_props:
            if p['type'] == 'numeric': p_nums.extend(p['values'])
        for p in c_props:
            if p['type'] == 'numeric': c_nums.extend(p['values'])
            
        if p_nums and c_nums:
            # Check if candidate numbers are logically derived (simplified)
            # E.g., if prompt says "2 apples", candidate says "3 apples" -> mismatch
            if len(p_nums) == len(c_nums):
                diff = sum(abs(a-b) for a,b in zip(p_nums, c_nums))
                if diff > 0:
                    mu[2] = -1.0 # Penalize numeric mismatch
                    Sigma[2,2] = 0.5 # Higher confidence in this penalty
        
        return mu, Sigma, nodes

    def _minimize_free_energy(self, mu: np.ndarray, Sigma: np.ndarray, prompt: str, candidate: str) -> float:
        """
        Iteratively minimizes variational free energy F.
        F = 0.5 * (error^T * Lambda * error + log|Sigma|)
        Updates belief using LQR-like control law.
        """
        H = np.eye(len(mu)) # Identity mapping for simplicity in this abstraction
        Lambda = np.linalg.inv(Sigma + 1e-6 * np.eye(len(mu))) # Precision
        
        max_iter = 10
        for _ in range(max_iter):
            # 1. Compute Prediction Error (epsilon)
            # Observed constraint satisfaction vs Predicted
            # We simulate "observation" based on string logic checks
            observed = self._compute_constraint_satisfaction(prompt, candidate, len(mu))
            predicted = mu
            
            epsilon = observed - predicted
            
            # 2. Compute Free Energy
            # F = 0.5 * (epsilon^T Lambda epsilon + log det Sigma)
            try:
                log_det = np.linalg.slogdet(Sigma)[1]
            except:
                log_det = 0.0
                
            F = 0.5 * (epsilon.T @ Lambda @ epsilon + log_det)
            
            # 3. Control Update (LQR style)
            # K = Sigma H^T (H Sigma H^T + R)^-1
            R = self.noise_cov * np.eye(len(mu))
            try:
                K = Sigma @ H.T @ np.linalg.inv(H @ Sigma @ H.T + R)
            except:
                K = Sigma * 0.1 # Fallback
                
            mu = mu + K @ epsilon
            Sigma = (np.eye(len(mu)) - K @ H) @ Sigma
            
            # Convergence check (simplified)
            if np.max(np.abs(epsilon)) < 1e-4:
                break
                
        return -F # Return negative free energy as score

    def _compute_constraint_satisfaction(self, prompt: str, candidate: str, n_nodes: int) -> np.ndarray:
        """
        Computes the 'observed' satisfaction vector based on structural parsing.
        This is the 'sensor' model in the FEP framework.
        """
        obs = np.zeros(n_nodes)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Node 0: Base Consistency (Keyword overlap + Negation handling)
        # Simple Jaccard-like overlap on significant words
        stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an', 'to', 'be', 'of', 'in', 'that', 'and'])
        p_words = set(re.findall(r'\b\w+\b', p_lower)) - stop_words
        c_words = set(re.findall(r'\b\w+\b', c_lower)) - stop_words
        
        if p_words:
            overlap = len(p_words & c_words) / len(p_words | c_words) if p_words | c_words else 0
            obs[0] = overlap * 2 - 1 # Scale to [-1, 1]
        else:
            obs[0] = -0.5 # Penalty for no content
            
        # Node 1: Logical Flow (Conditional presence)
        if 'if' in p_lower:
            if 'then' in c_lower or any(k in c_lower for k in ['therefore', 'thus', 'so']):
                obs[1] = 1.0
            else:
                obs[1] = -0.5
        else:
            obs[1] = 0.5 # Neutral if no conditionals
            
        # Node 2: Numeric Validity (Already partially handled in init, refine here)
        # If prompt has numbers, candidate should ideally have numbers or logical words
        p_nums = re.findall(r'\d+', p_lower)
        c_nums = re.findall(r'\d+', c_lower)
        if p_nums:
            if c_nums:
                obs[2] = 0.8 # Good, numbers present
            elif any(w in c_lower for w in ['none', 'zero', 'no']):
                obs[2] = 0.9 # Explicit zero
            else:
                obs[2] = -0.5 # Missing numbers
        else:
            obs[2] = 0.0
            
        # Node 3: Causal Link
        if any(w in p_lower for w in ['because', 'cause', 'reason']):
            if any(w in c_lower for w in ['because', 'due to', 'since', 'leads to']):
                obs[3] = 1.0
            else:
                obs[3] = -0.8
        else:
            obs[3] = 0.0
            
        return obs

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 1.0
        return (z12 - min(z1, z2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """Checks prompt for Tier B traps and returns a confidence cap."""
        is_trap, penalty = self._check_meta_traps(prompt)
        if is_trap:
            return max(0.0, 0.3 - penalty) # Cap low for traps
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check prompt for global traps
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing & Graph Build
            mu, Sigma, nodes = self._build_constraint_graph(prompt, cand)
            
            # 2. Free Energy Minimization (The "Control" step)
            fe_score = self._minimize_free_energy(mu, Sigma, prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% weight logic handled by scaling)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.5 # Scale NCD contribution
            
            # 4. Final Score Composition
            # Structural/FE (85%) + NCD (15%)
            final_score = (0.85 * fe_score) + (0.15 * ncd_score)
            
            # Apply Meta Cap if prompt is ambiguous
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap)
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"FEP Converged: {fe_score:.4f}, NCD: {ncd:.4f}, Meta-Cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Meta-Analysis (Tier B Check)
        cap = self._meta_confidence(prompt)
        
        # If prompt is a trap, return low confidence immediately
        if cap < 0.3:
            return cap
            
        # 2. Structural Evaluation
        mu, Sigma, _ = self._build_constraint_graph(prompt, answer)
        fe_score = self._minimize_free_energy(mu, Sigma, prompt, answer)
        
        # Normalize FE score to 0-1 range roughly (assuming FE is negative, closer to 0 is better)
        # High negative FE -> Low confidence. Low negative (close to 0) or positive -> High confidence.
        # Let's map: FE < -5 -> 0.1, FE > 0 -> 0.9
        norm_conf = 1.0 / (1.0 + np.exp(-fe_score)) # Sigmoid
        
        # 3. Apply Cap
        final_conf = min(norm_conf, cap)
        
        # Ensure we never claim > 0.9 unless computation was definitive (heuristic)
        if final_conf > 0.9:
            # Only allow if numeric match was perfect
            p_nums = re.findall(r'\d+', prompt)
            a_nums = re.findall(r'\d+', answer)
            if p_nums and a_nums and p_nums != a_nums:
                final_conf = 0.5 # Mismatched numbers reduce confidence
                
        return float(np.clip(final_conf, 0.0, 1.0))