import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Fractal-Chaos Free Energy Engine (FCFE) v2.

    1. Fractal Geometry: Multi-scale self-similarity at 2 and 4 partitions.
       Scale consistency signals coherent structure.
    2. Chaos Theory: Lyapunov exponent from character divergence + logistic reservoir.
       Edge-of-chaos preferred; extreme order or noise penalized.
    3. Free Energy Principle: F = prediction_error + complexity - fractal_prior.
       Structural matching drives prediction error; chaos penalty is complexity.
    """

    def __init__(self):
        self.chaos_param = 3.99

    def _parse(self, text):
        t = text.lower()
        neg = any(n in t for n in ['not','no ','never','false',"n't",'impossible'])
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        comp = any(w in t for w in ['greater','less','more','fewer','larger','smaller',
                                     'highest','lowest','maximum','minimum'])
        cond = 'if ' in t and 'then' in t
        return {'neg': neg, 'nums': nums, 'comp': comp, 'cond': cond}

    def _structural_match(self, prompt, candidate):
        ps, cs = self._parse(prompt), self._parse(candidate)
        score, reasons = 0.0, []
        if ps['neg'] == cs['neg']: score += 0.2
        else: score -= 0.15; reasons.append('neg_mismatch')
        if ps['nums'] and cs['nums']:
            score += 0.25 * len(set(ps['nums']) & set(cs['nums'])) / max(len(set(ps['nums'])), 1)
            p_low = prompt.lower()
            if any(w in p_low for w in ['largest','greatest','max','more']):
                score += 0.2 if max(cs['nums']) >= max(ps['nums']) else -0.1
            elif any(w in p_low for w in ['smallest','least','min','fewer']):
                score += 0.2 if min(cs['nums']) <= min(ps['nums']) else -0.1
        elif ps['nums'] and not cs['nums']:
            score -= 0.15; reasons.append('missing_nums')
        if ps['cond']:
            if any(w in candidate.lower() for w in ['yes','no','true','false','then']):
                score += 0.1
            else: score -= 0.1; reasons.append('cond_unanswered')
        return float(np.clip(score, -0.5, 1.0)), reasons

    def _ncd_raw(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _fractal_multiscale(self, text):
        if len(text) < 8: return 0.5
        scores = []
        for n in [2, 4]:
            ch = max(len(text) // n, 1)
            parts = [text[i*ch:(i+1)*ch] for i in range(n)]
            sims = [1.0 - self._ncd_raw(parts[i], parts[j])
                    for i in range(len(parts)) for j in range(i+1, len(parts))]
            if sims: scores.append(float(np.mean(sims)))
        if not scores: return 0.5
        mean_s = float(np.mean(scores))
        consistency = 1.0 - float(np.std(scores)) if len(scores) > 1 else mean_s
        return float(np.clip(0.5 * mean_s + 0.5 * consistency, 0.0, 1.0))

    def _lyapunov(self, text):
        if len(text) < 3: return 0.0
        vals = np.array([ord(c) / 255.0 for c in text])
        return float(np.mean(np.log(np.abs(np.diff(vals)) + 1e-6)))

    def _logistic_reservoir(self, text):
        if not text: return 0.5
        seed = 0.1 + 0.8 * ((sum(ord(c) for c in text) / (len(text) * 128.0)) % 1.0)
        x = seed
        for _ in range(30):
            x = self.chaos_param * x * (1.0 - x)
            x = max(0.001, min(0.999, x))
        return x

    def _free_energy(self, prompt, candidate):
        struct, reasons = self._structural_match(prompt, candidate)
        fractal = self._fractal_multiscale(candidate)
        chaos_pen = abs(self._lyapunov(candidate) + 3.0) * 0.1
        ncd_err = self._ncd_raw(prompt, candidate)
        div = abs(self._logistic_reservoir(prompt) - self._logistic_reservoir(candidate))
        pred_err = 0.5 * (1.0 - struct) + 0.15 * ncd_err
        fe = pred_err + chaos_pen - fractal * 0.2
        raw = -fe + 0.05 * div
        return raw, struct, fractal, chaos_pen, ncd_err, reasons

    def _reflect(self, results):
        if len(results) < 2: return results
        if results[0]['score'] - results[1]['score'] < 0.05:
            for r in results[:2]: r['reasoning'] += ' | metacog:tie_within_5pct'
        if any(w in results[0]['reasoning'] for w in ['neg_mismatch','missing_nums']):
            results[0]['reasoning'] += ' | metacog:structural_parse_warning'
        return results

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list): return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates: return []
        raw_data = [self._free_energy(prompt, c) for c in candidates]
        raws = np.array([d[0] for d in raw_data])
        if raws.max() - raws.min() > 1e-9:
            normed = (raws - raws.min()) / (raws.max() - raws.min())
        else:
            normed = np.full_like(raws, 0.5)
        results = []
        for i, (cand, (_, struct, fractal, chaos, ncd_err, s_reasons)) in enumerate(
                zip(candidates, raw_data)):
            score = float(np.clip(normed[i], 0.0, 1.0))
            parts = [f'execution:structural={struct:.2f},fractal={fractal:.2f}',
                     f'execution:chaos_penalty={chaos:.3f}']
            if s_reasons: parts.append(f'structural:issues=[{",".join(s_reasons)}]')
            parts.append(f'fallback:ncd={ncd_err:.2f}(15%)')
            results.append({'candidate': cand, 'score': round(score, 4),
                            'reasoning': ' | '.join(parts)})
        results.sort(key=lambda x: x['score'], reverse=True)
        return self._reflect(results)

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        null_score = self.evaluate(prompt, [''])[0]['score'] if prompt else 0.0
        conf = max(0.0, score - null_score) / max(1.0 - null_score, 1e-6)
        return float(np.clip(round(conf, 4), 0.0, 1.0))
