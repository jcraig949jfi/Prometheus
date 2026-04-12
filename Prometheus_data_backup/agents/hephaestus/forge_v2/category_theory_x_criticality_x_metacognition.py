"""Critical Functor-Metacognitive Scorer v2.
Concepts: Category Theory x Criticality x Metacognition.
Morphism-based feature transforms, power-law cascading, metacognitive reflection.
NCD capped at 15%.
"""
import math, re, zlib

_NEG = re.compile(r"\b(not|no|never|none|neither|without|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", re.I)
_CMP_GT = re.compile(r"(\S+)\s+(?:is\s+)?(?:greater|larger|more|bigger|higher|taller|faster|better|older)\s+than\s+(\S+)", re.I)
_CMP_LT = re.compile(r"(\S+)\s+(?:is\s+)?(?:less|smaller|fewer|shorter|lower|slower|worse|younger)\s+than\s+(\S+)", re.I)
_COND = re.compile(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)")
_NUM = re.compile(r"[-+]?\d*\.?\d+")
_SVO = re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+(?:the\s+)?(\w+)")
_TOK = re.compile(r"[a-z0-9]+")


class ReasoningTool:
    """Category-theoretic functors + criticality cascading + metacognitive audit."""

    def __init__(self):
        self._crit_exp = 3.0  # power-law exponent for critical cascade

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _tok(t): return set(_TOK.findall(t.lower()))

    @staticmethod
    def _ncd(a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba + bb))
            d = max(ca, cb); return (cab - min(ca, cb)) / d if d else 1.0
        except Exception: return 1.0

    # ── feature extraction (Objects in category H) ──────────────────────
    @staticmethod
    def _features(text):
        lo = text.lower()
        negs = len(_NEG.findall(lo))
        comps = len(_CMP_GT.findall(lo)) + len(_CMP_LT.findall(lo))
        conds = len(_COND.findall(text))
        nums = [float(m) for m in _NUM.findall(text)]
        toks = _TOK.findall(lo)
        return {"neg": negs, "comp": comps, "cond": conds, "nums": nums,
                "len": len(text), "vocab": len(set(toks)), "tok": set(toks)}

    # ── morphism: structural constraint checks ──────────────────────────
    def _morphism_score(self, prompt, cand):
        pf, cf = self._features(prompt), self._features(cand)
        pl, cl = prompt.lower(), cand.lower()
        sc, ck, notes = 0.0, 0, []
        # negation scope
        if pf["neg"]:
            ck += 1
            if cf["neg"]: sc += 1.0; notes.append("structural:neg_aligned")
            else: sc -= 0.3; notes.append("structural:neg_missing")
        # comparatives
        gt = _CMP_GT.findall(pl); lt = _CMP_LT.findall(pl)
        if gt or lt:
            ck += 1; order = {}
            for a, b in gt + lt: order.setdefault(a.strip(".,").lower(), set()).add(b.strip(".,").lower())
            if order and (order.keys() & cf["tok"]): sc += 0.8; notes.append("structural:comp_hit")
            else: sc += 0.2; notes.append("structural:comp_miss")
        # conditionals (modus ponens/tollens)
        for ant, con in _COND.findall(prompt):
            ck += 1
            conl = con.strip().lower()
            if conl in cl: sc += 1.0; notes.append("structural:modus_ponens")
            else: sc += 0.3; notes.append("structural:cond_unresolved")
        # numeric eval
        if pf["nums"]:
            ck += 1
            if cf["nums"] and any(abs(a - b) < 0.01 * (abs(b) + 0.1) for a in cf["nums"] for b in pf["nums"]):
                sc += 1.0; notes.append("execution:num_match")
            elif cf["nums"]: sc += 0.3; notes.append("execution:num_mismatch")
            else: notes.append("execution:num_absent")
        # subject-object
        for m in _SVO.finditer(prompt):
            ck += 1; subj, obj_ = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", pl): sc += 1.0 if obj_ in cl else -0.3
            elif re.search(r"who.+\w+ed", pl): sc += 1.0 if subj in cl else -0.3
            notes.append("structural:svo")
        return (sc / max(ck, 1) if ck else 0.5), notes or ["structural:no_constraints"]

    # ── natural transformation: jaccard coverage ────────────────────────
    @staticmethod
    def _jaccard(prompt, cand):
        pt, ct = ReasoningTool._tok(prompt), ReasoningTool._tok(cand)
        u = pt | ct
        return len(pt & ct) / len(u) if u else 0.0

    # ── criticality cascade (power-law penalty) ─────────────────────────
    def _cascade(self, base, tension):
        if tension > 0.5: return base * (1.0 - tension) ** self._crit_exp
        return base * (1.0 - 0.5 * tension)

    # ── metacognitive reflection ────────────────────────────────────────
    @staticmethod
    def _meta_tag(results):
        if len(results) >= 2:
            gap = abs(results[0]["score"] - results[1]["score"])
            if gap < 0.05:
                for r in results[:2]: r["reasoning"] += " | metacognition:low_confidence_close_scores"

    # ── public I/O ──────────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not prompt.strip(): return []
        if not isinstance(candidates, list) or not candidates: return []
        results = []
        for c in candidates:
            if not isinstance(c, str) or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            morph, notes = self._morphism_score(prompt, c)
            morph_n = (morph + 1.0) / 2.0  # normalise [-1,1] -> [0,1]
            jac = self._jaccard(prompt, c)
            ncd_val = self._ncd(prompt, c)
            ncd_sc = (1.0 - ncd_val) * 0.15  # NCD capped at 15%
            base = 0.50 * morph_n + 0.35 * jac
            tension = 1.0 - morph_n
            final = self._cascade(base, tension) + ncd_sc
            final = max(0.0, min(1.0, final))
            tag = f"execution:morph={morph:.2f},jac={jac:.2f}; {'; '.join(notes)}; fallback:ncd={ncd_val:.3f}"
            results.append({"candidate": c, "score": float(final), "reasoning": tag})
        results.sort(key=lambda x: x["score"], reverse=True)
        self._meta_tag(results)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        null = "This is a null baseline answer with no information."
        res = self.evaluate(prompt, [answer, null])
        if not res: return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        return float(max(0.0, min(1.0, 0.5 + (ans_sc - null_sc) * 0.5)))
