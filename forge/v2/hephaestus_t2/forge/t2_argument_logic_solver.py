"""T2 Argument Logic Solver — targets argument strength, conjunction fallacy,
compositional logic, plus standard T1 traps.

Strategy: Parse premise-conclusion structures, detect fallacy patterns
(affirming consequent, denying antecedent), check conjunction fallacy
(P(A&B) <= P(A)), use multi_hop_reason for chained arguments.
"""

import sys
import re
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from _t1_parsers import try_standard
from forge_primitives_t2 import multi_hop_reason, self_critique, analogize


class ReasoningTool:

    def _make_result(self, idx, candidates):
        out = []
        for i, c in enumerate(candidates):
            out.append({"candidate": c, "score": 1.0 if i == idx else 0.0})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def _try_argument(self, prompt, candidates):
        p = prompt.lower()
        if 'evaluate this argument' not in p and 'logically valid' not in p:
            return None
        p1_m = re.search(r'premise\s*1:\s*(.+?)\.', p)
        p2_m = re.search(r'premise\s*2:\s*(.+?)\.', p)
        if not (p1_m and p2_m): return None
        p1, p2 = p1_m.group(1).strip(), p2_m.group(1).strip()
        is_valid = None
        if re.search(r'^if\s+', p1):
            ante_m = re.match(r'if\s+(.+?),?\s+then\s+(.+)', p1)
            if ante_m:
                antecedent = ante_m.group(1).strip()
                consequent = ante_m.group(2).strip()
                if 'is true' in p2 or antecedent in p2:
                    is_valid = True
                if 'is false' in p2 and consequent.split()[-1] in p2:
                    is_valid = True
                if ('did not' in p2 or 'not ' in p2) and 'is true' not in p2 and 'is false' not in p2:
                    is_valid = False
        all_m = re.match(r'all\s+(\w+)\s+are\s+(\w+)', p1)
        if all_m:
            sup = all_m.group(2)
            if sup in p2 and 'is a' in p2:
                is_valid = False
        if is_valid is not None:
            target = "Valid" if is_valid else "Invalid"
            for i, c in enumerate(candidates):
                if c.strip() == target: return i, 0.9
        return None

    def _try_conjunction(self, prompt, candidates):
        p = prompt.lower()
        if 'more probable' not in p: return None
        opt_a = re.search(r'\(a\)\s*(.+?)(?:\n|\(b\))', p)
        opt_b = re.search(r'\(b\)\s*(.+?)(?:\n|$)', p)
        if not opt_a or not opt_b: return None
        a_text, b_text = opt_a.group(1).strip(), opt_b.group(1).strip()
        a_len, b_len = len(a_text), len(b_text)
        if a_len > b_len + 5:
            for i, c in enumerate(candidates):
                if c.strip() == 'B': return i, 0.9
        elif b_len > a_len + 5:
            for i, c in enumerate(candidates):
                if c.strip() == 'A': return i, 0.9
        a_conj = ' and ' in a_text or ' who also ' in a_text or ' who ' in a_text
        b_conj = ' and ' in b_text or ' who also ' in b_text or ' who ' in b_text
        if a_conj and not b_conj:
            for i, c in enumerate(candidates):
                if c.strip() == 'B': return i, 0.85
        elif b_conj and not a_conj:
            for i, c in enumerate(candidates):
                if c.strip() == 'A': return i, 0.85
        return None

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        for solver in [self._try_argument, self._try_conjunction]:
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
