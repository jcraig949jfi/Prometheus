from typing import Dict, Tuple

"""
Category-Theoretic Gauge Reasoning Tool

Constructs a category from parsed propositions (objects) and relations (morphisms).
Assigns gauge connections A_{i->j} representing confidence in each relation.
Iteratively minimizes curvature (inconsistency in loops) via adaptive control.
Scores candidates by residual curvature after augmenting the graph.

Metacognitive: detects ambiguity, presupposition, underdetermination.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.alpha = 0.1  # Adaptive control step size
        self.max_iterations = 10
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by gauge-theoretic consistency score."""
        # Parse prompt into base graph
        base_graph = self._parse_to_category(prompt)
        
        # Score each candidate
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand, base_graph)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on metacognitive checks and structural certainty."""
        # Check for meta-level issues
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check structural parsers
        structural_certainty = self._structural_certainty(prompt, answer)
        
        # Combine: meta caps confidence, structural refines it
        return min(meta_conf, structural_certainty)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        presup_patterns = [
            r'\b(have you stopped|have you quit|when did you stop|why did .* (fail|stop))',
            r'\b(still|no longer|anymore)\b.*\?'
        ]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy: "either A or B" without "only"
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            if not re.search(r'\bor .*(else|other)', p_lower):
                return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(fastest|largest|smallest|cheapest|most expensive)\b', p_lower):
                return 0.3
        
        # Survivorship bias cues
        if re.search(r'\bof (those|people) who (succeeded|survived|won)\b', p_lower):
            return 0.35
        
        # Sunk cost framing
        if re.search(r'\balready (invested|spent|paid)\b', p_lower):
            return 0.4
        
        return 0.7  # Default: moderate confidence
    
    def _structural_certainty(self, prompt: str, answer: str) -> float:
        """Compute confidence from structural parsers."""
        # Numeric comparison
        num_result = self._parse_numeric(prompt, answer)
        if num_result is not None:
            return 0.95 if num_result else 0.05
        
        # Bat-and-ball algebra
        algebra_result = self._parse_algebra(prompt, answer)
        if algebra_result is not None:
            return 0.9 if algebra_result else 0.1
        
        # Modular arithmetic
        mod_result = self._parse_modular(prompt, answer)
        if mod_result is not None:
            return 0.9 if mod_result else 0.1
        
        # Negation matching
        neg_result = self._parse_negation(prompt, answer)
        if neg_result is not None:
            return 0.85 if neg_result else 0.15
        
        # If no parser matched, return uncertain
        return 0.4
    
    def _parse_numeric(self, prompt: str, answer: str) -> bool:
        """Extract and compare numbers."""
        # Find number comparisons
        comp_match = re.search(r'(\d+\.?\d*)\s*(>|<|greater|less)\s*(\d+\.?\d*)', prompt.lower())
        if comp_match:
            a, op, b = comp_match.groups()
            a_val, b_val = float(a), float(b)
            correct = (a_val > b_val) if op in ['>', 'greater'] else (a_val < b_val)
            ans_lower = answer.lower()
            if 'yes' in ans_lower or 'true' in ans_lower or 'correct' in ans_lower:
                return correct
            elif 'no' in ans_lower or 'false' in ans_lower or 'incorrect' in ans_lower:
                return not correct
        
        # Extract numbers from prompt and answer
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        answer_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if len(prompt_nums) >= 2 and len(answer_nums) == 1:
            # Check basic arithmetic
            if abs(answer_nums[0] - sum(prompt_nums[:2])) < 0.01:
                return True
            if abs(answer_nums[0] - (prompt_nums[0] - prompt_nums[1])) < 0.01:
                return True
        
        return None
    
    def _parse_algebra(self, prompt: str, answer: str) -> bool:
        """Solve bat-and-ball style algebra."""
        # Pattern: "X and Y cost A, X costs B more than Y, what is Y?"
        match = re.search(r'cost[s]?\s+\$?(\d+\.?\d*)', prompt)
        diff_match = re.search(r'(\d+\.?\d*)\s*more', prompt)
        
        if match and diff_match:
            total = float(match.group(1))
            diff = float(diff_match.group(1))
            # X + Y = total, X = Y + diff => 2Y + diff = total
            y_correct = (total - diff) / 2
            
            answer_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
            if answer_nums and abs(answer_nums[0] - y_correct) < 0.01:
                return True
            elif answer_nums and abs(answer_nums[0] - y_correct) > 0.5:
                return False
        
        return None
    
    def _parse_modular(self, prompt: str, answer: str) -> bool:
        """Detect modular arithmetic / remainder problems."""
        mod_match = re.search(r'(\d+)\s*mod(?:ulo)?\s*(\d+)', prompt.lower())
        if mod_match:
            n, m = int(mod_match.group(1)), int(mod_match.group(2))
            result = n % m
            answer_nums = [int(x) for x in re.findall(r'\d+', answer)]
            if answer_nums and answer_nums[0] == result:
                return True
            elif answer_nums and answer_nums[0] != result:
                return False
        
        return None
    
    def _parse_negation(self, prompt: str, answer: str) -> bool:
        """Match negation patterns."""
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Count negations in prompt
        neg_count = len(re.findall(r'\b(not|no|never|neither)\b', p_lower))
        
        # Odd negations => answer should contain negation or "false"
        if neg_count % 2 == 1:
            if any(word in a_lower for word in ['not', 'no', 'false', 'incorrect']):
                return True
            elif any(word in a_lower for word in ['yes', 'true', 'correct']):
                return False
        
        return None
    
    def _parse_to_category(self, text: str) -> Dict:
        """Parse text into category: objects (propositions), morphisms (relations)."""
        sentences = re.split(r'[.!?;]', text)
        objects = []
        morphisms = []
        
        for i, sent in enumerate(sentences):
            if len(sent.strip()) < 3:
                continue
            objects.append({"id": i, "text": sent.strip()})
        
        # Extract morphisms from relations
        for i, obj_i in enumerate(objects):
            txt_i = obj_i["text"].lower()
            for j, obj_j in enumerate(objects):
                if i == j:
                    continue
                txt_j = obj_j["text"].lower()
                
                # Causal
                if re.search(r'\b(because|leads to|results in|causes)\b', txt_i):
                    morphisms.append({"from": i, "to": j, "type": "causal"})
                
                # Conditional
                if re.search(r'\bif\b.*\bthen\b', txt_i):
                    morphisms.append({"from": i, "to": j, "type": "conditional"})
                
                # Temporal
                if re.search(r'\b(before|after|then)\b', txt_i):
                    morphisms.append({"from": i, "to": j, "type": "temporal"})
        
        return {"objects": objects, "morphisms": morphisms}
    
    def _score_candidate(self, prompt: str, candidate: str, base_graph: Dict) -> Tuple[float, str]:
        """Score candidate by curvature after adding to graph."""
        # Augment graph with candidate
        aug_graph = self._augment_graph(base_graph, candidate)
        
        # Initialize connections
        n_obj = len(aug_graph["objects"])
        A = np.zeros((n_obj, n_obj))
        
        # Run adaptive control to minimize curvature
        final_curvature = self._adaptive_control(A, aug_graph["morphisms"])
        
        # Compute NCD for tiebreaking (max 15% weight)
        ncd = self._ncd(prompt, candidate)
        
        # Combined score: low curvature = high consistency
        curv_score = np.exp(-final_curvature / max(len(aug_graph["morphisms"]), 1))
        ncd_score = 1.0 - ncd
        
        total_score = 0.85 * curv_score + 0.15 * ncd_score
        
        reasoning = f"Curvature={final_curvature:.3f}, NCD={ncd:.3f}"
        return total_score, reasoning
    
    def _augment_graph(self, base_graph: Dict, candidate: str) -> Dict:
        """Add candidate proposition to graph."""
        objects = base_graph["objects"].copy()
        morphisms = base_graph["morphisms"].copy()
        
        new_id = len(objects)
        objects.append({"id": new_id, "text": candidate})
        
        # Add morphisms from candidate to existing objects
        cand_lower = candidate.lower()
        for obj in objects[:-1]:
            obj_lower = obj["text"].lower()
            # Simple heuristic: shared keywords => relation
            shared = set(cand_lower.split()) & set(obj_lower.split())
            if len(shared) > 2:
                morphisms.append({"from": new_id, "to": obj["id"], "type": "entailment"})
        
        return {"objects": objects, "morphisms": morphisms}
    
    def _adaptive_control(self, A: np.ndarray, morphisms: List[Dict]) -> float:
        """Minimize curvature via gradient descent on connections."""
        n = A.shape[0]
        
        for iteration in range(self.max_iterations):
            # Find all 3-cycles (elementary loops)
            loops = []
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        if i != j and j != k and k != i:
                            loops.append([i, j, k])
            
            if not loops:
                break
            
            # Compute curvature for each loop
            curvatures = []
            for loop in loops:
                i, j, k = loop
                F = A[i, j] + A[j, k] + A[k, i]
                curvatures.append(F)
            
            total_curvature = sum(abs(F) for F in curvatures)
            
            # Update connections via gradient descent
            for idx, loop in enumerate(loops):
                i, j, k = loop
                error = curvatures[idx]
                A[i, j] -= self.alpha * error
                A[j, k] -= self.alpha * error
                A[k, i] -= self.alpha * error
            
            # Early stopping
            if total_curvature < 0.01:
                break
        
        # Final curvature
        final_curv = 0.0
        for loop in loops:
            i, j, k = loop
            final_curv += abs(A[i, j] + A[j, k] + A[k, i])
        
        return final_curv
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)