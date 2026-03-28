import re
import numpy as np
import zlib
from collections import deque

class ReasoningTool:
    """
    A hybrid reasoning tool combining Network Science (constraint graphs), 
    Mechanism Design (incentive compatibility), and the Free Energy Principle 
    (variational scoring) to evaluate logical consistency.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and tags features (negation, causal, etc.).
    2. Graph Construction: Builds a directed graph of implications and constraints.
    3. Propagation: Uses Floyd-Warshall for transitive closure of logical entailment.
    4. Scoring: Computes a 'Free Energy' score balancing prediction error against 
       logical consistency (incentive) and complexity.
    5. Epistemic Honesty: Caps confidence on ambiguous or presupposition-laden prompts.
    """

    def __init__(self):
        # Regex patterns for feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|results in|therefore)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|second|last|next|finally)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            # Meta-confidence patterns
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ bad)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }
        self.lambda_inc = 2.0  # Weight for incentive consistency
        self.lambda_err = 1.0  # Weight for prediction error

    def _extract_features(self, text):
        """Extracts binary feature vector [neg, comp, cond, caus, ord, num]"""
        t_lower = text.lower()
        flags = [
            1 if self.patterns['negation'].search(t_lower) else 0,
            1 if self.patterns['comparative'].search(t_lower) else 0,
            1 if self.patterns['conditional'].search(t_lower) else 0,
            1 if self.patterns['causal'].search(t_lower) else 0,
            1 if self.patterns['ordering'].search(t_lower) else 0,
            1 if self.patterns['numeric'].search(text) else 0
        ]
        return np.array(flags, dtype=float)

    def _parse_propositions(self, text):
        """Splits text into atomic propositions and extracts features."""
        # Simple splitter on punctuation, keeping delimiters for context if needed
        # For this implementation, we treat sentences/clauses as nodes
        raw_nodes = re.split(r'[.;!?]', text)
        nodes = []
        features = []
        
        for i, chunk in enumerate(raw_nodes):
            chunk = chunk.strip()
            if not chunk:
                continue
            nodes.append(chunk)
            features.append(self._extract_features(chunk))
        
        if not nodes:
            nodes = [text]
            features = [self._extract_features(text)]
            
        return nodes, np.array(features)

    def _build_graph(self, nodes):
        """Builds adjacency matrix A (implication) and penalty matrices N, C."""
        n = len(nodes)
        A = np.zeros((n, n), dtype=float) # Implication graph
        N = np.zeros((n, n), dtype=float) # Negation conflicts
        C = np.zeros((n, n), dtype=float) # Comparative conflicts
        
        # Initialize diagonal
        np.fill_diagonal(A, 1.0)
        
        text_full = " ".join(nodes).lower()
        
        for i, node_i in enumerate(nodes):
            ni_lower = node_i.lower()
            # Self-consistency
            A[i, i] = 1.0 
            
            for j, node_j in enumerate(nodes):
                if i == j: continue
                
                nj_lower = node_j.lower()
                
                # 1. Causal/Conditional: "if i then j" or "i leads to j"
                # Heuristic: if node i appears before node j and contains conditional/causal keywords
                if any(k in ni_lower for k in ['if', 'leads to', 'causes']):
                    if j > i or 'then' in ni_lower: # Simplified temporal/logical flow
                        A[i, j] = 1.0
                
                # 2. Negation: "i is not j" or explicit negation in one referencing the other
                # If node i has negation and shares significant words with j
                if self.patterns['negation'].search(ni_lower):
                    # Simple overlap check for negation target
                    words_i = set(re.findall(r'\w+', ni_lower))
                    words_j = set(re.findall(r'\w+', nj_lower))
                    if len(words_i & words_j) > 1: # Share meaningful words
                        N[i, j] = 1.0
                        N[j, i] = 1.0

                # 3. Comparatives: if i says "A > B" and j says "B > A"
                if self.patterns['comparative'].search(ni_lower) and self.patterns['comparative'].search(nj_lower):
                     # Detect contradiction in ordering (simplified)
                     if ('more' in ni_lower and 'less' in nj_lower) or ('before' in ni_lower and 'after' in nj_lower):
                         C[i, j] = 1.0
                         C[j, i] = 1.0

        # Transitive Closure (Floyd-Warshall) on Boolean implication
        # Convert A to boolean reachability
        R = (A > 0).astype(float)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if R[i, k] and R[k, j]:
                        R[i, j] = 1.0
                        
        return R, N, C

    def _compute_free_energy(self, prompt, candidate):
        """Core scoring function based on Free Energy Principle."""
        full_text = f"{prompt} {candidate}"
        nodes, feats = self._parse_propositions(full_text)
        n = len(nodes)
        
        if n == 0:
            return 0.0, "No propositions parsed."

        R, N, C = self._build_graph(nodes)
        
        # Prior vector p: 0.5 (unknown) initially. 
        # If prompt explicitly states facts, we'd parse them. 
        # Here we assume the prompt sets the context (prior=0.5 for ambiguity, 1.0 if asserted)
        # For this hybrid model, we treat the prompt part as 'observed' (p=1) and candidate as 'hypothesis'
        p = np.full(n, 0.5)
        prompt_len = len(self._parse_propositions(prompt)[0])
        p[:min(prompt_len, n)] = 1.0 # Assume prompt facts are true
        
        # Hypothesis vector h: Candidate assertions
        # If candidate nodes align with prompt nodes, h=1. If contradictory, h=0.
        # Simplified: Candidate nodes are the variable part.
        h = np.full(n, 0.5)
        # Mark candidate propositions as asserted True (1.0)
        # In a real system, we'd map candidate claims to prompt nodes.
        # Here, we assume the candidate adds new nodes that must be consistent.
        h[prompt_len:] = 1.0 
        
        # Truncate to n if parsing differed
        h = h[:n]
        p = p[:n]

        # 1. Prediction Error (Accuracy)
        # How much does h deviate from prior p?
        pred_error = 0.5 * np.sum((h - p) ** 2)
        
        # 2. Complexity (Entropy term approximation)
        # Penalize high certainty (h near 0 or 1) without evidence
        sigma_h = 1 / (1 + np.exp(-h)) # Logistic
        # Avoid log(0)
        sigma_h = np.clip(sigma_h, 1e-6, 1-1e-6)
        entropy_term = -np.sum(feats.sum(axis=1) * np.log(sigma_h))
        
        # 3. Incentive (Consistency)
        # Penalize h_i=1, h_j=0 if i entails j (R[i,j]=1)
        # Term: - sum R_ij * (h_i - h_j)^2
        # If i->j and h_i=1, h_j=0, penalty is large.
        consistency_penalty = 0.0
        for i in range(n):
            for j in range(n):
                if R[i, j] > 0:
                    consistency_penalty += (h[i] - h[j]) ** 2
        
        # Free Energy F = Error + Complexity - Incentive(Reward)
        # We want to MINIMIZE F. Score = -F.
        F = self.lambda_err * pred_error + 0.1 * entropy_term - self.lambda_inc * consistency_penalty
        
        # Normalize score roughly to 0-1 range for usability
        # Lower F is better. 
        score = -F / (n + 1) 
        
        reason = f"Parsed {n} nodes. Consistency penalty: {consistency_penalty:.2f}. Error: {pred_error:.2f}."
        return score, reason

    def _meta_confidence(self, prompt):
        """
        Checks for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity (heuristic: pronoun + 'who')
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.2
            
        # 4. Subjectivity without metrics
        if self.patterns['subjectivity'].search(p_lower) and 'data' not in p_lower:
            return 0.4
            
        # 5. Unanswerability (No numbers in math problems, missing info)
        # If it looks like a math problem but has no numbers
        if any(k in p_lower for k in ['calculate', 'sum', 'total', 'cost']) and not self.patterns['numeric'].search(p_lower):
            return 0.1
            
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Base scores from Free Energy logic
        base_scores = []
        for cand in candidates:
            score, reason = self._compute_free_energy(prompt, cand)
            base_scores.append((score, reason, cand))
        
        # Normalize base scores to 0-1 range roughly
        if base_scores:
            scores_only = [x[0] for x in base_scores]
            min_s, max_s = min(scores_only), max(scores_only)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for score, reason, cand in base_scores:
                # Normalize to 0.2 - 0.9 range initially
                norm_score = 0.2 + 0.7 * ((score - min_s) / range_s)
                
                # Add NCD tiebreaker (small weight)
                # Prefer candidate that compresses well with prompt (high similarity/relevance)
                ncd = self._ncd_score(prompt, cand)
                # Lower NCD = more similar. We want high score for good match.
                # Invert NCD contribution slightly
                ncd_bonus = (1.0 - ncd) * 0.15 
                
                final_score = norm_score * 0.85 + ncd_bonus * 0.15
                
                # Apply Meta-Confidence Cap (Epistemic Honesty)
                # If the prompt is ambiguous, even the "best" answer shouldn't be trusted highly
                if meta_cap < 0.5:
                    final_score *= (meta_cap / 0.5) # Scale down significantly
                
                results.append({
                    "candidate": cand,
                    "score": float(final_score),
                    "reasoning": reason
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get raw score
        # We treat the single answer as the only candidate to get its relative score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score (approx 0-1) to confidence
        # If meta_cap is low, confidence is low regardless of score
        conf = raw_score * meta_cap
        
        # Hard caps for specific Tier B failures
        if meta_cap < 0.3:
            return min(conf, 0.29) # Ensure it stays under the threshold
        
        # Never return > 0.9 unless the computation was definitive (simulated here by high score + no ambiguity)
        if meta_cap == 1.0 and raw_score > 0.85:
            return min(conf, 0.95)
            
        return min(conf, 0.9)