import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vm.machine import (
    VMError, E_UNDERFLOW, E_STEP_CAP, block_hash, exec_meta, exec_object,
    ser, type_step,
)


def test_object_semantics():
    assert exec_object(("o0",), (3, 4)) == (7,)
    assert exec_object(("o1",), (3, 4)) == (12,)
    assert exec_object(("o2", "o0"), (5,)) == (10,)
    assert exec_object(("o3",), (1, 2)) == (2, 1)
    # skipz skips next instr when top == 0
    assert exec_object(("o4", "o2", "o2"), (7, 0)) == (7, 7)
    assert exec_object(("o4", "o2", "o2"), (7, 1)) == (7, 7, 7)
    assert exec_object((("P", 5), "o0"), (2,)) == (7,)


def test_object_errors_are_typed():
    try:
        exec_object(("o0",), (1,))
        assert False
    except VMError as e:
        assert e.descriptor() == (E_UNDERFLOW, 0, 1)


def test_meta_edit_ops():
    inp = ("o0", "o1", "o2")
    # append: t3 cat
    st = exec_meta(("t3", "d04"), [inp])
    assert st == (("o0", "o1", "o2", "o3"),)
    # prepend: t3 swap cat
    st = exec_meta(("t3", "d01", "d04"), [inp])
    assert st == (("o3", "o0", "o1", "o2"),)
    # split at 1, swap, cat -> rotation
    st = exec_meta(("d08", "d09", "d06", "d01", "d04"), [inp])
    assert st == (("o1", "o2", "o0"),)
    # qlit produces a lit-push instruction
    st = exec_meta(("d07",), [inp])
    assert st == ((("P", inp),),)
    # splt clamps: split at 4 on a length-3 block
    st = exec_meta(("d08", "d09", "d09", "d09", "d09", "d06"), [inp])
    assert st == (inp, ())


def test_determinism_and_hash():
    prog = ("d00", "d04")
    a = exec_meta(prog, [("o0", "o4")])
    b = exec_meta(prog, [("o0", "o4")])
    assert a == b == (("o0", "o4", "o0", "o4"),)
    h1 = block_hash(a[0])
    h2 = block_hash(("o0", "o4", "o0", "o4"))
    assert h1 == h2
    assert ser((("P", ("o0",)), "o1")) == "{[{o0}] o1}"


def test_typing_matches_runtime():
    # every typed-valid short program must execute without type errors
    from meta_language.grammar_v0 import TOKENS
    import itertools
    for n in (1, 2, 3):
        for prog in itertools.product(TOKENS, repeat=n):
            ts = ("B",)
            ok = True
            for tok in prog:
                ts = type_step(ts, tok)
                if ts is None:
                    ok = False
                    break
            if ok and ts == ("B",):
                st = exec_meta(prog, [("o0", "o1")])
                assert len(st) == 1 and isinstance(st[0], tuple)


def test_step_cap():
    try:
        exec_object(("o2",) * 100, (1,), max_steps=10)
        assert False
    except VMError as e:
        assert e.code == E_STEP_CAP


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
