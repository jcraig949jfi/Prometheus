"""Master Smith cycle 2 — candidate v2 (from v1: last-" in "-split of the domain; container stripped from premise phrases; plural existentials) for MINT-0001 (vacuous_truth).

Mechanism hypothesis: truth of a quantified claim = KERNEL(quantifier, |domain|, |satisfiers|),
where the kernel is three rules and everything else is finding, in the premises, facts about the
CLAIM'S OWN domain noun phrase (token-set equality after light stemming). No fact -> abstain.
"""
import re

_STOP = {"a", "an", "the", "of", "in", "on", "at", "that", "who", "which", "is", "are", "was", "were",
         "it", "them", "this", "these", "those", "and", "to", "be", "there"}
_IRREG = {"people": "person", "men": "man", "women": "woman", "children": "child"}


def _stem(w: str) -> str:
    w = _IRREG.get(w, w)
    if len(w) > 3 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("es") and w[-3] in "sxz":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _key(phrase: str) -> frozenset:
    toks = re.findall(r"[a-z0-9]+", phrase.lower())
    return frozenset(_stem(t) for t in toks if t not in _STOP)


def _split_domain(np_with_container: str) -> tuple[str, str]:
    """'red marble in the jar' -> ('red marble', 'the jar'); without ' in ' -> (np, '')."""
    m = re.match(r"(.+)\s+in\s+(.+)$", np_with_container.strip())
    return (m.group(1), m.group(2)) if m else (np_with_container.strip(), "")


def _parse_claim(claim: str):
    """-> (quantifier, domain_phrase, predicate) or None. Quantifier in
    {'universal','neg_universal','conditional','existential'}."""
    c = claim.strip().rstrip(".").lower()
    m = re.match(r"(?:every|each|any)\s+(.+?)\s+is\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "universal", d, m.group(2), cont
    m = re.match(r"all\s+(.+?)\s+are\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "universal", d, m.group(2), cont
    m = re.match(r"no\s+(.+?)\s+is\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "neg_universal", d, m.group(2), cont
    m = re.match(r"none of the\s+(.+?)\s+are\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "neg_universal", d, m.group(2), cont
    m = re.match(r"(?:if|whenever)\s+an?\s+(.+?)\s+is\s+(.+?),\s*(?:then\s+)?it\s+is\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "conditional", d + " that is " + m.group(2), m.group(3), cont
    m = re.match(r"(?:some|at least one)\s+(.+?)\s+(?:is|are)\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "existential", d, m.group(2), cont
    m = re.match(r"there (?:is|are)\s+(?:an?\s+)?(.+?)\s+that (?:is|are)\s+(.+)$", c)
    if m:
        d, cont = _split_domain(m.group(1)); return "existential", d, m.group(2), cont
    return None


_EMPTY_PATTERNS = [
    r"there are no\s+(.+?)(?:\s+in\s+[^,.]+)?[.,]",
    r"contains no\s+(.+?)(?:\s+in\s+[^,.]+)?[.,]",
    r"not a single\s+(.+?)\s+is in\s+[^,.]+[.,]",
    r"the number of\s+(.+?)\s+in\s+[^,.]+?\s+is zero[.,]",
    r"nobody has ever found an?\s+(.+?)\s+in\s+[^,.]+?,\s*and there are none now[.,]",
    r"there are exactly zero\s+(.+?)(?:\s+in\s+[^,.]+)?[.,]",
    r"contains exactly zero\s+(.+?)(?:\s+in\s+[^,.]+)?[.,]",
    r"(?:^|[.,]\s*)no\s+(.+?)\s+is\s+(.+?)[.,]",      # 'No X (in C) is Q.' -> domain 'X that is Q'
]

_CARD = re.compile(r"(?:there are|holds|contains)\s+exactly\s+(\d+)\s+(.+?)(?:\s+in\s+[^,.]+?)?(?=,|\.|\s+and\b)")
_SAT = re.compile(r"\b(?:and\s+)?(?:exactly\s+|only\s+)?(all\s+)?(\d+)\s+of them are\s+(.+?)[.,]")


def _domain_facts(text: str, dom_key: frozenset, pred_key: frozenset, container: str = ""):
    """-> (n_domain or None, n_sat or None). n_domain == 0 means an emptiness premise matched.
    The claim's container ('the jar') is removed from the premises first so that phrase
    boundaries do not depend on where ' in <container>' falls inside a noun phrase."""
    t = text.lower()
    if container:
        t = re.sub(r"\s+in\s+" + re.escape(container.lower()) + r"", "", t)
    for pat in _EMPTY_PATTERNS:
        for m in re.finditer(pat, t):
            phrase = m.group(1) if m.lastindex == 1 else m.group(1) + " that is " + m.group(2)
            if _key(phrase) == dom_key:
                return 0, None
    n_dom = None
    for m in _CARD.finditer(t):
        if _key(m.group(2)) == dom_key:
            n_dom = int(m.group(1))
            tail = t[m.end():]
            s = _SAT.search(tail)
            if s and _key(s.group(3)) == pred_key:
                return n_dom, int(s.group(2))
            return n_dom, None
    return n_dom, None


def quantified_truth(q: str, n_dom, n_sat):
    """The kernel. Three rules; None = not determined by the premises."""
    if n_dom == 0:
        return q != "existential"          # universal / neg_universal / conditional are vacuously true
    if n_dom and n_sat is not None:
        if q in ("universal", "conditional"):
            return n_sat == n_dom
        if q == "neg_universal":
            return n_sat == 0
        if q == "existential":
            return n_sat >= 1
    return None


def op_vacuous_truth(state):
    text = state.problem_text
    m = re.search(r"consider the claim:\s*(.*?)\.(?:\s|$)", text, re.I | re.S)
    if not m:
        return state
    parsed = _parse_claim(m.group(1))
    if not parsed:
        return state
    q, dom, pred, container = parsed
    n_dom, n_sat = _domain_facts(text, _key(dom), _key(pred), container)
    state.comparison = quantified_truth(q, n_dom, n_sat)
    return state
