import re
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    Differentiable Belief-Constraint Network (DBCN).
    
    Combines:
    - Differentiable Programming: gradient descent on belief vectors
    - Theory of Mind: separate belief vectors per agent + recursive modeling
    - Emergence: global consistency loss from local constraint interactions
    
    Parses propositions, builds constraint graph, optimizes belief coherence.
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._compute_coherence(prompt, cand)
            reasoning = f"Belief coherence: {score:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        coherence = self._compute_coherence(prompt, answer)
        # Cap by meta-confidence (epistemic honesty)
        return min(meta_conf, self._sigmoid(coherence - 0.5))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|when did.*stop|why did.*fail)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.35
        
        # Insufficient information
        if re.search(r'\b(not enough|cannot determine|insufficient|ambiguous)\b', p):
            return 0.25
        
        return 0.85  # Default: answerable
    
    def _compute_coherence(self, prompt: str, answer: str) -> float:
        """Main DBCN pipeline."""
        text = prompt + " " + answer
        
        # 1. Parse propositions and agents
        props, prop_map = self._extract_propositions(text)
        agents = self._extract_agents(text)
        
        # 2. Extract constraints
        constraints = self._extract_constraints(text, prop_map)
        
        # 3. Initialize belief vectors
        n_props = len(props)
        if n_props == 0:
            return self._ncd_fallback(prompt, answer)
        
        beliefs = {agent: np.random.uniform(0.3, 0.7, n_props) for agent in agents}
        beliefs['_global'] = np.random.uniform(0.3, 0.7, n_props)
        
        # 4. Optimize via gradient descent
        loss = self._optimize_beliefs(beliefs, constraints, agents, prop_map, text)
        
        # 5. Score = -loss (lower loss = higher coherence)
        score = np.exp(-loss)
        
        # 6. Add numeric/structural bonuses
        score += self._numeric_bonus(text, answer)
        score += self._structural_bonus(text, answer)
        
        return float(score)
    
    def _extract_propositions(self, text):
        """Extract atomic propositions."""
        props = []
        prop_map = {}
        
        # Negations
        for match in re.finditer(r'\bnot\s+(\w+)', text, re.IGNORECASE):
            prop = f"not_{match.group(1)}"
            if prop not in prop_map:
                prop_map[prop] = len(props)
                props.append(prop)
        
        # Simple entities/predicates
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        for w in words:
            if w not in prop_map:
                prop_map[w] = len(props)
                props.append(w)
        
        # Ensure at least one prop
        if not props:
            prop_map['_default'] = 0
            props.append('_default')
        
        return props, prop_map
    
    def _extract_agents(self, text):
        """Extract mentioned agents."""
        agents = set()
        # Common names
        for name in re.findall(r'\b([A-Z][a-z]+)\b', text):
            if len(name) > 2:
                agents.add(name)
        return list(agents) if agents else ['_global']
    
    def _extract_constraints(self, text, prop_map):
        """Extract logical/ordering/ToM constraints."""
        constraints = []
        
        # Comparatives: A > B, A < B
        for match in re.finditer(r'(\w+)\s*([><])\s*(\w+)', text):
            a, op, b = match.groups()
            if a in prop_map and b in prop_map:
                constraints.append({
                    'type': 'order',
                    'i': prop_map[a],
                    'j': prop_map[b],
                    'op': op
                })
        
        # Conditionals: if A then B
        for match in re.finditer(r'\bif\s+(\w+)\s+then\s+(\w+)', text, re.IGNORECASE):
            a, b = match.groups()
            if a in prop_map and b in prop_map:
                constraints.append({
                    'type': 'implies',
                    'i': prop_map[a],
                    'j': prop_map[b]
                })
        
        # Equality: A equals B, A is B
        for match in re.finditer(r'(\w+)\s+(equals?|is)\s+(\w+)', text, re.IGNORECASE):
            a, _, b = match.groups()
            if a in prop_map and b in prop_map:
                constraints.append({
                    'type': 'equal',
                    'i': prop_map[a],
                    'j': prop_map[b]
                })
        
        return constraints
    
    def _optimize_beliefs(self, beliefs, constraints, agents, prop_map, text):
        """Gradient descent on belief vectors."""
        lr = 0.1
        n_steps = 10
        
        for _ in range(n_steps):
            loss, grads = self._compute_loss_and_grad(beliefs, constraints, agents)
            
            # Update beliefs
            for agent in beliefs:
                beliefs[agent] -= lr * grads[agent]
                beliefs[agent] = np.clip(beliefs[agent], 0.01, 0.99)
        
        final_loss, _ = self._compute_loss_and_grad(beliefs, constraints, agents)
        return final_loss
    
    def _compute_loss_and_grad(self, beliefs, constraints, agents):
        """Compute differentiable loss and gradients."""
        total_loss = 0.0
        grads = {agent: np.zeros_like(beliefs[agent]) for agent in beliefs}
        
        # Constraint loss
        for c in constraints:
            for agent in beliefs:
                b = beliefs[agent]
                
                if c['type'] == 'order':
                    i, j, op = c['i'], c['j'], c['op']
                    if op == '<':
                        # b[i] should be < b[j]
                        violation = max(0, b[i] - b[j] + 0.1)
                        total_loss += violation ** 2
                        if violation > 0:
                            grads[agent][i] += 2 * violation
                            grads[agent][j] -= 2 * violation
                    else:
                        violation = max(0, b[j] - b[i] + 0.1)
                        total_loss += violation ** 2
                        if violation > 0:
                            grads[agent][j] += 2 * violation
                            grads[agent][i] -= 2 * violation
                
                elif c['type'] == 'implies':
                    # b[i] <= b[j] (if i then j)
                    i, j = c['i'], c['j']
                    violation = max(0, b[i] - b[j])
                    total_loss += violation ** 2
                    if violation > 0:
                        grads[agent][i] += 2 * violation
                        grads[agent][j] -= 2 * violation
                
                elif c['type'] == 'equal':
                    i, j = c['i'], c['j']
                    diff = b[i] - b[j]
                    total_loss += diff ** 2
                    grads[agent][i] += 2 * diff
                    grads[agent][j] -= 2 * diff
        
        # ToM loss: agent beliefs should align with global
        if len(agents) > 0 and '_global' in beliefs:
            for agent in agents:
                if agent != '_global' and agent in beliefs:
                    diff = beliefs[agent] - beliefs['_global']
                    kl_loss = np.sum(diff ** 2)
                    total_loss += 0.1 * kl_loss
                    grads[agent] += 0.2 * diff
                    grads['_global'] -= 0.2 * diff
        
        return total_loss, grads
    
    def _numeric_bonus(self, text, answer):
        """Reward correct numeric comparisons."""
        bonus = 0.0
        
        # Extract numbers
        nums_text = re.findall(r'\b\d+\.?\d*\b', text)
        nums_ans = re.findall(r'\b\d+\.?\d*\b', answer)
        
        if len(nums_text) >= 2:
            try:
                a, b = float(nums_text[0]), float(nums_text[1])
                if '<' in text or 'less' in text.lower():
                    if 'yes' in answer.lower() and a < b:
                        bonus += 0.3
                    elif 'no' in answer.lower() and a >= b:
                        bonus += 0.3
                elif '>' in text or 'greater' in text.lower():
                    if 'yes' in answer.lower() and a > b:
                        bonus += 0.3
                    elif 'no' in answer.lower() and a <= b:
                        bonus += 0.3
            except:
                pass
        
        return bonus
    
    def _structural_bonus(self, text, answer):
        """Reward structural alignment."""
        bonus = 0.0
        
        # Negation handling
        if re.search(r'\bnot\b', text, re.IGNORECASE):
            if re.search(r'\b(no|false|incorrect)\b', answer, re.IGNORECASE):
                bonus += 0.1
        
        # Conditional handling
        if re.search(r'\bif\b.*\bthen\b', text, re.IGNORECASE):
            if re.search(r'\b(yes|true|correct)\b', answer, re.IGNORECASE):
                bonus += 0.1
        
        return bonus
    
    def _ncd_fallback(self, prompt, answer):
        """Normalized Compression Distance as fallback."""
        import zlib
        c_p = len(zlib.compress(prompt.encode()))
        c_a = len(zlib.compress(answer.encode()))
        c_pa = len(zlib.compress((prompt + answer).encode()))
        ncd = (c_pa - min(c_p, c_a)) / max(c_p, c_a)
        return 1.0 - ncd
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))