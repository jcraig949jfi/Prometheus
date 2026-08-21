"""Replicate Pin B's N3 finding WITHOUT mutating any code (soak P39).

P31 found the P40 domain-skip pin scores 3/4: narrowing the guard from
`except spec.transform_errors` to `except ValueError` leaves the pin green,
because every operator in the pin raises only ValueError.

P38 replicated the checkpoint pin by transcribing it into subclasses, and flagged
that method's weakness: it runs through MY reconstruction of the code. For this
pin the function is far larger, so transcription risk is worse.

A better mechanism exists here. The guard reads `except spec.transform_errors:`,
and transform_errors is a SPEC FIELD, not a constant. So "narrow the caught set"
is reachable in INPUT SPACE: build a spec with transform_errors=(ValueError,) and
an operator that raises OverflowError. That exercises the REAL function, with no
code mutation, no transcription, and no bytecode involvement.

Step 0 establishes the equivalence rather than assuming it.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from harmonia.primitives.lattice_void_miner import (  # noqa: E402
    LatticeSpec, null_marginal_pairing,
)

ALWAYS = lambda a, b, r: True  # noqa: E731
CELL = {"inv_a": "x", "inv_b": "y", "f": "keep", "g": "keep", "rel": "always"}


def raiser(exc, k=50):
    def op(v):
        if v > k:
            raise exc("outside domain")
        return v
    return op


def spec_with(op, transform_errors):
    return LatticeSpec(
        side_a_name="A", side_b_name="B",
        side_a={"x": list(range(1, 101))}, side_b={"y": list(range(1, 101))},
        operators={"keep": op}, relations=("always",), eval_relation=ALWAYS,
        transform_errors=transform_errors,
    )


print("STEP 0 — is narrowing the FIELD equivalent to narrowing the except clause?")
src = inspect.getsource(null_marginal_pairing)
uses_field = "except spec.transform_errors:" in src
print(f"  guard reads `except spec.transform_errors:` : {uses_field}")
print(f"  => narrowing spec.transform_errors narrows exactly the caught set: {uses_field}")
if not uses_field:
    print("  NOT EQUIVALENT — this is not a replication. Stopping.")
    sys.exit(0)

print("\nSTEP 1 — the real function, no code touched:")
print(f"  {'spec':52s} {'outcome':>34s}")
print("  " + "-" * 88)
CASES = [
    ("default (ValueError, OverflowError) + ValueError op",    raiser(ValueError),    (ValueError, OverflowError)),
    ("default (ValueError, OverflowError) + OverflowError op", raiser(OverflowError), (ValueError, OverflowError)),
    ("NARROWED (ValueError,) + ValueError op",                 raiser(ValueError),    (ValueError,)),
    ("NARROWED (ValueError,) + OverflowError op",              raiser(OverflowError), (ValueError,)),
]
results = {}
for label, op, te in CASES:
    try:
        r = null_marginal_pairing(spec_with(op, te), CELL)
        out = f"OK  n_dropped={r['n_dropped']}"
        crashed = False
    except Exception as e:
        out = f"RAISED {type(e).__name__}"
        crashed = True
    results[label] = crashed
    print(f"  {label:52s} {out:>34s}")

print("  " + "-" * 88)
narrowed_of = results["NARROWED (ValueError,) + OverflowError op"]
default_of = results["default (ValueError, OverflowError) + OverflowError op"]
print(f"\n  OverflowError under the DEFAULT contract  : {'CRASHES' if default_of else 'handled'}")
print(f"  OverflowError under a NARROWED contract   : {'CRASHES' if narrowed_of else 'handled'}")

print("\nSTEP 2 — does the PIN cover the narrowed case?")
pin = open("harmonia/primitives/test_null_domain_skip.py", encoding="utf-8").read()
print(f"  pin mentions transform_errors : {'transform_errors' in pin}")
print(f"  pin mentions OverflowError    : {'OverflowError' in pin}")
print(f"  pin's only raiser is ValueError: {pin.count('raise ValueError') >= 1 and 'raise OverflowError' not in pin}")

print()
if narrowed_of and not default_of:
    print("REPLICATED, transcription-free: the real function tolerates OverflowError under")
    print("its declared contract and CRASHES when the contract is narrowed — and the pin")
    print("exercises neither, so it cannot see the narrowing. This is P31's N3 by a")
    print("mechanism that mutates no code.")
else:
    print("NOT replicated in input space; P31's N3 rests on the code mutation alone.")

# ---------------------------------------------------------------------------
# BREADTH: `except spec.transform_errors` appears at SIX sites in the miner.
# The pin exercises null_marginal_pairing only. Does the same narrowed spec
# reach the others? Input-space again -- no code touched.
print("\nSTEP 3 — how many ENTRY POINTS does the narrowed contract break?")
from harmonia.primitives.lattice_void_miner import evaluate_lattice, mine  # noqa: E402

narrowed = lambda: spec_with(raiser(OverflowError), (ValueError,))   # noqa: E731
default = lambda: spec_with(raiser(OverflowError), (ValueError, OverflowError))  # noqa: E731

ENTRIES = {
 "null_marginal_pairing (the pinned one)": lambda s: null_marginal_pairing(s, CELL),
 "evaluate_lattice":                       lambda s: evaluate_lattice(s),
 "mine":                                   lambda s: mine(s),
}
print(f"  {'entry point':40s} {'default contract':>18s} {'narrowed contract':>19s}")
print("  " + "-" * 80)
broke = 0
for label, call in ENTRIES.items():
    row = []
    for tag, mk in (("default", default), ("narrowed", narrowed)):
        try:
            call(mk())
            row.append("OK")
        except Exception as e:
            row.append(f"RAISED {type(e).__name__}")
    broke += row[1].startswith("RAISED")
    print(f"  {label:40s} {row[0]:>18s} {row[1]:>19s}")
print("  " + "-" * 80)
print(f"  entry points broken by narrowing: {broke}/{len(ENTRIES)}")
print("  (the pin covers exactly one of them)")
