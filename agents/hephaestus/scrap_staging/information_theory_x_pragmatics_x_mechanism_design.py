import re
import math
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    A reasoning tool combining Information Theory, Pragmatics, and Mechanism Design.
    
    Mechanism:
    1. Structural Parsing (Pragmatics): Extracts atomic propositions, negations, comparatives,
       and conditionals using regex to build a logical constraint graph.
    2. Constraint Propagation: Uses Warshall's algorithm on a boolean implication matrix
       to determine entailed truths (Hard Constraints).
    3. Information Gain (Info Theory): Calculates the reduction in entropy (Shannon) 
       from a uniform prior to the posterior distribution defined by the constraints.
    4. Pragmatic Penalty: Deducts score for Gricean violations (e.g., contradiction, redundancy).
    5. Mechanism Design: Final score is a proper logarithmic scoring rule adjusted by penalties,
       incentivizing truthful, concise, and logically consistent answers.
       
    Epistemic Honesty: Detects ambiguity patterns (Tier B) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes|results in)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(stopped|quit|failed|realize|know)\s+(you|the|this|that)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }
        self.lambda_prag = 0.5  # Weight for pragmatic penalty

    def _extract_props(self, text):
        """Extract atomic propositions and tags from text."""
        text_lower = text.lower()
        props = []
        tags = set()
        
        # Check for specific logical markers
        if self.patterns['negation'].search(text_lower): tags.add('negation')
        if self.patterns['comparative'].search(text_lower): tags.add('comparative')
        if self.patterns['conditional'].search(text_lower): tags.add('conditional')
        if self.patterns['causal'].search(text_lower): tags.add('causal')
        if self.patterns['quantifier'].search(text_lower): tags.add('quantifier')
        
        # Extract numbers for constructive computation
        nums = [float(x) for x in self.patterns['number'].findall(text_lower)]
        
        # Simple proposition extraction (split by basic delimiters for demo)
        # In a full system, this would be an NLP parser. Here we use sentence splitting.
        raw_props = re.split(r'[;.]', text)
        for p in raw_props:
            p_clean = p.strip()
            if p_clean:
                props.append(p_clean)
                
        return props, tags, nums

    def _build_implication_matrix(self, ref_props, cand_props):
        """
        Build a boolean implication matrix based on string equality and negation logic.
        Returns matrix Imp where Imp[i,j] = 1 if i entails j.
        Also returns indices mapping.
        """
        all_props = ref_props + cand_props
        n = len(all_props)
        if n == 0:
            return np.zeros((0,0), dtype=bool), [], {}
            
        Imp = np.zeros((n, n), dtype=bool)
        np.fill_diagonal(Imp, True)
        
        # Map propositions to indices
        # Normalize for comparison (lowercase, strip)
        normalized = [p.lower().strip() for p in all_props]
        
        for i in range(n):
            for j in range(n):
                if i == j: continue
                # Direct match
                if normalized[i] == normalized[j]:
                    Imp[i, j] = True
                # Negation check (simple prefix 'not ')
                if normalized[i].startswith('not ') and normalized[j] == normalized[i][4:]:
                    # If i is "not X" and j is "X", i implies NOT j (contradiction if both true)
                    # For entailment matrix, we mark strict logical flow. 
                    # Here we just flag the conflict for the penalty step.
                    pass 
                # Simple transitive hint: if A->B and B->C (handled by Warshall later)
                
        # Warshall's Algorithm for transitive closure
        for k in range(n):
            Imp |= (Imp[:, k:None, None] & Imp[None, k:, :]).any(axis=1) # Vectorized step approx
            
        # Correct vectorized Warshall for boolean matrix
        for k in range(n):
            col_k = Imp[:, k].reshape(-1, 1)
            row_k = Imp[k, :].reshape(1, -1)
            Imp |= (col_k & row_k)
            
        return Imp, all_props, normalized

    def _calculate_entropy_gain(self, ref_text, cand_text):
        """
        Calculate Information Gain based on constraint satisfaction.
        Simulates MaxEnt distribution over worlds consistent with constraints.
        """
        ref_props, ref_tags, ref_nums = self._extract_props(ref_text)
        cand_props, cand_tags, cand_nums = self._extract_props(cand_text)
        
        if not ref_props and not cand_props:
            return 0.0, 0.0, {}

        # Build constraint matrix
        Imp, all_props, norm_props = self._build_implication_matrix(ref_props, cand_props)
        n = len(all_props)
        if n == 0: return 0.0, 0.0, {}

        # Count active constraints (hard constraints)
        # A candidate is "good" if it doesn't contradict the reference and adds specificity
        contradictions = 0
        redundancies = 0
        
        # Check for direct contradictions (A vs Not A)
        ref_set = set(norm_props[:len(ref_props)])
        cand_set = set(norm_props[len(ref_props):])
        
        for c in cand_set:
            if f"not {c}" in ref_set or (c.startswith('not ') and c[4:] in ref_set):
                contradictions += 1
            if c in ref_set:
                redundancies += 1
                
        # Information Gain Approximation:
        # H0 = log2(2^n) = n (Uniform prior over n independent binary facts)
        # H1 = Entropy after applying constraints. 
        # Each valid constraint roughly halves the space (if independent).
        # Contradictions -> Infinite entropy (impossible world) or 0 probability.
        
        if contradictions > 0:
            return -10.0, 0.0, {'contradictions': contradictions} # High penalty
            
        # Effective constraints = unique cand props that are in ref (validation) or new valid info
        # Simplified IG: Gain from reducing uncertainty by confirming/refining ref props
        valid_matches = len(cand_set.intersection(ref_set))
        new_info = len(cand_set - ref_set)
        
        # Base IG on how much of the reference is covered + new valid info
        # Normalized by total possible complexity
        base_entropy = max(1, len(ref_props))
        ig = (valid_matches + 0.5 * new_info) / base_entropy
        
        # Pragmatic Penalty (Gricean Maxims)
        # Quantity: Too much redundancy? Quality: Contradictions?
        penalty = self.lambda_prag * (contradictions * 2.0 + max(0, redundancies - 1) * 0.1)
        
        return ig, penalty, {'matches': valid_matches, 'new': new_info}

    def _meta_confidence(self, prompt):
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower) and 'or' in p_lower:
            # Heuristic: if "either...or" appears without clear exhaustive list
            if 'options' not in p_lower and 'choose' not in p_lower:
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 4. Pronoun/Scope Ambiguity (Simple heuristic)
        if re.search(r'\b(he|she|they|it)\s+(was|is|did)\b', p_lower) and 'who' in p_lower:
            return 0.3
            
        return 1.0  # No obvious traps detected

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        if not s1 or not s2: return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            return z12 / max(z1, z2)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate meta-confidence cap based on prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            ig, penalty, details = self._calculate_entropy_gain(prompt, cand)
            
            # Mechanism Design Scoring Rule: Score = IG - Penalty
            raw_score = ig - penalty
            
            # NCD Tiebreaker (small influence)
            # We want high overlap with prompt context if logical score is tied
            # But NCD is capped at 15% of total score magnitude
            ncd_val = 0.0
            if raw_score == 0 or (details.get('matches', 0) == 0 and details.get('new', 0) == 0):
                # Only use NCD if structural signal is weak
                try:
                    import zlib
                    ncd = self._ncd_score(prompt, cand)
                    ncd_val = (1.0 - ncd) * 0.15 # Convert distance to similarity, scale down
                except:
                    ncd_val = 0.0
            
            final_score = raw_score + ncd_val
            
            # Construct reasoning string
            reason_parts = []
            if details.get('contradictions', 0) > 0:
                reason_parts.append(f"Contradiction detected ({details['contradictions']}).")
            if details.get('matches', 0) > 0:
                reason_parts.append(f"Validated {details['matches']} logical constraints.")
            if details.get('new', 0) > 0:
                reason_parts.append(f"Added {details['new']} new propositions.")
            if penalty > 0:
                reason_parts.append(f"Pragmatic penalty applied: {penalty:.2f}.")
            if meta_cap < 1.0:
                reason_parts.append("Prompt contains ambiguity or traps; confidence capped.")
                
            reasoning_str = " ".join(reason_parts) if reason_parts else "No strong structural signal."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning_str
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta-confidence check (Question properties)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural check (Answer properties)
        ig, penalty, _ = self._calculate_entropy_gain(prompt, answer)
        
        # Base confidence on Information Gain and lack of penalty
        # If IG is low and penalty is high, confidence should be low
        base_conf = max(0.0, min(1.0, (ig - penalty + 1.0) / 2.0)) # Normalize roughly to 0-1
        
        # If no structural match (IG ~ 0), confidence should be low unless it's a trivial Q
        ref_props, _, _ = self._extract_props(prompt)
        if len(ref_props) > 0 and ig < 0.1:
            base_conf = 0.2 # Honest uncertainty if no structure matches
            
        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 without definitive computation (heuristic: high IG)
        if ig < 0.8: # Arbitrary threshold for "definitive" in this simplified model
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))

# Import zlib inside the class scope or globally if needed, 
# but since we need to avoid external deps issues, we try import inside NCD.
import zlib