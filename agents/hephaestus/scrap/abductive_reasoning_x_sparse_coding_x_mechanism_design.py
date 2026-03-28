import re
import zlib
import math

class ReasoningTool:
    """
    Sparse Abductive Mechanism (SAM) Implementation.
    
    Mechanism:
    1. Abductive/Sparse Core (Structural Parsing): Instead of heavy L1 optimization,
       we perform 'sparse coding' by extracting only high-signal structural tokens
       (negations, comparatives, conditionals, numbers). This creates a compact
       hypothesis representation (z) of the prompt's logical constraints.
    2. Mechanism Design (VCG Auction): Candidates act as bidders.
       - Private Value (Bid): Structural match score (how well the candidate satisfies
         the extracted logical constraints).
       - Allocation: The candidate with the highest bid wins.
       - Payment (Externality): The winner's final score is adjusted by the gap to the
         runner-up (simulating the VCG payment), penalizing low-confidence wins and
         rewarding clear dominance.
    3. Confidence: Uses the same structural parser to verify if an answer logically
       entails the prompt's constraints, returning a calibrated 0-1 float.
       
    This approach prioritizes Mechanism Design for evaluation (as requested by causal
    analysis) while using Sparse Coding strictly for feature extraction to avoid
    historical failure modes associated with direct sparse scoring.
    """

    def __init__(self):
        # Structural keywords for sparse coding (hypothesis generation)
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self.booleans = {'yes', 'no', 'true', 'false'}
        
        # Regex patterns
        self.num_pattern = re.compile(r"-?\d+\.?\d*")
        self.word_pattern = re.compile(r"\b\w+\b")

    def _extract_features(self, text: str) -> dict:
        """Sparse coding step: Extract structural features only."""
        text_lower = text.lower()
        words = set(self.word_pattern.findall(text_lower))
        
        # 1. Logical Operators (Sparse presence)
        has_negation = bool(words & self.negations)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        
        # 2. Numeric Extraction
        numbers = [float(n) for n in self.num_pattern.findall(text)]
        
        # 3. Boolean presence
        has_boolean = bool(words & self.booleans)

        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': numbers,
            'bool': has_boolean,
            'len': len(text)
        }

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'bid' based on structural alignment.
        Higher score = better abductive fit to logical constraints.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 0.0
        
        # Constraint 1: Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or not contradict it
        if p_feat['neg']:
            score += 2.0 if c_feat['neg'] else 0.5 # Reward matching negation depth
        else:
            score += 1.0 if not c_feat['neg'] else -1.0 # Penalize unnecessary negation

        # Constraint 2: Comparative Logic
        if p_feat['comp']:
            # If prompt compares, candidate should ideally contain comparative words or numbers
            if c_feat['comp'] or c_feat['nums']:
                score += 2.0
            else:
                score -= 1.0
        
        # Constraint 3: Conditional Logic
        if p_feat['cond']:
            # Reward candidates that acknowledge conditions (often via length or specific keywords)
            if c_feat['cond'] or c_feat['len'] > 10: # Heuristic: conditionals usually need length
                score += 1.5
            else:
                score += 0.5

        # Constraint 4: Numeric Consistency
        if p_feat['nums'] and c_feat['nums']:
            # Simple check: if prompt has numbers, candidate having numbers is good (contextual)
            score += 1.0
            # Check magnitude alignment (heuristic: similar order of magnitude or exact match)
            p_max = max(p_feat['nums']) if p_feat['nums'] else 0
            c_max = max(c_feat['nums']) if c_feat['nums'] else 0
            if p_max == c_max:
                score += 3.0 # Exact number match is strong evidence
            elif p_max > 0 and abs(p_max - c_max) / p_max < 0.1:
                score += 1.5 # Close enough

        # Constraint 5: Boolean Directness
        if p_feat['bool']:
            if c_feat['bool']:
                score += 2.0
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # Step 1: Generate Bids (Structural Scores)
        bids = []
        for i, cand in enumerate(candidates):
            bid_value = self._compute_structural_score(prompt, cand)
            bids.append({'index': i, 'bid': bid_value, 'candidate': cand})
        
        # Sort by bid descending (Mechanism Design: Allocation Rule)
        bids.sort(key=lambda x: x['bid'], reverse=True)
        
        results = []
        n = len(bids)
        
        for i, item in enumerate(bids):
            idx = item['index']
            raw_score = item['bid']
            
            # Step 2: VCG Payment Calculation (Externality)
            # The "payment" is the loss imposed on others. 
            # In this single-item auction, the winner pays the bid of the runner-up.
            # We use this to adjust the score: 
            # Final Score = Raw Bid - (Winner Bid - RunnerUp Bid) if Winner, else Raw Bid
            # Simplified for ranking: We want the gap to matter.
            # Let's define Utility = Bid - Payment. 
            # If i is winner (i==0): Payment = bids[1].bid (if exists else 0). 
            # Utility = bids[0].bid - (bids[0].bid - bids[1].bid) = bids[1].bid? 
            # No, standard VCG: Winner pays second highest. 
            # Here we use the gap as a confidence booster/penalty.
            
            if i == 0 and n > 1:
                # Winner gets a bonus proportional to the gap over the runner-up
                runner_up_bid = bids[1]['bid']
                gap = raw_score - runner_up_bid
                # Scale gap: large gap = high confidence, small gap = low confidence
                # Base score + gap penalty/bonus
                final_score = raw_score + (gap * 0.5) 
            elif i == 0 and n == 1:
                final_score = raw_score + 1.0 # Solo winner bonus
            else:
                # Losers: Score is just their raw bid (they pay nothing in VCG if not winning, 
                # but here we rank all. We penalize those far from winner slightly)
                final_score = raw_score - (bids[0]['bid'] - raw_score) * 0.1

            # Step 3: NCD Tiebreaker
            # Only apply if structural scores are very close (within 0.1)
            tie_breaker = 0.0
            if n > 1 and abs(final_score - bids[1]['bid']) < 0.1 if i == 0 else False:
                # If winner is tied with runner up, use NCD against prompt
                ncd_val = self._ncd(prompt, item['candidate'])
                tie_breaker = (1.0 - ncd_val) * 0.05 # Small boost for similarity
            
            final_score += tie_breaker

            results.append({
                "candidate": item['candidate'],
                "score": round(final_score, 4),
                "reasoning": f"Structural match: {raw_score:.2f}, VCG adjustment applied."
            })
            
        # Re-sort based on final adjusted scores just in case tie-breakers shifted order
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural entailment.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        conf = 0.5 # Base uncertainty
        
        # Check Negation consistency
        if p_feat['neg'] == a_feat['neg']:
            conf += 0.2
        else:
            conf -= 0.3
            
        # Check Number consistency
        if p_feat['nums'] and a_feat['nums']:
            if set(p_feat['nums']) == set(a_feat['nums']):
                conf += 0.4
            elif max(p_feat['nums']) == max(a_feat['nums']):
                conf += 0.2
        elif not p_feat['nums'] and not a_feat['nums']:
            conf += 0.1 # Neutral match
            
        # Check Boolean consistency
        if p_feat['bool'] and a_feat['bool']:
            conf += 0.2
            
        # Structural length heuristic (answers shouldn't be empty if prompt is complex)
        if p_feat['len'] > 20 and a_feat['len'] < 2:
            conf -= 0.3
            
        return max(0.0, min(1.0, conf))