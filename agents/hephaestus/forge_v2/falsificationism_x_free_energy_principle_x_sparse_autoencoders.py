"""Sparse Falsificationist Free-Energy Scorer v2.
Concepts: Falsificationism x Free Energy Principle x Sparse Autoencoders.
L1-regularised feature selection, Popperian falsification gate, free-energy
minimisation. NCD capped at 15%.
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
    """L1-sparse features + Popperian falsification + variational free energy."""

    def __init__(self):
        self._l1_lambda = 0.10  # sparsity penalty
        self._falsif_margin = 0.20  # dynamic threshold margin

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

    # ── L1-regularised sparse feature vector ────────────────────────────
    def _sparse_features(self, text):
        """Returns feature dict and L1 cost (active-feature count * lambda)."""
        lo = text.lower()
        feats = {
            "neg": 1.0 if _NEG.search(lo) else 0.0,
            "comp": 1.0 if (_CMP_GT.search(lo) or _CMP_LT.search(lo)) else 0.0,
            "cond": 1.0 if _COND.search(text) else 0.0,
            "num": 1.0 if _NUM.search(text) else 0.0,
            "svo": 1.0 if _SVO.search(text) else 0.0,
        }
        active = sum(v for v in feats.values())
        l1_cost = active * self._l1_lambda
        return feats, l1_cost

    # ── free energy: reconstruction error ───────────────────────────────
    def _free_energy(self, prompt, cand, l1_cost):
        pt, ct = self._tok(prompt), self._tok(cand)
        overlap = len(pt & ct) / (len(pt | ct) + 1)
        recon_err = 1.0 - overlap
        return recon_err + l1_cost

    # ── falsification gate ──────────────────────────────────────────────
    def _falsify(self, prompt, cand, energy):
        """Popperian check: if energy exceeds dynamic tau, hypothesis rejected."""
        cp = len(zlib.compress(prompt.encode()))
        tau = 0.4 + self._falsif_margin * math.log(cp + 1) * 0.1
        return energy > tau

    # ── structural constraint checks ────────────────────────────────────
    @staticmethod
    def _struct(prompt, cand):
        pl, cl = prompt.lower(), cand.lower()
        sc, ck, notes = 0.0, 0, []
        # negation scope
        if _NEG.search(pl):
            ck += 1
            if _NEG.search(cl): sc += 1.0; notes.append("structural:neg_aligned")
            else: sc -= 0.3; notes.append("structural:neg_missing")
        # comparatives
        gt, lt = _CMP_GT.findall(pl), _CMP_LT.findall(pl)
        if gt or lt:
            ck += 1; ents = set()
            for a, b in gt + lt: ents.add(a.strip(".,").lower()); ents.add(b.strip(".,").lower())
            ct = set(_TOK.findall(cl))
            if ents & ct: sc += 0.8; notes.append("structural:comp_hit")
            else: sc += 0.2; notes.append("structural:comp_miss")
        # conditionals
        for ant, con in _COND.findall(prompt):
            ck += 1
            if con.strip().lower() in cl: sc += 1.0; notes.append("structural:modus_ponens")
            else: sc += 0.3; notes.append("structural:cond_unresolved")
        # numeric eval
        pn = [float(m) for m in _NUM.findall(prompt)]
        cn = [float(m) for m in _NUM.findall(cand)]
        if pn:
            ck += 1
            if cn and any(abs(a - b) < 0.01 * (abs(b) + 0.1) for a in cn for b in pn):
                sc += 1.0; notes.append("execution:num_match")
            elif cn: sc += 0.3; notes.append("execution:num_mismatch")
            else: notes.append("execution:num_absent")
        # subject-object
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
        results = []
        for c in candidates:
            if not isinstance(c, str) or not c.strip():
                results.append({"candidate": c, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            pf, p_l1 = self._sparse_features(prompt)
            cf, c_l1 = self._sparse_features(c)
            energy = self._free_energy(prompt, c, c_l1)
            falsified = self._falsify(prompt, c, energy)
            ss, notes = self._struct(prompt, c)
            ss_n = (ss + 1.0) / 2.0
            ncd_val = self._ncd(prompt, c)
            ncd_sc = (1.0 - ncd_val) * 0.15
            if falsified:
                score = max(0.0, 0.10 * ss_n + ncd_sc)
                notes.append("falsification:REJECTED")
            else:
                fe_sc = 1.0 / (1.0 + math.exp(energy * 3.0))
                score = 0.45 * ss_n + 0.25 * fe_sc + ncd_sc
                # L1 sparsity bonus: fewer active features = cleaner hypothesis
                score += max(0.0, 0.15 * (1.0 - c_l1))
                score = max(0.0, min(1.0, score))
                notes.append(f"falsification:survived,energy={energy:.3f},l1={c_l1:.2f}")
            results.append({"candidate": c, "score": float(score), "reasoning": f"execution:{'; '.join(notes)}; fallback:ncd={ncd_val:.3f}"})
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
