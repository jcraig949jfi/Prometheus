from typing import Dict, Tuple

"""
Spectral-Hoare-Bandit Reasoning Tool
Combines Hoare logic constraint propagation, spectral coherence analysis, and multi-armed bandits.
"""
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.arm_counts = {}
        self.arm_values = {}
        self.total_pulls = 0
        self.c_explore = 1.4
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Computational solvers (Frame E requirement)
            comp_score = self._compute_answer(prompt, cand)
            
            # Hoare-spectral-bandit pipeline
            props = self._extract_propositions(cand)
            truth_vec, contradiction_penalty = self._constraint_propagation(props)
            coherence = self._spectral_coherence(truth_vec) if len(truth_vec) > 0 else 0.5
            raw_reward = coherence * (1 - contradiction_penalty)
            
            # UCB bandit scoring
            ucb_score = self._ucb_update(cand, raw_reward)
            
            # Combine: 50% computational, 35% bandit, 15% NCD
            ncd_score = 1 - self._ncd(prompt, cand)
            final_score = 0.5 * comp_score + 0.35 * ucb_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"comp={comp_score:.2f} ucb={ucb_score:.2f} coh={coherence:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        comp_conf = self._compute_answer(prompt, answer)
        return min(meta_conf, max(0.1, min(0.85, comp_conf)))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable prompts (Tier B epistemic honesty)"""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.25
        
        # Scope ambiguity: "Every X did a Y"
        if re.search(r'\bevery \w+ .* \ba\b', p_lower):
            return 0.28
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and 'who' in p_lower:
            return 0.27
        
        # False dichotomy: "Either A or B"
        if re.search(r'\beither .* \bor\b', p_lower) and '?' in prompt:
            return 0.29
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(impossible to|cannot determine|not enough information)\b', p_lower):
            return 0.26
        
        return 1.0
    
    def _compute_answer(self, prompt: str, answer: str) -> float:
        """Frame E: Compute answers via parsing + execution"""
        score = 0.5
        
        # Numeric comparison parser
        num_match = re.search(r'(\d+\.?\d*)\s*(>|<|==|>=|<=)\s*(\d+\.?\d*)', prompt)
        if num_match:
            left, op, right = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
            result = eval(f"{left} {op} {right}")
            if (result and 'true' in answer.lower()) or (not result and 'false' in answer.lower()):
                return 0.9
        
        # Bat-and-ball algebra: "X and Y cost $A, X costs $B more than Y"
        bat_ball = re.search(r'(\w+) and (\w+) cost \$?([\d.]+).*\1 costs \$?([\d.]+) more', prompt, re.I)
        if bat_ball:
            total, diff = float(bat_ball.group(3)), float(bat_ball.group(4))
            y_val = (total - diff) / 2
            ans_nums = re.findall(r'\d+\.?\d*', answer)
            if ans_nums and abs(float(ans_nums[0]) - y_val) < 0.01:
                return 0.92
        
        # All-but-N parser
        all_but = re.search(r'all but (\d+)', prompt, re.I)
        if all_but:
            total_match = re.search(r'(\d+) (\w+)', prompt)
            if total_match:
                total, n = int(total_match.group(1)), int(all_but.group(1))
                if str(total - n) in answer:
                    return 0.88
        
        # Modular arithmetic
        mod_match = re.search(r'(\d+) mod (\d+)', prompt, re.I)
        if mod_match:
            val, mod = int(mod_match.group(1)), int(mod_match.group(2))
            if str(val % mod) in answer:
                return 0.91
        
        # Transitivity: A > B, B > C => A > C
        trans = re.findall(r'(\w+)\s*>\s*(\w+)', prompt)
        if len(trans) >= 2:
            chain = {trans[0][0]: trans[0][1]}
            for a, b in trans[1:]:
                if a in chain.values():
                    chain[a] = b
            first, last = trans[0][0], trans[-1][1]
            if f"{first}" in answer and f"{last}" in answer and ">" in answer:
                score = 0.85
        
        # Modus tollens: If A then B, not B => not A
        if_then = re.search(r'if (.+?) then (.+?)[\.,]', prompt, re.I)
        not_b = re.search(r'not (.+?)[\.,]', prompt, re.I)
        if if_then and not_b:
            if 'not' in answer.lower() and if_then.group(1).lower() in answer.lower():
                score = 0.87
        
        # Bayesian base rate
        base_rate = re.search(r'(\d+)% .* (\d+)% (sensitivity|accuracy)', prompt, re.I)
        if base_rate:
            prior = float(base_rate.group(1)) / 100
            likelihood = float(base_rate.group(2)) / 100
            posterior = (prior * likelihood) / ((prior * likelihood) + ((1 - prior) * 0.05))
            ans_pct = re.findall(r'(\d+)%', answer)
            if ans_pct and abs(float(ans_pct[0]) - posterior * 100) < 5:
                score = 0.93
        
        return score
    
    def _extract_propositions(self, text: str) -> List[Tuple]:
        """Extract Hoare-style triples from text"""
        props = []
        
        # Conditionals: if X then Y => (X, stmt, Y)
        for match in re.finditer(r'if (.+?) then (.+?)[\.,]', text, re.I):
            props.append((match.group(1).strip(), "implies", match.group(2).strip()))
        
        # Comparatives: X > Y
        for match in re.finditer(r'(\w+)\s*(>|<|==)\s*(\w+)', text):
            props.append((match.group(1), match.group(2), match.group(3)))
        
        # Negations: not X
        for match in re.finditer(r'not (.+?)[\.,]', text, re.I):
            props.append(("neg", "not", match.group(1).strip()))
        
        # Causal: X because Y
        for match in re.finditer(r'(.+?) because (.+?)[\.,]', text, re.I):
            props.append((match.group(2).strip(), "causes", match.group(1).strip()))
        
        return props
    
    def _constraint_propagation(self, props: List[Tuple]) -> Tuple[np.ndarray, float]:
        """Hoare-style constraint propagation"""
        if not props:
            return np.array([1]), 0.0
        
        truth = [1] * len(props)
        contradiction_count = 0
        
        # Check for direct contradictions
        for i, (pre1, op1, post1) in enumerate(props):
            for j, (pre2, op2, post2) in enumerate(props):
                if i >= j:
                    continue
                
                # Transitivity violation: A > B, B > A
                if op1 == ">" and op2 == ">" and post1 == pre2 and post2 == pre1:
                    truth[i] = 0
                    truth[j] = 0
                    contradiction_count += 1
                
                # Implication contradiction: if A then B, if A then not B
                if op1 == "implies" and op2 == "implies" and pre1 == pre2:
                    if ("not" in post1 and post1.replace("not", "").strip() == post2) or \
                       ("not" in post2 and post2.replace("not", "").strip() == post1):
                        truth[i] = 0
                        truth[j] = 0
                        contradiction_count += 1
        
        penalty = min(1.0, contradiction_count / (len(props) + 1))
        return np.array(truth, dtype=float), penalty
    
    def _spectral_coherence(self, truth_vec: np.ndarray) -> float:
        """Compute spectral flatness as coherence measure"""
        if len(truth_vec) < 2:
            return 0.5
        
        # Pad to power of 2 for FFT efficiency
        padded_len = 2 ** int(np.ceil(np.log2(len(truth_vec))))
        padded = np.pad(truth_vec, (0, padded_len - len(truth_vec)), constant_values=0.5)
        
        # Compute power spectral density
        fft_result = np.fft.rfft(padded)
        psd = np.abs(fft_result) ** 2
        psd = psd + 1e-10  # Avoid log(0)
        
        # Spectral flatness: geometric mean / arithmetic mean
        geo_mean = np.exp(np.mean(np.log(psd)))
        arith_mean = np.mean(psd)
        flatness = geo_mean / arith_mean
        
        # Low flatness => high coherence
        coherence = 1 - flatness
        return float(np.clip(coherence, 0, 1))
    
    def _ucb_update(self, arm: str, reward: float) -> float:
        """Multi-armed bandit UCB scoring"""
        if arm not in self.arm_counts:
            self.arm_counts[arm] = 0
            self.arm_values[arm] = 0.0
        
        # Update statistics
        self.arm_counts[arm] += 1
        self.total_pulls += 1
        
        # Incremental mean update
        n = self.arm_counts[arm]
        q = self.arm_values[arm]
        self.arm_values[arm] = q + (reward - q) / n
        
        # UCB score
        if self.total_pulls <= 1:
            return reward
        
        exploration_bonus = self.c_explore * np.sqrt(np.log(self.total_pulls) / n)
        ucb_score = self.arm_values[arm] + exploration_bonus
        
        return float(np.clip(ucb_score, 0, 1))
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% of score)"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0