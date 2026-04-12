import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool fusing Compositionality, Ergodic Theory, and Cognitive Load Theory.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic propositions and logical operators into a graph.
    2. Constraint Propagation (Ergodic-like): Iteratively resolves truth values via deterministic rules.
       The 'ergodic score' measures how quickly the system stabilizes (time_avg vs space_avg).
    3. Cognitive Load: Penalizes solutions requiring working memory chunks > 4.
    4. Epistemic Honesty (Tier B): Detects ambiguity/presuppositions to cap confidence.
    5. Scoring: Structural consistency (50%+) + Computation (20%+) + NCD tiebreaker (<15%).
    """
    
    def __init__(self):
        self.k_chunk = 4  # Working memory limit
        self.lambda_penalty = 0.5
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|because|therefore|implies)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'equality': re.compile(r'\b(equals|is|same|identical)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in)\b', re.IGNORECASE)
        }
        
        # Tier B Traps
        self.traps = {
            'presupposition': re.compile(r'\b(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE)
        }

    def _parse_text(self, text: str) -> Tuple[List[str], List[Tuple[int, str, int]]]:
        """Extract atomic propositions and edges (Compositionality)."""
        text_lower = text.lower()
        sentences = re.split(r'[.\?!]', text)
        nodes = []
        edges = []
        
        # Simple node extraction (split by connectors)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Naive tokenization for demo; in production, use NLP
            parts = re.split(r'\b(and|or|but|because|if|then)\b', sent, flags=re.IGNORECASE)
            
            start_idx = len(nodes)
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                # Clean part
                part_clean = re.sub(r'^[\s,]+|[\s,]+$', '', part)
                if part_clean:
                    nodes.append(part_clean)
                    
            # Add edges between consecutive parts in the sentence fragment
            for i in range(start_idx, len(nodes) - 1):
                op = 'and' # Default
                # Check connector between parts if available (simplified)
                edges.append((i, 'link', i+1))
                
        return nodes, edges

    def _propagate_constraints(self, nodes: List[str], edges: List[Tuple]) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Simulate constraint propagation as a dynamical system.
        Returns final truth vector and history of states.
        """
        n = len(nodes)
        if n == 0:
            return np.array([]), []
            
        truth = np.full(n, -1, dtype=float)  # -1: unknown, 0: false, 1: true
        history = []
        
        # Heuristic initialization based on simple patterns
        for i, node in enumerate(nodes):
            node_l = node.lower()
            if re.search(r'\b(true|yes|correct|fact)\b', node_l):
                truth[i] = 1.0
            elif re.search(r'\b(false|no|wrong|lie)\b', node_l):
                truth[i] = 0.0
            elif re.search(r'\b(not|never)\b', node_l):
                # If negation found, invert neighbor if known, else mark uncertain
                pass 
            # Numeric evaluation
            nums = re.findall(r'-?\d+\.?\d*', node_l)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if 'greater' in node_l or '>' in node:
                        truth[i] = 1.0 if v1 > v2 else 0.0
                    elif 'less' in node_l or '<' in node:
                        truth[i] = 1.0 if v1 < v2 else 0.0
                    elif 'equal' in node_l or '=' in node:
                        truth[i] = 1.0 if v1 == v2 else 0.0
                except: pass

        history.append(truth.copy())
        
        # Iterative propagation (Modus Ponens / Transitivity simulation)
        converged = False
        max_iter = 10
        for _ in range(max_iter):
            if converged:
                break
            old_truth = truth.copy()
            
            for src, op, tgt in edges:
                if src < len(truth) and tgt < len(truth):
                    # Propagate knowns
                    if truth[src] != -1 and truth[tgt] == -1:
                        truth[tgt] = truth[src] # Simplified propagation
                    elif truth[tgt] != -1 and truth[src] == -1:
                        truth[src] = truth[tgt]
            
            if np.array_equal(truth, old_truth):
                converged = True
            history.append(truth.copy())
            
        return truth, history

    def _calculate_ergodic_score(self, truth: np.ndarray, history: List[np.ndarray]) -> float:
        """Calculate ergodic score: 1 - |time_avg - space_avg|."""
        if len(history) == 0 or len(truth) == 0:
            return 0.0
            
        history_arr = np.array(history)
        # Time average: mean over iterations for each node
        # Filter out -1 (unknown) for mean calculation to avoid skewing, or treat as 0?
        # Treating unknown as neutral 0.5 for averaging dynamics
        clean_history = np.where(history_arr == -1, 0.5, history_arr)
        time_avg = np.mean(clean_history, axis=0)
        
        # Space average: mean of final resolved state (filtering unknowns)
        known_mask = truth != -1
        if not np.any(known_mask):
            return 0.5 # Neutral if nothing resolved
            
        space_avg_val = np.mean(truth[known_mask])
        # Broadcast space_avg to match time_avg shape for comparison
        space_avg_vec = np.full_like(time_avg, space_avg_val)
        
        diff = np.abs(time_avg - space_avg_vec)
        # Only consider nodes that eventually became known
        final_known = (truth != -1)
        if not np.any(final_known):
            return 0.0
            
        return float(1.0 - np.mean(diff[final_known]))

    def _calculate_cognitive_penalty(self, num_nodes: int) -> float:
        """Penalize if chunks exceed working memory limit k=4."""
        if num_nodes == 0:
            return 1.0
        num_chunks = int(np.ceil(num_nodes / self.k_chunk))
        ideal_chunks = max(1, int(np.ceil(num_nodes / 8))) # Heuristic ideal
        penalty = np.exp(-self.lambda_penalty * max(0, num_chunks - ideal_chunks))
        return float(penalty)

    def _check_meta_confidence(self, text: str) -> float:
        """Tier B: Detect ambiguity and traps."""
        text_l = text.lower()
        
        # 1. Presupposition
        if self.traps['presupposition'].search(text_l):
            return 0.2
        # 2. False Dichotomy (heuristic)
        if self.traps['false_dichotomy'].search(text_l) and 'or' in text_l:
            # Check if exhaustive (hard to detect, assume risky)
            return 0.4 
        # 3. Subjectivity
        if self.traps['subjectivity'].search(text_l):
            return 0.3
        # 4. Pronoun Ambiguity context
        if self.traps['pronoun_ambiguity'].search(text_l):
            return 0.3
            
        return 1.0 # No obvious trap

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1 + s2
        ncd = (len(z(concat.encode('utf-8'))) - min(len1, len2)) / max(len1, len2)
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_nodes, prompt_edges = self._parse_text(prompt)
        prompt_truth, prompt_hist = self._propagate_constraints(prompt_nodes, prompt_edges)
        prompt_ergodic = self._calculate_ergodic_score(prompt_truth, prompt_hist)
        prompt_penalty = self._calculate_cognitive_penalty(len(prompt_nodes))
        
        # Base structural score from prompt analysis
        base_structural_score = prompt_ergodic * prompt_penalty
        
        for cand in candidates:
            # 1. Structural Analysis of Candidate
            cand_nodes, cand_edges = self._parse_text(cand)
            cand_truth, cand_hist = self._propagate_constraints(cand_nodes, cand_edges)
            cand_ergodic = self._calculate_ergodic_score(cand_truth, cand_hist)
            cand_penalty = self._calculate_cognitive_penalty(len(cand_nodes))
            
            # 2. Consistency Check (Prompt vs Candidate)
            # Do they share logical operators?
            consistency = 0.5
            if len(cand_nodes) > 0:
                # Simple overlap check of logical keywords
                p_ops = set(re.findall(r'\b(and|or|not|if|then|because)\b', prompt.lower()))
                c_ops = set(re.findall(r'\b(and|or|not|if|then|because)\b', cand.lower()))
                if p_ops and c_ops:
                    consistency = len(p_ops & c_ops) / max(len(p_ops), len(c_ops))
                elif not p_ops and not c_ops:
                    consistency = 0.8 # Both simple statements
            
            # 3. Numeric/Constructive Verification
            numeric_score = 0.0
            p_nums = re.findall(r'-?\d+\.?\d*', prompt)
            c_nums = re.findall(r'-?\d+\.?\d*', cand)
            
            if p_nums and c_nums:
                # If numbers match exactly, high reward
                if set(p_nums) == set(c_nums):
                    numeric_score = 1.0
                else:
                    # Check if candidate computes something from prompt numbers
                    try:
                        # Very basic: if candidate is just a number, check if it matches a calc
                        if len(c_nums) == 1 and len(p_nums) >= 2:
                            val = float(c_nums[0])
                            p_vals = [float(x) for x in p_nums]
                            if abs(val - sum(p_vals)) < 1e-6 or abs(val - (p_vals[0] * p_vals[1])) < 1e-6:
                                numeric_score = 1.0
                    except: pass
            elif not p_nums and not c_nums:
                numeric_score = 0.5 # Neutral if no numbers
            
            # 4. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score Composition
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            # Normalize components
            struct_comp = (cand_ergodic * cand_penalty * 0.6) + (consistency * 0.2)
            comp_comp = numeric_score * 0.25
            ncd_comp = ncd_score * 0.15
            
            final_score = struct_comp + comp_comp + ncd_comp
            
            # Reasoning string
            reason = f"Ergodic:{cand_ergodic:.2f}, Load:{cand_penalty:.2f}, Num:{numeric_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        return self._check_meta_confidence(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computational proof exists.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Evaluate single candidate to get internal score
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # Map raw score to confidence range [0, 0.9] normally
        # If meta_cap is low (e.g., 0.2), confidence cannot exceed it
        base_conf = min(0.9, raw_score)
        
        final_conf = min(base_conf, meta_cap)
        
        # If no structural signal detected (score very low), return low confidence
        if raw_score < 0.2:
            final_conf = min(final_conf, 0.3)
            
        return float(np.clip(final_conf, 0.0, 1.0))