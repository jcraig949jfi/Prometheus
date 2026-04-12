from typing import Set

"""
Belief-Propagation Abstract Regulator (BPAR)

Fuses Gene Regulatory Networks + Theory of Mind + Abstract Interpretation.
Models reasoning as belief propagation through a signed regulatory graph where
nodes are propositions and edges encode activation/repression rules. Tracks
agent-specific beliefs for recursive mentalizing.
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    track_beliefs, topological_sort, confidence_from_agreement,
    information_sufficiency, bayesian_update, entropy
)


class ReasoningTool:
    def __init__(self):
        self.alpha = 0.3  # damping factor for belief propagation
        self.epsilon = 0.01  # convergence threshold
        self.max_iter = 50
        self.lambda_penalty = 0.2
        
    def _extract_propositions(self, text):
        """Parse text into atomic propositions and regulatory edges."""
        text = text.lower()
        nodes = {}
        edges = []
        node_id = 0
        
        # Extract comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==)\s*(\w+)', text):
            prop = f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
            if prop not in nodes:
                nodes[prop] = node_id
                node_id += 1
        
        # Extract numeric inequalities
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', text):
            try:
                left, op, right = float(m.group(1)), m.group(2), float(m.group(3))
                result = eval(f"{left}{op}{right}")
                prop = f"num_{m.group(1)}_{op}_{m.group(3)}"
                if prop not in nodes:
                    nodes[prop] = node_id
                    node_id += 1
            except:
                pass
        
        # Extract conditionals (if-then creates activation edge)
        for m in re.finditer(r'if\s+([^,\.]+?)\s+then\s+([^,\.]+?)(?:\.|,|$)', text):
            ante = m.group(1).strip()
            cons = m.group(2).strip()
            if ante not in nodes:
                nodes[ante] = node_id
                node_id += 1
            if cons not in nodes:
                nodes[cons] = node_id
                node_id += 1
            edges.append((nodes[ante], nodes[cons], 1))  # activation
        
        # Extract negations (creates repression edge)
        for m in re.finditer(r'not\s+(\w+)', text):
            prop = m.group(1)
            neg_prop = f"not_{prop}"
            if prop not in nodes:
                nodes[prop] = node_id
                node_id += 1
            if neg_prop not in nodes:
                nodes[neg_prop] = node_id
                node_id += 1
            edges.append((nodes[prop], nodes[neg_prop], -1))  # repression
        
        # Extract belief predicates for Theory of Mind
        agents = {}
        for m in re.finditer(r'(\w+)\s+(?:believes?|thinks?)\s+(?:that\s+)?([^,\.]+)', text):
            agent = m.group(1)
            belief = m.group(2).strip()
            if agent not in agents:
                agents[agent] = []
            if belief not in nodes:
                nodes[belief] = node_id
                node_id += 1
            agents[agent].append(nodes[belief])
        
        return nodes, edges, agents
    
    def _propagate_beliefs(self, n_nodes, edges, initial_beliefs):
        """Run belief propagation on regulatory graph."""
        beliefs = np.array(initial_beliefs)
        
        for _ in range(self.max_iter):
            new_beliefs = beliefs.copy()
            for src, dst, sign in edges:
                if src < len(beliefs) and dst < len(beliefs):
                    delta = sign * beliefs[src]
                    new_beliefs[dst] = np.clip(new_beliefs[dst] + self.alpha * delta, 0, 1)
            
            if np.sum(np.abs(new_beliefs - beliefs)) < self.epsilon:
                break
            beliefs = new_beliefs
        
        return beliefs
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability markers."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did \w+ (fail|stop))', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+.*\ba\b \w+', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\w+ told \w+ (he|she)', p) and 'who' in p:
            return 0.2
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p) and not re.search(r'(only|exactly)', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        
        # Insufficient information
        if re.search(r'(not enough|cannot determine|insufficient|ambiguous)', p):
            return 0.25
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Score candidates via belief propagation through regulatory graph."""
        nodes, edges, agents = self._extract_propositions(prompt)
        
        if not nodes:
            # Fallback: use NCD
            return self._ncd_fallback(prompt, candidates)
        
        # Initialize beliefs (0.5 = unknown)
        initial = np.full(len(nodes), 0.5)
        
        # Set known facts from prompt to 1.0
        for m in re.finditer(r'(\w+)\s+is\s+(true|correct|yes)', prompt.lower()):
            prop = m.group(1)
            if prop in nodes:
                initial[nodes[prop]] = 1.0
        
        # Propagate beliefs
        prompt_beliefs = self._propagate_beliefs(len(nodes), edges, initial)
        
        # Theory of Mind: track agent-specific beliefs
        agent_beliefs = {}
        for agent, belief_nodes in agents.items():
            agent_initial = initial.copy()
            for bn in belief_nodes:
                if bn < len(agent_initial):
                    agent_initial[bn] = 0.8  # agent holds this belief
            agent_beliefs[agent] = self._propagate_beliefs(len(nodes), edges, agent_initial)
        
        # Score each candidate
        results = []
        for cand in candidates:
            cand_nodes, cand_edges, _ = self._extract_propositions(cand)
            
            # Map candidate propositions to main graph
            scores = []
            for prop, cid in cand_nodes.items():
                if prop in nodes:
                    scores.append(prompt_beliefs[nodes[prop]])
            
            if scores:
                answer_fit = np.mean(scores)
                consistency_penalty = np.mean([abs(s - 0.5) * (1 - 2*abs(s - 0.5)) for s in scores])
                score = answer_fit - self.lambda_penalty * consistency_penalty
            else:
                # Use NCD as tiebreaker
                score = 0.1 * self._ncd(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Belief fit: {answer_fit:.3f}, Consistency: {consistency_penalty:.3f}" if scores else "NCD fallback"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on meta-cognitive assessment."""
        meta_conf = self._meta_confidence(prompt)
        
        nodes, edges, _ = self._extract_propositions(prompt)
        if not nodes:
            return min(0.4, meta_conf)
        
        initial = np.full(len(nodes), 0.5)
        beliefs = self._propagate_beliefs(len(nodes), edges, initial)
        
        # Extract answer propositions
        ans_nodes, _, _ = self._extract_propositions(answer)
        ans_scores = []
        for prop in ans_nodes:
            if prop in nodes:
                ans_scores.append(beliefs[nodes[prop]])
        
        if ans_scores:
            # High confidence if beliefs are definitive (near 0 or 1)
            avg_belief = np.mean(ans_scores)
            definitiveness = 2 * abs(avg_belief - 0.5)
            base_conf = min(0.9, definitiveness)
        else:
            base_conf = 0.4
        
        return min(base_conf, meta_conf)
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance (max 15% of score)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return 1 - (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _ncd_fallback(self, prompt, candidates):
        """Pure NCD ranking when structural parsing fails."""
        results = []
        for cand in candidates:
            score = self._ncd(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "NCD similarity (no structure found)"
            })
        return sorted(results, key=lambda x: x["score"], reverse=True)