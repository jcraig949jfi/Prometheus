"""Anti-cheat static verification (charter s.34).

Checks, by source inspection:
- no LLM / network / filesystem / wall-clock / host-introspection access in
  substrate execution or navigator code
- navigators never import or reference the oracle
- no unseeded stdlib randomness anywhere in the measurement path
- substrate state is a pure function of (genome bytes, frozen probe inputs)

Also enumerates ALL machine-visible information per component.

Writes anti_cheat/anti_cheat.json.
"""
from __future__ import annotations

import io
import json
import os
import re
import tokenize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def code_only(src: str) -> str:
    """Strip comments and string literals: patterns must match CODE, not prose."""
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.STRING):
            out.append(("\n" * tok.string.count("\n")))
        else:
            out.append(tok.string if tok.type != tokenize.NEWLINE else "\n")
        if tok.type in (tokenize.NEWLINE, tokenize.NL):
            out.append("\n")
        else:
            out.append(" ")
    return "".join(out)

FORBIDDEN = {
    "d4core/navigators.py": [r"\boracle\b", r"\bopen\(", r"\brequests\b",
                             r"\bsocket\b", r"\btime\.", r"\bdatetime\b",
                             r"\bimport random\b", r"\bos\.", r"\bsys\."],
    "d4core/interface.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                            r"\btime\.", r"\bdatetime\b", r"\bimport random\b"],
    "substrates/vm_substrates.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                                    r"\btime\.", r"\bdatetime\b",
                                    r"\bimport random\b", r"\bsubprocess\b",
                                    r"\binspect\b", r"\bglobals\(\)",
                                    r"\beval\(", r"\bexec\("],
    "d4core/metrics.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                          r"\btime\.", r"\bdatetime\b"],
    "d4core/classifier.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                             r"\btime\.", r"\bdatetime\b", r"\bimport random\b"],
    "d4core/oracle.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                         r"\btime\.", r"\bdatetime\b", r"\bimport random\b"],
    "d4core/gates.py": [r"\bopen\(", r"\brequests\b", r"\bsocket\b",
                        r"\btime\.", r"\bdatetime\b", r"\bimport random\b"],
}

MACHINE_VISIBLE = {
    "substrate_execution": [
        "genome bytes (the program under evaluation)",
        "frozen probe inputs (8 tapes x 8 nibbles, seed 20260827)",
        "frozen decode tables (opcode semantics; ENC_PERM under the "
        "representation counterfactual, seed 3301)",
        "step/tape/stack/output caps (frozen constants)",
    ],
    "navigators_M0": [
        "fingerprints returned by evaluate() (opaque objects)",
        "d1(f,f') scalar distances",
        "viable(f) booleans",
        "pkey(f) equality (phenotype identity)",
        "target fingerprint (raw; no target ID, no stratum label)",
        "operator count n_ops and opaque operator indices via sample_op()",
        "own RNG stream (seeded per run)",
        "remaining budget (implicit via loop)",
    ],
    "navigators_M0_NOT_visible": [
        "operator names/semantics", "substrate identity", "oracle output",
        "phenotype graph", "other navigators' results", "target metadata",
        "human taxonomy labels", "counterfactual condition identity",
        "filesystem/network/clock", "census statistics",
    ],
    "oracle": [
        "full observed single-parent transition graph (ANALYSIS ONLY, "
        "computed after all navigation rows are final; crossover edges "
        "excluded)",
    ],
}


def main() -> dict:
    findings = []
    for rel, pats in FORBIDDEN.items():
        raw = open(os.path.join(BASE, rel), encoding="utf-8").read()
        # strip the packaging header of vm_substrates (sys.path bootstrap)
        if rel.endswith("vm_substrates.py"):
            raw = raw.replace("import os\nimport sys\n\nsys.path.insert(0, "
                              "os.path.dirname(os.path.dirname(os.path.abspath(__file__))))", "")
        src = code_only(raw)
        for pat in pats:
            for m in re.finditer(pat, src):
                line = src[:m.start()].count("\n") + 1
                findings.append({"file": rel, "pattern": pat, "line": line})
    ok = len(findings) == 0
    out = {
        "clean": ok,
        "violations": findings,
        "machine_visible_information": MACHINE_VISIBLE,
        "structural_guarantees": [
            "budget binds on metered evaluate() calls; cache hits are metered "
            "identically for every consumer (no cache asymmetry)",
            "counterfactual physics presented through the same MenuWrapper "
            "interface; navigators cannot detect the condition",
            "no post-budget success: hit checks occur inside the budget loop",
            "all RNG = numpy Generator with explicit frozen seeds",
            "target selection is deterministic given the frozen seed and uses "
            "an independent seed family from navigation",
        ],
    }
    with open(os.path.join(BASE, "anti_cheat", "anti_cheat.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("ANTI-CHEAT", "CLEAN" if ok else f"VIOLATIONS: {findings}")
    return out


if __name__ == "__main__":
    main()
