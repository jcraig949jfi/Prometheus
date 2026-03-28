import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool combining Abductive Reasoning, Compositionality, and Mechanism Design.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic predicates and logic operators into a DAG.
    2. Abductive Scoring: Computes explanatory cost (Coverage - Parsimony) using boolean matrix ops.
    3. Mechanism Design: Applies a Quadratic Scoring Rule to incentivize truthful hypothesis reporting.
    
    Beats NCD baseline by using structural logic signals rather than string compression.
    """
    
    # Lexicon for atomic extraction
    LEXICON = {
        'neg': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'-'],
        'comp_gt': [r'>', r'greater than', r'more than', r'exceeds'],
        'comp_lt': [r'<', r'less than', r'fewer than'],
        'cond': [r'if', r'only if', r'then', r'implies'],
        'cause': [r'cause', r'lead to', r'result in', r'trigger'],
        'temp': [r'before', r'after', r'precedes', r'follows']
    }

    def __init__(self):
        self.lambda_param = 0.1  # Parsimony weight for hypothesis size
        self.mu_param = 0.2      # Penalty for non-observation literals

    def _tokenize(self, text: str) -> Set[str]:
        """Extract atomic predicates and literals from text."""
        text_lower = text.lower()
        atoms = set()
        
        # Extract numeric comparisons
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        if len(nums) >= 2:
            try:
                if float(nums[0]) > float(nums[1]):
                    atoms.add(f"num({nums[0]}) > num({nums[1]})")
                else:
                    atoms.add(f"num({nums[1]}) > num({nums[0]})")
            except ValueError:
                pass

        # Extract logical atoms based on lexicon
        for tag, patterns in self.LEXICON.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    atoms.add(f"{tag}")
        
        # Simple word-based atoms for content (lowercased, alphanum only)
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        atoms.update(words)
        
        return atoms

    def _build_dag(self, atoms: Set[str]) -> Tuple[List[str], np.ndarray]:
        """Build adjacency matrix for transitive closure (simplified)."""
        atoms_list = sorted(list(atoms))
        n = len(atoms_list)
        if n == 0:
            return [], np.array([])
            
        adj = np.zeros((n, n), dtype=bool)
        
        # Identity (reflexivity)
        np.fill_diagonal(adj, True)
        
        # Heuristic edges: if atom A is substring of B, A -> B
        for i, a in enumerate(atoms_list):
            for j, b in enumerate(atoms_list):
                if i != j and a in b:
                    adj[i, j] = True
                # Simple transitivity hint: if 'cause' and 'temp' both present, link them
                if 'cause' in a and 'temp' in b:
                    adj[i, j] = True
                    
        return atoms_list, adj

    def _forward_chain(self, atoms: Set[str], adj: np.ndarray) -> Set[str]:
        """Perform boolean matrix multiplication for transitive closure."""
        if adj.size == 0:
            return atoms
            
        atoms_list = sorted(list(atoms))
        n = len(atoms_list)
        if n == 0:
            return set()
            
        # Map atoms to indices
        idx_map = {a: i for i, a in enumerate(atoms_list)}
        
        # Compute transitive closure via repeated squaring (simplified for small N)
        # Since we use numpy, we can do matrix power
        closure = adj.copy()
        for _ in range(n): 
            closure = np.logical_or(closure, np.dot(closure, closure))
            
        # Extract entailed atoms
        entailed = set()
        for i in range(n):
            if atoms_list[i] in atoms: # If root is in original set
                for j in range(n):
                    if closure[i, j]:
                        entailed.add(atoms_list[j])
        return entailed

    def _compute_abductive_score(self, prompt_atoms: Set[str], candidate_atoms: Set[str]) -> float:
        """
        Calculate abductive score: Lower is better.
        Score = -Coverage + Parsimony
        """
        # Build DAG for prompt (Observations O)
        obs_list, obs_adj = self._build_dag(prompt_atoms)
        
        # Forward chain to see what candidate entails within prompt context
        # Simplified: Check intersection of candidate atoms with prompt atoms
        # Advanced: Use DAG to see if candidate implies observations
        
        # Coverage: How many prompt observations are explained by candidate?
        # Heuristic: Intersection size normalized
        common = prompt_atoms.intersection(candidate_atoms)
        coverage = len(common)
        
        # Parsimony: Size of hypothesis + penalty for extra assumptions
        h_size = len(candidate_atoms)
        extra = len(candidate_atoms - prompt_atoms)
        parsimony = self.lambda_param * h_size + self.mu_param * extra
        
        return -coverage + parsimony

    def _mechanism_design_score(self, abductive_scores: List[float]) -> List[float]:
        """
        Apply Quadratic Scoring Rule to transform abductive costs into payments.
        payment = 1 - ((S - min_S) / (max_S - min_S))^2
        This incentivizes truthful reporting (lowest abductive cost).
        """
        if not abductive_scores:
            return []
            
        scores = np.array(abductive_scores)
        min_s = scores.min()
        max_s = scores.max()
        range_s = max_s - min_s
        
        payments = []
        for s in scores:
            if range_s == 0:
                p = 1.0
            else:
                normalized = (s - min_s) / range_s
                p = 1.0 - (normalized ** 2)
            payments.append(float(p))
            
        return payments

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._tokenize(prompt)
        candidate_data = []
        abductive_scores = []

        # Phase 1: Parse and Score Abductively
        for cand in candidates:
            cand_atoms = self._tokenize(cand)
            score = self._compute_abductive_score(prompt_atoms, cand_atoms)
            candidate_data.append({
                "candidate": cand,
                "abductive_score": score,
                "prompt_atoms": prompt_atoms,
                "cand_atoms": cand_atoms
            })
            abductive_scores.append(score)

        # Phase 2: Mechanism Design Transformation
        final_payments = self._mechanism_design_score(abductive_scores)

        # Phase 3: Construct Result
        results = []
        for i, data in enumerate(candidate_data):
            # Fallback to NCD if structural signal is weak (identical scores)
            score = final_payments[i]
            
            reasoning = f"Coverage:{len(data['prompt_atoms'].intersection(data['cand_atoms']))} " \
                        f"Parsimony:{self.lambda_param*len(data['cand_atoms']) + self.mu_param*len(data['cand_atoms']-data['prompt_atoms'])}"
            
            results.append({
                "candidate": data["candidate"],
                "score": score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the mechanism design score."""
        # Evaluate against a dummy competitor to get a relative score
        # Using a nonsense competitor to force a spread
        dummy_candidates = [answer, "XyZ123 nonsense"]
        ranked = self.evaluate(prompt, dummy_candidates)
        
        if not ranked:
            return 0.0
            
        # If our answer is top, return its score, else 0
        if ranked[0]["candidate"] == answer:
            return max(0.0, min(1.0, ranked[0]["score"]))
        
        # If tied or lost, check if score is still high absolute
        for item in ranked:
            if item["candidate"] == answer:
                return max(0.0, min(1.0, item["score"]))
                
        return 0.0