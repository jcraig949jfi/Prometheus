"""Neuromodulated Critical Reservoir v2.
Phase Transitions x Criticality x Neuromodulation.
Spectral-radius reservoir, context-dependent gain, bifurcation detection, NCD<=15%.
"""
import re, zlib, math
import numpy as np
from typing import List, Dict

_NEG = re.compile(r"\b(not|no|never|none|neither|without|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", re.I)
_COND = re.compile(r"\bif\b(.+?)\bthen\b(.+?)(?:[.\n]|$)", re.I | re.S)
_COMP = re.compile(r"(\S+)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher)\s+than\s+(\S+)", re.I)
_NUM = re.compile(r"[-+]?\d*\.?\d+")
_SVO = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")
_TOK = re.compile(r"[a-z0-9]+")

class ReasoningTool:
    def __init__(self):
        rng = np.random.default_rng(42)
        self.N = 48
        W = rng.standard_normal((self.N, self.N)) * 0.5
        U, S, Vt = np.linalg.svd(W)
        self.reservoir = U @ np.diag(S / np.max(S) * 0.99) @ Vt
        self.readout = rng.standard_normal(self.N)
        self.readout /= np.linalg.norm(self.readout)

    @staticmethod
    def _tok(text): return _TOK.findall(text.lower())

    def _vec(self, text):
        v = np.zeros(self.N)
        for t in self._tok(text): v[hash(t) % self.N] += 1.0
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def _run(self, state, gain, steps=5):
        c = state.copy()
        for _ in range(steps): c = np.tanh(gain * (self.reservoir @ c))
        return c

    @staticmethod
    def _struct(prompt, cand):
        s, ck, R = 0.0, 0, []
        pl, cl = prompt.lower(), cand.lower()
        if _NEG.search(pl):
            ck += 1
            if _NEG.search(cl): s += 1.0; R.append("structural:negation_aligned")
            else: R.append("structural:negation_missing")
        conds = _COND.findall(prompt)
        if conds:
            ck += 1
            if conds[0][1].strip().rstrip('.').lower() in cl: s += 1.0; R.append("structural:modus_ponens")
            else: s += 0.3; R.append("structural:conditional_unresolved")
        pn = [float(n) for n in _NUM.findall(prompt)]
        cn = [float(n) for n in _NUM.findall(cand)]
        if pn:
            ck += 1
            if cn and any(abs(a-b) < 0.01*(abs(b)+0.1) for a in cn for b in pn):
                s += 1.0; R.append("execution:numeric_match")
            elif cn: s += 0.4; R.append("execution:numeric_mismatch")
            else: R.append("execution:numeric_absent")
        comps = _COMP.findall(pl)
        if comps:
            ck += 1
            if comps[0][0].strip(".,") in cl or comps[0][1].strip(".,") in cl:
                s += 0.8; R.append("structural:comp_present")
            else: s += 0.2; R.append("structural:comp_absent")
        svos = _SVO.findall(prompt)
        if svos:
            ck += 1
            pts = {x[2].lower() for x in svos}
            if pts & set(_TOK.findall(cl)): s += 1.0; R.append("structural:svo_match")
            else: s += 0.3; R.append("structural:svo_miss")
        return (s/max(ck,1) if ck > 0 else 0.5), R or ["structural:no_constraints"]

    @staticmethod
    def _gain(ss, var):
        if var < 0.01: base, ph = 1.4, "subcritical"
        elif var > 0.1: base, ph = 0.8, "supercritical"
        else: base, ph = 1.0, "critical"
        if ss > 0.7: g = base * 1.1
        elif ss < 0.3: g = base * 1.3
        else: g = base
        return g, ph

    @staticmethod
    def _ncd(a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            d = max(ca, cb); return (cab-min(ca,cb))/d if d > 0 else 1.0
        except Exception: return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_prompt"} for c in (candidates or [])]
        if not candidates: return []
        pv = self._vec(prompt)
        # Phase 1: structural + initial reservoir
        p1 = []
        for c in candidates:
            if not c or not c.strip(): p1.append((0.0, 0.0, ["structural:empty_candidate"])); continue
            ss, sr = self._struct(prompt, c)
            cv = self._vec(c); st = (pv + cv) / 2.0
            rr = float(np.dot(self._run(st, 1.0), self.readout))
            p1.append((ss, rr, sr))
        # Phase 2: neuromodulation
        rscores = [p[1] for p in p1]
        var = float(np.var(rscores)) if len(rscores) > 1 else 0.0
        avg_ss = np.mean([p[0] for p in p1])
        gain, phase = self._gain(avg_ss, var)
        results = []
        for i, c in enumerate(candidates):
            ss, _, reasons = p1[i]
            if not c or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            cv = self._vec(c); st = (pv + cv) / 2.0
            rm = float(np.dot(self._run(st, gain), self.readout))
            rn = 1.0 / (1.0 + math.exp(-rm * 2.0))
            ns = 1.0 - self._ncd(prompt, c)
            f = 0.50*ss + 0.35*rn + 0.15*ns
            fb = ss < 0.2 and rn < 0.3
            tag = "fallback:ncd" if fb else f"{'; '.join(reasons)}; reservoir:gain={gain:.2f},phase={phase}"
            results.append({"candidate": c, "score": float(np.clip(f,0,1)), "reasoning": tag})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results) >= 2 and results[0]['score'] > 0 and abs(results[0]['score']-results[1]['score'])/max(results[0]['score'],1e-9) < 0.05:
            for r in results[:2]: r['reasoning'] += " | metacognition:low_confidence_close_scores"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        r = self.evaluate(prompt, [answer])
        if not r: return 0.0
        sc = r[0]['score']
        nr = self.evaluate(prompt, [""]); ns = nr[0]['score'] if nr else 0.0
        lift = sc - ns
        if "negation_missing" in r[0].get('reasoning', ''): return max(0.0, min(0.15, lift))
        return float(np.clip(lift/max(1.0-ns, 0.1), 0.0, 1.0))
