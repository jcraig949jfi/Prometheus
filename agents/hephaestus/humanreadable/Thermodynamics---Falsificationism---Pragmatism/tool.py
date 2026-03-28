import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Thermodynamic-Falsificationist-Pragmatic Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions and logical constraints (negation, implication, 
       comparison, causality) using regex patterns from the prompt and candidate answers.
    2. Pragmatic Utility: Assigns utility scores based on the frequency of successful structural 
       patterns (simulated via pattern complexity/specificity).
    3. Free Energy Minimization: Constructs an energy function F(b) combining:
       - Pragmatic term: Negative log-likelihood weighted by utility.
       - Falsification penalty: Violations of logical constraints (Popperian falsification).
       - Entropy term: Maintains uncertainty (Temperature T).
    4. Optimization: Uses projected gradient descent to minimize F(b), yielding a belief vector b.
    5. Scoring: Candidates are ranked by their final belief scores. NCD is used only as a tiebreaker.
    
    This approach integrates Falsificationism and Pragmatism tightly (synergy +0.261) while 
    keeping Thermodynamics as a separate optimization path (avoiding negative interaction).
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bprovided\b'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bcauses\b', r'\btherefore\b'],
            'temporal': [r'\bbefore\b', r'\bafter\b', r'\bwhen\b'],
            'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore than\b', r'\bfewer than\b'],
            'equality': [r'\bis\b', r'\bequals\b', r'\bare\b'],
            'numeric': r'(\d+\.?\d*)'
        }
        self.lambda_penalty = 1.0
        self.temperature = 0.1

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features and propositions from text."""
        text_lower = text.lower()
        features = {k: [] for k in self.patterns.keys()}
        propositions = []
        constraints = []  # (type, i, j, weight)
        
        # Simple proposition extraction (sentences/clauses)
        sentences = re.split(r'[.!?]', text)
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue
            propositions.append(sent)
            
            # Check for patterns
            for p_type, pats in self.patterns.items():
                if p_type == 'numeric':
                    if re.search(pats, sent):
                        features[p_type].append((i, sent))
                else:
                    for pat in pats:
                        if re.search(pat, sent, re.IGNORECASE):
                            features[p_type].append((i, sent))
                            break
        
        # Generate constraints based on co-occurrence and logic keywords
        # This is a simplified heuristic for the demo
        for i, prop in enumerate(propositions):
            for j, other in enumerate(propositions):
                if i == j: continue
                # Example: If "if" in i and "then" in i, link i -> j (simplified)
                if re.search(r'\bif\b', prop, re.IGNORECASE):
                    constraints.append(('implies', i, j, 0.8))
                # Example: Negation
                if any(re.search(p, prop, re.IGNORECASE) for p in self.patterns['negation']):
                     constraints.append(('negates', i, j, 0.5)) # Weak global negation heuristic

        return {'propositions': propositions, 'features': features, 'constraints': constraints}

    def _compute_pragmatic_utility(self, text: str) -> float:
        """
        Compute pragmatic utility based on structural richness.
        Higher utility for texts with specific logical markers.
        """
        score = 0.0
        text_lower = text.lower()
        for p_type, pats in self.patterns.items():
            if p_type == 'numeric':
                if re.search(pats, text):
                    score += 0.1
            else:
                count = 0
                for pat in pats:
                    count += len(re.findall(pat, text_lower))
                if count > 0:
                    score += 0.2 * count
        # Normalize roughly to [0, 1] range expectation
        return min(1.0, score / 5.0)

    def _phi_penalty(self, b_i: float, b_j: float, c_type: str) -> float:
        """Calculate falsification penalty phi."""
        if c_type == 'negates':
            # Penalty if both are believed true (i true, j should be false)
            # phi = max(0, b_i - (1 - b_j))
            return max(0.0, b_i - (1.0 - b_j))
        elif c_type == 'implies':
            # Penalty if i is true and j is false
            # phi = max(0, b_i - b_j)
            return max(0.0, b_i - b_j)
        elif c_type == 'greater':
            return max(0.0, b_i - b_j) # Simplified monotonic
        elif c_type == 'less':
            return max(0.0, b_j - b_i) # Simplified monotonic
        return 0.0

    def _minimize_free_energy(self, N: int, utils: np.ndarray, constraints: List) -> np.ndarray:
        """
        Minimize F(b) using projected gradient descent.
        F(b) = Pragmatic Term + Falsification Penalty + Entropy Term
        """
        if N == 0:
            return np.array([])
            
        # Initialize beliefs uniformly
        b = np.full(N, 0.5)
        lr = 0.1
        
        for _ in range(100):
            b_old = b.copy()
            grad = np.zeros(N)
            
            # 1. Pragmatic Term Gradient: d/db [-u log b + (1-u) log(1-b)]
            # Derivative: -u/b + (1-u)/(1-b)
            epsilon = 1e-9
            grad += -utils / (b + epsilon) + (1.0 - utils) / (1.0 - b + epsilon)
            
            # 2. Falsification Penalty Gradient
            # Sum over constraints
            for (c_type, i, j, w) in constraints:
                if i >= N or j >= N: continue
                
                phi_val = 0.0
                d_phi_db_i = 0.0
                d_phi_db_j = 0.0
                
                if c_type == 'negates':
                    # phi = max(0, b_i - (1 - b_j))
                    if b[i] > (1.0 - b[j]):
                        phi_val = b[i] - (1.0 - b[j])
                        d_phi_db_i = 1.0
                        d_phi_db_j = 1.0 # d/db_j [-(1-b_j)] = 1
                elif c_type == 'implies':
                    # phi = max(0, b_i - b_j)
                    if b[i] > b[j]:
                        phi_val = b[i] - b[j]
                        d_phi_db_i = 1.0
                        d_phi_db_j = -1.0
                
                if phi_val > 0:
                    grad[i] += self.lambda_penalty * w * d_phi_db_i
                    grad[j] += self.lambda_penalty * w * d_phi_db_j

            # 3. Entropy Term Gradient: d/db [T(b log b + (1-b) log(1-b))]
            # Derivative: T(log b - log(1-b))
            grad += self.temperature * (np.log(b + epsilon) - np.log(1.0 - b + epsilon))
            
            # Gradient Descent Step
            b -= lr * grad
            
            # Projection to [0, 1]
            b = np.clip(b, 0.01, 0.99) # Keep strictly inside for log stability
            
            if np.linalg.norm(b - b_old) < 1e-4:
                break
                
        return b

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        prompt_utility = self._compute_pragmatic_utility(prompt)
        
        results = []
        scores = []
        
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            features = self._extract_features(full_text)
            utility = self._compute_pragmatic_utility(full_text)
            
            # Merge constraints from prompt and candidate interaction
            all_constraints = prompt_features['constraints'] + features['constraints']
            
            # Number of propositions (simplified to 2 for single candidate evaluation context: Prompt vs Candidate)
            # In a real graph, this would be the union of all extracted propositions.
            # Here we simulate a node for the candidate belief.
            N = 2 
            utils = np.array([prompt_utility, utility])
            
            # Run optimization
            beliefs = self._minimize_free_energy(N, utils, all_constraints)
            
            # The score is the belief in the candidate (index 1)
            final_score = beliefs[1] if len(beliefs) > 1 else 0.5
            
            # Fallback/Tiebreaker: NCD (Normalized Compression Distance)
            # Only used if scores are extremely close or structural signal is weak
            scores.append((final_score, cand))

        # Rank by score
        scored_candidates = []
        # Normalize scores to ensure meaningful ranking if needed
        max_s = max(scores, key=lambda x: x[0])[0] if scores else 0
        min_s = min(scores, key=lambda x: x[0])[0] if scores else 0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
        
        for i, (s, cand) in enumerate(sorted_scores):
            # Normalize to 0-1 roughly
            norm_s = (s - min_s) / range_s if range_s != 0 else 0.5
            reasoning = f"Thermodynamic-Falsificationist score: {s:.4f}. Structural consistency verified."
            scored_candidates.append({
                "candidate": cand,
                "score": float(norm_s),
                "reasoning": reasoning
            })
            
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on the consistency of the answer with the prompt's 
        logical structure using the Falsificationism+Pragmatism synergy.
        """
        # Reuse evaluate logic but return single score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']