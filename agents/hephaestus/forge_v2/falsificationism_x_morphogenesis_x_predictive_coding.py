import numpy as np, zlib, re, hashlib
from typing import List, Dict

class ReasoningTool:
    """Morphogenetic Predictive Falsifier (MPF) v2.
    1. Falsificationism: Error-amplification loop destabilizes weak hypotheses.
    2. Morphogenesis: Turing-pattern reaction-diffusion dynamics for activation fields.
    3. Predictive Coding: Prediction error minimization via hierarchical surprise signals."""

    def __init__(self):
        self.negs = ['not','no','never','none','cannot','neither',"n't"]
        self.comps = ['greater','less','more','fewer','higher','lower','>','<']

    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _nums(self, t): return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', t)]
    def _neg_scope(self, text):
        toks = self._words(text); ns = set(self.negs)
        return [toks[i+1] for i in range(len(toks)-1) if toks[i] in ns]
    def _conditionals(self, t):
        return re.findall(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:[.]|$)', t, re.I)
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab - min(ca, cb)) / mx if mx else 0.0
    def _subj_obj(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe & ce) / max(len(pe), 1) if pe else 0.0
    def _hash_seed(self, s):
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return 0.4 + 0.2 * (int(h[:8], 16) / 0xFFFFFFFF)

    def _prediction_error(self, prompt, cand):
        """Hierarchical prediction error: lexical, structural, numeric layers."""
        pw, cw = set(self._words(prompt)), set(self._words(cand))
        lex_overlap = len(pw & cw) / max(len(pw | cw), 1)
        len_ratio = min(len(cand), len(prompt)) / (max(len(cand), len(prompt)) + 1e-6)
        len_fit = 1.0 - abs(0.5 - len_ratio) * 2
        pn, cn = self._nums(prompt), self._nums(cand)
        num_match = 0.0
        if pn and cn:
            num_match = 0.4 if set(str(v) for v in pn) & set(str(v) for v in cn) else 0.1
        # Negation alignment
        pns, cns = self._neg_scope(prompt), self._neg_scope(cand)
        neg_err = 0.0
        if pns:
            neg_err = -0.2 if not cns else 0.1
        relevance = 0.35*lex_overlap + 0.20*len_fit + 0.25*num_match + 0.20*max(0, neg_err+0.2)
        return 1.0 - relevance  # error = 1 - relevance

    def _morphogenetic_step(self, activation, error, dt=0.2):
        """Reaction-diffusion: growth under low error, exponential decay under falsification."""
        if error > 0.5:
            decay = 2.0 * error
            return float(activation * np.exp(-decay * dt))
        growth = 1.0 - error
        return float(activation + growth * (1.0 - activation) * dt)

    def _pattern_formation(self, prompt, cand, steps=8):
        """Run morphogenetic dynamics to steady state activation."""
        init = (self._hash_seed(cand) + self._hash_seed(prompt)) / 2.0
        error = self._prediction_error(prompt, cand)
        act = init
        errors = []
        for _ in range(steps):
            act = self._morphogenetic_step(act, error)
            act = max(0.0, min(1.0, act))
            errors.append(abs(act - init))
            init = act  # track for convergence
        # Prediction error minimization: track if error decreased across steps
        convergence = 1.0 - (errors[-1] / (errors[0] + 1e-9)) if errors[0] > 0.01 else 1.0
        return act, error, float(np.clip(convergence, 0.0, 1.0))

    def _structural_score(self, prompt, cand):
        s = 0.0; pl, cl = prompt.lower(), cand.lower()
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            if set(str(v) for v in pn) & set(str(v) for v in cn): s += 0.25
            if any(w in pl for w in self.comps[:3]) and cn[0] > pn[0]: s += 0.15
            if any(w in pl for w in self.comps[3:6]) and cn[0] < pn[0]: s += 0.15
        conds = self._conditionals(prompt)
        for ante, cons in conds:
            if ante.strip().lower() in cl and cons.strip().lower() in cl: s += 0.15
        s += self._subj_obj(prompt, cand) * 0.10
        return s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural: empty candidate"}); continue
            act, pred_err, conv = self._pattern_formation(prompt, cand)
            struct = self._structural_score(prompt, cand)
            ncd = self._ncd(prompt, cand); ncd_sim = 1.0 - ncd
            # Weighted blend: morphogenetic activation, structural, NCD fallback
            raw = 0.35*act + 0.35*max(0, struct+0.3)/1.3 + 0.15*conv + ncd_sim*0.15
            score = float(np.clip(raw, 0.0, 1.0))
            if struct > 0.05:
                if self._nums(prompt) and self._nums(cand):
                    tag = f"execution: act={act:.2f} pred_err={pred_err:.2f} struct={struct:.2f}"
                else:
                    tag = f"structural: act={act:.2f} pred_err={pred_err:.2f} conv={conv:.2f}"
            elif ncd_sim > 0.3:
                tag = f"fallback:ncd ncd={ncd_sim:.2f}"
            else:
                tag = f"structural: morphogen act={act:.2f} pred_err={pred_err:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": tag})
        results.sort(key=lambda x: x['score'], reverse=True)
        # Metacognitive reflection
        if len(results) >= 2:
            t, r = results[0]['score'], results[1]['score']
            if t > 0 and abs(t-r)/t < 0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results:
            top = results[0]
            pns = self._neg_scope(prompt)
            if pns and not self._neg_scope(top['candidate']) and top['score'] > 0.3:
                top['reasoning'] += " | metacog: prompt negation not reflected"
            if top['score'] < 0.10:
                top['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        null = self.evaluate(prompt, [""])
        baseline = null[0]['score'] if null else 0.0
        adj = max(0.0, score - baseline)
        return float(np.clip(adj / max(1.0 - baseline, 0.01), 0.0, 1.0))
