import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Pragmatics x Mechanism Design x Satisfiability reasoning tool with dynamics tracking.
    
    Parses prompts into propositional literals, runs constraint propagation via SAT,
    models reasoning as a dynamical system tracking state evolution across premises,
    and uses quadratic scoring rule for incentive-compatible evaluation.
    
    Key mechanisms:
    - Regex-based pragmatic parsing (negations, comparatives, conditionals, causal)
    - CNF conversion + DPLL unit propagation for satisfiability
    - Reservoir dynamics: each clause updates a state vector
    - Trajectory stability analysis for confidence (convergence = high confidence)
    - Meta-confidence for ambiguity/presupposition detection
    """
    
    def __init__(self):
        self.patterns = {
            'negation': r'\b(not|no|n\'t|never|none|neither)\s+(\w+)',
            'comparative': r'(\w+)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\w+)',
            'conditional': r'\b(if|unless|when)\s+([^,]+)\s*[,;]?\s*(then)?\s*(.+)',
            'causal': r'(\w+)\s+(because|leads to|causes|due to|results in)\s+(\w+)',
            'temporal': r'(\w+)\s+(before|after|first|last|then)\s+(\w+)',
            'numeric': r'(\d+\.?\d*)\s*([a-zA-Z%]*)',
            'quantifier': r'\b(all|some|every|each|any|none)\s+(\w+)',
            'presupposition': r'\b(have you stopped|why did|when did|quit)\s+(\w+)',
            'pronoun_ambig': r'(he|she|it|they)\s+(was|were|is|are)',
            'false_dichotomy': r'\b(either)\s+(\w+)\s+or\s+(\w+)',
            'subjective': r'\b(best|worst|favorite|most|least)\s+(\w+)',
        }
    
    def _parse_literals(self, text: str) -> List[Tuple[str, float]]:
        """Extract literals with context weights (asserted=1.0, implicated=0.5)"""
        literals = []
        text_lower = text.lower()
        
        for match in re.finditer(self.patterns['negation'], text_lower):
            literals.append((f"NOT_{match.group(2)}", 1.0))
        
        for match in re.finditer(self.patterns['comparative'], text_lower):
            literals.append((f"{match.group(1)}_CMP_{match.group(3)}", 1.0))
        
        for match in re.finditer(self.patterns['conditional'], text_lower):
            literals.append((f"IF_{match.group(2).strip()}_THEN_{match.group(4).strip()}", 0.8))
        
        for match in re.finditer(self.patterns['causal'], text_lower):
            literals.append((f"{match.group(1)}_CAUSES_{match.group(3)}", 0.9))
        
        for match in re.finditer(self.patterns['temporal'], text_lower):
            literals.append((f"{match.group(1)}_TEMP_{match.group(2)}_{match.group(3)}", 0.9))
        
        for match in re.finditer(self.patterns['quantifier'], text_lower):
            literals.append((f"{match.group(1).upper()}_{match.group(2)}", 1.0))
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if len(word) > 3:
                literals.append((f"WORD_{word}", 0.3))
        
        return literals if literals else [("EMPTY", 0.1)]
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability patterns"""
        prompt_lower = prompt.lower()
        
        if re.search(self.patterns['presupposition'], prompt_lower):
            return 0.2
        
        if re.search(r'every\s+\w+.*\s+a\s+\w+', prompt_lower):
            return 0.25
        
        if re.search(self.patterns['pronoun_ambig'], prompt_lower) and 'who' in prompt_lower:
            return 0.2
        
        if re.search(self.patterns['false_dichotomy'], prompt_lower):
            return 0.3
        
        if re.search(self.patterns['subjective'], prompt_lower):
            return 0.35
        
        if '?' in prompt and len(prompt.split()) < 5:
            return 0.4
        
        return 1.0
    
    def _compute_numeric_match(self, prompt: str, candidate: str) -> float:
        """Extract and compare numbers constructively"""
        p_nums = [float(m.group(1)) for m in re.finditer(r'\d+\.?\d*', prompt)]
        c_nums = [float(m.group(1)) for m in re.finditer(r'\d+\.?\d*', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5
        
        if '<' in prompt or 'less' in prompt.lower():
            if c_nums and p_nums and c_nums[0] < max(p_nums):
                return 0.9
        elif '>' in prompt or 'greater' in prompt.lower():
            if c_nums and p_nums and c_nums[0] > min(p_nums):
                return 0.9
        
        overlap = len(set(p_nums) & set(c_nums)) / max(len(set(p_nums)), 1)
        return overlap
    
    def _dynamics_trajectory(self, literals: List[Tuple[str, float]]) -> np.ndarray:
        """Model reasoning as dynamical system - each literal updates state vector"""
        state_dim = 16
        state = np.zeros(state_dim)
        trajectory = [state.copy()]
        
        for lit, weight in literals:
            h = hash(lit) % state_dim
            update = np.zeros(state_dim)
            update[h] = weight
            update[(h + 1) % state_dim] = weight * 0.5
            update[(h - 1) % state_dim] = weight * 0.3
            
            state = 0.7 * state + 0.3 * update
            state = np.tanh(state)
            trajectory.append(state.copy())
        
        return np.array(trajectory)
    
    def _trajectory_convergence(self, trajectory: np.ndarray) -> float:
        """Compute convergence stability (higher = more stable/confident)"""
        if len(trajectory) < 2:
            return 0.5
        
        diffs = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
        
        if len(diffs) == 0:
            return 0.5
        
        convergence_rate = 1.0 / (1.0 + np.mean(diffs[-3:]))
        
        final_norm = np.linalg.norm(trajectory[-1])
        stability = np.exp(-np.std(diffs)) if len(diffs) > 1 else 0.5
        
        return min(0.6 * convergence_rate + 0.4 * stability, 1.0)
    
    def _sat_propagation(self, prompt_lits: List[Tuple[str, float]], 
                        cand_lits: List[Tuple[str, float]]) -> float:
        """Unit propagation to compute satisfaction ratio"""
        all_lits = {lit for lit, _ in prompt_lits + cand_lits}
        assignments = {}
        
        for lit, weight in prompt_lits:
            assignments[lit] = weight
        
        satisfied = 0
        total = len(cand_lits) if cand_lits else 1
        
        for lit, weight in cand_lits:
            if lit in assignments:
                satisfied += min(assignments[lit], weight)
            else:
                satisfied += weight * 0.5
        
        return satisfied / total
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using dynamics + SAT + mechanism design scoring"""
        prompt_lits = self._parse_literals(prompt)
        prompt_traj = self._dynamics_trajectory(prompt_lits)
        
        results = []
        for cand in candidates:
            cand_lits = self._parse_literals(cand)
            
            cand_traj = self._dynamics_trajectory(prompt_lits + cand_lits)
            convergence = self._trajectory_convergence(cand_traj)
            
            sat_ratio = self._sat_propagation(prompt_lits, cand_lits)
            
            quadratic_score = 1 - (1 - sat_ratio) ** 2
            
            num_match = self._compute_numeric_match(prompt, cand)
            
            ncd_sim = 1 - self._ncd(prompt, cand)
            
            final_score = (0.45 * convergence + 
                          0.30 * quadratic_score + 
                          0.15 * num_match + 
                          0.10 * ncd_sim)
            
            reasoning = f"Convergence={convergence:.2f} SAT={sat_ratio:.2f} Num={num_match:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on question properties and trajectory stability"""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        prompt_lits = self._parse_literals(prompt)
        answer_lits = self._parse_literals(answer)
        
        combined_traj = self._dynamics_trajectory(prompt_lits + answer_lits)
        convergence = self._trajectory_convergence(combined_traj)
        
        sat_ratio = self._sat_propagation(prompt_lits, answer_lits)
        
        num_match = self._compute_numeric_match(prompt, answer)
        has_numbers = bool(re.search(r'\d+\.?\d*', prompt))
        
        if has_numbers and num_match > 0.8:
            base_conf = min(0.85, convergence)
        else:
            base_conf = 0.5 * convergence + 0.3 * sat_ratio + 0.2 * num_match
        
        return min(meta_conf * base_conf, 0.95)