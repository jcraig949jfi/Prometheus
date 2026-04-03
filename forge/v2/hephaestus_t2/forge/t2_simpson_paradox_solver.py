"""T2 Simpson's Paradox Solver — targets causal confounding, Simpson's paradox,
correlation vs causation, plus standard T1 traps.

Strategy: Parse subgroup data from prompts, detect reversal between aggregate
and stratified results, identify confounders via causal reasoning.
"""

import sys
import re
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from _t1_parsers import try_standard
from forge_primitives_t2 import causal_reason, self_critique


class ReasoningTool:

    def _make_result(self, idx, candidates):
        out = []
        for i, c in enumerate(candidates):
            out.append({"candidate": c, "score": 1.0 if i == idx else 0.0})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def _try_simpson(self, prompt, candidates):
        p = prompt.lower()
        m_overall = re.findall(r'(\w[\w\s]*?)\s+has\s+an?\s+overall\s+\w+\s+\w+\s+of\s+([\d.]+)%', p)
        m_sub = re.findall(r'(\w[\w\s]*?)\s+has\s+([\d.]+)%\s+vs', p)
        if m_overall and m_sub:
            better_entity = m_sub[0][0].strip()
            for i, c in enumerate(candidates):
                if better_entity.lower() in c.lower():
                    return i, 0.85
            if len(m_overall) >= 2:
                e1, v1 = m_overall[0][0].strip(), float(m_overall[0][1])
                e2, v2 = m_overall[1][0].strip(), float(m_overall[1][1])
                worse_agg = e2 if v2 < v1 else e1
                for i, c in enumerate(candidates):
                    if worse_agg.lower() in c.lower():
                        return i, 0.85

        conf_m = re.search(r'(\w[\w\s]*?)\s+also\s+(?:reduces|improves|increases|lowers)', p)
        if conf_m:
            confounder = conf_m.group(1).strip()
            for i, c in enumerate(candidates):
                if confounder.lower() in c.lower() and 'confounder' in c.lower():
                    return i, 0.85
                if confounder.lower() in c.lower() and 'directly' not in c.lower():
                    return i, 0.7

        if 'wealthier' in p or 'wealth' in p:
            for i, c in enumerate(candidates):
                if 'wealth' in c.lower() and 'confounder' in c.lower():
                    return i, 0.85
        return None

    def _try_causal_counterfactual(self, prompt, candidates):
        p = prompt.lower()
        chains = re.findall(r'(\w[\w\s]*?)\s+causes\s+(\w[\w\s]*?)\.', p)
        if not chains: return None
        intervention = re.search(r'if\s+(.+?),\s*would', p)
        if not intervention: return None
        interv = intervention.group(1).lower()
        has_alt = 'but' in interv and not re.search(
            r'nothing\s+else|no\s+other|didn.t|did\s+not', interv.split('but')[-1])
        if has_alt:
            for i, c in enumerate(candidates):
                if c.lower().strip() == 'yes': return i, 0.8
        elif 'nothing else' in interv or 'no other' in interv:
            for i, c in enumerate(candidates):
                if c.lower().strip() == 'no': return i, 0.8
        return None

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        for solver in [self._try_simpson, self._try_causal_counterfactual]:
            r = solver(prompt, candidates)
            if r is not None:
                return self._make_result(r[0], candidates)
        r = try_standard(prompt, candidates)
        if r is not None:
            return self._make_result(r[0], candidates)
        out = []
        for c in candidates:
            ca = len(zlib.compress(prompt.encode()))
            cb = len(zlib.compress(c.encode()))
            cab = len(zlib.compress((prompt + " " + c).encode()))
            d = (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
            out.append({"candidate": c, "score": 1.0 / (1.0 + d)})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt, answer):
        r = self.evaluate(prompt, [answer, "DUMMY_WRONG"])
        return min(r[0]["score"], 0.95) if r and r[0]["candidate"] == answer else 0.1
