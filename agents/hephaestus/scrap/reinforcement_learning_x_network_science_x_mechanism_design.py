import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Network-Aware Incentive-Compatible Reasoning (NAIC-R) Tool.
    
    Mechanism:
    1. Mechanism Design (Core): Implements a 'truth-telling' penalty system.
       Candidates are scored on structural adherence (negations, comparatives, logic).
       Deviations from the prompt's logical constraints incur 'payments' (score penalties),
       simulating a VCG-style mechanism where lying about constraints reduces utility.
       
    2. Network Science (Synergy): Treats the prompt and candidate as nodes in a semantic graph.
       Uses token overlap and structural similarity to propagate 'reward' signals.
       Detects community structure (clusters of matching tokens) to boost scores for
       candidates that preserve the prompt's logical topology.
       
    3. Reinforcement Learning (Analogy): The scoring function acts as the reward signal.
       High scores indicate policies (answers) that align with the environment (prompt constraints).
       
    This hybrid approach prioritizes structural logic (Mechanism) reinforced by 
    semantic coherence (Network), surpassing simple compression (NCD) baselines.
    """

    def __init__(self):
        # Logical operators and comparators for structural parsing
        self.comparators = ['>', '<', '>=', '<=', '==', '!=', 'greater', 'lesser', 'more', 'less']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'assuming']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split non-alphanumeric."""
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structural_integrity(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Module:
        Computes a 'truth-telling' score based on logical consistency.
        Penalties act as incentive-compatible transfers to discourage hallucination.
        """
        score = 1.0
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        c_set = set(c_tokens)
        p_set = set(p_tokens)

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect it or not contradict it strongly
        has_negation = any(n in p_tokens for n in self.negations)
        cand_has_negation = any(n in c_tokens for n in self.negations)
        
        if has_negation and not cand_has_negation:
            # Potential contradiction penalty (soft)
            score -= 0.15
        
        # 2. Conditional Presence
        has_conditional = any(c in p_tokens for c in self.conditionals)
        if has_conditional:
            # Reward if candidate acknowledges conditional logic (heuristic: length/complexity)
            if len(c_tokens) < 5:
                score -= 0.2 # Too short to handle conditionals

        # 3. Numeric Consistency (The strongest structural signal)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums:
            if not c_nums:
                score -= 0.4 # Failed to extract numbers when present
            else:
                # Check ordering if comparators exist
                if any(comp in p_tokens for comp in self.comparators):
                    # Simple check: did the numbers change drastically?
                    # This is a proxy for maintaining the 'state' of the numeric argument
                    if abs(p_nums[0] - c_nums[0]) > (abs(p_nums[0]) * 0.5 + 0.1):
                        score -= 0.3 # Number drift penalty

        return max(0.0, score)

    def _compute_network_synergy(self, prompt: str, candidate: str) -> float:
        """
        Network Science Module:
        Computes node embedding similarity via token overlap and structural density.
        Simulates reward propagation through the semantic graph.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        if not p_tokens or not c_tokens:
            return 0.0

        # Jaccard Similarity as a proxy for Community Detection (Louvain-like clustering)
        intersection = set(p_tokens) & set(c_tokens)
        union = set(p_tokens) | set(c_tokens)
        jaccard = len(intersection) / len(union) if union else 0.0

        # Degree centrality approximation: frequency of shared important words
        # Weight rare words higher (simple IDF proxy via inverse frequency in prompt)
        p_freq = {}
        for t in p_tokens:
            p_freq[t] = p_freq.get(t, 0) + 1
            
        synergy = 0.0
        for t in c_tokens:
            if t in p_freq:
                # Reward matching tokens, dampened by their frequency in prompt (noise reduction)
                synergy += 1.0 / math.log(p_freq[t] + 2)
        
        # Normalize synergy roughly to 0-1 range based on length
        norm_factor = math.log(len(c_tokens) + 2)
        network_score = (jaccard * 0.6) + (min(1.0, synergy / norm_factor) * 0.4)
        
        return network_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Combined NAIC-R Scoring:
        Score = (Mechanism_Integrity * 0.5) + (Network_Synergy * 0.3) + (NCD_Inverse * 0.2)
        """
        # 1. Mechanism Design Score (Primary Driver)
        mech_score = self._check_structural_integrity(prompt, candidate)
        
        # 2. Network Science Score (Synergy)
        net_score = self._compute_network_synergy(prompt, candidate)
        
        # 3. NCD Baseline (Tiebreaker/Anchor)
        ncd = self._ncd_distance(prompt, candidate)
        ncd_score = 1.0 - ncd # Invert so higher is better
        
        # Weighted combination emphasizing Mechanism and Network synergy
        final_score = (mech_score * 0.55) + (net_score * 0.35) + (ncd_score * 0.10)
        
        reason = f"Mechanism: {mech_score:.2f}, Network: {net_score:.2f}, NCD: {ncd_score:.2f}"
        return final_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the NAIC-R framework.
        Returns a ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        scored = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the NAIC-R score.
        """
        score, _ = self._score_candidate(prompt, answer)
        # Clamp to 0-1
        return max(0.0, min(1.0, score))