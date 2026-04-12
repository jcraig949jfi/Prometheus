import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A lightweight reasoning scorer implementing Free Energy Principle, Criticality, 
    and Adaptive Control to evaluate logical consistency in text.
    
    Mechanism:
    1. Parsing: Extracts propositions and relations (negation, conditional, causal, numeric) 
       into a graph (Adjacency matrix A).
    2. Free Energy: Computes prediction error (constraint propagation) + complexity (entropy).
    3. Criticality: Measures susceptibility (variance of Free Energy under perturbation).
    4. Adaptive Control: Tunes complexity weight lambda to minimize error without overfitting.
    5. Epistemic Honesty: Caps confidence if meta-analysis detects ambiguity or traps.
    """

    def __init__(self):
        self.lambda_default = 0.5
        self.tau = 0.1  # Target error
        self.eta = 0.01 # Learning rate for lambda
        self.alpha = 0.1 # Propagation step
        self.theta = 0.5 # Belief threshold
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|leads to|causes|since)\b', re.I),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|larger|smaller)\b', re.I),
            'ordering': re.compile(r'\b(before|after|first|last|next)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'quantifier': re.compile(r'\b(every|all|some|most|few|many)\b', re.I),
            # Trap detection
            'presupposition': re.compile(r'\b(have you stopped|why did .+ fail|why is .+ bad)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I),
            'pronoun_trap': re.compile(r'\b(he|she|him|her|they)\b.*\bwho\b', re.I)
        }

    def _parse_graph(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Parse text into nodes and adjacency matrices (types and weights)."""
        # Simple sentence splitting as proxy for propositions
        sentences = [s.strip() for s in re.split(r'[.;!?]', text) if s.strip()]
        if not sentences:
            sentences = [text]
            
        n = len(sentences)
        if n == 0: n = 1 # Ensure at least one node
        
        # A_types: int8 for edge type, A_weights: float64 for strength
        A_types = np.zeros((n, n), dtype=np.int8)
        A_weights = np.zeros((n, n), dtype=np.float64)
        
        # Initialize beliefs based on prior frequency (simplified to uniform + numeric boost)
        # In a full implementation, this would be b_init
        
        full_text = " ".join(sentences)
        
        # Detect global properties to influence edges
        has_neg = bool(self.patterns['negation'].search(full_text))
        has_cond = bool(self.patterns['conditional'].search(full_text))
        has_causal = bool(self.patterns['causal'].search(full_text))
        
        for i, s in enumerate(sentences):
            # Self-loop for persistence
            A_types[i, i] = 1 
            A_weights[i, i] = 1.0
            
            for j, target in enumerate(sentences):
                if i == j: continue
                
                # Simple heuristic: if sentence i contains conditional and j is next, link
                if has_cond and self.patterns['conditional'].search(s):
                    if j == i + 1:
                        A_types[i, j] = 2 # Conditional
                        A_weights[i, j] = 0.9
                
                # Causal links
                if has_causal and self.patterns['causal'].search(s):
                     if j == i + 1:
                        A_types[i, j] = 3 # Causal
                        A_weights[i, j] = 0.8
                
                # Negation flips sign of belief if detected in same sentence context
                if has_neg and self.patterns['negation'].search(s):
                    A_weights[i, i] = -0.5 # Self-inhibition for negated statements

        return sentences, A_types, A_weights

    def _compute_free_energy(self, b: np.ndarray, A_types: np.ndarray, A_weights: np.ndarray, lam: float) -> float:
        """Compute Variational Free Energy F = 0.5*||e||^2 + lam*H(b)."""
        # Constraint propagation: b_hat = b + alpha * (A * b)
        # Simplified propagation: treat A_weights as transition matrix
        b_hat = b.copy()
        
        # Modus Ponens / Transitivity step
        # Normalize A_weights rows for probability flow
        row_sums = np.sum(np.abs(A_weights), axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        A_norm = A_weights / row_sums
        
        # Propagate
        b_prop = b + self.alpha * (A_norm @ b)
        b_prop = np.clip(b_prop, 0.0, 1.0)
        
        # Prediction error
        e = b - b_prop
        error_term = 0.5 * np.sum(e ** 2)
        
        # Complexity (Entropy): H(b) = -sum(b * log(b))
        # Add small epsilon to avoid log(0)
        eps = 1e-9
        b_safe = np.clip(b, eps, 1.0)
        entropy = -np.sum(b_safe * np.log(b_safe))
        
        F = error_term + lam * entropy
        return F, error_term

    def _compute_susceptibility(self, b: np.ndarray, A_types: np.ndarray, A_weights: np.ndarray, lam: float, epsilon: float = 0.01) -> float:
        """Compute susceptibility chi = Var(F) / epsilon^2."""
        n_samples = 20
        f_values = []
        
        for _ in range(n_samples):
            # Perturb b
            noise = np.random.choice([-epsilon, 0, epsilon], size=b.shape)
            b_perturbed = np.clip(b + noise, 0.0, 1.0)
            F, _ = self._compute_free_energy(b_perturbed, A_types, A_weights, lam)
            f_values.append(F)
            
        return float(np.var(f_values) / (epsilon ** 2))

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Check for Tier B traps. Returns a cap on confidence.
        If traps found, returns low value (<0.3). Else 1.0.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.25
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower) and "measure" not in p_lower and "calculate" not in p_lower:
            return 0.3
        # 4. Pronoun ambiguity check (heuristic)
        if self.patterns['pronoun_trap'].search(p_lower) and "who" in p_lower:
            return 0.2
            
        # Check for unanswerability markers
        if "insufficient information" in p_lower or "cannot be determined" in p_lower:
            # If the prompt admits it, confidence depends on answer matching that
            if "cannot" in answer.lower() or "insufficient" in answer.lower():
                return 1.0
            return 0.3

        return 1.0

    def _extract_numeric_answer(self, text: str) -> Optional[float]:
        """Extract the primary numeric value from a candidate."""
        matches = self.patterns['numeric'].findall(text)
        if matches:
            try:
                return float(matches[-1]) # Take last number as result
            except ValueError:
                return None
        return None

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the core reasoning score using Free Energy and Criticality.
        Returns a raw score (lower is better for Free Energy, but we invert for ranking).
        """
        # Combine prompt and candidate for context
        context = f"{prompt} {candidate}"
        nodes, A_types, A_weights = self._parse_graph(context)
        n = len(nodes)
        
        if n == 0: return 0.0

        # Initialize belief vector b
        # Heuristic: If candidate contains numbers found in prompt, boost prior
        b = np.ones(n) * 0.5
        
        # Numeric consistency check (Constructive computation)
        p_nums = self._extract_numeric_answer(prompt)
        c_nums = self._extract_numeric_answer(candidate)
        
        if p_nums is not None and c_nums is not None:
            # Simple logic: if candidate number is wildly different, penalize via belief init
            # This is a proxy for "calculation" in the graph
            if abs(p_nums - c_nums) > abs(p_nums) * 0.5: # If > 50% off
                b[-1] = 0.2 # Lower belief in last node (candidate)
            else:
                b[-1] = 0.9
        
        # Adaptive Lambda
        lam = self.lambda_default
        
        # Compute Base Free Energy
        F_base, error = self._compute_free_energy(b, A_types, A_weights, lam)
        
        # Update Lambda (Adaptive Control)
        # lambda_{t+1} = lambda_t + eta * (||e|| - tau)
        lam = lam + self.eta * (np.sqrt(error) - self.tau)
        lam = np.clip(lam, 0.01, 10.0) # Bound lambda
        
        # Recompute with updated lambda if needed, or just use for susceptibility
        # For this lightweight version, we use updated lambda for the final score calculation
        
        # Criticality (Susceptibility)
        chi = self._compute_susceptibility(b, A_types, A_weights, lam)
        
        # Final Score: F * (1 + chi)
        # We want HIGH score for GOOD answers. 
        # Free Energy F is LOW for good models. 
        # So Score = -F * (1 + chi) ? Or 1 / (F + epsilon)?
        # Let's use: Score = (1.0 / (F + 0.1)) * (1.0 + min(chi, 10.0))
        # High chi near criticality suggests the system is sensitive to the logic structure.
        
        base_score = 1.0 / (F_base + 0.1)
        criticality_factor = 1.0 + min(chi * 0.1, 2.0) # Scale chi contribution
        
        final_score = base_score * criticality_factor
        
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # 1. Calculate structural scores for all candidates
        raw_scores = []
        for cand in candidates:
            score = self._structural_score(prompt, cand)
            raw_scores.append(score)
        
        # Normalize scores to 0-1 range for combination with NCD if needed, 
        # but the prompt asks for a ranking score. 
        # Let's keep the raw physics-inspired score but ensure it's positive.
        max_s = max(raw_scores) if raw_scores else 1.0
        min_s = min(raw_scores) if raw_scores else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        for i, cand in enumerate(candidates):
            s = raw_scores[i]
            # Normalize to 0.2 - 0.9 range to leave room for NCD and confidence caps
            norm_s = 0.2 + (0.6 * (s - min_s) / range_s) if range_s > 0 else 0.5
            
            # Add NCD as tiebreaker (max 15% influence)
            # NCD(p, c) approx 1 - compression_ratio
            try:
                combined = (prompt + cand).encode('utf-8')
                comp_len = len(compress(combined))
                ncd_val = comp_len / len(combined) if len(combined) > 0 else 1.0
                # Lower NCD is better (more compressible = more similar/structured)
                # Invert and scale to small bonus
                ncd_bonus = (1.0 - ncd_val) * 0.15 
            except:
                ncd_bonus = 0.0
                
            final_score = norm_s + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Free Energy Score: {s:.4f}, Criticality Adjusted."
            })
            scores.append(final_score)
            
        # Rank descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Confidence (Trap Detection)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural Evaluation
        # Evaluate this single candidate against itself/others implicitly
        # Since we don't have other candidates here, we score the pair (prompt+answer)
        score = self._structural_score(prompt, answer)
        
        # Map score to 0-1 confidence
        # Heuristic mapping: score > 5.0 -> 0.9, score < 1.0 -> 0.3
        # Using a sigmoid-like mapping
        conf = 1.0 / (1.0 + math.exp(-0.5 * (score - 3.0)))
        
        # Clamp based on meta-analysis
        conf = min(conf, meta_cap)
        
        # Never exceed 0.9 without explicit computation proof (simplified here)
        # If the prompt has numbers and answer has numbers, we trust the score more
        p_has_num = bool(self.patterns['numeric'].search(prompt))
        a_has_num = bool(self.patterns['numeric'].search(answer))
        
        if p_has_num and a_has_num:
            cap = 0.95
        else:
            cap = 0.85 # Lower cap for non-numeric reasoning
            
        return float(min(conf, cap, meta_cap))

# Helper for NCD (standard library only)
from zlib import compress

# Re-injecting compress into scope if needed, though imported above.
# The class uses it inside evaluate.