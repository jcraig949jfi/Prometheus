"""Instrument smoke tests for RM-D5 VM + physics. Engineering, not evidence."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mutation'))
from rm_vm import run, behavior, MAX_LEN
from physics import mutate, crossover, SEED_REPERTOIRE, MUT_CLASSES
import random


def test_semantics():
    assert run((('MOV', 0, 0),), (42,))[0] == 42
    assert run((('SET', 0, 3),), (99,))[0] == 3            # palette[3] = 3
    assert run((('ADD', 0, 0),), (21,))[0] == 42
    assert run((('MUL', 0, 0),), (300,))[0] == (300 * 300) & 0xFFFF
    assert run((('SET', 1, 1), ('ADD', 0, 1)), (41,))[0] == 42
    assert run((('SUB', 0, 1),), (0, 1))[0] == 0xFFFF       # wraparound
    assert run((('SET', 1, 4), ('SHL', 0, 1)), (1,))[0] == 32  # palette[4]=5
    assert run((('MOD', 0, 1),), (17, 5))[0] == 2
    assert run((('MOD', 0, 1),), (17, 0))[0] == 0           # div-by-zero -> 0
    # SKZ skips next instruction when register is zero
    assert run((('SKZ', 1, 0), ('SET', 0, 9)), (7, 0))[0] == 7
    assert run((('SKZ', 1, 0), ('SET', 0, 9)), (7, 1))[0] == 255
    # JNZ loop: countdown r1 from 5, add r2=3 each iteration -> r0 = 15
    prog = (('SET', 2, 3), ('SET', 3, 1), ('ADD', 0, 2), ('SUB', 1, 3), ('JNZ', 1, 2))
    assert run(prog, (0, 5))[0] == 15
    # infinite loop terminates at step budget
    out, steps = run((('SET', 1, 1), ('JNZ', 1, 1)), (7,))
    assert steps == 512 and out == 7


def test_physics_closure():
    rng = random.Random(1000)  # engineering seed
    for seed_prog in SEED_REPERTOIRE:
        g = seed_prog
        for _ in range(500):
            g = mutate(g, rng)
            assert 1 <= len(g) <= MAX_LEN
            run(g, (17,))  # must never raise
    for _ in range(200):
        a = mutate(SEED_REPERTOIRE[0], rng)
        b = mutate(SEED_REPERTOIRE[3], rng)
        c = crossover(a, b, rng)
        assert 1 <= len(c) <= MAX_LEN
        run(c, (5,))


def test_determinism():
    rng = random.Random(1001)
    g = SEED_REPERTOIRE[0]
    for _ in range(200):
        g = mutate(g, rng)
    probe = [(x,) for x in range(64)]
    assert behavior(g, probe) == behavior(g, probe)


def test_ablation_classes():
    rng = random.Random(1002)
    for cls in MUT_CLASSES:
        allowed = [c for c in MUT_CLASSES if c != cls]
        g = SEED_REPERTOIRE[0]
        for _ in range(100):
            g = mutate(g, rng, allowed=allowed)
        run(g, (9,))


if __name__ == '__main__':
    test_semantics()
    test_physics_closure()
    test_determinism()
    test_ablation_classes()
    print("ALL SMOKE TESTS PASS")
