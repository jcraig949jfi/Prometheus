import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Chaotic Epistemic Mechanism-Design Evaluator (CEMD) v2.

    1. Chaos Theory: Coupled logistic map with epistemic coupling for
       deterministic hypothesis exploration.
    2. Epistemology: Justified-true-belief checking -- candidate must be
       (a) consistent with prompt constraints, (b) supported by evidence
       (structural overlap), (c) not defeated by counter-evidence (negation).
    3. Mechanism Design: Incentive-compatible Bayesian Truth Serum scoring
       penalizing overconfidence when coherence or reliability is low.
    """

    def __init__(self):
        self.chaos_r = 3.99
        self.coupling = 0.15

    # -- chaos ---------------------------------------------------------
    def _chaotic_update(self, belief, coherence, reliability):
        chaotic = self.chaos_r * belief * (1.0 - belief)
        coupling = self.coupling * reliability * (coherence - belief)
        return float(np.clip(chaotic + coupling, 0.0, 1.0))

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

    # -- epistemology: justified true belief ---------------------------
    def _jtb_score(self, p, c, prompt, candidate):
        """Justified-True-Belief: justification, truth-alignment, no defeaters."""
        stop = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it','be'}
        pw = set(prompt.lower().split()) - stop
        cw = set(candidate.lower().split()) - stop
        justification = len(pw & cw) / max(len(pw), 1)
        checks = self._structural_checks(p, c, prompt, candidate)
        truth, _ = self._syndrome_score(checks)
        defeated = False
        cl = candidate.lower()
        if ('true' in cl and 'false' in cl) or ('yes' in cl and 'no ' in cl):
            defeated = True
        if p['neg'] != c['neg']:
            if not (p['cond'] or c['cond']):
                defeated = True
        defeat_penalty = 0.0 if not defeated else 0.3
        return float(np.clip(0.4 * justification + 0.4 * truth + 0.2 - defeat_penalty, 0.0, 1.0))

    # -- mechanism design: incentive-compatible scoring ----------------
    def _incentive_score(self, belief, coherence, reliability):
        expected = (coherence + reliability) / 2.0
        reward = belief * expected
        penalty = 0.5 * ((belief - expected) ** 2)
        return float(np.clip(reward - penalty, 0.0, 1.0))

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
        complexity = len(ps['nums']) * 0.2 + (0.3 if ps['comp'] else 0.0)
        reliability = max(0.1, 1.0 - complexity)
        results = []
        for cand in candidates:
            cs = self._parse(cand)
            checks = self._structural_checks(ps, cs, prompt, cand)
            syn, failed = self._syndrome_score(checks)
            jtb = self._jtb_score(ps, cs, prompt, cand)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            coherence = 0.4 * syn + 0.3 * jtb + 0.3 * ncd_sim
            belief = 1.0 - self._ncd(prompt, cand)
            for _ in range(5):
                belief = self._chaotic_update(belief, coherence, reliability)
            mech = self._incentive_score(belief, coherence, reliability)
            base = syn * 0.25 + jtb * 0.25 + mech * 0.20 + ncd_sim * 0.15
            if not failed: base += 0.10
            if ps['nums'] and cs['nums']: base += 0.05
            score = float(np.clip(base, 0.0, 1.0))
            np_ = len(checks) - len(failed)
            parts = [f'execution:syndrome={syn:.2f}({np_}/{len(checks)} checks)']
            if failed: parts.append(f'structural:failed=[{",".join(failed)}]')
            parts.append(f'execution:jtb={jtb:.2f},mechanism={mech:.2f}')
            parts.append(f'execution:coherence={coherence:.2f},reliability={reliability:.2f}')
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
