"""egglog donor adapter -- e-graphs, equality saturation, extraction.

Upstream: github.com/egraphs-good/egglog-python, wrapping the Rust core at
github.com/egraphs-good/egglog. Licence MIT, 34 releases.

IDENTITY CAVEAT, RECORDED RATHER THAN SMOOTHED OVER. The `egglog` distribution declares NO
repository URL in its structured PyPI metadata -- only a self-referential PyPI link. The
upstream repo appears in the long description only, which a name-squatter can also copy. The
identity gate therefore rates this `description_only`, weaker than the `declared_url` evidence
behind tensorly, pyribs, DisCoPy and cvc5. It is installed here because it was ALREADY
installed before this assignment (version 13.2.0) and this generation's task for it is
inventory reconciliation, not acquisition. A fresh install on that evidence would need a
maintainer check first.

WHY THIS DONOR IS ARCHITECTURALLY INTERESTING AND WHY THAT IS NOT THIS SEAT'S CALL. An e-graph
holds many equivalent forms of an expression at once and refuses to pick one until extraction.
Lexis's library-learning study rates this family (egg / Ruler / babble / Enumo) as potentially
a better fit for Prometheus than the DreamCoder/Stitch family. That is a scientific judgement
and it stands with Lexis. What this seat can add is the acquisition fact: egglog is the ONLY
member of that family with a maintained Python binding -- babble, Ruler, Enumo and ShapeCoder
are Rust with no Python distribution, and those PyPI names belong to unrelated projects.

SELECTION RELATION. Extraction is not neutral: it returns the MINIMUM-COST representative of an
equivalence class under a cost model. So the donor does impose an ordering, over representations
rather than over solutions, and a bench that reads "the extracted form" as canonical is reading
egglog's cost model. Declared accordingly.
"""
from __future__ import annotations

from typing import Any, Mapping

from .contract import (
    DonorAdapter, DonorCapability, DonorError, DonorIdentity, SelectionRelation, register,
)


@register("egglog")
class EgglogAdapter(DonorAdapter):
    """Saturate a small arithmetic expression language under a caller-chosen ruleset."""

    native_selection_relation = SelectionRelation(
        kind="ordering",
        direction="minimize",
        over="extraction cost over members of an e-class (default: term size / DAG cost)",
        supplied_by="donor",
        note="equality saturation itself is order-free -- it holds all equivalent forms at "
             "once -- but EXTRACTION picks the cheapest under a cost model. The extracted "
             "form is therefore egglog's choice, not a canonical one.",
    )

    accepted_config = frozenset({"rules", "iterations", "saturate"})

    #: The rewrite rules this adapter will apply, by name. Kept as a closed menu because an
    #: adapter that accepted arbitrary rule source would be executing caller-supplied code
    #: through a wrapper whose provenance record claims it ran a named configuration.
    RULES = ("comm_add", "comm_mul", "assoc_add", "mul_one", "add_zero", "distribute")

    def _identity(self) -> DonorIdentity:
        try:
            import importlib.metadata as md
            v = md.version("egglog")
        except Exception as e:                                        # noqa: BLE001
            raise DonorError("egglog", "identity", "egglog is not installed", e)
        return DonorIdentity(
            name="egglog", distribution="egglog", version=v,
            upstream="github.com/egraphs-good/egglog-python", license="MIT",
            identity_evidence="description_only",
        )

    def _capabilities(self):
        return [
            DonorCapability(
                "saturate_extract",
                "build an e-graph over an arithmetic term, saturate under named rewrite rules, "
                "extract the minimum-cost representative",
                deterministic=True,
                inputs="payload = nested term, e.g. ['*', ['+', 2, 3], 1]; "
                       "config rules (subset of RULES), saturate, iterations",
                outputs="dict(input_term, extracted, changed, rules_applied)",
            ),
        ]

    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None):
        if capability != "saturate_extract":
            raise DonorError("egglog", "capability", "unreachable: " + repr(capability))

        rules = tuple(config.get("rules", self.RULES))
        unknown = sorted(set(rules) - set(self.RULES))
        if unknown:
            raise DonorError("egglog", "config",
                             "unknown rule(s) " + repr(unknown)
                             + "; available: " + repr(list(self.RULES)))

        from egglog import EGraph, Expr, i64Like, rewrite, ruleset, vars_

        class Num(Expr):
            def __init__(self, value: i64Like) -> None: ...
            def __add__(self, other: "Num") -> "Num": ...          # noqa: D105
            def __mul__(self, other: "Num") -> "Num": ...          # noqa: D105

        a, b, c = vars_("a b c", Num)
        catalogue = {
            "comm_add": rewrite(a + b).to(b + a),
            "comm_mul": rewrite(a * b).to(b * a),
            "assoc_add": rewrite((a + b) + c).to(a + (b + c)),
            "mul_one": rewrite(a * Num(1)).to(a),
            "add_zero": rewrite(a + Num(0)).to(a),
            "distribute": rewrite(a * (b + c)).to(a * b + a * c),
        }

        def build(term):
            if isinstance(term, bool):
                raise DonorError("egglog", "input", "booleans are not terms")
            if isinstance(term, int):
                return Num(term)
            if isinstance(term, (list, tuple)):
                if len(term) != 3:
                    raise DonorError("egglog", "input",
                                     "term must be [op, lhs, rhs], got " + repr(term))
                op, lhs, rhs = term
                L, R = build(lhs), build(rhs)
                if op == "+":
                    return L + R
                if op == "*":
                    return L * R
                raise DonorError("egglog", "input",
                                 "unsupported operator " + repr(op) + "; supported: + *")
            raise DonorError("egglog", "input", "unsupported term node " + repr(term))

        expr = build(payload)
        rs = ruleset(*[catalogue[r] for r in rules])
        eg = EGraph()
        handle = eg.let("root", expr)
        if config.get("saturate", True):
            eg.run(rs.saturate())
        else:
            eg.run(rs * int(config.get("iterations", 1)))
        extracted = str(eg.extract(handle))
        out = {"input_term": payload, "extracted": extracted,
               "changed": extracted != str(expr), "rules_applied": list(rules)}
        return out, None
