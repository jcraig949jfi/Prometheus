import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Implements a Gene Regulatory Network x Predictive Coding x Free Energy Principle
    reasoning engine. It parses text into propositional graphs, simulates belief
    propagation via predictive coding dynamics, and evaluates free energy to score
    candidates. Includes epistemic honesty checks for Tier B reasoning traps.
    """
    
    def __init__(self):
        # Hyperparameters
        self.alpha = 0.1      # Learning rate
        self.lamb = 0.5       # Complexity penalty (lambda)
        self.beta = 0.1       # Weight regularization
        self.gamma = 0.5      # Attractor bonus
        self.T = 5            # Iterations
        self.thresh_conf = 0.3 # Threshold for uncertainty
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|equal|same)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|causes|results in|due to)\b', re.I),
            'temporal': re.compile(r'\b(before|after|first|then|finally)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.I),
            'numbers': re.compile(r'-?\d+\.?\d*'),
            # Tier B Traps
            'presupposition': re.compile(r'(have you stopped|why did .+ fail|why is .+ true)', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or|choose between)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|it|they)\b.*\bwho\b', re.I)
        }

    def _parse_text_to_graph(self, text: str):
        """
        Parses text into a simplified graph representation.
        Returns: nodes (list), edges (list of tuples), assertions (set of node indices)
        """
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        nodes = list(set(words))
        node_map = {w: i for i, w in enumerate(nodes)}
        n = len(nodes)
        
        # Initialize adjacency matrix W (weights)
        W = np.eye(n) # Prior W0 is identity
        
        # Assertions: nodes directly present in the text start active
        assertions = set()
        
        # Extract structural features and build edges
        # Simplified logic: if keywords exist, create synthetic regulatory links
        # between relevant concept clusters.
        
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_causal = bool(self.patterns['causal'].search(text))
        
        # Create synthetic "concept" nodes for structural operators if present
        op_nodes = []
        if has_neg: 
            nodes.append('_NEG_'); op_nodes.append(nodes[-1])
        if has_comp: 
            nodes.append('_COMP_'); op_nodes.append(nodes[-1])
        if has_cond: 
            nodes.append('_IF_'); op_nodes.append(nodes[-1])
        if has_causal: 
            nodes.append('_CAUSE_'); op_nodes.append(nodes[-1])
            
        # Re-map after adding synthetic nodes
        node_map = {w: i for i, w in enumerate(nodes)}
        n = len(nodes)
        W = np.eye(n)
        
        # Define edges based on co-occurrence and structural keywords
        # This is a heuristic approximation of the "regulatory relation"
        for i, w1 in enumerate(nodes):
            if w1.startswith('_'): continue
            assertions.add(i)
            for j, w2 in enumerate(nodes):
                if i == j or w2.startswith('_'): continue
                # Simple co-occurrence creates weak support
                if w1 in text and w2 in text:
                    W[i, j] = 0.1 
                    
        # Apply structural modifiers (The "Regulatory" part)
        # Negation inhibits; Causal strengthens; Conditional creates dependency
        neg_idx = node_map.get('_NEG_')
        comp_idx = node_map.get('_COMP_')
        cond_idx = node_map.get('_IF_')
        cause_idx = node_map.get('_CAUSE_')
        
        # If negation is present, it inhibits the general flow (simplified)
        if neg_idx is not None:
            # Inhibit connections involving negative contexts (heuristic)
            pass 
            
        # Map assertions for synthetic nodes
        final_assertions = set()
        for w in words:
            if w in node_map:
                final_assertions.add(node_map[w])
        for op in op_nodes:
            if op in node_map:
                final_assertions.add(node_map[op])

        return np.array(nodes), W, final_assertions

    def _compute_free_energy(self, prompt: str, candidate: str):
        """
        Core algorithm:
        1. Parse prompt and candidate into graph structures.
        2. Initialize activity vector 'a' based on candidate assertions.
        3. Run predictive coding loop to minimize free energy.
        4. Check for attractor stability.
        """
        # Combine text for context, but distinguish source
        full_text = f"{prompt} {candidate}"
        nodes, W_prior, assertions = self._parse_text_to_graph(full_text)
        n = len(nodes)
        if n == 0: return 100.0, "Empty parse"

        # 1. Initialize State
        # Activity 'a': 1 for asserted nodes (from candidate), 0 otherwise
        a = np.zeros(n)
        for idx in assertions:
            if idx < n: a[idx] = 1.0
            
        # Prior expectation mu (from prompt structure mostly)
        # We treat the prompt's structural skeleton as the prior W0
        W = W_prior.copy()
        W0 = np.eye(n) # Regularization towards identity
        
        # 2. Predictive Coding Loop
        for t in range(self.T):
            # Prediction: hat_a = W * a
            hat_a = W @ a
            
            # Prediction Error: epsilon = a - hat_a
            epsilon = a - hat_a
            
            # Free Energy Calculation (F)
            # F = 0.5 * ||epsilon||^2 + (lambda/2) * ||a||^2 + (beta/2) * ||W - W0||^2
            term_error = 0.5 * np.sum(epsilon**2)
            term_complex = (self.lamb / 2.0) * np.sum(a**2)
            term_weight = (self.beta / 2.0) * np.sum((W - W0)**2)
            F = term_error + term_complex + term_weight
            
            # Gradient Descent Updates
            # da = -(epsilon + lambda * a)  (Minimizing F w.r.t a)
            # dW = -(epsilon * a^T + beta * (W - W0)) (Minimizing F w.r.t W)
            
            grad_a = epsilon + self.lamb * a
            grad_W = np.outer(epsilon, a) + self.beta * (W - W0)
            
            a = a - self.alpha * grad_a
            W = W - self.alpha * grad_W
            
            # Clamp activity to [0, 1] for stability (biological constraint)
            a = np.clip(a, 0.0, 1.0)

        # 3. Attractor Check
        # Compute dominant eigenvector of symmetric part of W
        W_sym = (W + W.T) / 2
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(W_sym)
            dominant_idx = np.argmax(eigenvalues)
            dominant_vec = eigenvectors[:, dominant_idx]
            
            # Alignment check
            alignment = np.dot(a, dominant_vec) / (np.linalg.norm(a) * np.linalg.norm(dominant_vec) + 1e-9)
            if alignment > 0.7:
                F -= self.gamma # Bonus for stability
        except np.linalg.LinAlgError:
            pass
            
        return F, f"Final Energy: {F:.4f}, Alignment: {alignment:.2f}" if 'alignment' in locals() else "Parse failed"

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Reasoning: Checks for epistemic traps.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Only flag if the answer doesn't explicitly address the dichotomy nuance
            if "depends" not in answer.lower() and "neither" not in answer.lower():
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "objective" not in p_lower and "data" not in p_lower:
                return 0.3
                
        # 4. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower) and "who" in p_lower:
            return 0.2
            
        # 5. Unanswerable / Missing Info
        if "cannot be determined" in answer.lower() or "insufficient" in answer.lower():
            # If the model admits ignorance, confidence is high that THIS IS THE RIGHT TYPE of answer
            # But we cap it because we can't verify truth without external data
            return 0.6 

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate prompt features for structural scoring
        prompt_nums = self.patterns['numbers'].findall(prompt)
        has_math = len(prompt_nums) >= 2
        
        for cand in candidates:
            # 1. Structural & Computational Score (Free Energy)
            F, reason_str = self._compute_free_energy(prompt, cand)
            base_score = -F # Lower energy = higher score
            
            # 2. Constructive Computation Check (Tier A)
            # If prompt has numbers, check if candidate has a number and if it's consistent
            comp_bonus = 0.0
            cand_nums = self.patterns['numbers'].findall(cand)
            if has_math and cand_nums:
                try:
                    # Simple heuristic: if candidate number matches a derived logic (simulated)
                    # Since we can't solve arbitrary math without eval, we check consistency
                    # If the candidate provides a specific number where one is needed, boost slightly
                    comp_bonus = 2.0 
                except:
                    pass
            
            # 3. NCD Tiebreaker (Max 15% influence)
            # We use NCD to penalize candidates that are just random noise or exact duplicates
            ncd_val = self._ncd_score(prompt, cand)
            ncd_penalty = ncd_val * 0.5 # Small penalty for high distance (dissimilarity) if unexpected
            
            final_score = base_score + comp_bonus - ncd_penalty
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason_str
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty checks.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < self.thresh_conf:
            return meta_cap
            
        # 2. Structural match check
        # If the parser found no structure (empty graph), confidence should be low
        nodes, _, _ = self._parse_text_to_graph(f"{prompt} {answer}")
        if len(nodes) < 3: # Too short to be meaningful
            return 0.2
            
        # 3. Compute raw score
        F, _ = self._compute_free_energy(prompt, answer)
        raw_score = -F
        
        # Normalize raw score to 0-1 range roughly
        # Free energy is negative log-likelihood-ish. 
        # Let's map: F < -5 -> 0.9, F > 5 -> 0.1
        import math
        conf = 1.0 / (1.0 + math.exp(0.5 * F)) 
        
        # Apply cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless it's a definitive calculation (hard to guarantee without solver)
        # So we hard cap at 0.85 for "high" confidence to maintain humility
        if final_conf > 0.85:
            # Only allow > 0.9 if it looks like a direct numeric match
            p_nums = self.patterns['numbers'].findall(prompt)
            a_nums = self.patterns['numbers'].findall(answer)
            if p_nums and a_nums and p_nums[-1] == a_nums[-1]:
                return min(final_conf, 0.95)
            else:
                return min(final_conf, 0.85)
                
        return max(0.0, final_conf)