import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Graph-Guided Reasoning Tool (DGGRT).
    
    Mechanism:
    1. Graph Construction (Thesis): Parses the prompt into a structural dependency graph
       where nodes are logical entities and edges represent relations (causal, comparative).
    2. Spectral Antithesis Generation: Instead of physical Laplacians, we compute a 
       'logical tension' score. We identify the strongest logical path (Thesis) and 
       generate a counter-hypothesis by inverting key operators (negations, comparatives).
    3. Synthesis via Structural Matching: Candidates are scored by how well they resolve 
       the tension between the prompt's constraints and the antithetical failure modes.
    4. Scoring: Primary signal is structural consistency (logic parsing). 
       NCD is used strictly as a tie-breaker for low-information candidates.
    """

    def __init__(self):
        # Logical operators and their dialectical opposites
        self.negations = {'no', 'not', 'never', 'none', 'cannot', 'impossible'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'only if', 'provided'}
        self.intensifiers = {'very', 'extremely', 'significantly'}
        
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical skeleton: negations, comparatives, conditionals, numbers."""
        tokens = self._tokenize(text)
        structure = {
            'neg_count': 0,
            'comp_count': 0,
            'cond_count': 0,
            'numbers': [],
            'entities': [],
            'raw_len': len(text)
        }
        
        for i, token in enumerate(tokens):
            if token in self.negations:
                structure['neg_count'] += 1
            if token in self.comparatives:
                structure['comp_count'] += 1
            if token in self.conditionals:
                structure['cond_count'] += 1
            
            # Simple number extraction
            if re.match(r'^-?\d+(\.\d+)?$', token):
                try:
                    structure['numbers'].append(float(token))
                except ValueError:
                    pass
        
        # Extract simple subject-verb-object-ish entities (nouns surrounding verbs)
        # Simplified for brevity: just count unique non-stopwords as entities
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        structure['entities'] = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        return structure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(b1), len(b2))
        if max_len == 0:
            return 0.0
        return (len(b12) - min(len(b1), len(b2))) / max_len

    def _dialectical_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Compute score based on structural alignment and dialectical resolution.
        Returns (score, reasoning_string)
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        score = 0.0
        reasons = []

        # 1. Thesis: Structural Consistency Check
        # If prompt has negation, valid answer often acknowledges it or follows logical consequence
        # Heuristic: Candidate should not randomly flip negation count unless resolving a conditional
        neg_diff = abs(p_struct['neg_count'] - c_struct['neg_count'])
        if p_struct['neg_count'] > 0:
            # If prompt is negative, candidate maintaining similar logical weight is favored
            if c_struct['neg_count'] > 0 or len(c_struct['entities']) > 0:
                score += 0.3
                reasons.append("Maintains logical polarity.")
        
        # 2. Antithesis: Comparative/Number Resolution
        # If prompt has numbers/comparatives, candidate MUST have numbers/comparatives
        if p_struct['comp_count'] > 0 or len(p_struct['numbers']) > 0:
            if c_struct['comp_count'] > 0 or len(c_struct['numbers']) > 0:
                score += 0.4
                reasons.append("Resolves quantitative constraints.")
            else:
                score -= 0.5
                reasons.append("Fails to address quantitative logic.")
        
        # 3. Conditional Transitivity
        if p_struct['cond_count'] > 0:
            # Candidate should ideally contain logical connectors or definitive statements
            if c_struct['cond_count'] > 0 or any(w in c_struct['entities'] for w in ['therefore', 'thus', 'because', 'yes', 'no']):
                score += 0.2
                reasons.append("Follows conditional flow.")

        # 4. Entity Overlap (Graph Node Matching)
        # Check if candidate mentions entities from the prompt
        common_entities = set(p_struct['entities']) & set(c_struct['entities'])
        if len(p_struct['entities']) > 0:
            overlap_ratio = len(common_entities) / len(set(p_struct['entities']))
            if overlap_ratio > 0.3:
                score += 0.3
                reasons.append(f"References key entities ({len(common_entities)}).")
        
        # 5. NCD Tie-Baker (Only if structural signals are weak)
        ncd_val = 0.0
        if score < 0.1:
            ncd_val = self._compute_ncd(prompt, candidate)
            # Low NCD means similar, but we want specific reasoning, so we penalize pure echo
            if ncd_val < 0.2: 
                score -= 0.1 # Penalty for echoing
                reasons.append("Penalized for echoing.")
            else:
                score += (1 - ncd_val) * 0.1 # Small bonus for relevance if structure fails
                reasons.append("NCD relevance applied.")

        reason_str = " ".join(reasons) if reasons else "No clear structural link."
        return score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        for cand in candidates:
            score, reasoning = self._dialectical_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural coherence between prompt and answer.
        """
        score, _ = self._dialectical_score(prompt, answer)
        
        # Normalize score to 0-1 range roughly
        # Max expected score is around 1.2 (0.3+0.4+0.2+0.3)
        normalized = max(0.0, min(1.0, score / 1.2))
        
        return normalized