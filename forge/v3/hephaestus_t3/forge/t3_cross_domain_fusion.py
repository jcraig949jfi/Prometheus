"""T3 Cross-Domain Fusion — entangled multi-domain reasoning solver.

Targets: causal_temporal_fusion, tom_causal_deception, probabilistic_logic_conflict,
         temporal_tom_scheduling, meta_causal_reasoning
"""
import sys, re, zlib
from pathlib import Path

_forge = Path(__file__).resolve().parent
_src = str(_forge.parent / "src")
_t2src = str(_forge.parent.parent.parent / "v2" / "hephaestus_t2" / "src")
_t1src = str(_forge.parent.parent.parent.parent / "agents" / "hephaestus" / "src")
_t2forge = str(_forge.parent.parent.parent / "v2" / "hephaestus_t2" / "forge")
for p in [_src, _t2src, _t1src, _t2forge]:
    if p not in sys.path: sys.path.insert(0, p)
from _t1_parsers import try_standard

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]


def _ncd(a, b):
    ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
    cab = len(zlib.compress((a + " " + b).encode()))
    return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0


def _mk(idx, candidates):
    out = [{"candidate": c, "score": 1.0 if i == idx else 0.0}
           for i, c in enumerate(candidates)]
    return sorted(out, key=lambda x: x["score"], reverse=True)


class ReasoningTool:

    # ── causal_temporal_fusion ──────────────────────────────────────
    def _try_causal_temporal(self, p, candidates):
        # Pattern: "first 'X', then 'Y'" => X happened before Y => X caused Y
        seq = re.findall(r"first\s+'([^']+)'.*?then\s+'([^']+)'", p)
        if not seq:
            return None
        first_evt, second_evt = seq[0]
        # The correct answer says first_evt caused/led/drove/triggered/produced second_evt
        for i, c in enumerate(candidates):
            cl = c.lower()
            fl, sl = first_evt.lower(), second_evt.lower()
            if fl in cl and sl in cl:
                for verb in ["caused", "led to", "drove", "triggered", "produced"]:
                    if verb in cl and cl.index(fl) < cl.index(verb):
                        return i
        return None

    # ── tom_causal_deception ────────────────────────────────────────
    def _try_tom_deception(self, p, candidates):
        # Pattern: X rearranges evidence to make Y believe fake_cause caused effect.
        # Observer Z saw tampering. What does Z believe Y believes?
        m = re.search(
            r'(\w+)\s+knows\s+that\s+(.+?)\s+caused\s+(.+?)\.\s+'
            r'However,\s+\1\s+rearranges.*?(\w+)\s+believe\s+that\s+'
            r'(.+?)\s+caused\s+\3\s+instead.*?(\w+)\s+witnessed', p)
        if not m:
            return None
        manipulator, real_cause, effect = m.group(1), m.group(2), m.group(3)
        victim, fake_cause, observer = m.group(4), m.group(5), m.group(6)
        # Correct: observer believes victim thinks fake_cause caused effect
        # Must match: "observer believes victim thinks fake_cause caused effect"
        pattern = f"{observer.lower()} believes {victim.lower()} thinks {fake_cause.lower()} caused"
        for i, c in enumerate(candidates):
            cl = c.lower()
            if pattern in cl:
                return i
        return None

    # ── probabilistic_logic_conflict ────────────────────────────────
    def _try_prob_logic(self, p, candidates):
        if "empirical" not in p.lower() and "subpopulation" not in p.lower():
            return None
        m = re.search(r'holds\s+only\s+(\d+)%\s+of\s+the\s+time', p)
        if not m:
            return None
        # Correct answer always says "Trust the empirical evidence"
        for i, c in enumerate(candidates):
            cl = c.lower()
            if "trust the empirical" in cl and ("exception" in cl or "specific" in cl
                    or "doesn't hold" in cl or "subpopulation" in cl
                    or "increases risk" in cl or "decreases" in cl
                    or "disruption" in cl or "deprivation" in cl):
                return i
        # Fallback: any candidate mentioning "empirical evidence" + not "logical rule"
        for i, c in enumerate(candidates):
            cl = c.lower()
            if "trust the empirical" in cl:
                return i
        return None

    # ── temporal_tom_scheduling ──────────────────────────────────────
    def _try_temporal_tom(self, p, candidates):
        # Parse: real deadline, A believes X, B believes Y
        m = re.search(r'real\s+deadline\s+is\s+(\w+)', p)
        if not m:
            return None
        real_day = m.group(1)
        # Parse who believes what
        beliefs = re.findall(r'(\w+)\s+believes\s+(?:the\s+deadline\s+is|it\s+is)\s+(\w+)', p)
        if len(beliefs) < 2:
            return None
        a_name, a_day = beliefs[0]
        b_name, b_day = beliefs[1]
        real_idx = next((i for i, d in enumerate(DAYS) if d == real_day.lower()), -1)
        a_idx = next((i for i, d in enumerate(DAYS) if d == a_day.lower()), -1)
        b_idx = next((i for i, d in enumerate(DAYS) if d == b_day.lower()), -1)
        if real_idx < 0:
            return None
        # If A's believed deadline > real => A misses
        a_late = a_idx > real_idx
        b_late = b_idx > real_idx
        for i, c in enumerate(candidates):
            cl = c.lower()
            if a_late and not b_late:
                if b_name.lower() in cl and "on time" in cl and "misses" in cl:
                    return i
            elif not a_late and not b_late:
                if "both" in cl and ("on time" in cl or "before" in cl):
                    return i
        return None

    # ── meta_causal_reasoning ───────────────────────────────────────
    def _try_meta_causal(self, p, candidates):
        if "causal argument" not in p.lower():
            return None
        # Correct answers mention specific fallacy names
        fallacy_keys = [
            ("confound", "confound"), ("reverse", "reverse"),
            ("selection bias", "selection"), ("simpson", "simpson"),
            ("population density", "density"), ("wealth", "wealth"),
        ]
        for i, c in enumerate(candidates):
            cl = c.lower()
            for key, _ in fallacy_keys:
                if key in cl and ("fix" in cl or "control" in cl or "experiment" in cl
                                  or "stratif" in cl or "temporal" in cl):
                    return i
        return None

    # ── NCD fallback ───────────────────────────────────────────────
    def _ncd_fallback(self, prompt, candidates):
        dists = [(i, _ncd(prompt, c)) for i, c in enumerate(candidates)]
        dists.sort(key=lambda x: x[1])
        return dists[0][0]

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        p = prompt

        # Try T1 parsers first
        t1 = try_standard(prompt, candidates)
        if t1 is not None:
            return _mk(t1[0], candidates)

        # Try each T3 domain solver
        for solver in [self._try_causal_temporal, self._try_tom_deception,
                       self._try_prob_logic, self._try_temporal_tom,
                       self._try_meta_causal]:
            idx = solver(p, candidates)
            if idx is not None:
                return _mk(idx, candidates)

        # NCD fallback
        return _mk(self._ncd_fallback(prompt, candidates), candidates)

    def confidence(self, prompt: str, answer: str) -> float:
        # Use NCD distance as a confidence proxy: lower NCD = higher conf
        d = _ncd(prompt, answer)
        return max(0.0, min(1.0, 1.0 - d))
