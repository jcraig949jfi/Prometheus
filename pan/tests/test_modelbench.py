"""PAN-19 controls for the model smoke-test checkers (no model, no network).

POSITIVE  reference solutions pass every probe
NEGATIVE  wrong answers fail every probe
CHEAT     a solution hard-coded to the prompt's own example fails the hidden
          tests; a math answer that states the right number but ends on a
          different integer fails; JSON with an extra key fails
"""
import pytest

from pan import modelbench as mb

REF = {
    "code_is_prime": "def is_prime(n):\n    if n < 2: return False\n    i = 2\n    while i*i <= n:\n        if n % i == 0: return False\n        i += 1\n    return True",
    "code_rle": "def rle(s):\n    out=[]; i=0\n    while i < len(s):\n        j=i\n        while j < len(s) and s[j]==s[i]: j+=1\n        out.append(s[i]+str(j-i)); i=j\n    return ''.join(out)",
    "code_flatten": "def flatten(xs):\n    out=[]\n    for x in xs:\n        out.extend(flatten(x) if isinstance(x, list) else [x])\n    return out",
    "code_reverse_words": "def reverse_words(s):\n    return ' '.join(s.split(' ')[::-1])",
    "code_fib": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n): a, b = b, a+b\n    return a",
    "code_balanced": "def balanced(s):\n    st=[]; pairs={')':'(',']':'[','}':'{'}\n    for c in s:\n        if c in '([{': st.append(c)\n        elif c in pairs:\n            if not st or st.pop()!=pairs[c]: return False\n    return not st",
}
CHEAT = {
    "code_rle": "def rle(s):\n    return 'a2b1'",
    "code_is_prime": "def is_prime(n):\n    return n in (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)",
    "code_fib": "def fib(n):\n    return [0,1,1,2,3,5,8,13,21,34][n]",
}
PROBES = {p["id"]: p for p in mb.PROBES}


def block(code):
    return "```python\n" + code + "\n```"


@pytest.mark.parametrize("pid", sorted(REF))
def test_positive_code(pid):
    ok, detail = mb.check(PROBES[pid], block(REF[pid]))
    assert ok, detail


@pytest.mark.parametrize("pid", sorted(CHEAT))
def test_cheat_code_hardcoded_fails(pid):
    ok, _ = mb.check(PROBES[pid], block(CHEAT[pid]))
    assert not ok


def test_math_positive_negative_cheat():
    p = PROBES["math_arith"]
    assert mb.check(p, "Working...\n461")[0]
    assert not mb.check(p, "460")[0]
    assert not mb.check(p, "It might be 461, but recomputing gives\n460")[0]


def test_json_positive_negative_cheat():
    p = PROBES["json_basic"]
    assert mb.check(p, 'Sure: {"name": "Pan", "count": 3, "tags": ["a", "b"]}')[0]
    assert not mb.check(p, '{"name": "Pan", "count": "3", "tags": ["a", "b"]}')[0]
    assert not mb.check(p, '{"name": "Pan", "count": 3, "tags": ["a", "b"], "extra": 1}')[0]


def test_thinking_is_stripped():
    assert mb.strip_thinking("<think>461? no</think>\n460") == "460"
