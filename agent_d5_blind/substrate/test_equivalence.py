"""Measurement equivalence: rm_fast must match rm_vm bit-for-bit on outputs.
Run over random mutation orbits (all opcodes, loops, step-budget truncation)
x all 64 single inputs + two-input grid. Any mismatch is a freeze-blocker."""
import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mutation'))
from rm_vm import run
from rm_fast import FastTask
from physics import mutate, SEED_REPERTOIRE


def main():
    rng = random.Random(1042)
    progs = []
    for s in SEED_REPERTOIRE:
        g = s
        for _ in range(150):
            g = mutate(g, rng)
            progs.append(g)
    # force loopy programs into the pool
    progs.append((('SET', 1, 1), ('JNZ', 1, 1)))
    progs.append((('SET', 2, 3), ('SET', 3, 1), ('ADD', 0, 2),
                  ('SUB', 1, 3), ('JNZ', 1, 2)))

    dom1 = [((x,), 0) for x in range(64)]
    dom2 = [((x, y), 0) for x in range(8) for y in range(8)]
    ft1 = FastTask({'table': dom1})
    ft2 = FastTask({'table': dom2})

    checked = 0
    for g in progs:
        ref1 = [run(g, inp)[0] for inp, _ in dom1]
        fast1 = list(ft1.outputs(g))
        assert ref1 == fast1, f'MISMATCH single-input: {g}'
        ref2 = [run(g, inp)[0] for inp, _ in dom2]
        fast2 = list(ft2.outputs(g))
        assert ref2 == fast2, f'MISMATCH two-input: {g}'
        checked += 1
    print(f'EQUIVALENCE PASS: {checked} programs x 128 inputs, bit-identical')


if __name__ == '__main__':
    main()
