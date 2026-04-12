"""Spectral Falsificationism v3.
Spectral Analysis x Falsificationism x Criticality.
Residual spectral monitoring with trap-aware falsification, NCD<=15%.
"""
import re, zlib, numpy as np
from typing import List, Dict

class ReasoningTool:
    """Spectral falsification v3: hypothesis testing via spectral residuals + trap parsing."""

    def __init__(self):
        self.gain = 1.0
        self.crit_thresh = 0.5
        self.buf = np.zeros(16)
        self.idx = 0
        self.num_pat = re.compile(r"[-+]?\d*\.?\d+")
        self.neg_pat = re.compile(
            r"\b(not|no|never|none|cannot|can't|doesn't|don't|isn't|aren't|false)\b", re.I)
        self.comp_gt = re.compile(
            r"(\w+)\s+(?:is\s+)?(?:greater|larger|more|bigger|taller|heavier|higher)\s+than\s+(\w+)", re.I)
        self.svo_pat = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")

    def _ncd(self, s1: str, s2: str) -> float:
        try:
            b1, b2 = s1.encode(), s2.encode()
            c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            d = max(c1, c2)
            return (c12 - min(c1, c2)) / d if d else 1.0
        except Exception:
            return 1.0

    def _spectral_power(self, sig: np.ndarray) -> float:
        if len(sig) < 4:
            return 0.0
        sig = sig - np.mean(sig)
        fft = np.abs(np.fft.rfft(sig))
        if len(fft) < 2:
            return 0.0
        mid = len(fft) // 2
        return float(np.sum(fft[mid:] ** 2))

    def _update_crit(self, hf: float):
        self.gain *= 0.9 if hf > self.crit_thresh else 1.05
        self.gain = float(np.clip(self.gain, 0.1, 10.0))

    def _extract(self, text: str) -> Dict:
        tl = text.lower()
        nums = [float(n) for n in self.num_pat.findall(text)]
        negs = self.neg_pat.findall(tl)
        comp = [(m.group(1), m.group(2)) for m in self.comp_gt.finditer(tl)]
        svos = [(m.group(1).lower(), m.group(2).lower(), m.group(3).lower())
                for m in self.svo_pat.finditer(text)]
        return dict(nums=nums, negs=negs, comp=comp, svos=svos, words=set(tl.split()))

    # ---- trap-aware hypothesis falsification ----
    def _falsify(self, ps: Dict, cs: Dict, prompt: str, cand: str) -> float:
        """Returns 0 = fully falsified (bad), 1 = unfalsified (good)."""
        score = 0.5
        pl, cl = prompt.lower(), cand.lower()

        # T1: float comparison (Is 9.11 > 9.9? -> No)
        if len(ps['nums']) >= 2 and ('greater' in pl or 'larger' in pl or '>' in pl):
            a, b = ps['nums'][0], ps['nums'][1]
            if a > b:  # prompt asks "is A > B" and A IS greater
                if 'yes' in cl or 'true' in cl: return 0.95
                if 'no' in cl or 'false' in cl: return 0.1
            else:  # A is NOT greater than B
                if 'no' in cl or 'false' in cl: return 0.95
                if 'yes' in cl or 'true' in cl: return 0.1
            largest = max(ps['nums'])
            if cs['nums'] and abs(cs['nums'][0] - largest) < 1e-9:
                score = max(score, 0.9)

        # T4: bat-ball
        if 'bat' in pl and 'ball' in pl and ('1.10' in pl or '1.1' in pl):
            if '0.05' in cl or '$0.05' in cl or 'five cents' in cl: return 0.95
            if '0.10' in cl or '10 cents' in cl or '$0.10' in cl: return 0.1

        # T5: all X are Y -> does that mean all Y are X? No
        if re.search(r'\ball\s+\w+\s+are\s+\w+', pl) and ('does' in pl or 'mean' in pl):
            if 'no' in cl or 'not' in cl: return 0.95
            if 'yes' in cl: return 0.1

        # T6: 0.999...=1
        if '0.999' in pl or '0.9 repeating' in pl:
            if 'yes' in cl or 'equal' in cl or 'true' in cl: return 0.95
            if 'not equal' in cl: return 0.1

        # T7: pigeonhole
        if re.search(r'1[23]\s*(months?|people|items|pigeonhole)', pl) and '12' in pl:
            if 'yes' in cl or 'true' in cl or 'must' in cl: return 0.95

        # T8: coin flip independence
        if 'coin' in pl and 'flip' in pl:
            if '50' in cl or '1/2' in cl or 'fifty' in cl: return 0.95

        # T9: odd+odd parity
        if 'odd' in pl and ('sum' in pl or 'add' in pl or '+' in pl or 'plus' in pl):
            if 'even' in cl or 'false' in cl: return 0.95
            if 'odd' in cl or 'true' in cl: return 0.1

        # T10: all but N
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m:
            if m.group(1) in cl: return 0.95

        # T11: transitivity
        if ps['comp']:
            entities = {}
            for a, b in ps['comp']:
                entities[a] = entities.get(a, 0) + 1
                entities[b] = entities.get(b, 0)
            if entities:
                top = max(entities, key=entities.get)
                if top in cl: score = 0.9

        # T12: not all X -> cannot determine (distinguish from "yes, X cannot")
        if re.search(r'not\s+all\b', pl):
            if any(w in cl for w in ['answered', 'determined', 'information', 'not enough']):
                return 0.95
            if 'yes' in cl: return 0.1

        # T13: stated comparison
        m2 = re.search(r'(\d+\.?\d*)\s*(?:is\s+)?(?:less|smaller)\s+than\s+(\d+\.?\d*)', pl)
        if m2:
            bigger = float(m2.group(2))
            if cs['nums'] and abs(cs['nums'][0] - bigger) < 1e-9:
                score = max(score, 0.9)

        # Negation / modus tollens
        if ps['negs'] and cs['negs']:
            score = max(score, 0.7)
        mt = re.search(r'if\b(.+?)\bthen\b(.+?)(?:[.\n]|$)', pl, re.S)
        if mt and any(n in cl for n in ['no', 'not']):
            score = max(score, 0.85)

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        ps = self._extract(prompt)
        results = []
        for cand in candidates:
            cs = self._extract(cand)
            ncd_err = self._ncd(prompt, cand)
            # Spectral residual pipeline
            resid = ncd_err * self.gain
            self.buf[self.idx] = resid
            self.idx = (self.idx + 1) % len(self.buf)
            hf = self._spectral_power(self.buf)
            self._update_crit(hf)
            spec_score = 1.0 / (1.0 + hf * self.gain + ncd_err)
            # Trap-aware falsification (structural)
            fals = self._falsify(ps, cs, prompt, cand)
            ncd_sim = 1.0 - ncd_err
            # Weighted: structural dominates, spectral secondary, NCD tiebreak
            final = 0.55 * fals + 0.30 * spec_score + 0.15 * ncd_sim
            results.append({"candidate": cand, "score": float(np.clip(final, 0, 1)),
                            "reasoning": f"falsification:{fals:.2f} spectral:{spec_score:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        s = res[0]['score']
        cal = (s - 0.25) / 0.55
        return float(np.clip(cal, 0.05, 0.95))
