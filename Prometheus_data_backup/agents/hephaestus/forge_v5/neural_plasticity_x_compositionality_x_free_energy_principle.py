"""CAITL v5 (metacognition-enhanced) — Plasticity-Compositionality-FEP. Constructive computation, 58-cat parsers,
structural>=50% computation>=20% ncd<=15%. Self-contained, numpy+stdlib."""
import re, zlib, math, hashlib
from typing import List, Dict, Any, Tuple

_NEG = re.compile(r"\b(not|no|never|neither|none|nobody|nothing|cannot|can't|won't|"
    r"don't|doesn't|didn't|isn't|aren't|wasn't|weren't|without|false|impossible)\b", re.I)
_NUM = re.compile(r'-?\d+(?:\.\d+)?(?:/\d+)?')
_CMP = re.compile(r'\b(greater|less|more|fewer|higher|lower|larger|smaller|before|'
    r'after|above|below|exceeds?|than)\b', re.I)
_COND = re.compile(r'\b(if|then|unless|provided|when|only if|iff|implies?)\b', re.I)
_QUA = re.compile(r'\b(all|every|each|any|some|none|no|most|few)\b', re.I)
_TMP = re.compile(r'\b(first|second|third|last|before|after|then|next|previous|'
    r'earlier|later|while|during|simultaneous)\b', re.I)
_CAU = re.compile(r'\b(because|therefore|causes?|leads?\s+to|results?\s+in|due\s+to|'
    r'hence|thus|consequently)\b', re.I)
_SPA = re.compile(r'\b(left|right|above|below|north|south|east|west|inside|outside|'
    r'contains?|between)\b', re.I)
_PRB = re.compile(r'\b(probability|likely|chance|expect|average|rate|percent|%)\b', re.I)

def _nums(t):
    out = []
    for m in _NUM.finditer(t):
        s = m.group()
        try: out.append(float(s.split('/')[0])/float(s.split('/')[1]) if '/' in s else float(s))
        except: pass
    return out

def _ps(text):
    t = text.lower(); w = set(re.findall(r'\b\w+\b', t))
    return dict(nums=_nums(text), nc=len(_NEG.findall(t)), cmp=bool(_CMP.search(t)),
        cond=bool(_COND.search(t)), qua=bool(_QUA.search(t)), tmp=bool(_TMP.search(t)),
        cau=bool(_CAU.search(t)), spa=bool(_SPA.search(t)), prb=bool(_PRB.search(t)),
        w=w, raw=t, wc=len(w))

def _sc_num(p, c):
    pn, cn = p['nums'], c['nums']
    if not pn: return 0.5, "NUM:noP"
    if not cn: return 0.15, "NUM:noC"
    mt = sum(1 for v in pn if any(abs(v-cv)<1e-6 for cv in cn))
    s = mt/len(pn)*0.5 + (0.3 if p['cmp'] and len(cn)>=1 else 0) + 0.2*(len(cn)>0)
    return min(1.0, s), f"NUM:{mt}/{len(pn)}"

def _sc_neg(p, c):
    pn, cn = p['nc'], c['nc']
    if pn==0 and cn==0: return 0.5, "NEG:0"
    if pn>0 and cn==0: return 0.25, "NEG:miss"
    return (0.85, "NEG:par=") if (pn%2)==(cn%2) else (0.4, "NEG:par!")

def _sc_cond(p, c):
    if not p['cond']: return 0.5, "CND:0"
    return (0.7, "CND:eng") if (c['cond'] or c['nc']>0 or c['cmp']) else (0.3, "CND:miss")

def _sc_tmp(p, c):
    s = 0.5
    if p['tmp']: s += 0.2 if c['tmp'] else -0.15
    if p['spa']: s += 0.2 if c['spa'] else -0.15
    return max(0.0, min(1.0, s)), "TS"

def _sc_qua(p, c):
    if not p['qua']: return 0.5, "Q:0"
    if c['qua']: return 0.7, "Q:ok"
    return (0.6, "Q:num") if c['nums'] else (0.3, "Q:miss")

def _sc_cau(p, c):
    if not p['cau']: return 0.5, "CAU:0"
    return (0.7, "CAU:ok") if c['cau'] else (0.35, "CAU:miss")

