import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Chaotic Hebbian Free-Energy Evaluator (CHFE) v2.

    1. Chaos Theory: Logistic map reservoir (r=3.99) perturbs similarity
       estimates for hypothesis-space exploration.
    2. Free Energy Principle: Prediction error between prompt/candidate
       structural feature vectors drives scoring.
    3. Hebbian Learning: Correlation-based weight updates -- features that
       co-activate in prompt and candidate get strengthened; anti-correlated
       features get weakened over iterative passes.
    """

    def __init__(self):
        self.chaos_r = 3.99
        self.iterations = 12
        self.hebbian_lr = 0.15

    # -- compression / NCD --------------------------------------------
    def _compress_len(self, s):
        return len(zlib.compress(s.encode('utf-8'))) if s else 0

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1, c2 = self._compress_len(s1), self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        return min((c12 - min(c1, c2)) / max(c1, c2, 1), 0.15)

    # -- text to feature vector ---------------------------------------
    def _text_vec(self, text, dim=32):
        v = np.zeros(dim)
        if not text: return v
        for i, c in enumerate(text):
            v[ord(c) % dim] += (i + 1) / len(text)
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

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

    # -- Hebbian correlation weight update ----------------------------
    def _hebbian_score(self, pv, cv):
        """Hebbian update: weight = correlation; iterate to consolidate."""
        w = np.ones(len(pv)) * 0.5
        for _ in range(self.iterations):
            corr = pv * cv
            w += self.hebbian_lr * corr
            w = np.clip(w, 0.0, 1.0)
        return float(np.mean(w * pv * cv))

    # -- chaotic trajectory -------------------------------------------
    def _chaos_score(self, pv, cv):
        state = float(np.clip(0.5 + 0.5 * np.dot(pv, cv), 0.001, 0.999))
        for _ in range(self.iterations):
            chaos = self.chaos_r * state * (1.0 - state)
            error = 1.0 - state
            state = float(np.clip(state + 0.1 * (chaos - error), 0.001, 0.999))
        return state

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
        pv = self._text_vec(prompt)
        results = []
        for cand in candidates:
            cs = self._parse(cand)
            cv = self._text_vec(cand)
            checks = self._structural_checks(ps, cs, prompt, cand)
            syn, failed = self._syndrome_score(checks)
            hebb = self._hebbian_score(pv, cv)
            chaos = self._chaos_score(pv, cv)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            base = syn * 0.30 + hebb * 0.20 + chaos * 0.10 + ncd_sim * 0.15
            if not failed: base += 0.10
            if ps['nums'] and cs['nums']: base += 0.05
            # free-energy prediction error bonus
            fe_error = float(np.linalg.norm(pv - cv))
            fe_bonus = 0.10 * (1.0 / (1.0 + fe_error))
            base += fe_bonus
            score = float(np.clip(base, 0.0, 1.0))
            np_ = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn:.2f}({np_}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            parts.append(f'execution:hebbian={hebb:.2f},chaos={chaos:.2f}')
            parts.append(f'execution:free_energy_bonus={fe_bonus:.3f}')
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
