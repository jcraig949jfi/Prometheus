"""Frozen probe batteries.

The OBJECT language is always G1 (LISPY): artifacts are G1 terms. Only the
TRANSFORM basis varies across G1/G2/G3, so all three bases are censused against
the same artifacts and the same inputs.

Frozen before the census ran. Hashes recorded in the census ledger.
"""

# A: 24 artifacts. The first four are the screen battery A4.
A = [
    "x",
    ("cons", ("head", "x"), ("tail", "x")),
    ("if", ("null", "x"), ("q", "a"), ("head", "x")),
    ("if", ("atom", "x"), "x", ("self", ("head", "x"))),
    ("head", "x"),
    ("tail", "x"),
    ("cons", ("q", "a"), "nil"),
    ("cons", "x", "nil"),
    ("if", ("atom", "x"), "x", "nil"),
    ("self", ("tail", "x")),
    ("if", ("null", "x"), "nil",
     ("cons", ("self", ("head", "x")), ("self", ("tail", "x")))),
    ("cons", ("q", "cons"), ("cons", "x", "nil")),
    ("q", "b"),
    "nil",
    ("cons", ("head", ("tail", "x")), "nil"),
    ("if", ("eq", ("head", "x"), ("q", "a")), ("q", "c"), ("q", "d")),
    ("tail", ("tail", "x")),
    ("cons", "x", "x"),
    ("if", ("not", ("atom", "x")), ("head", "x"), "x"),
    ("self", "x"),
    ("cons", ("q", "if"), ("cons", ("q", "true"), ("cons", "x", "nil"))),
    ("head", ("head", "x")),
    ("if", ("null", ("tail", "x")), ("head", "x"), ("self", ("tail", "x"))),
    ("cons", ("q", "q"), ("cons", ("q", "a"), "nil")),
]

A4 = A[:4]

# I: 12 inputs for extensional fingerprints.
I12 = [
    "a",
    (),
    ("a",),
    ("a", "b"),
    ("a", "b", "c"),
    (("a",), "b"),
    ("a", ("b", "c")),
    (("a", "b"), ("c", "d")),
    ("d", "d", "d", "d"),
    ((), "a"),
    ("c",),
    (("a", ("b",)), "c"),
]

# extension used only for the alias-stability gate CG-G
I24 = I12 + [
    "b",
    ("b",),
    ("c", "a"),
    ("a", "a", "a"),
    ((("a",),),),
    ("b", ("a", "b"), "c"),
    (((), ()),),
    ("d",),
    ("a", "b", "c", "d"),
    (("d",), ("c",), ("b",)),
    ("x", "nil"),
    (("q", "a"), "b"),
]
