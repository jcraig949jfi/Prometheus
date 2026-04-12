"""Critical NAS Free-Energy Scorer v2.
Concepts: Criticality x Free Energy Principle x Neural Architecture Search.
Dynamic NAS weight selection, architecture-evaluation scoring, edge-of-chaos
sensitivity. NCD capped at 15%.
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
    """NAS architecture search over weight vectors + criticality + free energy."""

    def __init__(self): pass

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

    # ── free energy (variational divergence) ────────────────────────────
    @staticmethod
    def _free_energy(prompt, cand):
        pt, ct = ReasoningTool._tok(prompt), ReasoningTool._tok(cand)
        if not pt: return 1.0, "execution:empty_prompt"
        overlap = len(pt & ct) / (len(pt | ct) + 1)
        ncd_raw = ReasoningTool._ncd(prompt, cand)
        energy = ncd_raw * 0.6 + (1.0 - overlap) * 0.4
        return energy, f"execution:fe={energy:.3f}"

    # ── criticality (edge-of-chaos sensitivity) ─────────────────────────
    @staticmethod
    def _criticality(cand):
        lo = cand.lower()
        sc = 0.0
        if _NEG.search(lo): sc += 0.30
        if _CMP_GT.search(lo) or _CMP_LT.search(lo): sc += 0.25
        if _COND.search(cand): sc += 0.20
        if _NUM.search(cand): sc += 0.15
        sc += min(1.0, len(cand) / 60.0) * 0.10
        return min(1.0, sc), f"execution:crit={min(1.0,sc):.2f}"

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

    # ── NAS: architecture-evaluation scoring ────────────────────────────
    @staticmethod
    def _nas_weights(ss, fe, crit):
        """Select best weight vector (architecture) by structural fitness."""
        archs = [
            (0.45, 0.25, 0.15, 0.15),  # balanced
            (0.55, 0.20, 0.10, 0.15),  # struct-dominant
            (0.30, 0.35, 0.20, 0.15),  # energy-dominant
            (0.35, 0.20, 0.30, 0.15),  # criticality-dominant
        ]
        best, best_fitness = archs[0], -1.0
        for ws, wf, wc, wn in archs:
            # architecture fitness = weighted score + penalty for over-relying on NCD
            fitness = ws * ss + wf * (1.0 - fe) + wc * crit
            if fitness > best_fitness:
                best_fitness = fitness; best = (ws, wf, wc, wn)
        return best

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
            ss, s_notes = self._struct(prompt, c)
            ss_n = (ss + 1.0) / 2.0
            fe, fe_r = self._free_energy(prompt, c)
            fe_sc = 1.0 / (1.0 + math.exp(fe * 3.0))
            crit, cr_r = self._criticality(c)
            ncd_val = self._ncd(prompt, c)
            ncd_sc = (1.0 - ncd_val) * 0.15
            ws, wf, wc, wn = self._nas_weights(ss_n, fe, crit)
            score = ws * ss_n + wf * fe_sc + wc * crit + wn * ncd_sc / 0.15 * ncd_sc
            # re-normalise: NCD contribution bounded
            score = ws * ss_n + wf * fe_sc + wc * crit + ncd_sc
            score = max(0.0, min(1.0, score))
            tag = (f"execution:{'; '.join(s_notes)}; {fe_r}; {cr_r}; "
                   f"nas:w=[{ws:.2f},{wf:.2f},{wc:.2f},{wn:.2f}]; fallback:ncd={ncd_val:.3f}")
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
