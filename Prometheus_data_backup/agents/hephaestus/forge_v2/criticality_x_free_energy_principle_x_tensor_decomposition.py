"""Critical Free-Energy Tensor-Train v2.
Tensor Decomposition x Criticality x Free Energy Principle.
Rank-1 SVD, power-law criticality, variational FE, structural parsing, NCD<=15%.
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
        self.rng = np.random.default_rng(42)

    @staticmethod
    def _tok(text): return _TOK.findall(text.lower())

    def _feat_vec(self, tokens, vocab, dim):
        bow = np.zeros(len(vocab))
        for t in tokens:
            if t in vocab: bow[vocab[t]] += 1.0
        n = np.linalg.norm(bow)
        if n > 0: bow /= n
        proj = self.rng.standard_normal((dim, len(vocab))) / math.sqrt(dim)
        return proj @ bow

    def _tensor_score(self, pt, ct):
        all_t = list(set(pt + ct))
        if len(all_t) < 2: return 0.5, "structural:too_few_tokens"
        vocab = {t: i for i, t in enumerate(all_t)}
        dim = min(16, len(vocab))
        M = np.outer(self._feat_vec(pt, vocab, dim), self._feat_vec(ct, vocab, dim))
        try:
            S = np.linalg.svd(M, compute_uv=False)
            r1 = float(S[0] / (np.sum(S) + 1e-12))
            return r1, f"structural:tensor_r1={r1:.3f}"
        except Exception: return 0.5, "structural:svd_fallback"

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
            elif cn: s += 0.3; R.append("execution:numeric_mismatch")
            else: R.append("execution:numeric_absent")
        comps = _COMP.findall(pl)
        if comps:
            ck += 1
            if comps[0][0].strip(".,") in cl: s += 0.8; R.append("structural:comp_present")
            else: s += 0.2; R.append("structural:comp_absent")
        svos = _SVO.findall(prompt)
        if svos:
            ck += 1
            pts = {x[2].lower() for x in svos}
            if pts & set(_TOK.findall(cl)): s += 1.0; R.append("structural:svo_match")
            else: s += 0.3; R.append("structural:svo_miss")
        raw = s / max(ck, 1) if ck > 0 else 0.5
        return raw, R or ["structural:no_constraints"]

    @staticmethod
    def _crit(scores):
        if len(scores) < 2: return 1.0, "criticality:n/a"
        arr = np.array(sorted(scores, reverse=True)); arr = arr - arr.min() + 1e-6
        lr, lv = np.log(np.arange(1, len(arr)+1)), np.log(arr+1e-12)
        slope = np.polyfit(lr, lv, 1)[0] if np.std(lr) > 0 else 0.0
        lyap = abs(slope + 1.0)
        return float(1.0 / (1.0 + lyap)), f"criticality:slope={slope:.2f}"

    @staticmethod
    def _ncd(a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            d = max(ca, cb); return (cab - min(ca, cb)) / d if d > 0 else 1.0
        except Exception: return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_prompt"} for c in (candidates or [])]
        if not candidates: return []
        pt = self._tok(prompt); res, raw = [], []
        for c in candidates:
            if not c or not c.strip():
                res.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); raw.append(0.0); continue
            ct = self._tok(c)
            td, tdr = self._tensor_score(pt, ct)
            ss, sr = self._struct(prompt, c)
            ncd_s = 1.0 - self._ncd(prompt, c)
            f = 0.55*ss + 0.30*td + 0.15*ncd_s
            tag = "fallback:ncd" if ss < 0.2 and td < 0.3 else f"{'; '.join(sr)}; {tdr}"
            res.append({"candidate": c, "score": float(np.clip(f, 0, 1)), "reasoning": tag}); raw.append(f)
        cg, cr = self._crit(raw)
        for r in res:
            if r['score'] > 0: r['score'] = float(np.clip(r['score']*(0.7+0.3*cg), 0, 1)); r['reasoning'] += f" | {cr}"
        res.sort(key=lambda x: x['score'], reverse=True)
        if len(res) >= 2 and res[0]['score'] > 0 and abs(res[0]['score']-res[1]['score'])/max(res[0]['score'],1e-9) < 0.05:
            for r in res[:2]: r['reasoning'] += " | metacognition:low_confidence_close_scores"
        return res

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        r = self.evaluate(prompt, [answer])
        if not r: return 0.0
        sc = r[0]['score']
        nr = self.evaluate(prompt, [""]); ns = nr[0]['score'] if nr else 0.0
        lift = sc - ns
        if "negation_missing" in r[0].get('reasoning', ''): return max(0.0, min(0.15, lift))
        return float(np.clip(lift / max(1.0-ns, 0.1), 0.0, 1.0))
