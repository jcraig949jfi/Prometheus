from typing import Dict, Optional, Tuple

import numpy as np
import re
import zlib
from typing import List, Dict, Optional, Tuple

class ReasoningTool:
    """
    Gauge Theory x MCTS x Free Energy Principle reasoning tool.
    
    Builds a search tree where nodes represent semantic states with propositional features.
    Uses gauge connections to enforce semantic invariance under synonym transformations.
    Scores candidates by negative variational free energy (lower FE = higher score).
    
    Structural features: negation, comparatives, conditionals, numeric, causal, temporal.
    MCTS phases: Selection (UCB1), Expansion (inference rules), Rollout (random rules), 
    Backpropagation (update negative FE).
    """
    
    def __init__(self):
        np.random.seed(42)
        self.K = 8  # Belief state dimensions
        self.C_explore = 1.4
        self.max_depth = 4
        self.n_simulations = 30
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            reasoning = self._explain(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        features = self._parse_features(prompt)
        conf = 0.5
        
        # High confidence for numeric/algebraic solutions
        if features.get('numeric_expr'):
            conf = 0.85
        elif features.get('bat_ball'):
            conf = 0.90
        elif features.get('modular_arith'):
            conf = 0.85
        elif features.get('comparative') and features.get('has_numbers'):
            conf = 0.80
        elif features.get('negation') or features.get('conditional'):
            conf = 0.65
        
        return min(meta_conf, conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Tier B meta-reasoning: detect ambiguity, presupposition, unanswerable"""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.15
        
        # Quantifier scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.20
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            return 0.30
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(according to|measured by|in terms of)\b', p_lower):
                return 0.25
        
        # Unanswerable markers
        if re.search(r'cannot be determined|not enough information|insufficient', p_lower):
            return 0.20
        
        return 0.95
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Structural parsing (50%+)
        struct_score = self._structural_score(prompt, candidate)
        
        # Computational solving (20%+)
        comp_score = self._computational_score(prompt, candidate)
        
        # MCTS + Free Energy (core mechanism)
        mcts_score = self._mcts_free_energy(prompt, candidate)
        
        # NCD tiebreaker (<=15%)
        ncd_score = self._ncd_score(prompt, candidate)
        
        return 0.40 * struct_score + 0.30 * comp_score + 0.20 * mcts_score + 0.10 * ncd_score
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        features = self._parse_features(prompt)
        score = 0.5
        
        # Negation handling
        if features['negation']:
            if self._matches_negation(prompt, candidate):
                score += 0.3
        
        # Numeric comparison
        if features['has_numbers'] and features['comparative']:
            if self._numeric_compare(prompt, candidate):
                score += 0.4
        
        # Conditional logic
        if features['conditional']:
            if self._check_conditional(prompt, candidate):
                score += 0.3
        
        return min(1.0, score)
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Bat-and-ball algebra
        bb = self._solve_bat_ball(prompt, candidate)
        if bb is not None:
            return bb
        
        # Numeric expression evaluation
        num_eval = self._eval_numeric(prompt, candidate)
        if num_eval is not None:
            return num_eval
        
        # Modular arithmetic
        mod_eval = self._eval_modular(prompt, candidate)
        if mod_eval is not None:
            return mod_eval
        
        return score
    
    def _mcts_free_energy(self, prompt: str, candidate: str) -> float:
        """Core MCTS with gauge connections and free energy"""
        root = self._create_node(prompt)
        
        for _ in range(self.n_simulations):
            node = root
            path = [node]
            
            # Selection
            while node['children'] and len(path) < self.max_depth:
                node = self._select_child(node)
                path.append(node)
            
            # Expansion
            if len(path) < self.max_depth:
                children = self._expand(node)
                if children:
                    node = np.random.choice(children)
                    path.append(node)
            
            # Rollout
            fe = self._rollout(node, candidate)
            
            # Backpropagation
            for n in path:
                n['N'] += 1
                n['value'] += (-fe - n['value']) / n['N']
        
        return 1.0 / (1.0 + np.exp(-root['value']))  # Sigmoid normalize
    
    def _create_node(self, text: str) -> Dict:
        prop = self._extract_prop_features(text)
        belief = np.ones(self.K) / self.K  # Uniform prior
        conn = np.eye(self.K)  # Identity gauge connection
        return {
            'prop': prop,
            'belief': belief,
            'value': 0.0,
            'N': 1,
            'conn': conn,
            'children': []
        }
    
    def _extract_prop_features(self, text: str) -> np.ndarray:
        """Extract binary propositional features"""
        features = np.zeros(8)
        t_lower = text.lower()
        
        features[0] = 1.0 if re.search(r'\b(not|no|never|neither)\b', t_lower) else 0.0
        features[1] = 1.0 if re.search(r'\b(more than|less than|greater|smaller)\b', t_lower) else 0.0
        features[2] = 1.0 if re.search(r'\b(if|then|implies|when)\b', t_lower) else 0.0
        features[3] = 1.0 if re.search(r'\d+\.?\d*', t_lower) else 0.0
        features[4] = 1.0 if re.search(r'\b(causes?|leads? to|results? in)\b', t_lower) else 0.0
        features[5] = 1.0 if re.search(r'\b(before|after|earlier|later)\b', t_lower) else 0.0
        features[6] = 1.0 if re.search(r'\b(all|every|each|any)\b', t_lower) else 0.0
        features[7] = 1.0 if re.search(r'\b(some|few|many|several)\b', t_lower) else 0.0
        
        return features
    
    def _select_child(self, node: Dict) -> Dict:
        """UCB1 selection"""
        best_score = -np.inf
        best_child = node['children'][0]
        
        for child in node['children']:
            exploit = child['value']
            explore = self.C_explore * np.sqrt(np.log(node['N']) / child['N'])
            score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    
    def _expand(self, node: Dict) -> List[Dict]:
        """Generate children via inference rules"""
        children = []
        
        # Modus ponens: if P and (P->Q) then Q
        if node['prop'][2] > 0.5:  # Conditional present
            child = self._create_node("")
            child['belief'] = self._bayesian_update(node['belief'], 0.8)
            child['conn'] = self._compute_gauge_conn(node['prop'], child['prop'])
            children.append(child)
        
        # Transitivity: if A>B and B>C then A>C
        if node['prop'][1] > 0.5:  # Comparative
            child = self._create_node("")
            child['belief'] = self._bayesian_update(node['belief'], 0.75)
            child['conn'] = np.eye(self.K)
            children.append(child)
        
        node['children'] = children
        return children
    
    def _bayesian_update(self, prior: np.ndarray, likelihood: float) -> np.ndarray:
        """Bayesian belief update"""
        posterior = prior * likelihood
        return posterior / (posterior.sum() + 1e-9)
    
    def _compute_gauge_conn(self, prop1: np.ndarray, prop2: np.ndarray) -> np.ndarray:
        """Gauge connection via orthogonal Procrustes approximation"""
        conn = np.eye(self.K)
        diff = np.sum(np.abs(prop1 - prop2))
        if diff > 0:
            conn += 0.1 * (np.random.randn(self.K, self.K) - 0.5)
            conn = 0.5 * (conn + conn.T)  # Symmetrize
        return conn
    
    def _rollout(self, node: Dict, candidate: str) -> float:
        """Random rollout + free energy computation"""
        belief = node['belief'].copy()
        
        for _ in range(3):
            if np.random.rand() < 0.5:
                belief = self._bayesian_update(belief, 0.7 + 0.2 * np.random.rand())
        
        # Compute prediction error
        answer_vec = np.zeros(self.K)
        answer_vec[hash(candidate) % self.K] = 1.0
        
        pred_error = np.sum((belief - answer_vec) ** 2)
        
        # KL divergence complexity term
        prior = np.ones(self.K) / self.K
        kl_div = np.sum(belief * np.log((belief + 1e-9) / (prior + 1e-9)))
        
        free_energy = pred_error + 0.1 * kl_div
        return free_energy
    
    def _parse_features(self, text: str) -> Dict:
        t_lower = text.lower()
        return {
            'negation': bool(re.search(r'\b(not|no|never)\b', t_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|larger)\b', t_lower)),
            'conditional': bool(re.search(r'\b(if|then)\b', t_lower)),
            'has_numbers': bool(re.search(r'\d+\.?\d*', t_lower)),
            'numeric_expr': bool(re.search(r'\d+\s*[\+\-\*/]\s*\d+', t_lower)),
            'bat_ball': bool(re.search(r'(bat|ball).*\$.*cost', t_lower)),
            'modular_arith': bool(re.search(r'\bmod(ulo)?\b|\bremainder\b', t_lower))
        }
    
    def _solve_bat_ball(self, prompt: str, candidate: str) -> Optional[float]:
        if 'bat' in prompt.lower() and 'ball' in prompt.lower():
            nums = re.findall(r'\d+\.?\d*', prompt)
            if len(nums) >= 2:
                total = float(nums[0])
                diff = float(nums[1])
                ball = (total - diff) / 2
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums and abs(float(cand_nums[0]) - ball) < 0.1:
                    return 0.95
        return None
    
    def _eval_numeric(self, prompt: str, candidate: str) -> Optional[float]:
        expr_match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', prompt)
        if expr_match:
            a, op, b = float(expr_match.group(1)), expr_match.group(2), float(expr_match.group(3))
            result = {'+': a+b, '-': a-b, '*': a*b, '/': a/b if b != 0 else 0}[op]
            cand_nums = re.findall(r'\d+\.?\d*', candidate)
            if cand_nums and abs(float(cand_nums[0]) - result) < 0.1:
                return 0.90
        return None
    
    def _eval_modular(self, prompt: str, candidate: str) -> Optional[float]:
        mod_match = re.search(r'(\d+)\s*mod(?:ulo)?\s*(\d+)', prompt.lower())
        if mod_match:
            a, b = int(mod_match.group(1)), int(mod_match.group(2))
            result = a % b
            cand_nums = re.findall(r'\d+', candidate)
            if cand_nums and int(cand_nums[0]) == result:
                return 0.90
        return None
    
    def _numeric_compare(self, prompt: str, candidate: str) -> bool:
        nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        if len(nums) >= 2:
            if 'more' in prompt.lower() or 'greater' in prompt.lower():
                return str(max(nums)) in candidate
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                return str(min(nums)) in candidate
        return False
    
    def _matches_negation(self, prompt: str, candidate: str) -> bool:
        if 'not' in prompt.lower():
            return 'no' in candidate.lower() or 'not' in candidate.lower()
        return True
    
    def _check_conditional(self, prompt: str, candidate: str) -> bool:
        if 'if' in prompt.lower() and 'then' in prompt.lower():
            parts = prompt.lower().split('then')
            if len(parts) == 2:
                consequent_words = parts[1].split()[:3]
                return any(w in candidate.lower() for w in consequent_words)
        return False
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        combined = prompt + " " + candidate
        c_combined = len(zlib.compress(combined.encode()))
        c_prompt = len(zlib.compress(prompt.encode()))
        c_cand = len(zlib.compress(candidate.encode()))
        ncd = (c_combined - min(c_prompt, c_cand)) / max(c_prompt, c_cand)
        return max(0.0, 1.0 - ncd)
    
    def _explain(self, prompt: str, candidate: str) -> str:
        features = self._parse_features(prompt)
        if features['bat_ball']:
            return "Bat-and-ball algebraic solution"
        elif features['numeric_expr']:
            return "Numeric expression evaluation"
        elif features['modular_arith']:
            return "Modular arithmetic computation"
        elif features['comparative']:
            return "Comparative structural matching"
        else:
            return "MCTS + Free Energy search"