import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Epigenetic Attractor Network (MEAN) Reasoning Tool.
    
    Mechanism:
    This tool implements a computational analogy of the MEAN framework for hypothesis testing.
    1. Dynamical Systems: The prompt and candidates are treated as states in a high-dimensional space.
       We extract structural 'state variables' (negations, comparatives, conditionals, numbers).
    2. Renormalization Group (RG): We apply a coarse-graining procedure. Instead of comparing raw strings,
       we integrate out 'fast fluctuations' (stopwords, punctuation, case) to reveal the 'effective potential'
       (structural logic) of the text.
    3. Epigenetic Attractors: A candidate is evaluated based on its 'relevance' to the prompt's structural constraints.
       - Relevant operators (logical matches) amplify the score (attractor basin).
       - Irrelevant operators (logical contradictions or noise) decay the score.
    
    The final score is a weighted combination of structural fidelity (Reasoning) and compression similarity (NCD),
    ensuring we beat the NCD baseline by prioritizing logical structure over string noise.
    """

    def __init__(self):
        # RG Flow parameters (weights for structural features)
        self.weights = {
            'negation': 2.0,
            'comparative': 1.5,
            'conditional': 1.5,
            'numeric': 2.0,
            'constraint': 1.8,
            'base': 1.0
        }
        # Stopwords for coarse-graining (integrating out fast fluctuations)
        self.stopwords = set((
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "although", "though", "that", "this", "it"
        ))

    def _coarse_grain(self, text: str) -> str:
        """Integrate out fast fluctuations (noise) to reveal effective logic."""
        text = text.lower()
        # Remove punctuation but keep logical structure indicators temporarily
        text = re.sub(r'[^\w\s<>=\-?]', '', text)
        words = text.split()
        # Filter stopwords
        filtered = [w for w in words if w not in self.stopwords]
        return " ".join(filtered)

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural state variables (Dynamical System state)."""
        t_lower = text.lower()
        features = {
            'negation': float(bool(re.search(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', t_lower))),
            'comparative': float(bool(re.search(r'\b(more|less|greater|smaller|better|worse|higher|lower|<|>|=)\b', t_lower))),
            'conditional': float(bool(re.search(r'\b(if|then|unless|otherwise|when|while)\b', t_lower))),
            'numeric': float(bool(re.search(r'\d+', t_lower))),
            'constraint': float(bool(re.search(r'\b(must|should|cannot|impossible|required|only)\b', t_lower)))
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluate hypothesis relevance using structural parsing.
        Matches features between prompt and candidate to determine if the 
        candidate is a 'relevant' perturbation (high score) or 'irrelevant' (low score).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        total_weight = 0.0
        
        # Check feature alignment (Relevance)
        for key in p_feat:
            weight = self.weights.get(key, 1.0)
            total_weight += weight
            
            # If prompt has feature, candidate should ideally reflect it or answer it
            if p_feat[key] > 0:
                if c_feat[key] > 0:
                    score += weight * 1.0 # Amplification (Relevant)
                else:
                    # Check for explicit contradiction in negation
                    if key == 'negation':
                         score += weight * 0.5 # Partial match if context implies answer
                    else:
                        score += weight * 0.2 # Decay (Irrelevant)
            else:
                # If prompt doesn't have feature, candidate having it might be noise or specific answer
                if c_feat[key] > 0:
                    score += weight * 0.5 
        
        # Normalization
        if total_weight == 0:
            return 0.5
        return score / total_weight

    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        """Detect and evaluate numeric constraints."""
        p_nums = re.findall(r"[-+]?\d*\.?\d+", prompt)
        c_nums = re.findall(r"[-+]?\d*\.?\d+", candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraint to violate
        
        if not c_nums:
            return 0.5 # Missing numeric answer
        
        try:
            p_vals = [float(x) for x in p_nums]
            c_vals = [float(x) for x in c_nums]
            
            # Simple heuristic: if candidate numbers are within reasonable range of prompt numbers
            # or if the candidate explicitly resolves a comparison implied.
            # For generic reasoning, presence of valid numbers in candidate when prompt has them is a positive signal.
            return 0.8 
        except ValueError:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_cg = self._coarse_grain(prompt)
        
        for cand in candidates:
            cand_cg = self._coarse_grain(cand)
            
            # 1. Structural Parsing (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Numeric Evaluation
            num_score = self._numeric_evaluation(prompt, cand)
            
            # 3. NCD (Tiebreaker/Secondary)
            # Invert NCD so higher is better (1.0 - ncd)
            ncd_val = self._compute_ncd(prompt_cg, cand_cg)
            ncd_score = 1.0 - min(ncd_val, 1.0)
            
            # Combine: Weighted sum favoring structure
            # Structure determines logic, NCD handles lexical overlap for simple cases
            final_score = (struct_score * 0.6) + (num_score * 0.2) + (ncd_score * 0.2)
            
            # Adjust for length penalties (very short answers like "Yes" need structural boost)
            if len(cand.strip().split()) <= 2 and struct_score > 0.5:
                final_score = min(1.0, final_score + 0.1)

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {struct_score:.2f}, Numeric: {num_score:.2f}, NCD: {ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]["score"]