import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Information Theory, Abductive Reasoning, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts logical atoms (negations, conditionals, comparatives, causals, 
       numerics, ordering, quantifiers) using regex to form a structured representation.
    2. Feature Vectorization: Maps atoms to a binary vector space.
    3. Information-Theoretic Scoring: Estimates Mutual Information I(C; H) as the base score,
       treating atoms as Bernoulli variables. High MI implies the hypothesis explains the context well.
    4. Pragmatic Penalties: Applies Gricean penalties (Quantity, Relevance, Quality, Manner)
       to deduct points for verbosity, irrelevance, contradictions, or complexity.
    5. Ranking: Candidates are ranked by Final Score = MI - Penalties.
    """

    # Regex patterns for atom extraction
    PATTERNS = {
        'negation': [r'\b(not|no|never|none|neither)\b', r'¬'],
        'conditional': [r'\b(if|then|unless|provided|implies)\b', r'→'],
        'comparative': [r'\b(more|less|greater|smaller|higher|lower)\b', r'[<>]=?'],
        'causal': [r'\b(causes|leads to|results in|because|due to)\b'],
        'numeric': [r'\d+(\.\d+)?'],
        'ordering': [r'\b(before|after|first|last|precede|follow)\b'],
        'quantifier': [r'\b(all|some|every|each|any|most)\b']
    }

    def __init__(self):
        # Compile regexes for efficiency
        self.compiled_patterns = {}
        for atom_type, patterns in self.PATTERNS.items():
            self.compiled_patterns[atom_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Pragmatic weights
        self.lambda_qty = 0.5
        self.lambda_rel = 0.3
        self.lambda_qual = 1.0
        self.lambda_man = 0.1
        self.tau_qty = 2  # Tolerance for extra atoms

    def _extract_atoms(self, text: str) -> Dict[str, List[Tuple]]:
        """Extract propositional atoms tagged by type."""
        atoms = {k: [] for k in self.PATTERNS.keys()}
        text_lower = text.lower()
        
        # Extract specific types
        for atom_type, regexes in self.compiled_patterns.items():
            for regex in regexes:
                for match in regex.finditer(text):
                    val = match.group()
                    # Determine polarity (simple heuristic: check for double negation nearby)
                    polarity = 1
                    if atom_type == 'negation':
                        polarity = -1
                    
                    atoms[atom_type].append((atom_type, polarity, val))
        
        # Special handling for numeric comparisons (simplified)
        nums = re.findall(r'(\d+(?:\.\d+)?)', text)
        if len(nums) >= 2:
            # Check for explicit comparison operators nearby
            if re.search(r'[<>]=?', text) or any(w in text_lower for w in ['greater', 'less', 'more', 'smaller']):
                atoms['numeric'].append(('numeric', 1, f"{nums[0]} vs {nums[1]}"))

        return atoms

    def _atoms_to_vector(self, atoms: Dict[str, List]) -> np.ndarray:
        """Convert atom dictionary to a binary feature vector."""
        vector = []
        # Order: negation, conditional, comparative, causal, numeric, ordering, quantifier
        keys = ['negation', 'conditional', 'comparative', 'causal', 'numeric', 'ordering', 'quantifier']
        for k in keys:
            vector.append(1 if atoms[k] else 0)
        return np.array(vector, dtype=float)

    def _check_contradiction(self, context_atoms: Dict, hyp_atoms: Dict) -> int:
        """Simple contradiction check (Quality penalty)."""
        contradictions = 0
        # If context has negation of X and hypothesis asserts X (simplified)
        ctx_negs = set([a[2].lower() for a in context_atoms.get('negation', [])])
        hyp_asserts = set([a[2].lower() for a in hyp_atoms.get('negation', [])]) # Simplified logic
        
        # Heuristic: If prompt says "not X" and answer implies "X" without negation context
        # Since full logic is hard with regex, we penalize length mismatch in negation counts as proxy
        ctx_neg_count = len(context_atoms.get('negation', []))
        hyp_neg_count = len(hyp_atoms.get('negation', []))
        
        if ctx_neg_count == 0 and hyp_neg_count > 2:
            contradictions += 1 # Suspicious over-negation
            
        return contradictions

    def _calculate_mi(self, v_c: np.ndarray, v_h: np.ndarray) -> float:
        """
        Estimate Mutual Information I(C; H) ≈ sum(v_c * v_h) / (|C| + |H|).
        Simplified for single-instance estimation without external corpus.
        """
        intersection = np.sum(v_c * v_h)
        union = np.sum(np.maximum(v_c, v_h))
        if union == 0:
            return 0.0
        # Normalized overlap as proxy for MI in this sparse setting
        return intersection / (union + 1e-9)

    def _gricean_penalties(self, c_atoms: Dict, h_atoms: Dict, c_vec: np.ndarray, h_vec: np.ndarray, h_text: str) -> float:
        """Calculate pragmatic penalties."""
        penalty = 0.0
        
        # 1. Quantity: Penalize if hypothesis has significantly more atoms than context
        c_count = sum(len(v) for v in c_atoms.values())
        h_count = sum(len(v) for v in h_atoms.values())
        if h_count > c_count + self.tau_qty:
            penalty += self.lambda_qty * (h_count - c_count - self.tau_qty)
            
        # 2. Relevance: 1 - Cosine Similarity
        norm_c = np.linalg.norm(c_vec)
        norm_h = np.linalg.norm(h_vec)
        if norm_c > 0 and norm_h > 0:
            cosine_sim = np.dot(c_vec, h_vec) / (norm_c * norm_h)
            penalty += self.lambda_rel * (1.0 - cosine_sim)
        else:
            penalty += self.lambda_rel # Max penalty if empty
            
        # 3. Quality: Contradictions
        contradictions = self._check_contradiction(c_atoms, h_atoms)
        penalty += self.lambda_qual * contradictions
        
        # 4. Manner: Complexity (avg clause length approximation via word count / sentence count)
        words = len(h_text.split())
        sentences = max(1, h_text.count('.') + h_text.count('!') + h_text.count('?'))
        avg_clause = words / sentences
        if avg_clause > 20: # Penalize overly long sentences
            penalty += self.lambda_man * (avg_clause - 20) / 10.0
            
        return penalty

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Compute final score and reasoning string."""
        c_atoms = self._extract_atoms(prompt)
        h_atoms = self._extract_atoms(candidate)
        
        c_vec = self._atoms_to_vector(c_atoms)
        h_vec = self._atoms_to_vector(h_atoms)
        
        # Abductive Score (Mutual Information)
        mi_score = self._calculate_mi(c_vec, h_vec)
        
        # Pragmatic Penalties
        penalties = self._gricean_penalties(c_atoms, h_atoms, c_vec, h_vec, candidate)
        
        final_score = mi_score - penalties
        
        # Reasoning summary
        reasons = []
        if mi_score > 0.5: reasons.append("High structural overlap")
        elif mi_score > 0: reasons.append("Moderate structural overlap")
        else: reasons.append("Low structural overlap")
        
        if penalties > 0.5: reasons.append("Significant pragmatic violations")
        if c_vec.sum() == 0 and h_vec.sum() == 0: 
            # Fallback to NCD if no structural features found
            import zlib
            data = prompt.encode() + candidate.encode()
            comp = len(zlib.compress(data))
            max_comp = max(len(zlib.compress(prompt.encode())), len(zlib.compress(candidate.encode())), 1)
            ncd = (comp - max_comp) / max_comp
            final_score = -ncd # Lower NCD is better, so negate
            reasons = ["No structural features detected; using compression baseline"]

        return final_score, "; ".join(reasons) if reasons else "Standard evaluation"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative scoring against a dummy negative."""
        # Generate a trivial negative candidate to compare against
        negative_candidate = "The answer is unrelated and incorrect."
        
        pos_score, _ = self._score_candidate(prompt, answer)
        neg_score, _ = self._score_candidate(prompt, negative_candidate)
        
        # Softmax-like normalization between positive and negative reference
        # If pos >> neg, confidence -> 1. If pos << neg, confidence -> 0.
        diff = pos_score - neg_score
        # Sigmoid mapping
        conf = 1.0 / (1.0 + math.exp(-diff * 2.0))
        return max(0.0, min(1.0, conf))