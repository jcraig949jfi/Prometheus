import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Critical Information-Theoretic Pragmatic Evaluator (CITPE) v2.

    1. Criticality: Logistic map reservoir (r=3.99) amplifies small textual
       differences via compression-delta variance (susceptibility proxy).
    2. Information Theory: NCD (capped 15%) plus compression-length ratio as
       an absolute complexity estimate for each candidate.
    3. Pragmatics: Gricean maxims -- Quantity, Relation, Manner -- with
       stopword-filtered overlap and self-contradiction detection.
    """

    def __init__(self):
        self.chaos_r = 3.99
        self.reservoir_steps = 40

    # -- helpers -------------------------------------------------------
    def _compress_len(self, s):
        return len(zlib.compress(s.encode('utf-8'))) if s else 0

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1, c2 = self._compress_len(s1), self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        return min((c12 - min(c1, c2)) / max(c1, c2, 1), 0.15)

    def _reservoir_state(self, text):
        if not text: return 0.5
        seed = 0.1 + 0.8 * ((sum(ord(c) for c in text) / (len(text) * 128.0)) % 1.0)
        x = seed
        for _ in range(self.reservoir_steps):
            x = self.chaos_r * x * (1.0 - x)
            x = max(0.001, min(0.999, x))
        return x

    def _susceptibility(self, prompt, candidate):
        if len(candidate) < 2: return 0.1
        base = self._compress_len(prompt)
        step = max(1, len(candidate) // 5)
        deltas = [self._compress_len(prompt + candidate[:i]) - base
                  for i in range(1, len(candidate), step)]
        if len(deltas) < 2: return 0.1
        mu = np.mean(deltas)
        var = np.mean([(d - mu) ** 2 for d in deltas])
        return float(min(1.0, np.sqrt(var) / 10.0))

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

    # -- pragmatic scoring --------------------------------------------
    def _pragmatic_score(self, prompt, candidate):
        pw, cw = prompt.split(), candidate.split()
        score, reasons = 1.0, []
        if len(pw) > 10 and len(cw) < 2:
            score -= 0.3; reasons.append('too_brief')
        elif len(cw) > len(pw) * 3:
            score -= 0.2; reasons.append('verbose')
        stop = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it','be'}
        pt = set(w.lower().strip('.,!?') for w in pw) - stop
        ct = set(w.lower().strip('.,!?') for w in cw) - stop
        if pt:
            ov = len(pt & ct) / len(pt)
            if ov == 0 and ct: score -= 0.4; reasons.append('irrelevant')
            else: score += 0.1 * ov
        cl = candidate.lower()
        if ('true' in cl and 'false' in cl) or ('yes' in cl and 'no ' in cl):
            score -= 0.3; reasons.append('self_contradiction')
        return float(np.clip(score, 0.0, 1.0)), reasons

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
        results = []
        for cand in candidates:
            cs = self._parse(cand)
            checks = self._structural_checks(ps, cs, prompt, cand)
            syn, failed = self._syndrome_score(checks)
            prag, pr = self._pragmatic_score(prompt, cand)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            susc = self._susceptibility(prompt, cand)
            compr = self._compress_len(cand) / max(len(cand.encode('utf-8')), 1)
            base = syn * 0.30 + prag * 0.20 + ncd_sim * 0.15 + susc * 0.10 + (1.0 - compr) * 0.10
            if not failed: base += 0.10
            if ps['nums'] and cs['nums']: base += 0.05
            score = float(np.clip(base, 0.0, 1.0))
            np_ = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn:.2f}({np_}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            if pr: parts.append(f'structural:pragmatic=[{",".join(pr)}]')
            else: parts.append(f'execution:pragmatics={prag:.2f}')
            parts.append(f'execution:susceptibility={susc:.2f}')
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
