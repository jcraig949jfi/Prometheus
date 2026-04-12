from typing import Dict, Tuple

import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Category Theory x Embodied Cognition x Satisfiability reasoner.
    Parses text to labeled graphs, grounds atoms to feature vectors,
    converts to CNF, performs unit propagation, and computes scores
    combining SAT satisfaction, unsatisfiable core, and embodiment similarity.
    """
    
    def __init__(self):
        self.weights = {'sat': 0.5, 'core': 0.3, 'emb': 0.2}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we have a computational solution
        comp_result = self._compute_answer(prompt)
        if comp_result is not None:
            # Deterministic answer from computation
            if self._answers_match(comp_result, answer):
                return 0.85
            else:
                return 0.15
        
        # Use scoring
        score, _ = self._score_candidate(prompt, answer)
        conf = min(0.75, max(0.25, score))
        return min(conf, meta_conf + 0.4)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition detection
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does) .+ (fail|stop|end)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|did)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+[?]', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        # Insufficient information
        if 'not enough information' in p or 'cannot be determined' in p:
            return 0.25
        
        return 0.8
    
    def _compute_answer(self, prompt: str):
        # Numeric comparison
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) == 2 and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'more', 'fewer']):
            a, b = float(nums[0]), float(nums[1])
            if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'more' in prompt.lower():
                return str(max(a, b))
            else:
                return str(min(a, b))
        
        # Bat and ball algebra: total - small = large
        if 'bat' in prompt.lower() and 'ball' in prompt.lower():
            match = re.search(r'(\d+\.?\d*).+more than.+ball', prompt.lower())
            if match and len(nums) >= 2:
                total = float(nums[0])
                diff = float(match.group(1))
                ball = (total - diff) / 2
                return f"{ball:.2f}"
        
        # Modular arithmetic
        if 'remainder' in prompt.lower() or 'modulo' in prompt.lower():
            if len(nums) >= 2:
                return str(int(nums[0]) % int(nums[1]))
        
        # Temporal ordering - simple first/last
        time_words = re.findall(r'\b(first|second|third|last|before|after)\b', prompt.lower())
        if time_words:
            items = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if 'first' in time_words and items:
                return items[0]
            if 'last' in time_words and items:
                return items[-1]
        
        return None
    
    def _answers_match(self, comp: str, cand: str) -> bool:
        c1, c2 = comp.lower().strip(), cand.lower().strip()
        if c1 == c2:
            return True
        if c1 in c2 or c2 in c1:
            return True
        try:
            if abs(float(c1) - float(c2)) < 0.01:
                return True
        except:
            pass
        return False
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        # Parse to graphs
        g_p = self._parse_graph(prompt)
        g_c = self._parse_graph(candidate)
        
        # Convert to CNF and solve
        cnf_p = self._graph_to_cnf(g_p)
        cnf_c = self._graph_to_cnf(g_c)
        cnf_combined = np.vstack([cnf_p, cnf_c]) if cnf_p.size > 0 and cnf_c.size > 0 else cnf_p
        
        sat_score, core_size = self._sat_solve(cnf_combined)
        
        # Embodiment similarity
        emb_p = self._aggregate_embeddings(g_p)
        emb_c = self._aggregate_embeddings(g_c)
        emb_sim = self._cosine_sim(emb_p, emb_c)
        
        # Compute NCD tiebreaker
        ncd = self._ncd(prompt, candidate)
        
        # Final score
        m = max(1, cnf_combined.shape[0])
        score = (self.weights['sat'] * sat_score / m - 
                 self.weights['core'] * core_size / m + 
                 self.weights['emb'] * emb_sim +
                 0.1 * (1 - ncd))
        
        reasoning = f"SAT:{sat_score}/{m}, Core:{core_size}, Emb:{emb_sim:.2f}, NCD:{ncd:.2f}"
        return score, reasoning
    
    def _parse_graph(self, text: str) -> Dict:
        atoms = []
        edges = []
        
        # Extract atoms (simple noun phrases and clauses)
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
            atoms.append(sent)
            
            # Extract relations
            if re.search(r'\bif .+ then\b', sent.lower()):
                parts = re.split(r'\bthen\b', sent.lower())
                if len(parts) == 2:
                    edges.append(('implies', parts[0].strip(), parts[1].strip()))
            
            if re.search(r'\bnot\b|\bno\b|\bnever\b', sent.lower()):
                edges.append(('negation', sent, ''))
            
            if re.search(r'(greater|less|more|fewer) than', sent.lower()):
                edges.append(('comparative', sent, ''))
            
            if re.search(r'\b(before|after|first|last)\b', sent.lower()):
                edges.append(('ordering', sent, ''))
        
        return {'atoms': atoms, 'edges': edges}
    
    def _graph_to_cnf(self, graph: Dict) -> np.ndarray:
        atoms = graph['atoms']
        if not atoms:
            return np.array([]).reshape(0, 0)
        
        n = len(atoms)
        clauses = []
        
        # Each atom becomes a clause
        for i in range(n):
            clause = np.zeros(n)
            clause[i] = 1
            clauses.append(clause)
        
        # Process edges
        for edge_type, src, tgt in graph['edges']:
            if edge_type == 'implies' and src in atoms and tgt in atoms:
                i, j = atoms.index(src), atoms.index(tgt)
                clause = np.zeros(n)
                clause[i] = -1
                clause[j] = 1
                clauses.append(clause)
            elif edge_type == 'negation':
                for i, atom in enumerate(atoms):
                    if atom == src:
                        clause = np.zeros(n)
                        clause[i] = -1
                        clauses.append(clause)
        
        return np.array(clauses) if clauses else np.array([]).reshape(0, n)
    
    def _sat_solve(self, cnf: np.ndarray) -> Tuple[int, int]:
        if cnf.size == 0:
            return 0, 0
        
        m, n = cnf.shape
        assignment = np.zeros(n, dtype=int)
        
        # Unit propagation
        for _ in range(10):
            changed = False
            for i in range(m):
                clause = cnf[i]
                unassigned = np.where((clause != 0) & (assignment == 0))[0]
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    assignment[lit] = 1 if clause[lit] > 0 else -1
                    changed = True
            if not changed:
                break
        
        # Count satisfied clauses
        satisfied = 0
        for i in range(m):
            clause = cnf[i]
            if any((clause[j] > 0 and assignment[j] > 0) or 
                   (clause[j] < 0 and assignment[j] < 0) for j in range(n)):
                satisfied += 1
        
        # Approximate unsat core
        core_size = m - satisfied
        
        return satisfied, core_size
    
    def _aggregate_embeddings(self, graph: Dict) -> np.ndarray:
        atoms = graph['atoms']
        if not atoms:
            return np.zeros(5)
        
        embeddings = []
        for atom in atoms:
            emb = self._ground_atom(atom)
            embeddings.append(emb)
        
        agg = np.mean(embeddings, axis=0)
        norm = np.linalg.norm(agg)
        return agg / norm if norm > 0 else agg
    
    def _ground_atom(self, atom: str) -> np.ndarray:
        emb = np.zeros(5)
        atom_l = atom.lower()
        
        # Motion verbs
        if any(w in atom_l for w in ['move', 'run', 'walk', 'fly', 'jump', 'go']):
            emb[0] = 1
        
        # Spatial prepositions
        if any(w in atom_l for w in ['in', 'on', 'above', 'below', 'left', 'right', 'near', 'far']):
            emb[1] = 1
        
        # Size adjectives
        if any(w in atom_l for w in ['big', 'small', 'large', 'tiny', 'huge', 'tall', 'short']):
            emb[2] = 1
        
        # Valence words
        if any(w in atom_l for w in ['good', 'bad', 'happy', 'sad', 'love', 'hate']):
            emb[3] = 1
        
        # Numeric magnitude
        nums = re.findall(r'\d+', atom)
        if nums:
            emb[4] = min(1.0, sum(int(n) for n in nums) / 100.0)
        
        norm = np.linalg.norm(emb)
        return emb / norm if norm > 0 else emb
    
    def _cosine_sim(self, a: np.ndarray, b: np.ndarray) -> float:
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0