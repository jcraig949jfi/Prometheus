from typing import Dict, Tuple

"""
Phenomenological-Metacognitive-Network Consistency Scorer (PMNCS)

Combines belief network propagation with structural parsing and metacognitive
uncertainty monitoring. Extracts propositions, builds a confidence-weighted
graph, propagates beliefs, and scores candidates by network consistency.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.k_rounds = 5  # belief propagation rounds
        self.lambda_penalty = 1.0
        self.damping = 0.3
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by network consistency + structural parsing."""
        results = []
        for cand in candidates:
            struct_score = self._structural_score(prompt, cand)
            net_score = self._network_score(prompt, cand)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weight: 60% structural, 25% network, 15% NCD
            final = 0.6 * struct_score + 0.25 * net_score + 0.15 * ncd_score
            
            reasoning = f"Struct:{struct_score:.2f} Net:{net_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        struct_score = self._structural_score(prompt, answer)
        net_score = self._network_score(prompt, answer)
        
        # High confidence only if both agree and structural parsing succeeded
        base_conf = 0.5 * struct_score + 0.5 * net_score
        return min(base_conf * meta_conf, 0.95)  # cap at 0.95
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect Tier B traps; return low confidence if ambiguous."""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does) .*(fail|stop|end)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+', p) and '?' in p:
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p) and not re.search(r'\bonly\b', p):
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p):
            if not re.search(r'\b(most|least|criterion|measure)', p):
                return 0.3
        
        # Unanswerability markers
        if 'cannot be determined' in p or 'not enough information' in p:
            return 0.4
        
        return 1.0  # no trap detected
    
    def _structural_score(self, prompt: str, answer: str) -> float:
        """Parse structure and compute answer; high score if match."""
        # Numeric comparison
        score = self._numeric_parser(prompt, answer)
        if score >= 0:
            return score
        
        # Bat-and-ball algebra
        score = self._algebra_parser(prompt, answer)
        if score >= 0:
            return score
        
        # All-but-N pattern
        score = self._all_but_n_parser(prompt, answer)
        if score >= 0:
            return score
        
        # Transitivity
        score = self._transitivity_parser(prompt, answer)
        if score >= 0:
            return score
        
        # Modus tollens
        score = self._modus_tollens_parser(prompt, answer)
        if score >= 0:
            return score
        
        # Fallback: token overlap
        return self._token_overlap(prompt, answer)
    
    def _numeric_parser(self, prompt: str, answer: str) -> float:
        """Parse numeric comparisons."""
        matches = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        if len(matches) >= 2:
            nums = [float(m) for m in matches[:2]]
            ans_lower = answer.lower()
            
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                correct = str(max(nums))
                if correct in answer:
                    return 1.0
                elif str(min(nums)) in answer:
                    return 0.0
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                correct = str(min(nums))
                if correct in answer:
                    return 1.0
                elif str(max(nums)) in answer:
                    return 0.0
        
        return -1  # not applicable
    
    def _algebra_parser(self, prompt: str, answer: str) -> float:
        """Solve simple algebra (bat-and-ball style)."""
        # "X and Y cost Z, X costs W more than Y"
        match = re.search(r'(\d+\.?\d*)\s*more than', prompt.lower())
        total_match = re.search(r'cost[s]?\s*(\d+\.?\d*)', prompt.lower())
        
        if match and total_match:
            diff = float(match.group(1))
            total = float(total_match.group(1))
            # x + y = total, x = y + diff => 2y + diff = total
            y = (total - diff) / 2
            x = y + diff
            
            ans_nums = re.findall(r'\d+\.?\d*', answer)
            if ans_nums:
                ans_val = float(ans_nums[0])
                if abs(ans_val - y) < 0.01 or abs(ans_val - x) < 0.01:
                    return 1.0
                else:
                    return 0.1
        
        return -1
    
    def _all_but_n_parser(self, prompt: str, answer: str) -> float:
        """All but N pattern."""
        match = re.search(r'all but (\d+)', prompt.lower())
        total_match = re.search(r'(\d+)\s+\w+', prompt.lower())
        
        if match and total_match:
            n = int(match.group(1))
            total = int(total_match.group(1))
            result = total - n
            
            if str(result) in answer:
                return 1.0
            else:
                return 0.0
        
        return -1
    
    def _transitivity_parser(self, prompt: str, answer: str) -> float:
        """A > B, B > C => A > C."""
        lines = prompt.split('.')
        relations = []
        
        for line in lines:
            match = re.search(r'(\w+)\s+(>|<|taller|shorter|faster|slower)\s+(\w+)', line.lower())
            if match:
                relations.append((match.group(1), match.group(2), match.group(3)))
        
        if len(relations) >= 2:
            # Simple transitive closure
            if relations[0][2] == relations[1][0]:  # B in both
                implied = (relations[0][0], relations[0][1], relations[1][2])
                if implied[0] in answer.lower() and implied[2] in answer.lower():
                    return 0.9
        
        return -1
    
    def _modus_tollens_parser(self, prompt: str, answer: str) -> float:
        """If P then Q. Not Q. => Not P."""
        if_match = re.search(r'if (.+?) then (.+?)[\.\?]', prompt.lower())
        not_match = re.search(r'not (.+?)[\.\?]', prompt.lower())
        
        if if_match and not_match:
            q = if_match.group(2).strip()
            not_q = not_match.group(1).strip()
            
            if q in not_q:  # Not Q holds
                p = if_match.group(1).strip()
                if 'not' in answer.lower() and p in answer.lower():
                    return 0.9
        
        return -1
    
    def _token_overlap(self, prompt: str, answer: str) -> float:
        """Fallback: normalized token overlap."""
        p_tokens = set(re.findall(r'\w+', prompt.lower()))
        a_tokens = set(re.findall(r'\w+', answer.lower()))
        
        if not a_tokens:
            return 0.3
        
        overlap = len(p_tokens & a_tokens) / len(a_tokens)
        return min(overlap, 0.6)  # cap fallback score
    
    def _network_score(self, prompt: str, answer: str) -> float:
        """Build belief network and score via consistency."""
        props = self._extract_propositions(prompt + " " + answer)
        if len(props) < 2:
            return 0.5
        
        n = len(props)
        W = self._build_graph(props)
        c = self._init_confidence(props)
        
        # Belief propagation
        for _ in range(self.k_rounds):
            c_new = np.clip(W.T @ c, 0, 1)
            c = (1 - self.damping) * c + self.damping * c_new
        
        # Error monitoring
        inconsistency = np.zeros(n)
        for i in range(n):
            for j in range(n):
                if W[i, j] > 0:
                    inconsistency[i] += abs(c[i] - c[j]) * W[i, j]
        
        c = c * np.exp(-self.lambda_penalty * inconsistency)
        
        # Score: mean confidence of answer propositions
        ans_props = self._extract_propositions(answer)
        ans_indices = [i for i, p in enumerate(props) if any(self._tokens(ap) <= self._tokens(p) for ap in ans_props)]
        
        if ans_indices:
            return float(np.mean(c[ans_indices]))
        else:
            return 0.5
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions with logical structure."""
        props = []
        
        # Conditionals
        props += re.findall(r'if .+? then .+?[\.\?]', text.lower())
        
        # Negations
        props += re.findall(r'not .+?[\.\?]', text.lower())
        
        # Comparatives
        props += re.findall(r'\w+ (>|<|more|less|greater|smaller) .+?[\.\?]', text.lower())
        
        # Causal
        props += re.findall(r'.+? (because|leads to|results in) .+?[\.\?]', text.lower())
        
        # Temporal
        props += re.findall(r'(before|after|while|then) .+?[\.\?]', text.lower())
        
        # Fallback: split sentences
        if not props:
            props = [s.strip() for s in re.split(r'[\.\?!]', text) if len(s.strip()) > 5]
        
        return props[:20]  # limit for efficiency
    
    def _tokens(self, text: str) -> set:
        """Extract token set (stop words removed)."""
        stop = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'to', 'of', 'and', 'or'}
        return set(re.findall(r'\w+', text.lower())) - stop
    
    def _build_graph(self, props: List[str]) -> np.ndarray:
        """Build weighted adjacency matrix."""
        n = len(props)
        W = np.eye(n)
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    ti = self._tokens(props[i])
                    tj = self._tokens(props[j])
                    if ti and tj:
                        jaccard = len(ti & tj) / len(ti | tj)
                        W[i, j] = jaccard
        
        return W
    
    def _init_confidence(self, props: List[str]) -> np.ndarray:
        """Initialize confidence from phenomenological cues."""
        c = np.ones(len(props)) * 0.5
        
        for i, p in enumerate(props):
            if re.search(r'\b(i think|i feel|in my experience)\b', p):
                c[i] += 0.2
            if re.search(r'\b(suppose|assume|consider)\b', p):
                c[i] += 0.1
        
        return np.clip(c, 0, 1)
    
    def _ncd_score(self, prompt: str, answer: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        cp = len(zlib.compress(prompt.encode()))
        ca = len(zlib.compress(answer.encode()))
        cpa = len(zlib.compress((prompt + answer).encode()))
        
        ncd = (cpa - min(cp, ca)) / max(cp, ca)
        return max(0, 1 - ncd)