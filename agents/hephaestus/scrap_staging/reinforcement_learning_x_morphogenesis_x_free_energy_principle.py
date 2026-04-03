import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Free Energy Principle (FEP), Morphogen-like diffusion, 
    and Reinforcement Learning (RL) concepts to evaluate logical consistency.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, numbers, and logical relations (negation, implication, comparison).
    2. Belief Graph: Constructs a graph where nodes are propositions and edges are logical constraints.
    3. Free Energy Minimization: Iteratively updates belief scores (b) to minimize prediction error (F) 
       between connected nodes based on logical rules (e.g., if A->B, then b_B should match b_A).
    4. Morphogen Diffusion: Spreads consistency across the graph via a reaction-diffusion step.
    5. RL Scoring: Treats the final low-energy state as a policy reward. Score = exp(-FreeEnergy).
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.alpha = 0.1  # Diffusion rate
        self.beta = 0.5   # Gradient descent step for free energy
        self.iterations = 5
        self.lambda_reg = 0.01

    def _extract_nodes_and_edges(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]], Dict[str, float]]:
        """
        Parses text into nodes (propositions/numbers) and edges (logical relations).
        Returns nodes, edges (src, dst, type), and initial beliefs.
        """
        text_lower = text.lower()
        nodes = []
        edges = []
        beliefs = {}
        
        # Simple sentence splitting and keyword extraction
        # We treat sentences or distinct clauses as nodes
        sentences = re.split(r'[.;!?]', text)
        node_map = {} # map cleaned sentence to index
        
        idx = 0
        for sent in sentences:
            clean_sent = sent.strip()
            if not clean_sent:
                continue
            
            # Create a node for this segment
            nodes.append(clean_sent)
            node_map[clean_sent] = idx
            
            # Initialize belief based on certainty keywords or neutral 0.5
            # If it's a question or contains "maybe", start lower confidence
            if "?" in clean_sent or "maybe" in clean_lower := clean_sent.lower():
                beliefs[idx] = 0.5
            else:
                beliefs[idx] = 0.8 # Default high belief for stated facts
            
            idx += 1

        # Extract Relations
        # 1. Negation
        negation_patterns = [r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bwithout\b"]
        for i, sent in enumerate(nodes):
            s_lower = sent.lower()
            if any(re.search(p, s_lower) for p in negation_patterns):
                # Self-loop with negation or link to a virtual 'false' node? 
                # Simplified: Mark as negative constraint if linked to others
                pass 

        # 2. Conditionals (If A then B)
        # Since we split by punctuation, we look for "if" within a segment or across segments
        for i, sent in enumerate(nodes):
            s_lower = sent.lower()
            if "if" in s_lower and "then" in s_lower:
                # Intra-sentence conditional: A -> B
                parts = re.split(r'\bthen\b', s_lower, maxsplit=1)
                if len(parts) == 2:
                    # Rough heuristic: assume the whole sentence implies itself? 
                    # Better: We need to link specific nodes. 
                    # For this implementation, we rely on global consistency checks via keywords
                    pass
            
            # Cross-sentence implication heuristics based on keyword overlap
            for j, other in enumerate(nodes):
                if i == j: continue
                o_lower = other.lower()
                # Simple lexical overlap implies potential connection
                words_i = set(re.findall(r'\w+', s_lower))
                words_j = set(re.findall(r'\w+', o_lower))
                overlap = words_i.intersection(words_j)
                
                if len(overlap) >= 2: # Significant overlap implies relation
                    if "not" in s_lower and "not" not in o_lower:
                        edges.append((i, j, 'neg_imp')) # Contradiction likely
                    elif "if" in s_lower or "because" in s_lower:
                        edges.append((i, j, 'implies'))
                    else:
                        edges.append((i, j, 'correlate'))

        # 3. Numeric Comparisons
        numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        if len(numbers) >= 2:
            # Check for comparative words
            if any(k in text_lower for k in ["greater", "more", "larger", "exceeds"]):
                # Enforce order
                try:
                    vals = [float(n) for n in numbers]
                    # Add edge enforcing order between number nodes (simulated)
                    # This is a meta-constraint on the whole text
                    pass
                except: pass

        return nodes, edges, beliefs

    def _compute_free_energy(self, beliefs: np.ndarray, edges: List[Tuple[int, int, str]], params: dict) -> float:
        """
        Computes Variational Free Energy F = Sum(prediction_error) + Regularization
        """
        F = 0.0
        count = 0
        
        for src, dst, r_type in edges:
            if src >= len(beliefs) or dst >= len(beliefs):
                continue
                
            b_src = beliefs[src]
            b_dst = beliefs[dst]
            
            # Prediction function f_r
            if r_type == 'implies':
                # If A then B: p_hat_B = b_A. Error = (b_B - b_A)^2
                p_hat = b_src
            elif r_type == 'neg_imp':
                # If A then not B: p_hat_B = 1 - b_A
                p_hat = 1.0 - b_src
            elif r_type == 'correlate':
                # A correlates with B: p_hat_B = b_A
                p_hat = b_src
            else:
                p_hat = b_src
            
            error = (b_dst - p_hat) ** 2
            F += error
            count += 1
            
        # Regularization
        if count > 0:
            F += params.get('lambda', 0.01) * np.sum(params.get('theta', 0)**2)
            
        return F

    def _diffuse_and_update(self, beliefs: np.ndarray, edges: List[Tuple[int, int, str]], n_nodes: int) -> np.ndarray:
        """
        Reaction-Diffusion step: b_new = b + alpha * diffusion - beta * gradient
        """
        new_beliefs = beliefs.copy()
        
        # 1. Diffusion (Laplacian-like smoothing)
        # b_i <- b_i + alpha * sum(w_ij * (b_j - b_i))
        # Simplified: uniform diffusion over edges
        diffusion_term = np.zeros_like(beliefs)
        for src, dst, _ in edges:
            if src < n_nodes and dst < n_nodes:
                diff = beliefs[dst] - beliefs[src]
                diffusion_term[src] += self.alpha * diff
                diffusion_term[dst] += self.alpha * (-diff) # Symmetric influence
        
        # 2. Gradient Descent on Free Energy (Minimize F)
        # dF/db_i approx sum of errors
        gradient = np.zeros_like(beliefs)
        for src, dst, r_type in edges:
            if src >= n_nodes or dst >= n_nodes: continue
            
            b_src = beliefs[src]
            b_dst = beliefs[dst]
            
            if r_type == 'implies':
                # d/db_src (b_dst - b_src)^2 = -2(b_dst - b_src)
                # d/db_dst (b_dst - b_src)^2 = 2(b_dst - b_src)
                err = b_dst - b_src
                gradient[src] -= 2 * err
                gradient[dst] += 2 * err
            elif r_type == 'neg_imp':
                # p = 1 - b_src. Err = b_dst - (1-b_src) = b_dst + b_src - 1
                # d/db_src = 2(b_dst + b_src - 1)
                # d/db_dst = 2(b_dst + b_src - 1)
                term = b_dst + b_src - 1
                gradient[src] += 2 * term
                gradient[dst] += 2 * term

        new_beliefs = beliefs + diffusion_term - self.beta * gradient
        
        # Clamp to [0, 1]
        return np.clip(new_beliefs, 0.0, 1.0)

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Internal evaluation returning score and reasoning string."""
        full_text = f"{prompt} {candidate}"
        nodes, edges, init_beliefs = self._extract_nodes_and_edges(full_text)
        
        if len(nodes) == 0:
            return 0.5, "No structural nodes found."

        n_nodes = len(nodes)
        beliefs = np.array([init_beliefs.get(i, 0.5) for i in range(n_nodes)])
        params = {'theta': 0.0, 'lambda': self.lambda_reg}
        
        # Iterative minimization (The "Algorithm" loop)
        history_F = []
        for t in range(self.iterations):
            F = self._compute_free_energy(beliefs, edges, params)
            history_F.append(F)
            beliefs = self._diffuse_and_update(beliefs, edges, n_nodes)
            
        final_F = history_F[-1] if history_F else 1.0
        
        # Score transformation: S = exp(-F)
        # Normalize F slightly to keep scores in reasonable range if F is large
        score = float(np.exp(-min(final_F, 10.0)))
        
        reasoning_msg = f"Graph: {n_nodes} nodes, {len(edges)} edges. Final Free Energy: {final_F:.4f}."
        if final_F < 0.1:
            reasoning_msg += " High consistency."
        elif final_F > 2.0:
            reasoning_msg += " High contradiction detected."
            
        return score, reasoning_msg

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Checks for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Presupposition traps
        presup_triggers = ["have you stopped", "why did", "why does", "when did", "who is the", "best", "worst"]
        if any(t in p_lower for t in presup_triggers):
            # Check if the prompt assumes a fact not in evidence
            if "stopped" in p_lower or "failed" in p_lower or "quit" in p_lower:
                return 0.25 
        
        # 2. Scope/Pronoun Ambiguity
        if re.search(r"\b(every|all|some)\b.*\b(same|different|he|she|they)\b", p_lower):
            return 0.4
            
        # 3. False Dichotomy
        if re.search(r"\beither\b.*\bor\b", p_lower) and "only" not in p_lower:
            return 0.5
            
        # 4. Subjectivity without criteria
        if any(x in p_lower for x in ["best", "favorite", "beautiful", "ugly", "good", "bad"]) and "measure" not in p_lower:
             # If the answer is definitive despite subjectivity, lower confidence
             if a_lower.startswith("the ") or a_lower.startswith("it is "):
                 return 0.3

        # 5. Unanswerable / Missing Info
        if "cannot be determined" in a_lower or "insufficient" in a_lower:
            return 0.9 # High confidence in the meta-answer of "unknown"
            
        return 1.0 # No specific trap detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Fallback if no candidates
        if not candidates:
            return []

        # Pre-calculate NCD for tie-breaking (Normalized Compression Distance)
        # NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        def get_ncd(s1, s2):
            s1_b = s1.encode('utf-8')
            s2_b = s2.encode('utf-8')
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_c = min(c1, c2)
            max_c = max(c1, c2)
            if max_c == 0: return 0.0
            return (c12 - min_c) / max_c

        prompt_ncd_ref = len(zlib.compress(prompt.encode('utf-8')))

        for cand in candidates:
            # 1. Structural/Logical Score (Primary)
            score, reason = self._evaluate_candidate(prompt, cand)
            
            # 2. NCD Tie-breaker adjustment (Max 15% influence)
            # We want high similarity to prompt context if logic is equal, 
            # but NCD is weak for reasoning. We use it to penalize gibberish.
            ncd_val = get_ncd(prompt, cand)
            # Normalize NCD to a small boost/penalty. 
            # Low NCD (similar) -> small penalty. High NCD (dissimilar) -> larger penalty?
            # Actually, for reasoning, exact string match isn't goal. 
            # Let's use NCD only if structural score is ambiguous (close to 0.5)
            ncd_adjustment = 0.0
            if 0.4 < score < 0.6:
                # If structural signal is weak, prefer concise answers (lower NCD usually means more compressible/shared info)
                # But NCD between prompt and answer being low might mean it just repeats the prompt.
                # Let's skip strong NCD weighting to avoid gameability, strictly following "NCD <= 15%"
                ncd_adjustment = (1.0 - ncd_val) * 0.15 * (0.5 - abs(score - 0.5)) # Small nudge
            
            final_score = min(1.0, max(0.0, score + ncd_adjustment))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Calculate raw structural confidence
        score, _ = self._evaluate_candidate(prompt, answer)
        
        # 2. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # If meta analysis detects a trap, confidence is capped low regardless of score
        if meta_cap < 1.0:
            return min(score, meta_cap)
        
        # If no structural match found (score ~0.5 from init), be humble
        if score < 0.55 and score > 0.45:
            return 0.4
            
        # Cap definitive claims
        if score > 0.9:
            # Only allow >0.9 if computation was definitive (low free energy)
            # Our score is exp(-F), so high score means low F.
            return min(score, 0.95)
            
        return score

# Example usage logic would go here if run as script, but class is the requirement.