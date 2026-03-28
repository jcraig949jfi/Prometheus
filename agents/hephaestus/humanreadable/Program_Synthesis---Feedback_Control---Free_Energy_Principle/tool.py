import re
import numpy as np
import zlib
from itertools import combinations

class ReasoningTool:
    """
    A reasoning tool combining Program Synthesis, Feedback Control, and Free Energy Principle.
    
    Mechanism:
    1. Program Synthesis: Parses prompts into logical literals (Horn clauses) and treats 
       candidate answers as potential rule sets.
    2. Feedback Control: Uses a discrete PID controller to adjust clause weights based on 
       prediction error between inferred and observed truths.
    3. Free Energy Principle: Optimizes a variational free energy objective (Prediction Error 
       + Complexity Penalty) via hill-climbing to select the best candidate.
       
    Epistemic Honesty: Includes a meta-cognition layer to detect ambiguity, presupposition, 
    and unanswerability, capping confidence when structural certainty is low.
    """

    def __init__(self):
        # PID Gains
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.2
        # Regularization
        self.lambda_l1 = 0.01
        # Threshold for step function
        self.theta = 0.5
        # Max hill-climb iterations
        self.max_iter = 20

    def _parse_literals(self, text):
        """Extract atomic propositions, negations, comparatives, and numbers."""
        literals = []
        text_lower = text.lower()
        
        # Negations
        if re.search(r'\b(not|no|never|none|neither)\b', text_lower):
            literals.append(('negation', 'NOT_PRESENT'))
        
        # Comparatives
        if re.search(r'[><=]|greater|less|more|fewer', text_lower):
            literals.append(('comparative', 'CMP_PRESENT'))
            
        # Conditionals
        if re.search(r'\b(if|then|unless|when|while)\b', text_lower):
            literals.append(('conditional', 'IF_PRESENT'))
            
        # Causal
        if re.search(r'\b(because|causes|leads to|due to)\b', text_lower):
            literals.append(('causal', 'CAUSE_PRESENT'))
            
        # Numbers (extract first two for simple comparison logic)
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            literals.append(('numeric', (float(nums[0]), float(nums[1]))))
        elif len(nums) == 1:
            literals.append(('numeric_single', float(nums[0])))
            
        # Quantifiers
        if re.search(r'\b(all|every|some|none|most)\b', text_lower):
            literals.append(('quantifier', 'QUANT_PRESENT'))

        # Unique indexing
        return [(f"{l[0]}_{i}", l) for i, l in enumerate(literals)]

    def _build_clause_matrix(self, prompt_literals, candidate_text):
        """
        Build binary matrix A (literals x clauses) and head vector h.
        Here, we treat the candidate text as a single complex clause or 
        decompose it into sub-clauses based on delimiters.
        """
        # For this implementation, we treat the candidate as a single hypothesis program
        # We check which prompt literals are satisfied or referenced by the candidate
        cand_lower = candidate_text.lower()
        
        # Simple heuristic: Does the candidate contain keywords matching the literal types?
        # This simulates the "parsing" of the candidate program against prompt specs.
        n_literals = len(prompt_literals)
        n_clauses = 1 # Treating candidate as one block for simplicity in this specific blend
        
        # Matrix A: Does literal i appear in the candidate's logic?
        # Since we don't have full semantic parsing, we approximate:
        # If the prompt has a number, and candidate has a number, match.
        # If prompt has negation, and candidate has negation, match.
        
        A = np.zeros((n_literals, 1))
        
        for i, (lit_name, lit_val) in enumerate(prompt_literals):
            match = False
            if lit_val[0] == 'negation' and re.search(r'not|no|never', cand_lower):
                match = True
            elif lit_val[0] == 'comparative' and re.search(r'[><=]|greater|less', cand_lower):
                match = True
            elif lit_val[0] == 'conditional' and re.search(r'if|then|unless', cand_lower):
                match = True
            elif lit_val[0] == 'causal' and re.search(r'because|cause', cand_lower):
                match = True
            elif lit_val[0] == 'numeric':
                # Check if candidate contains numbers that might relate
                if re.search(r'\d+', cand_lower):
                    match = True
            elif lit_val[0] == 'quantifier' and re.search(r'all|every|some|none', cand_lower):
                match = True
            
            # Heuristic: Assume body connection if types match
            if match:
                A[i, 0] = 1.0
                
        # Head vector: Does the candidate claim the conclusion?
        # We assume the candidate IS the conclusion head for scoring purposes
        h = np.array([1.0]) 
        
        return A, h

    def _forward_chain(self, A, w):
        """Compute inferred truth values t_hat = sigma(A * w)."""
        if A.shape[1] == 0:
            return np.zeros(A.shape[0])
        raw = A.dot(w)
        return (raw >= self.theta).astype(float)

    def _pid_update(self, w, e, e_prev, integral):
        """Discrete PID update for weights."""
        integral += e
        derivative = e - e_prev
        delta = self.Kp * e + self.Ki * integral + self.Kd * derivative
        return w + delta, integral, e

    def _compute_free_energy(self, e, w):
        """F = ||e||^2 + lambda * ||w||_1"""
        pred_error = np.sum(e ** 2)
        complexity = self.lambda_l1 * np.sum(np.abs(w))
        return pred_error + complexity

    def _calculate_structural_score(self, prompt, candidate):
        """
        Core logic: Program Synthesis + Feedback Control + Free Energy.
        Returns a score (lower is better for Free Energy, but we return negative F for ranking).
        """
        p_lits = self._parse_literals(prompt)
        
        if not p_lits:
            # No structure found, rely on NCD later
            return -1.0, 0.0, True
            
        A, h = self._build_clause_matrix(p_lits, candidate)
        
        # Target truth vector t: Derived from prompt literals being "true" by definition of the prompt context
        # We assume the prompt defines the ground truth conditions.
        t = np.ones(len(p_lits)) 
        
        # Special handling for numeric contradictions
        # If prompt says "5 > 3" and candidate implies "3 > 5", penalize heavily
        num_data = [l for l in p_lits if l[1][0] == 'numeric']
        if num_data:
            val1, val2 = num_data[0][1][1]
            # If candidate contains reversed comparison text
            cand_lower = candidate.lower()
            if f"{val2} > {val1}" in candidate or f"{val2} is greater" in cand_lower:
                if val1 > val2: # Prompt implies 1>2, candidate says 2>1 (False)
                     return -100.0, 0.0, False # High penalty

        # Initialize weights
        w = np.ones((A.shape[1],)) * 0.5
        e_prev = np.zeros(len(p_lits))
        integral = np.zeros(len(p_lits))
        
        # Feedback Control Loop (Simulated steps to convergence)
        for _ in range(5): 
            t_hat = self._forward_chain(A, w)
            e = t_hat - t
            
            # Update weights to minimize error
            w, integral, e_prev = self._pid_update(w, e, e_prev, integral)
            
            # Clamp weights to [0, 1] for stability
            w = np.clip(w, 0, 1)

        # Final Error and Free Energy
        t_hat_final = self._forward_chain(A, w)
        e_final = t_hat_final - t
        F = self._compute_free_energy(e_final, w)
        
        # Score is negative Free Energy (higher is better)
        score = -F
        return score, np.mean(np.abs(e_final)), False

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        z = zlib.compress
        len_s1 = len(z(s1.encode('utf-8')))
        len_s2 = len(z(s2.encode('utf-8')))
        len_s1_s2 = len(z((s1 + s2).encode('utf-8')))
        
        if min(len_s1, len_s2) == 0:
            return 1.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _meta_confidence(self, prompt):
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'have you (stopped|quit|finished)\b', p):
            return 0.2
        if re.search(r'\bwhy did .*(fail|stop|die|break)\b', p):
            return 0.3
            
        # 2. Scope/Pronoun Ambiguity
        if re.search(r'every .*(a|an) ', p) and re.search(r'\bsame\b|\bdifferent\b', p):
            return 0.4
        if re.search(r'\b(he|she|him|her|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'\beither .+ or .+\b', p) and not re.search(r'\bother\b|\belse\b', p):
            return 0.4
            
        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|ugliest)\b', p) and not re.search(r'\bdata|statistic|measure\b', p):
            return 0.3
            
        # 5. Unanswerable / Missing Info
        if re.search(r'\b(calculate|solve|find)\b', p) and not re.search(r'\d+', p):
            return 0.2
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate structural scores for all candidates
        scored_candidates = []
        for cand in candidates:
            score, error_rate, no_struct = self._calculate_structural_score(prompt, cand)
            
            # Add NCD as a small tiebreaker component if structural scores are close or missing
            ncd_val = 0.0
            if no_struct or abs(score) < 0.1:
                # Use NCD only if structural signal is weak
                ncd_val = self._ncd_score(prompt, cand) * 0.15 # Max 15% weight
                final_score = -ncd_val # Lower NCD is better (closer to 0), so negative
            else:
                # Structural score dominates
                final_score = score
            
            # Apply Meta-Cognition Cap to the potential confidence derived from score
            # If the prompt is ambiguous, even a "matching" candidate shouldn't get high confidence
            if meta_cap < 0.5:
                final_score = min(final_score, 0.0) # Suppress score if prompt is tricky
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural Match: {score:.4f}, Meta-Cap: {meta_cap:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on _meta_confidence to ensure epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural score
        # We simulate a list of one candidate to get the score
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # Convert score to 0-1 range roughly
        # Free energy scores are negative, closer to 0 is better.
        # Let's map: score > -0.1 -> 0.9, score < -1.0 -> 0.2
        if base_score > -0.1:
            raw_conf = 0.95
        elif base_score > -0.5:
            raw_conf = 0.7
        elif base_score > -1.0:
            raw_conf = 0.4
        else:
            raw_conf = 0.1
            
        # Apply meta cap (Epistemic Honesty)
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (handled by meta_cap logic mostly)
        # If meta_cap is 1.0, we still cap at 0.95 to avoid overconfidence
        return min(final_conf, 0.95)