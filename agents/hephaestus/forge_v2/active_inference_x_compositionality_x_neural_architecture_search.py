"""Compositional Active NAS v2.
Active Inference x Compositionality x Neural Architecture Search.
Expected Free Energy, clause decomposition, dynamic NAS weights, NCD<=15%.
"""
import re, zlib, math
from typing import List, Dict

_NEG = re.compile(r"\b(not|no|never|none|neither|without|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", re.I)
_COND = re.compile(r"\bif\b(.+?)\bthen\b(.+?)(?:[.\n]|$)", re.I | re.S)
_COMP_GT = re.compile(r"(\S+)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher)\s+than\s+(\S+)", re.I)
_COMP_LT = re.compile(r"(\S+)\s+(?:is\s+)?(?:less|smaller|fewer|shorter|lower)\s+than\s+(\S+)", re.I)
_NUM = re.compile(r"[-+]?\d*\.?\d+")
_SVO = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")
_TOK = re.compile(r"[a-z0-9]+")
_CLAUSE = re.compile(r"[,;]\s*(?:and|but|or|because|since|although|which|that)\s+", re.I)

class ReasoningTool:
    def __init__(self): pass

    @staticmethod
    def _tok(text): return _TOK.findall(text.lower())

    @staticmethod
    def _comp_score(text):
        clauses = _CLAUSE.split(text); nc = max(len(clauses), 1)
        tokens = _TOK.findall(text.lower())
        if not tokens: return 0.0, "compositionality:empty"
        freq = {}
        for t in tokens: freq[t] = freq.get(t, 0) + 1
        reuse = sum(1 for c in freq.values() if c > 1)
        div = len(freq) / (len(tokens) + 1)
        sc = reuse*0.1 + div*0.5 + min(nc*0.15, 0.5) - math.log(len(tokens)+1)*0.04
        return max(0.0, min(1.0, sc)), f"compositionality:cl={nc},reuse={reuse},div={div:.2f}"

    @staticmethod
    def _efe(prompt, cand):
        pt = set(_TOK.findall(prompt.lower())); ct = _TOK.findall(cand.lower())
        if not ct: return 0.0, "active_inference:empty"
        overlap = sum(1 for t in ct if t in pt)
        fit = (overlap+1) / (len(pt)+1); ambig = 1.0 - fit
        cpx = math.log(len(ct)+1) * 0.05
        epist = min(len(set(ct)-pt)*0.05, 0.3)
        G = ambig + cpx - epist
        sc = 1.0 / (1.0 + math.exp(G*3))
        return sc, f"active_inference:fit={fit:.2f},ambig={ambig:.2f}"

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
        gt, lt = _COMP_GT.findall(pl), _COMP_LT.findall(pl)
        if gt or lt:
            ck += 1; ents = set()
            for a, b in gt + lt: ents.add(a.strip(".,").lower()); ents.add(b.strip(".,").lower())
            if ents & set(_TOK.findall(cl)): s += 0.8; R.append("structural:comp_present")
            else: s += 0.2; R.append("structural:comp_absent")
        svos = _SVO.findall(prompt)
        if svos:
            ck += 1; pts = {x[2].lower() for x in svos}
            if pts & set(_TOK.findall(cl)): s += 1.0; R.append("structural:svo_match")
            else: s += 0.3; R.append("structural:svo_miss")
        return (s/max(ck,1) if ck > 0 else 0.5), R or ["structural:no_constraints"]

    @staticmethod
    def _nas_w(ss, cs, ai):
        ws, wc, wa, wn = 0.40, 0.25, 0.20, 0.15
        best = max([("s", ss), ("c", cs), ("a", ai)], key=lambda x: x[1])
        if best[0] == "s" and ss > 0.6: ws += 0.10; wc -= 0.05; wa -= 0.05
        elif best[0] == "c" and cs > 0.6: wc += 0.10; ws -= 0.05; wa -= 0.05
        elif best[0] == "a" and ai > 0.6: wa += 0.10; ws -= 0.05; wc -= 0.05
        return ws, wc, wa, wn

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
        results = []
        for c in candidates:
            if not c or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            ss, sr = self._struct(prompt, c)
            cs, cr = self._comp_score(c)
            ai, ar = self._efe(prompt, c)
            ns = 1.0 - self._ncd(prompt, c)
            ws, wc, wa, wn = self._nas_w(ss, cs, ai)
            f = ws*ss + wc*cs + wa*ai + wn*ns
            fb = ss < 0.2 and ai < 0.3
            tag = "fallback:ncd" if fb else f"{'; '.join(sr)}; {cr}; {ar}; nas:w=[{ws:.2f},{wc:.2f},{wa:.2f},{wn:.2f}]"
            results.append({"candidate": c, "score": float(max(0.0, min(1.0, f))), "reasoning": tag})
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
        return float(max(0.0, min(1.0, lift/max(1.0-ns, 0.1))))
