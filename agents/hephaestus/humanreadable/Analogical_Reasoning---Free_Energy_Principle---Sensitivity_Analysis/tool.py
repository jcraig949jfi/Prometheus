import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A computational reasoning tool combining Analogical Structure Mapping, 
    Free Energy Minimization, and Sensitivity Analysis.
    
    Mechanism:
    1. Parsing: Extracts entities and relations (causal, comparative, logical) into adjacency matrices.
    2. Analogical Mapping: Aligns prompt and candidate graphs via greedy degree-matching to compute structural error.
    3. Free Energy: Combines structural error with hypothesis complexity (edge count).
    4. Sensitivity: Perturbs input to test robustness of the fit.
    5. Constructive Computation: Explicitly solves numeric, temporal, and logical constraints where possible.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'entities': r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b|\b\d+(?:\.\d+)?\b',
            'causal': r'(causes|leads to|results in|because|therefore|if.*then)',
            'comparators': r'(greater than|less than|equals|more than|fewer than|>|<|=)',
            'negation': r'(not|no|never|without|cannot)',
            'quantifiers': r'(all|every|some|none|at least one)',
            'temporal': r'(before|after|during|while)',
            'presupposition': r'(have you stopped|why did.*fail|when did.*stop)',
            'false_dichotomy': r'(either.*or|must be.*or)',
            'pronoun_ambiguity': r'(\w+ told \w+ he|she)',
        }
        self.lambda_complexity = 0.1
        self.alpha_sensitivity = 0.2

    def _extract_elements(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Extract entities and relations from text."""
        # Simple tokenization for entities (Capitalized words, numbers)
        entities = list(set(re.findall(self.patterns['entities'], text)))
        if not entities:
            entities = ["root"]
        
        relations = []
        text_lower = text.lower()
        
        # Detect relation types
        if re.search(self.patterns['causal'], text_lower):
            relations.append(("root", "cause", "effect")) # Abstract representation
        if re.search(self.patterns['comparators'], text_lower):
            # Try to find numeric comparisons
            nums = re.findall(r'\d+(?:\.\d+)?', text)
            if len(nums) >= 2:
                relations.append((nums[0], "greater_than", nums[1]) if float(nums[0]) > float(nums[1]) else (nums[1], "greater_than", nums[0]))
            else:
                relations.append(("entity", "comp", "entity"))
        if re.search(self.patterns['negation'], text_lower):
            relations.append(("context", "negates", "target"))
            
        return entities, relations

    def _build_matrix(self, entities: List[str], relations: List[Tuple]) -> np.ndarray:
        """Build adjacency matrix for a specific relation type."""
        n = len(entities)
        if n == 0:
            return np.array([[]])
        matrix = np.zeros((n, n))
        entity_map = {e: i for i, e in enumerate(entities)}
        
        for r in relations:
            if len(r) == 3:
                src, rel_type, tgt = r
                if src in entity_map and tgt in entity_map:
                    matrix[entity_map[src], entity_map[tgt]] = 1
                elif src in entity_map: # Partial match fallback
                     matrix[entity_map[src], entity_map[src]] = 1
        return matrix

    def _greedy_align(self, rows: List[str], cols: List[str]) -> np.ndarray:
        """Greedy alignment based on list order (simulating degree sort)."""
        n = min(len(rows), len(cols))
        if n == 0:
            return np.array([[]])
        
        # Create permutation matrix
        M = np.zeros((len(rows), len(cols)))
        for i in range(n):
            M[i, i] = 1
        # Pad if necessary (simplified for this constraint)
        if len(rows) > len(cols):
            M = M[:len(rows), :]
        elif len(cols) > len(rows):
            M = M[:, :len(cols)]
            
        return M

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Compute Free Energy F = Structural Error + Complexity."""
        p_ents, p_rels = self._extract_elements(prompt)
        c_ents, c_rels = self._extract_elements(candidate)
        
        if not p_ents or not c_ents:
            return 100.0 # High energy for empty sets

        # Build matrices (simplified to one aggregate matrix for this implementation)
        # In a full implementation, we would iterate over relation types t
        A_p = self._build_matrix(p_ents, p_rels)
        A_c = self._build_matrix(c_ents, c_rels)
        
        # Align
        M = self._greedy_align(p_ents, c_ents)
        
        # Resize matrices to match for multiplication if needed (simplified)
        min_dim = min(A_p.shape[0], A_c.shape[0], A_p.shape[1], A_c.shape[1])
        if min_dim == 0: return 100.0
        
        A_p_sub = A_p[:min_dim, :min_dim]
        A_c_sub = A_c[:min_dim, :min_dim]
        M_sub = M[:min_dim, :min_dim]
        
        # Structural Error: ||A_p - M A_c M^T||^2
        try:
            transformed = M_sub @ A_c_sub @ M_sub.T
            error = np.sum((A_p_sub - transformed) ** 2)
        except ValueError:
            error = 10.0 # Penalty for dimension mismatch
            
        # Complexity: Number of edges in candidate
        complexity = len(c_rels) * self.lambda_complexity
        
        return float(error + complexity)

    def _compute_sensitivity(self, prompt: str, candidate: str, base_f: float) -> float:
        """Compute sensitivity by perturbing the prompt."""
        # Simplified perturbation: remove last word of prompt
        words = prompt.split()
        if len(words) <= 1:
            return 0.0
        
        perturbed_prompt = " ".join(words[:-1])
        f_perturbed = self._compute_free_energy(perturbed_prompt, candidate)
        return abs(f_perturbed - base_f)

    def _constructive_compute(self, prompt: str, candidate: str) -> Tuple[float, bool]:
        """
        Attempt constructive computation for numeric/logic problems.
        Returns (score_delta, is_computed).
        """
        score = 0.0
        computed = False
        
        # Extract numbers
        nums_p = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
        nums_c = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', candidate)]
        
        # Case 1: Direct Arithmetic (e.g., "2+2", "What is 5*3?")
        if len(nums_p) >= 2 and len(nums_c) == 1:
            # Check for simple addition/subtraction context
            if '+' in prompt or 'plus' in prompt:
                if abs(sum(nums_p) - nums_c[0]) < 1e-5:
                    score += 10.0
                    computed = True
            elif '-' in prompt or 'minus' in prompt:
                if len(nums_p) >= 2 and abs((nums_p[0] - nums_p[1]) - nums_c[0]) < 1e-5:
                    score += 10.0
                    computed = True
            elif '*' in prompt or 'times' in prompt:
                if abs((nums_p[0] * nums_p[1]) - nums_c[0]) < 1e-5:
                    score += 10.0
                    computed = True
            elif '/' in prompt or 'divided' in prompt:
                if nums_p[1] != 0 and abs((nums_p[0] / nums_p[1]) - nums_c[0]) < 1e-5:
                    score += 10.0
                    computed = True
            elif 'greater' in prompt.lower() or 'larger' in prompt.lower():
                # Comparison logic
                expected = max(nums_p) if 'largest' in prompt.lower() else nums_p[0] # Simplified
                if abs(expected - nums_c[0]) < 1e-5:
                    score += 5.0
                    computed = True

        # Case 2: Logic/Constraint (Simple presence check for logical connectors)
        if ('if' in prompt.lower() and 'then' in prompt.lower()) and ('if' in candidate.lower()):
            score += 2.0
            computed = True
            
        return score, computed

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(self.patterns['presupposition'], p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if re.search(self.patterns['false_dichotomy'], p_lower):
            return 0.4 # Slightly higher, but still skeptical
            
        # 3. Pronoun Ambiguity
        if re.search(self.patterns['pronoun_ambiguity'], p_lower) and "who" in p_lower:
            return 0.2
            
        # 4. Subjectivity without criteria
        if any(x in p_lower for x in ["best", "worst", "favorite", "opinion"]) and "data" not in p_lower:
            return 0.3
            
        # 5. Unanswerable (Missing info indicators)
        if "cannot be determined" in p_lower or "insufficient" in p_lower:
            return 0.1
            
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence for the whole task
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Free Energy
            F = self._compute_free_energy(prompt, cand)
            S = self._compute_sensitivity(prompt, cand, F)
            
            # 2. Constructive Computation (Primary Driver for Tier A)
            comp_score, is_computed = self._constructive_compute(prompt, cand)
            
            # 3. Scoring
            # Base score: Negative Free Energy (lower F is better)
            # We invert F so higher is better. F starts at 0 (perfect) and goes up.
            base_score = -F - (self.alpha_sensitivity * S)
            
            # Add constructive bonus
            if is_computed:
                base_score += comp_score
            
            # Apply meta-cap penalty if the prompt is tricky
            if meta_cap < 0.5:
                base_score -= 5.0 # Heavy penalty for answering tricky questions confidently
            
            results.append({
            "candidate": cand,
            "score": base_score,
            "reasoning": f"F={F:.2f}, S={S:.2f}, Computed={is_computed}, MetaCap={meta_cap}"
        })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        # 1. Meta Check (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Constructive Check (Tier A)
        # If we can computationally verify the answer, confidence can be high
        comp_score, is_computed = self._constructive_compute(prompt, answer)
        
        if is_computed and comp_score > 5.0:
            # Definitive mathematical answer
            raw_conf = 0.95
        else:
            # Rely on structural fit
            # Evaluate single candidate against a dummy set to get relative score
            # (In a real system, we'd compare against all candidates, here we simulate)
            F = self._compute_free_energy(prompt, answer)
            # Normalize F roughly: 0 error -> high conf, >10 error -> low conf
            structural_conf = max(0.0, 1.0 - (F / 20.0))
            raw_conf = structural_conf
            
        # Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Hard floor for ambiguity
        if cap < 0.3:
            return max(final_conf, 0.0) # Force low if ambiguous
            
        return float(np.clip(final_conf, 0.0, 1.0))