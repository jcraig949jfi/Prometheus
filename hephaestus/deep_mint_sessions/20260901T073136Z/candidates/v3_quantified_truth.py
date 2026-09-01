"""Master Smith cycle 3 — candidate v3 for MINT-0001 (vacuous_truth).

Mechanism: truth of a quantified claim = KERNEL(quantifier, |domain|, |satisfiers|) — three rules —
plus a parser that (1) extracts the claim, (2) identifies the claim's quantifier, its DOMAIN noun
phrase, its predicate and its container, (3) strips the container from the premises and accepts a
premise only if its noun phrase equals the claim's domain (token-set equality after light
stemming), (4) reads emptiness or cardinality facts about that domain. No fact -> abstain.

v3 fixes over v2 (both found by executed failure positions, not by reading): the container-strip
regex had a literal backspace byte where `\\b` was meant (v2 never stripped anything); the
cardinality and emptiness patterns carried optional "in ..." groups that truncated noun phrases
containing "in" ("letters written in latin").
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
    """'letter written in latin in the archive' -> ('letter written in latin', 'the archive').
    The container is always the LAST 'in ...'."""
    m = re.match(r"(.+)\s+in\s+(.+)$", np_with_container.strip())
    return (m.group(1), m.group(2)) if m else (np_with_container.strip(), "")


_CLAIM_FORMS = [
    ("universal",     r"(?:every|each|any)\s+(.+?)\s+is\s+(.+)$"),
    ("universal",     r"all\s+(.+?)\s+are\s+(.+)$"),
    ("neg_universal", r"no\s+(.+?)\s+is\s+(.+)$"),
    ("neg_universal", r"none of the\s+(.+?)\s+are\s+(.+)$"),
    ("existential",   r"(?:some|at least one)\s+(.+?)\s+(?:is|are)\s+(.+)$"),
    ("existential",   r"there (?:is|are)\s+(?:an?\s+)?(.+?)\s+that (?:is|are)\s+(.+)$"),
]
_COND = re.compile(r"(?:if|whenever)\s+an?\s+(.+?)\s+is\s+(.+?),\s*(?:then\s+)?it\s+is\s+(.+)$")


def _parse_claim(claim: str):
    """-> (quantifier, domain_phrase, predicate, container) or None."""
    c = claim.strip().rstrip(".").lower()
    m = _COND.match(c)
    if m:
        d, cont = _split_domain(m.group(1))
        return "conditional", d + " that is " + m.group(2), m.group(3), cont
    for q, pat in _CLAIM_FORMS:
        m = re.match(pat, c)
        if m:
            d, cont = _split_domain(m.group(1))
            return q, d, m.group(2), cont
    return None


# Premise patterns, applied AFTER the container has been removed from the text.
_EMPTY_PATTERNS = [
    r"there are no\s+(.+?)[.,]",
    r"contains no\s+(.+?)[.,]",
    r"not a single\s+(.+?)\s+is[.,]",
    r"the number of\s+(.+?)\s+is zero[.,]",
    r"nobody has ever found an?\s+(.+?),\s*and there are none now[.,]",
    r"there are exactly zero\s+(.+?)[.,]",
    r"contains exactly zero\s+(.+?)[.,]",
    r"(?:^|[.,]\s*)no\s+(.+?)\s+is\s+(.+?)[.,]",        # 'No X is Q.' -> domain 'X that is Q'
]
_CARD = re.compile(r"(?:there are|holds|contains)\s+exactly\s+(\d+)\s+(.+?)(?=,|\.|\s+and\b)")
_SAT = re.compile(r"\b(?:and\s+)?(?:exactly\s+|only\s+)?(?:all\s+)?(\d+)\s+of them are\s+(.+?)[.,]")


def _domain_facts(text: str, dom_key: frozenset, pred_key: frozenset, container: str):
    """-> (n_domain or None, n_sat or None). n_domain == 0 means an emptiness premise matched."""
    t = text.lower()
    if container:
        t = re.sub(r"\s+in\s+" + re.escape(container.lower()) + r"\b", "", t)
    for pat in _EMPTY_PATTERNS:
        for m in re.finditer(pat, t):
            phrase = m.group(1) if m.lastindex == 1 else m.group(1) + " that is " + m.group(2)
            if _key(phrase) == dom_key:
                return 0, None
    for m in _CARD.finditer(t):
        if _key(m.group(2)) == dom_key:
            n_dom = int(m.group(1))
            s = _SAT.search(t[m.end():])
            if s and _key(s.group(2)) == pred_key:
                return n_dom, int(s.group(1))
            return n_dom, None
    return None, None


def quantified_truth(q: str, n_dom, n_sat):
    """The kernel. Three rules; None = not determined by the premises."""
    if n_dom == 0:
        return q != "existential"          # universal / neg_universal / conditional: vacuously true
    if n_dom and n_sat is not None:
        if q in ("universal", "conditional"):
            return n_sat == n_dom
        if q == "neg_universal":
            return n_sat == 0
        if q == "existential":
            return n_sat >= 1
    return None


def op_vacuous_truth(state):
    m = re.search(r"consider the claim:\s*(.*?)\.(?:\s|$)", state.problem_text, re.I | re.S)
    if not m:
        return state
    parsed = _parse_claim(m.group(1))
    if not parsed:
        return state
    q, dom, pred, container = parsed
    n_dom, n_sat = _domain_facts(state.problem_text, _key(dom), _key(pred), container)
    state.comparison = quantified_truth(q, n_dom, n_sat)
    return state
