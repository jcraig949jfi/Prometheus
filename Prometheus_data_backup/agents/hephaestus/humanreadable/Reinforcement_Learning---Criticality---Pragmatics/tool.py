from typing import Any, Dict, Tuple

"""
Reasoning Tool: RL x Criticality x Pragmatics
Combines reward-based evaluation, phase-transition susceptibility, and pragmatic filtering.
"""
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    def __init__(self):
        self.lambda_crit = 0.3
        self.c_explore = 0.5
        self.p_prag = 0.2
        self.sigma_perturb = 0.1
        self.k_perturb = 10
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        clauses = self._parse_clauses(prompt)
        results = []
        
        for cand in candidates:
            interp = self._ground_interpretation(prompt, cand)
            reward = self._compute_reward(clauses, interp, prompt, cand)
            suscept = self._compute_susceptibility(clauses, interp, prompt, cand)
            prag_penalty = self._pragmatic_penalty(prompt, cand)
            
            score = reward - prag_penalty
            results.append({
                'candidate': cand,
                'reward': reward,
                'suscept': suscept,
                'prag_penalty': prag_penalty,
                'score': score
            })
        
        # UCB-style exploration adjustment
        N = len(candidates)
        chi_median = np.median([r['suscept'] for r in results])
        for i, res in enumerate(results):
            ucb = res['score'] - self.lambda_crit * abs(res['suscept'] - chi_median) + self.c_explore * np.sqrt(np.log(N))
            res['final_score'] = ucb
            res['reasoning'] = f"Reward={res['reward']:.2f} Suscept={res['suscept']:.2f} Prag={res['prag_penalty']:.2f}"
        
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return [{'candidate': r['candidate'], 'score': r['final_score'], 'reasoning': r['reasoning']} for r in results]
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        clauses = self._parse_clauses(prompt)
        interp = self._ground_interpretation(prompt, answer)
        reward = self._compute_reward(clauses, interp, prompt, answer)
        suscept = self._compute_susceptibility(clauses, interp, prompt, answer)
        
        base_conf = min(reward * 0.9, 0.9)
        conf = base_conf * (1.0 - 0.3 * min(suscept, 1.0))
        return max(min(conf, meta_conf), 0.0)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|faster|slower|cheaper|expensive)\b', p_lower):
            return 0.3
        
        # Insufficient information markers
        if re.search(r'\b(not enough|cannot determine|insufficient|ambiguous)\b', p_lower):
            return 0.25
        
        return 1.0
    
    def _parse_clauses(self, prompt: str) -> List[Tuple]:
        clauses = []
        
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*(>=?|<=?|=)\s*(\d+\.?\d*)', prompt):
            clauses.append(('numeric', float(m.group(1)), m.group(2), float(m.group(3))))
        
        # Negations
        for m in re.finditer(r'\b(not|no|n\'t)\s+(\w+)', prompt.lower()):
            clauses.append(('negation', m.group(2), None, -1))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.,;]', prompt.lower()):
            clauses.append(('conditional', m.group(1).strip(), m.group(2).strip(), None))
        
        # Causal (bidirectional)
        for m in re.finditer(r'(.+?)\s+because\s+(.+?)[\.,;]', prompt.lower()):
            clauses.append(('causal', m.group(1).strip(), m.group(2).strip(), None))
        
        # Temporal ordering
        for m in re.finditer(r'(\w+)\s+before\s+(\w+)', prompt.lower()):
            clauses.append(('temporal', m.group(1), '<', m.group(2)))
        
        for m in re.finditer(r'(\w+)\s+after\s+(\w+)', prompt.lower()):
            clauses.append(('temporal', m.group(2), '<', m.group(1)))
        
        return clauses
    
    def _ground_interpretation(self, prompt: str, candidate: str) -> Dict[str, Any]:
        interp = {}
        
        # Computational solvers
        interp['numeric_result'] = self._solve_numeric(prompt)
        interp['bayesian_result'] = self._solve_bayesian(prompt)
        interp['logic_result'] = self._solve_logic(prompt)
        interp['constraint_result'] = self._solve_constraints(prompt)
        interp['candidate_text'] = candidate.lower()
        
        # Extract numbers from candidate
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
        interp['candidate_nums'] = nums
        
        # Extract boolean markers
        interp['is_yes'] = 'yes' in candidate.lower()
        interp['is_no'] = 'no' in candidate.lower()
        
        return interp
    
    def _solve_numeric(self, prompt: str) -> float:
        # Bat-and-ball type problems: X + Y = A, X - Y = B
        m = re.search(r'(\w+)\s+and\s+(\w+)\s+cost\s+\$?(\d+\.?\d*)', prompt)
        m2 = re.search(r'(\w+)\s+costs?\s+\$?(\d+\.?\d*)\s+more', prompt)
        if m and m2:
            total = float(m.group(3))
            diff = float(m2.group(2))
            return (total - diff) / 2.0
        
        # PEMDAS expressions
        expr_match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)\s*([\+\-\*/])\s*(\d+)', prompt)
        if expr_match:
            try:
                return eval(expr_match.group(0))
            except:
                pass
        
        # All-but-N problems
        m = re.search(r'all\s+but\s+(\d+)', prompt.lower())
        m2 = re.search(r'(\d+)\s+total', prompt.lower())
        if m and m2:
            return float(m2.group(1)) - float(m.group(1))
        
        return None
    
    def _solve_bayesian(self, prompt: str) -> float:
        # P(H|E) = P(E|H) * P(H) / P(E)
        prior_m = re.search(r'(\d+)%?\s+(?:of|are)', prompt)
        likelihood_m = re.search(r'(\d+)%?\s+(?:positive|detect)', prompt)
        false_pos_m = re.search(r'(\d+)%?\s+(?:false|error)', prompt)
        
        if prior_m and likelihood_m:
            prior = float(prior_m.group(1)) / 100.0
            likelihood = float(likelihood_m.group(1)) / 100.0
            false_pos = float(false_pos_m.group(1)) / 100.0 if false_pos_m else 0.01
            
            p_e = likelihood * prior + false_pos * (1 - prior)
            if p_e > 0:
                return (likelihood * prior) / p_e
        
        return None
    
    def _solve_logic(self, prompt: str) -> str:
        # Modus tollens: If P then Q, not Q, therefore not P
        if re.search(r'if\s+(.+?)\s+then', prompt.lower()) and re.search(r'not\s+', prompt.lower()):
            return 'modus_tollens'
        
        # Transitivity: A > B, B > C => A > C
        comparisons = re.findall(r'(\w+)\s+(?:>|greater|more|faster)\s+(?:than\s+)?(\w+)', prompt.lower())
        if len(comparisons) >= 2:
            if comparisons[0][1] == comparisons[1][0]:
                return comparisons[0][0] + '_gt_' + comparisons[1][1]
        
        return None
    
    def _solve_constraints(self, prompt: str) -> Dict:
        # Extract entities and constraints
        entities = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        constraints = {}
        
        # Position constraints: X is first/second/last
        for m in re.finditer(r'([A-Z][a-z]+)\s+is\s+(first|second|third|last)', prompt):
            constraints[m.group(1)] = m.group(2)
        
        # Adjacency: X is next to Y
        for m in re.finditer(r'([A-Z][a-z]+)\s+(?:next to|beside)\s+([A-Z][a-z]+)', prompt):
            constraints[m.group(1)] = 'adjacent_' + m.group(2)
        
        return constraints
    
    def _compute_reward(self, clauses: List[Tuple], interp: Dict, prompt: str, candidate: str) -> float:
        if not clauses:
            # Fallback to computational match
            return self._computational_match(interp, candidate)
        
        satisfied = 0
        for clause in clauses:
            if self._is_satisfied(clause, interp, candidate):
                satisfied += 1
        
        base_reward = satisfied / len(clauses) if clauses else 0.0
        comp_reward = self._computational_match(interp, candidate)
        
        return 0.6 * base_reward + 0.4 * comp_reward
    
    def _computational_match(self, interp: Dict, candidate: str) -> float:
        score = 0.0
        count = 0
        
        # Numeric match
        if interp['numeric_result'] is not None and interp['candidate_nums']:
            for num in interp['candidate_nums']:
                if abs(num - interp['numeric_result']) < 0.01:
                    score += 1.0
            count += 1
        
        # Bayesian match
        if interp['bayesian_result'] is not None and interp['candidate_nums']:
            for num in interp['candidate_nums']:
                if abs(num - interp['bayesian_result'] * 100) < 1.0:
                    score += 1.0
            count += 1
        
        # Logic match
        if interp['logic_result'] is not None:
            if interp['logic_result'] in candidate.lower():
                score += 1.0
            count += 1
        
        return score / count if count > 0 else 0.5
    
    def _is_satisfied(self, clause: Tuple, interp: Dict, candidate: str) -> bool:
        c_type = clause[0]
        
        if c_type == 'numeric':
            if not interp['candidate_nums']:
                return False
            val1, op, val2 = clause[1], clause[2], clause[3]
            for num in interp['candidate_nums']:
                if op == '>' and num > val2:
                    return True
                if op == '<' and num < val2:
                    return True
                if op == '>=' and num >= val2:
                    return True
                if op == '<=' and num <= val2:
                    return True
                if op == '=' and abs(num - val2) < 0.01:
                    return True
            return False
        
        if c_type == 'negation':
            keyword = clause[1]
            return keyword not in candidate.lower()
        
        if c_type == 'conditional' or c_type == 'causal':
            # Simple substring match
            return clause[2] in candidate.lower()
        
        return True
    
    def _compute_susceptibility(self, clauses: List[Tuple], interp: Dict, prompt: str, candidate: str) -> float:
        rewards = []
        
        for _ in range(self.k_perturb):
            perturbed = interp.copy()
            
            # Perturb numeric results
            if perturbed['numeric_result'] is not None:
                perturbed['numeric_result'] += np.random.normal(0, self.sigma_perturb)
            
            if perturbed['bayesian_result'] is not None:
                perturbed['bayesian_result'] += np.random.normal(0, self.sigma_perturb)
            
            # Flip boolean
            if np.random.random() < 0.3:
                perturbed['is_yes'] = not perturbed['is_yes']
            
            r = self._compute_reward(clauses, perturbed, prompt, candidate)
            rewards.append(r)
        
        return np.var(rewards) if rewards else 0.0
    
    def _pragmatic_penalty(self, prompt: str, candidate: str) -> float:
        penalty = 0.0
        
        # Scalar implicature: "some" -> "not all"
        if 'some' in prompt.lower() and 'all' in candidate.lower():
            penalty += self.p_prag
        
        # Presupposition violation
        if re.search(r'\b(have you stopped|have you quit)\b', prompt.lower()):
            if 'yes' in candidate.lower() or 'no' in candidate.lower():
                penalty += self.p_prag
        
        return penalty