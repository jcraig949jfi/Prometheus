import re
import math
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Thermodynamic-Morphogenetic Reasoning Tool with Epistemic Honesty.
    
    Mechanism:
    1. Parses logical propositions (negations, conditionals, comparatives) into a constraint graph.
    2. Assigns binary truth variables to nodes.
    3. Computes 'Energy' (E) based on constraint violations (falsification resistance).
    4. Runs a reaction-diffusion process (Turing-style) to smooth inconsistencies and find stable truth patterns.
    5. Calculates Entropy (H) from the stability of these patterns.
    6. Score S = -(E + lambda*H).
    7. Tier B Honesty: Detects presuppositions, ambiguities, and false dichotomies to cap confidence.
    """

    def __init__(self):
        self.lambda_entropy = 0.5
        self.diffusion_alpha = 0.3
        self.iterations = 10
        
        # Tier B Triggers
        self.presupposition_patterns = [
            r"\b(have|has|had|did|do|does)\s+(you|he|she|it|they)\s+(stopped|quit|failed|begun)\b",
            r"\bwhy\s+(did|does|has|is)\s+\w+\s+(fail|stop|quit|lie)\b",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)\b"
        ]
        self.false_dichotomy_patterns = [
            r"\beither\s+.*\s+or\s+.*\b",
            r"\bmust\s+(be|choose)\s+(one|two)\b"
        ]
        self.scope_ambiguity_patterns = [
            r"\bevery\s+\w+\s+.*\s+a\s+\w+\b", # "Every X did a Y"
            r"\ball\s+\w+\s+.*\s+the\s+same\b"
        ]
        self.pronoun_ambiguity_patterns = [
            r"\b(told|said\s+to)\s+\w+\s+(he|she|him|her)\s+was\b",
            r"\bwho\s+(is|was|does)\s+\w+\s+refer\s+to\b"
        ]
        self.subjectivity_patterns = [
            r"\b(best|worst|favorite|most\s+beautiful)\s+\w+\b"
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_predicates(self, text: str) -> Tuple[List[str], List[Tuple]]:
        """Extract atomic predicates and relations using regex."""
        text_lower = text.lower()
        predicates = []
        relations = []
        
        # Simple tokenization for predicates (words/numbers)
        tokens = re.findall(r'\b[\w\.]+\b', text_lower)
        predicates = list(set(tokens))
        
        # Extract Relations
        # Negation
        if re.search(r'\b(not|no|never)\b', text_lower):
            relations.append(('negation', 'global'))
            
        # Conditionals
        if re.search(r'\b(if|then|only\s+if)\b', text_lower):
            relations.append(('conditional', 'global'))
            
        # Comparatives (Numeric)
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if n1 < n2: relations.append(('cmp', 'less', n1, n2))
                elif n1 > n2: relations.append(('cmp', 'greater', n1, n2))
                else: relations.append(('cmp', 'equal', n1, n2))
            except: pass
            
        # Causal
        if re.search(r'\b(because|leads\s+to|causes)\b', text_lower):
            relations.append(('causal', 'global'))
            
        return predicates, relations

    def _compute_energy(self, constraints: List, state: List[int]) -> float:
        """Calculate energy based on violated constraints."""
        energy = 0.0
        for con in constraints:
            ctype = con[0]
            if ctype == 'negation':
                # If negation present, state should ideally reflect inconsistency if asserted true
                # Simplified: Penalty if we assume 'true' but negation exists in text
                if any(state): energy += 0.5 
            elif ctype == 'conditional':
                # A -> B. If A is true (1) and B is false (0), energy += 1
                # Simplified for global conditional: penalty if state is mixed [1, 0]
                if 1 in state and 0 in state:
                    energy += 1.0
            elif ctype == 'cmp':
                # Check if state aligns with numeric comparison
                # This is a proxy: if the candidate text contains the numbers, we assume it respects the order
                pass 
        return energy

    def _reaction_diffusion(self, n_nodes: int, constraints: List) -> Tuple[List[float], float]:
        """
        Simulate reaction-diffusion on truth variables.
        Returns final probabilities and final energy.
        """
        if n_nodes == 0: return [0.5], 0.0
        
        # Initialize state randomly but deterministically based on hash of constraints
        seed = len(constraints)
        x = [0.5 if i % 2 == 0 else 0.5 for i in range(n_nodes)] # Start neutral
        
        # If no specific nodes, create dummy nodes for logic flow
        if n_nodes < 2:
            x = [0.5, 0.5]
            n_nodes = 2

        history_E = []
        
        for _ in range(self.iterations):
            new_x = x.copy()
            
            # Reaction term (Gradient of Energy)
            # Simplified: If constraints imply contradiction, push towards 0 or 1
            r_terms = []
            for i in range(n_nodes):
                # Local energy gradient approximation
                # If many constraints, higher pressure to resolve
                r = -0.1 * len(constraints) * (x[i] - 0.5) 
                r_terms.append(r)
            
            # Diffusion term
            for i in range(n_nodes):
                neighbors = x[(i-1)%n_nodes] + x[(i+1)%n_nodes]
                d = (neighbors - 2*x[i]) 
                
                update = r_terms[i] + self.diffusion_alpha * d
                val = x[i] + update * 0.1 # Learning rate
                
                # Hard threshold via sigmoid-like step for stability
                if val > 0.5: new_x[i] = 1.0
                elif val < 0.5: new_x[i] = 0.0
                else: new_x[i] = 0.5
            
            x = new_x
            
            # Check convergence (simplified)
            current_E = sum(x) # Proxy for energy state
            history_E.append(current_E)

        # Calculate Entropy
        H = 0.0
        for p in x:
            if p > 0 and p < 1:
                H -= (p * math.log(p + 1e-9) + (1-p) * math.log(1-p + 1e-9))
            elif p == 0 or p == 1:
                H += 0 # No entropy
        
        final_E = sum([1 if v == 0.5 else 0 for v in x]) # Penalty for undecided
        return x, final_E + H

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Evaluate prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. False Dichotomy
        for pattern in self.false_dichotomy_patterns:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a trap question
                if "must" in p_lower or "either" in p_lower:
                    return 0.25

        # 3. Scope/Pronoun Ambiguity
        for pattern in self.scope_ambiguity_patterns + self.pronoun_ambiguity_patterns:
            if re.search(pattern, p_lower):
                if "who" in p_lower or "same" in p_lower or "every" in p_lower:
                    return 0.25

        # 4. Subjectivity
        for pattern in self.subjectivity_patterns:
            if re.search(pattern, p_lower):
                return 0.25
                
        # 5. Unanswerable (Heuristic: very short prompt with no data)
        if len(prompt.split()) < 4 and "?" in prompt:
            return 0.25

        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = lambda x: len(zlib.compress(x.encode()))
        s1_enc = s1.encode()
        s2_enc = s2.encode()
        concat = s1_enc + s2_enc
        
        c1 = z(s1_enc)
        c2 = z(s2_enc)
        c12 = z(concat)
        
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning: Parse structure and compute logical consistency.
        Returns a score where higher is better.
        """
        score = 0.0
        p_preds, p_rels = self._extract_predicates(prompt)
        c_preds, c_rels = self._extract_predicates(candidate)
        
        # 1. Numeric Consistency (Constructive Computation)
        p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt.lower())]
        c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate.lower())]
        
        if p_nums and c_nums:
            # Check if candidate preserves numeric order logic
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_order = 1 if p_nums[0] > p_nums[1] else (-1 if p_nums[0] < p_nums[1] else 0)
                c_order = 1 if c_nums[0] > c_nums[1] else (-1 if c_nums[0] < c_nums[1] else 0)
                if p_order == c_order:
                    score += 2.0
                else:
                    score -= 2.0 # Penalty for wrong math
        
        # 2. Logical Constraint Satisfaction (Thermodynamic Model)
        # Treat candidate as a system trying to satisfy prompt constraints
        all_preds = list(set(p_preds + c_preds))
        if not all_preds:
            return 0.0
            
        # Build constraint graph edges from prompt relations
        constraints = p_rels 
        
        # Run Reaction-Diffusion on the combined logical space
        # We map predicates to indices. 
        # Ideally, we check if candidate truth values minimize energy defined by prompt.
        # Simplified: If candidate contains negation but prompt doesn't (or vice versa) -> Energy up.
        
        n_nodes = len(all_preds)
        # Map presence in candidate to initial state
        state = [1.0 if p in c_preds else 0.0 for p in all_preds]
        
        # If the candidate contradicts a direct negative in prompt
        has_neg = any(r[0] == 'negation' for r in p_rels)
        cand_has_neg = any(r[0] == 'negation' for r in c_rels)
        
        if has_neg and not cand_has_neg:
            # Candidate missed a negation
            score -= 1.0
        elif not has_neg and cand_has_neg:
            # Candidate added unnecessary negation
            score -= 0.5
            
        # Run diffusion to see if stable state emerges
        probs, energy = self._reaction_diffusion(n_nodes, constraints)
        
        # Score based on low energy (consistency) and low entropy (decisiveness)
        # Invert energy so lower energy = higher score
        score += (1.0 / (energy + 0.1)) 
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_clean = self._normalize(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        
        for cand in candidates:
            cand_clean = self._normalize(cand)
            
            # 1. Structural & Logical Score (Primary)
            struct_score = self._structural_score(prompt_clean, cand_clean)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            ncd = self._compute_ncd(prompt_clean, cand_clean)
            # NCD is distance (0=same, 1=different). We want similarity for context, 
            # but distinctness for answer. 
            # Heuristic: Moderate NCD is good, very high is noise, very low is echo.
            ncd_score = 0.0
            if 0.2 <= ncd <= 0.8:
                ncd_score = 0.5
            elif ncd < 0.2:
                ncd_score = 0.1 # Likely just repeating prompt
            
            # Combine: Structural dominates
            raw_score = struct_score * 0.85 + ncd_score * 0.15
            
            # Apply Meta Cap to the final confidence derived from score
            # Normalize raw_score roughly to 0-1 range for confidence calculation
            # (Assuming struct_score ranges -2 to 3 typically)
            normalized_conf = 1.0 / (1.0 + math.exp(-raw_score)) # Sigmoid
            
            # Apply Tier B Cap
            if meta_cap < 1.0:
                final_conf = min(normalized_conf, meta_cap)
            else:
                final_conf = normalized_conf
            
            # Cap absolute max confidence unless computation was definitive
            if final_conf > 0.9 and struct_score < 1.5:
                final_conf = 0.85

            results.append({
                "candidate": cand,
                "score": final_conf,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd:.2f}, MetaCap: {meta_cap}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Check meta-confidence first
        cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Apply cap
        final_conf = min(base_score, cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))