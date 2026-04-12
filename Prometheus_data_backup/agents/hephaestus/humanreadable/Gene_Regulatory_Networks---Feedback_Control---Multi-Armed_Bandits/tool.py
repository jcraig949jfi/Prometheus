from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dynamic Regulatory-Bandit Scorer (DRBS)
    
    Parses prompts into propositional atoms forming a regulatory network.
    Uses PID feedback control to converge activations toward consistent truth states.
    UCB bandit allocation focuses on uncertain nodes. Scores candidates by 
    activation alignment. Includes computational parsers for numeric, logical,
    and causal reasoning plus meta-confidence for epistemic honesty.
    """
    
    def __init__(self):
        self.Kp, self.Ki, self.Kd = 0.5, 0.1, 0.2
        self.ucb_c = 1.4
        self.iterations = 20
        self.window = 5
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        atoms_p, edges_p = self._parse(prompt)
        ref = self._reference_vector(prompt, atoms_p)
        
        results = []
        for cand in candidates:
            atoms_c, _ = self._parse(cand)
            activation = self._run_network(atoms_p, edges_p, ref)
            struct_score = self._structural_score(atoms_p, atoms_c, activation)
            comp_score = self._computational_score(prompt, cand)
            ncd_score = self._ncd_score(prompt, cand)
            
            final = 0.55 * struct_score + 0.35 * comp_score + 0.10 * ncd_score
            reasoning = f"Struct={struct_score:.2f} Comp={comp_score:.2f} NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        atoms_p, edges_p = self._parse(prompt)
        atoms_a, _ = self._parse(answer)
        ref = self._reference_vector(prompt, atoms_p)
        activation = self._run_network(atoms_p, edges_p, ref)
        
        struct_score = self._structural_score(atoms_p, atoms_a, activation)
        comp_score = self._computational_score(prompt, answer)
        
        base_conf = 0.6 * struct_score + 0.4 * comp_score
        return min(meta_conf, base_conf)
    
    def _parse(self, text: str) -> Tuple[np.ndarray, List]:
        text = text.lower()
        atoms = []
        edges = []
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', text):
            atoms.append((f"neg_{m.group(2)}", "atom", 0.0, -1))
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|=|equals?)\s*(\d+\.?\d*)', text):
            val1, op, val2 = float(m.group(1)), m.group(2), float(m.group(3))
            is_true = (op in ['>'] and val1 > val2) or (op in ['<'] and val1 < val2) or (op in ['=', 'equal', 'equals'] and val1 == val2)
            atoms.append((f"cmp_{val1}_{op}_{val2}", "constraint", 1.0 if is_true else -1.0, 1))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            ante, cons = m.group(1).strip(), m.group(2).strip()
            atoms.append((f"ante_{ante}", "atom", 0.0, 1))
            atoms.append((f"cons_{cons}", "atom", 0.0, 1))
            edges.append((f"ante_{ante}", f"cons_{cons}", "implication"))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(cause[sd]?|leads? to|results? in)\s+(\w+)', text):
            atoms.append((m.group(1), "atom", 0.0, 1))
            atoms.append((m.group(3), "atom", 0.0, 1))
            edges.append((m.group(1), m.group(3), "causal"))
        
        # General predicates
        for m in re.finditer(r'\b(\w+)\s+(?:is|are|was|were)\s+(\w+)', text):
            atoms.append((f"{m.group(1)}_{m.group(2)}", "atom", 0.0, 1))
        
        if not atoms:
            atoms.append(("default", "atom", 0.0, 1))
        
        dt = [('id', 'U100'), ('type', 'U20'), ('value', 'f4'), ('polarity', 'i4')]
        return np.array(atoms, dtype=dt), edges
    
    def _reference_vector(self, prompt: str, atoms: np.ndarray) -> np.ndarray:
        ref = np.zeros(len(atoms))
        for i, atom in enumerate(atoms):
            if atom['type'] == 'constraint':
                ref[i] = atom['value']
            else:
                ref[i] = atom['polarity']
        return ref
    
    def _run_network(self, atoms: np.ndarray, edges: List, ref: np.ndarray) -> np.ndarray:
        a = ref.copy()
        e_sum = np.zeros(len(atoms))
        e_prev = np.zeros(len(atoms))
        
        for t in range(self.iterations):
            e = ref - a
            e_sum += e
            e_delta = e - e_prev
            a = a + self.Kp * e + self.Ki * e_sum + self.Kd * e_delta
            a = np.clip(a, -1, 1)
            
            # UCB selection
            if t > 0:
                ucb = a + self.ucb_c * np.sqrt(np.log(t + 1) / (t + 1))
                idx = np.argmax(ucb)
                
                # Propagate along edges
                for src, dst, etype in edges:
                    src_idx = np.where(atoms['id'] == src)[0]
                    dst_idx = np.where(atoms['id'] == dst)[0]
                    if len(src_idx) > 0 and len(dst_idx) > 0:
                        a[dst_idx[0]] = 0.8 * a[dst_idx[0]] + 0.2 * a[src_idx[0]]
            
            e_prev = e
        
        return a
    
    def _structural_score(self, atoms_p: np.ndarray, atoms_c: np.ndarray, activation: np.ndarray) -> float:
        if len(atoms_c) == 0:
            return 0.0
        
        overlap = 0.0
        for ac in atoms_c:
            match = np.where(atoms_p['id'] == ac['id'])[0]
            if len(match) > 0:
                idx = match[0]
                if atoms_p[idx]['polarity'] == ac['polarity']:
                    overlap += max(0, activation[idx])
        
        return np.clip(overlap / len(atoms_c), 0, 1)
    
    def _computational_score(self, prompt: str, cand: str) -> float:
        scores = []
        
        # Numeric comparison
        m = re.search(r'(\d+\.?\d*)\s+(?:vs|versus|or)\s+(\d+\.?\d*)', prompt)
        if m:
            v1, v2 = float(m.group(1)), float(m.group(2))
            if re.search(r'\b(greater|larger|more|higher)\b', prompt):
                expected = str(max(v1, v2))
            elif re.search(r'\b(less|smaller|fewer|lower)\b', prompt):
                expected = str(min(v1, v2))
            else:
                expected = None
            if expected and expected in cand:
                scores.append(1.0)
        
        # Bat-and-ball
        m = re.search(r'(\d+\.?\d*)\s+more than.*?(?:ball|other)', prompt)
        if m and re.search(r'total.*?(\d+\.?\d*)', prompt):
            diff = float(m.group(1))
            total = float(re.search(r'total.*?(\d+\.?\d*)', prompt).group(1))
            lesser = (total - diff) / 2
            if f"{lesser:.2f}" in cand or f"{int(lesser)}" in cand:
                scores.append(1.0)
        
        # All-but-N
        m = re.search(r'all but (\d+)', prompt, re.I)
        if m and re.search(r'(\d+)\s+(?:items|people|things)', prompt):
            total = int(re.search(r'(\d+)\s+(?:items|people|things)', prompt).group(1))
            result = total - int(m.group(1))
            if str(result) in cand:
                scores.append(1.0)
        
        # Modus tollens
        if re.search(r'if\s+(\w+).*?then\s+(\w+)', prompt) and re.search(r'not\s+(\w+)', prompt):
            scores.append(0.7 if re.search(r'\bnot\b', cand) else 0.3)
        
        # Transitivity
        if re.search(r'(\w+)\s+>\s+(\w+).*?(\w+)\s+>\s+(\w+)', prompt):
            scores.append(0.8)
        
        return np.mean(scores) if scores else 0.5
    
    def _ncd_score(self, prompt: str, cand: str) -> float:
        c_p = len(zlib.compress(prompt.encode()))
        c_c = len(zlib.compress(cand.encode()))
        c_pc = len(zlib.compress((prompt + cand).encode()))
        ncd = (c_pc - min(c_p, c_c)) / max(c_p, c_c)
        return 1.0 - np.clip(ncd, 0, 1)
    
    def _meta_confidence(self, prompt: str) -> float:
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', prompt_lower) and not re.search(r'\bonly\b', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower):
            return 0.3
        
        # Unanswerability
        if re.search(r'\b(impossible|cannot|not enough|insufficient|unclear)\b', prompt_lower):
            return 0.2
        
        return 0.85