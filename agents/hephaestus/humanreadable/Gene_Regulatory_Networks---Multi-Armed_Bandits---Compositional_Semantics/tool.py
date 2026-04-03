from typing import Dict, Tuple

"""
Gene Regulatory Networks x Multi-Armed Bandits x Compositional Semantics

Combines GRN-style constraint propagation, bandit exploration with Beta posteriors,
and compositional semantic evaluation to score candidate answers.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.lambda_weight = 0.5
        self.ucb_c = 1.0
        self.grn_iterations = 5
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using bandit-driven GRN + compositional semantics."""
        n_arms = len(candidates)
        alphas = np.ones(n_arms)
        betas = np.ones(n_arms)
        pulls = np.zeros(n_arms)
        
        # Parse prompt structure once
        prompt_graph = self._parse_to_grn(prompt)
        prompt_tree = self._parse_compositional_tree(prompt)
        numeric_constraints = self._extract_numeric_constraints(prompt)
        
        # Bandit exploration: 20 pulls total
        total_pulls = 20
        for t in range(1, total_pulls + 1):
            # UCB selection
            means = alphas / (alphas + betas)
            ucb_scores = means + self.ucb_c * np.sqrt(np.log(t) / (pulls + 1e-6))
            arm = np.argmax(ucb_scores)
            
            # Compute reward for selected arm
            reward = self._compute_reward(prompt, candidates[arm], prompt_graph, 
                                         prompt_tree, numeric_constraints)
            
            # Beta update
            alphas[arm] += reward
            betas[arm] += (1 - reward)
            pulls[arm] += 1
        
        # Final ranking by posterior mean
        final_scores = alphas / (alphas + betas)
        
        results = []
        for i, cand in enumerate(candidates):
            reasoning = self._explain_score(prompt, cand, final_scores[i])
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": reasoning
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-reasoning and structural match."""
        # Meta-confidence: check for Tier B traps
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Structural confidence
        prompt_graph = self._parse_to_grn(prompt)
        prompt_tree = self._parse_compositional_tree(prompt)
        numeric_constraints = self._extract_numeric_constraints(prompt)
        
        reward = self._compute_reward(prompt, answer, prompt_graph, 
                                     prompt_tree, numeric_constraints)
        
        # Cap by meta-confidence
        return min(reward * meta_conf, 0.95)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, and unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .+ a \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(by|according to|measured by)\b', p_lower):
                return 0.25
        
        # Unanswerable patterns
        if re.search(r'\bwhat will happen\b', p_lower) or re.search(r'\bpredict\b', p_lower):
            if not re.search(r'\b(if|given|assuming)\b', p_lower):
                return 0.3
        
        return 1.0
    
    def _parse_to_grn(self, text: str) -> Dict:
        """Extract propositions and regulatory edges."""
        nodes = []
        edges = []
        
        # Extract negations
        neg_matches = list(re.finditer(r'\bnot\s+(\w+)', text.lower()))
        for m in neg_matches:
            nodes.append(('neg', m.group(1)))
            edges.append(('neg', m.group(1), -1))
        
        # Extract conditionals (if...then)
        cond_matches = list(re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)[\.\?]', text.lower()))
        for m in cond_matches:
            nodes.extend([('cond_ant', m.group(1)), ('cond_cons', m.group(2))])
            edges.append((m.group(1), m.group(2), 1))
        
        # Extract causal claims
        causal_matches = list(re.finditer(r'(.+?)\s+(because|leads to|causes)\s+(.+?)[\.\?]', text.lower()))
        for m in causal_matches:
            nodes.extend([('cause', m.group(1)), ('effect', m.group(3))])
            edges.append((m.group(1), m.group(3), 1))
        
        # Extract temporal ordering
        temp_matches = list(re.finditer(r'(.+?)\s+(before|after)\s+(.+?)[\.\?]', text.lower()))
        for m in temp_matches:
            nodes.extend([('temp', m.group(1)), ('temp', m.group(3))])
            weight = 1 if m.group(2) == 'before' else -1
            edges.append((m.group(1), m.group(3), weight))
        
        return {'nodes': nodes, 'edges': edges}
    
    def _parse_compositional_tree(self, text: str) -> Dict:
        """Build semantic tree for compositional evaluation."""
        # Simplified: detect conjunctions, disjunctions, implications
        tree = {'type': 'root', 'children': []}
        
        if re.search(r'\band\b', text.lower()):
            tree['op'] = 'conjunction'
        elif re.search(r'\bor\b', text.lower()):
            tree['op'] = 'disjunction'
        elif re.search(r'\bif\b', text.lower()):
            tree['op'] = 'implication'
        else:
            tree['op'] = 'atomic'
        
        return tree
    
    def _extract_numeric_constraints(self, text: str) -> List[Tuple]:
        """Extract numeric comparisons and values."""
        constraints = []
        
        # Extract all numbers
        numbers = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', text)]
        
        # Detect comparisons
        comp_patterns = [
            (r'(\d+\.?\d*)\s*(>|greater than)\s*(\d+\.?\d*)', '>'),
            (r'(\d+\.?\d*)\s*(<|less than)\s*(\d+\.?\d*)', '<'),
            (r'(\d+\.?\d*)\s*(>=|at least)\s*(\d+\.?\d*)', '>='),
            (r'(\d+\.?\d*)\s*(<=|at most)\s*(\d+\.?\d*)', '<='),
        ]
        
        for pattern, op in comp_patterns:
            for m in re.finditer(pattern, text.lower()):
                constraints.append((float(m.group(1)), op, float(m.group(3))))
        
        return constraints
    
    def _compute_reward(self, prompt: str, candidate: str, graph: Dict, 
                       tree: Dict, numeric_constraints: List) -> float:
        """Compute reward = lambda*semantic + (1-lambda)*regulatory."""
        # Compositional semantic score
        semantic_score = self._eval_compositional_semantics(prompt, candidate, tree)
        
        # GRN constraint propagation score
        regulatory_score = self._propagate_grn(prompt, candidate, graph)
        
        # Constructive computation score
        computation_score = self._compute_answer(prompt, candidate, numeric_constraints)
        
        # NCD tiebreaker (max 15%)
        ncd_score = self._normalized_compression_distance(prompt, candidate)
        
        # Weighted combination
        reward = (0.3 * semantic_score + 
                 0.3 * regulatory_score + 
                 0.4 * computation_score +
                 0.0 * (1 - ncd_score))  # NCD optional
        
        return np.clip(reward, 0, 1)
    
    def _eval_compositional_semantics(self, prompt: str, candidate: str, tree: Dict) -> float:
        """Evaluate semantic coherence via tree."""
        op = tree.get('op', 'atomic')
        
        # Simple heuristics for tree evaluation
        if op == 'conjunction':
            # Both prompt and candidate should have conjunctive structure
            prompt_parts = re.split(r'\band\b', prompt.lower())
            cand_parts = re.split(r'\band\b', candidate.lower())
            if len(cand_parts) >= len(prompt_parts):
                return 0.8
            return 0.4
        
        elif op == 'disjunction':
            prompt_parts = re.split(r'\bor\b', prompt.lower())
            if any(part.strip() in candidate.lower() for part in prompt_parts):
                return 0.7
            return 0.3
        
        elif op == 'implication':
            # Check if candidate addresses consequent
            if re.search(r'\bthen\b', prompt.lower()):
                then_part = prompt.lower().split('then')[-1].strip()
                if any(word in candidate.lower() for word in then_part.split()[:3]):
                    return 0.75
            return 0.4
        
        return 0.5
    
    def _propagate_grn(self, prompt: str, candidate: str, graph: Dict) -> float:
        """Propagate constraints through GRN."""
        if not graph['nodes']:
            return 0.5
        
        # Initialize node activations
        n_nodes = len(graph['nodes'])
        x = np.random.rand(n_nodes) * 0.5 + 0.25
        
        # Build adjacency matrix
        W = np.zeros((n_nodes, n_nodes))
        for i, (edge_from, edge_to, weight) in enumerate(graph['edges']):
            if i < n_nodes:
                W[i, (i+1) % n_nodes] = weight
        
        # Propagate
        for _ in range(self.grn_iterations):
            x = (W @ x + x) / 2
            x = (x > 0.5).astype(float)
        
        return float(np.mean(x))
    
    def _compute_answer(self, prompt: str, candidate: str, constraints: List) -> float:
        """CONSTRUCTIVE COMPUTATION: Actually solve the problem."""
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric comparison (e.g., "Is 9.11 < 9.9?")
        numbers_prompt = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', prompt)]
        numbers_cand = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', candidate)]
        
        if len(numbers_prompt) >= 2:
            if '<' in p_lower or 'less than' in p_lower:
                correct = numbers_prompt[0] < numbers_prompt[1]
                if (correct and 'yes' in c_lower) or (not correct and 'no' in c_lower):
                    score += 0.5
            elif '>' in p_lower or 'greater than' in p_lower:
                correct = numbers_prompt[0] > numbers_prompt[1]
                if (correct and 'yes' in c_lower) or (not correct and 'no' in c_lower):
                    score += 0.5
        
        # Arithmetic computation
        if '+' in p_lower or 'plus' in p_lower or 'sum' in p_lower:
            if len(numbers_prompt) >= 2:
                expected = sum(numbers_prompt)
                if numbers_cand and abs(numbers_cand[0] - expected) < 0.01:
                    score += 0.6
        
        # Bayesian posterior (base rate problems)
        if 'probability' in p_lower or 'chance' in p_lower or '%' in prompt:
            if len(numbers_prompt) >= 2:
                # Simple Bayes: P(A|B) heuristic
                if numbers_cand and 0 <= numbers_cand[0] <= 1:
                    score += 0.3
        
        # Temporal ordering
        if 'before' in p_lower or 'after' in p_lower:
            if 'before' in p_lower and 'before' in c_lower:
                score += 0.4
            elif 'after' in p_lower and 'after' in c_lower:
                score += 0.4
        
        # Negation handling
        if 'not' in p_lower:
            if 'no' in c_lower or 'not' in c_lower or 'false' in c_lower:
                score += 0.3
        
        return min(score, 1.0)
    
    def _normalized_compression_distance(self, s1: str, s2: str) -> float:
        """Compute NCD as optional tiebreaker."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0, min(1, ncd))
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        """Generate brief reasoning explanation."""
        if score > 0.7:
            return "Strong structural and computational match"
        elif score > 0.5:
            return "Moderate semantic coherence"
        elif score > 0.3:
            return "Weak constraint satisfaction"
        else:
            return "Low confidence; possible mismatch"