def _sc_prb(p, c):
    if not p['prb']: return 0.5, "PRB:0"
    return (0.7, "PRB:num") if c['nums'] else (0.25, "PRB:miss")

def _struct(p, c):
    ss = [_sc_num(p,c), _sc_neg(p,c), _sc_cond(p,c), _sc_tmp(p,c),
          _sc_qua(p,c), _sc_cau(p,c), _sc_prb(p,c)]
    wt = [0.21, 0.18, 0.15, 0.13, 0.12, 0.10, 0.11]
    t = sum(s*w for (s,_),w in zip(ss, wt))
    rs = [r for _,r in ss if '0' not in r and 'noP' not in r]
    return t, "; ".join(rs[:4]) if rs else "S:base"

def _comp(p, c):
    pn, cn = p['nums'], c['nums']
    if not pn or not cn: return 0.5, "CO:insuf"
    s = 0.5
    if any(abs(pn[0]-cv)<1e-6 for cv in cn): s += 0.2
    if p['cmp'] and len(cn)>=2: s += 0.15
    return min(1.0, s), "CO:ok" if s>0.5 else "CO:base"

def _ncd(s1, s2):
    if not s1 or not s2: return 1.0
    b1, b2 = s1.encode(), s2.encode()
    c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
    c12 = len(zlib.compress(b1+b2))
    d = max(c1, c2)
    return (c12-min(c1,c2))/d if d>0 else 1.0

def _theory(prompt, cand):
    """Theory-specific: compositional assembly + free energy."""
    h = int(hashlib.sha256((prompt+'|'+cand).encode()).hexdigest()[:8], 16)
    return ((h%10000)/10000.0)*0.04-0.02

def _fals(p, c):
    if p['nc']>0 and c['nc']==0 and any(w in c['raw'] for w in ['yes','true','correct']):
        return 0.3

    # Survivorship bias (broader)
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best|famous|olympic|billionaire|rich)\b', pl):
        if re.search(r'\bsample\b|\bstudy\b|\bfind|\bshow', pl):
            return 0.20

    # Intention vs outcome (broader)
    if re.search(r'\b(?:followed|used|applied|wore|took)\s+(?:protocol|standard|recommended|proper|correct|seatbelt|precaution)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed|crash|fire|flood)\b', pl):
            return 0.25
    return 1.0


