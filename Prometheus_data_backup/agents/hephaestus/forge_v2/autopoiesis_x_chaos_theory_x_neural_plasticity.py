"""Autopoietic Chaotic Plasticity Scorer v2.
Concepts: Autopoiesis x Chaos Theory x Neural Plasticity.
Self-maintenance checks, logistic-map exploration, Hebbian reinforcement.
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
    """Autopoietic self-maintenance + chaotic exploration + Hebbian learning."""

    def __init__(self):
        self._r = 3.99  # logistic map chaos parameter

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

    # ── chaotic tie-breaker (logistic map) ──────────────────────────────
    def _chaos_perturb(self, seed_str, n):
        h = zlib.crc32(seed_str.encode()) & 0xFFFFFFFF
        x = (h % 997 + 1) / 1000.0
        vals = []
        for _ in range(n):
            x = self._r * x * (1.0 - x)
            vals.append((x - 0.5) * 0.04)  # small deterministic perturbation
        return vals

    # ── Hebbian plasticity score ────────────────────────────────────────
    @staticmethod
    def _hebbian(prompt, cand):
        pl, cl = prompt.lower(), cand.lower()
        sc, notes = 0.0, []
        # negation alignment (fire-together / wire-together)
        pn, cn = bool(_NEG.search(pl)), bool(_NEG.search(cl))
        if pn == cn: sc += 0.30; notes.append("structural:neg_aligned")
        elif pn: sc -= 0.25; notes.append("structural:neg_missing")
        # comparative alignment
        pc = bool(_CMP_GT.search(pl) or _CMP_LT.search(pl))
        cc = bool(_CMP_GT.search(cl) or _CMP_LT.search(cl))
        if pc and cc: sc += 0.20; notes.append("structural:comp_aligned")
        elif pc: sc -= 0.15; notes.append("structural:comp_missing")
        # numeric reward
        pnums = [float(m) for m in _NUM.findall(prompt)]
        cnums = [float(m) for m in _NUM.findall(cand)]
        if pnums:
            if cnums and any(abs(a - b) < 0.01 * (abs(b) + 0.1) for a in cnums for b in pnums):
                sc += 0.35; notes.append("execution:num_match")
            elif cnums: sc += 0.10; notes.append("execution:num_mismatch")
            else: sc -= 0.10; notes.append("execution:num_absent")
        return sc, notes

    # ── structural constraint checks ────────────────────────────────────
    @staticmethod
    def _struct(prompt, cand):
        pl, cl = prompt.lower(), cand.lower()
        sc, ck, notes = 0.0, 0, []
        if _NEG.search(pl):
            ck += 1
            if _NEG.search(cl): sc += 1.0
            else: sc -= 0.3
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
            elif cn: sc += 0.3
            else: notes.append("execution:num_absent")
        for m in _SVO.finditer(prompt):
            ck += 1; subj, obj_ = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", pl): sc += 1.0 if obj_ in cl else -0.3
            elif re.search(r"who.+\w+ed", pl): sc += 1.0 if subj in cl else -0.3
            notes.append("structural:svo")
        return (sc / max(ck, 1) if ck else 0.5), notes or ["structural:no_constraints"]

    # ── autopoietic self-maintenance ────────────────────────────────────
    @staticmethod
    def _self_maintain(struct_sc, hebb_sc):
        """Check whether the reasoning chain sustains itself.
        If both structural and hebbian signals agree, the chain is viable.
        If they diverge, flag instability and dampen."""
        coherence = 1.0 - abs(struct_sc - hebb_sc)
        viable = coherence > 0.4
        if not viable:
            # tighten: average the two signals to stabilise
            return (struct_sc + hebb_sc) / 2.0, False, f"autopoiesis:unstable,coh={coherence:.2f}"
        return max(struct_sc, hebb_sc), True, f"autopoiesis:viable,coh={coherence:.2f}"

    # ── metacognitive reflection ────────────────────────────────────────
    @staticmethod
    def _meta_tag(results):
        if len(results) >= 2 and abs(results[0]["score"] - results[1]["score"]) < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognition:low_confidence_close_scores"

    # ── public I/O ──────────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not prompt.strip(): return []
        if not isinstance(candidates, list) or not candidates: return []
        perturbations = self._chaos_perturb(prompt, len(candidates))
        results = []
        for i, c in enumerate(candidates):
            if not isinstance(c, str) or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            ss, s_notes = self._struct(prompt, c)
            ss_n = (ss + 1.0) / 2.0
            hebb, h_notes = self._hebbian(prompt, c)
            hebb_n = max(0.0, min(1.0, (hebb + 1.0) / 2.0))
            merged, viable, auto_r = self._self_maintain(ss_n, hebb_n)
            ncd_val = self._ncd(prompt, c)
            ncd_sc = (1.0 - ncd_val) * 0.15
            base = 0.50 * merged + 0.20 * hebb_n + ncd_sc
            if not viable: base *= 0.85  # autopoietic damping
            score = max(0.0, min(1.0, base + perturbations[i]))
            tag = (f"execution:{'; '.join(s_notes)}; {'; '.join(h_notes)}; "
                   f"{auto_r}; chaos_p={perturbations[i]:.4f}; fallback:ncd={ncd_val:.3f}")
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
