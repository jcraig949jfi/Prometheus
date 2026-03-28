import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining Structural Parsing, Cellular Automata (Rule 110),
    and Information Theory to evaluate logical consistency and epistemic honesty.
    
    Mechanism:
    1. Parses atomic propositions (negations, comparatives, conditionals) into a binary state vector.
    2. Propagates truth values via a Cellular Automata layer (Rule 110) to simulate logical inference.
    3. Scores candidates based on the Mutual Information between the prompt's structural signature
       and the candidate's derived state, penalizing ambiguity and presupposition traps.
    """

    def __init__(self):
        # Rule 110 Lookup Table: Index is binary representation of (left, center, right)
        # 000->0, 001->1, 010->1, 011->1, 100->0, 101->1, 110->1, 111->0
        self.rule110 = np.array([0, 1, 1, 1, 0, 1, 1, 0], dtype=int)
        self.negation_words = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparative_ops = ['>', '<', '>=', '<=', 'more than', 'less than', 'greater', 'smaller']
        self.conditional_words = ['if', 'then', 'when', 'unless']
        self.causal_words = ['because', 'leads to', 'results in', 'causes', 'since']
        self.temporal_words = ['before', 'after', 'first', 'last', 'then']

    def _extract_propositions(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Extract atomic propositions and initialize polarity vector."""
        if not text:
            return [], np.array([], dtype=int)
            
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        propositions = []
        polarities = []
        
        # Simple sliding window for phrase detection
        for i, token in enumerate(tokens):
            # Check Negations
            if token in self.negation_words:
                propositions.append(f"neg_{i}")
                polarities.append(-1)
            # Check Comparatives
            elif token in self.comparative_ops or (i > 0 and tokens[i-1] in ['is', 'are', 'was']):
                 if any(c in token for c in ['>', '<']):
                     propositions.append(f"comp_{i}")
                     polarities.append(1)
            # Check Conditionals
            elif token in self.conditional_words:
                propositions.append(f"cond_{i}")
                polarities.append(1)
            # Check Causal
            elif token in self.causal_words:
                propositions.append(f"cause_{i}")
                polarities.append(1)
            # Check Temporal
            elif token in self.temporal_words:
                propositions.append(f"temp_{i}")
                polarities.append(1)
            # Generic atomic proposition (nouns/verbs roughly)
            elif len(token) > 3 and token not in ['the', 'and', 'that', 'this', 'with', 'from', 'have', 'been']:
                propositions.append(f"atom_{i}_{token}")
                polarities.append(1)

        if len(propositions) == 0:
            return ["empty"], np.array([0])
            
        return propositions, np.array(polarities[:len(propositions)], dtype=int)

    def _build_adjacency(self, n: int) -> np.ndarray:
        """Build a simplified adjacency matrix assuming local connectivity + global implication."""
        if n == 0: return np.zeros((0,0), dtype=int)
        A = np.zeros((n, n), dtype=int)
        for i in range(n):
            A[i, i] = 1 # Self loop
            if i > 0: A[i, i-1] = 1 # Previous implies current
            if i < n-1: A[i, i+1] = 1 # Current implies next
            # Dense connect for small n to ensure propagation
            if n < 10:
                A[i, :] = 1 
        return A

    def _run_ca_inference(self, s0: np.ndarray, steps: int) -> np.ndarray:
        """Run Rule 110 CA for T steps and return frequency distribution."""
        if len(s0) == 0:
            return np.array([0.0])
            
        n = len(s0)
        A = self._build_adjacency(n)
        s_t = (s0 > 0).astype(int) # Initial state: 1 if affirmed, 0 otherwise
        
        # Pad s_t if needed for rule application logic, but here we use vector sum
        history = np.zeros((steps, n), dtype=float)
        
        # Ensure s_t is float for calculation but int for rule lookup
        current_state = s_t.astype(int)
        
        for t in range(steps):
            # Neighborhood sum: Self + Inputs
            # Using matrix mult for neighborhood sum: n_i = sum(A[i,j] * s[j])
            # Note: A is defined such that row i sums inputs TO i? 
            # Standard CA: new[i] depends on neighbors. 
            # Let's interpret A[i,j]=1 as j affects i.
            neighborhood_sum = (A @ current_state).astype(int)
            
            # Apply Rule 110 vectorized
            # We need to map the sum to an index. 
            # Since our "neighborhood" is a sum of bits, it's not standard binary 3-bit.
            # Adaptation: Use sum % 8 as index into rule table, or clamp.
            # To strictly follow "Rule 110" spirit on a graph:
            # We treat the sum as an integer. If sum >= 8, mod 8.
            indices = np.minimum(neighborhood_sum, 7) 
            next_state = self.rule110[indices]
            
            history[t, :] = next_state.astype(float)
            current_state = next_state

        # Empirical distribution (frequency of being true)
        if steps == 0:
            return current_state.astype(float)
        return np.mean(history, axis=0)

    def _calculate_mi_score(self, p_prompt: np.ndarray, p_cand: np.ndarray) -> float:
        """Calculate Mutual Information based score."""
        if len(p_prompt) == 0 or len(p_cand) == 0:
            return 0.0
            
        # Normalize lengths by repeating or truncating to match for comparison
        n = max(len(p_prompt), len(p_cand))
        p_p = np.resize(p_prompt, n)
        p_c = np.resize(p_cand, n)
        
        # Add small epsilon for log stability
        eps = 1e-12
        p_p = p_p + eps
        p_c = p_c + eps
        
        # Normalize to probability distributions
        p_p = p_p / np.sum(p_p)
        p_c = p_c / np.sum(p_c_c := p_c) # Ensure sum to 1
        
        # Entropy H(p) = -sum(p log p)
        H_p = -np.sum(p_p * np.log(p_p))
        H_c = -np.sum(p_c * np.log(p_c))
        
        # Joint approximation (independence assumption for structural alignment)
        # If structures align, their entropy profiles should be similar.
        # We use a similarity metric based on entropy difference as a proxy for MI in this context
        # I(X;Y) = H(X) + H(Y) - H(X,Y). 
        # If independent, H(X,Y) = H(X)+H(Y) -> I=0.
        # If identical, H(X,Y)=H(X)=H(Y) -> I=H(X).
        # Here we approximate alignment by how close the distributions are.
        
        # Alternative: Direct KL divergence or simple correlation of the CA states
        # Let's use the formula from prompt: I = H(p_c) + H(p_r) - H(joint)
        # Joint approx outer product
        joint = np.outer(p_c, p_p)
        joint_flat = joint.flatten()
        joint_flat = joint_flat / (np.sum(joint_flat) + eps)
        H_joint = -np.sum(joint_flat * np.log(joint_flat + eps))
        
        I = H_p + H_c - H_joint
        I_max = max(H_p, H_c)
        
        if I_max == 0: return 0.5
        
        # Score: exp(-abs(I - I_max)) -> 1 if I == I_max (perfect alignment), 0 if far
        score = np.exp(-abs(I - I_max))
        return float(score)

    def _numeric_evaluation(self, text: str) -> float:
        """Extract and evaluate numeric comparisons if present."""
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        if len(numbers) < 2:
            return 0.5 # No numeric data to evaluate
        
        try:
            vals = [float(n) for n in numbers]
            # Check for monotonicity or specific patterns implied by prompt
            # Simple heuristic: if numbers are sorted, implies order consistency
            if all(vals[i] <= vals[i+1] for i in range(len(vals)-1)):
                return 0.8
            return 0.5
        except:
            return 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "why did", "why does", "when did", "quit ", "stopped "]
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                return 0.2 # High risk of trap

        # 2. Scope/Pronoun Ambiguity
        if re.search(r"\b(every|all|each)\b.*\b(a|an|the)\b", p_lower) and "same" in p_lower:
            return 0.4
        if re.search(r"\b(told|said|asked)\b.*\bhe|she|him|her\b", p_lower) and "who" in p_lower:
            return 0.3

        # 3. False Dichotomy
        if re.search(r"\beither\b.*\bor\b", p_lower) and "only" in p_lower:
            return 0.4
            
        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "opinion"]
        if any(w in p_lower for w in subjective_words) and "measure" not in p_lower:
            return 0.5

        # 5. Unanswerability (Missing info)
        if "cannot be determined" in p_lower or "insufficient" in p_lower:
            return 0.9 # The prompt itself acknowledges limits
            
        return 1.0 # No obvious traps detected

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0: return 1.0
        return (c12 - min_len) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Parse Prompt Structure
        props_p, pol_p = self._extract_propositions(prompt)
        n_steps = max(4, int(np.ceil(np.log2(len(props_p) + 1)))) if props_p else 4
        
        # Run CA on prompt to get reference distribution
        if len(pol_p) > 0:
            dist_p = self._run_ca_inference(pol_p, n_steps)
        else:
            dist_p = np.array([0.5]) # Neutral baseline

        results = []
        meta_cap = self._meta_confidence(prompt)
        prompt_numeric = self._numeric_evaluation(prompt)

        for cand in candidates:
            # Structural Parsing & CA for Candidate
            props_c, pol_c = self._extract_propositions(cand)
            if len(pol_c) > 0:
                dist_c = self._run_ca_inference(pol_c, n_steps)
            else:
                dist_c = np.array([0.5])
            
            # Information Theoretic Score
            mi_score = self._calculate_mi_score(dist_p, dist_c)
            
            # Numeric Consistency
            cand_numeric = self._numeric_evaluation(cand)
            numeric_bonus = 0.1 if abs(cand_numeric - prompt_numeric) < 0.1 else -0.1
            
            # NCD Tiebreaker (Max 15% weight)
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Final Score Composition
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            final_score = (mi_score * 0.6) + (numeric_bonus * 0.25) + ncd_score
            
            # Apply Epistemic Cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural alignment: {mi_score:.2f}. Meta-cap: {meta_cap:.2f}."
            if meta_cap < 0.5:
                reasoning += " Potential ambiguity/trap detected."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at meta-confidence if traps are detected.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        props_p, pol_p = self._extract_propositions(prompt)
        props_a, pol_a = self._extract_propositions(answer)
        
        # If no structure found in either, low confidence
        if len(pol_p) == 0 and len(pol_a) == 0:
            return min(0.3, meta_cap)
            
        # Run lightweight evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]["score"]
        
        # Cap by meta confidence
        final_conf = min(raw_score, meta_cap)
        
        # Never > 0.9 unless computation was definitive (simulated by high numeric match)
        if "numeric" in prompt.lower() and self._numeric_evaluation(answer) > 0.7:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.9)
            
        return float(np.clip(final_conf, 0.0, 1.0))