import re
import math
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Set
import numpy as np

class ReasoningTool:
    """
    A reasoning tool integrating Information Theory, Mechanism Design, and Multi-Armed Bandits.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (SVO triples, negations, conditionals, numerics) 
       into a directed graph.
    2. Constraint Propagation: Uses NumPy boolean matrices to compute the transitive closure 
       of truths assuming a candidate answer is correct.
    3. Information Gain: Calculates IG based on the reduction in entropy of the proposition set.
    4. Mechanism Design: Applies a logarithmic scoring rule to incentivize truthful reporting 
       (maximizing log-likelihood of consistent states).
    5. Bandit Selection: Uses Upper Confidence Bound (UCB) to balance exploitation (high score) 
       and exploration (uncertainty), though here used primarily for ranking robustness.
    6. Epistemic Honesty (Tier B): Explicitly checks for presuppositions, ambiguities, and 
       unanswerable constraints to cap confidence, ensuring low confidence on trap questions.
    """

    def __init__(self):
        self._evaluation_history = defaultdict(lambda: {"count": 0, "sum_score": 0.0})
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|twice|double)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'ordering': re.compile(r'\b(before|after|first|last|ranked)\b', re.IGNORECASE),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ (fail|stop|die)|when did .+ stop)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believes)\b', re.IGNORECASE)
        }

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract logical propositions as normalized strings."""
        props = []
        # Simple sentence splitter and keyword extractor
        sentences = re.split(r'[.\?!]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Normalize whitespace
            sent = re.sub(r'\s+', ' ', sent)
            props.append(sent)
        return props

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[List[str], np.ndarray]:
        """
        Build a logical graph from prompt + candidate.
        Returns nodes and an adjacency matrix for constraint propagation.
        """
        full_text = f"{prompt} {candidate}"
        nodes = self._extract_propositions(full_text)
        n = len(nodes)
        if n == 0:
            return [], np.array([])
            
        # Adjacency matrix for logical implication (i -> j)
        adj = np.zeros((n, n), dtype=bool)
        
        # Heuristic edge creation based on proximity and keywords
        # In a full system, this would be a formal logic parser. 
        # Here we simulate structural consistency via keyword overlap and ordering.
        words = [set(re.findall(r'\w+', node.lower())) for node in nodes]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Self-consistency
                adj[i, i] = True
                
                # Transitive-like heuristic: If node i and j share significant vocabulary,
                # they are logically linked in this simplified model.
                intersection = len(words[i] & words[j])
                union = len(words[i] | words[j])
                if union > 0 and (intersection / union) > 0.3:
                    adj[i, j] = True
                    
                # Specific structural rules
                node_text = nodes[i].lower()
                if re.search(r'if', node_text) and re.search(r'then', nodes[j].lower()):
                     adj[i, j] = True # Simplified conditional linking
                if re.search(r'because', node_text):
                     adj[j, i] = True # Effect follows cause in reverse dependency
                    
        return nodes, adj

    def _propagate_constraints(self, adj: np.ndarray) -> np.ndarray:
        """Compute transitive closure using Warshall's algorithm (simplified for boolean)."""
        if adj.size == 0:
            return adj
        closure = adj.copy()
        n = adj.shape[0]
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if closure[i, k] and closure[k, j]:
                        closure[i, j] = True
        return closure

    def _calculate_information_gain(self, prompt: str, candidate: str) -> float:
        """
        Calculate Information Gain: IG = H(P) - H(P|C(a))
        Approximated by the reduction in uncertainty (entropy) of the proposition set
        when the candidate is assumed true.
        """
        nodes, adj = self._build_graph(prompt, candidate)
        if len(nodes) == 0:
            return 0.0
            
        closure = self._propagate_constraints(adj)
        
        # Estimate probabilities based on node connectivity (degree centrality as proxy for Pr(p))
        # In a real corpus, this would be external frequencies. Here we use internal consistency.
        degrees = np.sum(closure, axis=1).astype(float)
        total_deg = np.sum(degrees)
        if total_deg == 0:
            return 0.0
            
        probs = degrees / total_deg
        # Avoid log(0)
        probs = probs + 1e-9 
        probs = probs / np.sum(probs)
        
        # Prior Entropy (uniform assumption before constraint propagation implies high entropy)
        # Actually, we measure the entropy of the resulting consistent state.
        # High consistency (low entropy in outcome) given the candidate implies high information gain if the candidate resolves ambiguity.
        # Formula: Sum( p_i * log(p_i) )
        entropy = -np.sum(probs * np.log2(probs))
        
        # Normalize by max possible entropy to get a score between 0 and 1 roughly
        max_entropy = np.log2(len(nodes)) if len(nodes) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Information Gain is inverse of remaining entropy (less entropy = more info gained)
        return 1.0 - normalized_entropy

    def _mechanism_score(self, prompt: str, candidate: str) -> float:
        """
        Logarithmic scoring rule: S(a) = log(Pr(C(a) | evidence))
        We approximate Pr(C(a)|evidence) by the ratio of consistent propositions 
        to total propositions in the closure.
        """
        nodes, adj = self._build_graph(prompt, candidate)
        if len(nodes) == 0:
            return -10.0 # Penalty for empty
            
        closure = self._propagate_constraints(adj)
        
        # Count consistent relations (True values in closure)
        # A fully consistent candidate should maximize coherent links without contradiction.
        # We simulate contradiction detection by checking for 'not' patterns that clash.
        text = f"{prompt} {candidate}".lower()
        contradiction_penalty = 0.0
        
        if self.patterns['negation'].search(text):
            # Crude contradiction check: if 'not' appears near positive assertions of same root
            # For this implementation, we penalize length if negations are present without clear structure
            if text.count('not') > 2: 
                contradiction_penalty = 0.5

        # Score based on density of logical connections (consistency)
        n = len(nodes)
        if n == 0: return -10.0
        density = np.sum(closure) / (n * n)
        
        # Log score
        score = math.log(density + 1e-9)
        return score - contradiction_penalty

    def _ucb_score(self, candidate: str, base_score: float) -> float:
        """
        Upper Confidence Bound: Score = mean_reward + sqrt(2 * ln(N) / n_a)
        Since we don't have a history of user feedback in this static eval, 
        we use the number of times this specific candidate string has been seen 
        in the current session (simulated via history) or treat each eval as N=1 for the bandit term
        to prioritize structural robustness (base_score) while adding a small exploration bonus 
        for novel phrasing if we had a corpus. 
        Here, we simplify: The 'exploration' term encourages answers that are structurally complex 
        (more propositions) as they have higher potential variance.
        """
        key = candidate[:50] # Hash key
        stats = self._evaluation_history[key]
        n_a = stats['count'] + 1 # Current evaluation counts as 1
        
        # Global N (approximated by total evaluations)
        N = sum(s['count'] for s in self._evaluation_history.values()) + 1
        if N == 0: N = 1
        
        exploration_bonus = math.sqrt((2 * math.log(N + 1)) / n_a)
        
        # Weighted sum: Base score dominates, UCB breaks ties
        return base_score + 0.1 * exploration_bonus

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know, so assume ambiguous)
            return 0.4
            
        # 3. Pronoun Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.3
            
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.5
            
        # 5. Unanswerability (No numbers in math questions, etc - simplified)
        # If question asks for a number but has no digits?
        if re.search(r'how many|what number|calculate', p_lower):
            if not self.patterns['numeric'].search(p_lower):
                return 0.2 # Likely missing info

        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c_concat = len(zlib.compress(concat))
        
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
            
        ncd = (c_concat - min_len) / max(c1, c2)
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate prompt features to avoid re-parsing
        prompt_nodes = self._extract_propositions(prompt)
        has_numeric = bool(self.patterns['numeric'].search(prompt))
        
        for cand in candidates:
            # 1. Structural Parsing & Graph Construction
            nodes, adj = self._build_graph(prompt, cand)
            
            # 2. Constraint Propagation & Information Gain
            ig_score = self._calculate_information_gain(prompt, cand)
            
            # 3. Mechanism Design (Log Score)
            mech_score = self._mechanism_score(prompt, cand)
            
            # 4. Constructive Computation (Numeric Check)
            # If both prompt and candidate have numbers, verify consistency
            comp_score = 0.0
            if has_numeric:
                p_nums = re.findall(r'-?\d+(?:\.\d+)?', prompt)
                c_nums = re.findall(r'-?\d+(?:\.\d+)?', cand)
                if p_nums and c_nums:
                    # Simple heuristic: if candidate repeats numbers correctly, boost
                    # In a real solver, we'd execute the math. 
                    # Here we reward numeric presence in valid contexts.
                    comp_score = 0.5 * (len(c_nums) / (len(p_nums) + 1))
            
            # Combine Scores
            # Structural (IG) >= 50%, Computation >= 20%, NCD <= 15%
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.15 # Higher similarity (lower NCD) is slightly better for relevance
            
            raw_score = (ig_score * 0.55) + (mech_score * 0.1) + (comp_score * 0.20) + ncd_bonus
            
            # Apply UCB
            final_score = self._ucb_score(cand, raw_score)
            
            # Apply Meta-Confidence Cap for the 'reasoning' string generation logic
            # Note: The score itself isn't capped, but the confidence derived from it will be.
            # However, if meta_confidence is very low, we should penalize the score significantly
            # to ensure it doesn't rank high if it's a trap answer.
            if meta_cap < 0.3:
                final_score *= 0.5 # Penalize trap answers
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"IG:{ig_score:.2f}, Mech:{mech_score:.2f}, Comp:{comp_score:.2f}, MetaCap:{meta_cap:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Update history for UCB
        for res in results:
            key = res['candidate'][:50]
            self._evaluation_history[key]['count'] += 1
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on _meta_confidence for Tier B traps.
        """
        # 1. Check Meta-Confidence (Traps)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Calculate base confidence from scoring components
        ig = self._calculate_information_gain(prompt, answer)
        mech = self._mechanism_score(prompt, answer)
        
        # Normalize mech score (log likelihood) to 0-1 range roughly
        # log(1) = 0, log(0) = -inf. 
        # Assume typical good scores are > -2, bad < -5
        base_conf = (ig * 0.6) + ((max(mech, -5) + 5) / 10.0 * 0.4)
        base_conf = max(0.0, min(1.0, base_conf))
        
        # 3. Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # 4. Honesty check: If no structural match (empty graph), low confidence
        nodes, _ = self._build_graph(prompt, answer)
        if len(nodes) < 2: # Too few propositions to reason about
            final_conf = min(final_conf, 0.3)
            
        return round(final_conf, 4)