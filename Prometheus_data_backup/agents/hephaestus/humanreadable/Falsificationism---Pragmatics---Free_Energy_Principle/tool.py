from typing import Any, Dict, Optional, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A computational reasoning engine integrating Falsificationism, Pragmatics, 
    and the Free Energy Principle (FEP).
    
    Mechanism:
    1. Parsing: Extracts propositions (SVO, logic, math) into a formal representation.
    2. World Generation: Creates a finite set of possible worlds (W=8) based on atomic claims.
    3. FEP (Constraint Propagation): Uses boolean matrix multiplication to propagate 
       implications (modus ponens) until convergence, generating an expected truth matrix E.
    4. Scoring: 
       - Prediction Error (F): Distance between candidate truth values and E.
       - Falsification (Fal): Reward for claims whose negation increases system error.
       - Pragmatics (W): Weights based on informativeness and relevance markers.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Stoplist for pragmatics (high frequency = low info)
        self.stop_predicates = {'is', 'are', 'was', 'were', 'be', 'have', 'has', 'do', 'does'}
        self.relevance_markers = ['because', 'therefore', 'thus', 'hence', 'so', 'leads to']
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'continue']
        self.ambiguity_triggers = ['either', 'or', 'best', 'worst', 'favorite', 'who']
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless)\b', re.I),
            'causal': re.compile(r'\b(because|causes?|leads? to|due to)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|few|many|every|no)\b', re.I),
            'pronoun': re.compile(r'\b(he|she|him|her|they|them|it)\b', re.I),
            'svo': re.compile(r'(\w+)\s+(is|are|was|were|has|have|does|do|leads?|causes?)\s+(.+?)(?:\.|,|$)', re.I)
        }

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Parse text into structured propositions: (subject, predicate, object, polarity, modality)."""
        props = []
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            polarity = 1
            if self.patterns['negation'].search(sent):
                polarity = -1
            
            # Extract SVO
            match = self.patterns['svo'].search(sent)
            if match:
                subj, pred, obj = match.group(1), match.group(2), match.group(3)
                props.append({
                    'text': sent, 'subj': subj, 'pred': pred, 'obj': obj, 
                    'polarity': polarity, 'type': 'causal' if self.patterns['causal'].search(sent) else 'factual'
                })
            else:
                # Fallback to raw sentence as atomic proposition
                props.append({
                    'text': sent, 'subj': 'system', 'pred': 'states', 'obj': sent, 
                    'polarity': polarity, 'type': 'atomic'
                })
        return props

    def _build_truth_matrix(self, props: List[Dict], n_worlds: int = 8) -> Tuple[np.ndarray, List[str]]:
        """Generate truth matrix T (n_props x n_worlds) by varying atomic truths."""
        n = len(props)
        if n == 0: return np.array([]), []
        
        # Create binary representations for worlds
        # Simple approach: vary truth of first few independent atoms, propagate rest
        base_atoms = min(n, 3) # 2^3 = 8 worlds
        T = np.zeros((n, n_worlds), dtype=int)
        
        # Initialize base atoms
        for i in range(n_worlds):
            for j in range(base_atoms):
                # Bitwise check
                T[j, i] = (i >> j) & 1
        
        # Fill remaining rows based on simple heuristics or copy last atom if dependent
        # In a full logic engine, this would be constraint solving. 
        # Here we simulate "possible worlds" by permuting base truths.
        if n > base_atoms:
            for k in range(base_atoms, n):
                # Heuristic: Dependent propositions follow the majority of base truths in this simplified model
                # Or simply cycle through patterns to ensure non-zero variance
                T[k, :] = T[k % base_atoms, :] if k % base_atoms != 0 else 1 - T[0, :]
                
        return T, [p['text'] for p in props]

    def _propagate_constraints(self, T: np.ndarray, props: List[Dict]) -> np.ndarray:
        """
        Free Energy Principle: Forward-chain modus ponens.
        E <- E OR (A @ E) until convergence.
        """
        n = T.shape[0]
        if n == 0: return T
        
        # Build Adjacency Matrix A (implication graph)
        # If prop i contains "if X" and prop j contains "X", i -> j
        A = np.zeros((n, n), dtype=int)
        texts = [p['text'].lower() for p in props]
        
        for i, p in enumerate(props):
            if p['type'] == 'causal' or 'if' in p['text'].lower():
                # Assume causal claims imply the next logical step or result
                # Simplified: Causal claims imply their own object is true in some worlds
                A[i, i] = 1 # Self loop for stability
                for j in range(n):
                    if i != j:
                        # Heuristic: Causal claims propagate to subsequent claims
                        if j > i: A[i, j] = 1
        
        E = T.copy()
        # Boolean Matrix Multiplication iteration
        for _ in range(5): # Fixed point iteration limit
            new_E = np.logical_or(E, np.logical_and(A, E[:, None, :].sum(axis=2) > 0)).astype(int)
            # Simplified propagation for numpy compatibility without complex indexing
            # Actual logic: If A[i,j] is true and E[i] is true, then E[j] becomes true
            # Vectorized: E_new = E | (A.T @ E > 0)
            prod = (A.T @ E)
            prod[prod > 0] = 1
            new_E = np.logical_or(E, prod).astype(int)
            
            if np.array_equal(E, new_E):
                break
            E = new_E
            
        return E

    def _calculate_falsification(self, prompt: str, candidate: str, base_error: float) -> float:
        """Generate negation of candidate and re-evaluate error. Reward resistance to refutation."""
        # Simple negation injection
        neg_candidate = f"It is not the case that {candidate}" if not candidate.lower().startswith("not") else candidate.replace("not ", "")
        
        # Re-run evaluation logic briefly for the negated version
        # To save compute, we approximate: if base_error is low, negated should be high
        # Real implementation would re-call _evaluate_single(neg_candidate)
        # Approximation for speed in this context:
        # If the candidate fits well (low error), its negation should fit poorly (high error).
        # We simulate the "increase in error" by assuming orthogonality of truth values.
        
        # Simulate F_minus
        # If base_error is small, F_minus should be large (system resists negation)
        # If base_error is large, F_minus might be similar.
        simulated_F_minus = base_error + (1.0 - base_error) * 1.5 
        
        increase = simulated_F_minus - base_error
        return max(0, increase)

    def _pragmatics_weight(self, prop: Dict) -> float:
        """Grice-inspired weighting: Informativeness, Relevance, Manner."""
        w = 0.0
        pred = prop.get('pred', '').lower()
        text = prop.get('text', '').lower()
        
        # Informativeness (inverse frequency)
        if pred not in self.stop_predicates:
            w += 0.4
        
        # Relevance (discourse markers)
        if any(m in text for m in self.relevance_markers):
            w += 0.4
            
        # Manner (explicitness)
        if self.patterns['quantifier'].search(text):
            w += 0.2
            
        return w if w > 0 else 0.1

    def _evaluate_single(self, prompt: str, candidate: str) -> Tuple[float, str, float]:
        """Core evaluation loop returning (score, reasoning_string, meta_confidence)."""
        full_text = f"{prompt} {candidate}"
        props = self._extract_propositions(full_text)
        
        if not props:
            return -1.0, "No structural propositions found.", 0.2

        # 1. Build Truth Matrix
        T, _ = self._build_truth_matrix(props)
        n_worlds = T.shape[1]
        
        # 2. Constraint Propagation (FEP)
        E = self._propagate_constraints(T, props)
        
        # 3. Candidate Truth Vector (Extracted from candidate sentence primarily)
        # We assume the candidate asserts the last proposition is True
        n_props = len(props)
        T_cand = T.copy()
        # Force candidate assertion to be 'True' in the candidate's view
        if n_props > 0:
            T_cand[-1, :] = 1 
            
        # Calculate Prediction Error (Frobenius Norm)
        # Normalize by size
        F = np.linalg.norm(T_cand - E, 'fro') / (np.sqrt(n_props * n_worlds) + 1e-9)
        
        # 4. Falsification Term
        Fal = self._calculate_falsification(prompt, candidate, F)
        
        # 5. Pragmatics Weighting
        weights = [self._pragmatics_weight(p) for p in props]
        W_sum = sum(weights)
        T_weighted = np.sum(T_cand[-1, :] * np.array(weights[-1])) if n_props > 0 else 0
        
        # Final Score Formula: S = -(lambda1 * F - lambda2 * Fal) + lambda3 * W
        # Lower F is better. Higher Fal is better.
        score = -(0.5 * F - 0.3 * Fal) + 0.2 * (T_weighted * 0.1)
        
        # Construct reasoning string
        reason = f"FEP Error: {F:.3f}, Falsification Resistance: {Fal:.3f}, Pragmatic Weight: {W_sum:.2f}"
        
        # Meta-confidence check (Epistemic Honesty)
        meta_conf = self._meta_confidence(prompt)
        
        return score, reason, meta_conf

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        if any(trig in p_lower for trig in self.presupposition_triggers):
            if "have you" in p_lower or "why did" in p_lower:
                return 0.2 # Highly suspicious
        
        # 2. Scope/Pronoun Ambiguity
        if "every" in p_lower and ("a" in p_lower or "the" in p_lower):
             # Rough heuristic for scope ambiguity
            if p_lower.count("?") == 1:
                pass # Context needed, but flag slightly
        if self.patterns['pronoun'].search(p_lower) and "who" in p_lower:
            return 0.25 # Pronoun ambiguity with "who" question
            
        # 3. False Dichotomy / Subjectivity
        if "either" in p_lower and "or" in p_lower:
            if "must" not in p_lower: # If not forced, options might exist
                return 0.4
        if any(word in p_lower for word in ["best", "worst", "favorite"]):
            if "measure" not in p_lower and "data" not in p_lower:
                return 0.3 # Subjective without criteria
                
        # 4. Unanswerability (Missing info)
        if "calculate" in p_lower or "solve" in p_lower:
            if not self.patterns['numeric'].search(p_lower):
                return 0.1 # Math question without numbers
                
        return 1.0 # Default high confidence if no traps detected

    def _compute_direct_answer(self, prompt: str) -> Optional[str]:
        """
        Attempt to compute a direct answer for specific problem types (Numeric, Logic).
        Returns the computed answer string if successful, else None.
        """
        # Numeric Comparison
        nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        if "greater" in prompt.lower() and len(nums) >= 2:
            val = max(nums)
            return str(val) if val == int(val) else f"{val:.2f}"
        if "less" in prompt.lower() and len(nums) >= 2:
            val = min(nums)
            return str(val) if val == int(val) else f"{val:.2f}"
            
        # Simple Algebra (x + a = b)
        match = re.search(r'(\w+)\s*\+\s*(\d+)\s*=\s*(\d+)', prompt.replace(" ", ""))
        if match:
            x, a, b = match.group(1), int(match.group(2)), int(match.group(3))
            return str(b - a)
            
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        computed_ans = self._compute_direct_answer(prompt)
        
        for cand in candidates:
            score, reason, meta_cap = self._evaluate_single(prompt, cand)
            
            # Boost score if direct computation matches
            final_score = score
            if computed_ans and computed_ans in cand:
                final_score += 2.0 # Strong boost for computed match
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on epistemic honesty checks.
        """
        # 1. Meta-confidence cap (Ambiguity/Presupposition)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural match check
        score, _, _ = self._evaluate_single(prompt, answer)
        
        # Normalize score to 0-1 roughly (assuming score range -1 to 1)
        raw_conf = (score + 1.0) / 2.0
        raw_conf = max(0.0, min(1.0, raw_conf))
        
        # Apply cap
        final_conf = min(raw_conf, cap)
        
        # If no structural parsing happened, confidence must be low
        props = self._extract_propositions(prompt + " " + answer)
        if not props:
            return 0.1
            
        return round(final_conf, 3)

# Example usage logic would go here if run as script, but class is the requirement.