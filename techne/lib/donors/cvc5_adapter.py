"""cvc5 donor adapter -- exact SMT decision + counterexample extraction.

Upstream: github.com/cvc5/cvc5 (identity RESOLVED from declared project URLs).

WHY IT IS HERE AND WHAT WOULD RETIRE IT. z3 5.0.0.0 is already installed and already covers
QF_LIA/QF_NIA/QF_BV decision and model extraction. So cvc5 has to justify itself against an
incumbent, and the honest Gen-0 answer may well be REDUNDANT_AT_GEN0. That is a successful
result, not a failure -- an arsenal that records "we already had this" is smaller and truer
than one that keeps a second solver because it was installed.

The mechanical differences that could matter to an adversary bench, and which the comparator
in `techne/scripts/donor_smt_comparator.py` measures rather than asserts: cvc5 carries native
decision procedures for finite-field, sequence, bag and separation-logic theories that z3 does
not expose, and its syntax-guided synthesis (SyGuS) front end is a different capability class
from model extraction. None of that is exercised at Gen 0.

SELECTION RELATION: NONE. A decision procedure returns sat/unsat/unknown plus a model. It
imposes no preference over the models it could have returned -- which is precisely why a
counterexample it hands back is a fact about the constraint system rather than about cvc5's
taste. Downstream code that treats "the model cvc5 happened to return" as canonical is reading
an arbitrary witness as a distinguished one.
"""
from __future__ import annotations

from typing import Any, Mapping

from .contract import (
    NO_SELECTION, DonorAdapter, DonorCapability, DonorError, DonorIdentity, register,
)


@register("cvc5")
class Cvc5Adapter(DonorAdapter):
    """Integer linear constraint solving with model extraction, over a small typed DSL."""

    native_selection_relation = NO_SELECTION

    accepted_config = frozenset({"logic", "produce_models", "timeout_ms"})

    def _identity(self) -> DonorIdentity:
        try:
            import importlib.metadata as md
            v = md.version("cvc5")
        except Exception as e:                                        # noqa: BLE001
            raise DonorError("cvc5", "identity", "cvc5 is not installed", e)
        return DonorIdentity(
            name="cvc5", distribution="cvc5", version=v,
            upstream="github.com/cvc5/cvc5", license="BSD-3-Clause",
            identity_evidence="declared_url",
        )

    def _capabilities(self):
        return [
            DonorCapability(
                "check_int_constraints",
                "decide a conjunction of linear integer constraints; return a model if sat",
                deterministic=True,
                inputs="payload = {'vars': [names], 'constraints': [(lhs_terms, op, rhs)]} "
                       "where lhs_terms maps var name -> integer coefficient and op is one of "
                       "== != < <= > >=; config logic, produce_models, timeout_ms",
                outputs="dict(result, model, n_vars, n_constraints)",
            ),
        ]

    _OPS = {"==", "!=", "<", "<=", ">", ">="}

    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None):
        import cvc5
        from cvc5 import Kind

        if capability != "check_int_constraints":
            raise DonorError("cvc5", "capability", "unreachable: " + repr(capability))
        if not isinstance(payload, Mapping) or "vars" not in payload \
                or "constraints" not in payload:
            raise DonorError("cvc5", "input",
                             "payload must be a mapping with 'vars' and 'constraints'")

        names = [str(v) for v in payload["vars"]]
        if len(set(names)) != len(names):
            raise DonorError("cvc5", "input", "duplicate variable names")

        # VALIDATE THE WHOLE PAYLOAD BEFORE ANY cvc5 OBJECT EXISTS.
        #
        # This is not only fail-fast hygiene. Raising while a live TermManager/Solver sits in
        # the frame leaves those native objects reachable from the exception's traceback, and
        # on this platform that combination -- a completed solve in one test plus a retained
        # error frame in another -- segfaults the interpreter at teardown (exit 139, after all
        # tests report PASS). Validating first means a caller error never captures a solver.
        # See TECHNE_GEN0_DONOR_HANDOFF.txt, cvc5 limitations.
        parsed = []
        for i, con in enumerate(payload["constraints"]):
            try:
                lhs, op, rhs = con
            except Exception as e:                                    # noqa: BLE001
                raise DonorError("cvc5", "input",
                                 "constraint " + str(i) + " must be (coeffs, op, rhs)", e)
            if op not in self._OPS:
                raise DonorError("cvc5", "input",
                                 "constraint " + str(i) + " has unsupported op " + repr(op)
                                 + "; supported: " + repr(sorted(self._OPS)))
            if not isinstance(lhs, Mapping):
                raise DonorError("cvc5", "input",
                                 "constraint " + str(i) + " lhs must be a coefficient mapping")
            for n in lhs:
                if str(n) not in names:
                    raise DonorError("cvc5", "input", "unknown variable " + repr(n))
            try:
                parsed.append(({str(n): int(c) for n, c in lhs.items()}, op, int(rhs)))
            except Exception as e:                                    # noqa: BLE001
                raise DonorError("cvc5", "input",
                                 "constraint " + str(i) + " has non-integer coefficients", e)

        # cvc5 1.3 routes term construction through a TermManager; older builds put those
        # methods on Solver. Support both rather than pinning a build.
        tm = cvc5.TermManager() if hasattr(cvc5, "TermManager") else None
        slv = cvc5.Solver(tm) if tm is not None else cvc5.Solver()
        mk = tm if tm is not None else slv
        slv.setLogic(str(config.get("logic", "QF_LIA")))
        if config.get("produce_models", True):
            slv.setOption("produce-models", "true")
        if "timeout_ms" in config:
            slv.setOption("tlimit-per", str(int(config["timeout_ms"])))

        Int = mk.getIntegerSort()
        sym = {n: mk.mkConst(Int, n) for n in names}

        def term_of(coeffs: Mapping[str, Any]):
            parts = [mk.mkTerm(Kind.MULT, mk.mkInteger(c), sym[n]) for n, c in coeffs.items()]
            if not parts:
                return mk.mkInteger(0)
            acc = parts[0]
            for p in parts[1:]:
                acc = mk.mkTerm(Kind.ADD, acc, p)
            return acc

        kind_of = {"==": Kind.EQUAL, "<": Kind.LT, "<=": Kind.LEQ,
                   ">": Kind.GT, ">=": Kind.GEQ}
        for lhs, op, rhs in parsed:
            L, R = term_of(lhs), mk.mkInteger(rhs)
            t = (mk.mkTerm(Kind.NOT, mk.mkTerm(Kind.EQUAL, L, R)) if op == "!="
                 else mk.mkTerm(kind_of[op], L, R))
            slv.assertFormula(t)

        r = slv.checkSat()
        result = "sat" if r.isSat() else ("unsat" if r.isUnsat() else "unknown")
        model = None
        if result == "sat" and config.get("produce_models", True):
            # getValue returns a Term; its integer value is read back through the API rather
            # than parsed out of str(), which is not a stable interface.
            model = {n: int(slv.getValue(sym[n]).getIntegerValue()) for n in names}
        out = {"result": result, "model": model,
               "n_vars": len(names), "n_constraints": len(parsed)}
        # Drop every native handle before returning. The payload is plain Python by
        # construction, so nothing cvc5-owned escapes this frame.
        del r, sym, Int, mk, slv, tm
        return out, None
