import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Critical Pragmatic Error-Correcting Reservoir (CPER) v2.

    1. Criticality: Logistic map reservoir (r=3.99) amplifies small textual diffs.
    2. Error Correcting Codes: Redundancy-based multi-signal syndrome checks with
       Hamming-like partial credit across negation/numeric/comparative/conditional.
    3. Pragmatics: Gricean maxims — Quantity, Quality, Relevance, Manner.
    """

    def __init__(self):
        self.chaos_param = 3.99
        self.reservoir_steps = 50

    def _reservoir_state(self, text):
        if not text: return 0.5
        seed = 0.1 + 0.8 * ((sum(ord(c) for c in text) / (len(text) * 128.0)) % 1.0)
        x = seed
        for _ in range(self.reservoir_steps):
            x = self.chaos_param * x * (1.0 - x)
            x = max(0.001, min(0.999, x))
        return x

    def _parse(self, text):
        t = text.lower()
        neg = any(n in t for n in ['not','no ','never','false',"n't",'impossible','neither'])
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        comp = any(w in t for w in ['greater','less','more','fewer','larger','smaller',
                                     'highest','lowest','maximum','minimum'])
        cond = 'if ' in t and 'then' in t
        subj = re.findall(r'\b[A-Z][a-z]+\b', text)
        return {'neg': neg, 'nums': nums, 'comp': comp, 'cond': cond, 'subj': subj}

    def _compute_syndromes(self, p, c, prompt, candidate):
        checks = [('negation', p['neg'] == c['neg'])]
        if p['nums']:
            checks.append(('num_present', bool(c['nums'])))
        if p['nums'] and c['nums']:
            p_low = prompt.lower()
            if any(w in p_low for w in ['largest','greatest','max','bigger','more']):
                checks.append(('num_max', max(c['nums']) >= max(p['nums'])))
            elif any(w in p_low for w in ['smallest','least','min','fewer','less']):
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

    def _pragmatic_score(self, prompt, candidate):
        p_w, c_w = prompt.split(), candidate.split()
        score, reasons = 1.0, []
        if len(p_w) > 10 and len(c_w) < 2:
            score -= 0.3; reasons.append('too_brief')
        elif len(c_w) > len(p_w) * 3:
            score -= 0.2; reasons.append('verbose')
        stop = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it','be'}
        p_tok = set(w.lower().strip('.,!?') for w in p_w) - stop
        c_tok = set(w.lower().strip('.,!?') for w in c_w) - stop
        if p_tok:
            ov = len(p_tok & c_tok) / len(p_tok)
            if ov == 0 and c_tok: score -= 0.4; reasons.append('irrelevant')
            else: score += 0.1 * ov
        c_low = candidate.lower()
        if ('true' in c_low and 'false' in c_low) or ('yes' in c_low and 'no ' in c_low):
            score -= 0.3; reasons.append('self_contradiction')
        return float(np.clip(score, 0.0, 1.0)), reasons

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _reflect(self, results):
        if len(results) < 2: return results
        if results[0]['score'] - results[1]['score'] < 0.05:
            for r in results[:2]: r['reasoning'] += ' | metacog:tie_within_5pct'
        if 'negation' in results[0].get('_failed', []):
            results[0]['reasoning'] += ' | metacog:negation_inconsistency_warning'
        return results

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list): return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates: return []
        p_struct, p_state = self._parse(prompt), self._reservoir_state(prompt)
        results = []
        for cand in candidates:
            c_struct, c_state = self._parse(cand), self._reservoir_state(cand)
            checks = self._compute_syndromes(p_struct, c_struct, prompt, cand)
            syn_val, failed = self._syndrome_score(checks)
            prag_val, prag_reasons = self._pragmatic_score(prompt, cand)
            div = abs(p_state - c_state)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            base = syn_val * 0.35 + prag_val * 0.25 + div * 0.10 + ncd_sim * 0.15
            if not failed: base += 0.10
            if p_struct['nums'] and c_struct['nums']: base += 0.05
            score = float(np.clip(base, 0.0, 1.0))
            n_pass = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn_val:.2f}({n_pass}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            if prag_reasons: parts.append(f'structural:pragmatic=[{",".join(prag_reasons)}]')
            else: parts.append(f'execution:pragmatics={prag_val:.2f}')
            parts.append(f'fallback:ncd={ncd_sim:.2f}(15%)')
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
