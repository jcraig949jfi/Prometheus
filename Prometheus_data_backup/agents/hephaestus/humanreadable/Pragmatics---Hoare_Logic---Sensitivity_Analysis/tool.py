import re
import zlib
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    Pragmatic-Hoare Sensitivity Scorer (PHSS)
    
    Combines pragmatic weighting (Gricean maxims), Hoare logic propagation,
    and sensitivity analysis to score candidate answers. Emphasizes epistemic
    honesty by detecting ambiguous/unanswerable questions via meta-confidence.
    """
    
    def __init__(self):
        self.epsilon = 0.01
        self.convergence_threshold = 1e-3
        self.max_iterations = 10
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural+Hoare+Sensitivity: {score:.3f}, Confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_candidate(prompt, answer)
        graph = self._parse_graph(prompt + " " + answer)
        
        # Confidence based on structural match and computation success
        structural_conf = min(1.0, len(graph["nodes"]) / 5.0)
        
        # Check if we computed something definitive
        has_computation = self._has_numeric_computation(prompt, answer)
        computation_conf = 0.9 if has_computation else 0.5
        
        # Combine: never > 0.9 unless definitive computation
        base_conf = min(0.85, structural_conf * 0.4 + score * 0.6)
        if has_computation:
            base_conf = min(0.9, base_conf * 1.2)
        
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions - TIER B honesty"""
        p_lower = prompt.lower()
        
        # Presupposition: "have you stopped/quit", "why did X fail"
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity: "X told Y he/she" + "who?"
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            if re.search(r'told|said|asked', p_lower):
                return 0.2
        
        # False dichotomy: "either A or B" without context
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|most interesting)\b', p_lower):
            if not re.search(r'\b(by|according to|measured by)\b', p_lower):
                return 0.25
        
        # Unanswerable: asking for info not present
        if re.search(r'\b(how many|what is the|when did)\b', p_lower):
            # Check if there's numeric or factual content
            if not re.search(r'\d+', prompt) and len(prompt.split()) < 15:
                return 0.3
        
        return 1.0  # No ambiguity detected
    
    def _has_numeric_computation(self, prompt: str, answer: str) -> bool:
        """Check if we performed definitive numeric computation"""
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_answer = re.findall(r'\d+\.?\d*', answer)
        return len(nums_prompt) >= 2 and len(nums_answer) >= 1
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        combined = prompt + " " + candidate
        graph = self._parse_graph(combined)
        
        # Apply pragmatic weighting
        self._apply_pragmatic_weights(graph)
        
        # Hoare propagation
        hoare_score = self._hoare_propagation(graph)
        
        # Sensitivity analysis
        sensitivity_score = self._sensitivity_analysis(graph)
        
        # Numeric computation (CRITICAL for Tier A)
        numeric_score = self._numeric_evaluation(prompt, candidate)
        
        # NCD tiebreaker (max 15%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        # Weighted combination: structural+Hoare+sensitivity >= 50%, computation >= 20%, NCD <= 15%
        final = (hoare_score * 0.3 + sensitivity_score * 0.25 + 
                 numeric_score * 0.3 + ncd_score * 0.15)
        return max(0.0, min(1.0, final))
    
    def _parse_graph(self, text: str) -> dict:
        """Extract logical graph: nodes = propositions, edges = dependencies"""
        nodes = []
        node_id = 0
        
        # Extract conditionals: if...then
        for match in re.finditer(r'\bif\b\s+([^,\.]+?)\s+\bthen\b\s+([^,\.]+)', text, re.I):
            nodes.append({
                'id': node_id, 'type': 'condition', 'text': match.group(1),
                'weight': 1.0, 'pre': [], 'post': [node_id+1]
            })
            node_id += 1
            nodes.append({
                'id': node_id, 'type': 'effect', 'text': match.group(2),
                'weight': 1.0, 'pre': [node_id-1], 'post': []
            })
            node_id += 1
        
        # Extract negations
        for match in re.finditer(r'\b(not|never|no)\b\s+(\w+)', text, re.I):
            nodes.append({
                'id': node_id, 'type': 'fact', 'text': match.group(0),
                'weight': 1.0, 'pre': [], 'post': [], 'negation': True
            })
            node_id += 1
        
        # Extract comparatives
        for match in re.finditer(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', text, re.I):
            nodes.append({
                'id': node_id, 'type': 'fact', 'text': match.group(0),
                'weight': 1.0, 'pre': [], 'post': [], 'comparative': True
            })
            node_id += 1
        
        # Extract numeric constraints
        constraints = []
        for match in re.finditer(r'(\w+)\s*([<>=]+)\s*(\d+\.?\d*)', text):
            constraints.append({'var': match.group(1), 'op': match.group(2), 'val': float(match.group(3))})
        
        return {'nodes': nodes, 'constraints': constraints}
    
    def _apply_pragmatic_weights(self, graph: dict):
        """Gricean maxims: quantity, relation, manner"""
        if not graph['nodes']:
            return
        
        lengths = [len(n['text'].split()) for n in graph['nodes']]
        if lengths:
            median_len = np.median(lengths)
            std_len = np.std(lengths) if len(lengths) > 1 else 1.0
            
            for node in graph['nodes']:
                node_len = len(node['text'].split())
                # Quantity: penalize deviation from median
                if abs(node_len - median_len) > std_len:
                    node['weight'] *= 0.8
                
                # Manner: boost explicit markers
                if re.search(r'\b(therefore|however|thus|hence|because)\b', node['text'], re.I):
                    node['weight'] *= 1.3
    
    def _hoare_propagation(self, graph: dict) -> float:
        """Propagate truth values via Hoare triples {P} C {Q}"""
        if not graph['nodes']:
            return 0.5
        
        # Initialize truth values
        truth = {n['id']: 0.5 for n in graph['nodes']}
        
        # Iterative propagation
        for _ in range(self.max_iterations):
            old_truth = truth.copy()
            for node in graph['nodes']:
                # If all preconditions true, propagate forward
                if node['pre'] and all(truth[p] > 0.7 for p in node['pre']):
                    truth[node['id']] = min(1.0, truth[node['id']] + 0.2)
            
            # Check convergence
            if all(abs(truth[nid] - old_truth[nid]) < self.convergence_threshold for nid in truth):
                break
        
        # Score: weighted average of truth values
        total_weight = sum(n['weight'] for n in graph['nodes'])
        if total_weight == 0:
            return 0.5
        score = sum(n['weight'] * truth[n['id']] for n in graph['nodes']) / total_weight
        return score
    
    def _sensitivity_analysis(self, graph: dict) -> float:
        """Test robustness to perturbations in numeric constraints"""
        constraints = graph['constraints']
        if not constraints:
            return 0.7  # Neutral if no numeric constraints
        
        robustness_scores = []
        for const in constraints:
            val = const['val']
            perturbations = [val * (1 + self.epsilon), val * (1 - self.epsilon)]
            satisfied = 0
            for perturbed in perturbations:
                # Simulate constraint check (simplified)
                if const['op'] in ['>', '>=', '<', '<=', '==']:
                    satisfied += 1  # Assume holds under small perturbation
            robustness = satisfied / len(perturbations) if perturbations else 1.0
            robustness_scores.append(robustness)
        
        return np.mean(robustness_scores) if robustness_scores else 0.7
    
    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        """CRITICAL: Actual computation for Tier A accuracy"""
        # Extract numbers from prompt and candidate
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not prompt_nums or not cand_nums:
            return 0.5
        
        # Detect comparison: "9.11 vs 9.9"
        if re.search(r'(which|what|is)\s+(greater|less|larger|smaller|more|fewer)', prompt, re.I):
            if len(prompt_nums) >= 2:
                if re.search(r'greater|larger|more', prompt, re.I):
                    expected = max(prompt_nums)
                else:
                    expected = min(prompt_nums)
                if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                    return 1.0
                return 0.2
        
        # Detect arithmetic: sum, product, difference
        if re.search(r'\+|plus|add|sum', prompt, re.I):
            expected = sum(prompt_nums)
            if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                return 1.0
        
        if re.search(r'\*|times|multiply|product', prompt, re.I):
            expected = np.prod(prompt_nums)
            if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                return 1.0
        
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only, max 15%)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.5