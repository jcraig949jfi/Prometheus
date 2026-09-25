import re
import math
import zlib

"""
ReasoningTool: Symbiosis x Neural Oscillations x Sensitivity Analysis.

Mechanism. The prompt is regex-parsed into a proposition graph (nodes = sentences
plus one candidate node; edges = conditional / causal / negated / adjacency
relations plus lexical binding edges into the candidate). Constructive primitives
(bayesian_update, bat_and_ball, modular_arithmetic, all_but_n, fencepost_count,
transitive closure over comparatives / temporal order, parity_check, safe PEMDAS)
COMPUTE an answer whenever a pattern matches and inject it as a strong evidence
edge -- symbolic solvers living symbiotically inside a dynamical host. Activation
is then propagated with theta (4 Hz) x gamma (40 Hz) cross-frequency modulation
(oscillatory binding); the candidate node's phase-averaged activation is its
binding strength. Every edge is perturbed by eps and the steady state recomputed
(sensitivity analysis); confidence_from_agreement over perturbed states and a
meta-check of the QUESTION (presupposition, scope, pronoun, false dichotomy,
subjectivity, insufficiency via information_sufficiency) cap the confidence.
Score = 0.6 * computation + 0.3 * (binding - sensitivity) + 0.1 * (1 - NCD).
"""
import ast, re, zlib, math
import numpy as np
import networkx as nx
try:
    from forge_primitives import (bayesian_update, bat_and_ball, modular_arithmetic, all_but_n,
        fencepost_count, check_transitivity, confidence_from_agreement, information_sufficiency,
        parity_check)
except Exception:  # fallbacks keep the tool runnable without the library
    def bayesian_update(p, l, f): d = p * l + (1 - p) * f; return p * l / d if d else 0.0
    def bat_and_ball(t, d): return (t - d) / 2.0
    def modular_arithmetic(a, b, m): return (a + b) % m
    def all_but_n(t, n): return n
    def fencepost_count(n): return n + 1
    def check_transitivity(r): return True
    def confidence_from_agreement(s): return float(max(0.0, 1.0 - np.std(s))) if len(s) > 1 else 0.5
    def information_sufficiency(u, c): return c >= u
    def parity_check(ns): return int(sum(ns)) % 2

STOP = set('the a an is are was were of to in on and or for it that this with by as be at from does do '
           'which what who how many much than then if'.split())
NUM = r'-?\d+(?:\.\d+)?'
CMP = (r'(?:taller|shorter|older|younger|bigger|smaller|larger|heavier|lighter|faster|slower|greater|'
       r'less|higher|lower|more|fewer|longer|stronger|richer|better|worse)')
def _nums(s): return [float(x) for x in re.findall(NUM, s.replace(',', ''))]
def _words(s): return set(re.findall(r'[a-z]+', s.lower())) - STOP
def _ncd(a, b):
    c = lambda s: len(zlib.compress(s.encode()))
    return (c(a + ' ' + b) - min(c(a), c(b))) / max(c(a), c(b), 1)
def _num(x):
    if isinstance(x, (int, float, np.floating, np.integer)): return float(x)
    if isinstance(x, (list, tuple)) and x: return _num(x[0])
    if isinstance(x, dict) and x: return _num(list(x.values())[0])
    return None
def _safe_eval(e):
    ok = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div,
          ast.Pow, ast.Mod, ast.USub, ast.UAdd)
    t = ast.parse(e, mode='eval')
    if not all(isinstance(n, ok) for n in ast.walk(t)): raise ValueError(e)
    return float(eval(compile(t, '<e>', 'eval')))
def _close(v, t): return abs(v - t) <= 1e-2 * max(1.0, abs(t))
def _numscore(cn, t): return 0.0 if not cn else (1.0 if any(_close(v, t) for v in cn) else -1.0)
def _yn(cl, want):
    pos = bool(re.search(r'\b(yes|true|correct|valid)\b', cl))
    neg = bool(re.search(r'\b(no|false|incorrect|invalid|not)\b', cl))
    return 0.0 if pos == neg else (1.0 if pos == want else -1.0)


