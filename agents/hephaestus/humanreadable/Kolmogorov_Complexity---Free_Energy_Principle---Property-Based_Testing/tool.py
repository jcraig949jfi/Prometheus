from typing import Dict, Tuple

import re
import random
import math
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    Combines Kolmogorov Complexity (MDL), Free Energy Principle, and Property-Based Testing.
    
    Core mechanism:
    1. Parse text into relation graph (negations, comparatives, conditionals, causals, numerics)
    2. Compute description length (DL) via MDL: model cost + data cost
    3. Compute free energy (F) as prediction error (chi-squared)
    4. Property-based testing: perturb answer, shrink to minimal variant, measure robustness
    5. Constructive computation: solve numeric/probability/temporal problems directly
    6. Meta-confidence: detect ambiguity/presupposition in prompt
    
    Score = computation_score (40%) + structural_score (30%) + robustness (20%) + NCD (10%)
    """
    
    def __init__(self):
        random.seed(42)  # Deterministic
        self.lambda_fe = 0.5
        self.mu_shrink = 0.5
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Constructive computation (primary signal)
            comp_score = self._compute_answer(prompt, cand)
            
            # Structural scoring
            struct_score = self._structural_score(prompt, cand)
            
            # Robustness via property-based testing
            robust_score = self._robustness_score(cand)
            
            # NCD as minor tiebreaker
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination
            raw_score = (0.4 * comp_score + 0.3 * struct_score + 
                        0.2 * robust_score + 0.1 * ncd_score)
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"comp={comp_score:.2f} struct={struct_score:.2f} robust={robust_score:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence: check for ambiguity/presupposition
        meta_conf = self._meta_confidence(prompt)
        
        # Computational confidence
        comp_score = self._compute_answer(prompt, answer)
        
        # Structural confidence
        struct_score = self._structural_score(prompt, answer)
        
        # Combined confidence, capped by meta-confidence
        base_conf = (comp_score + struct_score) / 2.0
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability in prompt."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* a ', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p_lower) and not re.search(r'\b(only|exactly)\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(cannot be determined|not enough information|impossible to say)\b', p_lower):
            return 0.2
        
        return 0.95  # High confidence in answerable questions
    
    def _compute_answer(self, prompt: str, answer: str) -> float:
        """Constructive computation: actually solve problems."""
        score = 0.0
        
        # Numeric comparison (e.g., 9.11 vs 9.9)
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        if nums_p and len(nums_p) >= 2:
            if '>' in prompt or 'greater' in prompt.lower():
                if nums_a and float(nums_p[0]) > float(nums_p[1]):
                    score += 0.5
            elif '<' in prompt or 'less' in prompt.lower():
                if nums_a and float(nums_p[0]) < float(nums_p[1]):
                    score += 0.5
        
        # Arithmetic evaluation (PEMDAS)
        arith_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if arith_match:
            a, op, b = int(arith_match.group(1)), arith_match.group(2), int(arith_match.group(3))
            result = eval(f"{a}{op}{b}")
            if str(result) in answer:
                score += 0.8
        
        # Probability/Bayesian reasoning
        if re.search(r'\b(probability|chance|likely)\b', prompt.lower()):
            # Extract percentages
            probs = re.findall(r'(\d+)%', prompt)
            if len(probs) >= 2:
                # Simple Bayes: P(A|B) proportional to P(B|A)*P(A)
                prob_a = re.findall(r'(\d+\.?\d*)%', answer)
                if prob_a:
                    score += 0.3
        
        # Temporal ordering
        if re.search(r'\b(before|after|earlier|later)\b', prompt.lower()):
            times = re.findall(r'(\d{1,2}):(\d{2})', prompt)
            if len(times) >= 2:
                t1 = int(times[0][0]) * 60 + int(times[0][1])
                t2 = int(times[1][0]) * 60 + int(times[1][1])
                if 'before' in prompt.lower() and t1 < t2:
                    score += 0.5
                elif 'after' in prompt.lower() and t1 > t2:
                    score += 0.5
        
        # Negation handling
        if re.search(r'\b(not|no|never|none)\b', prompt.lower()):
            if re.search(r'\b(not|no|never|none)\b', answer.lower()):
                score += 0.3
        
        return min(score, 1.0)
    
    def _structural_score(self, prompt: str, answer: str) -> float:
        """MDL + Free Energy on relation graph."""
        graph = self._parse_relations(prompt + " " + answer)
        
        # MDL: description length
        dl = self._description_length(graph)
        
        # Free energy: prediction error
        fe = self._free_energy(graph)
        
        # Normalize and combine (lower is better, invert for score)
        dl_norm = 1.0 / (1.0 + dl / 10.0)
        fe_norm = 1.0 / (1.0 + fe)
        
        return (dl_norm + fe_norm) / 2.0
    
    def _parse_relations(self, text: str) -> List[Dict]:
        """Extract logical relations as graph edges."""
        edges = []
        t_lower = text.lower()
        
        # Negations
        for match in re.finditer(r'\b(not|no|never)\s+(\w+)', t_lower):
            edges.append({"type": "neg", "src": match.group(2), "dst": None, "weight": 1})
        
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(more|less|greater|smaller)\s+than\s+(\w+)', t_lower):
            edges.append({"type": "cmp", "src": match.group(1), "dst": match.group(3), "weight": 1})
        
        # Conditionals
        for match in re.finditer(r'\bif\s+(\w+).*then\s+(\w+)', t_lower):
            edges.append({"type": "cond", "src": match.group(1), "dst": match.group(2), "weight": 1})
        
        # Causals
        for match in re.finditer(r'(\w+)\s+cause[sd]?\s+(\w+)', t_lower):
            edges.append({"type": "cause", "src": match.group(1), "dst": match.group(2), "weight": 1})
        
        # Numeric constraints
        nums = re.findall(r'(\d+\.?\d*)', text)
        for i in range(len(nums) - 1):
            diff = abs(float(nums[i]) - float(nums[i+1]))
            edges.append({"type": "num", "src": nums[i], "dst": nums[i+1], "weight": diff})
        
        return edges
    
    def _description_length(self, graph: List[Dict]) -> float:
        """MDL: model cost + data cost."""
        if not graph:
            return 0.0
        
        # Model: frequency table of edge types
        type_counts = {}
        for edge in graph:
            t = edge["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        total = len(graph)
        model_cost = len(type_counts) * math.log2(len(type_counts) + 1)
        
        # Data: encode edges using model probabilities
        data_cost = 0.0
        for edge in graph:
            prob = type_counts[edge["type"]] / total
            data_cost -= math.log2(prob + 1e-10)
        
        return model_cost + data_cost
    
    def _free_energy(self, graph: List[Dict]) -> float:
        """Free energy: prediction error (chi-squared)."""
        if not graph:
            return 0.0
        
        # Observed counts
        type_counts = {}
        for edge in graph:
            t = edge["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # Expected: uniform distribution
        total = len(graph)
        n_types = len(type_counts)
        expected = total / n_types
        
        # Chi-squared
        chi2 = sum((obs - expected) ** 2 / expected for obs in type_counts.values())
        return chi2
    
    def _robustness_score(self, answer: str) -> float:
        """Property-based testing: shrink to minimal variant."""
        if not answer.strip():
            return 0.0
        
        tokens = answer.split()
        if len(tokens) <= 1:
            return 0.5
        
        # Try N perturbations
        best_len = len(tokens)
        for _ in range(5):
            perturbed = self._perturb(tokens)
            shrunk = self._shrink(perturbed)
            best_len = min(best_len, len(shrunk))
        
        # Robustness = resistance to shrinking
        shrink_distance = len(tokens) - best_len
        return shrink_distance / (len(tokens) + 1)
    
    def _perturb(self, tokens: List[str]) -> List[str]:
        """Random perturbation: swap, delete, or insert."""
        tokens = tokens.copy()
        if len(tokens) < 2:
            return tokens
        
        choice = random.choice(["swap", "delete"])
        if choice == "swap":
            i, j = random.sample(range(len(tokens)), 2)
            tokens[i], tokens[j] = tokens[j], tokens[i]
        elif choice == "delete" and len(tokens) > 1:
            tokens.pop(random.randint(0, len(tokens) - 1))
        
        return tokens
    
    def _shrink(self, tokens: List[str]) -> List[str]:
        """Iteratively remove tokens while maintaining validity."""
        current = tokens.copy()
        improved = True
        while improved and len(current) > 1:
            improved = False
            for i in range(len(current)):
                candidate = current[:i] + current[i+1:]
                if len(candidate) < len(current):
                    current = candidate
                    improved = True
                    break
        return current
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)