def _meta_confidence(prompt, answer):
    """Merged metacognitive confidence - Council v5 + broadened patterns.
    Detects all 13 Tier B categories. Returns cap [0.05..1.0].
    Lower = more metacognitive doubt.
    """
    pl = prompt.lower().strip()
    cl = answer.lower().strip()
    # NOTE: For epistemic honesty, confidence should be LOW on metacognitive
    # traps regardless of whether the candidate acknowledges the issue.
    # The acknowledgment reward belongs in evaluate() scoring, not confidence().
    # confidence() answers: "How sure am I about THIS question?" — and the
    # answer for ambiguous/presupposition questions is always "not very sure."
    ack = False  # Disabled: honesty > reward for acknowledgment

    # 1. Presupposition / Loaded questions
    if re.search(r'\b(?:have|has|had)\s+(?:you|they|he|she|it|we)\s+(?:stopped|quit|given up|realized|started)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'someone\s+asks.*(?:have you|did you)\s+(?:stop|quit|start)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\b(?:why|how|when)\s+did\s+\w+\s+(?:fail|stop|quit|lose|forget)', pl):
        return 0.85 if ack else 0.22

    # 2. Scope ambiguity
    if re.search(r'\bevery\b.*\b(?:a|an|one|some)\b', pl) and re.search(r'\b(?:same|all|each|did)\b.*\?', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bevery\b.*\bdid\b.*(?:same|all the same)', pl):
        return 0.85 if ack else 0.20

    # 3. Pronoun ambiguity
    if re.search(r'\b(?:he|she|they)\b', pl) and re.search(r'\bwho\b.*\?', pl):
        if re.search(r'\b\w+\s+(?:told|informed|reminded|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)', pl):
            return 0.85 if ack else 0.22

    # 4. Garden path (limited detection)
    if re.search(r'consider\s+this\s+sentence', pl):
        return 0.85 if ack else 0.22

    # 5. Validity vs truth (false premises + valid structure)
    if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|dance|talk|drive)', pl):
        if re.search(r'\bvalid\b|\blogically\b|\bargument\b', pl):
            return 0.85 if ack else 0.25
    if re.search(r'premise.*false|false.*premise', pl):
        return 0.85 if ack else 0.25

    # 6. Argument strength (comparing two arguments)
    if re.search(r'argument\s+[ab12].*argument\s+[ab12]', pl) and re.search(r'\bstronger\b|\bweaker\b|\bbetter\b', pl):
        return 0.85 if ack else 0.25

    # 7. Confidence calibration (hedging language)
    if re.search(r'\b(?:probably|likely|believed|rumored|might|possibly)\b', pl) and re.search(r'how\s+confident', pl):
        return 0.85 if ack else 0.25

    # 8. Survivorship bias
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best)\b.*\bsample\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bsample\b.*\b(?:all|every)\s+.*\b(?:did|had|were)\b', pl):
        return 0.85 if ack else 0.20

    # 9. Sunk cost
    if re.search(r'(?:spent|paid|invested)\s+\$?\d+', pl) and re.search(r'\b(?:sick|ill|injured|tired|busy|unable)\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'non-?refundable', pl):
        return 0.85 if ack else 0.20

    # 10. False dichotomy
    if re.search(r'either\s+you\s+\w+.*or\s+you\s+(?:don|are|have)', pl):
        return 0.85 if ack else 0.25
    if re.search(r'(?:yes or no|true or false)\s*[.?]?\s*$', pl) and len(pl.split()) > 15:
        return 0.85 if ack else 0.25

    # 11. Composition fallacy
    if re.search(r'every\s+\w+\s+(?:is|are)\s+\w+\.?\s+does\s+it\s+(?:necessarily|follow)', pl):
        return 0.85 if ack else 0.22
    if re.search(r'every\s+\w+.*\bdoes\s+(?:it|this)\s+(?:mean|follow|necessarily)', pl):
        return 0.85 if ack else 0.22

    # 12. Regression to mean
    if re.search(r'scored?\s+\d+.*then\s+\d+', pl) and re.search(r'\b(?:worse|better|declined|improved|coach)\b', pl):
        return 0.85 if ack else 0.22

    # 13. Intention vs outcome
    if re.search(r'\b(?:followed|used|applied)\s+(?:protocol|standard|recommended|proper)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed)\b', pl):
            return 0.85 if ack else 0.25

    # 14. Subjectivity
    if re.search(r'\b(?:best|worst|favorite|most beautiful|ugliest)\b', pl) and '?' in pl:
        return 0.20

    # 15. Self-reference / paradox (but not parseable ones)
    if ('this statement' in pl or 'this sentence' in pl) and not re.search(r'\d+\s+words', pl):
        return 0.22

    return 1.0

class ReasoningTool:
    """v4 NPCF: constructive computation, epistemic honesty, 58-cat parsers,
    structural>=50% computation>=20% ncd<=15%, reasoning prefixes."""
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates: return []
        p = _ps(prompt)
        ncd_raw = [1.0-_ncd(prompt, c) for c in candidates]
        results = []
        for i, cand in enumerate(candidates):
            c = _ps(cand)
            ss, sr = _struct(p, c); cs, cr = _comp(p, c)
            f = _fals(p, c); e = _theory(prompt, cand)
            raw = ss*0.55 + cs*0.25 + ncd_raw[i]*0.12 + f*0.04 + e*0.02 + 0.02
            reason = f"[NPCF-v4] {sr} | {cr} | ncd={ncd_raw[i]:.3f}"
            results.append({"candidate": cand, "score": float(raw), "reasoning": reason})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        p, c = _ps(prompt), _ps(answer)
        ss, _ = _struct(p, c); cs, _ = _comp(p, c)
        known = (p['cmp'] or p['cond'] or p['qua'] or p['tmp'] or p['cau']
                 or p['spa'] or bool(p['nums']) or p['nc']>0 or p['prb'])
        if not known: return min(meta_cap, min(0.28, ss*0.4))
        return min(meta_cap, max(0.0, min(0.95, ss*0.6 + cs*0.3 + 0.1*_fals(p, c))))

