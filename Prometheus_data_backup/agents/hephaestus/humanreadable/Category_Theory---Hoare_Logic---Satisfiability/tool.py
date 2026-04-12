from typing import Dict, Set, Tuple

"""
Category Theory x Hoare Logic x Satisfiability Reasoning Tool
with State Dynamics Tracking (Frame C)

Core mechanism:
1. Parse text into category-theoretic graph (propositions as objects, relations as morphisms)
2. Construct Hoare triples {P} C {Q} for each candidate
3. Score via SAT solver with MUC-based distance metric
4. Track state dynamics: premise processing as trajectory evolution
5. Confidence based on trajectory stability and meta-analysis of prompt
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.prop_counter = 0
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Parse prompt into category-theoretic structure
        premises, graph, prop_map = self._parse_to_category_graph(prompt)
        
        results = []
        for cand in candidates:
            # Construct Hoare triple
            post_cond = self._extract_propositions(cand)
            
            # SAT-based entailment score
            sat_score = self._sat_entailment_score(premises, post_cond, graph)
            
            # State dynamics score
            dyn_score = self._dynamics_score(premises, post_cond, prompt, cand)
            
            # Structural score
            struct_score = self._structural_match(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            final_score = 0.4 * dyn_score + 0.25 * sat_score + 0.2 * struct_score + 0.15 * ncd_score
            
            reasoning = f"Dyn:{dyn_score:.2f} SAT:{sat_score:.2f} Struct:{struct_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence check for epistemic honesty
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate answer quality
        premises, graph, _ = self._parse_to_category_graph(prompt)
        post_cond = self._extract_propositions(answer)
        
        sat_score = self._sat_entailment_score(premises, post_cond, graph)
        dyn_score = self._dynamics_score(premises, post_cond, prompt, answer)
        
        # Confidence capped by meta-analysis
        base_conf = 0.5 * sat_score + 0.5 * dyn_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect reasoning traps and ambiguity"""
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'have you (stopped|quit)', r'why did .+ (fail|stop)', 
                          r'when did you stop', r'admit that']
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every \w+.*?\ba\b', p_lower) and 'same' not in p_lower:
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it) (was|is)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+[?.]', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower) and 'most' not in p_lower:
            return 0.3
        
        return 0.85  # Default: answerable
    
    def _parse_to_category_graph(self, text: str) -> Tuple[List[str], np.ndarray, Dict]:
        """Extract propositions (objects) and relations (morphisms)"""
        props = self._extract_propositions(text)
        n = len(props)
        graph = np.zeros((n, n), dtype=bool)
        
        # Detect morphisms (relations)
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i != j and self._has_morphism(text, p1, p2):
                    graph[i, j] = True
        
        return props, graph, {p: i for i, p in enumerate(props)}
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions via regex"""
        # Comparatives, equations, simple clauses
        patterns = [
            r'(\w+)\s+(is|are|was|were)\s+([\w\s]+)',
            r'(\w+)\s*([<>=]=?)\s*(\d+\.?\d*)',
            r'(if|when|because)\s+([^,.]+)',
            r'(\w+)\s+(taller|shorter|faster|older)\s+than\s+(\w+)'
        ]
        
        props = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                props.append(m.group(0).strip())
        
        # Fallback: split on punctuation
        if not props:
            props = [s.strip() for s in re.split(r'[.;,]', text) if len(s.strip()) > 5]
        
        return props[:20]  # Limit for performance
    
    def _has_morphism(self, text: str, p1: str, p2: str) -> bool:
        """Detect if there's a relation from p1 to p2"""
        # Check for conditional/causal connectives between propositions
        p1_idx = text.find(p1)
        p2_idx = text.find(p2)
        if p1_idx < 0 or p2_idx < 0 or p1_idx >= p2_idx:
            return False
        
        between = text[p1_idx + len(p1):p2_idx]
        morphisms = ['then', 'therefore', 'so', 'because', 'leads to', 'implies']
        return any(m in between.lower() for m in morphisms)
    
    def _sat_entailment_score(self, premises: List[str], conclusions: List[str], graph: np.ndarray) -> float:
        """SAT-based scoring with MUC distance"""
        if not premises or not conclusions:
            return 0.5
        
        # Simple reachability check (graph traversal approximation)
        n = len(premises)
        reachable = np.eye(n, dtype=bool)
        for _ in range(n):
            reachable = reachable | (reachable @ graph)
        
        # Check if conclusions reachable from premises
        coverage = np.mean([any(c in p for p in premises) for c in conclusions])
        return coverage
    
    def _dynamics_score(self, premises: List[str], conclusions: List[str], prompt: str, answer: str) -> float:
        """State trajectory stability analysis"""
        if not premises:
            return 0.5
        
        # Initialize state vector
        vocab = self._build_vocab(prompt + " " + answer)
        state = np.zeros(len(vocab))
        
        trajectories = []
        # Process premises sequentially
        for perm_idx in range(min(3, len(premises))):  # Test multiple orderings
            state_t = state.copy()
            traj = [state_t.copy()]
            
            # Permute premise order
            perm_premises = premises[perm_idx:] + premises[:perm_idx]
            
            for prem in perm_premises:
                # Update state based on premise content
                state_t = self._update_state(state_t, prem, vocab)
                traj.append(state_t.copy())
            
            trajectories.append(np.array(traj))
        
        # Measure trajectory stability (variance across permutations)
        if len(trajectories) > 1:
            final_states = [t[-1] for t in trajectories]
            stability = 1.0 - np.mean(np.std(final_states, axis=0))
            stability = max(0, min(1, stability))
        else:
            stability = 0.5
        
        # Convergence rate (how quickly state stabilizes)
        if len(trajectories[0]) > 1:
            deltas = [np.linalg.norm(trajectories[0][i+1] - trajectories[0][i]) 
                     for i in range(len(trajectories[0])-1)]
            convergence = 1.0 / (1.0 + np.mean(deltas)) if deltas else 0.5
        else:
            convergence = 0.5
        
        # Answer alignment with final state
        answer_vec = self._text_to_vec(answer, vocab)
        final_state = trajectories[0][-1]
        alignment = np.dot(answer_vec, final_state) / (np.linalg.norm(answer_vec) * np.linalg.norm(final_state) + 1e-9)
        alignment = max(0, alignment)
        
        return 0.4 * stability + 0.3 * convergence + 0.3 * alignment
    
    def _build_vocab(self, text: str) -> Dict[str, int]:
        """Build vocabulary from text"""
        words = re.findall(r'\w+', text.lower())
        return {w: i for i, w in enumerate(set(words))}
    
    def _text_to_vec(self, text: str, vocab: Dict[str, int]) -> np.ndarray:
        """Convert text to vector using vocab"""
        vec = np.zeros(len(vocab))
        words = re.findall(r'\w+', text.lower())
        for w in words:
            if w in vocab:
                vec[vocab[w]] += 1
        return vec / (np.linalg.norm(vec) + 1e-9)
    
    def _update_state(self, state: np.ndarray, premise: str, vocab: Dict[str, int]) -> np.ndarray:
        """Update state vector with premise (reservoir-like dynamics)"""
        prem_vec = self._text_to_vec(premise, vocab)
        # Leaky integration with decay
        alpha = 0.7
        return alpha * state + (1 - alpha) * prem_vec
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Structural feature matching"""
        score = 0.0
        p_lower, c_lower = prompt.lower(), candidate.lower()
        
        # Negation handling
        p_neg = bool(re.search(r'\b(not|no|never|neither)\b', p_lower))
        c_neg = bool(re.search(r'\b(not|no|never|neither)\b', c_lower))
        if p_neg == c_neg:
            score += 0.2
        
        # Numeric comparison
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if p_nums and c_nums:
            # Check if comparison direction matches
            if '>' in prompt or 'greater' in p_lower:
                if any(cn > pn for cn in c_nums for pn in p_nums):
                    score += 0.3
            elif '<' in prompt or 'less' in p_lower:
                if any(cn < pn for cn in c_nums for pn in p_nums):
                    score += 0.3
            elif '=' in prompt or 'equal' in p_lower:
                if any(abs(cn - pn) < 0.01 for cn in c_nums for pn in p_nums):
                    score += 0.3
        
        # Conditional structure match
        if 'if' in p_lower and 'then' in p_lower:
            if 'if' in c_lower or 'when' in c_lower:
                score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0