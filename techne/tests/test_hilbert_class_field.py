"""Test TOOL_HILBERT_CLASS_FIELD."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.hilbert_class_field import hilbert_class_field, class_field_tower


def test_Q_sqrt_minus_5():
    """Q(sqrt(-5)) has h=2; HCF = Q(sqrt(-5), i) = Q(sqrt(5), i)."""
    r = hilbert_class_field('x^2+5')
    assert r['class_number_K'] == 2
    assert r['degree_rel'] == 2
    assert r['degree_abs'] == 4
    assert not r['is_trivial']
    # Compute class number of HCF — should be 1 (single step terminates)
    t = class_field_tower('x^2+5', max_depth=3)
    assert t['terminates'] is True
    assert t['depth'] == 1
    assert t['class_number_sequence'] == [2, 1]
    print(f"[Q(sqrt(-5))] HCF={r['abs_poly']} disc={r['disc']} tower depth=1 OK")


def test_trivial_class_number():
    """Q(i) has h=1; HCF is trivial (= Q(i) itself)."""
    r = hilbert_class_field('x^2+1')
    assert r['is_trivial'] is True
    assert r['class_number_K'] == 1
    assert r['degree_rel'] == 1

    t = class_field_tower('x^2+1', max_depth=3)
    assert t['terminates'] is True
    assert t['depth'] == 0
    assert t['class_number_sequence'] == [1]
    print("[Q(i) trivial] OK")


def test_Q_sqrt_minus_23():
    """Q(sqrt(-23)) has h=3; HCF is a cubic extension, tower depth 1."""
    r = hilbert_class_field('x^2+23')
    assert r['class_number_K'] == 3
    assert r['degree_rel'] == 3
    assert r['degree_abs'] == 6

    t = class_field_tower('x^2+23', max_depth=3)
    assert t['terminates'] is True
    assert t['depth'] == 1
    assert t['class_number_sequence'] == [3, 1]
    print(f"[Q(sqrt(-23))] HCF deg 6, tower depth 1 OK")


def test_Q_sqrt_minus_47():
    """Q(sqrt(-47)) has h=5; tower should also terminate at depth 1."""
    t = class_field_tower('x^2+47', max_depth=3)
    assert t['class_number_sequence'][0] == 5
    assert t['terminates'] is True, f"got {t}"
    assert t['depth'] == 1
    print(f"[Q(sqrt(-47))] h=5 tower depth 1 OK")


def test_list_input():
    r = hilbert_class_field([1, 0, 5])  # x^2 + 5
    assert r['class_number_K'] == 2
    assert r['degree_abs'] == 4
    print("[list input] OK")


def test_large_class_number_guard():
    """h > max_class_number: hilbert_class_field raises ValueError.
    2.0.7751.1 has h=110 (Aporia's original failing case)."""
    try:
        hilbert_class_field('x^2+x+1938')
        assert False, "expected ValueError for large class number"
    except ValueError as e:
        assert 'class_number' in str(e) and '110' in str(e), str(e)
    # Custom threshold: h=3 for Q(sqrt(-23)) should now trigger guard with max=2
    try:
        hilbert_class_field('x^2+23', max_class_number=2)
        assert False, "expected ValueError with max_class_number=2"
    except ValueError as e:
        assert '3' in str(e) and 'max_class_number=2' in str(e), str(e)
    print("[large cn guard] OK")


def test_tower_graceful_abort():
    """class_field_tower aborts cleanly on high-h, doesn't raise."""
    t = class_field_tower('x^2+x+1938', max_depth=3)
    assert t['aborted'] is True
    assert t['terminates'] is False
    assert '110' in t['abort_reason']
    assert t['class_number_sequence'] == [110]
    print("[tower graceful abort] OK")


if __name__ == '__main__':
    test_Q_sqrt_minus_5()
    test_trivial_class_number()
    test_Q_sqrt_minus_23()
    test_Q_sqrt_minus_47()
    test_list_input()
    test_large_class_number_guard()
    test_tower_graceful_abort()
    print("\nALL HILBERT_CLASS_FIELD TESTS PASS")
