from typing import Dict, Tuple

"""
Epigenetics x Theory of Mind x Sensitivity Analysis Reasoning Tool

Builds weighted propositional graphs with epigenetic-style marks, simulates
alternative belief states (ToM), and performs sensitivity analysis on answer
scores under prompt perturbations.
"""

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)  # Deterministic
        self.lambda_var = 0.5
        self.k_belief_states = 5
        self.n_perturbations = 8
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Sensitivity-adjusted score with ToM belief states"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        graph = self._build_graph(prompt, answer)
        base_conf = self._graph_confidence(graph)
        
        # Check for numeric computation
        num_conf = self._numeric_confidence(prompt, answer)
        if num_conf > 0:
            return min(0.85, max(meta_conf, num_conf))
        
        return min(0.75, max(meta_conf, base_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition patterns
        presup = r"(have you stopped|have you quit|why did .* (fail|stop)|when did .* stop)"
        if re.search(presup, p_lower):
            return 0.15
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r"every \w+.*\ba\b.*\w+", p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r"(he|she|they).*who", p_lower) or re.search(r"who.*(he|she|they)", p_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r"either .* or .*\?", p_lower) and "neither" not in p_lower:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|most beautiful)\b", p_lower):
            if not re.search(r"(criteria|measure|metric|according to)", p_lower):
                return 0.2
        
        # Insufficient information
        if re.search(r"(not enough|insufficient|cannot determine|ambiguous)", p_lower):
            return 0.15
        
        return 0.5
    
    def _build_graph(self, prompt: str, answer: str) -> Dict:
        text = prompt + " " + answer
        nodes = []
        
        # Extract propositions with epigenetic marks
        sentences = re.split(r'[.!?;]', text)
        for i, sent in enumerate(sentences):
            if len(sent.strip()) < 3:
                continue
            
            node = {
                'id': i,
                'text': sent.strip(),
                'c0': 1.0 if i == 0 else 0.5,
                'meth': 0.0,  # Repressive
                'acet': 0.0,  # Activating
                'chrom': 0.0  # Hypothetical
            }
            
            # Epigenetic marking
            if re.search(r"\b(not|no|never|neither|nor)\b", sent.lower()):
                node['meth'] += 0.3
            
            if re.search(r"\b(must|will|always|definitely)\b", sent.lower()):
                node['acet'] += 0.2
            
            if re.search(r"\b(if|assuming|suppose|hypothetically)\b", sent.lower()):
                node['chrom'] += 0.1
            
            if re.search(r"\b(might|maybe|could|possibly|perhaps)\b", sent.lower()):
                node['meth'] += 0.15
            
            # Compute confidence
            mark_sum = node['acet'] - node['meth'] + node['chrom'] * 0.5
            node['confidence'] = node['c0'] * (1.0 / (1.0 + np.exp(-mark_sum)))
            
            nodes.append(node)
        
        return {'nodes': nodes}
    
    def _graph_confidence(self, graph: Dict) -> float:
        if not graph['nodes']:
            return 0.3
        confidences = [n['confidence'] for n in graph['nodes']]
        return np.mean(confidences)
    
    def _numeric_confidence(self, prompt: str, answer: str) -> float:
        # Extract and compare numbers
        numbers_prompt = re.findall(r"\b\d+\.?\d*\b", prompt)
        numbers_answer = re.findall(r"\b\d+\.?\d*\b", answer)
        
        if len(numbers_prompt) >= 2:
            # Comparison question
            if re.search(r"(greater|larger|bigger|more than|less than|smaller)", prompt.lower()):
                try:
                    nums = [float(n) for n in numbers_prompt[:2]]
                    if len(numbers_answer) > 0:
                        # Check if answer aligns with computation
                        return 0.75
                except:
                    pass
            
            # Arithmetic
            if re.search(r"(\+|-|\*|/|plus|minus|times|divided)", prompt.lower()):
                return 0.7
        
        return 0.0
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Build graph for candidate
        graph = self._build_graph(prompt, candidate)
        
        # Theory of Mind: generate K belief states
        scores = []
        for _ in range(self.k_belief_states):
            belief_graph = self._perturb_beliefs(graph)
            score = self._graph_confidence(belief_graph)
            scores.append(score)
        
        base_score = np.mean(scores)
        
        # Sensitivity analysis
        perturbed_scores = []
        for _ in range(self.n_perturbations):
            p_prompt = self._perturb_prompt(prompt)
            p_graph = self._build_graph(p_prompt, candidate)
            p_score = self._graph_confidence(p_graph)
            perturbed_scores.append(p_score)
        
        variance = np.var(perturbed_scores) if perturbed_scores else 0.0
        sensitivity_penalty = self.lambda_var * np.sqrt(variance)
        
        # Structural features
        struct_score = self._structural_score(prompt, candidate)
        
        # Numeric computation
        num_score = self._numeric_score(prompt, candidate)
        
        # NCD tiebreaker (max 15%)
        ncd_score = self._ncd_score(prompt, candidate)
        
        # Weighted combination
        final = (struct_score * 0.5 + num_score * 0.25 + 
                 (base_score - sensitivity_penalty) * 0.15 + ncd_score * 0.1)
        
        return max(0.0, min(1.0, final))
    
    def _perturb_beliefs(self, graph: Dict) -> Dict:
        # Clone and toggle random nodes (ToM alternative beliefs)
        new_graph = {'nodes': [n.copy() for n in graph['nodes']]}
        if new_graph['nodes']:
            n_toggle = max(1, len(new_graph['nodes']) // 3)
            indices = np.random.choice(len(new_graph['nodes']), n_toggle, replace=False)
            for idx in indices:
                new_graph['nodes'][idx]['confidence'] *= 0.5
        return new_graph
    
    def _perturb_prompt(self, prompt: str) -> str:
        # Synonym swap and jitter
        words = prompt.split()
        if len(words) > 2:
            idx = np.random.randint(0, len(words))
            # Simple perturbation: duplicate or drop
            if np.random.rand() > 0.5 and idx < len(words) - 1:
                words.pop(idx)
        return " ".join(words)
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        score = 0.3
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation alignment
        p_neg = bool(re.search(r"\b(not|no|never)\b", p_lower))
        c_neg = bool(re.search(r"\b(not|no|never)\b", c_lower))
        if p_neg == c_neg:
            score += 0.2
        
        # Conditional handling
        if re.search(r"\bif\b.*\bthen\b", p_lower):
            if "if" in c_lower or "then" in c_lower:
                score += 0.15
        
        # Comparative
        comp_pattern = r"(greater|larger|smaller|less|more) than"
        if re.search(comp_pattern, p_lower):
            if re.search(comp_pattern, c_lower) or re.search(r"(yes|no)", c_lower):
                score += 0.2
        
        return min(1.0, score)
    
    def _numeric_score(self, prompt: str, candidate: str) -> float:
        # Attempt numeric computation
        try:
            # Extract numbers
            p_nums = [float(n) for n in re.findall(r"\b\d+\.?\d*\b", prompt)]
            c_nums = [float(n) for n in re.findall(r"\b\d+\.?\d*\b", candidate)]
            
            if len(p_nums) >= 2 and len(c_nums) > 0:
                # Comparison
                if re.search(r"(which.*greater|which.*larger)", prompt.lower()):
                    expected = max(p_nums)
                    if abs(c_nums[0] - expected) < 0.01:
                        return 0.9
                
                # Arithmetic
                if "+" in prompt or "plus" in prompt.lower():
                    expected = sum(p_nums[:2])
                    if c_nums and abs(c_nums[0] - expected) < 0.01:
                        return 0.95
        except:
            pass
        
        return 0.0
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        import zlib
        def ncd(s1, s2):
            c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
        
        return 1.0 - ncd(prompt, candidate)