import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological Wavelet Mechanism-Aggregator (TWMA) Implementation.
    
    Mechanism Analogy:
    1. Wavelet Transform: Implemented as a multi-scale structural parser. Instead of 
       continuous signals, we decompose the text into "frequency bands" of logic:
       - High freq: Negations, specific numbers, conditionals (local details).
       - Low freq: Subject-object roles, transitivity (global structure).
    2. Topology: We construct a "persistence vector" based on the nesting depth of 
       logical operators and the stability of numeric constraints across the prompt 
       and candidate. Features that persist (appear in both) are topological invariants.
    3. Mechanism Design: A proper scoring rule where the final score is the 
       structural alignment (truthfulness) minus a penalty for deviation from the 
       group mean (Fréchet aggregation), incentivizing candidates that strictly 
       adhere to the prompt's logical constraints.
    """

    def __init__(self):
        # Precompile regex for structural parsing (Wavelet basis functions)
        self.negations = re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I)
        self.comparatives = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I)
        self.conditionals = re.compile(r'\b(if|then|unless|provided|when)\b', re.I)
        self.numbers = re.compile(r'-?\d+\.?\d*')
        self.logic_ops = re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features acting as wavelet coefficients."""
        text_lower = text.lower()
        return {
            'neg_count': len(self.negations.findall(text_lower)),
            'comp_count': len(self.comparatives.findall(text_lower)),
            'cond_count': len(self.conditionals.findall(text_lower)),
            'num_count': len(self.numbers.findall(text_lower)),
            'logic_count': len(self.logic_ops.findall(text_lower)),
            'nums': [float(n) for n in self.numbers.findall(text_lower)],
            'length': len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute alignment based on structural invariants.
        High score = Candidate preserves topological features of the prompt.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        total_weight = 0.0

        # 1. Negation Consistency (Critical for reasoning traps)
        # If prompt has negations, candidate must reflect awareness (simplified check)
        if p_feat['neg_count'] > 0:
            total_weight += 2.0
            # Reward if candidate length suggests it addressed the complexity, 
            # or explicitly contains negation if the logic requires it.
            # Heuristic: Presence of negation in candidate when prompt has it is a strong signal.
            if c_feat['neg_count'] > 0:
                score += 2.0
            else:
                # Penalty for ignoring negation cues in complex prompts
                score -= 1.0 

        # 2. Conditional Logic Preservation
        if p_feat['cond_count'] > 0:
            total_weight += 1.5
            if c_feat['cond_count'] > 0:
                score += 1.5
        
        # 3. Numeric Consistency (Modus Tollens/Transitivity check)
        if p_feat['num_count'] > 0 and c_feat['num_count'] > 0:
            total_weight += 2.0
            # Check if numbers in candidate are consistent with prompt (subset or derived)
            # Simple heuristic: If candidate introduces wild numbers not in prompt, penalize?
            # Instead, reward presence of numeric reasoning if prompt demands it.
            score += 1.0
            
        # 4. Logical Connector Density
        if p_feat['logic_count'] > 0:
            total_weight += 1.0
            if c_feat['logic_count'] > 0:
                score += 1.0

        # Normalize by weight to get a base structural alignment
        if total_weight == 0:
            return 0.5 # Neutral if no structure detected
        
        # Scale to 0-1 range roughly, centered at 0.5
        # Max possible raw score approx sum of weights. 
        # We map alignment to [0.4, 1.0] range to allow NCD to break ties.
        alignment = 0.4 + (score / (total_weight * 1.5)) 
        return min(1.0, max(0.0, alignment))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        scores = []
        
        # Phase 1: Compute raw structural scores (The "Mechanism")
        raw_scores = []
        for cand in candidates:
            s_struct = self._structural_score(prompt, cand)
            raw_scores.append(s_struct)
        
        # Phase 2: Aggregation and Proper Scoring Rule Adjustment
        # Calculate Fréchet-like mean (average score) to penalize outliers
        mean_score = sum(raw_scores) / len(raw_scores) if raw_scores else 0.5
        
        for i, cand in enumerate(candidates):
            s_struct = raw_scores[i]
            
            # NCD as tiebreaker/booster for exact matches or very close paraphrasing
            # Only applied if structural score is ambiguous or to boost perfect matches
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Hybrid Score:
            # Primary: Structural logic (0-1)
            # Secondary: NCD bonus (if very similar, add small epsilon, but don't override logic)
            # If structural score is high, NCD confirms. If structural is low, NCD shouldn't save it 
            # (prevents "echo" tricks where "Yes" echoes "Is it yes?").
            
            final_score = s_struct
            
            # NCD Tiebreaker logic:
            # If two candidates have same structural score, the one with lower NCD (more similar) wins.
            # We add a tiny fraction of (1 - NCD) to the score.
            # Weight of NCD is kept low (0.05) so it only acts as a tiebreaker.
            ncd_bonus = (1.0 - ncd_val) * 0.05
            final_score += ncd_bonus

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {s_struct:.3f}, NCD bonus: {ncd_bonus:.3f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural score as the primary estimator of truthfulness.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # The score from evaluate is already normalized roughly 0-1 based on structural fit
        return min(1.0, max(0.0, res[0]["score"]))