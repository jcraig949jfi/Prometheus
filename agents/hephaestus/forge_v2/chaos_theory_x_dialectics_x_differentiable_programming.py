import numpy as np
import re
import zlib
import math

class ReasoningTool:
    """
    Dialectical Chaotic Differentiable Evaluator (DCDE) v2.

    1. Chaos Theory: Logistic map (r=3.9) with Lyapunov exponent estimation;
       edge-of-chaos candidates score highest.
    2. Dialectics: Thesis (prompt features), antithesis (candidate features),
       synthesis (merged scoring with contradiction detection).
    3. Differentiable Programming: Finite-difference sensitivity analysis --
       perturb candidate, measure score delta as gradient proxy.
    """

    def __init__(self):
        self.chaos_r = 3.9
        self.lyap_steps = 50

    # -- compression / NCD --------------------------------------------
    def _compress_len(self, s):
        return len(zlib.compress(s.encode('utf-8'))) if s else 0

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1, c2 = self._compress_len(s1), self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        return min((c12 - min(c1, c2)) / max(c1, c2, 1), 0.15)

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

    # -- chaos: Lyapunov exponent -------------------------------------
    def _lyapunov(self, init_state):
        x = np.clip(init_state, 0.01, 0.99)
        xp = x + 1e-4
        total = 0.0
        for _ in range(self.lyap_steps):
            xn = self.chaos_r * x * (1.0 - x)
            xpn = self.chaos_r * xp * (1.0 - xp)
            d = abs(xn - xpn)
            if d > 1e-10:
                total += math.log(d / max(abs(x - xp), 1e-10))
            x, xp = xn, xpn
            if abs(x - xp) > 1.0:
                xp = x + 1e-4
        return total / max(self.lyap_steps, 1)

    def _chaos_score(self, lyap):
        """Edge-of-chaos: moderate positive Lyapunov is best."""
        if 0.2 < lyap < 0.8: return 0.5
        if lyap > 0: return 0.2
        return 0.1

    # -- dialectics: thesis / antithesis / synthesis -------------------
    def _dialectic_score(self, p, c, prompt, candidate):
        cl = candidate.lower()
        contradictions = [('impossible','possible'), ('false','true'), ('never','always')]
        penalty = 0.0
        for neg, pos in contradictions:
            if neg in prompt.lower() and pos in cl and neg not in cl:
                penalty += 0.15
        if ('true' in cl and 'false' in cl) or ('yes' in cl and 'no ' in cl):
            penalty += 0.2
        stop = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it','be'}
        pw = set(prompt.lower().split()) - stop
        cw = set(cl.split()) - stop
        synthesis = len(pw & cw) / max(len(pw | cw), 1)
        return float(np.clip(synthesis + 0.3 - penalty, 0.0, 1.0))

    # -- differentiable: finite-difference sensitivity ----------------
    def _sensitivity(self, prompt, candidate, base_score):
        words = candidate.split()
        if len(words) < 2: return 0.0
        perturbed = ' '.join(words[:-1])
        pp = self._parse(perturbed)
        ps = self._parse(prompt)
        checks = self._structural_checks(ps, pp, prompt, perturbed)
        p_syn, _ = self._syndrome_score(checks)
        return abs(base_score - p_syn)

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
            dial = self._dialectic_score(ps, cs, prompt, cand)
            norm_ent = sum(ord(c) for c in cand) / max(len(cand) * 128, 1)
            init_s = 0.01 + 0.98 * (0.3 * min(len(cand)/100, 1.0) + 0.3 * norm_ent + 0.4 * syn)
            lyap = self._lyapunov(init_s)
            ch_sc = self._chaos_score(lyap)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            sens = self._sensitivity(prompt, cand, syn)
            stability = 1.0 / (1.0 + sens * 5)
            base = syn * 0.25 + dial * 0.20 + ch_sc * 0.10 + ncd_sim * 0.15 + stability * 0.10
            if not failed: base += 0.10
            if ps['nums'] and cs['nums']: base += 0.05
            score = float(np.clip(base, 0.0, 1.0))
            np_ = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn:.2f}({np_}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            parts.append(f'execution:dialectic={dial:.2f},chaos={ch_sc:.2f}')
            parts.append(f'execution:sensitivity={sens:.3f},stability={stability:.2f}')
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
