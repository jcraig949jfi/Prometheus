"""Guard vs generate — the fresh-resource separation, executed.

The probe is ChatGPT's minimal one: (λx.λy.x) y  must step to something alpha-equal to
λz.y with z ∉ FV(y). A guard-only circuit DETECTS the capture and stops (honest); only a
circuit with an allocator COMPLETES the step. And the bounded-palette allocator reproduces
the R3 capacity phenomenon one level up: the adversary exhausts the palette by mentioning
every name, forcing the same forgot-vs-generate boundary.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.fresh_generation import (  # noqa: E402
    App, CaptureDetected, Lam, Var, alpha_equal, free_vars, gensym, is_fresh,
    palette_namer, substitute,
)


def K():  # (λx.λy.x)
    return Lam("x", Lam("y", Var("x")))


def test_the_minimal_probe_beta_step_needs_renaming():
    """(λx.λy.x) y: substituting x:=y under λy REQUIRES alpha-renaming; with the generator
    the result is alpha-equal to λz.y with z fresh."""
    body = K().body                                   # λy.x
    out = substitute(body, "x", Var("y"), gensym())
    assert isinstance(out, Lam)
    assert out.var not in free_vars(Var("y"))         # z ∉ FV(y)
    assert alpha_equal(out, Lam("w", Var("y")))       # ≡α λw.y


def test_GUARD_ONLY_detects_but_cannot_proceed():
    """The separation: same input, namer=None — capture is DETECTED (the guard works) but
    the step cannot complete. Guarding and generating are different powers."""
    with pytest.raises(CaptureDetected):
        substitute(K().body, "x", Var("y"), namer=None)


def test_guard_only_is_fine_when_no_capture_occurs():
    """The guard-only circuit is a complete R-whatever citizen on capture-free instances —
    the missing power is invisible until the adversary forces a mint."""
    out = substitute(Lam("y", Var("x")), "x", Var("a"), namer=None)
    assert alpha_equal(out, Lam("y", Var("a")))


def test_BOUNDED_palette_is_exhaustible_unbounded_generator_is_not():
    """Fresh-generation's capacity phenomenon: the adversary mentions every palette name
    free in the replacement; the palette allocator dies (StopIteration = nothing fresh
    left), gensym always succeeds. Same shape as the R3 width bound, one level up."""
    palette = ["p", "q", "r"]
    # replacement's free vars include the whole palette AND the binder name
    repl = App(App(Var("p"), Var("q")), App(Var("r"), Var("y")))
    with pytest.raises(StopIteration):
        substitute(Lam("y", Var("x")), "x", repl, palette_namer(palette))
    out = substitute(Lam("y", Var("x")), "x", repl, gensym())
    assert isinstance(out, Lam) and is_fresh(out.var, repl)


def test_deep_scope_is_stack_pressure_not_binder_magic():
    """λx1...λx40.z [z := x_k]: arbitrary lexical depth with an adversarial k. The
    recursive traversal (a stack) plus the generator handles it — confirming their
    diagnosis that depth is iteration pressure, not a binder-specific power."""
    n, k = 40, 17
    body = Var("z")
    for i in range(n, 0, -1):
        body = Lam(f"x{i}", body)
    out = substitute(body, "z", Var(f"x{k}"), gensym())
    # the binder λx17 must have been renamed on the path; x_k stays FREE at the core
    assert f"x{k}" in free_vars(out)
    cur, depth = out, 0
    while isinstance(cur, Lam):
        depth += 1
        cur = cur.body
    assert depth == n and cur == Var(f"x{k}")
