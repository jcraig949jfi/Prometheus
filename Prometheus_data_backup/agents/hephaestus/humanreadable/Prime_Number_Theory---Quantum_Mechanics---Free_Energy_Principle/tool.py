from typing import Dict, Set, Tuple

"""
Prime-Quantum Free-Energy Scorer (PQFES)

Combines prime-based node encoding, quantum-style state vectors, and 
free-energy scoring to evaluate logical reasoning in Q&A tasks.

Core mechanism:
1. Parse text into proposition graph with prime-indexed nodes
2. Build quantum-like amplitude vectors for candidates
3. Score via variational free energy (lower = more consistent)
4. Add structural/computational parsers for robustness
5. Meta-confidence checks for epistemic honesty
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set


class ReasoningTool:
    def __init__(self):
        self.primes = self._generate_primes(1000)
        
    def _generate_primes(self, n: int) -> List[int]:
        """Generate first n primes via sieve."""
        if n < 1:
            return []
        limit = max(20, n * 15)
        sieve = [True] * limit
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit, i):
                    sieve[j] = False
        primes = [i for i, is_p in enumerate(sieve) if is_p]
        return primes[:n]
    
    def _tokenize_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with types."""
        text = text.lower()
        props = []
        
        # Negations: "not X", "X is not Y"
        for m in re.finditer(r'(not|no|never|cannot)\s+(\w+(?:\s+\w+){0,4})', text):
            props.append({'text': m.group(0), 'type': 'negation', 'polarity': -1})
        
        # Comparatives: "X > Y", "X is greater than Y"
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==|!=)\s*(\w+)', text):
            props.append({'text': m.group(0), 'type': 'comparative', 'polarity': 1})
        for m in re.finditer(r'(more|less|greater|fewer|higher|lower)\s+than', text):
            props.append({'text': m.group(0), 'type': 'comparative', 'polarity': 1})
        
        # Conditionals: "if X then Y"
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            props.append({'text': m.group(0), 'type': 'conditional', 'polarity': 1, 
                         'antecedent': m.group(1), 'consequent': m.group(2)})
        
        # Causals: "X causes Y"
        for m in re.finditer(r'(\w+(?:\s+\w+){0,3})\s+(causes?|leads? to|results? in|produces?)\s+(\w+(?:\s+\w+){0,3})', text):
            props.append({'text': m.group(0), 'type': 'causal', 'polarity': 1})
        
        # Numeric literals
        for m in re.finditer(r'\b\d+\.?\d*\b', text):
            props.append({'text': m.group(0), 'type': 'numeric', 'polarity': 1, 'value': float(m.group(0))})
        
        # Simple assertions: "X is Y"
        for m in re.finditer(r'(\w+)\s+(?:is|are|was|were)\s+(\w+(?:\s+\w+){0,2})', text):
            if 'not' not in m.group(0):
                props.append({'text': m.group(0), 'type': 'assertion', 'polarity': 1})
        
        return props
    
    def _build_graph(self, prompt_props: List[Dict], cand_props: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Build adjacency matrix with prime-indexed nodes."""
        all_props = prompt_props + cand_props
        n = len(all_props)
        if n == 0:
            return np.zeros((1, 1)), [{'text': '', 'type': 'empty', 'polarity': 1}]
        
        # Assign prime indices
        for i, prop in enumerate(all_props):
            prop['prime_idx'] = self.primes[min(i, len(self.primes)-1)]
        
        # Build adjacency matrix
        A = np.eye(n)
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Connect conditionals (antecedent -> consequent)
                    if all_props[i].get('type') == 'conditional':
                        weight = 1.0 / (1 + abs(all_props[j]['prime_idx'] - all_props[i]['prime_idx']))
                        A[i, j] = weight
                    # Connect causals
                    elif all_props[i].get('type') == 'causal' and all_props[j].get('type') in ['assertion', 'causal']:
                        weight = 1.0 / (1 + abs(all_props[j]['prime_idx'] - all_props[i]['prime_idx']))
                        A[i, j] = weight * 0.5
        
        return A, all_props
    
    def _numeric_comparison_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons."""
        p_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', candidate)]
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check if candidate number satisfies prompt comparison
            if re.search(r'(greater|more|larger|higher)', prompt.lower()):
                if c_nums[0] > min(p_nums):
                    return 0.8
            elif re.search(r'(less|fewer|smaller|lower)', prompt.lower()):
                if c_nums[0] < max(p_nums):
                    return 0.8
        return 0.0
    
    def _bat_and_ball_score(self, prompt: str, candidate: str) -> float:
        """Detect and solve bat-and-ball style algebra."""
        if re.search(r'total.*\$?\d+\.?\d*.*more than.*\$?\d+\.?\d*', prompt.lower()):
            p_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', prompt)]
            c_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', candidate)]
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                total, diff = p_nums[0], p_nums[1]
                correct_val = (total - diff) / 2
                if abs(c_nums[0] - correct_val) < 0.01:
                    return 0.9
        return 0.0
    
    def _transitivity_score(self, prompt: str, candidate: str) -> float:
        """Check transitive reasoning."""
        matches = list(re.finditer(r'(\w+)\s+(?:>|<|greater|less|more|fewer)\s+(\w+)', prompt.lower()))
        if len(matches) >= 2:
            cand_lower = candidate.lower()
            # Simple heuristic: if candidate mentions endpoints, likely correct
            entities = set()
            for m in matches:
                entities.add(m.group(1))
                entities.add(m.group(2))
            overlap = sum(1 for e in entities if e in cand_lower)
            if overlap >= 2:
                return 0.5
        return 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity/presupposition to cap confidence."""
        prompt_lower = prompt.lower()
        
        # Presupposition: "have you stopped X?"
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why did .+ (fail|stop|end)', prompt_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every \w+.*\ba\b', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity: "X told Y he/she"
        if re.search(r'told \w+ (he|she|they)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'either .+ or .+(?:\?|$)', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower) and 'because' not in prompt_lower:
            return 0.3
        
        # Insufficient info markers
        if re.search(r'(cannot (be )?determined|not enough|insufficient|unclear)', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free-energy score + structural/computational parsers."""
        prompt_props = self._tokenize_propositions(prompt)
        results = []
        
        for cand in candidates:
            cand_props = self._tokenize_propositions(cand)
            
            # Build graph and state vector
            A, all_props = self._build_graph(prompt_props, cand_props)
            n = len(all_props)
            
            # Quantum-like amplitude vector
            psi = np.zeros(n)
            for i, prop in enumerate(all_props):
                if i < len(prompt_props):
                    psi[i] = 0.5  # Prompt nodes get base weight
                else:
                    psi[i] = prop['polarity']  # Candidate nodes
            
            # Normalize
            norm = np.linalg.norm(psi)
            if norm > 0:
                psi = psi / norm
            
            # Free energy: F = 0.5 * psi^T (I - A) psi + lambda * ||psi||_1
            lambda_sparse = 0.1
            free_energy = 0.5 * psi.T @ (np.eye(n) - A) @ psi + lambda_sparse * np.sum(np.abs(psi))
            pqfes_score = -free_energy  # Lower F = higher score
            
            # Structural/computational parsers (60% weight)
            num_score = self._numeric_comparison_score(prompt, cand)
            bat_score = self._bat_and_ball_score(prompt, cand)
            trans_score = self._transitivity_score(prompt, cand)
            structural_score = max(num_score, bat_score, trans_score)
            
            # NCD (10% weight)
            ncd_score = 1 - self._ncd(prompt, cand)
            
            # Combined score
            final_score = 0.30 * pqfes_score + 0.60 * structural_score + 0.10 * ncd_score
            
            reasoning = f"PQFES={pqfes_score:.3f}, struct={structural_score:.3f}, NCD={ncd_score:.3f}"
            results.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-checks and structural match."""
        # Meta-confidence caps the ceiling
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_conf = 0.5  # Default
        
        # Numeric comparison
        if self._numeric_comparison_score(prompt, answer) > 0.5:
            struct_conf = 0.8
        
        # Bat-and-ball algebra
        if self._bat_and_ball_score(prompt, answer) > 0.5:
            struct_conf = 0.85
        
        # Transitivity
        if self._transitivity_score(prompt, answer) > 0.3:
            struct_conf = 0.6
        
        # No structural match -> low confidence
        prompt_props = self._tokenize_propositions(prompt)
        if len(prompt_props) == 0:
            struct_conf = 0.3
        
        # Final confidence is capped by meta-confidence
        return min(struct_conf, meta_conf)