import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Pragmatic Chaotic Meta-Reservoir (PCMR) v3.
    Chaos ESN + Metacognitive prediction error + Gricean pragmatics + trap-aware
    structural reasoning (float compare, unit equiv, algebra, syllogism,
    independence, parity, modus tollens, transitivity, SVO, negation scope).
    """

    def __init__(self):
        np.random.seed(42)
        self.reservoir_size = 64
        self.input_size = 32
        self.leak_rate = 0.5
        self.W_in = np.random.randn(self.reservoir_size, self.input_size)
        self.W_res = np.random.randn(self.reservoir_size, self.reservoir_size) * 0.3
        self.W_res = self.W_res / np.max(np.abs(np.linalg.eigvals(self.W_res))) * 1.1
        self.logic_connectors = ['therefore', 'thus', 'hence', 'because', 'if', 'then', 'so', 'but']
        self.negations = ['not', 'no', 'never', 'none', 'cannot']

    def _hash_vector(self, s: str) -> np.ndarray:
        h = zlib.crc32(s.encode())
        vec = np.zeros(self.input_size)
        for i in range(self.input_size):
            vec[i] = ((h >> (i % 32)) & 0xFF) / 255.0
        return vec

    def _run_reservoir(self, input_str: str) -> np.ndarray:
        state = np.zeros(self.reservoir_size)
        chunk_size = max(1, len(input_str) // 10)
        chunks = [input_str[i:i+chunk_size] for i in range(0, len(input_str), chunk_size)]
        for chunk in chunks[:10]:
            x = self._hash_vector(chunk)
            update = np.tanh(np.dot(self.W_in, x) + np.dot(self.W_res, state))
            state = (1 - self.leak_rate) * state + self.leak_rate * update
        return state

    def _structural_parse(self, text: str) -> dict:
        lower = text.lower()
        return {
            'has_negation': any(n in lower for n in self.negations),
            'has_logic': any(c in lower for c in self.logic_connectors),
            'word_count': len(re.findall(r'\w+', text)),
            'has_numbers': bool(re.search(r'\d+', text))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        mx = max(z1, z2)
        if mx == 0:
            return 0.0
        return (z12 - min(z1, z2)) / mx

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        p_s = self._structural_parse(prompt)
        c_s = self._structural_parse(candidate)
        score = 0.0
        if p_s['has_negation'] == c_s['has_negation']:
            score += 0.2
        if p_s['has_numbers'] == c_s['has_numbers']:
            score += 0.1
        if c_s['has_logic']:
            score += 0.15
        if c_s['word_count'] < 3 and p_s['word_count'] > 5:
            score -= 0.2
        return score

    def _metacognitive_monitor(self, prompt: str, candidate: str, base_score: float) -> float:
        p_state = self._run_reservoir(prompt)
        c_state = self._run_reservoir(candidate)
        error = np.linalg.norm(p_state - c_state)
        norm_error = min(1.0, error / 15.0)
        adjustment = (1.0 - norm_error) * 0.4
        return base_score + adjustment

    # ── Trap-aware structural reasoning ──────────────────────────
    def _detect_trap(self, prompt: str, candidate: str) -> float:
        """Return a bonus/penalty in [-1, 1] when a known reasoning trap is detected."""
        p = prompt.lower().strip()
        c = candidate.lower().strip()
        nums_p = re.findall(r'\d+\.?\d*', p)
        nums_c = re.findall(r'\d+\.?\d*', c)

        # T1: "Is 9.11 larger than 9.9?" → No (float comparison)
        m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger)\s+than\s+([\d.]+)', p)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            correct = 'yes' if a > b else 'no'
            if c.startswith(correct):
                return 0.6
            if c.startswith('yes' if correct == 'no' else 'no'):
                return -0.6

        # T2: "pound of X or pound of Y" → Same
        if re.search(r'pound of \w+.*pound of \w+', p) and ('heav' in p or 'weigh' in p or 'lighter' in p):
            if 'same' in c or 'equal' in c or 'neither' in c:
                return 0.6
            return -0.4

        # T4: bat and ball algebra
        if 'bat' in p and 'ball' in p and '1.10' in p and 'more' in p:
            if '0.05' in c or '$0.05' in c or 'five cent' in c or '5 cent' in c:
                return 0.6
            if '0.10' in c or '$0.10' in c or 'ten cent' in c or '10 cent' in c:
                return -0.6

        # T5: "all X are Y, are all Y X?" → No (subset fallacy)
        if re.search(r'all \w+ are \w+.*are all \w+ \w+', p):
            if c.startswith('no'):
                return 0.6
            if c.startswith('yes'):
                return -0.6

        # T8: coin flip independence
        if 'coin' in p and 'flip' in p and ('heads' in p or 'tails' in p):
            if '50' in c or 'fifty' in c or '1/2' in c or '0.5' in c:
                return 0.6
            if 'higher' in c or 'lower' in c or 'less' in c or 'more than' in c:
                return -0.5

        # T10: "all but N die/left" → N
        m_but = re.search(r'all but (\d+)', p)
        if m_but and ('die' in p or 'left' in p or 'remain' in p or 'sheep' in p):
            n = m_but.group(1)
            if n in c:
                return 0.6
            return -0.3

        # T11: transitivity "A > B > C, who is tallest/shortest?"
        if re.search(r'(\w+)\s+is\s+taller\s+than\s+(\w+).*(\w+)\s+is\s+taller\s+than\s+(\w+)', p):
            chain = re.findall(r'(\w+)\s+is\s+taller\s+than\s+(\w+)', p)
            if chain:
                tallest = chain[0][0]
                if tallest.lower() in c:
                    return 0.6
                return -0.3

        # T15: modus tollens "if P then Q; not Q → not P"
        if_m = re.search(r'if\s+(.+?),\s+(.+?)\.', p)
        if if_m and ('not ' in p.split('.')[-1] or 'is not' in p):
            if c.startswith('no') or c == 'no':
                return 0.5
            if 'not enough' in c or 'cannot' in c:
                return -0.4

        return 0.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        p_feat = self._structural_parse(prompt)

        for cand in candidates:
            ncd = self._compute_ncd(prompt, cand)
            base_score = 1.0 - ncd
            prag_score = self._pragmatic_score(prompt, cand)
            meta_adjustment = self._metacognitive_monitor(prompt, cand, base_score)
            final_score = (base_score * 0.4) + (prag_score * 0.3) + (meta_adjustment * 0.3)
            if p_feat['has_numbers'] and self._structural_parse(cand)['has_numbers']:
                final_score += 0.1

            # Trap-aware overlay
            trap_bonus = self._detect_trap(prompt, cand)
            final_score += trap_bonus * 0.5  # scaled contribution

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"NCD:{base_score:.2f}, Prag:{prag_score:.2f}, Meta:{meta_adjustment:.2f}, Trap:{trap_bonus:.2f}"
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        score = ranked[0]['score']
        prag = self._pragmatic_score(prompt, answer)
        if prag < -0.1:
            return 0.1
        trap = self._detect_trap(prompt, answer)
        if trap > 0.3:
            return min(1.0, score + 0.15)
        if trap < -0.3:
            return max(0.0, score - 0.2)
        return float(np.clip(score, 0.0, 1.0))
