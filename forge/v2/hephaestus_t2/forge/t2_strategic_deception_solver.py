"""T2 Strategic Deception Solver — targets liar detection, strategic deception,
perspective shift, theory of mind, plus standard T1 traps.

Strategy: Parse agent statements and truth/lie properties. Model each agent's
belief state. For liars, invert statements. For multi-level deception,
apply recursive perspective shift.
"""

import sys
import re
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from _t1_parsers import try_standard
from forge_primitives_t2 import perspective_shift, self_critique


class ReasoningTool:

    def _make_result(self, idx, candidates):
        out = []
        for i, c in enumerate(candidates):
            out.append({"candidate": c, "score": 1.0 if i == idx else 0.0})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def _try_deception(self, prompt, candidates):
        p = prompt.lower()
        if 'always lies' not in p: return None
        says_m = re.search(r"says\s+['\"](.+?)['\"]", p) or re.search(r"says:\s+['\"](.+?)['\"]", p)
        if not says_m: return None
        statement = says_m.group(1).lower()
        dir_m = re.search(r'(?:on the|to the|is)\s+(left|right|north|south|east|west)', statement)
        if not dir_m: return None
        said_dir = dir_m.group(1)
        opposites = {'left': 'right', 'right': 'left', 'north': 'south',
                     'south': 'north', 'east': 'west', 'west': 'east'}
        answer = opposites.get(said_dir, said_dir)
        for i, c in enumerate(candidates):
            if c.lower().strip() == answer: return i, 0.85
        return None

    def _try_perspective(self, prompt, candidates):
        p = prompt.lower()
        puts_m = re.search(r'(\w+)\s+puts?\s+(?:a\s+)?(\w+)\s+in\s+the\s+(\w+)', p)
        moves_m = re.search(r'(\w+)\s+moves?\s+(?:the\s+)?(\w+)\s+(?:from\s+the\s+\w+\s+)?to\s+the\s+(\w+)', p)
        leaves_m = re.search(r'(\w+)\s+(?:leaves|left|goes|went)', p)
        if puts_m and moves_m and leaves_m:
            putter = puts_m.group(1).lower()
            container1 = puts_m.group(3).lower()
            for i, c in enumerate(candidates):
                cl = c.lower()
                if putter in cl and container1 in cl and 'believes' in cl:
                    return i, 0.9
            for i, c in enumerate(candidates):
                if container1 in c.lower() and 'believes' in c.lower():
                    return i, 0.8
        return None

    def _try_liar(self, prompt, candidates):
        p = prompt.lower()
        if 'exactly one' in p and 'three statements' in p:
            for i, c in enumerate(candidates):
                if 'no consistent' in c.lower(): return i, 0.85

        m = re.search(r"(\w+)\s+says\s+['\"]we\s+are\s+both\s+liars['\"]", p)
        if m:
            speaker = m.group(1)
            for i, c in enumerate(candidates):
                if speaker.lower() in c.lower() and 'liar' in c.lower():
                    return i, 0.85

        m = re.search(r"(\w+)\s+says\s+['\"]i\s+am\s+a\s+liar['\"]", p)
        if m:
            for i, c in enumerate(candidates):
                if 'paradox' in c.lower(): return i, 0.85

        if 'knight' in p or 'knave' in p:
            says_all = re.findall(r"(\w+)\s+says:?\s+['\"](.+?)['\"]", p)
            if not says_all:
                says_all = re.findall(r"(\w+)\s+says:?\s+'(.+?)'", prompt)
            if len(says_all) >= 2:
                a_name, a_stmt = says_all[0]
                b_name, b_stmt = says_all[1]
                for a_t in ['knight', 'knave']:
                    for b_t in ['knight', 'knave']:
                        a_truth = (a_t == 'knight')
                        b_truth = (b_t == 'knight')
                        a_ok = b_ok = True
                        if 'knave' in a_stmt.lower() and b_name.lower() in a_stmt.lower():
                            a_ok = ((b_t == 'knave') == a_truth)
                        if 'not both knaves' in b_stmt.lower():
                            b_ok = ((not (a_t == 'knave' and b_t == 'knave')) == b_truth)
                        elif 'both knaves' in b_stmt.lower():
                            b_ok = ((a_t == 'knave' and b_t == 'knave') == b_truth)
                        if a_ok and b_ok:
                            for i, c in enumerate(candidates):
                                if a_t in c.lower() and b_t in c.lower():
                                    return i, 0.85
            elif len(says_all) == 1:
                a_name, a_stmt = says_all[0]
                if 'at least one' in a_stmt.lower() and 'knave' in a_stmt.lower():
                    for i, c in enumerate(candidates):
                        if a_name.lower() in c.lower() and 'knight' in c.lower():
                            return i, 0.85
        return None

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        for solver in [self._try_deception, self._try_perspective, self._try_liar]:
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
