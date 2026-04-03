import re
import numpy as np
import zlib
from collections import defaultdict

class ReasoningTool:
    """
    Free-energy based reasoning tool combining thermodynamics, causal inference, 
    and variational inference. Parses prompts/answers into factor graphs, runs 
    belief propagation, and scores by variational free energy.
    
    Lower free energy = more consistent with logical/causal constraints.
    """
    
    def __init__(self):
        self.epsilon = 1e-8
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_answer(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free energy: {-score:.3f}, Confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we can compute a definitive answer
        comp_result = self._try_computational(prompt, answer)
        if comp_result is not None:
            return min(0.95, comp_result)
        
        # Base confidence on parsing success
        nodes, edges = self._parse_graph(prompt + " " + answer)
        if len(nodes) < 2:
            return 0.25
        
        return min(0.7, 0.4 + 0.3 * min(len(edges) / max(len(nodes), 1), 1))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'have you (stopped|quit|ceased)', r'why did .+ (fail|stop|end)',
                          r'when did you last', r'do you still']
        if any(re.search(pat, p_lower) for pat in presup_patterns):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every \w+.*\ba\b', p_lower) or re.search(r'all \w+.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity in questions
        if re.search(r'(he|she|it|they).*who', p_lower) or re.search(r'who.*(he|she|it)', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+[?.!]', p_lower) and 'only' not in p_lower:
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|greatest)\b', p_lower):
            if not re.search(r'(by|according to|measured|criteria)', p_lower):
                return 0.25
        
        # Unanswerable - asking for info not provided
        if re.search(r'(how many|what is|when did)', p_lower):
            if len(re.findall(r'\d+', prompt)) == 0 and 'not enough' not in p_lower:
                if len(prompt.split()) < 20:
                    return 0.3
        
        return 1.0
    
    def _score_answer(self, prompt: str, answer: str) -> float:
        # Try computational methods first
        comp_score = self._try_computational(prompt, answer)
        if comp_score is not None:
            return comp_score * 100
        
        # Build factor graph
        nodes, edges = self._parse_graph(prompt + " ANSWER: " + answer)
        if len(nodes) < 2:
            return self._ncd_score(prompt, answer) * 15
        
        # Run belief propagation
        marginals = self._belief_propagation(nodes, edges)
        
        # Compute free energy
        free_energy = self._compute_free_energy(nodes, edges, marginals)
        
        # Combine: lower free energy is better
        structure_score = 50 * np.exp(-free_energy / len(nodes))
        ncd_score = self._ncd_score(prompt, answer) * 15
        
        return structure_score + ncd_score
    
    def _try_computational(self, prompt: str, answer: str) -> float:
        # Numeric comparison
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_a = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if len(nums_p) >= 2 and len(nums_a) >= 1:
            if any(w in prompt.lower() for w in ['greater', 'larger', 'bigger', 'more']):
                expected = max(nums_p)
                if abs(nums_a[0] - expected) < 0.01:
                    return 0.95
            elif any(w in prompt.lower() for w in ['smaller', 'less', 'fewer']):
                expected = min(nums_p)
                if abs(nums_a[0] - expected) < 0.01:
                    return 0.95
        
        # Bat and ball algebra: X + Y = A, X = Y + B
        if 'together' in prompt.lower() or 'total' in prompt.lower():
            if len(nums_p) >= 2 and len(nums_a) >= 1:
                total = nums_p[0]
                diff = nums_p[1] if len(nums_p) > 1 else 0
                expected = (total - diff) / 2
                if abs(nums_a[0] - expected) < 0.01:
                    return 0.92
        
        # Modular arithmetic
        if 'remainder' in prompt.lower() or 'divisible' in prompt.lower():
            if len(nums_p) >= 2 and len(nums_a) >= 1:
                result = int(nums_p[0]) % int(nums_p[1])
                if abs(nums_a[0] - result) < 0.01:
                    return 0.90
        
        return None
    
    def _parse_graph(self, text: str):
        sentences = re.split(r'[.!?]', text)
        nodes = {}
        edges = []
        node_id = 0
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
            
            # Extract propositions
            props = self._extract_propositions(sent)
            for prop in props:
                nodes[node_id] = prop
                node_id += 1
        
        # Build edges from constraints
        node_list = list(nodes.items())
        for i, (id_i, prop_i) in enumerate(node_list):
            for j, (id_j, prop_j) in enumerate(node_list[i+1:], start=i+1):
                edge_type = self._infer_edge_type(prop_i, prop_j)
                if edge_type:
                    edges.append((id_i, id_j, edge_type))
        
        return nodes, edges
    
    def _extract_propositions(self, sent: str):
        props = []
        
        # Negations
        if re.search(r'\b(not|no|never|neither)\b', sent.lower()):
            props.append(('negation', sent))
        
        # Comparatives
        if re.search(r'\b(greater|less|more|fewer|larger|smaller)\b', sent.lower()):
            props.append(('comparative', sent))
        
        # Causals
        if re.search(r'\b(cause|lead|result|produce|trigger|enable)\b', sent.lower()):
            props.append(('causal', sent))
        
        # Conditionals
        if re.search(r'\bif\b.*\bthen\b', sent.lower()):
            props.append(('conditional', sent))
        
        # Numeric facts
        if re.search(r'\d+', sent):
            props.append(('numeric', sent))
        
        # Default proposition
        if not props:
            props.append(('statement', sent))
        
        return props
    
    def _infer_edge_type(self, prop1, prop2):
        type1, text1 = prop1
        type2, text2 = prop2
        
        if type1 == 'causal' or type2 == 'causal':
            return 'causal'
        if type1 == 'comparative' and type2 == 'comparative':
            return 'comparative'
        if type1 == 'negation' or type2 == 'negation':
            return 'negation'
        
        return None
    
    def _belief_propagation(self, nodes, edges, iterations=5):
        n = len(nodes)
        if n == 0:
            return {}
        
        # Initialize messages
        messages = defaultdict(lambda: np.array([0.5, 0.5]))
        
        for _ in range(iterations):
            new_messages = {}
            for src, tgt, etype in edges:
                msg = self._compute_message(src, tgt, etype, messages, edges)
                new_messages[(src, tgt)] = msg
                
                # Reverse message
                msg_rev = self._compute_message(tgt, src, etype, messages, edges)
                new_messages[(tgt, src)] = msg_rev
            
            messages.update(new_messages)
        
        # Compute marginals
        marginals = {}
        for node_id in nodes:
            incoming = [messages.get((other, node_id), np.array([0.5, 0.5])) 
                       for other, _, _ in edges if other != node_id] + \
                      [messages.get((other, node_id), np.array([0.5, 0.5])) 
                       for _, other, _ in edges if other != node_id]
            
            if incoming:
                belief = np.prod(incoming, axis=0)
                belief = belief / (belief.sum() + self.epsilon)
                marginals[node_id] = belief[1]
            else:
                marginals[node_id] = 0.5
        
        return marginals
    
    def _compute_message(self, src, tgt, etype, messages, all_edges):
        # Compute message from src to tgt
        psi = self._pairwise_potential(etype)
        
        # Collect incoming messages to src (excluding from tgt)
        incoming = [messages.get((other, src), np.array([0.5, 0.5])) 
                   for other, t, _ in all_edges if t == src and other != tgt]
        
        if incoming:
            belief_src = np.prod(incoming, axis=0)
        else:
            belief_src = np.array([0.5, 0.5])
        
        # Message is marginalization
        msg = np.array([
            np.sum(belief_src * psi[:, 0]),
            np.sum(belief_src * psi[:, 1])
        ])
        
        msg = msg / (msg.sum() + self.epsilon)
        return msg
    
    def _pairwise_potential(self, etype):
        if etype == 'causal':
            # Causal: prefer (1,1) and (0,0), penalize (1,0)
            return np.array([[1.0, 0.8], [0.3, 1.0]])
        elif etype == 'negation':
            # Negation: prefer (1,0) and (0,1)
            return np.array([[1.0, 0.2], [0.2, 1.0]])
        elif etype == 'comparative':
            # Comparative: asymmetric preference
            return np.array([[1.0, 0.5], [0.5, 0.8]])
        else:
            # Default: weak preference for agreement
            return np.array([[1.0, 0.7], [0.7, 1.0]])
    
    def _compute_free_energy(self, nodes, edges, marginals):
        # F = <E> - H where E is energy, H is entropy
        energy = 0.0
        
        # Unary terms
        for node_id in nodes:
            mu = marginals.get(node_id, 0.5)
            energy += mu * 0.5  # Small unary cost
        
        # Pairwise terms
        for src, tgt, etype in edges:
            mu_src = marginals.get(src, 0.5)
            mu_tgt = marginals.get(tgt, 0.5)
            psi = self._pairwise_potential(etype)
            
            # Approximate energy using marginals
            energy += mu_src * mu_tgt * (1 - psi[1, 1]) + \
                     (1 - mu_src) * (1 - mu_tgt) * (1 - psi[0, 0])
        
        # Entropy
        entropy = 0.0
        for node_id in nodes:
            mu = marginals.get(node_id, 0.5)
            mu = np.clip(mu, self.epsilon, 1 - self.epsilon)
            entropy -= mu * np.log(mu) + (1 - mu) * np.log(1 - mu)
        
        return energy - entropy
    
    def _ncd_score(self, prompt: str, answer: str):
        c_p = len(zlib.compress(prompt.encode()))
        c_a = len(zlib.compress(answer.encode()))
        c_pa = len(zlib.compress((prompt + answer).encode()))
        ncd = (c_pa - min(c_p, c_a)) / max(c_p, c_a, 1)
        return 1 - ncd