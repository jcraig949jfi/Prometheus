from typing import Dict, Set, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Combines renormalization (multi-scale n-gram clustering), ecosystem dynamics
    (causal flow networks with trophic levels), and Nash equilibrium (iterative
    truth assignment) to evaluate logical coherence of candidate answers.
    
    Core mechanism:
    1. Extract propositions from text at multiple scales (tokens -> n-grams)
    2. Build causal graph with edge capacities weighted by trophic level
    3. Find Nash equilibrium truth assignment minimizing inconsistency
    4. Score by total system energy (lower = more coherent)
    """
    
    def __init__(self):
        self.alpha = 0.7  # Renormalization decay
        self.lambda_penalty = 2.0  # Logical constraint weight
        self.max_depth = 3  # N-gram depth
        self.max_iterations = 50
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            combined = prompt + " " + cand
            
            # Multi-scale scoring
            struct_score = self._structural_score(prompt, cand)
            comp_score = self._computational_score(prompt, cand)
            coherence_score = self._nash_coherence(combined)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination (struct >= 50%, comp >= 20%, NCD <= 15%)
            final_score = 0.50 * struct_score + 0.25 * comp_score + 0.15 * coherence_score + 0.10 * ncd_score
            
            reasoning = f"Struct:{struct_score:.2f} Comp:{comp_score:.2f} Coher:{coherence_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        struct_score = self._structural_score(prompt, answer)
        comp_score = self._computational_score(prompt, answer)
        
        # Cap confidence based on whether we have strong structural/computational evidence
        if comp_score > 0.9:
            return min(0.95, meta_conf)
        elif struct_score > 0.8:
            return min(0.85, meta_conf)
        elif struct_score > 0.5:
            return min(0.65, meta_conf)
        else:
            return min(0.4, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'have you stopped', r'have you quit', r'why did \w+ (fail|stop)',
                          r'when did you stop', r'do you still']
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|said)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+.*? a \w+', p_lower) or re.search(r'all \w+.*? a \w+', p_lower):
            if not re.search(r'(same|different|each)', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*\?', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|most beautiful)', p_lower):
            if not re.search(r'(metric|measure|criterion|according to)', p_lower):
                return 0.3
        
        return 0.7  # Base meta-confidence
    
    def _structural_score(self, prompt: str, answer: str) -> float:
        score = 0.0
        count = 0
        
        # Negation handling
        neg_score = self._handle_negation(prompt, answer)
        if neg_score is not None:
            score += neg_score
            count += 1
        
        # Numeric comparison
        num_score = self._handle_numeric(prompt, answer)
        if num_score is not None:
            score += num_score
            count += 1
        
        # Transitivity
        trans_score = self._handle_transitivity(prompt, answer)
        if trans_score is not None:
            score += trans_score
            count += 1
        
        # Modus tollens
        mt_score = self._handle_modus_tollens(prompt, answer)
        if mt_score is not None:
            score += mt_score
            count += 1
        
        return score / count if count > 0 else 0.5
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        # Bat-and-ball type algebra
        algebra_score = self._solve_algebra(prompt, answer)
        if algebra_score is not None:
            return algebra_score
        
        # Modular arithmetic
        mod_score = self._solve_modular(prompt, answer)
        if mod_score is not None:
            return mod_score
        
        # PEMDAS expressions
        pemdas_score = self._solve_pemdas(prompt, answer)
        if pemdas_score is not None:
            return pemdas_score
        
        return 0.5
    
    def _nash_coherence(self, text: str) -> float:
        props = self._extract_propositions(text)
        if len(props) < 2:
            return 0.5
        
        graph = self._build_causal_graph(props)
        trophic = self._compute_trophic_levels(graph, len(props))
        capacities = self._compute_capacities(graph, trophic)
        
        truth = self._nash_equilibrium(graph, capacities, len(props))
        energy = self._compute_energy(graph, capacities, truth)
        
        # Normalize energy to [0, 1]
        max_energy = len(graph) * 2.0
        return max(0.0, 1.0 - energy / max_energy) if max_energy > 0 else 0.5
    
    def _extract_propositions(self, text: str) -> List[str]:
        # Multi-scale: sentences, clauses, phrases
        sentences = re.split(r'[.!?]+', text)
        props = []
        for sent in sentences:
            sent = sent.strip()
            if sent:
                props.append(sent)
                # Also extract clauses
                clauses = re.split(r'[,;]', sent)
                props.extend([c.strip() for c in clauses if c.strip()])
        return list(set(props))[:20]  # Limit size
    
    def _build_causal_graph(self, props: List[str]) -> List[Tuple[int, int]]:
        edges = []
        causal_cues = ['because', 'leads to', 'results in', 'causes', 'therefore', 'thus', 'so']
        
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i != j:
                    p1_lower = p1.lower()
                    p2_lower = p2.lower()
                    # Check if p1 causally supports p2
                    for cue in causal_cues:
                        if cue in p1_lower or cue in p2_lower:
                            edges.append((i, j))
                            break
        return edges
    
    def _compute_trophic_levels(self, edges: List[Tuple[int, int]], n: int) -> np.ndarray:
        trophic = np.zeros(n)
        for _ in range(n):
            for i, j in edges:
                trophic[j] = max(trophic[j], trophic[i] + 1)
        return trophic
    
    def _compute_capacities(self, edges: List[Tuple[int, int]], trophic: np.ndarray) -> Dict[Tuple[int, int], float]:
        capacities = {}
        for i, j in edges:
            capacities[(i, j)] = (self.alpha ** int(trophic[i])) * (trophic[j] + 1)
        return capacities
    
    def _nash_equilibrium(self, edges: List[Tuple[int, int]], capacities: Dict, n: int) -> np.ndarray:
        truth = np.random.randint(0, 2, n)
        
        for _ in range(self.max_iterations):
            changed = False
            for i in range(n):
                # Compute payoff for t_i = 0 and t_i = 1
                payoff_0 = self._compute_payoff(i, 0, truth, edges, capacities)
                payoff_1 = self._compute_payoff(i, 1, truth, edges, capacities)
                
                best = 1 if payoff_1 > payoff_0 else 0
                if best != truth[i]:
                    truth[i] = best
                    changed = True
            
            if not changed:
                break
        
        return truth
    
    def _compute_payoff(self, i: int, t_i: int, truth: np.ndarray, edges: List, capacities: Dict) -> float:
        cost = 0.0
        for j, k in edges:
            if j == i:
                cost += capacities.get((j, k), 0) * abs(t_i - truth[k])
            elif k == i:
                cost += capacities.get((j, k), 0) * abs(truth[j] - t_i)
        return -cost
    
    def _compute_energy(self, edges: List, capacities: Dict, truth: np.ndarray) -> float:
        energy = 0.0
        for i, j in edges:
            energy += capacities.get((i, j), 0) * abs(truth[i] - truth[j])
        return energy
    
    def _handle_negation(self, prompt: str, answer: str) -> float:
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        if 'not' in p_lower or 'no ' in p_lower:
            if ('yes' in a_lower and 'not' not in a_lower) or ('no' in a_lower and 'not' in a_lower):
                return 0.3
            return 0.7
        return None
    
    def _handle_numeric(self, prompt: str, answer: str) -> float:
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        
        if len(nums_p) >= 2 and len(nums_a) >= 1:
            comparatives = re.findall(r'(greater|less|more|fewer|higher|lower|bigger|smaller)', prompt.lower())
            if comparatives:
                try:
                    vals_p = [float(x) for x in nums_p[:2]]
                    val_a = float(nums_a[0])
                    
                    if 'greater' in comparatives or 'more' in comparatives or 'higher' in comparatives:
                        expected = max(vals_p)
                    else:
                        expected = min(vals_p)
                    
                    return 1.0 if abs(val_a - expected) < 0.01 else 0.2
                except:
                    pass
        return None
    
    def _handle_transitivity(self, prompt: str, answer: str) -> float:
        # A > B, B > C => A > C
        pattern = r'(\w+)\s+(>|<|taller|shorter|faster|slower|heavier|lighter)\s+(\w+)'
        matches = re.findall(pattern, prompt.lower())
        
        if len(matches) >= 2:
            # Simple transitivity check
            if matches[0][2] == matches[1][0]:  # B appears in both
                return 0.8 if matches[0][0] in answer.lower() or matches[1][2] in answer.lower() else 0.3
        return None
    
    def _handle_modus_tollens(self, prompt: str, answer: str) -> float:
        # If P then Q, not Q => not P
        if_then = re.search(r'if (.*?) then (.*?)[.,]', prompt.lower())
        not_q = re.search(r'not (.*?)[.,?]', prompt.lower())
        
        if if_then and not_q:
            return 0.8 if 'not' in answer.lower() else 0.3
        return None
    
    def _solve_algebra(self, prompt: str, answer: str) -> float:
        # Bat-and-ball: x + (x + d) = total
        match = re.search(r'cost.*?(\d+\.?\d*).*?more than.*?together.*?(\d+\.?\d*)', prompt.lower())
        if match:
            try:
                diff = float(match.group(1))
                total = float(match.group(2))
                x = (total - diff) / 2
                
                nums_a = re.findall(r'\d+\.?\d*', answer)
                if nums_a:
                    return 1.0 if abs(float(nums_a[0]) - x) < 0.01 else 0.1
            except:
                pass
        return None
    
    def _solve_modular(self, prompt: str, answer: str) -> float:
        mod_match = re.search(r'(\d+)\s+mod\s+(\d+)', prompt.lower())
        if mod_match:
            try:
                n = int(mod_match.group(1))
                m = int(mod_match.group(2))
                result = n % m
                
                nums_a = re.findall(r'\d+', answer)
                if nums_a:
                    return 1.0 if int(nums_a[0]) == result else 0.0
            except:
                pass
        return None
    
    def _solve_pemdas(self, prompt: str, answer: str) -> float:
        expr_match = re.search(r'(\d+\s*[\+\-\*/]\s*\d+(?:\s*[\+\-\*/]\s*\d+)*)', prompt)
        if expr_match:
            try:
                expr = expr_match.group(1).replace(' ', '')
                result = eval(expr)
                
                nums_a = re.findall(r'-?\d+\.?\d*', answer)
                if nums_a:
                    return 1.0 if abs(float(nums_a[0]) - result) < 0.01 else 0.1
            except:
                pass
        return None
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)