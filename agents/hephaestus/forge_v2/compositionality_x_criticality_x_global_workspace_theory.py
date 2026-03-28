import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Critical Compositional Global Workspace (CCGW) v2.

    Three intersecting concepts:
    1. Compositionality: Parses prompt into typed tokens (numbers, logic ops,
       entities). Builds compositional feature vectors for each candidate.
    2. Criticality: Homeostatic ignition threshold with branching ratio ~1.0.
       Activity history drives plasticity: too much ignition raises threshold,
       too little lowers it.
    3. Global Workspace: Specialized modules (numeric, logical, structural,
       pragmatic) compete. High-salience signals are broadcast and amplified
       across modules. Only candidates exceeding the critical threshold ignite.
    """

    def __init__(self):
        self.threshold = 0.5
        self.lr = 0.1
        self.history = []

    # ── compositionality: token extraction ────────────────────────────
    def _tokenize(self, text):
        t = text.lower()
        nums = re.findall(r'-?\d+\.?\d*', t)
        logic = [w for w in ['not','no','yes','true','false','if','then',
                             'greater','less','equal','never',"n't"] if w in t]
        words = set(re.findall(r'[a-z]{3,}', t)) - {
            'the','and','for','are','but','not','you','all','can','had',
            'her','was','one','our','out','has','his','how','its','let',
            'may','who','did','get','has','him','she','too','use'}
        return {'nums': nums, 'logic': logic, 'content': words}

    # ── module: numeric evaluation ────────────────────────────────────
    def _numeric_module(self, p, c):
        p_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', p)]
        c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', c)]
        if not p_nums:
            return 0.5
        score = 0.0
        p_low = p.lower()
        if c_nums:
            common = set(p_nums) & set(c_nums)
            score += 0.3 * len(common) / max(len(set(p_nums)), 1)
            if any(w in p_low for w in ['largest','greater','more','maximum','max','biggest']):
                score += 0.4 if (c_nums and max(c_nums) >= max(p_nums)) else 0.0
            elif any(w in p_low for w in ['smallest','less','fewer','minimum','min']):
                score += 0.4 if (c_nums and min(c_nums) <= min(p_nums)) else 0.0
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                expected = None
                if '+' in p or 'sum' in p_low or 'add' in p_low:
                    expected = sum(p_nums)
                elif '-' in p and 'subtract' in p_low:
                    expected = p_nums[0] - sum(p_nums[1:])
                if expected is not None and any(abs(x - expected) < 1e-6 for x in c_nums):
                    score += 0.5
        elif p_nums:
            score -= 0.2
        return float(np.clip(score, 0.0, 1.0))

    # ── module: logical evaluation ────────────────────────────────────
    def _logical_module(self, p, c):
        p_low, c_low = p.lower(), c.lower()
        score = 0.0
        neg_markers = ['not','no ','never',"n't",'false','impossible','neither','nor']
        p_neg = any(n in p_low for n in neg_markers)
        c_neg = any(n in c_low for n in neg_markers)
        if p_neg and c_neg:
            score += 0.4
        elif p_neg != c_neg:
            score -= 0.3
        affirm = ['yes','true','correct']
        deny = ['no','false','incorrect']
        if any(w in p_low for w in affirm):
            score += 0.3 if any(w in c_low for w in affirm) else -0.2
        if any(w in p_low for w in deny):
            score += 0.3 if any(w in c_low for w in deny) else -0.2
        if 'if ' in p_low and 'then' in p_low:
            score += 0.2 if ('then' in c_low or any(w in c_low for w in affirm + deny)) else -0.1
        return float(np.clip(score, -1.0, 1.0))

    # ── module: pragmatic evaluation ──────────────────────────────────
    def _pragmatic_module(self, p, c):
        p_tok = self._tokenize(p)['content']
        c_tok = self._tokenize(c)['content']
        overlap = len(p_tok & c_tok) / max(len(p_tok | c_tok), 1)
        p_len, c_len = len(p.split()), len(c.split())
        brevity = 0.0
        if p_len > 10 and c_len < 2:
            brevity = -0.4
        elif c_len > p_len * 3:
            brevity = -0.2
        return float(np.clip(overlap + brevity, 0.0, 1.0))

    # ── module: NCD structural (capped at 15%) ───────────────────────
    def _ncd_module(self, p, c):
        if not p or not c:
            return 0.0
        c1 = len(zlib.compress(p.encode()))
        c2 = len(zlib.compress(c.encode()))
        c12 = len(zlib.compress((p + c).encode()))
        dist = (c12 - min(c1, c2)) / max(c1, c2, 1)
        return float(np.clip(1.0 - dist, 0.0, 1.0))

    # ── global workspace: broadcasting + critical ignition ────────────
    def _broadcast_and_ignite(self, votes):
        arr = np.array(votes, dtype=float)
        salience = np.abs(arr)
        max_sal = np.max(salience) if len(salience) > 0 else 0.0
        if max_sal > 0.6:
            broadcast_weight = 0.3
            arr = arr + broadcast_weight * (arr[np.argmax(salience)] - arr)
        raw = float(np.mean(arr))
        margin = raw - self.threshold
        ignition = 1.0 / (1.0 + np.exp(-12 * margin))
        self.history.append(raw)
        if len(self.history) > 12:
            self.history.pop(0)
        if len(self.history) >= 4:
            avg = np.mean(self.history)
            self.threshold += self.lr * (avg - 0.5)
            self.threshold = float(np.clip(self.threshold, 0.1, 0.9))
        return float(ignition), raw

    # ── metacognitive reflection ──────────────────────────────────────
    def _reflect(self, results):
        if len(results) < 2:
            return results
        gap = results[0]['score'] - results[1]['score']
        if gap < 0.05:
            results[0]['reasoning'] += ' | metacog:tie_within_5pct'
            results[1]['reasoning'] += ' | metacog:tie_within_5pct'
        return results

    # ── public interface ──────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list):
            return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates:
            return []

        results = []
        for cand in candidates:
            v_num = self._numeric_module(prompt, cand)
            v_log = self._logical_module(prompt, cand)
            v_prag = self._pragmatic_module(prompt, cand)
            v_ncd = self._ncd_module(prompt, cand)

            # Weighted votes: 85% execution modules, 15% NCD
            exec_votes = [v_num * 0.35, v_log * 0.30, v_prag * 0.20]
            ncd_vote = v_ncd * 0.15
            all_votes = exec_votes + [ncd_vote]

            ignition, raw_act = self._broadcast_and_ignite(
                [v_num, v_log, v_prag, v_ncd])
            # Blend ignition with weighted sum
            weighted = sum(all_votes)
            score = float(np.clip(0.6 * ignition + 0.4 * weighted, 0.0, 1.0))

            parts = []
            if v_num > 0.3:
                parts.append(f'execution:numeric={v_num:.2f}')
            if abs(v_log) > 0.2:
                parts.append(f'execution:logic={v_log:.2f}')
            if v_prag > 0.3:
                parts.append(f'structural:pragmatic={v_prag:.2f}')
            parts.append(f'fallback:ncd={v_ncd:.2f}(15%)')
            if ignition > 0.8:
                parts.append('execution:ignited')
            elif raw_act < self.threshold:
                parts.append('structural:sub_threshold')
            reason = ' | '.join(parts)
            results.append({'candidate': cand, 'score': round(score, 4),
                            'reasoning': reason})

        results.sort(key=lambda x: x['score'], reverse=True)
        results = self._reflect(results)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str):
            return 0.0
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        null_res = self.evaluate(prompt, [''])
        null_score = null_res[0]['score'] if null_res else 0.0
        conf = max(0.0, score - null_score) / max(1.0 - null_score, 1e-6)
        return float(np.clip(round(conf, 4), 0.0, 1.0))
