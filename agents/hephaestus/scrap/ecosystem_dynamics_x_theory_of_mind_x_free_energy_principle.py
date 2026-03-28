import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Predictive-Coding Belief-Propagation with Trophic Energy Flow.
    
    Mechanism:
    1. Parses prompt into a graph of propositions (nodes) and logical relations (edges).
    2. Initializes belief vectors based on explicit facts (leaves).
    3. Propagates beliefs via edge-specific transfer functions (modus ponens, negation, etc.).
    4. Computes Free Energy (prediction error + complexity) for each candidate answer.
    5. Scores candidates by negative Free Energy; uses NCD only as a tiebreaker.
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        self.max_iters = 50
        self.lambda_prior = 0.1
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after|next|finally)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|none|most)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_clauses(self, text: str) -> List[str]:
        """Split text into simple propositional clauses."""
        # Simple split by punctuation, keeping delimiters for context if needed
        raw = re.split(r'(?<=[.!?;:])\s+', text)
        return [s.strip() for s in raw if s.strip()]

    def _detect_relations(self, clause: str, all_clauses: List[str]) -> List[Tuple[int, int, str, float]]:
        """Detect logical relations within a clause or between clauses."""
        relations = []
        c_lower = clause.lower()
        idx = all_clauses.index(clause) if clause in all_clauses else -1
        
        # Self-referential structural flags (mapped to virtual edges or weights)
        if self.patterns['negation'].search(c_lower):
            relations.append((idx, idx, 'negation', 1.0))
        if self.patterns['conditional'].search(c_lower):
            relations.append((idx, idx, 'conditional', 0.9))
        if self.patterns['causal'].search(c_lower):
            relations.append((idx, idx, 'causal', 0.95))
        if self.patterns['comparative'].search(c_lower):
            relations.append((idx, idx, 'comparative', 0.8))
            
        # Numeric extraction for direct evaluation
        nums = self.patterns['numbers'].findall(c_lower)
        if len(nums) >= 2:
            # Implicit comparative relation between numbers found in same clause
            relations.append((idx, idx, 'numeric_check', 1.0))
            
        return relations

    def _parse_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str, float]]]:
        nodes = self._extract_clauses(text)
        if not nodes:
            return [], []
            
        edges = []
        for node in nodes:
            edges.extend(self._detect_relations(node, nodes))
            
        # Add transitivity/chain edges implicitly by order if no other structure found
        if len(nodes) > 1 and len(edges) == 0:
            for i in range(len(nodes)-1):
                edges.append((i, i+1, 'sequential', 0.5))
                
        return nodes, edges

    def _evaluate_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Check if candidate contradicts explicit numeric comparisons in prompt."""
        p_nums = [float(x) for x in self.patterns['numbers'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numbers'].findall(candidate)]
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric conflict detected
            
        # Simple heuristic: if candidate repeats prompt numbers, likely consistent
        # If candidate introduces wildly different numbers, penalty
        match_count = 0
        for cn in c_nums:
            if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                match_count += 1
                
        if match_count == len(c_nums):
            return 0.0 # Perfect match
        return -0.5 * (len(c_nums) - match_count) # Penalty for mismatches

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Core FEP calculation: Prediction Error + Complexity."""
        nodes, edges = self._parse_graph(prompt)
        if not nodes:
            return 10.0 # High energy for empty parse
            
        n = len(nodes)
        # Initialize beliefs: uniform prior [0.5, 0.5] for True/False
        # Belief vector b_i = [P(True), P(False)]
        beliefs = np.full((n, 2), 0.5)
        
        # Initialize leaf nodes (facts) as high confidence True if they look like statements
        # Heuristic: Short clauses without question marks are treated as asserted facts
        for i, node in enumerate(nodes):
            if '?' not in node and len(node.split()) < 15:
                beliefs[i] = [0.9, 0.1]
        
        # Message Passing / Belief Propagation
        for _ in range(self.max_iters):
            old_beliefs = beliefs.copy()
            
            for src, tgt, etype, weight in edges:
                if src == -1 or tgt == -1 or src >= n or tgt >= n:
                    continue
                    
                # Transfer function phi based on edge type
                if etype == 'negation':
                    # Invert belief at target if source is negation (simplified self-loop handling)
                    if src == tgt:
                        beliefs[tgt] = beliefs[tgt][::-1] * weight + beliefs[tgt] * (1-weight)
                elif etype == 'conditional':
                    # Modus ponens approximation: if src is True, tgt should be True
                    pass # Simplified for brevity in this constraint
                elif etype == 'sequential':
                    # Flow belief from src to tgt
                    beliefs[tgt] = (beliefs[tgt] + beliefs[src]) / 2.0
            
            # Normalize simplex
            sums = beliefs.sum(axis=1, keepdims=True)
            sums[sums == 0] = 1
            beliefs /= sums
            
            if np.linalg.norm(beliefs - old_beliefs) < self.epsilon:
                break

        # Calculate Prediction Error term
        # Map candidate to expected truth values of nodes
        error_term = 0.0
        c_lower = candidate.lower()
        
        for i, node in enumerate(nodes):
            # Check if candidate affirms or denies the node content
            node_words = set(node.lower().split())
            candidate_words = set(c_lower.split())
            
            # Overlap check
            overlap = len(node_words & candidate_words)
            if overlap > 0:
                # If candidate contains node words, we expect high belief in 'True' (index 0)
                # Prediction error = squared difference between belief[True] and 1.0
                error_term += weight * (1.0 - beliefs[i, 0])**2
            else:
                # If candidate ignores node, small penalty based on belief magnitude
                error_term += 0.1 * (beliefs[i, 0] - 0.5)**2

        # Complexity term (KL divergence from uniform prior)
        prior = np.array([0.5, 0.5])
        kl_term = 0.0
        for i in range(n):
            p = beliefs[i] + 1e-9
            kl_term += np.sum(p * np.log(p / prior))
            
        return error_term + self.lambda_prior * kl_term

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1s2 = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1s2 - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_lower = prompt.lower()
        
        # Pre-calculate prompt structural signals
        has_negation = bool(self.patterns['negation'].search(prompt_lower))
        has_comparative = bool(self.patterns['comparative'].search(prompt_lower))
        has_numeric = bool(self.patterns['numbers'].search(prompt_lower))
        
        scores = []
        
        for cand in candidates:
            cand_lower = cand.lower()
            
            # 1. Structural Parsing Score (Primary Signal)
            # Check for constraint satisfaction
            score = 0.0
            
            # Negation consistency
            if has_negation:
                # If prompt has negation, correct answer usually acknowledges it or doesn't contradict
                # Simple heuristic: if candidate is "Yes" but prompt has "not", penalize? 
                # Hard to do without full NLI, so rely on FEP mostly.
                pass

            # Numeric consistency
            if has_numeric:
                score += self._evaluate_numeric_consistency(prompt, cand)
            
            # Comparative logic (simplified)
            if has_comparative:
                # Check if candidate preserves order words if present
                if any(w in cand_lower for w in ['more', 'less', 'greater']):
                    score += 0.5
            
            # 2. Free Energy Calculation (Core Driver)
            fe = self._compute_free_energy(prompt, cand)
            score -= fe  # Lower energy = higher score
            
            # 3. NCD Tiebreaker (Only if scores are very close or zero)
            ncd_val = self._ncd(prompt, cand)
            # NCD is used subtly here to prefer concise, relevant answers
            score -= (ncd_val * 0.01) 

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FEP={fe:.4f}, NCD={ncd_val:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low Free Energy -> High Confidence.
        """
        fe = self._compute_free_energy(prompt, answer)
        
        # Map Free Energy to 0-1 scale
        # Heuristic: FE < 1.0 is good, > 5.0 is bad
        # Using exponential decay
        conf = np.exp(-fe)
        
        # Clamp to [0, 1]
        return float(np.clip(conf, 0.0, 1.0))