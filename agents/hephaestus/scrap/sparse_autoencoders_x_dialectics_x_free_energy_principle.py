import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Sparse Free Energy Reasoner.
    
    Mechanism:
    1. Parsing: Extracts propositional triples and structural flags (negation, causal, etc.)
       into a binary feature vector x.
    2. Sparse Coding (ISTA): Solves min ||x - Da||^2 + lambda||a||_1 to find sparse code 'a'.
       The objective value is the Variational Free Energy.
    3. Dialectics: Generates an 'antithesis' by flipping logical polarities in the prompt.
       The dictionary D is updated to minimize joint energy of thesis/antithesis (Synthesis).
    4. Scoring: Candidates are scored by their Free Energy (lower energy = better fit).
       NCD is used strictly as a tie-breaker for low-information candidates.
    """
    
    def __init__(self):
        self.F = 64  # Feature dimension
        self.K = 128 # Dictionary size (overcomplete)
        self.lambda_reg = 0.1
        self.step_size = 0.01
        self.ista_iters = 20
        
        # Initialize Dictionary D randomly (F x K)
        np.random.seed(42)
        self.D = np.random.randn(self.F, self.K) * 0.1
        self.D = self.D / (np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9)
        
        # Entity mapping
        self.entities = {}
        self.ent_count = 0
        
        # Predicates map
        self.predicates = ["is", "causes", "precedes", "exceeds", "implies", "contains"]
        self.pred_map = {p: i % self.F for i, p in enumerate(self.predicates)}

    def _get_entity_id(self, text: str) -> int:
        if text not in self.entities:
            self.entities[text] = self.ent_count
            self.ent_count += 1
        return self.entities[text] % (self.F - 10) # Reserve space for flags

    def _parse_flags(self, text: str) -> np.ndarray:
        """Extract structural flags: negation, comparative, conditional, causal, ordering, numeric."""
        text_l = text.lower()
        flags = np.zeros(10)
        
        if re.search(r'\b(not|no|never|neither|without)\b', text_l): flags[0] = 1.0
        if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_l): flags[1] = 1.0
        if re.search(r'\b(if|then|unless|provided)\b', text_l): flags[2] = 1.0
        if re.search(r'\b(because|thus|hence|leads to|causes)\b', text_l): flags[3] = 1.0
        if re.search(r'\b(before|after|first|last|prior)\b|[<>]', text_l): flags[4] = 1.0
        if re.search(r'\d+(\.\d+)?', text_l): flags[5] = 1.0
        if re.search(r'\b(all|some|every|none|any)\b', text_l): flags[6] = 1.0
        
        # Numeric value extraction (simplified)
        nums = re.findall(r'-?\d+\.?\d*', text_l)
        if nums:
            try: flags[7] = float(nums[0]) / 100.0 # Normalize slightly
            except: pass
            
        return flags

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to binary feature vector x."""
        x = np.zeros(self.F)
        flags = self._parse_flags(text)
        x[:10] = flags
        
        # Simple triple extraction (Subject Predicate Object) approx
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        unique_words = list(dict.fromkeys(words)) # Preserve order, remove dupes
        
        # Map entities to indices
        for i, word in enumerate(unique_words[:5]):
            if word not in ["is", "are", "was", "were", "be", "the", "a", "an"]:
                idx = 10 + (self._get_entity_id(word) % (self.F - 10))
                if idx < self.F: x[idx] = 1.0
                
        # Map detected predicates
        for p in self.predicates:
            if p in text.lower():
                x[self.pred_map[p]] = 1.0
                
        return x

    def _ista(self, x: np.ndarray) -> Tuple[np.ndarray, float]:
        """Iterative Soft Thresholding for Lasso."""
        a = np.zeros(self.K)
        xt = x.reshape(-1, 1)
        Dt = self.D.T
        
        for _ in range(self.ista_iters):
            residual = xt - self.D @ a
            grad = Dt @ residual
            a = a + self.step_size * grad
            # Soft thresholding
            threshold = self.lambda_reg * self.step_size
            a = np.sign(a) * np.maximum(np.abs(a) - threshold, 0)
            
        recon = self.D @ a
        error = np.sum((xt - recon)**2)
        energy = float(error + self.lambda_reg * np.sum(np.abs(a)))
        return a, energy

    def _generate_antithesis(self, text: str) -> str:
        """Flip logical polarities to create dialectical antithesis."""
        t = text
        replacements = [
            (r"\bnot\b", "TEMP_NEG"), (r"\bno\b", "TEMP_NO"),
            (r"\bmore\b", "less"), (r"\bless\b", "more"),
            (r"\bhigher\b", "lower"), (r"\blower\b", "higher"),
            (r"\bbefore\b", "after"), (r"\bafter\b", "before"),
            (r"\bcauses\b", "prevents"), (r"\bleads to\b", "inhibits"),
            (r"\btrue\b", "false"), (r"\byes\b", "no"),
            (r"\ball\b", "none"), (r"\bsome\b", "none")
        ]
        for pat, sub in replacements:
            t = re.sub(pat, sub, t, flags=re.IGNORECASE)
        t = t.replace("TEMP_NEG", "is_not_contradicted").replace("TEMP_NO", "is_present")
        return t

    def _update_dictionary(self, x_thesis: np.ndarray, x_antithesis: np.ndarray):
        """Synthesis: Update D to minimize joint free energy of thesis and antithesis."""
        # Stack inputs
        X = np.column_stack([x_thesis, x_antithesis])
        
        # Compute codes for both
        a_t, _ = self._ista(x_thesis)
        a_a, _ = self._ista(x_antithesis)
        A = np.column_stack([a_t, a_a])
        
        # Gradient step for D: min ||X - DA||^2 -> grad = -2(X - DA)A^T
        # We do a single step: D_new = D + lr * (X - DA)A^T
        recon = self.D @ A
        error = X - recon
        grad = error @ A.T
        self.D += 0.05 * grad
        
        # Re-normalize columns
        norms = np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9
        self.D /= norms

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        
        # 1. Parse Prompt (Thesis)
        x_prompt = self._text_to_vector(prompt)
        
        # 2. Generate Antithesis & Update Dictionary (Synthesis Step)
        anti_text = self._generate_antithesis(prompt)
        x_anti = self._text_to_vector(anti_text)
        self._update_dictionary(x_prompt, x_anti)
        
        results = []
        base_energy = None
        
        # Evaluate candidates
        for cand in candidates:
            x_cand = self._text_to_vector(cand)
            _, energy = self._ista(x_cand)
            
            # Heuristic boost: If candidate contains explicit confirmation of prompt structure
            # and has low energy, it's strong.
            score = -energy # Lower energy = higher score
            
            results.append({"candidate": cand, "score": score, "energy": energy})
        
        # Normalize scores to 0-1 range roughly
        energies = [r["energy"] for r in results]
        min_e, max_e = min(energies), max(energies)
        span = max_e - min_e + 1e-9
        
        final_results = []
        for r in results:
            # Invert energy: low energy -> high score
            norm_score = 1.0 - ((r["energy"] - min_e) / span)
            
            # Tie-breaking with NCD if scores are very close
            if span < 1e-4:
                import zlib
                def ncd(a, b):
                    c = zlib.compress
                    la, lb, lab = len(c(a)), len(c(b)), len(c(a+b))
                    return (lab - min(la, lb)) / max(la, lb, 1)
                # Simple NCD check against prompt
                ncd_val = ncd(prompt.encode(), r["candidate"].encode())
                norm_score = (norm_score * 0.9) + ((1-ncd_val) * 0.1)

            final_results.append({
                "candidate": r["candidate"],
                "score": float(norm_score),
                "reasoning": f"Free Energy: {r['energy']:.4f}. Lower energy indicates better resolution of dialectical tension."
            })
            
        # Sort descending by score
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy relative to a baseline."""
        x_prompt = self._text_to_vector(prompt)
        x_ans = self._text_to_vector(answer)
        
        # Quick synthesis update for context
        x_anti = self._text_to_vector(self._generate_antithesis(prompt))
        self._update_dictionary(x_prompt, x_anti)
        
        _, energy = self._ista(x_ans)
        
        # Map energy to confidence: 
        # Assume typical energy range [0, 5]. < 1.0 is high confidence. > 3.0 is low.
        # Using exponential decay for confidence
        conf = np.exp(-0.5 * energy)
        return float(np.clip(conf, 0.0, 1.0))