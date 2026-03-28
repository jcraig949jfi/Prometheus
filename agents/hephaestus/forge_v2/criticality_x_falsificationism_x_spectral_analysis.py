import numpy as np
import re
import zlib

class ReasoningTool:
    """
    Spectral Falsification Engine (SFE) v2.

    Three intersecting concepts:
    1. Spectral Analysis: Builds a feature co-occurrence matrix from prompt/candidate
       pairs, computes eigenvalues to detect dominant structural modes. High spectral
       gap signals coherent structure; degenerate eigenvalues signal ambiguity.
    2. Falsificationism: Each candidate is treated as a hypothesis. Structural tests
       attempt to falsify it (negation mismatch, numeric inconsistency, conditional
       violation). Unfalsified candidates score higher.
    3. Criticality: Gain parameter tunes sensitivity. SOC feedback loop: high
       falsification power dampens gain, low falsification amplifies. System
       self-tunes to the edge between credulity and hyper-skepticism.
    """

    def __init__(self):
        self.gain = 1.0
        self.history = []

    # ── structural parsing ────────────────────────────────────────────
    def _parse(self, text):
        t = text.lower()
        neg = any(n in t for n in ['not','no ','never','false',"n't",'impossible','neither'])
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        comp = any(w in t for w in ['greater','less','more','fewer','larger','smaller',
                                     'highest','lowest','maximum','minimum'])
        cond = 'if ' in t and 'then' in t
        subj_tokens = re.findall(r'[A-Z][a-z]+', text)
        return {'neg': neg, 'nums': nums, 'comp': comp, 'cond': cond,
                'subjects': subj_tokens}

    # ── spectral analysis: eigenvalue computation ─────────────────────
    def _spectral_features(self, prompt, candidate):
        p_tok = set(re.findall(r'[a-z]+', prompt.lower()))
        c_tok = set(re.findall(r'[a-z]+', candidate.lower()))
        all_tok = sorted(p_tok | c_tok)
        if len(all_tok) < 2:
            return 0.5, 0.0
        n = min(len(all_tok), 20)
        all_tok = all_tok[:n]
        tok_idx = {t: i for i, t in enumerate(all_tok)}

        # Build co-occurrence matrix from both texts
        mat = np.zeros((n, n), dtype=float)
        for text in [prompt.lower(), candidate.lower()]:
            words = [w for w in re.findall(r'[a-z]+', text) if w in tok_idx]
            for i in range(len(words) - 1):
                a, b = tok_idx[words[i]], tok_idx[words[i + 1]]
                mat[a, b] += 1.0
                mat[b, a] += 1.0

        # Eigenvalue analysis
        try:
            eigvals = np.linalg.eigvalsh(mat)
            eigvals = np.sort(np.abs(eigvals))[::-1]
            top = eigvals[0] if len(eigvals) > 0 else 0.0
            second = eigvals[1] if len(eigvals) > 1 else 0.0
            spectral_gap = (top - second) / (top + 1e-9)
            spectral_energy = float(np.sum(eigvals[:3])) / (float(np.sum(eigvals)) + 1e-9)
        except Exception:
            spectral_gap, spectral_energy = 0.5, 0.5
        return float(np.clip(spectral_gap, 0.0, 1.0)), float(np.clip(spectral_energy, 0.0, 1.0))

    # ── falsification tests ───────────────────────────────────────────
    def _falsify(self, p_struct, c_struct, prompt, candidate):
        penalties = 0.0
        reasons = []
        if p_struct['neg'] != c_struct['neg']:
            penalties += 0.25
            reasons.append('neg_mismatch')
        if p_struct['nums'] and c_struct['nums']:
            p_low = prompt.lower()
            if any(w in p_low for w in ['largest','greatest','max','more','bigger']):
                if max(c_struct['nums']) < max(p_struct['nums']):
                    penalties += 0.2
                    reasons.append('numeric_max_fail')
            elif any(w in p_low for w in ['smallest','least','min','fewer','less']):
                if min(c_struct['nums']) > min(p_struct['nums']):
                    penalties += 0.2
                    reasons.append('numeric_min_fail')
        elif p_struct['nums'] and not c_struct['nums']:
            penalties += 0.15
            reasons.append('missing_numbers')
        if p_struct['cond'] and not c_struct['cond']:
            if not any(w in candidate.lower() for w in ['yes','no','true','false']):
                penalties += 0.15
                reasons.append('conditional_unanswered')
        return min(penalties, 1.0), reasons

    # ── NCD fallback (capped 15%) ─────────────────────────────────────
    def _ncd(self, s1, s2):
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    # ── criticality: SOC gain control ─────────────────────────────────
    def _update_gain(self, falsif_strength):
        if falsif_strength > 0.3:
            self.gain *= 0.9
        else:
            self.gain *= 1.05
        self.gain = float(np.clip(self.gain, 0.2, 5.0))

    # ── metacognitive reflection ──────────────────────────────────────
    def _reflect(self, results):
        if len(results) < 2:
            return results
        gap = results[0]['score'] - results[1]['score']
        if gap < 0.05:
            for r in results[:2]:
                r['reasoning'] += ' | metacog:tie_within_5pct'
        top = results[0]
        if 'neg_mismatch' in top['reasoning']:
            top['reasoning'] += ' | metacog:negation_inconsistency_warning'
        return results

    # ── public interface ──────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not isinstance(prompt, str) or not isinstance(candidates, list):
            return []
        candidates = [c for c in candidates if isinstance(c, str)]
        if not candidates:
            return []

        p_struct = self._parse(prompt)
        results = []
        for cand in candidates:
            c_struct = self._parse(cand)
            spec_gap, spec_energy = self._spectral_features(prompt, cand)
            falsif_pen, falsif_reasons = self._falsify(p_struct, c_struct, prompt, cand)
            self._update_gain(falsif_pen)
            ncd_sim = 1.0 - self._ncd(prompt, cand)

            # Composite: spectral coherence (30%) + unfalsified (30%) + spec energy (15%)
            # + ncd fallback (15%) + gain bonus (10%)
            structural = (1.0 - falsif_pen)
            gain_norm = float(np.clip(self.gain / 5.0, 0.0, 1.0))
            score = (spec_gap * 0.25 + structural * 0.30 + spec_energy * 0.15
                     + ncd_sim * 0.15 + gain_norm * 0.05 + 0.1 * (1.0 if not falsif_reasons else 0.0))
            score = float(np.clip(score, 0.0, 1.0))

            parts = []
            parts.append(f'execution:spectral_gap={spec_gap:.2f},energy={spec_energy:.2f}')
            if falsif_reasons:
                parts.append(f'structural:falsified=[{",".join(falsif_reasons)}]')
            else:
                parts.append('execution:unfalsified')
            parts.append(f'fallback:ncd={ncd_sim:.2f}(15%)')
            parts.append(f'execution:gain={self.gain:.2f}')
            results.append({'candidate': cand, 'score': round(score, 4),
                            'reasoning': ' | '.join(parts)})

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
