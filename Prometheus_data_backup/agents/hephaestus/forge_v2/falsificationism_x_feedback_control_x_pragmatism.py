"""Falsificationist PID-Pragmatic Scorer v2.
Concepts: Falsificationism x Feedback Control x Pragmatism.
Popperian falsification, PID-style error correction, Gricean maxims
(quantity, quality, relevance, manner). NCD capped at 15%.
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
    """PID error correction + Popperian falsification + Gricean pragmatics."""

    def __init__(self):
        self._kp, self._ki, self._kd = 1.2, 0.08, 0.04
        self._integral, self._last_err = 0.0, 0.0

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

    # ── PID error correction ────────────────────────────────────────────
    def _pid(self, error):
        p = self._kp * error
        self._integral += error
        i = self._ki * self._integral
        d = self._kd * (error - self._last_err)
        self._last_err = error
        return max(-0.4, min(0.4, p + i + d))

    # ── Gricean maxims ──────────────────────────────────────────────────
    @staticmethod
    def _gricean(prompt, cand):
        pt, ct = ReasoningTool._tok(prompt), ReasoningTool._tok(cand)
        notes = []
        # Quantity: informative but not excessive
        ratio = len(ct) / (len(pt) + 1)
        quantity = 1.0 - abs(1.0 - ratio) * 0.5
        quantity = max(0.0, min(1.0, quantity))
        notes.append(f"gricean:quantity={quantity:.2f}")
        # Quality: overlap indicates truthful relevance
        quality = len(pt & ct) / (len(pt | ct) + 1)
        notes.append(f"gricean:quality={quality:.2f}")
        # Relevance: prompt keywords appearing in candidate
        relevance = len(pt & ct) / (len(pt) + 1)
        notes.append(f"gricean:relevance={relevance:.2f}")
        # Manner: brevity + clarity (penalise extreme length)
        manner = math.exp(-0.3 * abs(len(cand) - len(prompt)) / (len(prompt) + 1))
        notes.append(f"gricean:manner={manner:.2f}")
        sc = 0.25 * quantity + 0.30 * quality + 0.25 * relevance + 0.20 * manner
        return sc, notes

    # ── falsification gate ──────────────────────────────────────────────
    @staticmethod
    def _falsify(prompt, cand):
        pl, cl = prompt.lower(), cand.lower()
        penalty = 0.0
        if _NEG.search(pl) and not _NEG.search(cl): penalty += 0.25
        pn = [float(m) for m in _NUM.findall(prompt)]
        cn = [float(m) for m in _NUM.findall(cand)]
        if pn and (_CMP_GT.search(pl) or _CMP_LT.search(pl)) and not cn: penalty += 0.30
        return max(0.0, 1.0 - penalty)

    # ── structural constraint checks ────────────────────────────────────
    @staticmethod
    def _struct(prompt, cand):
        pl, cl = prompt.lower(), cand.lower()
        sc, ck, notes = 0.0, 0, []
        if _NEG.search(pl):
            ck += 1
            if _NEG.search(cl): sc += 1.0; notes.append("structural:neg_aligned")
            else: sc -= 0.3; notes.append("structural:neg_missing")
        gt, lt = _CMP_GT.findall(pl), _CMP_LT.findall(pl)
        if gt or lt:
            ck += 1; ents = set()
            for a, b in gt + lt: ents.add(a.strip(".,").lower()); ents.add(b.strip(".,").lower())
            ct = set(_TOK.findall(cl))
            if ents & ct: sc += 0.8; notes.append("structural:comp_hit")
            else: sc += 0.2; notes.append("structural:comp_miss")
        for ant, con in _COND.findall(prompt):
            ck += 1
            if con.strip().lower() in cl: sc += 1.0; notes.append("structural:modus_ponens")
            else: sc += 0.3; notes.append("structural:cond_unresolved")
        pn = [float(m) for m in _NUM.findall(prompt)]
        cn = [float(m) for m in _NUM.findall(cand)]
        if pn:
            ck += 1
            if cn and any(abs(a - b) < 0.01 * (abs(b) + 0.1) for a in cn for b in pn):
                sc += 1.0; notes.append("execution:num_match")
            elif cn: sc += 0.3; notes.append("execution:num_mismatch")
            else: notes.append("execution:num_absent")
        for m in _SVO.finditer(prompt):
            ck += 1; subj, obj_ = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", pl): sc += 1.0 if obj_ in cl else -0.3
            elif re.search(r"who.+\w+ed", pl): sc += 1.0 if subj in cl else -0.3
            notes.append("structural:svo")
        return (sc / max(ck, 1) if ck else 0.5), notes or ["structural:no_constraints"]

    # ── metacognitive reflection ────────────────────────────────────────
    @staticmethod
    def _meta_tag(results):
        if len(results) >= 2 and abs(results[0]["score"] - results[1]["score"]) < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognition:low_confidence_close_scores"

    # ── public I/O ──────────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not prompt.strip(): return []
        if not isinstance(candidates, list) or not candidates: return []
        self._integral, self._last_err = 0.0, 0.0  # reset PID per batch
        # pre-compute population error for PID
        errs = []
        for c in (candidates or []):
            if isinstance(c, str) and c.strip():
                g, _ = self._gricean(prompt, c)
                errs.append(1.0 - g)
        avg_err = sum(errs) / len(errs) if errs else 0.5
        gain = self._pid(avg_err)
        results = []
        for c in candidates:
            if not isinstance(c, str) or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            ss, s_notes = self._struct(prompt, c)
            ss_n = (ss + 1.0) / 2.0
            grice, g_notes = self._gricean(prompt, c)
            fals = self._falsify(prompt, c)
            ncd_val = self._ncd(prompt, c)
            ncd_sc = (1.0 - ncd_val) * 0.15
            base = 0.40 * ss_n * fals + 0.30 * grice + ncd_sc
            adjusted = base * (1.0 - gain * 0.3)
            score = max(0.0, min(1.0, adjusted))
            tag = (f"execution:{'; '.join(s_notes)}; {'; '.join(g_notes)}; "
                   f"falsification:{fals:.2f}; pid_gain={gain:.3f}; fallback:ncd={ncd_val:.3f}")
            results.append({"candidate": c, "score": float(score), "reasoning": tag})
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
