import re
import math
import zlib
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Wavelet-like hierarchical feature extraction,
    Maximum Entropy priors, and Free Energy minimization for answer evaluation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical cues (negation, comparatives, numbers).
    2. Hierarchical Transform: Builds a binary tree of features (Haar-like wavelet).
       - Leaves = tokens with feature vectors.
       - Internal nodes = averages (approximation) and differences (detail).
    3. Free Energy Scoring: 
       - Computes surprise based on MaxEnt priors (constraint matching).
       - Penalizes structural mismatches (detail coefficients) between candidate and reference.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and unanswerability
       to cap confidence, ensuring the model admits uncertainty rather than guessing.
    """

    # Logical keywords for structural parsing
    NEGATIONS = {'not', "n't", 'no', 'never', 'none', 'neither'}
    COMPARATIVES = {'more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse', '-er'}
    CONDITIONALS = {'if', 'then', 'unless', 'otherwise', 'provided'}
    CAUSAL = {'because', 'since', 'leads', 'results', 'causes', 'due'}
    BOOL_OPS = {'and', 'or', 'either', 'both'}
    
    def __init__(self):
        self.max_iter = 100  # For iterative scaling approximation

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer preserving words and numbers."""
        return re.findall(r"[\w\-\.]+|[^\s\w]", text.lower())

    def _extract_features(self, token: str) -> np.ndarray:
        """
        Extracts a sparse feature vector for a token.
        Order: [is_neg, is_comp, is_cond, is_causal, is_num, is_bool, polarity]
        """
        t = token.lower()
        vec = np.zeros(7)
        
        if t in self.NEGATIONS or t.endswith("n't"): vec[0] = 1.0
        if any(c in t for c in self.COMPARATIVES) or t.endswith("er"): vec[1] = 1.0
        if t in self.CONDITIONALS: vec[2] = 1.0
        if any(c in t for c in self.CAUSAL): vec[3] = 1.0
        if t in self.BOOL_OPS: vec[5] = 1.0
        
        # Numeric detection
        try:
            val = float(t.replace(',', ''))
            vec[4] = 1.0
            # Normalize polarity based on sign if it's a number context (simplified)
            vec[6] = 1.0 if val > 0 else (-1.0 if val < 0 else 0.0)
        except ValueError:
            pass
            
        return vec

    def _build_tree(self, text: str) -> Dict:
        """
        Builds a binary tree of feature vectors.
        Returns a dict with 'leaves' (list of vectors) and 'levels' (list of lists of nodes).
        Each node: {'approx': vector, 'detail': vector, 'span': (start, end)}
        """
        tokens = self._tokenize(text)
        if not tokens:
            return {'levels': [], 'leaves': []}

        # Level 0: Leaves
        leaves = [self._extract_features(t) for t in tokens]
        levels = [[{'approx': v.copy(), 'detail': np.zeros(7), 'span': (i, i+1)} 
                   for i, v in enumerate(leaves)]]
        
        # Recursive merging (Haar-like)
        current_level = levels[0]
        while len(current_level) > 1:
            next_level = []
            n = len(current_level)
            # Pad if odd
            if n % 2 == 1:
                current_level.append({'approx': np.zeros(7), 'detail': np.zeros(7), 'span': (n, n+1)})
                n += 1
            
            for i in range(0, n, 2):
                left = current_level[i]
                right = current_level[i+1]
                
                # Approximation (Average)
                approx = (left['approx'] + right['approx']) / 2.0
                # Detail (Difference) - captures local mismatch
                detail = left['approx'] - right['approx']
                
                next_level.append({
                    'approx': approx,
                    'detail': detail,
                    'span': (left['span'][0], right['span'][1])
                })
            
            levels.append(next_level)
            current_level = next_level
            
        return {'levels': levels, 'leaves': leaves}

    def _maxent_prior(self, features: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estimates MaxEnt parameters (lambda) via moment matching (simplified).
        Returns expected mean and variance for the constraint set.
        """
        if not features:
            return np.zeros(7), np.ones(7)
        
        data = np.array(features)
        mean = np.mean(data, axis=0)
        var = np.var(data, axis=0) + 1e-6 # Avoid division by zero
        return mean, var

    def _compute_free_energy(self, cand_tree: Dict, ref_tree: Dict) -> float:
        """
        Computes the Free Energy score.
        F = Sum[ -log P(f) + 0.5 * ||detail||^2 ]
        Lower F is better. We return negative F so higher score is better.
        """
        if not cand_tree['levels'] or not ref_tree['levels']:
            return -100.0 # Penalty for empty

        total_energy = 0.0
        max_levels = min(len(cand_tree['levels']), len(ref_tree['levels']))
        
        # Aggregate all nodes for global prior estimation (simplified)
        all_cand_nodes = [n for level in cand_tree['levels'] for n in level]
        all_ref_nodes = [n for level in ref_tree['levels'] for n in level]
        
        if not all_cand_nodes: return -100.0

        # Estimate global constraints from Reference (as ground truth proxy)
        ref_means, ref_vars = self._maxent_prior([n['approx'] for n in all_ref_nodes])
        
        for l in range(max_levels):
            cand_nodes = cand_tree['levels'][l]
            ref_nodes = ref_tree['levels'][l]
            
            # Weight coarser levels higher (global meaning)
            weight = 1.0 + (l / max_levels) 
            
            level_energy = 0.0
            min_len = min(len(cand_nodes), len(ref_nodes))
            
            for i in range(min_len):
                c_node = cand_nodes[i]
                r_node = ref_nodes[i]
                
                # 1. Surprise term: How far is candidate approx from reference prior?
                # Using Gaussian approximation for MaxEnt: -log P ~ (x - mu)^2 / (2*var)
                diff_mean = c_node['approx'] - ref_means
                surprise = np.sum((diff_mean ** 2) / (ref_vars + 1e-6))
                
                # 2. Detail term: Structural mismatch (wavelet coefficient difference)
                detail_mismatch = np.sum((c_node['detail'] - r_node['detail']) ** 2)
                
                level_energy += surprise + 0.5 * detail_mismatch
            
            total_energy += weight * level_energy

        return -total_energy # Higher is better

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if len_both == 0: return 0.0
        return (len_both - min(len1, len2)) / max(len1, len2, 1)

    def _solve_numeric(self, text: str) -> Optional[float]:
        """Attempt to extract and evaluate simple numeric expressions."""
        # Look for patterns like "5 + 3", "10 / 2", or just numbers
        # This is a simplified constructive computation check
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            try:
                # If the text contains explicit math operators
                if any(op in text for op in ['+', '-', '*', '/', 'plus', 'minus']):
                    # Very basic eval safety check
                    clean = re.sub(r'[^\d+\-*/.\s]', '', text)
                    if clean:
                        return float(eval(clean))
            except:
                pass
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        presup_triggers = ["have you stopped", "why did", "when did", "how often did", "quit", "failed to"]
        if any(t in p for t in presup_triggers):
            return 0.25
            
        # 2. Scope/Pronoun Ambiguity
        if re.search(r'\b(every|all|each)\b.*\b(a|an|the)\b', p) and "same" in p:
            return 0.3
        if re.search(r'\b(told|said|asked)\b.*\b(he|she|him|her|they)\b', p) and "who" in p:
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and "only" in p:
            return 0.3
            
        # 4. Subjectivity without criteria
        if any(w in p for w in ["best", "worst", "favorite", "beautiful"]) and "according to" not in p:
            if "data" not in p and "chart" not in p and "table" not in p:
                return 0.4

        # 5. Unanswerable (Missing info indicators)
        if "not mentioned" in p or "insufficient information" in p:
            return 0.2
            
        return 1.0 # No red flags

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_tree = self._build_tree(prompt)
        
        # Heuristic: If prompt implies a specific numeric answer, try to compute it
        prompt_numeric = self._solve_numeric(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            cand_tree = self._build_tree(cand)
            
            # 1. Structural/Free Energy Score (Primary)
            fe_score = self._compute_free_energy(cand_tree, prompt_tree)
            # Normalize FE score roughly to 0-1 range based on empirical bounds
            # A perfect match would be near 0 energy, mismatch negative.
            # We map this: high negative energy -> low score. 
            # Let's assume typical range is -50 to 0.
            struct_score = max(0.0, min(1.0, (fe_score + 50) / 50.0))
            
            # 2. Constructive Computation (If applicable)
            comp_score = 0.0
            cand_numeric = self._solve_numeric(cand)
            if prompt_numeric is not None and cand_numeric is not None:
                if abs(prompt_numeric - cand_numeric) < 1e-5:
                    comp_score = 1.0
                    reasoning_parts.append("Numeric calculation matches.")
                else:
                    comp_score = 0.0
                    reasoning_parts.append(f"Numeric mismatch: expected {prompt_numeric}, got {cand_numeric}")
            elif prompt_numeric is not None:
                # Prompt has math, candidate doesn't seem to resolve it
                if cand_numeric is None:
                    comp_score = 0.2 # Penalty
                    reasoning_parts.append("Failed to perform implied calculation.")

            # 3. NCD Tiebreaker (Max 15% weight)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted Sum
            # Structural: 50%, Computation: 35%, NCD: 15%
            final_score = (struct_score * 0.50) + (comp_score * 0.35) + (ncd_score * 0.15)
            
            if comp_score > 0.8:
                final_score = 0.95 # Boost if calculation is exact
            
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Structural similarity and logical consistency analyzed."
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Base confidence from evaluation
        # We simulate a quick evaluation to get a raw score
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # Map raw score (0-1) to confidence, but heavily penalized by meta_cap
        # If meta_cap is 0.25 (ambiguous), confidence cannot exceed 0.25
        base_conf = raw_score * 0.8 + 0.1 # Spread out slightly
        
        final_conf = min(base_conf, meta_cap)
        
        # Ensure we don't return > 0.9 unless it's a definitive computation
        # (Heuristic: if answer contains numbers and prompt had numbers, allow higher)
        has_nums = bool(re.search(r'\d', answer))
        if not has_nums and final_conf > 0.85:
            final_conf = 0.85
            
        return float(np.clip(final_conf, 0.0, 1.0))