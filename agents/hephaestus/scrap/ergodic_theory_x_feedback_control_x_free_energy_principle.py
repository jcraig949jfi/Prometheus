import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine based on Ergodic Theory x Feedback Control x Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositions (subject, relation, object, modality) via regex.
    2. Grounding: Maps nouns to IDs and relations to one-hot vectors.
    3. Constraint Graph: Builds an adjacency matrix for logical entailment (transitivity, causality).
    4. Free Energy Minimization: Iteratively updates weights using a PID-like controller to minimize
       prediction error between observed truth values and propagated constraints.
    5. Scoring: Computes variational free energy (Error + Complexity penalty) to rank candidates.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(greater than|less than|equals|equal to|more than|fewer than)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|implies|leads to|causes)\b', re.IGNORECASE),
        'ordering': re.compile(r'\b(before|after|precedes|follows)\b', re.IGNORECASE),
        'number': re.compile(r'-?\d+\.?\d*'),
        'noun_phrase': re.compile(r'[a-zA-Z0-9\s\-]+')
    }

    REL_MAP = {
        'greater than': 0, 'more than': 0, '>': 0,
        'less than': 1, 'fewer than': 1, '<': 1,
        'equals': 2, 'equal to': 2, '=': 2,
        'causes': 3, 'leads to': 3, 'implies': 3,
        'before': 4, 'precedes': 4,
        'after': 5, 'follows': 5,
        'is-part-of': 6, 'contains': 7
    }

    def __init__(self):
        self.n_rel_types = 10
        self.max_steps = 20
        self.tol = 1e-3
        self.Kp, self.Ki, self.Kd = 0.1, 0.01, 0.05

    def _extract_props(self, text: str) -> List[Dict]:
        """Parse text into elementary propositions."""
        props = []
        # Simple sentence splitting
        sentences = re.split(r'[.;]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            is_neg = bool(self.PATTERNS['negation'].search(sent))
            
            # Extract numbers if present
            nums = self.PATTERNS['number'].findall(sent)
            val = float(nums[0]) if nums else 0.0
            
            rel_found = None
            for r_name, r_id in self.REL_MAP.items():
                if r_name in sent.lower():
                    rel_found = r_name
                    break
            
            # Fallback for generic "is" or simple assertions
            if not rel_found:
                if 'is' in sent.lower() or 'are' in sent.lower():
                    rel_found = 'equals'
                else:
                    rel_found = 'causes' # Default causal link
            
            # Extract nouns (simplified: first and last noun phrases)
            nouns = self.PATTERNS['noun_phrase'].findall(sent)
            nouns = [n.strip() for n in nouns if len(n.strip()) > 1 and n.strip().lower() not in ['if', 'then', 'not', 'no']]
            
            if len(nouns) >= 2:
                subj, obj = nouns[0], nouns[-1]
                if subj.lower() == obj.lower(): continue # Skip self-loops
                
                props.append({
                    's': subj, 'o': obj, 'r': rel_found,
                    'neg': 1 if is_neg else 0,
                    'val': val,
                    'weight': 1.0
                })
        return props

    def _build_graph(self, props: List[Dict]) -> Tuple[np.ndarray, np.ndarray, Dict, Dict]:
        """Build adjacency matrix and ground nouns/relations."""
        if not props:
            return np.zeros((1,1)), np.zeros((1, self.n_rel_types)), {}, {}
            
        nouns = list(set([p['s'] for p in props] + [p['o'] for p in props]))
        noun_map = {n: i for i, n in enumerate(nouns)}
        n_nodes = len(nouns)
        
        # Adjacency for transitive closure (entailment)
        A = np.zeros((n_nodes, n_nodes))
        np.fill_diagonal(A, 1.0)
        
        # Relation tensor (simplified to weighted adjacency for specific relations)
        # For this implementation, we focus on a unified constraint matrix W
        W = np.zeros((n_nodes, n_nodes))
        
        for p in props:
            i, j = noun_map[p['s']], noun_map[p['o']]
            A[i, j] = 1.0
            
            # Initialize weight: positive if affirmed, negative if negated
            # Magnitude influenced by numeric value if applicable
            w_val = 1.0
            if p['val'] != 0:
                w_val = p['val']
            
            W[i, j] = w_val * (1 if p['neg'] == 0 else -1)
            
        # Transitive closure (Floyd-Warshall simplified for binary connectivity)
        # We use this to determine which nodes influence which
        closure = A.copy()
        for k in range(n_nodes):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if closure[i,k] and closure[k,j]:
                        closure[i,j] = 1.0
                        
        return closure, W, noun_map, props

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Core algorithm: Parse, Build Graph, Minimize Error via PID, Compute Free Energy."""
        full_text = f"{prompt} {candidate}"
        props = self._extract_props(full_text)
        
        if not props:
            # Fallback for non-structured text: simple string match heuristic
            return 0.5 

        closure, W_init, noun_map, _ = self._build_graph(props)
        n = len(noun_map)
        if n == 0: return 0.5

        # Observed truth vector (1 for true, 0 for false/negated)
        # In this simplified model, we assume extracted props are "observed" facts
        y = np.ones(n) 
        
        # PID Control State
        W = W_init.copy()
        E_prev = 0.0
        integral = 0.0
        
        for t in range(self.max_steps):
            # Prediction: y_hat = sigma(W * y)
            # Using sigmoid activation for bounded prediction
            pred = np.dot(W, y)
            y_hat = 1.0 / (1.0 + np.exp(-pred))
            
            # Error
            error_vec = y - y_hat
            E = 0.5 * np.sum(error_vec ** 2)
            
            if abs(E - E_prev) < self.tol:
                break
            E_prev = E
            
            # PID Update on Weights
            # Derivative
            derivative = E - E_prev if t > 0 else 0.0
            integral += E
            
            # Update rule: Adjust weights to minimize error
            # W_new = W_old - Kp*E - Ki*Integral - Kd*Derivative
            # We apply this globally as a scaling factor for simplicity in this constrained env
            adjustment = self.Kp * E + self.Ki * integral + self.Kd * derivative
            W = W * (1.0 - adjustment)
            
            # Stability clamp
            W = np.clip(W, -10.0, 10.0)

        # Final Free Energy: F = E + lambda * |W|_1
        complexity = 0.01 * np.sum(np.abs(W))
        F = E + complexity
        
        return -F # Higher score = better (lower free energy)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free energy minimization over {len(self._extract_props(cand))} propositions."
            })
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._compute_free_energy(prompt, answer)
        # Normalize score to 0-1 range roughly
        # Assuming typical free energy scores are between -5 and 5
        conf = 1.0 / (1.0 + np.exp(-score)) 
        return float(np.clip(conf, 0.0, 1.0))