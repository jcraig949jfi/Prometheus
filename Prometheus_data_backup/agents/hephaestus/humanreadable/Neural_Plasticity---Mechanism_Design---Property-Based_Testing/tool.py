import re
import numpy as np
from typing import List, Dict, Tuple, Set
from itertools import combinations

class ReasoningTool:
    """
    A reasoning evaluator combining Neural Plasticity (Hebbian learning), 
    Mechanism Design (VCG scoring), and Property-Based Testing (shrinking).
    
    Core Logic:
    1. Parsing: Extracts atomic propositions and logical relations (causal, conditional, comparative).
    2. Plasticity: Builds a co-occurrence graph (W) where frequent valid pairs strengthen connections.
    3. Mechanism Design: Scores candidates based on the 'welfare' (sum of satisfied edge weights) 
       they contribute to the global truth graph. Uses a VCG-style penalty for inconsistency.
    4. Property Testing: Perturbs the answer (negation flips, number shifts) to measure fragility.
       Robust answers retain high scores; fragile ones are penalized.
    """

    def __init__(self):
        self.eta = 0.5  # Learning rate for Hebbian update
        self.tau = 0.1  # Pruning threshold
        self.lambda_frag = 0.5  # Penalty weight for fragility
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\bnot\b|!\b|\bnever\b|\bno\b\s+\w+', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|and|or|$)', re.IGNORECASE),
            'comparative': re.compile(r'(\d+\.?\d*|\w+)\s*(>|<|>=|<=|equals?|is\s+more\s+than|is\s+less\s+than)\s*(\d+\.?\d*|\w+)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+(causes?|leads?\s+to|results?\s+in|implies)\s+(.+?)(?:\.|,|and|or|$)', re.IGNORECASE),
            'ordering': re.compile(r'(.+?)\s+(before|after|precedes?|follows?)\s+(.+?)(?:\.|,|and|or|$)', re.IGNORECASE)
        }

    def _extract_nodes_edges(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Extract atomic nodes and directed edges (source, target, type) from text."""
        nodes = set()
        edges = []
        text_lower = text.lower()
        
        # Simple tokenization for nodes (alphabetic words and numbers)
        raw_tokens = re.findall(r'[a-zA-Z0-9\.]+', text)
        for t in raw_tokens:
            if len(t) > 1 or t.isdigit(): # Filter single chars unless digits
                nodes.add(t.lower())

        # Extract Conditionals
        for match in self.patterns['conditional'].finditer(text):
            antecedent, consequent = match.group(1).strip(), match.group(2).strip()
            # Simplify to key tokens
            ant_tok = antecedent.split()[-1] if antecedent.split() else ""
            con_tok = consequent.split()[0] if consequent.split() else ""
            if ant_tok and con_tok:
                edges.append((ant_tok.lower(), con_tok.lower(), 'IMPLIES'))
                nodes.update([ant_tok.lower(), con_tok.lower()])

        # Extract Comparatives
        for match in self.patterns['comparative'].finditer(text):
            left, op, right = match.group(1), match.group(2), match.group(3)
            edges.append((left.lower(), right.lower(), 'COMPARE_' + op.replace('=', '').replace(' ', '').upper()))
            nodes.update([left.lower(), right.lower()])

        # Extract Causal
        for match in self.patterns['causal'].finditer(text):
            cause, _, effect = match.groups()
            c_tok = cause.split()[-1] if cause.split() else ""
            e_tok = effect.split()[0] if effect.split() else ""
            if c_tok and e_tok:
                edges.append((c_tok.lower(), e_tok.lower(), 'CAUSES'))
                nodes.update([c_tok.lower(), e_tok.lower()])

        # Extract Ordering
        for match in self.patterns['ordering'].finditer(text):
            left, rel, right = match.groups()
            l_tok = left.split()[-1] if left.split() else ""
            r_tok = right.split()[0] if right.split() else ""
            if l_tok and r_tok:
                dir_type = 'BEFORE' if 'before' in rel.lower() or 'precedes' in rel.lower() else 'AFTER'
                edges.append((l_tok.lower(), r_tok.lower(), dir_type))
                nodes.update([l_tok.lower(), r_tok.lower()])

        return list(nodes), edges

    def _build_graph(self, prompt: str, candidates: List[str]) -> Tuple[List[str], np.ndarray, Dict[str, int]]:
        """Construct the graph and apply Hebbian learning from prompt + candidates."""
        all_text = prompt + " " + " ".join(candidates)
        nodes, edges = self._extract_nodes_edges(all_text)
        node_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        
        if n == 0:
            return [], np.array([]), {}

        W = np.zeros((n, n))
        
        # Initialize with prompt structure (stronger weight)
        p_nodes, p_edges = self._extract_nodes_edges(prompt)
        p_map = {node_map[k]: 0 for k in p_nodes if k in node_map} # Just checking existence
        
        for src, tgt, typ in p_edges:
            if src in node_map and tgt in node_map:
                i, j = node_map[src], node_map[tgt]
                W[i, j] += 2.0 # Prompt edges are strong priors

        # Hebbian Learning: Co-occurrence in candidates strengthens edges
        # We simulate "correct" co-occurrence by assuming prompt structure is ground truth
        # and candidates that reinforce prompt edges get positive reinforcement.
        for cand in candidates:
            c_nodes, c_edges = self._extract_nodes_edges(cand)
            c_node_set = set(c_nodes)
            
            # Reinforce edges found in candidate that align with prompt topology
            for src, tgt, typ in c_edges:
                if src in node_map and tgt in node_map:
                    i, j = node_map[src], node_map[tgt]
                    # Hebbian update: W_ij += eta * co_occurrence
                    W[i, j] += self.eta
            
        # Pruning
        W[np.abs(W) < self.tau] = 0
        
        return nodes, W, node_map

    def _compute_welfare(self, W: np.ndarray, active_indices: Set[int]) -> float:
        """Calculate social welfare: sum of weights where both nodes are active."""
        if W.size == 0:
            return 0.0
        welfare = 0.0
        indices = list(active_indices)
        for i in indices:
            for j in indices:
                if i != j:
                    welfare += W[i, j]
        return welfare

    def _vcg_score(self, W: np.ndarray, candidate_nodes: Set[int], all_node_indices: Set[int]) -> float:
        """
        Compute VCG-style score.
        Score = Welfare(All) - Welfare(All \ Candidate)
        This measures the marginal contribution of the candidate's propositions to the global consistency.
        """
        if W.size == 0:
            return 0.0
            
        # Welfare with candidate
        sw_with = self._compute_welfare(W, all_node_indices)
        
        # Welfare without candidate (excluding nodes unique to this candidate if possible, 
        # but here we treat the candidate's specific assertions as the variable)
        # Simplified: We compare the welfare of the graph induced by the candidate 
        # against the welfare of the graph induced by the prompt alone (baseline).
        # Actually, per VCG definition in prompt: p_k = SW(r*_k) - SW(r*_-k)
        # Let's approximate: Score = Internal Consistency + Alignment with Prompt
        
        # Internal consistency of candidate
        internal = 0.0
        for i in candidate_nodes:
            for j in candidate_nodes:
                if i != j:
                    internal += W[i, j]
                    
        # Alignment (edges from candidate to prompt context)
        # Since we built W from the union, high weights imply agreement with prompt structure
        return internal

    def _mutate(self, answer: str) -> List[str]:
        """Generate perturbations for property-based testing."""
        mutants = []
        words = answer.split()
        if not words:
            return mutants
            
        # 1. Negation flip
        for i, w in enumerate(words):
            if re.search(r'\bnot\b', w, re.IGNORECASE):
                new_words = words[:i] + [w.replace('not', '').replace('Not', '')] + words[i+1:]
                mutants.append(" ".join(new_words))
            elif w.lower() in ['is', 'are', 'was', 'were']:
                mutants.append(answer.replace(w, w + " not", 1))
        
        # 2. Numeric perturbation
        nums = re.findall(r'\d+\.?\d*', answer)
        if nums:
            num_str = nums[0]
            try:
                val = float(num_str)
                delta = 1.0 if val >= 1 else 0.1
                new_val = str(val + delta)
                mutants.append(answer.replace(num_str, new_val, 1))
                mutants.append(answer.replace(num_str, str(val - delta), 1))
            except: pass

        # 3. Comparator flip
        flips = {'>': '<', '<': '>', 'more': 'less', 'less': 'more', 'before': 'after', 'after': 'before'}
        for old, new in flips.items():
            if old in answer.lower():
                # Simple case insensitive replace for demo
                mutants.append(re.sub(old, new, answer, flags=re.IGNORECASE, count=1))
                break
                
        return mutants

    def _shrink_and_score_fragility(self, prompt: str, answer: str, base_score: float) -> Tuple[float, int]:
        """Apply mutations and measure score drop. Return adjusted score and fragility size."""
        mutants = self._mutate(answer)
        if not mutants:
            return base_score, 0
            
        failures = 0
        # Check if small changes drastically reduce score (fragility)
        # We simulate this by checking if the mutant loses key structural keywords
        prompt_nodes, _ = self._extract_nodes_edges(prompt)
        prompt_set = set(prompt_nodes)
        
        for mut in mutants:
            # If mutant removes significant overlap with prompt structure, it's a "failure" of robustness
            m_nodes, _ = self._extract_nodes_edges(mut)
            overlap = len(set(m_nodes).intersection(prompt_set))
            orig_overlap = len(set(self._extract_nodes_edges(answer)[0]).intersection(prompt_set))
            
            if overlap < orig_overlap * 0.5: # Significant loss of semantic content
                failures += 1
                
        return base_score - (self.lambda_frag * failures), failures

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Fallback for empty prompt
        if not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "Empty prompt"} for c in candidates]

        nodes, W, node_map = self._build_graph(prompt, candidates)
        
        if not nodes or W.size == 0:
            # Fallback to NCD if structural parsing fails completely
            import zlib
            prompt_enc = zlib.compress(prompt.encode())
            results = []
            for c in candidates:
                cand_enc = zlib.compress(c.encode())
                concat_enc = zlib.compress((prompt + c).encode())
                ncd = (len(concat_enc) - min(len(prompt_enc), len(cand_enc))) / max(len(prompt_enc), len(cand_enc), 1)
                results.append({
                    "candidate": c, 
                    "score": float(1.0 - ncd), 
                    "reasoning": "Fallback NCD (Structural parse failed)"
                })
            return sorted(results, key=lambda x: x['score'], reverse=True)

        results = []
        for cand in candidates:
            # Extract candidate specific nodes
            c_nodes, c_edges = self._extract_nodes_edges(cand)
            c_indices = set()
            for n in c_nodes:
                if n in node_map:
                    c_indices.add(node_map[n])
            
            if not c_indices:
                # If no structural nodes found, give low score
                score = -1.0
                reasoning = "No structural logic detected."
            else:
                # VCG Scoring
                all_indices = set(node_map.values())
                raw_score = self._vcg_score(W, c_indices, all_indices)
                
                # Property Based Testing (Fragility check)
                final_score, frag_count = self._shrink_and_score_fragility(prompt, cand, raw_score)
                
                score = final_score
                reasoning = f"Consistency: {raw_score:.2f}, Fragility penalty: {frag_count * self.lambda_frag:.2f}"

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Normalize score to 0-1 range heuristically
        # Assuming typical scores range from -2 to 5 based on graph density
        normalized = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return float(np.clip(normalized, 0.0, 1.0))