"""Controls for the seeded-bug generator (PAN-37 part 2; no sandbox, no database).

POSITIVE  every operator yields a parseable mutant that differs from the original exactly at its site
NEGATIVE  a function with no applicable site yields no sites
CHEAT     the mutant differs from the original on ONE line only (no reformatting tell), and the
          answer key's line points at that line
"""
from pan.reviewcal import mutate, sites

FN = '''def pick(xs, k=3):
    """Return the first k items above zero."""
    out = []
    for x in xs:
        if x > 0 and len(out) < k:
            out.append(x + 0)
    return out[:k]
'''


def changed_lines(a, b):
    return [i + 1 for i, (x, y) in enumerate(zip(a.splitlines(), b.splitlines())) if x != y]


def test_positive_every_operator_and_one_line_diff():
    ss = sites(FN)
    ops = {op for op, _ in ss}
    assert ops >= {"cmp_flip", "bool_flip", "arith_flip", "off_by_one", "negate_if", "return_none"}
    for op, idx in ss:
        res = mutate(FN, op, idx)
        assert res is not None, (op, idx)
        mutant, line, orig, new = res
        assert mutant != FN and orig != new
        assert len(mutant.splitlines()) == len(FN.splitlines())
        assert changed_lines(FN, mutant) == [line], (op, changed_lines(FN, mutant), line)


def test_specific_mutations():
    by = {}
    for op, idx in sites(FN):
        by.setdefault(op, mutate(FN, op, idx))
    assert "x >= 0" in by["cmp_flip"][0] or "len(out) <= k" in by["cmp_flip"][0]
    assert " or " in by["bool_flip"][0]
    assert "x - 0" in by["arith_flip"][0]
    assert "return None" in by["return_none"][0]
    assert "if not (" in by["negate_if"][0]


def test_negative_no_sites():
    assert sites("def f(name):\n    print(name)\n") == []
