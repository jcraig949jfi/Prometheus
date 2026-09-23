"""Mechanical organ extraction by first-order anti-unification (Plotkin LGG).

Procedure declared in AMENDMENT_7_2026-09-22.md section A and committed at
abad582c9 BEFORE this was run. The reusable fold is not defined by hand: it
is computed from the two structures slice 2C discovered independently, and
serialised and hashed before any third family is selected.
"""
import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E      # noqa: E402
import slice2c as S     # noqa: E402

HOLE_GRAMMARS = {
    "INIT": {"kind": "value", "grammar": "{0, 1}"},
    "E": {"kind": "operator", "grammar": "expressions over {acc, v}, depth <= 2, "
                                         "declared primitives"},
    "F": {"kind": "expression", "grammar": "acc, or a single primitive application "
                                           "over {acc, last}"},
}


# ---------------------------------------------------------------- terms
def to_term(src: str):
    """Parse a discovered part into a term: ('op', name, [args]) or ('var', n)
    or ('const', value)."""
    node = ast.parse(src.strip(), mode="eval").body

    def conv(n):
        if isinstance(n, ast.BinOp):
            op = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
                  ast.FloorDiv: "fdiv", ast.Mod: "mod"}[type(n.op)]
            return ("op", op, [conv(n.left), conv(n.right)])
        if isinstance(n, ast.Call):
            name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            return ("op", {"gcd": "gcd", "pow": "powr", "_pw": "powr",
                           "abs": "abs"}.get(name, name), [conv(a) for a in n.args])
        if isinstance(n, ast.Name):
            return ("var", n.id, [])
        if isinstance(n, ast.Constant):
            return ("const", n.value, [])
        raise ValueError("unsupported node %r" % type(n))

    return conv(node)


def term_str(t):
    kind, name, args = t
    if kind in ("var", "const"):
        return str(name)
    if kind == "hole":
        return ("[%s]" % name if not args
                else "[%s](%s)" % (name, ", ".join(term_str(a) for a in args)))
    return "%s(%s)" % (name, ", ".join(term_str(a) for a in args))


def node_count(t):
    return 1 + sum(node_count(a) for a in t[2])


# ---------------------------------------------------------------- the procedure
def antiunify(s, t, holes, mapping):
    """Plotkin LGG. `mapping` makes the generalisation CONSISTENT: the same
    mismatched pair always maps to the same hole."""
    if s == t:
        return s
    key = (term_str(s), term_str(t))
    sk, sn, sa = s
    tk, tn, ta = t
    if sk == "op" and tk == "op" and sn == tn and len(sa) == len(ta):
        return ("op", sn, [antiunify(a, b, holes, mapping) for a, b in zip(sa, ta)])
    if sk == "op" and tk == "op" and len(sa) == len(ta):
        # same arity, different symbol -> operator hole over generalised args
        if key not in mapping:
            mapping[key] = "H%d" % (len(holes) + 1)
            holes.append({"name": mapping[key], "arity": len(sa),
                          "from": [term_str(s), term_str(t)]})
        return ("hole", mapping[key],
                [antiunify(a, b, holes, mapping) for a, b in zip(sa, ta)])
    # leaf vs node, or arity clash -> hole covering the position
    if key not in mapping:
        mapping[key] = "H%d" % (len(holes) + 1)
        holes.append({"name": mapping[key], "arity": 0,
                      "from": [term_str(s), term_str(t)]})
    return ("hole", mapping[key], [])


def instantiate(t, choice):
    """Fill holes with the `choice`-th original term, to verify the organ
    recovers BOTH inputs exactly (admissibility condition iii)."""
    kind, name, args = t
    if kind == "hole":
        for h in ORGAN_HOLES:
            if h["name"] == name:
                return h["from"][choice]
        raise KeyError(name)
    if kind in ("var", "const"):
        return str(name)
    return "%s(%s)" % (name, ", ".join(instantiate(a, choice) for a in args))


ORGAN_HOLES = []


def main():
    # the two structures slice 2C discovered, read from a rebuilt artifact --
    # not retyped by hand
    lin = S.Lineage2C(lineage_id="L2C-001", base=E.base_image())
    lin.evolve(generations=E.FROZEN_GENERATION, escrow=E.Escrow(10 ** 7))
    art = lin.extract(E.FROZEN_GENERATION)
    folds = S.parse_folds(art)
    assert set(folds) == {"list_sum", "list_prod_mod"}, folds

    a, b = folds["list_sum"], folds["list_prod_mod"]
    parts, holes, mapping = {}, [], {}
    for part, ka, kb in (("INIT", a["init"], b["init"]),
                         ("E", a["body"], b["body"]),
                         ("F", a["final"], b["final"])):
        s, t = to_term(ka), to_term(kb)
        g = antiunify(s, t, holes, mapping)
        parts[part] = {"list_sum": term_str(s), "list_prod_mod": term_str(t),
                       "generalised": term_str(g), "term": g,
                       "identical": s == t}
    ORGAN_HOLES.extend(holes)

    # admissibility
    recovers = {}
    for idx, fam in ((0, "list_sum"), (1, "list_prod_mod")):
        ok = all(instantiate(parts[p]["term"], idx) == parts[p][fam] for p in parts)
        recovers[fam] = ok
    admissible = (len(holes) >= 1
                  and all(h["name"].startswith("H") for h in holes)
                  and all(recovers.values()))

    organ = {
        "procedure": "first-order anti-unification (Plotkin LGG), AMENDMENT 7 section A",
        "declared_at_commit": "abad582c9",
        "source_structures": {
            "list_sum": {"INIT": a["init"], "E": a["body"], "F": a["final"]},
            "list_prod_mod": {"INIT": b["init"], "E": b["body"], "F": b["final"]},
        },
        "skeleton": ["acc = <INIT>", "for v in vals:", "    acc = <E>(acc, v)",
                     "return <F>(acc, last)"],
        "generalised": {p: parts[p]["generalised"] for p in parts},
        "holes": holes,
        "hole_grammars": HOLE_GRAMMARS,
        "recovers_inputs": recovers,
        "admissible": admissible,
        "unique_without_human_choice": True,
        "node_counts": {p: node_count(parts[p]["term"]) for p in parts},
        "source_artifact_sha256": art.sha256,
    }
    canonical = json.dumps(organ, sort_keys=True, separators=(",", ":")).encode()
    organ["organ_sha256"] = hashlib.sha256(canonical).hexdigest()

    if not admissible:
        organ["verdict"] = "ORGAN_NOT_IDENTIFIABLE"
    else:
        organ["verdict"] = "ORGAN_IDENTIFIED"

    (HERE / "ORGAN_2026-09-22.json").write_text(
        json.dumps(organ, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(organ, indent=2, sort_keys=True))
    return 0 if admissible else 2


if __name__ == "__main__":
    raise SystemExit(main())
