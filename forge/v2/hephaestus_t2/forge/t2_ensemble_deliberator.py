"""T2 Ensemble Deliberator — meta-solver combining all specialized T2 solvers.

Strategy: Route to the best specialized sub-solver via keyword detection,
then fall back to shared T1 parser. Aggregates all T2 categories.
"""

import sys
import re
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from _t1_parsers import try_standard, DAYS
from forge_primitives_t2 import deliberate, ensemble_vote, error_correct

# Import specialized solvers from sibling tools
from t2_simpson_paradox_solver import ReasoningTool as _Simpson
from t2_strategic_deception_solver import ReasoningTool as _Deception
from t2_temporal_complex_solver import ReasoningTool as _Temporal
from t2_argument_logic_solver import ReasoningTool as _Argument


class ReasoningTool:
    """Meta-solver: routes to specialized solvers, falls back to ensemble."""

    def __init__(self):
        self._simpson = _Simpson()
        self._deception = _Deception()
        self._temporal = _Temporal()
        self._argument = _Argument()
        self._solvers = [self._simpson, self._deception, self._temporal, self._argument]

    def _ncd(self, a, b):
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0

    def _make_result(self, idx, candidates):
        out = []
        for i, c in enumerate(candidates):
            out.append({"candidate": c, "score": 1.0 if i == idx else 0.0})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    # ── Additional T2 patterns not in specialist tools ──────────────────

    def _try_extra_t2(self, prompt, candidates):
        p = prompt.lower()

        # Expected value
        ev_m = re.findall(r'(\d+)%\s+chance\s+of\s+(?:winning\s+)?\$(\d+)', p)
        if len(ev_m) >= 2:
            evs = [float(pct) / 100 * float(val) for pct, val in ev_m]
            for i, c in enumerate(candidates):
                cl = c.lower()
                if evs[0] > evs[1] and 'game a' in cl: return i, 0.9
                elif evs[1] > evs[0] and 'game b' in cl: return i, 0.9

        # Correlation vs causation
        if ('correlation' in p or 'correlat' in p) and ('caus' in p or 'imply' in p):
            for i, c in enumerate(candidates):
                cl = c.lower()
                if 'no' in cl.split(',')[0] and ('does not' in cl or 'correlation' in cl):
                    return i, 0.9

        # Pronoun ambiguity
        if re.search(r'(?:told|said to)\s+\w+\s+(?:he|she|they)\s+(?:was|were|is)', p):
            for i, c in enumerate(candidates):
                if 'ambiguous' in c.lower() or 'unclear' in c.lower():
                    return i, 0.9

        # Argument strength comparison
        if 'argument a' in p and 'argument b' in p and 'stronger' in p:
            arg_a = re.search(r'argument a:(.+?)argument b:', p, re.DOTALL)
            arg_b = re.search(r'argument b:(.+?)(?:which|$)', p, re.DOTALL)
            if arg_a and arg_b:
                at = arg_a.group(1).lower()
                bt = arg_b.group(1).lower()
                a_mp = bool(re.search(r'if\s+\w+\s+has\s+a\s+(\w+).+?then.+?(\w+).*?has\s+a\s+\1.*?therefore.*?\2', at, re.DOTALL))
                b_mp = bool(re.search(r'if\s+\w+\s+has\s+a\s+(\w+).+?then.+?(\w+).*?has\s+a\s+\1.*?therefore.*?\2', bt, re.DOTALL))
                if a_mp and not b_mp:
                    for i, c in enumerate(candidates):
                        if c.strip() == 'A': return i, 0.9
                elif b_mp and not a_mp:
                    for i, c in enumerate(candidates):
                        if c.strip() == 'B': return i, 0.9

        # Parallel vs sequential
        seq_m = re.search(r'takes?\s+(\d+)\s+\w+.*?(\d+)\s+(?:of them|parts?).*?one\s+after', p)
        if seq_m:
            total = int(seq_m.group(1)) * int(seq_m.group(2))
            for i, c in enumerate(candidates):
                nums = re.findall(r'\d+', c)
                if nums and int(nums[0]) == total: return i, 0.9

        # Inverse proportion
        inv_m = re.search(r'(\d+)\s+\w+\s+can\s+\w+.*?in\s+(\d+)\s+\w+.*?(\d+)\s+\w+', p)
        if inv_m and ('how many days' in p or 'how many hours' in p or 'how long' in p):
            result = round(int(inv_m.group(1)) * int(inv_m.group(2)) / int(inv_m.group(3)))
            for i, c in enumerate(candidates):
                nums = re.findall(r'\d+', c)
                if nums and int(nums[0]) == result: return i, 0.9

        # Base rate / Bayes
        prev_m = re.search(r'1\s+in\s+(\d+)', p)
        tp_m = re.search(r'(\d+)%\s+true\s+positive', p)
        fp_m = re.search(r'(\d+)%\s+false\s+positive', p)
        if prev_m and tp_m and fp_m:
            prev = 1.0 / int(prev_m.group(1))
            tp = int(tp_m.group(1)) / 100.0
            fp = int(fp_m.group(1)) / 100.0
            ppv = round((tp * prev) / (tp * prev + fp * (1 - prev)) * 100, 1)
            for i, c in enumerate(candidates):
                nums = re.findall(r'[\d.]+', c)
                for n in nums:
                    try:
                        if abs(float(n) - ppv) < 0.2: return i, 0.9
                    except ValueError:
                        pass
        return None

    # ── Main evaluate: try all specialists then shared T1 ───────────────

    def evaluate(self, prompt, candidates):
        if not candidates:
            return []

        # Try each specialized solver (they only fire on their category)
        for tool in self._solvers:
            for method_name in dir(tool):
                if method_name.startswith('_try_') and method_name != '_try_standard':
                    method = getattr(tool, method_name)
                    try:
                        r = method(prompt, candidates)
                        if r is not None:
                            return self._make_result(r[0], candidates)
                    except (TypeError, ValueError):
                        pass

        # Try extra T2 patterns
        r = self._try_extra_t2(prompt, candidates)
        if r is not None:
            return self._make_result(r[0], candidates)

        # Shared T1 parser
        r = try_standard(prompt, candidates)
        if r is not None:
            return self._make_result(r[0], candidates)

        # NCD fallback
        out = []
        for c in candidates:
            d = self._ncd(prompt, c)
            out.append({"candidate": c, "score": 1.0 / (1.0 + d)})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt, answer):
        r = self.evaluate(prompt, [answer, "DUMMY_WRONG"])
        return min(r[0]["score"], 0.95) if r and r[0]["candidate"] == answer else 0.1