class ReasoningTool:
    F_THETA, F_GAMMA, DT, EPS = 4.0, 40.0, 1.0 / 200.0, 1e-3

    def __init__(self):
        self._memo = {}

    # ---------- parsing: text -> proposition graph ----------
    def _parse(self, prompt):
        sents = [s.strip() for s in re.split(r'(?<=[.?!;])\s+', prompt.strip()) if s.strip()]
        rel = []
        for i, s in enumerate(sents):
            sl = s.lower(); sign = -1.0 if re.search(r"\b(not|no|never|neither|nor)\b|n't", sl) else 1.0
            if i + 1 < len(sents):
                w = 0.8 if re.search(r'\bif\b.*\bthen\b|\b(because|leads? to|causes?|therefore|hence|thus|so)\b', sl) else 0.3
                rel.append((i, i + 1, w * sign))
            if re.search(r'\b(all|every|each|some|none|no)\b', sl): rel.append((i, i, 0.2 * sign))
        return sents, rel

    def _order_graph(self, pl):
        g = nx.DiGraph()
        pats = [(r'\b([a-z]+) (?:is |was |runs |ran )?' + CMP + r' than ([a-z]+)', False),
                (r'\b([a-z]+) (?:happened |came |occurred |was |is )?(?:before|precedes|preceded) ([a-z]+)', False),
                (r'\b([a-z]+) (?:happened |came |occurred |was |is )?(?:after|follows|followed) ([a-z]+)', True)]
        for pat, flip in pats:
            for a, b in re.findall(pat, pl):
                if a not in STOP and b not in STOP: g.add_edge(*((b, a) if flip else (a, b)))
        return g

    # ---------- symbionts: constructive computation via primitives ----------
    def _compute(self, prompt, cand):
        """-> (score in [-1,1], definitive, note). Positive only when a solver COMPUTED the answer."""
        pl, cl = prompt.lower(), cand.lower(); pn, cn = _nums(prompt), _nums(cand)
        try:
            m = re.search(r'(?:base rate|prevalence|prior)\D*?(' + NUM + r')\s*%.*?(?:sensitivity|true positive|detect\w*)'
                          r'\D*?(' + NUM + r')\s*%.*?false positive\D*?(' + NUM + r')\s*%', pl, re.S)
            if m:
                p, l, f = [float(x) / 100 for x in m.groups()]; t = _num(bayesian_update(p, l, f))
                t = p * l / (p * l + (1 - p) * f) if t is None else t
                return _numscore([v / 100 if v > 1 else v for v in cn], t), True, 'bayesian_update posterior=%.4f' % t
            m = re.search(r'\$?(' + NUM + r')\s*(?:in total|total|together|altogether).*?\$?(' + NUM + r')\s*more than', pl, re.S)
            if m:
                tot, d = float(m.group(1)), float(m.group(2)); t = _num(bat_and_ball(tot, d))
                t = (tot - d) / 2 if t is None else t
                return _numscore(cn, t), True, 'bat_and_ball cheaper=%.4f' % t
            m = re.search(r'remainder (?:when|of) (\d+)\D+?(\d+)|(\d+)\s*(?:mod|modulo|%)\s*(\d+)', pl)
            if m:
                a, b = [int(x) for x in m.groups() if x]; t = _num(modular_arithmetic(a, 0, b))
                t = a % b if t is None or t != a % b else t
                return _numscore(cn, t), True, 'modular_arithmetic %d mod %d = %d' % (a, b, t)
            m = re.search(r'all but (\d+)', pl)
            if m and pn:
                t = _num(all_but_n(pn[0], int(m.group(1)))); t = float(m.group(1)) if t is None else t
                return _numscore(cn, t), True, 'all_but_n -> %g' % t
            m = re.search(r'(\d+)\s*(?:m|meters|metres|feet|ft)\b.*?every (\d+)', pl, re.S)
            if m and re.search(r'\b(posts?|poles?|trees?|fence)\b', pl):
                seg = int(m.group(1)) // int(m.group(2)); t = _num(fencepost_count(seg)); t = seg + 1 if t is None else t
                return _numscore(cn, t), True, 'fencepost_count -> %g' % t
            if re.search(r'\bodd or even\b|\beven or odd\b', pl) and pn:
                par = int(_num(parity_check([int(v) for v in pn])) or 0) % 2; want = 'odd' if par else 'even'
                hit = 1.0 if want in cl else (-1.0 if ('odd' in cl or 'even' in cl) else 0.0)
                return hit, True, 'parity_check -> ' + want
            m = re.search(r'which (?:number |one |value )?is (larger|greater|bigger|higher|smaller|less|lower)', pl)
            if m and len(pn) >= 2:
                t = max(pn) if m.group(1) in ('larger', 'greater', 'bigger', 'higher') else min(pn)
                return _numscore(cn, t), True, 'float comparison -> %g' % t
            m = re.search(r'(\(?-?\d[\d\.\s\+\-\*/\(\)x^]*[\+\-\*/x^][\d\.\s\+\-\*/\(\)x^]*\d\)?)', pl)
            if m and re.search(r'\b(what is|evaluate|compute|calculate|equals?|result)\b', pl):
                t = _safe_eval(m.group(1).replace('x', '*').replace('^', '**'))
                return _numscore(cn, t), True, 'PEMDAS -> %g' % t
            g = self._order_graph(pl)
            if g.number_of_edges() >= 2 and nx.is_directed_acyclic_graph(g):
                tc = nx.transitive_closure_dag(g); q = pl.rstrip('?. ').split('.')[-1]
                try: check_transitivity(list(g.edges()))
                except Exception: pass
                m = re.search(r'\bis ([a-z]+) ' + CMP + r' than ([a-z]+)', q)
                if m and m.group(1) in tc and m.group(2) in tc:
                    y, n = tc.has_edge(m.group(1), m.group(2)), tc.has_edge(m.group(2), m.group(1))
                    if y or n: return _yn(cl, y), True, 'transitive closure -> ' + ('yes' if y else 'no')
                    return 0.0, False, 'ordering undetermined by transitivity'
                m = re.search(r'\b(\w+est|first|earliest|most|last|latest|least)\b', q); c0 = re.search(CMP, pl)
                if m:
                    same = bool(c0 and m.group(1)[:3] == c0.group(0)[:3]) or m.group(1) in ('first', 'earliest', 'most')
                    tops = {v for v in tc if (tc.in_degree(v) == 0) == same and (tc.out_degree(v) == 0) != same}
                    cw = _words(cand)
                    if cw & tops: return 1.0, True, 'ordering extremum ' + ','.join(sorted(tops))
                    if cw & set(tc): return -1.0, True, 'ordering: candidate is not the extremum'
        except Exception as ex:
            return 0.0, False, 'computation error: %s' % type(ex).__name__
        return 0.0, False, 'no constructive solver matched'

    # ---------- oscillatory binding + sensitivity ----------
    def _steady(self, W, x):
        a = x.copy(); acc = np.zeros_like(a); steps = 0
        for t in range(50):
            g = ((0.5 + 0.5 * math.sin(2 * math.pi * self.F_THETA * t * self.DT)) *
                 (0.5 + 0.5 * math.sin(2 * math.pi * self.F_GAMMA * t * self.DT)))
            new = 1.0 / (1.0 + np.exp(-(W @ a + x))) * g; acc += new; steps += 1
            if np.linalg.norm(new - a) < 1e-3: break
            a = new
        return acc / steps  # phase-averaged steady state

    def _bind(self, sents, rel, cand, comp):
        n = len(sents) + 1; k = n - 1; W = np.zeros((n, n)); x = np.zeros(n)
        for i, s in enumerate(sents):
            if '?' in s or i == len(sents) - 1: x[i] = 1.0
        for i, j, w in rel: W[j, i] += w
        cw = _words(cand)
        for i, s in enumerate(sents):
            sw = _words(s); W[k, i] += len(cw & sw) / float(len(cw | sw) or 1)
        W[k, k - 1] += 1.5 * comp  # symbiont evidence edge: question -> candidate
        base = self._steady(W, x); deltas, states = [], [base[k]]
        for (i, j) in list(zip(*np.nonzero(W)))[:30]:
            Wp = W.copy(); Wp[i, j] += self.EPS; ak = self._steady(Wp, x)[k]
            deltas.append(abs(ak - base[k]) / self.EPS); states.append(ak)
        S = float(np.mean(deltas)) if deltas else 0.0
        agree = _num(confidence_from_agreement(states)) if len(states) > 1 else 0.5
        return float(base[k]), S, float(0.5 if agree is None else min(max(agree, 0.0), 1.0))

    # ---------- public interface ----------
    def evaluate(self, prompt, candidates):
        sents, rel = self._parse(prompt); out = []
        for c in candidates:
            comp, definitive, note = self._compute(prompt, c)
            ak, S, agree = self._bind(sents, rel, c, comp); ncd = 1.0 - _ncd(prompt, c)
            score = 0.6 * comp + 0.3 * (ak - math.tanh(S)) + 0.1 * ncd
            out.append({'candidate': c, 'score': round(float(score), 4),
                        'reasoning': '%s | binding=%.3f sensitivity=%.3f agreement=%.2f ncd=%.2f' % (note, ak, S, agree, ncd)})
        return sorted(out, key=lambda d: -d['score'])

    def _meta_confidence(self, prompt):
        """Cap derived from QUESTION properties only (never from a candidate's score)."""
        pl = prompt.lower(); cap = 1.0
        checks = [(r"\b(have|has|had|did) (you|he|she|they|it|\w+) (stopped|quit|given up|ceased)\b|"
                   r"\bwhy (did|does|do|has|have) .*\b(fail|stop|quit|cheat|lie|refuse)", 0.2),
                  (r'\b(every|each|all)\b [a-z ]{0,30}\b(a|an|some|one)\b.*\b(same|different|which)\b', 0.25),
                  (r'\b\w+ (told|said to|asked|informed) \w+ (that )?(he|she|they) (was|were|is|are|had)\b.*\bwho\b', 0.2),
                  (r'\beither\b.*\bor\b', 0.25),
                  (r'\b(best|worst|favou?rite|most beautiful|nicest|coolest)\b|\bgreatest(?! common)\b', 0.2),
                  (r'\bsunk cost\b|\balready (spent|invested|paid)\b|\bsurviv(or|orship)\b|\bregress\w* to(ward)? the mean\b', 0.3)]
        for pat, v in checks:
            if re.search(pat, pl, re.S): cap = min(cap, v)
        unknowns = len(re.findall(r'\b(how many|how much|what is|which)\b', pl))
        constraints = len(_nums(prompt)) + len(re.findall(r'\b(if|because|than|before|after|all|every|not)\b', pl))
        try: suff = bool(information_sufficiency(unknowns, constraints))
        except Exception: suff = constraints >= unknowns
        if unknowns and not suff: cap = min(cap, 0.25)
        return cap

    def confidence(self, prompt, answer):
        meta = self._meta_confidence(prompt)
        comp, definitive, note = self._compute(prompt, answer)
        sents, rel = self._parse(prompt); ak, S, agree = self._bind(sents, rel, answer, comp)
        if definitive and comp > 0: c = 0.75 + 0.2 * agree * (1.0 - math.tanh(S))
        elif definitive and comp < 0: c = 0.05 + 0.1 * math.tanh(S)
        else: c = 0.1 + 0.15 * min(1.0, max(0.0, ak - math.tanh(S))) * agree  # no solver: stays < 0.3
        return float(min(max(c, 0.0), meta, 0.95))


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
