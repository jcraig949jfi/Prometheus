import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Chaotic Free-Energy MDL Evaluator (CFE-MDL) v2.

    1. Chaos Theory: Logistic map (r=3.99) seeded from prompt hash drives
       deterministic trajectory divergence scoring.
    2. Free Energy Principle: Prediction error = structural mismatch between
       prompt/candidate feature vectors (negation, comparative, conditional).
    3. Kolmogorov Complexity: Compression-length ratio as concrete complexity
       proxy; MDL redundancy score via K(A+B) vs K(A)+K(B).
    """

    def __init__(self):
        self.chaos_r = 3.99
        self.chaos_steps = 50
        self.w_struct = 0.35
        self.w_mdl = 0.25
        self.w_chaos = 0.10

    # -- chaos ---------------------------------------------------------
    def _logistic_map(self, x0, steps):
        x = np.clip(x0, 0.001, 0.999)
        seq = np.empty(steps)
        for i in range(steps):
            x = self.chaos_r * x * (1.0 - x)
            seq[i] = x
        return seq

    def _chaos_seed(self, text):
        h = int(zlib.crc32(text.encode())) % 10000
        return 0.1 + 0.8 * (h / 10000.0)

    # -- compression / NCD --------------------------------------------
    def _compress_len(self, s):
        return len(zlib.compress(s.encode('utf-8'))) if s else 0

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1, c2 = self._compress_len(s1), self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        return min((c12 - min(c1, c2)) / max(c1, c2, 1), 0.15)

    def _complexity_ratio(self, text):
        """Compression-length ratio: concrete Kolmogorov proxy."""
        raw = len(text.encode('utf-8')) if text else 1
        return self._compress_len(text) / max(raw, 1)

    def _mdl_score(self, prompt, candidate):
        kp = self._compress_len(prompt)
        kc = self._compress_len(candidate)
        kpc = self._compress_len(prompt + ' ' + candidate)
        penalty = (kpc - kp) / max(kc, 1)
        return float(np.clip(1.0 - penalty, 0.0, 1.0))

    # -- structural parsing -------------------------------------------
    def _parse(self, text):
        t = text.lower()
        neg = any(n in t for n in ['not','no ','never','false',"n't",'neither'])
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        comp = any(w in t for w in ['greater','less','more','fewer','larger',
                                     'smaller','highest','lowest','maximum','minimum'])
        cond = 'if ' in t and 'then' in t
        subj = re.findall(r'\b[A-Z][a-z]+\b', text)
        return {'neg': neg, 'nums': nums, 'comp': comp, 'cond': cond, 'subj': subj}

    def _structural_checks(self, p, c, prompt, candidate):
        checks = [('negation', p['neg'] == c['neg'])]
        if p['nums']:
            checks.append(('num_present', bool(c['nums'])))
        if p['nums'] and c['nums']:
            pl = prompt.lower()
            if any(w in pl for w in ['largest','greatest','max','bigger','more']):
                checks.append(('num_max', max(c['nums']) >= max(p['nums'])))
            elif any(w in pl for w in ['smallest','least','min','fewer','less']):
                checks.append(('num_min', min(c['nums']) <= min(p['nums'])))
            if len(p['nums']) >= 2 and len(c['nums']) >= 2:
                checks.append(('num_order', (sorted(p['nums']) == p['nums']) ==
                               (sorted(c['nums']) == c['nums'])))
        if p['comp']:
            checks.append(('comparative', c['comp'] or bool(c['nums'])))
        if p['cond']:
            checks.append(('conditional', any(w in candidate.lower()
                          for w in ['yes','no','true','false','then','therefore'])))
        if p['subj']:
            checks.append(('subject_overlap', bool(set(p['subj']) & set(c['subj']))))
        return checks

    def _syndrome_score(self, checks):
        if not checks: return 1.0, []
        passed = sum(1 for _, ok in checks if ok)
        return passed / len(checks), [n for n, ok in checks if not ok]

    # -- metacognitive reflection -------------------------------------
    def _reflect(self, results):
        if len(results) < 2: return results
        if results[0]['score'] - results[1]['score'] < 0.05:
            for r in results[:2]:
                r['reasoning'] += ' | metacog:tie_within_5pct'
        if 'negation' in results[0].get('_failed', []):
            results[0]['reasoning'] += ' | metacog:negation_warning'
        return results

    # -- public API ---------------------------------------------------
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list): return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates: return []
        ps = self._parse(prompt)
        p_traj = self._logistic_map(self._chaos_seed(prompt), self.chaos_steps)
        results = []
        for cand in candidates:
            cs = self._parse(cand)
            checks = self._structural_checks(ps, cs, prompt, cand)
            syn, failed = self._syndrome_score(checks)
            mdl = self._mdl_score(prompt, cand)
            cr = self._complexity_ratio(cand)
            c_traj = self._logistic_map(self._chaos_seed(cand), self.chaos_steps)
            div = float(np.mean(np.abs(p_traj - c_traj)))
            chaos_sc = 1.0 / (1.0 + div)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            base = (syn * self.w_struct + mdl * self.w_mdl + chaos_sc * self.w_chaos
                    + ncd_sim * 0.10 + (1.0 - cr) * 0.10)
            if not failed: base += 0.08
            if ps['nums'] and cs['nums']: base += 0.05
            score = float(np.clip(base, 0.0, 1.0))
            np_ = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn:.2f}({np_}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            parts.append(f'execution:mdl={mdl:.2f},complexity_ratio={cr:.2f}')
            parts.append(f'execution:chaos_stability={chaos_sc:.2f}')
            parts.append(f'fallback:ncd={ncd_sim:.2f}(15%cap)')
            results.append({'candidate': cand, 'score': round(score, 4),
                            'reasoning': ' | '.join(parts), '_failed': failed})
        results.sort(key=lambda x: x['score'], reverse=True)
        results = self._reflect(results)
        for r in results: r.pop('_failed', None)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        null_score = self.evaluate(prompt, [''])[0]['score'] if prompt else 0.0
        conf = max(0.0, score - null_score) / max(1.0 - null_score, 1e-6)
        return float(np.clip(round(conf, 4), 0.0, 1.0))
