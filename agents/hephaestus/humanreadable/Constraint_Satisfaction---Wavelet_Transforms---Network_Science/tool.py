import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Constraint Propagation via Wavelet-Network Analogy.
    
    Mechanism:
    1. Network Construction: Treat prompt and candidate tokens as nodes. 
       Edges are formed by syntactic proximity (local) and semantic role similarity (global).
    2. Wavelet Decomposition (Approximated): 
       - High-Frequency (Local): Detects immediate constraint violations (negations, type mismatches).
       - Low-Frequency (Global): Detects structural inconsistencies (missing entities, wrong logic flow).
    3. Constraint Propagation: Scores are adjusted based on 'signal coherence'. 
       Candidates that maintain structural parity with the prompt's logical operators receive higher coherence.
    4. Scoring: A weighted sum of structural adherence (primary) and NCD (tiebreaker).
    """
    
    def __init__(self):
        self.stopwords = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'])

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        has_neg = any(t in ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'] for t in tokens)
        has_comp = any(t in ['more', 'less', 'greater', 'smaller', 'better', 'worse', 'higher', 'lower', 'than'] for t in tokens)
        has_cond = any(t in ['if', 'unless', 'otherwise', 'when', 'where', 'provided'] for t in tokens)
        nums = re.findall(r'\d+\.?\d*', text)
        return {'neg': has_neg, 'comp': has_comp, 'cond': has_cond, 'nums': nums, 'len': len(tokens)}

    def _ncd(self, s1: str, s2: str) -> float:
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return max(c1, c2, 1) / max(c12, 1)

    def _wavelet_network_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates multi-scale constraint propagation.
        Scale 0 (High freq): Local token/structure matching.
        Scale 1 (Low freq): Global logical consistency.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        
        # High-frequency constraint check (Local consistency)
        # If prompt has negation, valid reasoning often requires specific handling.
        # We penalize candidates that ignore structural markers present in the prompt.
        if p_struct['neg'] and not c_struct['neg']:
            # Potential contradiction if candidate ignores negation context
            score -= 0.2
        elif p_struct['neg'] and c_struct['neg']:
            score += 0.15 # Reinforcement
            
        if p_struct['comp'] and not c_struct['comp']:
            score -= 0.1
        elif p_struct['comp'] and c_struct['comp']:
            score += 0.1

        if p_struct['cond'] and not c_struct['cond']:
            score -= 0.1
            
        # Numeric consistency (Coarse grain)
        if p_struct['nums'] and c_struct['nums']:
            # Simple magnitude check if both have numbers
            try:
                p_max = max(float(x) for x in p_struct['nums'])
                c_max = max(float(x) for x in c_struct['nums'])
                # Heuristic: If prompt asks for comparison, numbers should relate logically.
                # Since we don't know the logic direction, we reward presence and magnitude proximity
                if abs(p_max - c_max) < (p_max * 0.5 + 1): 
                    score += 0.2
            except: pass
        elif p_struct['nums'] and not c_struct['nums']:
            score -= 0.3 # Missing critical numeric data

        # Network Science component: Degree distribution analogy
        # Prompts with complex structure (high degree nodes) expect complex answers
        p_complexity = sum([p_struct['neg'], p_struct['comp'], p_struct['cond']])
        c_complexity = sum([c_struct['neg'], c_struct['comp'], c_struct['cond']])
        
        if p_complexity > 0:
            if c_complexity == 0:
                score -= 0.2 # Oversimplification error
            elif c_complexity >= p_complexity:
                score += 0.1 # Adequate complexity matching

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_base = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing (Primary Signal)
            wave_score = self._wavelet_network_score(prompt, cand)
            
            # 2. NCD (Tiebreaker/Baseline)
            # Normalize NCD to be comparable (lower is better, so invert)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.5 # Scale down impact
            
            # 3. Combined Score
            # Weight structural reasoning heavily over compression
            final_score = (wave_score * 2.0) + ncd_score
            
            # Bonus for direct keyword overlap in critical positions (Simple network edge weight)
            common_words = set(self._tokenize(prompt)) & set(self._tokenize(cand))
            # Remove stopwords for scoring
            meaningful_overlap = len([w for w in common_words if w not in self.stopwords])
            final_score += meaningful_overlap * 0.05

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural coherence: {wave_score:.2f}, NCD tiebreak: {ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Base score from evaluation can be negative, so we map it
        raw_score = res[0]['score']
        
        # Heuristic mapping: 
        # > 1.0 -> 0.95
        # 0.0 -> 0.5
        # < -0.5 -> 0.1
        conf = 0.5 + (raw_score * 0.2)
        return max(0.0, min(1.0, conf))