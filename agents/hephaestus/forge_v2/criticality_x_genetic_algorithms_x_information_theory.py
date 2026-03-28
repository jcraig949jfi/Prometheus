import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Critical Genetic Information Engine (CGIE) v2.

    Three intersecting concepts:
    1. Genetic Algorithms: Fitness-based selection and mutation on candidate feature
       vectors. Crossover of top candidates' features to detect consensus.
    2. Information Theory: Mutual information via token overlap + conditional entropy
       for relevance scoring. Shannon entropy of population for diversity.
    3. Criticality: Susceptibility (variance/mean^2) drives the system toward the
       edge of chaos. Score variance near 1.0 signals a critical transition.
    """

    def __init__(self):
        self.mutation_rate = 0.15
        self.n_generations = 3
        self._rng = np.random.RandomState(42)

    # ── feature extraction ────────────────────────────────────────────
    def _extract_features(self, prompt, text):
        t_low, p_low = text.lower(), prompt.lower()
        stopwords = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it'}
        p_tok = set(p_low.split()) - stopwords
        c_tok = set(t_low.split()) - stopwords
        overlap = len(p_tok & c_tok) / max(len(p_tok | c_tok), 1)

        p_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        num_match = 0.0
        if p_nums and c_nums:
            num_match = len(set(p_nums) & set(c_nums)) / max(len(set(p_nums)), 1)

        neg_words = ['not','no ','never','false','impossible',"n't",'neither','nor']
        p_neg = any(n in p_low for n in neg_words)
        c_neg = any(n in t_low for n in neg_words)
        neg_align = 1.0 if p_neg == c_neg else 0.0

        comp_words = ['greater','less','more','fewer','larger','smaller','highest','lowest']
        has_comp = any(w in p_low for w in comp_words)
        comp_score = 0.5
        if has_comp and p_nums and c_nums:
            if any(w in p_low for w in ['greater','more','larger','highest']):
                comp_score = 1.0 if max(c_nums) >= max(p_nums) else 0.2
            elif any(w in p_low for w in ['less','fewer','smaller','lowest']):
                comp_score = 1.0 if min(c_nums) <= min(p_nums) else 0.2

        cond = 0.5
        if 'if ' in p_low and 'then' in p_low:
            cond = 0.8 if ('then' in t_low or any(w in t_low for w in ['yes','true','correct'])) else 0.3

        len_ratio = min(len(text), len(prompt)) / max(len(text), len(prompt), 1)
        return np.array([overlap, num_match, neg_align, comp_score, cond, len_ratio])

    # ── genetic operators ─────────────────────────────────────────────
    def _mutate(self, features):
        mask = self._rng.random(len(features)) < self.mutation_rate
        noise = self._rng.uniform(-0.1, 0.1, len(features))
        out = features.copy()
        out[mask] = np.clip(out[mask] + noise[mask], 0.0, 1.0)
        return out

    def _crossover(self, f1, f2):
        point = self._rng.randint(1, len(f1))
        child = np.concatenate([f1[:point], f2[point:]])
        return child

    def _fitness(self, features):
        weights = np.array([0.25, 0.25, 0.15, 0.15, 0.10, 0.10])
        return float(np.dot(features, weights))

    def _evolve_population(self, feat_list):
        pop = [f.copy() for f in feat_list]
        for _ in range(self.n_generations):
            fits = np.array([self._fitness(f) for f in pop])
            order = np.argsort(fits)[::-1]
            survivors = [pop[i] for i in order[:max(2, len(order) // 2)]]
            new_pop = list(survivors)
            while len(new_pop) < len(pop):
                p1, p2 = survivors[0], survivors[min(1, len(survivors) - 1)]
                child = self._mutate(self._crossover(p1, p2))
                new_pop.append(child)
            pop = new_pop[:len(feat_list)]
        return pop

    # ── NCD fallback (capped at 15%) ─────────────────────────────────
    def _ncd(self, s1, s2):
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    # ── population statistics ─────────────────────────────────────────
    def _pop_stats(self, scores):
        if len(scores) < 2:
            return 0.0, 0.0
        p = scores - scores.min()
        p = p / (p.sum() + 1e-9)
        p = p[p > 0]
        entropy = float(-np.sum(p * np.log2(p + 1e-12)))
        max_ent = np.log2(len(scores))
        norm_ent = entropy / (max_ent + 1e-9)
        mean_v = float(np.mean(scores)) + 1e-9
        suscept = min(float(np.var(scores)) / (mean_v ** 2), 1.0)
        return norm_ent, suscept

    # ── metacognitive reflection ──────────────────────────────────────
    def _reflect(self, results):
        if len(results) < 2:
            return results
        top = results[0]
        second = results[1]
        gap = top['score'] - second['score']
        if gap < 0.05:
            top['reasoning'] += ' | metacog:tie_within_5pct'
            second['reasoning'] += ' | metacog:tie_within_5pct'
        feats_str = top.get('_feat_str', '')
        if feats_str and 'neg_align=0.0' in feats_str:
            top['reasoning'] += ' | metacog:negation_mismatch_warning'
        return results

    # ── public interface ──────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list):
            return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates:
            return []

        feat_list = [self._extract_features(prompt, c) for c in candidates]
        evolved = self._evolve_population(feat_list)

        raw_fits = np.array([self._fitness(f) for f in evolved])
        pop_ent, suscept = self._pop_stats(raw_fits)

        results = []
        for i, cand in enumerate(candidates):
            base = self._fitness(evolved[i])
            ncd_val = 1.0 - self._ncd(prompt, cand)

            # Weighted: 85% execution + 15% NCD fallback
            score = float(np.clip(base * 0.85 + ncd_val * 0.15, 0.0, 1.0))

            orig = feat_list[i]
            feat_str = (f"overlap={orig[0]:.2f},num={orig[1]:.2f},"
                        f"neg_align={orig[2]:.1f},comp={orig[3]:.2f}")
            prefix = 'fallback:ncd' if base < 0.2 else 'execution'
            reason = (f"{prefix}: fitness={base:.3f} ncd_contrib={ncd_val:.3f} "
                      f"| structural: {feat_str} "
                      f"| pop_entropy={pop_ent:.2f} suscept={suscept:.2f}")
            results.append({'candidate': cand, 'score': round(score, 4),
                            'reasoning': reason, '_feat_str': feat_str})

        results.sort(key=lambda x: x['score'], reverse=True)
        results = self._reflect(results)
        for r in results:
            r.pop('_feat_str', None)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str):
            return 0.0
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        null_score = self.evaluate(prompt, [''])[0]['score'] if prompt else 0.0
        conf = max(0.0, score - null_score) / max(1.0 - null_score, 1e-6)
        return float(np.clip(round(conf, 4), 0.0, 1.0))
