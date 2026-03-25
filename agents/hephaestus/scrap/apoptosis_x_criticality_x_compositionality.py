import zlib
import math
import re

class ReasoningTool:
    """
    Implements a computational analogy of Apoptosis x Criticality x Compositionality.
    
    Mechanism:
    1. Compositionality: Decomposes prompt and candidates into structural tokens 
       (negations, comparatives, numbers, logic keywords) to form a "program syntax".
    2. Criticality: Computes a 'susceptibility' score based on the sensitivity of 
       the candidate's structural match to the prompt. Candidates that are too 
       generic (ordered) or too noisy (chaotic) are penalized. The system seeks 
       the 'edge of chaos' where structural overlap is significant but not trivial.
    3. Apoptosis: Prunes (scores near zero) candidates where the 'stress' signal 
       (divergence between prompt structure and candidate structure) exceeds thresholds.
       Specifically, if a candidate lacks critical logical operators found in the prompt 
       (e.g., 'not', 'greater than'), it undergoes 'apoptosis' (low score).
       
    Scoring combines structural constraint satisfaction (primary) with NCD (tiebreaker).
    """

    def __init__(self):
        # Logical keywords that trigger high-stakes evaluation (Criticality markers)
        self.logic_ops = ['not', 'no', 'never', 'without', 'except', 'false', 'wrong']
        self.comparators = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.all_markers = self.logic_ops + self.comparators + self.conditionals

    def _tokenize_structure(self, text):
        """Extracts structural/compositional primitives from text."""
        t = text.lower()
        tokens = set()
        # Extract logical markers
        for op in self.all_markers:
            if re.search(r'\b' + op + r'\b', t):
                tokens.add(op)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', t)
        for n in nums:
            tokens.add(f"NUM:{n}")
            
        # Basic subject-object role hint (very simplified)
        if re.search(r'\b(a|an|the)\s+\w+', t):
            tokens.add("DET_PRESENT")
            
        return tokens

    def _compute_ncd(self, s1, s2):
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _compute_stress_signal(self, prompt_tokens, cand_tokens):
        """
        Computes a stress signal based on missing critical components.
        High stress = missing logical negation or comparator present in prompt.
        This drives the 'Apoptosis' mechanism.
        """
        stress = 0.0
        total_critical = 0
        
        # Check for presence of critical logic in prompt
        prompt_logic = prompt_tokens.intersection(set(self.all_markers))
        
        if len(prompt_logic) == 0:
            return 0.0 # No specific logical constraints to violate
            
        for op in prompt_logic:
            total_critical += 1
            if op not in cand_tokens:
                # Missing a critical logical operator increases stress
                stress += 1.0
                
        return stress / max(1, total_critical)

    def _compute_susceptibility(self, prompt, candidate):
        """
        Estimates susceptibility (criticality) by measuring how much the 
        structural overlap changes with a small perturbation (simulated by 
        comparing strict token overlap vs NCD similarity).
        We want candidates that are structurally aligned but not identical copies.
        """
        p_tokens = self._tokenize_structure(prompt)
        c_tokens = self._tokenize_structure(candidate)
        
        if not p_tokens:
            return 0.5
            
        # Jaccard similarity of structural tokens
        intersection = len(p_tokens.intersection(c_tokens))
        union = len(p_tokens.union(c_tokens))
        struct_sim = intersection / max(1, union)
        
        # NCD similarity (1 - distance)
        ncd_dist = self._compute_ncd(prompt, candidate)
        
        # Susceptibility is high when structural match is moderate (edge of chaos)
        # and low when it's trivial (0 or 1). 
        # We model this as a deviation from the mean expected random overlap.
        # Ideally, struct_sim should be high, but ncd_dist should not be 0 (copying).
        
        # Criticality score: High if structurally relevant (high struct_sim) 
        # but distinct enough to be a reasoned answer (ncd_dist > 0).
        if struct_sim == 0:
            return 0.0
            
        # Penalty for exact copying (ncd ~ 0) unless the prompt is trivial
        if ncd_dist < 0.01 and len(prompt) > 10:
            return 0.2 # Low criticality for copying
            
        return struct_sim * (1.0 - math.exp(-5 * ncd_dist))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_tokens = self._tokenize_structure(prompt)
        
        for cand in candidates:
            cand_tokens = self._tokenize_structure(cand)
            
            # 1. Apoptosis Gate: Check stress (missing critical logic)
            stress = self._compute_stress_signal(prompt_tokens, cand_tokens)
            
            # Caspase-like gating: If stress is too high (>0.5), the unit dies (score ~0)
            # Sigma function approximation: gate = 1 / (1 + exp(alpha * (stress - theta)))
            # Let theta = 0.5, alpha = 10
            gate = 1.0 / (1.0 + math.exp(10.0 * (stress - 0.5)))
            
            if gate < 0.1:
                # Unit undergoes apoptosis
                score = 0.0
                reasoning = "Apoptosis triggered: Critical logical constraint missing."
            else:
                # 2. Criticality & Compositionality Scoring
                susceptibility = self._compute_susceptibility(prompt, cand)
                ncd = self._compute_ncd(prompt, cand)
                
                # Base score from structural alignment and criticality
                # Prefer high susceptibility (reasoned) and low NCD (relevant)
                base_score = susceptibility * 0.7 + (1.0 - ncd) * 0.3
                
                # Boost if numbers match exactly (Numeric evaluation pattern)
                p_nums = [t for t in prompt_tokens if t.startswith("NUM:")]
                c_nums = [t for t in cand_tokens if t.startswith("NUM:")]
                num_bonus = 0.0
                if p_nums and c_nums:
                    if set(p_nums) == set(c_nums):
                        num_bonus = 0.2
                    elif any(n in c_nums for n in p_nums):
                        num_bonus = 0.1
                
                score = min(1.0, base_score + num_bonus)
                reasoning = f"Criticality={susceptibility:.2f}, Stress={stress:.2f}, Gate={gate:.2f}"

            results.append({
                "candidate": cand,
                "score": round(score, 6),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against the prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        return res_list[0]["score"]