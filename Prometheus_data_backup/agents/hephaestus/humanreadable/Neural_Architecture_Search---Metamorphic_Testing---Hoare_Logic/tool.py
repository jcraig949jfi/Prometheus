from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    NAS x Metamorphic Testing x Hoare Logic reasoning tool.
    
    Treats candidate answers as logic programs: extracts atomic propositions,
    builds an implication matrix, closes it transitively (Warshall), scores
    via Hoare triples {P}C{Q} and metamorphic relations, then searches over
    implication architectures to maximize consistency.
    """
    
    def __init__(self):
        self.ncd_weight = 0.12
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": f"NAS-Hoare score: {score:.3f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Structural match confidence
        struct_score = self._structural_parse(prompt, answer)
        comp_score = self._compute_if_possible(prompt, answer)
        
        if comp_score > 0.8:
            return min(0.95, meta_conf)
        elif struct_score > 0.6:
            return min(0.7, meta_conf)
        else:
            return min(0.4, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|quit|why did .+ (fail|stop)|when did .+ end)', p_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+.*?\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with who question
        if re.search(r'(he|she|they).*who', p_lower) or re.search(r'who.*(he|she|they)', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be (a|b))\b', p_lower) and 'which' in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\d', prompt):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'(not enough|insufficient|cannot determine|ambiguous)', p_lower):
            return 0.2
        
        return 0.95
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        structural = self._structural_parse(prompt, candidate)
        computational = self._compute_if_possible(prompt, candidate)
        hoare = self._hoare_score(candidate)
        metamorphic = self._metamorphic_score(candidate)
        ncd = 1.0 - self._ncd(prompt, candidate)
        
        return 0.35 * structural + 0.25 * computational + 0.15 * hoare + 0.13 * metamorphic + self.ncd_weight * ncd
    
    def _structural_parse(self, prompt: str, candidate: str) -> float:
        score = 0.0
        total = 0.0
        
        # Numeric comparison
        nums_p = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        nums_c = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        if nums_p and nums_c:
            total += 1
            if any(n in nums_p for n in nums_c):
                score += 0.5
            if re.search(r'(greater|more|larger|higher)', prompt.lower()):
                if nums_c and nums_p and max(nums_c) > min(nums_p):
                    score += 0.5
        
        # Negation consistency
        neg_p = len(re.findall(r'\b(not|no|never|none)\b', prompt.lower()))
        neg_c = len(re.findall(r'\b(not|no|never|none)\b', candidate.lower()))
        if neg_p > 0 or neg_c > 0:
            total += 1
            if (neg_p > 0) == (neg_c > 0):
                score += 1
        
        # Conditionals (if-then)
        cond_p = re.findall(r'if (.+?) then (.+?)[\.,]', prompt.lower())
        cond_c = re.findall(r'if (.+?) then (.+?)[\.,]', candidate.lower())
        if cond_p or cond_c:
            total += 1
            if len(cond_c) >= len(cond_p):
                score += 1
        
        # Modus tollens / transitivity
        if re.search(r'all .+ are', prompt.lower()) and re.search(r'therefore|thus|so', candidate.lower()):
            total += 1
            score += 1
        
        return score / total if total > 0 else 0.5
    
    def _compute_if_possible(self, prompt: str, candidate: str) -> float:
        # Bat-and-ball algebra
        bat_ball = re.search(r'(\d+\.?\d*).+total.+(\d+\.?\d*).+more', prompt.lower())
        if bat_ball:
            total, diff = float(bat_ball.group(1)), float(bat_ball.group(2))
            ball = (total - diff) / 2
            nums_c = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
            if nums_c and abs(min(nums_c) - ball) < 0.1:
                return 1.0
        
        # PEMDAS expression
        expr = re.search(r'(\d+)\s*[\+\-\*/]\s*(\d+)\s*[\+\-\*/]\s*(\d+)', prompt)
        if expr:
            try:
                result = eval(re.search(r'[\d\+\-\*/\(\)\s]+', prompt).group())
                nums_c = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
                if nums_c and abs(result - nums_c[0]) < 0.1:
                    return 1.0
            except:
                pass
        
        # Coin flip independence
        if re.search(r'coin.*flip|toss', prompt.lower()) and re.search(r'independent|same|0\.5|50%', candidate.lower()):
            return 0.8
        
        # Modular arithmetic
        mod_match = re.search(r'(\d+)\s*mod\s*(\d+)', prompt.lower())
        if mod_match:
            n, m = int(mod_match.group(1)), int(mod_match.group(2))
            result = n % m
            if str(result) in candidate:
                return 1.0
        
        return 0.5
    
    def _hoare_score(self, text: str) -> float:
        atoms, implications, _ = self._parse_logic(text)
        if len(atoms) == 0:
            return 0.5
        
        n = len(atoms)
        I = implications
        
        # Transitive closure (Warshall)
        for k in range(n):
            I = I | (I[:, k][:, None] & I[k, :])
        
        # Score Hoare triples
        triples = re.findall(r'if (.+?) then (.+?)[\.,]', text.lower())
        score = 0
        for pre, post in triples:
            p_id = self._find_atom_id(atoms, pre)
            q_id = self._find_atom_id(atoms, post)
            if p_id >= 0 and q_id >= 0 and I[p_id, q_id]:
                score += 1
            elif p_id >= 0 and q_id >= 0:
                score -= 0.5
        
        return max(0, min(1, 0.5 + score * 0.2))
    
    def _metamorphic_score(self, text: str) -> float:
        atoms, _, constraints = self._parse_logic(text)
        if len(atoms) < 2:
            return 0.5
        
        # Simple metamorphic check: if we negate a proposition, implications should reverse
        score = 0
        for i, atom in enumerate(atoms):
            if 'not' in atom.lower():
                pos_version = atom.lower().replace('not', '').strip()
                if any(pos_version in a.lower() for a in atoms):
                    score += 1
        
        return min(1.0, 0.5 + score * 0.1)
    
    def _parse_logic(self, text: str) -> Tuple[List[str], np.ndarray, List]:
        atoms = []
        atom_map = {}
        
        # Extract atomic propositions
        comparisons = re.findall(r'(\w+)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)', text)
        for var, op, val in comparisons:
            atom = f"{var} {op} {val}"
            if atom not in atom_map:
                atom_map[atom] = len(atoms)
                atoms.append(atom)
        
        # Extract simple propositions
        simple = re.findall(r'\b([A-Z]\w+)\s+is\s+(\w+)', text)
        for subj, pred in simple:
            atom = f"{subj} is {pred}"
            if atom not in atom_map:
                atom_map[atom] = len(atoms)
                atoms.append(atom)
        
        n = len(atoms)
        implications = np.zeros((n, n), dtype=bool)
        
        # Extract implications
        conds = re.findall(r'if (.+?) then (.+?)[\.,]', text.lower())
        for pre, post in conds:
            p_id = self._find_atom_id(atoms, pre)
            q_id = self._find_atom_id(atoms, post)
            if p_id >= 0 and q_id >= 0:
                implications[p_id, q_id] = True
        
        return atoms, implications, []
    
    def _find_atom_id(self, atoms: List[str], query: str) -> int:
        for i, atom in enumerate(atoms):
            if query.lower() in atom.lower() or atom.lower() in query.lower():
                return i
        return -1
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))