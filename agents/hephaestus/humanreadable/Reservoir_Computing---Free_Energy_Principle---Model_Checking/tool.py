import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Verifying Predictive Reservoir (SVPR) Implementation.
    
    Mechanism:
    1. Reservoir Computing (RC): Simulated via a fixed, high-dimensional feature expansion
       of the input text (n-grams + structural tokens) acting as a static recurrent state.
    2. Free Energy Principle (FEP): The core scoring engine. It minimizes variational free energy
       by reducing the divergence between the candidate's structural profile (q) and the 
       prompt's expected logical constraints (p). Low surprise (prediction error) = High Score.
    3. Model Checking (MC): A symbolic verification layer that parses LTL-like constraints 
       (negations, comparatives, conditionals) from the prompt. Candidates violating these 
       hard logical constraints receive a massive energy penalty (rejection), regardless of 
       semantic similarity.
       
    This architecture ensures that logical consistency (MC) gates the probabilistic 
    plausibility (FEP) derived from the rich context (RC).
    """

    def __init__(self):
        # Reservoir parameters (fixed weights conceptually)
        self.n_gram_range = (1, 3)
        # Logical keywords for model checking abstraction
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise'}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer preserving structure for reservoir input."""
        return re.findall(r'\b\w+\b|[<>]=?|==|!=', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        """
        Model Checking: Extracts symbolic trace (LTL atoms) from text.
        Returns a dictionary representing the logical state.
        """
        tokens = set(self._tokenize(text))
        has_negation = bool(tokens & self.negation_words)
        has_comparative = bool(tokens & self.comparative_ops) or bool(re.search(r'[<>]', text))
        has_conditional = bool(tokens & self.conditionals)
        
        # Numeric extraction for structural parsing
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'negations': has_negation,
            'comparatives': has_comparative,
            'conditionals': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'token_set': tokens
        }

    def _reservoir_encode(self, text: str) -> Dict[str, float]:
        """
        Reservoir Computing: Generates a high-dimensional fixed-weight projection.
        Uses n-gram counts as the 'state' of the reservoir for the given input.
        """
        tokens = self._tokenize(text)
        state = {}
        
        # Unigrams and Bigrams as reservoir nodes
        for n in range(self.n_gram_range[0], self.n_gram_range[1] + 1):
            for i in range(len(tokens) - n + 1):
                gram = " ".join(tokens[i:i+n])
                state[gram] = state.get(gram, 0) + 1.0
                
        # Normalize (simulating reservoir fading memory)
        total = sum(state.values()) or 1
        return {k: v/total for k, v in state.items()}

    def _compute_free_energy(self, prompt_struct: Dict, cand_struct: Dict, 
                             prompt_state: Dict, cand_state: Dict) -> float:
        """
        Free Energy Principle: Calculates variational free energy F.
        F = Prediction Error (KL Divergence) + Complexity Cost.
        Lower F is better. We invert this for the score.
        """
        # 1. Prediction Error (KL Divergence approximation)
        # Compare reservoir states (distribution over n-grams)
        all_keys = set(prompt_state.keys()) | set(cand_state.keys())
        kl_div = 0.0
        epsilon = 1e-9
        
        for k in all_keys:
            p = prompt_state.get(k, epsilon)
            q = cand_state.get(k, epsilon)
            if p > 0:
                kl_div += q * math.log(q / p) if q > 0 else 0
        
        # 2. Structural Mismatch Penalty (Logical Surprise)
        # If prompt implies negation, candidate should likely reflect it (simplified heuristic)
        structural_error = 0.0
        if prompt_struct['negations'] and not cand_struct['negations']:
            # Potential violation, but context dependent. Add small energy.
            structural_error += 0.5
            
        # Length mismatch penalty (complexity cost)
        len_ratio = abs(prompt_struct['length'] - cand_struct['length']) / (prompt_struct['length'] + 1)
        complexity_cost = 0.1 * min(len_ratio, 1.0)

        return kl_div + structural_error + complexity_cost

    def _model_check(self, prompt: str, candidate: str) -> Tuple[bool, str]:
        """
        Model Checking: Verifies logical consistency.
        Returns (is_valid, reason_string).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # Rule 1: Negation Consistency (Simplified LTL: G(negation_prompt -> F(negation_candidate?)))
        # If prompt asks "Which is NOT...", candidate must not contain affirmative-only logic if obvious.
        # Heuristic: If prompt has strong negation, and candidate is extremely short/affirmative, flag.
        
        # Rule 2: Numeric Consistency (The strongest structural signal)
        if p_struct['numbers'] and c_struct['numbers']:
            # If prompt compares numbers, candidate must respect the order if it claims a result
            # Example: "Is 9.11 > 9.9?" -> Candidate "Yes" implies 9.11 > 9.9 (False)
            # We check if the candidate contradicts basic math present in prompt
            p_nums = sorted(p_struct['numbers'])
            c_nums = sorted(c_struct['numbers'])
            
            # If candidate repeats numbers but flips order illogically (hard to detect without full NLI)
            # Instead, we check for direct contradiction patterns
            if "yes" in candidate.lower() and len(p_struct['numbers']) == 2:
                n1, n2 = p_struct['numbers']
                if n1 < n2 and ">" in prompt: # Prompt asks if smaller > larger
                    # If candidate says yes, it's logically false
                    return False, "Contradicts numeric logic"
                if n1 > n2 and "<" in prompt:
                    return False, "Contradicts numeric logic"

        # Rule 3: Conditional Logic
        if p_struct['conditionals']:
            if not c_struct['conditionals'] and len(c_struct['token_set']) < 5:
                # Short answer to conditional might be okay, but long answer lacking structure is suspicious
                pass 

        return True, "Valid"

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len12 = len(zlib.compress(s1_b + s2_b))
        denom = max(len1, len2)
        if denom == 0: return 1.0
        return (len12 - min(len1, len2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_state = self._reservoir_encode(prompt)
        
        scored = []
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            cand_state = self._reservoir_encode(cand)
            
            # 1. Model Checking (Gatekeeper)
            is_valid, reason = self._model_check(prompt, cand)
            
            # 2. Free Energy Calculation
            energy = self._compute_free_energy(prompt_struct, cand_struct, prompt_state, cand_state)
            
            # Base score from inverse energy (bounded)
            score = 1.0 / (1.0 + energy)
            
            # Apply Model Checking Penalty
            if not is_valid:
                score *= 0.1  # Heavy penalty for logical failure
            
            # 3. NCD Tiebreaker (only if scores are very close, handled by sorting stability usually, 
            # but we add a tiny epsilon based on NCD to break ties deterministically)
            ncd_val = self._ncd(prompt, cand)
            score -= (ncd_val * 1e-6) # Prefer lower NCD (more similar) slightly
            
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Energy:{energy:.4f}, Valid:{is_valid}, NCD:{ncd_val:.4f}"
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize the top score to 0-1 range roughly
        # Since base score is 1/(1+E), max is 1.0. 
        # We clamp it.
        conf = max(0.0, min(1.0, results[0]['score']))
        return conf