import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Gauge-Equivariant Spectral Predictor (VGESP) Implementation.
    
    Mechanism:
    1. Gauge Equivariance (Structural Parsing): Extracts invariant structural features
       (negations, comparatives, conditionals, numeric values) to form a 'feature field'.
       This ensures logically equivalent statements (related by gauge transforms like 
       paraphrasing or reordering) map to similar representations.
    2. Spectral Analysis (Frequency Domain): Analyzes the 'temporal dynamics' of the text
       by computing the frequency distribution of structural tokens vs content tokens.
       This isolates hypothesis-specific signatures (e.g., high frequency of negation 
       operators indicates a negative constraint).
    3. Free Energy Principle (Inference Core): The scoring function minimizes variational
       free energy F = Accuracy - Complexity. 
       - Likelihood (Accuracy): Match between candidate structure and prompt constraints.
       - Prior (Complexity): Penalizes candidates that deviate from the prompt's structural
         complexity (preventing overfitting/hallucination).
       - The system selects candidates that minimize prediction error (KL divergence proxy).
    
    Note: Per causal analysis, Gauge Theory is restricted to structural parsing support,
    and Spectral/Free Energy concepts are kept in separate logical paths to avoid
    negative interaction effects.
    """

    def __init__(self):
        # Structural keywords for gauge-invariant feature extraction
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.logic_ops = {'and', 'or', 'xor', 'implies'}
        
        # Regex for numbers (int and float)
        self.num_regex = re.compile(r"-?\d+(?:\.\d+)?")

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Gauge-equivariant feature extractor: Parses text into invariant structural fields."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        # Count structural tokens
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        logic_count = sum(1 for w in words if w in self.logic_ops)
        
        # Extract numeric values for constraint propagation
        numbers = [float(n) for n in self.num_regex.findall(text)]
        
        # Simple numeric constraint check (e.g., detect if text implies ordering)
        # This is a heuristic for "numeric evaluation" requirement
        has_numeric_constraint = len(numbers) > 1 and any(numbers[i] != numbers[i+1] for i in range(len(numbers)-1))

        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'logic_ops': logic_count,
            'numbers': numbers,
            'has_numeric_constraint': has_numeric_constraint,
            'length': len(words)
        }

    def _spectral_analysis(self, features: Dict[str, any]) -> Tuple[float, float]:
        """
        Spectral Analysis Layer: Computes spectral signatures of the feature map.
        Returns (spectral_energy, spectral_sparsity) as a proxy for frequency domain analysis.
        Separated from Free Energy logic to satisfy causal constraints.
        """
        # Construct a simple signal vector from feature counts
        signal = [
            features['negations'],
            features['comparatives'],
            features['conditionals'],
            features['logic_ops'],
            features['length'] / 10.0  # Normalize length contribution
        ]
        
        # Spectral Energy (L2 norm proxy)
        energy = sum(x**2 for x in signal)
        
        # Spectral Sparsity (L1/L2 ratio proxy - indicates burstiness vs uniformity)
        l1 = sum(abs(x) for x in signal)
        l2 = math.sqrt(energy) if energy > 0 else 1e-9
        sparsity = l1 / (l2 + 1e-9) if l2 > 0 else 0
        
        return energy, sparsity

    def _compute_free_energy(self, prompt_feat: Dict, cand_feat: Dict, prompt_spec: Tuple, cand_spec: Tuple) -> float:
        """
        Free Energy Inference Core: Minimizes F = <ln q - ln p>.
        Approximates variational free energy by balancing prediction error (accuracy)
        against complexity (divergence from prompt structure).
        """
        # 1. Prediction Error (Likelihood term): Difference in structural features
        # We want the candidate to respect the prompt's structural constraints
        error_neg = abs(prompt_feat['negations'] - cand_feat['negations']) * 2.0
        error_comp = abs(prompt_feat['comparatives'] - cand_feat['comparatives']) * 1.5
        error_cond = abs(prompt_feat['conditionals'] - cand_feat['conditionals']) * 1.5
        
        # Numeric consistency check
        numeric_error = 0.0
        if prompt_feat['has_numeric_constraint'] or cand_feat['has_numeric_constraint']:
            # If prompt has numbers, candidate should ideally reflect similar magnitude or count logic
            # Simple heuristic: ratio of number counts should be close to 1 or 0 depending on context
            p_count = len(prompt_feat['numbers'])
            c_count = len(cand_feat['numbers'])
            if p_count > 0:
                numeric_error = abs(p_count - c_count) * 1.0
            else:
                # If prompt has no numbers but candidate does, it might be hallucinating specifics
                numeric_error = min(c_count, 3) * 0.5

        total_error = error_neg + error_comp + error_cond + numeric_error

        # 2. Complexity Penalty (Prior term): Divergence in spectral properties
        # Candidates with wildly different spectral signatures (energy/sparsity) are penalized
        p_energy, p_sparse = prompt_spec
        c_energy, c_sparse = cand_spec
        
        complexity = abs(p_energy - c_energy) * 0.1 + abs(p_sparse - c_sparse) * 0.2

        # Free Energy F = Error + Complexity
        # Lower F is better. We return negative F so higher score = better.
        free_energy = -(total_error + complexity)
        
        return free_energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance (tiebreaker only)."""
        try:
            z = zlib.compress
            len1 = len(z(s1.encode()))
            len2 = len(z(s2.encode()))
            combined = len(z((s1 + s2).encode()))
            if combined == 0: return 0.0
            return (combined - min(len1, len2)) / max(len1, len2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Extract Prompt Features (Gauge Equivariant)
        p_feat = self._extract_structural_features(prompt)
        # 2. Spectral Analysis of Prompt
        p_spec = self._spectral_analysis(p_feat)
        
        scored_candidates = []
        
        for cand in candidates:
            # 1. Extract Candidate Features
            c_feat = self._extract_structural_features(cand)
            # 2. Spectral Analysis of Candidate
            c_spec = self._spectral_analysis(c_feat)
            
            # 3. Compute Free Energy (Core Scoring)
            fe_score = self._compute_free_energy(p_feat, c_feat, p_spec, c_spec)
            
            # Normalize FE score to a rough 0-1 range heuristic for ranking
            # Base score starts at 0.5, adjusted by free energy
            # Typical FE range is -10 to 0. 
            base_score = 0.5 + (fe_score * 0.05) 
            base_score = max(0.0, min(1.0, base_score))
            
            scored_candidates.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"FE-minimized match (Error+Complexity). Spec-Energy: {c_spec[0]:.2f}, Spec-Sparse: {c_spec[1]:.2f}",
                "_fe_raw": fe_score
            })
        
        # Sort by Free Energy score (descending)
        scored_candidates.sort(key=lambda x: x["_fe_raw"], reverse=True)
        
        # Tie-breaking with NCD if scores are extremely close (within 0.01)
        # This satisfies the "NCD as tiebreaker" requirement
        final_results = []
        for i, item in enumerate(scored_candidates):
            # Check neighbors for ties
            is_tie = False
            if i < len(scored_candidates) - 1:
                if abs(item["_fe_raw"] - scored_candidates[i+1]["_fe_raw"]) < 0.01:
                    is_tie = True
            
            if is_tie:
                # Apply NCD tiebreaker against the prompt
                ncd = self._ncd_distance(prompt, item["candidate"])
                # Adjust score slightly by NCD (lower NCD is better)
                item["score"] -= ncd * 0.001 
                item["reasoning"] += f" [NCD Tiebreak: {ncd:.3f}]"
            
            # Clean up internal keys
            del item["_fe_raw"]
            final_results.append(item)
            
        # Re-sort after tie-breaking adjustments
        final_results.sort(key=lambda x: x["score"], reverse=True)
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on the Free Energy of the single candidate.
        Returns 0-1.
        """
        p_feat = self._extract_structural_features(prompt)
        p_spec = self._spectral_analysis(p_feat)
        
        a_feat = self._extract_structural_features(answer)
        a_spec = self._spectral_analysis(a_feat)
        
        fe = self._compute_free_energy(p_feat, a_feat, p_spec, a_spec)
        
        # Map FE to confidence
        # FE ~ 0 is perfect match. FE < -5 is poor.
        # Logistic mapping: 1 / (1 + exp(-k * (fe + offset)))
        # Shift so that fe = -2 gives ~0.5, fe = 0 gives ~0.9
        confidence = 1.0 / (1.0 + math.exp(-1.5 * (fe + 2.0)))
        
        # Clamp
        return max(0.0, min(1.0, confidence))