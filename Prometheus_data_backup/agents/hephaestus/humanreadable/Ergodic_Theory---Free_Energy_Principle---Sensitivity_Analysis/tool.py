import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Ergodic Theory, Free Energy Principle, 
    and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations (edges) from text.
    2. Free Energy Minimization: Models belief states as a vector b. Iteratively updates 
       b via gradient descent to minimize a variational free energy function F(b), 
       balancing prediction error (logical consistency) and entropy.
    3. Sensitivity Analysis: Computes the gradient of F with respect to edge weights 
       to determine robustness.
    4. Ergodic Scoring: Averages the free energy over T steps to approximate the 
       space average, providing a stable score (-F_avg).
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bequal\s+to\b', r'\bmore\s+than\b', r'\bfewer\s+than\b'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bonly\s+if\b', r'\bunless\b'],
        'causal': [r'\bbecause\b', r'\bleads\s+to\b', r'\bcauses\b', r'\btherefore\b'],
        'ordering': [r'\bbefore\b', r'\bafter\b', r'\bprecedes\b', r'\bfollows\b'],
        'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b'],
        'number': r'\d+(?:\.\d+)?'
    }

    def __init__(self):
        self.t_steps = 20  # Iterations for ergodic averaging
        self.lr = 0.1      # Learning rate for belief update
        self.epsilon = 1e-6 # Small constant to prevent log(0)

    def _extract_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, float]]]:
        """Parse text into vertices (propositions) and edges (logical relations)."""
        text_lower = text.lower()
        sentences = re.split(r'[.\?!]', text)
        vertices = []
        edges = []
        
        # Simple vertex extraction: non-empty sentences stripped
        for s in sentences:
            s_clean = s.strip()
            if s_clean:
                vertices.append(s_clean)
        
        n = len(vertices)
        if n == 0:
            return [], []
            
        # Create a fully connected graph with weights based on proximity and cues
        # In a real NLP system, this would be semantic. Here we use structural cues.
        for i in range(n):
            for j in range(i+1, n):
                s_combined = f"{vertices[i]} {vertices[j]}"
                weight = 0.5 # Base prior
                
                # Boost weight if logical cues exist between i and j
                for cue_type, patterns in self.PATTERNS.items():
                    if cue_type == 'number': continue
                    if any(re.search(p, s_combined) for p in patterns):
                        weight = 0.9
                        break
                
                # Determine relation type penalty logic (simplified for implementation)
                # If 'not' is present, relation is inhibitory (target ~0 if source ~1)
                # If 'if/then', relation is implicative (source <= target)
                is_negated = any(re.search(p, s_combined) for p in self.PATTERNS['negation'])
                is_conditional = any(re.search(p, s_combined) for p in self.PATTERNS['conditional'])
                
                # Encode edge type: 1.0 = imply (A->B), -1.0 = negate (A->!B), 0.0 = conjunctive
                edge_type = 0.0 
                if is_conditional:
                    edge_type = 1.0
                elif is_negated:
                    edge_type = -1.0
                
                edges.append((i, j, weight, edge_type))
                
        return vertices, edges

    def _compute_free_energy(self, b: np.ndarray, edges: List[Tuple], entropy_weight: float = 0.1) -> Tuple[float, np.ndarray]:
        """
        Compute Free Energy F(b) = Prediction Error + Entropy.
        Returns F and the gradient dF/db.
        """
        n = len(b)
        pred_error = 0.0
        grad_b = np.zeros_like(b)
        
        # Prediction Error Term
        for i, j, w, etype in edges:
            if i >= n or j >= n: continue
            
            bi, bj = b[i], b[j]
            penalty = 0.0
            d_penalty_di = 0.0
            d_penalty_dj = 0.0
            
            if etype == 1.0: # Implication: if bi then bj (bi <= bj)
                if bi > bj:
                    penalty = (bi - bj)**2
                    d_penalty_di = 2 * (bi - bj)
                    d_penalty_dj = -2 * (bi - bj)
            elif etype == -1.0: # Negation/Causal inverse: if bi then not bj
                if bi > (1 - bj):
                    penalty = (bi - (1-bj))**2
                    d_penalty_di = 2 * (bi - (1-bj))
                    d_penalty_dj = 2 * (bi - (1-bj)) # Derivative wrt bj is positive here
            
            pred_error += w * penalty
            grad_b[i] += w * d_penalty_di
            grad_b[j] += w * d_penalty_dj

        # Entropy Term: Sum[b log b + (1-b) log (1-b)]
        # We add small epsilon to avoid log(0)
        b_safe = np.clip(b, self.epsilon, 1-self.epsilon)
        entropy = np.sum(b_safe * np.log(b_safe) + (1-b_safe) * np.log(1-b_safe))
        
        # Gradient of entropy: log(b) - log(1-b)
        grad_entropy = np.log(b_safe) - np.log(1-b_safe)
        
        total_f = pred_error + entropy_weight * entropy
        grad_total = grad_b + entropy_weight * grad_entropy
        
        return total_f, grad_total

    def _run_dynamics(self, text: str) -> Tuple[float, float, str]:
        """Run the ergodic free-energy minimization and sensitivity analysis."""
        vertices, edges = self._extract_graph(text)
        n = len(vertices)
        
        if n == 0:
            return 0.0, 0.0, "No logical structure detected."
        
        # Initialize belief vector uniformly
        b = np.full(n, 0.5)
        
        f_history = []
        sensitivity_sum = 0.0
        
        # Pre-calculate base sensitivity (perturb weights slightly)
        base_f, _ = self._compute_free_energy(b, edges)
        
        for t in range(self.t_steps):
            # Gradient descent step
            f_val, grad = self._compute_free_energy(b, edges)
            b = b - self.lr * grad
            b = np.clip(b, 0.0, 1.0) # Project to valid probability space
            
            f_history.append(f_val)
            
            # Sensitivity Analysis: dF/dw approximation
            # Perturb all weights by delta and measure change in F
            delta = 0.01
            edges_perturbed = [(i, j, w + delta, etype) for i, j, w, etype in edges]
            f_perturbed, _ = self._compute_free_energy(b, edges_perturbed)
            sens = (f_perturbed - f_val) / (delta * len(edges) + 1e-6)
            sensitivity_sum += abs(sens)

        avg_f = np.mean(f_history)
        avg_sens = sensitivity_sum / self.t_steps
        
        # Reasoning summary
        reasoning = f"Analyzed {n} propositions. Converged to free energy {avg_f:.4f}. "
        if avg_sens > 0.5:
            reasoning += "High sensitivity: Logic is fragile."
        else:
            reasoning += "Low sensitivity: Logic is robust."
            
        return -avg_f, avg_sens, reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        full_texts = [f"{prompt} {c}" for c in candidates]
        
        scores = []
        for text in full_texts:
            score, sens, reason = self._run_dynamics(text)
            # Adjust score by sensitivity (penalize fragile logic)
            final_score = score * (1.0 / (1.0 + sens)) 
            scores.append((final_score, sens, reason))
        
        # Normalize scores to 0-1 range roughly if needed, but raw score works for ranking
        # Add NCD tiebreaker logic implicitly by sorting stable items first if scores are close
        ranked_indices = np.argsort([-s[0] for s in scores])
        
        output = []
        for idx in ranked_indices:
            c = candidates[idx]
            sc, sens, reason = scores[idx]
            output.append({
                "candidate": c,
                "score": float(sc),
                "reasoning": reason
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on the free energy score."""
        text = f"{prompt} {answer}"
        score, sens, _ = self._run_dynamics(text)
        
        # Map score to 0-1 confidence
        # High negative free energy (low F) -> High confidence
        # Sensitivity reduces confidence
        raw_conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        robust_conf = raw_conf / (1.0 + sens)
        
        return float(np.clip(robust_conf, 0.0, 1.0))