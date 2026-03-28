"""Information-Guided Sparse-Feature Bandit v2.
Information Theory x Multi-Armed Bandits x Sparse Autoencoders.
L1-sparse features, UCB1 with structural reward, MI via conditional entropy, NCD<=15%.
"""
import re, zlib, math
import numpy as np
from typing import List, Dict
from collections import Counter

_NEG = re.compile(r"\b(not|no|never|none|neither|without|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", re.I)
_COND = re.compile(r"\bif\b(.+?)\bthen\b(.+?)(?:[.\n]|$)", re.I | re.S)
_COMP = re.compile(r"(\S+)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher)\s+than\s+(\S+)", re.I)
_NUM = re.compile(r"[-+]?\d*\.?\d+")
_SVO = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")
_TOK = re.compile(r"[a-z0-9]+")

class ReasoningTool:
    def __init__(self):
        self._counts = Counter(); self._rewards = Counter(); self._total = 0

    @staticmethod
    def _tok(text): return _TOK.findall(text.lower())

    def _sparse_encode(self, text, k=8):
        tokens = self._tok(text); feats = Counter()
        for t in tokens: feats[("w", t)] += 1.0
        for i in range(len(tokens)-1): feats[("b", tokens[i], tokens[i+1])] += 0.5
        tl = text.lower()
        if _NEG.search(tl): feats[("s", "neg")] += 2.0
        if _COND.search(text): feats[("s", "cond")] += 2.0
        if _COMP.search(tl): feats[("s", "comp")] += 2.0
        for n in _NUM.findall(text): feats[("n", n)] += 2.0
        for s in _SVO.findall(text): feats[("svo", s[0].lower(), s[2].lower())] += 1.5
        return {f[0] for f in feats.most_common(k)} if feats else set()

    def _mi(self, feat):
        n = self._counts.get(feat, 0)
        if n < 1: return 0.0
        p = self._rewards.get(feat, 0.0) / n
        if p <= 0 or p >= 1: return 1.0
        return max(0.0, 1.0 + p*math.log2(p) + (1-p)*math.log2(1-p))

    def _ucb(self, feat):
        n = self._counts.get(feat, 0)
        if n == 0: return 2.0
        return self._mi(feat) + math.sqrt(2.0*math.log(self._total+2)/n)

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
                s += 0.8; R.append("structural:comp_entity_present")
            else: s += 0.2; R.append("structural:comp_absent")
        svos = _SVO.findall(prompt)
        if svos:
            ck += 1
            pts = {x[2].lower() for x in svos}
            if pts & set(_TOK.findall(cl)): s += 1.0; R.append("structural:svo_match")
            else: s += 0.3; R.append("structural:svo_miss")
        return (s/max(ck,1) if ck > 0 else 0.5), R or ["structural:no_constraints"]

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
        pf = self._sparse_encode(prompt); results, scores = [], []
        for c in candidates:
            if not c or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"})
                scores.append(0.0); continue
            cf = self._sparse_encode(c); shared = pf & cf
            bs = min(1.0, sum(self._ucb(f) for f in shared)/(len(cf)+1)) if shared else 0.0
            ss, sr = self._struct(prompt, c)
            ns = 1.0 - self._ncd(prompt, c)
            f = 0.45*ss + 0.40*bs + 0.15*ns
            fb = ss < 0.2 and bs < 0.2
            tag = "fallback:ncd" if fb else f"{'; '.join(sr)}; bandit_ucb={bs:.2f}"
            results.append({"candidate": c, "score": float(np.clip(f,0,1)), "reasoning": tag})
            scores.append(f)
        # Update bandit
        for c in candidates:
            if not c or not c.strip(): continue
            cf = self._sparse_encode(c); shared = pf & cf
            rw, _ = self._struct(prompt, c)
            for feat in shared:
                self._counts[feat] += 1; self._rewards[feat] += rw; self._total += 1
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
