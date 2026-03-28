import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Statistical Mechanics, Predictive Coding,
    and Abductive Reasoning. It parses logical propositions from text, constructs a constraint
    matrix, and scores candidates based on prediction error (energy) and constraint consistency (entropy).
    """
    
    def __init__(self):
        # Lexicons for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'provided', 'unless']
        self.causals = ['because', 'leads', 'results', 'causes', 'due to']
        self.orderings = ['before', 'after', 'first', 'last', 'precede', 'follow']
        self.beta = 1.0  # Inverse temperature for Boltzmann weighting

    def _extract_props(self, text: str) -> List[Dict]:
        """Extract structural features and atomic facts from text."""
        props = []
        text_lower = text.lower()
        
        # 1. Negations
        for word in self.negations:
            if re.search(r'\b' + word + r'\b', text_lower):
                props.append({'type': 'negation', 'content': word, 'val': 0})
        
        # 2. Comparatives & Numbers (Simple extraction)
        # Pattern: number word/phrase number
        num_pattern = r'(\d+\.?\d*)\s*(?:is|are|was|were|has|have)?\s*(greater|less|more|fewer|larger|smaller|higher|lower|equal)\s*(?:than)?\s*(\d+\.?\d*)'
        matches = re.findall(num_pattern, text_lower)
        for m in matches:
            v1, comp, v2 = m
            val = float(v1) < float(v2) if comp in ['less', 'fewer', 'smaller', 'lower'] else float(v1) > float(v2)
            props.append({'type': 'comparative', 'content': f"{v1} {comp} {v2}", 'val': val})
            
        # Generic comparative presence
        for word in self.comparatives:
            if re.search(r'\b' + word + r'\b', text_lower):
                props.append({'type': 'comp_keyword', 'content': word, 'val': 1})

        # 3. Conditionals
        has_if = 'if' in text_lower
        has_then = 'then' in text_lower
        if has_if or has_then:
            props.append({'type': 'conditional', 'content': 'if_then', 'val': 1 if (has_if and has_then) else 0.5})

        # 4. Causal
        for word in self.causals:
            if word in text_lower:
                props.append({'type': 'causal', 'content': word, 'val': 1})

        # 5. Ordering
        for word in self.orderings:
            if word in text_lower:
                props.append({'type': 'ordering', 'content': word, 'val': 1})
                
        return props

    def _build_matrix(self, prompt_props: List[Dict], cand_props: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Build binary matrix M and target vector t."""
        if not prompt_props and not cand_props:
            return np.array([]), np.array([])
            
        # Create a unified set of keys (simplified to indices for this implementation)
        n_props = len(prompt_props)
        if n_props == 0:
            return np.array([]), np.array([])
            
        M = np.zeros((n_props, n_props))
        t = np.zeros(n_props)
        
        # Fill diagonal with prompt truth values (self-consistency)
        # And set target t based on prompt assertions
        for i, p in enumerate(prompt_props):
            M[i, i] = 1.0
            t[i] = p['val']
            
        # Map candidate props to prompt props (simple matching)
        # If candidate contradicts a prompt proposition, it creates error
        for j, cp in enumerate(cand_props):
            for i, pp in enumerate(prompt_props):
                if cp['type'] == pp['type'] and cp['content'] == pp['content']:
                    # Match found: candidate asserts same fact
                    M[i, j % n_props] = 1.0 # Simplified mapping for demo
                    # If candidate implies opposite val, it's a contradiction
                    if cp['val'] != pp['val']:
                         t[i] = 0.0 # Force mismatch penalty logic later
                    break
        return M, t

    def _calc_entropy_term(self, props: List[Dict]) -> float:
        """Estimate entropy (Omega) based on constraint satisfaction space size."""
        if not props:
            return 1.0
        # Heuristic: More consistent logical types imply higher structural entropy (more ways to be true)
        # Fewer contradictions = higher Omega
        types = [p['type'] for p in props]
        unique_types = set(types)
        # Base entropy on diversity of logical structures detected
        return max(1.0, len(unique_types) * 0.5 + 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_props = self._extract_props(prompt)
        results = []
        
        # Baseline NCD calculation for tie-breaking
        import zlib
        def get_ncd(s1, s2):
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1+s2).encode()))
            denom = max(z1, z2)
            return z12 / denom if denom > 0 else 1.0

        max_ncd = 0.0
        ncd_scores = []
        
        # Pre-calculate NCD to find max for normalization if needed, or just use raw
        for cand in candidates:
            ncd = get_ncd(prompt, cand)
            ncd_scores.append(ncd)
            if ncd > max_ncd: max_ncd = ncd

        for i, cand in enumerate(candidates):
            cand_props = self._extract_props(cand)
            
            # 1. Structural Scoring (Primary)
            # If no structural features found, rely heavily on NCD later
            if not prompt_props or not cand_props:
                energy = 1.0 # High energy (bad) if no structure matched
                omega = 1.0
            else:
                # Calculate Prediction Error (Energy)
                # Simplified: Count mismatches in extracted features
                mismatches = 0
                matches = 0
                for cp in cand_props:
                    found = False
                    for pp in prompt_props:
                        if cp['type'] == pp['type']:
                            if cp['content'] == pp['content']:
                                matches += 1
                                if cp['val'] != pp['val']:
                                    mismatches += 1
                                found = True
                                break
                    if not found:
                        # Candidate introduces new concept not in prompt? 
                        # In abductive reasoning, this might be necessary, but strict adherence lowers error
                        pass 
                
                # Normalize energy: 0 is perfect, higher is worse
                # Penalize contradictions heavily
                energy = float(mismatches) * 2.0 
                if matches == 0 and len(cand_props) > 0:
                     energy += 1.0 # Penalty for no overlap
                    
                # Calculate Entropy Term
                omega = self._calc_entropy_term(cand_props)
            
            # Free Energy Score: S = E - (1/beta) * ln(Omega)
            # We want lower S. 
            # To make "Higher score = better" for the output, we invert: Score = -S
            ln_omega = np.log(omega + 1e-9)
            free_energy = energy - (1.0 / self.beta) * ln_omega
            score = -free_energy
            
            # 2. NCD Tiebreaker (Only if structural signal is weak)
            # If energy is 0 (no structural features detected), use NCD
            if energy == 0.0 or (len(prompt_props) == 0 and len(cand_props) == 0):
                ncd = ncd_scores[i]
                # Lower NCD is better. Convert to score.
                # Assume max_ncd is approx 1.2-1.5 usually. 
                score = (1.5 - ncd) * 0.1 # Small boost from NCD so it doesn't override structure
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Energy: {energy:.2f}, Entropy: {ln_omega:.2f}, NCD_boost: {ncd_scores[i]:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the relative score of the answer against a set of perturbations or baseline.
        Here simplified: 1.0 if structural match, scaled by error.
        """
        props_p = self._extract_props(prompt)
        props_a = self._extract_props(answer)
        
        if not props_p and not props_a:
            # Fallback to simple string overlap heuristic if no logic found
            words_p = set(prompt.lower().split())
            words_a = set(answer.lower().split())
            overlap = len(words_p.intersection(words_a))
            if len(words_p) == 0: return 0.5
            return min(1.0, overlap / len(words_p))

        # Calculate error
        mismatches = 0
        total_checks = 0
        for cp in props_a:
            for pp in props_p:
                if cp['type'] == pp['type'] and cp['content'] == pp['content']:
                    total_checks += 1
                    if cp['val'] != pp['val']:
                        mismatches += 1
        
        if total_checks == 0:
            # No direct logical conflict found, check for presence of key terms
            if len(props_a) > 0 and len(props_p) > 0:
                return 0.6 # Moderate confidence if structure exists but no direct map
            return 0.5

        error_rate = mismatches / total_checks
        return max(0.0, 1.0 - error_rate)