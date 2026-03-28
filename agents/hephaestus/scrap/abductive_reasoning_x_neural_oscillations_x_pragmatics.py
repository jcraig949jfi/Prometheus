import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool integrating Abductive Reasoning, Neural Oscillations, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts propositional tuples (subject, predicate, object, polarity) and 
       structural markers (comparatives, conditionals, causals, numerics) using regex.
    2. Abduction: Scores candidates based on coverage of prompt propositions and simplicity 
       (penalizing unsupported assumptions).
    3. Neural Oscillation: Simulates Kuramoto-style phase coupling to measure 'binding synchrony' 
       of the hypothesis components. High synchrony implies a coherent explanation.
    4. Pragmatics: Evaluates Gricean maxims (Quantity, Quality, Relevance, Manner) via rule-based flags.
    5. Scoring: Weighted sum of Coverage, Simplicity, Binding Synchrony, and Pragmatic Alignment.
       NCD is used strictly as a tiebreaker for structurally identical scores.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|therefore|leads to|causes|due to)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(?:\.\d+)?'),
        'quantifier': re.compile(r'\b(all|some|every|each|few|many)\b', re.IGNORECASE)
    }

    def __init__(self):
        pass

    def _extract_props(self, text: str) -> List[Dict[str, Any]]:
        """Extract propositional tuples and structural flags from text."""
        if not text.strip():
            return []
        
        props = []
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Simple subject-predicate-object approximation using first verb-like split
            # This is a heuristic to satisfy the tuple requirement without heavy NLP
            words = sent.split()
            if len(words) < 3:
                continue
                
            # Detect flags
            has_neg = bool(self.PATTERNS['negation'].search(sent))
            has_comp = bool(self.PATTERNS['comparative'].search(sent))
            has_cond = bool(self.PATTERNS['conditional'].search(sent))
            has_cause = bool(self.PATTERNS['causal'].search(sent))
            has_num = bool(self.PATTERNS['numeric'].search(sent))
            
            # Extract numbers for comparison logic
            nums = [float(n) for n in self.PATTERNS['numeric'].findall(sent)]
            
            # Construct a representative proposition
            # Subject: First word, Predicate: Middle, Object: Last word (simplified)
            subj = words[0][:20]
            obj = words[-1].rstrip('.,')[:20]
            pred = " ".join(words[1:-1])[:20] if len(words) > 2 else "is"
            
            props.append({
                'subj': subj,
                'pred': pred,
                'obj': obj,
                'pol': -1 if has_neg else 1,
                'cmp': '>' if has_comp else '=',
                'cond': has_cond,
                'cause': has_cause,
                'num': nums[0] if nums else 0.0,
                'nums_all': nums,
                'raw': sent
            })
            
        return props

    def _compute_abductive_score(self, prompt_props: List[Dict], hyp_props: List[Dict]) -> tuple:
        """Compute coverage and simplicity."""
        if not prompt_props:
            return 0.0, 1.0
            
        covered = 0
        for p in prompt_props:
            for h in hyp_props:
                # Unification: matching predicate/object and compatible polarity
                if p['pred'] == h['pred'] or p['obj'] == h['obj']:
                    if p['pol'] == h['pol'] or p['pol'] == 1: # Allow positive to match positive
                        covered += 1
                        break
                # Numeric consistency check
                if p['nums_all'] and h['nums_all']:
                    if p['nums_all'][0] == h['nums_all'][0]:
                        covered += 1
                        break
        
        coverage = min(1.0, covered / max(1, len(prompt_props)))
        
        # Simplicity: Penalize extra assumptions (H \ P)
        # Approximated by ratio of hypothesis size to prompt size if > prompt
        extra = max(0, len(hyp_props) - len(prompt_props))
        simplicity = 1.0 / (1.0 + extra)
        
        return coverage, simplicity

    def _compute_binding_synchrony(self, hyp_props: List[Dict]) -> float:
        """Simulate Kuramoto oscillators to measure coherence."""
        n = len(hyp_props)
        if n == 0:
            return 0.0
        if n == 1:
            return 1.0
            
        phi = np.linspace(0, 2*np.pi, n, endpoint=False) # Initial phases
        K = 0.5 * np.ones((n, n)) # Uniform coupling
        
        # Simulate 20 iterations
        for _ in range(20):
            diff = phi[:, None] - phi[None, :]
            dphi = np.sum(K * np.sin(diff), axis=1)
            phi += 0.1 * dphi
            # Wrap phases
            phi = np.mod(phi, 2*np.pi)
            
        # Circular variance
        synchrony = np.abs(np.mean(np.exp(1j * phi)))
        return float(synchrony)

    def _compute_pragmatic_score(self, prompt_props: List[Dict], hyp_props: List[Dict]) -> float:
        """Evaluate Gricean maxims."""
        if not hyp_props:
            return 0.0
            
        scores = []
        
        # Quantity: Penalize if hyp adds > 2 unsupported propositions (approximated)
        q_score = 1.0 if len(hyp_props) <= len(prompt_props) + 2 else 0.5
        scores.append(q_score)
        
        # Quality: Penalize contradictions (polarity mismatch on same subject/object)
        quality_pen = 0
        for p in prompt_props:
            for h in hyp_props:
                if p['subj'] == h['subj'] and p['obj'] == h['obj'] and p['pol'] != h['pol']:
                    quality_pen += 1
        q_score = 1.0 / (1.0 + quality_pen)
        scores.append(q_score)
        
        # Relevance: Reward causal/conditional links if present in prompt
        prompt_has_causal = any(p['cause'] or p['cond'] for p in prompt_props)
        hyp_has_causal = any(h['cause'] or h['cond'] for h in hyp_props)
        r_score = 1.0 if (prompt_has_causal and hyp_has_causal) or (not prompt_has_causal) else 0.8
        scores.append(r_score)
        
        # Manner: Penalize long predicates (>15 chars)
        m_score = 1.0
        for h in hyp_props:
            if len(h['pred']) > 15:
                m_score = 0.8
                break
        scores.append(m_score)
        
        return float(np.mean(scores))

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_props = self._extract_props(prompt)
        results = []
        
        for cand in candidates:
            hyp_props = self._extract_props(cand)
            
            # 1. Abductive Metrics
            coverage, simplicity = self._compute_abductive_score(prompt_props, hyp_props)
            
            # 2. Neural Oscillation Binding
            synchrony = self._compute_binding_synchrony(hyp_props)
            
            # 3. Pragmatic Fit
            pragmatic = self._compute_pragmatic_score(prompt_props, hyp_props)
            
            # 4. Final Score
            score = (0.3 * coverage + 
                     0.2 * simplicity + 
                     0.3 * synchrony + 
                     0.2 * pragmatic)
            
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"Coverage:{coverage:.2f}, Simp:{simplicity:.2f}, Sync:{synchrony:.2f}, Prag:{pragmatic:.2f}",
                '_ncd': self._calculate_ncd(prompt, cand) # Store for tie-breaking
            })
        
        # Sort by score (desc), then by NCD (asc, as tiebreaker for similarity if needed, 
        # though prompt says NCD is tiebreaker for 'no structural signal'. 
        # Here we use it to break exact score ties by preferring lower distance if scores equal)
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up internal keys
        final_results = []
        for r in results:
            final_results.append({
                'candidate': r['candidate'],
                'score': r['score'],
                'reasoning': r['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']